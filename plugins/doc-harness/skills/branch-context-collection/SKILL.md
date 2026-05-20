---
name: branch-context-collection
description: "현재 브랜치와 기본 브랜치 사이의 git diff·커밋·코드 구조를 수집해 문서 생성용 단일 컨텍스트(context.md + meta.json)로 정리하는 스킬. '브랜치 변경 수집', '문서용 컨텍스트', 'diff 정리', '브랜치 비교'를 다루거나 doc-harness의 context-collector가 호출될 때 사용한다. 재수집·base 변경 시에도 사용한다."
---

# 브랜치 컨텍스트 수집

문서의 모든 섹션은 이 단계의 산출물 위에 세워진다. 비교 기준이 틀리거나 변경 요약이 부정확하면 이후 전 섹션이 어긋난다. 그래서 수집은 **정확한 비교 기준 확정 → 변경 요약 → 코드 구조·테스트 현황 정리** 순으로 한다.

## 1) 비교 기준 확정

사용자가 base를 지정했으면 그대로 쓴다. 없으면 자동 감지한다.

```bash
git rev-parse --is-inside-work-tree                  # 저장소 여부 (아니면 즉시 중단)
git branch --show-current                            # 현재 브랜치
# 기본 브랜치 후보 탐지 (우선순위: origin/HEAD → main → master → develop)
git symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
git show-ref --verify --quiet refs/heads/main && echo main
git show-ref --verify --quiet refs/heads/master && echo master
```

확정한 base로 merge-base와 커밋 범위를 잡는다.

```bash
BASE=<확정된 base>
git merge-base HEAD "$BASE"                           # 분기점
git rev-list --count "$BASE"..HEAD                    # 커밋 수
git log --oneline --no-merges "$BASE"..HEAD           # 커밋 목록
git diff --stat "$BASE"...HEAD                        # 파일별 변경량 (3-dot: 분기 이후 변경)
```

**왜 3-dot(`base...HEAD`)인가:** 분기점 이후 현재 브랜치에서 일어난 변경만 보여줘, base가 그 사이 앞서가도 노이즈가 섞이지 않는다.

현재 브랜치 == base 이거나 diff가 비면, 워킹 트리 변경(`git diff`, `git status --porcelain`) 포함 여부를 사용자에게 묻고 결정에 따라 범위를 바꾼다.

## 2) 변경 요약 (해석 아님, 사실만)

`git diff "$BASE"...HEAD`를 읽고 **파일이 아니라 의미 단위**로 묶어 요약한다. 각 항목에 근거 경로를 단다.

- 변경을 기능/모듈 단위로 그룹화한다(예: "인증 흐름", "결제 API", "공통 UI").
- 각 그룹에 변경 성격 태그를 단다: `feat`/`fix`/`refactor`/`test`/`docs`/`chore`/`perf`/`breaking`.
- 신규 파일 / 수정 / 삭제 / 이름변경을 구분한다.
- 공개 인터페이스 변경(함수 시그니처, 라우트, 환경변수, DB 스키마, 설정 키)은 별도로 강조한다 — 기술스펙·영향 섹션의 핵심 재료다.

원문 diff를 통째로 옮기지 않는다. 섹션 분석가가 다시 찾아볼 수 있게 경로/해시만 남긴다.

## 3) 코드 구조 · 의존성 · 테스트 현황

변경에 닿는 범위에 한해 다음을 정리한다. 저장소 전체를 훑지 않는다.

- 변경된 모듈의 위치와 역할, 인접 모듈과의 연결(import/호출 관계).
- 새로 추가/변경된 의존성(package.json, requirements, go.mod 등 diff 기준).
- 테스트 현황: 추가/변경된 테스트 파일, 테스트 프레임워크, 실행 명령(README/package.json scripts에서 확인), 커버리지 도구 유무.

## 4) 출력

### `_workspace/context.md` — 섹션별 단서를 소제목으로 구획한다

```markdown
# 수집 컨텍스트

## 메타
- 브랜치 / base / merge-base / 커밋 범위 / 변경 규모

## 배경 단서
- 이 작업의 동기로 보이는 신호(커밋 메시지, 이슈 번호, PR 제목, 코드 주석)

## 기술스펙 단서
- 변경된 모듈 구조, 공개 인터페이스 변경, 데이터 흐름, 추가된 의존성

## 변경사항 목록 (의미 단위 + 태그 + 근거 경로)
- [feat] 인증 흐름: ... (auth/login.ts, a1b2c3d)

## 테스트 현황
- 추가/변경된 테스트, 실행 명령, 커버리지 도구
```

### `_workspace/meta.json`

```json
{
  "branch": "feature/x",
  "base": "main",
  "merge_base": "a1b2c3d",
  "commit_range": "a1b2c3d..HEAD",
  "files_changed": 12,
  "insertions": 340,
  "deletions": 85,
  "commit_count": 7,
  "generated_at": "2026-05-20T00:00:00Z"
}
```

## 5) 재수집 판단

- `meta.json`이 있고 `commit_range`가 동일 → 수집 생략, 기존 `context.md` 재사용.
- base 또는 HEAD가 바뀜 → `_workspace/` → `_workspace_prev/` 이동 후 새로 수집.

## 금지 사항

- 변경의 "왜/효과"를 여기서 평가하지 않는다(섹션 분석가의 몫).
- 근거 없는 사실을 만들지 않는다. 불확실하면 "확인 필요"로 표기.
