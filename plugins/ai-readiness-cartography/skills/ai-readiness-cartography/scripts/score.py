#!/usr/bin/env python3
"""AI-Readiness Cartography — repo scorer (v3 rubric, evidence-graded, gated).

v3는 2025~2026 1차 근거로 v2를 리팩토링한 것이다(근거·판정은
references/research/ 세션 md 참조). 핵심 변경:

- **집계**: 순수 가중합 → 가중합 + **blocking gate**(하나의 blocking 결함이
  등급에 상한을 씌운다 — Kenogami lowest-as-ceiling / Factory 게이팅).
  · Gate-1 Reference Integrity: 문서가 인용한 파일 경로/line range에 dangling(비존재)
    참조가 1건이라도 있으면 등급 상한 AI-Fragile. (명령 실재·패키지 lock 대조는
    session-3 함의이나 v3 스코어러 미구현 — 향후 확장 후보.)
  · Gate-2 Executable Verification: 실행 가능한 test/build/lint 명령이 하나도
    없으면 등급 상한 AI-Fragile.
- **가중치 재배분**(ORACLE-SWE ablation 서열): 실행·검증(E) > 의존 구조(D) >
  컨텍스트 문서(B/C) — 문서는 novelty·비중복일 때만 가점.
- **A(navigation)**: "보유율(존재율)" 만점 신호 폐기 → structure-first anchor
  (진입점·의존 이웃 명시) 측정(ETH Zurich 2602.11988 반증).
- **B(context)**: 절대 line 수 목표 삭제 → redundancy discipline·command-first.
- **D(dependency)**: "mermaid 존재" → 기계 판독 import 그래프 파싱·결합도.
- **god-file**: 라인 수 단독 임계값(근거 부재) → fan-in/fan-out 결합도. 라인 수는
  "휴리스틱, 근거 약함" 보조 신호.
- 신규 축: H(feedback-loop latency)·I(env & task-discovery reproducibility).
- G(outcomes): success ⁄ efficiency 분리.
- 모든 지표에 auto / heuristic / manual 라벨(score.py 자동화 범위 명확화).

Usage:
    python3 score.py [repo_path]                # default: .
    python3 score.py /path/to/repo --json out.json
    python3 score.py . --markdown               # human-readable to stdout (default)

Pure stdlib — no external dependencies. Python 3.10+.
"""
from __future__ import annotations

import argparse
import ast
import functools
import html
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
IGNORE_DIRS = {
    "node_modules", ".venv", "venv", ".git", ".next", "dist", "build",
    "__pycache__", ".turbo", ".ruff_cache", ".pytest_cache", ".mypy_cache",
    "target", "out", "coverage", ".cache", ".idea", ".vscode",
}
CODE_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".sql", ".swift", ".cs"}
JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
CONTEXT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md")
AGENT_CONTEXT = ("CLAUDE.md", "AGENTS.md")  # agent-directed context, stronger than README

# God-file coupling threshold: agent 편집 정확도로 직접 검증된 라인 수 임계값은
# 없다(session-4 C8) → 결합도(fan-in+fan-out)를 1급 신호로, 라인 수는 보조.
COUPLING_HOTSPOT = 14        # fan_in + fan_out 합이 이 값을 넘으면 결합 hotspot(god-file 1급 신호)
LARGE_FILE_LINES = 300       # 리포트에 '대형 파일'로 *나열*하는 라인 수 컷오프(점수 신호 아님 — 결합도 우선 정렬의 보조 표시)

# Heuristic regex
# ext는 longest-first + 종료 경계(?![A-Za-z0-9])로 .json→.js 절단 방지.
# 선두는 (../)+ | ./ | seg/ — ../ 지원이 없으면 "../lib/x.py"가 "./lib/x.py"로 절단 capture돼 오탐.
RE_PATH_REF = re.compile(
    r"(?<![A-Za-z0-9_/])"
    r"((?:(?:\.\./)+|\./|[A-Za-z0-9_]+/)[A-Za-z0-9_./-]+\.(?:tsx|jsx|mjs|cjs|jsonc|yaml|mdx|scss|ts|js|py|sql|json|yml|toml|md|html|css|sh|go|rs|java|kt|rb|php))"
    r"(?![A-Za-z0-9])"
)
# 좌측 경계 lookbehind 필수: 없으면 긴 [A-Za-z0-9_./-]+ 런의 모든 내부 오프셋이 매치 시작점이
# 되어 O(n²) 백트래킹(ReDoS) — 한 줄짜리 5MB 'aaa….md' 컨텍스트 파일로 수 분 CPU 소모 재현됨.
RE_LINE_RANGE = re.compile(r"(?<![A-Za-z0-9_/])([A-Za-z0-9_./-]+\.[A-Za-z0-9]+):(\d+)(?:[-–](\d+))?")
RE_BASH_FENCE = re.compile(r"```(?:bash|sh|shell|zsh|console)\s*\n([\s\S]*?)```", re.IGNORECASE)
RE_NON_OBVIOUS = re.compile(r"\b(Why:|Note:|Gotcha|Warning|Don't|Caveat|Important:|반드시|주의|Hidden|Deprecated)", re.IGNORECASE)
RE_DONE_CRITERIA = re.compile(r"\b(done when|verify|passes when|success criteria|검증|통과 기준|확인)\b", re.IGNORECASE)
RE_REL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://)([^)]+)\)")
RE_DEPS_HEADING = re.compile(r"^#+\s.*(depend|cross[- ]module|imports?|see also|related|entry point|진입점|의존)", re.IGNORECASE | re.MULTILINE)
RE_NEIGHBOR = re.compile(r"\b(depends on|imports? from|entry point|진입점|의존 이웃|calls into|used by|downstream|upstream)\b", re.IGNORECASE)
RE_PURPOSE_HEADING = re.compile(r"^#+\s.*(purpose|owns?|configures?|overview|책임)", re.IGNORECASE | re.MULTILINE)
RE_PATTERN_HEADING = re.compile(r"^#+\s.*(pattern|how to|common change|workflow|recipe|절차)", re.IGNORECASE | re.MULTILINE)
RE_MERMAID = re.compile(r"```mermaid", re.IGNORECASE)
RE_PKG_IMPORT_PY = re.compile(r"^\s*(?:from|import)\s+([A-Za-z0-9_]+)", re.MULTILINE)
# [^'"\n]{0,300}: import문은 한 줄·유한 길이 — 무제한 [^'"]*는 quote 없는 대형 입력에서 O(n²) 백트래킹(ReDoS)
RE_JS_IMPORT = re.compile(r"""(?:import\s[^'"\n]{0,300}from\s*|require\(\s*|import\(\s*)['"]([^'"\n]+)['"]""")
RE_JS_EXPORT = re.compile(r"^\s*export\s+(?:default\s+|const\s+|function\s+|class\s+|async\s+function\s+|\{)", re.MULTILINE)


# ----------------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------------
@dataclass
class Module:
    path: Path
    rel: str
    code_files: int
    has_context: bool
    context_file: Path | None = None
    context_kind: str = ""


@dataclass
class CategoryScore:
    key: str
    name: str
    score: int
    max: int
    label: str                       # Auto | Heuristic | Manual
    evidence_grade: str              # auto-high | auto-med | heuristic-med | heuristic-low
    basis: str                       # 근거 세션·claim 짧은 인용
    evidence: dict[str, Any] = field(default_factory=dict)
    sub_scores: dict[str, int] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)


@dataclass
class Gate:
    key: str
    name: str
    passed: bool
    detail: str


@dataclass
class Action:
    title: str
    category: str
    effort: str
    effort_hours: float
    impact: str
    impact_score: int
    priority: float
    evidence_grade: str = "heuristic-med"


@dataclass
class Report:
    meta: dict[str, Any]
    total: int
    grade: str
    grade_color: str
    grade_capped: bool
    raw_grade: str
    gates: list[Gate]
    categories: dict[str, CategoryScore]
    insights: list[str]
    actions: list[Action]
    extras: dict[str, Any]


# ----------------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------------
def walk_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            out.append(Path(r) / f)
    return out


# 신뢰할 수 없는 repo 대상 실행 가드: FIFO/디바이스에서의 영구 블록·symlink 통한
# repo 밖 읽기·초대형 파일 메모리 폭주를 막는다. 상한 초과/비정규 파일은 빈 값으로 취급.
MAX_READ_BYTES = 5_000_000


def _safe_readable(p: Path) -> bool:
    try:
        if p.is_symlink() or not p.is_file():
            return False
        return p.stat().st_size <= MAX_READ_BYTES
    except OSError:
        return False


@functools.lru_cache(maxsize=128)
def read_text(p: Path) -> str:
    # 단일 실행 내 동일 파일 재독(문맥 파일·pyproject 등) 방지 캐시.
    # maxsize×MAX_READ_BYTES가 메모리 상한 — 무제한으로 두지 않는다.
    try:
        if not _safe_readable(p):
            return ""
        return p.read_text(errors="ignore")
    except Exception:
        return ""


def count_lines(p: Path) -> int:
    try:
        if not _safe_readable(p):
            return 0
        return len(p.read_text(errors="ignore").splitlines())
    except Exception:
        return 0


def file_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except Exception:
        return 0.0


def pick_context_file(d: Path) -> tuple[Path | None, str]:
    for name in CONTEXT_FILES:
        p = d / name
        if p.exists():
            return p, name
    return None, ""


def find_core_modules(repo: Path) -> list[Module]:
    """Top-level + apps/* + packages/* + services/* + plugins/* code-bearing dirs."""
    # is_dir()는 심링크를 따라가므로 repo 밖을 가리키는 최상위 심링크 디렉토리가 모듈로
    # 채택되어 repo 밖 파일을 읽게 된다(path traversal) — is_symlink() 선제 배제 필수.
    candidates: list[Path] = []
    for d in sorted(repo.iterdir()):
        if not d.is_dir() or d.is_symlink() or d.name in IGNORE_DIRS or d.name.startswith("."):
            continue
        candidates.append(d)
    for parent_name in ("apps", "packages", "services", "plugins"):
        parent = repo / parent_name
        if parent.exists() and parent.is_dir() and not parent.is_symlink():
            candidates = [c for c in candidates if c != parent]
            for d in sorted(parent.iterdir()):
                if d.is_dir() and not d.is_symlink() and d.name not in IGNORE_DIRS and not d.name.startswith("."):
                    candidates.append(d)

    modules: list[Module] = []
    for d in candidates:
        code_count = 0
        for r, dirs, files in os.walk(d):
            dirs[:] = [x for x in dirs if x not in IGNORE_DIRS and not x.startswith(".")]
            for f in files:
                if Path(f).suffix in CODE_EXTS:
                    code_count += 1
        if code_count == 0:
            continue
        ctx_file, ctx_kind = pick_context_file(d)
        modules.append(Module(
            path=d, rel=str(d.relative_to(repo)), code_files=code_count,
            has_context=ctx_file is not None, context_file=ctx_file, context_kind=ctx_kind,
        ))
    return modules


def find_all_context_files(repo: Path) -> list[Path]:
    out: list[Path] = []
    for r, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            if f in CONTEXT_FILES:
                out.append(Path(r) / f)
    return out


def agent_context_files(context_files: list[Path]) -> list[Path]:
    """CLAUDE.md/AGENTS.md — agent-directed. README는 참고용이므로 별도 취급."""
    return [p for p in context_files if p.name in AGENT_CONTEXT]


def find_root_context(repo: Path) -> Path | None:
    for name in AGENT_CONTEXT:
        p = repo / name
        if p.exists():
            return p
    return None


# ----------------------------------------------------------------------------
# Import graph (session-4 C2·C9: 기계 판독 의존 구조가 1급 신호)
# ----------------------------------------------------------------------------
@dataclass
class GraphNode:
    rel: str
    fan_in: int = 0
    fan_out: int = 0
    exports: int = 0
    lines: int = 0


def build_import_graph(repo: Path) -> tuple[dict[str, GraphNode], int, int, int]:
    """repo 내부 파일 간 import 그래프를 파싱한다.

    반환: (nodes, parseable_code_files, total_code_files, supported_code_files)
    - Python: AST로 first-party import 판정(top-level 이름이 repo top-level 디렉터리/모듈과 일치).
    - JS/TS: 상대경로 import/require를 파일로 해석.
    파서는 Python·JS/TS만 지원 — 미지원 언어(Go/Rust/JVM 등)는 supported 집계에서 제외되고
    D1은 neutral 처리된다(파서 한계를 대상 repo 감점으로 전가하지 않는다).
    """
    top_level_names: set[str] = set()
    for d in repo.iterdir():
        if d.is_dir() and d.name not in IGNORE_DIRS and not d.name.startswith("."):
            top_level_names.add(d.name)
        elif d.is_file() and d.suffix == ".py":
            top_level_names.add(d.stem)

    code_files: list[Path] = []
    for p in walk_files(repo):
        # symlink는 그래프 대상에서 제외: 읽지 못하는(_safe_readable=False) 0줄 phantom
        # 노드가 되어 supported 분모·parse_ratio를 희석한다. repo 내부 실 타겟은 별도로 walk된다.
        if p.suffix in CODE_EXTS and not p.is_symlink():
            code_files.append(p)

    nodes: dict[str, GraphNode] = {}
    for p in code_files:
        rel = str(p.relative_to(repo).as_posix())
        nodes[rel] = GraphNode(rel=rel, lines=count_lines(p))

    edges: list[tuple[str, str]] = []  # (importer_rel, imported_rel)
    parseable = 0

    for p in code_files:
        rel = str(p.relative_to(repo).as_posix())
        text = read_text(p)
        if not text:
            continue
        if p.suffix == ".py":
            parsed_ok = False
            try:
                tree = ast.parse(text)
                parsed_ok = True
                for n in ast.walk(tree):
                    mods: list[str] = []
                    if isinstance(n, ast.Import):
                        mods = [a.name for a in n.names]
                    elif isinstance(n, ast.ImportFrom) and n.module:
                        mods = [n.module]
                    for m in mods:
                        top = m.split(".")[0]
                        if top in top_level_names:
                            edges.append((rel, top))  # module-level target
                nodes[rel].exports = len(re.findall(r"^\s*(?:def|class)\s+[A-Za-z_]", text, re.MULTILINE))
            except (SyntaxError, ValueError):
                # ValueError: null byte 포함 소스는 SyntaxError가 아닌 ValueError를 던져
                # 전체 스캔을 중단시킨다(악성/바이너리성 .py 1개로 DoS) — parse 실패로 처리.
                parsed_ok = False
            if parsed_ok:
                parseable += 1
        elif p.suffix in JS_EXTS:
            found = RE_JS_IMPORT.findall(text)
            local = [m for m in found if m.startswith(".")]
            if found:
                parseable += 1
            for m in local:
                target = _resolve_js(p, m, repo)
                if target:
                    edges.append((rel, target))
            nodes[rel].exports = len(RE_JS_EXPORT.findall(text))
        else:
            # 다른 언어: 파싱기는 없지만 코드 존재는 카운트(그래프 미기여)
            pass

    # fan_out: 파일이 내보내는 edge 수 / fan_in: 대상(모듈 top-level or 파일)이 받는 수
    fan_in_counter: dict[str, int] = {}
    for src, dst in edges:
        if src in nodes:
            nodes[src].fan_out += 1
        fan_in_counter[dst] = fan_in_counter.get(dst, 0) + 1
    for rel, node in nodes.items():
        # JS edge는 파일 rel을 직접 타겟팅 → 그대로 매칭.
        node.fan_in = fan_in_counter.get(rel, 0)
        # Python edge는 top-level 모듈명을 타겟팅:
        # (1) 루트 단일 파일 모듈 — "score.py" ← `import score` (counter 키 "score")
        if "/" not in rel:
            stem = rel.rsplit(".", 1)[0]
            node.fan_in += fan_in_counter.get(stem, 0)
        # (2) top-level 디렉터리 패키지 — `import pkg`는 pkg/__init__.py에 귀속(근사)
        elif rel.endswith("/__init__.py"):
            pkg = rel[: -len("/__init__.py")]
            if "/" not in pkg:
                node.fan_in += fan_in_counter.get(pkg, 0)

    supported = sum(1 for p in code_files if p.suffix == ".py" or p.suffix in JS_EXTS)
    return nodes, parseable, len(code_files), supported


def _resolve_js(importer: Path, spec: str, repo: Path) -> str | None:
    base = (importer.parent / spec).resolve()
    for cand in [base, *[base.with_suffix(e) for e in JS_EXTS], *[base / ("index" + e) for e in JS_EXTS]]:
        try:
            if cand.exists() and cand.is_file():
                return str(cand.relative_to(repo).as_posix())
        except Exception:
            continue
    return None


# ----------------------------------------------------------------------------
# Reference integrity (Gate-1) — session-3 C1·C5·C9
# ----------------------------------------------------------------------------
def check_reference_integrity(repo: Path, context_files: list[Path]) -> dict[str, Any]:
    """문서가 인용한 파일 경로·line range의 실존을 검증한다. dangling 0이 gate 통과 조건."""
    total_paths = 0
    total_ranges = 0  # 검증한 line-range 참조 수(E1 정확도 분모에 포함)
    dangling_paths: list[tuple[str, str]] = []
    dangling_ranges: list[tuple[str, str]] = []
    # Gate는 high-precision이어야 하므로(등급 상한 유발) 검증 대상을 보수적으로 한정:
    # 첫 세그먼트가 실제 top-level 엔트리이거나 ./·../ 로 시작하는 repo-상대 경로만 검증.
    # (md/SKILL.md 같은 illustrative/placeholder 경로의 false dangling 방지)
    # 보안: 후보 경로는 resolve 후 repo 내부일 때만 exists/count_lines 대상 —
    # repo 밖 파일시스템 probe·내용(줄 수) 누출 금지. 밖으로 나가는 ref는 검증 대상 제외.
    repo_resolved = repo.resolve()
    top_level = {e.name for e in repo.iterdir()}

    def _inside_repo(c: Path) -> bool:
        try:
            return c.resolve().is_relative_to(repo_resolved)
        except OSError:
            return False

    for p in context_files:
        text = read_text(p)
        for ref in set(RE_PATH_REF.findall(text)):
            first = ref.split("/")[0]
            if not (ref.startswith("./") or ref.startswith("../") or first in top_level):
                continue
            candidates = [c for c in (repo / ref, p.parent / ref) if _inside_repo(c)]
            if not candidates:
                continue  # repo 밖으로 나가는 참조 — probe하지 않고 미집계
            total_paths += 1
            if not any(c.exists() for c in candidates):
                dangling_paths.append((str(p.relative_to(repo)), ref))
        # line range 검증: file:start-end 가 실제 파일 길이 이내인지
        for m in RE_LINE_RANGE.finditer(text):
            fname, start, end = m.group(1), int(m.group(2)), m.group(3)
            target = None
            for c in [repo / fname, p.parent / fname]:
                if _inside_repo(c) and c.exists() and c.is_file():
                    target = c
                    break
            if target is None:
                continue
            total_ranges += 1
            n = count_lines(target)
            # count_lines는 MAX_READ_BYTES 초과/비정규 파일에 0을 반환한다 — 이를 "0줄"로
            # 오독하면 정상 대형 파일(schema.sql 등)에 대한 모든 range 참조가 dangling으로
            # 오판되어 Gate-1이 거짓 실패(등급 오상한)한다. 측정 불가면 판정하지 않는다.
            try:
                if n == 0 and target.stat().st_size > 0:
                    continue
            except OSError:
                continue
            hi = int(end) if end else start
            if hi > n or start < 1:
                dangling_ranges.append((str(p.relative_to(repo)), f"{fname}:{start}-{end or start} (파일 {n}줄)"))
    dangling = len(dangling_paths) + len(dangling_ranges)
    return {
        "total_paths": total_paths,
        "total_ranges": total_ranges,
        "dangling_paths": dangling_paths,
        "dangling_ranges": dangling_ranges,
        "dangling_total": dangling,
        "passed": dangling == 0,
    }


# ----------------------------------------------------------------------------
# Verification command detection (Gate-2 / E2) — session-1 C1, session-5 C8
# ----------------------------------------------------------------------------
def detect_verification(repo: Path) -> dict[str, Any]:
    """실행 가능한 test/build/lint 명령의 존재를 탐지한다(ORACLE-SWE: 실행·검증 신호가 최상위)."""
    signals: dict[str, Any] = {}
    pkg = repo / "package.json"
    test_cmd = build_cmd = lint_cmd = False
    if pkg.exists():
        try:
            data = json.loads(read_text(pkg) or "{}")
            scripts = data.get("scripts", {}) or {}
            keys = " ".join(scripts.keys()).lower()
            test_cmd = any(k in keys for k in ("test", "vitest", "jest", "e2e"))
            build_cmd = "build" in keys
            lint_cmd = any(k in keys for k in ("lint", "typecheck", "tsc"))
        except Exception:
            pass
    make = repo / "Makefile"
    if make.exists():
        mk = read_text(make).lower()
        test_cmd = test_cmd or bool(re.search(r"^test:", mk, re.MULTILINE)) or "pytest" in mk
        build_cmd = build_cmd or bool(re.search(r"^build:", mk, re.MULTILINE))
        lint_cmd = lint_cmd or "lint" in mk
    # Python: 루트뿐 아니라 1-depth 하위 패키지(pyproject monorepo)의 설정도 읽는다
    pyprojects = [q for q in [repo / "pyproject.toml", *sorted(repo.glob("*/pyproject.toml"))] if q.exists()]
    has_tox = (repo / "tox.ini").exists()
    if pyprojects or has_tox:
        py = " ".join(read_text(q) for q in pyprojects)
        test_cmd = test_cmd or "pytest" in py or has_tox
        lint_cmd = lint_cmd or any(t in py for t in ("ruff", "mypy", "flake8", "pyright"))
    # Go/Rust/JVM: 표준 빌드 도구가 test/build 명령을 내장(go test ./… · cargo test · gradle test / mvn test)
    toolchain_builtin = any((repo / f).exists() for f in (
        "go.mod", "Cargo.toml", "build.gradle", "build.gradle.kts",
        "settings.gradle", "settings.gradle.kts", "pom.xml",
    ))
    if toolchain_builtin:
        build_cmd = True
        # test_cmd는 아래에서 실제 테스트 흔적(파일)이 확인될 때만 인정 —
        # 매니페스트만으로 인정하면 테스트 0건 저장소가 Gate-2를 통과하는 과대평가가 된다.

    # 실제 테스트 하네스(파일) 존재 — 명령뿐 아니라 실행 대상.
    # test 디렉토리 *하위* 코드 파일은 파일명과 무관하게 카운트(관용적 레이아웃 지원).
    test_dir_names = {"tests", "test", "__tests__", "spec", "e2e"}
    test_files = 0
    for p in walk_files(repo):
        if p.suffix not in CODE_EXTS:
            continue
        n = p.name.lower()
        in_test_dir = bool(test_dir_names & {seg.lower() for seg in p.parts})
        if "test" in n or "spec" in n or in_test_dir:
            test_files += 1
    has_test_dir = any((repo / d).exists() for d in ("tests", "test", "__tests__", "spec", "e2e"))

    if toolchain_builtin and (test_files > 0 or has_test_dir):
        test_cmd = True

    ci = repo / ".github" / "workflows"
    ci_workflows = list(ci.glob("*.yml")) + list(ci.glob("*.yaml")) if ci.exists() else []
    ci_runs_tests = any(re.search(r"\b(test|pytest|jest|vitest|build|lint|typecheck)\b", read_text(w), re.IGNORECASE) for w in ci_workflows)

    runnable = test_cmd or build_cmd or test_files > 0
    signals.update({
        "test_cmd": test_cmd, "build_cmd": build_cmd, "lint_cmd": lint_cmd,
        "test_files": test_files, "has_test_dir": has_test_dir,
        "ci_workflows": len(ci_workflows), "ci_runs_tests": ci_runs_tests,
        "runnable": runnable,
        "passed": runnable,
    })
    return signals


# ----------------------------------------------------------------------------
# Category scorers
# ----------------------------------------------------------------------------
def score_E(repo: Path, refint: dict, verif: dict, context_files: list[Path]) -> CategoryScore:
    """E. Verification & Executable Signals /22 (Auto) — 최상위 가중(session-1 C1)."""
    sub: dict[str, int] = {}
    # E1 Reference accuracy /6 (Gate-1과 연동)
    # 분모·분자 모두 path + line-range 참조를 포함 — Gate-1을 뒤집는 dangling range가
    # E1 점수에는 반영되지 않던 비대칭 방지.
    total_refs = refint["total_paths"] + refint["total_ranges"]
    if total_refs == 0:
        sub["E1_RefAccuracy"] = 3  # 검증 대상 없음 — neutral
    else:
        acc = (total_refs - refint["dangling_total"]) / total_refs
        sub["E1_RefAccuracy"] = round(6 * acc)
    # E2 Executable verification /10 (Gate-2와 연동) — reproduction/test 최상위
    e2 = 0
    if verif["test_cmd"]:
        e2 += 4
    if verif["test_files"] > 0 or verif["has_test_dir"]:
        e2 += 3
    if verif["build_cmd"]:
        e2 += 2
    if verif["lint_cmd"]:
        e2 += 1
    sub["E2_Executable"] = min(10, e2)
    # E3 CI test pipeline /4
    e3 = 0
    if verif["ci_workflows"] > 0:
        e3 += 2
    if verif["ci_runs_tests"]:
        e3 += 2
    sub["E3_CI"] = e3
    # E4 Independent critic /2
    has_codeowners = any((repo / p).exists() for p in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"))
    has_pr = any((repo / p).exists() for p in (".github/pull_request_template.md", ".github/PULL_REQUEST_TEMPLATE.md"))
    sub["E4_Critic"] = (1 if has_codeowners else 0) + (1 if has_pr else 0)

    pts = min(22, sum(sub.values()))
    findings: list[str] = []
    if refint["dangling_total"] > 0:
        sample = ", ".join(f"{f}: {r}" for f, r in refint["dangling_paths"][:3])
        findings.append(f"⚠ dangling reference {refint['dangling_total']}건(Gate-1 실패) — 예: {sample}")
    if not verif["runnable"]:
        findings.append("⚠ 실행 가능한 test/build 명령 미탐지(Gate-2 실패) — reproduction·검증 신호 부재")
    if verif["ci_workflows"] == 0:
        findings.append("CI 워크플로 없음 — 변경 검증 자동화 부재")
    return CategoryScore(
        key="E", name="Verification & Executable Signals", score=pts, max=22,
        label="Auto", evidence_grade="auto-high",
        basis="ORACLE-SWE(2604.07789): reproduction/test 신호가 성공률 최대 기여(+26~27pp)",
        evidence={**{k: verif[k] for k in ("test_cmd", "build_cmd", "lint_cmd", "test_files", "ci_workflows", "ci_runs_tests")},
                  "ref_total": refint["total_paths"], "ref_dangling": refint["dangling_total"]},
        sub_scores=sub, findings=findings,
    )


def score_D(repo: Path, nodes: dict[str, GraphNode], parseable: int, total_code: int,
            supported_code: int, context_files: list[Path]) -> CategoryScore:
    """D. Dependency & Structure Mapping /18 (Auto) — 기계 판독 그래프 1급(session-4 C2)."""
    sub: dict[str, int] = {}
    # D1 Machine-readable dependency graph /8
    # 분모는 supported(파서 지원 언어)만 — 파서 미지원 언어(Go/Rust/JVM 등)뿐인 repo를
    # 파서 한계로 감점하지 않고 neutral(3) 처리한다(heuristic 한계는 대상 감점이 아님).
    parser_unsupported = supported_code == 0 and total_code > 0
    parse_ratio = (parseable / supported_code) if supported_code else 0.0
    edges = sum(n.fan_out for n in nodes.values())
    has_workspace = any((repo / f).exists() for f in ("turbo.json", "nx.json", "pnpm-workspace.yaml", "lerna.json", "go.work"))
    if parser_unsupported:
        d1 = 3  # neutral
        if has_workspace:
            d1 += 1  # 워크스페이스 파일로 그래프 도출 가능
    else:
        d1 = round(6 * parse_ratio)
        if edges > 0:
            d1 += 1
        if has_workspace:
            d1 += 1
    sub["D1_Graph"] = min(8, d1)
    # D2 Module boundary clarity /4 — 근사: top-level 모듈 수 대비 cross edges 명시성
    module_dirs = {n.rel.split("/")[0] for n in nodes.values() if "/" in n.rel}
    sub["D2_Boundaries"] = 4 if len(module_dirs) >= 2 and edges > 0 else (2 if module_dirs else 0)
    # D3 Coupling-based god-file (결합도 — 라인 수 아님) /4
    hotspots = [n for n in nodes.values() if (n.fan_in + n.fan_out) >= COUPLING_HOTSPOT]
    if total_code == 0:
        sub["D3_Coupling"] = 2
    elif not hotspots:
        sub["D3_Coupling"] = 4
    else:
        ratio = len(hotspots) / max(1, total_code)
        sub["D3_Coupling"] = 4 if ratio < 0.03 else (2 if ratio < 0.08 else 0)
    # D4 Architecture doc / deps section / mermaid /2 (부차)
    has_arch = any((repo / p).exists() for p in ("ARCHITECTURE.md", "docs/architecture.md", "docs/ARCHITECTURE.md", "docs/dependency-graph.md"))
    has_mermaid = any(RE_MERMAID.search(read_text(p)) for p in context_files)
    has_deps_section = any(RE_DEPS_HEADING.search(read_text(p)) for p in context_files)
    sub["D4_ArchDoc"] = min(2, (1 if has_arch or has_mermaid else 0) + (1 if has_deps_section else 0))

    pts = min(18, sum(sub.values()))
    findings: list[str] = []
    if parser_unsupported:
        findings.append("score.py 파서가 이 repo의 언어를 지원하지 않음(Python·JS/TS만 파싱) — D1은 neutral 처리(heuristic 한계, 감점 아님)")
    elif parse_ratio < 0.5 and supported_code > 0:
        findings.append(f"import 그래프 파싱 가능 코드 {parseable}/{supported_code}(지원 언어 기준) — 기계 판독 의존 구조 약함")
    if hotspots:
        top = sorted(hotspots, key=lambda n: -(n.fan_in + n.fan_out))[:3]
        findings.append("결합 hotspot(god-file 후보, 라인 수 아님·fan-in/out): " + ", ".join(f"{n.rel}(in{n.fan_in}/out{n.fan_out})" for n in top))
    return CategoryScore(
        key="D", name="Dependency & Structure Mapping", score=pts, max=18,
        label="Auto", evidence_grade="auto-high",
        basis="LocAgent(2503.09089): 의존 그래프가 embedding 대비 localization 우위(file-level 92.7%)",
        evidence={"parseable_code": parseable, "total_code": total_code, "supported_code": supported_code,
                  "parser_unsupported": parser_unsupported, "edges": edges,
                  "coupling_hotspots": len(hotspots), "workspace": has_workspace},
        sub_scores=sub, findings=findings,
    )


def _readme_corpus(repo: Path) -> set[str]:
    corpus: set[str] = set()
    for name in ("README.md",):
        p = repo / name
        if p.exists():
            for line in read_text(p).lower().splitlines():
                s = line.strip()
                if len(s) > 20:
                    corpus.add(s)
    return corpus


def score_B(repo: Path, context_files: list[Path]) -> CategoryScore:
    """B. Context Quality: Novelty & Discipline /15 (Heuristic) — redundancy·command-first(session-2 C3·C4·C6)."""
    # agent-directed context(CLAUDE.md/AGENTS.md)만 채점 — README 폴백은 README를
    # 자기 자신과 중복 비교(redundancy=1.0)하는 오류를 낳으므로 두지 않는다.
    agent_ctx = agent_context_files(context_files)
    if not agent_ctx:
        return CategoryScore(key="B", name="Context Quality: Novelty & Discipline", score=0, max=15,
                             label="Heuristic", evidence_grade="heuristic-med",
                             basis="ETH Zurich(2602.11988): 문서 존재≠성능, 중복·산문 overview는 순비용",
                             evidence={"agent_context_files": 0}, findings=["agent-directed context(CLAUDE.md/AGENTS.md) 없음"])
    pool = agent_ctx
    n = len(pool)
    readme = _readme_corpus(repo)
    sub: dict[str, int] = {}
    # B1 Redundancy discipline /5 — README와 중복 낮을수록, 산문 overview 적을수록 가점
    redundancy_scores = []
    over_long_prose = 0
    for p in pool:
        lines = [l.strip().lower() for l in read_text(p).splitlines() if len(l.strip()) > 20]
        if not lines:
            redundancy_scores.append(0.0)
            continue
        dup = sum(1 for l in lines if l in readme)
        redundancy_scores.append(dup / len(lines))
        if len(lines) > 120:
            over_long_prose += 1
    avg_redundancy = sum(redundancy_scores) / n
    b1 = round(5 * (1 - min(1.0, avg_redundancy)))
    if over_long_prose:
        b1 = max(0, b1 - 1)
    sub["B1_RedundancyDiscipline"] = b1
    # B2 Command-first (exact commands + done criteria) /4
    cmd_hit = sum(1 for p in pool if RE_BASH_FENCE.search(read_text(p))) / n
    done_hit = sum(1 for p in pool if RE_DONE_CRITERIA.search(read_text(p))) / n
    sub["B2_CommandFirst"] = min(4, round(3 * cmd_hit + 1 * done_hit))
    # B3 Non-obvious patterns /3
    nonobv = sum(1 for p in pool if RE_NON_OBVIOUS.search(read_text(p))) / n
    sub["B3_NonObvious"] = round(3 * nonobv)
    # B4 Key files (3-5 real refs) /3
    key_ratio = 0.0
    for p in pool:
        uniq = len(set(RE_PATH_REF.findall(read_text(p))))
        key_ratio += 1 if uniq >= 3 else (0.5 if uniq >= 1 else 0)
    sub["B4_KeyFiles"] = round(3 * key_ratio / n)

    pts = min(15, sum(sub.values()))
    findings: list[str] = []
    if avg_redundancy > 0.25:
        findings.append(f"context가 README와 {avg_redundancy:.0%} 중복 — novelty 낮음(중복은 순비용, session-2 C5)")
    if over_long_prose:
        findings.append(f"산문 overview 과다 context {over_long_prose}건(>120 lines) — repository overview는 distraction(session-2 C3)")
    if sub["B2_CommandFirst"] < 2:
        findings.append("exact command·done 기준 부족 — command-first는 B의 핵심 가점(session-2 C4·C6)")
    return CategoryScore(
        key="B", name="Context Quality: Novelty & Discipline", score=pts, max=15,
        label="Heuristic", evidence_grade="heuristic-med",
        basis="ETH Zurich(2602.11988): novelty·비중복·command-first가 성능 변수, 절대 line 수 아님",
        evidence={"agent_context_files": n, "avg_redundancy": round(avg_redundancy, 3), "over_long_prose": over_long_prose},
        sub_scores=sub, findings=findings,
    )


def score_C(repo: Path, modules: list[Module]) -> CategoryScore:
    """C. Tribal Knowledge Externalization /12 (Heuristic) — 비discoverable 지식(session-2 C5)."""
    has_memory = (repo / "MEMORY.md").exists() or bool(list(repo.glob(".claude/**/MEMORY.md")))
    adr = any((repo / d).exists() for d in ("docs/adr", "docs/decisions", "adr"))
    has_store = has_memory or adr
    n = max(1, len(modules))
    q = [0, 0, 0, 0]
    for m in modules:
        if not m.context_file:
            continue
        t = read_text(m.context_file)
        if RE_PURPOSE_HEADING.search(t) or "owns" in t.lower() or "configures" in t.lower():
            q[0] += 1
        if RE_PATTERN_HEADING.search(t):
            q[1] += 1
        if RE_NON_OBVIOUS.search(t):
            q[2] += 1
        if RE_DEPS_HEADING.search(t) or "depends on" in t.lower():
            q[3] += 1
    sub = {
        "C_Q1_Owns": round(2 * q[0] / n),
        "C_Q2_Patterns": round(2 * q[1] / n),
        "C_Q3_NonObvious": round(2 * q[2] / n),
        "C_Q4_Deps": round(2 * q[3] / n),
        "C_Q5_Store": 4 if has_store else 0,
    }
    pts = min(12, sum(sub.values()))
    findings: list[str] = []
    if not has_store:
        findings.append("MEMORY.md / ADR 부재 — tribal knowledge 외부화 store 없음")
    if q[2] < n / 2:
        findings.append("non-obvious(실패 유발) 패턴 문서화가 절반 이상 module에서 누락")
    return CategoryScore(
        key="C", name="Tribal Knowledge Externalization", score=pts, max=12,
        label="Heuristic", evidence_grade="heuristic-med",
        basis="ETH Zurich(2602.11988): 이득은 비자명·비discoverable 정보에서만",
        evidence={"memory": has_memory, "adr": adr, "modules": n, "q_pass": q},
        sub_scores=sub, findings=findings,
    )


def score_A(repo: Path, modules: list[Module], context_files: list[Path], root_ctx: Path | None) -> CategoryScore:
    """A. Navigation & Structure-First Anchors /8 (Heuristic) — 보유율 아님, anchor(session-4 C4·C5)."""
    sub: dict[str, int] = {}
    # A1 Root entry briefing (존재 + 진입점 명시) /3
    a1 = 0
    if root_ctx is not None:
        a1 += 1
        rt = read_text(root_ctx)
        if RE_NEIGHBOR.search(rt) or RE_DEPS_HEADING.search(rt):
            a1 += 2
        elif RE_REL_LINK.search(rt):
            a1 += 1
    sub["A1_RootBriefing"] = a1
    # A2 Structure-first anchors: context가 의존 이웃·진입점을 명시하는가 /5
    ctx = agent_context_files(context_files) or context_files
    if ctx:
        anchor_hit = sum(1 for p in ctx if RE_NEIGHBOR.search(read_text(p)) or RE_DEPS_HEADING.search(read_text(p))) / len(ctx)
    else:
        anchor_hit = 0.0
    sub["A2_Anchors"] = round(5 * anchor_hit)

    pts = min(8, sum(sub.values()))
    findings: list[str] = []
    if root_ctx is None:
        findings.append("root CLAUDE.md/AGENTS.md 부재 — 진입점 브리핑 없음")
    if sub["A2_Anchors"] < 3:
        findings.append("context가 의존 이웃·진입점을 명시하지 않음 — 보유율이 아니라 anchor가 navigation의 핵심(session-4 C5)")
    # 참고: 보유율은 점수화하지 않되 진단 정보로만 보고
    covered = sum(1 for m in modules if m.has_context)
    return CategoryScore(
        key="A", name="Navigation & Structure-First Anchors", score=pts, max=8,
        label="Heuristic", evidence_grade="heuristic-med",
        basis="RepoMirage(2605.26177): 파일 노출 아닌 structure-first anchor가 레버; 보유율은 성능과 무관(2602.11988)",
        evidence={"root_context": root_ctx.name if root_ctx else None,
                  "coverage_info_only": f"{covered}/{len(modules)}", "anchor_ratio": round(anchor_hit, 3)},
        sub_scores=sub, findings=findings,
    )


def latest_code_mtime(d: Path) -> float:
    latest = 0.0
    for r, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in IGNORE_DIRS and not x.startswith(".")]
        for f in files:
            if Path(f).suffix in CODE_EXTS:
                latest = max(latest, file_mtime(Path(r) / f))
    return latest


def score_F(repo: Path, modules: list[Module], refint: dict) -> CategoryScore:
    """F. Freshness & Self-Maintenance /8 (Auto) — stale-drift 방향성(session-3 C6)."""
    drifted = measurable = 0
    for m in modules:
        if not m.context_file:
            continue
        code_mtime = latest_code_mtime(m.path)
        if code_mtime == 0:
            continue
        measurable += 1
        if file_mtime(m.context_file) + 30 * 86400 < code_mtime:
            drifted += 1
    drift_ratio = (drifted / measurable) if measurable else 0.0
    ci = repo / ".github" / "workflows"
    workflows = (list(ci.glob("*.yml")) + list(ci.glob("*.yaml"))) if ci.exists() else []
    ctx_validation = any(re.search(r"context|docs|claude|adr|reference|path.*valid|ls-files", read_text(w), re.IGNORECASE) for w in workflows)
    hook_validates = any((repo / p).exists() for p in (".husky/pre-commit", ".husky/pre-push", ".pre-commit-config.yaml", "lefthook.yml"))

    sub = {}
    # F1 stale-drift /4 (dangling reference도 stale drift 신호)
    f1 = round(4 * (1 - drift_ratio)) if measurable else 2
    if refint["dangling_total"] > 0:
        f1 = max(0, f1 - 2)
    sub["F1_StaleDrift"] = f1
    # F2 CI/hook path validation /4
    sub["F2_Validation"] = (2 if ctx_validation else 0) + (2 if hook_validates else 0)
    pts = min(8, sum(sub.values()))
    findings: list[str] = []
    if drifted:
        findings.append(f"{drifted}/{measurable} module context가 코드 변경 후 30일+ 미갱신(stale drift)")
    if not ctx_validation and not hook_validates:
        findings.append("CI/hook에 path·reference validation 없음 — stale reference가 조용히 누적(session-3 C6)")
    return CategoryScore(
        key="F", name="Freshness & Self-Maintenance", score=pts, max=8,
        label="Auto", evidence_grade="auto-med",
        basis="Ashik et al.(2604.09515): stale context가 실행가능성 42.55%로 저하·능동적 오도",
        evidence={"drifted": drifted, "measurable": measurable, "drift_ratio": round(drift_ratio, 3),
                  "ctx_validation": ctx_validation, "hook_validates": hook_validates},
        sub_scores=sub, findings=findings,
    )


def score_H(repo: Path) -> CategoryScore:
    """H. Feedback-Loop Latency & Quality /9 (Auto, 신규) — DevEx feedback loops(session-5 C6·C7)."""
    sub: dict[str, int] = {}
    # H1 pre-commit hook /3
    hook = any((repo / p).exists() for p in (".husky", ".pre-commit-config.yaml", "lefthook.yml", ".githooks"))
    sub["H1_PreCommit"] = 3 if hook else 0
    # H2 static type config /3
    tsconfig = repo / "tsconfig.json"
    strict_ts = tsconfig.exists() and '"strict"' in read_text(tsconfig)
    py_types = any(t in read_text(repo / "pyproject.toml") for t in ("mypy", "pyright")) if (repo / "pyproject.toml").exists() else False
    py_types = py_types or (repo / "mypy.ini").exists() or (repo / ".mypy.ini").exists()
    sub["H2_StaticTypes"] = (2 if strict_ts else (1 if tsconfig.exists() else 0)) + (1 if py_types else 0)
    sub["H2_StaticTypes"] = min(3, sub["H2_StaticTypes"])
    # H3 fast lint/format config /3
    lint_cfg = any((repo / p).exists() for p in (
        "ruff.toml", ".ruff.toml", "biome.json", ".eslintrc", ".eslintrc.json", ".eslintrc.js",
        "eslint.config.js", "eslint.config.mjs", ".prettierrc", "prettier.config.js",
    ))
    lint_in_pyproject = (repo / "pyproject.toml").exists() and "ruff" in read_text(repo / "pyproject.toml")
    sub["H3_FastLint"] = 3 if (lint_cfg or lint_in_pyproject) else 0
    pts = min(9, sum(sub.values()))
    findings: list[str] = []
    if not hook:
        findings.append("pre-commit hook 없음 — 위반이 PR 전까지 조용히 누적(빠른 피드백 부재)")
    if sub["H2_StaticTypes"] == 0:
        findings.append("static type 설정 없음 — 컴파일 앞단 피드백 부재")
    return CategoryScore(
        key="H", name="Feedback-Loop Latency & Quality", score=pts, max=9,
        label="Auto", evidence_grade="auto-med",
        basis="DevEx(Forsgren et al.)·Factory Agent Readiness: feedback loop 속도가 성숙도 축(근거 등급 Med)",
        evidence={"pre_commit": hook, "strict_ts": strict_ts, "lint_config": lint_cfg or lint_in_pyproject},
        sub_scores=sub, findings=findings,
    )


def score_I(repo: Path) -> CategoryScore:
    """I. Environment & Task-Discovery Reproducibility /5 (Auto, 신규) — session-5 C6·C7."""
    sub: dict[str, int] = {}
    env = any((repo / p).exists() for p in (
        ".devcontainer", ".devcontainer.json", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        ".env.example", ".env.sample", "setup.sh", "scripts/setup.sh", "Makefile",
    ))
    sub["I1_EnvRepro"] = 3 if env else 0
    task_disc = any((repo / p).exists() for p in (
        "CONTRIBUTING.md", ".github/ISSUE_TEMPLATE", ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE.md",
    ))
    sub["I2_TaskDiscovery"] = 2 if task_disc else 0
    pts = min(5, sum(sub.values()))
    findings: list[str] = []
    if not env:
        findings.append("devcontainer/.env.example/setup script 부재 — 독립 실행 환경 재현 어려움")
    return CategoryScore(
        key="I", name="Environment & Task-Discovery Reproducibility", score=pts, max=5,
        label="Auto", evidence_grade="auto-med",
        basis="Factory Agent Readiness / agent-readiness-score: Dev Environment·Task Discovery 축(근거 등급 Med)",
        evidence={"env_repro": env, "task_discovery": task_disc}, sub_scores=sub, findings=findings,
    )


def score_G(repo: Path) -> CategoryScore:
    """G. Agent Performance Outcomes /3 (Auto) — success ⁄ efficiency 분리(session-5 C5)."""
    eval_dirs = [p for p in ("evals", "benchmarks", "agent-evals", "agent-metrics") if (repo / p).exists()]
    # 단어 경계 필터: "retrieval.json"·"medieval.json" 같은 substring 과탐 방지
    metric_files = [m for m in (list(repo.glob("**/agent-results.json")) + list(repo.glob("**/*eval*.json")))
                    if not any(seg in m.parts for seg in IGNORE_DIRS)
                    and (m.name == "agent-results.json"
                         or re.search(r"(^|[-_.])evals?([-_.]|$)", m.stem))]
    efficiency_hint = any(
        re.search(r"telemetry|opentelemetry|token.*usage|cost.*per|latency|session.*log", read_text(p), re.IGNORECASE)
        for p in (repo / "CLAUDE.md", repo / "README.md", repo / "AGENTS.md") if p.exists()
    )
    sub = {
        "G1_SuccessTelemetry": min(2, (1 if eval_dirs else 0) + (1 if metric_files else 0)),
        "G2_EfficiencyTelemetry": 1 if efficiency_hint else 0,
    }
    pts = min(3, sum(sub.values()))
    findings: list[str] = []
    if not eval_dirs and not metric_files:
        findings.append("evals/benchmarks 부재 — task success 측정 인프라 없음")
    if not efficiency_hint:
        findings.append("cost/efficiency(token·latency) telemetry 단서 없음 — success와 efficiency는 별개 축(session-5 C5)")
    return CategoryScore(
        key="G", name="Agent Performance Outcomes (success ⁄ efficiency)", score=pts, max=3,
        label="Auto", evidence_grade="auto-med",
        basis="Lulla et al.(2601.20404): success와 efficiency는 독립적으로 움직임 → 분리 측정",
        evidence={"eval_dirs": eval_dirs, "metric_files": [str(p.relative_to(repo)) for p in metric_files[:5]],
                  "efficiency_hint": efficiency_hint},
        sub_scores=sub, findings=findings,
    )


# ----------------------------------------------------------------------------
# Grade + gating (session-5 C1·C8: blocking gate가 등급에 상한)
# ----------------------------------------------------------------------------
GRADE_BANDS = [
    (90, "AI-Native", "green"),
    (75, "AI-Ready", "green"),
    (60, "AI-Assisted", "amber"),
    (40, "AI-Fragile", "amber"),
    (0, "AI-Hostile", "red"),
]
GATE_CEILING_SCORE = 59  # gate 실패 시 등급 상한(AI-Fragile band의 최대)


def grade_from_score(total: int) -> tuple[str, str]:
    for thresh, label, color in GRADE_BANDS:
        if total >= thresh:
            return label, color
    return "AI-Hostile", "red"


def apply_gates(total: int, gates: list[Gate]) -> tuple[str, str, str, bool]:
    """gate 실패 시 등급에 상한을 씌운다. 반환 (grade, color, raw_grade, capped)."""
    raw_grade, raw_color = grade_from_score(total)
    if all(g.passed for g in gates):
        return raw_grade, raw_color, raw_grade, False
    capped_grade, capped_color = grade_from_score(min(total, GATE_CEILING_SCORE))
    return capped_grade, capped_color, raw_grade, capped_grade != raw_grade


# ----------------------------------------------------------------------------
# ROI actions
# ----------------------------------------------------------------------------
def derive_actions(cats: dict[str, CategoryScore], gates: list[Gate], refint: dict,
                   verif: dict, nodes: dict[str, GraphNode]) -> list[Action]:
    actions: list[Action] = []
    gate_map = {g.key: g for g in gates}

    # Gate-1 실패 — 최우선(등급 상한 해제)
    if not gate_map["reference-integrity"].passed:
        actions.append(Action(
            title=f"dangling reference {refint['dangling_total']}건 수정 (Gate-1 — 등급 상한 해제)",
            category="E", effort="S", effort_hours=0.5,
            impact="hallucinated path는 agent를 능동 오도 + 등급 상한 AI-Fragile을 씌움 — 수정 시 상한 해제",
            impact_score=10, priority=10 / 0.5, evidence_grade="auto-high",
        ))
    # Gate-2 실패
    if not gate_map["executable-verification"].passed:
        actions.append(Action(
            title="실행 가능한 test/build 명령·하네스 도입 (Gate-2 — 등급 상한 해제)",
            category="E", effort="M", effort_hours=3.0,
            impact="reproduction/test 신호는 성공률 최대 기여(+26~27pp, ORACLE-SWE) + 등급 상한 해제",
            impact_score=10, priority=10 / 3.0, evidence_grade="auto-high",
        ))
    # D — 기계 판독 그래프 약함. score_D의 finding 조건과 정렬한다 —
    # 파서 미지원 언어(parser_unsupported·neutral 처리)나 완전 파싱된 repo에는 발화하지 않는다
    # (분모는 total_code가 아니라 supported_code — 파서 한계를 대상 감점으로 전가하지 않기 위함).
    d = cats["D"]
    _sup = d.evidence.get("supported_code", 0)
    if (not d.evidence.get("parser_unsupported") and _sup
            and d.evidence.get("parseable_code", 0) / _sup < 0.5):
        actions.append(Action(
            title="의존 그래프를 기계 판독 가능하게 정리(명시 import·workspace 경계)",
            category="D", effort="M", effort_hours=2.5,
            impact="의존 그래프는 localization 정확도의 강한 예측자(LocAgent file-level 92.7%)",
            impact_score=7, priority=7 / 2.5, evidence_grade="auto-high",
        ))
    # D — 결합 hotspot
    hotspots = [n for n in nodes.values() if (n.fan_in + n.fan_out) >= COUPLING_HOTSPOT]
    if hotspots:
        top = sorted(hotspots, key=lambda n: -(n.fan_in + n.fan_out))[:2]
        actions.append(Action(
            title="결합 hotspot 분리(라인 수 아닌 fan-in/out): " + ", ".join(n.rel for n in top),
            category="D", effort="L", effort_hours=3.0 * len(top),
            impact="god-file은 결합도로 정의해야(라인 수 임계값은 agent용 근거 부재, session-4 C8)",
            impact_score=6, priority=6 / max(3.0, 3.0 * len(top)), evidence_grade="auto-med",
        ))
    # B — redundancy
    b = cats["B"]
    if b.evidence.get("avg_redundancy", 0) > 0.25 or b.evidence.get("over_long_prose", 0):
        actions.append(Action(
            title="context에서 README/코드 중복·산문 overview 제거 (compass-not-encyclopedia)",
            category="B", effort="M", effort_hours=2.0,
            impact="중복·overview는 순비용(추론 token +20%, ETH Zurich) — novelty·command만 남긴다",
            impact_score=7, priority=7 / 2.0, evidence_grade="heuristic-med",
        ))
    # A — anchor 부족
    if cats["A"].sub_scores.get("A2_Anchors", 0) < 3:
        actions.append(Action(
            title="핵심 module context에 진입점·의존 이웃(structure-first anchor) 명시",
            category="A", effort="S", effort_hours=1.0,
            impact="파일 노출이 아니라 구조 anchor가 navigation 레버(RepoMirage exploration drift)",
            impact_score=7, priority=7 / 1.0, evidence_grade="heuristic-med",
        ))
    # C — no store
    if not cats["C"].evidence.get("memory") and not cats["C"].evidence.get("adr"):
        actions.append(Action(
            title="MEMORY.md 또는 docs/adr/ 도입으로 비discoverable tribal knowledge 외부화",
            category="C", effort="M", effort_hours=3.0,
            impact="이득은 비자명·비discoverable 정보에서만(ETH Zurich C5)", impact_score=6,
            priority=6 / 3.0, evidence_grade="heuristic-med",
        ))
    # F — no validation
    f = cats["F"]
    if not f.evidence.get("ctx_validation") and not f.evidence.get("hook_validates"):
        actions.append(Action(
            title="CI/pre-commit에 path·reference validation 추가",
            category="F", effort="S", effort_hours=1.0,
            impact="stale reference를 머지 시점 차단(session-3 C6) + Gate-1 회귀 방지",
            impact_score=7, priority=7 / 1.0, evidence_grade="auto-med",
        ))
    # H — feedback
    if cats["H"].score < 5:
        actions.append(Action(
            title="pre-commit hook + static type + fast lint로 피드백 앞단화",
            category="H", effort="M", effort_hours=2.0,
            impact="위반을 컴파일/커밋 시점에 잡아 PR 전 조용한 누적 방지(DevEx feedback loop)",
            impact_score=6, priority=6 / 2.0, evidence_grade="auto-med",
        ))
    # G — no eval
    if cats["G"].score < 2:
        actions.append(Action(
            title="evals/ + task success·cost(token/latency) telemetry 분리 도입",
            category="G", effort="L", effort_hours=6.0,
            impact="success·efficiency를 분리 측정해 개선 ROI 정량화(session-5 C5)",
            impact_score=5, priority=5 / 6.0, evidence_grade="auto-med",
        ))

    actions.sort(key=lambda a: -a.priority)
    return actions


# ----------------------------------------------------------------------------
# Large files (보조 신호 — 근거 약함 라벨)
# ----------------------------------------------------------------------------
def find_large_files(nodes: dict[str, GraphNode]) -> list[dict[str, Any]]:
    out = [{"path": n.rel, "lines": n.lines, "fan_in": n.fan_in, "fan_out": n.fan_out,
            "coupling": n.fan_in + n.fan_out}
           for n in nodes.values() if n.lines > LARGE_FILE_LINES]
    out.sort(key=lambda x: -x["coupling"] * 1000 - x["lines"])  # 결합도 우선, 라인 수 보조
    return out[:30]


# ----------------------------------------------------------------------------
# Insights
# ----------------------------------------------------------------------------
def generate_insights(cats: dict[str, CategoryScore], total: int, grade: str, capped: bool,
                      raw_grade: str, gates: list[Gate]) -> list[str]:
    out = [f"총점 {total}/100 · 등급 {grade}" + (f" (gate 상한 적용 — 순수 점수로는 {raw_grade})" if capped else "")]
    for g in gates:
        if not g.passed:
            out.append(f"⛔ Gate 실패: {g.name} — {g.detail} (등급 상한)")
    norm = sorted(cats.values(), key=lambda c: c.score / c.max)
    for c in norm[:2]:
        out.append(f"최약 카테고리: {c.key} {c.name} {c.score}/{c.max} [{c.label}]")
    return out


# ----------------------------------------------------------------------------
# Build report
# ----------------------------------------------------------------------------
def git_branch(repo: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo), "rev-parse", "--abbrev-ref", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def build_report(repo: Path) -> Report:
    modules = find_core_modules(repo)
    context_files = find_all_context_files(repo)
    root_ctx = find_root_context(repo)
    nodes, parseable, total_code, supported_code = build_import_graph(repo)
    refint = check_reference_integrity(repo, context_files)
    verif = detect_verification(repo)

    gates = [
        Gate("reference-integrity", "Reference Integrity (dangling=0)", refint["passed"],
             f"dangling {refint['dangling_total']}건" if not refint["passed"] else "모든 인용 경로 실존"),
        Gate("executable-verification", "Executable Verification (runnable test/build)", verif["passed"],
             "실행 가능한 test/build 명령 미탐지" if not verif["passed"] else "실행 가능한 검증 명령 존재"),
    ]

    cats = {
        "E": score_E(repo, refint, verif, context_files),
        "D": score_D(repo, nodes, parseable, total_code, supported_code, context_files),
        "B": score_B(repo, context_files),
        "C": score_C(repo, modules),
        "H": score_H(repo),
        "A": score_A(repo, modules, context_files, root_ctx),
        "F": score_F(repo, modules, refint),
        "I": score_I(repo),
        "G": score_G(repo),
    }
    total = sum(c.score for c in cats.values())
    grade, color, raw_grade, capped = apply_gates(total, gates)
    actions = derive_actions(cats, gates, refint, verif, nodes)
    insights = generate_insights(cats, total, grade, capped, raw_grade, gates)
    large = find_large_files(nodes)

    return Report(
        meta={
            # 절대경로(사용자명 포함)는 repo 커밋 대상 산출물(docs/…json)에 유출되므로 넣지 않는다
            "repo": repo.name,
            "scored_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "git_branch": git_branch(repo), "rubric_version": "v3-100pt-gated",
            "modules_total": len(modules), "context_files_total": len(context_files),
            "code_files_total": total_code, "parseable_code_files": parseable,
            "coupling_hotspots": sum(1 for n in nodes.values() if (n.fan_in + n.fan_out) >= COUPLING_HOTSPOT),
            "dangling_refs": refint["dangling_total"],
        },
        total=total, grade=grade, grade_color=color, grade_capped=capped, raw_grade=raw_grade,
        gates=gates, categories=cats, insights=insights, actions=actions,
        extras={
            "modules": [{"rel": m.rel, "code_files": m.code_files, "has_context": m.has_context,
                         "context_kind": m.context_kind} for m in modules],
            "large_files": large,
            "gate_ceiling_note": "gate 실패 시 등급 상한 AI-Fragile — blocking 결함이 다른 고득점에 희석되지 않게(Kenogami lowest-as-ceiling)",
        },
    )


def serialize(report: Report) -> dict[str, Any]:
    return {
        "meta": report.meta, "total": report.total, "grade": report.grade,
        "grade_color": report.grade_color, "grade_capped": report.grade_capped,
        "raw_grade": report.raw_grade,
        "gates": [asdict(g) for g in report.gates],
        "categories": {k: asdict(c) for k, c in report.categories.items()},
        "insights": report.insights, "actions": [asdict(a) for a in report.actions],
        "extras": report.extras,
    }


def html_escape_deep(value: Any) -> Any:
    """모든 문자열 값을 재귀 html.escape — template.html 채움은 이 사본(*.htmlsafe.json)만 사용.

    브랜치명·파일 경로·findings에 저장소 유래 텍스트가 들어가므로, 대시보드 XSS 차단을
    LLM 지침이 아니라 결정론 코드로 강제한다.
    """
    if isinstance(value, str):
        return html.escape(value, quote=True)
    if isinstance(value, list):
        return [html_escape_deep(v) for v in value]
    if isinstance(value, tuple):
        return tuple(html_escape_deep(v) for v in value)
    if isinstance(value, dict):
        return {html_escape_deep(k): html_escape_deep(v) for k, v in value.items()}
    return value


def render_markdown(report: Report) -> str:
    L: list[str] = []
    L.append(f"# AI-Readiness Audit · {report.meta['repo']} (v3 gated)")
    L.append("")
    cap = f" — gate 상한 적용(순수 점수 등급: {report.raw_grade})" if report.grade_capped else ""
    L.append(f"**Score:** {report.total}/100 · **Grade:** {report.grade}{cap}")
    L.append(f"**Branch:** `{report.meta['git_branch']}` · **Scored:** {report.meta['scored_at']} · rubric {report.meta['rubric_version']}")
    L.append(f"**Modules:** {report.meta['modules_total']} · **Context files:** {report.meta['context_files_total']} · "
             f"**Code files:** {report.meta['code_files_total']}(parseable {report.meta['parseable_code_files']}) · "
             f"**Coupling hotspots:** {report.meta['coupling_hotspots']} · **Dangling refs:** {report.meta['dangling_refs']}")
    L.append("")
    L.append("## Gates (blocking — 실패 시 등급 상한)")
    for g in report.gates:
        L.append(f"- {'✅' if g.passed else '⛔'} **{g.name}** — {g.detail}")
    L.append("")
    L.append("## Category Scores")
    L.append("")
    L.append("| Cat | Name | Score | Label | Evidence |")
    L.append("|-----|------|-------|-------|----------|")
    for k in ("E", "D", "B", "C", "H", "A", "F", "I", "G"):
        c = report.categories[k]
        L.append(f"| {k} | {c.name} | **{c.score}/{c.max}** | {c.label} | {c.evidence_grade} |")
    L.append("")
    L.append("## Insights")
    for i in report.insights:
        L.append(f"- {i}")
    L.append("")
    L.append("## Findings (per category)")
    for k in ("E", "D", "B", "C", "H", "A", "F", "I", "G"):
        c = report.categories[k]
        if not c.findings:
            continue
        L.append(f"### {k}. {c.name} ({c.score}/{c.max}) · {c.label}")
        L.append(f"> 근거: {c.basis}")
        for f in c.findings:
            L.append(f"- {f}")
    L.append("")
    L.append("## Top Actions (ROI 정렬)")
    L.append("")
    L.append("| # | Effort | Action | Impact | Evidence |")
    L.append("|---|--------|--------|--------|----------|")
    for i, a in enumerate(report.actions[:10], 1):
        L.append(f"| {i} | {a.effort} ({a.effort_hours:.1f}h) | [{a.category}] {a.title} | {a.impact} | {a.evidence_grade} |")
    L.append("")
    if report.extras["large_files"]:
        L.append("## Large / Coupled Files (결합도 우선 · 라인 수는 보조·근거 약함)")
        for lf in report.extras["large_files"][:10]:
            L.append(f"- {lf['path']} — {lf['lines']} lines · coupling {lf['coupling']}(in{lf['fan_in']}/out{lf['fan_out']})")
        L.append("")
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("repo", nargs="?", default=".", help="repo path (default: cwd)")
    p.add_argument("--json", dest="json_out", help="write JSON report to this path")
    p.add_argument("--markdown", action="store_true", help="emit markdown to stdout (default)")
    p.add_argument("--quiet", action="store_true", help="suppress stdout output")
    args = p.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"error: repo path not found: {repo}", file=sys.stderr)
        return 2

    try:
        report = build_report(repo)
    except Exception as e:  # 적대적/비정형 저장소에서 traceback 대신 정돈된 실패
        print(f"error: scoring failed for {repo.name}: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    payload = serialize(report)
    if args.json_out:
        out_path = Path(args.json_out)
        try:
            if out_path.parent and str(out_path.parent) not in (".", ""):
                out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            # HTML 대시보드 채움 전용 이스케이프 사본
            safe_path = out_path.with_name(out_path.stem + ".htmlsafe.json")
            safe_path.write_text(json.dumps(html_escape_deep(payload), indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as e:
            print(f"error: cannot write JSON to {out_path}: {e}", file=sys.stderr)
            return 2
    if not args.quiet:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
