#!/bin/bash
# stop-lint.sh — Stop 시점 lint 체인 실행 훅
# eslint --fix(js,jsx,ts,tsx) → stylelint --fix(css,scss) → prettier --write(js,jsx,ts,tsx)
# 이벤트별 분기:
#   Stop                    → git 변경 파일 전체(staged+unstaged, 삭제 제외)에 lint 체인 실행
#   PostToolUse(Edit|Write) → 방금 수정된 파일 1개만 (현재 배선은 incremental-lint.sh가 담당하며,
#                             stop-lint을 직접 PostToolUse에 배선했을 때의 폴백으로 분기는 유지)
# 각 도구가 프로젝트에 설치되어 있지 않으면 건너뜀. 모노레포: 변경 파일 기준 가장 가까운 node_modules 탐색.
# 안전: 바이너리 탐색은 git 프로젝트 루트까지로 제한하고, 후보 .bin 디렉토리와 도구 바이너리를
#       물리 경로(심링크 해석)로 재검증해 루트 내부일 때만 실행 — 프로젝트 밖(예: /tmp)의 공격자
#       바이너리를 `node_modules`→루트밖 심링크로 끌어와 실행하는 경계 우회를 차단한다
#       (incremental-lint.sh와 동일 정책). 신뢰할 수 없는 저장소에서는 이 훅을 활성화하지 말 것.
# 실패 전파: Stop은 전체 diff 정리(best-effort)이므로 도구 에러를 삼키고 통과한다(비차단).
#            편집 단위 실패 전파(exit 2)는 PostToolUse의 incremental-lint.sh가 담당한다.

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

[ -z "$changed_files" ] && exit 0

# 탐색 경계: 프로젝트 루트(물리 경로). git repo가 아니면 경계를 정할 수 없어 스킵.
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -z "$PROJECT_ROOT" ] && exit 0
PROJECT_ROOT=$(cd "$PROJECT_ROOT" 2>/dev/null && pwd -P) || exit 0

# 물리 경로 $1이 프로젝트 루트 내부인지 판정 (경계 검사 공용)
under_root() {
  case "$1/" in "$PROJECT_ROOT"/*) return 0 ;; esac
  return 1
}

# 심링크 체인을 물리 경로로 해석해 출력. 순환/과다 홉은 실패(반환 1).
# 정상 npm/pnpm의 node_modules/.bin/<tool>(상대 심링크)도 여기서 실체 위치(루트 내부)로 해석된다.
resolve_symlink() {
  local p="$1" hops=0 t d
  while [ -L "$p" ] && [ "$hops" -lt 40 ]; do
    t=$(readlink "$p") || return 1
    case "$t" in
      /*) p="$t" ;;
      *)  p="$(dirname "$p")/$t" ;;
    esac
    hops=$((hops + 1))
  done
  [ -L "$p" ] && return 1
  d=$(cd "$(dirname "$p")" 2>/dev/null && pwd -P) || return 1
  echo "$d/$(basename "$p")"
}

# 파일 디렉토리부터 프로젝트 루트까지 올라가며 node_modules/.bin 탐색.
# 물리 경로로 해석해 루트 내부일 때만 채택, 아니면 상위로 계속 탐색한다 — 보안 경계는 유지
# (루트 밖 경로는 절대 반환 안 함)하면서 상위의 정상 in-repo .bin으로 폴백한다.
find_bin_dir() {
  local dir real
  dir=$(dirname "$1")
  while [ -n "$dir" ] && [ "$dir" != "/" ]; do
    if [ -d "$dir/node_modules/.bin" ]; then
      if real=$(cd "$dir/node_modules/.bin" 2>/dev/null && pwd -P); then
        under_root "$real" && { echo "$real"; return 0; }
      fi
    fi
    [ "$dir" = "$PROJECT_ROOT" ] && break
    dir=$(dirname "$dir")
  done
  return 1
}

# 도구 실체(심링크 해석 후)가 루트 내부면 그 물리 경로를 출력, 아니면 실패(실행 금지).
# 실행은 이 물리 경로로 하여 검사 대상과 실행 대상을 일치시킨다(TOCTOU 여지 제거).
resolve_tool() {
  local bin="$1" real
  [ -x "$bin" ] || return 1
  real=$(resolve_symlink "$bin") || return 1
  under_root "$real" || return 1
  [ -x "$real" ] || return 1
  echo "$real"
}

# bin_dir별로 파일을 그룹핑하여 실행 (bash 3.2 호환: 연관 배열 대신 "bin_dir|file" 쌍 사용)
js_pairs=()
css_pairs=()

while IFS= read -r file; do
  [ -z "$file" ] && continue
  # 절대 물리 경로로 정규화 (git diff 상대경로는 CWD=레포 루트 기준으로 해석; symlink 대응)
  fdir=$(cd "$(dirname "$file")" 2>/dev/null && pwd -P) || continue
  file="$fdir/$(basename "$file")"
  [ ! -f "$file" ] && continue
  under_root "$file" || continue

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
  tool=$(resolve_tool "$bin_dir/eslint") || continue
  files=()
  while IFS= read -r f; do
    [ -n "$f" ] && files+=("$f")
  done < <(files_for_bin "$bin_dir" "${js_pairs[@]}")
  [ ${#files[@]} -gt 0 ] && "$tool" "${files[@]}" --fix --quiet 2>/dev/null || true
done < <(unique_bins "${js_pairs[@]}")

# --- Step 2: Stylelint --fix ---
while IFS= read -r bin_dir; do
  [ -z "$bin_dir" ] && continue
  tool=$(resolve_tool "$bin_dir/stylelint") || continue
  files=()
  while IFS= read -r f; do
    [ -n "$f" ] && files+=("$f")
  done < <(files_for_bin "$bin_dir" "${css_pairs[@]}")
  [ ${#files[@]} -gt 0 ] && "$tool" "${files[@]}" --fix --quiet 2>/dev/null || true
done < <(unique_bins "${css_pairs[@]}")

# --- Step 3: Prettier --write ---
while IFS= read -r bin_dir; do
  [ -z "$bin_dir" ] && continue
  tool=$(resolve_tool "$bin_dir/prettier") || continue
  files=()
  while IFS= read -r f; do
    [ -n "$f" ] && files+=("$f")
  done < <(files_for_bin "$bin_dir" "${js_pairs[@]}")
  [ ${#files[@]} -gt 0 ] && "$tool" "${files[@]}" --write --no-error-on-unmatched-pattern 2>/dev/null || true
done < <(unique_bins "${js_pairs[@]}")

exit 0
