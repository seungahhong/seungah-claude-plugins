# 방법론 카드 — Nightly

> **축 카드(방법론 열이되 엄밀히는 CI-stage/스케줄 축)**. 계층과 직교 — "어떤 테스트를 **게이트에서 빼 스케줄로 이연**하는가"를 정한다. 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **⚠️ nightly는 엄밀히는 방법론(test type)이 아니라 CI-stage/스케줄 지연 축**이다(ISTQB/ISO에 nightly test type 없음). "게이트에서 빼 스케줄(cron/야간/pre-release)로 미룬다"는 **라우팅 결정**.
- durable 태그로 실체화하되(`@nightly`) 그 본질은 스케줄 배치다.

## 2. 멤버십 기준 (어떤 테스트를 Nightly로 이연하는가) — 우세
- [ ] 선택기가 게이트에서 **서브셋만** 돌릴 때 놓친 회귀를 잡는 **full-suite 안전망**(targeted selection은 lossy이므로 — 파생 추론).
- [ ] per-run **비용/지연이 게이트 예산 초과**(느림·비쌈).
- [ ] **cross-browser·real-device·perf/load·visual·a11y**(clean·dedicated 환경 필요) 또는 **대규모 fuzzing 캠페인**(별도 시간예산).
- [ ] 결과는 merge-blocking 아닌 **non-blocking 리포트/티켓화**.
- [ ] ⚠️ **quarantine ≠ nightly**: flaky quarantine은 매 CI run 실행하되 non-blocking(별개 메커니즘 — 한 스케줄로 붕괴 금지).

## 3. 실체화 & CI 배치 (principles §3.5)
- **durable 태그**: `@nightly` 토큰 + `test:nightly` 셀렉터 스크립트(§3.5.2). 안전망 재실행은 durable 기본체 full-suite를 cron 스테이지에서 전량(옵션 B). 게이트에서 명시적으로 뺀 테스트만 `@nightly`로 carve-out(옵션 B, §3.5.4).
- **CI 배치**: cron/scheduled 스테이지 — full E2E/UI·perf·cross-browser의 귀착지(§3.5.5).

## 4. 오라클 기대
- 다양 — E2E 정확출력은 MR/얕은 상태, fuzz는 crash/invariant, perf는 임계 기반. **non-blocking이어도 오라클 강도는 낮추지 않는다**(느린 실행 ≠ 약한 판정). 스모크/동어반복 어서션 금지(§5-4).

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Nightly × E2E = STRONG(best-evidenced)**(대규모 E2E·cross-browser·fuzz), **Nightly × Integration = STRONG-ish**(느린 integration + selection 안전망), **Nightly × Unit = DEGEN(빈셀)**(unit은 빠르고 싸서 게이트 소속).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: **arXiv:2509.10279**(Targeted Test Selection) — primary, 원칙 HIGH: targeted selection이 lossy(>95%만 포착)임을 확립 → **nightly full 안전망은 이로부터의 파생 추론**(논문 주제는 selection). **arXiv:2510.16433**(대규모 CI Continuous Fuzzing 실증) — primary, **MED**(날짜 caveat): 지속 fuzzing이 별도 예산을 요함을 실증하나 **property-based·스케줄링은 논문이 다루지 않는 engineering practice**. BrowserStack/TestRail(대규모 E2E·cross-browser→nightly) — vendor/blog, MED. Google TAP pub45861(postsubmit) — foundational, MED(pre-2025).
- **caveat**: nightly는 방법론이 아니라 CI-stage 축(§1). arXiv:2509.10279 수치(15%/95% 등)는 특정 시스템 산물 → 기본 기대치/게이트 통과율로 승격 금지(귀속 인용만). **nightly-deferral 단독 효과의 2025+ 엄밀 측정은 못 찾음**. 비율% 하드코딩 금지.
