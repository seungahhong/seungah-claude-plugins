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

## 5. 테스트 배치 & API 모드 태그 규약

### 5.1 배치
- **E2E 테스트 경로는 사용자에게 초기에 입력받는다** — E2E는 별도 러너(Playwright/Cypress 등)·별도 디렉토리(`e2e/`, `tests/e2e/`, `cypress/e2e/` 등)를 쓰는 것이 일반적이므로, **Phase 1에서 E2E 계층이 선택되면 그 자리에서 테스트 경로를 문의**한다(SKILL Phase 1). 입력된 경로 아래에 여정별 스펙 파일을 둔다.
- unit/integration의 `__test__/` co-locate 규약은 E2E에 강제하지 않는다(E2E 대상은 특정 컴포넌트가 아니라 사용자 여정). 러너·입력 경로 관습을 따른다.

### 5.2 API 모드 태그 (`@e2e-mock` / `@e2e-live`) — principles §3.6.5·§3.6.5-a
E2E만 **API 경계를 태그로 선언**한다(unit/integration은 항상 mock이라 태그가 필요 없다).

| 태그 | 목적 | 실행 | 배치 |
|---|---|---|---|
| **`@e2e-mock`** (**비-smoke 기본**) | CI에서 **결정론적**으로 여정을 검증 | 러너 네트워크 인터셉트(`page.route` 등)로 캡처 fixture 주입 | CI 스테이지(선택 스코프에 따라 PR job·nightly 등) |
| **`@e2e-live`** (**Smoke 멤버십이면 필수** / 그 밖은 명시 요청 시만) | **실제 API 연동이 되는지** 검증 | 실제 백엔드 대상, mock 주입 없음 | **고정 CI 스테이지 없음 — 수동·on-demand만** |

- **스펙은 한 벌**이다. mock용/live용으로 시나리오를 복제하지 않고, 한 스펙에 **유효한 모드 태그를 병기**한다(둘 다 되면 `['@e2e-mock','@e2e-live']`).
- **Smoke 멤버십이 아닌 E2E는 기본이 `@e2e-mock`만**이다. 그런 스펙에 `@e2e-live`는 **사용자가 그 시나리오에 대해 명시적으로 요청했을 때만** 추가한다(자동 부여 금지).
- **⚠️ 단 하나의 규칙 기반 예외 — E2E smoke는 `@e2e-live` 전용**(principles §3.6.5-a): `@smoke` 멤버십을 가진 E2E 스펙은 **요청이 없어도 `@e2e-live`를 필수 부여**하고 **`@e2e-mock`을 부여하지 않는다**(mock 주입·fixture 없음). 아래 §5.2-a가 이 예외의 전문이다.

### 5.2-a E2E smoke = 실제 API 연동 필수 (live 전용) — principles §3.6.5-a·§3.6.5-b

| 항목 | 규칙 |
|---|---|
| 태그 | `['@smoke','@e2e-live']` — **`@e2e-mock` 금지**, `@regression`/`@nightly` **동시 부여 금지**(live 고정이라 그 스위트 CI에서 빠지는 phantom membership) |
| mock | **없음** — `page.route` 등 인터셉트를 걸지 않고 fixture도 만들지 않는다 |
| CI 배치 | **없음** — PR-gate·post-deploy·nightly 어디에도 넣지 않는다. `test:smoke`가 이걸 끌어오면 분리 검증 실패 |
| 실행 | 수동 on-demand `test:e2e:smoke:live` — 예 `E2E_MODE=live BASE_URL=… playwright test --grep "(?=.*@smoke)(?=.*@e2e-live)"` |
| 하네스 실행 | 게이트 B에서 **대상 환경 + 테스트 계정/데이터 + 그 자리 승인**이 모두 있을 때만(§3.6.5-b). 없으면 **UNVERIFIED** |
| 오라클 | 실제 응답이라 값이 흔들릴 수 있다 → **여정 도달·상태 전이·계약 형태**(필수 필드·타입·상태코드) 수준. 특정 시점 응답값 pinning 금지 |
| sanity | **선택 대상 아님**(레인은 `@e2e-mock`만 고른다) — 누락이 아니라 규칙의 결과이며 그렇게 표기 |

**대가(반드시 병기)**: 고정 CI 스테이지가 없으므로 **E2E smoke는 자동 배포 게이트가 아니라 승격 전 수동 체크포인트**다. 또한 이 결정은 "배포 게이트는 결정론·외부 의존 0"이라는 권고(MinimumCD·Fowler, MED)와 **상충하는 사용자 운영 결정**이다 — 근거로 정당화하지 않고 상충 사실을 적는다.
- **모드 전환은 명시 스위치로만** — env(`E2E_MODE=live`)·러너 project·fixture 라우팅 헬퍼. 예: CI `playwright test --grep @e2e-mock` / 연동 `E2E_MODE=live playwright test --grep @e2e-live`. 태그 문법은 principles §3.5.2 어댑터. **스위치 장치(헬퍼·project 설정·스크립트)는 새 코드/설정이므로 게이트 B 승인 대상**이고, 스위치 없이 태그만 붙이면 `@e2e-live`는 실행 불가능한 라벨(phantom)이 된다. `test:e2e:live` 레시피는 **`@e2e-live`가 실제로 1개 이상 있을 때만** 추가한다.
- **스테이지가 모드를 바꾸지 않는다** — nightly가 게이트 테스트를 임의로 재-mock 하거나 live로 승격시키지 않는다. cross-browser·real-device 매트릭스는 **브라우저/디바이스만 실제**이고 API 경계는 그 테스트의 모드 태그를 그대로 따른다([methodology-nightly.md](methodology-nightly.md) §3).
- **`@page:/route` 태그(선택)**: sanity가 "변경된 페이지의 E2E"를 고를 때 경로 미러 매핑이 모호하면 대상 페이지 태그를 부여한다([methodology-sanity.md](methodology-sanity.md) §2). 이는 **대상 메타**이지 스위트 태그가 아니다.
- **fixture**: `@e2e-mock`의 응답 fixture도 3단 폴백(기존 재사용 → 사용자 제공 → 스키마 유도+`[실측 캡처 아님]` 표기)과 출처 기록을 따른다(principles §3.6.3). 위치는 E2E 경로 아래 공용(`fixtures/`) 관습을 감지해 따른다. **E2E smoke(live 전용)는 fixture 대상이 아니다**(§5.2-a).

### 5.3 정직성 — mock 통과 ≠ 연동 검증
`@e2e-mock`이 전부 초록이어도 **연동이 정상이라는 뜻이 아니다** — fixture는 캡처 시점 스냅샷이라 계약 drift를 **정의상** 못 잡는다(principles §3.6.6). 이 하네스에서 연동을 확인하는 장치는 **`@e2e-live` 수동 실행뿐**이며, 계획·요약에 이 문장을 병기한다. "mock 전환으로 flaky N% 감소" 류 수치는 인용하지 않는다.

**live 쪽 정직성도 같은 무게로 적는다**(§5.2-a·principles §3.6.6):
- **"E2E smoke가 배포 게이트를 지킨다"고 쓰지 않는다** — 자동 차단이 없다(수동 체크포인트).
- **live 통과는 실행 시각·대상 환경에 한정된 관측**이다 — 항구적 연동 보증으로 확대하지 않고 시각·환경을 함께 적는다.
- **미실행은 UNVERIFIED**다 — 레시피·스위치를 만든 것은 검증이 아니다.
- **live 실패를 코드 결함으로 단정하지 않는다** — 테스트 결함 / 코드 결함 / **환경·외부계**(미배포·인증 만료·레이트리밋·시드 부재·업스트림 장애) 3분류(§3.6.5-b).
- "live smoke로 장애 N% 조기 포착" 류 효과 수치는 근거가 없다 — 인용 금지.

## 6. 이 계층 × 방법론 조합 (선택된 방법론 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Nightly × E2E = STRONG(best-evidenced nightly)** — 대규모/exhaustive E2E·cross-browser·real-device·perf/visual/a11y·대규모 fuzzing의 자연스러운 귀착지(non-blocking 리포트).
- **Smoke × E2E = STRONG(조건부) · 단 모드는 `@e2e-live` 고정** — 크리티컬 여정 happy-path acceptance smoke. ⚠️ 원래 "조건부"의 조건은 *결정론·fast 게이트 적격*이었으나 **live 전용 결정이 그 조건을 깨뜨렸다**(§5.2-a) — 이 조합은 CI 게이트가 아니라 **수동 체크포인트**로 산출되며, flaky real-world E2E를 게이트에서 빼는 취지는 "CI 스테이지에 넣지 않음"으로 이미 충족된다. ⚠️ 다만 **"flaky하면 nightly로"라는 탈출구는 쓸 수 없다**(nightly는 `@e2e-mock` 스테이지) — 여정을 좁히거나 대상 환경을 안정화하고, 그래도 안 되면 `@e2e-mock` 스펙으로 **분리**한다.
- **Regression × E2E = STRONG(멤버십)·대개 nightly 이연** — 전량 E2E 회귀는 비쌈 → nightly; 크리티컬 여정 subset만 per-commit. **`@e2e-mock` 유지**(회귀 판정은 결정론 전제). 같은 여정을 smoke로도 돌린다면 **스펙을 분리**한다(한 스펙에 `@smoke`+`@regression` 금지, §5.2-a).
- **Sanity × E2E = DEGEN(생성 조합) / 선택 레인으로는 정상** — "sanity 전용 E2E를 새로 만드는 것"은 근거가 없어 하지 않는다(DEGEN). 다만 sanity **선택 레인**은 변경된 페이지에 매핑된 **기존 `@e2e-mock` 스펙을 골라 돌린다**(non-blocking, [methodology-sanity.md](methodology-sanity.md) §2). 두 축이 다르므로 모순이 아니다([`_index.md`](_index.md) §3). **E2E smoke 스펙은 `@e2e-mock`이 없어 이 레인에서 정의상 제외**된다(§5.2-a).
- 선택 스코프에 없는 방법론과는 조합하지 않는다(_index §1).

## 7. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(system testing) — official-standard, HIGH. IEEE 829-2008 §3.1.37 — official-standard(철회·정의 유효). Fowler Practical Test Pyramid/SubcutaneousTest(push-down) — blog, MED~canonical. SWE@Google ch.11(large) — vendor-doc, MED.
- **caveat**: "이 버그는 E2E여야 잡는다"는 통념은 반증됨 — 값싼 unit이 더 많은 경계를 커버(RCA·비용 우위). E2E 유지비 "N배" 류 수치는 출처 0(folklore) — 인용 금지. 비율% 하드코딩 금지.
- **caveat(E2E smoke live 전용)**: §5.2-a는 **근거에서 유도된 규칙이 아니라 사용자 운영 결정**이며, MinimumCD·Fowler의 게이트 결정론·외부 의존 0 권고와 **상충**한다. 근거로 정당화하지 않고 상충·대가(자동 차단 상실)를 병기한다. 효과 수치("live smoke로 장애 N% 조기 포착")는 근거 0 — 인용 금지.
