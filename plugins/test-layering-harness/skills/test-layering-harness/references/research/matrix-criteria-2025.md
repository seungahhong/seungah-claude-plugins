# 방법론 · 계층 조합 라우팅 기준 근거 dossier (2025+)

> **출처**: `test-layering-harness`의 "각 방법론×계층 셀마다 AC를 명확한 기준으로 분해" 설계를 위한 deep-research(8각도 plain-text fan-out WebSearch/WebFetch → 3렌즈 적대 감사 → 1 synthesis, schema 미사용). 2026-07-06 수행. 기존 [`test-strategy-research.md`](test-strategy-research.md)를 **셀 단위 라우팅 기준**으로 심화한 자매 dossier다(방법론·계층·CI 배치의 상위 근거는 그 문서 A~G절).
> **정직성 규칙 계승**: 출처 없는 수치 배제, 모순은 "모순:" 명시, folklore/반증된 통념 표기, 각 결론에 신뢰도(HIGH/MED/LOW)와 SOURCE-TIER(official-standard / primary-paper / vendor-doc / blog). 인용 수치는 특정 조직·표본 컨텍스트임을 전제로 읽을 것 — **셀 카드에 하드코딩 금지**(저장소 감지·리스크 근거로만).

이 dossier는 **근거·강도의 기록(evidence of record)**이고, 실제 AC 라우팅에 쓰는 운영 기준(포함/제외 체크리스트)은 [`../matrix/`](../matrix/_index.md) 아래 **7개 축 카드**(방법론 4 + 계층 3)에 있다 — 12개 셀로 미리 물질화하지 않고 라우팅 시점에 두 축을 조합한다(§3 강도 lookup 참조). 축 카드는 이 문서를 인용한다.

---

## 0. 축 직교성 원칙 (셀 = 교집합, 4번째 유형 아님)

계층(layer: Unit/Integration/E2E)과 방법론(methodology: Smoke/Sanity/Regression/Nightly)은 **직교하는 두 축**이며 같은 차원이 아니다.

- **계층 = 개별 테스트의 durable(영속) 속성**: "무엇을 실제로 실행하고 무엇을 double로 대체하는가(**scope**)" + "단일 프로세스·단일 머신·다중 머신 중 어디까지 자원을 쓰는가(**size/hermeticity**)". 한 번 작성되면 그 테스트에 물리적으로 박힌다. [SWE@Google ch.11: size와 scope는 직교(vendor-doc, MED) · IEEE 829-2008 §3.1.45 test-level(정의 유효·문서 철회) · ISTQB CTFL v4.0 component/integration/system 레벨(official-standard, HIGH)]
- **방법론 = 그 계층 테스트들 위에 얹히는 selection/tag**: ISO/IEC/IEEE 29119-1:2022은 regression·retest를 "test level이 아니라 **test design and execution choices**"(§4.4.6)로 규정하고, ISTQB는 regression을 "수정 이후·변경 안 된 영역"이라는 **트리거+범위**로만 정의해 **모든 레벨을 가로지른다**. [official-standard, HIGH]

**따라서 12개 셀은 "독립된 4번째 테스트 유형"이 아니라 "그 계층에 존재하는 테스트 중 그 방법론 선택(tag)에 드는 것들의 교집합"이다.** 셀은 배타적 버킷이 아니다 — 한 Regression×Unit 테스트가 동시에 Smoke 태그·Nightly 실행 대상일 수 있다.

**태그의 영속성도 갈린다**(기존 principles §3.5.1과 정합):
- **Regression·Nightly = durable tag**(테스트에 안정적으로 붙음)
- **Sanity = transient**(변경 국소 재확인이라는 일회성 selection이지 테스트 속성이 아님 → 코드에 `@sanity` 안 심음)
- **Smoke = durable tag이되 "명명된 선별 서브셋"**이라는 selection 성격 겸함

**라우팅 함의(핵심)**: 셀 배정은 두 판정을 **분리**해야 한다 — ① "이 AC를 어느 계층 테스트로 구현하는가(layer)" ② "그 테스트를 어느 방법론 게이트/스케줄에 태우는가(methodology)". 한 AC는 보통 여러 셀로 분해된다.

**⚠️ 축 정합성 caveat (반드시 표기)**: **"Nightly"는 엄밀히는 방법론(test type)이 아니라 CI-stage/스케줄 지연 축이다.** ISTQB/ISO에 "nightly" test type 항목은 **없다**. Smoke/Sanity/Regression과 동렬 배치는 category 불일치이며, Nightly 열은 "어느 계층·어느 테스트를 게이트에서 빼 스케줄 실행으로 미루는가"라는 **라우팅 결정**으로 취급해야 한다. [engineering practice + vendor(MED) + arXiv:2509.10279 — Targeted Test Selection이 lossy(>95%만 포착)임을 확립; nightly full 안전망은 이로부터의 파생 추론(primary; 안전망 원칙 HIGH, 논문 주제는 selection)]

---

## 1. 계층 판정 기준 (Unit / Integration / E2E) — AC 슬라이스별

계층은 **두 질문의 결합**으로 결정한다. (1) **Scope** — 무엇을 실제로 쓰고 무엇을 double하는가. (2) **Size/hermeticity** — 자원·프로세스·네트워크 경계. 두 축은 직교하므로 별도 판정 후 합성.

**Unit**
- 대상이 개별 컴포넌트/함수/연관 클래스 묶음의 **내부 로직**. [ISTQB component testing; IEEE 829 §3.1.7 "개별 컴포넌트 격리"]
- solitary(모든 협력자 double)든 sociable(실제 협력자 동반)든 "단일 unit의 behavior"를 검증하면 unit — **실제 협력자를 쓴다는 사실만으로 자동 integration이 되지 않는다**. [Fowler UnitTest, blog MED]
- 자원: 단일 프로세스(대개 단일 스레드), sleep·I/O·blocking·네트워크·디스크 없음(SWE@Google "small"). 네트워크/디스크 차단 sandbox에서 통과.
- 근거: ISTQB Glossary(HIGH) + IEEE 829-2008 §3.1.7(정의 유효) + Fowler(MED) + SWE@Google ch.11(MED).

**Integration**
- 대상이 조합된 컴포넌트 간 **인터페이스·상호작용·데이터 교환**. [ISTQB integration testing; IEEE 829 §3.1.8]
- narrow(경계 코드 + 외부 서비스 double) vs broad(live 서비스 필수) 구분 — Fowler는 broad를 "system/e2e"로 부르라 권고. **한정어 없이 "integration"만 쓰지 말 것**.
- 자원: 단일 머신 내(멀티 프로세스/스레드 허용), 네트워크는 오직 localhost(SWE@Google "medium"). 외부 머신/백엔드로 나가면 자격 상실.
- caveat: ISTQB CTFL v4.0은 integration을 **component-integration + system-integration 2레벨**로 분리 — 단일 "Integration" 셀은 표준 대비 단순화임을 인지.
- 근거: ISTQB Glossary(HIGH) + Fowler IntegrationTest(MED) + SWE@Google(MED).

**E2E / System**
- 대상이 완결·통합된 전체 시스템의 요구 충족(블랙박스·엔드투엔드)이거나 live 다중 서비스가 **필수**. [ISTQB system testing; IEEE 829 §3.1.37]
- test double을 쓸 수 없거나 여러 머신에 걸쳐야 하면 E2E(SWE@Google "large").
- **하향 판정 우선(push-down)**: UI에 비즈니스 로직이 없으면 subcutaneous(도메인/서비스 계층)로 내려 검증 — E2E는 크리티컬 사용자 여정에만 최소 예약(ice-cream-cone 방지). "acceptance"라는 의도가 E2E 계층을 강제하지 않는다(ISTQB: **level ≠ type**).
- 근거: ISTQB Glossary(HIGH) + Fowler Practical Test Pyramid/SubcutaneousTest(MED~canonical) + SWE@Google(MED).

**⚠️ 직교성 가드(KILL)**: **"small=unit / medium=integration / large=system 1:1 대응"은 SWE@Google가 명시 반박** — out-of-process 의존을 전부 double로 대체하면 broad-scope도 small일 수 있다. 근사로만, 판정 규칙으로 쓰지 말 것.

**계층 순서**: unit→integration→system(하위 통과 후 상위)는 대체로 유지. 단 ISO 29119 계층-순서 근거는 **위키/요약본 경유(secondary-summary of official-standard, MED)** — official 원문 미열람.

---

## 2. 방법론 멤버십 기준 (Smoke / Sanity / Regression / Nightly)

각 방법론 = "어떤 테스트를 고르는 selection인가".

**Smoke** (durable tag + 명명된 선별 서브셋)
- 1차 필터: "main functionality가 동작하는가 + planned testing 이전 go/no-go 게이트인가". [ISTQB smoke-test]
- broad-but-shallow: 전 기능 subset의 **표면만·happy path만**. 깊은 검증·경계값·edge를 하면 smoke 멤버 아님.
- **showstopper 규칙**: "이 기능이 깨지면 이후 테스트가 무의미해지는가" = 예 → smoke. 화이트리스트 예: 인증/로그인, 핵심 내비게이션, DB read/write, 핵심 트랜잭션, 핵심 외부 통합.
- 게이트 오라클/의존 조건: commit-게이트 smoke는 **결정론적·외부 의존 0**. [MinimumCD, community-standard, MED]
- 근거: ISTQB Glossary(official-standard, HIGH) + Fowler DeploymentPipeline(blog authoritative, MED) + MinimumCD(MED).

**Sanity** (transient — 독립 근거 취약)
- **ISTQB는 sanity를 smoke의 동의어**(smoke/confidence/intake와 상호 synonym, 동일 정의문)로 등재 → **독립 방법론 셀 근거 없음**. [official-standard, HIGH]
- 셀로 남기려면 둘 중 하나로 재정의 필수: **(a) Smoke의 동의어**(=Smoke 행과 중복), 또는 **(b) 변경 국소 재확인 = confirmation testing(re-testing) + change-scoped RTS**. ISTQB는 confirmation을 regression과 별개 term으로 정의("실패했던 케이스가 이제 통과하는가")하나, "sanity=confirmation의 의도"라는 매핑은 ISTQB 진술이 아닌 **추론 다리(MED)**.
- **"sanity가 smoke보다 깊다/좁고 깊다"는 시간축 구분은 folklore/vendor-practice** — official-standard로 포장 금지. 고정 CI 스테이지 주장도 표준 근거 없음. (이 하네스는 sanity를 (b) transient change-scope로 운영 — principles §3.5.3의 무-태그 가드와 정합.)

**Regression** (durable tag, 계층 직교)
- 정의: 수정 이후, **변경 안 된 영역**에 결함이 유입·노출되지 않았는지 확인. "픽스 후 실패 테스트 재실행"은 regression이 아니라 **confirmation**(혼동 금지). [ISTQB, HIGH]
- 멤버십 = "변경된 코드를 커버/traverse하는 테스트"를 per-commit 재계산(change-relevance). 계층 무관 — 모든 계층에 얹힘. [ISO §4.4.6]
- **세 레버 구분(비-호환)**:
  - **Selection**(TCS/TIA): 볼륨 감축 · lossy unless safe.
  - **Prioritization**(TCP): 재정렬 · **볼륨/비용 불변 · latency만 감축**.
  - **Batching**: **무손실** 볼륨 감축(대략 빌드실패율 낮을 때 성립).
- **safe-RTS 원칙(최고신뢰 앵커)**: 변경을 traverse하는 모든 테스트 선택 + **매핑 불가/미지 파일타입 시 full-suite fallback 강제**. under-selection이 주 실패모드. [Rothermel-Harrold 1997 primary + Microsoft·Datadog TIA vendor 교차, HIGH]
- 근거: ISTQB Glossary(HIGH) + ISO 29119-1:2022 §4.4.6(HIGH) + batching 무손실 볼륨 감축 = ESEC/FSE 2023 arXiv:2308.13129(Parallel Batch Testing, primary, HIGH); (prioritization이 비용 불변인 것은 정의상 — 재정렬은 총 실행량 불변).

**Nightly** (durable tag이되 **스케줄 축** — 방법론 아님, §0 caveat)
- "게이트에서 빼 스케줄(연속/야간/pre-release) 실행으로 미룬다"는 CI-stage 라우팅.
- 이연 트리거: (a) 선택기가 게이트에서 서브셋만 돌릴 때 **full-suite를 안전망**으로 [arXiv:2509.10279 Targeted Test Selection — 선택은 lossy(~5% miss)임을 확립; full-suite 안전망은 파생 추론, primary·원칙 HIGH], (b) per-run 비용/지연이 게이트 예산 초과(느림·비쌈), (c) 대규모 fuzzing 캠페인(별도 시간예산) [fuzz-in-CI 실증 arXiv:2510.16433, MED·날짜 caveat; **fuzz→스케줄 이연·property-based는 논문이 다루지 않는 engineering practice**], (d) cross-browser·real-device·perf/visual/a11y(clean 환경).
- **quarantine ≠ nightly**: flaky quarantine은 매 CI run 실행하되 non-blocking(중립 상태) — nightly-batch 지연과 다른 메커니즘, 한 셀로 붕괴 금지.
- 근거: arXiv:2509.10279 Targeted Test Selection(선택 lossy→full 안전망은 파생, primary·원칙 HIGH) + BrowserStack/TestRail(vendor/blog, MED) + Google TAP pub45861(foundational, MED, pre-2025).

---

## 3. 조합 강도 lookup (계층 × 방법론 12조합) — 축 카드 조합의 참조

**12개 셀 파일이 아니라** 두 축([`../matrix/`](../matrix/_index.md)의 방법론 4 + 계층 3 카드)을 라우팅 시점에 조합할 때 참조하는 **강도 표**다. 각 조합의 **강도 라벨**(STRONG=흔하고 유용 / WEAK=드묾 / DEGENERATE=보통 두지 않음)과 근거·신뢰도. 정직성상 WEAK/DEGENERATE 조합은 억지로 만들지 않고 어디로 라우팅되는지 축 카드가 안내한다.

| 셀 | 강도 | 실체화 | 핵심 근거 | 신뢰도 |
|---|---|---|---|---|
| **Smoke×Unit** | WEAK | durable-tag | unit은 게이트에서 전량 실행 → 별도 smoke 선별 저부가(Fowler CD); 존재는 함(Wikipedia 반증) | MED |
| **Smoke×Integration** | **STRONG** | durable-tag | commit-stage smoke의 정본 — Fowler CD "소수의 중요한 integration·acceptance 테스트로 이뤄진 작은 smoke suite" + MinimumCD 게이트 결정론 | MED(원서 HIGH) |
| **Smoke×E2E** | STRONG(조건부) | durable-tag | 크리티컬 여정 happy-path acceptance smoke; **flaky real-world E2E는 fast 게이트 부적격→full acceptance/nightly** | MED |
| **Sanity×Unit** | DEGENERATE/WEAK | transient | ISTQB sanity≡smoke 동의어 → Smoke×Unit 중복 또는 confirmation(픽스 후 그 unit 재확인)+change-scope | HIGH(동의어)/MED(매핑) |
| **Sanity×Integration** | DEGENERATE/WEAK | transient | 동상 — Smoke×Integration 중복 또는 변경 국소 integration confirmation | MED |
| **Sanity×E2E** | DEGENERATE | transient | 실무에서 거의 안 둠 — E2E 변경 국소 재확인 비용 대비 실익 낮음·표준 근거 전무 | LOW |
| **Regression×Unit** | STRONG(멤버십)·**최고위험(오라클)** | durable-tag | 계층 직교 멤버십 HIGH; **LLM green-locks-bug 최대 리스크 셀** | HIGH(메커니즘)/MED(수치) |
| **Regression×Integration** | **STRONG** | durable-tag | 멤버십 HIGH + safe-RTS(변경 traverse+full fallback); selection/batching ROI가 per-test 비용에 비례 | HIGH(멤버십)/MED(selection) |
| **Regression×E2E** | STRONG(멤버십)·대개 nightly 이연 | durable-tag | 전량 E2E regression은 exhaustive·비쌈→nightly; 크리티컬 여정 subset만 per-commit | MED |
| **Nightly×Unit** | DEGENERATE(빈 셀) | (해당 없음) | unit은 빠르고 싸서 게이트 소속 — nightly 이연 근거 없음 | LOW |
| **Nightly×Integration** | STRONG-ish | durable-tag | 느린 integration + 게이트 selection 안전망 | MED |
| **Nightly×E2E** | **STRONG(best nightly)** | durable-tag | 대규모 E2E·cross-browser·real-device·perf/visual/a11y·fuzz의 자연스러운 귀착지 | MED~HIGH |

**셀별 오라클 프로필 요약**(§5 원리 문서 §5와 정합):
- Smoke×* : **얕음**(reachability/no-crash + 최소 값). "초록=검증" 오독 금지.
- Regression×Unit : **강함(값-동등 S1)** — 최대 implementation-bias 리스크, 기대(AC) 기준 오검증 필수.
- Regression×Integration : **강함(완전 행위 보존)** — 현재 구현=정답 가정 금지.
- Regression×E2E / Nightly×E2E : 정확 출력 pinning 비현실적일 때 **메타모픽 관계(MR)를 옵션**(강제 아님·부분 판정).
- Nightly×E2E(fuzz) : crash/invariant 오라클(긴 예산); perf는 임계 기반. **non-blocking 리포트**.
- Sanity(confirmation 해석) : "실패했던 케이스가 이제 통과"(기대=픽스된 동작).

**교차 판정**: durable-tag 셀 중 실무 정합 최강은 **Smoke×Integration · Regression×{Unit,Integration} · Nightly×E2E**. transient/DEGENERATE로 재정의·경고 필수는 **Sanity 3셀 + Nightly×Unit**.

---

## 4. 정직성·모순·folklore 원장

**smoke=sanity 동의어 caveat (KEEP-STRONG, HIGH)**: ISTQB Glossary는 smoke/sanity/confidence/intake를 동일 정의·상호 synonym으로 등재(5각도 교차). **Smoke·Sanity를 별개 방법론 셀로 쪼개는 것은 표준 근거 없음** — Sanity 3셀은 모두 DEGENERATE/WEAK로 강등. "smoke보다 깊은 sanity"·"고정 CI 스테이지"는 folklore/vendor-practice로 표기하고 official-standard로 포장 금지. 이 하네스는 sanity를 (b) transient change-scope로 운영한다.

**비율 미하드코딩 (KEEP absence-of-claim, HIGH)**: ISTQB/ISO 29119/IEEE 어디에도 계층·방법론 간 목표 비율·효과크기 규정 **없음**. 셀 비율은 저장소 감지·리스크 근거로만.

**반증된 통념/folklore (KILL — 인용 금지)**:
- "70/20/10" 및 모든 고정 계층 비율 — 근거 0.
- "smoke가 버그 80% 조기포착 / 릴리스 50% 단축" — 출처 0.
- **"prioritization이 CI 비용 절감"** — TCP는 재정렬이라 총 실행량 불변 = 비용 불변(**정의상**; arXiv:2308.13129은 batching 무손실 근거이지 TCP 반증 논문 아님). 이 하네스가 거부해야 할 최다반복 folklore.
- "small=unit/medium=integration/large=system 1:1" — SWE@Google 반박.
- "regression=픽스 후 실패 테스트 재실행" — confirmation과 혼동.
- "AC=E2E" — level≠type 범주 오류.
- "quarantine=nightly로 이동" — 별개 메커니즘.
- "minimization(TSM)=selection(TCS)" — TSM 영구삭제 vs TCS per-change.
- "TIA가 항상 커버리지 유지" — 그래프 완전할 때만 safe(vendor-marketing).
- "IEEE 829가 현행 표준" — 철회(→29119-3), **정의 어휘만** 승계.

**Unsupported-number 폐기 목록**: "smoke under 2분/5–20 케이스/15–30분"(출처 상충), 블로그 케이스·분 예시, "285M Chromium/98% blanket"(2차 오류; 1차는 276M Chrome + 전략별 %), "flakiness 10%→26%"(1차 미확인), "E2E 유지비 N배"(출처 0), Bazel size별 RAM 20/100/300/800MB(원문 verbatim 실패 — timeout 60/300/900/3600s만 확인). batching 감축치·arXiv:2509.10279 수치(15%/95% 등)·oracle 정밀수치는 **attributable하나 특정 벤치마크/시스템 산물 → 기본 기대치·게이트 통과율로 승격 금지, 귀속 인용/예시로만**.

**Provenance/date caveat**: arXiv:2605.25356은 세션 스크래치패드 추출 + 제출일 1일 불일치(safe-RTS 개념은 Rothermel-Harrold 1997로 독립 근거화, 이 논문 특정수치 MED). 2025~2026 arXiv 클러스터(2507.17542·2510.03071은 **2025**; 2601.05542·2606.18168은 2026)는 방향성 수렴이나 개별 정밀수치는 MED. 특히 arXiv:2507.17542(AssertFlip)는 green-locks-bug를 직접 연구한 게 아니라 'LLM이 버그 코드에 통과 테스트를 쓴다'는 성향을 역이용하는 bug-repro 기법으로 **인접(증상적)** 근거일 뿐 — 직접 앵커는 2410.21136·2601.05542. arXiv:2510.16433 내부 날짜 표기 모순. ISO 29119 계층-순서는 위키/요약본 경유(secondary-summary, MED). ISO/IEC/IEEE 29119-1:2022는 유료 표준이라 원문 verbatim 미열람 — 핵심 clause §4.4.6(regression=design/execution choice)는 복수 2차 요약으로 교차 확인했으나, 절 번호의 verbatim 대조는 못 함(주장 정확도는 HIGH·절번호 provenance는 secondary).

**근거 못 찾은 셀/공백 (정직 표기 — 수치로 메우지 말 것)**:
- **Integration 전용 오라클 강도 요구**: 2025+ 1차/표준이 Integration 셀 고유 오라클 강도를 특정한 것 없음(metamorphic·상태커버리지 일반론만).
- **Sanity 전 셀**: 독립 방법론 근거 없음(성격 규정만).
- **Nightly×Unit**: 사실상 빈 셀(성격 규정만).
- **AC→계층 분해 규칙의 2025+ 피어리뷰 1차**: 미확인 — 근거는 ISTQB(표준)+Fowler/Vocke(practitioner 정론)뿐.
- **smoke 멤버십 선정 기준 2025+ 1차**: 없음 — ISTQB glossary + Fowler/CD가 최상위.
- **layer×method 측정된 효과크기**: 없음(비용 방향 추론만, 수치 부착 금지).

---

## 5. 소스 인덱스 (핵심 앵커)

| 소스 | TIER | 2025 유효 | 쓰임 |
|---|---|---|---|
| ISTQB Glossary / CTFL v4.0 (smoke·sanity·regression·confirmation·test level) | official-standard | yes(current) | 방법론·계층 정의, smoke=sanity 동의어, level≠type |
| ISO/IEC/IEEE 29119-1:2022 §4.4.6 (regression·retest = design/execution choice) | official-standard | yes | 방법론⊥계층 직교성의 표준 근거 |
| IEEE 829-2008 §3.1.7/3.1.8/3.1.37/3.1.45 (test-level 정의) | official-standard(철회) | 정의 어휘만 | unit/integration/system 정의(문서 철회, 29119-3 승계) |
| SWE@Google ch.11 (test sizes small/medium/large, size⊥scope, hermeticity) | vendor-doc | yes | 계층 판정의 자원/hermeticity 기준, 1:1 매핑 반박 |
| Fowler: DeploymentPipeline·UnitTest·IntegrationTest·Practical Test Pyramid·SubcutaneousTest | blog(authoritative) | canonical | smoke suite·unit vs integration·push-down |
| MinimumCD | community-standard | yes | commit-게이트 결정론·외부의존0 |
| Rothermel-Harrold 1997 (safe-RTS) | primary-paper | 앵커 | 변경 traverse+full fallback, under-selection |
| arXiv:2308.13129 (Parallel Batch Testing, ESEC/FSE 2023) | primary-paper | HIGH | **batching 무손실** 볼륨 감축 (TCP가 latency만·비용 불변인 것은 정의상 별개) |
| arXiv:2509.10279 (Targeted Test Selection) | primary-paper | 2025 HIGH(원칙) | 선택은 lossy(>95%만 포착) → **nightly full 안전망은 파생 추론**(논문 주제는 selection) |
| arXiv:2510.16433 (Continuous Fuzzing 실증) | primary-paper | MED(날짜 caveat) | 대규모 CI fuzzing이 별도 예산을 요함을 실증; **fuzz→스케줄 이연은 engineering practice**(논문은 property-based·스케줄링 미다룸) |
| arXiv:2410.21136·2601.05542·2606.18168 | primary-paper | 방향 HIGH/수치 MED | LLM 오라클 implementation-bias·green-locks-bug·오라클 신호강도 |
| arXiv:2507.17542 (AssertFlip) | primary-paper | 인접(MED) | green-locks 직접 연구 아님 — bug-repro 기법(증상적 근거) |
| BrowserStack·TestRail·Datadog·Microsoft(TIA) | vendor-doc | MED | 대규모 E2E·cross-browser→nightly, change-based selection |
| Google TAP (pub45861) | foundational | MED(pre-2025) | postsubmit 연속 실행 |

> 전량 raw 수집(86,926자)·3렌즈 적대 감사(23,312자)는 이 리서치 세션의 워크플로우 journal(`.../subagents/workflows/wf_b01e92c5-5d0/journal.jsonl`)에 보존. 이 문서는 그 KEEP-STRONG만 승격하고 KILL/DOWNGRADE를 반영한 것이다.
