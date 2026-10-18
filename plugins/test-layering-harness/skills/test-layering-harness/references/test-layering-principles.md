# test-layering-harness 원리 (방법론 × 계층 · AC 분해 · 오라클 안전 · 프리셋)

> 이 문서는 오케스트레이터(`../SKILL.md`)가 Phase 1~3에서 참조한다. 근거는 [`research/test-strategy-research.md`](research/test-strategy-research.md) 참조. 신뢰도(HIGH/MED/LOW)·folklore·모순 표기는 근거 dossier를 그대로 계승한다.

## 목차
1. 방법론(Smoke/Sanity/Regression/nightly) — 정의·트리거·실패 조치
2. 계층(Unit/Integration/E2E) — 트레이드오프·비율 정직성
3. 방법론 × 계층 매트릭스 (CI 단계 배치)
3.5. 방법론 스위트 실체화(materialization) — 계획 라벨 → 실행 가능한 분리
3.6. **API 경계 처리 축 (mock / live)** — 계층별 기본값·E2E 모드 태그·fixture 규약·**E2E smoke = live 전용(§3.6.5-a)**·**live 실행 규약(§3.6.5-b)**·**E2E는 smoke·regression만, 포함 관계 smoke ⊆ regression(§3.6.5-c)**
3.7. **셀렉터 우선순위 축 (DOM 조회)** — 적용 범위·우선순위 사다리 9단·러너 이름 어댑터·테스트 ID 팀 합의·최후 수단 locator·정직성
4. AC → tier 분해 규칙 (GWT→AAA)
4.5. AC → 축 카드 조합 라우팅 (방법론 4 + 계층 3, 선택 스코프 내)
4.6. **인수조건 ID(AC-ID) 표기** — 제목 `[AC-1.2] …`·smoke/regression은 AC 기반만·nightly/sanity는 ID 없는 추가 허용
5. 오라클 강도 — LLM 생성 최대 리스크와 가드
6. 3개 적응형 프리셋 (Trophy-lean / Google-pipeline / Contract-honeycomb)
7. 저장소 감지 신호 (프리셋 추천용)
8. Anti-pattern

> **축 카드**: §3 매트릭스와 §4 분해의 **운영 라우팅 기준**은 [`matrix/`](matrix/_index.md)에 있다 — 12개 셀로 미리 물질화하지 않고 **방법론 카드 4개 + 계층 카드 3개**를 두어 라우팅 시점에 조합한다. 각 축 카드는 AC 포함/제외 체크리스트·오라클 프로필·실체화·근거(2025+ [`research/matrix-criteria-2025.md`](research/matrix-criteria-2025.md))를 담는다. **테스트는 사용자가 선택한 방법론·계층 안에서만 추가**한다(스코프 가드). Phase 2 라우팅 절차는 [`matrix/_index.md`](matrix/_index.md) §2.

---

## 1. 방법론 — 정의·트리거·실패 조치

| 방법론 | 스코프 | 트리거(도는 시점) | 목적 | 실패 시 |
|---|---|---|---|---|
| **Smoke (BVT)** | 넓고 얕게(broad-shallow) | 빌드/배포 직후·승격 전 go/no-go 게이트 (**단 E2E smoke는 CI 스테이지가 아니라 수동 체크포인트** — §3.6.5-a) | 후속 테스트 돌릴 가치 있는 빌드인지 판별 | 즉시 정지·차단(block)·fix-forward vs rollback (**E2E smoke는 자동 차단 아님 — 사람이 판단**) |
| **Sanity** | 좁고 깊게(narrow-deep) | **표준상 고정 스테이지 없음** — 표적 수정/핫픽스 직후 · **이 하네스의 운영 배치 = PR 전 change-scoped PR job**(§3.5.3) | 변경이 건드린 페이지/컴포넌트만 집중 확인 | 해당 수정 반려·재작업(unit/int blocking·mock E2E는 리포트) |
| **Regression** | 넓고 깊게(broad-deep) | 매 커밋(선택 실행)~main 머지(full) | 기존 기능 비회귀 | PR 내 관찰·수정 후 재푸시 |
| **Nightly** | full(선택 없음) | 스케줄(cron) | 선택 실행의 커버리지 갭 헤지·안전망 | 티켓화·다음날 컨텍스트 복원 수리 |

**⚠️ 반드시 표기할 정직성 규칙 (사용자에게도 노출)**:
- ISTQB 공식 용어집은 **smoke = sanity 를 동의어**로 본다. "smoke=넓고얕음 / sanity=좁고깊음" 구분은 *실무 컨벤션(folklore)*이지 표준이 아니다. 이 스킬은 컨벤션 표기를 쓰되 항상 "표준 아님"을 병기한다.
- **Smoke 실행시간 3~7분·15~30분 등 숫자는 소스마다 다르고 1차 근거가 약하다** — 목표치/대략치로만 제시하고 절대값으로 못 박지 않는다.
- "smoke 50% 단축 / 크리티컬 버그 80% 조기 포착 / regression 90%를 5% 시간에" 같은 효과 수치는 **folklore** — 인용 금지.

**2025+ 방향성(HIGH)**: nightly-only regression은 24h 피드백 안티패턴. **빠른 게이트(선택 실행) + nightly full 병치**의 2-tier가 현대 배치의 핵심.

---

## 2. 계층 — 트레이드오프·비율 정직성

| tier | 속도 | 비용 | 통합 신뢰 | RCA(원인 국소화) | 이 층이 답하는 질문 |
|---|---|---|---|---|---|
| **Unit** | 초 | 쌈 | 낮음 | 정확 | "이 함수/판정 로직이 맞나?" |
| **Integration** | 분 | 중간 | 균형 | 양호 | "모듈·컴포넌트·API가 함께 동작하나?" |
| **E2E** | 10~30분 | 비쌈 | 최고 | **약함** | "사용자 여정 전체가 되나?" |

**비율 정직성(중요)**: 70/20/10 같은 **정확한 비율%는 folklore**다 (Fowler 본인이 "숫자는 중요치 않다"고 상대화). Trophy(integration-heavy)·Honeycomb도 **전문가 휴리스틱**이지 통제 실험으로 입증된 최적 비율이 아니다. → **이 스킬은 비율을 하드코딩하지 않는다.** 대신 "AC→tier 분해 규칙 + CI 단계 배치"를 산출하고, 무게중심은 저장소에 맞춰 프리셋으로 제안한다.

**E2E 절제 근거(HIGH)**: E2E는 느리고·비싸고·flaky하며 RCA가 약하다(E절 flaky 클러스터·비용 근거). "이 버그는 E2E여야 잡는다"는 통념은 반증됨 — 값싼 unit이 더 많은 경계를 커버한다. E2E는 **핵심 사용자 여정 소수**로 제한한다.

---

## 3. 방법론 × 계층 매트릭스 (CI 단계 배치)

가장 단단한 앵커: **Google presubmit/postsubmit + Fowler DeploymentPipeline** — *tier는 파이프라인 뒤로 갈수록 넓어진다*(앞=빠르고 좁게, 뒤=느리고 넓게).

| 파이프라인 단계 | 트리거 | 배치 tier | 방법론 스위트 | 시간 예산(목표치) |
|---|---|---|---|---|
| Pre-commit/local | 로컬 | lint·정적분석·빠른 unit 일부 | (훅) | 초~수십초 |
| **PR-gate** | PR push | unit(전량) + integration(선택) + API, **TIA로 영향받은 것만** + smoke 소수 | selective regression + smoke | <5~15분 |
| Merge to main | merge | full unit+integration·contract·security | full regression(빠른 계층) | ~10분 |
| Post-deploy(staging/canary) | 배포 후 | 핵심 API/integration happy-path(**비-E2E smoke만** — E2E smoke는 수동 체크포인트, §3.6.5-a) | **smoke** + canary | 수분 |
| **Nightly** | cron | `@nightly`는 unit·integration만(느린 integration·perf·fuzz) — **E2E nightly 없음**(사용자 결정, §3.6.5-c) | `test:nightly` + `test:regression` full(이 안의 E2E는 regression mock 패스) · nightly 전용은 인수조건 밖 허용(§4.6) | 20분~수시간 |
| Pre-release(RC) | RC | 포괄 자동 스위트 | acceptance suite | — |

**배치 원칙**:
1. **선택(selection)·배치(batching) > 우선순위(prioritization)** — 우선순위는 실행 순서만 바꿔 총 실행량을 못 줄인다. PR-gate는 TIA로 영향받은 테스트만 돌리되, **이해 못 하는 커밋엔 전체 실행 안전 폴백**.
2. **배포를 막는 게이트는 빠르고 신뢰도 높아야** — 느린 E2E를 배포 게이트에 두면 우회당한다. 무거운 것은 nightly로(단 E2E는 nightly로 보내지 않고 크리티컬 subset으로 좁힌다, §3.6.5-c).
3. **sanity는 표준상 고정 스테이지가 아니다** — "변경 표적에 붙는 좁은 확인"이라는 성격이므로 표준 매트릭스에 고정 칸이 없다. 이 하네스는 그 성격을 **PR 전 change-scoped PR job**으로 운영하되(§3.5.3), 이것이 **표준이 아니라 운영 결정**임을 산출물에 병기한다.

> **매트릭스 = 두 축의 조합(4번째 유형 아님)**: 각 (방법론 × tier) 조합에 대한 **AC 포함/제외 운영 기준**은 [`matrix/`](matrix/_index.md)의 **축 카드 7개**(방법론 4 + 계층 3)를 라우팅 시점에 **조합**해 얻는다(12개 셀로 미리 물질화하지 않음). 계층은 개별 테스트의 durable 속성이고 방법론은 그 위의 selection/tag(sanity는 transient)이므로 — ISO/IEC/IEEE 29119-1:2022 §4.4.6은 regression을 "test level이 아니라 design/execution choice"로 규정 — **한 테스트는 여러 조합에 속할 수 있다**(배타 버킷 아님). 조합 강도(STRONG/WEAK/DEGENERATE)와 라우팅 절차·**스코프 가드(선택 안에서만 추가)**는 [`matrix/_index.md`](matrix/_index.md). **⚠️ "nightly"는 방법론이 아니라 CI-stage/스케줄 지연 축**임을 함께 표기한다(ISTQB/ISO에 nightly test type 없음).

---

## 3.5 방법론 스위트 실체화(materialization) — 계획 라벨을 실행 가능한 분리로

§3 매트릭스와 §4 row 형식에서 방법론 스위트(Smoke/Sanity/Regression/nightly)는 **계획표의 한 컬럼(라벨)** 으로만 존재한다. 라벨만으로는 (1) 코드에 물리 태그가 없고 (2) 그 스위트만 돌리는 실행 스크립트가 없고 (3) 분리가 실제로 되는지 확인할 방법이 없다 → **phantom suite**(계획엔 "smoke"가 있으나 독립 실행 단위로는 존재하지 않음). 이 절은 라벨을 **실행 가능한 분리**로 실체화하는 규칙이다.

### 3.5.1 durable-tag vs transient-selection 비대칭 (핵심)

네 방법론은 실행 모델이 **두 종류**로 갈린다. 이 비대칭은 임의가 아니라 근거에서 강제된다 — sanity는 "고정 스테이지 없음, 표적 수정 직후 좁은 확인이라는 성격"(§1 표·§3 배치원칙3).

| 방법론 | 실행 모델 | 실체화 아티팩트 | CI 고정 스테이지 |
|---|---|---|---|
| **Smoke** | **durable 태그** | 코드 물리 태그 `@smoke` + `test:smoke` 스크립트(**비-E2E만**) · E2E smoke는 `@smoke`+`@e2e-live` + `test:e2e:smoke:live`(수동) | **비-E2E는 있음**(post-deploy, PR-gate 소수) / **E2E smoke는 없음**(수동 on-demand, §3.6.5-a) |
| **Regression** | **durable 태그/기본체** | `@regression`(또는 durable 기본체 전량) + `test:regression` | 있음 (merge full·PR 선택) |
| **Nightly** | **durable 태그** | `@nightly` + `test:nightly` | 있음 (cron) |
| **Sanity** | **transient 선택** | 태그 아님 — 변경-스코프 선택 **레시피(command) + CI PR job 스니펫** | 표준 근거 **없음** / 운영 배치 = **change-scoped PR job**(하네스 결정) |

- **Smoke/Regression/Nightly = durable 태그**로 실체화: 고정 tag 토큰 → 러너 네이티브 기법으로 코드에 물리 부여 → 전용 스크립트 → 고정 CI 스테이지.
- **Sanity = transient 선택**으로 실체화: `@sanity` 태그를 코드에 **심지 않는다**(무-태그 가드). 대신 "이번 변경이 건드린 페이지/컴포넌트의 테스트만" 조립하는 선택 레시피(§3.5.3)를 산출하고, **PR 전에 도는 change-scoped PR job**으로 배치한다.
  - ⚠️ **정직성**: ISTQB/ISO에 sanity의 고정 CI 스테이지 근거는 **없다**. PR job 배치는 표준이 아니라 **이 하네스의 운영 결정**이며, 산출물에 그렇게 표기한다(smoke=sanity 동의어 caveat와 함께).

### 3.5.2 durable 스위트 — 프레임워크별 정확 태깅·분리 실행 문법

> 러너를 하나로 하드코딩하지 않는다. Phase 1에서 감지된 러너의 어댑터를 골라 적용한다. 각 문법에 최소 버전·출처를 병기.

**Playwright** (태그는 `@`로 시작, 키는 단수 `tag`)
- 태깅(권장, **v1.42+**): `test('로그인', { tag: '@smoke' }, async …)` / 복수·describe 상속: `test('리포트', { tag: ['@slow','@vrt'] }, …)`, `test.describe('그룹', { tag: '@regression' }, …)`. 출처: playwright.dev release-notes v1.42, docs/test-annotations.
- 레거시(항상 지원): 제목 문자열에 `@smoke` 삽입 — `--grep`가 제목을 포함하므로 동작. 최초 도입 버전 **확인 필요**(1.42 이전부터).
- 분리 실행(공식 확정): `playwright test --grep @smoke` / 제외 `--grep-invert @smoke` / OR `--grep "@smoke|@regression"` / AND(lookahead) `--grep "(?=.*@smoke)(?=.*@critical)"`. config 등가물 `grep`/`grepInvert`(전역·프로젝트). 출처: docs/test-annotations, API TestConfig.grep.
- ⚠️ `test.describe.configure(...)`는 태그용이 **아니다**(mode/retries/timeout 전용). 그룹 태그는 `describe('name',{tag:[...]},fn)`. 어노테이션 `{ annotation:{type,description} }`(1.42+)도 필터 대상 아님(리포트 메타데이터).

**Vitest** (네이티브 태그는 `@` 없이 이름, 키는 **복수 `tags`·배열**)
- 네이티브 태그(**v4.1.0+**): `test('renders', { tags: ['smoke'] }, …)` / suite 상속 `describe('API', { tags: ['regression'] }, …)`. config에 선언 필요(`test.tags:[{name:'smoke'}]`), `strictTags` 기본 true → 미선언 태그 사용 시 에러. 출처: vitest.dev/guide/test-tags, config/tags.
- 분리 실행: `vitest run --tags-filter="smoke"` / 불리언 `--tags-filter="regression && !flaky"` / `--list-tags`. 출처: vitest.dev/guide/test-tags.
- **4.1.0 미만 대안**: 이름패턴 — 제목에 `[@smoke]`, `vitest run -t "@smoke"`(정규식, full name 매칭). 출처: vitest.dev/guide/filtering. ⚠️ annotations(`context.annotate()`, 3.2+)는 **필터 불가** — 분리에 쓰지 말 것.

**Jest** (네이티브 태그 **없음** — 30.4 기준. "태그 전무"의 공식 부재 서술은 확인 필요)
- 이름패턴(전 버전): 제목에 `@smoke`, `jest -t '@smoke'`(정규식, describe 포함 full name). 출처: jestjs.io/docs/cli.
- 파일명 컨벤션 + projects: `jest.config.js` `projects:[{displayName:'smoke',testMatch:['<rootDir>/**/*.smoke.test.ts']}]` → `jest --selectProjects smoke`. 별도 config 분리 `jest -c jest.smoke.config.js`. 출처: jestjs.io/docs/cli, configuration.
- 경로 필터: **Jest 30+** `jest --testPathPatterns smoke`(복수); **Jest ≤29**는 `--testPathPattern smoke`(단수). breaking change 주의. 출처: jestjs.io/docs/upgrading-to-jest30.

**파일명 컨벤션 대안(러너 무관)**: `foo.smoke.test.ts` / `*.regression.test.ts`로 물리 분리. Vitest 위치 인자 `vitest run smoke`(경로 substring), Jest `testMatch`/`testRegex`, Playwright `testMatch:/.*smoke\.spec\.ts/`. Vitest 기본 include는 `*.smoke.test.ts`도 이미 전체 스위트에 잡으므로, 분리하려면 project/필터를 별도 지정해야 함.

### 3.5.3 sanity — 변경-스코프 선택(transient), 태그 아님 · **PR 전 실행**

sanity는 "**PR 올리기 전에**, 이번 변경이 건드린 **페이지/컴포넌트**만" 좁게 다시 도는 **선택 레인**이다. 태그를 갖지 않고 **호출 시점에만 리스트로 물질화**한다. 계획표에는 "대상 산정 레시피 + 실행 장치 + 폴백"을 기록한다.

**대상 산정 3단계** — 각 단계는 실패 시 **넓히는 방향으로만** 폴백한다(under-selection 회피, §3 배치원칙1).

1. **변경 파일 집합** — CI PR job은 `git diff --name-only origin/<base>...HEAD`(three-dot = PR 분기점 이후 변경), 로컬 실행은 `git diff --name-only HEAD`(staged·unstaged) + `git ls-files --others --exclude-standard`(새 파일). 러너 무관·문법 근거 불필요(git·경로 규칙).
   - **`<base>` 결정**: CI에서는 PR의 base 브랜치 변수(예: GitHub Actions `github.base_ref`)를 쓰고, 로컬/변수 부재 시 기본 브랜치를 감지한다(`git symbolic-ref refs/remotes/origin/HEAD`). **감지 실패하면 추측하지 말고 사용자에게 묻는다** — 잘못된 base는 조용한 under-selection을 만든다.
2. **역참조 확장 = "관련 페이지/컴포넌트"** — 변경 파일 자신의 테스트에서 멈추지 않고, **그 파일을 import하는 상위 페이지/컴포넌트**의 테스트까지 넓힌다(컴포넌트를 고치면 그 컴포넌트를 쓰는 페이지가 깨질 수 있으므로).
   - 1순위 **러너 네이티브 임포트 그래프**: Jest `--findRelatedTests <files>`/`--onlyChanged`, Vitest `--related <files>`/`--changed`, Playwright `--only-changed` — **정확 플래그·최소 버전은 사용 러너 문서에서 확인 필요**(근거 dossier 범위 밖).
   - 2순위 **grep 기반 import 역참조**(1홉 이상 반복).
   - ⚠️ **역참조는 원리상 불완전하다** — barrel re-export·동적 import·라우팅 규약·별칭 경로는 놓칠 수 있다. 불확실하면 좁히지 말고 전체(또는 해당 durable 스위트) 폴백.
3. **관련 페이지의 E2E — `@e2e-mock`만**(§3.6.5). ⚠️ **이 단계는 E2E가 Phase 1 선택 스코프에 있을 때만 수행한다**(스코프 가드, matrix/_index §1) — E2E 미선택이면 이 단계를 **건너뛰고** sanity 레인을 unit/integration으로만 구성하며, 계획에 "E2E 스코프 밖 — sanity 대상에 포함 안 함"으로 표기하고 확장 여부를 묻는다(E2E 경로도 Phase 1에서 받지 않았으므로 매핑 자체가 성립하지 않는다). 페이지↔스펙 매핑:
   - ① **경로 미러**(`src/pages/checkout/**` ↔ `e2e/checkout.spec.ts`)로 1차 매핑 →
   - ② 모호하면 스펙에 **대상 페이지 태그 `@page:/checkout`** 부여를 게이트 B에서 제안(코드 변경이므로 승인 대상) →
   - ③ 둘 다 실패하면 **`@e2e-mock` 전량 폴백**(좁힘 포기).
   - **`@e2e-live`는 sanity 대상이 아니다** — 수동 on-demand 전용(§3.6.5). 따라서 **E2E smoke 스펙(`@smoke`+`@e2e-live`)은 정의상 sanity 선택 대상에서 빠진다**(§3.6.5-a 귀결 3) — 누락이 아니라 규칙의 결과이며, sanity 블록에 "E2E smoke는 live 전용이라 이 레인에 포함되지 않음"을 표기한다.

**실행 장치(Phase 3 산출물)**: `test:sanity:changed`(unit/integration) + `test:sanity:e2e`(**E2E가 선택 스코프에 있을 때만** — 매핑된 `@e2e-mock`) + **CI PR job 스니펫**. CI yaml은 **직접 편집하지 않고 스니펫만 제안**한다(§3.5.5·배포 민감).

**차단성(운영 결정)**: unit/integration 실패 = **blocking**(머지 차단), 관련 페이지 mock E2E 실패 = **non-blocking 리포트**(E2E flaky가 PR을 잡는 것을 막기 위함). 표준 근거가 아니라 사용자 운영 결정임을 표기한다.

**부족분 생성**: 변경 관련 페이지/컴포넌트에 **테스트가 아예 없으면** 그 자리에서 새 테스트를 만든다(게이트 B 승인). 단 —
- 계층은 **Phase 1 선택 스코프 안**에서만(스코프 가드, matrix/_index §1),
- durable 방법론 태그는 **선택된 방법론 중에서만** 부여하고, 선택된 durable 방법론이 없으면 **태그 없이 기본체**로 두고 계획표에 그렇게 적는다(sanity 자체는 태그가 아니므로 `@sanity`를 대신 붙이지 않는다).

**무-태그 가드**: 코드에 `@sanity`를 심는 것을 금지한다. sanity는 선택이지 태그가 아니다(§3.5.6 caveat의 코드 레벨 대응물). — `@page:` 태그는 sanity 스위트 태그가 아니라 **대상 페이지 메타**이므로 이 가드 위반이 아니다.

### 3.5.4 분리 동작 검증 방법 (결정적 센서)

계획 라벨 vs 실행 분리의 최종 증명. durable 스위트별로, **membership 대수를 Phase 2 계획(게이트 A)에서 택1 선언**한 뒤 검증한다:
- **옵션 A(멀티태그)**: 각 테스트에 소속 durable 스위트 태그를 모두 부여(예 `@smoke`+`@regression`).
- **옵션 B(기본체+carve-out)**: regression=durable 기본체 전량, smoke/nightly는 명시 태그로 잘라냄.
- **선언 단위·제약**: 대수는 **계층별로** 선언할 수 있다(예: E2E=A, unit/integration=B). **E2E는 항상 옵션 A**다(§3.6.5-c). ID 없는 `@nightly` 전용 테스트(§4.6)가 있는 계층은 옵션 B의 "regression=기본체 전량"에 그 테스트가 끌려 들어가 AC-ID 단언(항목 6)을 깨므로 **옵션 A를 쓴다**.

durable 스위트 S(태그 T)마다 셀렉터를 **실제 실행/열거**해 확인:
1. **비공집합**: `SELECT(T)`가 0개면 phantom → 실패.
2. **정확 membership**: `SELECT(T)`가 계획이 선언한 집합과 정확히 일치(태그 누수=초과, 미부여=누락 둘 다 실패).
3. **부분집합/containment**: `SELECT(T) ⊆ 전체 실행 집합`, 옵션 A면 `@smoke ⊆ @regression` 등. **E2E는 포함관계가 규칙이다**(§3.6.5-c): `SELECT(@smoke) ⊆ SELECT(@regression)` — E2E는 옵션 A(멀티태그)를 강제하며 smoke 테스트가 `@regression`을 함께 지녀서 성립한다. E2E에는 `@nightly`가 없다.
4. **양방향 대조**: 물리 태그된 테스트 각각이 계획 row에 추적, durable 계획 row 각각의 테스트가 태그를 지님(orphan 없음).
5. **E2E smoke 격리 단언**(§3.6.5-a): ⓐ `test:smoke` 셀렉터 실행 목록에 **`@e2e-live` 스펙이 하나도 없다**(섞이면 실패 — CI 스테이지에 live가 들어간 것). ⓑ `@smoke`가 붙은 E2E 스펙에 **`@e2e-mock`이 없다**. ⓒ **E2E 태그 사다리**(§3.6.5-c): `@smoke`가 있는 E2E 스펙엔 `@regression`이 반드시 있고(빠지면 포함이 깨짐 → 실패), **E2E 스펙에 `@nightly`가 없다**(E2E는 smoke·regression만). ⓓ `test:e2e:smoke:live` 셀렉터가 **비-E2E smoke를 끌어오지 않는다**. ⓔ **포함·패스 단언**: E2E `@regression` 열거 ⊇ `@smoke` 열거(모드 무관 멤버십 기준)이고, regression의 mock 패스 + live 패스 합이 E2E regression 전체와 일치한다. **CI의 regression 실행 목록에 `@e2e-live` 스펙이 0개**이고(smoke가 `@regression`을 지니므로 `@e2e-mock` 필터가 빠지면 CI가 live를 끌어온다), **`test:nightly` 실행 목록에 E2E 스펙이 0개**다. ⓕ **모드 복제 파일 없음** — 같은 시나리오가 모드만 다른 두 스펙(파일)으로 존재하지 않는다.
6. **AC-ID 추적 단언**(§4.6): ⓐ `@smoke`·`@regression` 셀렉터 실행 목록의 테스트 제목이 모두 `[AC-…]`로 시작하고 그 ID가 입력 AC(또는 게이트 A에서 승인된 매핑표)에 있다 ⓑ ID 없는 테스트는 `@nightly`만 지닌 테스트이거나 sanity 부족분 생성 테스트이며, 각각 계획표 AC-ID 열에 사유가 적힌 승인된 행이 있다 ⓒ 입력에 없는 AC-ID를 지어내 붙인 테스트가 없다.

**sanity(transient)**: 레시피를 현재(또는 probe) 변경에 실행 → 구체 리스트 반환 · 비퇴화(전체를 반환하면 매핑 고장 — 단 §3.5.3의 **의도된 폴백**과 구분해 보고) · 변경 파일과 **그 파일을 import하는 페이지/컴포넌트**에 추적(역참조 확장이 실제로 걸리는지) · 매핑된 E2E가 `@e2e-mock`뿐이고 `@e2e-live`가 섞이지 않음 · 코드에 `@sanity` 태그 **없음** 단언.

> 검증은 위 3.5.2의 **검증된 셀렉터**(`--grep`/`--tags-filter`/`-t`/`--selectProjects`)를 실제 실행해 어떤 테스트가 뽑히는지 관찰하는 것으로 성립한다. **자기보고("계획했으니 분리됨") 불신** — 셀렉터 실행 출력으로만 인정(§5-2 실행 그라운딩과 동형).

**열거 방법·시점**: 실행하지 않고 **열거만** 한다 — Playwright `playwright test --list --grep …`(`--grep-invert`), Vitest `vitest list` + `--tags-filter`(4.1+) 또는 `-t <제목 패턴>`, Jest `jest -t <패턴> --listTests`. 두 러너를 묶은 스크립트는 러너별로 나눠 열거한다. ⓕ(모드 복제 파일)는 러너 출력으로 보이지 않으므로 E2E 스펙 파일 목록과 테스트 제목·AC-ID 중복을 비교해 확인하고, 6ⓑ의 sanity 부족분 테스트는 태그가 없으므로 계획표와 대조한다. ⓔ의 live 패스는 `test:e2e:regression:live`가 없으면(smoke와 같은 집합) smoke 레시피 열거로 대신한다. 6ⓐ의 "제목이 `[AC-`로 시작"은 describe 이름을 뺀 **테스트 제목 자체** 기준이다. **시점**: 마지막 E2E 행을 적용한 뒤 ⓐ~ⓕ와 항목 6을 한 번 전부 확인하고, Phase 4에서 다시 확인해 결과를 요약에 적는다.

### 3.5.5 CI 스테이지 ↔ 스위트 매핑 (§3 매트릭스 확장)

tier는 파이프라인 뒤로 갈수록 넓어짐(Google presubmit/postsubmit·Fowler DeploymentPipeline, HIGH). 스킬은 이 표를 계획에 첨부하고 게이트 A에서 승인받는다. **CI yaml은 직접 편집하지 않고 이 스니펫을 제안**한다(배포 민감·게이트 경계).

| CI 스테이지 | 트리거 | durable 실행(selector 스크립트) | sanity(transient) | 시간예산(목표치·대략) | 근거·신뢰도 |
|---|---|---|---|---|---|
| Pre-commit/local | 로컬 저장 | (훅) 빠른 unit 일부 | 로컬 on-demand: `test:sanity:changed` | 초~수십초 | HIGH [Google 로컬·Fowler] |
| PR-gate | PR push | `test:smoke`(@smoke, **비-E2E만**) + TIA 선택 regression(@regression 부분집합) | **주 사용처 — change-scoped PR job**: `test:sanity:changed`(**blocking**) + `test:sanity:e2e`(@e2e-mock 매핑분, **non-blocking**) | <5~15분 | 배치=**하네스 운영 결정**(표준 근거 없음)·상위 스테이지 원리만 HIGH |
| Merge to main | merge | `test:regression`(full 빠른 계층) + contract·security | — | ~10분 | MED [CircleCI] |
| Post-deploy(staging/canary) | 배포 후 | `test:smoke`(@smoke, **비-E2E만**·넓고 얕게) + canary | — | 수분 | MED-HIGH [Harness] |
| **(스테이지 없음) E2E live 패스** | **수동 on-demand** | `test:e2e:smoke:live`(`@smoke`+`@e2e-live`) · 포함 관계에 따라 `test:e2e:regression:live`(§3.6.5-c) — **CI 스테이지에 넣지 않음** | — | — | **사용자 운영 결정**(§3.6.5-a)·게이트 결정론 권고와 **상충** 병기 |
| Nightly | cron | `test:nightly`(@nightly — **unit/integration만, E2E 없음** §3.6.5-c) + `test:regression`(full — E2E는 **mock 패스**만) | — | 20분~수시간 | HIGH [Google postsubmit/TAP] |
| Pre-release(RC) | RC | 포괄 자동 스위트(=prod probers) | — | — | HIGH [Google Ch.23] |

**표 정직성 주석(그대로 인쇄)**:
- **sanity의 고정 스테이지는 표준 근거가 없다** — ISTQB/ISO에 sanity 스테이지 규정은 없다. 위 표의 **PR job 배치·차단성(unit/int blocking, mock E2E non-blocking)은 이 하네스의 운영 결정**이며 표준으로 포장하지 않는다(§3.5.3).
- **E2E는 smoke·regression만 있고 포함 관계(smoke ⊆ regression, §3.6.5-c)는 멤버십 기준이다** — CI의 regression 행은 E2E mock 패스만 돌리므로 E2E smoke는 거기 들지 않는다(E2E regression 전체 = CI mock 패스 + 수동 live 패스). `test:nightly`(`@nightly`)에는 E2E가 없다 — nightly 스테이지가 함께 돌리는 `test:regression`의 E2E mock 패스만 있다.
- **`@e2e-live`(실제 API 연동 E2E)는 CI 스테이지 행이 없다** — 고정 CI 스테이지를 두지 않고 **수동·on-demand로만** 실행한다(§3.6.5·§3.6.5-a). 계획에는 실행 레시피만 기록한다.
- **`test:smoke`는 비-E2E smoke만 뽑는다** — **E2E smoke는 `@e2e-live` 전용**(§3.6.5-a)이라 PR-gate·post-deploy·nightly 어디에도 들어가지 않는다. 따라서 **E2E smoke는 자동 배포 게이트가 아니라 승격 전 사람이 돌리는 수동 체크포인트**이며, 이 대가와 **게이트 결정론 권고(MinimumCD·Fowler, MED)와의 상충**을 계획·요약에 병기한다. 셀렉터가 E2E smoke를 끌어오지 않는지는 §3.5.4 분리 검증으로 확인한다(`test:smoke` 실행 목록에 `@e2e-live` 스펙이 섞이면 실패).
- **post-deploy의 `test:smoke`는 배포된 시스템을 직접 보지 않는다** — 비-E2E smoke는 unit/integration이라 항상 mock(§3.6.1)이므로 post-deploy 스테이지에서 돌아도 배포 환경을 자동으로 확인하지 않는다. 배포 환경을 실제로 확인하는 장치는 수동 E2E smoke(live)뿐이며, 이 사실을 계획·요약에 적는다.
- **시간예산은 목표치/예시**(다수 벤더 출처)이며 절대 표준 아님. smoke 3~7분 vs 15~30분은 소스마다 다르고 1차 근거 약함 → 대략치로만(§1).
- **선택·배치 > 우선순위**(우선순위는 총 실행량 불변); unknown 커밋엔 전체 폴백.
- **비율% 없음** — smoke 집합 크기는 "전체의 N%"가 아니라 AC 분해 + 프리셋 무게중심으로 결정. 70/20/10은 folklore(§2).

### 3.5.6 smoke=sanity 동의어 caveat를 유지하며 분리를 주는 법

ISTQB 용어집은 **smoke=sanity 동의어**이고 "smoke=넓고 얕음/sanity=좁고 깊음"은 실무 컨벤션(folklore)이지 표준이 아니다(§1). 이 절은 **용어가 아니라 실행 모델로 분리**하므로 caveat를 위반하지 않는다:
- 두 스위트를 "서로 다른 **표준** 방법론"이라 주장하지 않는다.
- smoke는 durable 태그(고정 selector·스테이지)로, sanity는 transient 선택(무-태그·on-demand)으로 **운영 방식이 다를 뿐**이며 이 차이는 근거가 뒷받침한다(§3).
- smoke/sanity가 등장하는 모든 산출물에 "ISTQB는 동의어; broad-shallow/narrow-deep 구분은 컨벤션·표준 아님"을 병기한다.
- **무-태그 가드**(§3.5.3)가 caveat의 코드 레벨 대응 — `@sanity`를 심지 않음으로써 folklore 구분을 표준 택소노미로 못 박는 것을 물리적으로 방지한다.

**추가 anti-pattern**: phantom suite(라벨만) · sanity reification(`@sanity` 고정 태그) · 태그 누수/미부여(selector≠membership) · fake separation(러너 기능 없이 분리된 척 → "advisory label only" 정직 강등) · over-narrowing sanity(매핑 실패 시 전체 폴백 포기).

---

## 3.6 API 경계 처리 축 (mock / live) — 계층·방법론과 직교하는 **테스트 속성**

§3.5가 "이 테스트가 **어느 스위트로 뽑히는가**"라면, 이 절은 "이 테스트가 **외부 API 경계를 어떻게 다루는가**"다. 새로운 분류 유형(4번째 축 카드)을 만드는 게 아니라 **각 테스트의 속성**이며, 계층이 기본값을 강제하고 **E2E만 모드를 태그로 선언**한다.

> **⚠️ 먼저 읽을 예외**: **Smoke 멤버십을 가진 E2E(=E2E smoke)는 `@e2e-live` 전용**이며 `@e2e-mock`을 부여하지 않는다 — 아래 기본값(E2E는 `@e2e-mock` 기본)의 **유일한 예외**다. 규칙 전문은 **§3.6.5-a**, 실행 규약은 **§3.6.5-b**.

### 3.6.1 계층별 기본값 (불변식)

> 아래 표의 첫 열은 **계층**이되, E2E 두 행은 **(계층 × 방법론 멤버십) 조합**으로 갈린다 — 이는 **새 분류 유형을 만드는 것이 아니라** 기존 두 축의 조합에 API 경계 속성이 달리 붙는 것이다(§3.6 머리말·축 직교성 유지).

| 계층 (E2E는 방법론 멤버십으로 갈림) | API 경계 | 강제 수준 | 태그 |
|---|---|---|---|
| **Unit** | **항상 mock**(외부 의존 0) | **불변식·예외 없음** | 불필요 — 계층이 함의 |
| **Integration** | **항상 mock**(narrow: 경계 코드 + 외부 서비스 double) | **불변식·예외 없음** | 불필요 — 계층이 함의 |
| **E2E — Smoke 멤버십** | **항상 live**(실제 API 연동) | **불변식 — `@e2e-mock` 부여 금지**(§3.6.5-a) | `@e2e-live` **필수** |
| **E2E — Regression** | **모드 선언 — 스위트 안에서 mock·live 혼합 가능** | `@e2e-mock` 기본 / `@e2e-live`는 명시 요청 시만. 포함된 E2E smoke는 live(§3.6.5-c) | **필수**(§3.6.5) |
| **E2E — Nightly·Sanity** | **없음** — E2E는 smoke·regression만 만든다(사용자 운영 결정, §3.6.5-c) | — | — |

- unit/integration이 실제 API로 나가면 **규약 이전에 정의상** 그 계층 자격을 잃는다 — small = 네트워크/디스크 없음, medium = localhost 경계(SWE@Google ch.11, MED). 그러므로 "live 호출 금지"는 선택지가 아니라 계층 정의의 귀결이다.
- E2E 기본은 `@e2e-mock`(CI 결정론). `@e2e-live`는 **사용자가 명시적으로 요청한 시나리오에만** 병기한다(자동 부여 금지) — **단 E2E smoke는 요청 없이도 규칙상 `@e2e-live`가 강제**된다(§3.6.5-a).

### 3.6.2 mock을 거는 경계 — 2종·네트워크 우선

| 순위 | 경계 | 기법(스택별 등가물) | 검증 범위 |
|---|---|---|---|
| ① **우선** | **네트워크 경계 인터셉터** | MSW·nock(JS), Playwright `page.route`(E2E), `responses`·`respx`·vcrpy(python), `httptest`(go), WireMock(java) | 실제 클라이언트 코드(요청 조립·직렬화·상태코드/에러 처리)가 **그대로 실행됨** |
| ② 폴백 | **모듈 경계 double** | `vi.mock`/`jest.mock`, monkeypatch, DI 주입 | 클라이언트 코드가 **검증 범위 밖으로 빠짐** → 그 사실을 계획표에 표기 |

- 인터셉터 도구가 저장소에 없으면 ②로 가되, "무엇이 검증되지 않는지"를 계획표 'API 경계' 열에 적는다. ① 도구 설치를 제안할 수도 있으나 **의존성 추가는 게이트 B 승인 대상**이다.
- E2E `@e2e-mock`의 mock 주입은 러너의 네트워크 인터셉트(예: Playwright `page.route`)로 하며 **모드 스위치로만 켠다**(§3.6.5).

### 3.6.3 fixture 확보 — 3단 폴백 + 출처 표기

**하네스는 fixture를 만들려고 live API를 직접 호출하지 않는다.** 확보 순서:

> **적용 대상**: unit/integration 전부 + `@e2e-mock` E2E. **E2E smoke(`@e2e-live` 전용)는 mock을 걸지 않으므로 fixture 대상이 아니다**(§3.6.5-a) — 대신 **실제 대상 환경과 테스트 계정/데이터**를 확보해야 하고 그 규약은 §3.6.5-b다.

1. **저장소 기존 fixture·응답 샘플 재사용**(가장 먼저 찾는다).
2. **사용자에게 실제 응답 샘플 요청**(붙여넣기·파일 경로).
3. **타입/OpenAPI/스키마·기존 코드에서 유도** → 반드시 **`[스키마 유도 — 실측 캡처 아님]`** 표기.

- **위치**: 저장소의 fixture 배치 관습을 감지해 따르고, 없으면 `<대상 파일 폴더>/__test__/fixtures/`에 둔다(파일명에 엔드포인트·상태코드를 담는다: `orders.get.200.json`).
- **출처 기록**: ①/②/③ 중 무엇인지와(③이면 실측 아님 표기) 캡처 시점을 **계획표 'API 경계' 열 + 적용 요약**에 남긴다.
- fixture는 커밋해 재현 가능하게 하고, 오라클은 fixture가 아니라 **기대(AC)** 에서 유도한다(§5-1 — fixture를 정답으로 굳히면 green-locks-bug와 같은 구조).

### 3.6.4 live 호출 금지 — 정적 검사(게이트 B)

**검사 대상**: unit/integration 전부 + `@e2e-mock` E2E 스펙·헬퍼·셋업. **`@e2e-live` 스펙(E2E smoke 포함)은 정의상 실제 API를 호출하므로 이 검사의 대상이 아니다** — 대상에서 뺐다는 사실을 게이트 B 보고에 한 줄로 남긴다(조용한 면제 금지). 모드 스위치 헬퍼는 **양쪽 경로를 다 갖는 파일**이므로, live 분기 밖(=mock 경로·공용 셋업)에 외부 호출이 새지 않았는지만 본다.

작성 후 **정적 검사만** 수행한다:
- 외부 URL 리터럴(`http(s)://` non-localhost)·환경변수 기반 실 엔드포인트 참조,
- mock 되지 않은 `fetch`/`axios`/HTTP 클라이언트 호출 경로,
- 실제 인증 토큰·시크릿 참조.

발견 시 **보고 → 교정 후에만** 게이트 B를 통과시킨다. **런타임 네트워크 차단은 강제하지 않는다** — 그러므로 **정적 검사 통과는 "네트워크로 안 나간다"의 증명이 아니다**(우회 가능). 이 한계를 그대로 표기한다(자기보고 불신 원칙의 정직한 적용).

**기존 테스트가 live를 호출하고 있으면**: 발견 사실·위치를 보고하고 **mock 전환 patch를 게이트 B로 제안**한다. 승인 시에만 수정한다(무단 개조 금지).

### 3.6.5 E2E 모드 태그 실체화 (`@e2e-mock` / `@e2e-live`)

- **스펙은 한 벌**이다. 시나리오를 mock용/live용으로 복제하지 않고, **모드 태그**로 "이 시나리오가 어느 모드에서 유효한가"를 선언한다. 둘 다 유효하면 두 태그를 병기한다.
- **모드는 기존 테스트의 태그로만 표현한다 — 파일을 따로 만들지 않는다.** mock 전용·live 전용 파일이나 디렉터리(예 `*.mock.spec.ts`·`*.live.spec.ts`·`e2e/live/`)를 만들지 않는다. 이미 있는 E2E 테스트에 모드를 적용할 때는 **그 스펙에 태그를 추가**한다. 저장소에 모드별로 복제된 파일이 이미 있으면 위치를 보고하고 **한 스펙으로 합치는 patch를 게이트 B로 제안**한다(승인 시에만 수정).
- **모드 전환은 명시 스위치로만** — env(`E2E_MODE=live`)·러너 project·fixture 라우팅 헬퍼. 태그 부여·셀렉터 문법은 §3.5.2 어댑터를 그대로 쓴다. **이 스위치 장치(헬퍼·project 설정·스크립트)는 그 자체가 새 코드/설정이므로 게이트 B 승인 대상**이며, 없는 것을 있는 척하지 않는다(스위치 없이 태그만 붙이면 `@e2e-live`는 실행 불가능한 라벨 = phantom).
- **스크립트는 실체가 있을 때만 만든다** — live 레시피(`test:e2e:smoke:live`·`test:e2e:regression:live`, §3.6.5-c)는 그 셀렉터가 실제로 뽑는 `@e2e-live` 스펙이 하나 이상이고 바로 아래 레시피와 결과가 다를 때만 추가한다(0개면 phantom suite·같으면 중복, §3.5.6).
  - 예(Playwright): `test('결제', { tag: ['@e2e-mock','@e2e-live'] }, …)` → CI `playwright test --grep @e2e-mock` / 연동 `E2E_MODE=live playwright test --grep @e2e-live`.
- **배치**: `@e2e-mock`은 선택 스코프에 따른 CI 스테이지(PR job·nightly 등). **`@e2e-live`는 고정 CI 스테이지를 두지 않고 수동·on-demand로만** 실행하며, 계획에는 실행 레시피만 기록한다.
- **스테이지가 모드를 바꾸지 않는다** — 어느 스테이지에서 돌든 실행 모드는 **태그 + 명시 스위치**가 결정한다. nightly가 게이트 테스트를 임의로 재-mock 하거나 live로 승격시키지 않는다.
- 분리 검증(§3.5.4)은 모드 태그에도 적용한다: `--grep @e2e-mock`이 계획 집합과 정확히 일치하고 `@e2e-live` 전용 시나리오를 끌어오지 않는지 **실행 출력**으로 확인한다.

### 3.6.5-a E2E smoke = **실제 API 연동 필수(live 전용)** — 사용자 운영 결정

**Smoke 멤버십을 가진 E2E 스펙은 `@e2e-live`를 필수로 부여하고 `@e2e-mock`을 부여하지 않는다.** §3.6.1 기본값(E2E는 `@e2e-mock` 기본)의 유일한 예외이며, "명시 요청 시만 live"라는 §3.6.5 규칙보다 **우선**한다(요청이 없어도 규칙상 강제).

| 항목 | 규칙 |
|---|---|
| 태그 | `@smoke` `@regression` + `@e2e-live`(포함 관계 태그 사다리, §3.6.5-c). **`@e2e-mock` 병기 금지**(mock 데이터로는 smoke를 검증할 수 없어 mock smoke는 만들지 않는다) |
| mock 주입 | **없음** — 네트워크 인터셉트(`page.route` 등)를 걸지 않는다. fixture 대상 아님(§3.6.3) |
| 대상 | 실제 백엔드(스테이징/카나리 등 사용자가 지정한 환경) |
| CI 배치 | **고정 CI 스테이지 없음** — PR-gate·post-deploy·nightly 어디에도 넣지 않는다 |
| 실행 | **수동·on-demand 전용**. 레시피 `test:e2e:smoke:live`(예: `E2E_MODE=live BASE_URL=… playwright test --grep "(?=.*@smoke)(?=.*@e2e-live)"`) |
| 하네스 실행 | 게이트 B에서 **대상 환경 제공 + 그 자리 승인이 둘 다 있을 때만** 실행(§3.6.5-b). 아니면 UNVERIFIED |

**파생 귀결(전부 명시적으로 산출물에 적는다)**:

1. **E2E smoke는 자동 배포 게이트로 작동하지 않는다.** 고정 스테이지가 없으므로 파이프라인이 이걸로 승격을 막지 않는다 — **승격 전 사람이 수동 실행하는 체크포인트**다. "smoke 게이트가 지켜준다"고 쓰지 않는다.
2. **CI의 `test:smoke`는 비-E2E smoke만 뽑는다**(주로 Smoke×Integration). 계획표·CI 매핑표(§3.5.5)에 "E2E smoke는 이 스크립트에 포함되지 않음"을 적는다.
3. **sanity 선택 레인은 E2E smoke 스펙을 고를 수 없다** — 레인 3단계는 `@e2e-mock`만 선택하는데(§3.5.3) smoke E2E엔 그 태그가 없다. 정의상 제외이며 누락이 아니다(그 사실을 sanity 블록에 표기).
4. **E2E smoke는 regression에 포함된다**(§3.6.5-c, smoke ⊆ regression). smoke 스펙은 `@smoke` `@regression` `@e2e-live`를 지니고, 회귀용 **`@e2e-mock` 복제 스펙은 만들지 않는다**(mock 데이터로는 smoke를 검증할 수 없다). 포함분은 regression의 **수동 live 패스**에서 돌고, CI mock 패스에는 들지 않는다(`@e2e-mock` 필터). E2E에는 nightly가 없다.
5. **결정론 근거와 상충한다** — "배포 게이트 smoke는 결정론적·외부 의존 0"(MinimumCD, MED / Fowler DeploymentPipeline, MED)과 정면으로 충돌하는 **사용자 운영 결정**이다. 산출물에 상충 사실을 병기한다. 완화 요인은 **고정 CI 게이트에 두지 않는다는 점**이다 — 외부계 불안정이 파이프라인을 막지는 않는다(대신 위 1번 대가를 치른다).

### 3.6.5-b live 실행 규약 — 하네스 live 호출의 **유일한 예외**

이 하네스는 원칙적으로 실제 API를 호출하지 않는다(§3.6.3 fixture 확보용 호출 금지). **유일한 예외**가 E2E smoke(`@e2e-live`)의 실행 그라운딩이며, 아래를 **모두** 만족할 때만 실행한다:

**실행 전제(하나라도 없으면 실행하지 않고 UNVERIFIED)**
- [ ] 사용자가 **대상 환경**을 제공했다(base URL / 엔드포인트).
- [ ] 사용자가 **테스트 계정·시드 데이터**를 제공했거나 "불필요"를 확인했다.
- [ ] **그 자리에서 실행 승인**을 받았다(게이트 B 안의 별도 문의 — 계획 승인이 실행 승인을 대신하지 않는다).

**안전 규약**
- **대상이 프로덕션이면 별도로 한 번 더 경고하고 재확인**한다(기본은 스테이징 권유). 사용자가 프로덕션을 재확인하면 따르되, 그 사실을 적용 요약에 남긴다.
- **부작용이 있는 시나리오**(결제·발송·삭제·외부 과금·알림)는 실행 전에 부작용을 **한 줄로 고지**하고 개별 확인을 받는다.
- **비밀은 대화에 붙여넣게 하지 않는다** — 환경변수·`.env`(gitignore 확인)·CI secret 경로로 받고, 명령·로그·산출물에 값이 남지 않게 한다(마스킹).
- **레이트리밋·정리(cleanup)** 를 고려한다. 생성한 데이터가 남으면 그 사실을 보고한다(하네스가 임의로 정리 삭제를 수행하지 않는다).

**실패 해석 — 3분류(2분류로 뭉개지 않는다)**
live에서는 mock에 없는 세 번째 원인이 생긴다. 이를 코드 결함으로 단정하지 않는다:
1. **테스트 결함**(셀렉터·대기·오라클) → 수정 제안.
2. **코드 결함**(AC 위반 발견) → 기록·문의.
3. **환경·외부계 문제**(대상 미배포·인증 만료·레이트리밋·시드 데이터 부재·업스트림 장애) → **결함이 아니라 환경 사유로 기록**하고 재실행/보류를 문의한다.

**결과의 지위**
- live 실행 결과는 **그 시점 그 환경 상태에 대한 관측**이다. 재현성이 보장되지 않으므로 **실행 시각·대상 환경을 함께 기록**하고, "연동이 정상이다"가 아니라 "**언제·어디에 대해** 통과했다"로 적는다.
- 실행하지 못했으면 레시피를 **UNVERIFIED**로 남긴다 — 미실행을 통과로 옮기지 않는다.

### 3.6.5-c E2E 스위트 범위·포함 관계 — **E2E는 smoke·regression만, smoke ⊆ regression** (사용자 운영 결정)

방법론 스위트별 API 모드는 계층마다 다르고, **E2E는 smoke·regression으로만 만든다.**

| 계층 | Smoke | Regression | Nightly | Sanity(부족분 생성) |
|---|---|---|---|---|
| Unit / Integration | mock | mock | mock | mock |
| E2E | **live만**(mock 데이터로는 smoke를 검증할 수 없다 — §3.6.5-a) | mock·live 혼합 가능 | **만들지 않음** | **만들지 않음** |

- **E2E에는 `@nightly`를 붙이지 않고**, `test:nightly` 실행에 E2E가 들지 않는다. sanity 부족분을 새로 만들 때도 E2E로는 만들지 않는다(선택 레인이 기존 `@e2e-mock` regression E2E를 골라 돌리는 것은 그대로다, §3.5.3).
  - **대가(계획에 병기)**: 근거상 nightly의 대표 귀착지(대규모·exhaustive E2E·cross-browser·real-device·visual)가 **이 하네스에는 없다** — 조합 강도표의 Nightly×E2E=STRONG은 근거 등급으로 남기되 생성하지 않는다. 비싼 E2E 회귀는 nightly로 미룰 수 없으므로 **크리티컬 여정 subset으로 좁힌다**. 사용자가 E2E nightly가 필요하다고 하면 이 결정을 바꿀지 묻는다(임의로 만들지 않음).
- **포함 관계**: E2E regression은 E2E smoke를 모두 포함한다.
- **태그 사다리**(E2E는 §3.5.4 옵션 A 멀티태그를 강제한다):

  | E2E 테스트 | 스위트 태그 | 뽑히는 실행 |
  |---|---|---|
  | smoke | `@smoke` `@regression` | smoke · regression |
  | regression | `@regression` | regression |

  각 스위트는 **자기 태그 하나로만** 고른다. regression 테스트에 `@smoke`를 붙이지 않는다 — 붙이면 smoke가 되어 live가 강제된다.
- **포함 관계로 붙는 `@regression`의 오라클** — E2E smoke가 smoke ⊆ regression 때문에 지니는 `@regression`은 regression 멤버십 체크리스트의 "완전 행위 보존 오라클" 요구에서 **예외**다. 오라클은 smoke 기준(여정 도달·상태 전이·계약 형태)을 그대로 두고, "이 여정의 regression 판정은 smoke 수준으로 얕다"는 대가를 계획에 적는다. 깊은 회귀 검증이 필요하면 같은 AC의 **하위 계층(integration·unit) regression 테스트**로 보강한다(mock 복제 스펙을 만들지 않는다).
- **모드 태그는 별개다** — E2E smoke는 `@e2e-live`만(예: `['@smoke','@regression','@e2e-live']`), regression 전용 테스트는 mock·live 중 하나 또는 둘 다.
- **실행은 모드별 두 패스** — E2E regression 실행 = **mock 패스**(`@regression ∧ @e2e-mock`, mock 스위치) + **live 패스**(`@regression ∧ @e2e-live`, live 스위치). 두 모드 태그가 병기된 스펙은 양쪽 패스에 모두 든다.
  - mock 패스 → CI(`test:regression`, merge·nightly 스테이지, §3.5.5). ⚠️ smoke도 `@regression`을 지니므로 **CI의 regression E2E 셀렉터는 반드시 `@e2e-mock`으로 거른다** — 거르지 않으면 CI가 live smoke를 끌어와 실제 API를 친다(§3.5.4-5ⓔ).
  - live 패스 → **고정 CI 스테이지 없음·수동 on-demand**(§3.6.5). 레시피 `test:e2e:smoke:live` / `test:e2e:regression:live`. **하네스는 regression live 패스를 실행하지 않는다** — 하네스의 live 실행은 E2E smoke 실행 그라운딩뿐이며(§3.6.5-b), regression live 패스는 레시피만 남기고 UNVERIFIED로 기록한다.
  - 예(Playwright): `test:e2e:regression:live` = `E2E_MODE=live BASE_URL=… playwright test --grep "(?=.*@regression)(?=.*@e2e-live)"` / regression mock 패스 = `playwright test --grep "(?=.*@regression)(?=.*@e2e-mock)"`. 러너별 문법은 §3.5.2 어댑터.
- **정직성 — CI의 regression은 mock 패스뿐이다.** 포함된 smoke(live 전용)와 그 밖의 live 멤버는 수동 live 패스에서만 돈다. **E2E regression 전체 실행 = CI mock 패스 + 수동 live 패스**로 적는다.
- **태그 누락이 포함 관계를 깨뜨린다** — smoke에 `@regression`이 빠지면 포함이 조용히 깨진다. 게이트 B에서 draft마다 확인하고 분리 검증(§3.5.4-5ⓒ)으로 실행 출력에서 다시 확인한다.
- **레시피는 실체가 있고 결과가 달라질 때만** — `test:e2e:regression:live`는 smoke 레시피와 같은 집합이면(live가 smoke뿐이면) 만들지 않는다(중복·phantom, §3.5.6).
- **모드는 태그로만 — 파일을 나누지 않는다**(§3.6.5): mock/live용 복제 스펙이나 smoke를 회귀용으로 옮긴 `@e2e-mock` 스펙을 만들지 않는다.
- **범위**: 포함 관계는 **E2E에만** 적용한다. unit/integration은 기존 membership 대수(§3.5.4 옵션 A/B)를 그대로 따른다.
- **AC-ID**: E2E는 smoke·regression뿐이므로 **모든 E2E 테스트가 제목에 AC-ID를 지닌다**(§4.6).

### 3.6.6 정직성 — **mock 통과 ≠ 연동 검증**

- fixture는 **캡처 시점의 스냅샷**이다. 실제 API가 바뀌어도 mock 테스트는 초록으로 남는다(**정의상** — 계약 drift를 구조적으로 못 잡는다). 이는 §5 green-locks-bug와 **같은 형태의 리스크**가 API 경계에서 재현된 것이다.
- 따라서 "mock E2E 전부 통과 = 연동 정상"이라고 **쓰지 않는다**. 산출물에는 "연동 확인 장치는 `@e2e-live` **수동 실행**뿐"을 병기한다.
- **`[스키마 유도 — 실측 캡처 아님]` 표기는 절대 지우지 않는다**(§3.6.3-3).
- **효과 수치 금지**: "mock 전환으로 flaky N% 감소", "mock E2E가 결함 X% 포착" 류는 근거가 없으므로 인용하지 않는다.
- 정적 검사(§3.6.4)의 한계("우회 가능·네트워크 미접속 증명 아님")를 감춘 채 "live 호출 없음 확인"으로 보고하지 않는다.

**E2E smoke(live 전용)에 대한 추가 정직성**(§3.6.5-a·§3.6.5-b):
- **"E2E smoke가 배포 게이트를 지킨다"고 쓰지 않는다** — 고정 CI 스테이지가 없으므로 자동 차단이 일어나지 않는다. 표기는 "**승격 전 수동 체크포인트**"다.
- **결정론 권고와 상충한다는 사실을 감추지 않는다** — 게이트 결정론·외부 의존 0 권고(MinimumCD·Fowler, MED)와 충돌하는 **운영 결정**임을 병기한다. "표준을 따른다"고 포장하지 않는다.
- **live 통과를 항구적 연동 보증으로 옮기지 않는다** — 관측은 실행 시점·대상 환경에 한정된다(실행 시각·환경 병기).
- **미실행을 통과로 옮기지 않는다** — 대상 환경·승인이 없어 못 돌렸으면 **UNVERIFIED**이며, "레시피를 만들었다"는 검증이 아니다.
- **live 실패를 코드 결함으로 단정하지 않는다** — 환경·외부계 원인(3분류)을 구분해 보고한다.
- **효과 수치 금지**: "live smoke로 장애 N% 조기 포착", "연동 결함 X% 차단" 류는 근거가 없다.

---

## 3.7 셀렉터 우선순위 축 (DOM 조회 규약) — 계층·방법론·API 경계와 **직교**

§3.6이 "이 테스트가 **외부 API 경계를 어떻게 다루는가**"라면, 이 절은 "이 테스트가 **화면의 요소를 무엇으로 찾는가**"다. §3.6과 마찬가지로 **새 축 카드가 아니라 테스트의 속성**이며, 계층·방법론·API 모드와 무관하게 **DOM을 조회하는 모든 테스트**에 같은 사다리가 적용된다.

### 3.7.1 적용 범위 — **DOM을 조회하는 테스트에만**

이 하네스는 도메인 무관이므로 스코프를 먼저 못박는다:

| 대상 | 적용 |
|---|---|
| Testing Library 계열(React/Vue/Svelte/DOM Testing Library)로 컴포넌트·페이지를 렌더해 조회 | **적용** |
| Playwright·Cypress 등 브라우저 러너로 페이지를 조회 | **적용** |
| 순수 함수·계산/판정 로직 unit, 서버 API integration, CLI·배치 등 **DOM이 없는 테스트** | **해당 없음** — 계획표에 `셀렉터: 해당 없음(비-DOM)`으로 적고 억지로 채우지 않는다 |

### 3.7.2 우선순위 사다리 — **위에서부터 시도하고, 불가능을 확인한 뒤에만 내려간다**

| 순위 | 그룹 | 쿼리 | 무엇을 근거로 찾는가 |
|---|---|---|---|
| 1 | **시각 요소 / 사용자 인터랙션** | **`getByRole`** | 접근성 트리의 역할(+ `name` 옵션) |
| 2 | 〃 | **`getByLabelText`** | 폼 컨트롤의 라벨 |
| 3 | 〃 | **`getByPlaceholderText`** | placeholder |
| 4 | 〃 | **`getByText`** | 화면에 보이는 텍스트 |
| 5 | 〃 | **`getByDisplayValue`** | 폼 요소의 현재 값 |
| 6 | **HTML5 · ARIA 속성** | **`getByAltText`** | 이미지 등의 `alt` |
| 7 | 〃 | **`getByTitle`** | `title` 속성 |
| 8 | **테스트 ID** | **`getByTestId`** | 테스트 전용 속성 — **위 1~7로 불가능한 값을 찾을 때만** |
| 9 | **최후 수단** | **`locator(...)`** (CSS/속성 셀렉터) | 위 사다리로 접근이 아예 불가능할 때만(§3.7.5) |

**적용 규칙**:
- **한 단계씩 내려간다.** 상위 쿼리로 **왜 안 되는지**(해당 role/label/text가 없음, 중복이라 특정 불가 등)를 확인한 뒤에만 다음 순위로 간다. "쓰기 편해서"·"덜 깨져서"는 내려갈 사유가 아니다.
- **1~5군과 6~7군은 별개 사다리**다 — 6~7은 "HTML5·ARIA 속성을 테스트하려는 경우"의 순위이지, 1~5의 연장선에서 무조건 6번을 먼저 시도하라는 뜻이 아니다. 찾으려는 대상의 성격(보이는 요소/인터랙션인가, 속성인가)으로 사다리를 먼저 고른다.
- **8·9번은 사유를 적는다.** `getByTestId`·`locator`를 쓰면 계획표·적용 요약에 **왜 상위 쿼리가 불가능했는지**를 한 줄로 남긴다(§3.7.5).
- **기존 테스트의 셀렉터는 무단 개조하지 않는다** — 사다리에 어긋나는 기존 셀렉터를 발견하면 **위치와 함께 보고**하고, 전환이 필요하면 **게이트 B로 patch를 제안**한다(§3.6.4의 live 전환 patch와 동형).

### 3.7.3 러너별 이름 어댑터 — **⚠️ 러너마다 이름이 다르다**

사다리는 **개념 순서**이고 API 이름은 러너를 따른다. 러너를 하드코딩하지 않는다(§3.5.2 어댑터와 같은 원칙).

| 순위 | Testing Library(정본 이름) | Playwright | 비고 |
|---|---|---|---|
| 1 | `getByRole` | `getByRole` | 동일 |
| 2 | `getByLabelText` | **`getByLabel`** | 이름 다름 |
| 3 | `getByPlaceholderText` | **`getByPlaceholder`** | 이름 다름 |
| 4 | `getByText` | `getByText` | 동일 |
| 5 | `getByDisplayValue` | **없음** | 아래 대체 규칙 |
| 6 | `getByAltText` | `getByAltText` | 동일 |
| 7 | `getByTitle` | `getByTitle` | 동일 |
| 8 | `getByTestId` | `getByTestId` | 속성명은 §3.7.4 |
| 9 | (`container.querySelector` 등) | `page.locator` / `container.locator` | §3.7.5 |

- **Playwright에 `getByDisplayValue`가 없다** — 이 자리를 억지로 만들지 않는다. 값으로 특정해야 하면 **상위 순위(주로 1·2번)로 요소를 찾고 값은 어서션으로 검증**한다(`expect(locator).toHaveValue(...)`). 즉 **"값으로 찾기"를 "찾고 나서 값을 단언하기"로 재설계**한다.
- Cypress에서 Testing Library 플러그인을 쓰면 정본 이름을 그대로 따르고, 안 쓰면 위 개념 순서를 러너의 등가물에 매핑한 뒤 **매핑 사실을 계획표에 적는다**(있는 척 금지).
- 비동기 조회가 필요하면 각 러너의 `find*`/자동 대기 형태를 쓰되 **순위는 동일**하다(`get`/`find`/`query` 접두는 대기·존재 여부 축이지 우선순위 축이 아니다).

### 3.7.4 테스트 ID 규약 — 속성명은 **팀 합의 사항**

- **하네스가 testid 속성명을 임의로 정하지 않는다.** Phase 0에서 저장소를 감지한다: `data-testid`·`data-test`·`data-qa`·`data-cy` 등 기존 사용 흔적, Playwright config의 `testIdAttribute` 설정, 린트 규칙.
- **감지되면 그 관습을 따른다.** 여러 개가 섞여 있거나 하나도 없으면 **추측하지 말고 묻는다**("팀에서 쓰는 test id 속성이 무엇인가요? 없으면 무엇으로 정할까요?").
- ⚠️ **제품 코드에 testid를 새로 추가하는 것은 테스트 파일 밖의 변경**이다 — 어떤 파일의 어느 요소에 무엇을 추가할지 제시하고 **게이트 B로 별도 승인**을 받는다(승인 없이 제품 코드를 건드리지 않는다). 승인이 안 되면 사다리 9번(locator)으로 내려가고 그 사실을 적는다.

### 3.7.5 최후 수단 `locator` — **허용하되 결합 비용을 적는다**

사다리 1~8로 접근이 불가능하면 `locator`를 쓴다. 형태 예:

```
await container.locator('[data-ga-action="찜하기_추가"]')
page.locator('[class*="SimpleRecentKeywordList_container"]')
```

**쓸 때 반드시 함께 적는 것** — 계획표의 셀렉터 항목과 적용 요약에 **`[최후 수단 locator — 사유]`**:

| 형태 | 결합되는 대상 | 깨지는 시점 |
|---|---|---|
| **다른 목적의 data 속성**(`[data-ga-action="…"]` 등 애널리틱스·트래킹 속성) | **테스트가 아닌 용도로 존재하는 계약** | 마케팅·트래킹 스펙이 바뀌면 테스트가 깨진다(테스트를 의식하지 않는 소유자가 바꾼다) |
| **클래스 부분일치**(`[class*="Foo_container"]`) | **구현 세부**(CSS Module 해시 클래스명·번들러 설정) | 컴포넌트 리네임·스타일 도구/설정 변경에 취약 |

- 이 결합은 §5-1의 "구현 스냅샷 오라클"과 **같은 형태의 리스크가 셀렉터 층에서 재현된 것**이다 — 다만 **오라클이 아니라 조회 경로**이므로 판정을 오염시키지는 않고, **깨지기 쉬움(brittleness)** 비용으로 계상한다.
- **위험은 경고하되 수용은 사용자 결정**이다 — 사용자가 이 방식을 택하면 따르고, 승인된 선택을 조용히 보류하지 않는다. 대신 사유와 결합 비용 표기는 지운다.

### 3.7.6 정직성

- 이 사다리는 **Testing Library 공식 Priority 가이드**(vendor-doc, MED)에 근거한 **설계 원칙**이다 — 근거의 성격은 *"사용자·보조기술이 요소를 찾는 방식에 가깝게 조회한다"*는 **의도**이지, 통제 실험으로 입증된 우월성이 아니다.
- **효과 수치 금지**: "getByRole로 바꾸면 flaky가 N% 준다", "testid를 없애면 결함을 X% 더 잡는다" 류는 **근거 0 — 인용하지 않는다**.
- **접근성 개선을 이 하네스의 성과로 주장하지 않는다** — `getByRole` 사용이 접근성 문제를 드러낼 수는 있으나, 이 하네스는 접근성을 측정하지도 개선을 보장하지도 않는다.
- **셀렉터는 오라클이 아니다** — 셀렉터를 상위 순위로 올려도 **오라클 강도는 올라가지 않는다**(§5는 별개 축). "getByRole을 썼으니 좋은 테스트"라고 쓰지 않는다.
- **사다리 준수를 점수화하지 않는다**(준수율 %·등급 금지) — 각 사용처의 **사유 표기**로만 다룬다.

---

## 4. AC → tier 분해 규칙 (GWT→AAA)

**GWT→AAA 매핑(표준, HIGH)**: Given=Arrange(사전상태) · When=Act(행위) · Then=Assert(기대변화). (Meszaros 4-Phase의 Setup/Exercise/Verify/Teardown과 동형)

**분해 규칙**:
- **AC 한 건 = 여러 tier로 분해**한다. 하나의 AC를 하나의 테스트로 등치하지 않는다.
  - 계산·판정·검증 **로직** → **Unit**
  - 모듈·컴포넌트·상태관리·**API 엔드포인트** 협업 → **Integration**
  - 로그인→결제 같은 **핵심 사용자 여정** → **E2E** (소수만)
- **AC ≠ E2E**: "모든 E2E는 인수테스트가 될 수 있으나 모든 인수테스트가 E2E는 아니다." AC를 자동으로 E2E로 밀어넣으면 상단이 과밀해진다(ice-cream-cone 안티패턴).
- **GWT는 어떤 tier로도 표현 가능** — 같은 Given-When-Then을 unit에서도 integration에서도 쓸 수 있다. tier는 "무엇을 격리하고 무엇을 실제로 쓸지"로 결정한다.
- 각 테스트에는 **명시적 오라클**(무엇이 성공/실패인가 = 기대 상태·불변식)을 부착한다. 스모크·동어반복(tautological) 어서션 금지(§5).

**계획 산출물의 한 행(row) 형식** (Phase 2에서 사용):
```
[AC-ID] · [계층(카드)] · [방법론(카드·태그+셀렉터)] · [조합 강도] · [API 경계(mock/live·경계기법·fixture 소스)] · [DOM 셀렉터(사다리 순위·8·9면 사유)] · 오라클(결합·기대·불변식) · 테스트 파일 경로 · GWT 요약 · 근거
```
> ⚠️ '방법론' 열의 **셀렉터**는 *스위트를 뽑는 러너 셀렉터*(`--grep @smoke`)이고, 'DOM 셀렉터' 열은 *화면 요소를 찾는 쿼리*(§3.7)다 — **다른 것이므로 혼동하지 않는다.**
> `DOM 셀렉터` 열(§3.7): 이 테스트가 DOM을 조회하면 **사다리에서 쓸 최상위 순위**를 적고(예 `1 getByRole(name)`), 8·9번이면 **사유**를 함께(`8 getByTestId — role/label/text로 특정 불가`, `9 locator [class*="…"] — 최후 수단·구현 세부 결합`). DOM이 없는 테스트는 `해당 없음(비-DOM)`.
> `API 경계` 열(§3.6): unit/integration은 항상 `mock`(+① 인터셉터/② 모듈 double, fixture 소스 ①재사용/②사용자제공/③스키마유도-실측아님), E2E는 모드 태그(`@e2e-mock` 기본 / 명시 요청 시 `@e2e-live` 병기). **⚠️ E2E × Smoke는 `@e2e-live` 전용**(`@e2e-mock` 금지·CI 스테이지 없음·수동 레시피·§3.6.5-a) — 이 행에는 fixture 소스 대신 **대상 환경·테스트 계정 확보 여부**를 적는다.

---

## 4.5 AC → 축 카드 조합 라우팅 (방법론 4 + 계층 3, 선택 스코프 내)

§4가 "AC를 어느 tier로 쪼개나"라면, 이 절은 "그 tier 테스트를 어느 방법론 선택에 태우나"까지 결합한다. **12개 셀로 미리 물질화하지 않고** [`matrix/`](matrix/_index.md)의 **방법론 카드 4개 + 계층 카드 3개(7개 축 카드)**를 라우팅 시점에 조합한다. 운영 절차·조합 강도 lookup·스코프 가드는 [`matrix/_index.md`](matrix/_index.md) §1~§3. 요약:

**Step 0 — 스코프 확정**: Phase 1의 (선택 방법론) × (선택 계층). **이 밖으로는 테스트를 추가하지 않는다**(스코프 가드, matrix/_index §1).
1. **AC를 슬라이스로 쪼갠다**(§4, AC≠단일 테스트).
2. **각 슬라이스에 계층 배정**(선택된 계층 중에서만; 계층 카드; scope + size/hermeticity; push-down; `small=unit` 1:1 금지). 자연 계층 미선택 시 push-down/up 또는 "스코프 밖 — 추가 안 함" 표시 후 확장 문의.
3. **각 (슬라이스, 계층)에 방법론 멤버십 부여**(선택된 방법론 중에서만·비배타·다중; 방법론 카드): Regression?(변경 traverse/보존 — 대부분) · Smoke?(happy·표면·결정론·showstopper) · Nightly 이연?(느림/비쌈/flaky/cross-browser/exhaustive/fuzz — **E2E는 nightly로 이연하지 않는다**, §3.6.5-c) · Sanity?(durable 아님 — transient change-scope, `@sanity` 안 심음).
4. **상황에 맞는 조합 선택**: 조합 강도 lookup(아래·matrix/_index §3)을 보고 **스코프 안에서** 가장 적합한 조합으로 구체화. **WEAK/DEGENERATE 조합**은 억지로 만들지 않고 스코프 내 STRONG 조합으로(스코프 내 STRONG이 아예 없으면 §1 폴백: '추가 안 함' 표기+확장 문의).
5. **계획표 행으로 적는다** — 한 슬라이스가 여러 방법론 suite에 속하면 membership 대수(§3.5.4 옵션 A/B)로 표기.

**조합 강도 lookup**(정직성 — 있는 척 금지, [`matrix/_index.md`](matrix/_index.md) §3):

| 계층 \ 방법론 | Smoke | Sanity | Regression | Nightly |
|---|---|---|---|---|
| Unit | WEAK | DEGEN/WEAK | **STRONG**(최고위험 오라클) | DEGEN(빈셀) |
| Integration | **STRONG** | DEGEN/WEAK | **STRONG** | STRONG-ish |
| E2E | STRONG(조건부)·live 전용 | DEGEN·생성 안 함 | STRONG(nightly 이연 불가) | STRONG(best) → **생성 안 함**(사용자 결정) |

- 실무 정합 최강: Smoke×Integration · Regression×{Unit,Integration} · Nightly×E2E — 단 **Nightly×E2E는 사용자 운영 결정으로 생성하지 않는다**(근거상 STRONG이지만 E2E는 smoke·regression만, §3.6.5-c).
- **Smoke×E2E는 강도와 별개로 API 경계가 고정된다** — 이 조합으로 만든 스펙은 **`@e2e-live` 전용**(실제 API 연동 필수·`@e2e-mock` 금지·CI 스테이지 없이 수동 레시피)이다(§3.6.5-a). "조건부 STRONG"의 조건(결정론·게이트 적격)이 이 결정으로 **성립하지 않으므로**, 이 조합을 고를 때는 **자동 게이트가 아니라 수동 체크포인트**라는 대가를 계획에 함께 적는다.
- **Sanity 열은 '생성 조합'에서만 DEGEN이다 — 실행 선택 레인으로는 1급이다.** 이 표는 "**새 테스트를 어떤 조합으로 만드는가**"의 강도이고, sanity는 이미 만들어진 테스트를 **골라 돌리는 선택 레인**(§3.5.3)이므로 이 표의 판정 대상이 아니다. 즉 Sanity×* = DEGEN(생성) **이면서 동시에** PR 전 change-scoped 실행 레인으로는 정상 운영된다 — 모순이 아니라 **다른 축**이다(ISTQB 동의어 근거와 실운영을 둘 다 유지).
- Nightly×Unit은 빈 셀(unit은 게이트 소속).
- 라우팅은 배타 분류가 아니라 **다중 멤버십**이며, **선택 스코프 안에서만** 추가한다. 비율%는 정하지 않는다. **⚠️ E2E는 smoke·regression만이고 포함 관계가 강제된다**(smoke ⊆ regression, §3.6.5-c) — smoke 슬라이스는 regression 멤버십을 함께 갖는다(`@smoke @regression`). smoke는 live 전용이라 회귀용 `@e2e-mock` 복제 행을 만들지 않는다. **smoke·regression 행은 AC-ID 필수**이고, AC-ID 열에 사유만 적힌 행(인수조건 밖)은 nightly·sanity에서만 허용한다(§4.6).
- 조합이 정해지면 **API 경계(§3.6)** 를 함께 확정한다 — unit/integration은 항상 mock, E2E는 `@e2e-mock` 기본, **E2E × Smoke는 `@e2e-live` 전용**(§3.6.5-a).
- 그 테스트가 **DOM을 조회하면 셀렉터 사다리(§3.7)** 도 함께 확정한다 — 쓸 최상위 순위와, 8·9번이면 사유. DOM이 없으면 `해당 없음(비-DOM)`.

---


## 4.6 인수조건 ID(AC-ID) 표기 — 스위트별 규칙 (사용자 운영 결정)

테스트가 어느 인수조건을 검증하는지 **테스트 코드에서 바로 보이게** 한다.

| 스위트 | 인수조건 기반 테스트 | 인수조건 밖 테스트 |
|---|---|---|
| Smoke | **AC-ID 필수** | **추가하지 않는다** |
| Regression | **AC-ID 필수** | **추가하지 않는다** |
| Nightly | AC-ID 필수 | **ID 없이 추가할 수 있다**(성능·부하·대규모 fuzz·exhaustive 경계 탐색 등) |
| Sanity(부족분 생성) | AC-ID 필수 | **ID 없이 추가할 수 있다**(변경 관련 대상에 테스트가 없는데 대응하는 AC가 없을 때) |

- **표기 형식**: 각 테스트 제목 맨 앞에 `[AC-1.2]`를 붙인다 — `test('[AC-1.2] 비로그인 사용자는 결제 버튼이 비활성이다', …)`. 한 테스트가 여러 AC를 검증하면 `[AC-1.2][AC-1.3]`처럼 이어 붙인다. `it(`·Playwright `test(` 모두 같고, `describe` 이름이 아니라 **각 테스트 제목**에 붙인다. 러너 제목에 대괄호를 쓸 수 없으면(예: pytest 함수명) 설명(docstring 첫 줄)에 같은 형식으로 적고 그 사실을 보고한다.
- **ID 출처**: 입력 AC에 있는 ID를 그대로 쓴다. 입력 AC에 ID가 없으면 `AC-n.m`(n = 사용자 스토리·기능 묶음 순번, m = 그 안의 인수조건 순번)을 붙인 **매핑표를 게이트 A에서 승인**받은 뒤 쓴다(조용히 만들지 않는다). 스토리 구분이 없으면 n=1로 두고 입력 순서대로 m을 매긴다(`AC-1.1`, `AC-1.2`, …). 한 AC에 Then이 여럿이어도 AC 하나에 ID 하나다. **입력에 없는 ID를 지어내 붙이지 않는다.**
- **태그와의 관계**: `@smoke`나 `@regression`이 하나라도 붙은 테스트는 AC-ID가 필수다. 그래서 ID 없는 테스트는 `@nightly`만 지닌 테스트이거나 sanity 부족분 생성 테스트뿐이다. E2E는 smoke·regression만이므로(§3.6.5-c) **모든 E2E 테스트가 AC-ID를 지닌다**.
- **ID 없는 테스트의 계획표 표기**: AC-ID 열에 ID 대신 **사유만** 적는다(예: `성능 — 1만 건 입력 처리 시간 확인`, `fuzz — 검색어 특수문자 조합`). 게이트 A에서 AC 기반 행과 **따로 묶어** 보여 주고 승인받는다. 스코프 가드(§4.5)는 그대로 — 선택된 방법론·계층 안에서만.
- **smoke·regression에 넣고 싶은데 대응하는 AC가 없으면**: 테스트를 지어내 넣지 않는다. AC를 추가할지(기획 쪽 결정) 또는 nightly·sanity에 ID 없이 둘지 사용자에게 묻는다.
- **인수조건 밖 추가 요청의 처리**: 사용자가 인수조건에 없는 테스트(예: 성능·부하)를 요청하면 Phase 1에서 받아 기록하고, Phase 2에서 AC와 같은 절차로 **선택 스코프 안**의 계층에 라우팅한다(방법론은 nightly·sanity만). 오라클(기대·임계값)은 **사용자가 준 값만** 쓰고, 없으면 `[확인 필요]`로 두어 게이트 A에서 묻는다(지어내지 않는다).
- **검증**: §3.5.4 항목 6(AC-ID 추적 단언).

## 5. 오라클 강도 — LLM 생성 최대 리스크와 가드

**핵심 리스크(HIGH)**: LLM은 명세(기대)가 아니라 **구현(실제 동작)을 포착·고착**시키는 경향이 있다. 버그 있는 코드를 "정답"으로 만들면, 그 테스트는 회귀를 초록으로 은폐한다. LLM은 자기 오라클의 정오도 스스로 잘 못 가린다(생성 > 판별).

**필수 가드(스킬이 개별 테스트 적용 전 항상 수행)**:
1. **오라클 오검증(cross-check)**: 어서션이 *현재 구현이 내는 값*을 그대로 굳힌 것인지, *AC가 요구하는 기대*를 검증하는지 구분한다. AC(기대)로부터 오라클을 유도하고, 필요하면 사용자에게 "이 기대가 맞습니까?"를 확인한다. **구현을 그대로 스냅샷한 오라클은 거부**한다.
2. **실행 그라운딩(execution grounding)**: 생성한 테스트를 실제로 **컴파일→실행**한다. 통과/실패를 자기보고가 아니라 실행 결과로 확인한다.
3. **flaky baseline 선결**: LLM 생성 전, **기존 flaky를 먼저 확인·고친다**. flaky한 컨텍스트를 주입하면 42~78%로 flakiness가 **전이(shortcut learning)**된다. 정렬 안 된 결과 순서 의존(ORDER BY 누락류)을 특히 경계한다.
4. **스모크/동어반복 어서션 금지**: `expect(true).toBe(true)`류, 방금 세팅한 값을 그대로 다시 읽는 어서션, 커버리지만 올리고 판정하지 않는 어서션은 "연기만 나고 경보는 안 울린다". 각 오라클은 **틀렸을 때 실제로 실패**해야 한다.
5. **false-alarm 인지**: 생성 오라클이 정상 코드를 실패시킬 수 있다(false alarm). 신뢰 전 정상 경로에서도 통과하는지 확인한다.
6. **fixture-as-oracle 금지**(§3.6): mock fixture는 **입력이지 정답이 아니다**. fixture 값을 그대로 기대값으로 복사하면 "캡처 시점 응답 = 명세"로 굳히는 것이라 §5-1과 같은 실패다. 기대는 AC에서 유도하고, fixture는 그 기대를 만들어내는 전제(Given)로만 쓴다. 스키마에서 유도한 fixture(§3.6.3-3)는 실측이 아니므로 특히 그렇다.

**정직성**: 오라클 정확도·개선 수치를 인용할 때 절대값을 못 박지 않는다(근거 dossier D·G절: 자동요약이 지어낸 %를 폐기한 이력). 프롬프트 전략은 zero/few-shot이 CoT/ToT보다 나은 경향(반직관, MED)이나 이는 상황 의존이다.

---

## 6. 3개 적응형 프리셋

스킬은 저장소를 감지(§7)해 **하나를 근거와 함께 추천**하고 사용자가 확정/변경한다. 어느 것도 비율을 하드코딩하지 않는다.

### 프리셋 1 — Trophy-lean (FE/컴포넌트 중심)
- 무게중심: **integration 최대 + 얇은 unit + 최소 E2E**
- AC 분해 기본값: integration 우선, 판정 로직만 unit, 필수 여정만 E2E
- CI 배치: PR(TIA로 unit+integration) / post-deploy(smoke) / nightly(full unit·integration — E2E는 사용자 결정으로 nightly 없음, §3.6.5-c)
- 근거: Dodds Testing Trophy(**FE 한정 명시** — MED), Fowler(HIGH)
- 주의: "integration ROI 우위"는 실증 아닌 **휴리스틱**

### 프리셋 2 — Google-pipeline (플랫폼/대규모)
- 무게중심: **성숙도별** — presubmit unit-heavy → merge full → nightly full
- AC 분해 기본값: presubmit unit/API, 넓은 검증은 postsubmit
- CI 배치: §3 매트릭스 그대로(presubmit selective → postsubmit full)
- 근거: SWE at Google Ch.23(HIGH), Meta 예측적 선택(HIGH)
- 주의: presubmit 지연 예산 ~10분대 유지 필요

### 프리셋 3 — Contract-honeycomb (분산/MSA·BFF)
- 무게중심: **integration(계약) 중심, E2E ≈ 0 지향**
- AC 분해 기본값: consumer/provider contract + integration
- CI 배치: PR(contract+integration) / nightly(contract·integration full) — E2E smoke는 수동 live 레시피, E2E nightly 없음(§3.6.5-c)
- 근거: Spotify Honeycomb(2018 백엔드 MSA — HIGH, FE 전이 MED)
- 주의: Honeycomb은 백엔드 MSA 맥락 — 프론트 전이 시 검증 필요

**공통 불변식(프리셋 무관)**: ① AC→tier 분해·AC≠E2E ② GWT→AAA 고정 ③ 오라클 가드(§5) ④ 비율 하드코딩 금지.

---

## 7. 저장소 감지 신호 (프리셋 추천용)

읽기 전용 감지(추측이 아니라 신호 인용). 확신이 낮으면 사용자에게 묻는다.

| 신호 | 프리셋 시사 |
|---|---|
| `package.json`에 react/vue/svelte + @testing-library/* + jest/vitest, playwright/cypress | **Trophy-lean** |
| 모노레포(pnpm/nx/turbo workspaces)·대량 패키지·기존 CI test-selection/TIA 설정 | **Google-pipeline** |
| 다수 서비스 디렉토리·OpenAPI/proto·pact/contract 테스트·docker-compose 다서비스 | **Contract-honeycomb** |
| 기존 테스트 프레임워크(jest/vitest/mocha/pytest/go test/junit …)·`test` npm script | (환경 감지 — Phase 0) |

**환경 감지(Phase 0)**: 테스트 러너·실행 명령·테스트 디렉토리 관습(`__tests__`, `*.test.*`, `*.spec.*`, `e2e/`)을 파악해 이후 적용 시 그 관습을 따른다. 감지 실패 시 사용자에게 확인.

---

## 8. Anti-pattern

- **AC를 통째로 E2E로** — 상단 과밀(ice-cream-cone). tier 분해 규칙(§4) 위반.
- **비율 하드코딩(70/20/10)** — folklore. 저장소 무관 강제 금지.
- **구현 스냅샷 오라클** — 버그를 정답으로 고착(§5-1).
- **스모크/동어반복 어서션** — 커버리지만 올리고 결함 못 잡음(§5-4).
- **flaky 방치 위 생성** — flakiness 전이(§5-3).
- **재시도로 flaky 마스킹** — 격리+백로그로 관리(재시도는 데이터 정제용만).
- **우선순위로 CI 비용 절감 기대** — 실행량 불변. 선택·배치로(§3-1).
- **승인 없이 파일 적용** — 이 스킬의 근본 위반. 계획→개별→최종 3게이트를 건너뛰지 않는다.
- **smoke=sanity 표준 구분을 단정** — ISTQB는 동의어. "컨벤션·표준 아님" 병기.
- **효과 수치 인용** — 근거 없는 %(80% 조기 포착 등)는 folklore.
- **셀을 12개로 미리 물질화·배타 유형으로 취급** — 축 카드 7개(방법론4+계층3)를 라우팅 시 조합(다중 멤버십)하지, 12개 독립 셀 파일을 두지 않음(§4.5·matrix/_index §0).
- **선택 스코프 밖 테스트 추가** — 사용자가 Phase 1에서 안 고른 방법론·계층에 테스트를 임의로 넣음. 스코프 밖은 "추가 안 함" 표기 후 확장 문의(matrix/_index §1 스코프 가드).
- **DEGENERATE/WEAK 조합을 억지로 채움** — Sanity 전 조합·Nightly×Unit을 있는 척 생성. 정직히 비우고 스코프 내 STRONG 조합으로 라우팅(§4.5).
- **nightly를 방법론으로 단정** — nightly는 CI-stage/스케줄 지연 축(ISTQB/ISO에 test type 없음). "어느 테스트를 게이트에서 빼 스케줄로 미루나"로 표기.
- **prioritization으로 CI 비용 절감 기대** — TCP는 latency만 줄이고 볼륨/비용 불변(정의상 — 재정렬은 총 실행량 불변). 절감은 selection·batching(무손실, ESEC/FSE 2023 arXiv:2308.13129)·병렬화로.
- **`small=unit/medium=integration/large=system` 1:1 매핑** — SWE@Google 반박. 근사일 뿐.
- **unit/integration이 실제 API로 나감** — 계층 자격을 정의상 잃는다. 네트워크 인터셉터(우선)/모듈 double + 캡처 fixture로 처리(§3.6.1·§3.6.2).
- **mock 통과를 연동 검증으로 보고** — fixture는 캡처 시점 스냅샷이라 계약 drift를 구조적으로 못 잡는다. 연동 확인은 `@e2e-live` 수동 실행뿐(§3.6.6).
- **스테이지가 API 모드를 바꿈** — 같은 E2E를 게이트에선 mock, nightly에선 live로 임의 전환. 모드는 태그+명시 스위치가 결정한다(§3.6.5).
- **스키마 유도 fixture를 실측처럼 표기** — `[스키마 유도 — 실측 캡처 아님]` 표기를 지우지 않는다(§3.6.3).
- **정적 검사 통과를 '네트워크 미접속 증명'으로 보고** — 정적 검사는 우회 가능하다는 한계를 함께 적는다(§3.6.4).
- **sanity 역참조를 조용히 좁힘** — barrel/동적 import로 매핑이 불확실한데 좁은 집합만 돌리고 넘어감. 불확실하면 전체 폴백(§3.5.3).
- **`@e2e-live`를 sanity/PR 게이트에 넣음** — 외부 API 불안정이 PR을 막는다. live는 수동 on-demand 전용(§3.5.3·§3.6.5).
- **E2E smoke에 `@e2e-mock`을 부여** — E2E smoke는 **live 전용**이다. mock smoke를 만들면 "실제 API 연동 필수"가 무력화되고, 두 벌이 생겨 어느 쪽이 게이트인지 모호해진다(§3.6.5-a).
- **live E2E smoke를 CI 고정 스테이지에 넣음** — PR-gate·post-deploy·nightly 어디에도 넣지 않는다. 수동 레시피(`test:e2e:smoke:live`)만 산출한다(§3.6.5-a).
- **`test:smoke` 스크립트가 E2E smoke를 끌어옴** — 셀렉터가 `@e2e-live`를 잡으면 CI가 실제 API를 치게 된다. 분리 검증 5-ⓐ로 단언한다(§3.5.4).
- **E2E 태그 사다리 누락·E2E nightly** — smoke 스펙에 `@regression`이 빠지면 포함이 깨지고, E2E에 `@nightly`를 붙이면 사용자 결정(E2E는 smoke·regression만)을 어긴다(§3.6.5-c). 회귀용 `@e2e-mock` 복제 스펙으로 포함을 흉내 내는 것도 금지.
- **CI regression 셀렉터에 `@e2e-mock` 필터 누락** — smoke 스펙이 `@regression`을 지니므로 필터 없이 고르면 CI가 live smoke를 끌어와 실제 API를 친다(§3.5.4-5ⓔ).
- **smoke·regression 테스트에 AC-ID 누락·지어낸 AC-ID** — smoke·regression은 인수조건 ID 기반으로만 만든다. ID 없는 테스트는 nightly·sanity에서만, 계획표 AC-ID 열에 사유를 적어 승인받는다(§4.6).
- **mock/live 모드를 파일로 분리** — `*.mock.spec.ts`·`*.live.spec.ts`처럼 모드별 파일을 만들면 시나리오가 두 벌로 갈라져 drift가 생긴다. 모드는 기존 스펙의 태그로만(§3.6.5).
- **E2E smoke를 "배포 게이트"로 서술** — 고정 스테이지가 없어 자동 차단이 일어나지 않는다. "승격 전 수동 체크포인트"로 적고, 게이트 결정론 권고와의 **상충**을 병기한다(§3.6.5-a 귀결 1·5).
- **대상 환경·그 자리 승인 없이 live 실행** — 하네스의 live 호출은 §3.6.5-b 전제를 **모두** 만족할 때만. 계획 승인이 실행 승인을 대신하지 않는다.
- **live 실패를 코드 결함으로 단정** — 환경·외부계(미배포·인증 만료·레이트리밋·시드 부재·업스트림 장애)를 3분류로 구분한다(§3.6.5-b).
- **미실행 live 레시피를 검증으로 보고** — "레시피를 만들었다"는 통과가 아니다. UNVERIFIED로 남긴다(§3.6.5-b).
- **live 통과를 항구적 연동 보증으로 확대** — 관측은 실행 시점·대상 환경 한정. 시각·환경을 병기한다(§3.6.6).
- **셀렉터 사다리를 건너뛰고 `getByTestId`·`locator`부터 씀** — 상위 쿼리가 **왜 불가능한지** 확인하지 않고 편의로 내려가는 것. 1→9 순서로 시도하고 8·9는 사유를 적는다(§3.7.2).
- **러너 API 이름을 잘못 옮김** — Playwright는 `getByLabel`/`getByPlaceholder`이고 **`getByDisplayValue`가 없다**. 정본 이름을 그대로 써서 없는 API를 부르거나, 없는 자리를 억지로 만들지 않는다(값은 상위 순위로 찾고 어서션으로 검증 — §3.7.3).
- **testid 속성명을 하네스가 임의로 정함** — 팀 합의 사항이다. 감지 → 없으면 문의(§3.7.4).
- **승인 없이 제품 코드에 testid를 추가** — 테스트 파일 밖의 변경이므로 게이트 B 별도 승인. 승인 없으면 사다리 9번으로 내려가고 그 사실을 적는다(§3.7.4).
- **최후 수단 locator를 사유·결합 비용 없이 사용** — 애널리틱스 속성(`[data-ga-action]`)·클래스 부분일치(`[class*="…"]`)는 각각 **다른 목적의 계약**·**구현 세부**에 결합된다. 사유와 깨지는 시점을 표기한다(§3.7.5).
- **셀렉터 개선을 오라클 강도·접근성 성과로 보고** — 셀렉터는 오라클이 아니고(§5는 별개 축), 이 하네스는 접근성을 측정하지 않는다. 준수율 점수화도 금지(§3.7.6).
- **E2E 미선택인데 sanity가 E2E를 끌어옴** — sanity 3단계는 E2E가 선택 스코프에 있을 때만. 미선택이면 건너뛰고 확장 문의(§3.5.3·matrix/_index §1).
- **스위치 없이 모드 태그만 부여** — `@e2e-live` 태그는 있는데 mode 스위치(env/project/fixture 라우팅)가 없으면 실행 불가능한 라벨(phantom live). 뽑히는 `@e2e-live`가 0개인데 live 레시피(`test:e2e:*:live`)만 만드는 것도 같은 실수(§3.6.5·§3.6.5-c).
- **base 브랜치 추측** — sanity diff의 `<base>`를 감지·문의 없이 가정하면 조용한 under-selection이 된다(§3.5.3-1).
