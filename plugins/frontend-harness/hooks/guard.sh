#!/bin/bash
# guard.sh — Bash 실행 전 위험 명령 차단
# PreToolUse hook (Bash matcher)
# 주의: regex 기반 advisory 가드다. 우회 가능하며 보안 경계(sandbox)가 아니다.
# 파서(jq/python3)가 없으면 stderr 경고 후 통과한다(fail-open — Bash 자체를 막지 않기 위함).
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
COMMAND=$(hook_field '.tool_input.command') || true

# 폴백: 환경변수 방식
if [ -z "$COMMAND" ]; then
  COMMAND="${TOOL_INPUT_COMMAND:-}"
fi
[ -z "$COMMAND" ] && exit 0

# 멀티라인 우회 차단: grep은 행 단위 매칭이라 라인 컨티뉴에이션(\ + 개행)으로
# 분리된 명령이 모든 규칙을 통과한다 → 개행·탭을 공백으로 평탄화 후 매칭
# (;로 이어진 별개 행을 한 행으로 보는 과차단 방향의 오차만 남음 — blocklist에 안전한 방향)
COMMAND=$(printf '%s' "$COMMAND" | tr '\n\t' '  ')

# git add . / git add ./ / git add -A 차단 (파일 명시 필요) — 결합형 짧은 플래그(-Av 등) 포함
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+add\s+(-[A-Za-z]*A[A-Za-z]*|--all|\./?)(\s|$)'; then
  echo "BLOCKED: 'git add .' / 'git add -A' 금지. 파일을 명시적으로 지정하세요." && exit 2
fi

# force push 차단
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+push\s+.*(--force|--force-with-lease|-f)(\s|$)'; then
  echo "BLOCKED: force push 금지." && exit 2
fi

# --no-verify 차단 (짧은 형태 -n 포함; --amend 등 --류 오탐 없게 단일 대시만)
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+commit\s+(.*\s)?(--no-verify|-[a-zA-Z]*n[a-zA-Z]*)(\s|$)'; then
  echo "BLOCKED: '--no-verify' 금지." && exit 2
fi

# git stash drop/clear 차단
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+stash\s+(drop|clear)'; then
  echo "BLOCKED: 'git stash drop/clear' 금지." && exit 2
fi

# 패키지 배포 차단
if printf '%s\n' "$COMMAND" | grep -qE '(yarn|npm|pnpm)\s+publish'; then
  echo "BLOCKED: 패키지 배포 금지." && exit 2
fi

# 루트/홈 삭제 차단 — 분리형 플래그(rm -r -f, --recursive --force)와 /* 도 커버
if printf '%s\n' "$COMMAND" | grep -qE 'rm\s+((-[A-Za-z]+|--recursive|--force|--no-preserve-root)\s+)+(/\*?|~/?|\$HOME/?)(\s|$)'; then
  echo "BLOCKED: 루트/홈 삭제 금지." && exit 2
fi

# DROP TABLE/DATABASE 차단
if printf '%s\n' "$COMMAND" | grep -qiE 'DROP\s+(TABLE|DATABASE)'; then
  echo "BLOCKED: DROP TABLE/DATABASE 금지." && exit 2
fi

# git reset --hard 차단
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+reset\s+--hard'; then
  echo "BLOCKED: 'git reset --hard' 금지." && exit 2
fi

# git checkout/restore . 차단 (git checkout -- . 형태 포함)
if printf '%s\n' "$COMMAND" | grep -qE 'git\s+(checkout|restore)\s+(--\s+)?\./?(\s|$)'; then
  echo "BLOCKED: 모든 변경사항 되돌리기 금지." && exit 2
fi

exit 0
