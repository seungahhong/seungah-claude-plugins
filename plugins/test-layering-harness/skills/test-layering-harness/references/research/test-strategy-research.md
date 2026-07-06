# 테스트 방법론 × 계층 근거 dossier (2025+)

> **출처**: `test-layering-harness` 설계를 위한 deep-research(plain-text fan-out 5각도 병렬 조사 + 1 synthesis, schema 미사용). 2026-07-05 수행.
> **정직성 규칙 적용**: 출처 없는 수치는 배제, 모순은 "모순:" 명시, folklore/반증된 통념 표기, 각 결론에 신뢰도(HIGH/MED/LOW). '개선 N% 보장' 문구 없음. 인용 수치는 특정 조직·특정 표본 컨텍스트임을 전제로 읽을 것.

---

## A. 방법론 정의·트리거·CI 배치

| 방법론 | 정의(1줄) | 트리거(도는 시점) | 목적 | 실패 시 조치 | 신뢰도 · 출처 |
|---|---|---|---|---|---|
| **Smoke (BVT)** | 넓고 얕은(broad-shallow) 빌드 검증 관문 — "이 빌드를 더 테스트할 가치가 있나?" | 빌드/배포 직후(특히 staging 배포 후), production 승격 전 go/no-go 게이트 | 주요 기능 정상 여부로 후속 테스트 진행 판단 | 즉시 정지·아티팩트 캡처·fix-forward vs rollback 결정, 승격/심화 진행 차단(block) | 정의 HIGH [ISTQB smoke-test], 배치 HIGH [Harness DevOps Academy] |
| **Sanity** | 좁고 깊은(narrow-deep) 확인 — 특정 버그픽스/소규모 변경이 의도대로 동작하는지, 이미 안정된 빌드 위에서 | 표적 수정/핫픽스 직후 (고정 스테이지 아님) | 변경 영역만 집중 검증 | 변경 영역 회귀 시 해당 수정 반려·재작업 | 정의 MED [Yuri Kan; Harness], **스테이지 배치는 근거 못 찾음** (성격 규정이지 파이프라인 고정 위치 아님) |
| **Regression** | 넓고 깊은(broad-deep) 비회귀 — 변경 후 기존 기능이 깨지지 않았는지 | 이상적으로 매 커밋(속도 계층화), full은 main 머지·nightly | 전체 기능 보존 확인 | 짧은 피드백 루프로 PR 내에서 관찰·수정 후 재푸시(downstream 전파 전 교정) | HIGH [CircleCI], HIGH [Fowler 10분 빌드 원리] |
| **Nightly** | 선택 로직 없이 full regression + full E2E를 스케줄(cron)로 실행하는 안전망 | 야간 스케줄(cron), 실 디바이스/병렬 | 커밋 단위 선택 실행의 커버리지 갭 헤지, 지속 모니터링 | 발견 결함을 티켓화, 다음날 컨텍스트 복원해 수리(24h 피드백은 비용) | HIGH [arXiv 2509.10279 Targeted Test Selection — 선택은 lossy이므로 nightly full은 파생된 안전망], MED [Drizz TIA] |

핵심 배치 원칙(교차 합의, HIGH):
- **스코프-트리거 매핑은 소스 간 일관** — Smoke=넓고 얕음/배포 후·승격 전, Regression=넓고 깊음/매 커밋~main 머지, Nightly=full/스케줄 안전망. [ISTQB · Yuri Kan · CircleCI · arXiv 2509.10279]
- **Smoke 실행시간 목표 3~7분**, 이보다 길면 문제로 취급 — 배포 게이트가 딜리버리를 늦추면 안 됨. MED (벤더 목표치, 표준 아님) [Harness]. → **모순: A** 아래 G 참조(folklore 블로그의 "smoke 15~30분"과 상충).
- **2025+ 방향성 (HIGH)**: nightly-only regression은 24h 피드백 루프라는 **안티패턴**으로 재평가. targeted test selection으로 빠른 게이트를 만들되 nightly full을 병치하는 2-tier가 현대 배치의 핵심. [CircleCI · arXiv 2509.10279]

⚠️ **반증/논쟁(HIGH, 반드시 표기)**: ISTQB 공식 용어집은 sanity와 smoke를 **동의어(동일 정의)**로 취급한다. 업계가 애용하는 "smoke=broad-shallow vs sanity=narrow-deep" 구분은 표준이 아니라 실무 컨벤션(folklore)이다. [ISTQB sanity-test glossary] — 표준으로 단정 금지.
⚠️ **folklore(LOW)**: smoke 어원(하드웨어 연기), "smoke 스위트가 릴리스 시간 ~50% 단축·크리티컬 버그 80% 조기 포착"[Quash], "regression 90%를 5% 시간에" 등 효과 수치는 방법론·표본 미제시 → 1차 근거 없이 인용 금지.

---

## B. 테스트 계층 비율 — pyramid vs trophy vs honeycomb

**2025+ 결론(교차 합의)**: "정확한 비율%"를 다투는 것 자체가 distraction이라는 데 원저자들이 수렴한다. Fowler·web.dev·Dodds 본인 모두 "아키텍처와 사용자 이익에 맞춰 계층을 섞어라"로 귀결. — HIGH [web.dev "Pyramid or Crab?" · Fowler TestPyramid · Dodds "Write tests"]

각 모델의 핵심 주장:

| 모델 | 핵심 주장 | 맥락·한계 | 신뢰도 |
|---|---|---|---|
| **Pyramid (70/20/10)** | unit ≫ integration ≫ e2e | 70/20/10은 예시일 뿐 Fowler 본인이 "정확한 숫자 중요치 않다"고 상대화 → **비율은 folklore** | 형태 MED, 비율 LOW |
| **Testing Trophy** | 속도/비용이 아니라 "ROI=신뢰도"로 재배열, **integration을 가장 큰 층**으로 | 저자가 **프론트/브라우저 코드에 한정**해 제안했음을 명시 | 1차 정의 HIGH, 최적비율 실증은 아님 |
| **Honeycomb (Spotify)** | MSA는 복잡성이 상호작용에 있으므로 integration 중심, E2E("integrated")는 이상적 0 | **2018년·백엔드 MSA 맥락** — 프론트 전이 주의 | HIGH(1차), 전이 MED |
| **Ice-cream-cone** | 수동/E2E 과다 = 안티패턴(느린 피드백·고비용·RCA 실패) | 업계 광범위 합의지만 통제 실증 아닌 추론 | 확립된 통념 MED |

FE/컴포넌트 맥락 "integration 비중↑" 주장의 **근거와 반론**:
- **근거(휴리스틱, HIGH as 철학 / LOW as 실증)**: "테스트가 실제 사용 방식을 닮을수록 더 큰 신뢰를 준다" → mock 최소화한 integration이 신뢰/속도 트레이드오프의 최적점, 커버리지 ~70% 이상은 수확 체감. [Dodds] — 단 이는 **전문가 휴리스틱**이지 RCT류 검증이 아님.
- **반론**: "피라미드는 2025에도 유효 — E2E 남용이 오히려 비용·flaky를 키운다"[QAlified, MED]. "피라미드는 낡은 경제 모델(integration 작성 비용 급감)"[WireMock, LOW-MED, 벤더 마케팅].
- **정직성 메모(중요)**: **"integration 비중을 높이면 unit 대비 ROI가 높다"를 통제 실험으로 입증한 논문은 조사에서 못 찾음.** Trophy/Honeycomb은 전문가 휴리스틱이지 실증 검증된 최적 비율이 아니다.

각 tier 비용/속도/신뢰도(여러 1차 출처 수렴, HIGH [web.dev]):

| tier | 속도 | 비용 | 통합 신뢰 | 원인 국소화(RCA) |
|---|---|---|---|---|
| unit | 빠름(초) | 쌈 | 낮음 | 정확 |
| integration | 중간(분) | 중간 | 균형 | 양호 |
| E2E | 느림(10~30분) | 비쌈 | 최고 | **약함**("뭐가 틀렸다"는 알려도 "어디가"는 못 알림) |

E2E가 느리고·비싸고·flaky·RCA 약하다는 것은 **실증으로 뒷받침되는 확립된 합의(HIGH)**: 아래 E절의 flaky 클러스터·비용 근거 참조. 단 **"E2E여야 이 버그를 잡는다"는 통념은 반증**됨 — 희귀 경로 포착은 테스트 레벨이 아니라 엔지니어 역량 문제이고 값싼 unit이 더 많은 경계를 커버 [Aniche, MED-HIGH, 논리적 추론].

⚠️ **논쟁적/과장**: "피라미드는 죽었다"는 주장은 미해결 논쟁이며 과장이다. 논쟁의 상당 부분은 용어 불일치(web.dev). 원저자 이분법('트로피 vs 피라미드')도 Dodds 본인이 완화했다.

---

## C. 방법론 × 계층 매트릭스 (핵심 산출)

가장 단단한 앵커는 **Google presubmit vs postsubmit**(SWE at Google Ch.23, HIGH)와 **Fowler DeploymentPipeline**(앞단=빠름/뒷단=느림·확신↑, HIGH). 두 1차 근거가 정확히 수렴: **tier는 스테이지가 뒤로 갈수록 넓어진다.**

| 파이프라인 단계 | 트리거 | 배치 tier | methodology suite | 시간 예산(목표치) | 근거·신뢰도 |
|---|---|---|---|---|---|
| **Pre-commit / local** | 로컬 저장 | lint·정적분석·시크릿, 빠른 unit 일부 | (훅 게이트) | 초~수십초 | HIGH [Google 로컬 루프 · Fowler] |
| **Commit / PR-gate** | PR push | **unit(전량)** + integration(선택) + API, **TIA로 영향받은 테스트만** + smoke 소수 | selective regression + smoke | <5~15분 (Google presubmit 평균 ~11분) | HIGH [Google presubmit 통과 시 나머지 통과 95%+ · Datadog TIA] |
| **Merge to main** | merge | full unit+integration, contract, security scan | full regression(빠른 계층) | 8~10분 | MED [CircleCI progressive] |
| **Post-deploy (staging/canary)** | 배포 후 | **핵심 E2E/API happy-path** | **smoke**(넓고 얕게) + canary | 수분 | MED-HIGH [Harness · Total Shift Left] |
| **Nightly / scheduled** | cron | **full E2E/UI + full regression** (postsubmit 전량) | full regression + nightly E2E | 20분~수시간 (Google postsubmit 상시 420만 테스트) | HIGH [Google postsubmit/TAP · arXiv 2509.10279] |
| **Pre-release (RC)** | 릴리스 후보 | 포괄 자동 스위트 = prod probers와 동일 | acceptance suite | — | HIGH [Google Ch.23 성숙도 5단계] |

배치 근거 3줄:
1. **PR-gate 이동(2025+, MED-HIGH)**: 전량이 아니라 TIA/test-selection으로 "영향받은 테스트만" — 단 **flaky/stateful 테스트가 신호를 왜곡**하고, 이해 못 하는 커밋엔 **전체 실행 안전 폴백**이 원칙. [Datadog · minware · arXiv 2311.13413]
2. **게이트가 느리면 우회당한다(실무 격언, MED)**: 45분 E2E를 배포 게이트에 두면 개발자가 우회. 배포를 막는 테스트는 빠르고 신뢰도 높아야. [Total Shift Left]
3. **sanity는 고정 스테이지가 없다(근거 못 찾음)** — "표적 수정 직후 좁은 확인"이라는 성격 규정. 표의 시간 예산 다수는 목표치/예시(벤더 출처)이며 절대 표준 아님.

---

## D. AC(Given-When-Then)→테스트 생성 방법론 + LLM 근거

**GWT→AAA/4-Phase 매핑은 확립된 표준(HIGH)** [Fowler "Given When Then"]:

| Gherkin/GWT | AAA (Bill Wake) | 4-Phase (Meszaros) |
|---|---|---|
| **Given** = 사전상태 세팅 | Arrange | Setup |
| **When** = 명세할 행위 | Act | Exercise |
| **Then** = 기대 변화 | Assert | Verify |
| (암묵) | — | Teardown |

AC→tier 도출 규칙(확립된 합의, MED-HIGH [Fowler Practical Test Pyramid · Momentic]):
- **AC 한 건은 여러 tier로 분해된다** — 계산/판정 로직=unit, API 엔드포인트=integration, 핵심 사용자 흐름=E2E.
- **GWT는 단일 세분화 수준에 묶이지 않고 어떤 tier로든 표현 가능** [Fowler].
- **모든 E2E는 인수테스트가 될 수 있으나 모든 인수테스트가 E2E는 아니다** — AC를 자동으로 E2E로 등치하지 말 것(상단 과밀 유발). 각 층의 질문이 다름: "함수 맞나/컴포넌트 협업하나/사용자 흐름 되나". MED [Bunnyshell · getautonoma]
- **living/executable spec**: Gherkin+SbE(Specification by Example, Adzic)로 AC를 실행 가능 문서화. HIGH(원저자), 단 50+ 프로젝트 경험 종합이지 통제 실험 아님.
- ⚠️ **논쟁적(MED)**: "고전 피라미드는 acceptance 층을 빠뜨려 취약한 E2E에 떠넘긴다 → AC를 별도 acceptance 층으로 다뤄라"[Optivem] — 근거 있는 재해석이나 **컨센서스 아님**.

**LLM 생성의 신뢰성·오라클·flaky caveat**:
- **산업 사례(HIGH)**: user story→Gherkin(AutoUAT)→Cypress(Test Flow), GPT-4 Turbo. 시나리오 95% 유용·실행테스트 92% 유용하나 **즉시 사용가능은 60%뿐**(minor fix 8%, 재생성 24%, 폐기 8%). "유용성"과 "즉시 실행가능성"의 격차 = Gherkin→코드 변환·oracle 단계가 병목. **사람 리뷰는 전 구간 필수**. [arXiv 2504.07244, 단일 파트너사 self-report]
- **최대 리스크 = test oracle 강도(HIGH)**: LLM은 spec(기대)이 아니라 **구현(실제 동작)을 포착·굳히는 경향** → 버그 있는 코드를 "정답"으로 만들 위험. 자기 oracle의 정오도 스스로 못 가림(생성 > 판별). [arXiv 2410.21136, 24개 Java 레포 통제실험]
  - **정직성 주의(중요)**: 이 논문 초록에는 구체 %가 **전혀 없다**. 조사 중 자동요약이 "60~70%" 등 수치를 지어냈고 검증 후 **폐기**함. 인용 시 % 붙이지 말 것.
  - 완화(정성, HIGH): 의미있는 test/변수 이름(구현이 아니라 의도 반영)이 있으면 더 나은 oracle 생성.
- **오라클 컨텍스트 의존(HIGH)**: 클래스 전체(CUT) 컨텍스트가 메서드만보다 정확도 ~12.9%p↑(53.64% vs 40.38%), 컴파일률 76.26% vs 59.23%. **프롬프트 전략이 최대 영향(폭 25.3%p)이고 zero/few-shot이 CoT·ToT보다 우수**(CoT 31%·ToT 29%로 오히려 저하 — 반직관). [arXiv 2601.05542, AIware 2025]
- **false-alarm 위험(HIGH)**: 생성 오라클이 버그코드를 실패시키는 비율(70.84%)이 정상코드를 통과시키는 비율(58.13%)보다 높음 → 탐지한 "버그"가 실제 기대동작과 어긋날 수 있음. 신뢰 전 반드시 오검증. [arXiv 2601.05542]
- **flaky/hallucination(MED-HIGH)**: LLM 생성 테스트의 절대 flaky는 낮으나(0.0~0.7%), 수동검사 결과 지배 원인은 **ORDER BY 누락 = 정렬 안 된 결과 순서 의존**(115건 중 63~72건). temp 0에서도 발생. "flakiness 전이": 컨텍스트에 flaky가 주입되면 42~78%(SAP HANA ~69%·MySQL ~42%)로 복제 — shortcut learning. **권고: LLM 생성 적용 전 기존 flaky부터 고치고 맞춤 컨텍스트 제공.** [arXiv 2601.08998, ICSE-SEIP 2026]

---

## E. flaky·oracle·CI 비용 최적화

**Flaky(HIGH)**:
- **flaky는 고립 사건이 아니라 클러스터(systemic)로 발생** — 810개 중 75%(606개)가 클러스터 소속, 평균 클러스터 13.5개, 평균 2.9개 클래스에 걸침. 지배 원인은 **간헐적 네트워킹·외부 의존성 불안정**. → 개별 수리보다 **공유 근본원인 일괄 수리**가 정답. [arXiv 2504.16777, EASE 2025, 24개 Java·10,000 run·peer-reviewed]
- Google: 테스트 run의 ~1.5%가 flaky, 테스트의 ~16%가 flaky 이력(7개 중 1개꼴). MED — **2016년 수치로 오래됨**, 널리 인용되는 산업 기준선. [Google Testing Blog]
- **재시도(retry)는 "고치는" 게 아니라 "가리는" 것**(합의 HIGH). 단 **Meta는 재시도를 라벨 정제(일관 실패=진짜 regression vs 비재현 flaky 분리)에 사용** — 데이터 수집용으로는 정당. 방치 방지 위해 **자동 격리(quarantine)+버그 등록**으로 관리("격리는 해결이 아니라 TODO"). [Google · Meta]
- 비용 근거(MED-HIGH, 단일 기업): flaky 수리에 개발자 시간 ~1.28%(광의 2.5%), 중견팀 월 ~$2,250. [ICST 2024 산업 사례]

**Oracle problem(HIGH)**:
- 오라클 문제 = 올바른/잘못된 동작을 구분하는 문제, 자동화의 핵심 병목. 확립된 자동화 계열은 **명세/모델링·계약(contract)·metamorphic**이며 어느 것도 충분치 않을 때 **최종 오라클은 여전히 사람**("완전 자동 오라클"은 미해결). [Barr et al. TSE 2015 · Oracle Survey · Metamorphic SLR arXiv 2507.22610]

**CI 비용/시간 최적화 — 핵심 실증(HIGH/MED-HIGH)**:
- **선택(selection) > 우선순위(prioritization)**: Meta 예측적 선택은 전이 의존 테스트의 ~1/3만 실행해 인프라 효율 2배·regression 99.9%↑ 포착(요건: 결과 95%↑ 정확 예측). [engineering.fb.com, HIGH]
- **배치(batching)가 실패 무손실**: 대규모 실증(Chrome·JMRI) — 선택은 피드백 최대 96%↓·실행 66%↓지만 **실패의 최대 55%를 놓칠 수 있음**; 배치는 **실패를 하나도 놓치지 않으면서** 피드백 최대 99%↓·실행 최대 98%↓. [EMSE 2025, MED-HIGH]
- **우선순위는 원리적으로 비용 절감력이 없다** — 실행 순서만 바꿀 뿐 총 실행량 불변. "TCP가 CI 비용을 줄인다"는 통념의 중요한 반례. [EMSE 2025, MED-HIGH]
- **mutation 유도 > 커버리지 유도**: Meta ACH는 미탐 결함(mutant)만 표적 생성, test-a-thon에서 73% 수용. 등가 mutant 탐지는 전처리로 precision/recall 0.79/0.47→0.95/0.96 → **후처리·정적/동적 검증 레이어 필수**. [arXiv 2501.12862, HIGH, 10,795 Kotlin 클래스 프로덕션]

**실무 권고(수렴된 처방)**:
1. flaky는 클러스터로 보고 공유 원인 일괄 수리 + 자동 격리 + 수리 백로그(재시도로 마스킹 금지).
2. CI 비용은 **선택·배치·병렬화로 줄이고 우선순위에 기대지 말 것**. unknown 커밋엔 전체 폴백.
3. 생성/실행 테스트는 raw로 믿지 말고 **컴파일→정적→동적→mutation 게이트**를 쌓고, false-alarm·flakiness 전이를 오검증. "깨끗한 baseline + 맞춤 컨텍스트"가 선결조건.

---

## F. 실무 권고 — "AC→계층별 테스트 스킬"이 채택할 기본 구성

세 옵션 모두 공통 불변식(교차 합의 근거): ① AC 한 건은 tier로 분해(unit/integration/E2E), AC≠E2E 등치 금지 ② GWT→AAA 매핑 고정 ③ LLM 생성물은 oracle 강도가 최대 리스크 → 사람 리뷰 게이트 + 실행 그라운딩 필수 ④ 비율%에 집착하지 말고 아키텍처에 맞춤.

| | **옵션 1: Trophy-lean (FE/컴포넌트)** | **옵션 2: Google-pipeline (플랫폼/규모)** | **옵션 3: Contract-honeycomb (분산/MSA·BFF)** |
|---|---|---|---|
| **무게중심 tier** | integration 최대 + 얇은 unit + 최소 E2E | 성숙도별(presubmit unit-heavy → nightly full) | integration(계약) 중심, E2E ≈ 0 지향 |
| **AC 분해 기본값** | AC→integration 우선, 판정로직만 unit, 필수여정만 E2E | AC→presubmit unit/API, 넓은 검증은 postsubmit | AC→consumer/provider contract + integration |
| **CI 배치** | PR: TIA로 unit+integration / post-deploy: smoke / nightly: full E2E | C절 매트릭스 그대로(presubmit selective → postsubmit full) | PR: contract+integration / nightly: cross-service E2E smoke |
| **적합 상황** | 브라우저/컴포넌트 중심 프론트, 팀 소~중 | 대규모 모노레포, 성숙 CI 인프라, TIA/test-selection 보유 | 서비스 경계 다수, E2E flaky·RCA 비용이 큰 조직 |
| **근거** | Dodds Trophy(FE 한정 명시) MED, Fowler HIGH | SWE at Google Ch.23 HIGH, Meta 선택 HIGH | Spotify Honeycomb(2018 MSA) HIGH, 전이 MED |
| **주의** | integration ROI 우위는 **실증 아닌 휴리스틱** | presubmit 지연 예산 ~10분대 유지 필요 | Honeycomb은 백엔드 MSA 맥락 — FE 전이 검증 필요 |

**권장 기본값**: 신규 스킬이 FE/컴포넌트를 주 대상으로 한다면 **옵션 1을 default, 옵션 2를 "규모 확장 시" 프리셋**으로 노출. 비율은 하드코딩하지 말고(70/20/10은 folklore) "AC→tier 분해 규칙 + CI 단계 배치(C절 표)"를 산출하되, LLM 생성 테스트에는 **oracle 오검증 + flaky-baseline 선결 체크 + 사람 승인 게이트**를 기본 내장할 것.

---

## G. 모순·미해결·낮은 신뢰 항목

**모순(cross-validation에서 드러남)**:
1. **모순: ISTQB(smoke=sanity 동의어, HIGH) vs 실무 컨벤션(smoke=broad-shallow / sanity=narrow-deep, MED)** — 1차 표준과 다수 블로그가 정면 충돌. 스킬은 컨벤션 쪽을 쓰되 "표준 아님"을 표기해야.
2. **모순: smoke 실행시간 3~7분[Harness, MED] vs 15~30분[CloudBees 등 folklore 블로그, LOW]** — 숫자가 소스마다 다르고 1차 근거 없음. 대략치로만.
3. **모순(같은 논문 상이 요약): arXiv 2509.10279를 각도 1은 "15% 테스트·실패 95%+·5.9×/5.6×·프로덕션 0.8%/~30×"로, 각도 3은 "~2.8× 가속·약 50% 감소"로 인용.** → 절대 수치를 스킬 문구에 못 박지 말 것.
4. **모순(oracle 비관 vs 낙관): 구현포착 위험[arXiv 2410.21136, HIGH] vs "편향통제 데이터셋에서 mutation score를 human 수준으로 올림"[ASE 2025, HIGH].** 병치 해석 = "약하지만 유용" — mutation score는 오르나 spec 위반 탐지는 별개. 논쟁적.
5. **모순: "피라미드는 죽었다"[WireMock, LOW-MED] vs "2025에도 유효"[QAlified, MED].** 미해결. Fowler·web.dev·Dodds는 "% 논쟁은 distraction"으로 수렴.

**미해결·근거 못 찾음**:
- **integration-heavy가 unit 대비 ROI 우위임을 통제 실험으로 입증한 논문 없음** — Trophy/Honeycomb은 전문가 휴리스틱.
- **sanity의 CI 고정 스테이지 표준 없음** — 성격 규정만 존재.
- **nightly-deferral 단독 효과를 정량화한 2025+ 엄밀 연구 없음** — 관행은 EMSE/샤딩 문헌이 전제하나 단독 측정 미발견.

**낮은 신뢰(LOW)·folklore — 인용 시 반드시 표기**:
- 지어낸 정량 수치: "smoke 50% 단축/버그 80% 조기 포착/regression 90%를 5%에"[Quash], "89% 고성과팀 병렬화"·ML 선택 "평균 84%↓/90% 포착"[Ranger] — 방법론·표본 불명, **Meta 1차 수치와 혼동 금지**.
- smoke 어원(하드웨어 연기) — 1차 출처 불명 folklore.
- "동어반복(tautological) 어서션이 LLM 테스트의 약점"은 1차 출처 못 찾음 — 검증된 형태는 "구현포착"(2410.21136).
- 70/20/10 피라미드 비율 — Fowler 본인이 상대화한 예시(folklore).
- Google 1.5%/16% flaky — 2016년 수치, 오래됨.

**중대한 정직성 노트**: 조사 과정에서 자동요약이 arXiv 2410.21136에 존재하지 않는 %를 지어내(hallucinated) 검증 후 폐기했다. 이 논문 관련 수치를 인용하는 산출물은 원 초록에 %가 없음을 기억할 것.
