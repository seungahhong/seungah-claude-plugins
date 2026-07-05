# 세션 5 — cost-of-pass·토큰 예산·효율 벤치마크

> 조사 렌즈: 점수 루브릭 전체의 프레이밍과 정직성. "토큰 수가 옳은 효율 지표인가", "성공을 못 보는 로그로 무엇을 단정할 수 있나", "예산 인지 기법은 순이득인가".
> 상태: deep-research 각도 5, 적대 검증 완료 (2026-07-04). 주요 확인: cost-of-pass 정의·frontier cost-of-pass 급락·성능지향 스케일링의 순손실.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | cost-of-pass = 정답 1건 생성의 기대 화폐비용; frontier cost-of-pass = 가용 모델·인간 전문가 중 최소 |
| C2 | **CONFIRMED** | frontier cost-of-pass가 최근 1년 급락(복잡 정량 작업은 수개월마다 반감) → 절대 $ 수치는 빨리 낡음 |
| C3 | **CONFIRMED** | 성능지향 inference-time 스케일링(다수결·self-refine)은 한계 이득 대비 비용을 정당화 못하는 경우 많음; TALE-EP(예산 인지)만 유망 |
| C4 | **CONFIRMED** | 모델 클래스 비용효율은 작업 의존(session-4 C1과 동일 소스) |
| C5 | **CONFIRMED** | 예: Claude 3.7 Sonnet 최고 정확도 61.82%지만 cost-of-pass 3.54 vs 0.98 — 정확도≠비용효율 |

## 검증된 핵심 발견

**토큰 수는 효율의 옳은 지표가 아니다(C1).** cost-of-pass는 **성공-가중 비용**(정답 1건의 기대 화폐비용)을 옳은 지표로 정의한다. 저토큰 세션이라도 **작업에 실패했다면** 효율적이지 않다. 스킬은 JSONL 로그에서 task success를 관측할 수 없다 → **점수는 효율 프록시일 뿐 cost-of-pass가 아님**을 반드시 명시하고, "저토큰=우수"로 단정하지 않는다. 이것이 C10 정직성 수정의 핵심이다.

**절대 $ 수치는 빨리 낡는다(C2).** frontier cost-of-pass는 최근 1년 급락(복잡 정량은 수개월마다 반감). → 대시보드의 절감 $는 "실행 전 추정치, 실행 후 재측정" 원칙을 명시. 가격표는 `--pricing`으로 갱신 가능해야 한다(C1 구현과 정합).

**더 많이 생각/재시도 ≠ 이득(C3).** 성능지향 inference-time 스케일링(majority voting·self-refinement)은 한계 성능 이득이 비용을 정당화 못하는 경우가 많다. 예산 인지 기법(TALE-EP)만 유망. → 재시도·다수결 남발은 순낭비 신호일 수 있음(duplicate-tools/subagent-overuse와 정합).

**정확도와 비용효율은 다르다(C5).** Claude 3.7 Sonnet이 정확도 61.82%로 최고여도 cost-of-pass 3.54는 어떤 모델의 0.98보다 나쁘다. → "가장 똑똑한 모델 = 가장 효율적"이 아님을 라우팅(session-4)이 활용.

## 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** "We formalize cost-of-pass: the expected monetary cost of generating a correct solution. We then define the frontier cost-of-pass: the minimum cost-of-pass achievable across available models or the human-expert(s)." — cost-of-pass, **arXiv:2508.02694**(v1 2025-07-24 제출·2025-08 공개 — ID의 2508은 공개월).
- **[C2 · CONFIRMED]** "tracking the frontier cost-of-pass over the past year reveals significant progress, particularly for complex quant. tasks where the cost roughly halved every few months." — 동.
- **[C3 · CONFIRMED]** "performance-oriented methods with marginal performance gains rarely justify the costs, while TALE-EP [token-budget-aware] shows some promise." — 동.
- **[C4 · CONFIRMED]** 모델 클래스 비용효율 작업 의존(session-4 C1과 동일 인용).
- **[C5 · CONFIRMED]** "Claude 3.7 Sonnet achieves the highest accuracy ... 61.82% ... but its cost-of-pass is significantly higher (3.54 vs. 0.98)." — 동.

## 이 스킬에 반영 (매핑)

- **점수 = 효율 프록시(≠cost-of-pass) 명시(C1·C10)**: analyze_sessions 종료 메시지·SKILL.md·대시보드 KPI에 "성공률을 볼 수 없음" 경고. 저토큰=우수로 단정 금지.
- **축별 근거 등급 표기(C1)**: cache=CONFIRMED, redundancy=PLAUSIBLE, density/tool=HEURISTIC. 대시보드 rubric에 근거 문자열 렌더.
- **절감 $는 "실행 전 추정"(C2)**: 대시보드 마지막 카드에 재측정 원칙. 가격은 `--pricing` 갱신 가능.
- **재시도/스케일링 남발 신호(C3)**: duplicate-tools·subagent-overuse가 이를 부분 포착. 추가 정량 감점은 근거 부족으로 보류.
- **라우팅 근거 공유(C4·C5)**: session-4의 세션별 후보 판별과 동일 소스.

### 바꾸지 말 것
- 성공률을 추정하려는 프록시(예: 저토큰=성공) — 로그로 관측 불가, 인과 없음.
- 특정 cost-of-pass 절대값을 루브릭에 고정 — 수개월마다 반감(C2).

## 소스 (검증 상태)
- Cost-of-Pass: An Economic Framework for Evaluating Language Models — arXiv:2508.02694 (정의·frontier·TALE-EP·Claude 3.7 예시 전부 원문 확인)
- 보강: RouterBench(라우팅 평가), TALE-EP(예산 인지) — 참조
