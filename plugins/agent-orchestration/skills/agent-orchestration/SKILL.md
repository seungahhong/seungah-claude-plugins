---
name: agent-orchestration
description: 한 작업을 여러 에이전트로 병렬화할지·어떻게 협업시킬지를 판단 규칙으로 결정하고, 그 협업이 단일 에이전트 baseline을 실제로 능가하는지 적대적으로 검증하는 도메인 무관 멀티 에이전트 오케스트레이터. 사용자가 "이 작업을 여러 에이전트로 나눌까 한 에이전트로 할까 판단해줘", "멀티 에이전트로 병렬화하는 게 이득인지 결정해줘", "이 작업에 맞는 에이전트 아키텍처(single/multi·centralized/independent) 골라줘", "서브에이전트 몇 개로 어떻게 협업시킬지 설계해줘", "에이전트 협업이 자꾸 깨지는데 coordination 가드 설계해줘", "에이전트를 더 붙이면 정말 나아지는지 baseline과 비교해 검증해줘", "이 멀티 에이전트 구성이 단일보다 나은지 확인하고 아니면 단일 권고해줘", "병렬화하면 안 되는 경우면 그렇다고 말해줘"를 언급하며 멀티 에이전트 사용 여부·방식·검증을 결정하려 할 때 발동한다. 작업의 분해 가능성·도구 밀도로 단일 baseline을 추정(Phase 0)하고, architecture-task alignment·capability-ceiling 휴리스틱으로 아키텍처를 권고(Phase 1)하며, communication·commitment·expectation 실패와 context-pollution을 막는 가드를 설계(Phase 2)하고, 계획이 baseline을 능가하는지 검증해 못 하면 단일을 권고한다(Phase 3). "에이전트를 더 붙인다고 항상 이득이 아니다"가 핵심이다. 발동하지 않는다 — 모델에 넣을 컨텍스트 페이로드 조립·압축, AI 출력의 엄밀한 평가(judge 구성), 엔지니어용 구현 명세 작성, 단일 자율 반복 루프, 새 하네스/에이전트 팀을 처음부터 생성, 프로덕션 장애 대응, 커밋/PR 리뷰, settings.json 설정 변경.
---

# Agent Orchestration — 멀티 에이전트 결정·설계·검증 오케스트레이터

한 작업을 **여러 에이전트로 병렬화할지·어떻게 협업시킬지**를 *판단 규칙*으로 결정하고, 그 협업이
**단일 에이전트 baseline을 실제로 능가하는지** 적대적으로 검증한다. 핵심 메시지는 하나다 —
**"에이전트를 더 붙인다고 항상 이득이 아니다."** 멀티 에이전트의 이득/손해는 *에이전트 수*가 아니라
작업 속성과 아키텍처의 정합(architecture-task alignment)이 결정하고, 협업 자체에 비용(curse of
coordination)이 들기 때문이다.

## 무엇을 결정하는가 (네 질문)

1. 이 작업은 *나눌 수 있는가* — 분해 가능성·도구 밀도·의존 구조는 어떤가? (Phase 0)
2. *단일로 할까 멀티로 할까*, 멀티면 *어떤 토폴로지*인가? (Phase 1)
3. 멀티라면 *협업이 깨지지 않게* 어떤 가드를 둘까? (Phase 2)
4. 이 계획이 *단일 baseline을 실제로 능가*하는가, 아니면 *병렬화하면 안 되는가*? (Phase 3)

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'여러 에이전트를 쓸지/어떻게 협업시킬지 결정한다'**. 다음은 명시적으로 범위 밖이다.

- **컨텍스트 페이로드 조립·압축** — 모델에 *무엇을 넣을지*(retrieval·압축·큐레이션)는 컨텍스트 설계 도메인이다. 이 하네스는
  *몇 개의 에이전트로 어떻게 협업시킬지*를 다룬다. (단, 멀티 구성에서 에이전트별 컨텍스트 *격리*는 coordination 가드의 일부로 다룬다 — 페이로드 *최적화*가 아니라 *cross-agent 오염 방지*.)
- **AI 출력의 엄밀한 평가(judge 구성)** — LLM-as-a-Judge·benchmark validity 같은 *산출물 평가*는 평가 도메인이다. 이 하네스의
  검증(Phase 3)은 *멀티 에이전트 계획이 단일 baseline을 능가하는가*에 한정한다(아키텍처 결정 검증이지 산출물 채점이 아니다).
- **엔지니어용 구현 명세 작성** — 코드 생성용 실행가능 명세(spec) 작성은 명세 도메인이다.
- **단일 자율 반복 루프** — 한 목표를 통과할 때까지 한 흐름으로 반복 수행하는 것은 멀티 에이전트 *결정*이 아니다.
- **새 하네스/에이전트 팀을 처음부터 생성** — 도메인 하네스를 생성하는 것은 범위 밖이다(이 하네스는 *주어진 작업*의 오케스트레이션을 결정한다).
- **프로덕션 장애 대응·운영** — 인시던트 탐지·완화는 운영 도메인이다.

경계가 모호하면 한 질문으로 확인한다 — "여러 에이전트를 쓸지/어떻게 협업시킬지 *결정*하려는 건가요, 아니면 *다른 것*(컨텍스트 조립·산출물 평가·명세 작성·단일 반복 루프)인가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **에이전트 수 ≠ 이득** — 멀티의 성패는 architecture-task alignment가 결정한다. 같은 작업도 토폴로지에 따라 단일 대비 큰 이득과 큰 손해로 갈린다(references §1).
- **capability ceiling(언제 병렬화하면 안 되는가)** — 단일 에이전트가 *이미 충분히 잘 푸는* 작업은 에이전트 추가가 음의 수익일 수 있다(coordination 비용 > 한계 개선, references §2). 이는 *경험적 임계*지 결정론적 rule이 아니다 — decomposability·tool density·토폴로지가 뒤집을 수 있다.
- **협업에는 비용이 든다(curse of coordination)** — 에이전트 협업은 사람 팀과 달리 '인원 추가 = 생산성 증가'가 보장되지 않는다. 페어 협업이 각자 수행보다 성공률이 떨어지는 경향이 보고된다(references §3, 방향성 성립·크기 비균일).
- **실패는 root-cause로 조직화** — 협업 실패는 증상이 아니라 communication·commitment·expectation 세 메커니즘으로 진단한다(references §4). 가드는 각 메커니즘을 겨냥한다(expectation이 최대 실패원, 우선).
- **컨텍스트는 격리한다** — N개 에이전트가 컨텍스트를 공유하면 cross-agent 오염이 결정 품질을 떨어뜨릴 수 있다(references §5, 질적 메커니즘만). per-agent 격리로 완화한다.
- **baseline 대비 순이득으로 검증** — 마지막 게이트는 'multi라서 좋다'가 아니라 *단일 baseline 대비 순이득이 양인가*다. 증명 못 하면 단일을 권고하고 병렬화를 *거절*한다.
- **falsifiable·over-rule 금지** — 모든 휴리스틱(capability-ceiling 임계·alignment 부호)은 관찰 가능한 입력으로 적어 반증 가능하게 하되, 단정적 '법칙'으로 과강화하지 않는다.
- **관찰 가능성·승인** — Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 결과를 보고한다. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Decompose & Assess | `task-decomposer` | 분해 가능성·도구 밀도·의존 구조 평가 + 단일 에이전트 baseline 추정 |
| 1 Decide Architecture | `architecture-selector` | 선택 규칙 적용 → single vs multi + 토폴로지(centralized/independent) 권고 |
| 2 Design Coordination | `coordination-designer` | communication/commitment/expectation 가드 + context-pollution 격리 설계 |
| 3 Verify-or-Reject | `orchestration-verifier` | 계획이 단일 baseline을 능가하는지 적대 검증, 병렬화 금지면 플래그·단일 권고 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 분해 신호 평가·아키텍처 선택·baseline 순이득 추론의 품질이 결정의 정확성을 좌우한다.

## 참조 문서

- 멀티 에이전트 오케스트레이션 원리·anti-pattern·선택 규칙·토폴로지/협업 설계 지침: [references/agent-orchestration-principles.md](./references/agent-orchestration-principles.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도·caveat·반박된 주장): [references/agent-orchestration-research.md](./references/agent-orchestration-research.md)

---

# 인터랙티브 플로우

## Phase 0 — 작업 분해·평가 (Decompose & Assess) · 승인 게이트

`task-decomposer`를 호출해 작업을 멀티 에이전트 결정의 *입력 신호*로 변환한다 — 분해 가능성·도구 밀도·의존 구조 + 단일 에이전트 baseline 추정.

```
Agent(
  subagent_type="task-decomposer", model="opus",
  prompt="""
  [역할] 작업을 멀티 에이전트 결정의 입력 신호로 변환한다.
  [입력] 작업: {사용자 발화}
  [규칙] 작업을 독립 검증 가능한 하위작업으로 분해하고 의존 그래프(직렬/병렬)를 그린다.
         decomposability·tool density를 관찰 가능한 근거로 평가한다(수치 발명 금지, 모르면 '미상').
         단일 에이전트가 지금 얼마나 잘 푸는지(baseline)를 추정하고, 이미 충분히 풀리면 capability-ceiling 후보로 표시한다.
         결정(single/multi)은 하지 않는다 — 결정의 입력만 만든다.
  [출력] Task Assessment(분해·신호·단일 baseline 추정·미상/가정).
  """
)
```

Task Assessment를 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 작업 분해·신호 평가 완료 — 다음: 아키텍처 결정. 진행할까요?`

승인 전에는 아키텍처 결정을 시작하지 않는다(잘못된 신호로 잘못된 병렬화를 권고하지 않기 위함).

## Phase 1 — 아키텍처 결정 (Decide Architecture)

`architecture-selector`를 호출해 Phase 0 신호에 선택 규칙을 적용한다 — single vs multi + 토폴로지.

```
Agent(
  subagent_type="architecture-selector", model="opus",
  prompt="""
  [역할] 신호에 선택 규칙을 적용해 아키텍처를 권고한다.
  [입력] Task Assessment(분해 가능성·도구 밀도·의존 구조·단일 baseline 추정): {Phase 0 산출}
  [규칙] architecture-task alignment를 우선한다(에이전트 수가 아니라 작업-아키텍처 정합이 성패를 가른다).
         단일 baseline이 이미 높으면(capability ceiling) 에이전트 추가의 음의 수익을 경고하고 단일을 기본 권고로 둔다.
         멀티면 토폴로지를 함께 권고한다 — independent는 centralized보다 오류 증폭이 크다.
         capability-ceiling 임계·alignment 부호는 경험적 경향이지 결정론적 rule이 아님을 명시하고,
         권고마다 '이 권고가 틀릴 조건'을 한 줄 단다. 멀티는 단일보다 나은 이유를 댈 수 있을 때만 권고한다.
  [출력] Architecture Recommendation(권고·근거·falsifiability·병렬화 금지 플래그).
  """
)
```

`single` 권고면 → Phase 2를 건너뛰고 Phase 3로 가서 "단일이 baseline 대비 우월/충분한가"를 확인한 뒤 마무리한다. `multi` 권고면 → Phase 2로 간다.

1줄 보고: `[Phase 1] 아키텍처 권고(single/multi·토폴로지) — 다음: {협업 가드 설계 | 단일 검증}. 진행할까요?`

## Phase 2 — 협업 가드 설계 (Design Coordination) · 멀티일 때만

`coordination-designer`를 호출해 협업 실패 가드 + 컨텍스트 격리를 설계한다.

```
Agent(
  subagent_type="coordination-designer", model="opus",
  prompt="""
  [역할] 멀티 에이전트 협업이 깨지지 않도록 coordination 가드를 설계한다.
  [입력] Architecture Recommendation(토폴로지·역할): {Phase 1 산출}
         의존 그래프(핸드오프 지점): {Phase 0 산출}
  [규칙] 협업 실패를 세 root-cause로 조직화해 각각 가드를 붙인다 —
         communication(모호·부정확 메시지로 채널 정체), commitment(약속 이탈), expectation(타 에이전트 계획·관측 오해).
         expectation이 최대 실패원이므로 우선한다. 메시지·동기화는 최소로(채널 정체 자체가 실패원).
         context pollution을 막기 위해 per-agent 컨텍스트 격리를 둔다(오케스트레이터는 에이전트별 경량 상태 요약,
         특정 에이전트 다룰 때만 풀 컨텍스트). 토폴로지에 맞춰 가드를 정합한다(independent는 핸드오프 계약을 더 엄격히).
         추가한 coordination 비용·가정을 명시해 Phase 3가 baseline과 비교하게 한다.
  [출력] Coordination Design(역할·경계·세 실패 가드·컨텍스트 격리·가드 비용/가정).
  """
)
```

1줄 보고: `[Phase 2] 협업 가드·컨텍스트 격리 설계 완료 — 다음: baseline 능가 검증. 진행할까요?`

## Phase 3 — baseline 능가 검증 / 거절 (Verify-or-Reject)

`orchestration-verifier`를 호출해 계획이 단일 에이전트 baseline을 *실제로* 능가하는지 적대적으로 검증한다.

```
Agent(
  subagent_type="orchestration-verifier", model="opus",
  prompt="""
  [역할] 멀티 에이전트 계획이 단일 에이전트 baseline을 실제로 능가하는지 적대적으로 검증한다.
  [입력] Architecture Recommendation: {Phase 1}
         Coordination Design(가드·비용·가정): {Phase 2, 멀티일 때}
         Task Assessment(단일 baseline 추정·의존 구조): {Phase 0}
  [규칙] 'multi라서 좋다'를 버리고 baseline 대비 순이득(멀티 이득 − coordination 비용 − 오류 증폭)이 양인지 따진다.
         curse of coordination을 비용으로 계상하고, 단일 baseline이 이미 높으면(capability ceiling) 병렬화를 강하게 비권고한다.
         적대적으로 '단일보다 못할 시나리오'를 먼저 찾는다(순차 의존·가드가 채널 정체 가중·independent 오류 증폭).
         순이득이 0 근처면 보수적으로 단일을 권고한다. 능가를 증명 못 하면 REJECT(단일 권고)가 정당한 결과다.
         아키텍처/가드를 직접 고치지 않고, 통과 못 하면 어느 Phase로 무엇을 바꿀지(REVISE) 신호만 낸다.
  [출력] Verification Verdict(PASS 멀티 채택 | REJECT 단일 권고 | REVISE) + 순이득 분석 + capability-ceiling 점검.
  """
)
```

분기:
- **PASS** → 멀티 에이전트 계획(아키텍처 + 가드)을 최종 권고로 확정한다.
- **REJECT** → 멀티를 거절하고 *단일 에이전트*를 권고한다(왜 단일이 나은지 + 단일로 진행하는 법 포함). 이것은 실패가 아니라 정당한 산출물이다.
- **REVISE** → 지정된 Phase(1: 토폴로지·역할 축소 / 2: 가드 단순화)로 되돌려 1회 보정 후 재검증한다. 같은 곳을 반복 REVISE해도 순이득이 안 남으면 단일을 최종 권고한다(불필요한 orchestration 회피).

1줄 보고: `[Phase 3] {PASS 멀티 채택 | REJECT 단일 권고 | REVISE}: {핵심 근거} — {다음 단계}`

## 마무리 — 결과 보고

플로우가 끝나면 다음을 요약 보고한다.

- **결정**: 단일 에이전트 / 멀티 에이전트(토폴로지: centralized|independent).
- **근거**: architecture-task alignment 신호 + baseline 대비 순이득 + (해당 시) capability-ceiling 플래그.
- **멀티면**: 역할·협업 가드(communication/commitment/expectation)·컨텍스트 격리 요약.
- **단일이면(REJECT)**: 왜 병렬화가 비권고인지 + 단일 에이전트로 진행하는 방법.
- **남은 불확실성**: baseline 추정이 미상이었던 부분과 그것을 줄일 관찰(예: 단일 dry-run).

보고 형식(최종): `[Orchestration 결정] {단일 | 멀티:토폴로지} — 순이득 {양/음/경계}, 근거 {핵심 신호}`
