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
| Harness Generator | `/harness-generator` | 도메인 무관 하네스(에이전트팀 + 스킬 + 오케스트레이터) 자동 생성 — 7단계 메타 프로세스 (감사 → 도메인 분석 → 아키텍처 → 에이전트 정의 → 스킬 작성 → 오케스트레이션 → 검증/진화) |

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

> `meta-harness`는 "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1)를 토대로, **압축 요약이 아닌 full-trace experience store**(repo-wide 기본 `.claude/experience-store/`, plugin opt-in `plugins/{target}/experience-store/`)를 proposer가 직접 `grep`/`cat`으로 조회하는 것을 핵심으로 한다(논문 Table 3: full-trace가 요약 기반보다 우월). 4명의 에이전트(`trace-capturer`, `failure-diagnostician`, `pareto-refiner`, `experience-historian`)를 서브에이전트로 spawn한다(모두 `model: "opus"`). 모든 패치는 **사용자 승인 게이트** 후에만 적용한다.
