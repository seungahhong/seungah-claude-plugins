# Agent Orchestration — 연구 dossier (cited)

> 이 문서는 `agent-orchestration` 하네스 설계의 근거가 된 1차 자료 조사 결과다(deep-research: 도메인 발화를 다각도로
> 팬아웃 → 소스 fetch → 주장 추출 → 3-vote 적대적 교차검증 → confirmed만 채택, 2026-06-25 기준).
> [agent-orchestration-principles.md](./agent-orchestration-principles.md)의 원칙과 상호 참조된다(§N은 이 dossier의 절 번호).
> 빠르게 변하는 분야이므로 각 출처에 신뢰도(vote)와 CAVEAT를 함께 표기하고, 정량 수치는 vote/CAVEAT와 함께만 인용한다.
> "개선 N% 보장" 류의 단정은 쓰지 않는다(모든 수치는 baseline-before-target 비교의 *관찰값*이다).

---

## §1. architecture-task alignment · 오류 증폭 — *멀티 성패는 에이전트 수가 아니다*

- **제목**: "Towards a Science of Scaling Agent Systems"
- **저자**: Yubin Kim et al. (Google Research · MIT · Google DeepMind · Anthropic)
- **arXiv ID / 연도**: arXiv:2512.08296 (Dec 2025; v3 Apr 2026)
- **규모**: 260 controlled experiments (일부 버전 ~180).
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 멀티 에이전트의 이득/손해는 *에이전트 수*가 아니라 **architecture-task alignment**가 결정한다. 단일 에이전트
  baseline 대비 상대 성능 변화가 분해 가능한 작업에서 큰 양(+), 순차 작업에서 큰 음(−)으로 갈린다. 예측 모델이 미지 task의
  87%에서 최적 아키텍처를 선택하며(task 속성=decomposability·tool density 기반), 오류 증폭은 independent 구성이 centralized보다 크다.
- **인용**: "Relative performance change compared to single-agent baseline ranges from +80.8% on decomposable financial reasoning to −70.0% on sequential planning, demonstrating that architecture-task alignment determines collaborative success."
- **오류 증폭(같은 논문, 보조 수치)**: error amplification 17.2x(independent) vs 4.4x(centralized) — 토폴로지가 오류 전파를 좌우.
- **CAVEAT**: +80.8% ~ −70.0%는 *특정 task의 baseline-before-target 관찰값*이지 보편 보장이 아니다. 예측 모델 87%도 해당 실험 분포 내 정확도다.

## §2. capability ceiling — *언제 병렬화하면 안 되는가*

- **출처**: 같은 논문 arXiv:2512.08296 (Kim et al., 2025).
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 단일 에이전트가 *이미 충분히 잘 푸는* 작업(정확도가 경험적 임계 약 45%를 초과)은 에이전트 추가 시 음의 수익이
  난다 — coordination 비용이 한계 개선을 넘어서기 때문이다. β=−0.236, p=0.004; 경계 P*_SA≈0.45. = 언제 병렬화하면 안 되는지의 falsifiable 휴리스틱.
- **인용**: "Tasks where single-agent performance already exceeds 45% accuracy experience negative returns from additional agents, as coordination costs exceed diminishing improvement potential."
- **CAVEAT**: **45%는 경험적 임계지 결정론적 rule이 아니다.** 임계 회귀의 설명력은 절반 미만(R²=0.513 — 절반 이상 미설명)이며,
  decomposability·topology·tool density가 임계를 무효화할 수 있다(예: Finance-Agent는 분해형이라 centralized로 +80.9%). "rule"로
  과강화하지 말 것 — capability-ceiling은 "병렬화를 의심하라"는 신호다.

## §3. curse of coordination — *협업은 사람 팀처럼 인원=생산성이 아니다*

- **제목**: "CooperBench: Why Coding Agents Cannot be Your Teammates Yet"
- **저자**: Khatua, Zhu, …, Diyi Yang
- **arXiv ID / 연도**: arXiv:2601.13295 (submitted Jan 2026)
- **규모**: 600+ collaborative coding tasks, 12 libraries, 4 languages.
- **신뢰도(vote)**: 2-1 (high)
- **핵심**: **curse of coordination** — 페어 협업이 각자 수행 대비 평균 30% 낮은 성공률을 보인다. 팀 크기가 커질수록 성공률이
  단조 감소(2→68.6%, 3→46.5%, 4→30.0%). 사람 팀과 대조적(사람은 보통 인원 추가가 생산성↑) — 에이전트 협업은 그 보장이 없다.
- **인용**: "we observe the curse of coordination: agents achieve on average 30% lower success rates when working together compared to performing both tasks individually, across the full spectrum of task difficulties."
- **CAVEAT**: "across all task difficulties"는 *균일성*을 과장한다 — 실제 gap은 mid-difficulty에서 최대이고 난도별로 비균일하다.
  **방향성(협업이 비용을 수반한다)은 성립하나 크기는 비균일**이다. 30%·단조감소 수치는 이 벤치(코딩 협업)의 관찰값이다.

## §4. 세 coordination 실패 메커니즘 — *증상이 아니라 root-cause*

- **출처**: 같은 논문 arXiv:2601.13295 (Khatua et al., 2026).
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 협업 실패는 무작위가 아니라 세 가지 진단 가능한 root-cause 역량 결핍으로 조직화된다 — (1) communication(모호·
  부정확·타이밍 어긋난 메시지로 채널 정체), (2) commitment(효과적 소통에도 약속 이탈), (3) expectation(타 에이전트의 계획·
  관측·소통 오해). 분포는 expectation 실패 ~42%, communication ~26%.
- **인용**: "Our analysis reveals three key issues: (1) communication channels become jammed with vague, ill-timed, and inaccurate messages; (2) even with effective communication, agents deviate from their commitments; and (3) agents often hold incorrect expectations about others' plans, observations, and communication."
- **CAVEAT**: 42%/26% 분포는 이 벤치의 관찰값이다 — 가드 *우선순위*(expectation 우선) 근거로는 견고하나 다른 도메인에서 비율은 다를 수 있다.

## §5. context pollution — *컨텍스트 공유에 의한 cross-agent 간섭* (medium 신뢰)

- **제목**: "Dynamic Attentional Context Scoping"
- **저자**: Nickson Patel
- **arXiv ID / 연도**: arXiv:2604.07911 (submitted 2026-04-09)
- **신뢰도(vote)**: 2-1 (**medium**)
- **핵심**: N개 동시 에이전트가 오케스트레이터의 컨텍스트 윈도우를 *공유*하면 각 에이전트의 작업 상태·부분 출력·미해결 질문이
  *다른 에이전트의 steering 상호작용을 오염*시켜 결정 품질을 떨어뜨린다(context pollution). → per-agent 컨텍스트 격리가 완화책.
- **인용**: "Multi-agent LLM orchestration systems suffer from context pollution: when N concurrent agents compete for the orchestrator's context window, each agent's task state, partial outputs, and pending questions contaminate the steering interactions of every other agent, degrading decision quality."
- **CAVEAT (medium 신뢰 — 명시)**: 단독저자·비피어리뷰 preprint다. 정량 수치(90-98% vs 21-60%)는 대부분 합성 벤치(200 중 160이
  scripted stub, 실제 LLM은 40 trial)이므로 **수치는 채택하지 않고 질적 실패모드(메커니즘)만 인용**한다. 단, "subagent마다 독립
  컨텍스트 윈도우를 둔다"는 실무 멀티 에이전트 시스템의 격리 관행과 context-rot 문헌이 *질적 메커니즘*을 독립 보강한다(존재 증명·완화 방향으로는 견고).

---

## 반박된 주장 (투명성)

> 아래는 조사 과정에서 *검토했으나 채택하지 않은/반박된* 주장이다. 본문 근거로 쓰지 않으며, 투명성을 위해 기록한다.

- **DACS의 정량 격리 효과 수치(90-98% vs 21-60%)** — arXiv:2604.07911(§5)의 정량 결과는 합성 벤치(200 trial 중 160이
  scripted stub, 실제 LLM은 40 trial) 비중이 커 신뢰가 낮다(vote 2-1 medium). 본 하네스는 이 수치를 *근거로 쓰지 않고*,
  context pollution의 *질적 메커니즘*과 per-agent 격리 *방향*만 채택한다(§5 CAVEAT).
- **"멀티 에이전트가 일반적으로 단일을 능가한다"류의 보편 주장** — §1·§2가 반증한다: 정렬되지 않은 아키텍처는 단일 대비 큰
  음의 수익(−70.0%)을 내고, 단일 baseline이 높으면(capability ceiling) 추가 에이전트가 음의 수익이다. "more agents is
  better"는 본 하네스가 명시적으로 거부하는 anti-pattern이다(principles §7).
- **capability-ceiling 45%를 결정론적 금지 rule로 사용** — §2 원문이 R²=0.513(절반 미만 설명)임을 보고하므로, 45%를
  "초과하면 무조건 단일"로 단정하는 것은 *원전의 과강화*다. decomposability·topology·tool density가 임계를 뒤집을 수 있다(§2 CAVEAT).
  본 하네스는 이를 "병렬화를 의심하라"는 falsifiable 신호로만 쓴다(over-rule 금지, principles §2.2·§7).

## 방법론 — deep-research 3-vote 적대 검증

- **팬아웃**: agent-orchestration 도메인 질문(언제 멀티/단일인가·토폴로지·협업 실패·컨텍스트 격리)을 다각도로 분해해 1차 자료를 병렬 수집했다.
- **추출**: 각 소스에서 load-bearing 주장을 분리하고, 정량 수치는 baseline 비교 형태로 보존했다.
- **3-vote 적대 검증**: 각 주장을 독립적으로 3회 교차검증해 confirmed(채택)/refuted(반박)/medium(조건부)로 분류했다. confirmed만 본문 근거로 쓰고, refuted는 위 "반박된 주장(투명성)"에 기록했다.
- **신뢰도 표기**: 출처별 vote(예: 3-0 high, 2-1 medium)와 CAVEAT를 명시했다. medium(arXiv:2604.07911)은 질적 메커니즘만 채택하고 수치는 미채택임을 §5에 명기했다.
- **정직성 가드**: "개선 N% 보장" 류 단정을 금지하고, 모든 수치를 *특정 벤치의 관찰값*(baseline-before-target)으로 한정했다. 경험적 임계(45%·30%)는 결정론 rule이 아님을 반복 표기했다.
