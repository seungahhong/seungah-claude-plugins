# 방법론 카드 — Sanity (변경-스코프 선택 레인 · PR 전 실행)

> **축 카드(방법론)**. 계층과 직교 — "어떤 테스트가 **Sanity 선택**에 드는가"만 정한다(계층 무관). 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 실체화·대상 산정 절차는 principles §3.5.3, 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **transient 선택 (durable 태그 아님)**. **PR 올리기 전에, 이번 변경이 건드린 페이지/컴포넌트만** 좁게 다시 돌린다.
- ⚠️ **ISTQB상 sanity ≡ smoke 동의어** → 독립 방법론 근거 없음. 이 하네스는 sanity를 **(b) 변경 국소 confirmation + change-scoped 선택**으로만 운영한다(재정의).
- **운영 배치 = change-scoped PR job**(unit/integration blocking + 매핑된 `@e2e-mock` non-blocking). ⚠️ **표준 근거가 아니라 이 하네스의 운영 결정**이다 — ISTQB/ISO에 sanity의 CI 스테이지 규정은 없다(산출물에 병기).
- **선택 레인이지 생성 조합이 아니다** — 조합 강도표([`_index.md`](_index.md) §3)에서 Sanity 열이 DEGEN인 것은 "sanity 전용 테스트를 새로 만들지 않는다"는 뜻이고, 이 카드의 **실행 선택**과는 다른 축이다(모순 아님).

## 2. 멤버십 기준 (어떤 테스트가 Sanity 실행에 드는가) — transient·호출 시점 조립

**대상 산정 3단계**(principles §3.5.3, 실패 시 **넓히는 방향으로만** 폴백):

1. **변경 파일** — PR job은 `git diff --name-only origin/<base>...HEAD`(three-dot), 로컬은 `git diff --name-only`. **`<base>`는 CI의 PR base 변수 → 기본 브랜치 감지(`git symbolic-ref refs/remotes/origin/HEAD`) 순으로 정하고, 실패하면 추측 말고 문의**(잘못된 base = 조용한 under-selection).
2. **역참조 확장 = 관련 페이지/컴포넌트** — 변경 파일을 **import하는 상위 페이지/컴포넌트**의 테스트까지 포함한다(컴포넌트를 고치면 그것을 쓰는 페이지가 깨지므로). 1순위 러너 네이티브 임포트 그래프(Jest `--findRelatedTests`, Vitest `--related`, Playwright `--only-changed` — 정확 플래그·버전 **확인 필요**), 2순위 grep 기반 import 역참조(1홉 이상).
   - ⚠️ 역참조는 **원리상 불완전**(barrel re-export·동적 import·별칭 경로·라우팅 규약) → 불확실하면 좁히지 말고 **전체(또는 durable 스위트) 폴백**.
3. **관련 페이지의 E2E — `@e2e-mock`만** — ⚠️ **E2E가 Phase 1 선택 스코프에 있을 때만 수행**한다(스코프 가드 [`_index.md`](_index.md) §1; 미선택이면 이 단계를 건너뛰고 "E2E 스코프 밖 — sanity 대상 아님" 표기 후 확장 문의 — E2E 경로도 받지 않았으므로 매핑이 성립하지 않는다). 매핑: ① 경로 미러(`src/pages/checkout/**` ↔ `e2e/checkout.spec.ts`) → ② 모호하면 스펙에 `@page:/checkout` 태그 부여를 **게이트 B로 제안** → ③ 둘 다 실패하면 `@e2e-mock` **전량 폴백**.
   - **`@e2e-live`는 sanity 대상이 아니다**(수동 on-demand 전용 — 외부 API 불안정이 PR을 막지 않게, [`layer-e2e.md`](layer-e2e.md) §5.2).

**성격 기준**:
- [ ] 직전 변경이 건드린 영역을 재확인한다(= confirmation/re-testing).
- [ ] **미변경 영역 보존** 확인이 목적이면 sanity 아님 → [`methodology-regression.md`](methodology-regression.md).

## 3. 실체화 (principles §3.5.3 — 태그 아님)
- **`@sanity` 태그를 코드에 심지 않는다(무-태그 가드).** 호출 시점에만 리스트로 물질화한다. (`@page:` 태그는 **대상 페이지 메타**이지 스위트 태그가 아니므로 가드 위반이 아니다.)
- **Phase 3 산출물(3종)**:
  1. `test:sanity:changed` — 변경+역참조 대상의 unit/integration 선택 실행.
  2. `test:sanity:e2e` — 매핑된 `@e2e-mock` 스펙 선택 실행(**E2E가 선택 스코프에 있을 때만 만든다** — 없으면 이 장치를 만들지 않는다).
  3. **CI PR job 스니펫** — **제안만**(CI yaml 직접 편집 금지). blocking step(1) + non-blocking step(2, `continue-on-error` 등가물).
- **부족분 생성**: 변경 관련 페이지/컴포넌트에 **테스트가 아예 없으면** 그 자리에서 새 테스트를 만든다(게이트 B). 단 **계층은 Phase 1 선택 스코프 안**에서만(스코프 가드 [`_index.md`](_index.md) §1), durable 방법론 태그는 **선택된 방법론 중에서만** 부여하고 없으면 **무-태그 기본체**로 두고 계획표에 그렇게 적는다(`@sanity`를 대신 붙이지 않는다).
- **차단성**: unit/integration 실패 = blocking, 매핑된 mock E2E 실패 = non-blocking 리포트(운영 결정 — 표준 아님).
- 스크립트·job 스니펫 추가도 코드/설정 변경이므로 **게이트 B 대상**이다. sanity는 durable 태그가 없어 "첫 테스트" 트리거가 성립하지 않으므로, 이 장치는 **게이트 A 승인 후 1회** 추가한다.

## 4. 오라클 기대
- **confirmation 오라클**: "실패했던/변경된 동작이 기대대로 통과"(기대=AC). 구현이 아니라 **AC 기준**으로 오검증(§5-1).
- 선택 레인이므로 **오라클은 원 테스트의 것을 그대로 계승**한다 — sanity라고 오라클을 얕게 낮추지 않는다.

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **생성 조합**: Sanity × {Unit, Integration} = DEGEN/WEAK, Sanity × E2E = DEGEN — **sanity 전용 테스트를 새로 만들지 않는다**(독립 근거 취약). 필요한 검증은 Regression(미변경 보존)/Smoke(게이트)로 라우팅 — **단 그 방법론이 선택 스코프 밖이면 배정 말고 '추가 안 함'+확장 문의(_index §1)**.
- **선택 레인**: 위 §2의 대상 산정으로 **이미 존재하는 테스트**(어느 계층이든)를 골라 PR 전에 돌린다. 이건 강도표의 판정 대상이 아니다.
- Sanity는 durable 스케줄/회귀와 **결합 셀을 신설하지 않는다**(transient이므로).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(sanity-test = smoke synonym; confirmation-testing) — official-standard, HIGH(동의어 사실)/MED(sanity=confirmation 매핑은 추론 다리).
- **caveat**: **"sanity가 smoke보다 깊다/좁고 깊다"는 folklore** — official-standard로 포장 금지. **PR job 배치·차단성 분리(unit/int blocking, mock E2E non-blocking)는 사용자 운영 결정**이지 표준·측정 근거가 아니다. **근거 못 찾음: 독립 방법론으로서의 sanity**(성격 규정만). 역참조 매핑의 완전성·"변경 관련 테스트만 돌려 CI 비용 N% 절감" 류 수치는 **인용하지 않는다**(selection은 볼륨을 줄이지만 이 하네스가 측정한 값이 아니다). 수치로 메우지 않는다.
