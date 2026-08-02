#!/usr/bin/env python3
"""evals.json의 근거 인용이 실제 shipped 파일에 존재하는지 검증한다.

왜 이 스크립트가 있는가
-----------------------
이 하네스의 수용 평가(evals.json)는 "shipped 파일이 불변식을 강제하는가"를
`file :: anchor` 인용으로 채점하는 design-conformance 방식이다. 그런데 인용은
사람이 손으로 적고 본문은 개정되므로, **인용은 조용히 썩는다.** 실제로 v0.1.0
2차 검증 개정에서 SKILL.md의 번호 목록이 밀리면서 인용 4건이 다른 항목을
가리키게 됐고, 아무도 알아채지 못한 채 27개 assertion이 전부 `passed: true`로
출하됐다.

자기보고를 확인으로 옮기지 말라는 것이 이 하네스의 논지다. 그러니 이 하네스의
평가도 저자의 선언이 아니라 **실행된 검사**여야 한다. 이 스크립트가 그 검사다.

인용 형식
---------
각 assertion의 `evidence`는 앵커 목록이다. 앵커 하나는 이렇게 쓴다:

    <파일명> :: <파일에 그대로 존재하는 문자열>

파일명은 플러그인 안에서 유일한 basename이면 된다(SKILL.md, quiz-design.md,
debt-cartographer.md ...). 앵커 문자열은 **파일에 있는 그대로**여야 한다 —
요약하거나 다듬으면 이 스크립트가 잡는다. 그게 요점이다.

여러 앵커는 `;`로 나눈다. 산문 설명을 덧붙이고 싶으면 앵커 목록 뒤에 `//`를
쓰고 자유롭게 적는다(검사 대상이 아니다).

사용법
------
    python3 evals/check_evidence.py            # 검증만
    python3 evals/check_evidence.py --write    # 검증 후 passed 필드를 결과로 갱신

종료 코드는 실패한 앵커 수(0이면 통과)다. CI에 걸 수 있다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = PLUGIN_ROOT / "evals" / "evals.json"
ANCHOR_SEP = "::"
COMMENT = "//"


def load_sources() -> dict[str, tuple[Path, str]]:
    """플러그인 안의 모든 .md를 basename으로 인덱싱한다."""
    sources: dict[str, tuple[Path, str]] = {}
    for path in sorted(PLUGIN_ROOT.rglob("*.md")):
        name = path.name
        if name in sources:
            # basename이 겹치면 인용이 모호해진다. 겹치지 않게 파일명을 짓는 게 규약.
            raise SystemExit(
                f"basename 충돌: {name} — {sources[name][0]} vs {path}. "
                "인용을 모호하게 만들므로 파일명을 유일하게 유지하라."
            )
        sources[name] = (path, path.read_text(encoding="utf-8"))
    return sources


def parse_anchors(evidence: str) -> list[tuple[str, str]]:
    body = evidence.split(COMMENT, 1)[0]
    anchors = []
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ANCHOR_SEP not in chunk:
            anchors.append(("", chunk))  # 형식 위반 — 아래에서 실패로 잡힌다
            continue
        fname, anchor = chunk.split(ANCHOR_SEP, 1)
        anchors.append((fname.strip(), anchor.strip()))
    return anchors


def check(write: bool) -> int:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    assertions = data["eval_metadata"]["assertions"]
    sources = load_sources()

    failures = 0
    for idx, assertion in enumerate(assertions):
        anchors = parse_anchors(assertion.get("evidence", ""))
        problems: list[str] = []

        if not anchors:
            problems.append("앵커가 없다 — 근거 없는 assertion은 통과로 셀 수 없다")

        for fname, anchor in anchors:
            if not fname:
                problems.append(f"형식 위반(`파일 :: 앵커` 아님): {anchor!r}")
            elif fname not in sources:
                problems.append(f"파일 없음: {fname}")
            elif anchor not in sources[fname][1]:
                problems.append(f"{fname}에 앵커 없음: {anchor!r}")

        passed = not problems
        if write:
            assertion["passed"] = passed
            assertion["checked_anchors"] = len(anchors)

        if problems:
            failures += len(problems)
            print(f"[FAIL #{idx:2d}] {assertion['text'][:70]}")
            for problem in problems:
                print(f"          {problem}")

    total = len(assertions)
    ok = total - sum(1 for a in assertions if not parse_anchors(a.get("evidence", "")) or
                     any(f not in sources or a2 not in sources[f][1]
                         for f, a2 in parse_anchors(a.get("evidence", "")) if f))
    print(f"\n{ok}/{total} assertion의 앵커가 전부 실재한다. 실패 앵커 {failures}건.")

    if write:
        EVALS_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"passed 필드를 검사 결과로 갱신했다 → {EVALS_PATH}")

    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="검증 결과를 evals.json의 passed 필드에 기록한다(저자 선언을 실행 결과로 대체)",
    )
    args = parser.parse_args()
    sys.exit(check(args.write))


if __name__ == "__main__":
    main()
