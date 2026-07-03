#!/bin/bash
# stop-lint.sh — lint 체인 실행 훅
# eslint --fix(ts,tsx,js,jsx) → stylelint --fix(css,scss) → prettier --write(ts,tsx,js,jsx)
# 이벤트별 분기:
#   PostToolUse(Edit|Write) → 방금 수정된 파일 1개만 린트 (전체 diff 재실행 방지)
#   Stop                    → git 변경 파일 전체에 lint 체인 실행
# 각 도구가 프로젝트에 설치되어 있지 않으면 건너뜀
# 모노레포 지원: 변경 파일 기준으로 가장 가까운 node_modules를 탐색
# 신뢰 전제: 변경 파일에서 가장 가까운 node_modules/.bin의 eslint/stylelint/prettier를
# 자동 실행한다. 신뢰할 수 없는 저장소에서는 이 플러그인 훅을 활성화하지 말 것.

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
EVENT=$(hook_field '.hook_event_name') || true

if [ "$EVENT" = "PostToolUse" ]; then
  # 방금 수정된 파일만 대상
  changed_files=$(hook_field '.tool_input.file_path') || true
  [ -z "$changed_files" ] && exit 0
else
  # Stop(또는 이벤트 판별 불가): git 변경 파일 전체 (staged + unstaged, 삭제 제외)
  changed_files=$(git -c core.quotepath=false diff --name-only --diff-filter=d HEAD 2>/dev/null)
  if [ -z "$changed_files" ]; then
    changed_files=$(git -c core.quotepath=false diff --name-only --cached --diff-filter=d 2>/dev/null)
  fi
fi

if [ -z "$changed_files" ]; then
  exit 0
fi

# 파일 경로에서 가장 가까운 node_modules/.bin 경로를 찾는 함수
# 파일의 디렉토리부터 위로 올라가며 node_modules/.bin 존재 여부를 확인
find_bin_dir() {
  local file="$1"
  local dir
  dir=$(dirname "$file")

  while [ "$dir" != "." ] && [ "$dir" != "/" ]; do
    if [ -d "$dir/node_modules/.bin" ]; then
      echo "$dir/node_modules/.bin"
      return 0
    fi
    dir=$(dirname "$dir")
  done

  # 루트(CWD)의 node_modules도 확인
  if [ -d "node_modules/.bin" ]; then
    echo "node_modules/.bin"
    return 0
  fi

  return 1
}

# bin_dir별로 파일을 그룹핑하여 실행 (bash 3.2 호환: 연관 배열 대신 "bin_dir|file" 쌍 사용)
js_pairs=()
css_pairs=()

while IFS= read -r file; do
  [ ! -f "$file" ] && continue

  ext="${file##*.}"
  bin_dir=$(find_bin_dir "$file") || continue

  case "$ext" in
    js|jsx|ts|tsx)
      js_pairs+=("${bin_dir}|${file}")
      ;;
    css|scss)
      css_pairs+=("${bin_dir}|${file}")
      ;;
  esac
done <<< "$changed_files"

# 쌍 배열에서 고유 bin_dir 목록 추출
unique_bins() {
  local pair
  for pair in "$@"; do
    echo "${pair%%|*}"
  done | sort -u
}

# 특정 bin_dir에 해당하는 파일 목록 추출
files_for_bin() {
  local target="$1"
  shift
  local pair
  for pair in "$@"; do
    if [ "${pair%%|*}" = "$target" ]; then
      echo "${pair#*|}"
    fi
  done
}

# --- Step 1: ESLint --fix ---
while IFS= read -r bin_dir; do
  [ -z "$bin_dir" ] && continue
  if [ -x "$bin_dir/eslint" ]; then
    files=()
    while IFS= read -r f; do
      [ -n "$f" ] && files+=("$f")
    done < <(files_for_bin "$bin_dir" "${js_pairs[@]}")
    [ ${#files[@]} -gt 0 ] && "$bin_dir/eslint" "${files[@]}" --fix --quiet 2>/dev/null || true
  fi
done < <(unique_bins "${js_pairs[@]}")

# --- Step 2: Stylelint --fix ---
while IFS= read -r bin_dir; do
  [ -z "$bin_dir" ] && continue
  if [ -x "$bin_dir/stylelint" ]; then
    files=()
    while IFS= read -r f; do
      [ -n "$f" ] && files+=("$f")
    done < <(files_for_bin "$bin_dir" "${css_pairs[@]}")
    [ ${#files[@]} -gt 0 ] && "$bin_dir/stylelint" "${files[@]}" --fix --quiet 2>/dev/null || true
  fi
done < <(unique_bins "${css_pairs[@]}")

# --- Step 3: Prettier --write ---
while IFS= read -r bin_dir; do
  [ -z "$bin_dir" ] && continue
  if [ -x "$bin_dir/prettier" ]; then
    files=()
    while IFS= read -r f; do
      [ -n "$f" ] && files+=("$f")
    done < <(files_for_bin "$bin_dir" "${js_pairs[@]}")
    [ ${#files[@]} -gt 0 ] && "$bin_dir/prettier" "${files[@]}" --write --no-error-on-unmatched-pattern 2>/dev/null || true
  fi
done < <(unique_bins "${js_pairs[@]}")

exit 0
