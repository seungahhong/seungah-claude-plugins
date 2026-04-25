#!/bin/bash
# Stop 훅: Claude Code 응답 완료 후 git 변경 파일에 대해 lint 체인 실행
# eslint --fix(ts,tsx,js,jsx) → stylelint --fix(css,scss) → prettier --write(ts,tsx,js,jsx)
# 각 도구가 프로젝트에 설치되어 있지 않으면 건너뜀
# 모노레포 지원: 변경 파일 기준으로 가장 가까운 node_modules를 탐색

# git 변경 파일 목록 수집 (staged + unstaged, 삭제된 파일 제외)
changed_files=$(git diff --name-only --diff-filter=d HEAD 2>/dev/null)
if [ -z "$changed_files" ]; then
  changed_files=$(git diff --name-only --cached --diff-filter=d 2>/dev/null)
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
