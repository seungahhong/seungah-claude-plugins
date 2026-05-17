---
name: review-to-pr
description: "변경 파일 기반으로 리뷰 → 커밋 → PR 생성까지 한 번에 처리하는 올인원 워크플로우 스킬. Commit과 PR 중 실행할 단계를 선택하면, 각 단계에서 /simplify + /review 리뷰를 자동 수행하고 수정을 적용한 뒤 커밋 또는 PR을 생성한다. 'PR 준비', 'PR 만들어줘', '리뷰하고 커밋하고 PR', 'review to pr', 'pr-ready', '머지 준비', 'PR 올려줘', '코드 리뷰하고 PR', '리뷰부터 PR까지', 'PR 프로세스', '커밋하고 PR' 등의 키워드에 반응한다. PR 생성이 포함된 워크플로우를 요청할 때 반드시 이 스킬을 사용한다."
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob, Edit, Write, Agent
---

# Review-to-PR — 리뷰 → 커밋 → PR

변경된 파일을 대상으로 **리뷰 내장 커밋**과 **리뷰 내장 PR 생성**을 수행하는 올인원 워크플로우.
Commit과 PR 각 단계 안에서 `/simplify` + `/review` 리뷰가 자동으로 실행된다.

## 워크플로우

```
Phase 0: 사전 조건 (변경 파일 확인)
    │
    ▼
Phase 1: 실행 단계 선택
  Commit / PR / Commit + PR
    │
    ├─── Commit 선택 시 ──────────────────────┐
    │                                          │
    ▼                                          │
Phase 2: Commit 실행                           │
  리뷰 여부 확인 → [리뷰 → 수정] → /commit    │
    │                                          │
    ├─── PR 선택 시 ───────────────────────────┤
    │                                          │
    ▼                                          ▼
Phase 3: PR 실행
  gh CLI 확인 → 리뷰 여부 확인 → [리뷰 → 수정] → PR 생성
```

---

## Phase 0: 사전 조건

### 변경 사항 확인

```bash
git status --porcelain
git diff --stat HEAD
git diff --name-only HEAD
```

변경 파일이 없으면 사용자에게 알리고 종료한다.

---

## Phase 1: 실행 단계 선택

```
[PR-Ready] 실행할 단계를 선택해주세요.

  □ 1. Commit       — 리뷰 후 커밋
  □ 2. PR           — 리뷰 후 PR 생성
  □ 3. Commit + PR  — 리뷰 후 커밋, 이어서 PR 생성

선택 (1 / 2 / 3):
```

- `1` → Phase 2만 실행
- `2` → Phase 3만 실행
- `3` → Phase 2 → Phase 3 순차 실행

---

## Phase 2: Commit 실행

### 2-1. 리뷰 진행 여부 확인

커밋 전 리뷰를 진행할지 사용자에게 먼저 확인한다.

```
[Commit] 커밋 전에 /simplify + /review 리뷰를 진행할까요?

  1. 진행 — 리뷰 후 커밋
  2. 건너뛰기 — 리뷰 없이 바로 커밋

선택 (1 / 2):
```

- `1` → 2-2 리뷰 실행으로 진행
- `2` → 2-2, 2-3을 건너뛰고 2-4 커밋으로 바로 이동

### 2-2. 현재 변경사항 기준 리뷰

**현재 파일 변경사항**(staged + unstaged)을 대상으로 `/simplify`와 `/review`를 **병렬 실행**한다.

리뷰 실행·수정 절차의 상세는 `references/review-process.md`를 따른다.

```bash
git diff HEAD                    # 리뷰 대상 diff
git diff --name-only HEAD        # 리뷰 대상 파일 목록
```

### 2-3. 리뷰 결과 수정

리뷰 결과에서 발견된 이슈를 **두 가지로 분류**하여 처리한다:

**자동 수정** — 사용자 확인 없이 바로 적용:
- 코드 스타일 수정 (포맷팅, 네이밍, 불필요한 공백)
- /simplify가 제안한 간소화 (중복 제거, 가독성 개선)
- 단순 코드 수정 (미사용 import 제거, 타입 오류 등)

**사용자 확인 필요** — 이슈를 출력하고 수정 여부를 묻는다:
- 로직 변경이 수반되는 수정
- 인터페이스/API 시그니처 변경
- 동작이 달라질 수 있는 리팩토링

```
[Review] 사용자 확인이 필요한 이슈가 N건 있습니다.

| # | 심각도    | 파일:라인 | 이슈 | 수정 제안 |
|---|----------|----------|------|----------|
| 1 | Critical | ...      | ...  | ...      |
| 2 | Important| ...      | ...  | ...      |

각 항목에 대해 선택해주세요:
- 수정: 항목 번호 (예: "1, 2")
- 전체 수정: "전체"
- 건너뛰기: "skip" — 수정 없이 커밋 단계로 진행
```

### 2-4. 커밋

리뷰를 건너뛴 경우 또는 리뷰 결과 수정이 완료되면 `/commit` 스킬의 전체 프로세스를 실행한다:

1. 전제 조건 확인 — `git status`, `git diff --staged`, `git log`
2. 이슈 번호 추출 (브랜치명에서 `[A-Z]{2,}-\d+`)
3. Type 결정 (feat/fix/docs/style/refactor/test/chore)
4. 제목 작성 (한국어 명령형)
5. 본문 필요 여부 판단 (§1.4 본문 작성 판단 프로세스)
6. Validation → 프리뷰 → 사용자 승인 후 커밋

Phase 1에서 `Commit + PR`을 선택한 경우, 커밋 완료 후 Phase 3으로 진행한다.

---

## Phase 3: PR 실행

### 3-0. gh CLI 확인

```bash
which gh && gh auth status
```

gh가 설치되지 않았거나 인증되지 않은 경우 아래 메시지를 출력하고 **스킬을 즉시 종료**한다.

```
[PR-Ready] gh CLI가 설치되지 않았거나 인증되지 않았습니다.

다음 단계를 완료한 후 다시 실행해주세요:
1. gh 설치: brew install gh
2. 인증: gh auth login

스킬을 종료합니다.
```

PR 메시지 포맷·생성 절차의 상세 사양은 `references/pr-creation.md`를 따른다.

### 3-1. 타겟 브랜치 입력

```
[PR] Pull Request를 생성합니다.

현재 브랜치: <현재 브랜치명>
PR 타겟(base) 브랜치를 입력해주세요 (예: rc, rc2, main):
```

### 3-2. 리뷰 진행 여부 확인

PR 생성 전 리뷰를 진행할지 사용자에게 먼저 확인한다.

```
[PR] PR 생성 전에 /simplify + /review 리뷰를 진행할까요?

  1. 진행 — 리뷰 후 PR 생성
  2. 건너뛰기 — 리뷰 없이 바로 PR 생성

선택 (1 / 2):
```

- `1` → 3-3 리뷰 실행으로 진행
- `2` → 3-3, 3-4를 건너뛰고 3-5 PR 생성으로 바로 이동

### 3-3. 타겟 브랜치 대비 리뷰

현재 브랜치와 타겟 브랜치 간의 diff를 대상으로 `/simplify`와 `/review`를 **병렬 실행**한다.

리뷰 실행·수정 절차의 상세는 `references/review-process.md`를 따른다.

```bash
git fetch origin <target-branch> --quiet
git diff origin/<target-branch>..HEAD              # 리뷰 대상 diff
git diff origin/<target-branch>..HEAD --name-only  # 리뷰 대상 파일 목록
```

### 3-4. 리뷰 결과 수정

Phase 2-3과 동일한 방식으로 처리한다:

- **자동 수정**: 스타일, 간소화, 단순 코드 수정 → 바로 적용
- **사용자 확인 필요**: 로직 변경, 인터페이스 변경 → 출력 후 선택 (건너뛰기 가능)

### 3-5. PR 생성

수정이 완료되면 PR 제목과 본문을 생성한다.

commit 스킬의 **본문 작성 판단 프로세스(§1.4)**를 기반으로 diff를 분석한다:

1. **변경 범위 파악** — 수정 파일 수, 변경 라인 수, 영향 모듈/레이어
2. **의도 추론** — 단순 버그 픽스인지, 구조 변경인지, 새 요구사항인지
3. **숨겨진 영향 탐색** — 인터페이스 변경, 동작 차이, 하위 호환성, 성능
4. **테스트 변경 확인** — 테스트 파일 추가/수정 여부, 커버 케이스

PR 메시지 포맷은 `references/pr-creation.md`를 따른다.

### 3-6. 프리뷰 및 생성

```
[PR] 다음 내용으로 PR을 생성합니다.

제목: <PR 제목>
Base: <target-branch>

--- 본문 ---
<PR 본문 프리뷰>
--- 본문 끝 ---

진행할까요?
1. 승인 — PR 생성
2. 수정 — 제목/본문 수정 후 재프리뷰
```

승인 시:

```bash
git push -u origin <현재-브랜치>
gh pr create --base <target-branch> --title "<제목>" --body "<본문>"
```

PR URL을 사용자에게 출력하고 스킬을 종료한다.

---

## 사용자 소통 원칙

- 모든 Phase 전환 시 현재 진행 상황을 안내한다
- `git push`나 `gh pr create` 같은 외부 영향 행위는 반드시 사용자 승인을 받는다
- 에러 발생 시 구체적 에러 메시지와 해결 방안을 함께 제시한다
- 리뷰에서 자동 수정한 항목은 수정 내역을 간략히 보고한다
