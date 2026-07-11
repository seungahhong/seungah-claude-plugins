#!/usr/bin/env python3
"""legibility_scan.py — 코드 *본문* 층위 AI 가독성 census (결정론적 스캐너).

이 스크립트는 **등급을 매기지 않는다.** 점수·백분율·합격/불합격을 내지 않는다.
이 플러그인의 **측정 모드(score.py)** 가 저장소 층 등급(0~100·5밴드)을 내며(본문 층은 census만),
코드 본문 층위의 "몇 점" 을 정당화할 1차 근거는 존재하지 않는다(근거 dossier O-1/O-3).

대신 **census(인벤토리) + 개입 후보 목록**을 낸다. 각 탐지기에는 근거 등급 라벨이 붙는다:

    auto-high    AST/토크나이저로 결정론적으로 판정. 거짓양성이 구조적으로 낮다.
    auto-med     결정론적으로 *후보*를 뽑되 사람/LLM 확인이 필요하다.
    heuristic    근거가 약하거나 없다. 진단 정보로만 쓴다.
    report-only  판정하지 않는다. 목록만 제공한다.

stdlib only · Python 3.10+ · 코드를 수정하지 않는다(읽기 전용).

사용:
    python3 legibility_scan.py <repo_root> [--out census.json]
                               [--axes naming,comments,structure]
                               [--git-drift] [--drift-days 90]
                               [--top 20] [--max-files 5000]
"""

from __future__ import annotations

import argparse
import ast
import builtins
import io
import json
import keyword
import os
import re
import subprocess
import sys
import tokenize
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

SCHEMA_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# 안전 한계 (신뢰할 수 없는 저장소를 스캔한다는 전제)
# ---------------------------------------------------------------------------
MAX_FILE_BYTES = 1_000_000       # 초과 시 스킵. "0줄"로 오독하지 않는다.
MAX_FILES_DEFAULT = 5_000
GIT_TIMEOUT_SEC = 15

SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "out",
    ".venv", "venv", "env", "__pycache__", ".next", ".nuxt", ".turbo",
    "target", "vendor", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "coverage", "htmlcov", ".tox", ".gradle", "Pods", ".idea", ".vscode",
    "site-packages", "bower_components", ".terraform",
})

PY_EXT = frozenset({".py", ".pyi"})

# 언어별 주석 문법. (line_prefixes, block_pairs)
GENERIC_LANGS: dict[str, tuple[tuple[str, ...], tuple[tuple[str, str], ...]]] = {
    ".js": (("//",), (("/*", "*/"),)),
    ".jsx": (("//",), (("/*", "*/"),)),
    ".ts": (("//",), (("/*", "*/"),)),
    ".tsx": (("//",), (("/*", "*/"),)),
    ".mjs": (("//",), (("/*", "*/"),)),
    ".cjs": (("//",), (("/*", "*/"),)),
    ".java": (("//",), (("/*", "*/"),)),
    ".kt": (("//",), (("/*", "*/"),)),
    ".go": (("//",), (("/*", "*/"),)),
    ".rs": (("//",), (("/*", "*/"),)),
    ".c": (("//",), (("/*", "*/"),)),
    ".h": (("//",), (("/*", "*/"),)),
    ".cc": (("//",), (("/*", "*/"),)),
    ".cpp": (("//",), (("/*", "*/"),)),
    ".hpp": (("//",), (("/*", "*/"),)),
    ".cs": (("//",), (("/*", "*/"),)),
    ".swift": (("//",), (("/*", "*/"),)),
    ".scala": (("//",), (("/*", "*/"),)),
    ".php": (("//", "#"), (("/*", "*/"),)),
    ".rb": (("#",), ()),
    ".sh": (("#",), ()),
    ".bash": (("#",), ()),
}

# ---------------------------------------------------------------------------
# 명명 사전
# ---------------------------------------------------------------------------
# 문맥 없이 의미를 운반하지 못하는 이름. 도메인 무관하게 정보량이 0에 가깝다.
NONDESCRIPTIVE = frozenset({
    "tmp", "temp", "data", "datas", "val", "vals", "value2", "res", "resp",
    "ret", "retval", "obj", "objs", "arr", "lst", "dct", "dict2",
    "foo", "bar", "baz", "qux", "thing", "things", "stuff", "info",
    "aux", "misc", "var", "vars", "param", "params2", "arg2", "args2",
    "flag2", "num2", "str2", "check2", "handle2", "helper2",
    "do_it", "do_stuff", "process_data", "handle_data", "my_func", "test1",
})

# 단일 문자 중 관용적으로 허용되는 것 (루프/좌표/누산기 문맥에서만).
IDIOMATIC_SHORT = frozenset({"i", "j", "k", "n", "x", "y", "z", "_", "e", "f", "s", "t"})

# 루프/컴프리헨션 밖에서도 허용할 단일 문자는 없다고 본다.
LOOPY_ALLOWED = frozenset({"i", "j", "k", "n", "_", "x", "y", "z", "e"})

# 술어(predicate) 접두사 — bool을 약속한다.
PREDICATE_PREFIXES = ("is_", "has_", "can_", "should_", "was_", "were_", "does_", "did_", "must_", "needs_")
PREDICATE_CAMEL = re.compile(r"^(is|has|can|should|was|were|does|did|must|needs)[A-Z]")

# 조회(getter) 접두사 — 값을 약속한다.
GETTER_PREFIXES = ("get_", "fetch_", "read_", "load_", "find_", "compute_", "calculate_", "build_", "make_", "parse_", "to_")
GETTER_CAMEL = re.compile(r"^(get|fetch|read|load|find|compute|calculate|build|make|parse|to)[A-Z]")

# ---------------------------------------------------------------------------
# 주석 내 "식별자 참조" 추출 — 구문적으로 표시된 것만 잡아 거짓양성을 억제한다.
# 각 패턴은 중첩 수량자가 없어 백트래킹 폭발이 불가능하다(ReDoS 가드).
#
# 마커 강도를 구분한다:
#   strong — 백틱(`foo`) 또는 호출 표기(foo()). "이 파일의 코드 심볼"을 가리킬 개연성이 높다.
#   weak   — 산문 속 맨 snake_case / CamelCase. 외부 JSON 키·이벤트명·고유명사일 수 있다.
#            (실측: 훅 스크립트 주석의 `tool_input`·`PreToolUse` 는 코드 심볼이 아니라 외부 스키마다.)
# strong만 개입 후보(auto-med)로 올리고, weak는 heuristic 진단 정보로만 남긴다.
# ---------------------------------------------------------------------------
RE_BACKTICK = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]{2,63})`")
RE_CALL = re.compile(r"(?<![A-Za-z0-9_.$])([A-Za-z_][A-Za-z0-9_]{2,63})\(\)")
# 앞에 `.` 나 `$` 가 오면 멤버 접근·JSON 경로·셸 변수다. 이 파일의 심볼이라는 근거가 못 된다.
RE_SNAKE = re.compile(r"(?<![A-Za-z0-9_.$])([a-z][a-z0-9]*(?:_[a-z0-9]+)+)(?![A-Za-z0-9_])")
RE_CAMEL = re.compile(r"(?<![A-Za-z0-9_.$])([A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*)(?![A-Za-z0-9_])")
RE_TODO = re.compile(r"(?<![A-Za-z0-9_])(TODO|FIXME|HACK|XXX|BUG|WTF|REFACTOR)(?![A-Za-z0-9_])")
RE_URLISH = re.compile(r"://")
# 따옴표로 감싼 구간은 리터럴(경로·표현식)이지 코드 심볼 참조가 아니다. 선형 스캔(백트래킹 안전).
RE_QUOTED = re.compile(r"'[^'\n]{0,200}'|\"[^\"\n]{0,200}\"")
# 최상위 def/class — 심볼 인덱스용 경량 패스(전체 AST 파싱 회피).
RE_PY_TOPLEVEL = re.compile(r"^(?:async[ \t]+def|def|class)[ \t]+([A-Za-z_][A-Za-z0-9_]*)", re.M)

# 코드처럼 보이지만 실제로는 도구 지시자인 주석 — 주석처리된 코드로 오판하지 않는다.
RE_DIRECTIVE = re.compile(
    r"^\s*(noqa|type\s*:|fmt\s*:|pylint\s*:|mypy\s*:|ruff\s*:|pragma|isort\s*:|flake8\s*:|coverage\s*:|eslint|prettier|ts-ignore|ts-expect-error|@ts-)",
    re.IGNORECASE,
)

# 주석에 흔히 등장하지만 식별자가 아닌 영어/문서 토큰.
COMMENT_STOPWORDS = frozenset({
    "TODO", "FIXME", "HACK", "XXX", "BUG", "NOTE", "WARNING", "NOTES",
    "Args", "Arguments", "Returns", "Return", "Raises", "Yields", "Example",
    "Examples", "Parameters", "Attributes", "See", "Also", "None", "True", "False",
    "JSON", "HTTP", "HTTPS", "API", "URL", "URI", "UUID", "HTML", "CSS", "SQL",
    "GitHub", "JavaScript", "TypeScript", "README", "CHANGELOG", "Copyright",
    # 명명 규칙을 *논하는* 주석이 자기 자신을 dangling으로 만들지 않게.
    "snake_case", "camel_case", "kebab_case", "camelCase", "PascalCase", "SCREAMING_SNAKE",
})

PY_RESERVED = frozenset(keyword.kwlist) | frozenset(dir(builtins))

# docstring 파라미터 문법
RE_SPHINX_PARAM = re.compile(r"^\s*:param\s+(?:[\w\[\],. |]+\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*:")
RE_GOOGLE_SECTION = re.compile(r"^\s*(Args|Arguments|Parameters)\s*:\s*$")
RE_GOOGLE_PARAM = re.compile(r"^\s{1,}\*{0,2}([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]{0,80}\))?\s*:")
RE_OTHER_SECTION = re.compile(r"^\s*(Returns|Raises|Yields|Example|Examples|Attributes|Note|Notes)\s*:\s*$")
RE_NUMPY_PARAM_HDR = re.compile(r"^\s*(Parameters)\s*$")

# 제네릭(비-Python) 선언 추출 — 단순 패턴, 백트래킹 안전.
RE_JS_DECL = re.compile(
    r"(?<![A-Za-z0-9_$])(?:const|let|var|function|class)\s+([A-Za-z_$][A-Za-z0-9_$]{0,63})"
)
RE_IDENT_TOKEN = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]{0,63}")


# ---------------------------------------------------------------------------
# 자료구조
# ---------------------------------------------------------------------------
@dataclass
class Finding:
    detector: str
    grade: str            # auto-high | auto-med | heuristic | report-only
    axis: str             # naming | comments | structure
    file: str
    line: int
    symbol: str = ""
    message: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "detector": self.detector,
            "grade": self.grade,
            "axis": self.axis,
            "file": self.file,
            "line": self.line,
            "message": self.message,
        }
        if self.symbol:
            payload["symbol"] = self.symbol
        if self.extra:
            payload["extra"] = self.extra
        return payload


@dataclass
class ScanState:
    root: Path
    axes: set[str]
    findings: list[Finding] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    files_scanned: int = 0
    py_files: int = 0
    generic_files: int = 0
    # repo-wide symbol index: simple name -> set(relpath)
    repo_symbols: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    unit_sizes: list[dict[str, Any]] = field(default_factory=list)

    def add(self, f: Finding) -> None:
        if f.axis in self.axes:
            self.findings.append(f)


# ---------------------------------------------------------------------------
# 파일 순회 (심링크·대용량·바이너리 가드)
# ---------------------------------------------------------------------------
def iter_source_files(root: Path, max_files: int, skipped: list[dict[str, str]]) -> Iterator[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        parent_dir = Path(dirpath)
        # 잡음 디렉토리 + 숨김 디렉토리 제외
        dirnames[:] = [n for n in dirnames if n not in SKIP_DIRS and not n.startswith(".")]
        # 심링크 디렉토리는 따라가지 않는다 (repo 밖으로 탈출 방지)
        dirnames[:] = [n for n in dirnames if not (parent_dir / n).is_symlink()]
        for name in sorted(filenames):
            path = parent_dir / name
            ext = path.suffix.lower()
            if ext not in PY_EXT and ext not in GENERIC_LANGS:
                continue
            if path.is_symlink():
                skipped.append({"file": relpath(path, root), "reason": "symlink"})
                continue
            try:
                size = path.stat().st_size
            except OSError as exc:  # pragma: no cover - 환경 의존
                skipped.append({"file": relpath(path, root), "reason": f"stat-failed: {exc.__class__.__name__}"})
                continue
            if size > MAX_FILE_BYTES:
                # 측정 불가는 "깨끗함"이 아니다. 명시적으로 기록한다.
                skipped.append({"file": relpath(path, root), "reason": f"too-large ({size}B > {MAX_FILE_BYTES}B)"})
                continue
            count += 1
            if count > max_files:
                skipped.append({"file": relpath(path, root), "reason": "max-files-exceeded"})
                return
            yield path


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover
            return None


# ---------------------------------------------------------------------------
# Python — 식별자 수집
# ---------------------------------------------------------------------------
def python_tokens(src: str) -> tuple[set[str], list[tuple[int, str]]]:
    """단일 토크나이즈 패스로 (코드 식별자, 주석)을 함께 뽑는다.

    문자열·주석 안의 텍스트는 식별자로 세지 않는다. 토크나이즈가 중간에 실패하면
    거기까지 모은 것을 반환한다 — 부분 식별자 집합은 dangling 판정을 *보수적으로*
    만들어(거짓양성 감소) 안전한 방향으로 틀린다.
    """
    idents: set[str] = set()
    comments: list[tuple[int, str]] = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.NAME:
                idents.add(tok.string)
            elif tok.type == tokenize.COMMENT:
                comments.append((tok.start[0], tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        pass
    return idents, comments


# ---------------------------------------------------------------------------
# Python — AST 방문자
# ---------------------------------------------------------------------------
class LoopBindingCollector(ast.NodeVisitor):
    """루프/컴프리헨션에 바인딩된 이름을 모은다 (단일문자 관용 예외 판정용)."""

    def __init__(self) -> None:
        self.loop_bound: set[str] = set()

    def visit_For(self, node: ast.For) -> None:
        self._collect_target(node.target)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._collect_target(node.target)
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self._collect_target(node.target)
        self.generic_visit(node)

    def _collect_target(self, target: ast.AST) -> None:
        for node in ast.walk(target):
            if isinstance(node, ast.Name):
                self.loop_bound.add(node.id)


def _is_stub_body(body: list[ast.stmt]) -> bool:
    """`pass` / `...` / docstring만 / raise NotImplementedError 로 이루어진 본문."""
    real = [s for s in body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if not real:
        return True
    if len(real) == 1:
        s = real[0]
        if isinstance(s, ast.Pass):
            return True
        if isinstance(s, ast.Raise):
            return True
    return False


def _own_returns(fn: ast.AST) -> list[ast.Return]:
    """중첩 함수의 return은 제외하고 이 함수 자신의 return만 모은다."""
    out: list[ast.Return] = []

    def walk(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            if isinstance(child, ast.Return):
                out.append(child)
            walk(child)

    walk(fn)
    return out


def _has_own_yield(fn: ast.AST) -> bool:
    def walk(node: ast.AST) -> bool:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            if isinstance(child, (ast.Yield, ast.YieldFrom)):
                return True
            if walk(child):
                return True
        return False

    return walk(fn)


def _non_bool_literal(node: ast.expr | None) -> str | None:
    """확정적으로 bool이 아닌 리터럴이면 그 종류를 반환. 판단 불가면 None."""
    if node is None:
        return None
    if isinstance(node, ast.Constant):
        v = node.value
        if v is True or v is False:
            return None
        if v is None:
            return None  # None 반환은 별도로 다룬다 (Optional[bool] 가능)
        return type(v).__name__
    if isinstance(node, ast.Dict):
        return "dict"
    if isinstance(node, ast.List):
        return "list"
    if isinstance(node, ast.Set):
        return "set"
    if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
        return "comprehension"
    if isinstance(node, ast.Tuple):
        return "tuple"
    if isinstance(node, ast.JoinedStr):
        return "str"
    return None


def _is_predicate_name(name: str) -> bool:
    return name.startswith(PREDICATE_PREFIXES) or bool(PREDICATE_CAMEL.match(name))


def _is_getter_name(name: str) -> bool:
    return name.startswith(GETTER_PREFIXES) or bool(GETTER_CAMEL.match(name))


def _nondescriptive(name: str) -> str | None:
    """무의미 이름이면 사유를 반환. `Foo`·`TMP` 처럼 케이스만 다른 형태도 잡는다."""
    lowered = name.lower()
    if lowered in NONDESCRIPTIVE:
        return "stopword"
    if re.fullmatch(r"[a-z]{1,2}\d{1,2}", lowered):
        return "letter-digit"
    base = lowered.rstrip("0123456789")
    if base and base != lowered and base in NONDESCRIPTIVE:
        return "stopword-suffixed"
    return None


def scan_python(path: Path, src: str, state: ScanState) -> None:
    rel = relpath(path, state.root)
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError, RecursionError) as exc:
        state.skipped.append({"file": rel, "reason": f"python-parse-failed: {exc.__class__.__name__}"})
        # 파싱 실패해도 제네릭 경로로 주석만은 훑는다.
        scan_generic(path, src, state, forced_ext=".py_fallback")
        return

    code_idents, py_comments = python_tokens(src)

    collector = LoopBindingCollector()
    collector.visit(tree)
    loop_bound = collector.loop_bound

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _scan_function(node, rel, state, loop_bound, code_idents)
        elif isinstance(node, ast.ClassDef):
            _scan_class(node, rel, state, code_idents)

    # 최상위 심볼을 repo index에 등록
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            state.repo_symbols[node.name].add(rel)

    if "comments" in state.axes:
        _scan_py_comments(rel, py_comments, code_idents, state)
        doc = ast.get_docstring(tree, clean=False)
        if doc:
            _check_comment_text(doc, 1, rel, code_idents, state, source="docstring")


def _scan_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    rel: str,
    state: ScanState,
    loop_bound: set[str],
    code_idents: set[str],
) -> None:
    name = node.name

    # --- 구조(report-only): 크기·분기 ---
    if "structure" in state.axes:
        end = getattr(node, "end_lineno", None) or node.lineno
        loc = max(1, end - node.lineno + 1)
        branches = sum(
            1 for n in ast.walk(node)
            if isinstance(n, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.BoolOp))
        )
        state.unit_sizes.append(
            {"file": rel, "line": node.lineno, "symbol": name, "loc": loc, "branches": branches}
        )

    if "naming" not in state.axes and "comments" not in state.axes:
        return

    # ------------------------------------------------------------------
    # 명명 축
    # ------------------------------------------------------------------
    if "naming" in state.axes:
        reason = _nondescriptive(name)
        if reason and not name.startswith("__"):
            state.add(Finding(
                "N1_NONDESCRIPTIVE", "auto-high", "naming", rel, node.lineno, name,
                f"함수명 `{name}`이 의미를 운반하지 않는다 ({reason}).",
                {"kind": "function"},
            ))

        returns = _own_returns(node)
        is_gen = _has_own_yield(node)
        stub = _is_stub_body(node.body)

        # N2 — 술어 이름인데 bool이 아닌 리터럴을 반환한다.
        if _is_predicate_name(name) and not is_gen and not stub:
            bad: list[str] = []
            for r in returns:
                lit = _non_bool_literal(r.value)
                if lit:
                    bad.append(lit)
            if bad:
                state.add(Finding(
                    "N2_MISLEADING_PREDICATE", "auto-high", "naming", rel, node.lineno, name,
                    f"`{name}`은 bool을 약속하지만 {sorted(set(bad))} 리터럴을 반환한다.",
                    {"kind": "function", "returned": sorted(set(bad))},
                ))
            elif not returns:
                state.add(Finding(
                    "N2_MISLEADING_PREDICATE", "auto-high", "naming", rel, node.lineno, name,
                    f"`{name}`은 bool을 약속하지만 값을 반환하지 않는다(None).",
                    {"kind": "function", "returned": ["None"]},
                ))

        # N3 — 조회 이름인데 아무 값도 반환하지 않는다.
        if _is_getter_name(name) and not is_gen and not stub:
            valued = [r for r in returns if r.value is not None]
            if not valued:
                state.add(Finding(
                    "N3_MISLEADING_GETTER", "auto-high", "naming", rel, node.lineno, name,
                    f"`{name}`은 값을 약속하지만 반환문이 없다(None).",
                    {"kind": "function"},
                ))

        # 파라미터 명명
        for arg in _all_args(node):
            if arg.arg in ("self", "cls"):
                continue
            r = _nondescriptive(arg.arg)
            if r:
                state.add(Finding(
                    "N1_NONDESCRIPTIVE", "auto-high", "naming", rel, node.lineno, arg.arg,
                    f"파라미터 `{arg.arg}`가 의미를 운반하지 않는다 ({r}).",
                    {"kind": "parameter", "function": name},
                ))
            elif len(arg.arg) == 1 and arg.arg not in IDIOMATIC_SHORT:
                state.add(Finding(
                    "N1_NONDESCRIPTIVE", "auto-med", "naming", rel, node.lineno, arg.arg,
                    f"파라미터 `{arg.arg}`가 단일 문자다.",
                    {"kind": "parameter", "function": name},
                ))

        # 지역 변수 명명 (루프 바인딩 단일문자는 관용 허용)
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                nm = n.id
                r = _nondescriptive(nm)
                if r:
                    state.add(Finding(
                        "N1_NONDESCRIPTIVE", "auto-high", "naming", rel, n.lineno, nm,
                        f"지역 변수 `{nm}`가 의미를 운반하지 않는다 ({r}).",
                        {"kind": "variable", "function": name},
                    ))
                elif len(nm) == 1 and nm not in LOOPY_ALLOWED and nm not in loop_bound:
                    state.add(Finding(
                        "N1_NONDESCRIPTIVE", "auto-med", "naming", rel, n.lineno, nm,
                        f"지역 변수 `{nm}`가 단일 문자이며 루프 변수가 아니다.",
                        {"kind": "variable", "function": name},
                    ))

    # ------------------------------------------------------------------
    # 주석 축 — docstring 파라미터 불일치 (stale docstring, 결정론)
    # ------------------------------------------------------------------
    if "comments" in state.axes:
        doc = ast.get_docstring(node, clean=False)
        if doc:
            documented = _docstring_params(doc)
            sig = {a.arg for a in _all_args(node)} - {"self", "cls"}
            stale = sorted(documented - sig)
            if stale:
                state.add(Finding(
                    "C2_DOCSTRING_PARAM_MISMATCH", "auto-high", "comments", rel, node.lineno, name,
                    f"`{name}` docstring이 시그니처에 없는 파라미터 {stale}를 문서화한다 (코드가 변했고 주석은 안 변했다).",
                    {"documented_but_absent": stale, "signature": sorted(sig)},
                ))
            missing = sorted(sig - documented)
            if documented and missing:
                state.add(Finding(
                    "C5_DOCSTRING_PARAM_UNDOCUMENTED", "report-only", "comments", rel, node.lineno, name,
                    f"`{name}` docstring이 파라미터 {missing}를 문서화하지 않는다.",
                    {"undocumented": missing},
                ))
            # docstring 본문의 dangling 참조. 이미 C2로 보고한 파라미터명은 중복 보고하지 않는다.
            _check_comment_text(
                doc, node.lineno, rel, code_idents | documented, state, source="docstring"
            )


def _all_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.arg]:
    a = node.args
    out = list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)
    if a.vararg:
        out.append(a.vararg)
    if a.kwarg:
        out.append(a.kwarg)
    return out


def _scan_class(node: ast.ClassDef, rel: str, state: ScanState, code_idents: set[str]) -> None:
    if "comments" in state.axes:
        doc = ast.get_docstring(node, clean=False)
        if doc:
            _check_comment_text(doc, node.lineno, rel, code_idents, state, source="docstring")
    if "naming" not in state.axes:
        return
    reason = _nondescriptive(node.name)
    if reason:
        state.add(Finding(
            "N1_NONDESCRIPTIVE", "auto-high", "naming", rel, node.lineno, node.name,
            f"클래스명 `{node.name}`이 의미를 운반하지 않는다 ({reason}).",
            {"kind": "class"},
        ))
    elif len(node.name) <= 2:
        state.add(Finding(
            "N1_NONDESCRIPTIVE", "auto-med", "naming", rel, node.lineno, node.name,
            f"클래스명 `{node.name}`이 너무 짧다.",
            {"kind": "class"},
        ))


def _docstring_params(doc: str) -> set[str]:
    """Sphinx(:param x:) / Google(Args:) / NumPy(Parameters) 문법에서 문서화된 파라미터명을 추출."""
    found: set[str] = set()
    lines = doc.splitlines()

    for ln in lines:
        m = RE_SPHINX_PARAM.match(ln)
        if m:
            found.add(m.group(1))

    # Google style
    in_args = False
    for ln in lines:
        if RE_GOOGLE_SECTION.match(ln):
            in_args = True
            continue
        if in_args:
            if RE_OTHER_SECTION.match(ln):
                in_args = False
                continue
            if ln.strip() == "":
                continue
            if not ln.startswith((" ", "\t")):
                in_args = False
                continue
            m = RE_GOOGLE_PARAM.match(ln)
            if m:
                found.add(m.group(1))

    # NumPy style: "Parameters\n----------\nname : type"
    for idx, ln in enumerate(lines[:-1]):
        if RE_NUMPY_PARAM_HDR.match(ln) and set(lines[idx + 1].strip()) == {"-"}:
            for body_line in lines[idx + 2:]:
                if not body_line.strip():
                    break
                if set(body_line.strip()) == {"-"}:
                    break
                m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", body_line)
                if m:
                    found.add(m.group(1))
    return found


def _scan_py_comments(
    rel: str, comments: list[tuple[int, str]], code_idents: set[str], state: ScanState
) -> None:
    # C4 — 부채 마커
    for line, text in comments:
        for m in RE_TODO.finditer(text):
            state.add(Finding(
                "C4_DEBT_MARKER", "auto-high", "comments", rel, line, "",
                f"{m.group(1)} 마커.",
                {"marker": m.group(1), "text": text.strip()[:160]},
            ))
        _check_comment_text(text, line, rel, code_idents, state, source="comment")

    # C3 — 주석처리된 코드 (연속 블록을 합쳐 파싱 시도)
    _scan_commented_out_python(rel, comments, state)


def _check_comment_text(
    text: str, line: int, rel: str, code_idents: set[str], state: ScanState, source: str
) -> None:
    """C1 — 주석이 언급하는 식별자가 이 파일 어디에도 없다 (stale 후보)."""
    if RE_URLISH.search(text):
        return

    strong: set[str] = set()
    for rx in (RE_BACKTICK, RE_CALL):
        for m in rx.finditer(text):
            strong.add(m.group(1))

    # 산문 토큰은 따옴표 구간을 제거한 뒤에만 본다 ('.tool_input.command' 같은 리터럴 배제).
    scrubbed = RE_QUOTED.sub(" ", text)
    weak: set[str] = set()
    for rx in (RE_SNAKE, RE_CAMEL):
        for m in rx.finditer(scrubbed):
            weak.add(m.group(1))
    weak -= strong

    for ref, marker in [(r, "strong") for r in sorted(strong)] + [(r, "weak") for r in sorted(weak)]:
        base = ref.split(".", 1)[0]
        if len(base) < 3:
            continue
        if base in COMMENT_STOPWORDS or base in PY_RESERVED:
            continue
        if base in code_idents:
            continue
        # 파일 안에 없다. 저장소 심볼 인덱스에 있으면 "이동됨", 없으면 "인덱스 미발견".
        # 인덱스는 최상위 선언만 담으므로 *부재의 증명이 아니다*.
        elsewhere = sorted(state.repo_symbols.get(base, ()))
        grade = "auto-med" if marker == "strong" else "heuristic"
        hint = (f" (다른 파일에 존재: {elsewhere[:3]})" if elsewhere
                else " (저장소 최상위 심볼 인덱스에도 없음 — 부재의 증명은 아니다)")
        if marker == "weak":
            hint += " · 산문 토큰이라 외부 스키마 키·고유명사일 수 있다(개입 후보로 승격 금지)."
        state.add(Finding(
            "C1_DANGLING_IDENT", grade, "comments", rel, line, base,
            f"{source}이 `{base}`를 언급하지만 이 파일에 그 식별자가 없다." + hint,
            {"reference": ref, "source": source, "marker": marker,
             "severity": "moved-or-stale" if elsewhere else "not-in-index",
             "defined_in": elsewhere[:3]},
        ))


def _scan_commented_out_python(rel: str, comments: list[tuple[int, str]], state: ScanState) -> None:
    CODE_NODES = (
        ast.Assign, ast.AugAssign, ast.If, ast.For, ast.While, ast.Return,
        ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef, ast.With,
        ast.Try, ast.Raise, ast.Assert, ast.Delete,
    )
    block: list[tuple[int, str]] = []
    prev_line = -10

    def flush() -> None:
        nonlocal block
        if not block:
            return
        body_lines = []
        kept_lines = []
        for line_no, raw in block:
            stripped = raw.lstrip("#")
            # 도구 지시자(`# noqa: E501`·`# type: ignore`)는 코드처럼 파싱되지만 코드가 아니다.
            # 블록 전체를 버리지 말고 그 줄만 제외한다.
            if RE_DIRECTIVE.match(stripped):
                continue
            kept_lines.append(line_no)
            body_lines.append(stripped[1:] if stripped.startswith(" ") else stripped)
        if not body_lines:
            block = []
            return
        first_line = kept_lines[0]
        text = "\n".join(body_lines).strip("\n")
        if len(text.strip()) < 4:
            block = []
            return
        try:
            mod = ast.parse(_dedent(text))
        except (SyntaxError, ValueError, RecursionError):
            block = []
            return
        if not mod.body:
            block = []
            return
        code_like = any(isinstance(s, CODE_NODES) for s in mod.body)
        if not code_like:
            # Expr(Call) 만 있는 경우도 코드로 본다: `# print(x)`
            code_like = any(
                isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) for s in mod.body
            )
        if code_like:
            state.add(Finding(
                "C3_COMMENTED_OUT_CODE", "auto-med", "comments", rel, first_line, "",
                f"주석처리된 코드 {len(kept_lines)}줄. 에이전트에게는 실행되지 않는 노이즈다.",
                {"lines": len(kept_lines), "preview": text.strip()[:120]},
            ))
        block = []

    for line, raw in comments:
        if line == prev_line + 1:
            block.append((line, raw))
        else:
            flush()
            block = [(line, raw)]
        prev_line = line
    flush()


def _dedent(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return text
    indent = min(len(ln) - len(ln.lstrip()) for ln in lines)
    return "\n".join(ln[indent:] if len(ln) >= indent else ln for ln in text.splitlines())


# ---------------------------------------------------------------------------
# 제네릭 언어 (auto-low) — 문자열을 건너뛰는 상태기계로 주석 추출
# ---------------------------------------------------------------------------
def extract_generic_comments(src: str, line_prefixes: tuple[str, ...], blocks: tuple[tuple[str, str], ...]) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    i, n = 0, len(src)
    line = 1
    while i < n:
        ch = src[i]
        if ch == "\n":
            line += 1
            i += 1
            continue
        # 문자열 리터럴 스킵
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == "\n":
                    line += 1
                    if quote != "`":
                        break
                if src[i] == quote:
                    i += 1
                    break
                i += 1
            continue
        # 블록 주석
        matched_block = False
        for open_, close_ in blocks:
            if src.startswith(open_, i):
                end = src.find(close_, i + len(open_))
                if end == -1:
                    end = n
                chunk = src[i:end]
                out.append((line, chunk))
                line += chunk.count("\n")
                i = end + len(close_)
                matched_block = True
                break
        if matched_block:
            continue
        # 라인 주석
        matched_line = False
        for pref in line_prefixes:
            if src.startswith(pref, i):
                end = src.find("\n", i)
                if end == -1:
                    end = n
                out.append((line, src[i:end]))
                i = end
                matched_line = True
                break
        if matched_line:
            continue
        i += 1
    return out


def _tokens_outside_comments(src: str, comments: list[tuple[int, str]]) -> set[str]:
    joined = src
    for _, c in comments:
        joined = joined.replace(c, " ", 1)
    return set(RE_IDENT_TOKEN.findall(joined))


def scan_generic(path: Path, src: str, state: ScanState, forced_ext: str | None = None) -> None:
    rel = relpath(path, state.root)
    ext = forced_ext or path.suffix.lower()
    if ext == ".py_fallback":
        prefixes, blocks = ("#",), ()
    else:
        prefixes, blocks = GENERIC_LANGS[ext]

    comments = extract_generic_comments(src, prefixes, blocks)
    code_idents = _tokens_outside_comments(src, comments)

    if "comments" in state.axes:
        for line, text in comments:
            for m in RE_TODO.finditer(text):
                state.add(Finding(
                    "C4_DEBT_MARKER", "auto-high", "comments", rel, line, "",
                    f"{m.group(1)} 마커.",
                    {"marker": m.group(1), "text": text.strip()[:160]},
                ))
            _check_comment_text(text, line, rel, code_idents, state, source="comment")

    if "naming" in state.axes and ext != ".py_fallback":
        for m in RE_JS_DECL.finditer(_strip_comments(src, comments)):
            nm = m.group(1)
            reason = _nondescriptive(nm)
            line = src[: m.start()].count("\n") + 1
            if reason:
                state.add(Finding(
                    "N1_NONDESCRIPTIVE", "auto-low", "naming", rel, line, nm,
                    f"선언 `{nm}`이 의미를 운반하지 않는다 ({reason}).",
                    {"kind": "declaration"},
                ))


def _strip_comments(src: str, comments: list[tuple[int, str]]) -> str:
    out = src
    for _, c in comments:
        out = out.replace(c, " " * len(c), 1)
    return out


# ---------------------------------------------------------------------------
# 이름 충돌 (heuristic · 진단 정보)
# ---------------------------------------------------------------------------
def scan_collisions(state: ScanState, min_modules: int = 3) -> None:
    if "naming" not in state.axes:
        return
    for name, files in sorted(state.repo_symbols.items()):
        if len(files) >= min_modules and not name.startswith("_"):
            state.add(Finding(
                "N4_SYMBOL_COLLISION", "heuristic", "naming", sorted(files)[0], 0, name,
                f"최상위 심볼 `{name}`이 {len(files)}개 모듈에 정의돼 있다. grep·국소화가 모호해진다.",
                {"modules": sorted(files)[:8], "count": len(files),
                 "evidence": "근거 없음 — 진단 정보로만 사용한다."},
            ))


# ---------------------------------------------------------------------------
# git 기반 주석 드리프트 (heuristic · opt-in)
# ---------------------------------------------------------------------------
def git_available(root: Path) -> bool:
    if not (root / ".git").exists():
        return False
    try:
        subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            check=True, capture_output=True, timeout=GIT_TIMEOUT_SEC,
        )
        return True
    except (subprocess.SubprocessError, OSError):
        return False


def scan_git_drift(state: ScanState, drift_days: int) -> None:
    """주석 라인의 마지막 수정 시각이 함수 본문보다 drift_days 이상 오래됐으면 후보."""
    if "comments" not in state.axes:
        return
    if not git_available(state.root):
        state.skipped.append({"file": ".", "reason": "git-drift: not a git worktree"})
        return

    targets = defaultdict(list)
    for f in state.findings:
        if f.detector in ("C1_DANGLING_IDENT", "C3_COMMENTED_OUT_CODE"):
            targets[f.file].append(f.line)

    threshold = drift_days * 86400
    for rel, lines in list(targets.items())[:200]:
        times = _git_line_times(state.root, rel)
        if not times:
            continue
        file_newest = max(times.values(), default=0)
        for line_no in lines:
            line_time = times.get(line_no)
            if line_time is None:
                continue
            if file_newest - line_time >= threshold:
                state.add(Finding(
                    "C6_COMMENT_DRIFT", "heuristic", "comments", rel, line_no, "",
                    f"주석 라인이 파일 최신 변경보다 {int((file_newest - line_time) / 86400)}일 오래됐다 (drift 후보).",
                    {"days_behind": int((file_newest - line_time) / 86400),
                     "evidence": "코드-주석 불일치(CCI) 문헌의 조작적 프록시. 확정 판정 아님."},
                ))


def _git_line_times(root: Path, rel: str) -> dict[int, int]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "blame", "--line-porcelain", "--", rel],
            check=True, capture_output=True, timeout=GIT_TIMEOUT_SEC,
        )
    except (subprocess.SubprocessError, OSError):
        return {}
    out: dict[int, int] = {}
    cur_line = None
    for raw in proc.stdout.decode("utf-8", errors="replace").splitlines():
        if re.match(r"^[0-9a-f]{7,40} \d+ \d+", raw):
            parts = raw.split()
            try:
                cur_line = int(parts[2])
            except (IndexError, ValueError):
                cur_line = None
        elif raw.startswith("author-time ") and cur_line is not None:
            try:
                out[cur_line] = int(raw.split()[1])
            except (IndexError, ValueError):
                pass
    return out


# ---------------------------------------------------------------------------
# 출력
# ---------------------------------------------------------------------------
DETECTOR_META = {
    "N1_NONDESCRIPTIVE": ("naming", "무의미 식별자", "E-N1·E-N3"),
    "N2_MISLEADING_PREDICATE": ("naming", "술어 이름 ↔ 비-bool 반환", "E-N1·E-C1(오도 우선)"),
    "N3_MISLEADING_GETTER": ("naming", "조회 이름 ↔ 반환 없음", "E-N1·E-C1(오도 우선)"),
    "N4_SYMBOL_COLLISION": ("naming", "심볼 충돌", "근거 없음(진단 정보)"),
    "C1_DANGLING_IDENT": ("comments", "주석이 없는 식별자를 언급", "E-C3"),
    "C2_DOCSTRING_PARAM_MISMATCH": ("comments", "docstring 파라미터 불일치", "E-C3"),
    "C3_COMMENTED_OUT_CODE": ("comments", "주석처리된 코드", "E-C1(noise)"),
    "C4_DEBT_MARKER": ("comments", "TODO/FIXME 부채 마커", "존재는 결정론·해악은 heuristic"),
    "C5_DOCSTRING_PARAM_UNDOCUMENTED": ("comments", "문서화되지 않은 파라미터", "report-only"),
    "C6_COMMENT_DRIFT": ("comments", "주석-코드 시간 드리프트", "E-C3(프록시)"),
}

HONESTY_NOTES = [
    "이 스캐너는 등급·점수를 내지 않는다. 코드 본문 층위의 '몇 점'을 정당화할 1차 근거가 없다(O-1·O-3).",
    "저장소 층 등급(0~100·5밴드)은 측정 모드(score.py) 소관이고, 본문 층 census는 등급을 내지 않는다.",
    "C1_DANGLING_IDENT는 *후보*다. illustrative 예시·외부 라이브러리 심볼을 잡을 수 있으므로 사람/LLM이 확인해야 한다.",
    "함수 크기(unit_sizes)는 report-only다. '몇 줄 초과 = 나쁨'을 판정할 근거는 없다.",
    "N4_SYMBOL_COLLISION은 근거 없는 진단 정보다. 개입 후보로 승격하지 않는다.",
    "측정 불가(too-large·parse-failed·symlink)는 '결함 없음'이 아니다. skipped 목록을 반드시 함께 읽어라.",
    "census 델타는 '개입이 반영되었는가'의 결정론적 확인이지 에이전트 성공률의 대리 지표가 아니다.",
]


def build_report(state: ScanState, top: int) -> dict[str, Any]:
    by_detector: dict[str, int] = defaultdict(int)
    by_axis: dict[str, int] = defaultdict(int)
    for f in state.findings:
        by_detector[f.detector] += 1
        by_axis[f.axis] += 1

    findings_by_axis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in state.findings:
        findings_by_axis[f.axis].append(f.as_dict())

    unit_sizes = sorted(state.unit_sizes, key=lambda d: (-d["loc"], -d["branches"]))[:top]

    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(state.root),
        "axes_scanned": sorted(state.axes),
        "scanned": {
            "files": state.files_scanned,
            "python": state.py_files,
            "generic": state.generic_files,
            "skipped": state.skipped[:200],
            "skipped_total": len(state.skipped),
        },
        "counts": {
            "total_findings": len(state.findings),
            "by_axis": dict(sorted(by_axis.items())),
            "by_detector": dict(sorted(by_detector.items())),
        },
        "detector_meta": {
            k: {"axis": v[0], "what": v[1], "evidence": v[2]} for k, v in DETECTOR_META.items()
        },
        "findings": {k: v for k, v in sorted(findings_by_axis.items())},
        "structure_report_only": {
            "note": "임계값 없음. 크기는 진단 정보이지 판정 기준이 아니다.",
            "largest_units": unit_sizes,
        },
        "honesty_notes": HONESTY_NOTES,
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
VALID_AXES = frozenset({"naming", "comments", "structure"})


def run_scan(
    root: Path,
    axes: set[str],
    top: int = 20,
    max_files: int = MAX_FILES_DEFAULT,
    git_drift: bool = False,
    drift_days: int = 90,
) -> dict[str, Any]:
    """스캔 파이프라인 전체. main()과 테스트가 같은 경로를 공유한다."""
    state = ScanState(root=root, axes=axes)
    files = list(iter_source_files(root, max_files, state.skipped))

    # 1차 패스: repo 최상위 심볼 인덱스를 먼저 채운다 (C1의 "다른 파일에 존재" 판정에 필요).
    # 여기서는 AST를 파싱하지 않는다 — 최상위 def/class 는 열 0에서 시작하므로 경량 정규식으로 충분하고,
    # 파일당 전체 파싱을 한 번 아낀다.
    for path in files:
        src = read_text(path)
        if src is None:
            continue
        rel = relpath(path, root)
        pattern = RE_PY_TOPLEVEL if path.suffix.lower() in PY_EXT else RE_JS_DECL
        for m in pattern.finditer(src):
            state.repo_symbols[m.group(1)].add(rel)

    # 2차 패스: 실제 스캔
    for path in files:
        src = read_text(path)
        if src is None:
            state.skipped.append({"file": relpath(path, root), "reason": "binary-or-unreadable"})
            continue
        state.files_scanned += 1
        if path.suffix.lower() in PY_EXT:
            state.py_files += 1
            scan_python(path, src, state)
        else:
            state.generic_files += 1
            scan_generic(path, src, state)

    scan_collisions(state)
    if git_drift:
        scan_git_drift(state, drift_days)
    return build_report(state, top)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="코드 본문 층위 AI 가독성 census (등급 없음)")
    ap.add_argument("root", help="스캔할 저장소 루트")
    ap.add_argument("--out", help="JSON 출력 경로 (기본: stdout)")
    ap.add_argument("--axes", default="naming,comments,structure",
                    help="스캔할 축 (쉼표 구분). 사용자가 선택한 스코프 밖은 스캔하지 않는다.")
    ap.add_argument("--git-drift", action="store_true", help="git blame 기반 주석 드리프트(heuristic·느림)")
    ap.add_argument("--drift-days", type=int, default=90)
    ap.add_argument("--top", type=int, default=20, help="구조 진단 목록 길이")
    ap.add_argument("--max-files", type=int, default=MAX_FILES_DEFAULT)
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: {root} 는 디렉토리가 아니다", file=sys.stderr)
        return 2

    axes = {a.strip() for a in args.axes.split(",") if a.strip()}
    unknown = axes - VALID_AXES
    if unknown:
        print(f"error: 알 수 없는 축 {sorted(unknown)}", file=sys.stderr)
        return 2

    report = run_scan(
        root, axes, top=args.top, max_files=args.max_files,
        git_drift=args.git_drift, drift_days=args.drift_days,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
        print(f"census → {out}  ({report['counts']['total_findings']} findings, "
              f"{report['scanned']['files']} files, {report['scanned']['skipped_total']} skipped)")
    else:
        print(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # 신뢰할 수 없는 입력에서 스택트레이스로 죽지 않는다
        print(f"error: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
