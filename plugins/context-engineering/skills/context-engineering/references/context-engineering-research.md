# Context Engineering — 연구 dossier (cited)

> 이 문서는 `context-engineering` 하네스 설계의 근거가 된 1차 자료 조사 결과다(deep-research: 다각도 팬아웃 → 소스 fetch
> → 주장 추출 → 3-vote 적대적 교차검증 → confirmed claims 복구, 2026-06-25 기준). [context-engineering-principles.md](./context-engineering-principles.md)의 원칙과 상호 참조된다.
> 빠르게 변하는 분야이므로 각 출처에 신뢰도(vote)와 caveat을 함께 표기한다. 정량 수치는 vote/CAVEAT와 함께만 인용하고
> "개선 N% 보장"으로 일반화하지 않는다. **반박(refuted)된 주장은 맨 끝 '반박된 주장(투명성)' 절에만 기록하고 본문 근거로 쓰지 않는다.**

---

## 출처 1 — Context Engineering의 정의 (taxonomy의 토대)

- **제목**: A Survey of Context Engineering for Large Language Models
- **저자**: Lingrui Mei et al.
- **arXiv ID / 연도**: arXiv:2507.13334 (submitted 2025-07-17, v2 2025-07-21)
- **URL**: https://arxiv.org/abs/2507.13334
- **규모**: 1,400+편 분석 서베이.
- **핵심**: Context Engineering = 단순 프롬프트 설계를 넘어, LLM에 전달하는 *정보 페이로드*의 체계적 최적화.
- **인용**: "This survey introduces Context Engineering, a formal discipline that transcends simple prompt design to
  encompass the systematic optimization of information payloads for LLMs."
- **신뢰도(vote)**: 3-0 (high).
- **CAVEAT**: "formal discipline" 프레이밍은 저자들의 것이며, 일부 실무자는 prompt engineering의 리브랜딩이라 비판한다(HN).
  보편적 합의로 단정하지 말 것. 논문 발행은 2025-07(8월 이전)이나 "2025+ 학술 근거" 요구를 충족하므로 적격이다.
- **하네스 매핑**: SKILL.md 핵심 프레이밍·내재화 원칙("체계적 최적화 ≠ 더 채우기"), CLAUDE.md Conventions, principles §1.

## 출처 2 — 도메인 무관 분류 체계 (4단계 구조의 근거)

- **제목 / arXiv ID**: 같은 arXiv:2507.13334.
- **핵심**: 3대 foundational component(retrieval and generation · processing · management) + 아키텍처 구현(RAG ·
  memory systems and tool-integrated reasoning · multi-agent systems). 이 분류가 본 하네스 Phase 구조의 근거.
- **인용**: "Foundational components: Context retrieval and generation; Context processing; Context management ...
  Architectural implementations: Retrieval-augmented generation (RAG); Memory systems and tool-integrated reasoning;
  Multi-agent systems"
- **신뢰도(vote)**: 3-0 (high).
- **하네스 매핑**: 세 component → Phase 1(Retrieve/Generate)·Phase 2(Process)·Phase 3(Manage). 그 앞단에 Phase 0(Scope)
  게이트를 얹음. RAG → Phase 1, multi-agent → Phase 3 격리. principles §2.

## 출처 3 — ACE: 진화하는 playbook (큐레이션 설계의 근거)

- **제목**: Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models
- **저자 / 소속**: Zhang et al. (Stanford / SambaNova / UC Berkeley)
- **arXiv ID / 연도**: arXiv:2510.04618 (submitted 2025-10-06; accepted ICLR 2026)
- **URL**: https://arxiv.org/abs/2510.04618
- **핵심**: ACE = 컨텍스트를 *진화하는 playbook*으로 취급. 3역할 모듈 구조(generation / reflection / curation). 고정
  system prompt와 구별. 보고된 이득: agent benchmark +10.6%, finance +8.6%.
- **인용**: "ACE treats contexts as evolving playbooks that accumulate, refine, and organize strategies through a
  modular process of generation, reflection, and curation."
- **신뢰도(vote)**: 3-0 (high).
- **CAVEAT**: +10.6%/+8.6%는 ACE *전체 시스템*·특정 벤치의 수치다. 본 하네스는 ACE의 *설계 원리*(진화하는 playbook·
  generation/reflection/curation·구조적 증분)를 채택하며 같은 수치를 *보장*하지 않는다. "개선 N% 보장"으로 일반화 금지.
- **하네스 매핑**: context-curator playbook 큐레이션, SKILL.md "playbook 큐레이션" 원칙, principles §5.

## 출처 4 — ACE: 두 실패모드(brevity bias·context collapse)와 구조적 증분 대응

- **제목 / arXiv ID**: 같은 arXiv:2510.04618.
- **핵심**: 기존 접근은 brevity bias(간결 요약 위해 도메인 통찰 누락)와 context collapse(반복 재작성이 디테일 침식)를 겪는다.
  대응은 "detailed knowledge를 보존하는 구조적·증분적 업데이트"다.
- **인용**: "Prior approaches improve usability but often suffer from brevity bias, which drops domain insights for
  concise summaries, and from context collapse, where iterative rewriting erodes details over time."
- **신뢰도(vote)**: 3-0 (high).
- **하네스 매핑**: context-processor·context-curator "구조적 증분(전면 재작성 금지)", SKILL.md 내재화 원칙, principles §4(1·2).

## 출처 5 — DACS: context pollution (멀티 에이전트 실패모드)

- **제목**: Dynamic Attentional Context Scoping
- **저자**: Nickson Patel (단독저자)
- **arXiv ID / 연도**: arXiv:2604.07911 (submitted 2026-04-09)
- **URL**: https://arxiv.org/abs/2604.07911
- **핵심**: context pollution = N개 동시 에이전트가 오케스트레이터 컨텍스트 윈도우를 공유할 때 상호 오염해 의사결정 품질 저하.
- **인용**: "Multi-agent LLM orchestration systems suffer from context pollution: when N concurrent agents compete for
  the orchestrator's context window, each agent's task state, partial outputs, and pending questions contaminate the
  steering interactions of every other agent, degrading decision quality."
- **신뢰도(vote)**: 2-1 (**medium**).
- **CAVEAT(중요)**: 단독저자·비피어리뷰 preprint. 정량수치(90-98% vs 21-60%)는 대부분 합성 벤치(200 중 160이 scripted
  stub, 실제 LLM은 40 trial)에서 나온 것이므로 **수치는 인용하지 않고** *질적 실패모드(context pollution)*만 인용한다.
  단, 이 질적 메커니즘은 멀티 에이전트 시스템에서 subagent별 독립 컨텍스트 윈도우를 두는 업계 실천과 context-rot 문헌이
  독립적으로 보강하므로, *질적 설계 패턴*으로 채택한다.
- **하네스 매핑**: principles §4(4)·§6, context-curator 격리 동기. SKILL.md "멀티 에이전트 격리" 원칙(CAVEAT 명시).

## 출처 6 — DACS: REGISTRY/FOCUS 격리 패턴 (서술적)

- **제목 / arXiv ID**: 같은 arXiv:2604.07911.
- **핵심**: DACS = agent-triggered·asymmetric·deterministic per-agent 컨텍스트 격리. REGISTRY(에이전트당 ≤200토큰 상태
  요약) + FOCUS(a_i)(한 에이전트 풀 컨텍스트, 나머지는 registry로 압축). 재사용 가능한 벤더 비종속 오케스트레이션 패턴.
- **인용**: "In REGISTRY mode it holds only lightweight per-agent status summaries (<= 200 tokens each), remaining
  responsive to all agents and the user. When an agent emits a STEERING REQUEST, the orchestrator enters FOCUS(a_i)
  mode, injecting the full context of agent a_i while compressing all other agents to their registry entries."
- **신뢰도(vote)**: 3-0 (high) — *패턴의 서술* 자체는 명확하나, 효과의 정량 주장은 출처 5의 CAVEAT를 따른다.
- **CAVEAT**: 패턴의 *형태*(REGISTRY/FOCUS)는 vote 3-0으로 명확히 서술되지만, 그 *정량 효과*는 출처 5의 합성 벤치 한계를
  공유하므로 수치 없이 *질적 격리 패턴*으로만 적용한다(멀티 에이전트일 때만 활성화하는 선택 레인).
- **하네스 매핑**: context-curator "멀티 에이전트 격리(REGISTRY/FOCUS)", SKILL.md Phase 3 격리 설계 프롬프트, principles §6.

---

## 반박된 주장 (투명성)

deep-research 3-vote 적대 검증에서 *반박(refuted)*되거나 본 하네스가 *채택하지 않은* 주장을 투명성 차원에서 기록한다.
이들은 **본문 근거로 인용하지 않는다.**

- **DACS 정량수치 (90-98% vs 21-60% 등)** — arXiv:2604.07911의 핵심 정량 주장. 대부분 합성 벤치(200 trial 중 160이
  scripted stub, 실제 LLM은 40 trial)에서 나와 *실세계 일반화가 입증되지 않았다*. vote 2-1(medium)로 *질적 실패모드/
  패턴 형태*만 채택하고 **수치는 본문에 인용하지 않는다.**
- **"Context Engineering = formal discipline(정식 학문)으로 보편 합의됨"** — arXiv:2507.13334의 프레이밍을 *합의된 사실*로
  과장하는 해석. 일부 실무자는 prompt engineering 리브랜딩이라 비판하므로(HN), 본 하네스는 이를 *실무 설계 규율*로만 채택하고
  "분야 합의"로 단정하지 않는다.
- **"ACE/playbook 큐레이션이 임의 작업에서 +10.6%/+8.6% 개선을 보장"** — arXiv:2510.04618의 수치는 ACE 전체 시스템·특정
  벤치의 결과다. 임의 컨텍스트 작업으로의 일반화·"보장"은 채택하지 않는다(설계 원리만 채택). "개선 N% 보장" 금지 규약에 따른다.

## 방법론 메모 — deep-research 3-vote 적대 검증

- **팬아웃**: context engineering 정의·taxonomy·playbook 큐레이션·멀티 에이전트 격리 등 다각도 검색.
- **검증**: 각 추출 주장에 대해 독립 3-vote 적대 교차검증(confirmed / killed / medium 분류).
- **신뢰도 표기**: high(3-0), medium(2-1)을 출처별로 명시하고, medium·정량수치에는 CAVEAT를 붙인다.
- **수치 정책**: baseline-before-target 원칙. 검증된 수치만 vote/CAVEAT와 함께 인용하고, "개선 N% 보장"은 금지한다.
- **독립성**: 각 논문은 primary로 직접 인용하며, 다른 마켓플레이스 플러그인에 의존하지 않는다.
- **시의성**: 2025+ 학술 근거(arXiv:2507.13334·2510.04618·2604.07911)로 뒷받침한다. 이 주제는 addyo.substack 발(發) deep-research
  과정에서 도출됐으나, 본 하네스의 *근거*는 위 1차 논문이며 특정 Osmani 글을 출처로 인용하지 않는다(혼입 방지). 빠르게 변하는 분야이므로 신뢰도·caveat을 상시 병기한다.
