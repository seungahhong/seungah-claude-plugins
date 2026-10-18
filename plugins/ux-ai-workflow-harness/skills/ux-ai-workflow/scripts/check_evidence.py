#!/usr/bin/env python3
"""근거 앵커 검증 — 플러그인 문서가 인용하는 E·X번호가 evidence.md에 실재하는지, 금지 문구를 쓰지 않았는지 검사한다.

이 하네스는 "AI가 낸 출처는 사람이 열어 보기 전까지 확인이 아니다"를 규칙으로 둔다.
그래서 자기 문서의 인용도 실행된 검사로 확인한다.
한계: 정규식 휴리스틱이다. 표현을 바꾼 효과 약속·점수는 놓칠 수 있다 — 통과는 '알려진 형태가 없다'는 뜻이지 위반이 없다는 증명이 아니다.

사용법:
    python3 check_evidence.py                 # 플러그인 루트를 자동 탐색
    python3 check_evidence.py <plugin-root>
종료 코드: 0 통과 / 1 실패
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# evidence.md 인용 금지 목록(X1~X15)의 주장 형태. 다른 문서에 나타나면 하네스가 스스로 금지한 주장을 하는 것이다.
FORBIDDEN_OUTSIDE_EVIDENCE = [
    ("생산성 66%/126% (X1)", r"(66|126)\s*%"),
    ("트윈·합성 85%/0.85 (X2·X15)", r"85\s*%|0\.85"),
    ("아이디어 품질 3배 (X3)", r"(품질|아이디어)[^\n]{0,12}3\s*배"),
    ("judge F1 0.8 기준 (X5)", r"F1\s*0\.8"),
    ("UX-Ray 95% (X11)", r"95\s*%"),
    ("효과 N% 약속 (X12)", r"\d+\s*(%|퍼센트|프로)[^\n]{0,10}(향상|개선|증가|빨라|단축|줄|올라|오른|올린|끌어올|높아|높인|좋아)"),
    ("효과 N배 약속 (X12)", r"(\d+|두|세|네|몇)\s*배[^\n]{0,8}(빨라|좋아|향상|개선|늘|높아|가 된|로 된)"),
]

# 산출물 규약: 점수·등급 어휘(INV-6).
SCORE_WORDS = [
    ("성숙도 등급", r"성숙도\s*(등급|레벨|L[1-5])"),
    ("종합 점수", r"종합\s*점수"),
    ("N점 만점·점수 수치", r"(점수|평점|총점)\s*[:=]?\s*\d+(\.\d+)?\s*(/|점)"),
    ("성숙도 N단계", r"성숙도\s*\d+\s*단계"),
]

# 허용 규칙: 금지 문구 앞뒤 WINDOW자 안에 인용 금지 번호(X1~X15)나 '금지' 표지가 있을 때만 허용한다.
# 교정표·금지 선언처럼 수치를 '바로잡기 위해' 인용하는 줄은 X번호를 함께 적어야 통과한다.
# 같은 줄 아무 데나 '없다'·'아니다'가 있다고 허용하던 이전 규칙은 실제 위반을 통과시켜 폐기했다.
# X번호는 ±80자, '금지'·'만들지 않'은 ±25자 안에 있어야 한다(무관한 '금지'가 먼 곳에 있어 통과하는 것을 막는다).
# 숫자 뒤에 한글 조사가 붙어도 인식되도록 \b 대신 영숫자 경계만 본다.
X_RE = re.compile(r"(?<![A-Za-z0-9])X\d+(?!\d)")
NEG_RE = re.compile(r"금지|만들지 않")
X_WINDOW, NEG_WINDOW = 80, 25


def _window(text: str, start: int, end: int, width: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    line_end = len(text) if line_end == -1 else line_end
    return text[max(line_start, start - width): min(line_end, end + width)]


def is_allowed(text: str, start: int, end: int) -> bool:
    return bool(X_RE.search(_window(text, start, end, X_WINDOW)) or NEG_RE.search(_window(text, start, end, NEG_WINDOW)))


def find_root(argv: list[str]) -> Path:
    if len(argv) > 1:
        return Path(argv[1]).resolve()
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "skills").is_dir() and (p / ".claude-plugin").is_dir():
            return p
    return here.parents[3]


def main() -> int:
    root = find_root(sys.argv)
    ev_candidates = list(root.glob("skills/*/references/evidence.md"))
    if not ev_candidates:
        print(f"FAIL: evidence.md를 찾지 못했다 (root={root})")
        return 1
    evidence_path = ev_candidates[0]
    evidence = evidence_path.read_text(encoding="utf-8")

    defined_e = set(re.findall(r"^\*\*(E\d+)\b", evidence, flags=re.M))
    defined_x = set(re.findall(r"^\|\s*(X\d+)\s*\|", evidence, flags=re.M))
    if not defined_e or not defined_x:
        print("FAIL: evidence.md에 정의된 E번호 또는 X번호가 없다")
        return 1

    failures: list[str] = []
    checked_files = 0
    allowed_negated = 0

    # evidence.md 자체 무결성: 본문 E 항목이 모두 등급 라벨을 갖는가(E2는 구조적 관찰).
    for fid, rest in re.findall(r"^\*\*(E\d+)\s*([^*]*)\*\*", evidence, flags=re.M):
        if "`[" not in rest and "[구조적 관찰]" not in rest:
            failures.append(f"evidence.md: {fid}에 등급 라벨이 없다")
    # evidence.md 내부의 E 교차참조도 정의돼 있어야 한다.
    for cited in sorted(set(re.findall(r"(?<![A-Za-z0-9])E(\d+)(?!\d)", evidence))):
        if f"E{cited}" not in defined_e:
            failures.append(f"evidence.md: 정의되지 않은 내부 참조 E{cited}")

    targets = sorted(root.rglob("*.md")) + sorted(root.glob(".claude-plugin/*.json"))
    for md in targets:
        if md == evidence_path:
            continue
        text = md.read_text(encoding="utf-8")
        checked_files += 1
        rel = md.relative_to(root)

        for cited in sorted(set(re.findall(r"(?<![A-Za-z0-9])E(\d+)(?!\d)", text))):
            if f"E{cited}" not in defined_e:
                failures.append(f"{rel}: 정의되지 않은 근거 앵커 E{cited}")
        for cited in sorted(set(re.findall(r"(?<![A-Za-z0-9])X(\d+)(?!\d)", text))):
            if f"X{cited}" not in defined_x:
                failures.append(f"{rel}: 정의되지 않은 인용 금지 번호 X{cited}")

        for label, pat in FORBIDDEN_OUTSIDE_EVIDENCE + SCORE_WORDS:
            for m in re.finditer(pat, text):
                lineno = text[: m.start()].count("\n") + 1
                if is_allowed(text, m.start(), m.end()):
                    allowed_negated += 1
                    continue
                failures.append(f"{rel}:{lineno}: 금지 문구 사용 ({label}) — '{m.group(0)}'")

    print(
        f"검사한 문서: {checked_files}개 · 정의 앵커 E {len(defined_e)}개 / X {len(defined_x)}개 "
        f"· 금지 표지 근처라 허용: {allowed_negated}건"
    )
    if failures:
        print(f"\nFAIL {len(failures)}건")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS — 정의되지 않은 앵커 없음, 인용 금지 문구 없음, 점수 어휘 없음")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
