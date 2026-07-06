# 계층 카드 — E2E / System

> **축 카드(계층)**. 방법론과 직교 — "어떤 AC 슬라이스가 **E2E/System 계층 테스트**가 되는가"만 정한다. 방법론 멤버십은 [`methodology-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §1.

## 1. 정체 (scope + size/hermeticity)
- **scope**: 완결·통합된 **전체 시스템**의 요구 충족(블랙박스·엔드투엔드)이거나 **live 다중 서비스가 필수**.
- **size/hermeticity**: test double을 쓸 수 없거나 여러 머신에 걸침(SWE@Google "large").
- 답하는 질문: "사용자 여정 전체가 되나?" 속도 10~30분·비용 비쌈·**RCA 약함**·flaky 경향.

## 2. AC 포함 기준 (이 슬라이스가 E2E가 되려면) — AND/우세
- [ ] **가장 크리티컬한 사용자 여정**(로그인→결제류)이거나 live 다중 서비스가 필수다.
- [ ] **하위 계층(unit/integration)에서 못 잡는** 통합/여정 관점의 잔여분이다(push-down 후 남은 것).
- [ ] E2E는 **핵심 여정 소수**로 절제한다(ice-cream-cone 방지).

## 3. AC 제외 기준 (아니면 어느 계층으로)
- UI에 비즈니스 로직이 없으면 **subcutaneous로 하향**(도메인/서비스 계층) → [`layer-integration.md`](layer-integration.md)/[`layer-unit.md`](layer-unit.md). (Fowler SubcutaneousTest·push-down)
- 저수준 분기·값 판정 → 하위 계층.
- 가드: **"acceptance" 의도가 E2E를 강제하지 않는다** — 모든 인수테스트가 E2E는 아니다(level≠type). AC≠E2E 등치 금지.

## 4. 오라클 프로필 (principles §5)
- **얕은 편**: 정확 출력 pinning이 비현실적일 때가 많다 → 주요 여정 도달·완료 확인 + 최소 상태 확인.
- 정확 pinning 대신 **메타모픽 관계(MR)를 옵션**으로(강제 아님·부분 판정).
- green-locks-bug 리스크는 상대적으로 낮으나(주장 자체가 얕음) "초록=검증" 오독 리스크. 스모크/동어반복 어서션 금지(§5-4).

## 5. 이 계층 × 방법론 조합 (선택된 방법론 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Nightly × E2E = STRONG(best-evidenced nightly)** — 대규모/exhaustive E2E·cross-browser·real-device·perf/visual/a11y·대규모 fuzzing의 자연스러운 귀착지(non-blocking 리포트).
- **Smoke × E2E = STRONG(조건부)** — 크리티컬 여정 happy-path acceptance smoke. flaky real-world E2E는 fast 게이트 부적격 → full acceptance/nightly로.
- **Regression × E2E = STRONG(멤버십)·대개 nightly 이연** — 전량 E2E 회귀는 비쌈 → nightly; 크리티컬 여정 subset만 per-commit.
- **Sanity × E2E = DEGEN** — 실무에서 거의 안 둠(비용 대비 실익 낮음·표준 근거 전무).
- 선택 스코프에 없는 방법론과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(system testing) — official-standard, HIGH. IEEE 829-2008 §3.1.37 — official-standard(철회·정의 유효). Fowler Practical Test Pyramid/SubcutaneousTest(push-down) — blog, MED~canonical. SWE@Google ch.11(large) — vendor-doc, MED.
- **caveat**: "이 버그는 E2E여야 잡는다"는 통념은 반증됨 — 값싼 unit이 더 많은 경계를 커버(RCA·비용 우위). E2E 유지비 "N배" 류 수치는 출처 0(folklore) — 인용 금지. 비율% 하드코딩 금지.
