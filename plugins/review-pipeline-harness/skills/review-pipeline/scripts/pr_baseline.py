#!/usr/bin/env python3
"""review-pipeline 하네스 Phase 0 기준선 — 머지된 PR JSON에서 사람 시간 지표를 계산한다.

입력은 사용자가 받은 파일 하나다(네트워크 호출 없음, 읽기 전용):

    gh pr list --state merged --limit 200 \
      --json number,title,author,createdAt,mergedAt,additions,deletions,reviews,comments \
      > prs.json
    python3 pr_baseline.py prs.json [--json] [--bot-pattern REGEX] [--bot-login LOGIN ...]

출력 지표(metrics-guardrails.md §1):
  H1 PR당 사람 승인 수(median·p95, 봇 제외·작성자 제외·리뷰어 중복 제외)
  H2 PR당 사람 코멘트 수(봇 제외)
  H3 첫 사람 리뷰까지·머지까지 시간(시간 단위 median·p95)
  크기 분포, revert 제목 PR 비율(G1의 하한 근사)

점수·등급을 만들지 않는다. 기준선 관측값만 낸다.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime

DEFAULT_BOT_PATTERN = r"(\[bot\]$|^app/|bot$|^github-actions$)"
REVERT_PATTERN = re.compile(r"^\s*revert\b", re.IGNORECASE)
SIZE_BUCKETS = [(50, "<=50"), (200, "51-200"), (1000, "201-1000"), (math.inf, ">1000")]


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def login_of(obj: dict | None) -> str:
    if not obj:
        return ""
    author = obj.get("author") if "author" in obj else obj
    if not isinstance(author, dict):
        return ""
    return author.get("login") or ""


def percentile(values: list[float], pct: float) -> float | None:
    """nearest-rank 백분위수."""
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def summarize(values: list[float]) -> dict:
    return {"n": len(values), "median": percentile(values, 50), "p95": percentile(values, 95)}


def analyze(prs: list[dict], is_bot) -> dict:
    approvals, human_comments, first_review_h, merge_h = [], [], [], []
    sizes = {label: 0 for _, label in SIZE_BUCKETS}
    reverts = 0
    bot_logins: set[str] = set()
    bot_authored = 0

    for pr in prs:
        pr_author = login_of(pr)
        author_obj = pr.get("author") or {}
        if is_bot(pr_author) or author_obj.get("is_bot"):
            bot_authored += 1
            bot_logins.add(pr_author)
        created = parse_ts(pr.get("createdAt"))
        merged = parse_ts(pr.get("mergedAt"))

        approvers: set[str] = set()
        comment_count = 0
        first_human_review: datetime | None = None
        for review in pr.get("reviews") or []:
            who = login_of(review)
            if not who:
                continue
            if is_bot(who):
                bot_logins.add(who)
                continue
            if who == pr_author:
                continue
            state = (review.get("state") or "").upper()
            if state == "APPROVED":
                approvers.add(who)
            if state in ("COMMENTED", "CHANGES_REQUESTED") or (review.get("body") or "").strip():
                comment_count += 1
            ts = parse_ts(review.get("submittedAt"))
            if ts and (first_human_review is None or ts < first_human_review):
                first_human_review = ts
        for comment in pr.get("comments") or []:
            who = login_of(comment)
            if not who:
                continue
            if is_bot(who):
                bot_logins.add(who)
                continue
            comment_count += 1

        approvals.append(float(len(approvers)))
        human_comments.append(float(comment_count))
        if created and first_human_review:
            first_review_h.append((first_human_review - created).total_seconds() / 3600)
        if created and merged:
            merge_h.append((merged - created).total_seconds() / 3600)

        churn = (pr.get("additions") or 0) + (pr.get("deletions") or 0)
        for limit, label in SIZE_BUCKETS:
            if churn <= limit:
                sizes[label] += 1
                break
        if REVERT_PATTERN.match(pr.get("title") or ""):
            reverts += 1

    total = len(prs)
    no_human_review = sum(1 for a in approvals if a == 0)
    return {
        "pr_count": total,
        "H1_human_approvals_per_pr": summarize(approvals),
        "H1_prs_with_zero_human_approvals": no_human_review,
        "H2_human_comments_per_pr": summarize(human_comments),
        "H3_hours_to_first_human_review": summarize(first_review_h),
        "H3_hours_to_merge": summarize(merge_h),
        "size_distribution_lines_changed": sizes,
        "G1_revert_titled_prs": {
            "count": reverts,
            "share": (reverts / total) if total else None,
            "note": "제목이 'Revert'로 시작하는 PR만 센 하한 근사. 제목 규약을 따르지 않는 revert·hotfix는 세지 못한다.",
        },
        "bot_authored_prs": bot_authored,
        "bot_logins_detected": sorted(bot_logins),
    }


def fmt(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def render_table(result: dict, pattern: str) -> str:
    lines = [f"PR {result['pr_count']}건 기준선 (점수 아님 — 관측값)", ""]
    lines.append("| 지표 | n | median | p95 |")
    lines.append("|------|---|--------|-----|")
    for key, label in [
        ("H1_human_approvals_per_pr", "H1 PR당 사람 승인 수"),
        ("H2_human_comments_per_pr", "H2 PR당 사람 코멘트 수"),
        ("H3_hours_to_first_human_review", "H3 첫 사람 리뷰까지(시간)"),
        ("H3_hours_to_merge", "H3 머지까지(시간)"),
    ]:
        s = result[key]
        lines.append(f"| {label} | {s['n']} | {fmt(s['median'])} | {fmt(s['p95'])} |")
    lines.append("")
    lines.append(f"- 사람 승인 0건으로 머지된 PR: {result['H1_prs_with_zero_human_approvals']}건")
    sizes = ", ".join(f"{k}: {v}" for k, v in result["size_distribution_lines_changed"].items())
    lines.append(f"- 크기 분포(변경 줄 수): {sizes}")
    g1 = result["G1_revert_titled_prs"]
    share = f"{g1['share'] * 100:.1f}%" if g1["share"] is not None else "-"
    lines.append(f"- G1 revert 제목 PR: {g1['count']}건 ({share}) — {g1['note']}")
    lines.append(f"- 봇 작성 PR: {result['bot_authored_prs']}건")
    detected = ", ".join(result["bot_logins_detected"]) or "없음"
    lines.append(f"- 봇으로 판정한 계정: {detected}")
    lines.append(f"- 봇 판정 패턴: `{pattern}` (+ --bot-login). 판정이 틀리면 패턴을 바꿔 다시 돌린다.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", help="gh pr list --json 출력 파일")
    parser.add_argument("--json", action="store_true", help="JSON으로 출력")
    parser.add_argument("--bot-pattern", default=DEFAULT_BOT_PATTERN, help="봇 계정 login 정규식")
    parser.add_argument("--bot-login", action="append", default=[], help="봇으로 취급할 login(반복 가능)")
    args = parser.parse_args(argv)

    try:
        with open(args.path, encoding="utf-8") as fh:
            prs = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"입력을 읽을 수 없다: {exc}", file=sys.stderr)
        return 2
    if not isinstance(prs, list):
        print("입력은 gh pr list --json 이 내는 배열이어야 한다.", file=sys.stderr)
        return 2

    regex = re.compile(args.bot_pattern, re.IGNORECASE)
    extra = {login.lower() for login in args.bot_login}

    def is_bot(login: str) -> bool:
        return bool(login) and (login.lower() in extra or bool(regex.search(login)))

    result = analyze(prs, is_bot)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_table(result, args.bot_pattern))
    return 0


if __name__ == "__main__":
    sys.exit(main())
