# 근거 — 개발 방법론 진단·제안 (2024-2026 조사)

이 문서는 `methodology-advisor`의 사실 기반이다. deep-research 하네스(웹 검색 팬아웃 → 소스 fetch → **주장별 적대적 검증** → 종합)로 수집했고, **24개 소스에서 추출한 75개 주장을 내부 3표 적대 검증**해 **70건 confirmed / 5건 refuted**로 판정했다(수치는 내부 검증 집계이며, 소스 원장 전문은 본 문서에 부록으로 첨부하지 않았다 — 성격은 '내부 조사'다). refuted 5건은 아래 [교정](#refuted--반드시-교정)에 명시하고 **본문·제안에서 절대 그대로 말하지 않는다**.

정직성 원칙(이 도구 전반): **방법론 우열이 아니라 맥락 적합성**, **은탄환·'N% 개선' 약속 금지**, **수치는 SOURCE-TIER·출처와 함께만(관찰값)**, **모든 권고에 트레이드오프+안티패턴 동반**.

## SOURCE-TIER (신뢰도 등급)

| 등급 | 의미 | 인용 태도 |
|------|------|-----------|
| **PRIMARY** | 1차 학술·원저·공식 리포트·1차 증언(내부자 회고) | 프레임워크·정의의 근거로 사용 |
| **SECONDARY** | 리포트 요약·독립 언론 | 1차와 교차 확인 후 사용 |
| **BLOG** | 실무 블로그·벤더 | 실무 관행·예시로만, 수치는 벤더 자기주장으로 표기 |

핵심 PRIMARY: Boehm & Turner『Balancing Agility and Discipline』/ IEEE Computer 2003(home ground 5인자·위험기반 균형), Clarke & O'Connor 2012(상황 요인 8분류 44요인), Ahimbisibwe et al. 2015(contingency fit·37 CSF), DORA 2024/2025 State of DevOps(2025 실제 제목 'State of AI-assisted Software Development'), Jeremiah Lee 2020(Spotify 회고, 내부자 1차 증언).

---

## REFUTED — 반드시 교정 (그대로 말하지 말 것)

1. **DORA 2025 AI 채택률은 95%가 아니라 90%다.** (confidence high) 한 2차 블로그(Faros)가 95%로 오기했으나 1차(Google Cloud·dora.dev)는 "90%로 급증(전년 대비 14%p↑, 2024 약 76%)". 생산성 향상 ">80%"는 정확. → **"약 90% 채택, >80%가 생산성 향상 인식"** 으로만 인용.
2~3. (동일 오류의 다른 2차 소스 2건도 같은 이유로 refuted.)
4~5. **Boehm & Turner 위험기반 방법은 4단계가 아니라 5단계다.** (confidence high, 1차 IEEE 2003) 4단계 요약은 책의 *예시*의 하위단계(Step 4a/4b)를 일반 방법으로 오독한 것. 실제: **① 위험분석(환경·agile·plan-driven 3범주) → ② 순수 home ground인지 평가 → ③ 명확한 home ground가 없으면 하이브리드 아키텍처(agile 강점 부분 + plan-driven 나머지) → ④ 통합 위험해소 전략 수립 → ⑤ 지속 모니터링·재조정.** 특히 **Step 3(하이브리드 분할)과 Step 5(지속 재조정)** 가 이 방법의 핵심 통찰이다. → [selection-frameworks.md](../selection-frameworks.md)에 5단계로 반영.

---

## 축 1 — 컨틴전시(맥락 적합) 이론이 이 도구의 심장 [PRIMARY]

- **Boehm & Turner** [PRIMARY, IEEE 2003·저서]: agile과 plan-driven은 배타가 아니라 **하나의 연속선**. **home ground 5인자 = Size·Criticality·Dynamism·Personnel·Culture**(5축 극좌표). Dynamism·Personnel 축은 **비대칭**(agile은 변경률 고·저 모두 OK지만 plan-driven은 저변경률에서만; plan-driven은 숙련도 고·저 모두 OK지만 agile은 상위 숙련 비중 요구 — 원저 예시상 변경률 높은 국면의 agile home ground는 상위 숙련(대략 Cockburn L2/3 30%대) 비중을 요구하며, 정확한 %는 표·국면마다 다르다). 결론: **"은탄환 없음 · 미래 앱은 agility와 discipline을 함께 요구."** home ground에서 멀어질수록 순수 사용 위험↑, 반대 방식 혼합 가치↑.
- **Clarke & O'Connor 2012** [PRIMARY]: 상황 요인 **8분류(Personnel·Requirements·Application·Technology·Organisation·Operation·Management·Business)·44요인**. 용도는 **"현행 상황 프로파일 구축 → 프로세스 정의·최적화·재단"** — 본 하네스의 *진단→제안* 워크플로를 직접 정당화. 예: Business 분류의 **결제 조건** — 고정 계약이면 agile 부적합, T&M+요구 불확실이면 엄격 waterfall 부적합.
- **Ahimbisibwe et al. 2015** [PRIMARY]: contingency fit 모델(37 CSF, org/team/customer). **프로젝트 특성과 방법론 불일치가 실패의 핵심 동인** — 방법론 오적용은 감정이 아니라 실패 원인이다.
- **Cynefin/Stacey** [프레임워크]: 신규 개발은 대개 Complex(probe-sense-respond) → 경험주도. 단 Stacey diagram은 Ralph Stacey 본인이 단순화된 규범적 사용과 거리를 둠(대화 도구로만).

## 축 2 — 방법론 카탈로그 사실 [BLOG·1차 혼합]

- **Scrum/Kanban/Lean/XP** [BLOG, 2024]: Scrum=보통 1~4주 스프린트(출처 표기는 2~4주)·3역할, 동적 환경에선 경직될 수 있음(스타트업). Kanban=WIP+연속흐름·역할/회의 불요·지원/유지보수 적합·마감 모호 위험. Lean=낭비제거·결합 가능. XP=기술관행(TDD·페어·CI), 비기술 팀엔 과함. **one-size-fits-all 없음, 하이브리드 흔함**(Scrum 스프린트에 Kanban WIP).
- **Shape Up** [BLOG]: 6주 사이클+cooldown·betting table·shaping·회의 최소(no daily standup). **성숙 제품('Scrum 피로')에 적합, POC/MVP엔 부적합.** 단점: 버그/기술부채 최대 6주 지연, 다팀 확장 난이도.
- **스케일드 애자일** [BLOG]: 팀 수 범위 — **SAFe 8~100+·LeSS 2~8(단일 PO/제품)·Nexus 3~9**. **과도 채택 흔함**(LeSS로 충분한 규모에 더 무거운 SAFe 도입 — 밴드 경계는 LeSS Huge/SAFe를 binding-constraint로 판단). 선택 규칙: **"묶인 제약(binding constraint)을 한 문장으로 못 말하면 프레임워크 결정은 아직 준비 안 됨."** SAFe 비판(Gothelf): 학습이 아니라 예측가능 전달 최적화, "경영 그대로 둔 채 agile 흉내."
- **Spotify 'model'** [PRIMARY, 2020 회고]: **작성 시점에도 완전 실행 안 됨("일부는 야망, 일부는 근사")·창작자가 복제 경고.** 정렬 없는 자율 → 일관성 붕괴·조율비↑·관리 책임 공백·agile 성숙도 부재. **복제는 문서화된 안티패턴.**
- **Waterfall home ground** [BLOG]: 안정 요구·규제(국방/의료/금융). DevOps는 "전통 의미의 개발 방법론이 아니라 dev-ops 교량 관행."

## 축 3 — 현행 진단 실무 [BLOG·1차]

- **애자일 성숙도 모델** [BLOG]: 5단계(Ad hoc→Optimizing / Crawl-Walk-Run / Pre-Crawl→Fly), **레이더 차트**로 단일 점수 대신 다차원 제시, **"doing agile vs being agile"**(카고컬트 탐지), 자가·익명, 재평가 주기 **월/분기(스프린트마다 아님)**. (TeamRetro의 "~15% 완전 성숙·~60% 2~3단계 정체"는 BLOG 자기주장.)
- **Value Stream Mapping** [BLOG+1차]: idea→production 흐름 시각화·**대기시간 정량화**·병목/핸드오프 표적. **측정 가능한 개선 목표를 먼저 정의**, 팀이 **최고 ROI 한 가지에 합의·행동**(분석마비 회피) 후 반복. DORA 지표(리드타임·배포빈도·변경실패율·복구시간)로 접지.
- **본 하네스 설계 정당화** — 성숙도 모델·VSM·contingency 프로파일 모두 *현행 진단 → 근거 기반 개선 제안*이라는 동일 워크플로를 지지한다.

## 축 4 — 2024-2026 동향 (AI가 프로세스를 바꾼다)

- **DORA 2025**("State of AI-assisted Software Development") [PRIMARY/SECONDARY]: **AI는 amplifier** — 조직의 기존 강점은 키우고 약점(역기능)은 악화. **채택 ~90%·생산성 향상 >80%·AI 코드 불신 30%·자율 에이전트 모드 미사용 61%.** 전통 티어(Elite/High/Med/Low)를 **7개 팀 아키타입**으로 교체. **AI ROI는 도구가 아니라 조직/프로세스에서 나온다**(작은 배치·버전관리·user-centric 등 7역량). 동반 'DORA AI Capabilities Model'.
- **DORA 2024** [PRIMARY]: AI가 생산성·몰입·만족은↑ 그러나 **전달 안정성·처리량엔 부정적**("만병통치 아님"). **작은 배치+견고한 테스트는 여전히 필수.** 불안정한 조직 우선순위 → 번아웃(완화 저항적). (이 2024 방향성을 'DORA 2024 anomaly'로 재특징화한 것은 Gene Kim의 **해석 코멘터리**[SECONDARY]이지 리포트 1차 데이터가 아니다.)
- **Spec-driven / vibe coding** [1차/BLOG]: SDD=**명세가 source of truth**, 4단계(Specify/Plan/Implement/Validate), vibe coding(비결정적 trial-and-error)의 해독제. 도구: GitHub Spec Kit(/specify·/plan·/tasks)·Amazon Kiro. "AI는 패턴 완성엔 강하나 의도 추론엔 약함." **AI 에이전트 시대의 난제는 코드 작성이 아니라 의도 명세로 이동.** (SDD "오류 최대 50% 감소" 주장은 **미인용·nascent** — 인용하지 말 것.)
- **함의**(이 도구): 방법론 제안에 **AI 활용 현실**을 반영하되, "AI 도입=개선"이 아니라 **AI는 증폭기**임을 명시. 작은 배치·테스트·버전관리 같은 fundamentals가 AI 시대에 더 중요.

---

## 이 도구가 근거를 쓰는 규칙

1. 수치는 **SOURCE-TIER·연도·출처와 함께**, **관찰값**으로만(예: "DORA 2025 관찰 — 이 팀의 보장 아님"). "N% 개선" 약속 금지.
2. BLOG 자기주장 수치(예: "~15% 완전 성숙")는 **벤더 주장으로 표기**.
3. refuted 5건(95% 채택·4단계 Boehm-Turner)은 **교정본으로만**.
4. 프레임워크(Cynefin·Stacey·home ground)는 **대화·판단 도구**이지 결정론적 계산기가 아님 — 과신 금지.
5. 방법론 **우열 단정 금지** — 맥락 적합성·트레이드오프·안티패턴으로만.
