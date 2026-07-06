# 방법론 카드 — Regression

> **축 카드(방법론)**. 계층과 직교 — "어떤 테스트가 **Regression 선택**에 드는가"만 정한다(모든 계층에 얹힘). 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 실체화 문법은 principles §3.5, 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **durable tag / 기본체 (계층 직교)**. 수정 이후 **변경 안 된 영역**에 결함이 유입·노출되지 않았는지 확인. ISO/IEC/IEEE 29119-1:2022 §4.4.6: regression은 "test level이 아니라 design/execution choice" → **모든 계층에 얹힌다**.
- ⚠️ "픽스 후 실패 테스트 재실행"은 regression이 아니라 **confirmation**(혼동 금지 → [`methodology-sanity.md`](methodology-sanity.md)).

## 2. 멤버십 기준 (어떤 테스트가 Regression에 드는가) — AND/우세
- [ ] **미변경 영역의 행위 보존**(비회귀)을 검증하거나, 이 테스트가 **변경을 traverse/커버**한다(per-commit change-relevance 재계산).
- [ ] **완전 행위 보존 오라클**을 요구한다(값·상태를 명세에서 유도).
- [ ] **safe-RTS**: 변경을 traverse하는 것을 선택하되 **매핑 불가/미지 파일타입이면 full-suite fallback 강제**(under-selection이 주 실패모드).

## 3. 실체화 & CI 배치 (principles §3.5)
- **durable 태그**: `@regression`(옵션 A 멀티태그) 또는 durable 기본체 전량(옵션 B carve-out) — Phase 2 계획(게이트 A) 택1(§3.5.4). 러너별 문법 §3.5.2. 셀렉터 실행 분리 검증(§3.5.4).
- **세 레버(비-호환)**: **Selection**(TCS/TIA — 볼륨 감축·lossy unless safe) / **Prioritization**(TCP — 재정렬·**볼륨/비용 불변·latency만**) / **Batching**(무손실 볼륨 감축).
- **CI 배치**: PR-gate는 TIA로 선택된 `@regression` 부분집합, Merge to main은 full 빠른 계층, 예산 초과분은 Nightly(§3.5.5).

## 4. 오라클 기대
- **강함(완전 행위 보존)**. 현재 구현=정답 가정 금지(implementation-bias).
- ⚠️ **Unit과 조합 시 최고위험 오라클 셀**: LLM이 명세가 아니라 현재 구현을 regression oracle로 굳혀 버그를 초록으로 은폐(green-locks-bug). 완화: AC 기준 오검증(§5-1)·실행 그라운딩(§5-2)·통과 assertion을 기대 기준으로 역전. 게이트는 테스트 개수가 아니라 **오라클 신호 강도**로(correct≠strong).

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Regression × Unit = STRONG(멤버십)·최고위험 오라클**(경계/에러/edge 회귀), **Regression × Integration = STRONG**(통합 비회귀·safe-RTS), **Regression × E2E = STRONG(멤버십)·대개 nightly 이연**(전량은 비쌈).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(regression·confirmation 구분) — official-standard, HIGH. ISO/IEC/IEEE 29119-1:2022 §4.4.6(design/execution choice, 계층 직교) — official-standard, HIGH(원문 paywalled·2차 요약 교차확인, 절번호 provenance는 secondary). safe-RTS = Rothermel-Harrold 1997(primary) + Microsoft·Datadog TIA(vendor) 교차. **batching 무손실 = arXiv:2308.13129**(Parallel Batch Testing, ESEC/FSE 2023, primary). green-locks 앵커 = arXiv:2410.21136·2601.05542·2606.18168(primary, 방향 HIGH/수치 MED); **인접(직접 앵커 아님) arXiv:2507.17542(AssertFlip)**.
- **caveat**: **prioritization은 CI 비용을 못 줄인다**(latency만·정의상 — 재정렬은 총 실행량 불변). "regression 90%를 5% 시간에" 류 수치는 folklore. green-locks-bug 정밀수치는 특정 벤치마크 산물 → 하드코딩 금지. 비율% 하드코딩 금지.
