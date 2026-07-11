# 주석 축 근거 dossier — comments · docstrings

> 층위: 코드 **본문** 층의 주석·독스트링. 저장소 층(README·CLAUDE.md 등)은 이 플러그인의 측정 모드(score.py) 소유.
> 인용 원천은 정본 근거 시트(`EVIDENCE-SHEET.md`) §2 하나뿐. 여기 없는 수치·논문·URL은 쓰지 않는다.
> 각 인용에는 SOURCE-TIER 라벨 + 발표연월을 붙인다.

---

## 이 축의 결론 한 줄

주석 개입에서 **효과가 확실하고 위험이 0인 유일한 클래스는 "오도·stale 주석의 삭제/수정"(P1)** 이다.
주석 *추가*(P3)와 자동 *수정*은 사실성 위험이 커서 반드시 사람 승인 게이트를 거친다.

---

## E-C1 · 오도 주석 하나 = 구조 변형 세 개를 합친 것 [PRIMARY-2025+ · 2025-04, NeurIPS 2025] `CONFIRMED (3-0)`

- 출처: *CodeCrash*, arXiv:2504.14119 (NeurIPS 2025) — 17개 LLM·1,279문항.
- 수치: 오도 주석 주입(MDC) **−13.47pp**, 오도 print 주입(MPS) **−13.28pp** ≈ 구조 변형 3종 결합(ALL) **−14.04pp**.
  → 즉 **주석 하나가 구조 왜곡 세 개와 맞먹는 오도력**을 가진다.
- verbatim: `"average performance degradation of 23.2% in output prediction tasks"` — 오도 NL 문맥 주입 시 출력 예측 평균 −23.2%.
- verbatim: `"Even with Chain-of-Thought ... 13.8% drop due to distractibility and rationalization"` — **CoT로도 −13.8% 잔존**. 추론을 시켜도 방어되지 않는다.
- ⚠️ 스코프 caveat: 이 값들은 **코드 추론(출력/입력 예측) 태스크** 측정치이며, 일반 코드 생성 성공률이 아니다. CoT 13.8%는 전체 perturbation 평균값.

**핵심 문장 (이 플러그인의 P1 근거)**:
> stale·오도 주석은 토큰 낭비가 아니라 **능동적 오도**다.
> 그리고 **삭제는 동작을 깨뜨릴 수 없다**(주석은 실행되지 않는다) → 기대이익 확실 + 위험 0인 **유일한** 개입 → **P1**.

---

## E-C2 · 주석은 양방향 인과 인자(품질이 관건) [PRIMARY-2025+ · 2025-12, ICSE 2026] `CONFIRMED (3-0)` · 신뢰도 medium

- 출처: *Inside Out*, arXiv:2512.16790 (2025-12, ICSE 2026 채택).
- verbatim: `"LLMs not only internalize comments as distinct latent concepts but also differentiate between subtypes such as Javadocs, inline, and multiline"` — 모델은 주석을 잠재 개념으로 내부화하고 Javadoc/inline/multiline 하위유형을 구분한다.
- 함의: 주석은 무시되는 장식이 아니라 **양방향 인과 인자**다. 좋으면 돕고 나쁘면 해친다 → 품질이 관건이지 존재 여부가 아니다.
- 🚫 **CAV 개입치 인용 주의**: 이 논문의 `"-90% to +67%"`는 **CAV로 임베딩 공간을 조작한 개입치**이지, *실제 주석 텍스트를 추가/삭제한 효과가 아니다*. 방향·상한의 증거로만 쓰고, 주석 편집 효과와 **동일시 금지**(근거 시트 §7-3).

---

## E-C3 · 코드-주석 불일치(CCI)는 실측 가능한 결함 유형 [PRIMARY-2025+ · 2025-12] `CONFIRMED (3-0)` · 신뢰도 medium

- 출처: *Larger Is Not Always Better*, arXiv:2512.19883 (2025-12).
- CCI 정의(verbatim): `"Comment inconsistency arises when developers modify code but neglect to update...comments, potentially misleading future maintainers and introducing errors."`
- 기법: 코드 변경을 `replacing / deleting / adding` **순서 있는 수정 활동 시퀀스(구조화 diff)**로 모델링해 outdated 주석 상관을 포착. CodeT5+ 백본 최대 **+13.54% F1**.
- ⚠️ caveat: 탐지 성능은 저자 자체 벤치마크 기준이며 **독립 재현 미확인**.
- 배경 tier: CCI의 개념 정의 원류는 iComment(2007) — `PRIMARY-pre2025` **배경**으로만 표기.
- 함의: 우리 census는 이 "코드 변경 vs 주석 미변경" 시그널을 **stale 후보 인벤토리**로 삼는다(등급이 아님).

---

## E-C4 · 자동 주석 수정은 특화 파인튜닝 모델도 35~45%가 틀린다 [PRIMARY-2025+ · 2025, ICSE 2025] `보강근거`

- 출처: C4RLLaMA, ICSE 2025, DOI 10.1109/ICSE55347.2025.00035.
- verbatim: `"Manual evaluation showed that the percentage of correct comment updates by C4RLLaMA was 65.0% and 55.9% in Just-in-time and Post Hoc, respectively"` — 정확률 65.0% / 55.9% → 나머지 **35~45%가 틀린다**.
- 함의: 주석을 **자동으로 생성/수정해 그대로 적용하는 것은 금지**. 반드시 사람 승인 게이트(게이트 B)를 통과한다. 특화 파인튜닝 모델도 이 정도이므로 범용 LLM은 더 보수적으로 취급한다.

---

## E-C5 · 최상위 모델도 생성 주석의 약 20%가 검증가능하게 부정확 [PRIMARY-pre2025 · 2024-06 · **배경**] `CONFIRMED (3-0)`

- 출처: arXiv:2406.14836 (KAIST, 2024-06) — **pre-2025 배경 tier**로만 표기(2025+ 1차 근거를 대체하지 않음).
- verbatim: `"even for the best-performing LLM, roughly a fifth of its comments contained demonstrably inaccurate statements"` — 최상위 모델도 생성 주석의 약 20%가 실증적으로 부정확.
- `document testing`(주석에서 실행 가능한 테스트를 생성·실행해 pass/fail로 채점)이 주석 정확도와 **통계적으로 유의**한 관계(point-biserial p<1e-11, Welch t p<1e-9). 기존 CCI 기법은 유의성 없었음.
- 필터 효과: 정확도<0.8로 필터 시 **부정확 주석 46% 제거·정확 주석 72% 보존**.
- ⚠️ caveat: 실효 분류력 **modest (ROC-AUC 0.67)**, Java/Defects4J·141개 라벨 **한정**, 테스트 생성 LLM 자체도 환각 가능.
- 함의(P3): 주석 *추가*의 1급 센서는 코드 대조 + **실행 그라운딩(document testing)**이지, 모델 자기보고가 아니다.

---

## 주석 3분류 운영 정의 (census가 태깅하는 라벨)

우리 census는 주석을 아래 3종으로 라벨링하고, 개입 우선순위(P1)와 직접 연결한다.

1. **오도(misleading)** — 코드와 **모순**되는 주석. 읽는 에이전트를 능동적으로 틀린 방향으로 민다(E-C1).
   → **삭제/수정 최우선(P1)**. 동작 위험 없음.
2. **stale** — 코드는 변했는데 주석은 안 변한 것(E-C3의 CCI). 과거엔 맞았으나 지금은 어긋난다.
   → 삭제 또는 현행화. 코드 대조로 판정.
3. **noise** — 코드를 그대로 되뇌는 **중복** 주석, 또는 **주석 처리된 죽은 코드**. 틀리진 않지만 신호 대 잡음비를 떨어뜨린다.
   → 제거 후보(P1). 삭제 위험 없음.

> 세 라벨 모두 개입의 1급 센서는 **사람 확인 + 코드 대조**다(주석은 실행되지 않으므로 삭제로 동작이 깨질 수 없다).

---

## 이 축의 미해결 질문 (답한다고 주장하지 않는다)

- **O-4 (주석 밀도)**: 주석이 도움이 되다가 중복·오도로 해로워지는 교차점(최적 밀도)은 **미상**이다. 모델·태스크별로 어떻게 다른지도 근거 없음.
  → 🚫 따라서 이 플러그인은 **주석 밀도 목표치(예: "주석 비율 20%")를 만들지 않는다**(근거 시트 §7-8). census는 밀도를 등급화하지 않고 위 3라벨의 **인벤토리**만 낸다.
- 주석 *추가*의 양(positive) 효과 크기(O-3)도 현 근거는 대부분 제거 ablation이라 **대칭 가정 불가** → P3를 "확실한 이득"으로 과장하지 않는다.
