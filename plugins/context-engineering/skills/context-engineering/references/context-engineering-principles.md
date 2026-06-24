# Context Engineering — 원리·anti-pattern·설계 지침

이 문서는 `context-engineering` 하네스 4단계(Scope → Retrieve → Process → Manage)와 멀티 에이전트 격리 패턴의
설계 원리·실패모드·지침을 모은다. 근거 출처·인용·신뢰도는 [context-engineering-research.md](./context-engineering-research.md)와 상호 참조된다.
빠르게 변하는 분야이므로 각 절 끝에 신뢰도와 caveat을 함께 표기한다.

## 1. context engineering이란 — 프롬프트 설계와의 구분

**Context Engineering = "단순 프롬프트 설계를 넘어, LLM에 전달하는 *정보 페이로드*를 체계적으로 최적화하는 것."**
프롬프트 엔지니어링이 *지시 문구를 다듬는* 것이라면, context engineering은 *모델의 컨텍스트 윈도우에 무엇을 어떤 형태로
채울지*를 설계한다 — 무엇을 가져오고(retrieve), 무엇을 생성하고(generate), 무엇을 압축·정렬하고(process), 무엇을
누적·격리·관리하는가(manage). 핵심 전환은 **"많이 넣기"가 아니라 "필요한 정보를 정확히 닿게 하기"** 다.
(신뢰도 high, 3-0) — arXiv:2507.13334 "A Survey of Context Engineering for LLMs."
> caveat: "formal discipline"(정식 학문)이라는 프레이밍은 저자들의 것이며, 일부 실무자는 이를 prompt engineering의
> 리브랜딩이라 비판한다(HN 토론). "보편 합의된 분야"로 단정하지 말고, *실무 설계 규율*로서 채택한다.

## 2. 4단계 구조의 근거 (foundational components)

arXiv:2507.13334은 Context Engineering을 세 **foundational component**로 분해한다 — **context retrieval and
generation · context processing · context management** — 그리고 그 위에 아키텍처 구현(RAG · memory systems and
tool-integrated reasoning · multi-agent systems)을 둔다. 이 도메인 무관 taxonomy가 본 하네스 단계 구조의 근거다.
- 본 하네스는 세 component를 **Phase 1(Retrieve/Generate) · Phase 2(Process) · Phase 3(Manage)** 로 직접 매핑하고,
  그 앞단에 **Phase 0(Scope)** 를 게이트로 얹었다 — 수집·압축 전에 "무엇이 *반드시* 도달해야 하고 예산은 얼마인가"를
  먼저 정의해, 빈약한 범위 위에 비싼 수집·압축을 쌓지 않기 위함이다.
- 아키텍처 구현 중 **RAG**는 Phase 1의 retrieval and generation으로, **multi-agent**는 Phase 3의 격리 설계로 들어온다.
(신뢰도 high, 3-0) — arXiv:2507.13334.

## 3. Phase별 설계 지침

### Phase 0 Scope — retrieval need + 토큰 예산
- 수집 전에 retrieval need를 must-have / nice-to-have / out-of-scope로 분류하고, 각 need에 "왜 필요한가(없으면 무엇이
  막히나)"를 정당화한다. 정당화되지 않는 정보는 페이로드에 넣지 않는다.
- 전체 토큰 예산을 정한다(윈도우·작업·비용 근거). 예산이 이후 압축·우선순위의 하드 기준이 된다.
- 컨텍스트가 단일 호출용인지, *여러 에이전트가 공유하는 오케스트레이터 컨텍스트*인지 판정한다(후자면 Phase 3 격리 필요 플래그).

### Phase 1 Retrieve/Generate — 후보 풀(누락 방지가 목표)
- need 기반으로 retrieve(존재하는 사실)·generate(없는 합성)을 구분하고, 생성물은 명시한다.
- 각 후보에 출처·충족 need·relevance·토큰을 붙인다. *여기서 성급히 요약·삭제하지 않는다* — 절삭은 Phase 2 책임.
- must-have need 미충족은 *생성으로 메우지 말고 보고*한다(환각 컨텍스트는 가장 비싼 오류).

### Phase 2 Process — 압축·정렬·중복제거(신호 보존이 목표)
- 예산 준수와 신호 보존을 동시에 만족시킨다. 그냥 짧게가 아니라, 필요한 정보가 *닿도록* 압축한다.
- 의미 중복만 제거하고 충돌(다른 값)은 보존·표시한다. 출처를 보존한다.

### Phase 3 Manage — playbook 큐레이션·격리·검증
- 컨텍스트를 진화하는 playbook으로 큐레이션한다(generation/reflection/curation, §5).
- 멀티 에이전트면 per-agent 격리를 설계한다(§6).
- 출하 전 검증한다 — 예산·must-have 충족·충돌·출처·위치 배치(검증 없는 출하 금지).
(신뢰도 high, 3-0) — arXiv:2507.13334 component 정의 + arXiv:2510.04618 큐레이션.

## 4. anti-pattern — 컨텍스트 처리의 4대 실패모드

좋은 컨텍스트 엔지니어링은 다음 실패모드를 *구조적으로* 막는다.

1. **brevity bias** — 간결한 요약을 위해 도메인 통찰을 떨어뜨림. arXiv:2510.04618(ACE)의 표현: prior approaches가
   "drops domain insights for concise summaries." → 대응: 도메인 디테일(수치·식별자·경계조건·예외)은 요약하지 말고 보존.
2. **context collapse** — 반복 재작성이 디테일을 시간에 걸쳐 침식("iterative rewriting erodes details over time").
   → 대응: 전면 재작성 금지, "detailed knowledge를 보존하는 구조적·증분적 업데이트"(추가/표시지 통째 재작성 아님).
3. **lost-in-the-middle** — 긴 컨텍스트에서 모델은 처음·끝을 잘 활용하고 중간을 덜 활용함. → 대응: 가장 중요한 컨텍스트를
   페이로드 앞·뒤로 위치 배치(Phase 2). (lost-in-the-middle은 컨텍스트 위치 효과로 널리 관찰되는 현상이며, 본 하네스는
   *위치 인지 배치*를 처리 단계의 기본 가드로 둔다.)
4. **context pollution** — 여러 에이전트가 한 오케스트레이터 윈도우를 공유할 때 서로의 task state·부분 출력이 상호 오염
   (§6). → 대응: per-agent 격리(REGISTRY/FOCUS).
(brevity bias·context collapse: 신뢰도 high, 3-0 — arXiv:2510.04618. context pollution: 질적 메커니즘만, §6 caveat 참조.)

## 5. playbook 큐레이션 — 진화하는 컨텍스트 (ACE)

arXiv:2510.04618(Agentic Context Engineering, ACE)은 컨텍스트를 일회성 system prompt가 아니라 **"축적·정련·조직되는
진화하는 playbook"** 으로 다룬다. 모듈식 과정은 세 역할이다:
- **generation** — 무엇을 컨텍스트에 넣었는가(전략·출처).
- **reflection** — 무엇이 효과적이었고 무엇이 불필요/과적재였나 성찰.
- **curation** — 검증된 항목만 누적·정련(전면 재작성 아닌 증분).

본 하네스 적용: context-curator가 playbook.md를 *증분적으로* 갱신해, 회차를 거치며 효과적인 컨텍스트 전략이 쌓이게 한다.
고정 system prompt와 구별되는 점은 "컨텍스트가 *진화*한다"는 것이다. (ACE는 agent benchmark에서 baseline 대비 +10.6%,
finance에서 +8.6%를 보고한다 — 단, 이는 ACE 전체 시스템의 수치이며 본 하네스가 같은 이득을 *보장*하지 않는다. 본 하네스는
ACE의 *playbook 큐레이션·구조적 증분* 설계 원리를 채택한다.)
(신뢰도 high, 3-0) — arXiv:2510.04618.
> caveat: +10.6%/+8.6%는 ACE 시스템·특정 벤치 수치다. "개선 N% 보장"으로 일반화하지 말 것. 채택하는 것은 설계 원리(진화하는
> playbook·구조적 증분·brevity/collapse 가드)이지 수치가 아니다.

## 6. 멀티 에이전트 격리 — context pollution과 REGISTRY/FOCUS

여러 에이전트가 한 오케스트레이터 컨텍스트 윈도우를 공유하면, 각 에이전트의 task state·부분 출력·미결 질문이 다른 모든
에이전트의 steering 상호작용을 오염시켜 의사결정 품질을 떨어뜨린다 — **context pollution**. arXiv:2604.07911(DACS)이
이 실패모드를 서술하고, 격리 패턴을 제시한다:
- **REGISTRY 모드** — 오케스트레이터가 에이전트당 *가벼운 상태요약*(예: ≤200 토큰)만 보유해, 모든 에이전트·사용자에게 반응한다.
- **FOCUS(a_i) 모드** — 한 에이전트가 STEERING REQUEST를 보내면, 오케스트레이터가 그 에이전트 a_i의 *풀 컨텍스트*를 주입하고
  나머지 에이전트는 registry 항목으로 압축한다(asymmetric·deterministic·agent-triggered 격리).

본 하네스 적용: context-curator가 멀티 에이전트 공유 컨텍스트일 때만 이 격리를 설계한다(단일 호출이면 불필요한 복잡도 추가 금지).
이는 *벤더 비종속 오케스트레이션 패턴*이며, 멀티 에이전트 시스템에서 subagent별 독립 컨텍스트 윈도우를 두는 업계 실천과 같은
메커니즘이다.
(질적 메커니즘: 신뢰도 medium, vote 2-1 — arXiv:2604.07911 + 업계 실천·context-rot 문헌이 독립 보강.)
> **CAVEAT(중요)**: arXiv:2604.07911은 단독저자·비피어리뷰 preprint다. 정량수치(예: 90-98% vs 21-60%)는 대부분 합성 벤치
> (200 중 160이 scripted stub, 실제 LLM은 40 trial)에서 나온 것이라 **수치는 인용하지 않는다**. 채택하는 것은 *질적 실패모드
> (context pollution)와 격리 패턴의 형태(REGISTRY/FOCUS)* 뿐이다. 격리가 오염을 막는다는 질적 메커니즘은 멀티 에이전트
> 시스템의 subagent별 독립 컨텍스트 실천과 context-rot 문헌이 독립적으로 보강하므로, *질적 설계 패턴*으로만 신뢰한다.

## 7. 설계 불변식 (요약)

- **Scope 우선** — retrieval need·예산을 먼저 정의(없으면 비싼 수집·압축이 흔들린다).
- **누락 방지 → 신호 보존 → 검증** — 단계별 책임 분리(수집은 과수집 허용, 처리는 절삭·정렬, 관리는 큐레이션·검증).
- **구조적 증분** — 전면 재작성 금지(brevity bias·context collapse 가드).
- **위치 인지** — 핵심을 앞·뒤로(lost-in-the-middle 가드).
- **격리(opt-in)** — 멀티 에이전트 컨텍스트일 때만 REGISTRY/FOCUS.
- **사실 보존·출처 추적** — 생성 금지, 출처를 페이로드까지 보존, 빈 must-have를 생성으로 메우지 않음.
- **검증 없는 출하 금지** — 예산·충족·충돌·출처·배치를 curator가 검증.
- **승인 게이트·관찰성** — Phase 0 Brief 승인, 매 단계 토큰 보고, 사이드 에이전트·중복 실행 금지.

## 8. 참고문헌 (전문·인용은 research dossier)

- arXiv:2507.13334 — A Survey of Context Engineering for LLMs (정의·taxonomy 근거).
- arXiv:2510.04618 — Agentic Context Engineering / ACE (playbook 큐레이션·brevity bias·context collapse).
- arXiv:2604.07911 — Dynamic Attentional Context Scoping / DACS (context pollution·REGISTRY/FOCUS, medium·caveat).

상세 인용·신뢰도·반박된 주장은 [context-engineering-research.md](./context-engineering-research.md) 참조.
