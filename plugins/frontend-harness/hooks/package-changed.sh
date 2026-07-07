#!/bin/bash
# package-changed.sh — package.json 변경 시 의존성 변경 알림
# PostToolUse hook (Edit|Write matcher) — 수정된 파일이 package.json일 때만 동작한다.
# 모노레포 대응: 루트 고정이 아니라 방금 수정된 package.json 자체를 diff한다.
set -u

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
FILE_PATH=$(hook_field '.tool_input.file_path') || true

[ -z "$FILE_PATH" ] && exit 0
[ "$(basename "$FILE_PATH")" = "package.json" ] || exit 0

echo "[hooks] package.json이 변경되었습니다. npm install / yarn install 실행이 필요할 수 있습니다." >&2

# 변경된 의존성 확인 (첫 커밋 전 등 diff 불가 시 조용히 통과)
DIFF=$(git diff HEAD -- "$FILE_PATH" 2>/dev/null)

if [ -n "$DIFF" ]; then
  ADDED=$(printf '%s\n' "$DIFF" | grep '^+.*":\s*"' | grep -v '^\+\+\+' | head -5)
  REMOVED=$(printf '%s\n' "$DIFF" | grep '^-.*":\s*"' | grep -v '^\-\-\-' | head -5)

  if [ -n "$ADDED" ]; then
    echo "[hooks] 추가된 의존성:" >&2
    printf '%s\n' "$ADDED" | sed 's/^+/  /' >&2
  fi
  if [ -n "$REMOVED" ]; then
    echo "[hooks] 제거된 의존성:" >&2
    printf '%s\n' "$REMOVED" | sed 's/^-/  /' >&2
  fi
fi

exit 0
