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
| Figma-Extract | `/figma-extract` | Figma 링크→디자인 컨텍스트 추출/파일화 (metadata 노드맵 우선→대상 노드만 get_design_context/variable_defs/screenshot 상세 추출→`.claude/design/`에 json·spec·png 산출, 부모엔 경로+요약만 반환해 토큰 폭주 차단; 코드 생성 안 함, 단독 동작) |

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

> `meta-harness`는 "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1)를 토대로, **압축 요약이 아닌 full-trace experience store**(repo-wide 기본 `.claude/experience-store/`, plugin opt-in `.claude/plugin-store/{target}/`)를 proposer가 직접 `grep`/`cat`으로 조회하는 것을 핵심으로 한다(논문 Table 3: full-trace가 요약 기반보다 우월). 4명의 에이전트(`trace-capturer`, `failure-diagnostician`, `pareto-refiner`, `experience-historian`)를 서브에이전트로 spawn한다(모두 `model: "opus"`). 모든 패치는 **사용자 승인 게이트** 후에만 적용한다. 추가로 **self-heal 캡처 훅(`UserPromptSubmit`)** 이 사용자의 '수정/보강/방향전환' 발화를 세션 중 `signals/*.jsonl`에 원형 적재하고(캡처 전용·비차단·요약 금지), 추후 회차의 healer가 Phase 1 warm-start로 누적 신호를 끌어와 진단·패치에 쓴다(적용은 승인 게이트 후). **(2026-06 v0.3.0)** 데이터 적재(신호 캡처)와 지침 보강(patch 설계)이 자족 reference `references/data-capture-criteria.md`(C1~C9 적재 기준 + CLAUDE.md/Skill/hook/rule 메커니즘 선택, 1차 출처 인라인)를 operative하게 따르도록 additive 배선했다 — 묶음 캡처·요약 금지·그 순간 기록·프로젝트 최상단 모음·strong/weak 신호 등급·고칠 곳(전역 메모리 포함)+이름 통일·검증 후 재사용, 반복 무시 규칙→hook 전환(③ 장치화). 훅은 흔한 한국어 교정어 포착 확장·신호 등급·git-root 모음·status를 더했고(캡처 전용·exit 0 불변), 승인 게이트·Pareto 비후퇴·full-trace 보존은 그대로다. 1차 출처(Anthropic context-engineering·best-practices·hooks·steering blog)는 deep-research가 3-0 확인을 보고(과정 보고; arXiv 2606.13174/2505.16067/2603.07670은 기준 문서 근거 인용, 재검증 안 함). **(2026-06-28 v0.4.0)** 결정론 근거를 hook/permission으로 **1급 라우팅**하도록 additive 배선 — 진단이 enforcement 성격을 먼저 분류(`enforcement_class`: deterministic-enforce/record/judgment)해 매번 반드시 일어나야/막혀야 하는 근거는 advisory 본문(CLAUDE.md/Skill)이 아니라 hook/permission으로 **첫 발생부터** 보내고, hook이면 신규 자족 reference `references/hook-lifecycle.md`(공식 hooks 라이프사이클 distill: 전체 event·상황→event 선택·record(exit0)/enforce(exit2·deny)·config·matcher)로 상황에 맞는 event를 고른다. 배치는 경계 유지(플러그인 hook=plugin 모드 in-boundary·repo-wide면 hook_spec 동봉 scope-escalation; `.claude/settings.json`은 직접 수정 않고 `update-config` 핸드오프). 자체 라이프사이클 훅으로 SessionStart `warm-start-nudge`(미소비 strong 신호 표면화, 주입 전용·근사치·env 비활성) 추가. **정직성 정정**: `.claude/rules`는 결정론이 아니라 advisory(결정론 강제는 hook·permission뿐). 안전 불변(승인 게이트·Pareto 비후퇴·full-trace·exit 0·settings.json 직접수정 금지) 그대로. 1차 출처(code.claude.com hooks·hooks-guide·memory·skills·settings + steering blog)는 등급(VERBATIM/요약/추론)과 함께 플러그인 내 `references/hooks-grounding.md`(provenance)에 보존, 지침 .md는 URL 인라인.

### Plugin: `product-spec-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Product Spec | `/product-spec` | 기획자(PM)용 **기획문서(PRD) + 사용자 스토리** 작성·검증 + **기획 완성도 점검(DoR)(생성 전 선행)** 진입 오케스트레이터. 개발 착수 *전* 단계, 도메인 무관 인터랙티브. Phase 0~4 (요구/문제 정의(Discovery) → 기획 완성도 점검(DoR) → PRD 작성 → 사용자 스토리 도출 → 적대적 검증). **기획안을 인자로 주면** 카드 추출 후 생성 전 완성도 점검(DoR) → 보강점 반영해 PRD·스토리 생성. 매 Phase 산출물 미리보기 + **사용자 승인 게이트** 후 진행, 1줄 보고 `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?` |

5 Phase 구성 (입력 모드 A 기획안 / B 인터뷰):

- **Phase 0 요구/문제 정의(Discovery)** — `requirements-analyst`. 기획안이 있으면(모드 A) 전문에서 **문제 정의 카드**(고정필드: problem / target_users / goals(비즈니스·사용자) / constraints / success_metrics(관찰형))를 **추출**하고 모호 필드만 한 번에 1질문 보강. 없으면(모드 B) grill-me 인터뷰. 승인 게이트.
- **Phase 1 기획 완성도 점검(DoR)(모드 A 진입질문 필수·생성 전 선행)** — `dor-evaluator`. PRD·스토리 생성 *전*, 모드 A에선 **진입 질문을 반드시 제시**하고(생략·자동 스킵 금지) 사용자 동의(예/모호한 긍정) 시 **원본 기획안**을 기획 완성도 점검(DoR)으로 평가 — 기획 완성도 게이트(DoR 게이트) · 좋은 스토리 6가지 기준 점수표(INVEST 스코어카드; Testable·Independent=0이면 차단) · 조건·행동·결과(Given-When-Then) 완결성(정상/경계/에러/빈/권한) · 모호성 점검 · 의존성/계약 참조. `# 기획 완성도 점검 결과(DoR Review)` + **보완할 점 점검표(보강 체크리스트)**(충족=`[O]` / 미충족=`[ ]`+보강 예시)를 **채팅으로 제시**하고 그 보강점을 이후 PRD·스토리에 반영. 방법론은 `references/dor-review-rubric.md`에 **내재화**(외부 플러그인 참조·의존 없음 — 단독 설치로 독립 동작). 파일 저장은 마무리에서 사용자가 선택할 때만(`.claude/_docs/<슬러그>/product-spec-review.md`). ([references/dor-review-rubric.md])
- **Phase 2 기획문서(PRD) 작성** — `prd-writer`. 구조: 배경·문제 / 목표·성공지표(관찰형) / 범위(In·Out 명시) / 핵심 요구사항(기능·비기능) / 가정·리스크 / 마일스톤. Phase 1 보강점 반영. 쓰기 전 미리보기 승인. ([references/prd-template.md])
- **Phase 3 사용자 스토리 도출** — `story-writer`. PRD 요구사항→스토리("…로서 …하고 싶다, 왜냐하면 …") + 수용기준(조건·행동·결과(Given/When/Then)) + 좋은 스토리 6가지 기준(INVEST) 자가점검. Phase 1 보강점(예외 흐름 등) 반영. ([references/user-story-guide.md])
- **Phase 4 적대적 검증** — `spec-reviewer`. **칭찬형 금지**: 요구↔스토리 추적 매트릭스(완전성) · 좋은 스토리 6가지 기준(INVEST) 통과 · 수용기준 관찰성 · 목표↔요구↔스토리 일관성 · 모호/판정불가 문장 색출. **리포트는 채팅 제시 + 동의 시 `.claude/_docs/<슬러그>/adversarial-review.md` 저장**, 결함은 additive-first로 PRD·스토리에 반영.
- **마무리(opt-in 저장)** — 산출물은 `.claude/_docs/<기획서 슬러그>/`(기획서별 폴더)에 모은다. Phase 1 기획 완성도 점검(DoR) 결과는 **PRD·스토리 생성 후 사용자가 저장을 선택할 때만** `product-spec-review.md`로 저장(즉시 저장 안 함). 적대적 검증 리포트도 동의 시 `adversarial-review.md`로 저장.

> `product-spec-harness`는 **개발 전 제품 기획 산출물(PRD·사용자 스토리) 작성 + 생성 전 기획안의 기획 완성도 점검(DoR)**에 특화한 도메인 무관 인터랙티브 하네스다. 5명의 에이전트(`requirements-analyst`, `dor-evaluator`, `prd-writer`, `story-writer`, `spec-reviewer`)를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 순차). 내재화 원칙 — 승인 게이트(미리보기 후 쓰기) · 관찰형 수용기준(조건·행동·결과(Given/When/Then)) · 요구↔스토리 완전성 추적 · 적대적 검증(채팅 제시 + 동의 시 `adversarial-review.md` 저장) · 기획 완성도 점검(DoR) 내재화(생성 전 선행, 저장 opt-in, Honesty Guardrail·2025+ 근거) · additive-first · 한 번에 한 질문. 산출물은 `.claude/_docs/<기획서 슬러그>/`에 모은다. **독립성** — 단독 설치로 동작하며 다른 마켓플레이스 플러그인을 참조·의존하지 않는다(기획 완성도 점검(DoR) 평가 방법론 내재화). **경계** — 프론트엔드 화면 구현·기술 설계용 PRD·구현 요구사항·코드 작성, 코드/하네스/커밋 작업, *이미 완성된* 상류 산출물을 핸드오프 게이트로 검수만 하는 작업은 범위가 아니다(트리거 충돌 방지를 위해 description·trigger-eval에 명시).

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

> `loop-engineering`은 **주어진 작업을 검증 루프로 완성**하는 데 특화한 도메인 무관 멀티 에이전트 하네스다. 5명의 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`). 루프 메모리는 `.claude/loop-memory/{goal-slug}/`(goal.md / iterations.jsonl / lessons.md)에 누적되어 회차·세션을 넘어 학습한다(continual learning). **경계** — 하네스 자체 진단·개선(meta-harness)·새 하네스 생성(harness-generator)·기획문서(product-spec/frontend)·커밋/PR 리뷰(git-harness)·native `/loop`(시간 간격 폴링)은 범위가 아니다. native `/goal` 위에 검증기 설계·재시도 전 진단·지속학습 메모리·무진전 감지를 구조화해 얹은 버전으로 위치한다. **(2026-06 심화)** Osmani "Loop Engineering" 원전을 additive 반영 — 여섯 빌딩블록(factory model: automations·worktrees·skills·plugins/connectors·sub-agents·external memory) 중 skills(하네스 자체)·sub-agents·external memory를 *기본 구현*으로(sub-agents는 실제 검증을 실행하는 강한 verifier로), 나머지를 코어 흐름 불변의 *opt-in 레인*으로 framing하고, 기계 검증이 막지 못하는 사람-쪽 결함(comprehension rot·cognitive surrender·orchestration tax)에 stay-the-engineer 가드(merge 전 diff 이해 게이트 green CI≠구현·병렬 review-bandwidth 상한·loop-verifier reward-hacking 경계)를 더했다(현재 기능 전부 보존, principles §8 / research dossier §9).

### Plugin: `review-harness`

| 스킬·커맨드 | Command | Description |
|-------------|---------|-------------|
| Handoff Review (커맨드) | `/handoff-review` | 오케스트레이터(진입점). 넘어온 상류 산출물에 해당하는 게이트(dor/design/contract/test-coverage)를 사용자에게 선택받아 **병렬 실행**하고, 게이트별 판정을 **착수 준비도(Readiness) 통합 리포트** + 각 팀(기획/디자인/BE/QA)에 되돌릴 질문으로 묶는다. 하나라도 Blocker면 착수 보류로 시작 |
| DoR Review | `/dor-review` | 기획 산출물(PRD/유저스토리/인수조건/티켓) 착수 준비도 — DoR 게이트 · INVEST 스코어카드(Testable·Independent=0이면 차단) · GWT 완결성(음성/엣지/에러/빈/권한 경로) · 모호성 린트 · 의존성/계약 참조 |
| Design Handoff Review | `/design-handoff-review` | 디자인 핸드오프(Figma MCP·스펙) 사각지대 — 검증에러/에러페이지/로딩/빈/요소 상태 누락 · 토큰·변수 바인딩 · 컴포넌트↔코드(Code Connect) 매핑 · 상태별 oracle |
| Contract Review | `/contract-review` | API 계약(OpenAPI/스키마) FE 착수 전 — 엔드포인트 완결성(spectral) · 배포 계약 대비 breaking-change diff(oasdiff)·SemVer 권고 · 소비자(CDC/Pact) 커버리지 · 코드↔spec drift |
| Test Coverage Review | `/test-coverage-review` | QA 상류(인수조건↔테스트) 커버리지 — 인수조건 테스트가능성(Gherkin 변환) · AC↔테스트 매핑(스펙없는 테스트/검증없는 스펙) · 커버리지 채점(LLM-as-judge) · 누락 음성/엣지 시나리오 발굴 |

> `review-harness`는 코드 착수 *전* **상류 산출물(기획·디자인·API 계약·QA 인수조건)** 을 핸드오프 시점에 '착수 게이트'로 검수하는 데 특화한 도메인 무관 하네스다. 4개 게이트 스킬은 모두 `disable-model-invocation: true`(명시 호출 또는 `handoff-review`가 spawn)·`allowed-tools`에 Edit/Write 없음(읽기 위주, 산출물 직접 수정 금지)이다. `handoff-review` 오케스트레이터는 선택된 게이트를 한 메시지에서 병렬 spawn한다(`frontend-harness`의 `/review` 패턴과 동일). **내재화 원칙** — Shift-Left(상류 게이트) · Honesty Guardrail(검증된 2025+ 근거만 등급과 함께 인용, '개선 N%' 약속 금지, baseline-before-target, 반증된 신화 수치 인용 금지) · LLM 자동탐지는 사람 검토를 보조(이상적 템플릿 과대탐지 경향 인지). **경계** — 완성된 코드 리뷰(`frontend-harness` `/review`·qa-inspector·security-audit) · PRD·스토리 *작성*(`product-spec-harness`) · 커밋/PR 리뷰(`git-harness`) · 하네스 자체 진단(`meta-harness`)은 범위가 아니며, 트리거 충돌 방지를 위해 description·`evals/trigger-eval.json`에 명시한다.

### Plugin: `ops-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Ops Harness | `/ops-harness` | 프로덕션 운영·인시던트 대응 진입 오케스트레이터. traces+logs+metrics 텔레메트리 기반 인시던트 전 생애주기를 AIOpsLab 4단계(L1 Detection → L2 Localization → L3 RCA → L4 Mitigation+위험평가)로 분해. 인프라는 중재 읽기 액션(get_logs/get_metrics/get_traces/exec_shell)으로만 관측·완화는 사람 집행, 매 Phase 승인 게이트·1줄 보고. 단순 케이스는 Straight-Shot 폴백 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **L1 Detection** — `incident-detector`. 텔레메트리에서 이상을 탐지·트리아지(RED/USE)하고 증상·영향·심각도·시작시각을 확정(범인 지목은 다음 단계).
- **L2 Localization** — `incident-localizer`. traces 우선으로 범인 후보를 국소화하고 metrics/logs 증거로 순위화.
- **L3 RCA** — `root-cause-analyst`. 증상→원인 인과사슬을 확정. **RCA 가드레일**(anchoring·정체·임의 증거선택·신념 미갱신 경계, 경쟁 가설·반증 우선) + 단순/작은 모델엔 **Straight-Shot 폴백**.
- **L4 Mitigation** — `mitigation-planner`. 완화안 + 위험/롤백/blast radius 평가 + **DQ=0.40·타당성+0.30·구체성+0.30·정확성** 자가 채점. 사람 집행 대기(직접 변경 금지).

> `ops-harness`는 **배포 이후 런타임** 인시던트(탐지·국소화·RCA·완화)에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; L1→L4 순차). **내재화 원칙** — 단계 분해(직전 증거만 입력) · 진단(L1–L3)↔조치/위험(L4) 역할 분리 · 중재 읽기·휴먼-인-더-루프 · DQ 품질 게이트 · RCA anti-anchoring 가드 · Honesty Guardrail(역할분리 100%/1.7%·RCA 15%p/45%는 한계 동반 인용, 일반화·인과 단정 금지). **경계** — 하네스 자체 진단(`meta-harness`)·검증 루프 완성(`loop-engineering`)·완성 코드 리뷰(`frontend-harness`/`git-harness`)·상류 핸드오프 게이트(`review-harness`)·PRD 작성(`product-spec-harness`)은 범위가 아니다. 근거: AIOpsLab(arXiv:2501.06706)[GOLD/SILVER] · 역할분리 오케스트레이션(arXiv:2511.15755)[SILVER] · RCA 추론 실패모드(arXiv:2601.22208)[SILVER].

### Plugin: `backend-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Backend Harness | `/backend-harness` | 백엔드/API **실행 기반 검증** 구현 진입 오케스트레이터. 범위/계약 → 설계 → 환경(1급) → 구현 → 실행 검증 5단계. 통과는 자기보고가 아니라 빌드·테스트의 실제 통과로만 인정(reward-hacking 가드), 매 Phase 승인 게이트 |
| Test Generator | `/test-generator` | 기존 코드 실행기반 테스트를 generate→compile→execute→repair 공진화 루프로 생성·수리 (5 경험적 수리 템플릿·커버리지 게이트·judge 캘리브레이션). FE TDD(test-first)와 구분(test-after) |

4개 에이전트 구성 (모두 `model: "opus"`):

- **설계** — `be-architect`. 서비스 경계·API 계약·데이터 모델/마이그레이션 + 검증 후크·환경 요구사항.
- **환경(1급)** — `env-provisioner`. 빌드·실행·테스트 가능 상태를 **독립 Phase**로 확보(환경 구성이 저장소 단위 작업 최대 병목 — arXiv:2512.06915).
- **구현** — `be-implementer`. API·서비스 로직·DB 스키마/마이그레이션을 계약 준수로 구현(자기보고≠통과).
- **검증(핵심)** — `be-verifier`. 빌드·마이그레이션·테스트를 직접 재실행해 PASS/FAIL, 고커버리지 요구, reward-hacking(테스트 무력화/우회) 적대적 점검.

> `backend-harness`는 **백엔드/API 구현을 실행 기반 검증으로 완성**하는 데 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 순차). **내재화 원칙** — 실행 기반 검증(증거 없는 PASS 금지) · 환경 우선(1급 시민) · generator/checker 분리 · reward-hacking 가드 · 계약 준수 · 승인 게이트 · Honesty Guardrail(TestART 수치는 2024 데이터·효과크기 단정 금지). **경계** — API 계약 *검수*(`review-harness/contract-review`)·FE 화면 구현(`frontend-harness`)·PRD 작성(`product-spec-harness`)·커밋/PR(`git-harness`)·하네스 진단(`meta-harness`)·단발 자율 반복(`loop-engineering`)은 범위가 아니며, `test-generator`는 FE Red-Green-Refactor(`frontend-harness/tdd`)와 구분된다. 근거: 저장소 단위 작업 난도·환경 병목·자기보고 불일치(arXiv:2510.04852·2505.09569·2505.07473·2512.06915)[GOLD] · TestART(arXiv:2408.03095, ACM TOSEM 2025)[SILVER].

### Plugin: `cicd-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| CICD Harness | `/cicd-harness` | 코드 커밋→프로덕션 전달 파이프라인 진입 오케스트레이터. CI 파이프라인(build/test 게이트) → IaC(terraform plan + OPA 결정론적 검증) → 릴리스·배포 결정(canary·rollback·feature-flag·flaky, trust-tier 단계적 자율) → 전달 안정성 가드(DORA 통제) 4단계. defense-in-depth(읽기전용·사람 사전승인), 매 Phase 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Phase 1 CI 파이프라인** — `pipeline-architect`. build/test 게이트·릴리스 전략 설계/검수. YAML 변경은 *제안* diff만(직접 적용·커밋·푸시 금지).
- **Phase 2 IaC·환경** — `iac-reviewer`. IaC 변경을 **terraform plan(실행 검증) + OPA(policy-as-code)** 결정론적 게이트로 통과/차단. LLM 판단을 게이트로 두지 않음. apply는 사람 집행.
- **Phase 3 릴리스·배포 결정** — `release-gatekeeper`. flaky·rollback·feature-flag·canary 승격을 **trust-tier 단계적 자율**(낮은 위험=제안+자동, 높은 위험=사람 필수)로 결정. 배포 자동 실행 안 함.
- **Phase 4 전달 안정성 가드** — `delivery-verifier`. **DORA 통제**(강한 테스트 자동화·작은 배치) 점검 + defense-in-depth 사람 사전 승인 목록 정리.

> `cicd-harness`는 **코드 커밋→프로덕션의 전달 파이프라인(CI/CD·릴리스·IaC·배포 게이트)**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 순차, 없는 단계는 Phase 0에서 건너뜀). **내재화 원칙** — defense-in-depth(읽기전용·쓰기/apply/deploy는 사람 사전 승인 후 제안→집행) · policy-as-code 결정론적 게이트(terraform plan + OPA) · trust-tier 단계적 자율 · DORA 통제 프레이밍 · 역할 분리 · Honesty Guardrail. **DORA 정직성(필수)** — AI-불안정 통제책으로 사실 인용 가능한 것은 **small batches + robust test automation 두 가지뿐**이며, '버전관리·느슨한 결합도 통제요소'·'긴밀결합 팀 무이득'은 반증된 신화로만 표기한다. **경계** — 배포 *이후* 런타임 인시던트(`ops-harness`)·BE 코드 *구현*(`backend-harness`)·빌드 그린까지 자율 반복(`loop-engineering`)·커밋/PR(`git-harness`)·계약 검수(`review-harness/contract-review`)·PRD(`product-spec-harness`)·FE(`frontend-harness`)·하네스 진단(`meta-harness`)은 범위가 아니다. 근거: DORA 2025·DORA AI Capabilities Model[GOLD] · AI-Augmented CI/CD(arXiv:2508.11867)·GitHub Agentic Workflows·MACOG(arXiv:2510.03902)[SILVER].

### Plugin: `context-engineering`

| Skill | Command | Description |
|-------|---------|-------------|
| Context Engineering | `/context-engineering` | LLM·에이전트에 넣을 **컨텍스트 페이로드를 체계적으로 조립·최적화**하는 진입 오케스트레이터. Scope(도달 정보·토큰 예산·retrieval need) → Retrieve/Generate(후보 수집·생성) → Process(압축·정렬·중복제거, brevity bias·lost-in-the-middle 대응) → Manage(playbook 큐레이션·context-collapse 가드·격리·검증·조립) 4단계. Phase 0 Context Brief 승인 게이트, 멀티 에이전트 컨텍스트면 per-agent 격리(REGISTRY/FOCUS) 설계 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Scope** — `context-scoper`. 작업이 모델에 *반드시 도달해야 할 정보*와 *토큰 예산*을 정의. retrieval need를 must/nice/out으로 분류하고 각 need에 '왜 필요한가'를 붙임(컨텍스트는 많을수록 좋은 게 아니다).
- **Retrieve/Generate** — `context-retriever`. retrieval need(특히 must-have)를 충족하는 후보 컨텍스트를 RAG식으로 수집·생성. 출처·relevance·토큰·충돌을 표기하고 must-have 미충족은 생성으로 메우지 않고 보고.
- **Process** — `context-processor`. 예산 안으로 압축·정렬·중복제거. 전면 재작성 금지(디테일 보존 구조적 증분), 가장 중요한 컨텍스트를 앞·뒤 배치(lost-in-the-middle 대응), 충돌은 둘 다 보존·표시.
- **Manage** — `context-curator`. 진화하는 playbook으로 큐레이션(generation/reflection/curation), context-collapse 가드, (멀티 에이전트면) REGISTRY(≤200토큰 상태요약)/FOCUS(a_i) 격리, 최종 페이로드 검증(예산·must-have·출처·위치) 후 출하.

> `context-engineering`은 **모델에 들어갈 정보 페이로드의 조립·최적화**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Scope→Retrieve→Process→Manage 순차). 산출물은 `.claude/context-engineering/{slug}/`(context-brief.md / payload.md / playbook.md)에 모이고 같은 slug 재실행 시 playbook을 먼저 참조한다. **내재화 원칙** — Scope 우선(retrieval need 먼저) · 체계적 최적화≠더 채우기 · 구조적 증분(brevity bias·context collapse 가드) · 위치 인지 배치(lost-in-the-middle) · playbook 큐레이션 · 사실 보존·환각 컨텍스트 금지 · 멀티 에이전트 per-agent 격리(opt-in) · 검증 없는 출하 금지 · 승인 게이트. **경계** — 작업의 에이전트 병렬화 판단 · AI 산출물 평가(judge 구성) · 엔지니어용 실행 명세 작성 · 기획자용 PRD · 하네스 자체 진단 · 단발 코드 수정은 범위가 아니며(일반 개념으로만 변별, 타 플러그인 비의존), description·trigger-eval에 명시한다. 근거: A Survey of Context Engineering(arXiv:2507.13334)[정의·taxonomy, vote 3-0] · ACE: Agentic Context Engineering(arXiv:2510.04618, ICLR 2026)[진화 playbook·brevity bias·context collapse, vote 3-0] · DACS: Dynamic Attentional Context Scoping(arXiv:2604.07911)[context pollution·REGISTRY/FOCUS, vote 2-1 medium — 정량수치 비인용, 질적 패턴만].

### Plugin: `agent-orchestration`

| Skill | Command | Description |
|-------|---------|-------------|
| Agent Orchestration | `/agent-orchestration` | 한 작업을 **여러 에이전트로 병렬화할지·어떻게 협업시킬지** 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증하는 진입 오케스트레이터. 작업 분해·평가(decomposability·tool density·단일 baseline 추정) → 아키텍처 결정(architecture-task alignment·capability ceiling → single/multi·토폴로지) → 협업 가드 설계(communication·commitment·expectation·context-pollution) → baseline 능가 검증(능가 못 하면 단일 권고) 4단계. Phase 0 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Decompose & Assess** — `task-decomposer`. 작업의 분해 가능성·도구 밀도·의존 구조를 평가하고 단일 에이전트 baseline을 추정(범인 지목이 아니라 구조 분석).
- **Decide Architecture** — `architecture-selector`. 선택 규칙(architecture-task alignment·45% capability ceiling)으로 single vs multi와 토폴로지(centralized/independent) 권고. 휴리스틱은 falsifiable하게 적되 결정론 rule로 과강화 금지.
- **Design Coordination** — `coordination-designer`. communication/commitment/expectation 세 실패 메커니즘 가드(expectation 우선) + per-agent 컨텍스트 격리(context-pollution 회피) 설계. 멀티일 때만.
- **Verify-or-Reject** — `orchestration-verifier`. 계획이 단일 baseline을 *실제로* 능가하는지 적대 검증. 순이득이 양임을 증명 못 하면 단일 에이전트 권고(REJECT)가 정당한 결과.

> `agent-orchestration`은 **여러 에이전트를 쓸지/어떻게 협업시킬지 결정·설계·검증**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차, single이면 Phase 2 skip). 핵심 메시지는 **"에이전트를 더 붙인다고 항상 이득이 아니다 — 성패는 수가 아니라 architecture-task alignment가 결정한다"**. **내재화 원칙** — 에이전트 수≠이득 · capability ceiling(경험적 임계, over-rule 금지) · 협업에는 비용(curse of coordination) · 실패는 root-cause(communication/commitment/expectation) · baseline 대비 순이득 검증 · falsifiable·over-rule 금지 · 승인 게이트. **경계** — 컨텍스트 페이로드 조립·압축 · AI 출력 평가(judge 구성) · 엔지니어용 구현 명세 작성 · 단일 자율 반복 루프 · 새 하네스 생성 · 프로덕션 장애 대응은 범위가 아니다. 근거: Towards a Science of Scaling Agent Systems(arXiv:2512.08296, Google/MIT/DeepMind/Anthropic)[+80.8%~−70.0% architecture-task alignment·45% capability ceiling, vote 3-0] · CooperBench(arXiv:2601.13295)[curse of coordination·communication/commitment/expectation 3실패모드, vote 3-0/2-1] · DACS(arXiv:2604.07911)[context pollution, vote 2-1 medium — 수치 비인용].

### Plugin: `eval-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Eval Harness | `/eval-harness` | AI 생성물(코드·에이전트 출력)을 **엄밀하게 평가**하는 진입 오케스트레이터. 핵심 질문은 '점수가 몇 점인가'가 아니라 **'이 점수를 믿어도 되는가'**. 정의·validity(task/outcome validity) → judge 구성(LLM-as-a-Judge 다중표본≥3·다관점 분해·실행 grounding) → validity 감사(ABC: shortcut·harness≠model 귀인·instruction density, BLOCK 게이트) → 실행·집계·보고(confidence·CAVEAT) 4단계. Phase 0 Eval Spec 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Define & Validity** — `eval-designer`. 평가 대상·관찰형 성공기준 + task validity(목표 역량 있어야만 풀린다)·outcome validity(결과가 실제 성공을 가리킨다) 명세 + 귀인 단위(model/harness/environment).
- **Build Judge** — `judge-builder`. judge를 단일 샷이 아니라 다중 표본(≥3)으로 구성하고, 어려운 판정을 다관점으로 분해(MCTS식 프레이밍), 가능하면 실행 결과에 grounding. temp-0 재현성을 정확성으로 착각 금지.
- **Audit Validity** — `validity-auditor`. ABC 관점으로 shortcut(풀지 않고 만점·파일시스템 악용)·harness≠model 귀인 혼동·instruction density 과밀을 judge 실행 *전에* 감사. 위반이면 BLOCK.
- **Run & Report** — `eval-runner`. 다중 표본 실행·집계, 분산을 confidence로 환산, validity 잔여 위험·grounding 유무·귀인 한계를 CAVEAT로 동반. baseline 대비로만 비교('개선 N% 보장' 금지).

> `eval-harness`는 **AI 생성물의 판정 신뢰성**(누가·어떻게·몇 번 채점하면 결과를 믿을 수 있는가)을 설계·감사·실행하는 데 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — validity 우선(상대 최대 100% 왜곡, 상한치) · single-shot 금지(다중 표본 ≥3) · 다관점 분해·실행 grounding · shortcut 적대 감사 · harness≠model 귀인 · instruction density 절제 · confidence·CAVEAT·baseline 대비 · 승인 게이트. **경계** — 컨텍스트 페이로드 조립 · 작업의 에이전트 병렬화 판단 · 엔지니어용 구현 명세 작성 · 기존 코드의 일반 실행 테스트 생성 · 커밋/PR 코드 리뷰는 범위가 아니다. 근거: Establishing Best Practices for Building Rigorous Agentic Benchmarks(ABC, arXiv:2507.02825)[task/outcome validity·상대 최대 100% 왜곡, vote 3-0] · Can You Trust LLM Judgments?(arXiv:2412.12509)[single-shot 위험·다중 표본, vote 3-0] · MCTS-Judge(arXiv:2502.12468)[test-time 다관점 분해, vote 2-1 — '41%→80%' 수치는 반박되어 비인용] · IFScale(arXiv:2507.11538)[instruction density 68%@500, vote 2-1] · Coding Benchmarks Are Misaligned(arXiv:2606.17799)[harness≠model 20+pp, vote 3-0].

### Plugin: `spec-driven-development`

| Skill | Command | Description |
|-------|---------|-------------|
| Spec-Driven Development | `/spec-driven-development` | 엔지니어용 **실행 가능 명세(spec)를 source of truth로 작성**하고 에이전트가 명세대로 코드 생성→명세 대비 자기검증하게 하는 진입 오케스트레이터. 워크플로를 코드 우선→명세 우선으로 역전(명세=1차 산출물, 코드=2차). 명세 작성(구조화 contract) → 인수기준·자기검증 설계 → 명세 대비 구현 → 명세 대비 검증(+comprehension 게이트) 4단계. Phase 0 명세 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Author Spec** — `spec-author`. 산문이 아니라 *구조화된 contract*(목표·범위 In/Out·인터페이스·동작·제약·엣지케이스)로 실행 가능 명세 작성. 에이전트가 그대로 구현·검증할 수 있게.
- **Acceptance** — `acceptance-designer`. 인수기준·테스트 계획·자기검증 체크를 명세 안에서 자족적으로 설계(LLM-as-a-Judge식 인수 점검을 이 플러그인 안에서 직접 기술, 외부 의존 금지). 인수기준이 명세를 falsifiable하게 덮는지 확인.
- **Generate-against-spec** — `spec-implementer`. 명세를 구현한 코드(또는 구현 가이드) + 추적성(어느 spec 조항을 어디서 구현했는지).
- **Verify-against-spec** — `spec-verifier`. "코드가 *명세대로* 도나"를 조항별로 검증(충족/미충족+증거) + comprehension 게이트(완료 선언 전 diff를 읽고 무엇이 왜 바뀌었는지 확인 — comprehension debt 방지, 명세가 이해의 앵커).

> `spec-driven-development`는 에이전트가 코드를 생성할 **엔지니어용 실행 가능 구현 명세 contract**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — 명세=source of truth · 명세 승인 게이트(구현 착수 전) · 구조화된 contract · 인수기준+자기검증 내재화 · 명세 대비 검증(추적성) · comprehension 게이트(comprehension debt 방지) · 과장 금지(정직성, 비판도 dossier에 기록). **경계** — 기획자용 PRD·사용자 스토리(문제정의·비즈니스 요구) 작성 · AI 출력 평가 judge 구성 · 컨텍스트 페이로드 조립 · 완성 코드 리뷰·커밋/PR · 하네스 자체 진단은 범위가 아니다(일반 개념으로 변별, 타 플러그인 의존 금지). 근거: Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants(arXiv:2602.00180)[명세=source of truth·워크플로 역전, vote 3-0; Martin Fowler의 non-determinism·overhead 비판 동반 — 'super-prompt' 주장은 반박되어 비인용] · Addy Osmani "How to write a good spec for AI agents"(2026-01, addyo.substack)[구조화·계획·반복, vote 3-0] · "The 80% Problem in Agentic Coding"(2026-01)[comprehension debt, vote 3-0].

### Plugin: `human-agent-teaming`

| Skill | Command | Description |
|-------|---------|-------------|
| Human-Agent Teaming | `/human-agent-teaming` | 사람과 AI 에이전트가 **한 팀으로** 효과적으로 협업하도록 **분업·공통기반·감독/신뢰·검증/지속**을 설계하는 진입 오케스트레이터. 축은 AI↔AI 토폴로지가 아니라 **사람↔에이전트의 분업·감독**이고 산출물은 프롬프트가 아니라 **협업 설계(teaming playbook)**. 분업·위임(Team Charter) → 공통기반(Common Ground Brief) → 감독·신뢰 보정(Oversight & Trust Plan) → 검증·지속(Verification & Sustain Plan) 4단계. Phase 0 분업 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Charter & Delegate** — `delegation-designer`. 작업을 사람↔에이전트 분업 charter로 변환 — 사람 소유(전략·북극성·하드 트레이드오프 결정·최종 검증·책임) vs 에이전트 소유(전문 실행 역할), 위임(human/agent/co-delegation + 실패 시 deferred·conditional delegation·trustworthy region), 자율 수준(작업 종류별 보수적 기본, 미입증이면 전수 검토), 운영 모드(human-in-the-loop vs human-on-the-loop), 고위험·비가역 결정점, 명확한 역할 경계.
- **Establish Common Ground** — `common-ground-builder`. "적혀 있지 않으면 에이전트엔 존재하지 않는다" — 팀원 온보딩 브리핑(북극성·제약·좋은 결과의 모습·자료 위치·예시·에스컬레이션) + AI 오류 경계 노출(parsimony·stochasticity로 mental model 보정) + workspace awareness(초점·의도 가시화) + 재정렬 루프(SMM은 영속 협상, 일회성 설정 아님). 토큰 컨텍스트 페이로드 조립이 아니라 협업 수준 공통기반·working agreement.
- **Calibrate Oversight & Trust** — `oversight-designer`. 모든 행동 승인이 아닌 **모니터링 기반 감독**(투명성 실시간 계획·개입/스티어링·단계적 가역 권한 read-only→쓰기 전 승인→영속·위험/신뢰 트리거) + 적절한 의존으로의 신뢰 보정(신뢰 최대화 아님, stakes×uncertainty 비례) + 특징적 실패모드 가드(over-reach→한 번에 하나의 경계 작업) + 자동화 편향/러버스탬프 가드. 에이전트 자기제한에 안전을 의존하지 않는다(반박된 패턴).
- **Verify & Sustain** — `verification-designer`. 인간 검증을 요구되는 마지막 층으로 운영화(코드=테스트·그 외=루브릭/스타일 가이드·Doer-Verifier fresh-context+Write/Edit 없는 평가자) + 검증 스캐폴딩(조기 완료 선언 차단) + 대칭 전문성 대응(하위 주장 분해·ground-truth 프로브) + 검증은 충분조건 아님 명시 + 핸드오프 연속성(진행 로그·기능 목록 passes:true/false·서술적 커밋) + 후속 재정렬(After-Action Review) + 책임은 사람(moral crumple zone 금지).

> `human-agent-teaming`은 **사람과 에이전트가 한 팀으로 어떻게 협업할지 설계**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — 에이전트는 도구가 아니라 팀원(멀티플레이어 분업) · 중심 긴장 자율성⇄통제(고위험·비가역 전 인간 통제) · 신뢰는 적절한 의존으로 보정(최대화 아님) · 감독=모니터링+개입(전수 승인 아님) · 공통기반은 만들고 지속 재협상(SMM 영속) · 명확한 역할 경계(restrained 에이전트) · 검증은 운영화된 마지막 층(Doer-Verifier, 충분조건 아님) · 책임은 사람 · 정직성(벤더=설계 의도·반박된 패턴 미사용)·승인 게이트. **경계** — 여러 AI 에이전트 병렬화·토폴로지(single/multi·centralized/independent) 결정 · 컨텍스트 페이로드 조립·압축 · AI 출력 평가(judge 구성) · 단일 자율 반복 루프 · 상류 산출물 핸드오프 게이트 검수 · 새 하네스 생성·하네스 진단 · PRD 작성 · 커밋/PR은 범위가 아니다(일반 개념으로 변별, 타 플러그인 의존 금지). 근거: Anthropic "Building Effective Human-Agent Teams"(claude.com/blog)[멀티플레이어 분업·4 fundamentals·역할 명문화·검증 산출물, vote 3-0 — 벤더 1차, 설계 의도] · "Building Effective Agents"[workflow vs agent·체크포인트·인간 리뷰 필요] · "Our framework for safe and trustworthy agents"[중심 긴장 자율성⇄통제·투명성·개입·단계적 가역 권한] · "Measuring Agent Autonomy"[감독=모니터링+개입, auto-approve 20%→40%/interrupt 5%→9% 관찰값] · "Effective harnesses for long-running agents"[over-reach·조기 완료·한 번에 하나의 작업·핸드오프 연속성] · arXiv:2504.10918 "Adaptive Human-Agent Teaming"(133개 경험 연구 리뷰)[위임 메커니즘·역할 경계 실패모드·신뢰≠의존·SMM 영속, vote 3-0] · arXiv:2602.05987 "From Human-Human to Human-Agent Collaboration"(CHI EA '26)[도구→팀원·CSCW 설계 질문, vote 3-0 medium — 비피어리뷰 제안서]. **정직성** — 벤더 소스는 설계 의도(크기 주장 "dramatically improved" 미인용)·수치는 코호트·시점 관찰값("개선 N% 보장" 금지)·반박된 주장(에이전트 자기제한 1차 감독 REFUTED 1-2·more-trust-is-better·approve-everything=안전)은 본문 미사용·반례(METR RCT 경험 개발자 ~19% 감속) 기록 — 모두 research dossier 반박 섹션에 기록.

### Plugin: `code-as-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Code as Agent Harness | `/code-as-harness` | 코드를 단순 산출물이 아니라 **실행 가능(executable)·검사 가능(inspectable)·상태 보존(stateful)** 한 운영 기반으로 다루고, 한 번의 **거버넌스된 Plan→Execute→Verify 제어 루프**로 코드 변경을 안전·검증 가능하게 수행하는 진입 오케스트레이터. 계획 계약(Plan Contract: 의도한 변경·결정적 센서·행동 위험 분류) → 권한 실행(Permissioned Execute: 가역 우선·안전임계 사람 게이트·실행 trace) → 실행 검증(Execution Verify: 자기보고 불신·결정적 센서 실행·reward-hacking·불완전 피드백 UNVERIFIED·최종 너머) → 텔레메트리 진단·수렴(Telemetry Diagnose & Converge: trace 인용 진단·regression-free 수정·CONVERGED/ITERATE/ESCALATE) 4단계. Phase 0 계획 계약 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Plan Contract** — `plan-contractor`. 작업을 *변경 계약*으로 변환 — 의도한 변경(파일·동작·불변식·바꾸지 않을 것)을 조항화하고, 성공을 판정할 **결정적 센서**(테스트·빌드·타입·린트·실행)를 *사전* 명시하며(각 조항에 '무엇이 반증인가'), 각 행동을 가역 vs 안전임계/비가역(삭제·마이그레이션·스키마·네트워크 egress·시크릿·프로덕션)으로 분류해 사람 게이트 표시. 계약만(실행·검증 상세 금지).
- **Permissioned Execute** — `permissioned-executor`. 계약을 권한·샌드박스 경계에서 최소 변경·**가역 우선**으로 실현, 안전임계/비가역 행동은 *실행 전 사람 승인 게이트*(전수 승인 아님 — 가역은 진행), 계획조항→diff→관측 피드백을 **구조화된 실행 trace**로 적재(Phase 2·3가 직접 조회). 센서 판정·테스트 약화는 하지 않음.
- **Execution Verify** — `execution-verifier`. 계약의 **결정적 센서를 실제로 돌려** 조항별 PASS/FAIL/UNVERIFIED를 센서 출력 증거와 함께 판정(자기보고 불신), reward-hacking·verifier-gaming(테스트 약화·skip·기대값 맞추기·하드코딩·형식 우회) 가드, 불완전 피드백이면 PASS 단정 금지(UNVERIFIED·confidence 강등), 최종 task 성공 너머 불변식·부작용·인접 회귀도 확인. 코드 수정 안 함(검증 전용).
- **Telemetry Diagnose & Converge** — `telemetry-diagnostician`. 실행 trace를 최적화 substrate로 읽어 root cause를 **trace 인용**(어느 조항·diff·센서 출력)으로 진단(추측 금지), 통과 센서 비회귀를 점검한 **regression-free** 차기 수정안 제안, 무진전(반복·진동)이면 ESCALATE, **CONVERGED/ITERATE/ESCALATE** 결정(최종 수렴 사람 게이트). 코드 수정 안 함(진단·제안만).

> `code-as-harness`는 **코드를 실행·검증 가능한 하네스로 다루는 거버넌스된 Plan→Execute→Verify 제어 사이클**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차, 필요 시 사람 승인 하 1회 ITERATE). **내재화 원칙** — 코드=운영 기반(executable·inspectable·stateful) · 계획=변경 계약 · 권한·샌드박스 실행(가역 우선·안전임계 사람 게이트) · 실행 기반 검증(자기보고 불신) · reward-hacking 가드 · 불완전 피드백 UNVERIFIED(증거 없는 PASS 금지)·최종 너머 · 검사 가능 trace=텔레메트리 substrate · regression-free 개선(무진전 ESCALATE) · 사람 감독은 안전임계 집중 · 정직성(서베이=개념 프레임·인접 기법 귀속 분리·반박된 AgentFlow 4-phase 미사용)·승인 게이트. **경계** — 통과까지 자율 반복+교차세션 학습 메모리(자율 반복 도메인) · 백엔드 환경 provisioning 1급 구현(백엔드 구현 도메인) · 실행 가능 명세 작성(명세 우선 도메인) · AI 에이전트 병렬화·토폴로지(멀티 에이전트 오케스트레이션 도메인) · 컨텍스트 페이로드 조립(컨텍스트 설계 도메인) · AI 출력 평가(평가 도메인) · 하네스 자체 진단(메타 도메인) · 상류 핸드오프 검수(핸드오프 리뷰 도메인) · 프로덕션 인시던트 대응(운영 도메인) · PRD·커밋/PR·settings는 범위가 아니다(일반 개념으로 변별, 타 플러그인 의존 금지). 근거: arXiv:2605.18747 "Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems"(2026-05)[코드=operational substrate·3-layer(Interface/Mechanisms/Scaling)·Plan-Execute-Verify 제어 루프·sandboxed·permissioned 실행·결정적 센서+human-review gate·open challenge(evaluation beyond final success·verification under incomplete feedback·regression-free improvement·human oversight for safety-critical)=가드레일, vote merged 3-0] · 인접 1차 arXiv:2604.08224 Externalization[weights→context→harness, 3-0] · arXiv:2506.11442 ReVeal[generation-verification 공진화·turn-level credit, 3-0] · arXiv:2604.20801 AgentFlow[harness 민감도 several-fold·사전 검증 게이트(20% 기각), 3-0] · arXiv:2508.00083 code-gen taxonomy[3-0] · arXiv:2512.14012 "developers don't vibe, they control"[plan-first·전 산출물 검증, 3-0] · 보강 arXiv:2604.15149 verifier reward-hacking · arXiv:2603.07084 sandbox 격리(failure-modes 각도 보강). **정직성** — 대상 서베이는 *개념 프레임*(벤치마크 결과 아님)·인접 논문 기법(TAPO·AgentFlow DSL)은 *각 출처에만* 귀속·'several-fold(4x)'는 *특정 세팅값*·반박된 AgentFlow 4-phase 루프(REFUTED 1-2)는 본문 미사용·"개선 N% 보장" 금지 — 모두 research dossier 반박/CAVEAT 섹션에 기록.

### Plugin: `llm-guardrails-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| LLM Guardrails Harness | `/llm-guardrails-harness` | LLM/에이전트 앱에 **런타임 외부 가드레일**을 설계·강제하는 진입 오케스트레이터. 위협 모델링·정책(OWASP LLM Top 10 2025 매핑·fail-closed) → 입력 레일(jailbreak/injection 탐지·Llama-Guard 분류·거부/재작성) → 출력·검색 레일(PII 리댁션·독성/정책·grounding·untrusted 청크) → 행동 강제·적대 검증(최소 권한 tool 스코핑·비가역 행동 사람 게이트·ASR/FPR red-team) 4단계. Phase 0 정책 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Phase 0 위협 모델링·정책** — `threat-modeler`. 대상 앱을 OWASP LLM Top 10 2025(LLM01 injection·LLM02 disclosure·LLM05 output·LLM06 agency·LLM08 vector)에 매핑, 콘텐츠/행동 카테고리를 분류기 판정 가능한 ID로 내리고 레일 배치·fail-closed 정책 명문화(정책만).
- **Phase 1 입력 레일** — `input-rail-engineer`. 모델 호출 전 jailbreak/prompt-injection 탐지·Llama-Guard 스타일 SAFE/UNSAFE+카테고리 분류·요청 검증으로 거부/재작성/마스킹. 분류기 불확실 시 fail-closed.
- **Phase 2 출력·검색 레일** — `output-rail-engineer`. 생성 후 PII 리댁션·독성/정책 필터·grounding/환각 점검 + 검색 시점 untrusted 청크 필터링(indirect prompt injection).
- **Phase 3 행동 강제·적대 검증** — `enforcement-redteamer`. 최소 권한 tool 스코핑·인자/결과 검증(execution rails)·비가역 행동 사람 승인 게이트 + 전체 레일 red-team(ASR 대 FPR 함께 측정, 우회 반복 보강).

> `llm-guardrails-harness`는 **LLM I/O·tool 호출의 콘텐츠·행동 정책을 런타임에 외부에서 인라인 강제하는 방어심층**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — 외부 강제>시스템 프롬프트 신뢰 · 전체 레일 taxonomy(input/dialog/output/retrieval/execution) 커버 · fail-closed 기본값 · 가드레일 자체가 공격 가능한 LLM(다층 방어) · excessive agency 최소 권한+사람 게이트(LLM05→LLM06) · 검색/도구 반환 콘텐츠 불신(LLM08) · safety-utility(ASR↔FPR) 트레이드오프 명시 · 런타임·인라인·관측 · 정직성(사내 구현 비귀속·개선 N% 금지·가드레일은 위험 감소지 제거 아님)·승인 게이트. **경계** — 오프라인 AI 출력 judge 채점(`eval-harness`) · 프로덕션 장애 RCA(`ops-harness`) · 상류 핸드오프 검수(`review-harness`) · 사람↔에이전트 협업 설계(`human-agent-teaming`) · 에이전트 병렬화·토폴로지(`agent-orchestration`) · 일반 백엔드 구현(`backend-harness`) · 코딩 에이전트 코드 변경 거버넌스(`code-as-harness`) · 웹 소스 취약점 스캔(`frontend-harness`) · 토큰·스코프·위임 등 아이덴티티/인가 아키텍처 설계(`agent-authorization-harness`)는 범위가 아니다(일반 개념으로 변별). excessive agency(LLM06)는 `agent-authorization-harness`와 공유 이음매 — 본 하네스는 런타임 콘텐츠·행동 레일, agent-authorization은 그 아래 자격/스코프 계층이다. 근거: OWASP Top 10 for LLM Applications 2025[HIGH] · NVIDIA NeMo Guardrails(5 rail types)[HIGH] · Llama Guard(arXiv:2312.06674)[HIGH] · SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597, ASR/FPR·adaptive bypass)[HIGH] · OWASP LLM Prompt Injection Prevention Cheat Sheet[HIGH] · Adaptive Evaluation of Out-of-Band Defenses(arXiv:2606.26479)[MEDIUM]. 출처: Tech-Verse 2026 S04 "Beyond Intelligence to Safety: External AI Guardrails"의 전이 가능한 코어만 일반화.

### Plugin: `qa-agent-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| QA Agent Harness | `/qa-agent-harness` | **end-to-end 에이전틱 소프트웨어 QA**(FE+API 무관) 진입 오케스트레이터. 리스크 기반 테스트 전략(리스크 노출=확률×영향) → 시나리오 설계(리스크 매핑 + 명시적 오라클, 살아있는 라이브러리) → 오라클 우선 생성 + 자가치유 실행(로케이터/DOM 드리프트 점수화·로깅·게이트) → 실패 트리아지(결함 vs 플래키 vs 환경·공유 근본원인 클러스터·변경 기반 우선순위) 4단계. 점진적 자율성·HITL 게이트. Phase 0 전략 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Phase 0 리스크 기반 전략** — `test-architect`. 요구사항·변경·리스크를 리스크 노출 등급으로 정규화, 균일 커버리지가 아니라 노출도로 테스트 깊이·순서를 배분한 전략 산출.
- **Phase 1 시나리오 설계** — `scenario-designer`. 스토리/API/도메인 규칙을 리스크 매핑 시나리오로 번역하되 각 시나리오에 명시적 오라클(기대 상태·불변식) 부착, 정적 회귀팩이 아닌 진화하는 라이브러리.
- **Phase 2 오라클 우선 생성·자가치유 실행** — `test-engineer`. 스모크/동어반복 금지·진짜 오라클, 로케이터 드리프트는 role→data-testid→접근성 트리→가시 텍스트 우선순위로 점수화 자가치유(로깅·게이트, 회귀 은폐 금지).
- **Phase 3 실패 트리아지** — `failure-triager`. 재시도 전에 결함 vs 플래키 vs 환경 분류, 플래키는 공유 근본원인 클러스터링, 변경 영향+리스크로 재실행 우선순위화.

> `qa-agent-harness`는 **리스크→오라클→실행→트리아지의 독립 end-to-end 에이전틱 QA 라이프사이클**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — 리스크 노출이 노력 배분 · 오라클 우선(커버리지≠결함탐지) · 오라클 독립 검증(CANDOR 합의) · 자가치유는 점수화·로깅·게이트 · 재시도 전 트리아지 · 변경 기반 우선순위화 · 점진적 자율성+HITL 게이트 · 커버리지 연극·리워드 해킹 가드 · 정직성(조직 도입·성숙도 층 제외·회사별 수치는 관찰값·개선 N% 금지)·승인 게이트. **경계** — 넓은 FE 개발 워크플로우 안의 FE 한정 QA(`frontend-harness`) · 구현 흐름 내 단일 test-generator(`backend-harness`) · 오프라인 judge 채점(`eval-harness`) · 프로덕션 인시던트 RCA(`ops-harness`) · 상류 인수조건↔테스트 핸드오프 검수(`review-harness`) · 도메인 무관 자율 반복 루프(`loop-engineering`) · 에이전트 병렬화 판단(`agent-orchestration`) · 사람↔에이전트 분업(`human-agent-teaming`) · LLM 입출력 가드레일(`llm-guardrails-harness`)은 범위가 아니다. 근거: arXiv:2601.02454 "The Rise of Agentic Testing"[HIGH] · arXiv:2506.02943 CANDOR(오라클 다중표본 합의)[HIGH] · arXiv:2606.18168 "All Smoke, No Alarm"(오라클 신호)[HIGH] · arXiv:2504.16777 "Systemic Flakiness"(공동발생 클러스터)[HIGH] · arXiv:2601.05542 LLM 오라클[MEDIUM] · Requirements-based test prioritization 산업연구[MEDIUM] · Katalon Agentic QA 운영모델[MEDIUM]. 출처: Tech-Verse 2026 S06 "10x Speed With QA Agent Platform"의 harnessable core만 추출(성숙도·변경관리 층 제외).

### Plugin: `agent-authorization-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Agent Authorization Harness | `/agent-authorization-harness` | 에이전트/MCP 도구/A2A 시스템의 **머신 아이덴티티·인가(authorization) 아키텍처를 벤더 무관하게 설계·red-team**하는 진입 오케스트레이터. 신뢰·스코프 모델링(참여자·authN vs authZ·최소 스코프) → 그랜트·위임 설계(단명 audience-bound 토큰 RFC 8707·on-behalf-of 토큰 교환 RFC 8693·no passthrough) → 동의·집행(authN/authZ 분리·deny-by-default·end-to-end audience 검증·동의 게이트·감사) → 적대적 인가 검증(confused-deputy·토큰 재생·스코프 크리프·무제한 위임) 4단계. 산출물은 설계+위협 분석(IdP 배포 아님). Phase 0 모델링 승인 게이트 |

4개 에이전트 구성 (모두 `model: "opus"`):

- **Phase 0 신뢰·스코프 모델링** — `trust-scope-modeler`. subject/actor/client/resource와 인증(IdP) vs 인가(PDP) authority를 열거, 접촉하는 도구·리소스·에이전트를 매핑해 상호작용별 최소 스코프·신뢰 경계 산출.
- **Phase 1 그랜트·위임 설계** — `grant-delegation-designer`. 장수 공유 자격증명 대신 단명·audience-bound 스코프 토큰, on-behalf-of 위임은 토큰 교환(`subject_token`/`actor_token`/`may_act`)으로 매 신뢰 경계 fresh exchange·no passthrough, 표준 그랜트(OAuth 2.1·ID-JAG) 우선.
- **Phase 2 동의·집행 설계** — `consent-enforcement-designer`. 인증(누구)/인가(허가되는가) 분리·deny-by-default·민감/비가역 스코프 사람 동의 게이트·모든 resource server의 end-to-end audience 검증·감사 로깅(인가는 LLM이 아니라 외부 시스템).
- **Phase 3 적대적 인가 검증** — `authorization-redteamer`. confused-deputy(injection→특권 도구 호출)·토큰 재생/passthrough·과대/ambient 스코프·무제한 위임 체인·네트워크를 신뢰로 착각을 상대로 RESISTS/PARTIAL/FAILS 위협 분석(산출물은 분석, 라이브 배포 아님).

> `agent-authorization-harness`는 **만들어지는 에이전트/도구/A2A 시스템의 머신 아이덴티티·인가 모델 설계+red-team**에 특화한 도메인 무관 하네스다. 4개 에이전트를 서브에이전트로 spawn한다(모두 `model: "opus"`; Phase 0→3 순차). **내재화 원칙** — 접근 근거로 네트워크·공유 키·LLM 판단 불신 · 최소 권한(LLM06 과대 기능/권한/자율) · 단명·audience-bound 토큰(RFC 8707, end-to-end 검증) · 표준 on-behalf-of 위임(RFC 8693 may_act, no passthrough) · 인증≠인가(외부 시스템) · deny-by-default+동의+감사 · 표준 준수>자체 구현 · 설계+red-team이 산출물(배포 아님·벤더 illustrative) · 런타임 레일과 합성(대체 아님) · 정직성(discipline HIGH/framing MEDIUM·개선 N% 금지)·승인 게이트. **경계** — 런타임 콘텐츠·행동 레일 집행(`llm-guardrails-harness`, LLM06 공유 이음매 — guardrails는 요청 시점 행동 한계 집행, 본 하네스는 그 한계가 존재·최소권한이 되게 하는 자격/스코프/위임 설계, 합성하되 중복 아님) · 사람↔에이전트 업무 분업·감독(`human-agent-teaming`) · 파이프라인/릴리스 policy-as-code OPA(`cicd-harness`) · 코딩 에이전트 자신 파일수정 권한·샌드박스(`code-as-harness`) · 일반 API 구현(`backend-harness`) · 장애 RCA(`ops-harness`) · 상류 핸드오프 검수(`review-harness`) · 오프라인 judge 채점(`eval-harness`) · 병렬화·토폴로지(`agent-orchestration`) · 특정 IdP/Keycloak/Athenz 배포·인프라 provisioning은 범위가 아니다. 근거: RFC 8707 Resource Indicators[HIGH·published] · RFC 8693 Token Exchange[HIGH·published] · OWASP LLM06:2025 Excessive Agency[HIGH] · A2A Protocol spec[HIGH] — discipline HIGH; ID-JAG draft-ietf-oauth-identity-assertion-authz-grant-04 · MCP Authorization draft · OWASP Agentic ASI01/ASI03(2025-12) · Okta XAA(illustrative) — framing MEDIUM(in-flux 초안). 출처: Tech-Verse 2026 S07 "ID-JAG: Enterprise-Ready Standard for AI Agent Authorization in the MCP and A2A Era"의 배포 사례가 아니라 이전 가능한 설계 규율만 추출.

### Plugin: `ai-readiness-cartography`

| Skill | Command | Description |
|-------|---------|-------------|
| AI-Readiness Cartography | `/ai-readiness-cartography` | 임의 git 저장소가 'AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스'인지를 **측정하고(결정론 스코어러) 개선을 설계하는(멀티 에이전트)** 단일 스킬(2모드). ① 측정 모드: score.py 자동 채점 → HTML 대시보드 → ROI 가이드. ② 진단·개선 모드: score.py를 센서로 2축 진단(승인 게이트)→빌드 가드레일→standalone→수용 증명·재측정. 발동 시 모드 확정 |

**단일 스킬 2모드 (측정 / 진단·개선). 개선 모드는 4 에이전트(모두 `model: "opus"`)를 spawn.** 핵심 자산:

- **`scripts/score.py`** (stdlib only, Python 3.10+) — 100점·9카테고리(E22/D18/B15/C12/H9/A8/F8/I5/G3) + **3 blocking gate**(Gate-1 Reference Integrity·Gate-2 Executable Verification=Auto·상한 AI-Fragile / Gate-3 Architecture Enforcement=Heuristic·개선 모드 전용·상한 AI-Assisted). **gating 집계** — blocking 결함이 등급에 상한을 씌운다(순수 가중합 아님). import 그래프·결합도 god-file·reference integrity 자동 산출. 개선 모드에서 Phase 0 진단 seed·Phase 3 재측정 델타로 재사용.
- **4 에이전트** (`agents/`) — `accessibility-assessor`(Phase 0: score.py seed 위 2축 진단 + 5밴드 등급 + Gate-3 예비판정) · `guardrail-architect`(Phase 1: 빌드 가드레일·의존 방향 물리 강제·피드백 3차원) · `standalone-designer`(Phase 2: port/adapter·use-case seed) · `acceptance-verifier`(Phase 3: 수용 증명 + 결정론 델타 위 강제 probe로 Gate-3·등급 재측정).
- **`references/scoring-rubric.md`** — v3 루브릭(9카테고리 + 3 gate). **`references/ai-readable-codebase-principles.md`** — 개선 모드 원리(2축·빌드 가드레일·standalone·수용 증명). **`references/research/`·dossier** — 2025~2026 1차 근거(`deep-research` 5세션 적대 검증). **`assets/template.html`** — 대시보드 원본.

> `ai-readiness-cartography`는 **코드베이스 AI 준비도를 측정(결정론 5밴드+3 gate)하고 그 위에서 구조 개선을 설계**하는 단일 스킬(2모드)이다. 등급은 단일 5밴드만 쓰고(L1~L5 폐기·`점수/20=L` 선형변환 금지) enforcement 축은 Gate-3로 흡수한다. **내재화 원칙** — 모드 게이트 먼저 · 결정론 우선·사람 보강 · gating(Gate-1/2→AI-Fragile, Gate-3→AI-Assisted) · 근거 서열=가중치 서열 · 문서 존재≠좋음(보유율 미채점) · god-file=결합도 · A축≠Q축·구조가 프롬프트보다 먼저·빌드가 강제하고 문서가 설명한다(개선 모드) · generator/checker 분리 · auto/heuristic/manual 라벨 · 제안만 · 과장 금지. **경계** — 한 기능 구현(`backend-harness`)·상류 핸드오프 검수(`review-harness`)·하네스 자체 진단(`meta-harness`)·전달 파이프라인(`cicd-harness`)·명세 작성(`spec-driven-development`)·컨텍스트 조립(`context-engineering`)·AI 생성물 judge(`eval-harness`)·병렬화·토폴로지(`agent-orchestration`)·완성 코드 리뷰·PR(`frontend/git-harness`)은 범위 밖. 근거: 측정은 ORACLE-SWE(2604.07789)·LocAgent(2503.09089)·ETH Zurich(2602.11988)·USENIX 2025 slopsquatting·RepoMirage(2605.26177)·Factory/Kenogami; 개선 모드는 flex.team 5부작 + arXiv:2505.10443·2602.11481·2306.09896. 출처: 외부 스킬 v2를 v3로 리팩토링(deep-research 5세션)한 뒤 별도 `ai-readable-codebase` 플러그인을 진단·개선 모드로 흡수(v0.2.0).

### Plugin: `token-efficiency`

| Skill | Command | Description |
|-------|---------|-------------|
| Token Efficiency | `/token-efficiency` | Claude Code **세션 JSONL 로그**를 파싱해 레포 단위 토큰/컨텍스트 효율을 정량 측정·시각화하고 $ 절감안을 내는 결정론적 단일 스킬. analyze_sessions.py(4축 가중 점수) → detect_patterns.py(8개 비효율 탐지기) → build_dashboard.py(오프라인/CSP 안전 인라인-SVG HTML). 산출물: session_analysis.json + pattern_analysis.json + 단일 HTML 대시보드 |

**단일 스킬 구성 (에이전트 팀 없음 — 로그 분석기 본성에 충실)**. 핵심 자산:

- **`scripts/analyze_sessions.py`** (stdlib only, Python 3.9+) — 4축 가중 점수(cache 35·redundancy 30·density 15·tool 20, 각 축에 근거 등급 CONFIRMED/PLAUSIBLE/HEURISTIC). 현행 PRICING(Opus $5/$25·Fable 5 $10/$50, 캐시배수를 입력가에서 파생 read 0.1×/write5m 1.25×/write1h 2×), `--pricing`·`--weights` 오버라이드. 종료 메시지에 "효율 프록시≠cost-of-pass" 경고.
- **`scripts/detect_patterns.py`** — 8개 결정론 탐지기(context-bloat·giant-tool·poor-cache·duplicate·subagent + 신규 stale-observation·cache-invalidation-churn·read-exploration-heavy). 낭비 $는 각 세션 dominant 모델가로.
- **`scripts/build_dashboard.py`** — 인라인 SVG HTML(외부 CDN 없음, CSP/오프라인 안전). 세션별 라우팅 후보 판별·compact 캐시-깨짐 caveat·근거 등급 rubric.
- **`scripts/test_efficiency.py`** — 회귀 테스트 61건(가중치 합·양방향 가격 동기화·탐지기·사이드체인 배제·golden 점수·경로 인코딩).
- **`references/research/`** — 2025~2026 1차 근거(합성 README + 5 세션, `deep-research` 5세션 적대 검증. ACON "무손실" claim REFUTED·Context-Folding 10× 강등 등 정직 반영).

> `token-efficiency`는 **런타임 세션 로그의 토큰 경제를 결정론적으로 측정·시각화**하는 단일 스킬이다. 외부 스킬 `improve-token-efficiency`를 deep-research(5 세션 적대 검증)의 2025~2026 근거로 개선했다. **내재화 원칙** — 결정론 우선·제안만(자동 수정 안 함) · 점수=효율 프록시(≠cost-of-pass, task success 미관측) · 현행 가격(두 스크립트 동기화, `--pricing` 갱신) · 낭비는 세션 실제 모델가 · giant-tool fix는 blind 절단 금지(Squeez Last-N 0.05 recall) · compact엔 캐시-깨짐 caveat(35% 캐시 축 상충) · 대시보드 오프라인/CSP 안전. **경계** — 정적 저장소 AI 준비도(`ai-readiness-cartography`, 런타임 세션 로그 vs 정적 구조 — **상보**) · 새 코드·PR 리뷰(`frontend/git-harness`) · 하네스 진단(`meta-harness`) · AI 생성물 judge(`eval-harness`) · 컨텍스트 페이로드 조립(`context-engineering`)은 범위 밖. 근거: ACON(2510.00615, 컨텍스트 부풀림 품질 harm·압축 캐시 깸)·Squeez(2604.04979, 관측치 92% 프루닝·naive 절단 실패)·AgentDiet(2509.23586, 궤적낭비 3분류 useless/redundant/expired)·SWE-Pruner(2601.16746, task-aware 프루닝)·Complexity Trap(2508.21433, stale 마스킹 ~52% 절감)·읽기 지배(2606.14066, 76.1%)·cost-of-pass(2508.02694, 성공-가중 비용·작업 의존 라우팅)·Anthropic 캐싱 1차(exact-prefix·배수·최소 프리픽스). 출처: 외부 스킬 `improve-token-efficiency`(4축 점수+5 탐지기+6 절감 휴리스틱)를 deep-research 5세션 적대 검증으로 개선.

### Plugin: `test-layering-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Test Layering Harness | `/test-layering-harness` | 인수조건(AC, Given-When-Then)을 **방법론·계층 축 카드 7개(방법론4+계층3)**로 조합·CI 단계에 배치해 계획하고, **계획→개별→최종 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정하는 진입 오케스트레이터. Phase 0 초기문의(AC·개발환경 각각 스킵 가능·환경 미입력 시 현재 경로) → 1 적응형 프리셋 추천+체크박스 다중선택(=구속 스코프)+조합 강도 lookup → 2 **각 AC를 축 카드(`references/matrix/`) 조합으로 라우팅**(Step0 스코프→선택된 계층/방법론만→조합 선택)+결합 오라클 프로필+게이트A → 3 개별 순차 적용+게이트B → 4 반영+게이트C. **⚠️ 스코프 가드: 선택한 방법론·계층 안에서만 추가**(밖은 확장 문의). 조합=다중 멤버십(12셀 미리 물질화 안 함)·nightly는 CI-stage 축·sanity≡smoke 동의어라 WEAK/DEGENERATE 조합 정직히 비움 |

**단일 스킬 구성 (에이전트 팀 없음 — 인터랙티브 오케스트레이터 본성에 충실)**. 핵심 자산:

- **`SKILL.md`** — 5-Phase·3-Gate 오케스트레이터. Phase 0 초기 문의(AC **3지선다 명시 프롬프트** (a)붙여넣기 (b)파일·링크 경로 (c)없음→저장소 후보 채굴 — 채굴은 사용자 명시 선택이지 곧장 건너뛰기 아님·최초 요청 인라인 AC면 재질문 금지; 개발환경 스킵 시 현재 경로 기준 러너/디렉토리 관습 감지·부재 러너 보고·비차단) → Phase 1 적응형 방법론×계층 구성(감지 신호로 3 프리셋 추천 + 매트릭스 제시 + **방법론 스위트(Smoke/Sanity/Regression/nightly)·계층(Unit/Integration/E2E) 체크박스 다중선택** — 프리셋 기본체크·러너 부재 계층 '추가 필요' 명시·스코프 고정) → Phase 2 AC→계층 계획(GWT→AAA 분해·오라클 부착·계획표) + **게이트 A 계획 승인** → Phase 3 개별 순차 적용(오라클 오검증·flaky baseline·draft + **durable 스위트 태그 물리 부여·분리 실행 스크립트 추가·셀렉터 실행 분리 검증**, sanity는 무-태그 변경-스코프 선택) + **게이트 B 개별 적용 승인** + 실행 그라운딩 → Phase 4 반영 + **게이트 C 최종 재확인**(커밋 직접 안 함·git-harness 핸드오프).
- **`references/test-layering-principles.md`** — 방법론 정의·트리거·CI 배치 매트릭스(tier는 파이프라인 뒤로 갈수록 넓어짐)·AC→tier 분해 규칙(§4, AC≠E2E)·**AC→축 카드 조합 라우팅(§4.5, 스코프 가드)**·실체화(§3.5)·오라클 강도 5개 가드·3 프리셋(Trophy-lean/Google-pipeline/Contract-honeycomb)·저장소 감지 신호·anti-pattern·경계.
- **`references/matrix/`** — **방법론·계층 축 카드 7개**(방법론 카드 4 + 계층 카드 3) + `_index.md`(축 직교성·**스코프 가드(선택 안에서만 추가)**·조합 라우팅 절차·조합 강도 lookup·정직성 불변식). 12개 셀로 미리 물질화하지 않고 라우팅 시 두 축을 조합. 각 축 카드는 포함/제외 체크리스트·오라클 프로필·실체화·근거를 담는다.
- **`references/research/matrix-criteria-2025.md`** — 조합 라우팅 기준 근거 dossier(직교성·계층/방법론 판정·조합 강도 lookup·정직성 원장·소스 인덱스; ISO/IEC/IEEE 29119-1:2022 §4.4.6·ISTQB·SWE@Google test sizes·arXiv 2025+, 인용 교정 완료).
- **`references/research/test-strategy-research.md`** — 2025+ 근거 dossier(A~G, 신뢰도 HIGH/MED/LOW·folklore·모순 표기, `deep-research` plain-text fan-out 5각도 적대 검증).

> `test-layering-harness`는 **AC를 방법론·계층 축 카드 7개(방법론4+계층3)로 조합 라우팅해 계층별 테스트로 계획하고 계획→개별→최종 3게이트로 순차 적용**하는 도메인 무관 인터랙티브 단일 스킬이다. **내재화 원칙** — 3게이트를 건너뛰지 않음(승인 없이 파일 쓰기 없음) · **스코프 가드: 테스트는 사용자가 Phase 1에서 선택한 방법론·계층 안에서만 추가**(밖은 임의 추가 금지·'추가 안 함' 표기 후 확장 문의·3게이트와 동급) · **배치·mock 규약**: unit/integration은 대상(컴포넌트/유틸) 파일 폴더의 `__test__/`에 `*.test.*`로 두고 외부 API는 캡처 응답 mock(fixture)로 double(live 금지)·E2E는 선택 시 테스트 경로 초기 문의·nightly full-suite도 캡처 mock로 결정론 실행(cross-browser/real-device는 실제·API는 mock) · 비율%(70/20/10) 하드코딩 금지(folklore) · **각 AC를 축 카드 조합으로 라우팅**(Step0 스코프→슬라이스→선택된 계층만→선택된 방법론만(비배타·다중)→조합 강도 lookup으로 상황 선택→계획행) · **조합은 다중 멤버십이지 12개 셀로 미리 물질화 안 함·4번째 유형 아님**(계층=durable 속성·방법론=selection/tag, ISO/IEC/IEEE 29119-1:2022 §4.4.6) · **nightly는 방법론 아니라 CI-stage/스케줄 축**(ISTQB/ISO에 test type 없음) · **sanity≡smoke ISTQB 동의어**라 Sanity 전 조합·Nightly×Unit·Smoke×Unit=WEAK/DEGENERATE 정직히 비움 · **prioritization은 CI 비용 못 줄임**(latency만, 정의상(재정렬=총실행량 불변))·safe-RTS full fallback · **Regression×Unit=최고위험 오라클 셀**(LLM green-locks-bug) · 오라클 강도가 최대 리스크(LLM은 명세 아니라 구현을 굳혀 버그를 초록 은폐 → 기대(AC) 기준 오검증·실행 그라운딩·flaky baseline 선결·스모크/동어반복 어서션 금지) · AC≠E2E(한 AC는 여러 tier로 분해·E2E는 핵심여정 소수) · 적응형 프리셋 추천(고정 강제 아님) · CI 배치는 tier가 뒤로 갈수록 넓어짐·선택>우선순위 · 근거 없는 효과 수치 금지 · 커밋 직접 안 함(git-harness 핸드오프) · 제안·게이트만·자동 커밋 없음. **경계** — 리스크 노출 기반 오라클·자가치유 실행·결함/플래키 트리아지 end-to-end QA(`qa-agent-harness`) · 백엔드 기존 코드 generate→compile→execute→repair test-generator(`backend-harness`) · 이미 있는 AC↔테스트 커버리지 읽기전용 핸드오프 검수(`review-harness`/test-coverage-review) · FE 개발 워크플로우 내 TDD(`frontend-harness`) · 에이전트용 실행 가능 명세 작성(`spec-driven-development`) · 커밋/PR(`git-harness`)은 범위 밖. 근거: Google presubmit/postsubmit(SWE at Google Ch.23)·Fowler DeploymentPipeline/UnitTest·Kent C. Dodds Testing Trophy(FE 한정)·Spotify Honeycomb(2018 MSA)·SWE@Google test sizes·ISO/IEC/IEEE 29119-1:2022·ISTQB Glossary/CTFL·arXiv:2504.16777 Systemic Flakiness·arXiv:2601.05542 LLM 오라클·arXiv:2504.07244 AutoUAT·arXiv:2410.21136·arXiv:2308.13129 batching 무손실(ESEC/FSE 2023)·arXiv:2509.10279 targeted test selection(선택 lossy)·arXiv:2601.08998 flakiness 전이. 출처: `/deep-research`(내장 워크플로 schema 즉사 회피 위해 plain-text fan-out 커스텀 워크플로 저작) — 설계 5각도 + 셀 기준 8각도(2025+ 공식표준/논문) 적대 검증.

---

## methodology-advisor

팀의 **현행 개발·회사·사업 프로세스를 먼저 진단**하고, frontend-harness `grill-me`를 **개발 방법론 선택**에 특화·확장한 다각도 문진 뒤, 내장 방법론 카탈로그 + 컨틴전시 프레임워크에 근거해 상황 적합 방법론을 **순위 shortlist + 1순위**로 제안하는 도메인 무관 인터랙티브 멀티 에이전트 하네스.

| 스킬 | 명령 | 설명 |
|------|------|------|
| Methodology Advisor | `/methodology-advisor` | 진입 오케스트레이터. Phase 0 현행 진단(**첫 행동=현행 진단**·발명 금지) → 1 다각도 문진(개발/회사/사업 3축·한 번에 한 질문·답변 분기·충돌 감지) → 2 방법론 매칭·제안(shortlist + 1순위 + additive 도입 로드맵) → 3 적대적 적합성 검증(은탄환·숨은 가정·안티패턴·정직성). 매 Phase 승인 게이트. |

**에이전트 4종(opus)** — `process-cartographer`(Phase 0 현행 진단·관측만) / `context-interviewer`(Phase 1 grill-me 3축 문진·충돌 감지) / `methodology-matcher`(Phase 2 매칭·제안·우열 금지·트레이드오프+안티패턴 필수) / `fit-critic`(Phase 3 반증·1순위 흔들면 재정렬).

**references** — `methodology-catalog.md`(14 방법론: Waterfall·Scrum·Kanban·Scrumban·XP·Lean·Crystal·FDD·DSDM·Shape Up·SAFe/LeSS/Nexus·Spotify(복제주의)·DevOps/DORA·Wagile, 각 원칙·의식·아티팩트·적합 조건·안티패턴) · `selection-frameworks.md`(Cynefin·Stacey·**Boehm-Turner home ground 5인자**·risk-based 5단계·컨틴전시 축→방법론 매핑) · `interview-axes.md`(개발/회사/사업 3축 질문뱅크·충돌 감지 쌍) · `research/README.md`(2024-2026 1차 조사, deep-research 24소스·75주장 적대 검증 → **70 confirmed / 5 refuted**, SOURCE-TIER).

> `methodology-advisor`는 **'사람 개발팀이 어떤 개발 방법론/프로세스로 일할지'를 현행 진단 → 다각도 문진 → 근거 기반 제안**한다. **내재화 원칙** — 첫 행동=현행 진단(발명 금지) · 매 Phase 승인 게이트 · **방법론 우열 단정 금지**(맥락 적합성으로만) · **은탄환/'N% 개선' 약속 금지**(수치는 SOURCE-TIER·출처와 함께 관찰값) · 모든 권고에 **트레이드오프+안티패턴 동반** · **제안만**(조직 변경 자동 실행 안 함·도입은 사람 결정) · additive-first · opt-in 저장 · 독립 동작. **REFUTED 교정** — DORA 2025 채택률 **90%**(95% 아님) · Boehm-Turner 위험기반 **5단계**(4단계 아님·Step3 하이브리드·Step5 재조정). **경계** — 기획문서(PRD)·스토리 작성(`product-spec-harness`) · 하네스 생성(`harness-generator`)·진단(`meta-harness`) · 상류 핸드오프 게이트 검수(`review-harness`) · 사람↔AI 에이전트 협업 설계(`human-agent-teaming`) · AI 에이전트 병렬화(`agent-orchestration`) · 코드 구현/리뷰/커밋(`frontend/backend/git-harness`)은 범위 밖. **frontend-harness `grill-me`와 구분** — grill-me는 계획/설계 정렬 일반 인터뷰, 이 하네스는 방법론 선택 특화(문진→카탈로그·컨틴전시 근거 제안). 근거 PRIMARY: Boehm&Turner IEEE 2003·Clarke&O'Connor 2012·Ahimbisibwe 2015·DORA 2024/2025.
