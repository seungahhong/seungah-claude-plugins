# Dev Workflow Multi-Agent Skills

분석 → 설계 → 개발 → 리뷰 → 검증까지, 소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스입니다. 정적 분석 5개 관점(코드 간소화·PR 리뷰·보안·성능·통합 정합성)을 병렬로 돌리고 수정·재리뷰 루프로 마무리하는 6단계 오케스트레이터를 제공합니다.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`frontend-harness`](#plugin-frontend-harness) | 프론트엔드 개발 워크플로우용 멀티에이전트 스킬 모음 (Planning, Implementation, Quality, Security, Performance, QA, Verification) |
| [`harness-generator`](#plugin-harness-generator) | 도메인 무관 하네스(에이전트 팀 + 스킬 + 오케스트레이터) 자동 생성 메타 플러그인 |
| [`git-harness`](#plugin-git-harness) | Git 워크플로우 멀티 에이전트 스킬 모음 (한국어 커밋 메시지 작성, 다각도 PR 리뷰) |
| [`meta-harness`](#plugin-meta-harness) | Meta-Harness 논문(arXiv 2603.28052v1) 기반 메타 하네스 엔지니어링 플러그인 (full-trace experience store + causal reasoning + Pareto 비후퇴, 사용자 승인 게이트) |

---

## Plugin: `frontend-harness`

프론트엔드 개발 전 과정을 지원하는 스킬과 커맨드, 훅을 제공하는 플러그인입니다.

### Skills

#### Planning & Design

| Skill | Command | Description |
|-------|---------|-------------|
| **Planner** | `/planner` | 4단계 프로세스(인터뷰 → 조사 → 계획 생성 → 승인)를 통해 실행 가능한 PRD를 작성합니다 |
| **Architecture** | `/architecture` | 시스템 구조, API, 컴포넌트, 데이터 흐름, 기술 선택의 근거를 체계적으로 설계합니다 |
| **Critic** | `/critic` | 설계의 약점, 리스크, 누락 사항을 체계적으로 분석합니다. `/planner`나 `/architecture`와 함께 사용하면 효과적입니다 |
| **Grill Me** | `/grill-me` | 계획이나 설계에 대해 집요하게 질문하여 모호한 부분을 명확히 합니다 |

#### Implementation

| Skill | Command | Description |
|-------|---------|-------------|
| **TDD** | `/tdd` | Red-Green-Refactor 루프 기반 테스트 주도 개발을 지원합니다 |

#### Quality & Optimization

| Skill | Command | Description |
|-------|---------|-------------|
| **A11y** | `/a11y` | React/JSX 코드의 웹접근성(WAI-ARIA)을 점검하고 개선합니다 |
| **Semantic HTML** | `/semantic-html` | React/JSX 코드의 시맨틱 HTML 태그 사용을 점검하고 개선합니다 |
| **SEO/GEO Optimizer** | `/seo-geo-optimizer` | 전통적 검색엔진과 AI 검색엔진 모두에 대한 최적화를 수행합니다 |

#### Verification

| Skill | Command | Description |
|-------|---------|-------------|
| **E2E Verifier** | `/e2e-verifier` | Chrome MCP / Playwright MCP / Agent-Browser 중 선택한 도구로 PRD 인수 조건 기반 브라우저 검증을 수행합니다 |
| **Lighthouse Performance** | `/lighthouse-performance` | Lighthouse CLI로 Core Web Vitals(LCP, CLS, INP, TTFB, FCP)와 성능 점수를 측정하고 프레임워크별 개선 방안을 제시합니다 |
| **QA Inspector** | `/qa-inspector` | API 응답↔훅 타입, 파일 경로↔링크, 상태 전이 맵↔코드를 교차 비교하여 모듈 간 경계면 불일치를 탐지합니다 |

#### Security

| Skill | Command | Description |
|-------|---------|-------------|
| **Security Audit** | `/security-audit` | OWASP Top 10(A01/A03/A05/A07/A10) 코드 분석, `npm audit` 의존성 스캔, 보안 헤더·시크릿 탐지를 수행합니다 |

### Commands

스킬과 서브에이전트를 조합한 상위 레벨 커맨드입니다. 각 커맨드는 독립된 서브에이전트를 spawn하여 스킬별 작업을 분리 실행합니다.

| Command | Description |
|---------|-------------|
| **Orchestrator** (`/orchestrator`) | research → prd → develop → **review → verify** 6단계 순차 실행 후 통합 리포트 생성. Review 단계는 `/simplify` + `/review` + `security-audit` + `lighthouse-performance` + `qa-inspector` 5개 관점을 병렬 실행하고 수정·재리뷰 루프를 돌립니다. Verify 단계는 E2E + 타입/빌드 검사로 동작과 빌드 가능성을 확인합니다. 정적 검사를 먼저 끝내고 비싼 E2E를 마지막에 돌리는 순서입니다. 커밋은 별도로 `git-harness` 플러그인의 `/commit`을 사용합니다 |
| **Research** (`/research`) | grill-me 스킬을 서브에이전트로 활용하여 요구사항을 체계적으로 분석하고 명세를 도출합니다 |
| **PRD** (`/prd`) | planner → architecture → critic 각각을 서브에이전트로 spawn하여 계획 → 설계 → 비평 루프를 순환하며 PRD를 작성합니다 |
| **Frontend Guidelines** (`/frontend-guidelines`) | a11y, semantic-html, seo-geo, tdd 각 스킬을 서브에이전트로 병렬 spawn하여 프론트엔드 개발 가이드라인 기반 개발(Develop)을 수행합니다 |
| **Verifier** (`/verifier`) | e2e-verifier 스킬을 로드하여 개발 완료 후 PRD 인수 조건 기반 E2E 브라우저 검증을 수행합니다 |
| **Verify** (`/verify`) | E2E 브라우저 검증(`/verifier` 활용)과 타입/빌드 검사(`tsc --noEmit`, `npm run build`)를 통합 실행해 동작과 배포 가능한 산출물 생성 여부를 확인합니다 |
| **Review** (`/review`) | `/simplify`(간소화), 빌트인 `/review`(PR 리뷰), `security-audit`(보안), `lighthouse-performance`(성능), `qa-inspector`(통합 정합성) 5개 관점을 사용자에게 제시하고 **선택받은 항목만 병렬 서브에이전트로 동시 실행**한 뒤 통합 결과를 보고합니다(선택 항목 수에 관계없이 단일 메시지 동시 spawn). 수정 필요 항목은 사용자 승인 후 적용하고 재리뷰 루프를 돌려 모든 이슈가 해소될 때까지(최대 3라운드) 반복합니다. 커밋은 `git-harness` 플러그인의 `/commit`을 별도로 사용합니다 |

### Hooks

| Hook | Trigger | Description |
|------|---------|-------------|
| **stop-lint** | `Stop` | Claude Code 응답 완료 시 git 변경 파일에 대해 `eslint --fix` → `stylelint --fix` → `prettier --write`를 자동 실행합니다. 모노레포를 지원하며, 도구가 설치되지 않은 프로젝트는 건너뜁니다 |

---

## Plugin: `harness-generator`

특정 도메인에 종속되지 않는 멀티에이전트 하네스(에이전트 팀 + 스킬 + 오케스트레이터)를 자동으로 생성하는 메타 플러그인입니다. 새로운 도메인의 다단계 워크플로우(연구 → 설계 → 실행 → 검증)를 체계적으로 자동화하고 싶을 때 사용합니다.

### Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **Harness Generator** | `/harness-generator` | 7단계 메타 프로세스(감사 → 도메인 분석 → 아키텍처 → 에이전트 정의 → 스킬 작성 → 오케스트레이션 → 검증/진화)로 도메인용 하네스를 한 묶음으로 설계·생성합니다. 재실행, 보완, 기존 하네스 수정/감사에도 사용합니다 |

---

## Plugin: `git-harness`

Git 워크플로우를 지원하는 스킬 모음입니다. 한국어 커밋 메시지 작성과 다각도 PR 리뷰를 지원합니다.

### Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **Commit** | `/commit` | `이슈번호 type: 제목` 형식의 한국어 커밋 메시지를 작성합니다. 명령형 제목과 함께, 필요 시 요약/배경/설계/영향/테스트 시나리오 본문을 자동 구성합니다. Secrets 검사와 보호 브랜치 경고를 포함합니다 |
| **Review to PR** | `/review-to-pr` | 변경 파일 기반 **리뷰 → 커밋 → PR 생성** 올인원 워크플로우. Commit/PR 각 단계에서 `/simplify` + `/review`를 자동 수행하고 수정을 적용한 뒤 커밋 또는 PR을 생성합니다 |

---

## Plugin: `meta-harness`

하네스(루트 CLAUDE.md + SKILL.md + agents + commands + hooks = "LLM 주위의 코드")의 결함을 **압축 요약이 아닌 full-trace experience store**로 진단·개선하는 메타 하네스 엔지니어링 플러그인입니다. "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1)를 토대로, proposer가 raw trace를 직접 `grep`/`cat`으로 조회해 causal reasoning으로 root cause를 진단합니다. 모든 patch는 사용자 승인 게이트 통과 후에만 적용됩니다 (자동 적용 금지). `agents/` 정의 파일로 4명의 에이전트가 서브에이전트로 동작합니다 (모두 `model: "opus"`).

트리거는 세 가지입니다 — R1 현세션 redirect·보강, R2 plugin 자체 개선, R3 외부 .md 산출물의 생산 에이전트/skill 역추적.

### Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **Meta-Harness** | `/meta-harness` | 진입점 오케스트레이터. R1 현세션 redirect/보강 · R2 plugin 개선 · R3 외부 .md 역추적 트리거. Phase 0~8 + R4 보고, **사용자 승인 게이트(자동 적용 금지)** |
| **Session Signal Capture** | `/session-signal-capture` | R1 현세션 발화·직전 산출물·active skill + R3 외부 .md를 **요약 없이 원형 trace로** 캡처. R3는 산출물 출처를 3단 폴백(경로 규약 → 메타마커 → 구조·문체+git blame)으로 역추적 + confidence |
| **Causal Diagnosis** | `/causal-diagnosis` | experience-store raw trace를 grep/cat로 직접 조회해 confound 격리 → 단독검증 → why-first로 root cause 진단(근거는 trace step/경로 인용) |
| **Pareto Refinement** | `/pareto-refinement` | additive-first → compose(직교 승리만) → transfer로 4축(behavior-alignment·rule-body-cost·trigger-precision·generalization) Pareto **비후퇴** 패치 생성 (patch만, 자동 적용 금지) |

### Agents

| Agent | Description |
|-------|-------------|
| **trace-capturer** | 현세션 신호 + 외부 .md → 원형 trace 정규화 (요약 금지, R3 3단 폴백 출처 역추적) |
| **failure-diagnostician** | 결함 1건당 root cause 진단 (병렬, raw trace grep/cat 직접 조회, confound 격리) |
| **pareto-refiner** | additive-first → compose → transfer patch 생성 (자동 적용 금지) |
| **experience-historian** | experience-store 큐레이션 (history/index/pareto/recurring) |

### Experience Store

대상 스코프에 따라 `experience-store/` 디렉토리가 생성되어 회차 간 full-trace와 패턴이 누적됩니다 (repo-wide 기본 `.claude/experience-store/`, plugin opt-in `plugins/{target}/experience-store/`). proposer는 이 raw trace를 직접 조회합니다 (논문 Table 3: full-trace가 요약 기반보다 우월).

> `meta-harness`와 `harness-generator`의 책임 경계: 신규 하네스 구축은 `harness-generator`, 이미 사용 중인 하네스의 문제 진단·개선은 `meta-harness`. 단발 스킬 작성/평가는 마켓플레이스 공식 `skill-creator` 사용.

---

## Recommended Workflow

### 스킬 단위 실행

```
/grill-me                # 1. 요구사항 명확화
    ↓
/planner                 # 2. 구현 계획 수립 (PRD)
    ↓
/architecture            # 3. 기술 아키텍처 설계
    ↓
/critic                  # 4. 설계 검증 및 리스크 분석
    ↓
/tdd                     # 5. 테스트 주도 구현
    ↓
/a11y                    # 6. 웹접근성 점검
/semantic-html           #    시맨틱 HTML 점검
/seo-geo-optimizer       #    SEO/GEO 최적화
    ↓
/review                  # 7. 통합 리뷰 (5개 관점 중 사용자 선택 항목만 병렬 + 재리뷰 루프)
    ↓
/verify                  # 8. 동작·빌드 검증 (E2E + tsc + build)
    ↓
/commit (git-harness)    # 9. 커밋 메시지 작성
```

### 오케스트레이터로 전체 자동화

```
/orchestrator      # 아래 전체 파이프라인을 자동 실행
```

```
Phase 1. Research 커맨드                  # 요구사항 분석 (grill-me 활용)
    ↓
Phase 2. PRD 커맨드                       # PRD 작성 (planner → architecture → critic 서브에이전트 루프)
    ↓
Phase 3. Develop (Frontend Guidelines)    # 가이드라인 기반 개발 (a11y + semantic-html + seo-geo + tdd 병렬)
    ↓
Phase 4. Review (통합 리뷰)                # 5개 관점(/simplify, /review, security-audit, lighthouse, qa-inspector) 중 사용자 선택 항목만 병렬 → 수정·재리뷰 루프 (최대 3회)
    ↓
Phase 5. Verify                           # E2E 브라우저 검증 + 타입/빌드 검사
    ↓
Phase 6. 통합 리포트 생성                   # 전 단계 결과 통합

[후속 단계, 별도 호출]
/commit (git-harness)
```

### 메타 워크플로우 — 하네스 자체를 다루기

```
/harness-generator           # 0. 신규 도메인용 하네스(에이전트+스킬+오케스트레이터) 한 묶음 생성
    ↓ (사용 중 문제 발견 시)
/meta-harness                # N. 대상 하네스를 full-trace로 캡처·진단·개선 + experience-store/ 누적
                             #    동일 표적 반복 시 → /harness-generator 재실행 권고
```

## Installation

Claude Code에서 설치:

```bash
claude plugin add seungahhong/seungah-claude-plugins
```

설치 후 모든 스킬을 슬래시 커맨드(`/planner`, `/tdd` 등)로 사용할 수 있습니다.

## Project Structure

```
.claude-plugin/
  marketplace.json                                       # 마켓플레이스 리스팅 정보 (plugins 배열)
plugins/
  frontend-harness/                                      # 플러그인 루트
    .claude-plugin/
      plugin.json                                        # 플러그인 메타데이터
    commands/
      orchestrator.md                                    # 전체 워크플로우 오케스트레이터 (research → prd → develop → review → verify)
      research.md                                        # 요구사항 분석 커맨드
      prd.md                                             # PRD 작성 커맨드
      frontend-guidelines.md                             # Develop 단계 — 프론트엔드 가이드라인 커맨드
      review.md                                          # Review — /simplify + /review + security-audit + lighthouse + qa-inspector 5개 관점 병렬 + 재리뷰 루프
      verifier.md                                        # E2E 브라우저 검증 커맨드 (e2e-verifier 스킬 기반)
      verify.md                                          # Verify 통합 — E2E 브라우저 검증 + 타입/빌드 검사
    hooks/
      hooks.json                                         # Stop 훅 설정
      stop-lint.sh                                       # lint 체인 자동 수정 스크립트
    skills/
      planner/                                           # 계획 수립 (+ references/)
      architecture/                                      # 아키텍처 설계
      critic/                                            # 설계 검증
      grill-me/                                          # 인터뷰
      tdd/                                               # 테스트 주도 개발 (+ references/)
      a11y/                                              # 웹접근성 점검 (+ references/)
      semantic-html/                                     # 시맨틱 HTML 점검
      seo-geo-optimizer/                                 # SEO/GEO 최적화 (+ references/)
      e2e-verifier/                                      # E2E 브라우저 검증 (+ references/)
      lighthouse-performance/                            # Lighthouse Core Web Vitals 측정
      qa-inspector/                                      # 경계면 정합성 검증 (+ references/)
      security-audit/                                    # OWASP Top 10 보안 감사 (+ references/)
  harness-generator/                                     # [독립 플러그인] 도메인 무관 하네스 자동 생성 메타 플러그인
    .claude-plugin/
      plugin.json
    skills/
      harness-generator/                                 # 하네스(에이전트팀+스킬+오케스트레이터) 자동 생성 제너레이터 스킬 (+ references/)
  git-harness/                                           # [독립 플러그인] Git 워크플로우 멀티 에이전트 스킬 모음
    .claude-plugin/
      plugin.json
    skills/
      commit/                                            # 한국어 커밋 메시지 작성 스킬
      review-to-pr/                                      # 리뷰 → 커밋 → PR 생성 올인원 워크플로우 스킬
  meta-harness/                                          # [독립 플러그인] Meta-Harness 논문(arXiv 2603.28052v1) 기반 메타 하네스 엔지니어링 (full-trace experience store + causal reasoning + Pareto 비후퇴, 사용자 승인 게이트)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 변경 이력
    README.md                                            # 사용자용 개요
    agents/                                              # 모두 model: "opus"
      trace-capturer.md                                  # 현세션 신호 + 외부 .md → 원형 trace 정규화 (요약 금지)
      failure-diagnostician.md                           # 결함 1건당 root cause 진단 (병렬, raw trace 직접 조회)
      pareto-refiner.md                                  # additive-first → compose → transfer patch 생성 (자동 적용 금지)
      experience-historian.md                            # experience-store 큐레이션 (history/index/pareto/recurring)
    skills/
      meta-harness/                                      # 진입점 오케스트레이터 (Phase 0~8 + R4 보고) (+ references/)
      session-signal-capture/                            # R1/R3 신호 캡처 방법론 (원본 보존)
      causal-diagnosis/                                  # full-trace 기반 causal 진단 루브릭
      pareto-refinement/                                 # Pareto/additive patch 생성 방법론
    evals/                                               # acceptance assertion + 트리거 평가 + dry-run 리포트
```

## License

MIT
