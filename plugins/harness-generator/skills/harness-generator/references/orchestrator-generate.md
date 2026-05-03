# 오케스트레이터 생성 템플릿

하네스의 단일 진입점인 오케스트레이터 스킬을 생성할 때 사용하는 3가지 모드별 템플릿. SKILL.md Phase 5의 보충 자료.

## 목차
1. [공통 골격](#1-공통-골격)
2. [템플릿 A — 에이전트 팀 모드](#2-템플릿-a--에이전트-팀-모드)
3. [템플릿 B — 서브에이전트 모드](#3-템플릿-b--서브에이전트-모드)
4. [템플릿 C — 하이브리드 모드](#4-템플릿-c--하이브리드-모드)
5. [공통 작성 원칙](#5-공통-작성-원칙)

---

## 1. 공통 골격

모든 오케스트레이터는 동일한 외형을 갖는다.

```
Phase 0  컨텍스트 확인     이전 산출물(_workspace/) 검사 → 초기/후속/부분 재실행 자동 판별
Phase 1  준비             입력 분석, _workspace/ 생성, 모드 선언
Phase 2..N  주요 작업      도메인 본 작업 (모드별 실행)
Phase 마지막  정리         통합 산출물, _workspace/ 보존/이동, 결정 이력
```

**Phase 0에서 자동 판별 규칙:**
- `_workspace/` 없음 → **초기 실행**
- `_workspace/` 있음 + 입력 동일 → **부분 재실행** (변경 부분만 다시)
- `_workspace/` 있음 + 입력 변경 → **새 실행** (`_workspace/` → `_workspace_prev/` 이동 후 재생성)

---

## 2. 템플릿 A — 에이전트 팀 모드

> 2명 이상이 협업하고 실시간 통신·토론이 필요한 경우의 기본 선택.

```markdown
---
name: {domain}-orchestrator
description: {도메인} 워크플로우를 처음부터 끝까지 실행한다. "{도메인} 시작", "{도메인} 다시 실행", "{도메인} 보완" 등에 트리거. 단순 질문은 직접 답변.
---

# {Domain} Orchestrator (Agent Team Mode)

## 실행 모드
**에이전트 팀** — 팀원 간 직접 통신과 공유 작업 목록으로 자체 조율.

## Phase 0 — 컨텍스트 확인
- `_workspace/` 검사 → 초기 / 후속 / 부분 재실행 판별
- 결과를 사용자에게 1줄 보고 후 진행 승인

## Phase 1 — 준비
- 사용자 요구 1줄 요약
- `_workspace/` 생성 (또는 이전본을 `_workspace_prev/`로 이동)
- 입력 산출물 정리

## Phase 2 — 팀 구성
TeamCreate(
  team_name="{domain}-team",
  members=[ "agent-a", "agent-b", "agent-c" ]   # 정의 파일은 agents/ 아래
)
TaskCreate(
  - "작업 1 (담당: agent-a, blockedBy: -)"
  - "작업 2 (담당: agent-b, blockedBy: 작업 1)"
  - "작업 3 (담당: agent-c, blockedBy: 작업 1)"
)

## Phase 3 — 팀 자체 조율
- 팀원이 SendMessage로 발견·이슈를 공유
- TaskUpdate로 진척 보고
- 모든 Agent 호출에 model: "opus"

## Phase 4 — 결과 통합
- 산출물을 `_workspace/{phase}_{agent}_{artifact}.{ext}`로 수집
- 통합본을 사용자 경로(예: docs/, 루트)에 저장

## Phase 5 — 정리
- 팀 종료
- `_workspace/` 보존 (다음 후속 실행을 위해)
- 변경/결정 이력 1줄 갱신
- CLAUDE.md Change History에 1줄 추가

## 데이터 전달
- 작업: TaskCreate / TaskUpdate
- 메시지: SendMessage
- 산출: _workspace/{phase}_{agent}_{artifact}.{ext}

## 에러 정책
- 1회 재시도 → 실패 시 결과 누락 처리하고 진행 (출처 태그 보존)

## 테스트 시나리오
- 정상 흐름: {입력 예} → {기대 산출}
- 에러 흐름: {특정 에이전트 실패} → 누락 처리 + 사용자 보고
```

---

## 3. 템플릿 B — 서브에이전트 모드

> 단발 결과 핸드오프만 필요하고 통신 오버헤드가 불필요한 경우.

```markdown
---
name: {domain}-orchestrator
description: ...
---

## 실행 모드
**서브에이전트** — 결과만 수집, 직접 통신 없음.

## Phase 0 — 컨텍스트 확인 (공통)

## Phase 1 — 준비 (공통)

## Phase 2 — 병렬 호출
- Agent(subagent_type="general-purpose", model="opus", run_in_background=true,  prompt="...A...")
- Agent(subagent_type="general-purpose", model="opus", run_in_background=true,  prompt="...B...")
- (필요 시 동기 호출)

## Phase 3 — 결과 수집
- 각 서브의 반환 메시지를 `_workspace/{phase}_{agent}_{artifact}.{ext}`로 저장

## Phase 4 — 통합 산출물 작성

## Phase 5 — 정리 (공통)

## 데이터 전달
- 반환 메시지로 단발 핸드오프
- 큰 데이터는 파일로 우회

## 에러 정책 / 테스트 시나리오 (공통)
```

---

## 4. 템플릿 C — 하이브리드 모드

> Phase별 특성이 크게 다른 경우. 각 Phase의 모드를 반드시 명시한다.

```markdown
## Phase 2 — 자료 수집 [모드: 서브에이전트]
독립 병렬 호출 후 결과 파일로 저장.

## Phase 3 — 합의 형성 [모드: 에이전트 팀]
서로 다른 관점을 가진 멤버들이 SendMessage로 토론하여 결론 도출.

## Phase 4 — 검증 [모드: 서브에이전트]
독립 검증자 1명이 합의 결과를 채점.
```

**필수 표기:** Phase 헤더 옆 `[모드: ...]`, 모드 경계에서 데이터 손실이 없도록 파일 기반 전달.

---

## 5. 공통 작성 원칙

1. **실행 모드를 본문 상단에 명확히 선언** — 검증과 재현성에 필수.
2. **TeamCreate / SendMessage / TaskCreate 사용법은 모드 A에서 구체화** — 팀원 이름, 작업 의존성, 메시지 토픽까지.
3. **파일 경로는 `_workspace/` 기준 절대 경로** — Phase 간 산출물 추적용.
4. **에러 핸들링과 테스트 시나리오를 본문에 포함** — 정상 1개 + 에러 1개 이상.
5. **description에 후속 작업 키워드 포함** — "재실행", "업데이트", "수정", "보완", "이전 결과 기반으로".
6. **모든 Agent 호출에 `model: "opus"` 명시** — 빠뜨리면 추론 품질 보장 못 함.
7. **`commands/`를 자동 생성하지 않음** — 오케스트레이터는 스킬로 충분.
8. **CLAUDE.md 포인터 등록을 마지막 단계에 포함** — 트리거 규칙 + 변경 이력 1줄.
