#!/usr/bin/env bash
# meta-harness warm-start nudge hook (SessionStart)
# 세션 시작 시(모든 source: startup/resume/clear/compact — hooks.json에서 matcher 생략=전체), experience-store의 signals 레인에 쌓인 미소비(status:new)·강(strong) 신호가 있으면
# 짧게 한 줄로 알린다. 주입 전용·비차단(항상 exit 0) — 진단·패치·적용은 하지 않는다(=/meta-harness healer + 승인 게이트 소관).
#
# 왜 SessionStart인가(라이프사이클 선택 근거):
#   - "세션 시작마다 컨텍스트 주입"은 SessionStart event의 정석 용도다. SessionStart는 차단 불가 event이고,
#     exit 0 의 stdout이 Claude 컨텍스트에 추가된다(공식 문서 의역 — 영어 원문 verbatim은 미확보, 등급은 skills/meta-harness/references/hooks-grounding.md 참조).
#   - self-heal-capture(UserPromptSubmit)가 적재만 하던 신호를, healer(/meta-harness)를 매번 수동 호출하지 않아도
#     세션 시작 시 표면화해 cross-session 기억의 가치를 살린다(상황→event 선택은 hook-lifecycle.md §3).
#   - (근거: code.claude.com/docs/en/hooks · /docs/en/hooks-guide,
#      이벤트 선택은 skills/meta-harness/references/hook-lifecycle.md)
#
# 정직성: 정확한 "미소비" 집계는 index.json 소비 포인터를 보는 /meta-harness warm-start(Phase 1) 소관이다.
#   이 훅은 그걸 대신하지 않고 "최근 7일 status:new·strong" 근사치만 알린다(과대표기 가능성 명시). 신호가 없으면 침묵.
#   한계: 미소비 상태가 갱신/archive 되기 전까지는 자격 있는 세션 시작마다 같은 건을 반복 표면화할 수 있다(반복 nag 가능 — 정확 소비 집계는 /meta-harness).
# 비활성: env META_HARNESS_NUDGE=off|0|false|no 로 끌 수 있다.
set -u

case "${META_HARNESS_NUDGE:-on}" in off|0|false|no) exit 0;; esac

payload="$(cat)"

# --- cwd 추출 (self-heal-capture와 동일 폴백; 대부분의 hook payload에 cwd common field가 있으나 미보장 — 없으면 $PWD 폴백) ---
cwd=""
command -v jq >/dev/null 2>&1 && cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"
if [ -z "$cwd" ] && command -v python3 >/dev/null 2>&1; then
  cwd="$(printf '%s' "$payload" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("cwd") or "")' 2>/dev/null)"
fi
cwd="${cwd:-$PWD}"

# C5: 프로젝트 최상단(git root)에서 단일 signals 레인을 본다(self-heal-capture 적재 위치와 동일).
root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || echo "$cwd")"
store="$root/.claude/experience-store/signals"
[ -d "$store" ] || exit 0

# --- 최근 7일 날짜별 signals 파일에서 status:new + strength:strong 줄 수를 센다(archive/ 제외, 근사치) ---
count=0
while IFS= read -r f; do
  [ -n "$f" ] && [ -f "$f" ] || continue
  c="$(grep -E '"status":[[:space:]]*"new"' "$f" 2>/dev/null | grep -cE '"strength":[[:space:]]*"strong"' 2>/dev/null)"
  count=$((count + c))
done <<EOF
$(find "$store" -maxdepth 1 -name '*.jsonl' -mtime -7 2>/dev/null)
EOF

[ "$count" -gt 0 ] 2>/dev/null || exit 0

# SessionStart stdout → Claude 컨텍스트(한 줄, 근사치임을 명시). 적용은 승인 게이트 후에만.
printf '[meta-harness] 최근 7일 self-heal 신호 약 %s건(status:new·strong, 정확한 미소비 건수는 /meta-harness가 집계). 누적된 "수정/보강/방향전환" 요청을 "/meta-harness"로 진단·고도화할 수 있습니다 — 적용은 사용자 승인 게이트 통과 후에만.\n' "$count"
exit 0
