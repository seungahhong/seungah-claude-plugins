# test-layering-harness 원리 (방법론 × 계층 · AC 분해 · 오라클 안전 · 프리셋 · 경계)

> 이 문서는 오케스트레이터(`../SKILL.md`)가 Phase 1~3에서 참조한다. 근거는 [`research/test-strategy-research.md`](research/test-strategy-research.md) 참조. 신뢰도(HIGH/MED/LOW)·folklore·모순 표기는 근거 dossier를 그대로 계승한다.

## 목차
1. 방법론(Smoke/Sanity/Regression/nightly) — 정의·트리거·실패 조치
2. 계층(Unit/Integration/E2E) — 트레이드오프·비율 정직성
3. 방법론 × 계층 매트릭스 (CI 단계 배치)
3.5. 방법론 스위트 실체화(materialization) — 계획 라벨 → 실행 가능한 분리
4. AC → tier 분해 규칙 (GWT→AAA)
5. 오라클 강도 — LLM 생성 최대 리스크와 가드
6. 3개 적응형 프리셋 (Trophy-lean / Google-pipeline / Contract-honeycomb)
7. 저장소 감지 신호 (프리셋 추천용)
8. Anti-pattern
9. 경계 (인접 하네스와 구분)

---

## 1. 방법론 — 정의·트리거·실패 조치

| 방법론 | 스코프 | 트리거(도는 시점) | 목적 | 실패 시 |
|---|---|---|---|---|
| **Smoke (BVT)** | 넓고 얕게(broad-shallow) | 빌드/배포 직후·승격 전 go/no-go 게이트 | 후속 테스트 돌릴 가치 있는 빌드인지 판별 | 즉시 정지·차단(block)·fix-forward vs rollback |
| **Sanity** | 좁고 깊게(narrow-deep) | **고정 스테이지 없음** — 표적 수정/핫픽스 직후 | 변경 영역만 집중 확인 | 해당 수정 반려·재작업 |
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
| Post-deploy(staging/canary) | 배포 후 | 핵심 E2E/API happy-path | **smoke** + canary | 수분 |
| **Nightly** | cron | full E2E/UI + full regression | full regression + nightly E2E | 20분~수시간 |
| Pre-release(RC) | RC | 포괄 자동 스위트 | acceptance suite | — |

**배치 원칙**:
1. **선택(selection)·배치(batching) > 우선순위(prioritization)** — 우선순위는 실행 순서만 바꿔 총 실행량을 못 줄인다. PR-gate는 TIA로 영향받은 테스트만 돌리되, **이해 못 하는 커밋엔 전체 실행 안전 폴백**.
2. **배포를 막는 게이트는 빠르고 신뢰도 높아야** — 느린 E2E를 배포 게이트에 두면 우회당한다. 무거운 것은 nightly로.
3. **sanity는 고정 스테이지가 아니다** — 표적 수정 직후 좁은 확인이라는 성격이므로 매트릭스에 고정 칸을 두지 않고 "변경 표적"에 붙인다.

---

## 3.5 방법론 스위트 실체화(materialization) — 계획 라벨을 실행 가능한 분리로

§3 매트릭스와 §4 row 형식에서 방법론 스위트(Smoke/Sanity/Regression/nightly)는 **계획표의 한 컬럼(라벨)** 으로만 존재한다. 라벨만으로는 (1) 코드에 물리 태그가 없고 (2) 그 스위트만 돌리는 실행 스크립트가 없고 (3) 분리가 실제로 되는지 확인할 방법이 없다 → **phantom suite**(계획엔 "smoke"가 있으나 독립 실행 단위로는 존재하지 않음). 이 절은 라벨을 **실행 가능한 분리**로 실체화하는 규칙이다.

### 3.5.1 durable-tag vs transient-selection 비대칭 (핵심)

네 방법론은 실행 모델이 **두 종류**로 갈린다. 이 비대칭은 임의가 아니라 근거에서 강제된다 — sanity는 "고정 스테이지 없음, 표적 수정 직후 좁은 확인이라는 성격"(§1 표·§3 배치원칙3).

| 방법론 | 실행 모델 | 실체화 아티팩트 | CI 고정 스테이지 |
|---|---|---|---|
| **Smoke** | **durable 태그** | 코드 물리 태그 `@smoke` + `test:smoke` 스크립트 | 있음 (post-deploy, PR-gate 소수) |
| **Regression** | **durable 태그/기본체** | `@regression`(또는 durable 기본체 전량) + `test:regression` | 있음 (merge full·PR 선택) |
| **Nightly** | **durable 태그** | `@nightly` + `test:nightly` | 있음 (cron) |
| **Sanity** | **transient 선택** | 태그 아님 — 변경-스코프 선택 **레시피(command)** | **없음** (변경 표적에 부착) |

- **Smoke/Regression/Nightly = durable 태그**로 실체화: 고정 tag 토큰 → 러너 네이티브 기법으로 코드에 물리 부여 → 전용 스크립트 → 고정 CI 스테이지.
- **Sanity = transient 선택**으로 실체화: `@sanity` 태그를 코드에 **심지 않는다**(무-태그 가드). 대신 "지금 이 변경이 건드린 테스트만" 조립하는 선택 레시피(§3.5.3)를 산출한다.

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

### 3.5.3 sanity — 변경-스코프 선택(transient), 태그 아님

sanity는 "안정된 빌드 위, 표적 수정/핫픽스 직후, 그 변경이 건드린 것만"(§1). 태그·CI 스테이지를 갖지 않고 **호출 시점에만 리스트로 물질화**한다. 계획표에는 "레시피 command + 폴백"만 기록한다.

1. **1순위(러너 무관·확정): git-diff + 경로 매핑** — `git diff --name-only`로 변경 소스 → 테스트 경로 관습(`*.test.*`/`__tests__`/mirror 경로)으로 역매핑. 문법 근거 불필요(git·경로 규칙).
2. **2순위(러너 네이티브 change-selection)**: 러너가 diff/임포트 그래프로 변경-스코프 집합을 계산하는 플래그가 있으면 사용. 예: Jest `--onlyChanged`/`--findRelatedTests <files>`, Vitest `--changed`/`--related <files>`, Playwright `--only-changed` — **정확 플래그·최소 버전은 사용 러너 문서에서 확인 필요**(근거 dossier 범위 밖).
3. **폴백 원칙**: 이해 못 하는(매핑 실패) 변경엔 좁힘을 포기하고 **전체(또는 해당 durable 스위트) 폴백** — under-selection으로 회귀를 놓치지 않기 위함(§3 배치원칙1).
4. **무-태그 가드**: 코드에 `@sanity`를 심는 것을 금지한다. sanity는 선택이지 태그가 아니다(§3.5.6 caveat의 코드 레벨 대응물).

### 3.5.4 분리 동작 검증 방법 (결정적 센서)

계획 라벨 vs 실행 분리의 최종 증명. durable 스위트별로, **membership 대수를 Phase 1에서 택1 선언**한 뒤 검증한다:
- **옵션 A(멀티태그)**: 각 테스트에 소속 durable 스위트 태그를 모두 부여(예 `@smoke`+`@regression`).
- **옵션 B(기본체+carve-out)**: regression=durable 기본체 전량, smoke/nightly는 명시 태그로 잘라냄.

durable 스위트 S(태그 T)마다 셀렉터를 **실제 실행/열거**해 확인:
1. **비공집합**: `SELECT(T)`가 0개면 phantom → 실패.
2. **정확 membership**: `SELECT(T)`가 계획이 선언한 집합과 정확히 일치(태그 누수=초과, 미부여=누락 둘 다 실패).
3. **부분집합/containment**: `SELECT(T) ⊆ 전체 실행 집합`, 옵션 A면 `@smoke ⊆ @regression` 등.
4. **양방향 대조**: 물리 태그된 테스트 각각이 계획 row에 추적, durable 계획 row 각각의 테스트가 태그를 지님(orphan 없음).

**sanity(transient)**: 레시피를 현재(또는 probe) 변경에 실행 → 구체 리스트 반환 · 비퇴화(전체를 반환하면 매핑 고장) · 변경 파일에 추적 · 코드에 `@sanity` 태그 **없음** 단언.

> 검증은 위 3.5.2의 **검증된 셀렉터**(`--grep`/`--tags-filter`/`-t`/`--selectProjects`)를 실제 실행해 어떤 테스트가 뽑히는지 관찰하는 것으로 성립한다. **자기보고("계획했으니 분리됨") 불신** — 셀렉터 실행 출력으로만 인정(§5-2 실행 그라운딩과 동형).

### 3.5.5 CI 스테이지 ↔ 스위트 매핑 (§3 매트릭스 확장)

tier는 파이프라인 뒤로 갈수록 넓어짐(Google presubmit/postsubmit·Fowler DeploymentPipeline, HIGH). 스킬은 이 표를 계획에 첨부하고 게이트 A에서 승인받는다. **CI yaml은 직접 편집하지 않고 이 스니펫을 제안**한다(배포 민감·게이트 경계).

| CI 스테이지 | 트리거 | durable 실행(selector 스크립트) | sanity(transient) | 시간예산(목표치·대략) | 근거·신뢰도 |
|---|---|---|---|---|---|
| Pre-commit/local | 로컬 저장 | (훅) 빠른 unit 일부 | **주 사용처**: `test:sanity:changed`(표적 수정 직후) | 초~수십초 | HIGH [Google 로컬·Fowler] |
| PR-gate | PR push | `test:smoke`(@smoke) + TIA 선택 regression(@regression 부분집합) | 없음(push 전 로컬 sanity) | <5~15분 | HIGH [Google presubmit ~11분·TIA] |
| Merge to main | merge | `test:regression`(full 빠른 계층) + contract·security | — | ~10분 | MED [CircleCI] |
| Post-deploy(staging/canary) | 배포 후 | `test:smoke`(@smoke, 넓고 얕게) + canary | — | 수분 | MED-HIGH [Harness] |
| Nightly | cron | `test:nightly`(@nightly full E2E) + `test:regression`(full) | — | 20분~수시간 | HIGH [Google postsubmit/TAP] |
| Pre-release(RC) | RC | 포괄 자동 스위트(=prod probers) | — | — | HIGH [Google Ch.23] |

**표 정직성 주석(그대로 인쇄)**:
- **sanity는 고정 스테이지가 없다** — 독립 행이 아니라 "표적 수정 직후 on-demand(주로 local/pre-push·hotfix)"(§3 배치원칙3).
- **시간예산은 목표치/예시**(다수 벤더 출처)이며 절대 표준 아님. smoke 3~7분 vs 15~30분은 소스마다 다르고 1차 근거 약함 → 대략치로만(§1).
- **선택·배치 > 우선순위**(우선순위는 총 실행량 불변); unknown 커밋엔 전체 폴백.
- **비율% 없음** — smoke 집합 크기는 "전체의 N%"가 아니라 AC 분해 + 프리셋 무게중심으로 결정. 70/20/10은 folklore(§2).

### 3.5.6 smoke=sanity 동의어 caveat를 유지하며 분리를 주는 법

ISTQB 용어집은 **smoke=sanity 동의어**이고 "smoke=넓고 얕음/sanity=좁고 깊음"은 실무 컨벤션(folklore)이지 표준이 아니다(§1). 이 절은 **용어가 아니라 실행 모델로 분리**하므로 caveat를 위반하지 않는다:
- 두 스위트를 "서로 다른 **표준** 방법론"이라 주장하지 않는다.
- smoke는 durable 태그(고정 selector·스테이지)로, sanity는 transient 선택(무-태그·on-demand)으로 **운영 방식이 다를 뿐**이며 이 차이는 근거가 뒷받침한다(§3).
- smoke/sanity가 등장하는 모든 산출물에 "ISTQB는 동의어; broad-shallow/narrow-deep 구분은 컨벤션·표준 아님"을 병기한다.
- **무-태그 가드**(§3.5.3-4)가 caveat의 코드 레벨 대응 — `@sanity`를 심지 않음으로써 folklore 구분을 표준 택소노미로 못 박는 것을 물리적으로 방지한다.

**추가 anti-pattern(§8에 합류)**: phantom suite(라벨만) · sanity reification(`@sanity` 고정 태그/스테이지) · 태그 누수/미부여(selector≠membership) · fake separation(러너 기능 없이 분리된 척 → "advisory label only" 정직 강등) · over-narrowing sanity(매핑 실패 시 전체 폴백 포기).

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
[AC-ID] · [tier] · [방법론 스위트] · 오라클(기대·불변식) · 테스트 파일 경로 · GWT 요약 · 근거
```

---

## 5. 오라클 강도 — LLM 생성 최대 리스크와 가드

**핵심 리스크(HIGH)**: LLM은 명세(기대)가 아니라 **구현(실제 동작)을 포착·고착**시키는 경향이 있다. 버그 있는 코드를 "정답"으로 만들면, 그 테스트는 회귀를 초록으로 은폐한다. LLM은 자기 오라클의 정오도 스스로 잘 못 가린다(생성 > 판별).

**필수 가드(스킬이 개별 테스트 적용 전 항상 수행)**:
1. **오라클 오검증(cross-check)**: 어서션이 *현재 구현이 내는 값*을 그대로 굳힌 것인지, *AC가 요구하는 기대*를 검증하는지 구분한다. AC(기대)로부터 오라클을 유도하고, 필요하면 사용자에게 "이 기대가 맞습니까?"를 확인한다. **구현을 그대로 스냅샷한 오라클은 거부**한다.
2. **실행 그라운딩(execution grounding)**: 생성한 테스트를 실제로 **컴파일→실행**한다. 통과/실패를 자기보고가 아니라 실행 결과로 확인한다(§ code-as-harness와 같은 결정적 센서 철학이나, 여기선 AC-tier 매핑 맥락).
3. **flaky baseline 선결**: LLM 생성 전, **기존 flaky를 먼저 확인·고친다**. flaky한 컨텍스트를 주입하면 42~78%로 flakiness가 **전이(shortcut learning)**된다. 정렬 안 된 결과 순서 의존(ORDER BY 누락류)을 특히 경계한다.
4. **스모크/동어반복 어서션 금지**: `expect(true).toBe(true)`류, 방금 세팅한 값을 그대로 다시 읽는 어서션, 커버리지만 올리고 판정하지 않는 어서션은 "연기만 나고 경보는 안 울린다". 각 오라클은 **틀렸을 때 실제로 실패**해야 한다.
5. **false-alarm 인지**: 생성 오라클이 정상 코드를 실패시킬 수 있다(false alarm). 신뢰 전 정상 경로에서도 통과하는지 확인한다.

**정직성**: 오라클 정확도·개선 수치를 인용할 때 절대값을 못 박지 않는다(근거 dossier D·G절: 자동요약이 지어낸 %를 폐기한 이력). 프롬프트 전략은 zero/few-shot이 CoT/ToT보다 나은 경향(반직관, MED)이나 이는 상황 의존이다.

---

## 6. 3개 적응형 프리셋

스킬은 저장소를 감지(§7)해 **하나를 근거와 함께 추천**하고 사용자가 확정/변경한다. 어느 것도 비율을 하드코딩하지 않는다.

### 프리셋 1 — Trophy-lean (FE/컴포넌트 중심)
- 무게중심: **integration 최대 + 얇은 unit + 최소 E2E**
- AC 분해 기본값: integration 우선, 판정 로직만 unit, 필수 여정만 E2E
- CI 배치: PR(TIA로 unit+integration) / post-deploy(smoke) / nightly(full E2E)
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
- CI 배치: PR(contract+integration) / nightly(cross-service E2E smoke)
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
- **승인 없이 파일 적용/커밋** — 이 스킬의 근본 위반. 계획→개별→최종 3게이트를 건너뛰지 않는다.
- **smoke=sanity 표준 구분을 단정** — ISTQB는 동의어. "컨벤션·표준 아님" 병기.
- **효과 수치 인용** — 근거 없는 %(80% 조기 포착 등)는 folklore.

---

## 9. 경계 (인접 하네스와 구분)

이 스킬의 축은 **"AC → 방법론×계층 택소노미로 계층별 테스트 계획 → 계획/개별/최종 3게이트로 순차 생성·적용"**이다. 다음은 범위 밖:

- **qa-agent-harness** — 리스크 노출(확률×영향) 기반 전략 → 오라클 명시 시나리오 → 자가치유 실행 → 결함/플래키/환경 트리아지의 end-to-end 에이전틱 QA. *리스크·오라클·자가치유·트리아지*가 축. 이 스킬은 *방법론×계층 택소노미·AC 분해·인간 게이트*가 축(오라클 강도는 공유 관심사지만 조직 원리가 다름).
- **backend-harness / test-generator** — 기존 백엔드 코드의 generate→compile→execute→repair 공진화 수리 루프. *백엔드·실행 수리*가 축.
- **review-harness / test-coverage-review** — AC↔테스트 커버리지를 **읽기 전용**으로 핸드오프 게이트 검수(테스트를 쓰지 않음). 이 스킬은 계획하고 **쓴다**.
- **frontend-harness / tdd** — FE 개발 워크플로우 내부의 test-first 실천. 이 스킬은 독립·도메인 무관·AC 기반.
- **spec-driven-development / acceptance-designer** — 에이전트가 코드 생성할 실행 가능 명세(spec) + 인수기준 설계. 이 스킬은 *이미 있는 AC*에서 계층별 테스트를 계획·적용.
- **git-harness** — 커밋/PR. 이 스킬은 최종 게이트에서 "반영" 재확인만 하고 커밋은 직접 하지 않으며 필요 시 git-harness로 핸드오프.
