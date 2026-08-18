# 방법론 카드 — Smoke

> **축 카드(방법론)**. 계층과 직교 — "어떤 테스트가 **Smoke suite 선택**에 드는가"만 정한다(계층 무관). 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 실체화 문법은 principles §3.5, 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **durable tag + 명명된 선별 서브셋**. 넓고 얕은(broad-shallow) 배포 게이트 — "이 빌드를 더 테스트할 가치가 있나?"의 go/no-go.
- ⚠️ **이 카드는 계층에 따라 두 갈래로 갈린다**: **비-E2E smoke**는 위 정의대로 **CI 고정 스테이지의 자동 게이트**이고, **E2E smoke**는 **실제 API 연동 필수(live 전용)이자 CI 스테이지 없는 수동 체크포인트**다(§2-b·§3.2·principles §3.6.5-a). 이 카드의 서술은 별도 표기가 없으면 **비-E2E smoke 기준**으로 읽는다.

## 2. 멤버십 기준 (어떤 테스트가 Smoke에 드는가) — AND/우세 · **계층 무관**
- [ ] **main functionality의 정상 경로(happy path)**만, **표면 수준**(깊은 검증·경계값·edge를 하면 smoke 아님).
- [ ] **showstopper**: "이 기능이 깨지면 이후 테스트가 무의미해지는가" = 예. 화이트리스트 예: 인증/로그인, 핵심 내비게이션, DB read/write, 핵심 트랜잭션, 핵심 외부 통합.

### 2-b. 멤버십이 정해진 뒤 갈리는 API 경계 (배타 분기 — 체크리스트 아님)

위 두 기준으로 Smoke 멤버십이 정해지면, **그 테스트의 계층에 따라 API 경계가 배타적으로 갈린다**:

| 계층 | API 경계 | CI 배치 | 근거 지위 |
|---|---|---|---|
| **비-E2E**(주로 Integration) | **결정론적·외부 의존 0**(느리거나 flaky면 nightly/full acceptance로 이연) | `test:smoke` — PR-gate 소수·post-deploy | 권고 근거대로(MinimumCD·Fowler, MED) |
| **E2E** | **⚠️ 실제 API 연동 필수** — `@e2e-live` 부여, **`@e2e-mock` 금지**(mock·fixture 없음) | **없음** — 수동 `test:e2e:smoke:live` | **사용자 운영 결정**(principles §3.6.5-a) |

⚠️ 아래 칸(E2E)은 위 칸(비-E2E)의 "게이트 결정론·외부 의존 0" 권고와 **정면으로 상충**한다. 상충 사실을 산출물에 병기하고 "표준을 따른다"고 포장하지 않는다. 완화 요인은 **파이프라인 게이트가 아니라는 점**(외부계 불안정이 CI를 막지 않는다)이며, 그 대가로 **E2E smoke는 자동 차단을 하지 못하는 수동 체크포인트**가 된다. 또한 **E2E smoke는 flaky해도 nightly로 이연할 수 없다**(nightly는 `@e2e-mock` 스테이지) — flaky하면 여정을 좁히거나 대상 환경을 안정화하고, 그래도 안 되면 **`@e2e-mock` 회귀 스펙으로 분리**해 CI에서 돌린다.

## 3. 실체화 & CI 배치 (principles §3.5) — **비-E2E와 E2E가 갈린다**

### 3.1 비-E2E smoke (Unit/Integration)
- **durable 태그**: `@smoke` 토큰 → 러너 네이티브 부여 + `test:smoke` 셀렉터 스크립트(Playwright `{tag}`·`--grep`, Vitest `{tags}`·`--tags-filter`, Jest 이름패턴/파일명·`--selectProjects` — §3.5.2). 셀렉터 실행으로 분리 검증(§3.5.4).
- **CI 배치**: post-deploy(staging/canary) 넓고 얕게 + PR-gate 소수(§3.5.5). 배포를 막는 게이트는 빠르고 신뢰도 높아야.

### 3.2 E2E smoke (**live 전용** — principles §3.6.5-a)
- **태그**: `@smoke` + **`@e2e-live` 필수**. **`@e2e-mock` 부여 금지**. mock 주입(`page.route` 등)을 걸지 않고 fixture도 만들지 않는다.
- **CI 배치**: **없음.** PR-gate·post-deploy·nightly 어디에도 넣지 않는다. `test:smoke`가 이 스펙을 끌어오면 분리 검증 실패로 처리한다(§3.5.4-5ⓐ).
- **실행**: 수동 on-demand 레시피 `test:e2e:smoke:live` — 예 `E2E_MODE=live BASE_URL=… playwright test --grep "(?=.*@smoke)(?=.*@e2e-live)"`. 모드 스위치 장치(env 분기·러너 project·라우팅 헬퍼)는 게이트 B 승인 대상이며, 스위치 없이 태그만 붙이면 phantom이다.
- **하네스 실행**: 게이트 B에서 **대상 환경(base URL)·테스트 계정/데이터 제공 + 그 자리 승인**이 모두 있을 때만 실제로 돌린다(하네스 live 호출의 유일한 예외, §3.6.5-b). 없으면 **UNVERIFIED**로 남긴다.
- **다중 멤버십 금지**: 같은 E2E 스펙에 `@regression`/`@nightly`를 겹치지 않는다(live 고정이라 그 스위트 CI 실행에서 빠지는 phantom membership) — 필요하면 `@e2e-mock` 스펙으로 **분리**해 계획표 두 행으로.
- **sanity 레인 제외**: sanity는 `@e2e-mock`만 고르므로 E2E smoke는 정의상 선택되지 않는다(누락 아님 — 표기).

## 4. 오라클 기대
- **얕음**(reachability/no-crash + 최소 값). "초록=검증" 오독 금지 — 완전 행위 검증으로 취급하지 않는다. 스모크/동어반복 어서션 금지(§5-4).
- **E2E smoke(live)**: 실제 응답이므로 값이 실행마다 달라질 수 있다 — **정확 출력 pinning 대신 여정 도달·상태 전이·계약 형태(필수 필드·타입·상태코드)** 수준으로 잡는다. 특정 시점 응답값을 굳히면 환경 변화에 무너지는 오라클이 된다.

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Smoke × Integration = STRONG**(정본), **Smoke × E2E = STRONG(조건부)**(크리티컬 여정 happy-path), **Smoke × Unit = WEAK**(unit은 게이트 전량 실행이라 별도 선별 저부가).
- ⚠️ **Smoke × E2E의 "조건부"가 이제 성립하지 않는다** — 조건이었던 *결정론·게이트 적격*을 live 전용 결정이 깨뜨렸다(§2-b·§3.2). 이 조합을 만들 때는 강도 라벨과 별개로 **"자동 게이트가 아니라 수동 체크포인트"** 라는 대가를 계획에 적는다.
- ⚠️ **"flaky하면 nightly로"라는 종래 탈출구는 E2E smoke에 적용되지 않는다** — nightly는 `@e2e-mock` 스테이지이고 E2E smoke는 live 전용이라 그리로 옮길 수 없다. 여정을 좁히거나 대상 환경을 안정화하고, 그래도 안 되면 **`@e2e-mock` 회귀/nightly 스펙으로 분리**한다(선택 스코프에 그 방법론이 없으면 배정 말고 '추가 안 함'+확장 문의).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(smoke-test) — official-standard, HIGH. Fowler DeploymentPipeline(작은 smoke suite) — blog authoritative, MED. MinimumCD(게이트 결정론·외부의존0) — community-standard, MED.
- **caveat**: **smoke = sanity 는 ISTQB 동의어** — "broad-shallow/narrow-deep" 구분은 컨벤션(folklore)·표준 아님(병기 필수). "smoke가 릴리스 50% 단축·버그 80% 조기포착" 류 수치는 folklore(출처 0) — 인용 금지. smoke 실행시간 3~7분/15~30분은 소스마다 다름(대략치만). 비율% 하드코딩 금지.
- **⚠️ 근거와의 상충 명시(E2E smoke live 전용)**: MinimumCD·Fowler의 게이트 결정론·외부 의존 0 권고와 **상충하는 사용자 운영 결정**이다(근거로 정당화하지 않는다). 상충을 줄이는 장치는 **고정 CI 게이트에 두지 않는 것**뿐이며, 그 대가는 **자동 차단 상실**이다. "live smoke로 장애 N% 조기 포착" 류 효과 수치는 **근거 0 — 인용 금지**. live 통과는 **실행 시각·대상 환경에 한정된 관측**이지 항구적 연동 보증이 아니다.
