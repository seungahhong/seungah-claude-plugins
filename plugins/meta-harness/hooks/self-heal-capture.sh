#!/usr/bin/env bash
# meta-harness self-heal capture hook (UserPromptSubmit)
# 사용자의 수정/보강/방향전환(redirect) 발화를 감지해 experience-store의 signals 레인에 원형 적재.
# 캡처 전용·비차단(항상 exit 0). 진단·패치·적용은 하지 않는다(=/meta-harness healer + 승인 게이트 소관).
#
# 역할 = "record an event"(사건 기록, 3층 모델 ①). UserPromptSubmit + exit 0 은 차단하지 않는 로깅 훅이다.
#   guardrail(강제)이 아니라 recorder(기록)다 — 강제가 필요하면 PreToolUse+exit2 같은 별도 장치가 맡는다.
#   왜 UserPromptSubmit인가: "사용자 발화를 매번 캡처"는 이 event의 정석 용도다(상황→event 선택은
#   skills/meta-harness/references/hook-lifecycle.md §3). 적재된 신호의 세션시작 표면화는 형제 훅 warm-start-nudge(SessionStart)가 맡는다.
#   (근거: code.claude.com/docs/en/hooks, code.claude.com/docs/en/hooks-guide, claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
# 적재 기준은 skills/meta-harness/references/data-capture-criteria.md (C1~C9)를 따른다:
#   C2 원문 보존(요약·절단 금지) · C4 그 순간 lightweight identifier(transcript_path) 고정 ·
#   C5 프로젝트 최상단(git root) 한 곳에 모음 · C6 status 부여 · C7 strong/weak 등급 + 흔한 한국어 교정어 포착.
#
# stdin: UserPromptSubmit 훅 payload(JSON). 프롬프트 텍스트 필드는 `.prompt`(2026-06-18 실측 확정).
#        공식 문서엔 미명시라 .user_prompt/.message/전체 payload로 방어적 폴백을 유지한다(견고성).
# 적재: {project-top}/.claude/experience-store/signals/<YYYY-MM-DD>.jsonl (append-only, 원문 보존, 요약 금지)
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
# C7: 흔한 한국어 교정어를 놓치지 않게 넓게 잡는다(빼줘/바꿔/빠졌/제거/누락 등). 놓친 신호는 흔적 없이 사라진다.
patterns="${SELF_HEAL_PATTERNS:-수정해|수정 좀|고쳐|고치|다시 해|다시해|다시 만들|재작성|왜 그렇게|왜 그랬|왜 이렇게|방향.*다시|이게 아니|그게 아니|아니라|틀렸|잘못|보강|개선해|반복.*안 ?하|빼줘|빼고|빼라|제거|지워|없애|바꿔|바꿀|바꾸|변경|빠졌|빠진|누락|안 ?보여|안 ?나와|왜 안|추가해|추가 좀|넣어|다시 ?(빌드|실행|돌려|시도)|재실행|재시도|fix this|fix it|redo|that.s wrong|thats wrong|not what i|try again|revise|why did you|why not|remove this|change it|missing|rebuild|rerun|run again|build again|retry}"
printf '%s' "$hay" | grep -iqE "$patterns" || exit 0   # 매칭 없으면 조용히 통과

kind="redirect"
printf '%s' "$hay" | grep -iqE "수정|고쳐|고치|틀렸|잘못|빼|제거|지워|없애|바꿔|변경|빠졌|누락|fix|wrong|remove|change|missing" && kind="fix"
printf '%s' "$hay" | grep -iqE "보강|개선|추가|넣어|augment|improve|enhance" && kind="augment"

# --- C7 신호 강도(strong|weak): '순수 재실행'만 약하게 강등 ---
# kind이 이미 fix/augment로 분류됐으면(빼/바꿔/빠졌/추가 등 실질 교정어 포함) 강등하지 않는다 —
# 'redirect'(재실행류 외 교정어 없음)인데 재실행 단어만 있고 교정 단어가 없을 때만 weak.
strength="strong"
if [ "$kind" = "redirect" ] && printf '%s' "$hay" | grep -iqE "다시 ?(빌드|실행|돌려|시도|run|build)|재시도|rebuild|run again|rerun|retry|build again"; then
  printf '%s' "$hay" | grep -iqE "틀렸|잘못|아니|전혀|방향|이게 아니|그게 아니|wrong|not what" || strength="weak"
fi

# --- 적재 위치: {cwd}/.claude/experience-store/signals/ (스토어 컨벤션 준수) ---
cwd=""; sid=""; tpath=""
if command -v jq >/dev/null 2>&1; then
  cwd="$(printf '%s' "$payload"   | jq -r '.cwd // empty' 2>/dev/null)"
  sid="$(printf '%s' "$payload"   | jq -r '.session_id // empty' 2>/dev/null)"
  tpath="$(printf '%s' "$payload" | jq -r '.transcript_path // empty' 2>/dev/null)"
elif command -v python3 >/dev/null 2>&1; then
  # jq 없을 때도 C4 lightweight identifier(cwd/session_id/transcript_path)가 비지 않게 python3 폴백
  cwd="$(printf '%s' "$payload"   | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("cwd") or "")' 2>/dev/null)"
  sid="$(printf '%s' "$payload"   | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("session_id") or "")' 2>/dev/null)"
  tpath="$(printf '%s' "$payload" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("transcript_path") or "")' 2>/dev/null)"
fi
cwd="${cwd:-$PWD}"
# C5: 프로젝트 최상단(git root)에 모은다 — 어느 하위 폴더에서 캡처해도 한 곳. git 밖이면 cwd로 폴백.
root="$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null || echo "$cwd")"
store="$root/.claude/experience-store/signals"
mkdir -p "$store" 2>/dev/null || exit 0
out="$store/$(date -u +%F).jsonl"; ts="$(date -u +%FT%TZ)"; raw="${prompt:-$payload}"

# 무한 성장 가드: 트리거 패턴에 흔한 단어(변경/추가해/missing 등)가 포함되어 있어
# 대용량 문서 붙여넣기도 전문 적재될 수 있다. 200KB 초과 발화는 교정 신호가 아니라
# 붙여넣기로 간주하고 스킵한다(transcript_path는 이미 캡처되므로 healer가 원문 역추적 가능).
# C2(원문 보존)는 '신호로 판정된 발화'에 적용되는 기준이며 이 임계 이하에선 그대로 유지된다.
[ "${#raw}" -gt 200000 ] && exit 0

# --- 레코드 append (원본 보존·요약 금지; jq로 안전 이스케이프, 없으면 python3) ---
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg ts "$ts" --arg kind "$kind" --arg strength "$strength" --arg raw "$raw" --arg sid "$sid" --arg cwd "$cwd" --arg root "$root" --arg tpath "$tpath" \
    '{ts:$ts,actor:"user",kind:$kind,strength:$strength,status:"new",source:"hook:UserPromptSubmit",session_id:$sid,cwd:$cwd,root:$root,transcript_path:$tpath,raw:$raw,captured_by:"meta-harness/self-heal-capture"}' >> "$out" 2>/dev/null
elif command -v python3 >/dev/null 2>&1; then
  TS="$ts" KIND="$kind" STRENGTH="$strength" CWD="$cwd" ROOT="$root" OUT="$out" RAW="$raw" SID="$sid" TP="$tpath" python3 -c '
import os,json
rec={"ts":os.environ["TS"],"actor":"user","kind":os.environ["KIND"],"strength":os.environ["STRENGTH"],"status":"new",
"source":"hook:UserPromptSubmit","session_id":os.environ["SID"],"cwd":os.environ["CWD"],"root":os.environ["ROOT"],
"transcript_path":os.environ["TP"],"raw":os.environ["RAW"],"captured_by":"meta-harness/self-heal-capture"}
open(os.environ["OUT"],"a").write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")' 2>/dev/null
fi
exit 0
