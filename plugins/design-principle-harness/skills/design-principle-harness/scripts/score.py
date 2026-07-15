#!/usr/bin/env python3
"""design-principle-harness — 코드 설계 품질 스코어러 (Step 1: scoring-rubric 점수화).

이 스코어러는 임의 git 저장소를 두 층위(tier)로 채점한다.

  Tier A — Surface Legibility (표면 가독성, **act-first·근거 강함)** /60
    A1 Identifier Clarity   변수·함수·클래스·컴포넌트명 명료성 (28)
    A2 Naming Consistency   명명 규약(casing) 일관성            (12)
    A3 Comment Health       주석 건강도(오도/커멘트아웃/마커)   (20)

  Tier B — Design Principles (설계 원칙, **defer·진단·근거 약함)** /40
    B1 Complexity (KISS)                복잡도                  (8)
    B2 Cohesion & Coupling (SRP·응집/결합)                      (8)
    B3 Duplication (DRY·중복)                                   (8)
    B4 Cyclic Dependencies (의존 방향·acyclic principle)        (8)
    B5 Over-abstraction (DIP·DI/IoC·YAGNI·과대추상)             (8)

**정직성(핵심)**: 총점은 '인증(certification)'이나 '최적화 목표'가 아니라
**개선 작업 우선순위를 정하기 위한 진단 지표(prioritization index)**다. 특히 Tier B의
설계 원칙 점수는 고전 구조 지표가 (코드 길이를 통제하면) LLM 과제 성능과 무상관이고,
전부 사람 대상으로만 검증됐으며(=AI 가독성으로의 외삽), 준수도를 점수·게이트로 만들면
Goodhart/reward-hacking(표면 변형으로 게임)을 부른다는 근거 때문에 **낮은 가중·낮은 confidence·
report 성격**으로 싣는다. Tier A(명명·주석)는 **사람 대상 근거가 견고**하고 '오도/불일치/stale' 신호는
LLM에도 해로워 act-first·가중을 높였다 — 단 LLM 대상 식별자 리네임 효과는 **부호가 불안정·과제 의존적**이라
단일 수치로 못 쓴다. **개입(같은 저장소를 개선하면 같은 에이전트 성공률이 오른다) 연구는 없다** — 모든 구조/설계
점수는 측정된 예측자가 아니라 추론된 휴리스틱이고, 총점은 '안전 기여' 인증이 아니다(가장 강한 기여 신호=실행 가능·
의존성 무결성은 이 스코어러 범위 밖).
자세한 근거·출처는 references/research/evidence-dossier.md 참조.

이 스크립트는 **측정만** 한다(코드 수정 없음). 개선은 SKILL.md의 Step 2에서
섹션별 사람 승인 게이트 뒤에 이루어진다.

Usage:
    python3 score.py [repo_path]                # default: .  (markdown to stdout)
    python3 score.py /path/to/repo --json out.json
    python3 score.py . --json -                 # JSON to stdout

Pure stdlib — 외부 의존성 없음. Python 3.10+.
"""
from __future__ import annotations

import argparse
import ast
import functools
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

# ----------------------------------------------------------------------------
# Constants & robustness guards (신뢰할 수 없는 repo 대상 실행 하드닝)
# ----------------------------------------------------------------------------
IGNORE_DIRS = {
    "node_modules", ".venv", "venv", ".git", ".next", "dist", "build",
    "__pycache__", ".turbo", ".ruff_cache", ".pytest_cache", ".mypy_cache",
    "target", "out", "coverage", ".cache", ".idea", ".vscode", "vendor",
    ".gradle", "bin", "obj", ".svelte-kit",
}
PY_EXTS = {".py"}
JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
JSX_EXTS = {".tsx", ".jsx"}
CODE_EXTS = PY_EXTS | JS_EXTS
MAX_READ_BYTES = 5_000_000          # 초대형/비정규 파일은 빈 값 취급(메모리 폭주·FIFO 블록 가드)
MAX_FILES = 20_000                  # 파일 수 상한(비용 가드)

# 무의미·난독형 선언 이름(소문자 기준). 근거: 사람 대상 근거 견고(서술적 명명이 이해를 돕는다) +
# '오도/무의미' 이름은 LLM에도 해롭다(arXiv:2504.10557·2510.03178). 단 LLM 대상 식별자 리네임 효과는
# 부호가 불안정·과제 의존적이라 단일 수치로 못 쓴다(가드레일 #14, references/research/).
NONDESCRIPTIVE_NAMES = frozenset({
    "tmp", "temp", "temp1", "temp2", "data", "datas", "data1", "data2", "val", "vals",
    "value1", "value2", "res", "res1", "res2", "resp", "ret", "retval", "result1", "result2",
    "obj", "objs", "obj1", "arr", "arr1", "lst", "dct", "dict1", "dict2", "foo", "bar", "baz",
    "qux", "quux", "thing", "things", "stuff", "info", "aux", "misc", "var", "vars", "var1", "var2",
    "param1", "param2", "arg1", "arg2", "args2", "flag1", "flag2", "num1", "num2", "str1", "str2",
    "do_it", "do_stuff", "dostuff", "myfunc", "my_func", "myfunction", "func1", "func2", "test1",
    "test2", "helper", "helper1", "util", "utils1", "handle", "handler1", "process1", "cb1",
    "el1", "el2", "item1", "item2", "x1", "x2", "y1", "y2", "aaa", "asdf", "qwer", "abc",
})
# 관용적으로 허용되는 짧은 식별자(루프 변수·수학·표준 약어).
IDIOMATIC_SHORT = frozenset({
    "i", "j", "k", "n", "m", "x", "y", "z", "_", "e", "f", "s", "t", "id", "ok", "db", "io",
    "fn", "cb", "el", "ev", "dx", "dy", "dt", "px", "py", "ns", "os", "re", "df", "ax", "ui",
})
BRANCH_TOKENS_JS = re.compile(
    r"(?<![A-Za-z0-9_$])(?:if|for|while|case|catch)(?![A-Za-z0-9_$])|\?\.?|&&|\|\|"
)
# 문자열 리터럴/정규식 근사 제거용(주석·문자열 안의 branch 토큰 오탐 축소, 완전하지 않음 — 근사).
RE_JS_STRINGS = re.compile(r"'(?:\\.|[^'\\\n]){0,2000}'|\"(?:\\.|[^\"\\\n]){0,2000}\"|`(?:\\.|[^`\\]){0,4000}`")
RE_JS_LINE_COMMENT = re.compile(r"//[^\n]*")
RE_JS_BLOCK_COMMENT = re.compile(r"/\*[\s\S]{0,20000}?\*/")
# 선언 추출(JS/TS). 바운드 수량자로 ReDoS 회피.
RE_JS_FUNC = re.compile(r"(?<![A-Za-z0-9_$])function\s+([A-Za-z_$][\w$]{0,63})")
RE_JS_DECL = re.compile(r"(?<![A-Za-z0-9_$])(?:const|let|var)\s+([A-Za-z_$][\w$]{0,63})")
RE_JS_CLASS = re.compile(r"(?<![A-Za-z0-9_$])class\s+([A-Za-z_$][\w$]{0,63})")
RE_JS_ARROW_ASSIGN = re.compile(r"(?<![A-Za-z0-9_$])(?:const|let|var)\s+([A-Za-z_$][\w$]{0,63})\s*=\s*(?:async\s*)?\(")
RE_JS_IMPORT = re.compile(r"""(?:import\s[^'"\n]{0,300}from\s*|require\(\s*|import\(\s*|export\s[^'"\n]{0,120}from\s*)['"]([^'"\n]{1,300})['"]""")
RE_JS_EXPORT_NAME = re.compile(
    r"(?<![A-Za-z0-9_$])export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]{0,63})"
)
RE_TS_INTERFACE = re.compile(r"(?<![A-Za-z0-9_$])interface\s+([A-Za-z_$][\w$]{0,63})")
RE_TS_IMPLEMENTS = re.compile(r"(?<![A-Za-z0-9_$])implements\s+([A-Za-z_$][\w$,\s]{0,200})")
RE_CODEISH = re.compile(r"[;{}]|=>|\breturn\b|\bimport\b|\bfunction\b|\bdef\b|\bconst\b|==|!=|\)\s*\{|\w+\(")
RE_TODO = re.compile(r"(?<![A-Za-z])(TODO|FIXME|HACK|XXX|WTF|BUG|REFACTOR|커멘트아웃|임시)(?![A-Za-z])", re.IGNORECASE)

# --- 주석 도움 후보(comment-gap) 탐지기 — 코드만으로 '왜/맥락'을 알기 어려운 지점 -----
# report-only: 점수에 반영하지 않는다(주석 볼륨 가점=Goodhart). 개선 모드에서 opt-in '왜' 주석 추가 후보로만.
RE_PY_EMPTY_EXCEPT = re.compile(r"except\b[^\n:]{0,120}:\s*(?:#[^\n]*)?\n[ \t]*pass\b")
RE_JS_EMPTY_CATCH = re.compile(r"catch\s*(?:\([^)\n]{0,80}\))?\s*\{\s*\}")
# 매직 넘버: 3자리+ 정수 또는 소수(0/1/2… 관용값·인덱스는 제외). 문자열/주석 제거 후 스캔.
RE_MAGIC_NUM = re.compile(r"(?<![\w.])(?:\d+\.\d+|\d{3,})(?![\w.\d])")
# 정규식 리터럴(무엇을 매칭하는지 코드만으론 불명): 보수적으로 명시 API만.
RE_REGEX_USE = re.compile(r"\bre\.(?:compile|match|search|sub|subn|findall|finditer|fullmatch)\s*\(|new\s+RegExp\s*\(")

# --- Tier C (AI-맥락 신호 · report-only) 탐지기 -----------------------------
# 근거: references/research/semantic-a11y-test-dossier.md
#   - 세 신호(시맨틱 마크업·a11y·테스트 설명) 전부 report-only(직접 개입 근거는 명명 채널뿐).
#   - ARIA/role '볼륨'은 가점 금지(WebAIM: ARIA 많을수록 오류↑·auto-ARIA는 harm/Goodhart 벡터).
#   - native 시맨틱 사용을 측정하고, native로 대체 가능한 role=·onClick div는 결함 후보로만 보고.
MARKUP_EXTS = {".html", ".htm", ".vue", ".svelte"}      # JSX는 기존 walk에 포함(.tsx/.jsx)
# div/span에 onClick — "div soup 버튼"(native <button> 대신) 안티패턴
RE_NONSEMANTIC_CLICK = re.compile(r"<(?:div|span)\b[^>]{0,600}?\bon[Cc]lick\b", re.DOTALL)
# native 시맨틱/인터랙티브 요소
RE_NATIVE_SEMANTIC = re.compile(
    r"<(?:button|nav|main|header|footer|article|section|aside|label|form|table|figure|figcaption|"
    r"h[1-6]|ul|ol|fieldset|legend|dialog|details|summary|time|address)\b", re.IGNORECASE)
RE_ROLE_ATTR = re.compile(r"""\brole\s*=\s*['"]([a-zA-Z]+)['"]""")
RE_ARIA_ATTR = re.compile(r"\baria-[a-z]+\s*=", re.IGNORECASE)
RE_IMG_TAG = re.compile(r"<img\b", re.IGNORECASE)
RE_IMG_ALT = re.compile(r"<img\b[^>]{0,600}?\balt\s*=", re.IGNORECASE | re.DOTALL)
# native 요소로 대체 가능한 role(=native 우선 원칙 위반 후보). 'First rule of ARIA'.
ROLES_WITH_NATIVE = frozenset({
    "button", "link", "navigation", "main", "banner", "contentinfo", "heading",
    "list", "listitem", "checkbox", "radio", "textbox", "article", "form",
    "table", "row", "cell", "img", "figure", "complementary", "dialog", "search",
})
# 테스트 파일: it/test/describe 제목, py test 함수명
RE_JS_TEST_TITLE = re.compile(r"\b(?:it|test|describe)\s*(?:\.\w+)?\s*\(\s*(['\"`])((?:\\.|(?!\1).){1,240})\1", re.DOTALL)
RE_PY_TEST_DEF = re.compile(r"\bdef\s+(test[A-Za-z0-9_]*)\s*\(")
# 접근성 우선 셀렉터(의미 기반·refactor-robust) vs 비의미 셀렉터
RE_ACCESSIBLE_QUERY = re.compile(r"\b(?:get|find|query)(?:All)?By(?:Role|LabelText|Text|PlaceholderText|AltText|DisplayValue|Title)\b")
RE_NONSEMANTIC_QUERY = re.compile(r"\b(?:get|find|query)(?:All)?ByTestId\b|data-testid|\bquerySelector(?:All)?\b|\.locator\(\s*['\"][.#\[]|By\.(?:css|xpath)\b")
# 모호/무의미 테스트 제목(오도·저정보 → 삭제/리네임 후보). 존재≠가점, 오도=감점.
VAGUE_TEST_TITLES = frozenset({
    "", "test", "tests", "test1", "test 1", "test case", "testcase", "case", "case1",
    "works", "it works", "should work", "should works", "works correctly", "ok", "todo",
    "wip", "placeholder", "example", "sample", "foo", "bar", "baz", "temp", "tmp",
    "동작", "동작함", "된다", "잘된다", "테스트", "테스트1",
})


# ----------------------------------------------------------------------------
# Data classes
# ----------------------------------------------------------------------------
@dataclass
class Section:
    key: str
    name: str
    tier: str                    # "surface" | "design"
    score: int
    max: int
    confidence: str              # strong | medium | weak | report-only
    subjects: str                # human | LLM | both  (근거가 검증된 대상)
    effort: str                  # S | M | L  (개선 난이도)
    act_order: int               # 1=가장 먼저(쉬움·근거강함) … 큰 수=나중(어려움·근거약함)
    fix_mechanism: str           # 안전 개선 메커니즘(삭제전용/AST리네임/opt-in 구조 등)
    caveat: str
    evidence: dict[str, Any] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)


@dataclass
class Report:
    meta: dict[str, Any]
    total: int
    band: str
    tier_scores: dict[str, dict[str, Any]]
    sections: list[Section]
    improvement_order: list[str]
    extras: dict[str, Any]


# ----------------------------------------------------------------------------
# File IO (하드닝)
# ----------------------------------------------------------------------------
def _safe_readable(p: Path) -> bool:
    try:
        if p.is_symlink() or not p.is_file():
            return False
        return p.stat().st_size <= MAX_READ_BYTES
    except OSError:
        return False


@functools.lru_cache(maxsize=256)
def read_text(p: Path) -> str:
    try:
        if not _safe_readable(p):
            return ""
        return p.read_text(errors="ignore")
    except Exception:
        return ""


def walk_code_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            p = Path(r) / f
            if p.suffix in CODE_EXTS and not p.is_symlink():
                out.append(p)
                if len(out) >= MAX_FILES:
                    return out
    return out


# ----------------------------------------------------------------------------
# Declaration & comment extraction
# ----------------------------------------------------------------------------
@dataclass
class Decl:
    name: str
    kind: str        # func | class | var | component
    lang: str        # py | js


def extract_python_decls(text: str) -> list[Decl]:
    out: list[Decl] = []
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(Decl(node.name, "func", "py"))
        elif isinstance(node, ast.ClassDef):
            out.append(Decl(node.name, "class", "py"))
    # module-level assignments only (locals are too noisy & dynamic)
    try:
        mod = ast.parse(text)
        for node in mod.body:
            targets = []
            if isinstance(node, ast.Assign):
                targets = node.targets
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    out.append(Decl(t.id, "var", "py"))
    except (SyntaxError, ValueError):
        pass
    return out


def _strip_js_comments(text: str) -> str:
    """주석만 공백 치환(문자열은 보존 — import specifier 파싱용)."""
    return RE_JS_LINE_COMMENT.sub(" ", RE_JS_BLOCK_COMMENT.sub(" ", text))


def _strip_js_noise(text: str) -> str:
    """문자열·주석을 공백으로 치환(선언/토큰 오탐 축소). 근사. import specifier도 지워지므로 import 파싱엔 쓰지 말 것."""
    return RE_JS_STRINGS.sub('""', _strip_js_comments(text))


def extract_js_decls(text: str, is_jsx: bool) -> list[Decl]:
    clean = _strip_js_noise(text)
    out: list[Decl] = []
    for m in RE_JS_FUNC.finditer(clean):
        name = m.group(1)
        kind = "component" if (is_jsx and name[:1].isupper()) else "func"
        out.append(Decl(name, kind, "js"))
    arrow_names = {m.group(1) for m in RE_JS_ARROW_ASSIGN.finditer(clean)}
    for m in RE_JS_DECL.finditer(clean):
        name = m.group(1)
        if name in arrow_names:
            kind = "component" if (is_jsx and name[:1].isupper()) else "func"
        else:
            kind = "var"
        out.append(Decl(name, kind, "js"))
    for m in RE_JS_CLASS.finditer(clean):
        out.append(Decl(m.group(1), "class", "js"))
    return out


def split_words(name: str) -> list[str]:
    # snake_case / kebab / camelCase / PascalCase 분해
    parts = re.split(r"[_\-]+", name)
    words: list[str] = []
    for p in parts:
        words.extend(re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", p) or ([p] if p else []))
    return [w for w in words if w]


def is_nondescriptive(d: Decl) -> bool:
    base = d.name.strip("_").lower()
    if not base:
        return True
    if base in NONDESCRIPTIVE_NAMES:
        return True
    # 단일/이중 문자 비관용 이름
    if len(base) <= 2 and base not in IDIOMATIC_SHORT:
        # 클래스/컴포넌트는 두 글자 이름이 특히 불명료
        return True
    # 모음이 전혀 없는 3글자+ 약어(관용 제외) — 예: 'usr', 'btn'은 통과시키되 'xyzq'류만
    if len(base) >= 3 and base not in IDIOMATIC_SHORT and not re.search(r"[aeiou]", base):
        # 단, 흔한 무모음 약어는 허용
        if base not in {"btn", "src", "dst", "ctx", "idx", "cfg", "msg", "req", "res", "err",
                        "str", "num", "arr", "obj", "url", "uri", "img", "css", "sql", "npm",
                        "gql", "jwt", "env", "dev", "svg", "png", "jpg", "min", "max", "sum",
                        "avg", "std", "cwd", "pwd", "usr", "grp", "pid", "tcp", "udp", "dns"}:
            return True
    return False


def casing_violation(d: Decl) -> bool:
    """언어별 관례 위반 여부(휴리스틱). py: func/var=snake, class=Pascal. js: func/var=camel, class/component=Pascal."""
    name = d.name.strip("_")
    if not name or name.isupper():   # 상수(ALL_CAPS)는 허용
        return False
    has_underscore = "_" in name
    starts_upper = name[:1].isupper()
    if d.lang == "py":
        if d.kind == "class":
            return not starts_upper           # 클래스는 PascalCase 기대
        # func/var: snake_case 기대 → 대문자 시작이나 camelCase(내부 대문자)면 위반
        return starts_upper or bool(re.search(r"[a-z][A-Z]", name))
    else:  # js
        if d.kind in ("class", "component"):
            return not starts_upper           # PascalCase 기대
        # func/var: camelCase 기대 → snake_case(밑줄) 또는 Pascal 시작이면 위반
        return has_underscore or starts_upper


# ----------------------------------------------------------------------------
# Tier A scorers
# ----------------------------------------------------------------------------
def score_A1_identifiers(decls: list[Decl]) -> Section:
    MAXP = 28
    total = len(decls)
    if total == 0:
        return Section("A1", "Identifier Clarity (변수·함수·컴포넌트명)", "surface", MAXP // 2, MAXP,
                       "medium", "LLM", "S/M", 2, "AST/LSP 리네임 위임(수동 치환 금지)",
                       "선언(함수·클래스·최상위 변수·컴포넌트) 이름만 측정 — 지역 변수·파라미터·비-ASCII 이름은 미측정(미측정≠명료).",
                       {"declarations": 0}, ["측정 대상 선언 없음 — neutral"])
    bad = [d for d in decls if is_nondescriptive(d)]
    clarity = 1 - len(bad) / total
    score = round(MAXP * clarity)
    findings: list[str] = []
    if bad:
        sample = ", ".join(f"{d.name}({d.kind})" for d in bad[:8])
        findings.append(f"무의미/난독형 선언 {len(bad)}/{total} ({len(bad)/total:.0%}) — 예: {sample}")
    else:
        findings.append("무의미/난독형 선언 없음 — 명명 명료도 양호")
    return Section(
        "A1", "Identifier Clarity (변수·함수·컴포넌트명)", "surface", score, MAXP,
        "medium", "both", "S/M", 2, "AST/LSP 리네임 위임(수동 문자열 치환 금지·동적 참조/직렬화 주의)",
        "명명은 사람 comprehension 근거가 견고하고 '오도/무의미' 이름은 LLM에도 해로워 act-first — 그래서 Tier B보다 가중이 높다. "
        "단 LLM 대상 식별자 리네임 효과는 **부호가 불안정·과제 의존적**(intent 과제 -11~-29pp[arXiv:2510.03178]·알고리즘 ≈0·모델별 +14~-32pp)이라 "
        "단일 수치로 못 쓴다(가드레일 #14). act-first는 '명백히 오도하는 이름'에 한정하고 repo-wide 리네임 캠페인은 defer. "
        "측정은 선언 수준·ASCII 근사(지역 변수/파라미터 미측정)이며 타당도(AI 가독성 예측)는 외삽이다.",
        {"declarations": total, "nondescriptive": len(bad),
         "examples": [{"name": d.name, "kind": d.kind} for d in bad[:20]]},
        findings,
    )


def score_A2_consistency(decls: list[Decl]) -> Section:
    MAXP = 12
    total = len(decls)
    if total == 0:
        return Section("A2", "Naming Consistency (규약 일관성)", "surface", MAXP // 2, MAXP,
                       "weak", "human", "M", 3, "AST/LSP 리네임 위임",
                       "casing 규약 위반은 휴리스틱(언어 기본 관례 가정) — 팀 규약이 다르면 오탐 가능.",
                       {"declarations": 0}, ["측정 대상 선언 없음 — neutral"])
    viol = [d for d in decls if casing_violation(d)]
    consistency = 1 - len(viol) / total
    score = round(MAXP * consistency)
    findings: list[str] = []
    if viol:
        sample = ", ".join(f"{d.name}({d.kind}/{d.lang})" for d in viol[:8])
        findings.append(f"명명 규약 위반 후보 {len(viol)}/{total} ({len(viol)/total:.0%}) — 예: {sample}")
    else:
        findings.append("명명 규약(casing) 일관성 양호")
    return Section(
        "A2", "Naming Consistency (규약 일관성)", "surface", score, MAXP,
        "weak", "both", "M", 3, "AST/LSP 리네임 위임(공개 API 리네임은 소비자 영향 확인)",
        "이득은 '관례적(conventional)' 명명에 있다(에이전트는 관용 이름을 활용·특이한 '깔끔한' 리네임은 도움 안 될 수 있음). 언어 기본 관례(py=snake/Pascal, js=camel/Pascal)를 가정한 "
        "휴리스틱이라 팀 규약 상이 시 오탐. 측정은 결정론(High)이나 AI 가독성 타당도는 약함/외삽.",
        {"declarations": total, "violations": len(viol),
         "examples": [{"name": d.name, "kind": d.kind, "lang": d.lang} for d in viol[:20]]},
        findings,
    )


def analyze_comments(text: str, lang: str) -> dict[str, int]:
    lines = text.splitlines()
    code_lines = comment_lines = commented_out = todo = 0
    in_block = False
    for raw in lines:
        s = raw.strip()
        if not s:
            continue
        is_comment = False
        body = ""
        if lang == "py":
            if s.startswith("#"):
                is_comment, body = True, s[1:]
        else:
            # 매우 단순한 블록 추적(문자열 내 // 는 오탐 가능 — 근사)
            if in_block:
                is_comment, body = True, s
                if "*/" in s:
                    in_block = False
            elif s.startswith("//"):
                is_comment, body = True, s[2:]
            elif s.startswith("/*"):
                is_comment, body = True, s[2:]
                if "*/" not in s:
                    in_block = True
        if is_comment:
            comment_lines += 1
            if RE_TODO.search(body):
                todo += 1
            elif RE_CODEISH.search(body) and len(body.strip()) >= 6:
                commented_out += 1
        else:
            code_lines += 1
    return {"code": code_lines, "comment": comment_lines,
            "commented_out": commented_out, "todo": todo}


def _strip_py_noise(text: str) -> str:
    """py 주석·문자열을 공백으로(매직 넘버·정규식이 주석/문자열 안에서 오탐되지 않게). 근사."""
    text = re.sub(r"'''[\s\S]{0,20000}?'''|\"\"\"[\s\S]{0,20000}?\"\"\"", " ", text)
    text = re.sub(r"#[^\n]*", "", text)
    text = re.sub(r"'(?:\\.|[^'\\\n]){0,2000}'|\"(?:\\.|[^\"\\\n]){0,2000}\"", " ", text)
    return text


def find_comment_gap_candidates(files: list[Path]) -> dict[str, Any]:
    """코드만으로 '왜/맥락'을 알기 어려운 지점(침묵 예외·매직 넘버·정규식)을 센다.
    report-only — 점수에 반영하지 않고, 개선 모드의 opt-in '왜' 주석 추가 후보로만 쓴다."""
    empty_handlers = magic = regex = 0
    MAGIC_CAP_PER_FILE = 50
    samples: list[str] = []
    for p in files:
        text = read_text(p)
        if not text:
            continue
        if p.suffix in PY_EXTS:
            eh = len(RE_PY_EMPTY_EXCEPT.findall(text))
            body = _strip_py_noise(text)
        else:
            eh = len(RE_JS_EMPTY_CATCH.findall(text))
            body = _strip_js_noise(_strip_js_comments(text))
        mg = min(MAGIC_CAP_PER_FILE, len(RE_MAGIC_NUM.findall(body)))
        rx = len(RE_REGEX_USE.findall(body))
        empty_handlers += eh
        magic += mg
        regex += rx
        if (eh or rx) and len(samples) < 8:
            bits = []
            if eh:
                bits.append(f"침묵 예외 {eh}")
            if rx:
                bits.append(f"정규식 {rx}")
            samples.append(f"{p.name}: {'·'.join(bits)}")
    return {"empty_handlers": empty_handlers, "magic_numbers": magic,
            "regex_literals": regex, "samples": samples}


def score_A3_comments(files: list[Path]) -> Section:
    MAXP = 20
    agg = {"code": 0, "comment": 0, "commented_out": 0, "todo": 0}
    for p in files:
        text = read_text(p)
        if not text:
            continue
        lang = "py" if p.suffix in PY_EXTS else "js"
        c = analyze_comments(text, lang)
        for k in agg:
            agg[k] += c[k]
    code = max(1, agg["code"])
    # A3 = 오도/노이즈 감점 방식(주석이 '많다'고 가점하지 않음 — 정직성).
    # commented_out(죽은 코드 주석)·todo 마커의 코드 대비 비율로 감점. density는 report-only.
    co_ratio = agg["commented_out"] / code
    todo_ratio = agg["todo"] / code
    penalty = min(MAXP, round(MAXP * min(1.0, co_ratio * 12)) + round(MAXP * 0.4 * min(1.0, todo_ratio * 20)))
    score = max(0, MAXP - penalty)
    findings: list[str] = []
    if agg["commented_out"]:
        findings.append(f"커멘트아웃된(죽은) 코드 주석 {agg['commented_out']}줄 — 삭제 대상(위험 ~0, 오히려 오도 제거)")
    if agg["todo"]:
        findings.append(f"TODO/FIXME/HACK 마커 {agg['todo']}건 — 미해결 부채 신호(트리아지 후 처리/삭제)")
    density = agg["comment"] / code
    findings.append(f"[report-only] 주석 밀도 {density:.2f}(주석 {agg['comment']}/코드 {code}) — 밀도 자체는 점수에 반영하지 않음(많다≠좋다).")
    # 주석 도움 후보(comment-gap) — 코드만으로 문맥 파악이 어려운 곳. report-only(점수 무관)·opt-in 추가 후보.
    gap = find_comment_gap_candidates(files)
    gap_total = gap["empty_handlers"] + gap["regex_literals"] + gap["magic_numbers"]
    if gap["empty_handlers"]:
        findings.append(f"[report-only·주석 도움 후보] 침묵 예외 처리(empty except/catch) {gap['empty_handlers']}건 — 왜 삼키는지 '왜' 주석 추가 후보(opt-in·사람이 정확성 검증).")
    if gap["regex_literals"]:
        findings.append(f"[report-only·주석 도움 후보] 정규식 사용 {gap['regex_literals']}건 — 무엇을 매칭/치환하는지 예시와 함께 주석 후보.")
    if gap["magic_numbers"]:
        findings.append(f"[report-only·주석 도움 후보] 매직 넘버(3자리+/소수) {gap['magic_numbers']}건 — 단위·의미·출처를 담은 주석 후보(코드만으로 문맥 파악 어려운 곳).")
    if gap_total:
        findings.append("↳ 주석 추가는 **opt-in·'왜/맥락'(what 아님)·사람이 정확성 검증**: 코드에 없는 의도·외부 제약·우회 이유를 보충하는 곳에만. 올바른 주석의 LLM 이해 이득은 약하나(개입 근거 미미) 코드로 못 얻는 맥락을 채우고, **오도 주석이 실측 해악**이라 정확성 게이트가 핵심(자동 생성 주석을 사실로 단정 금지).")
    return Section(
        "A3", "Comment Health (주석 건강도)", "surface", score, MAXP,
        "medium", "both", "S", 1,
        "삭제 우선(오도·stale·죽은 코드 주석 제거·위험 ~0) + **코드만으로 문맥 파악 어려운 곳(침묵 예외·매직 넘버·정규식·비자명 우회)에 '왜/맥락' 주석 opt-in 추가**(사람이 정확성 검증·검증된 계약 주석)",
        "주석은 '많을수록 좋다'가 아니다 — 자동 생성 주석 상당수 부정확·주석↔코드 정합 현실분포 약함. 그래서 밀도·볼륨은 report-only(가점 안 함)이고, "
        "오도/죽은-코드/미해결 마커 제거만 점수 대상(삭제는 위험 ~0). **추가**는 점수와 무관한 opt-in 개선으로만 — 코드만으로 '왜'를 알기 어려운 곳에 사람이 정확성을 검증한 맥락 주석을 넣는다(올바른 주석의 LLM 이해 이득은 약해도 사람·비파생 맥락에 도움·오도 주석은 실측 해악).",
        {**agg, "comment_density": round(density, 3), "commented_out_ratio": round(co_ratio, 4),
         "comment_gap": gap},
        findings,
    )


# ----------------------------------------------------------------------------
# Import graph (design tier 공용)
# ----------------------------------------------------------------------------
@dataclass
class Node:
    rel: str
    lines: int = 0
    fan_in: int = 0
    fan_out: int = 0
    exports: set[str] = field(default_factory=set)
    imports: set[str] = field(default_factory=set)   # 대상 모듈명(py) 또는 파일 rel(js)


def build_graph(repo: Path, files: list[Path]) -> dict[str, Node]:
    top_level: set[str] = set()
    for d in repo.iterdir():
        try:
            if d.is_dir() and not d.is_symlink() and d.name not in IGNORE_DIRS and not d.name.startswith("."):
                top_level.add(d.name)
            elif d.is_file() and d.suffix == ".py":
                top_level.add(d.stem)
        except OSError:
            continue
    nodes: dict[str, Node] = {}
    for p in files:
        rel = p.relative_to(repo).as_posix()
        nodes[rel] = Node(rel=rel, lines=len(read_text(p).splitlines()))
    fan_in: dict[str, int] = defaultdict(int)
    for p in files:
        rel = p.relative_to(repo).as_posix()
        text = read_text(p)
        if not text:
            continue
        if p.suffix == ".py":
            try:
                tree = ast.parse(text)
            except (SyntaxError, ValueError):
                continue
            for n in ast.walk(tree):
                mods: list[str] = []
                if isinstance(n, ast.Import):
                    mods = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom) and n.module:
                    mods = [n.module]
                for mod in mods:
                    top = mod.split(".")[0]
                    if top in top_level:
                        nodes[rel].imports.add(top)
        elif p.suffix in JS_EXTS:
            comment_free = _strip_js_comments(text)   # 문자열(=import specifier) 보존
            for m in RE_JS_IMPORT.finditer(comment_free):
                spec = m.group(1)
                if spec.startswith("."):
                    tgt = _resolve_js(p, spec, repo)
                    if tgt:
                        nodes[rel].imports.add(tgt)
            for m in RE_JS_EXPORT_NAME.finditer(_strip_js_noise(text)):
                nodes[rel].exports.add(m.group(1))
    for rel, node in nodes.items():
        node.fan_out = len(node.imports)
        for tgt in node.imports:
            fan_in[tgt] += 1
    for rel, node in nodes.items():
        node.fan_in += fan_in.get(rel, 0)
        if "/" not in rel:
            node.fan_in += fan_in.get(rel.rsplit(".", 1)[0], 0)
        elif rel.endswith("/__init__.py"):
            pkg = rel[: -len("/__init__.py")]
            if "/" not in pkg:
                node.fan_in += fan_in.get(pkg, 0)
    return nodes


def _resolve_js(importer: Path, spec: str, repo: Path) -> str | None:
    base = importer.parent / spec
    cands = [base] + [base.with_suffix(e) for e in JS_EXTS] + [base / ("index" + e) for e in JS_EXTS]
    repo_r = repo.resolve()
    for c in cands:
        try:
            if not c.is_file():
                continue
            cr = c.resolve()
            if cr.is_relative_to(repo_r):
                # rel은 resolve된 repo 기준으로 계산 — macOS /var↔/private/var 혼용 시 relative_to 실패 방지.
                # node rel(=p.relative_to(repo))과 같은 서브패스 문자열이 된다.
                return cr.relative_to(repo_r).as_posix()
        except OSError:
            continue
    return None


# ----------------------------------------------------------------------------
# Tier B scorers (설계 원칙 — report/weak confidence, defer)
# ----------------------------------------------------------------------------
def python_complexity(text: str) -> list[tuple[str, int, int]]:
    """(func_name, cyclomatic, length) per Python function (AST — 정확)."""
    out: list[tuple[str, int, int]] = []
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return out
    BRANCH = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp, ast.ExceptHandler,
              ast.With, ast.AsyncWith, ast.Assert)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1
            for sub in ast.walk(node):
                if isinstance(sub, BRANCH):
                    cc += 1
                elif isinstance(sub, ast.BoolOp):
                    cc += len(sub.values) - 1
                elif isinstance(sub, ast.comprehension):
                    cc += 1 + len(sub.ifs)
                elif hasattr(ast, "match_case") and isinstance(sub, getattr(ast, "match_case")):
                    cc += 1
            length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
            out.append((node.name, cc, length))
    return out


def js_file_complexity(text: str) -> dict[str, int]:
    clean = _strip_js_noise(text)
    branches = len(BRANCH_TOKENS_JS.findall(clean))
    funcs = len(RE_JS_FUNC.findall(clean)) + len(RE_JS_ARROW_ASSIGN.findall(clean))
    depth = maxdepth = 0
    for ch in clean:
        if ch == "{":
            depth += 1
            maxdepth = max(maxdepth, depth)
        elif ch == "}":
            depth = max(0, depth - 1)
    return {"branches": branches, "funcs": funcs, "max_brace_depth": maxdepth,
            "lines": len(text.splitlines())}


CC_HOT = 15          # 함수 순환복잡도 hotspot 임계(SonarSource 기본 15 근사; 근거 약함 라벨)
FUNC_LONG = 80       # 긴 함수 라인 임계
JS_DEPTH_HOT = 6     # JS brace nesting 깊이 hotspot


def score_B1_complexity(repo: Path, files: list[Path]) -> Section:
    MAXP = 8
    py_funcs = 0
    py_hot: list[str] = []
    js_files = 0
    js_hot: list[str] = []
    for p in files:
        text = read_text(p)
        if not text:
            continue
        if p.suffix in PY_EXTS:
            for name, cc, length in python_complexity(text):
                py_funcs += 1
                if cc > CC_HOT or length > FUNC_LONG:
                    py_hot.append(f"{p.relative_to(repo).as_posix()}::{name} (cc={cc},len={length})")
        elif p.suffix in JS_EXTS:
            js_files += 1
            c = js_file_complexity(text)
            if c["max_brace_depth"] > JS_DEPTH_HOT or (c["funcs"] and c["branches"] / max(1, c["funcs"]) > CC_HOT):
                js_hot.append(f"{p.relative_to(repo).as_posix()} (depth={c['max_brace_depth']},branch/fn≈{c['branches']}/{c['funcs']})")
    denom = max(1, py_funcs + js_files)
    hot = len(py_hot) + len(js_hot)
    health = 1 - min(1.0, hot / denom * 4)     # hotspot 비율 25%면 0점
    score = round(MAXP * health)
    findings: list[str] = []
    if py_hot:
        findings.append(f"복잡도 hotspot 함수(Python·정확) {len(py_hot)}건 — 예: {py_hot[0]}")
    if js_hot:
        findings.append(f"복잡도 hotspot 파일(JS/TS·근사) {len(js_hot)}건 — 예: {js_hot[0]}")
    if not hot:
        findings.append("복잡도 hotspot 미탐지")
    return Section(
        "B1", "Complexity (KISS·복잡도)", "design", score, MAXP,
        "weak", "human", "L", 5,
        "opt-in 고위험 리팩터(함수 분해) — 행위 센서 관측·'테스트 통과≠동작 보존'",
        "복잡도 지표는 사람 '읽기 시간'(r=0.54)은 예측해도 '정확도'는 못 하고(r=-0.13), 길이 통제 시 LLM 성능과 무상관이며(arXiv:2602.07882) "
        "McCabe는 인지부하와 무관(Peitek). 전부 사람 대상 검증(=AI로의 외삽). **McCabe보다 nesting-depth·param-count가 낫고 반드시 SLOC와 함께 해석**. "
        "hotspot은 사람이 볼 후보일 뿐, 점수 목표로 삼지 말 것(Goodhart). JS는 파일 수준 근사.",
        {"py_functions": py_funcs, "js_files": js_files, "hotspots": hot,
         "py_hotspots": py_hot[:15], "js_hotspots": js_hot[:15]},
        findings,
    )


COUPLING_HOTSPOT = 14
BIG_FILE = 400


def score_B2_cohesion(repo: Path, nodes: dict[str, Node]) -> Section:
    MAXP = 8
    if not nodes:
        return Section("B2", "Cohesion & Coupling (SRP·응집/결합)", "design", MAXP // 2, MAXP,
                       "weak", "human", "L", 6, "opt-in 구조 리팩터(경계 분리)",
                       "파서 지원 코드(py·js/ts) 없음 — neutral.", {"nodes": 0}, ["측정 불가 — neutral"])
    hotspots = [n for n in nodes.values() if (n.fan_in + n.fan_out) >= COUPLING_HOTSPOT]
    big = [n for n in nodes.values() if n.lines > BIG_FILE]
    ratio = len(hotspots) / max(1, len(nodes))
    health = 1 - min(1.0, ratio * 8)
    score = round(MAXP * health)
    findings: list[str] = []
    if hotspots:
        top = sorted(hotspots, key=lambda n: -(n.fan_in + n.fan_out))[:5]
        findings.append("결합 hotspot(god-file 후보·라인 수 아님): " +
                        ", ".join(f"{n.rel}(in{n.fan_in}/out{n.fan_out})" for n in top))
    if big:
        findings.append(f"[보조] 대형 파일(>{BIG_FILE}줄) {len(big)}건 — 라인 수는 근거 약한 보조 신호")
    if not hotspots:
        findings.append("결합 hotspot 미탐지")
    return Section(
        "B2", "Cohesion & Coupling (SRP·응집/결합)", "design", score, MAXP,
        "weak", "human", "L", 6,
        "opt-in 고위험 구조 리팩터(책임 분리) — 격리 렌더/라우트 센서·opt-in(리팩터 위험이 가장 큼)",
        "결합도는 **가독성 신호가 아니라 변경 위험(blast-radius) 진단**이다(30년 사람-결함 검증이지 LLM 내비게이션 근거 없음·Lens 3 재등급). "
        "god-file은 fan-in/out으로 정의(라인 수 임계값은 근거 부재). LCOM류 응집 지표는 8+ 변종이 값 불일치라 미채택. SRP 준수도는 직접 측정 불가"
        "(정적 SRP 지표 없음·god-class 문헌은 모순: size-normalize하면 God class가 오히려 덜 변함) — 사람이 볼 후보 목록이다. **'SOLID=N/100' 금지.**",
        {"nodes": len(nodes), "coupling_hotspots": len(hotspots), "big_files": len(big)},
        findings,
    )


DUP_MIN_RUN = 6
DUP_MAX_WINDOWS = 300_000
DUP_MAX_CLUSTERS = 40


def score_B3_duplication(repo: Path, nodes: dict[str, Node]) -> Section:
    MAXP = 8
    buckets: dict[str, list[tuple[str, int]]] = defaultdict(list)
    windows = 0
    truncated = False
    total_lines = 0
    for rel, node in nodes.items():
        if node.lines > 6000:
            continue
        text = read_text(repo / rel)
        if not text:
            continue
        norms: list[str | None] = []
        for ln in text.splitlines():
            s = ln.strip()
            if not s or s[0] in "#*" or s[:2] in ("//", "/*"):
                norms.append(None)
                continue
            n = re.sub(r'"[^"\n]{0,500}"|\'[^\'\n]{0,500}\'|`[^`\n]{0,500}`', "§", s)
            n = re.sub(r"\b\d[\w.]*\b", "0", n)
            n = re.sub(r"\s+", " ", n)
            norms.append(n if len(n) >= 8 else None)
        total_lines += sum(1 for v in norms if v is not None)
        i, tot = 0, len(norms)
        while i + DUP_MIN_RUN <= tot:
            window = norms[i:i + DUP_MIN_RUN]
            gap = next((j for j, v in enumerate(window) if v is None), -1)
            if gap != -1:
                i += gap + 1
                continue
            buckets["\n".join(window)].append((rel, i + 1))
            windows += 1
            i += 1
            if windows >= DUP_MAX_WINDOWS:
                truncated = True
                break
        if truncated:
            break
    clusters = []
    dup_windows = 0
    for locs in buckets.values():
        uniq = sorted(set(locs))
        if len(uniq) >= 2:
            dup_windows += len(uniq)
            files = sorted({r for r, _ in uniq})
            clusters.append({"occurrences": len(uniq), "files": files[:6], "example": f"{uniq[0][0]}:{uniq[0][1]}"})
    clusters.sort(key=lambda c: -c["occurrences"])
    dup_ratio = dup_windows / max(1, windows)
    health = 1 - min(1.0, dup_ratio * 3)
    score = round(MAXP * health)
    findings: list[str] = []
    if clusters:
        findings.append(f"정확/매개변수 중복(Type-1/2) 클러스터 {len(clusters)}개 — 예: {clusters[0]['example']} ×{clusters[0]['occurrences']}")
    else:
        findings.append("Type-1/2 중복 클러스터 미탐지")
    if truncated:
        findings.append("[비용 상한] 중복 스캔 truncated — 일부 미집계")
    return Section(
        "B3", "Duplication (DRY·중복)", "design", score, MAXP,
        "medium", "both", "M", 4,
        "extract(중복 제거) — 행위 센서 관측·'잘못된 추상화보다 중복이 쌀 수도'",
        "정확·매개변수 중복(Type-1/2)만 신뢰 측정. 의미 중복(Type-3/4)은 정적 측정 불가(보고 안 함·누락≠없음). "
        "중복이 항상 해로운 것은 아니다(Kapser&Godfrey) — 성급한 잘못된 추상화가 더 비쌀 수 있어, 제거는 사람 판단.",
        {"windows": windows, "duplicate_windows": dup_windows, "cluster_count": len(clusters),
         "truncated": truncated, "clusters": clusters[:DUP_MAX_CLUSTERS]},
        findings,
    )


MAX_CYCLE_MODULES = 800


def _module_of(rel: str) -> str:
    return rel.rsplit("/", 1)[0] if "/" in rel else rel.rsplit(".", 1)[0]


def _module_graph(nodes: dict[str, Node]) -> dict[str, set[str]]:
    node_rels = set(nodes)
    adj: dict[str, set[str]] = {}
    for rel, node in nodes.items():
        src = _module_of(rel)
        adj.setdefault(src, set())
        for tgt in node.imports:
            dst = _module_of(tgt) if tgt in node_rels else tgt
            if dst != src:
                adj[src].add(dst)
    return adj


def _sccs(adj: dict[str, set[str]]) -> list[list[str]]:
    idx: dict[str, int] = {}
    low: dict[str, int] = {}
    onstack: set[str] = set()
    stack: list[str] = []
    out: list[list[str]] = []
    counter = 0
    for start in list(adj):
        if start in idx:
            continue
        work: list[tuple[str, Iterator[str]]] = [(start, iter(sorted(adj.get(start, ()))))]
        idx[start] = low[start] = counter
        counter += 1
        stack.append(start)
        onstack.add(start)
        while work:
            v, it = work[-1]
            pushed = False
            for w in it:
                if w not in adj:
                    continue
                if w not in idx:
                    idx[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    onstack.add(w)
                    work.append((w, iter(sorted(adj.get(w, ())))))
                    pushed = True
                    break
                if w in onstack:
                    low[v] = min(low[v], idx[w])
            if pushed:
                continue
            if low[v] == idx[v]:
                comp: list[str] = []
                while True:
                    w = stack.pop()
                    onstack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    out.append(sorted(comp))
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
    return out


def score_B4_cycles(nodes: dict[str, Node]) -> Section:
    MAXP = 8
    adj = _module_graph(nodes)
    if not adj:
        return Section("B4", "Cyclic Dependencies (의존 방향)", "design", MAXP // 2, MAXP,
                       "weak", "human", "L", 7, "opt-in 의존 역전(dependency inversion)",
                       "그래프 없음 — neutral.", {"modules": 0}, ["측정 불가 — neutral"])
    if len(adj) > MAX_CYCLE_MODULES:
        return Section("B4", "Cyclic Dependencies (의존 방향)", "design", MAXP // 2, MAXP,
                       "weak", "human", "L", 7, "opt-in 의존 역전",
                       f"모듈 {len(adj)} > {MAX_CYCLE_MODULES} — 탐지 스킵(비용). 미측정≠순환 없음.",
                       {"modules": len(adj), "measured": False}, ["비용 상한 — 미측정"])
    cycles = _sccs(adj)
    cycles.sort(key=lambda c: -len(c))
    n = len(cycles)
    if n == 0:
        score = MAXP
    else:
        health = 1 - min(1.0, n / max(4, len(adj)) * 4)
        score = round(MAXP * health)
    findings: list[str] = []
    if cycles:
        findings.append(f"모듈(디렉터리) 순환 의존 {n}개 — 예: {' ↔ '.join(cycles[0][:4])}")
    else:
        findings.append("모듈 순환 의존 없음(acyclic)")
    return Section(
        "B4", "Cyclic Dependencies (의존 방향·acyclic principle)", "design", score, MAXP,
        "weak", "human", "L", 7,
        "opt-in 의존 역전(dependency inversion)으로 방향 정리",
        "순환 탐지는 **결정론적으로 신뢰 가능**(측정 High)하나, **'acyclic → 더 나은 LLM 내비게이션'은 미측정 외삽**이다(순환 인접 클래스가 변경 잦음은 "
        "사람 연구). **LocAgent(92.7%)·RepoGraph(+32.8%) 이득을 순환 제거 효과로 귀속 금지**(그건 툴 측 그래프 인덱스 효과·RepoGraph는 acyclicity를 주장 안 함). "
        "Python 중첩 패키지 순환은 과소탐지될 수 있음(미측정≠없음).",
        {"modules": len(adj), "cycle_count": n, "measured": True,
         "cycles": [{"modules": c, "size": len(c)} for c in cycles[:20]]},
        findings,
    )


def score_B5_overabstraction(repo: Path, nodes: dict[str, Node]) -> Section:
    MAXP = 8
    iface_decls: dict[str, str] = {}
    impls: dict[str, int] = defaultdict(int)
    for rel, node in nodes.items():
        if not rel.endswith((".ts", ".tsx")):
            continue
        text = read_text(repo / rel)
        if not text:
            continue
        clean = _strip_js_noise(text)
        for m in RE_TS_INTERFACE.finditer(clean):
            iface_decls.setdefault(m.group(1), rel)
        for m in RE_TS_IMPLEMENTS.finditer(clean):
            for nm in re.split(r"[,\s]+", m.group(1).strip()):
                if nm:
                    impls[nm] += 1
    single = [{"interface": name, "declared_in": loc}
              for name, loc in sorted(iface_decls.items()) if impls.get(name, 0) == 1]
    # 미참조 파일(fan_in 0·엔트리 아님) — YAGNI/dead-code 근사(보조)
    orphan = [n.rel for n in nodes.values()
              if n.fan_in == 0 and n.fan_out == 0 and not re.search(r"(index|main|__init__|app|setup|conf)", n.rel.rsplit("/", 1)[-1])]
    ts_total = max(1, len(iface_decls))
    over_ratio = len(single) / ts_total if iface_decls else 0.0
    health = 1 - min(1.0, over_ratio)
    score = round(MAXP * health) if iface_decls else MAXP // 2
    findings: list[str] = []
    if single:
        findings.append(f"구현 1개뿐인 TS 인터페이스 {len(single)}건 — 불필요 간접참조 후보(DIP 과적용)")
    if orphan:
        findings.append(f"[report-only] 미참조 파일 {len(orphan)}건 — YAGNI/dead-code 후보(공개 API·엔트리·동적 로드 제외 필요, 오탐 잦음)")
    if not single and not iface_decls:
        findings.append("TS 인터페이스 없음 — 과대추상 신호 측정 대상 아님(neutral)")
    return Section(
        "B5", "Over-abstraction (DIP·DI/IoC·YAGNI·과대추상)", "design", score, MAXP,
        "weak", "human", "M", 8,
        "간접참조 축소(단일 구현 인터페이스 인라인) — opt-in·정당한 경계일 수 있음",
        "DI/IoC 준수도는 런타임 배선이라 정적 측정 불가 — 이 섹션은 '과대추상' 반대편 신호(단일 구현 인터페이스)의 근사일 뿐. "
        "미참조 파일은 오탐이 잦아 report-only. 정당한 확장 경계일 수 있어 판정이 아니라 후보다.",
        {"ts_interfaces": len(iface_decls), "single_impl_interfaces": len(single),
         "orphan_files": len(orphan), "examples": single[:20], "orphans": orphan[:20]},
        findings,
    )


# ----------------------------------------------------------------------------
# Assemble
# ----------------------------------------------------------------------------
BANDS = [
    (85, "Strong (설계 부채 낮음)"),
    (70, "Fair (표면 개선 여지)"),
    (50, "Weak (표면+구조 개선 권장)"),
    (0, "Fragile (우선순위 개선 필요)"),
]


def band_of(total: int) -> str:
    for th, label in BANDS:
        if total >= th:
            return label
    return "Fragile (우선순위 개선 필요)"


# ----------------------------------------------------------------------------
# Tier C — AI-맥락 신호 (report-only · 총점 미합산)
# ----------------------------------------------------------------------------
def walk_markup_files(root: Path) -> list[Path]:
    """.html/.vue/.svelte 수집(JSX는 별도로 CODE walk에서 옴). 동일 하드닝·상한."""
    out: list[Path] = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            p = Path(r) / f
            if p.suffix.lower() in MARKUP_EXTS and not p.is_symlink():
                out.append(p)
                if len(out) >= MAX_FILES:
                    return out
    return out


def is_test_file(p: Path) -> bool:
    n = p.name.lower()
    parts = {seg.lower() for seg in p.parts}
    if parts & {"__tests__", "__test__", "e2e", "cypress", "playwright"}:
        return True
    return (".test." in n or ".spec." in n
            or (p.suffix in PY_EXTS and (n.startswith("test_") or n.endswith("_test.py"))))


def score_C1_semantic_markup(repo: Path, files: list[Path]) -> Section:
    """시맨틱 HTML/JSX·a11y 신호. report-only(총점 미합산). native 시맨틱 측정,
    role=/onClick-div/무-alt는 결함 후보로 보고. ARIA '볼륨'은 절대 가점하지 않는다."""
    MAXP = 10
    markup = [p for p in files if p.suffix in JSX_EXTS] + walk_markup_files(repo)
    native = nonsem_click = role_native = role_total = aria = img = img_noalt = 0
    for p in markup:
        text = read_text(p)
        if not text:
            continue
        native += len(RE_NATIVE_SEMANTIC.findall(text))
        nonsem_click += len(RE_NONSEMANTIC_CLICK.findall(text))
        aria += len(RE_ARIA_ATTR.findall(text))
        imgs = len(RE_IMG_TAG.findall(text))
        img += imgs
        img_noalt += max(0, imgs - len(RE_IMG_ALT.findall(text)))
        for m in RE_ROLE_ATTR.finditer(text):
            role_total += 1
            if m.group(1).lower() in ROLES_WITH_NATIVE:
                role_native += 1
    findings: list[str] = []
    if not markup:
        return Section(
            "C1", "Semantic Markup & a11y (시맨틱 마크업)", "context", MAXP, MAXP,
            "report-only", "web-agent/추론", "M", 9,
            "N/A — 마크업 파일 없음(비-프론트엔드 저장소)",
            "마크업 파일(JSX/.html/.vue/.svelte)이 없어 해당 없음. 이 신호는 프론트엔드 UI 코드에만 적용된다.",
            {"markup_files": 0}, ["마크업 파일 없음 — 해당 없음(점수 미반영)."])
    interactive = native + nonsem_click
    # 지표: div-onclick(비시맨틱 클릭) 비율 + native-대체가능 role 비율 → 낮을수록 좋음(report-only 표시용).
    click_ratio = nonsem_click / max(1, interactive)
    role_ratio = role_native / max(1, role_total) if role_total else 0.0
    penalty = round(MAXP * min(1.0, click_ratio * 1.5)) + round(MAXP * 0.3 * min(1.0, role_ratio))
    score = max(0, MAXP - min(MAXP, penalty))
    if nonsem_click:
        findings.append(f"`<div/span onClick>` {nonsem_click}건 — native `<button>`/`<a>`로 승격 후보(키보드·포커스·역할 자동 획득). 승격은 행위 센서 관측·opt-in.")
    if role_native:
        findings.append(f"native 요소로 대체 가능한 `role=` {role_native}/{role_total}건 — 'First rule of ARIA'(native 우선). role로 native 시맨틱을 덮어쓰면 오히려 해로울 수 있음.")
    if img_noalt:
        findings.append(f"`alt` 없는 `<img>` {img_noalt}/{img}건 — alt 추가 후보. **자동 생성 alt/ARIA는 confident-but-wrong 위험**이라 사람 확인 필수(자동 채움 금지).")
    findings.append(f"[report-only] native 시맨틱 {native}건 · 비시맨틱 클릭 {nonsem_click}건 · ARIA 속성 {aria}건(볼륨은 가점 안 함) · role {role_total}건.")
    return Section(
        "C1", "Semantic Markup & a11y (시맨틱 마크업)", "context", score, MAXP,
        "report-only", "web-agent/추론", "M", 9,
        "삭제/교정 우선(native 대체 가능한 role= 제거)·`<div onClick>`→`<button>` 승격은 행위 센서 관측·opt-in·**자동 ARIA/alt 생성 금지**",
        "AI 가독성 이득은 **모델 역량 조건부**이고(강한 모델=full HTML 유리, 약한 모델=a11y-tree 유리) "
        "landmark/heading/button-vs-div를 격리 측정한 직접 연구는 없다 — 그래서 report-only. "
        "**ARIA/role 볼륨은 절대 가점하지 않는다**(WebAIM: ARIA 많을수록 오류↑·상관≠인과). native 시맨틱 사용만 신호.",
        {"markup_files": len(markup), "native_semantic": native, "nonsemantic_click": nonsem_click,
         "role_total": role_total, "role_with_native": role_native, "aria_attrs": aria,
         "img": img, "img_missing_alt": img_noalt},
        findings,
    )


def score_C2_test_legibility(files: list[Path]) -> Section:
    """테스트 코드의 설명 건강도. report-only(총점 미합산). 모호/오도 제목·비의미 셀렉터를
    결함 후보로 보고. 존재는 가점 안 하고, 오도/모호만 삭제·리네임 대상. 자동 어서션 생성 금지."""
    MAXP = 10
    test_files = [p for p in files if is_test_file(p)]
    titles: list[str] = []
    accessible = nonsemantic = 0
    for p in test_files:
        text = read_text(p)
        if not text:
            continue
        if p.suffix in PY_EXTS:
            titles.extend(m.group(1) for m in RE_PY_TEST_DEF.finditer(text))
        else:
            titles.extend(m.group(2) for m in RE_JS_TEST_TITLE.finditer(text))
        accessible += len(RE_ACCESSIBLE_QUERY.findall(text))
        nonsemantic += len(RE_NONSEMANTIC_QUERY.findall(text))
    if not test_files:
        return Section(
            "C2", "Test Legibility (테스트 설명 건강도)", "context", MAXP, MAXP,
            "report-only", "LLM(비대칭)", "S", 10,
            "N/A — 테스트 파일 없음",
            "테스트 파일(.test./.spec./test_*.py)이 없어 해당 없음.",
            {"test_files": 0}, ["테스트 파일 없음 — 해당 없음(점수 미반영)."])
    vague = 0
    for t in titles:
        norm = re.sub(r"[\s_]+", " ", t.strip().lower()).strip()
        norm2 = re.sub(r"^test\s*", "", norm).strip()
        if norm in VAGUE_TEST_TITLES or norm2 in VAGUE_TEST_TITLES or len(norm.split()) <= 1 or re.fullmatch(r"test\s*\d*", norm):
            vague += 1
    total_titles = max(1, len(titles))
    vague_ratio = vague / total_titles
    penalty = round(MAXP * min(1.0, vague_ratio * 2))
    score = max(0, MAXP - min(MAXP, penalty))
    findings: list[str] = []
    if vague:
        findings.append(f"모호/무의미 테스트 제목 {vague}/{len(titles)}건 — 의도(대상·동작·기대결과) 담도록 리네임 후보. **오도 제목은 삭제/교정**(오도 문서는 LLM 이해를 측정 가능하게 저해).")
    if nonsemantic:
        sel_ratio = accessible / max(1, accessible + nonsemantic)
        findings.append(f"비의미 셀렉터(testid/CSS/xpath) {nonsemantic}건 vs 접근성 셀렉터(getByRole/LabelText/Text) {accessible}건(의미 비율 {sel_ratio:.0%}) — getByRole류로 이관 후보(refactor-robust). 단 getByRole=green이어도 a11y 깨질 수 있어 axe 대체 아님·이관은 행위 센서 opt-in.")
    findings.append(f"[report-only] 테스트 제목 {len(titles)}건 · 모호 {vague}건 · 접근성 셀렉터 {accessible}/비의미 {nonsemantic}. **올바른 설명은 LLM 이해 이득이 미미**(개입 근거 약함)·**오도 설명만 측정 가능한 해악**이라 삭제-우선. **테스트를 오라클로 자동 생성·자동 어서션 금지**(구현을 굳혀 버그 은폐=green-locks-bug).")
    return Section(
        "C2", "Test Legibility (테스트 설명 건강도)", "context", score, MAXP,
        "report-only", "LLM(비대칭)", "S", 10,
        "삭제/리네임 우선(오도·모호 제목)·비의미 셀렉터→getByRole 이관은 행위 센서 opt-in·**자동 어서션/오라클 생성 금지**",
        "controlled 연구상 **올바른 문서/이름은 LLM 이해에 유의한 이득이 없고, 오도 문서만 측정 가능하게 해롭다**(비대칭). "
        "테스트를 LLM 최적화 오라클로 쓰면 구현을 굳혀 버그를 은폐한다(overfitting). "
        "제목↔본문 괴리는 컴파일러 미검증. accessible 셀렉터는 refactor-robust(MEDIUM)이나 AI 이해 향상 근거는 없음.",
        {"test_files": len(test_files), "titles": len(titles), "vague_titles": vague,
         "accessible_queries": accessible, "nonsemantic_queries": nonsemantic},
        findings,
    )


def build_report(repo: Path) -> Report:
    files = walk_code_files(repo)
    # 선언 수집(A1/A2)
    decls: list[Decl] = []
    for p in files:
        text = read_text(p)
        if not text:
            continue
        if p.suffix in PY_EXTS:
            decls.extend(extract_python_decls(text))
        elif p.suffix in JS_EXTS:
            decls.extend(extract_js_decls(text, p.suffix in JSX_EXTS))
    nodes = build_graph(repo, files)

    core_sections = [
        score_A1_identifiers(decls),
        score_A2_consistency(decls),
        score_A3_comments(files),
        score_B1_complexity(repo, files),
        score_B2_cohesion(repo, nodes),
        score_B3_duplication(repo, nodes),
        score_B4_cycles(nodes),
        score_B5_overabstraction(repo, nodes),
    ]
    # Tier C — AI-맥락 신호(report-only). 총점(A+B=100)에 합산하지 않는다.
    context_sections = [
        score_C1_semantic_markup(repo, files),
        score_C2_test_legibility(files),
    ]
    sections = core_sections + context_sections
    surface = [s for s in core_sections if s.tier == "surface"]
    design = [s for s in core_sections if s.tier == "design"]
    context = context_sections
    surface_score = sum(s.score for s in surface)
    surface_max = sum(s.max for s in surface)
    design_score = sum(s.score for s in design)
    design_max = sum(s.max for s in design)
    context_score = sum(s.score for s in context)
    context_max = sum(s.max for s in context)
    total = surface_score + design_score          # context 제외(report-only)

    improvement_order = [s.key for s in sorted(core_sections, key=lambda s: s.act_order)]
    context_order = [s.key for s in sorted(context, key=lambda s: s.act_order)]

    meta = {
        "tool": "design-principle-harness/score.py",
        "version": "0.3.0",
        "repo": str(repo.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_files": len(files),
        "declarations": len(decls),
        "graph_nodes": len(nodes),
        "python_only": all(p.suffix in PY_EXTS for p in files) if files else False,
    }
    return Report(
        meta=meta,
        total=total,
        band=band_of(total),
        tier_scores={
            "surface": {"score": surface_score, "max": surface_max, "confidence": "medium",
                        "note": "act-first — 명명/주석. 사람 근거 견고·'오도/stale' 신호는 LLM에도 해로워 가중↑(단 LLM 리네임 효과는 부호 불안정)."},
            "design": {"score": design_score, "max": design_max, "confidence": "weak/diagnostic",
                       "note": "defer — SOLID·복잡도·중복·DI/IoC·DRY/KISS/YAGNI. 전부 사람 대상 검증·약한 프록시·타당도(AI 가독성 예측)는 외삽. 진단(점수 목표 아님)."},
            "context": {"score": context_score, "max": context_max, "confidence": "report-only",
                        "note": "AI-맥락 신호(시맨틱 마크업·테스트 설명) — **총점(100)에 합산하지 않음**. 직접 개입 근거 없음(명명 채널만 실측 인과)·역량 조건부·ARIA 볼륨 가점 금지·자동 생성 금지. 존재는 가점 안 하고 오도/모호/native-대체가능만 개선 후보."},
        },
        sections=sections,
        improvement_order=improvement_order,
        extras={
            "honesty": [
                "총점은 인증/최적화 목표가 아니라 개선 우선순위용 진단 지표(design-debt hotspot 지도)다. Tier B 점수를 '목표'로 삼으면 Goodhart/reward-hacking(표면 변형 게임)을 부른다.",
                "**개입 연구 없음**: 어떤 점수를 올리면 같은 저장소에서 같은 에이전트 성공률이 오른다는 연구는 없다 — 구조/설계 점수는 측정된 예측자가 아니라 추론된 휴리스틱. 점수 델타를 리팩터 성과로 귀속하려면 같은 저장소 재측정 행위 probe 필요.",
                "**안전 기여 인증 아님**: 에이전트 기여의 가장 강한 신호(실행 가능 재현 테스트·의존성 무결성)는 이 스코어러 범위 밖이다.",
                "**두 축 등급**: 측정 신뢰도≠타당도 신뢰도. 정밀 계산(예: MI)이 타당도를 함의하지 않는다(MI는 원시 LoC보다 못한 예측력).",
                "가중치는 ad hoc이다 — 밴드가 ±가중 변동에도 유지되는지 감도로 보라. LOC/파일 수 증가는 점수를 올리면 안 된다.",
                "개선은 Step 2에서 쉬운 것(주석→명명)부터 사람 승인 뒤에, 구조(SOLID 등)는 opt-in.",
                "**Tier C(AI-맥락 신호)는 총점에 합산하지 않는 report-only다**: 시맨틱 마크업·a11y·테스트 설명은 AI 이해 이득이 **모델 역량 조건부**이거나(강한 모델=full HTML 유리) **개입 근거가 없다**(관용/추론). ARIA/role/셀렉터/설명 '볼륨'을 가점하면 안 되고(WebAIM: ARIA 많을수록 오류↑), 자동 ARIA/alt/어서션 생성은 confident-but-wrong·green-locks-bug 위험이라 금지. 개선은 삭제/교정 우선(오도 제목·native 대체가능 role)·승격은 행위 센서 opt-in.",
            ],
            "improvement_first": improvement_order[:3],
            "improvement_deferred": improvement_order[3:],
            "context_signals_order": context_order,
            "context_note": "Tier C는 total에 미포함(report-only). 사용자 요청으로 측정·개선 흐름은 제공하되, 점수 인증이 아니라 개선 후보 census로만 쓴다.",
        },
    )


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
def to_dict(rep: Report) -> dict[str, Any]:
    d = asdict(rep)
    return d


def render_markdown(rep: Report) -> str:
    L: list[str] = []
    L.append(f"# 설계 품질 점수표 — {rep.total}/100 · {rep.band}")
    L.append("")
    L.append(f"> ⚠️ 총점은 **인증이 아니라 개선 우선순위용 진단 지표**입니다. 점수를 목표로 최적화하지 마세요(Goodhart).")
    L.append("")
    L.append(f"- **Tier A 표면 가독성(act-first)**: {rep.tier_scores['surface']['score']}/{rep.tier_scores['surface']['max']} · confidence medium")
    L.append(f"- **Tier B 설계 원칙(defer·진단)**: {rep.tier_scores['design']['score']}/{rep.tier_scores['design']['max']} · confidence weak/diagnostic")
    ctx = rep.tier_scores.get("context")
    if ctx:
        L.append(f"- **Tier C AI-맥락 신호(report-only·총점 미포함)**: {ctx['score']}/{ctx['max']} · 시맨틱 마크업·테스트 설명 — 개선 후보 census(점수 인증 아님)")
    L.append("")
    L.append("## 섹션별 점수")
    L.append("")
    L.append("> Tier C(context)는 **총점 100에 합산하지 않는 report-only 신호**입니다 — 존재를 가점하지 않고 오도/모호/native-대체가능 항목만 개선 후보로 보고합니다.")
    L.append("")
    L.append("| # | 섹션 | Tier | 점수 | conf | 근거대상 | 난이도 | 개선순서 |")
    L.append("|---|------|------|------|------|----------|--------|----------|")
    for s in sorted(rep.sections, key=lambda s: (s.tier == "context", s.act_order)):
        note = " (미합산)" if s.tier == "context" else ""
        L.append(f"| {s.key} | {s.name} | {s.tier} | {s.score}/{s.max}{note} | {s.confidence} | {s.subjects} | {s.effort} | {s.act_order} |")
    L.append("")
    L.append("## 개선 순서(쉬운 것부터 · Tier A/B)")
    L.append("")
    for i, key in enumerate(rep.improvement_order, 1):
        s = next(x for x in rep.sections if x.key == key)
        L.append(f"{i}. **{s.key} {s.name}** — {s.fix_mechanism}")
    ctx_order = rep.extras.get("context_signals_order") or []
    if ctx_order:
        L.append("")
        L.append("### Tier C 개선 후보(opt-in · report-only · 총점 무관)")
        for key in ctx_order:
            s = next(x for x in rep.sections if x.key == key)
            L.append(f"- **{s.key} {s.name}** — {s.fix_mechanism}")
    L.append("")
    L.append("## 섹션 상세")
    for s in sorted(rep.sections, key=lambda s: s.act_order):
        L.append("")
        L.append(f"### {s.key} · {s.name}  —  {s.score}/{s.max} [{s.confidence}]")
        L.append(f"- 근거 대상: {s.subjects} · 개선 난이도: {s.effort} · 메커니즘: {s.fix_mechanism}")
        L.append(f"- ⚠️ caveat: {s.caveat}")
        for fnd in s.findings:
            L.append(f"- {fnd}")
    L.append("")
    L.append("---")
    L.append(f"_{rep.meta['tool']} v{rep.meta['version']} · 코드 파일 {rep.meta['code_files']} · 선언 {rep.meta['declarations']} · "
             f"측정만 수행(코드 수정 없음). 개선은 SKILL Step 2에서 섹션별 승인 뒤._")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="design-principle-harness 설계 품질 스코어러")
    ap.add_argument("repo", nargs="?", default=".", help="스캔할 저장소 경로(기본: .)")
    ap.add_argument("--json", metavar="OUT", help="JSON 출력 경로('-'=stdout)")
    ap.add_argument("--markdown", action="store_true", help="사람용 markdown을 stdout에 출력(기본)")
    args = ap.parse_args(argv)

    repo = Path(args.repo)
    if not repo.exists() or not repo.is_dir():
        print(f"error: {repo} 는 디렉터리가 아닙니다", file=sys.stderr)
        return 2
    try:
        rep = build_report(repo)
    except Exception as exc:  # noqa: BLE001 — 신뢰 불가 repo에서 부분 실패해도 죽지 않게
        print(f"error: 스캔 실패 — {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = json.dumps(to_dict(rep), ensure_ascii=False, indent=2)
        if args.json == "-":
            print(payload)
        else:
            Path(args.json).write_text(payload, encoding="utf-8")
            print(f"wrote {args.json}", file=sys.stderr)
        if not args.markdown:
            return 0
    print(render_markdown(rep))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
