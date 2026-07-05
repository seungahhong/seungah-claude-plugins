#!/bin/bash
# incremental-lint.sh — PostToolUse 훅: 방금 수정/생성된 단일 파일만 lint
# Edit/Write 직후 해당 파일에 대해서만 eslint --fix → prettier --write (js/ts) / stylelint --fix (css)
# 전체 변경분 체인은 Stop 훅의 stop-lint.sh가 담당 — 매 편집마다 전체 재lint 하던 중복을 제거한다.
# 각 도구가 프로젝트에 설치되어 있지 않으면 건너뜀. 모노레포: 파일 기준 가장 가까운 node_modules 탐색.
# 안전: 바이너리 탐색은 git 프로젝트 루트까지로 제한하고, 후보 .bin 디렉토리와 도구 바이너리를
#       물리 경로(심링크 해석)로 재검증해 루트 내부일 때만 실행 — 프로젝트 밖(예: /tmp)의 공격자
#       바이너리를 `node_modules`→루트밖 심링크로 끌어와 실행하는 경계 우회를 차단한다.
#       git repo가 아니거나 파일이 루트 밖이면 스킵.
# 실패 전파: --fix로 못 고친 에러가 남으면 요약을 stderr로 출력하고 exit 2 (모델에 전달됨).
# stdin JSON은 다른 훅과 동일하게 공용 lib.sh(hook_field, jq→python3 폴백·부재 시 통과)로 파싱한다.

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
. "$SCRIPT_DIR/lib.sh"

INPUT=$(cat)
FILE=$(hook_field '.tool_input.file_path') || true

[ -z "$FILE" ] && exit 0
[ ! -f "$FILE" ] && exit 0

# 물리 경로로 정규화 (macOS /tmp → /private/tmp 등 symlink 대응, 상대 경로 포함)
FILE_DIR=$(cd "$(dirname "$FILE")" 2>/dev/null && pwd -P) || exit 0
FILE="$FILE_DIR/$(basename "$FILE")"

# git repo가 아니면 lint 스킵 (탐색 경계를 정할 수 없음)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -z "$PROJECT_ROOT" ] && exit 0
# 물리 경로로 정규화 — FILE(물리)과 같은 기준으로 경계를 비교하고 이후 심링크 해석의 기준점이 된다
PROJECT_ROOT=$(cd "$PROJECT_ROOT" 2>/dev/null && pwd -P) || exit 0

# 대상 파일이 프로젝트 루트 내부일 때만 lint
case "$FILE" in
  "$PROJECT_ROOT"/*) ;;
  *) exit 0 ;;
esac

ext="${FILE##*.}"

# 물리 경로 $1이 프로젝트 루트 내부인지 판정 (경계 검사 공용)
under_root() {
  case "$1/" in "$PROJECT_ROOT"/*) return 0 ;; esac
  return 1
}

# 심링크 체인을 물리 경로로 해석해 출력. 순환/과다 홉은 실패(반환 1).
# 정상 npm의 node_modules/.bin/<tool>(상대 심링크)도 여기서 실체 위치(루트 내부)로 해석된다.
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
# 발견 시 물리 경로로 해석해 루트 내부일 때만 채택 — `node_modules`→루트밖 심링크로
# 경계를 우회하는 것을 차단한다(문자열 경로만 보던 기존 검사의 허점 보강).
find_bin_dir() {
  local dir real
  dir=$(dirname "$1")
  while [ -n "$dir" ] && [ "$dir" != "/" ]; do
    if [ -d "$dir/node_modules/.bin" ]; then
      # 물리 경로로 해석해 루트 내부일 때만 채택. 루트 밖(심링크 우회)이거나 해석 불가하면
      # 채택하지 않고 상위로 계속 탐색한다 — 보안 경계는 유지(루트 밖 경로는 절대 반환 안 함)하면서
      # 상위의 정상 in-repo .bin으로 폴백해 정당한 모노레포(중첩 패키지의 node_modules가 트리 밖을
      # 가리키는 심링크 등)에서 lint 누락을 막는다.
      if real=$(cd "$dir/node_modules/.bin" 2>/dev/null && pwd -P); then
        under_root "$real" && { echo "$real"; return 0; }
      fi
    fi
    [ "$dir" = "$PROJECT_ROOT" ] && break
    dir=$(dirname "$dir")
  done
  return 1
}

bin_dir=$(find_bin_dir "$FILE") || exit 0

fail_summary=""

run_fix() {
  # $1: 도구명, 나머지: 실행 커맨드. 실패(비정상 종료) 시에만 요약 누적.
  local tool="$1"
  shift
  local out
  if ! out=$("$@" 2>&1); then
    local errors first
    # 카운트도 첫줄과 동일하게 대소문자 무시로 통일("Error:"도 집계). 실패 분기이므로 최소 1건으로 바닥 처리.
    errors=$(printf '%s\n' "$out" | grep -ciE '(^|[[:space:]])error([[:space:]]|$|:)')
    [ "$errors" -eq 0 ] 2>/dev/null && errors=1
    first=$(printf '%s\n' "$out" | grep -m1 -iE 'error' | sed 's/^[[:space:]]*//')
    [ -z "$first" ] && first=$(printf '%s\n' "$out" | grep -m1 -E '[^[:space:]]' | sed 's/^[[:space:]]*//')
    [ -z "$first" ] && first="(도구가 출력 없이 비정상 종료)"
    fail_summary="${fail_summary}[${tool}] 에러 ${errors}건 — ${first}"$'\n'
  fi
}

# 도구 실행 게이트: 도구 바이너리 실체(심링크 해석 후)가 루트 내부일 때만, 검증한 바로 그 물리
# 경로를 실행한다. node_modules/.bin/<tool>이 루트 밖을 가리키는 심링크면 실행 거부(경계 우회 차단).
# $bin(심링크)을 다시 실행하지 않고 $real을 실행 — 검사 대상과 실행 대상을 일치시켜 검사-후-교체
# (TOCTOU) 여지를 없앤다. 정상 npm/pnpm의 .bin/<tool>도 실체 .js 경로로 동일하게 동작한다.
run_tool() {
  local tool="$1" bin="$2"
  shift 2
  [ -x "$bin" ] || return 0
  local real
  real=$(resolve_symlink "$bin") || return 0
  under_root "$real" || return 0
  [ -x "$real" ] || return 0
  run_fix "$tool" "$real" "$@"
}

case "$ext" in
  js|jsx|ts|tsx)
    run_tool eslint "$bin_dir/eslint" "$FILE" --fix --quiet
    run_tool prettier "$bin_dir/prettier" "$FILE" --write --no-error-on-unmatched-pattern
    ;;
  css|scss)
    run_tool stylelint "$bin_dir/stylelint" "$FILE" --fix --quiet
    ;;
esac

if [ -n "$fail_summary" ]; then
  printf '[incremental-lint] --fix 후에도 해결되지 않은 에러가 있습니다 (%s):\n%s' "$FILE" "$fail_summary" >&2
  exit 2
fi

exit 0
