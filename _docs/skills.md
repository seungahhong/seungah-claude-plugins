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

> `meta-harness`는 "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1)를 토대로, **압축 요약이 아닌 full-trace experience store**(repo-wide 기본 `.claude/experience-store/`, plugin opt-in `.claude/plugin-store/{target}/`)를 proposer가 직접 `grep`/`cat`으로 조회하는 것을 핵심으로 한다(논문 Table 3: full-trace가 요약 기반보다 우월). 4명의 에이전트(`trace-capturer`, `failure-diagnostician`, `pareto-refiner`, `experience-historian`)를 서브에이전트로 spawn한다(모두 `model: "opus"`). 모든 패치는 **사용자 승인 게이트** 후에만 적용한다. 추가로 **self-heal 캡처 훅(`UserPromptSubmit`)** 이 사용자의 '수정/보강/방향전환' 발화를 세션 중 `signals/*.jsonl`에 원형 적재하고(캡처 전용·비차단·요약 금지), 추후 회차의 healer가 Phase 1 warm-start로 누적 신호를 끌어와 진단·패치에 쓴다(적용은 승인 게이트 후).

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
