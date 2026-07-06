# 방법론 카드 — Smoke

> **축 카드(방법론)**. 계층과 직교 — "어떤 테스트가 **Smoke suite 선택**에 드는가"만 정한다(계층 무관). 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 실체화 문법은 principles §3.5, 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **durable tag + 명명된 선별 서브셋**. 넓고 얕은(broad-shallow) 배포 게이트 — "이 빌드를 더 테스트할 가치가 있나?"의 go/no-go.

## 2. 멤버십 기준 (어떤 테스트가 Smoke에 드는가) — AND/우세
- [ ] **main functionality의 정상 경로(happy path)**만, **표면 수준**(깊은 검증·경계값·edge를 하면 smoke 아님).
- [ ] **showstopper**: "이 기능이 깨지면 이후 테스트가 무의미해지는가" = 예. 화이트리스트 예: 인증/로그인, 핵심 내비게이션, DB read/write, 핵심 트랜잭션, 핵심 외부 통합.
- [ ] commit/배포 게이트 smoke는 **결정론적·외부 의존 0**(느리거나 flaky면 nightly/full acceptance로).

## 3. 실체화 & CI 배치 (principles §3.5)
- **durable 태그**: `@smoke` 토큰 → 러너 네이티브 부여 + `test:smoke` 셀렉터 스크립트(Playwright `{tag}`·`--grep`, Vitest `{tags}`·`--tags-filter`, Jest 이름패턴/파일명·`--selectProjects` — §3.5.2). 셀렉터 실행으로 분리 검증(§3.5.4).
- **CI 배치**: post-deploy(staging/canary) 넓고 얕게 + PR-gate 소수(§3.5.5). 배포를 막는 게이트는 빠르고 신뢰도 높아야.

## 4. 오라클 기대
- **얕음**(reachability/no-crash + 최소 값). "초록=검증" 오독 금지 — 완전 행위 검증으로 취급하지 않는다. 스모크/동어반복 어서션 금지(§5-4).

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Smoke × Integration = STRONG**(정본), **Smoke × E2E = STRONG(조건부)**(크리티컬 여정 happy-path; flaky면 nightly로 — 단 nightly 미선택이면 배정 말고 '추가 안 함'+확장 문의), **Smoke × Unit = WEAK**(unit은 게이트 전량 실행이라 별도 선별 저부가).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(smoke-test) — official-standard, HIGH. Fowler DeploymentPipeline(작은 smoke suite) — blog authoritative, MED. MinimumCD(게이트 결정론·외부의존0) — community-standard, MED.
- **caveat**: **smoke = sanity 는 ISTQB 동의어** — "broad-shallow/narrow-deep" 구분은 컨벤션(folklore)·표준 아님(병기 필수). "smoke가 릴리스 50% 단축·버그 80% 조기포착" 류 수치는 folklore(출처 0) — 인용 금지. smoke 실행시간 3~7분/15~30분은 소스마다 다름(대략치만). 비율% 하드코딩 금지.
