---
name: test-layering-harness
description: >-
  인수조건(AC, Given-When-Then)에서 테스트를 방법론(Smoke/Sanity/Regression/nightly)×계층(Unit/Integration/E2E)
  택소노미로 분해·CI 단계에 배치해 계획하고, 계획→개별→최종 3단계 인간 승인 게이트로 테스트를 하나씩 순차 생성·적용·확정하는
  도메인 무관 인터랙티브 스킬. 방법론×계층을 12개 셀로 미리 물질화하지 않고 references/matrix/에 방법론 카드 4개+계층 카드 3개(7개 축 카드)를
  두어, 각 AC를 필요한 시점에 두 축을 조합해 상황에 맞는 테스트로 라우팅한다(기준은 2025+ 공식표준·논문에 연결하되 1차 근거 없으면 정직 표기). 조합은
  다중 멤버십이고 WEAK/DEGENERATE 조합은 정직히 비운다. **테스트는 사용자가 Phase 1에서 선택한 방법론·계층 안에서만 추가한다**(스코프 가드 — 밖은 임의 추가 금지·확장 문의). 사용자가 "인수조건으로 테스트 짜줘", "이 AC를 unit/통합/E2E로 나눠서", "스모크/회귀 테스트 계획
  세워줘", "테스트 피라미드(트로피)로 계층 잡아줘", "테스트를 하나씩 승인받으며 추가", "AC 기반 계층별 테스트 스위트", "CI 단계별로
  어떤 테스트를 어디에 둘지" 같은 요청을 하거나 테스트 계층 전략·CI 배치를 논할 때 반드시 사용한다. 대상 저장소를 감지해 3개 프리셋
  (Trophy-lean/Google-pipeline/Contract-honeycomb) 중 근거와 함께 적응형으로 추천하고 비율%(70/20/10)는 folklore이므로
  하드코딩하지 않는다. LLM 생성 테스트의 최대 리스크인 오라클 강도(구현이 아니라 기대·명세를 검증하는가)를 오라클 오검증·실행
  그라운딩·flaky baseline 선결로 가드한다. 초기 문의에서 AC 입력과 개발 환경을 각각 스킵(pass) 가능하며 개발 환경 미입력 시
  현재 프로젝트 경로를 기준으로 삼는다. 경계: 리스크 기반 오라클·자가치유 실행·flaky 트리아지 end-to-end QA(qa-agent-harness),
  백엔드 실행기반 test-generator(backend-harness), AC↔테스트 커버리지 읽기전용 검수(review-harness/test-coverage-review),
  FE 개발 흐름 내 TDD(frontend-harness), 실행 가능 명세 작성(spec-driven-development), 커밋/PR(git-harness)은 범위 밖이다.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# test-layering-harness

인수조건(AC)을 **방법론(Smoke/Sanity/Regression/nightly) × 계층(Unit/Integration/E2E)** 택소노미로 계층별 테스트 스위트로 계획하고, **계획 → 개별 → 최종의 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정한다. 도메인 무관·독립 실행.

**왜 이렇게 만드는가**: AI가 테스트를 자동 생성할수록 위험은 "작성"이 아니라 "무엇을, 어느 층에, 어떤 오라클로 검증하는가"로 옮겨간다. 근거([`references/research/test-strategy-research.md`](references/research/test-strategy-research.md) · [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md))가 반복해 말하는 최대 리스크는 **오라클 강도** — LLM은 명세(기대)가 아니라 구현(실제 동작)을 굳혀 버그를 초록으로 은폐한다. 그래서 이 스킬은 (1) 테스트를 계층 택소노미로 **분해**하고, (2) 매 적용을 **사람이 승인**하며, (3) 오라클을 **오검증·실행 그라운딩**한다.

작업 원리·매트릭스·프리셋·오라클 가드·anti-pattern·경계는 [`references/test-layering-principles.md`](references/test-layering-principles.md)에 있다. Phase 1~3에서 해당 절을 열어 근거를 인용하라.

**방법론·계층 축 카드(7개)**: 방법론×계층을 12개 셀로 미리 물질화하지 않고, **방법론 카드 4개**([`methodology-smoke.md`](references/matrix/methodology-smoke.md)·[`methodology-sanity.md`](references/matrix/methodology-sanity.md)·[`methodology-regression.md`](references/matrix/methodology-regression.md)·[`methodology-nightly.md`](references/matrix/methodology-nightly.md))와 **계층 카드 3개**([`layer-unit.md`](references/matrix/layer-unit.md)·[`layer-integration.md`](references/matrix/layer-integration.md)·[`layer-e2e.md`](references/matrix/layer-e2e.md))를 두고, **필요한 시점에 두 축을 조합**해 상황에 맞는 테스트를 고른다. 라우팅 절차·조합 강도 lookup·**스코프 가드**는 [`references/matrix/_index.md`](references/matrix/_index.md), 2025+ 근거 원장은 [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md). **셀은 조합(다중 멤버십)이지 독립된 4번째 유형이 아니다.** **⚠️ 스코프 가드**: 테스트는 **사용자가 Phase 1에서 선택한 방법론·계층 안에서만** 추가한다 — 밖으로는 임의 추가 금지(스코프 확장은 사용자에게 문의).

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

> Phase 0은 진행을 **차단하지 않되**, AC 3지선다 제시는 생략하지 않는다 — (c)를 고르면 채굴로, 환경 미입력이면 현재 경로로 이어가되 **그 선택이 사용자에게서 나오게** 한다.

---

## Phase 1 — 방법론×계층 구성 (적응형 추천 + 체크박스 다중선택 확정)

목적: 이 저장소에 맞는 **방법론×계층 스코프**를 정한다. 비율은 하드코딩하지 않는다.

1. `references/test-layering-principles.md` §7(감지 신호)로 저장소를 읽어 **3개 프리셋 중 하나를 근거와 함께 추천**한다:
   - **Trophy-lean**(FE/컴포넌트) · **Google-pipeline**(대규모/모노레포) · **Contract-honeycomb**(분산/MSA)
   - 추천 형식: "감지 신호 → 추천 프리셋 → 근거(신뢰도) → 이 프리셋의 AC 분해 기본값·CI 배치".
2. `references/test-layering-principles.md` §3(방법론×계층 매트릭스: 파이프라인 단계별 tier·스위트)를 함께 제시한다.

3. **방법론 스위트 — 체크박스 다중선택**: Smoke / Sanity / Regression / nightly를 **다중선택(`AskUserQuestion` multiSelect=체크박스)**으로 제시하고, **추천 프리셋 기준 기본값을 미리 체크**한 상태로 사용자가 가감하게 한다.
   - 각 항목에 한 줄 성격을 붙인다: Smoke=넓고 얕은 배포 게이트 / Sanity=표적 변경을 좁고 깊게 / Regression=기존 기능 비회귀 / nightly=스케줄 full regression+E2E.
   - **정직성 병기**: smoke=sanity는 ISTQB상 **동의어**(구분은 실무 컨벤션·표준 아님). Sanity는 고정 CI 스테이지가 없다(표적 변경에 붙는 성격).

4. **대상 계층 — 체크박스 다중선택**: Unit / Integration / E2E를 **다중선택(체크박스)**으로 제시하고, 프리셋 무게중심을 기본 체크한다.
   - **Phase 0에서 감지한 인프라를 반영**한다 — 러너가 없는 계층은 `☐ Unit(러너 추가 필요: 예 vitest+@testing-library)`처럼 **"추가 필요"를 명시**해, 선택 시 러너 셋업이 계획(Phase 2)에 포함됨을 알린다. E2E는 **핵심 여정 소수**로 절제하도록 안내한다.
   - **E2E가 선택되면 그 자리에서 E2E 테스트 경로를 문의**한다([`layer-e2e.md`](references/matrix/layer-e2e.md) §5) — E2E는 별도 러너·디렉토리 관습(`e2e/`, `tests/e2e/`, `cypress/e2e/` 등)이므로 경로를 초기에 받아 Phase 3의 E2E 스펙 파일 위치로 쓴다. 미입력이면 감지된 관습을 제안하고 확인받는다.

5. 선택된 **(방법론 집합) × (계층 집합)**을 Phase 2/3의 **구속 스코프로 고정**한다(확정 문의). **이것이 스코프 가드의 기준선이다** — Phase 2/3는 이 선택 밖으로 어떤 테스트도 추가하지 않는다([`references/matrix/_index.md`](references/matrix/_index.md) §1). 선택 안 된 방법론/계층은 계획에서 제외하고, 비율은 하드코딩하지 않는다.
   - **조합 강도 lookup**([`references/matrix/_index.md`](references/matrix/_index.md) §3)을 한 줄로 제시해 — 실무 정합 최강(Smoke×Integration·Regression×{Unit,Integration}·Nightly×E2E)과 **WEAK/DEGENERATE 조합**(Sanity 전 조합·Nightly×Unit·Smoke×Unit)을 미리 알린다. 사용자가 WEAK/DEGENERATE만 나올 선택을 해도 강제로 채우지 않고 "보통 비움 + 스코프 내 STRONG 조합으로 라우팅"을 안내한다.

> 사용자가 체크박스 대신 자유형으로 답하면 그 취지를 위 스코프로 정규화한다. 이 선택은 Phase 2 계획표의 **'계층(카드)' 열·'방법론(카드·태그+셀렉터)' 열·조합 강도, 그리고 CI 단계 배치**를 결정하며 **Phase 2/3의 허용 스코프**를 못박는다. (이 단계는 게이트가 아니라 스코프 확정 — 실제 승인 게이트는 Phase 2의 게이트 A다.)

---

## Phase 2 — AC→계층별 테스트 계획 + 게이트 A (계획 승인)

목적: 각 AC를 tier로 분해해 **계층별 테스트 계획표**를 만들고 **전체를 한 번에 승인**받는다.

1. **각 AC를 축 카드 조합으로 라우팅한다** — [`references/matrix/_index.md`](references/matrix/_index.md) §2 절차(=principles §4.5)를 AC마다 적용한다. **모든 배정은 Phase 1의 선택 스코프 안에서만**(§1 스코프 가드):
   - **Step 0 스코프 확정** — Phase 1의 (선택 방법론) × (선택 계층)을 이 AC 처리 경계로 고정.
   - **Step 1** AC를 슬라이스로 쪼갠다(§4, AC≠단일 테스트·AC≠E2E).
   - **Step 2 계층 배정(선택된 계층 중에서만)** — 계층 카드([`layer-unit.md`](references/matrix/layer-unit.md)·[`layer-integration.md`](references/matrix/layer-integration.md)·[`layer-e2e.md`](references/matrix/layer-e2e.md))의 포함/제외 기준으로: 계산·판정 로직 → Unit / 인터페이스·데이터 교환 → Integration / 핵심 여정 → E2E(소수·push-down). `small=unit` 1:1 금지. **자연 계층이 미선택이면** 선택 계층으로 push-down/up하거나, 불가하면 "스코프 밖 — 추가 안 함" 표시 후 확장 문의(임의 추가 금지).
   - **Step 3 방법론 멤버십(선택된 방법론 중에서만·비배타·다중)** — 방법론 카드([`methodology-*.md`](references/matrix/methodology-regression.md))의 멤버십 기준으로: Regression?(변경 traverse/보존 — 대부분) · Smoke?(happy·표면·결정론·showstopper) · Nightly 이연?(느림/비쌈/flaky/cross-browser/exhaustive/fuzz) · Sanity?(durable 아님 — transient change-scope, `@sanity` 안 심음). **미선택 방법론엔 배정 안 함**.
   - **Step 4 상황에 맞는 조합 선택** — (계층×방법론) 조합 강도 lookup([`_index.md`](references/matrix/_index.md) §3)을 보고 **스코프 안에서** 가장 적합한 조합으로 구체화. **WEAK/DEGENERATE 조합**(Sanity 전 조합·Nightly×Unit·Smoke×Unit)은 억지로 만들지 않고 스코프 내 STRONG 조합으로(스코프 내 STRONG이 아예 없으면 §1 폴백: '추가 안 함' 표기+확장 문의·있는 척 금지).
   - **Step 5** 한 슬라이스가 여러 방법론 suite에 속하면 membership 대수(principles §3.5.4 옵션 A/B)로 표기.
   - 근거는 각 축 카드가 인용하는 [`references/research/matrix-criteria-2025.md`](references/research/matrix-criteria-2025.md)에 있다.
2. 각 계획 행에 **명시적 오라클**(기대 상태·불변식)을 부착한다. **오라클 강도는 (계층 카드 §4 + 방법론 카드 오라클 기대)의 결합 = 더 얕은 쪽이 상한(min)**을 따른다(단 Regression×Unit처럼 강한 쪽이 리스크면 그 리스크 가드는 유지) — 예: Regression×Unit=강한 값-동등·최고위험, Smoke×*=얕은 reachability. 스모크·동어반복 어서션은 계획 단계에서 배제한다.
3. 계획표를 이 형식으로 제시한다:

   | # | AC-ID | 계층(카드) | 방법론(카드·태그+셀렉터) | 조합 강도 | 오라클(결합 프로필·기대·불변식) | 테스트 파일(예정) | GWT 요약 | 근거(축 카드) |
   |---|-------|-----------|--------------------------|-----------|--------------------------------|-------------------|----------|---------------|

   그리고 CI 단계 배치(어느 계층이 PR-gate/post-deploy/nightly에 가는지)를 principles §3 매트릭스로 요약한다. **조합은 다중 멤버십**이므로 한 슬라이스가 여러 방법론 열에 겹칠 수 있다(예 Regression×Unit이면서 `@smoke`). **스코프 밖 슬라이스는 "추가 안 함"으로 표기**하고 별도로 확장 문의한다.

3-b. **방법론 스위트 열을 실체화 형태로 적는다** (`references/test-layering-principles.md` §3.5):
   - **durable(Smoke/Regression/nightly)**: 라벨이 아니라 **구체 태그 토큰 + 그 태그를 뽑는 셀렉터**를 명시한다 — 예 `@smoke → playwright test --grep @smoke`(러너별 정확 문법·최소 버전은 §3.5.2). 계획에 **'분리 실행 스크립트(추가될 것)'** 항목을 포함한다: `test:smoke`/`test:regression`/`test:nightly`가 Phase 3에서 `package.json`(또는 저장소 관습: Makefile/tox/pytest.ini)에 추가될 예정임을 적는다.
   - **sanity(선택 시)**: 태그가 아니라 **변경-스코프 선택 레시피(command)** 를 적는다(§3.5.3) — 1순위 `git diff --name-only` 경로 매핑, 폴백은 전체. `@sanity` 태그는 계획하지 않는다(무-태그 가드).
   - **membership 대수 택1 선언**(§3.5.4): 옵션 A(멀티태그) 또는 옵션 B(regression=durable 기본체+carve-out). 이후 분리 검증이 well-defined 되게 한다.
   - **CI 스테이지↔스위트 매핑표(§3.5.5)** 를 계획에 첨부한다(CI yaml은 직접 편집하지 않고 스니펫 제안).
   - 정직성: 태그 모델은 membership/분리에 관한 것이지 **비중이 아니다** — "smoke는 전체의 X%"라고 말하지 않는다. smoke/sanity 동의어 caveat를 이 표에도 병기한다.

   > 러너에 태그/선택 기능이 없으면 분리를 있는 척하지 않는다 — 제목 substring 컨벤션+grep으로 관습 부여하고 한계를 명시하거나, 해당 스위트를 "advisory label only — 실행 분리 아님"으로 정직 강등해 계획에 표기한다(§3.5.6).

4. **게이트 A — 계획 승인**: "이 계층별 계획으로 진행할까요? (전체 승인 / 특정 행 수정·제외 / 프리셋 재조정)". 이제 **태그 스킴 + 추가될 분리 스크립트 + CI 스테이지↔스위트 매핑표 + membership 대수**까지 함께 승인한다. 승인 전에는 **어떤 파일도 만들지 않는다.**

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
   - **배치·mock 규약**(계층 카드 §5): **unit/integration**은 테스트 대상(컴포넌트/유틸) 파일이 있는 폴더에 `__test__/`를 만들어 그 안에 `*.test.*`로 둔다 — **단 Phase 0에서 이미 co-location 관습(예 `__tests__` 복수·`test/`)이 감지되면 그 관습을 따르고(분산 방지), 없을 때 `__test__/`를 기본값**으로 한다. 외부 API는 **실제 응답을 캡처한 mock(fixture)** 로 double한다(live 호출 금지·fixture 커밋). **E2E**는 Phase 1에서 입력받은 경로에 여정 스펙을 둔다. **nightly** full-suite도 캡처 mock로 결정론 실행(cross-browser/real-device는 실제·API는 mock).
2-b. **스위트 태그를 코드에 물리적으로 부여**(`references/test-layering-principles.md` §3.5.2):
   - durable 스위트(Smoke/Regression/nightly)에 배치된 테스트는 draft를 쓸 때 **러너 네이티브 기법으로 태그를 코드에 물리적으로 붙인다** — Playwright `{ tag: '@smoke' }`(1.42+), Vitest `{ tags: ['smoke'] }`(4.1.0+, config 선언 필요), Jest는 네이티브 태그가 없으므로 제목 `@smoke`+`-t` 또는 파일명 `*.smoke.test.ts`+projects. 계획 라벨만 있고 코드 태그가 없는 durable 테스트는 **실체화 실패로 거부/수정**한다(phantom suite 방지).
   - **sanity는 태그를 심지 않는다** — 변경-스코프 선택 레시피로만 처리(§3.5.3). `@sanity` 태그 부여 금지(무-태그 가드).
   - 태그 부여는 오라클 가드(§5)와 **직교**이며 둘 다 게이트 B에서 통과해야 한다 — 태그가 오라클을 대체하지 않는다.
   - **카테고리(스위트)의 첫 테스트를 적용할 때**, durable 스위트의 분리 실행 스크립트(`test:smoke`/`test:regression`/`test:nightly`)를 `package.json`(또는 저장소 관습)에 추가한다. **sanity는 durable 태그가 없어 '첫 테스트' 트리거가 성립하지 않는다** — `test:sanity:changed` 변경-스코프 레시피는 특정 테스트와 무관하므로 게이트 A 승인 후 1회 추가한다. 스크립트 추가도 코드 변경이므로 **게이트 B 대상**이다(자동 편집 금지).
3. **게이트 B — 개별 적용 승인**: "이 테스트를 적용할까요? (적용 / 수정 후 적용 / 이 테스트만 건너뜀 / 여기서 중단)". **승인 시에만** 파일을 쓴다(Write/Edit).
4. **실행 그라운딩**: 적용한 테스트를 실제로 실행한다(Bash로 러너 호출). 결과(PASS/FAIL)를 자기보고가 아니라 실행 출력으로 보고한다.
   - 통과: 다음 행으로. 실패: 원인이 (a) 테스트 결함인지 (b) 실제 코드 결함(=AC 위반 발견)인지 구분해 보고하고, 사용자에게 다음 조치(테스트 수정 / 코드 결함으로 기록 / 건너뜀)를 문의한다.
   - false-alarm 인지: 정상 경로에서도 통과하는지 함께 확인한다.
   - **분리 실제 동작 검증**: 방금 부여한 태그가 실제로 뽑히는지 셀렉터를 실행해 확인한다 — `--grep @smoke`(Playwright)/`--tags-filter="smoke"`(Vitest)/`-t '@smoke'`·`--selectProjects smoke`(Jest)가 이 테스트를 그 스위트로 뽑고 다른 스위트엔 안 뽑는지(§3.5.4 정확 membership)를 자기보고가 아니라 **실행 출력**으로 보고한다. 뽑히지 않거나 초과로 뽑히면 태그 누수/미부여로 기록하고 수정한다.
5. 진행 상황을 짧게 갱신한다(예: "3/8 적용, 2 PASS · 1 코드결함 의심").

**중단 지점**은 언제든 존중한다 — 사용자가 멈추면 지금까지 적용된 것만 남기고 Phase 4로 넘어간다.

---

## Phase 4 — 재확인·반영 (최종 게이트 C)

목적: 적용된 테스트 전체를 **다시 확인**하고, **재승인될 경우에만** 확정("반영")한다.

1. 적용 요약을 제시한다: 적용/건너뜀/실패 테스트 목록, 각 tier·스위트 분포, 발견된 코드 결함 의심 목록, 남은 UNVERIFIED 항목.
2. 전체 스위트를 한 번 실행해 현재 상태를 보고한다(가능하면).
3. **게이트 C — 최종 반영 재확인**: "이대로 반영(확정)할까요? (확정 / 특정 테스트 되돌리기 / 추가 조정)".
   - "반영"은 적용된 파일을 **유지·정리**하는 것을 의미한다. 재승인 시: 불필요 스캐폴드 정리, 최종 요약 산출.
   - **커밋/PR은 이 스킬의 범위가 아니다**(git-harness). 재승인 후 원하면 커밋 메시지 작성·커밋을 `git-harness`로 핸드오프하겠다고 제안만 한다 — 직접 커밋하지 않는다.
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
- [ ] 적용된 테스트를 실제로 실행해 결과를 확인했는가(자기보고 금지)?
- [ ] 3개 게이트(계획→개별→최종)를 모두 통과했는가?
- [ ] 커밋을 직접 하지 않고 git-harness로 핸드오프만 제안했는가?
- [ ] 인접 하네스(qa-agent/backend/review/frontend/spec) 범위를 침범하지 않았는가([`references/test-layering-principles.md`](references/test-layering-principles.md) §9)?
