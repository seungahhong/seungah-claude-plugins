# spec-driven-development

엔지니어용 **실행 가능 명세(spec)를 source of truth로 작성**하고, 에이전트가 그 명세대로 코드를 생성한 뒤
**명세 대비 자기검증**하게 하는 도메인 무관 멀티 에이전트 하네스입니다.

핵심 전환은 워크플로의 **역전**입니다 — 보통은 코드를 먼저 짜고 문서를 사후에 붙이지만, Spec-Driven Development(SDD)는
**명세를 1차 산출물(source of truth)로 두고, 코드를 그 명세로부터 생성·검증되는 2차 산출물**로 다룹니다. 코딩 에이전트에게
명세는 *지시*이자 *검증 기준*이고, 사람에게는 *이해의 앵커*입니다.

> 이 하네스는 *엔지니어용 구현 명세*(에이전트가 코드를 생성할 실행 가능한 contract)에 특화합니다.
> 문제정의·비즈니스 요구를 담는 기획자용 PRD/사용자 스토리 작성은 범위 밖입니다(그건 제품 기획 도메인).

## 왜 명세 우선인가

- **명세=contract**: 좋은 명세는 산문이 아니라 구조화된 contract입니다 — 목표·범위·인터페이스·동작·제약·엣지케이스를
  에이전트가 그대로 구현·검증할 수 있게 적습니다("How to structure, plan, and iterate for high-performance coding agents", Osmani).
- **명세가 source of truth**: SDD는 "명세를 source of truth로 취급하고 코드를 생성/검증되는 2차 산출물로 다루어
  전통 워크플로를 역전"합니다(arXiv:2602.00180).
- **이해의 앵커(comprehension)**: 에이전트가 출력을 빠르게 늘릴수록, 사람의 *읽고 이해하는 능력*이 그만큼 따라가지 못하면
  "엔지니어링이 아니라 희망"이 됩니다 — 생성(쓰기)과 식별(읽기)은 다른 인지 능력입니다(Osmani, "The 80% Problem in Agentic Coding").
  명세는 무엇이 맞는지의 기준을 미리 못 박아 이 격차(comprehension debt)를 줄입니다.

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `spec-driven-development` 플러그인을 활성화하면,
`spec-driven-development` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `spec-driven-development` | 오케스트레이터(진입점). 명세 작성(Author Spec) → 인수 설계(Acceptance) → 명세 대비 구현(Generate) → 명세 대비 검증(Verify + comprehension 게이트)의 4단계를 진행하며, 각 단계에서 전용 에이전트(spec-author / acceptance-designer / spec-implementer / spec-verifier)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Author Spec | `spec-author` | 실행 가능 명세를 source of truth로 작성(구조화된 contract — 목표·범위·인터페이스·제약·엣지케이스, 구조·계획·반복) |
| 1 Acceptance | `acceptance-designer` | 인수기준 + 테스트 계획 + 자기검증 체크(self-verification)를 명세 안에서 설계 |
| 2 Generate | `spec-implementer` | 명세대로 코드 생성(또는 구현 가이드) + 추적성(어느 조항을 어디서 구현했는지) |
| 3 Verify | `spec-verifier` | 코드가 *명세대로* 도는지 조항별 검증 + comprehension 게이트(diff 이해 확인) |

## 5단계 사용법

1. **요청 입력** — 만들/고칠 동작을 기술합니다. 모호하면 `spec-author`가 명세화에 필요한 최소 질문을 합니다.
2. **명세 승인 게이트** — Phase 0에서 실행 가능 명세(Executable Spec)를 받아 **검토·승인**합니다. 승인 전에는 구현을 시작하지 않습니다(잘못된 명세로 코드 생성 비용을 낭비하지 않기 위함).
3. **인수기준 확인** — Phase 1에서 인수기준·테스트 계획·자기검증 체크가 명세를 falsifiable하게 덮는지 확인합니다.
4. **명세 대비 생성** — Phase 2에서 에이전트가 명세대로 코드를 생성하고, 어느 spec 조항을 어디서 구현했는지 추적성을 남깁니다.
5. **명세 대비 검증 + comprehension 게이트** — Phase 3에서 코드가 *명세대로* 도는지 조항별로 검증하고, 완료 선언 전에 diff를 읽어 "무엇이 왜 바뀌었는지"를 확인합니다(green CI ≠ 명세 구현 완료).

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- 코딩 에이전트가 구현할 **실행 가능한 구현 명세를 source of truth로 먼저 작성**하고 싶을 때
- 작성한 명세를 **인수기준·테스트 계획·자기검증 체크**로 falsifiable하게 만들고 싶을 때
- 에이전트가 **명세대로 코드를 생성한 뒤 명세 부합을 조항별로 검증**하게 하고 싶을 때
- 빠르게 생성된 코드를 **이해한 채로(comprehension 게이트)** 받아들이고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖)**
- 기획자용 **PRD·사용자 스토리**(문제정의·비즈니스 요구) 작성 — 이건 제품 기획 도메인입니다(엔지니어용 구현 명세가 아님)
- AI 생성물·에이전트 출력을 평가할 **judge(LLM-as-a-Judge) 구성**·평가 하네스 운영 — 이 하네스는 *명세*를 만들지 *평가기*를 만들지 않습니다
- 모델에 넣을 **컨텍스트 페이로드 조립·압축·관리**
- 이미 **완성된 코드의 리뷰·커밋 메시지·PR 리뷰**
- 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선

경계가 모호하면 한 질문으로 확인합니다 — "에이전트가 구현할 *실행 가능한 구현 명세*를 먼저 작성하는 건가요, 아니면 *기획/평가/리뷰*인가요?"

## 진행 방식

| Phase | 단계 | 핵심 산출물 |
|-------|------|-------------|
| 0 | 명세 작성 (Author Spec) | Executable Spec (구조화된 contract) — **명세 승인 게이트** |
| 1 | 인수 설계 (Acceptance) | 인수기준 + 테스트 계획 + 자기검증 체크 |
| 2 | 명세 대비 구현 (Generate) | 명세를 구현한 코드(또는 구현 가이드) + 추적성 |
| 3 | 명세 대비 검증 (Verify) | 조항별 부합 Verdict + 증거 + **comprehension 게이트** |

## 근거 논문·자료

설계 근거는 `skills/spec-driven-development/references/spec-driven-development-research.md`에 출처·인용·신뢰도·caveat와 함께 정리되어 있습니다. 핵심 출처는 다음과 같습니다.

- **Addy Osmani, "How to write a good spec for AI agents"** (addyo.substack.com, 2026-01-19; O'Reilly Radar 재게재) — 코딩 에이전트용 명세를 *구조화·계획·반복*하는 법(구조화된 contract·self-verification·LLM-as-a-Judge·test plan).
- **arXiv:2602.00180, "Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants"** (Deepak Babu Piskala, 2026-01-30) — SDD = 명세를 source of truth로, 코드를 생성/검증되는 2차 산출물로 두는 워크플로 역전. *(CAVEAT: 효율·실효성 비판도 있음 — dossier 참조.)*
- **Addy Osmani, "The 80% Problem in Agentic Coding"** (addyo.substack.com, 2026-01-28) — comprehension debt: 생성과 식별은 다른 인지 능력이며, 읽기가 출력 속도를 못 따라가면 "엔지니어링이 아니라 희망"이다 → comprehension 게이트의 동기.

> 정직성 노트: 정량 효과가 "보장"되지 않습니다. SDD의 효율·non-determinism에 대한 비판과 dossier에 기록된 *반박된 주장*은 본문 근거로 쓰지 않고 투명성 차원에서만 남깁니다.
