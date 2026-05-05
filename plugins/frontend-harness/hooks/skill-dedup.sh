#!/bin/bash
# skill-dedup.sh — SKILL.md 생성 전 중복 스킬 확인
# PreToolUse hook (Write matcher, pathPattern **/SKILL.md)

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

# SKILL.md 파일이 아니면 통과
case "$FILE_PATH" in
  */SKILL.md) ;;
  *) exit 0 ;;
esac

# 이미 존재하는 파일이면 통과 (수정은 허용)
[ -f "$FILE_PATH" ] && exit 0

# 새 스킬의 디렉토리명 추출
SKILL_DIR=$(dirname "$FILE_PATH")
SKILL_NAME=$(basename "$SKILL_DIR")

# 같은 이름의 스킬이 다른 경로에 이미 존재하는지 확인
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
EXISTING=$(find "$PROJECT_ROOT" -path "*/skills/$SKILL_NAME/SKILL.md" -not -path "$FILE_PATH" 2>/dev/null | head -1)

if [ -n "$EXISTING" ]; then
  echo "BLOCKED: 동일 이름의 스킬이 이미 존재합니다: $EXISTING" && exit 2
fi

exit 0
