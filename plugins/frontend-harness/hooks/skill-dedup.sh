#!/bin/bash
# skill-dedup.sh — SKILL.md 생성 전 중복 스킬 확인
# PreToolUse hook (Write matcher) — 대상 판별은 아래 case의 */SKILL.md 가드가 담당한다.
# 파서(jq/python3)가 없으면 stderr 경고 후 통과한다(fail-open).
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
FILE_PATH=$(hook_field '.tool_input.file_path') || true

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
# git 밖이면 통과: pwd 폴백은 $HOME 등 거대 트리 find → 10s 타임아웃 → 조용한 fail-open이 됨
# (형제 훅 incremental-lint/stop-lint와 동일한 || exit 0 정책)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
# find -path는 글롭 패턴: 스킬명 속 * ? [ ] \ 가 매칭 의미를 바꾸지 않게 이스케이프
GLOB_SAFE_NAME=$(printf '%s' "$SKILL_NAME" | sed 's/[][*?\\]/\\&/g')
EXISTING=$(find "$PROJECT_ROOT" -path "*/skills/$GLOB_SAFE_NAME/SKILL.md" -not -path "$FILE_PATH" 2>/dev/null | head -1)

if [ -n "$EXISTING" ]; then
  echo "BLOCKED: 동일 이름의 스킬이 이미 존재합니다: $EXISTING" && exit 2
fi

exit 0
