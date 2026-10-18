---
name: test-layering-harness
description: >-
  인수조건(AC, Given-When-Then)을 방법론(Smoke/Sanity/Regression/nightly)×계층(Unit/Integration/E2E) 축 카드로 조합해 CI 단계별 테스트
  계획을 세우고, 계획→개별→최종 3단계 승인 게이트로 테스트를 하나씩 생성·적용·확정하는 도메인 무관 인터랙티브 스킬. 사용자가 "인수조건으로 테스트 짜줘", "이 AC를 unit/통합/E2E로
  나눠서", "스모크/회귀 테스트 계획 세워줘", "테스트 피라미드(트로피)로 계층 잡아줘", "테스트를 하나씩 승인받으며 추가", "AC 기반 계층별 테스트 스위트", "CI 단계별로 어떤 테스트를
  어디에 둘지" 같은 요청을 하거나 테스트 계층 전략·CI 배치를 논할 때 반드시 사용한다.
allowed-tools: Read, Grep, Glob
---

# test-layering-harness

인수조건(AC)을 **방법론(Smoke/Sanity/Regression/nightly) × 계층(Unit/Integration/E2E)** 택소노미로 계층별 테스트 스위트로 계획하고, **계획 → 개별 → 최종의 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정한다. 도메인 무관·독립 실행.

**왜 이렇게 만드는가**: AI가 테스트를 자동 생성할수록 위험은 "작성"이 아니라 "무엇을, 어느 층에, 어떤 오라클로 검증하는가"로 옮겨간다. 근거([`references/research/test-strategy-research.md`](references/research/test-strategy-research.md) · [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md))가 반복해 말하는 최대 리스크는 **오라클 강도** — LLM은 명세(기대)가 아니라 구현(실제 동작)을 굳혀 버그를 초록으로 은폐한다. 그래서 이 스킬은 (1) 테스트를 계층 택소노미로 **분해**하고, (2) 매 적용을 **사람이 승인**하며, (3) 오라클을 **오검증·실행 그라운딩**한다.

작업 원리·매트릭스·프리셋·오라클 가드·anti-pattern은 [`references/test-layering-principles.md`](references/test-layering-principles.md)에 있다. Phase 1~3에서 해당 절을 열어 근거를 인용하라.

**방법론·계층 축 카드(7개)**: 방법론×계층을 12개 셀로 미리 물질화하지 않고, **방법론 카드 4개**([`methodology-smoke.md`](references/matrix/methodology-smoke.md)·[`methodology-sanity.md`](references/matrix/methodology-sanity.md)·[`methodology-regression.md`](references/matrix/methodology-regression.md)·[`methodology-nightly.md`](references/matrix/methodology-nightly.md))와 **계층 카드 3개**([`layer-unit.md`](references/matrix/layer-unit.md)·[`layer-integration.md`](references/matrix/layer-integration.md)·[`layer-e2e.md`](references/matrix/layer-e2e.md))를 두고, **필요한 시점에 두 축을 조합**해 상황에 맞는 테스트를 고른다. 라우팅 절차·조합 강도 lookup·**스코프 가드**는 [`references/matrix/_index.md`](references/matrix/_index.md), 2025+ 근거 원장은 [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md). **셀은 조합(다중 멤버십)이지 독립된 4번째 유형이 아니다.** **⚠️ 스코프 가드**: 테스트는 **사용자가 Phase 1에서 선택한 방법론·계층 안에서만** 추가한다 — 밖으로는 임의 추가 금지(스코프 확장은 사용자에게 문의).

**API 경계 축(mock/live)**: 계층·방법론과 직교하는 **테스트 속성**이며 새 축 카드가 아니다([`references/test-layering-principles.md`](references/test-layering-principles.md) §3.6 = 단일 출처, 요약은 [`references/matrix/_index.md`](references/matrix/_index.md) §3-c·§3-d). **Unit/Integration = 항상 mock**(예외 없음 — live로 나가면 정의상 계층 자격 상실), **E2E = 모드 태그**(`@e2e-mock` 기본 / `@e2e-live`는 명시 요청 시만·수동 on-demand). **⚠️ 유일한 규칙 기반 예외 — E2E smoke(`@smoke` × E2E)는 `@e2e-live` 전용**(요청 없이도 강제·`@e2e-mock` 금지·CI 스테이지 없음·수동 레시피·게이트 B는 조건 충족 시에만 실제 실행): principles **§3.6.5-a**(규칙)·**§3.6.5-b**(실행 규약)·[`_index.md`](references/matrix/_index.md) §3-d. **sanity는 실행 선택 레인**이라 조합 강도표의 판정 대상이 아니다(§3-b).

**셀렉터 우선순위 축(DOM 조회)**: 역시 계층·방법론과 직교하는 **테스트 속성**이다([`references/test-layering-principles.md`](references/test-layering-principles.md) **§3.7 = 단일 출처**, 요약은 [`references/matrix/_index.md`](references/matrix/_index.md) §3-e). **DOM을 조회하는 테스트에만** 적용하고 비-DOM은 `해당 없음`이다. 사다리: **`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue`**(시각 요소·사용자 인터랙션) · **`getByAltText` > `getByTitle`**(HTML5·ARIA 속성) · **`getByTestId`**(위로 불가능할 때만) · **`locator`**(최후 수단·사유 표기).

---

## 진행 원칙 (전 구간 관통)

- **승인 게이트를 건너뛰지 않는다.** 이 스킬의 근본 계약이다: 계획 승인 없이 개별 적용 없음, 개별 승인 없이 파일 쓰기 없음, 최종 승인 없이 "반영" 없음.
- **제안만·정직하게.** 비율%(70/20/10)는 folklore이므로 하드코딩하지 않는다. 수치는 신뢰도(HIGH/MED/LOW)와 함께, 근거 없는 효과 수치("버그 80% 조기 포착" 등)는 인용하지 않는다. smoke=sanity는 ISTQB상 동의어임을 병기한다.
- **읽기 우선, 추측 금지.** 저장소 감지는 신호를 인용한다(파일 경로·설정). 확신이 낮으면 사용자에게 묻는다.
- **한 번에 한 테스트.** 개별 적용은 순차(병렬 아님) — 각 테스트를 실행해 결과를 확인하고 다음으로 간다.

---

## Phase 0 — 초기 문의 (Initial Inquiry)

**AC 선택지를 먼저 사용자에게 제시한다. 채굴·감지로 곧장 건너뛰지 않는다.** — 실행자가 사용자 문의를 생략하고 저장소에서 임의로 후보를 뽑아 진행하는 것이 이 스킬의 가장 흔한 실수다. 사용자가 정본 AC 문서(스토리·PRD·Gherkin)를 이미 갖고 있을 수 있으므로, 채굴은 사용자가 "없음"을 **고른 뒤에만** 한다.

### 1. 인수조건(AC) — 3지선다 명시 프롬프트

사용자의 최초 요청에 AC가 이미 인라인으로 포함돼 있으면 그것을 정본으로 삼고 이 프롬프트는 생략한다(재질문 금지). 그렇지 않으면 **반드시 아래 세 갈래를 제시하고 사용자의 선택을 기다린다**:

- **(a) 붙여넣기** — AC 내용을 대화에 직접 붙여넣기. → 그대로 정본.
- **(b) 파일·링크 경로** — AC 문서의 경로/링크(예: `docs/…`, `.claude/_docs/…`, 이슈·Notion 링크 내용)를 제공. → Read로 읽어 정본으로.
- **(c) 없음 → 저장소에서 후보 AC 채굴** — (a)·(b)가 없을 때만. 저장소에서 후보를 찾는다(`.claude/_docs/**`·PRD·스토리·이슈·기존 테스트의 `describe/it` 제목·컴포넌트가 드러내는 사용자 동작). 찾은 후보를 요약 제시하고 **"이 후보로 진행할까요, 아니면 의도를 직접 알려주시겠어요?"로 다시 확인**한다. 아무것도 없으면 한 줄 의도라도 받아 최소 AC로 승격한다.

즉 (c)는 "패스(skip)" 경로지만 **묵시적 기본값이 아니라 사용자가 명시적으로 고른 선택**이어야 한다.

### 2. 테스트 반영할 개발 환경(경로) — 스킵 가능

- 경로를 주면 그 경로를, **미입력(스킵) 시 현재 프로젝트 경로**를 기준으로 삼는다(어느 쪽인지 명시 보고).
- 대상 경로에서 테스트 러너·실행 명령·테스트 디렉토리 관습을 감지한다(`package.json` scripts, jest/vitest/mocha/playwright/cypress/pytest/go test/junit, `__tests__`·`*.test.*`·`*.spec.*`·`e2e/`). **감지 결과와 부재한 러너(예: "unit 러너 없음, Playwright E2E만")를 한 줄로 보고**한다 — 이는 Phase 1 프리셋·tier 선택에 직접 영향을 준다. 실패·모호 시 사용자에게 확인.
- **mock 인프라도 함께 감지한다**(§3.6 배선용): 네트워크 경계 인터셉터(msw/nock/WireMock·python `responses`·`respx`·go `httptest`) 유무, 기존 **fixture 배치 관습**(`fixtures/`·`__mocks__/`·`*.fixture.*`), 기존 테스트의 **live 호출 흔적**(외부 URL 리터럴). 인터셉터가 없으면 "모듈 double 폴백 또는 도구 추가(게이트 B 승인)"를 Phase 1에 알린다. **live 호출 흔적이 있으면 위치를 보고**하되 이 단계에서 고치지 않는다(전환 patch는 Phase 3 게이트 B 제안).
- **DOM 조회 인프라·testid 관습도 감지한다**(§3.7 배선용): DOM을 렌더해 조회하는 러너·라이브러리(`@testing-library/*`·`@playwright/test`·`cypress`) 유무와, **기존 test id 속성명**(`data-testid`·`data-test`·`data-qa`·`data-cy` 사용 흔적, Playwright config의 `testIdAttribute`, 관련 린트 규칙). **여러 개가 섞여 있거나 하나도 없으면 추측하지 말고 Phase 1에서 묻는다**(속성명은 팀 합의 사항). 기존 테스트에 **최후 수단 셀렉터**(`[class*="…"]` 같은 클래스 부분일치·애널리틱스 속성 조회)가 이미 쓰이고 있으면 **위치만 보고**하고 이 단계에서 고치지 않는다(전환은 Phase 3 게이트 B 제안).
- **E2E live 대상 환경 후보도 함께 감지한다**(E2E smoke가 선택되면 Phase 1에서 바로 확인용): E2E 러너 config의 `baseURL`/`use.baseURL`, `.env.example`·`.env.test`의 API 호스트 키 이름, CI에 이미 있는 스테이징 URL/secret 키 **이름**. **값은 읽어서 출력하지 않는다**(키 이름·파일 경로만 보고).

> Phase 0은 진행을 **차단하지 않되**, AC 3지선다 제시는 생략하지 않는다 — (c)를 고르면 채굴로, 환경 미입력이면 현재 경로로 이어가되 **그 선택이 사용자에게서 나오게** 한다.

---

## Phase 1 — 방법론×계층 구성 (적응형 추천 + 체크박스 다중선택 확정)

목적: 이 저장소에 맞는 **방법론×계층 스코프**를 정한다. 비율은 하드코딩하지 않는다.

1. `references/test-layering-principles.md` §7(감지 신호)로 저장소를 읽어 **3개 프리셋 중 하나를 근거와 함께 추천**한다:
   - **Trophy-lean**(FE/컴포넌트) · **Google-pipeline**(대규모/모노레포) · **Contract-honeycomb**(분산/MSA)
   - 추천 형식: "감지 신호 → 추천 프리셋 → 근거(신뢰도) → 이 프리셋의 AC 분해 기본값·CI 배치".
2. `references/test-layering-principles.md` §3(방법론×계층 매트릭스: 파이프라인 단계별 tier·스위트)를 함께 제시한다.

3. **방법론 스위트 — 체크박스 다중선택**: Smoke / Sanity / Regression / nightly를 **다중선택(`AskUserQuestion` multiSelect=체크박스)**으로 제시하고, **추천 프리셋 기준 기본값을 미리 체크**한 상태로 사용자가 가감하게 한다.
   - 각 항목에 한 줄 성격을 붙인다: Smoke=넓고 얕은 배포 게이트 / **Sanity=변경 관련 페이지·컴포넌트를 PR 전에(선택 레인·새 테스트를 만드는 축이 아님)** / Regression=기존 기능 비회귀 / nightly=스케줄 실행(nightly 전용 테스트는 unit·integration만 — E2E nightly 없음; regression 전체도 함께 돈다).
   - **정직성 병기**: smoke=sanity는 ISTQB상 **동의어**(구분은 실무 컨벤션·표준 아님). **Sanity의 PR job 배치·차단성은 표준이 아니라 이 하네스의 운영 결정**이다.
   - **Sanity가 선택되면 그 성격을 한 번 더 명시**한다 — sanity는 태그를 심지 않고, **변경 파일 → 역참조 상위 페이지/컴포넌트 → 매핑된 `@e2e-mock`**을 골라 **PR job**에서 돌리는 선택 레인이며(unit/integration **blocking** + mock E2E **non-blocking**), 산출물은 **선택 스크립트 2종 + CI PR job 스니펫(제안만)**이다. 변경 관련 대상에 테스트가 **아예 없을 때만** 선택 스코프 안에서 새로 만든다([`methodology-sanity.md`](references/matrix/methodology-sanity.md) §2·§3).

4. **대상 계층 — 체크박스 다중선택**: Unit / Integration / E2E를 **다중선택(체크박스)**으로 제시하고, 프리셋 무게중심을 기본 체크한다.
   - **Phase 0에서 감지한 인프라를 반영**한다 — 러너가 없는 계층은 `☐ Unit(러너 추가 필요: 예 vitest+@testing-library)`처럼 **"추가 필요"를 명시**해, 선택 시 러너 셋업이 계획(Phase 2)에 포함됨을 알린다. E2E는 **핵심 여정 소수**로 절제하도록 안내한다.
   - **E2E가 선택되면 그 자리에서 E2E 테스트 경로를 문의**한다([`layer-e2e.md`](references/matrix/layer-e2e.md) §5.1) — E2E는 별도 러너·디렉토리 관습(`e2e/`, `tests/e2e/`, `cypress/e2e/` 등)이므로 경로를 초기에 받아 Phase 3의 E2E 스펙 파일 위치로 쓴다. 미입력이면 감지된 관습을 제안하고 확인받는다.
   - **E2E 모드 태그 안내(경로 문의와 같은 자리)**: "E2E는 **스펙 한 벌**에 모드 태그를 붙여 분기합니다 — **기본은 `@e2e-mock`**(CI에서 캡처 fixture로 결정론 실행)이고, **실제 API 연동까지 검증할 시나리오가 있으면 알려주시면 그 시나리오에만 `@e2e-live`를 병기**해 **수동·on-demand 레시피**로 남깁니다(CI 고정 스테이지 없음)." — `@e2e-live`를 **임의로 부여하지 않는다**([`layer-e2e.md`](references/matrix/layer-e2e.md) §5.2). 답이 없으면 **(E2E smoke를 제외한) 나머지를 전부 `@e2e-mock`으로** 진행하고 계획표에 그렇게 적는다. ⚠️ **E2E smoke는 이 문의의 대상이 아니다** — 답이 없어도 규칙상 `@e2e-live`가 강제된다(아래 항목·§3.6.5-a).
   - **⚠️ Smoke + E2E를 둘 다 선택했으면 그 자리에서 아래를 고지·문의한다**(principles §3.6.5-a·§3.6.5-b, [`layer-e2e.md`](references/matrix/layer-e2e.md) §5.2-a):
     - **고지(선택지가 아니라 규칙)**: "**E2E smoke는 실제 API 연동이 필수**입니다 — `@smoke` E2E 스펙에는 `@e2e-live`만 붙고 `@e2e-mock`은 붙지 않습니다(mock·fixture 없음). 대신 **CI 고정 스테이지에 넣지 않고 수동으로만** 돌립니다(`test:e2e:smoke:live`). 그래서 **E2E smoke는 자동 배포 게이트가 아니라 승격 전 수동 체크포인트**이고, 이는 '배포 게이트는 결정론·외부 의존 0'이라는 통상 권고와 **상충하는 운영 결정**입니다."
     - **문의(대상 환경 — 여기서 못 받으면 나중에 실행 불가)**: ① **base URL/엔드포인트**(스테이징 권장 — **프로덕션이면 그렇게 말씀해 주세요**, 별도 확인 절차를 둡니다) ② **테스트 계정·시드 데이터** 필요 여부와 제공 방법(**값은 대화에 붙여넣지 말고 env·`.env`·CI secret 경로로**) ③ **부작용이 있는 여정**(결제·발송·삭제·외부 과금·알림)을 smoke에 넣을지.
     - 미제공이면 **계획은 그대로 세우되** 게이트 B에서 실행하지 않고 **UNVERIFIED 레시피**로 남긴다고 알린다(계획을 막지 않는다).
   - **E2E를 선택했으면 E2E 스위트 범위·포함 관계를 알린다** — **E2E는 smoke·regression만** 만들고(nightly·sanity E2E 없음), smoke 테스트는 `@smoke @regression`을 지녀 regression에 포함된다. regression은 mock·live를 섞을 수 있고, CI의 regression은 mock 패스만 돌며 smoke를 포함한 live 멤버는 수동 live 패스로 돈다(principles §3.6.5-c). 모드는 기존 테스트의 태그로만 붙이고 mock/live 전용 파일을 만들지 않는다. **Nightly·Sanity를 E2E와 함께 선택해도** E2E는 그 스위트에 배정되지 않는다고 미리 알린다.
   - **인수조건 ID 규칙을 알린다**(principles §4.6, 계층·방법론과 무관하게 항상) — 테스트 제목 맨 앞에 `[AC-1.2]`를 붙인다. smoke·regression은 인수조건 기반 테스트만 만들고, nightly·sanity는 인수조건 밖에서 필요한 테스트를 ID 없이 추가할 수 있다. 입력 AC에 ID가 없으면 `AC-n.m` 매핑표를 게이트 A에서 승인받는다. 인수조건 밖에서 추가할 테스트가 있으면 이때 함께 받는다.
   - **DOM을 조회하는 계층을 선택했으면(컴포넌트 렌더 unit/integration 또는 E2E) 셀렉터 규약을 한 줄로 알린다**([`references/test-layering-principles.md`](references/test-layering-principles.md) §3.7): "화면 요소는 **`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue`** 순으로 찾고, 속성은 **`getByAltText` > `getByTitle`**, **`getByTestId`는 위로 불가능할 때만**, 그래도 안 되면 **`locator`**(사유 표기)를 씁니다."
     - **testid 속성명이 Phase 0에서 확정되지 않았으면 여기서 묻는다** — "팀에서 쓰는 test id 속성이 무엇인가요?(`data-testid` / `data-test` / `data-qa` / `data-cy` / 기타 / 아직 없음)". **하네스가 임의로 정하지 않는다**(팀 합의 사항). "아직 없음"이면 무엇으로 할지 함께 정하고, 정해지지 않으면 **사다리 9번(`locator`)으로 내려간다는 사실**을 알린다.
     - **제품 코드에 testid를 새로 넣어야 할 수 있음**을 미리 알린다 — 그건 테스트 파일 밖의 변경이라 **게이트 B에서 파일·요소를 지목해 별도 승인**을 받는다(승인 없이 제품 코드를 고치지 않는다).
     - 비-DOM만 선택했으면(순수 로직 unit·서버 API integration 등) 이 안내를 생략하고 계획에 `셀렉터: 해당 없음(비-DOM)`으로 적는다.

5. 선택된 **(방법론 집합) × (계층 집합)**을 Phase 2/3의 **구속 스코프로 고정**한다(확정 문의). **이것이 스코프 가드의 기준선이다** — Phase 2/3는 이 선택 밖으로 어떤 테스트도 추가하지 않는다([`references/matrix/_index.md`](references/matrix/_index.md) §1). 선택 안 된 방법론/계층은 계획에서 제외하고, 비율은 하드코딩하지 않는다.
   - **조합 강도 lookup**([`references/matrix/_index.md`](references/matrix/_index.md) §3)을 한 줄로 제시해 — 실무 정합 최강(Smoke×Integration·Regression×{Unit,Integration}·Nightly×E2E — 단 이 하네스는 사용자 결정으로 E2E nightly를 만들지 않음)과 **WEAK/DEGENERATE 조합**(Sanity 전 조합·Nightly×Unit·Smoke×Unit)을 미리 알린다. 사용자가 WEAK/DEGENERATE만 나올 선택을 해도 강제로 채우지 않고 "보통 비움 + 스코프 내 STRONG 조합으로 라우팅"을 안내한다.

> 사용자가 체크박스 대신 자유형으로 답하면 그 취지를 위 스코프로 정규화한다. 이 선택은 Phase 2 계획표의 **'계층(카드)' 열·'방법론(카드·태그+셀렉터)' 열·조합 강도, 그리고 CI 단계 배치**를 결정하며 **Phase 2/3의 허용 스코프**를 못박는다. (이 단계는 게이트가 아니라 스코프 확정 — 실제 승인 게이트는 Phase 2의 게이트 A다.)

---

## Phase 2 — AC→계층별 테스트 계획 + 게이트 A (계획 승인)

목적: 각 AC를 tier로 분해해 **계층별 테스트 계획표**를 만들고 **전체를 한 번에 승인**받는다.

1. **각 AC를 축 카드 조합으로 라우팅한다** — [`references/matrix/_index.md`](references/matrix/_index.md) §2 절차(=principles §4.5)를 AC마다 적용한다. **모든 배정은 Phase 1의 선택 스코프 안에서만**(§1 스코프 가드):
   - **Step 0 스코프 확정** — Phase 1의 (선택 방법론) × (선택 계층)을 이 AC 처리 경계로 고정.
   - **Step 1** AC를 슬라이스로 쪼갠다(§4, AC≠단일 테스트·AC≠E2E).
   - **Step 2 계층 배정(선택된 계층 중에서만)** — 계층 카드([`layer-unit.md`](references/matrix/layer-unit.md)·[`layer-integration.md`](references/matrix/layer-integration.md)·[`layer-e2e.md`](references/matrix/layer-e2e.md))의 포함/제외 기준으로: 계산·판정 로직 → Unit / 인터페이스·데이터 교환 → Integration / 핵심 여정 → E2E(소수·push-down). `small=unit` 1:1 금지. **자연 계층이 미선택이면** 선택 계층으로 push-down/up하거나, 불가하면 "스코프 밖 — 추가 안 함" 표시 후 확장 문의(임의 추가 금지).
   - **Step 3 방법론 멤버십(선택된 방법론 중에서만·비배타·다중)** — 방법론 카드([`methodology-*.md`](references/matrix/methodology-regression.md))의 멤버십 기준으로: Regression?(변경 traverse/보존 — 대부분) · Smoke?(happy·표면·결정론·showstopper) · Nightly 이연?(느림/비쌈/flaky/cross-browser/exhaustive/fuzz — **E2E는 nightly로 이연하지 않는다**) · Sanity?(durable 아님 — transient change-scope, `@sanity` 안 심음). **미선택 방법론엔 배정 안 함**. **E2E는 Smoke·Regression에만 배정**한다(principles §3.6.5-c).
   - **Step 4 상황에 맞는 조합 선택** — (계층×방법론) 조합 강도 lookup([`_index.md`](references/matrix/_index.md) §3)을 보고 **스코프 안에서** 가장 적합한 조합으로 구체화. **WEAK/DEGENERATE 조합**(Sanity 전 조합·Nightly×Unit·Smoke×Unit)은 억지로 만들지 않고 스코프 내 STRONG 조합으로(스코프 내 STRONG이 아예 없으면 §1 폴백: '추가 안 함' 표기+확장 문의·있는 척 금지).
   - **Step 4-b API 경계 확정**(principles §3.6·[`_index.md`](references/matrix/_index.md) §3-c·§3-d) — **Unit/Integration은 항상 mock**: 경계 기법(① 네트워크 인터셉터 우선 / ② 모듈 double·검증 범위 밖 항목 명시)과 **fixture 소스**(① 기존 재사용 / ② 사용자 제공 요청 / ③ 스키마 유도=**`[실측 캡처 아님]`**)를 이 단계에서 정해 계획표 열에 적는다. **E2E는 모드 태그**: 기본 `@e2e-mock`, Phase 1에서 사용자가 지목한 시나리오에만 `@e2e-live` 병기(수동 레시피). ②·③이면 무엇이 검증되지 않는지를 함께 적는다.
     - **⚠️ 이 행이 (E2E × Smoke)면 모드가 고정된다**(principles §3.6.5-a): `@e2e-live` **필수**·`@e2e-mock` **금지**·mock/fixture 없음·**CI 스테이지 없음**. API 경계 열에는 fixture 소스 대신 **`live · 대상 {base URL 또는 미제공} · 계정/시드 {제공/불필요/미제공} · 수동 레시피 test:e2e:smoke:live`** 를 적고, 대상 환경이 미제공이면 **`[UNVERIFIED 예정 — 실행 불가]`** 를 함께 적는다.
     - **E2E는 smoke·regression만이고 포함 관계다 — smoke ⊆ regression**(principles §3.6.5-c). smoke 행의 방법론은 smoke·regression을 함께 적는다. smoke는 live 전용이므로 회귀용 `@e2e-mock` 복제 행이나 파일을 만들지 않는다. regression 행은 mock·live를 섞을 수 있다.
   - **Step 4-c DOM 셀렉터 확정**(principles §3.7·[`_index.md`](references/matrix/_index.md) §3-e) — 이 테스트가 DOM을 조회하면 **사다리에서 쓸 최상위 순위**를 정해 계획표 열에 적는다(예 `1 getByRole('button', {name:'찜하기'})`). **8(`getByTestId`)·9(`locator`)를 쓸 수밖에 없으면 왜 상위 쿼리가 불가능한지**를 함께 적고, 9번이면 **결합 비용**(애널리틱스 속성=다른 목적의 계약 / 클래스 부분일치=구현 세부)도 적는다. 러너 API 이름은 §3.7.3 어댑터로 옮긴다(**Playwright에 `getByDisplayValue`가 없으므로** 값 특정은 상위 순위 조회 + `toHaveValue` 어서션으로 재설계). DOM이 없으면 `해당 없음(비-DOM)`.
   - **Step 5** 한 슬라이스가 여러 방법론 suite에 속하면 membership 대수(principles §3.5.4 옵션 A/B)로 표기.
   - **인수조건 밖 추가 요청**(Phase 1에서 받은 것)도 같은 절차로 라우팅하되 방법론은 nightly·sanity만, 오라클은 사용자가 준 기대·임계값만 쓴다(없으면 `[확인 필요]`, principles §4.6).
   - 근거는 각 축 카드가 인용하는 [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md)에 있다.
2. 각 계획 행에 **명시적 오라클**(기대 상태·불변식)을 부착한다. **오라클 강도는 (계층 카드 §4 + 방법론 카드 오라클 기대)의 결합 = 더 얕은 쪽이 상한(min)**을 따른다(단 Regression×Unit처럼 강한 쪽이 리스크면 그 리스크 가드는 유지 · E2E smoke에 포함 관계로 붙는 `@regression`은 smoke 오라클을 유지하고 대가를 적는다, principles §3.6.5-c) — 예: Regression×Unit=강한 값-동등·최고위험, Smoke×*=얕은 reachability. 스모크·동어반복 어서션은 계획 단계에서 배제한다.
3. 계획표를 이 형식으로 제시한다:

   | # | AC-ID | 계층(카드) | 방법론(카드·태그+셀렉터) | 조합 강도 | **API 경계(mock/live·경계기법·fixture 소스)** | **DOM 셀렉터(순위·8·9면 사유)** | 오라클(결합 프로필·기대·불변식) | 테스트 파일(예정) | GWT 요약 | 근거(축 카드) |
   |---|-------|-----------|--------------------------|-----------|--------------------------------------------|--------------------------------|--------------------------------|-------------------|----------|---------------|

   > `AC-ID` 열(principles §4.6) — 인수조건 기반 행은 `AC-1.2`처럼 ID를 적는다. **smoke·regression 행은 반드시 ID**가 있어야 한다. 인수조건 밖 테스트(nightly·sanity에서만 허용)는 ID 대신 **사유만** 적고(예: `성능 — 1만 건 입력 처리 시간 확인`), 계획표 아래에 **따로 묶어** 다시 보여 준다.

   > `API 경계` 열 표기 예 — unit/integration: `mock · ① MSW 인터셉트 · fixture ② 사용자 제공`, `mock · ② 모듈 double(요청 조립·에러 매핑 미검증) · fixture ③ 스키마 유도[실측 캡처 아님]`. E2E: `@e2e-mock`(기본) / `@e2e-mock + @e2e-live(수동)`. **E2E smoke: `@e2e-live 전용 · 대상 https://staging… · 계정 env E2E_USER · 수동 test:e2e:smoke:live`** (대상 미제공이면 `[UNVERIFIED 예정 — 실행 불가]`).

   > `DOM 셀렉터` 열 표기 예 — `1 getByRole('button', {name:'찜하기'})` / `2 getByLabelText('이메일')` / `8 getByTestId('recent-keyword-list') — role·label·text 없음(아이콘 전용)` / `9 locator('[class*="SimpleRecentKeywordList_container"]') — 사다리 전부 불가·⚠️CSS Module 해시=구현 세부 결합` / `해당 없음(비-DOM)`. **'방법론' 열의 셀렉터(`--grep @smoke`)와 다른 열**임에 주의한다.

   그리고 CI 단계 배치(어느 계층이 PR-gate/post-deploy/nightly에 가는지)를 principles §3 매트릭스로 요약한다. **조합은 다중 멤버십**이므로 한 슬라이스가 여러 방법론 열에 겹칠 수 있다(예 Regression×Unit이면서 `@smoke`) — **E2E는 smoke·regression만이고 포함 관계가 강제된다** — smoke 슬라이스는 regression 열에도 표시하고, E2E는 nightly·sanity 열에 두지 않는다(§3.6.5-c). **스코프 밖 슬라이스는 "추가 안 함"으로 표기**하고 별도로 확장 문의한다.

   > **CI 배치 요약에 반드시 포함할 문장(E2E smoke가 있으면)**: "**E2E smoke는 CI 스테이지에 배치되지 않는다** — `test:smoke`는 비-E2E smoke만 뽑고, E2E smoke는 수동 `test:e2e:smoke:live`로만 돈다. 따라서 **자동 배포 게이트가 아니라 승격 전 수동 체크포인트**이며, 이는 게이트 결정론 권고(MinimumCD·Fowler, MED)와 **상충하는 운영 결정**이다."

3-b. **방법론 스위트 열을 실체화 형태로 적는다** (`references/test-layering-principles.md` §3.5):
   - **durable(Smoke/Regression/nightly)**: 라벨이 아니라 **구체 태그 토큰 + 그 태그를 뽑는 셀렉터**를 명시한다 — 예 `@smoke → playwright test --grep @smoke`(러너별 정확 문법·최소 버전은 §3.5.2). 계획에 **'분리 실행 스크립트(추가될 것)'** 항목을 포함한다: `test:smoke`/`test:regression`/`test:nightly`가 Phase 3에서 `package.json`(또는 저장소 관습: Makefile/tox/pytest.ini)에 추가될 예정임을 적는다.
     - **⚠️ E2E smoke가 계획에 있으면 스크립트가 두 갈래로 갈린다**(§3.6.5-a): `test:smoke`는 **비-E2E smoke만** 뽑도록 셀렉터를 짜고(`@e2e-live`가 섞이면 CI가 실제 API를 친다), E2E smoke는 별도 **수동 레시피 `test:e2e:smoke:live`**(예 `E2E_MODE=live BASE_URL=… playwright test --grep "(?=.*@smoke)(?=.*@e2e-live)"`)로 적는다. **`test:e2e:smoke:live`를 어떤 CI 스테이지에도 배치하지 않는다** — CI 스테이지↔스위트 매핑표(§3.5.5)에는 **"(스테이지 없음) E2E smoke — 수동 on-demand" 행으로만 기록**한다(표에서 지우지도, 스테이지 행으로 올리지도 않는다).
   - **sanity(선택 시)**: 태그가 아니라 **변경-스코프 선택 레시피(command)** 를 적는다(§3.5.3) — 1순위 `git diff --name-only` 경로 매핑, 폴백은 전체. `@sanity` 태그는 계획하지 않는다(무-태그 가드).
   - **membership 대수 택1 선언**(§3.5.4): 옵션 A(멀티태그) 또는 옵션 B(regression=durable 기본체+carve-out). 계층별로 선언할 수 있고, **E2E는 항상 A**, ID 없는 nightly 전용 테스트가 있는 계층도 **A**다. 이후 분리 검증이 well-defined 되게 한다.
   - **CI 스테이지↔스위트 매핑표(§3.5.5)** 를 계획에 첨부한다(CI yaml은 직접 편집하지 않고 스니펫 제안).
   - 정직성: 태그 모델은 membership/분리에 관한 것이지 **비중이 아니다** — "smoke는 전체의 X%"라고 말하지 않는다. smoke/sanity 동의어 caveat를 이 표에도 병기한다.

   > 러너에 태그/선택 기능이 없으면 분리를 있는 척하지 않는다 — 제목 substring 컨벤션+grep으로 관습 부여하고 한계를 명시하거나, 해당 스위트를 "advisory label only — 실행 분리 아님"으로 정직 강등해 계획에 표기한다(§3.5.6).

3-c. **Sanity를 선택했다면 별도 '선택 레인' 블록을 계획에 추가한다**(계획표 행이 아니다 — [`methodology-sanity.md`](references/matrix/methodology-sanity.md) §2·§3, principles §3.5.3):
   - **대상 산정 레시피 3단계**(실패 시 넓히는 방향으로만 폴백): ① 변경 파일(`git diff --name-only origin/<base>...HEAD`, 로컬은 `git diff --name-only HEAD` + `git ls-files --others --exclude-standard`; **`<base>`는 CI의 PR base 변수 → 기본 브랜치 감지 순으로 정하고 실패 시 추측 말고 문의**) → ② **역참조 확장**(그 파일을 import하는 상위 페이지/컴포넌트 — 러너 네이티브 `--findRelatedTests`/`--related`/`--only-changed` 우선, 없으면 grep 역참조; **불완전하므로 불확실하면 전체 폴백**) → ③ **관련 페이지의 `@e2e-mock`** — ⚠️ **E2E가 Phase 1 선택 스코프에 있을 때만**(미선택이면 이 단계를 건너뛰고 "E2E 스코프 밖 — sanity 대상 아님" 표기 후 확장 문의) — 경로 미러 → `@page:/route` 태그 부여 제안 → `@e2e-mock` 전량 폴백. **`@e2e-live`는 대상 아님**.
   - **실행 장치(추가될 것)**: `test:sanity:changed`(unit/integration) · `test:sanity:e2e`(**E2E가 선택 스코프에 있을 때만**·매핑된 `@e2e-mock`) · **CI PR job 스니펫**(제안만·yaml 직접 편집 금지) — blocking step(unit/integration) + non-blocking step(mock E2E, E2E 스코프 있을 때만).
   - **부족분 목록**: 변경 관련 페이지/컴포넌트 중 **테스트가 아예 없는 대상**을 별도로 적고, 새로 만들 계획 행을 **선택 스코프 안에서** 세운다(durable 태그는 선택된 방법론 중에서만·없으면 무-태그 기본체·**E2E로는 만들지 않는다**).
   - **정직 표기**: sanity의 CI 배치·차단성은 **표준이 아니라 운영 결정**이며, `@sanity` 태그는 심지 않는다(`@page:`는 대상 메타라 무-태그 가드 위반 아님). **E2E smoke는 live 전용이라 이 레인의 선택 대상이 아니다**(레인은 `@e2e-mock`만 고른다) — 변경된 페이지의 E2E가 smoke뿐이면 **"이 페이지의 E2E는 smoke(live)뿐 — sanity 레인 대상 없음"으로 표기**하고 억지로 끌어오지 않는다(누락 아님·§3.6.5-a 귀결 3).

3-d. **E2E smoke가 계획에 있으면 별도 'live smoke' 블록을 추가한다**(계획표 행과 별개 — principles §3.6.5-a·§3.6.5-b):
   - **대상 환경**: base URL / 프로덕션 여부 / 테스트 계정·시드 데이터 확보 상태(env 키 이름만 — **값은 적지 않는다**) / 부작용 있는 여정 포함 여부.
   - **실행 레시피**: `test:e2e:smoke:live` 명령 전문 + 모드 스위치 장치(env 분기 헬퍼·러너 project·라우팅) — **게이트 B 승인 대상**.
   - **배치 = 없음**: "PR-gate·post-deploy·nightly 어디에도 넣지 않음"을 명시하고, `test:smoke`/`test:regression`/`test:nightly` 셀렉터가 이 스펙을 **끌어오지 않는지 게이트 B에서 실행 검증**함을 적는다.
   - **실행 계획**: 대상 환경·계정이 확보됐고 게이트 B에서 승인하면 하네스가 **실제로 1회 실행**, 아니면 **UNVERIFIED**. 어느 쪽인지 지금 시점 예상을 적는다.
   - **정직 표기(그대로 인쇄)**: "E2E smoke는 **자동 배포 게이트가 아니라 승격 전 수동 체크포인트**다. 이는 게이트 결정론·외부 의존 0 권고(MinimumCD·Fowler, MED)와 **상충하는 운영 결정**이며 근거로 정당화하지 않는다. live 통과는 **실행 시각·대상 환경에 한정된 관측**이다."

4. **게이트 A — 계획 승인**: "이 계층별 계획으로 진행할까요? (전체 승인 / 특정 행 수정·제외 / 프리셋 재조정)". 이제 **태그 스킴(방법론 + E2E 모드) + API 경계·fixture 소스 열 + sanity 선택 레인(레시피·장치 3종·부족분) + live smoke 블록(대상 환경·레시피·배치 없음·실행 계획) + 추가될 분리 스크립트 + CI 스테이지↔스위트 매핑표 + membership 대수 + AC-ID 매핑표(입력 AC에 ID가 없을 때) + ID 없는 테스트 묶음(사유만 적힌 행)**까지 함께 승인한다. 승인 전에는 **어떤 파일도 만들지 않는다.** ⚠️ **계획 승인은 live 실행 승인이 아니다** — 실제 API 호출은 게이트 B에서 별도로 묻는다(§3.6.5-b).

---

## Phase 3 — 개별 테스트 순차 생성·적용 + 게이트 B (개별 승인)

목적: 승인된 계획의 각 테스트를 **하나씩** 생성·적용한다. 한 테스트마다 게이트를 통과해야 다음으로 간다.

각 계획 행에 대해 순차로:

0. **이 테스트의 축 카드 조합을 연다** — 배정된 **계층 카드 + 방법론 카드**([`references/matrix/`](references/matrix/_index.md))의 **오라클 프로필·실체화·포함/제외 기준**을 작성 지침으로 결합한다. **이 행이 Phase 1 선택 스코프 안인지 재확인**(스코프 밖이면 적용하지 않는다 — §1 가드). Regression×Unit 등 **최고위험 조합**이면 오라클 오검증을 특히 엄격히 한다.
1. **오라클 안전 선검사** (`references/test-layering-principles.md` §5 + 계층/방법론 카드 오라클):
   - 오라클이 *현재 구현이 내는 값을 그대로 굳힌 것*인지, *AC가 요구하는 기대*를 검증하는지 구분한다. 구현 스냅샷이면 AC(기대)에서 오라클을 다시 유도하고, 애매하면 사용자에게 "이 기대가 맞습니까?"를 확인한다.
   - **조합 프로필에 오라클 강도를 맞춘다**: Smoke×*는 얕은 reachability로 충분하되 "초록=검증" 오독 금지, Regression×{Unit,Integration}은 강한 값-동등/행위 보존 오라클을 요구(implementation-bias·green-locks-bug 최대 리스크), E2E 정확출력이 비현실적이면 메타모픽 관계(MR)를 옵션으로.
   - 첫 테스트 적용 전, 대상 영역의 **기존 flaky를 점검**한다(flakiness 전이 방지). 정렬 순서 의존(ORDER BY 누락류)을 특히 경계.
2. **테스트 코드 draft 제시**: 감지된 프레임워크·디렉토리 관습에 맞춰 작성. 오라클을 명시하고 스모크·동어반복 어서션을 넣지 않는다. GWT→AAA 구조를 따른다.
   - **배치 규약**(계층 카드 §5): **unit/integration**은 테스트 대상(컴포넌트/유틸) 파일이 있는 **바로 그 폴더에 `__test__/` 디렉토리를 만들어**(없으면 생성) 그 안에 `*.test.*`로 둔다. **⚠️ `__test__/`는 무조건 강제(스코프 가드·3게이트와 동급 불변식) — 저장소에 이미 다른 배치 관습(`__tests__` 복수·`test/`·소스 폴더 bare `*.test.ts`)이 감지돼도 그 관습으로 대체하지 않고 항상 `__test__/`를 만들어 그 안에 둔다.** 러너 config가 특정 폴더로만 매칭을 제한해 `__test__/`가 안 잡히면 관습을 바꾸는 게 아니라 testMatch/include 조정을 이 게이트 B에서 제안한다('확인 필요'). **E2E**는 Phase 1에서 입력받은 경로에 여정 스펙을 둔다(E2E는 `__test__/` 강제 대상 아님 — 별도 러너·디렉토리 관습).
   - **API 경계 규약(계층 카드 §5 + principles §3.6 — 계획표 'API 경계' 열대로 구현)**: **unit/integration은 실제 API를 호출하지 않는다**(예외 없음 — live로 나가면 정의상 계층 자격 상실). ① **네트워크 경계 인터셉터**(MSW/nock/`responses`/`httptest`)를 우선 쓰고, 없으면 ② **모듈 double**(`vi.mock`/`jest.mock`)로 폴백하되 무엇이 검증 범위 밖인지 draft에 주석/보고로 남긴다. **fixture는 3단 폴백**(① 저장소 기존 재사용 → ② 사용자에게 실제 응답 샘플 요청 → ③ 스키마/타입 유도 + **`[스키마 유도 — 실측 캡처 아님]` 표기**)으로 확보하고 — **하네스가 fixture를 만들려고 live API를 호출하지 않는다** —, 위치는 **저장소 fixture 관습 감지 우선·없으면 `<대상 폴더>/__test__/fixtures/`**(`orders.get.200.json`처럼 엔드포인트·상태코드 명명), fixture는 커밋한다. **fixture 값을 그대로 기대값으로 복사하지 않는다**(fixture-as-oracle 금지, principles §5-6). **nightly** full-suite도 같은 mock 규약으로 결정론 실행한다(E2E nightly 없음).
   - **셀렉터 규약(계층 카드 §5 + principles §3.7 — 계획표 'DOM 셀렉터' 열대로 구현)**: DOM을 조회하는 draft는 **사다리를 위에서부터** 쓴다 — **`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue`**(시각 요소·사용자 인터랙션) → **`getByAltText` > `getByTitle`**(HTML5·ARIA 속성) → **`getByTestId`**(위로 불가능한 값을 찾을 때만) → **`locator`**(최후 수단).
     - **내려갈 때는 사유를 draft 옆에 적는다** — 상위 쿼리가 **왜 불가능한지**(해당 role/label/text 없음, 중복이라 특정 불가 등). "쓰기 편해서"·"덜 깨져서"는 사유가 아니다.
     - **러너 API 이름을 어댑터로 옮긴다**(§3.7.3) — Playwright는 **`getByLabel`·`getByPlaceholder`** 이고 **`getByDisplayValue`가 없다**. 없는 API를 부르지 말고, 값 특정이 필요하면 **상위 순위로 찾고 값은 어서션으로**(`expect(locator).toHaveValue(...)`) 검증한다.
     - **testid 속성명은 감지·합의된 것만 쓴다**(§3.7.4·Phase 0/1). 확정 안 됐으면 임의로 만들지 말고 묻거나 사다리 9번으로 내려간다.
     - ⚠️ **제품 코드에 testid를 새로 추가해야 하면 게이트 B에서 별도 승인**을 받는다 — 어느 파일의 어느 요소에 무엇을 넣을지 제시한다. **테스트 파일 밖의 변경이므로 승인 없이 쓰지 않는다.** 거절되면 9번으로 내려가고 그 사실을 적는다.
     - **최후 수단 `locator`를 쓰면 결합 비용을 draft 주석·보고에 남긴다** — 애널리틱스 속성(`[data-ga-action="…"]`)은 **다른 목적의 계약**에, 클래스 부분일치(`[class*="…"]`)는 **구현 세부**에 결합돼 그 소유자가 바꾸면 깨진다. 위험은 알리되 **사용자가 수용하면 따른다**.
     - **기존 테스트의 셀렉터는 무단 개조하지 않는다** — 사다리에 어긋난 것을 발견하면 위치와 함께 보고하고 **전환 patch를 게이트 B로 제안**한다(승인 시에만 수정).
     - **DOM이 없는 테스트**(순수 함수 unit·서버 API integration 등)에는 이 규약을 적용하지 않는다 — `해당 없음(비-DOM)`.
   - **배치 강제 검사(이 편차가 이 스킬의 흔한 실수)**: (a) **작성 전** — draft의 테스트 파일 경로가 `<대상 파일 폴더>/__test__/…`(unit/integration)인지 확인하고, 아니면 draft를 거부·경로를 `__test__/` 아래로 교정한 뒤에만 게이트 B로 넘긴다. (b) **작성 시** — `__test__/` 디렉토리가 없으면 파일 쓰기와 함께 생성한다(Write는 상위 폴더를 만들지만, mkdir이 필요한 러너 셋업이면 명시적으로 만든다). (c) **작성 후** — 실제 생성 경로가 `__test__/` 아래인지 확인(`Glob`/`ls`)하고 진행 보고에 경로를 남긴다.
2-b. **스위트 태그를 코드에 물리적으로 부여**(`references/test-layering-principles.md` §3.5.2):
   - durable 스위트(Smoke/Regression/nightly)에 배치된 테스트는 draft를 쓸 때 **러너 네이티브 기법으로 태그를 코드에 물리적으로 붙인다** — Playwright `{ tag: '@smoke' }`(1.42+), Vitest `{ tags: ['smoke'] }`(4.1.0+, config 선언 필요), Jest는 네이티브 태그가 없으므로 제목 `@smoke`+`-t` 또는 파일명 `*.smoke.test.ts`+projects. 계획 라벨만 있고 코드 태그가 없는 durable 테스트는 **실체화 실패로 거부/수정**한다(phantom suite 방지).
   - **AC-ID를 테스트 제목 맨 앞에 붙인다**(principles §4.6) — `test('[AC-1.2] …', …)`, 여러 개면 `[AC-1.2][AC-1.3]`. `@smoke`·`@regression`이 붙은 draft에 AC-ID가 없거나 입력(또는 승인된 매핑표)에 없는 ID면 거부·보완한다. ID 없는 테스트는 계획표에서 사유로 승인된 nightly·sanity 행만 허용한다.
   - **E2E 모드 태그도 이때 물리 부여한다**([`layer-e2e.md`](references/matrix/layer-e2e.md) §5.2, principles §3.6.5) — **기본 `@e2e-mock`**, Phase 1에서 사용자가 지목한 시나리오에만 `@e2e-live`를 병기한다(**임의 부여 금지**). 스펙은 **한 벌**이고 **모드는 기존 테스트의 태그로만** 표현한다(mock/live 전용 파일을 새로 만들지 않고, 이미 있는 E2E 테스트에는 태그만 추가). 모드 전환은 **명시 스위치**(env `E2E_MODE`·러너 project·fixture 라우팅 헬퍼)로만 — 스테이지가 모드를 바꾸는 코드를 쓰지 않는다. sanity가 E2E를 고르기 위해 `@page:/route` 태그가 필요하면 그 부여도 여기서 제안한다(대상 메타 태그).
   - **⚠️ 이 행이 E2E smoke면 모드가 규칙으로 고정된다**([`layer-e2e.md`](references/matrix/layer-e2e.md) §5.2-a, principles §3.6.5-a): 태그는 **`['@smoke','@regression','@e2e-live']`** 이고 **`@e2e-mock`을 붙이지 않는다**(mock 데이터로는 smoke를 검증할 수 없다). **mock 주입 코드(`page.route` 등)를 쓰지 않고 fixture도 만들지 않는다.** **E2E 태그 사다리를 확인한다**(principles §3.6.5-c) — `@smoke`면 `@regression`이 함께 있어야 하고(빠지면 거부·보완), E2E에 `@nightly`가 붙었으면 거부한다(E2E는 smoke·regression만). 오라클은 실제 응답이므로 **정확 출력 pinning 대신 여정 도달·상태 전이·계약 형태**(필수 필드·타입·상태코드)로 잡는다 — 특정 시점 응답값을 굳힌 draft는 거부한다.
   - **sanity는 태그를 심지 않는다** — 변경-스코프 선택 레시피로만 처리(§3.5.3). `@sanity` 태그 부여 금지(무-태그 가드).
   - 태그 부여는 오라클 가드(§5)와 **직교**이며 둘 다 게이트 B에서 통과해야 한다 — 태그가 오라클을 대체하지 않는다.
   - **카테고리(스위트)의 첫 테스트를 적용할 때**, durable 스위트의 분리 실행 스크립트(`test:smoke`/`test:regression`/`test:nightly`)를 `package.json`(또는 저장소 관습)에 추가한다. E2E가 스코프에 있으면 E2E mock 패스는 `test:regression` 셀렉터(`@e2e-mock` 필터)로 돌린다(별도 스크립트를 만들지 않는다). **live 레시피는 두 갈래이고 각각 실체가 있을 때만 만든다**(0개인데 만들면 phantom):
     - **`test:e2e:smoke:live`** — `@smoke`+`@e2e-live` 스펙이 1개 이상일 때만(§3.6.5-a). 비-E2E smoke를 끌어오지 않는다(격리 단언 ⓓ).
     - **`test:e2e:regression:live`** — `@regression` ∧ `@e2e-live`(포함 관계라 smoke가 함께 뽑힘, principles §3.6.5-c). **smoke 레시피와 같은 집합이면 만들지 않는다**(live가 smoke뿐이면 중복·phantom). 수동 실행 전용(CI 스테이지에 넣지 않음). E2E nightly가 없으므로 nightly live 레시피도 없다.
     - **CI의 regression E2E 셀렉터는 `@e2e-mock`으로 거른다** — smoke 스펙도 `@regression`을 지니므로 필터가 없으면 CI가 live smoke를 끌어온다(격리 단언 ⓔ). `test:nightly`는 E2E를 뽑지 않는다.
     - **E2E smoke가 있으면 `test:smoke` 셀렉터를 비-E2E smoke만 뽑도록** 짠다(예 `@e2e-live` 제외 필터 또는 프로젝트 분리). **`test:e2e:smoke:live`를 CI 스테이지·PR job 스니펫에 넣지 않는다**(매핑표에는 '스테이지 없음' 행으로만). **모드 스위치 장치**(env 분기 헬퍼·러너 project 설정·fixture 라우팅)도 새 코드/설정이므로 함께 제시해 승인받는다 — 스위치 없이 태그만 붙이면 `@e2e-live`는 실행 불가능한 라벨이다. **sanity는 durable 태그가 없어 '첫 테스트' 트리거가 성립하지 않는다** — 선택 레인 장치 3종(`test:sanity:changed`·`test:sanity:e2e`·CI PR job 스니펫)은 특정 테스트와 무관하므로 게이트 A 승인 후 1회 추가한다. 스크립트 추가도 코드 변경이므로 **게이트 B 대상**이다(자동 편집 금지·**CI yaml은 스니펫 제안만**).

2-c. **live 호출 정적 검사**(principles §3.6.4): **게이트 B로 넘기기 전 draft**(및 새로 만드는 헬퍼/셋업)에 **외부 URL 리터럴(non-localhost)·mock 되지 않은 `fetch`/`axios`/HTTP 클라이언트 호출·실 인증 토큰 참조**가 남았는지 확인하고, 파일을 쓴 뒤(항목 3 이후) 실제 파일에 대해 grep으로 한 번 더 확인한다. 발견되면 보고하고 **교정 후에만** 다음으로 간다.
   - **검사 대상**: unit/integration 전부 + `@e2e-mock` 스펙. **`@e2e-live` 스펙(E2E smoke 포함)은 정의상 실제 API를 호출하므로 대상이 아니다** — 대상에서 뺐다는 사실을 보고에 한 줄로 남긴다(조용한 면제 금지). 모드 스위치 헬퍼는 **live 분기 밖**(mock 경로·공용 셋업)에 외부 호출이 새지 않았는지만 본다.
   - **한계를 반드시 병기한다** — 정적 검사는 우회 가능하므로 **"통과 = 네트워크로 안 나감"의 증명이 아니다**. 런타임 네트워크 차단은 강제하지 않는다.
   - **기존 테스트가 live를 호출 중이면**(Phase 0 감지분 포함) 위치와 함께 보고하고 **mock 전환 patch를 게이트 B로 제안**한다 — 승인 시에만 수정하고, 승인 없이는 건드리지 않는다.
2-d. **셀렉터 사다리 검사**(principles §3.7): 게이트 B로 넘기기 전 draft에서 확인한다 — ⓐ **더 상위 순위로 찾을 수 있는데 아래로 내려간 조회가 없는가**(있으면 상위로 교정) ⓑ **8·9번 사용처마다 사유가 적혀 있는가**(없으면 거부·보완) ⓒ **러너에 없는 API를 부르지 않았는가**(예: Playwright `getByDisplayValue`·`getByLabelText`) ⓓ **합의되지 않은 testid 속성명을 임의로 쓰지 않았는가** ⓔ **제품 코드 testid 추가가 필요하면 별도 승인 항목으로 분리됐는가**. 비-DOM 테스트는 이 검사를 건너뛰고 `해당 없음`으로 보고한다.
   - ⚠️ 이 검사는 **오라클 가드(§5)와 직교**다 — 셀렉터를 고쳤다고 오라클이 강해지지 않으며, 둘 다 게이트 B를 통과해야 한다.

3. **게이트 B — 개별 적용 승인**: "이 테스트를 적용할까요? (적용 / 수정 후 적용 / 이 테스트만 건너뜀 / 여기서 중단)". **승인 시에만** 파일을 쓴다(Write/Edit). **제품 코드 testid 추가가 있으면 테스트 파일과 분리해 따로 묻는다**(§3.7.4).
4. **실행 그라운딩**: 적용한 테스트를 실제로 실행한다(Bash로 러너 호출). 결과(PASS/FAIL)를 자기보고가 아니라 실행 출력으로 보고한다.
   - ⚠️ **이 항목의 실행 대상에서 `@e2e-live` 스펙을 제외한다** — 실제 API를 치기 때문이다. **비-smoke live**는 실행하지 않고 레시피를 UNVERIFIED로 남기고, **E2E smoke live**는 이 항목을 건너뛰어 **4-b의 조건부 실행 절차**로 보낸다(동의 없이 여기서 먼저 돌리지 않는다). 셀렉터에 `@e2e-live` 제외 필터를 걸고, 아래 분리 검증은 **열거(dry-run/`--list`)** 로 수행해 실제 호출이 일어나지 않게 한다.
   - 통과: 다음 행으로. 실패: 원인이 (a) 테스트 결함인지 (b) 실제 코드 결함(=AC 위반 발견)인지 구분해 보고하고, 사용자에게 다음 조치(테스트 수정 / 코드 결함으로 기록 / 건너뜀)를 문의한다.
   - false-alarm 인지: 정상 경로에서도 통과하는지 함께 확인한다.
   - **분리 실제 동작 검증**: 방금 부여한 태그가 실제로 뽑히는지 셀렉터를 실행해 확인한다 — `--grep @smoke`(Playwright)/`--tags-filter="smoke"`(Vitest)/`-t '@smoke'`·`--selectProjects smoke`(Jest)가 이 테스트를 그 스위트로 뽑고 다른 스위트엔 안 뽑는지(§3.5.4 정확 membership)를 자기보고가 아니라 **실행 출력**으로 보고한다. 뽑히지 않거나 초과로 뽑히면 태그 누수/미부여로 기록하고 수정한다.
   - **E2E 모드 분리 검증**: `--grep @e2e-mock`이 계획 집합과 일치하고 `@e2e-live` 전용 시나리오를 끌어오지 않는지 실행 출력으로 확인한다. **E2E가 있으면 격리 단언 6종을 실행 출력으로 확인한다**(principles §3.5.4-5): ⓐ `test:smoke` 목록에 `@e2e-live`가 **하나도 없다** ⓑ `@smoke` E2E 스펙에 `@e2e-mock`이 **없다** ⓒ **E2E 태그 사다리** — `@smoke`면 `@regression`이 **있고** E2E에 `@nightly`가 **없다** ⓓ `test:e2e:smoke:live`가 비-E2E smoke를 끌어오지 않는다 ⓔ `@regression` ⊇ `@smoke`이고 regression mock 패스 + live 패스 합이 E2E regression 전체와 같으며, **CI의 regression 실행 목록에 `@e2e-live`가 0개**, `test:nightly` 목록에 E2E가 0개다 ⓕ 같은 시나리오가 모드만 다른 **복제 파일로 존재하지 않는다**. 하나라도 어긋나면 태그/셀렉터를 수정한다. 열거 명령·확인 시점은 principles §3.5.4 "열거 방법·시점"을 따른다(마지막 E2E 행 적용 후 한 번 + Phase 4에서 한 번 더).
   - **AC-ID 추적 검증**(principles §3.5.4-6): `@smoke`·`@regression` 셀렉터 실행 목록의 테스트 제목이 모두 `[AC-…]`로 시작하고 그 ID가 입력(또는 승인된 매핑표)에 있는지, ID 없는 테스트는 사유로 승인된 nightly·sanity 행뿐인지 확인한다.
   - **일반 `@e2e-live`(비-smoke)는 이 자리에서 실행하지 않는다** — 수동 on-demand 레시피를 **UNVERIFIED**로 기록해 사용자에게 넘긴다.

4-b. **E2E smoke(live) 실행 그라운딩 — 조건부**(principles §3.6.5-b, 하네스 live 호출의 **유일한 예외**):

   - **전제 확인(하나라도 없으면 실행하지 않고 UNVERIFIED)**: ① 대상 환경(base URL) 제공됨 ② 테스트 계정·시드 데이터 제공됨 또는 "불필요" 확인됨 ③ **그 자리 실행 승인**. **게이트 A(계획 승인)·게이트 B(적용 승인)는 실행 승인을 대신하지 않는다** — 별도로 묻는다.
   - **실행 문의 형식**: "이 스펙을 **실제 API로 지금 돌릴까요?** — 대상 `{BASE_URL}` · 계정 `{env 키 이름}` · 이 여정의 부작용 `{있음: 결제/발송/삭제/과금/알림 … | 없음}` → [실행 / 레시피만 남기고 UNVERIFIED]".
   - **안전 규약**: 대상이 **프로덕션이면 한 번 더 경고하고 재확인**(재확인 시 따르되 요약에 기록) · **부작용 여정은 개별 확인** · **비밀 값을 대화·명령·로그에 노출하지 않는다**(env/`.env`/CI secret 경로만 참조, `.env`는 gitignore 확인) · 레이트리밋 고려 · **생성된 데이터를 하네스가 임의로 지우지 않고 남았다고 보고**한다.
   - **실행 후 보고(자기보고 금지 — 실행 출력 인용)**: PASS/FAIL + **실행 시각·대상 환경**을 함께 적는다. 결과는 "연동이 정상"이 아니라 "**{시각}에 {환경}에 대해 통과**"로 기술한다.
   - **실패는 3분류**(2분류로 뭉개지 않는다): (a) **테스트 결함**(셀렉터·대기·오라클) → 수정 제안 / (b) **코드 결함**(AC 위반) → 기록·문의 / (c) **환경·외부계**(미배포·인증 만료·레이트리밋·시드 부재·업스트림 장애) → **결함이 아니라 환경 사유로 기록**하고 재실행/보류를 문의한다.
   - **실행하지 못했으면** 레시피를 **UNVERIFIED**로 남긴다 — "레시피·스위치를 만들었다"를 검증으로 옮기지 않는다.

5. 진행 상황을 짧게 갱신한다(예: "3/8 적용, 2 PASS · 1 코드결함 의심").

**Sanity 선택 레인 적용**(sanity를 선택한 경우 — 계획 3-c 승인분, 게이트 B 대상):
- 장치를 순차로 적용한다: ① `test:sanity:changed`(변경+역참조 대상의 unit/integration) ② `test:sanity:e2e`(매핑된 `@e2e-mock` — **E2E가 선택 스코프에 있을 때만 만든다**) ③ **CI PR job 스니펫 제안**(blocking step=①, non-blocking step=② — **yaml 직접 편집 금지**).
- **레시피 실행 그라운딩**: 현재(또는 probe) 변경으로 레시피를 실제 실행해 **어떤 파일이 뽑혔는지 출력으로** 보고한다 — 변경 파일뿐 아니라 **그것을 import하는 페이지/컴포넌트**가 실제로 걸리는지, `@e2e-live`가 섞이지 않는지, 코드에 `@sanity` 태그가 없는지 확인한다(§3.5.4). 매핑이 퇴화(전체 반환)하면 **의도된 폴백인지 매핑 고장인지 구분해** 보고한다.
- **부족분 생성**: 변경 관련 대상에 테스트가 아예 없으면 그 테스트를 **선택 스코프 안에서** 새로 만든다 — 위 1~4 절차(오라클 선검사 → draft → 게이트 B → 실행)를 그대로 거친다. durable 태그는 선택된 방법론 중에서만 부여하고, 없으면 무-태그 기본체로 두고 보고한다.

**중단 지점**은 언제든 존중한다 — 사용자가 멈추면 지금까지 적용된 것만 남기고 Phase 4로 넘어간다.

---

## Phase 4 — 재확인·반영 (최종 게이트 C)

목적: 적용된 테스트 전체를 **다시 확인**하고, **재승인될 경우에만** 확정("반영")한다.

1. 적용 요약을 제시한다: 적용/건너뜀/실패 테스트 목록, 각 tier·스위트 분포, 발견된 코드 결함 의심 목록, 남은 UNVERIFIED 항목.
   - **API 경계 요약**: fixture 소스별 목록(①재사용/②사용자제공/**③스키마 유도=실측 캡처 아님**), 모듈 double로 폴백해 **검증 범위 밖으로 남은 부분**, 정적 검사에서 발견된 live 호출과 그 처리(전환/보류).
   - **미실행 `@e2e-live` 레시피**를 UNVERIFIED로 명시하고, **"mock E2E 통과는 연동 검증이 아니다 — 연동 확인은 `@e2e-live` 수동 실행뿐"**을 병기한다(principles §3.6.6).
   - **셀렉터 요약**(DOM 조회 테스트가 있으면): 사다리 순위별 사용처 목록과 **8(`getByTestId`)·9(`locator`) 사용처의 사유**, **제품 코드에 추가한 testid**(승인분)와 **거절돼 9번으로 내려간 항목**, 기존 테스트에서 발견했지만 **전환하지 않은 셀렉터**(보고만). ⚠️ **준수율·점수를 만들지 않는다** — 목록과 사유로만 적는다.
   - **E2E smoke(live) 상태**(있으면): 스펙 목록 · 대상 환경·실행 시각 · **실행됨(PASS/FAIL) 또는 UNVERIFIED(사유: 대상 미제공/미승인)** · 실패 시 3분류 판정 · 남은 테스트 데이터 · 격리 단언 6종 결과. 그리고 **그대로 인쇄**: "**E2E smoke는 CI 스테이지에 없다 — 자동 배포 게이트가 아니라 승격 전 수동 체크포인트다.** 이는 게이트 결정론 권고와 **상충하는 운영 결정**이며, live 통과는 **실행 시각·대상 환경에 한정된 관측**이다."
   - **sanity 레인 상태**: 장치 3종 적용 여부, 레시피 실행이 실제로 뽑은 대상 수, 매핑 폴백 발생 여부, 부족분으로 새로 만든 테스트, **E2E smoke가 레인에서 제외된 페이지 목록**(정의상 제외 — 누락 아님).
2. 전체 스위트를 한 번 실행해 현재 상태를 보고한다(가능하면). ⚠️ **이 전체 실행에 `@e2e-live`(E2E smoke 포함)를 포함하지 않는다** — 실제 API 호출은 §3.6.5-b 전제(대상 환경·계정·그 자리 승인)를 만족한 개별 실행에서만 하며, 여기서 재실행하려면 다시 묻는다.
3. **게이트 C — 최종 반영 재확인**: "이대로 반영(확정)할까요? (확정 / 특정 테스트 되돌리기 / 추가 조정)".
   - "반영"은 적용된 파일을 **유지·정리**하는 것을 의미한다. 재승인 시: 불필요 스캐폴드 정리, 최종 요약 산출.
   - 되돌리기 요청 시 해당 테스트 파일 변경을 원복한다.

---

## 산출물 저장 (opt-in)

계획표·근거 요약은 기본적으로 대화로만 제시한다. 사용자가 원하면 `<대상경로>/.claude/_docs/test-layering/<슬러그>/`에 `test-plan.md`(계획표)와 `applied-summary.md`(적용 요약)로 저장한다. 저장은 항상 사용자 선택(opt-in).

---

## 정직성·경계 체크리스트 (마무리 전 자문)

- [ ] 비율%를 하드코딩하지 않았는가(70/20/10 folklore)?
- [ ] smoke=sanity ISTQB 동의어 caveat를 병기했는가?
- [ ] **스코프 가드** — 테스트를 **사용자가 Phase 1에서 선택한 방법론·계층 안에서만** 추가했는가? 스코프 밖은 임의 추가하지 않고 "추가 안 함" 표기 후 확장 문의했는가?
- [ ] 각 AC를 **축 카드 조합**(계층 카드 + 방법론 카드)으로 라우팅하고(§4.5 절차), 조합을 **다중 멤버십**으로 다뤘는가(12개 셀로 미리 물질화 안 함)?
- [ ] **WEAK/DEGENERATE 조합**(Sanity 전 조합·Nightly×Unit·Smoke×Unit)을 억지로 채우지 않고 정직히 비워 스코프 내 STRONG 조합으로 라우팅했는가?
- [ ] **nightly를 방법론이 아니라 CI-stage/스케줄 지연 축**으로 표기했는가?
- [ ] **prioritization으로 CI 비용 절감을 주장하지 않았는가**(latency만; selection·batching·병렬화로)?
- [ ] 근거 없는 효과 수치를 인용하지 않았는가?
- [ ] 모든 오라클을 기대(AC) 기준으로 오검증했는가(구현 스냅샷 거부)?
- [ ] **배치 강제** — unit/integration 테스트를 **모두** 대상 파일 폴더의 `__test__/` 안에 두었는가? 저장소에 다른 관습이 있어도 예외 없이 `__test__/`를 만들었고, 작성 전 경로 검사·작성 후 경로 확인을 했는가(E2E는 Phase 1 경로 별개)?
- [ ] **API 경계 강제** — unit/integration에 **실제 API 호출이 하나도 없는가**(네트워크 인터셉터 우선·모듈 double 폴백)? fixture를 3단 폴백으로 확보하고 **스키마 유도분에 `[실측 캡처 아님]`을 표기**했는가? fixture를 기대값으로 그대로 복사하지 않았는가? 정적 검사를 수행하고 **그 한계(우회 가능·네트워크 미접속 증명 아님)** 를 함께 적었는가?
- [ ] **셀렉터 우선순위**(principles §3.7) — DOM 조회를 **`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue`** / **`getByAltText` > `getByTitle`** 순으로 시도하고, **`getByTestId`는 위로 불가능할 때만**, `locator`는 **최후 수단**으로만 썼는가? **8·9번 사용처마다 사유**(상위가 왜 불가능했는지)를 적었고, 9번엔 **결합 비용**(애널리틱스 속성=다른 목적의 계약 / 클래스 부분일치=구현 세부)도 적었는가? **러너에 없는 API를 부르지 않았는가**(Playwright `getByLabel`/`getByPlaceholder`·`getByDisplayValue` 부재 → 상위 조회 + `toHaveValue`)? **testid 속성명을 임의로 정하지 않고** 감지·합의된 것만 썼는가? **제품 코드 testid 추가를 게이트 B에서 별도로 승인**받았는가(거절 시 9번으로 하향·표기)? 기존 테스트 셀렉터를 **무단 개조하지 않고** 보고·patch 제안했는가? **준수율을 점수화하지 않고** 효과 수치·접근성 성과를 주장하지 않았는가? 비-DOM은 `해당 없음`으로 적었는가?
- [ ] **E2E 모드 태그** — 스펙 **한 벌**에 `@e2e-mock`(기본)을 부여하고, `@e2e-live`는 **사용자가 지목한 시나리오에만** 병기했는가(E2E smoke는 예외 — live 강제)? 모드 전환을 명시 스위치로만 했고(스테이지가 모드를 바꾸지 않음), `@e2e-live`를 CI 스테이지·sanity에 넣지 않고 **수동 레시피(UNVERIFIED)** 로 남겼는가? **"mock 통과 ≠ 연동 검증"** 을 산출물에 병기했는가?
- [ ] **E2E smoke = live 전용**(principles §3.6.5-a) — `@smoke` E2E에 **`@e2e-live`를 필수 부여하고 `@e2e-mock`을 안 붙였는가**(mock 주입·fixture 없음)? **E2E는 smoke·regression만** 만들고(nightly·sanity E2E 없음) **태그 사다리**(smoke `@smoke @regression` / regression `@regression`, principles §3.6.5-c)를 빠짐 없이 붙였는가? mock/live **복제 파일·스펙을 만들지 않고** 기존 테스트에 태그만 추가했는가? **CI 스테이지(PR-gate·post-deploy·nightly)에 넣지 않고** 수동 live 레시피만 만들었는가? CI의 regression E2E 셀렉터를 **`@e2e-mock`으로 걸렀는가**? **격리 단언 6종**(ⓐ`test:smoke`에 live 없음 ⓑsmoke E2E에 mock 태그 없음 ⓒE2E 태그 사다리·E2E nightly 없음 ⓓlive 레시피가 비-E2E 안 끌어옴 ⓔ포함 관계 + CI regression 실행에 live 0개 ⓕ모드 복제 파일 없음)을 **실행 출력**으로 확인했는가? sanity 레인 제외를 **누락이 아니라 규칙의 결과로 표기**했는가?
- [ ] **AC-ID**(principles §4.6) — smoke·regression 테스트 제목이 모두 `[AC-…]`로 시작하고 입력에 있는 ID인가? 인수조건 밖 테스트는 nightly·sanity에만 두고, 계획표 AC-ID 열에 **사유만** 적어 게이트 A에서 따로 승인받았는가? 입력 AC에 ID가 없었다면 매핑표를 승인받았는가?
- [ ] **live 실행 규약**(principles §3.6.5-b) — 실제 API 실행 전에 **대상 환경 + 계정/시드 + 그 자리 승인** 세 전제를 모두 확인했는가(계획 승인으로 갈음하지 않음)? **프로덕션 재확인·부작용 개별 확인·비밀 미노출**을 지켰는가? 결과를 **실행 시각·대상 환경과 함께** 적고 "연동 정상"이 아니라 "언제·어디서 통과"로 기술했는가? 실패를 **3분류**(테스트/코드/**환경·외부계**)로 구분했는가? 못 돌렸으면 **UNVERIFIED**로 남기고 "레시피를 만들었다"를 검증으로 옮기지 않았는가?
- [ ] **E2E smoke 정직성** — **"자동 배포 게이트가 아니라 승격 전 수동 체크포인트"** 와 **게이트 결정론 권고(MinimumCD·Fowler, MED)와의 상충이 사용자 운영 결정**임을 산출물에 병기했는가? 근거로 정당화하거나 "표준을 따른다"고 포장하지 않았는가? "live smoke로 장애 N% 조기 포착" 류 **효과 수치를 인용하지 않았는가**?
- [ ] **sanity 선택 레인** — `@sanity`를 심지 않고, 변경 파일 → **역참조 상위 페이지/컴포넌트** → 매핑된 `@e2e-mock`(**E2E가 선택 스코프에 있을 때만**)으로 대상을 산정했는가? `<base>`를 추측하지 않고 감지·문의로 정했는가? 불확실할 때 **좁히지 않고 폴백**했는가? 장치 3종(스크립트 2 + **CI PR job 스니펫 제안**)을 게이트 B로 적용하고 **CI yaml을 직접 편집하지 않았는가**? 차단성(unit/int blocking·mock E2E non-blocking)과 **"표준 아닌 운영 결정"** 을 표기했는가? 부족분 생성은 **선택 스코프 안에서만** 했는가?
- [ ] 적용된 테스트를 실제로 실행해 결과를 확인했는가(자기보고 금지)?
- [ ] 3개 게이트(계획→개별→최종)를 모두 통과했는가?
