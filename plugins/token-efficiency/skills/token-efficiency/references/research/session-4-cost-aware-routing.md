# 세션 4 — 비용 인지 모델 라우팅·캐스케이드

> 조사 렌즈: model-routing 절감 휴리스틱을 재조작화. "플랫 30% Opus→Sonnet이 타당한가", "라우팅/캐스케이드는 어떻게 비용을 줄이나".
> 상태: deep-research 각도 4, 적대 검증 완료 (2026-07-04). 주요 확인: 모델 비용효율의 작업 의존성·캐스케이드 구조비용·pre-generation 라우터.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | 모델 비용효율은 작업 의존: 경량=저난도 정량, 대형=지식집약, 추론모델=복잡 정량 |
| C2 | **CONFIRMED** | 캐스케이드는 escalation 전에 저렴 모델을 먼저 실행 → "구조적 비용"이 성능 한계 |
| C3 | **PLAUSIBLE** | pre-generation 라우터가 5개 중 4개 데이터셋에서 최적 캐스케이드를 능가(저렴 모델 생성비 회피) |
| C4 | **CONFIRMED(참조)** | RouterBench: 405k+ 사전계산 추론 출력 — 라우팅 휴리스틱 평가 표준 벤치 |
| C5 | **PLAUSIBLE** | EET: 경험 기반 조기 종료로 SWE 에이전트 비용 절감 |

## 검증된 핵심 발견

**"30% 플랫 다운그레이드"는 조악하다(C1).** 모델 비용효율은 작업 유형에 달렸다 — 경량 모델은 기초 정량 작업의 cost-of-pass를 최소화하고, 대형 모델은 지식집약 작업, 추론 모델은 복잡 정량 문제에서(높은 per-token 가격에도) 최적이다. 즉 "전체 비용의 30%를 무조건 Sonnet으로"가 아니라 **작업 특성별로 후보를 판별**해야 한다.

**캐스케이드의 한계는 구조적 비용이다(C2·C3).** 캐스케이드는 escalation 판단 *전에* 저렴 모델을 이미 실행(생성비 지불)하므로, 그 구조적 비용이 성능을 제한한다. **pre-generation 라우터**(생성 전에 라우팅)는 큰 모델로 직행할 쿼리에서 저렴 모델의 생성비를 회피해 5개 중 4개 데이터셋에서 최적 캐스케이드를 능가했다. → Claude Code 로그 분석 관점에선 **사전 판별(세션 특성으로 downgradeable 후보 식별)**이 사후 캐스케이드보다 자연스럽다.

**Opus/Sonnet 비용비 정정.** 원 스킬은 "Opus = Sonnet × 5"로 절감을 계산했으나, 현행가로 Opus $5 / Sonnet $3 = **~1.67×**(입력 기준). 5×는 폐기가($15/$3) 시절 수치. → 라우팅 절감 배수를 1.67로 교정.

## 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** "Model class cost-effectiveness is task-dependent: lightweight models minimize cost-of-pass on basic quantitative tasks, large models on knowledge-intensive tasks, and reasoning models on complex quantitative problems despite higher per-token prices." — cost-of-pass, **arXiv:2508.02694**(2025-07-24 제출·2025-08 공개). session-5와 공유.
- **[C2 · CONFIRMED]** "cascade performance is limited primarily by structural cost, since cascades pay the cheap model before any escalation decision." — 캐스케이드 분석 논문(각도 4 소스).
- **[C3 · PLAUSIBLE]** "pre-generation router exceeds the best cascade policy on four of five datasets, mainly because it avoids the cheap model's generation cost on queries sent directly to a larger model." — 동. normalized gain 차이 ≤0.014, CR@90 MMLU/TriviaQA/MATH 동일.
- **[C4 · CONFIRMED]** "RouterBench ... provides over 405k precomputed inference outputs" — 라우팅 평가 표준 벤치(각도 4 소스). 휴리스틱을 이 벤치로 검증 가능.
- **[C5 · PLAUSIBLE]** EET: 경험 기반 조기 종료로 비용효율 SWE 에이전트 — "EET: Experience-Driven Early Termination for Cost-Efficient Software Engineering Agents", **arXiv:2601.05777**(v2 2026-04).

## 이 스킬에 반영 (매핑)

- **model-routing을 세션별 후보 판별로 재조작화(C1·C3)**: `looks_downgradeable(s)` = **Opus급 이상(dominant_input_price > $3)** AND 이미지 없음 AND 출력 < 30k AND 도구 < 40 AND output_ratio < 0.02. 이미 저렴한 모델(Sonnet/Haiku) 세션은 후보에서 제외 — "다운그레이드"가 성립하지 않으므로. 이 후보 세션의 *실제 비용*만 절감 계산. 플랫 30% 폐기.
- **절감비는 세션별(가격정정)**: `save = Σ(후보 비용) × (1 − SONNET_IN/dominant_input_price)` — Opus→Sonnet 1−3/5=40%, Fable→Sonnet 1−3/10=70%. 원 스킬의 5× 배수는 폐기가 시절 수치.
- **정직성**: 라우팅은 "저난도 후보만"이며 작업 의존이므로 자동 적용 아닌 제안. 대시보드 카드에 근거(2508.02694) 명시.

### 바꾸지 말 것
- 특정 라우팅 정확도/절감률을 보장 — 작업·데이터셋 의존. 후보 개수·추정치만 제시.
- RouterLLM/FrugalGPT 특정 수치 인용 — 스킬은 로그 분석기이지 라우터 구현이 아님. 개념 프레임만 차용.

## 소스 (검증 상태)
- cost-of-pass — arXiv:2508.02694 (모델 작업 의존성 확인; session-5 상술)
- 캐스케이드 구조비용·pre-generation 라우터 — 각도 4 fetch(정성 확인)
- RouterBench — 405k 출력 표준 벤치(참조)
- EET — arXiv:2601.05777 (조기 종료)
