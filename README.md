# Dev Workflow Multi-Agent Skills

요구사항 분석 → 계획 → 설계 → 검증 → 구현 → E2E 검증 → 최적화까지, 소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스입니다.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`frontend-guidelines`](#plugin-frontend-guidelines) | 프론트엔드 개발 워크플로우용 멀티에이전트 스킬 모음 (Planning, Implementation, Quality, Verification) |
| [`harness-generator`](#plugin-harness-generator) | 도메인 무관 하네스(에이전트 팀 + 스킬 + 오케스트레이터) 자동 생성 메타 플러그인 |

---

## Plugin: `frontend-guidelines`

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

### Commands

스킬과 서브에이전트를 조합한 상위 레벨 커맨드입니다. 각 커맨드는 독립된 서브에이전트를 spawn하여 스킬별 작업을 분리 실행합니다.

| Command | Description |
|---------|-------------|
| **Orchestrator** (`/orchestrator`) | research → prd → frontend-guidelines → verifier 순차 실행 후 통합 리포트 생성. 새로운 프론트엔드 기능 개발 시 전체 워크플로우를 한 번에 실행합니다 |
| **Research** (`/research`) | grill-me 스킬을 서브에이전트로 활용하여 요구사항을 체계적으로 분석하고 명세를 도출합니다 |
| **PRD** (`/prd`) | planner → architecture → critic 각각을 서브에이전트로 spawn하여 계획 → 설계 → 비평 루프를 순환하며 PRD를 작성합니다 |
| **Frontend Guidelines** (`/frontend-guidelines`) | a11y, semantic-html, seo-geo, tdd 각 스킬을 서브에이전트로 병렬 spawn하여 프론트엔드 개발 가이드라인을 제공합니다 |
| **Verifier** (`/verifier`) | e2e-verifier 스킬을 로드하여 개발 완료 후 PRD 인수 조건 기반 브라우저 검증을 수행합니다 |

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

## Recommended Workflow

### 스킬 단위 실행

```
/grill-me          # 1. 요구사항 명확화
    ↓
/planner           # 2. 구현 계획 수립 (PRD)
    ↓
/architecture      # 3. 기술 아키텍처 설계
    ↓
/critic            # 4. 설계 검증 및 리스크 분석
    ↓
/tdd               # 5. 테스트 주도 구현
    ↓
/a11y              # 6. 웹접근성 점검
/semantic-html     #    시맨틱 HTML 점검
/seo-geo-optimizer #    SEO/GEO 최적화
    ↓
/e2e-verifier      # 7. 브라우저 기반 E2E 검증
```

### 오케스트레이터로 전체 자동화

```
/orchestrator      # 아래 전체 파이프라인을 자동 실행
```

```
Research 커맨드                  # 1. 요구사항 분석 (grill-me 활용)
    ↓
PRD 커맨드                       # 2. PRD 작성 (planner → architecture → critic 서브에이전트 루프)
    ↓
Frontend Guidelines 커맨드        # 3. 프론트엔드 개발 (a11y + semantic-html + seo-geo + tdd 병렬 서브에이전트)
    ↓
Verifier 커맨드                   # 4. E2E 브라우저 검증 (PRD 인수 조건 기반)
    ↓
타입/빌드 검사                    # 5. tsc --noEmit / npm run build
    ↓
통합 리포트 생성                  # 6. 전 단계 결과 통합
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
  frontend-guidelines/                                   # 플러그인 루트
    .claude-plugin/
      plugin.json                                        # 플러그인 메타데이터
    commands/
      orchestrator.md                                    # 전체 워크플로우 오케스트레이터
      research.md                                        # 요구사항 분석 커맨드
      prd.md                                             # PRD 작성 커맨드
      frontend-guidelines.md                             # 프론트엔드 가이드라인 커맨드
      verifier.md                                        # E2E 브라우저 검증 커맨드
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
  harness-generator/                                     # [독립 플러그인] 도메인 무관 하네스 자동 생성 메타 플러그인
    .claude-plugin/
      plugin.json
    skills/
      harness-generator/                                 # 하네스(에이전트팀+스킬+오케스트레이터) 자동 생성 메타 스킬 (+ references/)
```

## License

MIT
