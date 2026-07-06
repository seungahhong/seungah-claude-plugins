# 방법론 카드 — Sanity

> **축 카드(방법론)**. 계층과 직교 — "어떤 테스트가 **Sanity 선택**에 드는가"만 정한다(계층 무관). 계층 판정은 [`layer-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §2.

## 1. 정체 (selection 성격)
- **transient 선택 (durable 태그 아님)**. 변경 국소 재확인 — 표적 수정/핫픽스 직후 "그 변경이 건드린 것만" 좁게. **고정 CI 스테이지 없음**.
- ⚠️ **ISTQB상 sanity ≡ smoke 동의어** → 독립 방법론 근거 없음. 이 하네스는 sanity를 **(b) 변경 국소 confirmation + change-scoped 선택**으로만 운영한다(재정의).

## 2. 멤버십 기준 (어떤 테스트가 Sanity에 드는가) — transient·호출 시점 조립
- [ ] 직전 변경이 **특정 영역을 건드렸고**, 그 변경으로 **실패했던/새로 추가된 케이스**를 재실행해 픽스 성공을 확인한다(= confirmation/re-testing).
- [ ] **change-scoped**: `git diff --name-only` → 테스트 경로 매핑(1순위·러너 무관)으로 변경 traverse하는 것만 조립. 매핑 실패 시 **전체(또는 durable 스위트) 폴백**(under-selection 회피).
- [ ] **미변경 영역 보존** 확인이 목적이면 sanity 아님 → Regression.

## 3. 실체화 (principles §3.5.3 — 태그 아님)
- **`@sanity` 태그를 코드에 심지 않는다(무-태그 가드).** 호출 시점에만 리스트로 물질화 — 계획표엔 "레시피 command + 폴백"만 기록.
- 러너 네이티브 change-selection(Jest `--onlyChanged`/`--findRelatedTests`, Vitest `--changed`/`--related`, Playwright `--only-changed`)은 정확 플래그·버전 **확인 필요** 표기.
- CI: 고정 스테이지 없음 — 주 사용처는 pre-commit/pre-push·hotfix on-demand.

## 4. 오라클 기대
- **confirmation 오라클**: "실패했던 케이스가 이제 통과"(기대=픽스된 동작). 구현이 아니라 **AC 기준**으로 오검증(§5-1).

## 5. 이 방법론 × 계층 조합 (선택된 계층 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Sanity × {Unit, Integration} = DEGEN/WEAK**, **Sanity × E2E = DEGEN** — 모두 독립 근거 취약. smoke 동의어로 흡수되거나 change-scoped confirmation으로만. 억지로 채우지 말고 Regression(미변경 보존)/Smoke(게이트)로 재라우팅 — **단 그 방법론이 선택 스코프 밖이면 배정 말고 '추가 안 함'+확장 문의(_index §1)**.
- Sanity는 durable 스케줄/회귀와 **결합 셀을 신설하지 않는다**(transient이므로).
- 선택 스코프에 없는 계층과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(sanity-test = smoke synonym; confirmation-testing) — official-standard, HIGH(동의어 사실)/MED(sanity=confirmation 매핑은 추론 다리).
- **caveat**: **"sanity가 smoke보다 깊다/좁고 깊다"·"고정 CI 스테이지"는 folklore/vendor-practice** — official-standard로 포장 금지. **근거 못 찾음: 독립 방법론으로서의 sanity**(성격 규정만). 수치로 메우지 않는다.
