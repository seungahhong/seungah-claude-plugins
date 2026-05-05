#!/bin/bash
# package-changed.sh — package.json 변경 시 의존성 변경 알림
# FileChanged hook (package.json matcher)

echo "[hooks] package.json이 변경되었습니다. npm install / yarn install 실행이 필요할 수 있습니다." >&2

# 변경된 의존성 확인
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
DIFF=$(git diff HEAD -- "$PROJECT_ROOT/package.json" 2>/dev/null)

if [ -n "$DIFF" ]; then
  ADDED=$(echo "$DIFF" | grep '^+.*":\s*"' | grep -v '^\+\+\+' | head -5)
  REMOVED=$(echo "$DIFF" | grep '^-.*":\s*"' | grep -v '^\-\-\-' | head -5)

  if [ -n "$ADDED" ]; then
    echo "[hooks] 추가된 의존성:" >&2
    echo "$ADDED" | sed 's/^+/  /' >&2
  fi
  if [ -n "$REMOVED" ]; then
    echo "[hooks] 제거된 의존성:" >&2
    echo "$REMOVED" | sed 's/^-/  /' >&2
  fi
fi

exit 0
