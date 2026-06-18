#!/usr/bin/env bash
# meta-harness self-heal capture hook (UserPromptSubmit)
# 사용자의 수정/보강/방향전환(redirect) 발화를 감지해 experience-store의 signals 레인에 원형 적재.
# 캡처 전용·비차단(항상 exit 0). 진단·패치·적용은 하지 않는다(=/meta-harness healer + 승인 게이트 소관).
#
# stdin: UserPromptSubmit 훅 payload(JSON). 프롬프트 텍스트 필드는 `.prompt`(2026-06-18 실측 확정).
#        공식 문서엔 미명시라 .user_prompt/.message/전체 payload로 방어적 폴백을 유지한다(견고성).
# 적재: {cwd}/.claude/experience-store/signals/<YYYY-MM-DD>.jsonl (append-only, 원문 보존, 요약 금지)
# 오버라이드: env SELF_HEAL_PATTERNS 로 트리거 패턴 교체 가능.
set -u
payload="$(cat)"

# --- 프롬프트 텍스트 추출 (.prompt 실측 확정; 폴백은 견고성 위해 유지) ---
prompt=""
command -v jq >/dev/null 2>&1 && prompt="$(printf '%s' "$payload" | jq -r '.prompt // .user_prompt // .message // empty' 2>/dev/null)"
if [ -z "$prompt" ] && command -v python3 >/dev/null 2>&1; then
  prompt="$(printf '%s' "$payload" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("prompt") or d.get("user_prompt") or d.get("message") or "")' 2>/dev/null)"
fi
hay="${prompt:-$payload}"   # 추출 실패 시 전체 payload를 매칭 대상으로

# --- redirect/fix/augment 의도 매칭 (오버라이드: env SELF_HEAL_PATTERNS) ---
patterns="${SELF_HEAL_PATTERNS:-수정해|수정 좀|고쳐|고치|다시 해|다시해|다시 만들|재작성|왜 그렇게|왜 그랬|왜 이렇게|방향.*다시|이게 아니|그게 아니|아니라|틀렸|잘못|보강|개선해|반복.*안 ?하|fix this|fix it|redo|that.s wrong|thats wrong|not what i|try again|revise|why did you}"
printf '%s' "$hay" | grep -iqE "$patterns" || exit 0   # 매칭 없으면 조용히 통과

kind="redirect"
printf '%s' "$hay" | grep -iqE "수정|고쳐|고치|틀렸|잘못|fix|wrong" && kind="fix"
printf '%s' "$hay" | grep -iqE "보강|개선|augment|improve|enhance" && kind="augment"

# --- 적재 위치: {cwd}/.claude/experience-store/signals/ (스토어 컨벤션 준수) ---
cwd=""; sid=""; tpath=""
if command -v jq >/dev/null 2>&1; then
  cwd="$(printf '%s' "$payload"   | jq -r '.cwd // empty' 2>/dev/null)"
  sid="$(printf '%s' "$payload"   | jq -r '.session_id // empty' 2>/dev/null)"
  tpath="$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null)"
fi
cwd="${cwd:-$PWD}"
store="$cwd/.claude/experience-store/signals"
mkdir -p "$store" 2>/dev/null || exit 0
out="$store/$(date -u +%F).jsonl"; ts="$(date -u +%FT%TZ)"; raw="${prompt:-$payload}"

# --- 레코드 append (원본 보존·요약 금지; jq로 안전 이스케이프, 없으면 python3) ---
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg ts "$ts" --arg kind "$kind" --arg raw "$raw" --arg sid "$sid" --arg cwd "$cwd" --arg tpath "$tpath" \
    '{ts:$ts,actor:"user",kind:$kind,source:"hook:UserPromptSubmit",session_id:$sid,cwd:$cwd,transcript_path:$tpath,raw:$raw,captured_by:"meta-harness/self-heal-capture"}' >> "$out" 2>/dev/null
elif command -v python3 >/dev/null 2>&1; then
  TS="$ts" KIND="$kind" CWD="$cwd" OUT="$out" RAW="$raw" SID="$sid" TP="$tpath" python3 -c '
import os,json
rec={"ts":os.environ["TS"],"actor":"user","kind":os.environ["KIND"],"source":"hook:UserPromptSubmit",
"session_id":os.environ["SID"],"cwd":os.environ["CWD"],"transcript_path":os.environ["TP"],
"raw":os.environ["RAW"],"captured_by":"meta-harness/self-heal-capture"}
open(os.environ["OUT"],"a").write(json.dumps(rec,ensure_ascii=False)+"\n")' 2>/dev/null
fi
exit 0
