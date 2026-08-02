# git-harness

커밋·push·PR 생성·PR 리뷰를 **하나의 파이프라인**으로 처리하는 Claude Code 플러그인입니다. 저장소 상태를 먼저 읽어 어디서부터 시작할지 추천하고, 고른 지점부터 끝까지 이어서 진행합니다.

## 설치

```bash
claude plugin add seungahhong/seungah-claude-plugins
```

## 스킬

| Skill | Command | 설명 |
|-------|---------|------|
| Commit-PR | `/commit-pr` | 상태 기반 진입점(commit / push / pr) 선택 → 커밋 전 리뷰(+차단 게이트) → 한국어 커밋 메시지 → push → PR 생성 → PR 리뷰까지 한 흐름 |

## 사용법

```
/commit-pr
```

### 1. 진입점 선택

실행하면 먼저 저장소 상태(변경 파일 · 미push 커밋 · 열린 PR)를 읽고, 지금 상태에 맞는 시작점을 **추천 이유와 함께** 제시합니다.

```
[commit-pr] 어디서부터 시작할까요?

  1. commit — 변경 3개 파일이 스테이징돼 있습니다 (추천)
  2. push   — 미push 커밋 없음
  3. pr     — push된 커밋이 없어 아직 PR을 만들 수 없습니다

중간에서 멈추고 싶으면 그 지점에서 말씀해 주세요.
```

`pr`을 고르면 **기존 PR 지정**(이미 열린 PR 리뷰만) / **새 PR 생성** 중 하나를 다시 고릅니다.

### 2. 이후 흐름

```
commit  →  /simplify 문의 → 코드리뷰 문의 → 커밋 게이트 → 커밋 메시지 승인 → push → PR 생성 → PR 리뷰 문의
push    →  push → PR 생성 → PR 리뷰 문의
새 PR    →  PR 생성 → PR 리뷰 문의
기존 PR  →  PR 리뷰 문의
```

**진입점을 고른 순간 이후 단계까지 승인한 것으로 봅니다.** 중간에 "push할까요?", "PR 만들까요?"를 다시 묻지 않습니다 — 흐름만 끊고 정보를 더해주지 않는 질문이기 때문입니다. 대신 다음 두 지점에서는 반드시 확인을 받습니다:

- **커밋 메시지 / PR 제목·본문 프리뷰** — 여부가 아니라 "이 내용이 맞나"를 묻습니다.
- **PR 리뷰 실행 여부** — 팀원이 보는 인라인 코멘트가 GitHub에 남기 때문에 모드와 무관하게 따로 묻습니다.

멈추고 싶으면 언제든 말하면 그 지점에서 멈춥니다.

### 3. 커밋 전 리뷰와 차단 게이트

`commit` 모드에서는 커밋 전에 두 가지를 선택적으로 돌립니다.

- **/simplify** — `code-simplifier` 서브에이전트가 기능 변경 없이 명확성·중복·가독성을 정리하고 재스테이징합니다.
- **코드리뷰** — correctness · security · performance · readability 관점으로 리뷰하고, 각 발견에 `CONFIRMED`(재현 조건까지 특정) / `PLAUSIBLE`(의심) 판정을 답니다.

리뷰 결과는 severity 3등급으로 환산됩니다:

| severity | 조건 | 처리 |
| -------- | ---- | ---- |
| 치명 | correctness & CONFIRMED | 차단 |
| 중요 | correctness & PLAUSIBLE, 또는 그 외 & CONFIRMED | 차단 |
| 경미 | 그 외 & PLAUSIBLE | 통과 |

한 줄로: **correctness이거나 CONFIRMED면 커밋을 막습니다.** 차단되면 수정 → 재스테이징 → 재리뷰로 돌아갑니다(고쳤다는 자기보고가 아니라 재리뷰 결과로 판정). 다만 게이트는 경고이지 거부권이 아니어서, 의도된 것이라고 알려주면 무엇을 안고 가는지 기록한 뒤 진행합니다.

### 4. 안전장치

- 보호 브랜치(`main`/`master`/`dev`/`cdev`/`develop`/`release`/`rc*`) 커밋·push·PR 생성 전 중단
- diff 내 secret 의심 문자열(`API_KEY=`, `SECRET=`, `TOKEN=`, `Bearer `, `-----BEGIN`) 검사
- `--force` 류 플래그는 명시 요청 없이는 사용하지 않음, push 실패 시 원문 에러 출력 후 중단
- 커밋 메시지에 출처 표기(`Co-Authored-By`) 미기재

> `/commit-pr`로 직접 부를 수도 있고, "커밋해줘"·"PR 올려줘"처럼 커밋·push·PR을 언급하면 자동으로 발동합니다.

## 라이선스

MIT
