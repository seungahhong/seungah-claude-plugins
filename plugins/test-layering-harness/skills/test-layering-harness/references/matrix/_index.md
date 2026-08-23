# 방법론 · 계층 축 카드 — 인덱스 & 조합 라우팅

> 이 디렉토리는 방법론×계층을 **12개 교집합 셀로 미리 채우지 않는다.** 대신 **두 축을 각각 카드로** 둔다 — **방법론 카드 4개**(`methodology-{smoke,sanity,regression,nightly}.md`)와 **계층 카드 3개**(`layer-{unit,integration,e2e}.md`). 각 AC는 **필요한 시점에** 이 축 카드들을 **조합**해 "상황에 맞는 테스트"를 골라 추가한다 — **단, 사용자가 Phase 1에서 선택한 방법론·계층 안에서만.**
>
> 근거 원장은 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md)(2025+ 공식표준/논문, 인용 교정 완료), 상위 원리는 [`../test-layering-principles.md`](../test-layering-principles.md). 오케스트레이터(`../../SKILL.md`)는 Phase 2에서 §2 라우팅 절차를 따른다.

## 0. 왜 축 카드인가 (직교성)

**계층은 개별 테스트의 durable 속성**(scope=무엇을 실제로 쓰고 무엇을 double하나 + size/hermeticity), **방법론은 그 테스트 위에 얹히는 selection/tag**(sanity는 transient)다. ISO/IEC/IEEE 29119-1:2022 §4.4.6은 regression을 "test level이 아니라 design/execution choice"로 규정한다. 두 축은 **직교**하므로 — 12개 교집합은 "독립된 4번째 유형"이 아니라 두 축의 **조합**이다. 그래서 **셀을 미리 12개로 물질화하지 않고, 축 카드 7개를 두고 라우팅 시점에 조합**한다:

- **계층 카드(3)** = "어떤 AC 슬라이스가 이 계층 테스트가 되는가"(방법론 무관).
- **방법론 카드(4)** = "어떤 테스트가 이 suite 선택에 드는가"(계층 무관).
- **조합** = (계층 × 방법론)은 라우팅 시 §3 **조합 강도 lookup**으로 상황에 맞게 고른다. 한 테스트는 여러 방법론 suite에 들 수 있다(다중 멤버십).

**⚠️ Nightly 정합성**: "nightly"는 엄밀히는 방법론(test type)이 아니라 **CI-stage/스케줄 지연 축**이다(ISTQB/ISO에 nightly test type 없음). 방법론 카드로 두되 "게이트에서 빼 스케줄로 미룬다"는 라우팅 결정으로 읽는다([`methodology-nightly.md`](methodology-nightly.md)).

## 1. 스코프 가드 (핵심 불변식 — 선택 안에서만 추가)

**Phase 1에서 사용자가 체크박스로 고른 (선택 방법론 집합) × (선택 계층 집합)이 유일한 허용 스코프다. 이 밖으로는 어떤 테스트도 추가하지 않는다.**

- 어떤 AC 슬라이스의 "자연스러운" 계층/방법론이 **선택되지 않았다면**, 임의로 추가하지 않는다.
  - 선택된 계층으로 **push-down/up**해 담을 수 있으면 담는다(예: E2E 미선택 시 여정 검증을 Integration으로 내림).
  - 담을 수 없으면 **"선택 스코프 밖 — 추가 안 함"**으로 계획표에 표시하고, 사용자에게 **스코프 확장 여부를 묻는다**(먼저 추가하고 사후 통보 금지).
- 방법론도 동일: 미선택 방법론에는 태깅/배치하지 않는다(예: Nightly 미선택 시 무거운 테스트를 nightly로 몰지 않고, 스코프 내 처리 방법을 제시하거나 확장 문의).
- 이 가드는 3개 승인 게이트와 **동급 불변식**이다 — 스코프를 넘는 추가는 게이트 위반이다.

## 2. AC 라우팅 절차 (Phase 2의 결정 알고리즘)

각 AC(Given-When-Then)에 대해:

**Step 0 — 스코프 확정.** §1의 (선택 방법론) × (선택 계층)을 이 AC 처리의 경계로 고정한다.

**Step 1 — AC를 슬라이스로 쪼갠다.** 하나의 AC를 하나의 테스트로 등치하지 않는다(principles §4). 판정 로직·협업·여정 관점을 후보 슬라이스로 나눈다.

**Step 2 — 각 슬라이스에 계층을 배정한다** — **선택된 계층 중에서만**. [`layer-unit.md`](layer-unit.md) / [`layer-integration.md`](layer-integration.md) / [`layer-e2e.md`](layer-e2e.md)의 **AC 포함/제외 기준**으로 판정한다.
- 자연 계층이 미선택이면 §1 스코프 가드를 적용(선택 계층으로 push-down/up, 불가하면 표시+문의).
- 가드: `small=unit / medium=integration / large=system` 1:1 매핑 금지. "acceptance" 의도가 E2E를 강제하지 않는다(level≠type).

**Step 3 — 각 (슬라이스, 계층)에 방법론 멤버십을 부여한다** — **선택된 방법론 중에서만**(비배타·다중). 방법론 카드([`methodology-regression.md`](methodology-regression.md) 등)의 멤버십 기준으로:
- Regression?(변경 traverse/보존 — 대부분) · Smoke?(happy·표면·결정론·showstopper) · Nightly로 이연?(느림/비쌈/flaky/cross-browser/exhaustive/fuzz) · Sanity?(durable 아님 — transient change-scope, `@sanity` 안 심음).
- 미선택 방법론에는 배정하지 않는다(§1).

**Step 4 — 상황에 맞는 테스트를 선택(조합)한다.** (계층 × 방법론) 조합의 **강도 lookup**(§3)을 보고, **선택 스코프 안에서** 가장 적합한 조합으로 이 슬라이스의 테스트를 구체화한다. WEAK/DEGENERATE 조합은 억지로 만들지 않고 스코프 내 STRONG 조합으로 옮기되, 스코프 내 STRONG 조합이 아예 없으면(선택이 WEAK만 산출) 억지로 만들지 말고 §1 폴백('추가 안 함' 표기+확장 문의). 오라클 강도는 그 계층 카드 §4 + 방법론 카드의 오라클 기대를 결합한다.

**Step 4-b — API 경계를 확정한다**(principles §3.6). 계층이 기본값을 강제한다: **Unit/Integration = 항상 mock**(① 네트워크 인터셉터 우선 / ② 모듈 double, fixture 3단 폴백·출처 표기, live 호출 금지 — 정의상 계층 자격 문제), **E2E = 모드 태그**(`@e2e-mock` 기본, 사용자가 명시 요청한 시나리오에만 `@e2e-live` 병기 — live는 고정 CI 스테이지 없이 수동 on-demand).
- **⚠️ 이 슬라이스가 (E2E × Smoke)면 모드가 고정된다** — `@e2e-live` 필수·`@e2e-mock` 금지·CI 스테이지 없음·수동 레시피(§3-d). 이 행에는 fixture 소스 대신 **대상 환경·테스트 계정 확보 여부**를 적고, `@regression`/`@nightly`를 같은 스펙에 겹치지 않는다(필요하면 `@e2e-mock` 스펙으로 분리해 두 행).

**Step 4-c — DOM 셀렉터를 확정한다**(principles §3.7·§3-e). 이 테스트가 DOM을 조회하면 **사다리에서 쓸 최상위 순위**를 정하고, `getByTestId`(8)·`locator`(9)를 쓸 수밖에 없으면 **왜 상위 쿼리가 불가능한지**를 함께 적는다. DOM이 없으면 `해당 없음(비-DOM)`. 러너 API 이름은 §3.7.3 어댑터로 옮긴다.

**Step 5 — 계획표 행으로 적는다.** `AC · 계층(카드) · 방법론(카드·태그+셀렉터) · 조합 강도 · API 경계(mock/live·경계기법·fixture 소스) · DOM 셀렉터(순위·사유) · 오라클 · 파일 · GWT · 근거`. ⚠️ '방법론' 열의 *셀렉터*(`--grep @smoke`)와 'DOM 셀렉터' 열(`getByRole` 등)은 **다른 것**이다. 한 슬라이스가 여러 방법론 suite에 속하면 membership 대수(principles §3.5.4 옵션 A/B)로 표기.

## 3. 조합 강도 lookup (계층 × 방법론) — Step 4에서 참조

**이 표는 "새 테스트를 어떤 조합으로 *만드는가*"의 강도다**(생성 축). "이미 있는 테스트를 *골라 돌리는*" 선택 레인(=sanity, §3-b)은 이 표의 판정 대상이 아니다. 정직성상 모든 조합이 실무에서 유용하지 않으므로, **선택 스코프 안에서** STRONG 조합에 집중하고 WEAK/DEGENERATE 조합은 비운다(근거: [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §3·§5).

| 계층 \ 방법론 | Smoke | Sanity | Regression | Nightly |
|---|---|---|---|---|
| **Unit** | WEAK | DEGEN/WEAK | **STRONG**·최고위험오라클 | DEGEN(빈셀) |
| **Integration** | **STRONG** | DEGEN/WEAK | **STRONG** | STRONG-ish |
| **E2E** | STRONG(조건부) | DEGEN | STRONG·대개nightly이연 | **STRONG**(best) |

- **실무 정합 최강**: Smoke×Integration · Regression×{Unit,Integration} · Nightly×E2E.
- **WEAK/DEGENERATE(억지 생성 금지)**: Sanity 전 조합(ISTQB상 smoke 동의어 → transient change-scope로만) · Nightly×Unit(unit은 게이트 전량 실행) · Smoke×Unit.
- 이 표는 **조합의 강도 참고**이지 12개 셀 파일이 아니다 — 라우팅 시점에 축 카드를 조합해 상황에 맞는 것만 만든다.

### 3-b. Sanity = 실행 선택 레인 (강도표와 다른 축 — 모순 아님)

**Sanity 열이 전부 DEGEN인 것은 "sanity 전용 테스트를 새로 만들지 않는다"는 뜻이지, "sanity를 운영하지 않는다"는 뜻이 아니다.** sanity는 **이미 존재하는 테스트를 변경 스코프로 골라 PR 전에 돌리는 선택 레인**으로 1급이다([`methodology-sanity.md`](methodology-sanity.md) §2, principles §3.5.3):

- 대상 = 변경 파일 → **역참조로 상위 페이지/컴포넌트까지** → 매핑된 **`@e2e-mock`** 스펙(불확실하면 넓히는 폴백). ⚠️ **3단계(E2E)는 E2E가 선택 스코프에 있을 때만** — 미선택이면 건너뛰고 unit/integration으로만 구성 후 확장 문의(§1 스코프 가드).
- 배치 = **change-scoped PR job**(unit/integration **blocking** + mock E2E **non-blocking**). ⚠️ **표준 근거 아님 — 하네스 운영 결정**(ISTQB/ISO에 sanity 스테이지 규정 없음).
- 코드에 `@sanity` 태그를 심지 않는다(무-태그 가드). 변경 관련 페이지/컴포넌트에 테스트가 **아예 없을 때만** 선택 스코프 안에서 새로 만든다(게이트 B).

### 3-c. API 경계 축 (mock / live) — principles §3.6

계층·방법론과 **직교하는 테스트 속성**이다(4번째 축 카드가 아니다):

> 첫 열은 **계층**이되 E2E 두 행은 **(계층 × 방법론 멤버십) 조합**으로 갈린다 — **4번째 유형을 만드는 게 아니라** 두 축의 조합에 붙는 속성이 다를 뿐이다(§0 직교성 유지).

| 계층 (E2E는 방법론 멤버십으로 갈림) | API 경계 | 태그 |
|---|---|---|
| Unit · Integration | **항상 mock**(예외 없음 — live로 나가면 정의상 계층 자격 상실) | 불필요 |
| **E2E × Smoke** | **항상 live**(실제 API 연동 필수) — **`@e2e-mock` 금지**·CI 스테이지 없음·수동 on-demand | `@e2e-live` **필수** |
| E2E(그 밖) | **모드 선언** — `@e2e-mock` 기본(CI 결정론) / `@e2e-live`는 명시 요청 시만·**수동 on-demand** | 필수 |

- mock 경계: ① 네트워크 인터셉터 우선 → ② 모듈 double. fixture: ① 기존 재사용 → ② 사용자 제공 → ③ 스키마 유도(**`[실측 캡처 아님]` 표기**). 하네스는 fixture 확보용 live 호출을 하지 않는다.
- **mock 통과 ≠ 연동 검증** — fixture는 캡처 시점 스냅샷이라 계약 drift를 정의상 못 잡는다. 연동 장치는 `@e2e-live` 수동 실행뿐(§3.6.6).

### 3-d. E2E smoke = 실제 API 연동 필수 (live 전용) — principles §3.6.5-a·§3.6.5-b

**`@smoke` 멤버십을 가진 E2E 스펙은 요청 없이도 `@e2e-live`가 강제되고 `@e2e-mock`을 갖지 않는다.** 사용자 운영 결정이며 §3-c 기본값의 유일한 예외다. 라우팅 시 반드시 함께 적는 귀결:

1. **CI 스테이지 없음** — `test:smoke`(비-E2E만)·`test:regression`·`test:nightly` 어디에도 안 들어간다. 수동 레시피 `test:e2e:smoke:live`만.
2. **자동 배포 게이트가 아니다** — 승격 전 **사람이 돌리는 수동 체크포인트**. "게이트가 지켜준다"고 쓰지 않는다.
3. **sanity 레인 제외** — 레인은 `@e2e-mock`만 고르므로 정의상 빠진다(누락 아님 — 표기, §3-b).
4. **다중 멤버십 금지** — 한 E2E 스펙에 `@smoke` + `@regression`/`@nightly`를 겹치지 않는다(phantom membership). 필요하면 `@e2e-mock` 스펙으로 **분리**해 두 행으로.
5. **결정론 권고와 상충** — "배포 게이트는 결정론·외부 의존 0"(MinimumCD·Fowler, MED)과 충돌한다. 근거로 정당화하지 않고 상충·대가를 병기한다.
6. **하네스 실행은 조건부** — 게이트 B에서 **대상 환경 + 테스트 계정/데이터 + 그 자리 승인**이 모두 있을 때만 실제로 돌린다(하네스 live 호출의 유일한 예외). 없으면 **UNVERIFIED**. 실패는 **테스트 결함 / 코드 결함 / 환경·외부계** 3분류로 구분한다.

### 3-e. 셀렉터 우선순위 축 (DOM 조회) — principles §3.7

API 경계와 마찬가지로 **계층·방법론과 직교하는 테스트 속성**이다(축 카드 아님). **DOM을 조회하는 테스트에만** 적용하고, 비-DOM(순수 함수 unit·서버 API integration·CLI)은 `해당 없음(비-DOM)`으로 적는다.

| 사다리 | 쿼리 | 규칙 |
|---|---|---|
| **시각 요소·사용자 인터랙션** | `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` | 위에서부터 시도 |
| **HTML5·ARIA 속성** | `getByAltText` > `getByTitle` | 속성을 찾을 때의 별도 사다리 |
| **테스트 ID** | `getByTestId` | **위로 불가능한 값을 찾을 때만** · 속성명은 **팀 합의**(감지→문의) |
| **최후 수단** | `locator('[data-…]')` · `locator('[class*="…"]')` | 사다리로 불가능할 때만 · **사유·결합 비용 표기** |

- **한 단계씩 내려가고 8·9번은 사유를 적는다.** "편해서" 내려가지 않는다.
- **러너 이름은 어댑터로**(§3.7.3) — Playwright는 `getByLabel`/`getByPlaceholder`, **`getByDisplayValue` 없음**(상위 순위로 찾고 값은 어서션).
- **제품 코드에 testid 추가는 게이트 B 별도 승인**(테스트 파일 밖의 변경).
- **기존 테스트 셀렉터는 무단 개조 금지** — 보고 + 전환 patch 제안.
- 정직성: 근거는 vendor-doc(MED)의 **설계 의도**이지 측정된 우월성이 아니다 — **효과 수치·준수율 점수화 금지**, 접근성 개선을 성과로 주장하지 않음, **셀렉터는 오라클이 아님**.

## 4. 축 카드 목록

| 방법론 카드(4) | 계층 카드(3) |
|---|---|
| [`methodology-smoke.md`](methodology-smoke.md) — 넓고 얕은 배포 게이트(durable-tag) | [`layer-unit.md`](layer-unit.md) — 단일 unit behavior·단일 프로세스 |
| [`methodology-sanity.md`](methodology-sanity.md) — 변경 국소 재확인(transient·무-태그) | [`layer-integration.md`](layer-integration.md) — 인터페이스·데이터 교환·단일 머신 |
| [`methodology-regression.md`](methodology-regression.md) — 미변경 비회귀(durable-tag·계층 직교) | [`layer-e2e.md`](layer-e2e.md) — 완결 시스템·사용자 여정 |
| [`methodology-nightly.md`](methodology-nightly.md) — 스케줄 이연(CI-stage 축) | |

## 5. 정직성 불변식 (모든 축 카드가 계승)

- **스코프 가드** — 선택된 방법론·계층 밖으로 테스트를 추가하지 않는다(§1). 필요해 보이면 추가 말고 확장 문의.
- **셀은 미리 12개로 물질화하지 않는다** — 축 카드 7개를 라우팅 시 조합. 조합은 다중 멤버십.
- **smoke = sanity 는 ISTQB 동의어** — "smoke=넓고얕음/sanity=좁고깊음"은 컨벤션(folklore)이지 표준 아님. 병기 필수.
- **비율% 하드코딩 금지**(70/20/10 folklore). 조합 크기는 저장소 감지·리스크로만.
- **prioritization은 CI 비용을 못 줄인다**(latency만·정의상 — 재정렬은 총 실행량 불변). 절감은 selection·batching(무손실, ESEC/FSE 2023 arXiv:2308.13129)·병렬화로.
- **근거 없는 효과 수치 금지**. 신뢰도(HIGH/MED/LOW)·SOURCE-TIER·folklore·모순 표기 계승.
- **WEAK/DEGENERATE 조합은 정직히 비움** — 있는 척하지 않는다.
- **unit/integration은 live API를 호출하지 않는다** — 규약 이전에 계층 정의의 귀결(§3-c).
- **mock 통과 ≠ 연동 검증** — fixture는 캡처 시점 스냅샷. "mock 전부 초록 = 연동 정상"으로 쓰지 않고, 연동 장치는 `@e2e-live` 수동 실행뿐임을 병기(§3-c).
- **셀렉터는 사다리를 지키되 점수화하지 않는다**(§3-e) — `getByRole`부터 시도하고 `getByTestId`·`locator`는 **불가능을 확인한 뒤 사유와 함께**. 러너 API 이름은 어댑터로 옮기고(없는 API를 부르지 않음), testid 속성명은 **팀 합의**이며 **제품 코드 변경은 별도 승인**. 근거는 vendor-doc의 **설계 의도**이지 측정된 우월성이 아니다 — 효과 수치·준수율 % 금지, **셀렉터는 오라클이 아님**.
- **E2E smoke는 live 전용이고 자동 게이트가 아니다**(§3-d) — `@e2e-mock` 부여 금지·CI 스테이지 없음·"배포 게이트가 지켜준다" 서술 금지(수동 체크포인트). **결정론 권고와 상충하는 운영 결정**임을 병기하고 근거로 정당화하지 않는다. **미실행은 UNVERIFIED**, live 통과는 **실행 시각·대상 환경 한정 관측**, live 실패는 **3분류**(테스트/코드/환경·외부계). 효과 수치("live smoke로 장애 N% 조기 포착") 인용 금지.
- **스키마 유도 fixture는 `[실측 캡처 아님]` 표기 유지**, 정적 live-호출 검사는 **우회 가능**하다는 한계를 함께 표기(통과=네트워크 미접속 증명 아님).
- **sanity 배치·차단성은 운영 결정**(표준 근거 아님)임을 병기하고, 역참조 매핑이 불확실하면 **좁히지 말고 폴백**(§3-b).
