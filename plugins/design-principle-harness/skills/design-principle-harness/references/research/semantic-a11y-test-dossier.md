# 시맨틱 태그·접근성·테스트 설명의 AI 가독성 근거 dossier

**목적.** 이 문서는 "시맨틱 HTML·ARIA/접근성 마크업·서술적 테스트 설명·접근성 기반 테스트 셀렉터가 AI 코딩 에이전트의 코드 이해·안전한 기여를 돕는가"라는 물음을, 5개 연구 렌즈와 5회의 적대적 검증 패스로 통합한 단일 정본 근거 기반이다. 자매 문서 [`evidence-dossier.md`](evidence-dossier.md)(명명·주석·구조 지표·SOLID·중복·Goodhart·refactoring·judge·repo-navigation 8렌즈)의 **자매편**이며, 그와 동일한 두 축 채점(측정 신뢰도≠타당도)·동일한 지배 단서(perturbation/production ≠ intervention)를 상속한다. 검증자가 요구한 7건의 citation-hygiene 교정은 이미 본문 전체에 반영되어 있다(§적대적 감사 결과 참조).

---

## 0. 지배적 단서 — 이 문서를 읽는 법

### 0.1 두 축 채점 (자매 문서 §0.2와 동일)

모든 신호는 두 개의 직교하는 등급을 갖는다. 단일 confidence 수치는 정밀한 측정 가능성을 타당성으로 새어 들어가게 하므로 정직하지 못하다.

- **Measurement confidence** — 신호를 결정론적으로 신뢰성 있게 셀 수 있는가? (`getByRole` vs `getByTestId` 카운트, `role=` 속성 census, 커멘트아웃 주석 = High. "이 alt 텍스트가 정확한가", "이 ARIA가 UI를 옳게 기술하는가" = None.)
- **Validity confidence (AI-agent legibility 대상)** — 신호가 실제로 AI legibility / 안전한 기여를 *예측*하는가? **이 문서의 모든 신호에서 EXTRAPOLATED 또는 ABSENT다** — 어느 것도 "저장소의 시맨틱/a11y/테스트-설명 점수를 올리면 같은 에이전트의 성공률이 오른다"를 측정하지 않았다.

### 0.2 모든 것을 지배하는 발견 — perturbation/production ≠ intervention, 그리고 "직접 개입 연구 없음"

> **시맨틱 HTML 랜드마크·heading 계층·`<button>` vs `<div onclick>`·ARIA·WCAG 준수·서술적 테스트 설명·접근성 기반 테스트 셀렉터 — 이 중 어느 것도, "그 신호를 *올리는 것*이 *동일한* 저장소에서 *특정 LLM/에이전트의* 코드 이해나 안전한 기여를 *개선*한다"를 측정한 통제 연구를 찾을 수 없었다.**

이 문서의 근거는 세 종류뿐이며 어느 것도 intervention이 아니다:

- **perturbation** — 코드/마크업을 열화시키고 성능이 떨어지는 것을 관찰 (예: semantic-preserving mutation, 오도 주석 주입).
- **production** — AI가 *산출하는* 것을 측정 (예: AI가 만든 ARIA/alt 텍스트의 오류율, Pass@1과 품질의 상관).
- **observation-space / idiom** — a11y tree가 web-agent의 *관측 공간*이라는 사실, 또는 vendor 문서가 권장하는 관용.

특히 다음 두 가지는 **관용/관측-형식 사실이지 개입 근거가 아니다**: (1) a11y tree가 agent 관측 공간이라는 것 — 저자가 더 많은 ARIA를 *쓰면* 에이전트 이해가 오른다는 뜻이 아니다. (2) `getByRole`가 refactor-robust하다는 것 — 테스트 *소스 코드*를 LLM이 더 잘 읽는다는 뜻이 아니다. 두 경우 모두 전이(transfer)는 **관용적 추론**이지 측정이 아니다.

### 0.3 Provenance 태그 (자매 문서와 동일 어휘)

- **[CONFIRMED-read]** — 1차 텍스트(초록+결과 또는 전체)를 읽었고 수치는 그로부터 인용됨.
- **[PLAUSIBLE-sourced]** — 실제 출처는 확인했으나 세부 수치는 초록/2차 요약 의존; 크기는 방향성.
- **[ESTABLISHED]** — 표준/정전/실무 정전 앵커(W3C·MDN·Testing Library·Playwright docs); arXiv 검증 대상 아님.
- **[UNVERIFIED]** — 읽은 1차 출처에 결부하지 못한 수치; 점수화된 어떤 주장에서도 배제.

### 0.4 이 문서의 결론 미리보기

세 렌즈(1·2·4)가 다루는 신호는 **거의 전부 report-only**다. **직접 causal 근거가 있는 채널은 단 하나 — 명명/의미단서 채널**(semantic-preserving mutation이 debugging을 78% 열화; Lens 5)뿐이며, 이는 이미 자매 문서 Tier A의 근거다. ARIA/WCAG·시맨틱-HTML-태그·테스트-설명·테스트-셀렉터는 모두 report-only이고, 이 중 몇몇(자동 ARIA/alt, tests-as-oracle, 오도 주석)은 **긍정이 아니라 위험 벡터**다.

---

## Lens 1 — semantic-html-llm

**종합.** "시맨틱 HTML이 LLM에 늘 이롭다"는 명제는 **거짓**이다. 유일한 깨끗한 실증 대조는 *표현 형식* ablation(a11y-tree vs full-HTML)이며 승자가 **모델 역량에 따라 뒤집힌다**: 강한 모델은 fuller HTML에서 유리(WorkArena L1 +11~+17.5pp), 약한 모델은 compact a11y-tree가 우세(−7.9~−18.8pp). **`<nav>/<main>/<article>` 랜드마크·h1–h6 계층·`<button>` vs `<div onclick>`·`label/for`를 treatment로 격리해 LLM 이해 델타를 잰 연구는 존재하지 않는다** — 실재하는 evidence gap이다. a11y tree는 role+name+state+hierarchy의 더 작은 canonical subset으로서 web-agent 벤치마크가 LLM에 먹이는 *substrate*이지, 저자가 더 많은 시맨틱 마크업을 *쓰면* 이해가 오른다는 개입 근거가 아니다.

| Title | Authors / Year | arXiv / 출처 | Finding + numbers | Subjects | Tag |
|---|---|---|---|---|---|
| Read More, Think More: Revisiting Observation Reduction for Web Agents | Enomoto, Obara, Zhang, Oyamada 2026 | arXiv:2604.01535 | **조건부 승자**: 강한 모델 full-HTML 유리, 약한 모델 a11y-tree 유리. thinking-token budget이 HTML 이득을 증폭; 강한 모델은 layout/구조(CSS z-index) 활용해 grounding, 약한 모델은 긴 입력에서 element hallucination | web-agent / LLM | [CONFIRMED-read] |
| (동상, WorkArena L1 per-model) | 〃 | arXiv:2604.01535 Table 1 | a11y→HTML 성공률: Claude Sonnet 4.6 52.4→67.0 (**+14.6pp**); GPT-5.1(high) 55.8→73.3 (**+17.5pp**); Gemini-2.5-flash 45.5→56.7 (**+11.2pp**); **GPT-OSS-120B 46.7→38.8 (−7.9pp, a11y 승)**; **GPT-OSS-20B 46.4→27.6 (−18.8pp)**; **Llama-3.1-70B 18.2→3.6 (−14.6pp)** | web-agent | [CONFIRMED-read] |
| (동일 저자군의 companion) | Enomoto et al. 2026 | arXiv:2605.29397 | 도메인 의존: WebLinx는 text-content ablation −59.5% coverage; WorkArena L1은 `id` −16.9%, `class` −10.2%. 프로그램적 축소(GEPA) 2.2× 빠른 step에 84% 성공(WorkArena)/3.1×에 89%(WebLinx). **"보편적 승자 없음"** | web-agent | [CONFIRMED-read] |
| Understanding HTML with Large Language Models | Gur, Nachum, Miao, … Faust (Google) 2022/2023 | arXiv:2210.03945 | fine-tuning이 HTML element 시맨틱 분류 **+12%**; MiniWoB 내비게이션 **+50% 완료를 192× 적은 데이터**로. 단 "semantic vs div-soup" 대조가 아니라 *HTML 상의 task 성능* | LLM / web-agent | [CONFIRMED-read; 2022 T5-era] |
| WebArena: A Realistic Web Environment | Zhou, Xu, … Neubig 2023 | arXiv:2307.13854 | a11y tree를 element-targeting/observation space로 사용 — "시맨틱 구조 = agent에 주어지는 substrate"의 grounding fact | web-agent | [CONFIRMED-read 존재; per-modality 수치 unverified] |
| First Rule of ARIA / 네이티브 우선 | W3C WAI · MDN | 표준 | 네이티브 시맨틱 요소가 존재하면 ARIA로 덧대지 말라. LLM 측정이 아니라 정규 표준 | production / standard | [ESTABLISHED] |

**반증 / caveat.**
- **역량 게이트.** 테스트된 6개 모델 중 3개는 compact a11y-tree가 fuller HTML을 7.9~18.8pp *이겼다*(arXiv:2604.01535). "시맨틱 디테일이 많을수록 좋다"는 monotonic하지 않다.
- **격리 연구 부재.** 모든 대조는 *표현 형식*(a11y-tree vs DOM)이나 *축소 전략*이지, 랜드마크·heading-vs-div ablation이 아니다. **`<button>` vs `<div onclick>`를 토글해 LLM 이해 델타를 잰 직접 연구는 없다.**
- **삼각검증 아님(교정 #4).** arXiv:2604.01535와 2605.29397은 **동일 저자군(Enomoto et al.)의 한 research line**이며 companion 논문이다 — 독립적 제3자 삼각검증이 아니다. cross-source 교차확인의 인상을 주면 안 된다.
- **DOM 배수 삭제(교정 #3).** "a11y tree ≈ DOM의 ~10×축소" 수치는 인용된 2605.29397이 *실제로 명시하지 않는다*(그 논문은 "more compact representation"이라고만 함). ~10×는 web-agent 문헌의 folklore이며 **인용 근거 없음 → 삭제**. "role+name+state+hierarchy의 더 작은 canonical subset"만 유지한다.
- **비용 곡선.** fuller HTML은 토큰 비용을 올리고 약한 모델에서 hallucination을 유발("not-found" element 급증)한다 — 구조 풍부함은 monotonic 이득이 아니다.
- **연대 caveat.** 2210.03945는 2022 T5급 모델 — 2025–26 frontier로의 전이 보장 없음.

**루브릭 결론.** 시맨틱 HTML/a11y 구조를 **낮은 가중·report-only·C-tier 휴리스틱, confidence WEAK–MEDIUM**으로 채점하라. 이득은 (a) 역량 조건부이고 (b) ARIA/role의 *존재* ≠ 정확성이므로, **validity check 없이 마크업 존재에 점수를 주지 말 것**. 격리 연구 부재를 제품에 명시하라.

---

## Lens 2 — aria-wcag-machine-semantics

**종합.** a11y tree는 LLM web/GUI 에이전트의 **관측 공간**(관용·observation format)이라 BENEFIT은 **WEAK**다 — "저자가 ARIA/WCAG 준수를 더하면 AI 에이전트 이해가 오른다"는 개입 근거는 없다. 반면 RISK 측은 **STRONG**이다: 더 많은 ARIA는 더 많은 탐지 오류와 상관(단 correlation≠causation), bad ARIA는 no ARIA보다 나쁘고, WCAG의 ~25~40%만 자동검사 가능하며, 자동/LLM 생성 ARIA·alt 텍스트와 overlay는 실증된 harm/Goodhart 벡터다.

| Title | Authors / Year | arXiv / 출처 | Finding + numbers | Subjects | Tag |
|---|---|---|---|---|---|
| AgentOccam | Yang, Liu, Chaudhary, Fakoor et al. (Amazon/UPenn) 2024 | arXiv:2410.13825 | "web page content is represented in HTML or accessibility tree format in most text-only web agents" — a11y tree = 표준 텍스트 관측 형식 | web-agent / LLM | [CONFIRMED-read] |
| LUMOS: Semantic OS Layer for Accessibility-Grounded AI Agents | Thota (UT Dallas) 2026 | arXiv:2606.30697 | OS/브라우저의 네이티브 a11y 메타데이터(roles/names/values/bounds/affordances)를 agent perception으로 재활용. 연구 단계 프로토타입, 실증 검증 없음 | web-agent / LLM | [PLAUSIBLE-sourced (research-stage)] |
| WebCanvas / LineRetriever | 2024 / 2025 | arXiv:2406.12373 · 2507.00210 | a11y tree는 "redundant"라 tag/visibility/text로 필터링해야 하고 context limit을 자주 초과 — 유용하나 noisy | web-agent / LLM | [PLAUSIBLE-sourced] |
| Using ARIA §Rule 1 / "No ARIA is better than bad ARIA" | W3C · MDN | 표준 | 네이티브 시맨틱 우선; ARIA 사용 시 브라우저 동작을 script로 mimic할 책임. 잘못된 ARIA는 "more harm than good", 네이티브 시맨틱을 덮어씀 | human / production | [ESTABLISHED (normative)] |
| WebAIM Million (연도별 census) | WebAIM | webaim.org/projects/million | **방향성**: ARIA 사용 페이지가 미사용 페이지보다 탐지 오류가 지속적으로 더 많음. WebAIM 자체 caveat(verbatim): "does **not necessarily mean** that ARIA introduced these errors (these pages are more complex)" | production (1M 페이지) | [CONFIRMED-read 방향성] |
| WCAG 자동검사 가능 비율 | Groves 2012 · Yoong via Roselli 2023 | adrianroselli.com | WCAG의 "a quarter to a third"만 machine-testable; 자동 도구 "100%"조차 인간 개입 전 **~57% 천장**. WebAIM Million은 50개 WCAG 2.1 AA SC 중 ~16개만 자동탐지 사용 | production / human | [PLAUSIBLE-sourced] |
| Overlay harm | NFB 2021 · UIUC 2023 overlay study · FTC accessiBe | 2차/advocacy | 자동 ARIA remediation overlay가 conflicting ARIA 주입·focus order/DOM 파괴·AT 설정 override → screen-reader 사용자에 실질 harm, 법적 보호 없음 | production / human | [PLAUSIBLE-sourced (2차)] |

**효과 수치 (연도 명시·교정 #5).**
- **고정 배수를 쓰지 말 것.** 2025 snapshot: ARIA 有 페이지 평균 **57** vs 無 **27** 오류. 2026 snapshot: **59.1 vs 42.0**(~**+40%**, "두 배"가 **아님**). headline 배수는 연도마다 불안정하다(MDN "41% more", 2024 "34.2% more", 2025 "over twice"). **오직 방향성**("ARIA가 많을수록 탐지 오류가 많다")으로만, 연도와 함께 인용하라. **correlation≠causation** — WebAIM 자신이 ARIA-heavy 페이지는 더 복잡하다고 경고한다.
- Roselli 단일 페이지 사례: 수동 리뷰 37 failures(18 SC) vs 최선 자동 도구 소수 — 방향성 "수동이 최선 도구의 여러 배"는 안전, 정확한 개별 카운트는 [UNVERIFIED].
- **LLM alt-text/ARIA 정확도**: 신뢰할 만한 정량 hallucination 율 없음. GPT-4V system card는 "did hallucinate… inaccurate information" 인정(정성적). "machine-generated a11y is X% wrong"은 이 pass에서 **정량 미확보** → 정성적으로만.

**반증 / caveat.**
- **bad ARIA > no ARIA.** "ARIA 볼륨/마크업 밀도가 높다"를 긍정으로 채점하면 *알려진 위험 벡터를 보상*한다(WebAIM: ARIA↑ ⇒ 오류↑).
- **자동 도구는 심각한 false negative**(60~70%+ miss)와 false positive를 낸다. 깨끗한 axe/Lighthouse run은 천장이 아니라 바닥이며, ≈WCAG의 싼 ~30%만 잰다.
- **Goodhart 구체 사례.** overlay는 자동 점수/compliance 배지 metric을 최적화하면서 실제 목표(사용 가능한 시맨틱)를 악화시킨다. "a11y 준수"를 AI-legibility proxy로 채점하면 동일 gaming을 초대한다.

**루브릭 결론.** a11y-tree 품질을 **WEAK·낮은 가중·대부분 report-only**로 재라. **ARIA/마크업 *볼륨*에 결코 보상하지 말 것**(WebAIM 역상관), 자동 a11y 점수를 ground truth로 신뢰하지 말 것(WCAG의 ~25~40%만 machine-checkable), 자동/LLM 생성 ARIA·alt를 긍정이 아니라 Goodhart/harm 벡터로 flag하라 — risk에 MEDIUM, benefit에 WEAK.

---

## Lens 3 — test-descriptions-context

**종합 (핵심 비대칭).** **올바르거나 누락된 문서는 LLM 코드 이해에 유의한 이득을 주지 않는다 — 오직 오도 문서만 측정 가능하게 해롭다**(arXiv:2404.03114, 저자 자신의 가설을 반증). tests-as-oracle은 exploitable하다: LLM 패치는 제공된 테스트에 과적합해 버그를 초록으로 굳힌다(overfitting; arXiv:2511.16858). LLM 오라클은 expected(명세)가 아니라 actual(구현) 동작을 인코딩한다(arXiv:2410.21136). 서술적 테스트 이름은 의도를 인코딩하지만 **컴파일러가 검증하지 않아** 이름↔본문 괴리로 흐른다.

| Title | Authors / Year | arXiv / 출처 | Finding + numbers | Subjects | Tag |
|---|---|---|---|---|---|
| Testing the Effect of Code Documentation on LLM Code Understanding | Macke & Doyle 2024 | arXiv:2404.03114 | verbatim: "incorrect documentation can greatly hinder code understanding, **while incomplete or missing documentation does not seem to significantly affect** an LLM's ability to understand code." 오도 주석 = 테스트된 최악 조건, α=0.05 유의. 오도 "animal" 변수명 작은-유의 하락(GPT-3.5 44.7→40.6; GPT-4 78.5→76.6) | LLM | [CONFIRMED-read 방향성; 세부 % analyst-reported] |
| Investigating Test Overfitting on SWE-bench | Ahmed, Ganhotra, Shinnar, Hirzel 2025 | arXiv:2511.16858 | tests-as-oracle 과적합 실재: 패치가 visible 테스트를 통과하되 held-out/black-box에서 실패("green-locks-bug"). **구체 수치(21.8%/33.0% 등)는 결과 표 미검증 → 방향성만**: refining against tests가 overfitting을 **악화**시키고, black-box 테스트 공개가 이를 **감소**시킨다 | LLM | [CONFIRMED-read 방향성; 수치 UNVERIFIED] |
| Do LLMs generate test oracles that capture actual or expected behaviour? | Konstantinou, Degiovanni, Papadakis 2024 | arXiv:2410.21136 | LLM 오라클은 "the **actual** program behaviour rather than the expected one"을 포착; buggy 코드에서 정확도 8.4~9.5% 하락. 의미 있는 변수/테스트 이름 +16.10%; Evosuite-식 자동 이름은 심하게 열화 | LLM | [CONFIRMED-read] |
| LLMs Gaming Verifiers (RLVR) | Helff, Delfosse, Steinmann et al. 2026 | arXiv:2604.15149 | 모델이 규칙 학습 대신 extensional/불완전 verifier를 shortcut으로 만족; Isomorphic Perturbation Testing이 fix. tests-as-oracle Goodhart의 정성적 corroboration | LLM | [CONFIRMED-read thesis] |
| Acceptance Test Generation with LLMs: Industrial Case Study | Ferreira, Viegas, Faria, Lima 2025 | arXiv:2504.07244 | BDD/Gherkin 인수 시나리오가 실무에서 spec으로 usable(AutoUAT **95% helpful**), 누락 요구를 표면화 — 단 품질은 입력 명료성에 bounded. "8/10 quality"·인과 진술은 [UNVERIFIED] | LLM + human (PO) | [CONFIRMED-read helpful-rate; 세부 UNVERIFIED] |
| Descriptive test names encode intent (name↔body drift) | McGill 2025 EMSE · Daka et al. ISSTA 2017 | 2차/snippet | 서술적 이름은 unit-under-test/feature/expected를 인코딩해 본문 없이 이해 가능 — 그러나 **컴파일러 미검증**이라 이름/본문 불일치로 drift | human (pre-LLM) | [PLAUSIBLE-sourced] |

**반증 / caveat.**
- **올바른 문서는 입증된 comprehension 레버가 아니다.** 유일한 직접 통제 연구가 완전/정확 주석의 유의 이득을 못 찾았다(2404.03114). 문서의 *측정된* 효과는 상방 이득이 아니라 **하방 위험**(오도 문서가 해롭다)이다.
- **tests-as-doc/oracle이 버그를 굳힌다.** 테스트를 LLM이 최적화하는 spec으로 쓰면 silently-incorrect 코드를 낳고, 테스트 신호로 반복하면 악화된다(2511.16858 — 방향성). 서술적-이름/오라클 Goodhart의 구체화.
- **이름↔본문 괴리는 컴파일러 미검증 실패 모드**다. 서술적 이름은 본문이 구현 안 할 수도 있는 의도를 주장하고, 이를 신뢰하는 LLM은 그 거짓을 상속한다.
- **자동 생성 NL spec/오라클은 부정확**하고 입력 context가 얇으면 Gherkin 품질이 붕괴한다(2504.07244).
- **스코프 caveat.** 2404.03114는 단일 proxy task(HumanEval 164 짧은 함수의 test-pass)라 좁고 작음 — 대형 repo 이해로 일반화 보장 없음.

**루브릭 결론.** 서술적 테스트 이름 / GWT-BDD / tests-as-doc를 **weak-positive·report-only legibility 신호**로 다루고 점수화된 comprehension 배수로 쓰지 말 것. 어떤 credit도 **괴리/정확성 체크**(name↔body, comment↔code)와 짝지어라 — 지배적 실증 위험은 *누락*이 아니라 *오도 설명과 oracle-gaming*이다. confidence MEDIUM(전반), STRONG(반증).

---

## Lens 4 — accessible-test-selectors

**종합.** `getByRole` > `data-testid` 선호는 **vendor-idiomatic STRONG**(refactor-robust): 정규 vendor 문서(Testing Library, Playwright)와 2026 robustness 논문이 시맨틱/접근성 셀렉터가 마크업 churn에 더 강함에 수렴한다. 그러나 "접근성 체크를 겸한다(doubles as a11y check)"는 **WEAK**(`getByRole`가 초록이어도 a11y가 깨질 수 있고 axe 대체가 아님), "AI 이해를 향상"은 **ABSENT**(관용적 추론). 기계적으로 탐지 가능하다(`getByRole/getByLabelText/getByText` vs `getByTestId/CSS/xpath`).

| Title | Authors / Year | arXiv / 출처 | Finding + numbers | Subjects | Tag |
|---|---|---|---|---|---|
| About Queries (우선순위) | Testing Library docs | testing-library.com | 원칙: "test should resemble how users interact"; 우선순위 `getByRole` > LabelText > PlaceholderText > Text > DisplayValue > AltText/Title > **TestId(최후)**. getByRole는 "every element exposed in the accessibility tree"를 쿼리 | human | [ESTABLISHED (verbatim 확인)] |
| Locators | Playwright docs | playwright.dev/docs/locators | "prioritizing user-facing attributes and explicit contracts such as `page.getByRole()`"; role locator는 "reflect how users and assistive technology perceive the page"; `getByTestId` 7개 중 최후 | human / production | [ESTABLISHED (verbatim 확인)] |
| Test IDs are an a11y smell | Dorfmeister (tkdodo.eu) | blog | `data-testid`는 "not part of the accessibility tree and add no semantic value"; 개발자가 모르게 inaccessible 마크업 출시 가능. 단 getByRole는 "axe 같은 전용 a11y 테스트를 대체하지 않는다" | human / production | [ESTABLISHED (실무 정전)] |
| Why I rarely use getByRole | Noonan (dev.to) | blog | "accessible component를 완전히 깨뜨려도 getByRole 초록 테스트를 유지할 수 있다." `<div role="button">`는 getByRole 통과하나 키보드 활성화/tab order/focus/pressed 상실. getByRole는 `selector` 옵션이 없어 실제 `<button>`임을 강제 못 함 | human / production | [ESTABLISHED (반증 정전)] |
| Beyond LLM-based test automation: Zero-Cost Self-Healing via DOM A11y Tree | Joseph 2026 | arXiv:2603.20358 | 10-tier locator 계층에 `get_by_role`를 **1순위**(W3C 표준·가장 시맨틱 robust). 31/31(100%) pass, 22s 병렬, stale 셀렉터 <1s 재발견. **단 healing robustness 측정이지 AI용 test-code 가독성 아님·tiny N** | production / web-agent | [CONFIRMED-read] |
| Enhancing Web Agents with a Hierarchical Memory Tree | Tan, Gao, Wu 2026 | arXiv:2603.07024 | 액션 수준 "transferable semantic element descriptions(role/label/상대위치/구조 context)"를 site-specific id 대신 저장; Mind2Web+WebArena 검증. **앱의 런타임 a11y tree 관측이지 test-code 아님** | LLM / web-agent | [CONFIRMED-read (교정 #7: 실재 확인, 기존 "unreadable/unverified" hedge 철회)] |
| Prune4Web / LUMOS | Zhang et al. 2026 · Thota 2026 | arXiv:2511.21398 · 2606.30697 | Prune4Web: 시맨틱 DOM 필터링이 sub-task grounding 46.8→88.28%. 모두 **앱 런타임 a11y tree grounding**이지 test authoring 아님 — 인접 근거 | LLM / web-agent | [PLAUSIBLE-sourced] |

**반증 / caveat.**
- **getByRole 초록 ≠ a11y 온전.** role은 부분 계약이다 — `<div role="button">`이 getByRole를 통과하되 키보드/focus/pressed/고대비를 잃는다. getByRole 기반 테스트는 *거짓* a11y 신뢰를 주며 axe 대체가 아니다(Testing Library 옹호자도 인정).
- **취약성은 양방향.** getByRole는 정확한 accessible-name 계산에 의존해 ARIA/label 변경에 깨지고 getByTestId보다 느릴 수 있다. data-testid는 text/role 변경에 가장 resilient — 안정성과 시맨틱 충실도가 긴장 관계다.
- **AI-comprehension 논지의 결정적 공백.** 접근성 기반 테스트 *코드*가 LLM의 UI 의도 이해에 더 나은 context 신호인지 실증한 출처는 **없다**. 모든 agent/LLM 근거(2603.20358, 2603.07024, 2606.30697, 2511.21398)는 *앱의 런타임 a11y tree* grounding — test source와 다른 artifact다. 전이는 관용적 추론이지 측정이 아니다.
- **자동 생성 caveat.** self-healing/AI locator 도구가 조용히 다른 스코프 element로 재작성할 수 있어, role-preserving heal이 실제 기능 회귀를 가릴 수 있다.

**루브릭 결론.** **낮은 가중·기계 탐지 가능·report-only 시맨틱-품질 신호**로 채점하라: role/label/text 셀렉터를 CSS/xpath/data-testid보다 선호(카운트 가능). confidence — "more robust/semantic"에 MEDIUM(vendor + 2026 robustness 1편), "doubles as a11y check"에 WEAK(getByRole 초록이어도 a11y 깨질 수 있음·axe 아님), "better AI context signal"에 **ABSENT/추론뿐**. agent-grounding 논문을 test-code-가독성 근거로 오귀속하지 말 것.

---

## Lens 5 — measurement-validity-goodhart

**종합.** 이 문서 전체에서 **명명/의미단서 채널만이 직접 causal 열화 근거**를 가진다: semantic-preserving mutation이 debugging을 78% 열화(arXiv:2504.04372). **functional-pass ≠ 품질/보안**은 이제 STRONG이다(arXiv:2508.14727, Pass@1과 품질/보안 사이 상관 *없음*을 명시). LLM 오라클은 expected가 아니라 actual을 인코딩한다(2410.21136). **자동 생성이 core Goodhart trap**이다 — 자동 식별자/주석/테스트-이름/ARIA/alt가 정확히 LLM 추론을 열화시키는 것이라, "존재"에 보상하는 루브릭은 저품질 auto-fill로 만족되어 상황을 *악화*시킨다. "measurable ≠ valid predictor".

| Title | Authors / Year | arXiv / 출처 | Finding + numbers | Subjects | Tag |
|---|---|---|---|---|---|
| **Assessing the Impact of Code Changes on the Fault Localizability of LLMs** | **Haroon, Khan, Humayun, Gill, Amjad, Butt, Khan, Gulzar 2025** | **arXiv:2504.04372** | semantic-preserving mutation(SPM)이 이전에 localized된 fault에 대해 **78%** 케이스에서 LLM을 실패시킴(교정 #1: 81% 아님). 규모 **750,013 tasks·1,300+ programs·10 LLMs**. position bias(관련 코드가 앞에 있을 때 추론 강함) → LLM 이해는 부분적으로 lexical/표면적 | LLM | [CONFIRMED-read] |
| Assessing the Quality and Security of AI-Generated Code | Sabra, Schmitt, Tyler 2025 | arXiv:2508.14727 | verbatim: **"no direct correlation between a model's functional performance (Pass@1) and the overall quality and security of its generated code."** 4,442 Java tasks(SonarQube), 통과 코드에도 hard-coded password·path traversal·code smell (교정 #6: MEDIUM→**STRONG**) | LLM | [CONFIRMED-read] |
| Do LLMs generate test oracles… actual or expected? | Konstantinou, Degiovanni, Papadakis 2024 | arXiv:2410.21136 | 오라클이 actual behaviour 인코딩; correct-code/correct-assertion 분류 40.77~46.26%, wrong-code 31.94~37.01%(−8.4~9.5%); 의미 있는 이름 +16.10%; Evosuite 자동 이름 열화. "<50% 분류 = 모든 제안이 인간 검수 필요" | LLM | [CONFIRMED-read] |
| Measuring how readability attributes affect LLM code-quality evaluation | Simoes & Venson 2025 | arXiv:2507.05289 | 9 LLM이 comment 제거/식별자 난독/smell refactor에 민감("all LLMs were sensitive"), oscillation 9.37~14.58%; 단 smell-refactor는 "high agreement for original and refactored" — **개입 효과 약함/비대칭** | LLM | [CONFIRMED-read] |
| a11y 자동검사 커버리지 (실증) | gov.uk 2017 · alphagov | accessibility.blog.gov.uk | 143 barrier 페이지: 전 도구 collective 71% 탐지, **42개(29%)는 모든 도구가 miss**; 최선 단일 41%(Asqatasun), Tenon 37%, Google DevTools 17% — 24pt 스프레드 | web-agent / human | [CONFIRMED-read] |
| 자동 도구는 conformance 판정 불가 | W3C WAI | 표준 | 자동 도구는 "can only assist", "cannot check all", "can produce false or misleading results" — 단일 도구 점수는 valid conformance proxy 아님 | production / human | [ESTABLISHED] |
| Benchmarks don't predict production | Blaxel blog · survey 2508.00083 | 2차 | 정적 코드-품질 metric이 task success와 상관하나 real-world(production) agent 성능 예측자로 검증 안 됨 | LLM / production | [PLAUSIBLE-sourced (illustrative)] |

**반증 / caveat.**
- **자동 생성 부정확이 세 신호(시맨틱/a11y/테스트-설명)의 core Goodhart trap.** 마크업/주석/테스트-설명 *존재*에 보상하면 저품질 auto-fill(자동 ARIA/alt, 자동 주석, tautological assertion)로 만족되어 comprehension을 악화시킨다.
- **개입 근거만 causal — 나머지는 추론.** 통제 난독화에서 강한 causal 열화를 보인 채널은 **명명/의미단서**(2504.04372)뿐이다. smell-refactor 개입은 "high agreement"(변화 미미; 2507.05289)로 확인됨 → 세 신호 중 명명만 직접 causal backing을 가진다; 시맨틱-HTML-as-comprehension·a11y-as-comprehension은 추론이다.
- **RAISING a score → agent success는 미입증.** 정적 a11y/테스트-설명 점수를 *올리는 것*이 LLM/에이전트 task success를 올린다는 출처는 하나도 없다 — production-prediction gap은 명시적이다. correlation ≠ intervention은 이 신호들에서 여전히 미연결.

**루브릭 결론.** 시맨틱-마크업·접근성·테스트-설명 품질을 **낮은 가중·report-only 진단 신호(census/presence)**로 다루고 certified AI-readiness 예측자로 쓰지 말 것: 명명/의미단서 채널만 직접 causal 근거가 있고, a11y 자동화는 이슈의 ~17~71%만 커버하며, 테스트 "품질"은 actual-not-expected 동작을 green-lock할 수 있다. **자동 생성 마크업/주석/테스트-이름에 결코 점수 주지 말고**, metric 달성(함수 분할·boilerplate 주석·tautological assertion)이 실제 comprehensibility를 열화시키는 Goodhart 실패를 명시적으로 가드하라.

---

## 적대적 감사 결과 (교정 1~7 반영)

5회 검증 패스가 감사한 결과다. 모든 arXiv ID는 실재하는 논문으로 resolve됐고 **날조/환각 ID는 0개**다. 아래 라벨은 각 신호가 점수화 주장에서 어떤 지위를 갖는지 확정한다.

### VERIFIED-CLEAN
- **arXiv:2604.01535** ("Read More, Think More…", Enomoto et al. 2026) — 6개 per-model WorkArena L1 수치 전부 Table 1과 정확 일치.
- **arXiv:2210.03945 · 2307.13854** — 제목/저자/연도 및 +12%/+50%/192× 확인.
- **arXiv:2410.13825**(AgentOccam) · **2606.30697**(LUMOS) · **2507.00210**(LineRetriever) — 실재, a11y-tree=관측 형식 지지.
- **arXiv:2508.14727** (교정 #6) — 실재, **STRONG으로 승급**: Pass@1과 품질/보안 사이 **상관 없음**을 명시.
- **arXiv:2410.21136 · 2507.05289** — 오라클=actual 동작, 가독성 개입=약함/비대칭 확인.
- **arXiv:2404.03114 · 2504.07244 · 2604.15149** — 오도 문서 해악·95% helpful·RLVR gaming 확인.
- **getByRole 계열 전부**(교정 #7): Testing Library·Playwright docs verbatim; **arXiv:2603.20358**(Joseph, 100% pass·<1s heal) · **2603.07024 = "Enhancing Web Agents with a Hierarchical Memory Tree"**(Tan/Gao/Wu, 실재 확인 — 기존 "unreadable/unverified" hedge **철회**) · **2511.21398**(Prune4Web 46.8→88.28%) 확인.
- **gov.uk a11y 커버리지**(143 barrier·29% miss·collective 71%) — 산술 일치.

### DOWNGRADED
- **arXiv:2504.04372**(교정 #1) — 제목이 틀렸었다. 실제 = **"Assessing the Impact of Code Changes on the Fault Localizability of Large Language Models"**(Haroon et al. 2025). 수치 교정: **78%**(81% 아님), **750,013 tasks·1,300+ programs·10 LLMs**. 논지·수치는 이 실재 논문에서 검증됨(causal 열화 STRONG 유지).
- **arXiv:2511.16858**(교정 #2) — 제목이 틀렸었다. 실제 = **"Investigating Test Overfitting on SWE-bench"**(Ahmed, Ganhotra, Shinnar, Hirzel 2025). 구체 overfitting % (21.8%/33.0% 등)는 결과 표 미검증 → **방향성만**(refining worsens overfitting; black-box tests reduce it). 정성적 finding 유지, confidence STRONG→MEDIUM.
- **WebAIM 배수**(교정 #5) — "57 vs 27 / over twice"는 2025 연도-특정. 2026은 59.1 vs 42.0(~+40%). **고정 배수 금지 → 방향성 + 연도**로만, correlation≠causation caveat 동반.
- **Gherkin "8/10 quality" · 인과 진술** — 초록 미확인 → [UNVERIFIED]. helpful-rate(95%)만 solid.

### REFUTED / DROPPED (uncited·폐기)
- **잘못된 논문 제목 2건**: "How Accurately Do LLMs Understand Code?"(2504.04372의 오제목)와 "Is the Cure Still Worse Than the Disease?…"(2511.16858의 오제목) — **둘 다 폐기**, 재현 금지.
- **"81%"** mutation-fragility 수치와 **"~575,000 tasks / 670 Java+637 Python / 9 LLMs"** — 폐기, 78% / 750,013 / 1,300+ / 10 LLMs로 대체.
- **"a11y tree ≈ DOM의 ~10× 축소"**(교정 #3) — 인용된 2605.29397이 명시하지 않는 folklore → **폐기**. "role+name+state+hierarchy의 더 작은 canonical subset"만 유지.
- **고정 ARIA 배수**("두 배"/57-vs-27을 불변 효과로) — 폐기(위 DOWNGRADED 참조).

### UNVERIFIABLE (fact로 취급 금지)
- **동일 저자군 caveat**(교정 #4): 2604.01535와 2605.29397은 Enomoto et al.의 **한 research line·companion**이지 독립 삼각검증이 아니다 — cross-source 교차확인으로 제시 금지.
- **causal transfer 공백**: "접근성 테스트 셀렉터 → 더 나은 AI UI-의도 이해"는 진짜 미측정 — verification 실패가 아니라 evidence gap. REPORT-ONLY 유지.
- **litigation "22.6% overlay"** · **UIUC 2023 overlay study · NFB 2021 · FTC accessiBe** · **"Ramadan et al." ~100-tool 리뷰** · **WebCanvas(2406.12373)** — 2차/미재확인, non-load-bearing.
- **LLM alt-text/ARIA hallucination 율** — 정성적으로만, 방어 가능한 % 없음.

---

## 본 하네스가 채택한 결론 (score.py Tier C 매핑)

세 신호는 모두 **report-only(총점 100 미합산)**다 — 자매 문서 §0.4의 지배 단서(개입 연구 없음)와 Lens 5의 자동-생성 Goodhart trap을 그대로 상속한다. `score.py`는 census/presence와 명백한 결함만 결정론적으로 재고, 등급·가점은 만들지 않는다.

### C1 — Semantic Markup (시맨틱 마크업)
- **(a) 결정론 측정 가능**: 네이티브 시맨틱 요소 사용 census(`<button>/<nav>/<main>/<article>/<label for>` 등), 네이티브 대체 가능한 `role=` 속성(예: `<div role="button">`)의 결함 후보 flag, ARIA 속성 볼륨(가점 아님·**정보 표시만**).
- **(b) report-only 권고**: 네이티브 시맨틱을 측정하되 **ARIA 볼륨에 가점 금지**(WebAIM 역상관). 네이티브로 대체 가능한 `role=`은 결함 후보로 표시. **자동 ARIA/alt 생성 금지**(자동 생성 = Goodhart trap·harm 벡터).
- **(c) confidence**: benefit WEAK(역량 조건부·격리 연구 부재), risk MEDIUM(bad ARIA > no ARIA).
- **(d) Goodhart 가드**: 마크업/ARIA *존재·볼륨*에 결코 보상하지 말 것 — validity check 없는 마크업 존재는 위험 벡터일 수 있다. presence ≠ correctness.

### C2 — Test Legibility (테스트 가독성)
- **(a) 결정론 측정 가능**: 모호/오도 테스트 제목 census, accessible selector census(`getByRole/getByLabelText/getByText` vs `getByTestId/CSS/xpath` 카운트), 이름↔본문 괴리 후보(휴리스틱).
- **(b) report-only 권고**: 모호/오도 제목 = **삭제·리네임 후보**(오도 삭제만 위험 0·자매 문서 §Tier A). accessible selector는 report-only census. **자동 assertion/오라클 생성 금지**(tests-as-oracle가 버그를 green-lock; 오라클은 actual 인코딩).
- **(c) confidence**: 오도 제목 삭제 STRONG(2404.03114 비대칭); selector "more robust" MEDIUM; "doubles as a11y check" WEAK; "better AI context" ABSENT.
- **(d) Goodhart 가드**: 테스트를 개선 에이전트의 최적화 오라클로 닫지 말 것(refining worsens overfitting). 서술적 제목/셀렉터 *존재*를 comprehension 배수로 쓰지 말고, 항상 괴리/정확성 체크와 짝지어라.

**공통 불변식**: C1·C2는 **총점 미합산 report-only**이며, 코드 수정은 승인 게이트 뒤 오도/stale 삭제·명백히 오도하는 이름/제목 교정에 한정한다(자동 생성 일절 금지). 표면 편집을 에이전트 성공률·툴그래프 이득으로 오귀속 금지.

---

## 미해결 질문 / 추가로 필요한 근거

**핵심 공백 (제품에 반드시 명시):**
- **landmark-vs-divsoup 격리 실험 부재.** `<nav>/<main>/<article>` 랜드마크·h1–h6 계층·`<button>` vs `<div onclick>`·`label/for`를 treatment로 토글해 LLM 이해 델타를 잰 직접 연구가 **없다**. 모든 대조는 표현-형식 ablation(a11y-tree vs HTML)이며 승자가 역량에 따라 뒤집힌다.
- **test-code-selector → LLM 이해 개입 연구 부재.** 접근성 기반 테스트 *소스*가 LLM의 UI 의도 이해에 더 나은 context인지 실증한 연구가 없다. 모든 agent 근거는 *앱 런타임* a11y tree grounding(다른 artifact)이다.
- **ARIA/WCAG 준수 → agent 이해 개입 연구 부재.** a11y tree가 관측 공간이라는 관용은 있으나, 저자가 ARIA/WCAG를 더하면 에이전트 이해가 오른다는 개입 근거는 없다. BENEFIT은 WEAK.
- **tests-as-oracle overfitting 구체 수치 미검증.** arXiv:2511.16858의 % (21.8%/33.0% 등)는 결과 표 미확인 → 방향성만.
- **LLM 생성 ARIA/alt hallucination 정량 부재.** 정성적 증거만 있고 방어 가능한 % 없음.
- **동일 저자군 = 삼각검증 아님.** 시맨틱-HTML 렌즈의 핵심 두 논문(2604.01535·2605.29397)은 한 팀의 한 research line이라, 그 headline 효과 크기는 **잠정치**로 취급해야 한다.

**Dropped numbers (인용 금지):**
- "a11y tree ≈ DOM의 ~10× 축소" (인용 논문이 명시 안 함).
- 고정 ARIA 오류 배수("두 배"/57-vs-27을 불변으로) — 방향성+연도로만.
- "81%" mutation-fragility, "~575,000 tasks / 9 LLMs" — 78% / 750,013 / 10 LLMs로 대체.
- 잘못된 논문 제목 2건("How Accurately Do LLMs Understand Code?", "Is the Cure Still Worse Than the Disease?…").
- Gherkin "8/10 quality" 및 "품질=입력 명료성" 인과 진술.
