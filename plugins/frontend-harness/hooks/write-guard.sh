#!/bin/bash
# write-guard.sh — Write 실행 전 민감 파일 생성 차단
# PreToolUse hook (Write matcher)

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0

BASENAME=$(basename "$FILE_PATH")

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
