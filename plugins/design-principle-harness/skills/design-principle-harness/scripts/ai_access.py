#!/usr/bin/env python3
"""AI Accessibility Assessor — 에이전트가 코드베이스를 읽고 안전하게 수정하기 쉬운가를
결정론적으로 측정하는 stdlib-only 스코어러(design-principle-harness 트랙 B).

정직성(근거: references/research/ai-accessibility-dossier.md):
  - "build enforces, docs explain": 기계 검증 가능 속성(강제된 의존 방향·실행 가능 테스트)이
    산문 문서보다 신뢰도 높은 신호다. 그래서 그 둘만 SCORED, 나머지는 REPORT-ONLY.
  - intervention ≠ correlation: 6지표 중 대부분의 '에이전트 이득'은 측정된 개입이 아니라
    인간-SE 이득 + 첫 원리로부터의 추론이다 → 점수 driver로 승격하지 않는다.
  - tool-index ≠ code-structure: LocAgent(92.7%)·RepoGraph(+32.8%) 같은 툴 이득을
    저장소 layout/구조의 공로로 귀속하지 않는다.
  - 유일하게 '측정된 agent-specific 레버'는 독립 oracle(에이전트 저작 테스트와 구별): 격리-green
    테스트가 실제 정답이 아닌 경우가 실패의 81~100%(arXiv:2606.26978) → runnability + 독립-oracle 가드만 SCORED.
  - 측정만 한다(코드 수정 없음). 개선(가드레일 추가·가이드 작성)은 SKILL 트랙 B에서 승인 게이트 뒤에만.

Python 3.10+ · stdlib only. `python3 ai_access.py <repo> [--json OUT] [--markdown]`
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------------
IGNORE_DIRS = {
    "node_modules", ".git", "dist", "build", "out", ".next", ".nuxt", "coverage",
    "__pycache__", ".venv", "venv", "vendor", ".turbo", ".cache", "target", ".idea",
    ".mypy_cache", ".pytest_cache", "__snapshots__", ".gradle",
}
MAX_READ_BYTES = 2_000_000
MAX_FILES = 20_000
JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
PY_EXTS = {".py"}

# --- 의존 방향 강제(M1) 설정 파일/시그니처 -----------------------------------
DEPCRUISER_FILES = {".dependency-cruiser.js", ".dependency-cruiser.cjs",
                    ".dependency-cruiser.json", ".dependency-cruiser.mjs", "dependency-cruiser.config.js"}
IMPORTLINTER_FILES = {".importlinter"}
RE_ESLINT_BOUNDARY = re.compile(r"boundaries/|eslint-plugin-boundaries|no-restricted-imports|no-restricted-paths|import/no-restricted-paths")
RE_NX_BOUNDARY = re.compile(r"enforce-module-boundaries|@nx/enforce-module-boundaries|depConstraints")
RE_ARCHUNIT = re.compile(r"\bArchUnit|com\.tngtech\.archunit|archunit|ArchRuleDefinition|slices\(\)")
RE_IMPORTLINTER_CFG = re.compile(r"\[importlinter\]|\[tool\.importlinter\]|importlinter\.contracts")

RE_TS_STRICT = re.compile(r'"strict"\s*:\s*true')
RE_TS_STRICT_SUB = re.compile(r'"(noImplicitAny|strictNullChecks|noUncheckedIndexedAccess|noImplicitReturns)"\s*:\s*true')
RE_TS_REFERENCES = re.compile(r'"references"\s*:\s*\[')

# 테스트 러너(M2/M5)
RUNNER_SIGNATURES = {
    "jest": re.compile(r'"jest"|jest\.config|from ["\']@jest|jest\.setup'),
    "vitest": re.compile(r"vitest|vite\.config.*test|defineConfig.*test"),
    "mocha": re.compile(r'"mocha"|\.mocharc'),
    "pytest": re.compile(r"\[tool\.pytest|\[pytest\]|pytest\.ini|conftest\.py"),
    "playwright": re.compile(r"@playwright/test|playwright\.config"),
    "go-test": re.compile(r"_test\.go"),
}
RE_TEST_FILE = re.compile(r"(\.test\.|\.spec\.|(^|/)test_[^/]+\.py$|_test\.py$|(^|/)__tests__/|(^|/)tests?/)")

# 에이전트 가이드(M6)
AGENT_GUIDE_FILES = {
    "CLAUDE.md": "CLAUDE.md", "AGENTS.md": "AGENTS.md", "AGENT.md": "AGENT.md",
    ".cursorrules": ".cursorrules", "llms.txt": "llms.txt", ".windsurfrules": ".windsurfrules",
    "GEMINI.md": "GEMINI.md", ".github/copilot-instructions.md": "copilot-instructions.md",
}
# non-inferable(코드로 알 수 없는) 내용 신호 — build/test/env 명령·경계·규약
RE_NONINFERABLE = re.compile(
    r"```|npm run |pnpm |yarn |make |bazel |cargo |go test|pytest|npx |docker |"
    r"env |export |PORT|경계|boundary|architecture|아키텍처|의존|convention|규약|"
    r"do not|하지 ?마|never |always |must ", re.IGNORECASE)

CI_DIRS = [".github/workflows", ".gitlab-ci.yml", ".circleci", "azure-pipelines.yml",
           "Jenkinsfile", ".buildkite", "bitbucket-pipelines.yml"]

RE_JS_IMPORT = re.compile(
    r"""(?:import\s[^'"\n]{0,300}from\s*|require\(\s*|import\(\s*|export\s[^'"\n]{0,120}from\s*)['"]([^'"\n]{1,300})['"]""")
RE_JS_REQUIRE = re.compile(r"\brequire\s*\(")
RE_JS_ESM = re.compile(r"^\s*(?:import\s|export\s)", re.MULTILINE)


# ----------------------------------------------------------------------------
@dataclass
class Metric:
    key: str
    name: str
    scored: bool                 # True=결정론적 사실이라 점수, False=report-only
    score: int
    max: int
    confidence: str              # STRONG | MEDIUM | WEAK | QUALITATIVE | report-only
    agent_evidence: str          # measured | inferred | mixed  (에이전트 이득이 측정됐나)
    findings: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class Assessment:
    meta: dict[str, Any]
    enforced_score: int          # SCORED 지표만의 소계(인증 아님)
    enforced_max: int
    metrics: list[Metric]
    honesty: list[str]
    improvement_candidates: list[str]


# ----------------------------------------------------------------------------
def _safe(p: Path) -> bool:
    try:
        if p.is_symlink() or not p.is_file():
            return False
        return p.stat().st_size <= MAX_READ_BYTES
    except OSError:
        return False


def read_text(p: Path) -> str:
    if not _safe(p):
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return ""


def walk_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".") or d in {".github"}]
        for f in files:
            p = Path(r) / f
            if not p.is_symlink():
                out.append(p)
                if len(out) >= MAX_FILES:
                    return out
    return out


def rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return p.name


def exists_any(root: Path, names: set[str]) -> list[str]:
    found = []
    for n in names:
        if (root / n).exists():
            found.append(n)
    return found


def read_package_json(root: Path) -> dict[str, Any]:
    p = root / "package.json"
    if not p.exists():
        return {}
    try:
        return json.loads(read_text(p) or "{}")
    except (json.JSONDecodeError, ValueError):
        return {}


# ----------------------------------------------------------------------------
# M1 — dependency-direction-enforcement (SCORED · Gate)
# ----------------------------------------------------------------------------
def detect_dep_enforcement(root: Path, files: list[Path], pkg: dict) -> Metric:
    MAXP = 10
    tools: list[str] = []
    # dependency-cruiser
    if exists_any(root, DEPCRUISER_FILES):
        tools.append("dependency-cruiser")
    # import-linter (py)
    if exists_any(root, IMPORTLINTER_FILES):
        tools.append("import-linter")
    for cfg in ("setup.cfg", "pyproject.toml", "tox.ini"):
        t = read_text(root / cfg)
        if t and RE_IMPORTLINTER_CFG.search(t):
            tools.append("import-linter")
            break
    # eslint boundaries / no-restricted-imports
    eslint_names = {".eslintrc", ".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json",
                    ".eslintrc.yml", ".eslintrc.yaml", "eslint.config.js", "eslint.config.mjs", "eslint.config.cjs"}
    for n in eslint_names:
        t = read_text(root / n)
        if t and RE_ESLINT_BOUNDARY.search(t):
            tools.append("eslint-boundaries")
            break
    # nx module boundaries
    for n in ("nx.json", ".eslintrc.json", "eslint.config.js"):
        t = read_text(root / n)
        if t and RE_NX_BOUNDARY.search(t):
            tools.append("nx-boundaries")
            break
    # tsconfig project references
    ts = read_text(root / "tsconfig.json")
    if ts and RE_TS_REFERENCES.search(ts):
        tools.append("ts-project-references")
    # ArchUnit (java/kotlin/csharp test files)
    for p in files[:MAX_FILES]:
        if p.suffix in {".java", ".kt", ".cs"}:
            t = read_text(p)
            if t and RE_ARCHUNIT.search(t):
                tools.append("ArchUnit")
                break
    tools = sorted(set(tools))
    # CI가 실제로 강제를 돌리는가(가드레일이 pre-commit/CI에서 fail하는가)
    ci = detect_ci(root)
    findings: list[str] = []
    if tools:
        score = min(MAXP, 6 + 2 * (len(tools) >= 2) + 2 * bool(ci))
        findings.append(f"의존 방향 강제 tooling {tools} — 금지 import를 빌드/CI에서 물리 차단하는 결정론 신호(build enforces).")
        if not ci:
            findings.append("⚠️ 강제 설정은 있으나 CI 실행 흔적 미검출 — 설정이 실제로 pre-commit/CI에서 nonzero-exit로 fail하는지 확인 필요(설정 존재≠실제 강제).")
    else:
        score = 0
        findings.append("의존 방향 강제 tooling 미검출 — dependency-cruiser·eslint-boundaries·import-linter·ArchUnit·Nx·TS project refs 없음. **개선 후보**(승인 후 가드레일 추가).")
    findings.append("↳ 에이전트 이득은 **추론**(inferred): 강제가 에이전트 아키텍처 위반율을 낮춘다는 통제 개입 연구는 없다(human-SE·tooling 근거 + 첫 원리). 존재·실제 fail만 사실로 점수, 규칙 수/모듈 수는 가점 안 함.")
    return Metric(
        "M1", "의존성 방향 강제 (dependency-direction-enforcement)", True, score, MAXP,
        "STRONG" if tools else "report-only", "inferred",
        findings, {"tools": tools, "ci_present": bool(ci)})


def detect_ci(root: Path) -> list[str]:
    found = []
    wf = root / ".github" / "workflows"
    if wf.is_dir():
        try:
            if any(wf.iterdir()):
                found.append(".github/workflows")
        except OSError:
            pass
    for c in CI_DIRS[1:]:
        if (root / c).exists():
            found.append(c)
    return found


# ----------------------------------------------------------------------------
# M2 — standalone-verifiability (SCORED gate + report-only modularity)
# ----------------------------------------------------------------------------
def detect_standalone(root: Path, files: list[Path], pkg: dict) -> Metric:
    MAXP = 10
    runners: set[str] = set()
    test_files = 0
    # runner config / signatures
    scripts = (pkg.get("scripts") or {}) if isinstance(pkg, dict) else {}
    haystacks = [read_text(root / n) for n in
                 ("package.json", "pyproject.toml", "setup.cfg", "pytest.ini", "vitest.config.ts",
                  "vitest.config.js", "jest.config.js", "jest.config.ts", ".mocharc.json")]
    hay = "\n".join(h for h in haystacks if h)
    for name, rx in RUNNER_SIGNATURES.items():
        if rx.search(hay):
            runners.add(name)
    for p in files:
        if RE_TEST_FILE.search("/" + rel(p, root)):
            test_files += 1
        if p.name == "conftest.py":
            runners.add("pytest")
        if p.suffix == ".go" and p.name.endswith("_test.go"):
            runners.add("go-test")
    # buildability / entrypoints
    build_script = bool(re.search(r'"build"\s*:', json.dumps(scripts)))
    has_test_script = bool(re.search(r'"test"\s*:', json.dumps(scripts)))
    # workspaces / monorepo(부분을 독립 실행 가능)
    workspaces = bool(pkg.get("workspaces")) or (root / "pnpm-workspace.yaml").exists() or (root / "nx.json").exists() or (root / "turbo.json").exists()
    runnable = bool(runners) and (build_script or has_test_script or test_files > 0)
    findings: list[str] = []
    score = 0
    if runners:
        score += 5
        findings.append(f"테스트 러너 {sorted(runners)} · 테스트 파일 {test_files}건 — 부분을 전체 없이 검증할 실행 기질(runnable/buildable).")
    else:
        findings.append("테스트 러너 미검출 — 부분 검증 수단 불명. **개선 후보**(러너·격리 테스트 도입은 승인 후).")
    if build_script or has_test_script:
        score += 2
    if workspaces:
        score += 3
        findings.append("workspace/monorepo 구성 — 패키지를 독립적으로 build/test 가능(부분 검증 용이).")
    score = min(MAXP, score)
    findings.append("⚠️ **독립 oracle 가드(핵심·유일하게 측정된 agent-specific 레버)**: 에이전트가 *스스로 작성/선택한* 테스트가 green이어도 실제 정답이 아닐 수 있다 — 실패의 81~100%가 self-validated green(arXiv:2606.26978). 개선/검증은 **에이전트 저작과 구별되는 독립 ground-truth oracle**로 확인(‘격리-green=correct’로 credit 금지).")
    findings.append("↳ '실행 가능(gate)'은 측정 레버지만, **fine-grained modularity/DI/ports-adapters → 에이전트 self-verify 향상**은 CI/human best-practice에서의 **추론**(agent 개입 미검증). mock 남용은 격리-green·통합-fail blind spot.")
    return Metric(
        "M2", "독립 실행 가능성 (standalone-verifiability)", True, score, MAXP,
        "MEDIUM" if runners else "report-only", "mixed",
        findings, {"runners": sorted(runners), "test_files": test_files,
                   "workspaces": workspaces, "build_script": build_script})


# ----------------------------------------------------------------------------
# M3 — build-type-feedback (REPORT-ONLY · 저가중)
# ----------------------------------------------------------------------------
def detect_build_feedback(root: Path, pkg: dict) -> Metric:
    MAXP = 6
    signals: list[str] = []
    ts = read_text(root / "tsconfig.json") or read_text(root / "tsconfig.base.json")
    strict = bool(ts and (RE_TS_STRICT.search(ts) or RE_TS_STRICT_SUB.search(ts)))
    scripts = json.dumps((pkg.get("scripts") or {}) if isinstance(pkg, dict) else {})
    typecheck = bool(re.search(r"tsc\s+--noEmit|\"typecheck\"|\"type-check\"|mypy|pyright", scripts) or
                     (root / "mypy.ini").exists() or "mypy" in (read_text(root / "pyproject.toml") or ""))
    lint = bool(re.search(r"\"lint\"|eslint|ruff|flake8", scripts) or exists_any(root, {".eslintrc", ".eslintrc.js", ".eslintrc.json", "ruff.toml", ".flake8"}))
    ci = detect_ci(root)
    if strict:
        signals.append("TS strict 타입")
    if typecheck:
        signals.append("typecheck 스크립트/설정")
    if lint:
        signals.append("lint 설정")
    if ci:
        signals.append("CI")
    score = min(MAXP, len(signals) * 2)
    findings = [f"빌드/타입 피드백 신호: {signals or '없음'}."]
    findings.append("↳ **report-only·저가중**: '정밀·조기 진단이 self-repair를 돕는다'는 task-level MEDIUM 근거(2306.09896·2602.11481)이나, '주어진 repo에 strong typing이 에이전트 editability를 높인다'는 **repo-level 개입 부재(WEAK·추론)**. **테스트/컴파일 통과를 correctness로 credit 금지**(에이전트가 해킹할 바로 그 oracle·ImpossibleBench 76% exploit) — tamper-resistance(hidden/read-only 테스트)는 별도 확인.")
    return Metric(
        "M3", "빌드 피드백 품질 (build-type-feedback)", False, score, MAXP,
        "report-only", "inferred", findings,
        {"ts_strict": strict, "typecheck": typecheck, "lint": lint, "ci": bool(ci)})


# ----------------------------------------------------------------------------
# M4 — module-boundary-predictability (REPORT-ONLY)
# ----------------------------------------------------------------------------
CONVENTIONAL_DIRS = {"components", "services", "utils", "lib", "hooks", "models", "controllers",
                     "routes", "api", "pages", "features", "modules", "domain", "core", "shared",
                     "types", "config", "middleware", "store", "context", "helpers", "adapters", "ports"}


def detect_module_predictability(root: Path, files: list[Path]) -> Metric:
    MAXP = 6
    dirs: dict[str, int] = {}
    depths: list[int] = []
    code = [p for p in files if p.suffix in (JS_EXTS | PY_EXTS)]
    src_root = root / "src" if (root / "src").is_dir() else root
    for p in code:
        r = rel(p, src_root) if str(p).startswith(str(src_root)) else rel(p, root)
        parts = Path(r).parts
        if len(parts) > 1:
            dirs[parts[0].lower()] = dirs.get(parts[0].lower(), 0) + 1
            depths.append(len(parts))
    conventional = sorted(d for d in dirs if d in CONVENTIONAL_DIRS)
    depth_var = (max(depths) - min(depths)) if depths else 0
    findings = []
    score = 0
    if conventional:
        score += min(4, len(conventional))
        findings.append(f"관례적 디렉터리 택소노미: {conventional} — 에이전트가 '어디에 코드를 놓을지' 추론 단서.")
    else:
        findings.append("관례적 디렉터리 택소노미 약함 — 모듈 경계 예측 단서 부족(개선 후보).")
    if depths and depth_var <= 3:
        score += 2
    score = min(MAXP, score)
    findings.append(f"[report-only] 디렉터리 {len(dirs)}종·깊이 편차 {depth_var}.")
    findings.append("↳ **report-only**: code localization은 확립된 어려운 병목(STRONG)이나, 그 이득은 **툴 그래프 인덱스**(LocAgent 92.7%·RepoGraph +32.8%)의 것이지 **layout 자체가 인과 레버라는 근거는 WEAK**(고정 에이전트에 layout 통제 개입 연구 0). tool 효과를 layout에 귀속 금지·over-fragmentation은 오히려 해로울 수 있음.")
    return Metric(
        "M4", "모듈 경계 예측 가능성 (module-boundary-predictability)", False, score, MAXP,
        "report-only", "inferred", findings,
        {"conventional_dirs": conventional, "dir_kinds": len(dirs), "depth_variance": depth_var})


# ----------------------------------------------------------------------------
# M5 — pattern-consistency (report-only · naming은 코드품질 트랙 A1/A2와 상보)
# ----------------------------------------------------------------------------
def detect_pattern_consistency(root: Path, files: list[Path]) -> Metric:
    MAXP = 6
    esm = cjs = 0
    for p in files:
        if p.suffix in JS_EXTS:
            t = read_text(p)
            if not t:
                continue
            if RE_JS_ESM.search(t):
                esm += 1
            if RE_JS_REQUIRE.search(t):
                cjs += 1
    total_js = esm + cjs
    mixed_modules = total_js > 0 and min(esm, cjs) / max(1, total_js) > 0.15
    findings = []
    score = MAXP
    if mixed_modules:
        score -= 3
        findings.append(f"모듈 시스템 혼용(ESM {esm} / require {cjs}) — 같은 종류 문제를 다른 방식으로 푸는 비일관 신호(에이전트에 모호).")
    else:
        findings.append("모듈 시스템 일관 — 같은 문제를 같은 방식으로.")
    findings.append("[report-only] 식별자 단위 naming 품질/일관성은 **코드 품질 트랙 A1/A2**가 담당(2510.03178: 오도·난독 식별자가 LLM 이해를 -11~-29pt 저하). 여기선 cross-file 패턴 일관성만 접선 신호로 본다.")
    findings.append("↳ **report-only**: '내부 일관성을 높이면 같은 에이전트가 더 잘 확장한다'는 **mechanism-inferred**(RepoCoder retrieval)이지 통제 개입 아님. uniformity 자체가 아니라 *의미 있는* 일관성만·misleading-but-consistent가 최악.")
    return Metric(
        "M5", "패턴 일관성 (pattern-consistency)", False, score, MAXP,
        "report-only", "inferred", findings,
        {"esm_files": esm, "cjs_files": cjs, "mixed_module_systems": mixed_modules})


# ----------------------------------------------------------------------------
# M6 — agent-guides-context (REPORT-ONLY · 약)
# ----------------------------------------------------------------------------
def detect_agent_guides(root: Path) -> Metric:
    MAXP = 4
    present: list[str] = []
    non_inferable = 0
    bloat = 0
    for path, label in AGENT_GUIDE_FILES.items():
        p = root / path
        t = read_text(p)
        if t:
            present.append(label)
            lines = t.splitlines()
            non_inferable += len(RE_NONINFERABLE.findall(t))
            if len(lines) > 400:
                bloat += 1
    findings = []
    score = 0
    if present:
        # 존재는 약한 신호. non-inferable 내용 밀도에만 cap된 소점수.
        score = min(MAXP, 1 + min(3, non_inferable // 3))
        findings.append(f"에이전트 가이드 {present} — 빌드가 강제 못하는 설계 의도 문서화 후보. non-inferable(빌드/테스트/env 명령·경계·규약) 신호 {non_inferable}건.")
        if bloat:
            score = max(0, score - bloat)
            findings.append(f"⚠️ 비대(400줄+) 가이드 {bloat}건 — bloat는 adherence를 저하(Anthropic: 'Bloated CLAUDE.md files cause Claude to ignore your actual instructions'). 감점.")
    else:
        findings.append("CLAUDE.md/AGENTS.md 등 에이전트 가이드 없음 — 빌드로 못 잡는 설계 의도가 문서화 안 됨(**개선 후보**·단 자동 생성 금지).")
    findings.append("↳ **report-only(약)**: 유일한 통제 개입(arXiv:2602.11988)은 context 파일이 성공을 **높이지 않고** LLM-생성본은 5/8에서 낮췄다 — **presence ≠ performance**(STRONG). 점수는 *non-inferable·build-checkable 내용*에만·cap. **자동 생성 금지**·bloat/staleness 감점·'이 줄 지우면 실수 나나?' 밀도만 보상.")
    return Metric(
        "M6", "에이전트 가이드 문서화 (agent-guides-context)", False, score, MAXP,
        "report-only", "measured (presence≠performance)", findings,
        {"guides": present, "non_inferable_signals": non_inferable, "bloat_files": bloat})


# ----------------------------------------------------------------------------
def build_assessment(root: Path) -> Assessment:
    files = walk_files(root)
    pkg = read_package_json(root)
    metrics = [
        detect_dep_enforcement(root, files, pkg),
        detect_standalone(root, files, pkg),
        detect_build_feedback(root, pkg),
        detect_module_predictability(root, files),
        detect_pattern_consistency(root, files),
        detect_agent_guides(root),
    ]
    scored = [m for m in metrics if m.scored]
    enforced_score = sum(m.score for m in scored)
    enforced_max = sum(m.max for m in scored)
    candidates = []
    for m in metrics:
        for f in m.findings:
            if "개선 후보" in f:
                candidates.append(f"{m.key} {m.name}: {f.split('—')[0].strip()}")
    meta = {
        "tool": "design-principle-harness/ai_access.py",
        "version": "0.1.0",
        "repo": str(root.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(files),
    }
    honesty = [
        "이 assessment는 '에이전트 성공률 인증'이 아니다. **6지표 중 5개의 '에이전트 이득'은 측정된 개입이 아니라 인간-SE 이득+첫 원리로부터의 추론**이다(intervention≠correlation). 그래서 SCORED는 '기계 검증 가능한 사실'(의존 방향 강제 존재·실제 CI fail / 독립 실행 가능 gate)뿐이고 나머지는 REPORT-ONLY.",
        "**build enforces, docs explain**: 강제된 의존 방향·실행 테스트 같은 기계 검증 신호가 산문 문서보다 신뢰도 높다. 에이전트 가이드 '존재'는 성능 예측자가 아니다(arXiv:2602.11988: context 파일이 성공을 안 높이고 LLM-생성본은 낮춤).",
        "**tool-index ≠ code-structure**: LocAgent(92.7%)·RepoGraph(+32.8%) 같은 localization 이득은 코드 위에 얹은 그래프 인덱스(tooling)의 것이지 저장소 layout의 공로가 아니다 — 등급에 귀속 금지.",
        "**유일하게 측정된 agent-specific 레버는 독립 oracle**: 에이전트 저작 테스트의 격리-green이 실제 정답이 아닌 경우가 실패의 81~100%(arXiv:2606.26978) → runnability + 독립 ground-truth oracle만 신뢰, '격리-green=correct' credit 금지.",
        "**Goodhart**: 규칙 수·모듈 수·문서 줄 수를 보상하지 않는다(존재·정확성·의미만). enforcement/리팩터 credit은 behavior·readability 센서와 짝짓는다. **에이전트 가이드 자동 생성 금지**.",
        "측정만 수행(코드·설정 수정 없음). 개선(가드레일 추가·가이드 작성)은 SKILL 트랙 B에서 계획→개별→최종 승인 게이트 뒤에만·커밋 안 함.",
    ]
    return Assessment(meta, enforced_score, enforced_max, metrics, honesty, candidates)


# ----------------------------------------------------------------------------
def to_dict(a: Assessment) -> dict[str, Any]:
    return asdict(a)


def render_markdown(a: Assessment) -> str:
    L: list[str] = []
    L.append(f"# AI 접근성 assessment — build-enforced 사실 {a.enforced_score}/{a.enforced_max}")
    L.append("")
    L.append("> ⚠️ 이것은 **에이전트 성공률 인증이 아니다**. SCORED는 기계 검증 가능한 사실(의존 방향 강제·독립 실행 가능)뿐이고, "
             "나머지 지표의 '에이전트 이득'은 **측정된 개입이 아니라 추론**이라 REPORT-ONLY입니다.")
    L.append("")
    L.append("## 지표별")
    L.append("")
    L.append("| # | 지표 | 유형 | 점수 | 신뢰(에이전트 이득) | 근거 |")
    L.append("|---|------|------|------|--------------------|------|")
    for m in a.metrics:
        typ = "**SCORED**" if m.scored else "report-only"
        sc = f"{m.score}/{m.max}" if m.scored else f"({m.score}/{m.max})"
        L.append(f"| {m.key} | {m.name} | {typ} | {sc} | {m.confidence} | {m.agent_evidence} |")
    L.append("")
    for m in a.metrics:
        L.append(f"### {m.key} · {m.name}  —  {m.score}/{m.max} [{'SCORED' if m.scored else 'report-only'} · {m.confidence}]")
        for f in m.findings:
            L.append(f"- {f}")
        L.append("")
    if a.improvement_candidates:
        L.append("## 개선 후보 (승인 게이트 뒤에만·트랙 B Step 2)")
        for c in a.improvement_candidates:
            L.append(f"- {c}")
        L.append("")
    L.append("## 정직성")
    for h in a.honesty:
        L.append(f"- {h}")
    L.append("")
    L.append("---")
    L.append(f"_{a.meta['tool']} v{a.meta['version']} · 파일 {a.meta['files_scanned']} · 측정만(수정 없음)._")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AI Accessibility 결정론 assessor")
    ap.add_argument("repo", nargs="?", default=".", help="스캔할 저장소 경로(기본: .)")
    ap.add_argument("--json", metavar="OUT", help="JSON 출력('-'=stdout)")
    ap.add_argument("--markdown", action="store_true", help="markdown 출력(기본)")
    args = ap.parse_args(argv)
    root = Path(args.repo)
    if not root.exists() or not root.is_dir():
        print(f"error: {root} 는 디렉터리가 아닙니다", file=sys.stderr)
        return 2
    try:
        a = build_assessment(root)
    except Exception as exc:  # noqa: BLE001 — 신뢰 불가 repo에서 부분 실패해도 죽지 않게
        print(f"error: 스캔 실패 — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if args.json:
        payload = json.dumps(to_dict(a), ensure_ascii=False, indent=2)
        if args.json == "-":
            print(payload)
        else:
            outp = Path(args.json)
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(payload, encoding="utf-8")
            print(f"[ai_access] JSON → {outp}", file=sys.stderr)
    if not args.json or args.markdown:
        print(render_markdown(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
