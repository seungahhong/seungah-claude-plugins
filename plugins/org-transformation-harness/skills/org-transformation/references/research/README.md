# 근거 dossier — 조직 전환(목적조직·AI native) (2023–2026 1차 조사)

이 하네스의 주장은 `/deep-research`(6각도 팬아웃 → 소스 페치 → 3표 적대 검증)로 2023~2026 문헌과 대조해 **근거 등급**을 붙였다. 이 문서는 그 결과를 정직하게 요약한다. 핵심 메시지: **조직 전환에 은탄환은 없다.** 특히 AI 도입은 1차 데이터상 개인 체감과 시스템 성과가 갈린다.

## 이 도구가 근거를 쓰는 규칙 (정직성)

1. **수치는 출처·등급과 함께 관찰값으로만 인용한다.** "이걸 하면 N% 좋아진다"고 약속하지 않는다.
2. **STRONG이라도 조건부다.** DORA 데이터는 "AI 도입이 delivery 성과를 자동으로 올리지 않는다"는 걸 보여준다 — 승리 조건을 함께 말한다.
3. **report-only(folklore)를 실증으로 포장하지 않는다.** Kotter short-term wins·additive-first·RICE/WSJF는 널리 쓰이는 실무 프레임이지 측정된 인과 우월성이 아니다.
4. **REFUTED/과장은 교정본으로만 인용한다.** "AI 파일럿 95% 실패"·"AI = 자동 생산성" 같은 유행 수치는 반박·맥락과 함께.

## SOURCE-TIER

- **PRIMARY** — 1차 연구·대규모 서베이(DORA 2024/2025, 학술지 논문). 최우선.
- **SECONDARY** — 1차를 분석한 신뢰 매체(RedMonk 등).
- **PRACTITIONER/BLOG** — 실무자 프레임·책·블로그(Cagan, Team Topologies, SAFe). 유용하나 실증 아님.

---

## 각도 1 — 처방 전에 현행부터 진단하는 것 (등급: MEDIUM, 이론·컨센서스 / 측정된 인과 아님)

**주장**: 목표 구조/방법론을 처방하기 전에 현행(current operating model)을 먼저 진단하면 전환이 잘 된다.

- **관찰**: 조직 진단은 "적절한 개입을 고르고 변화 준비도(readiness-to-change)를 높이는 데 결정적 역할"을 한다고 변화관리 문헌이 말한다. *"Organizational diagnosis plays a critical role ... in terms of both choosing appropriate interventions and contributing to readiness-to-change."* (PRIMARY, Change Management 학술지, tandfonline 10.1080/14697017.2011.630506 / ResearchGate 239796277)
- **정직성(중요)**: 같은 논문이 스스로 밝힌다 — 진단 부실이 변화 실패율에 기여한다는 건 **"likely"한 이론적 주장이지 측정된 효과가 아니다**(*"likely to be significant factors"*). 게다가 "진단이 통합적이라고들 하지만 진단 과정 자체는 학술적 관심을 거의 못 받았다"고 인정한다. → **현행 우선은 강한 컨센서스이자 이론적 근거이나, "진단하면 성공률이 X% 오른다"는 측정값은 없다.** 실무 도구로서 채택하되 실증으로 포장하지 않는다.
- **실무 보강**: Prosci는 변화 착수 전 readiness assessment를 권고(PRACTITIONER, prosci.com). Cagan 『Transformed』도 "먼저 현재 모델(IT/프로젝트/영업주도)을 성찰하라"를 첫 단계로 둔다(BLOG). POM 실패 분석: *"Success requires examining what needs to change in the architecture, the flow of work, the funding model, and the team design"* — 목표 모델을 현행 환경 이해 없이 적용하면 실패(BLOG, 2025).

## 각도 2 — 목적조직(target/product operating model) 정의와 성공/실패 조건 (등급: MEDIUM, 실무 컨센서스 다수 수렴)

**주장**: '목적조직'(미션/제품 중심 팀, target operating model)으로의 전환은 조건이 맞을 때 성공한다.

- **정의**: 제품/목적 중심 운영 모델은 *"단일 프로세스가 아니라 원칙에 기반한 개념 모델이며, 제품을 만드는 단 하나의 옳은 방법은 없다"*(BLOG, Cagan/Transformed). → AI가 "목적조직 = X"라고 단정하면 안 되는 1차 근거.
- **성공/실패 조건(여러 실무 소스가 수렴)**:
  - *"The model itself is rarely the constraint. The system and its boundaries are. Most failed transformations happen ... without understanding the environment."* (BLOG, 2025-11)
  - 팀이 *"a complete slice of value"* 를 오너십하고 *"real domain boundaries, not arbitrary org charts"* 에 맞춰 설계될 때 최소 조율로 전달 가능(Team Topologies류, BLOG).
  - 성공 구현의 공통 특징: 자율을 뒷받침하는 아키텍처·가시적 value stream·flow metrics·성숙한 DevOps(BLOG).
  - *"동기는 대개 경쟁 위협·강한 보상·좌절한 리더에서 오고, 많은 회사가 첫 시도에 실패한다"*(BLOG, Cagan). → **전환은 흔히 실패하며, CEO 수준의 전사 변화가 필요**하다는 정직한 신호.
- **정직성**: 이 조건들은 실무자 관찰(책·블로그)이지 통제 실험이 아니다. "목적조직이면 성과가 오른다"가 아니라 **"주변 시스템(아키텍처·경계·펀딩·팀 설계)이 목표 모델과 맞아야 성공한다"** 로만 말한다.

## 각도 3 — AI native 전환 (등급: STRONG 데이터, 단 반직관적·조건부) ★ 가장 강한 근거

**주장**: 'AI native'가 되면 조직 성과가 오른다 → **부분적으로만 참이며 자동이 아니다.** DORA(구글, 매년 ~5,000명 서베이)가 1차 근거.

- **개인 체감 vs 시스템 성과의 괴리(PRIMARY)**:
  - DORA 2024: *"When AI adoption increases 25%: Throughput delivery decreases 1.5% ... Delivery stability decreases 7.2%."* 그런데 75.9%가 AI를 업무에 쓰고 75%가 생산성 향상을 체감. → **체감 생산성 ≠ 시스템 delivery 성과.** (dora.dev/research/2024, RedMonk 분석 SECONDARY)
  - DORA 2024: *"improving the development process does not automatically improve software delivery — at least not without ... small batch sizes and robust testing."* → **flow 기본기가 게이팅 조건.**
- **2025년 업데이트(PRIMARY, dora.dev 2025, ~5,000명)**: *"positive relationship between AI adoption on ... throughput and product performance. However, AI adoption does continue to have a negative relationship with software delivery stability."* → 처리량·제품성과는 +로 돌아섰지만 **안정성은 여전히 −**.
- **AI는 조건을 증폭한다(PRIMARY)**: *"acceleration can expose weaknesses downstream. Without robust control systems — automated testing, mature version control, fast feedback loops — an increase [in AI] ... "* → **느슨한 결합+빠른 피드백 팀은 이득, 강한 결합+느린 프로세스 팀은 이득 거의 없음.** 내부 플랫폼 품질이 AI 가치 실현과 직접 상관(플랫폼 엔지니어링이 토대).
- **신뢰는 낮다(PRIMARY)**: AI 코드에 대해 2024년 39%, 2025년 30%가 "거의/전혀 신뢰 안 함". → 검증·거버넌스가 성과를 가른다.
- **REFUTED/과장 — 반드시 교정**: "기업 GenAI 파일럿의 95%가 실패"(MIT 인용, Fortune/Forbes 2025-08)는 **널리 반박되는 유행 수치**다(youreverydayai 등: 표본·정의·방법론 논란, "무시하라"는 반론). → **"95% 실패"를 사실로 인용 금지.** 도입이 어렵다는 방향성만 취하고 수치는 쓰지 않는다.
- **결론(하네스 적용)**: AI native를 은탄환으로 제시하지 않는다. "어떤 업무에·어떤 통제(테스트/버전관리/피드백/플랫폼) 위에서" 넣을지가 성패를 가른다고 말한다.

## 각도 4 — 스프린트/일하는 방식·산출물 관리 (등급: STRONG 게이팅 원리 / MEDIUM 개별 관행)

- **게이팅 원리(PRIMARY, DORA)**: 프로세스 개선은 *small batch sizes·robust testing* 같은 기본기 없이는 delivery를 자동 개선하지 않는다(위 인용). 병목은 코드 생성이 아니라 *"putting good code into production"*(SECONDARY, RedMonk).
- **우선순위 불안정의 해악(PRIMARY, DORA 2024)**: *"Instability in priorities, even with strong leadership, ... can significantly hinder progress."* → 잦은 방향 전환(무분별 pivot)은 리더십·문서·사용자중심이 좋아도 성과·웰빙을 해친다. → **big-bang·잦은 재편에 대한 경계 근거.**
- **개별 관행(PRACTITIONER)**: WIP 제한·flow metrics(리드타임 등)는 흐름을 드러내는 유용한 도구지만(agility-at-scale, getdx) 실증 인과는 약함. 지표는 **관찰용**이지 목표가 아니다(목표화 시 Goodhart).
- **정직성**: DORA 성과 등급(tier)은 고정 벤치마크가 아니라 매년 군집분석에서 새로 나온다 — 임계값을 절대 기준으로 인용 금지(SECONDARY).

## 각도 5 — 변화 시퀀싱: quick-wins/additive vs big-bang (등급: report-only / folklore + 이론)

- **Kotter short-term wins**: 초기 성과가 전환 동력·신뢰를 만든다는 8단계 모델의 한 축. 널리 가르쳐지고 체계적 문헌고찰도 있으나(rsisinternational systematic review, researchgate 338345322) **측정된 인과 우월성은 약하다** → PRACTITIONER 프레임으로만.
- **additive/incremental change**: 되돌리기 쉬운 작은 개입을 먼저 두는 접근(walkme incremental-change, BLOG). DORA의 "우선순위 불안정 해악"이 **잦은 전면 전환에 대한 간접 경계**를 준다(PRIMARY).
- **정직성**: **"additive-first가 big-bang보다 낫다"를 실증으로 말하지 않는다.** 되돌리기 쉬움·현행 강점 보존이라는 리스크 관리 논리로만 제시한다. big-bang이 옳은 맥락(경쟁 위협·전사 위임)도 실무 문헌이 인정한다(Cagan).

## 각도 6 — 우선순위화(영향·노력·의존성): RICE/ICE/WSJF (등급: report-only / 실무 프레임)

- **프레임**: RICE(Reach·Impact·Confidence·Effort), ICE(Impact·Confidence·Ease), WSJF(=지연비용 Cost of Delay ÷ 작업규모, SAFe). WSJF는 cost-of-delay 경제 논리를 갖는다(framework.scaledagile.com/wsjf, wikipedia Cost_of_delay, centercode RICE-vs-WSJF).
- **정직성**: 이들은 **판단을 구조화하는 실무 도구**이지 "이 공식이 최적 순서를 보장한다"는 실증이 없다. → 점수를 절대 진리로 포장 금지. 영향·노력·의존성 **신호를 드러내고 사람이 읽을 근거 한 줄**을 함께 두는 데만 쓴다. 의존성이 있으면 영향이 커도 지금 시작할 수 없다(선행 먼저).

---

## 주요 출처

**PRIMARY**
- DORA 2024 Report — dora.dev/research/2024 · cloud.google.com/blog(2024 DORA)
- DORA 2025 Report — dora.dev · cloud.google.com/blog(2025 DORA, ~5,000명)
- Organizational Diagnosis: An Evidence-based Approach — Change Management(tandfonline 10.1080/14697017.2011.630506)

**SECONDARY**
- RedMonk, "DORA 2024" 분석 — redmonk.com/rstephens/2024/11/26/dora2024
- McKinsey, The State of AI — mckinsey.com/capabilities/quantumblack

**PRACTITIONER / BLOG**
- Marty Cagan, 『Transformed』(product operating model) — producttalk.org · leaddev.com · medium 요약
- "When the system fits the Product Operating Model works" — medium(2025-11)
- Team Topologies × Product Operating Model — teamtopologies.com · planview.com POM guide
- Kotter 8-step systematic review — rsisinternational.org
- WIP limits — agility-at-scale.com · getdx.com flow-metrics
- WSJF / Cost of Delay / RICE — framework.scaledagile.com/wsjf · en.wikipedia.org/wiki/Cost_of_delay · centercode.com
- Incremental change / readiness — walkme.com · prosci.com

**REFUTED / 교정 인용만**
- "기업 GenAI 파일럿 95% 실패"(MIT 인용, Fortune/Forbes 2025-08) — 표본·정의·방법론 논란으로 널리 반박됨(youreverydayai). **수치 인용 금지**, 방향성만.

> 주의: 위 등급은 이 조사 시점(2026-07) 기준이다. DORA는 매년 갱신되고 등급·수치가 바뀌므로, 인용 시 연도를 명시하고 최신본을 확인한다. `/deep-research` 최종 synthesize 에이전트가 중단되어, 이 dossier는 검증 단계까지 통과한 claim(6 소스 블록 + 검색 스윕 URL)으로 직접 구성했다.
