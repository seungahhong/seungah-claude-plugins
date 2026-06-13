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
