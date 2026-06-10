# 연구 근거 (Research Foundations)

generator-harness의 설계 선택을 뒷받침하는 1차 출처 모음. deep-research(6각도 → 29출처 → 25주장 3표 적대검증 → 21확정/4기각)의 confirmed 결과만 싣는다. SKILL.md의 보충 자료이며, 운영 규칙이 아니라 **근거·반증·미해결**을 담는다.

## 목차
1. [자동 에이전트 설계/탐색](#1-자동-에이전트-설계탐색)
2. [평가 신호 — Pareto와 전이성](#2-평가-신호--pareto와-전이성)
3. [Anthropic 빌딩블록](#3-anthropic-빌딩블록)
4. [반증된 주장 (과장 금지)](#4-반증된-주장-과장-금지)
5. [미해결 질문 (설계에 반영한 보수적 선택)](#5-미해결-질문-설계에-반영한-보수적-선택)

---

## 1. 자동 에이전트 설계/탐색

네 논문이 서로 다른 탐색공간·최적화로 같은 문제(하네스를 자동 탐색)를 푼다. 각 항목은 3표 만장일치(또는 명시된 split)로 검증됐다.

| 논문 | 탐색공간 | 최적화 | 본 도구 적용 | 출처 |
|------|----------|--------|--------------|------|
| **ADAS** (Meta Agent Search) | 코드 전체 = Turing-complete (프롬프트·도구·워크플로 임의 조합) | 이전 발견 아카이브 기반 메타 에이전트가 반복 프로그래밍 | 후보를 코드/모듈 spec으로 정의; 진화 라운드에 직전 후보 노출. **무제약 합성은 디폴트 아님**(논문도 "최적해 탐색은 virtually impossible" 인정) | [2408.08435](https://arxiv.org/abs/2408.08435) |
| **AFlow** | 코드로 표현된 워크플로(LLM 노드+엣지) | MCTS + code modification + tree-structured experience + **execution feedback** | 채점에 execution feedback(dry-run) 사용; SOTA 대비 +5.7% | [2410.10762](https://arxiv.org/abs/2410.10762) |
| **AgentSquare** (MoLAS) | **모듈러 4종**: Planning·Reasoning·Tool Use·Memory + uniform IO | **module evolution(신규) + recombination(재조합)** | **디폴트 탐색공간·진화 연산자** (ADAS 전체 코드탐색의 의도적 부분집합) | [2410.06153](https://arxiv.org/abs/2410.06153) |
| **MaAS** | agentic supernet = 아키텍처 확률·연속 분포 | 질의별 샘플링 + 난이도별 자원 동적 할당 | 전이성을 도메인 무관성 검증축으로; 라운드 비용 게이트의 지향점 | [2502.04180](https://arxiv.org/abs/2502.04180) |
| **GPTSwarm** | 계산 그래프(노드=프롬프트, 엣지=토폴로지) | node + edge 동시 최적화(연속완화+REINFORCE) | 후보 설계 시 노드(프롬프트)와 엣지(에이전트 연결)를 분리해 기술 | [PMLR v235](https://proceedings.mlr.press/v235/zhuge24a.html) |

**핵심 함의:** 표현력(ADAS)과 탐색가능성(AgentSquare 모듈 제약)은 trade-off다. 본 도구는 **AgentSquare 모듈러를 디폴트, ADAS 코드확장을 상위옵션**으로 둔다. 또한 **디폴트 탐색은 경량 evolution/recombination**(Phase 5, ≤2라운드)이며, AFlow의 MCTS·MaAS의 supernet은 *그 자체*가 아니라 **평가신호**(정확도-비용 Pareto·전이성·dry-run feedback)만 차용한다(풀스케일 MCTS/supernet은 opt-in 지향점).

## 2. 평가 신호 — Pareto와 전이성

검증된 가장 실무적 교훈: **하네스 품질 = 정확도 × 토큰비용 Pareto** (단일 정확도 금지).

- **AFlow** — 작은/싼 모델이 GPT-4o를 *특정 태스크에서* 능가, 비용은 **4.55%**. ('on specific tasks' 한정어 보존 — 보편 보장 아님) [2410.10762](https://arxiv.org/abs/2410.10762)
- **MaAS** — 기존 비용의 **6~45%로 +0.54~11.82%** = Pareto 우월, 그리고 **cross-dataset·cross-LLM-backbone 전이성** 우수. (수치는 저자보고 best-case '범위' — 단일 보장으로 인용 금지) [2502.04180](https://arxiv.org/abs/2502.04180)

→ 본 도구 Phase 4 채점은 `pareto_coord{quality, cost}` + `transfer_score`를 **반드시** 산출한다. 전이성이 "도메인 무관성"의 조작적 정의다.

## 3. Anthropic 빌딩블록

후보를 *무엇으로 조립할지*에 대한 1차(first-party) 근거.

- **Context Engineering** ([anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)) — "추론 중 system instructions·tools·MCP·external data·history 전체를 관리하며 최적 토큰 집합을 큐레이션" = 하네스의 정의. 서브에이전트는 **clean context로 1,000~2,000 토큰 요약만 반환**.
- **Building Effective Agents** ([anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)) — **workflows(고정 코드경로) vs agents(동적 자기지휘)** 2분류 + **5패턴**: prompt chaining / routing / parallelization(sectioning·voting) / orchestrator-workers / evaluator-optimizer.
- **Multi-agent Research System** ([anthropic.com/engineering/multi-agent-research-system](https://www.anthropic.com/engineering/multi-agent-research-system)) — orchestrator-worker가 breadth-first 탐색에서 단일 대비 **+90.2%** (단, ~15배 토큰비용). → 멀티에이전트 이득은 task-dependent.
- **반대 관점 (균형)** — Cognition "Don't Build Multi-Agents" ([cognition.ai/blog/dont-build-multi-agents](https://cognition.ai/blog/dont-build-multi-agents)): read-only 탐색 서브에이전트는 지지하나, 병렬 *의사결정* 서브에이전트(충돌)는 경계. → proposer/evaluator는 read·채점 전용이라 본 패턴과 정합.

## 4. 반증된 주장 (과장 금지)

3표 적대검증에서 **죽은** 주장. 본 도구 설계·산출 보고에서 *약속하면 안 된다*.

- ❌ "자동탐색이 **코딩·과학·수학 전 도메인**에서 수동설계를 압도" (ADAS, **0-3**)
- ❌ "발견된 에이전트가 **도메인·모델 전이에서도 우월**" (ADAS, 1-2) — MaAS만 전이성 입증
- ❌ "AgentSquare가 6벤치 **평균 +17.2%로 전 도메인 우위**" (1-2) → "재사용 가능한 탐색공간 추상화"로만 인용
- ❌ Anthropic "**context rot / n² attention budget**" 논거 (1-2) → 컨텍스트 유한성 일반론은 신중히

**정직한 주장 범위 = "자동탐색은 *특정 벤치/태스크에서* 효과적이고 비용효율을 개선한다"까지.** 이 한계가 Phase 6 승인 게이트와 confidence 하향 보고의 근거다.

## 5. 미해결 질문 (설계에 반영한 보수적 선택)

deep-research가 1차 출처로 확정하지 못한 빈틈 — 본 도구는 이를 *보수적 디폴트*로 흡수한다.

1. **탐색 비용** — 하네스 한 묶음을 자동 생성하는 LLM 호출·달러·시간은 미보고. → **경량 탐색 디폴트**(N=3, 진화 ≤2). 풀스케일은 opt-in.
2. **개방형 도메인 평가신호** — 정답·자동채점기 없는 도메인의 execution feedback/LLM-judge 신뢰성 미확정. → **confidence 하향 + 승인 게이트**가 안전망.
3. **자기진화 루프** — Voyager/Reflexion/Gödel Agent는 confirmed 집합 밖. → 생성된 하네스의 *사후* 개선은 meta-harness에 위임(본 도구는 생성까지).
4. **안전 게이트의 학술 근거** — human approval·비후퇴의 academic best practice 미확정. → meta-harness의 승인 게이트·Pareto 비후퇴 DNA를 그대로 차용.
