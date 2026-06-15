# Skills

### Plugin: `frontend-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Planner | `/planner` | 인터뷰 → 조사 → 계획 생성 → 승인 4단계 PRD 작성 |
| Architecture | `/architecture` | 시스템 구조, API, 데이터 흐름 설계 |
| Critic | `/critic` | 설계의 약점, 리스크, 누락 사항 분석 |
| Grill Me | `/grill-me` | 요구사항 명확화를 위한 집요한 질문 |
| TDD | `/tdd` | Red-Green-Refactor 루프 기반 개발 |
| A11y | `/a11y` | WAI-ARIA 기반 웹접근성 점검/개선 |
| Semantic HTML | `/semantic-html` | 시맨틱 태그 사용 점검/개선 |
| SEO/GEO | `/seo-geo-optimizer` | 검색엔진 + AI 검색 최적화 |
| E2E Verifier | `/e2e-verifier` | Chrome MCP / Playwright MCP / Agent-Browser 기반 브라우저 검증 |
| Lighthouse Performance | `/lighthouse-performance` | Lighthouse CLI 기반 Core Web Vitals(LCP, CLS, INP, TTFB, FCP) 측정 및 개선 방안 |
| QA Inspector | `/qa-inspector` | API 응답↔훅 타입, 라우팅, 상태 전이, 데이터 흐름 교차 비교로 경계면 불일치 탐지 |
| Security Audit | `/security-audit` | OWASP Top 10 코드 분석, npm audit 의존성 스캔, 보안 헤더·시크릿 탐지 |

### Plugin: `harness-generator`

| Skill | Command | Description |
|-------|---------|-------------|
| Harness Generator | `/harness-generator` | 도메인 무관 하네스(에이전트팀 + 스킬 + 오케스트레이터) **수동·인터랙티브** 생성 — 7단계 메타 프로세스 (감사 → 도메인 분석 → 아키텍처 → 에이전트 정의 → 스킬 작성 → 오케스트레이션 → 검증/진화) |

### Plugin: `git-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Commit | `/commit` | 한국어 커밋 메시지 작성 (`이슈번호 type: 제목` 형식, 명령형 제목, 필요 시 요약/영향/테스트 시나리오 본문 포함) |
| Review to PR | `/review-to-pr` | 리뷰 → 커밋 → PR 생성 올인원 워크플로우. Commit/PR 각 단계에서 `/simplify` + `/review`를 자동 수행하고 수정 적용 후 커밋 또는 PR 생성 |

### Plugin: `meta-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Meta-Harness | `/meta-harness` | 하네스(루트 CLAUDE.md + SKILL.md + agents + commands + hooks = "LLM 주위의 코드")의 결함을 full-trace experience store로 진단·개선하는 진입 오케스트레이터. R1 현세션 redirect/보강 · R2 plugin 개선 · R3 외부 .md 역추적 트리거. Phase 0~8 + R4 보고, **사용자 승인 게이트(자동 적용 금지)** |
| Session Signal Capture | `/session-signal-capture` | R1 현세션 발화·직전 산출물·active skill + R3 외부 .md를 **요약 없이 원형 trace로** 캡처. R3는 산출물 출처를 3단 폴백(경로 규약 → 메타마커 → 구조·문체+git blame)으로 역추적 + confidence |
| Causal Diagnosis | `/causal-diagnosis` | experience-store raw trace를 grep/cat로 직접 조회해 confound 격리 → 단독검증 → why-first로 root cause 진단(근거는 trace step/경로 인용) |
| Pareto Refinement | `/pareto-refinement` | additive-first → compose(직교 승리만) → transfer로 4축(behavior-alignment·rule-body-cost·trigger-precision·generalization) Pareto **비후퇴** 패치 생성 (patch만, 자동 적용 금지) |

> `meta-harness`는 "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1)를 토대로, **압축 요약이 아닌 full-trace experience store**(repo-wide 기본 `.claude/experience-store/`, plugin opt-in `.claude/plugin-store/{target}/`)를 proposer가 직접 `grep`/`cat`으로 조회하는 것을 핵심으로 한다(논문 Table 3: full-trace가 요약 기반보다 우월). 4명의 에이전트(`trace-capturer`, `failure-diagnostician`, `pareto-refiner`, `experience-historian`)를 서브에이전트로 spawn한다(모두 `model: "opus"`). 모든 패치는 **사용자 승인 게이트** 후에만 적용한다.

### Plugin: `product-spec-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Product Spec | `/product-spec` | 기획자(PM)용 **기획문서(PRD) + 사용자 스토리** 작성·검증 진입 오케스트레이터. 개발 착수 *전* 단계, 도메인 무관 인터랙티브. Phase 0~3 (요구/문제 정의(Discovery) → PRD 작성 → 사용자 스토리 도출 → 적대적 검증). 매 Phase 산출물 미리보기 + **사용자 승인 게이트** 후 진행, 1줄 보고 `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?` |

4 Phase 구성:

- **Phase 0 요구/문제 정의(Discovery)** — `requirements-analyst`. 한 번에 1질문(grill-me)으로 **문제 정의 카드**(고정필드: problem / target_users / goals(비즈니스·사용자) / constraints / success_metrics(관찰형)) 작성. 승인 게이트.
- **Phase 1 기획문서(PRD) 작성** — `prd-writer`. 구조: 배경·문제 / 목표·성공지표(관찰형) / 범위(In·Out 명시) / 핵심 요구사항(기능·비기능) / 가정·리스크 / 마일스톤. 쓰기 전 미리보기 승인. ([references/prd-template.md])
- **Phase 2 사용자 스토리 도출** — `story-writer`. PRD 요구사항→스토리("…로서 …하고 싶다, 왜냐하면 …") + 수용기준(Given/When/Then) + INVEST 자가점검. ([references/user-story-guide.md])
- **Phase 3 검증** — `spec-reviewer`. **적대적 검증**(칭찬형 금지): 요구↔스토리 추적 매트릭스(완전성) · INVEST 통과 · 수용기준 관찰성 · 목표↔요구↔스토리 일관성 · 모호/판정불가 문장 색출. 검증 리포트 + 승인(보완 시 additive-first).

> `product-spec-harness`는 **개발 전 제품 기획 산출물(PRD·사용자 스토리)** 에 특화한 도메인 무관 인터랙티브 하네스다. 4명의 에이전트(`requirements-analyst`, `prd-writer`, `story-writer`, `spec-reviewer`)를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 순차). 내재화 원칙 — 승인 게이트(미리보기 후 쓰기) · 관찰형 수용기준(Given/When/Then) · 요구↔스토리 완전성 추적 · 적대적 검증 · additive-first · 한 번에 한 질문. **경계** — 프론트엔드 개발용 PRD·구현 요구사항·코드 작성(frontend-harness의 prd/planner 영역)이나 코드/하네스/커밋 작업은 범위가 아니다(트리거 충돌 방지를 위해 description·trigger-eval에 명시).

### Plugin: `loop-engineering`

| Skill | Command | Description |
|-------|---------|-------------|
| Loop Engineering | `/loop-engineering` | 검증 가능한 목표를 향해 한 작업을 **자율 반복(loop)으로 완성**하는 진입 오케스트레이터. 실행 루프(① 목표 → ② 실행 → ③ 검증 → ④ 실패시 수정 → ⑤ 통과시 종료)와 지속학습 루프(실패 → 조사 → 검증 → 정립 → 참조)를 결합한다. Phase 0 목표 설계(Goal Card 승인 게이트, auto/gated 확정) → Phase 1 자율 반복(Execute→Verify→(FAIL)Diagnose→Distill). 중단조건(통과·최대 반복·무진전·예산)으로 무한 루프를 막는다 |

5개 에이전트 구성 (모두 `model: "opus"`):

- **Goal** — `goal-setter`. 모호한 요청을 **검증 가능한 목표(Goal Card)** 로 변환 — 관찰형 성공기준 + *실행 가능한* 검증 방법 + 중단조건(최대 반복·무진전·예산) + 범위(In/Out). "루프는 검증기만큼만 좋다"가 제1원칙.
- **Execute** — `loop-executor`. 목표를 향한 **1회 반복**. 2회차+엔 메모리의 관련 교훈을 consult하고 직전 개선안을 적용해 검증기를 통과시킬 **최소 변경 1개**(confound 격리)를 시도.
- **Verify** — `loop-verifier`. 검증 방법을 **실제로 실행**해 기준별 **엄격 PASS/FAIL + 증거**. 적대적(먼저 실패할 이유를 찾음), 증거 없는 PASS 금지.
- **Investigate** — `failure-analyst`. FAIL 시 **재시도 전에 root cause**를 진단(증상 ≠ 원인) → trace 증거로 **사실로 전환** → **다음 반복의 접근을 직접 작성**(사람이 아니라 에이전트가 개선 프롬프트를 씀). 같은 원인 M회면 무진전 → 구조 변경 권고.
- **Distill/Consult** — `memory-curator`. *검증된* 교훈만 **distill**해 `lessons.md`에 쌓고, 다음 반복에 관련 규칙만 **surface(consult)**. raw 반복 trace(`iterations.jsonl`)는 보존(요약 금지).

> `loop-engineering`은 **주어진 작업을 검증 루프로 완성**하는 데 특화한 도메인 무관 멀티 에이전트 하네스다. 5명의 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`). 루프 메모리는 `.claude/loop-memory/{goal-slug}/`(goal.md / iterations.jsonl / lessons.md)에 누적되어 회차·세션을 넘어 학습한다(continual learning). **경계** — 하네스 자체 진단·개선(meta-harness)·새 하네스 생성(harness-generator)·기획문서(product-spec/frontend)·커밋/PR 리뷰(git-harness)·native `/loop`(시간 간격 폴링)은 범위가 아니다. native `/goal` 위에 검증기 설계·재시도 전 진단·지속학습 메모리·무진전 감지를 구조화해 얹은 버전으로 위치한다.

### Plugin: `review-harness`

| 스킬·커맨드 | Command | Description |
|-------------|---------|-------------|
| Handoff Review (커맨드) | `/handoff-review` | 오케스트레이터(진입점). 넘어온 상류 산출물에 해당하는 게이트(dor/design/contract/test-coverage)를 사용자에게 선택받아 **병렬 실행**하고, 게이트별 판정을 **착수 준비도(Readiness) 통합 리포트** + 각 팀(기획/디자인/BE/QA)에 되돌릴 질문으로 묶는다. 하나라도 Blocker면 착수 보류로 시작 |
| DoR Review | `/dor-review` | 기획 산출물(PRD/유저스토리/인수조건/티켓) 착수 준비도 — DoR 게이트 · INVEST 스코어카드(Testable·Independent=0이면 차단) · GWT 완결성(음성/엣지/에러/빈/권한 경로) · 모호성 린트 · 의존성/계약 참조 |
| Design Handoff Review | `/design-handoff-review` | 디자인 핸드오프(Figma MCP·스펙) 사각지대 — 검증에러/에러페이지/로딩/빈/요소 상태 누락 · 토큰·변수 바인딩 · 컴포넌트↔코드(Code Connect) 매핑 · 상태별 oracle |
| Contract Review | `/contract-review` | API 계약(OpenAPI/스키마) FE 착수 전 — 엔드포인트 완결성(spectral) · 배포 계약 대비 breaking-change diff(oasdiff)·SemVer 권고 · 소비자(CDC/Pact) 커버리지 · 코드↔spec drift |
| Test Coverage Review | `/test-coverage-review` | QA 상류(인수조건↔테스트) 커버리지 — 인수조건 테스트가능성(Gherkin 변환) · AC↔테스트 매핑(스펙없는 테스트/검증없는 스펙) · 커버리지 채점(LLM-as-judge) · 누락 음성/엣지 시나리오 발굴 |

> `review-harness`는 코드 착수 *전* **상류 산출물(기획·디자인·API 계약·QA 인수조건)** 을 핸드오프 시점에 '착수 게이트'로 검수하는 데 특화한 도메인 무관 하네스다. 4개 게이트 스킬은 모두 `disable-model-invocation: true`(명시 호출 또는 `handoff-review`가 spawn)·`allowed-tools`에 Edit/Write 없음(읽기 위주, 산출물 직접 수정 금지)이다. `handoff-review` 오케스트레이터는 선택된 게이트를 한 메시지에서 병렬 spawn한다(`frontend-harness`의 `/review` 패턴과 동일). **내재화 원칙** — Shift-Left(상류 게이트) · Honesty Guardrail(검증된 2025+ 근거만 등급과 함께 인용, '개선 N%' 약속 금지, baseline-before-target, 반증된 신화 수치 인용 금지) · LLM 자동탐지는 사람 검토를 보조(이상적 템플릿 과대탐지 경향 인지). **경계** — 완성된 코드 리뷰(`frontend-harness` `/review`·qa-inspector·security-audit) · PRD·스토리 *작성*(`product-spec-harness`) · 커밋/PR 리뷰(`git-harness`) · 하네스 자체 진단(`meta-harness`)은 범위가 아니며, 트리거 충돌 방지를 위해 description·`evals/trigger-eval.json`에 명시한다.
