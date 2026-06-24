# agent-orchestration

한 작업을 **여러 에이전트로 병렬화할지·어떻게 협업시킬지**를 *판단 규칙*으로 결정하고,
그 협업이 **단일 에이전트 baseline을 실제로 능가하는지** 적대적으로 검증하는 도메인 무관 멀티 에이전트 하네스입니다.

핵심 메시지는 하나입니다 — **"에이전트를 더 붙인다고 항상 이득이 아니다."**
멀티 에이전트의 이득/손해는 *에이전트 수*가 아니라 작업 속성과 아키텍처의 정합(architecture-task alignment)이 결정하고,
협업 자체에 비용(curse of coordination)이 들기 때문입니다. 그래서 이 하네스는 *언제 멀티가 정당한지, 언제 단일이 나은지*를 근거로 가립니다.

## 무엇을 결정하나 (네 질문)

1. 이 작업은 *나눌 수 있는가* — 분해 가능성·도구 밀도·의존 구조는? (Phase 0)
2. *단일로 할까 멀티로 할까*, 멀티면 *어떤 토폴로지*(centralized/independent)인가? (Phase 1)
3. 멀티라면 *협업이 깨지지 않게* 어떤 가드를 둘까? (Phase 2)
4. 이 계획이 *단일 baseline을 실제로 능가*하는가, 아니면 *병렬화하면 안 되는가*? (Phase 3)

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `agent-orchestration` 플러그인을 활성화하면,
`agent-orchestration` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `agent-orchestration` | 오케스트레이터(진입점). 작업 분해·평가(Task Assessment) → 아키텍처 결정(single/multi·토폴로지) → 협업 가드 설계 → baseline 능가 검증의 흐름을 진행하며, 각 단계에서 전용 에이전트(task-decomposer / architecture-selector / coordination-designer / orchestration-verifier)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Decompose & Assess | `task-decomposer` | 분해 가능성·도구 밀도·의존 구조 평가 + 단일 에이전트 baseline 추정 |
| 1 Decide Architecture | `architecture-selector` | 선택 규칙(architecture-task alignment·capability ceiling) → single/multi + 토폴로지 권고 |
| 2 Design Coordination | `coordination-designer` | communication/commitment/expectation 가드 + context-pollution 격리 설계 |
| 3 Verify-or-Reject | `orchestration-verifier` | 계획이 단일 baseline을 능가하는지 적대 검증, 병렬화 금지면 단일 권고(reject) |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- 한 작업을 **여러 에이전트로 나눌지 한 에이전트로 할지** 근거로 결정하고 싶을 때
- 멀티로 갈 때 **어떤 토폴로지**(centralized/independent)와 **어떤 협업 가드**를 둘지 설계하고 싶을 때
- "에이전트를 더 붙이면 정말 나아지는가"를 **단일 baseline과 비교해 검증**하고, 아니면 *병렬화하지 말라*는 결론까지 받고 싶을 때
- 에이전트 협업이 자꾸 깨질 때, 실패를 **communication/commitment/expectation root-cause**로 진단해 가드를 두고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖)**
- 모델에 넣을 **컨텍스트 페이로드 조립·압축**(retrieval·큐레이션) — 컨텍스트 설계 도메인. (단, 멀티 구성의 *에이전트별 컨텍스트 격리*는 이 하네스의 가드에 포함됩니다 — 페이로드 최적화가 아니라 cross-agent 오염 방지.)
- **AI 출력의 엄밀한 평가**(LLM-as-a-Judge·benchmark validity) — 산출물 평가 도메인. (이 하네스의 검증은 *아키텍처 결정*이 baseline을 능가하는가에 한정합니다.)
- **엔지니어용 구현 명세 작성**(코드 생성용 실행가능 spec) — 명세 도메인.
- **단일 자율 반복 루프**(한 흐름으로 통과까지 반복) — 멀티 에이전트 *결정*이 아닙니다.
- **새 하네스/에이전트 팀을 처음부터 생성** — 이 하네스는 *주어진 작업*의 오케스트레이션을 결정합니다.
- **프로덕션 장애 대응·운영** — 인시던트 대응 도메인.
- **커밋 메시지·PR 리뷰**, settings.json 설정 변경 — 범위 밖.

## 진행 방식 (5단계)

| 단계 | 무엇을 | 결과 |
|------|--------|------|
| 0 작업 분해·평가 | task-decomposer가 분해 가능성·도구 밀도·의존 구조 평가 + 단일 baseline 추정 | Task Assessment — **승인 게이트** |
| 1 아키텍처 결정 | architecture-selector가 선택 규칙 적용 | single/multi + 토폴로지 권고(+ 병렬화 금지 플래그) |
| 2 협업 가드 설계 | (멀티일 때만) coordination-designer가 가드·격리 설계 | 세 실패 가드 + per-agent 컨텍스트 격리 |
| 3 baseline 능가 검증 | orchestration-verifier가 순이득 적대 검증 | PASS(멀티 채택) / REJECT(단일 권고) / REVISE |
| — 마무리 | 결정·근거·가드(멀티면)·남은 불확실성 요약 | `[Orchestration 결정] {단일|멀티:토폴로지} — 순이득 {…}, 근거 {…}` |

- 시작 직후 Task Assessment **승인 게이트**(잘못된 신호로 잘못된 병렬화를 권고하지 않기 위함).
- `single` 권고면 Phase 2를 건너뛰고 Phase 3에서 "단일이 충분/우월한가"를 확인한 뒤 마무리합니다.
- **거절(REJECT)은 정당한 결과**입니다 — 멀티가 baseline을 못 넘으면 단일 에이전트를 권고하고 그 이유와 진행법을 함께 제시합니다.

## 도구 경계 (한 줄 변별)

- "여러 에이전트를 쓸지/어떻게 협업시킬지 *결정*" → **이 하네스**.
- "모델에 *무엇을 넣을지*(컨텍스트 조립·압축)" → 컨텍스트 설계 도메인.
- "산출물을 *엄밀히 채점*(judge 구성·validity)" → 평가 도메인.
- "코드 생성용 *실행가능 명세 작성*" → 명세 도메인.
- "한 목표를 *통과까지 한 흐름으로 반복*" → 단일 자율 반복 도메인.

## 근거 논문 (deep-research dossier)

설계 근거는 2025+ 1차 자료를 3-vote 적대 검증해 채택했습니다(출처·인용·신뢰도·CAVEAT·반박된 주장은 [references/agent-orchestration-research.md](skills/agent-orchestration/references/agent-orchestration-research.md)).

- **arXiv:2512.08296** — "Towards a Science of Scaling Agent Systems" (Yubin Kim et al.; Google Research·MIT·Google DeepMind·Anthropic; Dec 2025). *architecture-task alignment가 멀티 성패를 결정*(단일 대비 +80.8% ~ −70.0%), capability ceiling(단일 정확도가 경험적 임계 ~45% 초과 시 추가 에이전트 음의 수익), 오류 증폭(independent > centralized). vote 3-0(high). — 단, 45%는 경험적 임계지 결정론 rule이 아님(R²≈0.51).
- **arXiv:2601.13295** — "CooperBench: Why Coding Agents Cannot be Your Teammates Yet" (Khatua, Zhu, …, Diyi Yang; Jan 2026). *curse of coordination*(페어 협업이 각자 수행보다 평균 30% 낮은 성공률, 팀 크기 단조 감소) + 세 root-cause 실패 메커니즘(communication/commitment/expectation). vote high. — gap 크기는 난도별 비균일.
- **arXiv:2604.07911** — "Dynamic Attentional Context Scoping" (Nickson Patel; 2026). *context pollution*(N개 에이전트가 컨텍스트 공유 시 cross-agent 오염) → per-agent 격리 완화. vote 2-1(**medium** — 질적 메커니즘만 채택, 합성 벤치 수치 미채택).

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger)와 발동하면 안 되는 경우
(should-not-trigger — 컨텍스트 조립·AI 출력 평가·구현 명세·단일 반복 루프·하네스 생성·장애 대응 등 인접 도메인)를 정의해 트리거 정확도를 점검합니다.
`evals/evals.json`은 shipped 파일이 핵심 불변식(에이전트 수≠이득·capability ceiling·세 실패 가드·컨텍스트 격리·baseline 능가 검증·falsifiability·경계)을 명세·강제하는지 file:section 인용으로 채점합니다.
