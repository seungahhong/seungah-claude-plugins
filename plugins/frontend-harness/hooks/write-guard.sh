#!/bin/bash
# write-guard.sh — Write 실행 전 민감 파일 생성 차단
# PreToolUse hook (Write matcher)
# 주의: Write 도구만 가드한다(Bash 리다이렉션·Edit 경유 생성은 범위 밖). advisory 가드.
# 파서(jq/python3)가 없으면 stderr 경고 후 통과한다(fail-open).
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
FILE_PATH=$(hook_field '.tool_input.file_path') || true

[ -z "$FILE_PATH" ] && exit 0

BASENAME=$(basename "$FILE_PATH")
# macOS APFS/Windows NTFS는 기본 대소문자 무시라 .ENV/server.PEM 등이 가드를 우회 → 소문자 정규화 후 매칭
BASENAME=$(printf '%s' "$BASENAME" | tr '[:upper:]' '[:lower:]')

# .env 파일 생성 차단
case "$BASENAME" in
  .env|.env.local|.env.production|.env.development|.env.staging)
    echo "BLOCKED: '$BASENAME' 파일 생성 금지. 환경변수 파일은 직접 관리하세요." && exit 2
    ;;
esac

# 인증서/키 파일 생성 차단
case "$BASENAME" in
  *.pem|*.key|*.p12|*.pfx|*.jks)
    echo "BLOCKED: 인증서/키 파일('$BASENAME') 생성 금지." && exit 2
    ;;
esac

# 시크릿/자격증명 파일 차단
case "$BASENAME" in
  credentials.json|secrets.json|service-account.json)
    echo "BLOCKED: 자격증명 파일('$BASENAME') 생성 금지." && exit 2
    ;;
esac

exit 0
