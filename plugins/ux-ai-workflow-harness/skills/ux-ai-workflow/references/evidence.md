# UX × AI 근거 정본 (evidence)

이 하네스의 모든 판단·문안·금지 규칙은 이 파일을 근거로 한다. **여기 없는 수치는 하네스 산출물에 쓰지 않는다.**

**검증 방법** — 출발점은 NN/g 스터디 가이드 "Using AI for UX Work: Study Guide"(Tanner Kohler, 2026-09-04)다. 가이드는 약 80개 링크를 모은 색인이라 그 자체로는 주장이 얇다. 그래서 가이드가 링크한 NN/g 원문 기사 약 40편을 직접 받아 읽고, 원문이 인용한 1차 연구 중 설계에 영향을 주는 것(P&G 아이디에이션 실험·디지털 트윈·Baymard 감사·2023 생산성 재분석)은 원 출처나 원 출처의 직접 요약과 대조했다. **대조 결과 원문과 달라진 것은 항목 안에 `교정:`으로 적었다.**

## 등급 체계

등급은 **증거의 강도가 아니라 출처 유형**이다. 강도는 각 항목의 DV(결과변수)·표본·한계로 판단한다.

| 등급 | 뜻 |
|---|---|
| `[PRIMARY]` | 학술 문헌·워킹페이퍼 본문에서 직접 확인한 측정 |
| `[PRIMARY-VIA-NNG]` | 1차 연구이지만 **NN/g의 요약으로만** 확인했다. 수치는 NN/g 전사이며 원문 대조를 하지 않았다 |
| `[PRACTITIONER-STUDY]` | NN/g가 직접 수행한 소규모 평가·사용 실험(표본을 항목에 적는다). 통계적 일반화 근거가 아니다 |
| `[PRACTITIONER-GUIDANCE]` | NN/g 전문가 지침. 측정이 아니라 **실무 합의·권고**다 |
| `[INDUSTRY-MEASURE]` | 업계 기관의 자체 측정(이해상충이 있으면 명시) |
| `[SNAPSHOT]` | 특정 시점·모델에 묶인 결과. **현재 값으로 인용하지 않는다** |
| `[HYPOTHESIS]` | 저자가 가설·전망으로 제시한 것(측정 아님) |
| `[구조적 관찰]` | 하네스가 근거 전체를 보고 내린 판단 — 측정이 아니다 |

**모든 측정 항목에 DV를 적는다.** DV가 다른 결과를 "AI 쓰면 UX가 N% 좋아진다"는 한 문장으로 합치는 것이 이 주제의 지배적 오류다(인용 금지 X1·X3·X12).

---

## A. 이 하네스가 존재하는 이유

**E1 `[PRACTITIONER-GUIDANCE]`** 스터디 가이드 서문(Kohler 2026-09-04): "Should you use AI in your work? Yes. The question is no longer if it can be helpful, but when? And how?" / "Does AI guarantee better, more efficient work? No." / "If you don't want to work for the robot, make the robot work for you."
→ 하네스의 질문을 "AI를 쓸까"가 아니라 **"이 UX 작업의 어느 단계에, 어떤 조건으로"**로 고정한다(Phase 1 위임 지도).

**E2 [구조적 관찰]** 가이드가 모은 근거의 대부분은 `[PRACTITIONER-GUIDANCE]`·`[PRACTITIONER-STUDY]`다. **UX 작업에서 AI를 썼을 때 산출물 품질이나 의사결정 결과가 어떻게 달라지는지를 통제 실험으로 잰 연구는 이 가이드 범위에 없다.** 가장 가까운 통제 실험(E32)은 UX가 아니라 신제품 아이디어 과제이고, 결과변수는 전문가 품질 평정이다.
→ **INV-6의 근거다.** 하네스는 효과를 약속하지 않고, 단계별 위험과 확인 절차만 말한다.

---

## B. AI와 일하는 기본 자세

**E3 `[PRACTITIONER-GUIDANCE]`** CARE 프롬프트 구조(Kate Moran, 2024-05-24): Context(상황) · Ask(구체적 요청: 역할·산출물·개수·단계·형식) · Rules(제약) · Examples(좋은·나쁜 예). "you don't always have to write prompts in this exact order" / 단순 정보 탐색에는 이만큼 필요 없다. 예시 프롬프트는 "15개 생성 → 기준으로 5개 선택 → 순위·이유 → 표"의 단계 지시와 **"Ask me for additional information you need to do this"**로 끝난다. "it's very rare that I can just accept genAI's output exactly as it's returned to me."
→ Phase 2 프롬프트 골격. 단 CARE는 **기억 보조 장치이지 효과가 측정된 기법이 아니다.**

**E4 `[PRACTITIONER-GUIDANCE]`** AI를 인턴처럼(Kate Moran, 2024-09-20, "Ari"): 산출물은 초안, 사실은 이중 확인, 구체적·단계적 지시, 맥락 공유. 아첨(sycophancy)과 환각(hallucination)을 경계. **"Ari is your intern, not your mentor. If you're new to UX, be aware that it'll be much harder for you to catch Ari's mistakes and incorrect advice."** / "the amount of context, instructions, and double-checking they'll need may not always be worthwhile."
→ D7(검수 역량) 테스트와 INV-3의 근거. "AI가 안 맞는 일도 있다"를 정상 결론으로 둔다.

**E5 `[PRACTITIONER-GUIDANCE]`** 7가지 AI 죄악과 덕목(Tanner Kohler, 2025-09-26). 근거는 "nearly 400 hours with over 3,000 UX professionals" 와의 대화 관찰이며 **결과를 측정한 연구가 아니다.**

| 죄악 | 덕목 | 하네스에서 쓰는 곳 |
|---|---|---|
| Outsourced thinking — 추천을 그대로 받기, 여러 입력의 종합을 맡기기, 최종 품질 점검을 맡기기, 첫 초안·첫 아이디어를 맡기기 | **Ownership** — "Think first, ask second." / "If AI disappeared tomorrow, could you still confidently do what you do?" | Phase 0 '먼저 생각 한 줄'(선택), INV-3 |
| Wasted time — AI 길들이기가 직접 하는 것보다 오래 걸림 | **Automation** — 반복 작업에 쓰고 일회성은 신중히 | D5 반복성 테스트 |
| Lost details — 요약에 의존해 세부를 잃음 | **Selectivity** — 세부를 책임져야 할 때는 원문을 읽는다 | D4 책임 테스트 |
| Isolated ideation — 사람 없이 AI와만 발산 | **Inclusion** — AI로 대화를 준비하고 사람을 포함 | 워크숍 카드, Phase 4 |
| Naïve trust — 검증 비용 때문에 그냥 믿음 | **Skepticism** — "The more important truth and quality are, the more discerning you need to be about where you get your information from." | Phase 3 |
| Bland taste — 평범·획일 | **Originality** — AI 산출을 출발점으로 변형 | Phase 3 획일성 점검 |
| Defensive outlook — 변화 거부 | **Experimentation** — 비효율·병목에서 시도, 안 맞으면 강요하지 않음 | Phase 1 L4가 아니면 시도 가능 |

**E6 `[PRACTITIONER-GUIDANCE]`** 시작하기(2023-11-03): 작은 일부터, 출처와 링크를 요구하고 확인할 것("ChatGPT once cited a nonexistent NN/g employee"), 여러 안 요청, 반복(accordion editing·apple picking), 프롬프트 라이브러리. "AI Is Safest for Experienced UX Professionals."
→ 데스크 리서치 단계의 "출처 직접 확인" 체크포인트.

**E7 `[PRACTITIONER-GUIDANCE]`** 디자인 프로세스는 압축됐지 사라지지 않았다(Gibbons & Wang, 2026-03-13): 경험 많은 디자이너의 "그냥 만들었다"는 내면화된 프로세스의 압축이다. 직관은 주니어에게 신뢰도가 낮고, 책임 추적이 안 되고("What evidence backs this up?"), 규제 산업에서 위험하며, 편향을 숨긴다. 솔루션 퍼스트는 성숙한 도메인에서만 통하고 성공 사례만 보는 생존자 편향이 있다. 핵심은 **process literacy — 문제에 맞는 프로세스를 의도적으로 고르기.**
→ Phase 1에서 "AI로 단계를 건너뛰자"는 요청을 압축(허용)과 생략(위험 표기)으로 구분한다.

---

## C. 리서치

**E8 `[PRACTITIONER-GUIDANCE]`** 리서치 가속(Moran & Rosala 2024-09-27, 2026-01-21 재검토): **"AI ... is currently most helpful in the planning and analysis stages."**
- 계획: 데스크 리서치 시작점(최종 출처 아님·사실 확인 용도 금지·1차 출처 요구), 질문·과제 아이데이션(모범 사례 위반 주의 — "AI often writes tasks that can be leading or priming, even when you provide it with good examples"), 문서화(**템플릿을 주고** 채우게 하되 동의서 권한 등 오류 확인).
- 진행: 노트테이커는 행동을 못 보고 화자를 잘못 붙인다. **"AI tools aren't truly capable of properly facilitating or even notetaking during usability testing."** AI 인터뷰어는 구조화 인터뷰만.
- 분석: 전사·번역·요약(오류 확인), PII 정제(실수함 — 연구 대상 툴 이름을 회사명으로 오인해 지운 사례), 1차 코딩·군집(키워드 기반 피상적 묶음·"기타" 범주 과다·구간 누락), 정량 보조(검산 필수). **"Never rely on AI tools to perform all your analysis for you."** 사람이 묻는 맥락 질문(같은 참가자의 다른 발언과 모순? 진행자가 유도했나? 부끄러워 말 못 했나? 모집 기준에 안 맞았나?)은 AI가 못 한다. **"Don't attempt to use AI analysis tools for usability testing."**
- 정량: 주의할 점으로 "Mistakes"와 "Oversight of statistical assumptions".
- 보고: 페르소나·여정지도 초안은 **실제 리서치에 근거할 때만**. 교정·청중 맞춤에서 주의할 점 — "Outputs that don't fit your audience's communication style", 도움받을 일 — "Avoiding UX jargon (especially for a nonUX audience)".

**E9 `[PRACTITIONER-GUIDANCE]`** 리서치 계획을 AI로(Rosala 2024-04-05): "It can be tempting to just ask an AI tool to give you a research plan for a project. Don't do that." 계획을 부분으로 쪼개 순서대로 — 맥락 → 연구 질문(필요한 것보다 많이 요청, 외부 문서로 옮겨 중복 제거·재작성, **선택한 것만 들고 새 세션**) → 방법(어떤 질문에 어떤 방법인지·이유를 묻기, **행동 질문에 인터뷰·포커스그룹을 제안하는 경향**) → 포함 기준 → 스크리너·과제·가이드. **"Don't expect the AI to ask you the right questions in order to get a comprehensive outcome."** 스크리너·과제·가이드에 대해: "Unfortunately, there are a lot of bad examples of the above on the web. Conversational AI has been trained on all this data." AI가 자주 하는 실수 5가지: 과제 지시에 인터페이스 단어 사용(프라이밍) · 다른 사람이라고 상상하게 하는 과제 · 과제에 목표·행동 유도 없음 · 스크리너에 위장용 보기 없음 · 모집 문안에 과장된 마케팅 어조.
→ R-PLAN 카드의 단계 순서와 Phase 3 과제·스크리너 점검표.

**E10 `[PRACTITIONER-GUIDANCE]`** 학습은 위임할 수 없다(Rosala 2026-07-17): 리서치는 두 가지를 만든다 — 산출물(테마·권고·보고서)과 **수행한 사람들에게 일어나는 학습.** "A team that outsources research to AI gets a report, but it doesn't get the learning." 판정 질문: **"does doing it teach the team anything? If the answer is no, it's a good candidate to hand off."** 넘겨도 되는 것 — 모집·일정, 전사, 원자료 정리, 1차 토론 가이드 초안, 사고가 끝난 뒤 보고서 서식, 팀이 검증할 패턴 띄우기. 지킬 것 — **세션 진행, 실시간 관찰, 함께 하는 디브리프, 데이터가 무엇을 뜻하는지 정하는 해석.** "Let AI handle the support work, not the sense making." 완성도 높은 보고서는 **학습의 착각**을 만든다.
→ **D1 학습 테스트와 INV-1의 직접 근거.** 단 이 글의 신경과학 인용(E11)은 배경이다.

**E11 `[PRIMARY-VIA-NNG]` 배경** E10이 인용한 생성 효과 메타분석(Bertsch et al. 2007, *Memory & Cognition*): 스스로 생성한 정보가 읽기만 한 정보보다 잘 기억된다. 이야기 청취 시 fMRI 동기화 연구(Stephens et al. 2010; Grall et al. 2021). 옥시토신 연구는 NN/g가 Zak의 **잡지 기사**(Greater Good Magazine, 2013)로 인용했다 — 1차 연구 인용이 아니다.
→ **메커니즘 배경으로만 쓴다.** UX 팀이 리서치를 직접 할 때 학습·결정이 나아지는지를 잰 연구가 아니다(인용 금지 X10).

**E12 `[PRACTITIONER-STUDY]`** 합성 사용자(Rosala & Moran 2024-06-21). 방법: 이전에 실제 사용자로 수행한 **3개 연구**를 Synthetic Users·ChatGPT로 재현해 정성 비교. 관찰:
- 비현실적 행동 묘사 — 실제 학습자는 강좌를 끝까지 못 마쳤다고 말했지만 합성 사용자는 "다 마쳤다", 실제로는 안 쓰는 토론 게시판을 높이 평가.
- **모든 것을 중요하게 여김** — 우선순위가 없어 기능 우선순위·페르소나에 쓸모없음. 답이 얕고 추가 질문에도 모호함.
- 상상한 경험은 신뢰할 수 없음 — 의견보다 '과거 경험' 이야기가 더 틀림. **컨셉 테스트는 매우 위험**(드론 배송 아이디어에도 호의적).
- 권고: 실제 리서치 준비용(새 사용자군 학습·탐색 주제 고르기·인터뷰 가이드 파일럿) / **가설로 취급** / 실제 리서치 대체 금지 / **합성 결과를 실제 사용자 결과로 제시 금지("unethical")** / 니치·전문 사용자군은 피함 / 이해관계자가 대체물로 볼 조직이면 도입하지 않음.
- NN/g 슬로건: "UX without real-user research isn't UX."

**E13 `[PRIMARY]`** Park et al., arXiv:2411.10109. **버전이 바뀐 논문이다.** v1(2024-11-15) 제목은 "Generative Agent Simulations of 1,000 People"이고, v2(2026-04-22)·v3(2026-06-28)에서 "LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals"로 바뀌었다. **1,052명**을 2시간 인터뷰하고 그 녹취로 개인별 에이전트를 만들었다.
- **v1 본문**: GSS 응답 재현의 정규화 정확도 0.85 — 원 정확도 68.85% ÷ 참가자 본인이 2주 뒤 다시 답한 일관성 81.25%. 즉 *본인 재응답 일관성 대비* 비율이다.
- **v3 초록**: "achieved accuracies equal to 83%, 82%, and 86% of participants' own two-week test-retest consistency benchmark"(인터뷰만·설문만·둘 다), "compared with 74% for demographics-only agents." 인터뷰 기반 값은 v3에서 0.83이다. v3 본문 수치는 확인하지 않았다. **인용할 때는 버전을 함께 적는다**(X15). 인구통계만 준 모델·페르소나 문단 모델보다 인터뷰 기반이 정확했고 인종·이념 집단 간 편향도 줄었다. 경제 게임에서는 세 모델이 비슷했다(NN/g 전사: 0.66 동률).
- **DV**: 같은 개인의 설문·성격검사·경제게임 응답 재현. **제품 사용 행동이 아니다.**
- **이것은 '합성 사용자'가 아니라 실제 사람을 깊게 인터뷰한 뒤 만든 디지털 트윈이다** — 실제 사용자 데이터가 먼저 있어야 한다.

**E14 `[PRIMARY-VIA-NNG]`** Kim & Lee(arXiv:2305.09620): GSS 데이터로 미세조정한 디지털 트윈. 결측 응답 보완·과거 문항 소급 78%, 새 문항 예측 67%. 집단 수준 상관 r=0.98(보완) vs 0.68(새 문항). 고소득·고학력·백인 응답자에서 더 정확했다.
→ **보간은 되지만 외삽은 약하다.** 새 질문(= 대부분의 UX 리서치 질문)일수록 약해진다.

**E15 `[PRIMARY-VIA-NNG]`** Arora et al. 2025(*Journal of Marketing*): 실제 응답자 분포를 맞춘 합성 사용자 605명이 **방향(추세)은 따랐지만 크기가 유의하게 달랐고 분산이 일관되게 작았다.** NN/g는 이어서 "even though all these differences are statistically significant, they are fairly small ... their directional accuracy might still be useful in exploratory research"라고 적었다. 실제 인터뷰 16건을 RAG로 붙이자 분산이 늘었다.
→ 평균 차이는 작았다. 문제는 분산이다 — 변동은 "might reveal meaningful subgroups"이고 분산이 낮은 것은 "can be problematic"(NN/g). 합성 데이터로는 **극단값·양극화·하위집단을 보기 어렵다.**

**E16 `[PRIMARY-VIA-NNG]`** Sauro et al. 2024(MeasuringU): 트리 테스트에서 ChatGPT가 대부분의 실제 사용자를 크게 앞질러 **대체물로 부적합**했다.

**E17 `[PRIMARY-VIA-NNG]`** Sharma et al. 2023(arXiv:2310.13548) 언어모델 아첨 연구 — E12의 호의적·과장된 응답과 E19 AI 인터뷰어의 과잉 칭찬의 메커니즘 배경.

**E18 `[PRACTITIONER-GUIDANCE]`** 디지털 트윈(2025-08-01)·시뮬레이션 연구 리뷰(Budiu 2025-08-15): 합성 사용자(집단 서술로 생성)와 디지털 트윈(특정 개인 데이터로 생성)은 **연속선**이다. 맥락이 풍부할수록 낫다. 윤리 문제 — 참가자가 자기 데이터의 이런 재사용에 동의했는가, 의도 밖 맥락 사용. **"digital twins should complement, not replace, human-centered research."**

**E19 `[PRACTITIONER-STUDY]`** AI 진행 인터뷰(Rosala 2026-01-30). 표본: **연구 리더·ResearchOps 10명, 도구 2종(Marvin·UserFlix).** 관찰: 대본을 따르지 통찰을 따르지 않음(새 질문 생성·순서 변경·생략 못 함), 요약 후 확인 없이 다음 질문, 인터럽트·긴 침묵, 과잉 칭찬(아첨), 13~56분 편차, 소개 없이 시작해 정보를 감춤(프라이버시). "The conversation felt natural" 동의 3/10, "I felt comfortable" 5/10.
- 쓸 곳: 제품 피드백(구조화), 리서처 없는 팀의 디딤돌, 통역 없는 다국어 인터뷰, 모집 스크리닝.
- 쓰지 말 곳: **깊은 도메인 지식이 필요할 때 · 아직 모르는 문제 공간 탐색 · 인터뷰마다 경로가 달라질 때 · 보여줘야(화면 공유·시연) 할 때.**
- "structured interviews will likely remain the practical ceiling for most AI interviewer products."

**E20 `[PRACTITIONER-STUDY]`** AI 설문 작성(Banawa 2026-04-03). 방법: ChatGPT 5.4 Thinking·Claude Sonnet 4.6·Claude Opus 4.6에 **같은 프롬프트를 도구당 2회 이상.** 잘하는 것 — 여러 차원을 덮는 문항, 중립적 문장, 이중 질문 회피, 주제별 묶음, 폐쇄·개방형 혼합, 여러 표현 제안. 못하는 것 —
- 응답 부담 과소평가: 10분에 안 들어가는 분량을 들어간다고 함, **그리드 문항 권장**(일직선 응답 유발), **보기 10개 초과 다중선택**, **인구통계를 앞에 배치**, 다중선택 지시 불일치("정확히 3개" vs "최대 2개").
- 응답 보기 결함: **'기타' 누락**, 의미가 비대칭인 척도 끝점(Very poor ↔ Excellent), **자작 척도**, **리커트 범주 누락**(Agree·Disagree 빠진 5점).
- 형식 간과: 의미변별척도·단순 순위 문항을 고려하지 않음.
- 팁 7개 중: ① 명확한 연구 목적(연구 질문·연관 결정·대상·숨길 목적·분석 계획·목표 길이를 프롬프트에) ② 모범 사례를 지시 ③ **대안 생성** — "One of the most useful applications of genAI is producing multiple alternatives of a question or response set" ⑦ **"Pilot with Real People."** 
→ Phase 3 설문 점검표. 결과는 모델 버전에 묶여 있다(저자 명시).

**E21 `[PRACTITIONER-STUDY]`** 리서치 도구의 방법론 문제(Rosala 2026-03-13): AI 계획 도우미가 만든 사용성 과제가 **유도적**이었다 — 화면 용어를 그대로 쓰고 주의를 줄 곳을 지시("Pay close attention to whether the available courses are live online or self-paced"), 갈 곳과 단계를 지시("Navigate to 'Consulting'. 1) Identify ..."). 인터뷰와 사용성 테스트를 혼동(사용성 테스트 계획을 'Interview plan'으로 부름). **트랜스크립트만으로 사용성 테스트를 분석한다는 도구는 "snake oil"** — 참가자는 흥미로운 행동을 할 때 말하지 않는 경우가 많다. 도입 시: 벤더에게 AI 기능 설계·학습 데이터·통제 범위를 묻고, 데모만 믿지 말고 **훈련된 리서처가 실제 연구로 파일럿**, 비전문가 팀용 가드레일.

**E22 `[PRACTITIONER-STUDY]` + `[SNAPSHOT]`** AI 리서치 도구 한계(2023-07-02). 평가한 도구들의 광고 문구 예: "We'll do your research analysis for you! No need to analyze or tag your data." / "AI has no bias! Reduce bias in your research!" / "Our tool can analyze data from any kind of user-research method, including usability testing!" 관찰: 시각 입력 처리 불가 → 참가자는 모든 행동·요소를 말하지 않고 제품을 오해하기도 함 / 모호한 요약 / 연구 목표·이전 결과·참가자 맥락을 못 받음 / **인용·출처 연결 없음** / 불안정 / 편향. 요구할 것 — 맥락 입력, 연구자 수정 수용, **정확하고 구체적인 출처 연결**, 영상 처리.
→ Phase 3 분석 산출물 점검: "각 주장이 어느 세션·어느 발언에서 왔는지 연결되는가."

---

## D. 디자인

**E23 `[PRACTITIONER-GUIDANCE]` + `[HYPOTHESIS]`** UX-컨텍스트 디자인(Tony Alicea 2026-07-24): 모델은 맥락이 없으면 평균적인 화면을 만든다("it produces an average search screen"). 원자료를 통째로 주는 것에 대해 — "Without human guidance, however, it's possible that important takeaways may be lost in all the noise, or the AI may over-focus on the wrong takeaway." 디자이너만 디자인하는 것이 아니라 PM·엔지니어가 AI로 디자인 결정을 내리고 있으므로, **리서치·디자인 산출물의 소비자가 AI가 된다.** 실재하는 것 — Google Labs의 **DESIGN.md**(2026-04 오픈소스 초안 명세: 기계가 읽는 정확한 값 + 용도·do/don't 산문). **UX.md는 저자가 "A Hypothesis"로 명시한 제안**이다: 리서치 종합(제약으로 쓰일 수 있게 서술), 인터랙션 표준, 용어집, 사용자 모델, 세계 모델(사용 맥락: 중단·스트레스·규정). "Our experiments suggest that curated UX context improves AI-generated UI" — **실험이 공개되지 않았고 수치가 없다.** 미해결 질문을 저자가 열거: 어떤 산출물이 가장 도움이 되나, 원자료는 언제·얼마나, 효과 측정 지표, 모델이 바뀌면, **맥락이 너무 많을 수도 있나.**
→ Phase 2 'UX 맥락 팩'. 형식은 쓰되 **효과를 주장하지 않는다**(X6).

**E24 `[PRACTITIONER-GUIDANCE]`** AI 시대 디자인의 핵심 역량은 비평(Adam Elman 2026-06-12): 비결정적 시스템에는 정확한 명세 대신 **"좋음"의 정의를 판정 기준으로** 준다. 기준은 **객관적이되 자의적이지 않게**(예: "10초 미만" 같은 임의 임계값 대신, 응답 유형을 먼저 분류하고 유형별 기준), 복잡한 기준은 쪼개고 일부는 결정론 규칙으로, LLM 판정자는 **사람 주석과 대조해 보정**, 회귀 감시. 저자는 F1 0.8이면 "reliable enough"라고 했으나 **본인 실무 경험**이다(X5).
→ Phase 3 점검 기준을 쓰는 규칙("모호한 '좋은가?' 금지, 확인 가능한 문장으로").

**E25 `[PRACTITIONER-GUIDANCE]`** Promptframes(Evan Sunwall 2024-05-17): 와이어프레임 영역마다 콘텐츠의 목적·요구를 프롬프트로 문서화해 lorem ipsum 대신 현실적인 콘텐츠로 테스트한다. 공통 맥락 — 역할·조직·목표·톤·용어 정의·시각 원칙·**변형 개수**; 영역별 — 목적·원하는 결과·예시 + 문구(메시지·컨테이너·제약·톤 조정)/이미지(대상·동작·배경·크기·스타일)/데이터 시각화(유형·데이터와 이상치·열·정렬·축 …). 주의 — 완벽주의 경계, **임원 리뷰용 아님**, 콘텐츠는 수정 필요, **조직 AI 정책 준수**, 최종본은 사람의 "white-glove treatment".

**E26 `[PRACTITIONER-GUIDANCE]`** 프로토타입 테스트용 목 데이터(2024-09-06): 실제 데이터는 신중히. 표 생성 명세 — 고유성, 고정값, 서식, 그럴듯한 범위, **테스트 과제가 의존하는 값은 고정 제약으로 명시**(예: 특정 제품이 불만 최다), 분포(정규·파레토·균등·사용자 정의). **계산은 코드 실행으로, 계산 과정 표시, 합계 검증을 지시.** 차트 — 보여줄 것을 서술, 잡음 제거, 이상치 강조, 치수, SVG, "Don't Delegate Critical Thinking."

**E27 `[PRACTITIONER-STUDY]`** 모호한 프롬프트로 인터페이스 만들기(Huei-Hsin Wang 2025-12-05). 방법: 같은 페이지를 여러 AI 프로토타이핑 도구(Lovable·Bolt·Figma Make 등)에 상세 vs 모호 프롬프트로 생성해 비교. 모호한 프롬프트는 **'프랑켄슈타인 레이아웃'** — 불필요한 시각적 잡음, 같은 정보 반복, 직관에 어긋난 흐름, **정보 밀도 낮은 큰 컨테이너(숫자 하나짜리 카드)**·중요도와 어긋난 시각 위계. 개선 전략 5가지 — 정확한 시각 키워드(예: "neobrutalist", 특정 브랜드 모방은 지양), 가벼운 시각 참조, AI로 시각 분석 후 프롬프트화, **목 데이터 제공**, 코드 스니펫(라이선스 확인·컨텍스트 과부하 주의). **"don't confuse visual fidelity with design quality."** "Good Design Decisions Can't be Automated."

**E28 `[SNAPSHOT]`** AI 디자인 도구 현황(2024-04 "not ready", 2025-05 "marginally better"): 좁은 범위 기능(레이어 이름 바꾸기·문구 고치기·유사 찾기)이 가장 쓸모 있고 와이어프레임·프로토타입 생성은 아직 부족, 디자인 시스템이 필요.

---

## E. 글쓰기

**E29 `[PRACTITIONER-STUDY]` + `[SNAPSHOT]`** ChatGPT와 톤(Taylor Dykes 2024-03-08, 저자의 비공식 시도): **톤 단어 하나는 과장된다**("happy" → "delightful journey ... magic"). 미묘한 톤 단어를 여러 개 주면 낫다. **기존 문안을 예시로 주는 것이 미묘한 톤 단어 여러 개보다 나았다**("achieved even better results than a set of nuanced tone words"). 여러 대안을 요청하라. 유명인 이름으로 톤 지정은 피하라. 톤 가이드가 없으면 좋은 문안의 톤을 분석시켜 초안을 만든다.
→ W-COPY 카드: 형용사 대신 기존 문안·복수 대안.

**E30 `[PRACTITIONER-GUIDANCE]`** 스터디 가이드 글쓰기 절: "relying on it too heavily can grind away the unique style, tone, and message you wish to convey ... it will ultimately create a cacophony of monotony over time."

---

## F. 서비스 디자인

**E31 `[HYPOTHESIS]`** 서비스 디자인과 AI 에이전트(2025-02-14, 가설이라 명시하지는 않은 전망 글): 사용자 대리 개인 AI 비서와 조직의 AI 에이전트가 **새 행위자**로 들어온다. 지표가 바뀔 것 — AI 간 호환성, AI↔직원 호환성, 데이터 정확도·품질, 자동화 효과(완료율), 사용자 신뢰. **전망이지 측정이 아니다.**
→ SD-SERVICE 카드에서 블루프린트에 AI 행위자 줄을 추가하는 관점으로만 쓴다.

---

## G. 아이디에이션·워크숍

**E32 `[PRIMARY]`** Dell'Acqua et al. 2025, "The Cybernetic Teammate"(NBER w33641, SSRN 5188231). *Organization Science* 2026 게재판(DOI 10.1287/orsc.2025.20702)은 제목이 바뀌었고, **아래 수치는 모두 NBER w33641 본문 기준**이다. P&G 전문가 **776명**, 2×2(개인/2인 팀 × AI 없음/있음), 팀은 상업+R&D 1명씩, 사내 신제품 개발 과정에서 실제 사업 과제. **DV: 맹검 전문가의 해결안 품질 평정**(실행·시장 결과 아님).
- 품질(개인·AI 없음 대비): 팀·AI 없음 **+0.24 SD**, 개인+AI **+0.37 SD**, 팀+AI **+0.39 SD.** 팀+AI와 개인+AI는 "not significantly different."
- 소요 시간: 개인+AI **16.4% 감소**, 팀+AI **12.7% 감소.** 해결안은 AI를 쓰면 훨씬 길어졌다.
- **상위 10% 해결안(Table 10)**: 대조군 기준율 **5.8%** 대비 팀+AI **+9.2%p**(유의, 약 3배). 개인+AI +1.9%p, 팀·AI 없음 +3.7%p는 **유의하지 않다.** 팀+AI와 개인+AI의 **직접 차이도 p≈0.06~0.08로 통상 기준(p<.05)에서 유의하지 않고**, 팀+AI와 팀·AI 없음의 차이는 p≈0.18~0.21이다.
- AI 사용자는 자기 해결안이 상위 10%일 거라고 **9.2%p 덜** 예상했다(실제와 체감의 괴리).
- AI가 상업/기술 사일로를 허물었고 긍정 정서가 늘었다.
- NN/g 기사(2025-05-23)는 이를 대체로 정확히 옮겼다 — 평균에서 개인+AI가 "fiercely compete with teams using AI", 최상위는 "The AI-powered teams generated a disproportionately high number of the top 10%". 같은 글의 "even AI-absent teams had more ideas in the top 10% percentile"(개인+AI 대비)은 **둘 다 유의하지 않은 점추정끼리의 비교**다(0.037 vs 0.019).
- 교정: **스터디 가이드의 한 줄 요약**("Teams using AI for ideation outperformed individuals and teams without AI, as well as individuals with AI")은 개인+AI 대비 부분이 과장이다 — 평균 차이는 유의하지 않고 최상위에서도 직접 차이는 p<.05에 못 미친다. 하네스가 말할 수 있는 것은 **"대조군 대비 최상위 비율이 유의하게 늘어난 것은 2인 팀+AI뿐"**까지다(X3·X4).
- 한계: 하루짜리 과제, 2인 팀, 단일 기업, 참가자의 AI 프롬프팅 경험이 적었다(저자 명시).

**E33 `[PRACTITIONER-GUIDANCE]`** AI 워크숍 준비(Kohler 2025-05-30): AI 워밍업(같은 LLM 사용 권장), **맥락 파일 업로드**(텍스트 형식, 미리 업로드해 읽히는지 확인; 사용자 데이터는 맥락용이지 **워크숍 중 정식 분석 금지**), 커스텀 AI(GPT·Gem·Project), CARE 예시 프롬프트(출발점이지 통제가 아님). 저자는 페르소나 커스텀 AI가 "just as reliable as asking team members to predict user behavior"라고 했으나 **측정되지 않은 의견이다**(X13).

**E34 `[PRACTITIONER-GUIDANCE]`** AI 워크숍 진행(Kohler 2025-06-06): 사람은 첫 아이디어에 고착되고 권위자를 따르지만(양), AI는 발산이 쉽다(토끼). 구조를 바꾼다 — **AI로 발산(프롬프트당 15~20개) → 기준으로 AI가 상위 안 추림(예: 실현 가능성·바람직함·사업성 점수표) → 사람이 수렴·토론.** 개인 작업 시간은 AI 없이 5분이면 AI와 **8~10분**(읽고 고치는 시간). 2~4명이 **프롬프트를 같이 쓰기**("The discussion people have while drafting a prompt together is often as valuable as the outputs"). 디지털 문서로 기록. 앞선 글(2025-05-23): **"it's safest to rely on AI for activities like ideation, where 'truth' is not the primary criterion for success (as opposed to something like data analysis)."**
→ D2 진실 기준 테스트와 I-WORKSHOP 카드.

---

## H. AI UX 도구의 정확도

**E35 `[INDUSTRY-MEASURE]` + `[SNAPSHOT]`** Baymard 2023: GPT-4로 이커머스 페이지 **12개**를 UX 감사해 전문가 결과와 비교. 제안의 정확도 **20%(80%가 오탐)**, 스크린샷 기준 실제 이슈의 **26%**, 라이브 페이지 기준 **14%** 발견. 평균 2.9개 맞히고 18.5개 놓침, 10.6개는 시간 낭비, **1.3개는 따르면 해로움.** GPT-4 시대 결과다. 교정: NN/g 전사는 "discovered only 14% of the UX issues present in the input screens"로 적었지만, Baymard 원문에서 14%는 **라이브 페이지** 기준이고 스크린샷 기준은 26%다. Baymard는 자사 AI 감사 도구(E37)를 파는 기관이라 이해상충이 있다.

**E36 `[INDUSTRY-MEASURE]` + `[SNAPSHOT]`** 이후 측정은 **한 연구**다 — Microsoft 연구자 2명이 2025-03 AI 도구 4종을 평가했다. NN/g(2026-01-30)는 정확도를 **50~70%**로 전사했고, Baymard 블로그 "AI heuristic evaluations"(2026-05 갱신)는 같은 연구를 **50~75%**로 적는다. **상단값이 출처마다 다르고(70 vs 75) 원문을 확인하지 못했다** — 독립된 두 측정으로 세지 않는다(X14). 핵심 논지는 수치가 아니라 구조다 — **"Seven of them are good recommendations… but three of them aren't ... But you can't tell which recommendations are the good ones."** 작은 변경이 전환율에 큰 영향을 준 사례(캐러셀 점 → 썸네일, +1%).

**E37 `[INDUSTRY-MEASURE]` (벤더 자기보고 — 이해상충)** Baymard의 UX-Ray: 가이드라인 700여 개 중 **AI가 95% 이상 정확도를 낸 154개만** 검사. AI는 **패턴 분류**에만 쓰고 그 패턴이 좋은지 나쁜지의 **평가는 결정론 규칙**으로 처리 — "Second step is determining, 'Is that [design pattern] a problem here? Is that good or bad, or somewhere in between?' And we find that, when you ask LLMs to do that, that's where things go off the rails." 가이드라인 개수(154/700+)는 NN/g 2026-01 시점 값이다 `[SNAPSHOT]`. 벤더에게 물을 것 3가지: 정확도를 어떻게 평가하나 / 어디서 깨지나 / 어떤 가드레일이 있고 생성형 AI가 정확히 어떤 역할인가.
→ T-TOOL 카드의 질문 목록과, Phase 3에서 **분류(무엇이 있나)와 평가(좋은가)를 나눠 묻는** 원칙. 95%는 벤더 자기보고로만 인용한다(X11).

---

## I. 생산성·현황 스냅샷 (현재 값으로 쓰지 않는다)

**E38 `[SNAPSHOT]`** NN/g 2023 재분석(Nielsen): 고객지원 상담원 시간당 문의 처리 **+13.8%**, 비즈니스 문서 시간당 **+59%**, 프로그래머 주당 프로젝트 **+126%**, 세 연구 평균 **+66%**. 신규 데이터가 아니라 세 통제 연구의 재분석이고, 서로 무관한 과제를 평균했다. 스터디 가이드 자체가 이 절을 "some highlight findings that still hold today, others have likely changed"라고 단서를 달았다.

**E39 `[PRIMARY]` + `[SNAPSHOT]` (인접 분야, NN/g 원문이 인용한 연구 아님)** METR 2025-07 무작위 대조 실험(2025년 초 도구): 숙련 오픈소스 개발자 **16명**, 자기 대형 저장소 과제, AI 허용 시 소요 시간 **+19%**(신뢰구간 +2%~+39%). 참가자는 24% 빨라질 거라 예상했고 끝난 뒤에도 약 20% 빨랐다고 믿었다. UX 과제가 아니고 표본이 작다.
- **후속(METR 2026-02-24)**: "we believe it is likely that developers are more sped up from AI tools now" — 새 실험 추정치는 복귀 참가자 −18%(−38%~+9%), 신규 참가자 −4%(−15%~+9%)(음수 = 빨라짐)이지만 METR 스스로 "an unreliable signal"이라 했다(AI 없이 일하기를 거부한 개발자의 불참 등).
- 그래서 이 항목에서 쓰는 것은 **"2025년 초 시점에 체감과 실측이 반대였다"**는 관찰뿐이다. "AI를 쓰면 느려진다"는 현재 사실로 쓰지 않는다.
→ E38과 함께 두는 이유: **체감 속도는 실제 속도의 센서가 아니다.** E32의 "자기 결과를 과소평가" 관찰과 방향은 반대지만 결론은 같다 — **자기보고로 효과를 판정하지 않는다.**

**E40 `[PRACTITIONER-GUIDANCE]`** 스터디 가이드의 커리어·현황 절(2025~2026 글 다수): 사람을 이해하고 좋은 질문을 하는 기본기는 남는다 / 전략·스토리텔링·성과·데이터 판단 / 제너럴리스트 / 취향과 분별 / AI가 VR 하이프 사이클을 따를 수 있다 / "AI 디자인"은 네 직무(AI로 디자인·AI 제품 디자인·AI 에이전트를 위한 디자인·AI 자체 디자인)로 갈라졌다 / 컨설팅 고객은 여전히 판단·리서치 엄밀성·현실 제약 존중을 기대 — "Maintain a clear distinction between exploratory signals and design recommendations" / State of UX 2026: 안정화, 차별화와 사업 성과.
→ **게이트·규칙의 근거로 쓰지 않는다.** 하네스의 경계(AI *제품* 디자인은 범위 밖)와 Phase 4 보고 문구("탐색 신호 vs 권고 구분")에만 쓴다.

---

## 인용 금지 목록 (do-not-cite)

하네스 산출물에 아래 형태로 쓰지 않는다.

| # | 금지 주장 | 왜 | 대신 |
|---|---|---|---|
| X1 | **"AI가 UX 작업 생산성을 66%(또는 126%) 올린다"** | 2023 재분석이고 무관한 과제를 평균했다(E38). 인접 분야 RCT는 2025년 초 시점 숙련자에서 오히려 느려졌다(E39, 후속은 현재 더 빨라졌을 가능성을 언급 — 방향도 시점에 따라 바뀐다). UX 과제를 잰 통제 실험은 이 가이드 범위에서 확인되지 않았다(E2) | "반복되는 지원 작업에서 시간이 줄 수 있으나, 이 작업에서 실제로 줄었는지는 **체감이 아니라 소요 시간을 재야** 안다" |
| X2 | **"합성 사용자·디지털 트윈이 85% 정확도로 사용자를 예측한다"** | 0.85는 v1 기준 본인 2주 재응답 일관성 대비 비율이고(v3 초록은 인터뷰 기반 0.83), DV는 설문·성격·게임이지 제품 행동이 아니며, 같은 사람을 2시간 인터뷰한 트윈이다 — 합성 사용자가 아니다(E13) | "실제 인터뷰 데이터로 만든 개인 트윈은 설문 응답을 상당히 재현했다. 집단 서술만으로 만든 합성 사용자는 방향만 맞고 크기·분산이 달랐다(E15)" |
| X3 | **"AI를 쓰면 아이디어 품질이 3배"** | 3배는 **팀(2인)+AI가 상위 10%에 들 확률**(대조군 5.8% 대비)이고, 개인+AI는 대조군 대비 유의하지 않았다(E32) | "2인 팀이 AI와 함께할 때 대조군보다 최상위 아이디어 비율이 높아졌다(하루짜리 사내 과제, 전문가 평정)" |
| X4 | **"AI와 혼자 하면 팀이 필요 없다"** | 평균 품질이 AI 없는 2인 팀과 비슷했을 뿐이고, 대조군 대비 최상위 비율이 유의하게 늘어난 것은 팀+AI뿐이다(개인+AI와의 직접 차이는 p≈0.06~0.08)(E32). 아이디어를 실행할 사람들의 합의는 측정 대상이 아니었다(E5 Isolated ideation) | "개인+AI의 평균 품질은 AI 없는 2인 팀과 비슷했다" |
| X5 | **"LLM 판정자 F1 0.8이면 충분하다"**를 기준처럼 | 한 실무자의 경험치(E24) | "사람 주석 표본과 대조해 보정하라" |
| X6 | **"UX.md(UX 맥락 파일)가 AI 산출물 품질을 올린다"** | 저자가 가설로 명시했고 실험이 공개되지 않았으며 맥락 과잉 가능성을 스스로 묻는다(E23) | "맥락 없이는 평균적 산출이 나온다는 관찰에서 나온 **가설**이다. 이 팀에서 효과는 전후 비교로 직접 봐야 한다" |
| X7 | **"AI UX 감사 정확도 70%면 쓸 만하다"** 또는 Baymard 20%를 현재 값으로 | 시점 스냅샷이고(E35·E36), 핵심 문제는 수치가 아니라 **어느 30%가 틀렸는지 모른다는 것**이다 | "AI 감사 결과는 항목마다 사람이 맞는지 판정해야 쓸 수 있다" |
| X8 | **"AI 인터뷰어가 사용자 인터뷰를 대체한다"** | 구조화 인터뷰까지만, 표본 10명 관찰(E19) | "구조화 피드백·스크리닝·다국어에는 쓸 수 있고, 탐색형 반구조화 인터뷰는 사람이 한다" |
| X9 | **"트랜스크립트로 사용성 테스트를 분석할 수 있다"** | 행동은 발화에 없다(E8·E21·E22) | "트랜스크립트 분석은 발화 분석이다. 사용성 결론은 행동 관찰에서 나온다" |
| X10 | **"리서치를 직접 하면 뇌가 동기화돼 팀 성과가 오른다"** | fMRI·옥시토신·생성 효과는 배경 메커니즘이고 UX 팀 결과를 잰 연구가 아니다(E11) | "직접 관찰·해석하는 과정에서 학습이 일어난다는 것이 NN/g의 권고다(E10)" |
| X11 | **"UX-Ray는 95% 정확하다"**를 독립 사실로 | 벤더 자기보고(E37) | "Baymard는 자사 기준으로 95% 이상인 항목만 검사한다고 밝힌다" |
| X12 | **"이 하네스를 쓰면 리서치·디자인 품질/속도가 N% 오른다"** | 측정 없음(E2) | 주장할 수 있는 것은 Phase 4의 두 가지뿐 |
| X13 | **"페르소나 챗봇은 팀원이 사용자 행동을 예측하는 것만큼 믿을 만하다"** | 저자 의견, 측정 없음(E33). 합성 응답은 아첨·이상화 경향(E12·E17) | "페르소나 챗봇은 실제 리서치로 만든 페르소나를 팀이 떠올리게 하는 보조물이다. 답을 사용자 근거로 쓰지 않는다" |
| X14 | **Microsoft 50~70%와 Baymard 50~75%를 독립된 두 측정으로** | 같은 Microsoft 2025-03 연구를 두 출처가 다르게 전사했다(E36) | "한 연구에서 도구 4종이 대략 50~70%대(출처마다 상단값이 다름)" |
| X15 | **Park 0.85를 버전 표기 없이** | v1(2024) 값이고 v3(2026) 초록은 인터뷰 기반 0.83이다(E13) | "v1 기준 0.85, 최신판 초록 0.83 — 둘 다 본인 재응답 일관성 대비" |

## 확인하지 못한 것 (UNVERIFIED — 단정 금지)

- 스터디 가이드의 **동영상·팟캐스트 링크**(약 15개)의 내용 — 텍스트가 없어 확인하지 않았다. 하네스는 그것들을 근거로 쓰지 않는다.
- Kim & Lee·Arora·Sauro 수치의 **원문 대조** — NN/g 전사로만 확인(`[PRIMARY-VIA-NNG]`).
- Microsoft 2025 평가(E36)의 원문 — NN/g(50~70%)와 Baymard(50~75%)의 전사가 상단값에서 갈리고, 어느 쪽이 맞는지 확인하지 못했다.
- Park et al. v3(E13)의 본문 수치 — 초록만 확인했다.
- DESIGN.md(E23)의 공개 시점 — NN/g 기사와 2차 출처로만 확인했다.
- **UX 맥락 파일(DESIGN.md/UX.md류)이 AI 생성 UI를 개선하는 정도** — 공개된 측정을 찾지 못했다.
- AI 보조 UX 리서치·디자인이 **최종 제품 결과(전환·과업 성공·만족)**를 바꾸는지 — 측정을 찾지 못했다.
