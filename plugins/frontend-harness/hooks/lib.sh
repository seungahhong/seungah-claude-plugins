#!/bin/bash
# lib.sh — 훅 공용 stdin JSON 파서
# jq 우선 → python3 폴백. 둘 다 없으면 stderr 경고 후 실패(호출부는 fail-open으로 통과).
# 사용법: 호출 스크립트에서 INPUT=$(cat) 후 hook_field '.tool_input.command' 호출.

# $1: jq 경로 표현식 (점 표기, 예: '.tool_input.file_path')
# 전역 $INPUT을 읽는다. 값이 없으면 빈 문자열, 파서 자체가 없으면 반환코드 1.
hook_field() {
  local path="$1"
  if command -v jq >/dev/null 2>&1; then
    printf '%s' "$INPUT" | jq -r "$path // empty" 2>/dev/null
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$INPUT" | HOOK_FIELD_PATH="$path" python3 -c "
import sys, json, os
try:
    d = json.load(sys.stdin)
    for k in os.environ['HOOK_FIELD_PATH'].lstrip('.').split('.'):
        d = d.get(k) if isinstance(d, dict) else None
    print(d if isinstance(d, str) else '')
except Exception:
    print('')
" 2>/dev/null
    return 0
  fi
  echo "[hooks] 경고: jq/python3가 없어 훅 stdin JSON을 파싱할 수 없습니다. 가드 없이 통과합니다." >&2
  return 1
}
