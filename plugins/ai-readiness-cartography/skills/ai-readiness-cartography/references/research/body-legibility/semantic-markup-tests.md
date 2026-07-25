# 시맨틱 마크업 · 테스트 설명 · comment-gap — 근거 dossier (E-MK · E-TL · E-CG)

> 이 축들은 **흡수된 자산**이다(구 `design-principle-harness` Tier C + comment-gap 탐지기, v0.5.0에서 이 플러그인 모드 ③로 통합).
> 자매 문서 [`naming.md`](./naming.md)·[`comments.md`](./comments.md)·[`structure.md`](./structure.md)와 동일한 SOURCE-TIER 규약·동일한 지배 단서를 상속한다.

## 0. 지배적 단서 — 이 문서를 읽는 법

### 0.1 두 축 채점 (자매 문서와 동일)

모든 신호는 직교하는 두 등급을 갖는다. 단일 confidence 수치는 *측정 정밀도*를 *타당도*로 새어 들어가게 하므로 정직하지 못하다.

- **측정 신뢰도** — 결정론적으로 셀 수 있는가? (`getByRole` vs `getByTestId` 카운트, `role=` census, 무-alt `<img>` = High. "이 alt가 정확한가", "이 ARIA가 UI를 옳게 기술하는가" = None.)
- **타당도(AI 가독성 예측)** — 이 문서의 **모든 신호에서 EXTRAPOLATED 또는 ABSENT다.** 어느 것도 "저장소의 시맨틱/테스트-설명 신호를 올리면 같은 에이전트의 성공률이 오른다"를 측정하지 않았다.

### 0.2 모든 것을 지배하는 발견 — perturbation/production ≠ intervention

> **시맨틱 HTML 랜드마크·heading 계층·`<button>` vs `<div onclick>`·ARIA·WCAG 준수·서술적 테스트 설명·접근성 기반 테스트 셀렉터 — 이 중 어느 것도, "그 신호를 *올리는 것*이 *동일* 저장소에서 *특정* LLM/에이전트의 코드 이해나 안전한 기여를 *개선*한다"를 측정한 통제 연구가 없다.**

근거는 세 종류뿐이고 어느 것도 intervention이 아니다 — **perturbation**(열화시키고 하락 관측) · **production**(AI가 *산출*하는 것의 오류율) · **observation-space/idiom**(a11y tree가 web-agent의 관측 공간이라는 사실, 벤더 문서의 권장 관용).

특히 다음 둘은 **관용·관측 형식의 사실이지 개입 근거가 아니다**: (1) a11y tree가 agent 관측 공간이라는 것 ≠ 저자가 ARIA를 더 쓰면 이해가 오른다, (2) `getByRole`가 refactor-robust하다는 것 ≠ 테스트 *소스 코드*를 LLM이 더 잘 읽는다. 전이는 **관용적 추론**이지 측정이 아니다.

---

## E-MK1 · 시맨틱 HTML의 이득은 모델 역량 조건부다 (격리 연구 부재)

- **판정**: report-only · 타당도 **EXTRAPOLATED**
- **핵심**: "시맨틱 HTML이 LLM에 늘 이롭다"는 **거짓**이다. 유일한 깨끗한 대조는 *표현 형식* ablation(a11y-tree vs full-HTML)이며 **승자가 모델 역량에 따라 뒤집힌다** — WorkArena L1에서 강한 모델은 full-HTML이 유리(Claude Sonnet 4.6 52.4→67.0 **+14.6pp** · GPT-5.1(high) 55.8→73.3 **+17.5pp** · Gemini-2.5-flash 45.5→56.7 **+11.2pp**), 약한 모델은 compact a11y-tree가 우세(GPT-OSS-120B **−7.9pp** · GPT-OSS-20B **−18.8pp** · Llama-3.1-70B **−14.6pp**).
- **출처**: arXiv:2604.01535 (Enomoto, Obara, Zhang, Oyamada 2026) `[PRIMARY-2025+ · 2026]` · companion arXiv:2605.29397.
- **결정적 공백**: **`<nav>/<main>/<article>` 랜드마크·h1–h6 계층·`<button>` vs `<div onclick>`·`label/for`를 treatment로 격리해 LLM 이해 델타를 잰 연구는 존재하지 않는다.** 실재하는 evidence gap이다.
- **caveat**: 2604.01535와 2605.29397은 **동일 저자군의 한 research line·companion**이지 독립 삼각검증이 아니다(cross-source 교차확인으로 제시 금지). 또 fuller HTML은 토큰 비용을 올리고 약한 모델에서 element hallucination을 유발한다 — 구조 풍부함은 **monotonic 이득이 아니다**.
- 🚫 **폐기된 수치**: "a11y tree ≈ DOM의 ~10× 축소"는 인용 논문이 명시하지 않는 folklore → 인용 금지. "role+name+state+hierarchy의 더 작은 canonical subset"만 유지.
- **하네스에서의 귀결**: `MK1_NONSEMANTIC_CLICK`은 **census 전용**이다(개입 카드 없음). 승격의 이득은 접근성·사람 사용성이지 AI 이해가 아니고, 접근성은 이 하네스의 표적이 아니므로 후보만 보여준다.

---

## E-MK2 · native 우선 — 잘못된 ARIA는 no-ARIA보다 나쁘다

- **판정**: 규범 표준(ESTABLISHED) · AI 이득은 **ABSENT**
- **핵심**: W3C/MDN 'First rule of ARIA' — native 시맨틱 요소가 존재하면 ARIA로 덧대지 말라. ARIA 사용 시 브라우저 동작을 script로 mimic할 책임이 생기고, 잘못된 ARIA는 "more harm than good"으로 native 시맨틱을 **덮어쓴다**. 무-alt `<img>`는 WCAG 위반이다.
- **출처**: W3C WAI `Using ARIA` §Rule 1 · MDN `[ESTABLISHED · normative]`.
- **하네스에서의 귀결**: `MK2_REDUNDANT_ROLE`·`MK3_IMG_MISSING_ALT`도 **census 전용**이다. 어느 경로에서도 **자동 ARIA/alt 생성은 금지** — 자동 remediation overlay가 conflicting ARIA 주입·focus order 파괴로 실제 harm을 낸 사례가 있고(NFB 2021·UIUC 2023 overlay study `[PLAUSIBLE-sourced · 2차]`), LLM alt/ARIA의 신뢰할 만한 정확도 수치는 확보되지 않았다(GPT-4V system card가 정성적으로 hallucination 인정).

---

## E-MK3 · ARIA '볼륨'은 어느 방향으로도 점수가 아니다

- **판정**: report-only · **가점 금지**(Goodhart 벡터)
- **핵심**: WebAIM Million census에서 **ARIA를 쓴 페이지가 안 쓴 페이지보다 탐지 오류가 지속적으로 더 많다**. 단 WebAIM 자신의 caveat(verbatim): "does **not necessarily mean** that ARIA introduced these errors (these pages are more complex)".
- **수치 취급**: 고정 배수를 쓰지 말 것 — 2025 snapshot은 ARIA 有 평균 **57** vs 無 **27** 오류, 2026 snapshot은 **59.1 vs 42.0**(~+40%, "두 배"가 **아님**). headline 배수가 연도마다 불안정하다 → **방향성만, 연도와 함께, correlation≠causation과 함께** 인용한다.
- **보강**: WCAG의 "a quarter to a third"만 machine-testable이고, 자동 도구 "100%"조차 사람 개입 전 **~57% 천장**이다 `[PLAUSIBLE-sourced]`. 깨끗한 axe/Lighthouse run은 천장이 아니라 바닥이다.
- **하네스에서의 귀결**: `MK4_ARIA_VOLUME`은 **census 전용**이고 개입 후보로 승격하지 않는다. ARIA를 *늘리는* 개입은 제안하지 않는다 — 볼륨에 보상하는 루브릭은 알려진 위험 벡터를 보상하는 것이다.

---

## E-TL1 · 비대칭 — 올바른 설명은 이득이 미미하고, 오도 설명만 해롭다

- **판정**: report-only · 반증 방향은 **STRONG**
- **핵심(verbatim)**: "incorrect documentation can greatly hinder code understanding, **while incomplete or missing documentation does not seem to significantly affect** an LLM's ability to understand code." 오도 주석이 테스트된 최악 조건(α=0.05 유의)이었다.
- **출처**: arXiv:2404.03114 (Macke & Doyle 2024) `[PRIMARY-pre2025 · 배경]`.
- **caveat**: 단일 proxy task(HumanEval 164개 짧은 함수의 test-pass)라 **좁고 작다** — 대형 repo 이해로의 일반화는 보장되지 않는다.
- **보강(이름↔본문 괴리)**: 서술적 테스트 이름은 unit-under-test/기대결과를 인코딩하지만 **컴파일러가 검증하지 않아** 본문과 어긋난 채 표류한다(McGill 2025 EMSE · Daka et al. ISSTA 2017 `[PLAUSIBLE-sourced]`). 이를 신뢰하는 LLM은 그 거짓을 상속한다.
- **tests-as-oracle 위험**: LLM 패치는 제공된 테스트에 과적합해 버그를 초록으로 굳힌다(green-locks-bug; arXiv:2511.16858 *Investigating Test Overfitting on SWE-bench*, Ahmed et al. 2025 — **구체 %는 미검증, 방향성만**: refining against tests가 overfitting을 악화시키고 black-box 테스트 공개가 감소시킨다). LLM 오라클은 expected(명세)가 아니라 **actual(구현) 동작을 인코딩**한다(arXiv:2410.21136).
- **하네스에서의 귀결**: `TL1_VAGUE_TEST_TITLE`은 **census 전용**이다. 올바른 설명의 이득이 미미하고 오도만 해로운 비대칭이라 '설명 늘리기' 개입은 애초에 만들지 않으며, **자동 어서션·오라클 생성은 금지**다.

---

## E-TL2 · 접근성 셀렉터는 벤더 관용이지 AI 이해 근거가 아니다

- **판정**: report-only · "refactor-robust" **MEDIUM(vendor idiom)** / "AI 이해 향상" **ABSENT**
- **핵심**: Testing Library·Playwright 정규 문서가 `getByRole` > LabelText > Text > … > **TestId(최후)** 우선순위에 수렴한다 `[ESTABLISHED]`. self-healing 연구도 `get_by_role`를 10-tier 중 1순위로 둔다(arXiv:2603.20358 — 단 **healing robustness 측정이지 test-code 가독성이 아니고 N이 작다**).
- **반증**: **getByRole 초록 ≠ a11y 온전.** `<div role="button">`은 getByRole를 통과하면서 키보드 활성화·tab order·focus·pressed 상태를 잃는다 — getByRole는 실제 `<button>`임을 강제하지 못하며 **axe 대체가 아니다**. 취약성도 양방향이다(accessible-name 계산 의존이라 ARIA/label 변경에 깨진다).
- **결정적 공백**: 접근성 기반 테스트 *코드*가 LLM의 UI 의도 이해에 더 나은 context 신호인지 실증한 출처는 **없다**. 관련 agent 논문(2603.20358·2603.07024·2606.30697·2511.21398)은 전부 **앱의 런타임 a11y tree grounding**이지 test source가 아니다 — **다른 artifact이며 전이는 관용적 추론이다.**
- **하네스에서의 귀결**: `TL2_NONSEMANTIC_QUERY`는 파일 단위 **census 전용**이다. →getByRole 이관은 이 하네스가 제안하지 않는다(AI 이해 근거 ABSENT).

---

## E-CG1 · comment-gap — '왜' 주석 추가는 opt-in이며 근거는 비파생 맥락뿐

- **판정**: report-only · 효과 **추론(O-3)**
- **근거 화해**: E-TL1(2404.03114)의 null 결과는 *이미 읽히는* 코드에 문서를 더한 경우다. comment-gap(침묵 예외·매직 넘버·정규식)은 **코드에 아예 없는 정보를 보충**하는 별개 사례다 — 그래도 이득은 **사람 이해 + 코드로 파생 불가한 맥락**으로만 말하고, "LLM 성공률 +N%"로 말하지 않는다.
- **사실성 위험 상속**: 생성 주석은 최상위 모델도 약 **20%**가 검증가능하게 부정확하고(E-C5), 특화 파인튜닝 모델의 주석 수정조차 **35~45%**가 틀린다(E-C4). 그리고 오도 주석은 **−13.47pp**로 측정된 유일한 실증 해악이다(E-C1).
- **하네스에서의 귀결**: `C7_SILENT_HANDLER`·`C8_MAGIC_NUMBER`·`C9_REGEX_LITERAL`은 **결함이 아니라 C1 개입의 seed**다. 추가는 **opt-in·what이 아니라 why·사람이 사실성 검증**이며, **주석 개수·밀도는 어떤 점수에도 들어가지 않는다**(볼륨 가점 = Goodhart). 삭제(C0)가 여전히 위험 0의 기본이다.

---

## 넣지 말 것 (이 문서 고유 정직성 가드)

1. 🚫 시맨틱 마크업·테스트 설명 개선을 **"에이전트 성공률/툴그래프 이득"으로 귀속** — 격리 연구가 없다(E-MK1·E-TL1·E-TL2).
2. 🚫 **ARIA/role/셀렉터/테스트 제목의 '볼륨'에 가점** — WebAIM 역상관(E-MK3). 존재 채우기·자동 생성 금지.
3. 🚫 **자동 ARIA/alt/어서션 생성** — confident-but-wrong(E-MK2)·green-locks-bug(E-TL1).
4. 🚫 **WebAIM 고정 배수**("두 배") 인용 — 연도마다 불안정, 방향성만(E-MK3).
5. 🚫 **"a11y tree ≈ DOM의 ~10×"** — folklore, 폐기(E-MK1).
6. 🚫 **getByRole green을 a11y 보장·VERIFIED로 취급** — axe 대체 아님(E-TL2).
7. 🚫 **web-agent 런타임 grounding 논문을 test-code 가독성 근거로 오귀속**(E-TL2).
8. 🚫 **주석 밀도·개수를 점수화** — comment-gap은 후보 census일 뿐(E-CG1·O-4).
9. 🚫 이 축들로 **저장소 층 등급을 만들거나 총점에 합산** — 본문 층은 census만(모드 ③ 불변식).
