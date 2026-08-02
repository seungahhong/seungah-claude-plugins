#!/usr/bin/env python3
"""근거 앵커 검증 — 플러그인 문서가 인용하는 F번호가 evidence.md에 실재하는지, 금지 문구를 쓰지 않았는지 검사한다.

이 하네스의 논지가 "자기보고를 확인으로 옮기지 마라"이므로, 자기 문서의 인용도 실행된 검사로 확인한다.

사용법:
    python3 check_evidence.py                 # 플러그인 루트를 자동 탐색
    python3 check_evidence.py <plugin-root>
종료 코드: 0 통과 / 1 실패
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# evidence.md 안에서만 등장해야 하는 문구(인용 금지 목록의 원문 형태).
# 다른 문서에 나타나면 하네스가 스스로 금지한 주장을 하고 있다는 뜻이다.
FORBIDDEN_OUTSIDE_EVIDENCE = [
    ("토큰 상한 수치", r"<\s*15,?000|<\s*25,?000|<\s*20,?000"),
    ("100K~200K 실사용 한도", r"100K\s*[-~–]\s*200K"),
    ("193,217 토큰을 실측처럼", r"193,?217"),
    ("가시성 40% 전이", r"가시성[^\n]{0,12}40\s*%"),
    ("개선 N% 보장", r"(정확도|성능)[^\n]{0,10}(향상|개선)[^\n]{0,6}보장"),
]

# 하네스 산출물 규약: 점수·등급 어휘를 스킬 본문에서 쓰지 않는다(INV-3).
SCORE_WORDS = [
    ("성숙도 등급", r"성숙도\s*(등급|레벨)"),
    ("종합 점수", r"종합\s*점수"),
]

# 금지 문구를 "쓰지 않는다"고 선언하는 문장은 위반이 아니다.
# 같은 줄에 아래 표지가 있으면 부정 맥락으로 보고 허용하되, 몇 건이 허용됐는지 보고한다.
# 한계: 줄 단위 휴리스틱이라 한 줄에 금지 주장과 부정이 섞이면 놓칠 수 있다.
NEGATION_MARKERS = [
    "금지", "쓰지 않", "만들지 않", "하지 않", "없다", "아니다", "위반",
    "존재하지 않", "권고하지 않", "인용 금지", "MISSTATED", "오인용",
]


def is_negated(line: str) -> bool:
    return any(m in line for m in NEGATION_MARKERS)


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

    defined = set(re.findall(r"\*\*(F\d+)\b", evidence))
    if not defined:
        print("FAIL: evidence.md에 정의된 F번호가 없다")
        return 1

    failures: list[str] = []
    checked_files = 0
    allowed_negated = 0

    for md in sorted(root.rglob("*.md")):
        if md == evidence_path:
            continue
        text = md.read_text(encoding="utf-8")
        checked_files += 1
        rel = md.relative_to(root)

        for cited in sorted(set(re.findall(r"\bF(\d+)\b", text))):
            token = f"F{cited}"
            if token not in defined:
                failures.append(f"{rel}: 정의되지 않은 근거 앵커 {token}")

        lines = text.split("\n")
        for label, pat in FORBIDDEN_OUTSIDE_EVIDENCE:
            for m in re.finditer(pat, text):
                lineno = text[: m.start()].count("\n") + 1
                if is_negated(lines[lineno - 1]):
                    allowed_negated += 1
                    continue
                failures.append(f"{rel}:{lineno}: 인용 금지 문구 사용 ({label}) — '{m.group(0)}'")

        for label, pat in SCORE_WORDS:
            for m in re.finditer(pat, text):
                lineno = text[: m.start()].count("\n") + 1
                if is_negated(lines[lineno - 1]):
                    allowed_negated += 1
                    continue
                failures.append(f"{rel}:{lineno}: 점수·등급 어휘 사용 ({label}) — INV-3 위반")

    # evidence.md 자체 무결성: 모든 F번호가 등급 라벨을 갖는가
    for block in re.findall(r"\*\*(F\d+)\*\*\s*(`\[[A-Z\-]+[^`]*`)?", evidence):
        fid, grade = block
        if not grade and fid not in ("F1", "F24", "F35"):  # F1/F24/F35는 판정·구조 항목
            failures.append(f"evidence.md: {fid}에 등급 라벨이 없다")

    print(
        f"검사한 문서: {checked_files}개 · evidence.md 정의 앵커: {len(defined)}개 "
        f"· 부정 맥락으로 허용: {allowed_negated}건"
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
