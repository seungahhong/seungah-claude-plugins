# Code as Agent Harness — 연구 dossier (cited)

> 이 문서는 `code-as-harness` 하네스 설계의 근거가 된 조사 결과다(deep-research: 도메인 질문을 5각도로 팬아웃
> [primary-paper · method-components · academic-adjacent · practitioner-implementation · failure-modes-guardrails] →
> 20개 소스 fetch → 96개 주장 추출 → 상위 25개를 3-vote 적대 검증 → **24 confirmed / 1 killed** → 11개로 종합,
> 2026-06-25 기준). 출발점은 **arXiv:2605.18747 "Code as Agent Harness: Toward Executable, Verifiable, and Stateful
> Agent Systems"**(Xuying Ning et al., UIUC/Meta/Stanford, 2026-05) 정독이다.
> [code-as-harness-principles.md](./code-as-harness-principles.md)의 원칙과 상호 참조된다(§N은 이 dossier의 절 번호).
>
> **정직성 가드(머리말).** (1) 대상 서베이(2605.18747)는 **개념적·조직적 프레임워크**이지 실험적으로 검증된 벤치마크
> 결과가 아니다 — 3-layer 분류는 저자들의 *설계 스캐폴드*로 견고하나 "이 구조가 N% 더 낫다"는 주장이 아니다. (2) 여러
> 보강 근거는 *인접 논문*(2604.08224·2506.11442·2604.20801·2508.00083·2512.14012)이다 — 같은 harness 프레이밍을
> 보강·운영화하나 **별개의 연구**이므로 그들의 구체 기법(ReVeal의 TAPO, AgentFlow의 DSL)을 대상 서베이에 귀속하지
> 않는다. (3) AgentFlow의 'several-fold(4x, 20%→80%)' 민감도는 *특정 취약점 발견/TerminalBench-2 세팅*의 관찰값이지
> 보편 법칙이 아니다. (4) AgentFlow의 정확한 4-phase 루프(Propose/Execute&Observe/Score/Diagnose) 주장은 적대
> 검증에서 **반박(1-2)** 되어 본문 근거로 쓰지 않는다(아래 "반박된 주장"). (5) "개선 N% 보장"을 쓰지 않는다.

---

## §1. 코드는 운영 기반(operational substrate) — *산출물이 아니라 executable·inspectable·stateful 매체*

- **제목**: "Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems"
- **저자/연도**: Xuying Ning, Katherine Tieu, Dongqi Fu, Tianxin Wei, Zihao Li, Yuanchen Bei, Jiaru Zou et al.
  (UIUC/Meta/Stanford, ~42 저자); submitted 2026-05-18 (**1차 표적 소스**)
- **출처**: https://arxiv.org/abs/2605.18747 · https://arxiv.org/html/2605.18747v1 · https://huggingface.co/papers/2605.18747 ·
  https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: emerging agentic systems에서 **코드는 더 이상 target output만이 아니다** — 에이전트가 *추론·행동·환경 모델링·
  실행 기반 검증*을 하는 **운영 기반(operational substrate)** 이다. 코드의 세 성질이 명시 정의된다 — **executable**(모델
  출력이 *형식적으로 검증 가능한 결과를 갖는 연산*이 된다), **inspectable**(중간 계산이 harness가 *읽고·저장하고·행동에
  쓸 수 있는 구조화된 trace*로 노출된다), **stateful**(진화하는 프로그램이 *단계 너머로 영속하는 task 진행 상태*를 표상한다).
- **인용**: "code is no longer only a target output. It increasingly serves as an operational substrate for agent reasoning,
  acting, environment modeling, and execution-based verification." / "an executable, inspectable, and stateful medium through
  which agents reason, act, observe feedback, and verify progress." / "Unlike natural language, code is executable, meaning
  model outputs become operations with formally verifiable outcomes; inspectable, meaning intermediate computation is exposed
  as structured traces that the harness can read, store, and act upon."
- **CAVEAT**: 서베이(개념 프레임). v1(2026-05)이라 개정 가능 — 절 번호·challenge 목록이 버전 간 바뀔 수 있다.

## §2. 3-layer 프레임워크 — Interface / Mechanisms / Scaling

- **출처**: 동 §1 소스
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: 서베이는 code-as-harness를 세 층으로 조직한다 — **(1) Harness Interface**: 코드가 에이전트를 *추론·행동·환경
  모델링*에 연결(§2). **(2) Harness Mechanisms**: *planning · memory/context engineering · tool use · feedback-driven
  control · optimization*(§3). **(3) Scaling**: single-agent → multi-agent, *공유 코드 artifact* 위에서 coordination·
  review·verification(§4). 본 하네스는 단일 에이전트 제어 사이클(Layer 2의 control loop)에 초점을 두고, multi-agent
  scaling(Layer 3)은 명시적으로 범위 밖에 둔다.
- **인용**: HTML 절 제목 — §2 "Harness Interface: Code for Reasoning, Acting, and Environment Modeling"; §3 "Harness
  Mechanisms: Planning, Memory, Tool Use, Control, and Optimization"; §4 "Scaling the Harness: Multi-Agent Orchestration over
  Code." / "shared code artifacts support multi-agent coordination, review, and verification."
- **CAVEAT**: Layer 3 하위요소(Shared-Harness Synchronization·Harness-State Convergence)는 저자 GitHub repo에서 확인 —
  multi-agent shared-state는 서베이가 **open challenge**로도 명명(§5).

## §3. Plan-Execute-Verify 제어 루프 + 샌드박스·권한 실행 — *Layer 2의 control*

- **출처**: https://arxiv.org/html/2605.18747v1 · https://huggingface.co/papers/2605.18747
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: Harness Mechanisms 층은 **'Plan, Execute, and Verify' 제어 루프**를 중심에 둔다(§3.4). 운영 방식: **계획은
  의도한 변경에 대한 *계약(contract)* 을 이루고**, 실행은 그것을 **샌드박스·권한 환경(sandboxed and permissioned
  environments)** 안에서 적용하며, **검증은 결정적 센서(deterministic sensors) + human-review gate**로 한다. §3.4 하위에
  "Sandboxed Execution and Permissioned State Transition"이 있고, §3.5 "Agentic Harness Engineering for Adaptive Harness
  Optimization"(§3.5.1 "Deep Telemetry as the Optimization Substrate")이 최적화를 다룬다.
- **인용**: "plans form contracts over intended changes, execution applies them inside sandboxed and permissioned
  environments, and verification uses deterministic sensors and human-review gates." / 절 제목 "Harness Control through the
  Plan, Execute, and Verify Loop" · "Sandboxed Execution and Permissioned State Transition" · "Deep Telemetry as the
  Optimization Substrate."
- **CAVEAT**: Plan-Execute-Verify는 mechanisms 중 *하나의 제어 패턴*이지 유일 메커니즘이 아니다(planning·memory·tool
  use·optimization과 병렬). 본 하네스는 이 control 패턴을 4 Phase로 운영화한다.

## §4. 실행 기반 검증의 근거 — *코드는 executable + inspectable이라 NL보다 검증 가능*

- **출처**: https://huggingface.co/papers/2605.18747 · https://arxiv.org/html/2605.18747v1
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 코드를 harness로 쓰는 이점은 자연어 대비 **결과가 형식적으로 검증 가능**(executable)하고 **중간 계산이
  구조화된 trace로 노출**(inspectable)된다는 점이다 — 이것이 *실행 기반 검증*을 스킬 설계 원칙으로 삼는 load-bearing 근거다.
- **인용**: §1 인용 재게재("model outputs become operations with formally verifiable outcomes ... structured traces that
  the harness can read, store, and act upon").
- **CAVEAT**: '형식적으로 검증 가능'은 *센서가 있는 한*이다 — 센서가 불완전하면 검증도 불완전(§5 open challenge "verification
  under incomplete feedback"와 연결).

## §5. 서베이가 명명한 open challenge = 본 하네스의 가드레일

- **출처**: https://arxiv.org/abs/2605.18747 · https://huggingface.co/papers/2605.18747
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 서베이는 harness engineering의 open challenge를 열거하는데, 이들이 곧 본 하네스의 **anti-pattern/가드레일**로
  매핑된다 — **(a) evaluation beyond final task success**(최종 성공만으로 보상/판정하지 말 것 → 불변식·부작용도 검증),
  **(b) verification under incomplete feedback**(부분 센서에서 PASS 단정 금지 → UNVERIFIED·confidence 강등), **(c)
  regression-free harness improvement**(개선이 통과한 것을 깨지 말 것), **(d) consistent shared state across multiple
  agents**(다중 에이전트 공유 상태 — 본 하네스는 단일 사이클로 한정), **(e) human oversight for safety-critical
  actions**(안전임계 행동은 사람 감독 게이트), (f) multimodal 확장.
- **인용**: "We further outline open challenges for harness engineering, including evaluation beyond final task success,
  verification under incomplete feedback, regression-free harness improvement, consistent shared state across multiple
  agents, human oversight for safety-critical actions, and extensions to multimodal environments."
- **CAVEAT**: 서베이는 이들을 *미해결 과제*로 명명할 뿐 구체적 해법·메트릭을 주지 않는다(openQuestion). 본 하네스는 이를
  *가드(설계 제약)* 로 운영화하되 만능 해결로 약속하지 않는다.

## §6. Externalization — *weights → context → harness* (인접 1차)

- **제목**: "Externalization in LLM Agents" (Zhou et al., SJTU/Sun Yat-Sen/CMU/OPPO, 2026-04)
- **arXiv ID**: arXiv:2604.08224
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: 에이전트 진보는 *모델 가중치 변경*보다 **런타임 재조직**에서 온다 — Memory(시간 너머 상태)·Skills(절차적
  전문성)·Protocols(상호작용 구조)·**Harness Engineering(이들을 governed execution으로 조율하는 통합 층)**. "from weights
  to context to harness"라는 역사적 진행을 그린다. → 본 하네스의 전제("성패는 모델만이 아니라 더 나은 외부 인지
  인프라/harness가 좌우")를 인접 각도에서 보강.
- **인용**: "built less by changing model weights than by reorganizing the runtime around them ... harness engineering serves
  as the unification layer that coordinates them into governed execution." / "We trace a historical progression from weights
  to context to harness." / "practical agent progress increasingly depends not only on stronger models, but on better
  external cognitive infrastructure."
- **CAVEAT**: *별개 서베이*다 — 대상 2605.18747의 주장으로 귀속하지 않고 *수렴하는 인접 프레이밍*으로 인용.

## §7. 프로 개발자는 vibe하지 않고 *통제*한다 — plan-first + 전 산출물 검증 (인접 1차)

- **제목**: "Professional Software Developers Don't Vibe, They Control" (N=13 관찰 + N=99 설문, 2025-12)
- **arXiv ID**: arXiv:2512.14012
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: 숙련 개발자는 **vibe coding을 하지 않는다** — *계획·감독으로 에이전트를 통제*하고 **모든 agentic 산출물을
  검증**한다. 11/13이 새 기능을 만들며 설계를 통제(계획을 리뷰하거나 직접 작성), 13/13이 구현을 통제(에이전트가 설치한
  의존성 거부·오동작 코드 수동 디버깅). → 본 하네스의 *계획 계약(Phase 0) + 안전임계 사람 게이트(Phase 1) + 실행 검증
  (Phase 2)* 을 이론이 아닌 실무 관행으로 접지.
- **인용**: "professional developers do not vibe code. Instead, they carefully control the agents through planning and
  supervision." / "they plan before implementing and validate all agentic outputs."
- **CAVEAT**: 소표본 관찰 연구(N=13) + 설문(N=99). 방향(통제·검증이 실무 기본)은 견고하나 효과 *크기*는 인용하지 않는다.

## §8. 검증 전술 — *line-by-line·테스트 실행·린트* (인접 1차)

- **출처**: arXiv:2512.14012 (동 §7)
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 프로의 검증 전술 — 요구(PRD) 대비 계획/코드 line-by-line 리뷰, UI/IDE 진행 점검, 터미널 기능 테스트, 린터
  피드백·테스트 실행 리뷰. 설문자들은 평균적으로 **약 절반(3.0/5)** 에이전트 생성 코드를 수정한다고 보고. → 본 하네스의
  Phase 2 결정적 센서 집합(테스트·빌드·타입·린트·실행)의 실무 근거.
- **인용**: Table 2 — "Verified plan output line-by-line against PRD requirements" · "Tested functionality in terminal" ·
  "Reviewed output via linter feedback and test execution." / "modifying agent-generated code about half the time (3.0/5)."
- **CAVEAT**: 3.0/5는 *특정 코호트 자기보고*다 — 관찰값으로만 읽는다.

## §9. ReVeal — *generation-verification 공진화* (인접 1차)

- **제목**: "ReVeal: Multi-turn RL evolving code via self-verification and tool-based evaluation" (ICLR 2026, 2025-06)
- **arXiv ID**: arXiv:2506.11442
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: 코드 생성을 *반복적 generation-verification 턴*으로 구조화하고 self-verification·tool-based evaluation으로
  **코드와 테스트 생성을 공진화**시킨다. turn-level credit assignment(TAPO/TA-PPO)로 *검증 자체를 명시 최적화*한다(기존은
  outcome reward만). 3턴만 학습해도 추론 시 LiveCodeBench에서 self-constructed test·tool feedback로 *20+턴 진화*. → Plan-
  Execute-Verify 루프를 벤치마크된 구체 메커니즘으로 운영화하는 인접 근거.
- **인용**: "a multi-turn reinforcement learning framework that evolves code generation through self-verification and
  tool-based evaluation ... incorporates TAPO for turn-level credit assignment, fostering the co-evolution of code and test
  generation." / "existing methods rely solely on outcome rewards, without explicitly optimizing verification."
- **CAVEAT**: RL 학습 기법이다 — 본 하네스는 *오케스트레이션 패턴*만 차용(코드↔테스트 공진화·검증 명시화)하고 RL은
  쓰지 않는다. 내부 표현 불일치(abstract '20+' vs 본문 'up to 19', TAPO vs TA-PPO)는 그대로 표기. 기법명을 대상
  서베이에 귀속하지 않는다.

## §10. AgentFlow — *harness 민감도 + 사전 검증 게이트* (인접 1차)

- **제목**: "AgentFlow: Synthesizing Multi-Agent Harnesses for Vulnerability Discovery" (2026-04)
- **arXiv ID**: arXiv:2604.20801
- **신뢰도(vote)**: merged 3-0 (high) — *단, 4-phase 루프 하위주장은 반박(아래)*
- **핵심**: harness를 **typed graph DSL의 프로그램**으로 표현(노드=에이전트, 엣지=dataflow/retry)하고, **3단계 검증
  파이프라인**(구문 파싱 → well-formedness → smoke test)이 LLM 추론 *전에* proposer 출력의 **~20%를 기각**한다. **모델을
  고정해도 harness만 바꾸면 성공률이 several-fold 변한다**(TerminalBench-2·동일 Claude Opus에서 20%→80%, 4x 범위) →
  *harness 설계(모델 선택이 아니라)가 1차 레버*. → 본 하네스의 가치 명제(계획·실행·검증 *구조*가 성패를 좌우)를 보강하고,
  "실행 전 결정적 게이트로 먼저 거른다"(Phase 0 계약·Phase 2 센서)는 설계를 보강.
- **인용**: "represents every harness as a program in a typed graph DSL: nodes are agents, edges are dataflow or retry
  links" / "roughly 20% of proposer outputs fail the check and are rejected before consuming any LLM model inference" /
  "When the language model is held fixed, changing only the harness can still change success rates by several-fold ... yet
  most harnesses are written by hand."
- **CAVEAT**: 'several-fold(4x, 20%→80%)'는 *취약점 발견/TerminalBench-2 세팅*값이지 보편 법칙이 아니다. multi-agent
  harness 합성 연구 — 본 하네스는 *단일 사이클*이므로 DSL·합성은 차용하지 않고 "harness가 1차 레버 + 사전 결정적 게이트"
  교훈만 쓴다.

## §11. code-gen 에이전트 taxonomy (인접 1차)

- **제목**: code-generation agent 서베이 (Dong et al., 2025)
- **arXiv ID**: arXiv:2508.00083
- **신뢰도(vote)**: merged 3-0 (high)
- **핵심**: single-agent = (1) planning/reasoning(분해), (2) tool integration & retrieval(RAG), (3) reflection/self-
  improvement(반복 정제·오류 교정). multi-agent = pipeline 분업 · 계층적 planning-execution · self-negotiation 순환 최적화 ·
  self-evolving 구조 갱신 + context management(blackboard·memory·shared KB). → 컴포넌트 어휘·참조 시스템 제공.
- **인용**: §4.1 "Planning and Reasoning" · "Tool Integration and Retrieval Enhancement" · "Reflection and Self-
  Improvement"; multi-agent "Pipeline-Based Labor Division" · "Hierarchical Planning-Execution" · "Self-Negotiation
  Circular Optimization" · "Self-Evolving Structural Updates."
- **CAVEAT**: 폭넓은 taxonomy — 본 하네스는 single-agent reflection/self-improvement(Phase 3 진단·수정) 어휘만 차용.

## §12. verifier reward-hacking · sandbox 격리 (failure-modes 각도, 보강)

- **출처**: arXiv:2604.15149 "Gaming Verifiers: RLVR can Lead to Reward Hacking"(failure-modes 각도, fetch됨, claimCount 4) ·
  arXiv:2603.07084(sandbox 격리, claimCount 4) · https://www.augmentcode.com/guides/agent-execution-sandbox
- **신뢰도(vote)**: **medium(보강)** — failure-modes 각도에서 *fetch·추출*되었으나 상위 25 3-vote 종합에는 들지 않음.
  *보강 근거*로만 쓰고 효과 수치는 인용하지 않는다.
- **핵심**: (a) **reward hacking / verifier gaming** — *extensional correctness만 보는 불완전 verifier*는 task 요구를
  포착하지 못한 채 **direct answer hacking · format exploitation · shortcut solution**을 허용한다. → 본 하네스 Phase 2의
  reward-hacking 가드(센서 약화·테스트 무력화·하드코딩 금지)와 §5(a) "evaluation beyond final task success"를 보강. (b)
  **sandbox = 프로덕션 격리 경계** — filesystem 접근·network egress·host 상호작용을 독립적으로 제한. → Phase 1 권한·
  샌드박스 실행을 보강.
- **인용**: "imperfect verifiers that check only extensional correctness admit ... a reward-hacking failure mode." /
  "via direct answer hacking, format exploitation, and shortcut solutions." / "a sandbox is a production isolation boundary
  that restricts filesystem access, network egress, and host interaction."
- **CAVEAT**: *보강 소스*(3-vote 종합 외). 본 하네스의 reward-hacking 가드의 *1차 근거*는 대상 서베이 §5(a)(b)이고,
  이 절은 그 가드를 구체화하는 보조 인용이다. RLVR 맥락 기법은 차용하지 않는다.

---

## 반박된 주장 (투명성)

> 조사에서 *검토했으나 반박된* 주장이다. 본문 근거로 쓰지 않으며 투명성을 위해 기록한다.

- **(REFUTED 1-2) AgentFlow의 정확한 4-phase 루프** — "AgentFlow가 Propose / Execute & Observe / Score / Diagnose의
  4단계 반복 루프로, LLM이 harness 프로그램을 생성하고 5개 컴포넌트(agent set·communication topology·message schemas·
  tool allocation·coordination protocol) 전반의 실패를 진단한다"는 주장은 **적대 검증에서 반박되었다(1-2)**. AgentFlow
  근거는 *검증된 부분(typed-graph DSL · 3단계 검증 · several-fold harness 민감도, §10)* 으로만 한정하고, 이 4-phase
  루프는 본 하네스 설계에 쓰지 않는다.
- **인접 논문 기법의 대상 서베이 귀속** — ReVeal의 TAPO, AgentFlow의 DSL 같은 *인접 논문의 구체 기법*을 대상
  서베이(2605.18747)의 주장으로 귀속하는 것은 잘못이다. 본 dossier는 각 기법을 *그 출처 논문*에만 귀속한다(§머리말 (2)).
- **벤치마크 결과로서의 3-layer** — 2605.18747의 3-layer 분류를 *실험으로 검증된 우월 구조*로 인용하는 것은 과강하다.
  서베이의 *개념적 조직 프레임*이며 설계 스캐폴드로만 쓴다(§1 CAVEAT).
- **'several-fold' 민감도의 보편화** — AgentFlow의 4x(20%→80%)는 *특정 취약점 발견/TerminalBench-2 세팅*값이다.
  "harness만 바꾸면 항상 몇 배 좋아진다"는 보편 주장으로 쓰지 않는다(§10 CAVEAT).

## 방법론 — deep-research 3-vote 적대 검증

- **팬아웃(5각도)**: primary-paper(대상 서베이) · method-components(명명된 단계·컴포넌트) · academic-adjacent(2025+
  인접·후속·경쟁 연구) · practitioner-implementation(실무 하네스·베스트프랙티스) · failure-modes-guardrails(실패모드·
  안티패턴·가드).
- **수집·추출**: 20개 소스 fetch(URL 중복 6 제거) → 96개 load-bearing 주장 추출.
- **3-vote 적대 검증**: 상위 25개 표적을 독립 3회 교차검증(각 voter는 *반박 시도*, ≥2/3 반박 시 kill) → **24 confirmed /
  1 killed**(AgentFlow 4-phase) → 11개로 종합. confirmed만 본문 근거로 쓰고 killed/반박은 위에 기록.
- **정직성·정확 귀속 가드**: 대상 서베이(개념 프레임) vs 인접 1차(별개 연구) vs 보강 소스(종합 외)를 절마다 구분.
  서베이는 설계 스캐폴드로, 인접 기법은 *그 출처에만* 귀속, 수치는 *특정 세팅·코호트 관찰값*으로 한정. 시점 민감성
  (소스 2025-06~2026-05, 보고 2026-06)을 명기한다.
