# Human-Agent Teaming — 연구 dossier (cited)

> 이 문서는 `human-agent-teaming` 하네스 설계의 근거가 된 1차 자료 조사 결과다(deep-research: 도메인 발화를
> 6각도로 팬아웃 → 26개 소스 fetch → 130개 주장 추출 → 25개 표적을 3-vote 적대적 교차검증 → 24 confirmed/1 killed →
> 13개로 종합, 2026-06-25 기준). 출발점은 Anthropic의 **"Building Effective Human-Agent Teams"**(claude.com/blog) 정독이다.
> [human-agent-teaming-principles.md](./human-agent-teaming-principles.md)의 원칙과 상호 참조된다(§N은 이 dossier의 절 번호).
>
> **정직성 가드(머리말).** 가장 직접적이고 실행 가능한 주장은 Anthropic 1차 자료(HAT 블로그·Building Effective Agents·
> safe-agents 프레임워크·Measuring Agent Autonomy·long-running-agents 엔지니어링 글·Claude Code 보안 문서)에서 왔다.
> 이들은 **설계 의도와 작동 예시로는 권위 있으나 벤더 자기서술(자사 제품·관행 기술)이지 독립 효과성 연구가 아니다.**
> 따라서 (1) 벤더의 크기 주장("dramatically improved" 류)은 *증명된 효과*로 인용하지 않고, (2) 모든 수치는 *특정 코호트·
> 시점의 관찰값*으로 한정하며("개선 N% 보장" 금지), (3) 원전이 hedge한 표현("helps"·"some level of trust")을 단정형
> ("requires"·"prerequisite")으로 굳히지 않고 *권장 패턴/휴리스틱*으로 쓴다. 빠르게 변하는 분야이므로 출처마다
> vote와 CAVEAT를 표기한다.

---

## §1. 멀티플레이어 분업 — *프롬프트가 아니라 팀을 설계한다*

- **제목**: "Building Effective Human-Agent Teams"
- **출처**: claude.com/blog/building-effective-human-agent-teams (Anthropic / Claude — **1차 표적 소스**)
- **신뢰도(vote)**: 3-0 (high; 단 *벤더 자기서술*)
- **핵심**: 일은 단일 플레이어에서 **멀티플레이어 게임**으로 옮겨간다 — *사람 팀이 전략을 세우고 Claude가 실행*한다.
  효과적 분업은 사람이 **전략·역할 정의(who does what)·하드 트레이드오프 의사결정·최종 검증**을 소유하고, 에이전트가
  **구별된 전문 역할**(한 에이전트는 데이터 분석, 다른 에이전트는 디자인 표준 집행, 또 다른 에이전트는 리서치 종합)을
  맡으며, 이를 **roster + skill 파일**로 명문화하는 것이다. Anthropic은 네 가지 fundamentals를 제시한다 — (1) **공개적으로
  일하고 넓은 컨텍스트 제공**("적혀 있고 접근 가능하지 않으면, 에이전트에겐 존재하지 않는다"), (2) **역할 정의 + 올바른 도구**,
  (3) **북극성(north star)**(능동성의 근거), (4) **시간을 들여 쌓는 신뢰**.
- **인용**: "Work now looks a lot more like a multiplayer game, with teams of humans setting the strategy, and Claude executing the work." / "one might own the data analysis for a project, another will hold and enforce the design standard, and a third will run research synthesis." / "decisions with hard tradeoffs always had a human in the loop." / "Rubrics or tests for humans and agents to verify key work products." / "Writing skill files to define specific agents' roles."
- **CAVEAT**: 벤더 1차 자료(설계 의도·예시로는 권위 있음). 제3자 보강(mindstudio.ai·sitepoint·agentpatterns.ai)은 같은
  프레임을 재서술하나 독립 효과 측정은 아니다.

## §2. 중심 긴장 — *자율성 ⇄ 통제* (workflow vs agent)

- **출처**: anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents · anthropic.com/research/building-effective-agents (둘 다 Anthropic 1차)
- **신뢰도(vote)**: 3-0 (high; 벤더 자기서술)
- **핵심**: 인간-에이전트 팀의 **중심 긴장**은 *에이전트 자율성*과 *인간 통제*의 균형이다 — 에이전트는 자율적으로 일해야
  하고(그 독립성이 곧 가치다), 그러나 인간은 **목표가 *어떻게* 추구되는지에 대한 통제**를, 특히 *고위험·비가역 결정 이전에*
  유지해야 한다. Anthropic은 **workflow**(LLM·도구가 *미리 정해진 코드 경로*로 조율됨)와 **agent**(LLM이 자기 과정·도구
  사용을 *동적으로 스스로 지휘*함)를 구분한다 — 이 통제-지휘 축이 *구조적으로 얼마나 감독이 필요한지*를 가른다.
- **인용**: "Agents must be able to work autonomously—their independent operation is exactly what makes them valuable. But humans should retain control over how their goals are pursued, particularly before high-stakes decisions are made." (이를 "central tension"으로 명명) / "Workflows are systems where LLMs and tools are orchestrated through predefined code paths" vs "Agents ... where LLMs dynamically direct their own processes and tool usage."
- **CAVEAT**: 검증 중 표면화 — "구조적으로 요구된다(structurally required)"는 Anthropic의 *스펙트럼/권장 관행* 프레이밍보다
  약간 과강하다. 감독은 *권장 설계*이지 모든 작업에 동일 강도로 강제되는 법칙이 아니다.

## §3. 점진적 신뢰 보정 — *적절한 의존(appropriate reliance)이지 신뢰 최대화가 아니다*

- **출처**: claude.com/blog/building-effective-human-agent-teams · anthropic.com/research/building-effective-agents (보강: designative.info 2026-05 trust-calibration)
- **신뢰도(vote)**: 3-0 (high; 벤더 1차 + 실무 블로그 보강)
- **핵심**: 신뢰는 가정하지 않고 **작업 종류별로 점진 보정**한다 — 에이전트는 *입증된 신뢰성에 비례해* 자율을 *획득*하고,
  처음엔 **모든 산출물을 수동 검토**(품질 검증·피드백·검증 체크리스트 설계)하다가 *반복 성공 후 의도적으로* 범위를 넓힌다.
  목표는 **신뢰 최대화가 아니라 적절한 의존(calibrated trust)** — *과신은 위험하고 과소신은 무시*로 이어진다. 에이전트는
  설계된 체크포인트(특히 비가역 행동 이전)에서 인간에게 추가 정보·판단을 요청한다.
- **인용**: "Teams at Anthropic grant agents autonomy in proportion to demonstrated reliability, then expand it deliberately." / "Tracking which kinds of tasks each agent has earned autonomy on and expanding scope per task type after repeated successes." / "At the beginning, humans reviewed every decision made by an agent." / (Building Effective Agents) "you must have some level of trust in its decision-making" + "checkpoints where agents pause for human review ... before they carry out irreversible actions." / (designative) "The goal is not maximizing trust. The goal is appropriate reliance ... A system trusted too much becomes dangerous. A system trusted too little becomes ignored."
- **CAVEAT**: "some level of trust"(원전 hedge)를 "prerequisite"로 굳히지 않는다 — *경험적 권장*이다. 자율 확대의 단위
  (작업 종류별)는 견고하나, 구체적 확대 속도는 팀·도메인마다 다르다. CHI 2025 연구(arXiv §reliance)는 **reliance
  intervention이 과의존은 줄이나 적절한 의존을 *개선하지 못하고* 일부 맥락에선 오답 후 자신감을 *높인다***고 보고한다 —
  신뢰 보정 장치가 역효과를 낼 수 있음을 함께 적는다(§10과 연결).

## §4. 감독 = 모니터링 + 개입 — *모든 행동 승인이 아니다*

- **출처**: anthropic.com/news/measuring-agent-autonomy (Anthropic 1차) · anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents · code.claude.com/docs/en/security
- **신뢰도(vote)**: 3-0 (high; 벤더 1차, 3개 독립 검증 통과)
- **핵심**: 효과적 감독은 **모든 개별 행동 승인을 요구하지 않는다** — 필요할 때 *개입할 위치*에 있는 것이다(행동별 승인 →
  **모니터링 기반 감독**으로의 이동). 모든 행동 승인을 강제하는 처방은 *승인 피로·러버스탬프*를 낳아 *마찰만 늘고 안전
  이득은 없을 수 있다*. 모니터링 기반 감독을 가능케 하는 1급 요소: **투명성**(실시간 to-do 체크리스트로 계획 노출 — 너무
  적으면 감독 불능, 너무 많으면 압도, 그 사이를 잡는다), **개입 가능성/스티어링**(언제든 중단·재지정·작업계획 조정),
  **단계적·가역 권한**(기본 읽기 전용=무승인 → 쓰기/수정 전 인간 승인 → 신뢰된 루틴엔 선택적 영속 권한).
- **인용**: "effective oversight doesn't require approving every action but being in a position to intervene when it matters." / "Oversight requirements that prescribe specific interaction patterns, such as requiring humans to approve every action, will create friction without necessarily producing safety benefits." / "Claude shows its planned actions through a real-time to-do checklist, and users can jump in at any time to ask about or adjust Claude's workplan." / "In Claude Code, humans can stop Claude whenever they want and redirect its approach." / "It has read-only permissions by default ... but must ask for human approval before taking any actions that modify code or systems." / "Users can grant persistent permissions for routine tasks they trust."
- **수치(관찰값, CAVEAT 동반)**: 신규 사용자(<50 세션)는 full auto-approve를 ~20%에서 쓰다가 750 세션에선 40%+로 증가하나,
  **interrupt rate는 함께 상승(약 5%→9%)** — 자율 위임이 *방치*가 아니라 *능동 모니터링*임을 시사. ⚠️ 이 수치는 *특정
  Claude Code 코호트·도구 시점*의 관찰값으로 제품 진화에 따라 변한다(§머리말 정직성 가드). 또한 auto-approve 20%→40%는
  원문에 직접 인용문이 있으나 interrupt 5%→9%는 원문의 *수치·서술*에서 온 것으로 직접 인용 문장으로는 확인되지 않는다 —
  방향(경험↑ → interrupt↑·능동 모니터링)은 견고하나 정확 수치는 이 한정 아래 읽는다.
- **CAVEAT(Anthropic 자가)**: 이 이동은 *신뢰할 만한 가시성 + 단순한 개입 장치*가 전제다. 또 **"에이전트 산출 검증이
  생산과 같은 전문성을 요구하는 분야에선 더 느리거나 다른 형태"**일 수 있다(→ §5 대칭 전문성 문제). openQuestion: 모니터링
  전제(사람이 실제로 본다)가 깨지는 러버스탬프/승인 피로를 *탐지·상쇄*하는 장치(interrupt-rate 텔레메트리·주기적 강제
  리뷰·자동화 편향 넛지)는 미해결 — 본 하네스는 이를 가드로 *명시*하되 만능으로 약속하지 않는다.

## §5. 인간 검증 — *자동 검증이 가능해도 마지막 검증 층은 사람* (Doer-Verifier)

- **출처**: claude.com/blog/building-effective-human-agent-teams · anthropic.com/research/building-effective-agents · anthropic.com/engineering/effective-harnesses-for-long-running-agents
- **신뢰도(vote)**: 3-0 (high; 벤더 1차 + 독립 보강)
- **핵심**: **인간 검증은 자동 검증이 가능할 때조차 요구되는 마지막 validation 층**이며, *구체적 산출물*로 운영한다 — 코드엔
  테스트, 그 외 작업엔 *루브릭/스타일 가이드*, 그리고 **Doer-Verifier 패턴**(한 에이전트는 작업을, *별도의* 에이전트는
  그 작업 검사를 맡는다 — 이상적으로 **fresh-context + Write/Edit 도구 없는** 평가자). 자동 테스트는 *기능*을 검증하나,
  인간 리뷰는 *더 넓은 시스템 요구·의도와의 정합*을 위해 필수다.
- **인용**: "Code solutions are verifiable through automated tests" 그러나 "human review remains crucial for ensuring solutions align with broader system requirements." / "Code has tests, of course, but most other work can be verified as well ... technical docs can have rubrics and style guides applied to them." / "give one agent the job of doing the task and another agent the job of checking the first agent's work. This is often called the Doer-Verifier agent harness." / (engineering) "a fresh-context evaluator ... a separate agent with no Write/Edit tools that grades the work."
- **독립 보강**: CodeRabbit 470-PR 분석(AI 공동작성 PR에서 약 1.7배 많은 이슈) · Veracode 2025(45% OWASP 취약점) ·
  "AI-reviewing-AI is a closed loop" 비판(arXiv:2603.15911) — *AI가 AI를 검증하는 폐루프*의 한계 → 인간 층의 필요성을 보강.
- **CAVEAT(대칭 전문성)**: 검증 비용이 생산 비용과 같아지는 경우(전문가만 검증 가능) 모니터링 이동이 막힌다. openQuestion:
  *검증 가능한 하위 주장으로 분해 · ground-truth 프로브 · 독립 컨텍스트 Doer-Verifier* 같은 패턴이 후보다. **검증 스캐폴딩은
  *필요조건이지 충분조건이 아니다*** — 에이전트 종단 성공률이 100% 미만(WebArena ~35.8%)이고 도구에 사각(예: Puppeteer는
  브라우저 네이티브 alert 모달을 못 봄)이 있어, 검증을 두어도 통과를 단정하지 않는다.

## §6. 에이전트의 특징적 실패모드 — *구조적 가드로 막는다*

- **출처**: anthropic.com/engineering/effective-harnesses-for-long-running-agents (Anthropic 1차, Nov 2025)
- **신뢰도(vote)**: 3-0 (high; 단일 1차, 2개 독립 검증 + 실무 보강)
- **핵심**: 에이전트엔 구조적으로 막아야 할 특징적 실패모드가 있다 — (a) **한 번에 너무 많이 하고 조기에 승리를 선언**(one-shot
  시도) → *한 번에 하나의 경계 있는 기능/작업으로 제한*("critical"하다고 표현). (b) **제대로 테스트하지 않고 완료로 표시**
  → *검증을 명시적으로 스캐폴딩*(브라우저 자동화 도구 제공, "사람 사용자처럼 테스트하라" 지시, "신중히 테스트한 뒤에만
  passing으로 표시하라" 요구). 이는 위임의 *범위 제약·검증 스캐폴딩* 패턴 자체다.
- **인용**: "the agent tended to try to do too much at once—essentially to attempt to one-shot the app." / "a later agent instance would look around, see that progress had been made, and declare the job done." / "asked to work on only one feature at a time. This incremental approach turned out to be critical." / "Claude's tendency to mark a feature as complete without proper testing." / "do all testing as a human user would."
- **CAVEAT**: 벤더의 "dramatically improved" 프레이밍은 *증명된 효과*로 인용하지 않는다(§머리말). WebArena ~35.8% 실세계
  웹작업 성공률이 신뢰 상한을 제약한다.

## §7. 세션 간 핸드오프 — *기억 없는 교대 근무자를 위한 연속성 산출물*

- **출처**: anthropic.com/engineering/effective-harnesses-for-long-running-agents (Anthropic 1차)
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 세션 간(에이전트↔에이전트, 확장하면 인간↔에이전트) 효과적 핸드오프는 **fresh-context 작업자가 이전 작업 상태를
  빨리 이해**하도록 *구조화된 환경 연속성 산출물*을 요구한다 — **진행 로그**(claude-progress.txt), **구조화된 기능/요구
  목록**(passes:true/false JSON), **서술적 git 커밋 이력**. 동기 비유: *교대 근무 엔지니어 — 각자 이전 교대의 기억 없이 출근*.
- **인용**: "finding a way for agents to quickly understand the state of work when starting with a fresh context window, which is accomplished with the claude-progress.txt file alongside the git history." / "Imagine a software project staffed by engineers working in shifts, where each new engineer arrives with no memory of what happened on the previous shift."
- **독립 보강**: Addy Osmani(progress.txt + feature-list.json + commit + 동일 교대 비유) · Augment Code 핸드오프 가이드
  ("현재 상태·알려진 이슈·다음 행동") · arXiv:2508.00031(Git Context Controller).
- **CAVEAT**: 원전의 비유는 *인간↔인간 교대*다 — 인간↔에이전트 핸드오프로의 적용은 합리적 일반화지 원전의 직접 주장이 아니다.

## §8. 위임 메커니즘 — *human/agent/co-delegation + 조건부 위임* (학술)

- **제목**: "Adaptive Human-Agent Teaming: A Review of Empirical Studies from the Process Dynamics Perspective"
- **저자/연도**: Wang et al., Apr 2025 (133개 경험 연구 리뷰)
- **arXiv ID**: arXiv:2504.10918
- **신뢰도(vote)**: 3-0 (high; 견고한 체계적 리뷰)
- **핵심**: HAT 분업은 세 위임 메커니즘으로 작동한다 — **human delegation, agent delegation, co-delegation** + 위임 실패 시
  **deferred/backup** 행동. 효과적 *agent delegation*은 **AI의 오류 경계(parsimony·stochasticity)를 드러내** 사용자가
  *정확한 mental model*을 형성하게 하는 데 달려 있고, **conditional delegation**(인간·에이전트가 *trustworthy region*을
  협상하고 그 너머를 위임)으로 *역량 경계*와 *그에 대한 인간 인식*을 함께 세운다.
- **인용**: "We categorize these mechanisms ... into human delegation, agent delegation, co-delegation, and deferred mechanisms when delegation is unsuccessful." / "revealing AI error boundaries—particularly its parsimony and stochasticity—helps users form accurate mental models, improving team performance." / "Lai et al. propose conditional delegation, where humans and agents define trustworthy regions, beyond which tasks are delegated."
- **CAVEAT**: "requires"는 원전의 "helps/propose"보다 강하다 — *권장 메커니즘*으로 쓴다. non-peer-reviewed track 원고.

## §9. 흐릿한 역할 경계 = 실패 원천 — *제한된(restrained) 에이전트 + 명확한 역할*

- **출처**: arXiv:2504.10918 (Wang et al., 2025)
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 인간-에이전트 간 **흐릿한 역할/책임 경계**는 구체적 실패를 낳는다 — **역할 혼동, 의사결정 지연·오류, 신뢰 하락,
  인간 무임승차(free-riding), 과도하게 낙관적인 과신**. 따라서 HAT 설계는 *명확한 역할 정의를 가진 제한된(restrained)
  에이전트*로 **인간 주도성(initiative)을 보존**하고 *능동적 인간 참여*를 장려해야 한다.
- **인용**: "Given current agent limitations, a restrained design with clear role definitions is crucial. Blurred responsibility divisions can also lead to human free-riding." / "if an intelligent agent incorrectly takes over a human's role, it may lead to role confusion, decision delays and errors, and decreased trust." / "encourage active participation, emphasizing human initiative."
- **CAVEAT**: 적대 탐색(자율↑이 항상 낫다)은 반증 대신 보강을 돌려줬다(arXiv:2506.09420 · PMC "Human control of AI systems:
  from supervision to teaming"). 실패모드는 같은 1차 소스의 두 절에서 묶였다.

## §10. 신뢰 ≠ 의존 · SMM은 영속 협상 — *일회성 설정이 아니다*

- **출처**: arXiv:2504.10918 (Wang et al., 2025); 보강: arXiv:2503.19607(After-Action Review/Explanation)
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: **신뢰 보정만으론 적절한 의존에 불충분**하다 — *의존(reliance)은 신뢰(trust)와 행동적으로 구별*된다(신뢰 없이
  의존 가능: AI 전유·권위 복종). 그래서 감독 장치는 신뢰 *태도*만이 아니라 mental model의 세 요소 — **reasoning,
  commitments, beliefs** — 를 다뤄야 한다. 또 **Shared Mental Model(SMM)은 미리 정의되지 않고**, 명시적·암묵적 신호의
  지속 교환(divergence ↔ convergence)으로 *영속적으로 재협상*된다 → 하네스는 *일회성 컨텍스트 설정*이 아니라 **지속적
  재정렬(re-alignment) 루프**를 지원해야 한다. 군사 디브리프인 **After-Action Review**를 인간-AI용 *After-Action
  Explanation*으로 적응하면 사후 SMM 구축에 쓸 수 있다(arXiv:2503.19607).
- **인용**: "trust reflects cognitive beliefs about agents, whereas reliance manifests behaviorally." / "participants may also rely on AI without trusting it, such as by appropriating AI resiliently or obeying authority." / "trust calibration is just one factor in achieving appropriate reliance." / "SMM is not pre-defined but perpetually negotiated."
- **CAVEAT**: 명령형 "must"는 원전의 "not the only path"보다 강하다 — *권장*이다. 메커니즘은 견고하나 *재정렬 주기/산출물*의
  구체값은 원전이 주지 않는다(openQuestion: 최소 재정렬 루프 — 주기적 plan-restatement·divergence 감지·AAR).

## §11. 도구 → 팀원 패러다임 + CSCW 설계 질문 (medium 신뢰)

- **제목**: "From Human-Human Collaboration to Human-Agent Collaboration ..."
- **저자/연도**: Yao, Chen, A.Y. Wang, T. Wu, T. Li, D. Wang — CHI EA '26 workshop, Feb 2026
- **arXiv ID**: arXiv:2602.05987
- **신뢰도(vote)**: 3-0 (확인되었으나 **medium** — 비피어리뷰 워크숍 *제안서*; 세 속성은 기존 CSCW 개념의 재서술)
- **핵심**: 효과적 HAT는 **도구 패러다임**(지시를 기다리는 수동 도구)에서 **팀원 패러다임**으로 이동한다 — 세 속성:
  **mutual awareness**(누가 무엇을 하는지 공유 이해), **adaptivity**(상대의 변하는 목표에 동적 적응), **shared
  accountability**(결과에 대한 공동 책임). LLM 에이전트를 *"원격 인간 협력자"*로 설계·연구하라 — *분산 팀워크에 대한 수십
  년의 CSCW 연구*(신뢰·awareness·common ground)에 접지한다. 하네스가 답해야 할 **CSCW 설계 질문**: (1) *체험 경험이
  없는* 에이전트와 어떻게 **common ground**를 세우나, (2) 에이전트의 *초점·의도*에 대한 **workspace awareness** 표상은
  무엇인가, (3) 에이전트가 언제 **articulation work**(작업 조율)를 맡고 어떻게 감독에 *노출*하나. (원전은 lean 통신 속
  협상을 위한 *media richness*를 네 번째로 더 든다.)
- **인용**: "moving beyond the tool paradigm, where systems act as passive instruments awaiting human instructions, to interactions that resemble genuine teammate." / "mutual awareness ... adaptivity ... shared accountability." / "to design and study LLM agents as remote human collaborators ... grounds human-agent collaboration in decades of CSCW research." / "How can humans establish common ground with agents that lack lived experience? What representations support workspace awareness of an agent's focus? When should agents take on articulation work, and how should they expose it for oversight?"
- **CAVEAT(medium — 명시)**: 비피어리뷰 워크숍 *제안서*다 — "framework"는 *연구 의제/생성 휴리스틱*이지 검증된 경험 결과가
  아니다. 세 팀원 속성은 *기존 CSCW 개념의 재서술*(이 논문의 신규 결과 아님). 본 하네스는 이를 *설계 렌즈*로만 채택하고
  효과 수치는 인용하지 않는다. 보강: arXiv:2508.14825("From Passive Tool to Socio-cognitive Teammate") · CollabSim(2606.06399).

## §12. human-in-the-loop vs human-on-the-loop — *분업 모델은 신뢰성·중요도에 따라*

- **출처**: arXiv:2510.02557(Manager Agent / human-on-the-loop) · arXiv:2602.16844(HITL vs HOTL 형식화)
- **신뢰도(vote)**: confirmed (보조 — fetch 단계 추출, 종합에서 보조 위치)
- **핵심**: **human-in-the-loop**(인간이 에이전트 보조 하에 *모든 최종 결정*을 내림)과 **human-on-the-loop**(에이전트가
  자율 작동하고 인간이 *결과를 감독*; 인간은 고수준 목표·감독을 유지하고 Manager Agent가 운영 관리를 처리)을 구분하며,
  *적절한 모델은 에이전트 신뢰성과 작업 중요도에 따라* 달라진다. = §2 자율성-통제 축의 구체적 운영 모드.
- **인용**: "Human-in-the-loop: Humans make all final decisions with agent assistance / Human-on-the-loop: agents operate autonomously with human oversight of outcomes." / "the human stakeholder retains control over high-level objectives and oversight."
- **CAVEAT**: 보조 근거 — 본 하네스는 HITL/HOTL을 *작업 중요도×신뢰성에 따라 고르는 운영 모드*로만 쓴다.

---

## 반박된 주장 (투명성)

> 조사에서 *검토했으나 채택하지 않은/반박된* 주장이다. 본문 근거로 쓰지 않으며, 투명성을 위해 기록한다.

- **(REFUTED 1-2) 에이전트 자기제한을 *1차 감독 장치*로 삼기** — "가장 복잡한 작업에서 Claude가 인간이 개입하는 것보다
  2배 이상 자주 스스로 멈춰 질문하므로 *자기제한*이 주 감독 메커니즘"이라는 주장은 **반박되었다(1-2)**. 본 하네스는
  **에이전트의 자기멈춤을 안전장치로 설계하지 않는다** — 감독은 *인간의 모니터링+개입*과 *구조적 가드*에 둔다(§4·§6).
- **"신뢰/자율은 많을수록 좋다"** — §3(적절한 의존: 과신은 위험)·§9(역할 침범 → 과신·무임승차)가 반증한다. 목표는
  *신뢰 최대화*가 아니라 *적절한 의존*이다. "more autonomy is better"는 본 하네스가 명시적으로 거부하는 anti-pattern이다.
- **"모든 행동 승인이 안전을 만든다"** — §4가 반증한다: 행동별 승인 강제는 *승인 피로·러버스탬프*로 *마찰만 늘고 안전
  이득은 없을 수 있다*. 감독은 *모니터링+개입*이지 *전수 승인*이 아니다.
- **벤더 크기 주장("dramatically improved")을 증명된 효과로 인용** — §5·§6 원전의 자기서술 프레이밍이다. 본 하네스는
  *메커니즘·패턴*만 채택하고 *효과 크기*는 인용하지 않는다(§머리말 정직성 가드).
- **"AI는 항상 개발 속도를 높인다"** — 반례: **METR RCT**(metr.org, 2025-07; 경험 많은 OSS 개발자 16명·실제 이슈 246건)는
  익숙한 저장소에서 **AI 도구가 오히려 ~19% *느리게* 만들었다**고 보고한다(개발자 본인 추정과 반대 방향). 본 하네스는
  "AI 팀 도입=속도↑"를 보편 약속으로 쓰지 않고, *적절히 설계된 분업·검증*이 조건임을 강조한다(정직성).

## 방법론 — deep-research 3-vote 적대 검증

- **팬아웃(6각도)**: Anthropic 1차 가이드 · 학술(HAT·SMM) · 신뢰 보정/적절한 의존/감독 · 개입/스티어링/위임·핸드오프 ·
  실무 HITL 멀티에이전트 패턴 · *반대(contrarian) 실패모드·한계*.
- **수집·추출**: 26개 소스 fetch → 130개 load-bearing 주장 추출(정량은 baseline 비교/관찰값 형태로 보존).
- **3-vote 적대 검증**: 상위 25개 표적을 독립 3회 교차검증 → **24 confirmed / 1 killed**(자기제한 주장) → 종합 13개.
  confirmed만 본문 근거로 쓰고, killed/반박은 위 "반박된 주장(투명성)"에 기록.
- **신뢰도·정직성 가드**: 출처별 vote(3-0 high 등)와 CAVEAT 명시. **벤더 1차 vs 학술**을 구분(벤더=설계 의도·예시,
  독립 효과 연구 아님). 원전의 hedge를 단정으로 굳히지 않고(helps→requires 경계 명시), "개선 N% 보장"을 금지하며,
  모든 수치를 *특정 코호트·시점의 관찰값*으로 한정했다. 시점 민감성(소스 2024-12~2026-02, 보고 2026-06)을 명기한다.
