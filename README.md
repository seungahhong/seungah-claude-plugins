# Dev Workflow Multi-Agent Skills

분석 → 설계 → 개발 → 리뷰 → 검증까지, 소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스입니다. 정적 분석 5개 관점(코드 간소화·PR 리뷰·보안·성능·통합 정합성)을 병렬로 돌리고 수정·재리뷰 루프로 마무리하는 6단계 오케스트레이터를 제공합니다.

## Plugins

| Plugin | Description |
|--------|-------------|
| [`frontend-harness`](#plugin-frontend-harness) | 프론트엔드 개발 워크플로우용 멀티에이전트 스킬 모음 (Planning, Implementation, Quality, Security, Performance, QA, Verification) |
| [`harness-generator`](#plugin-harness-generator) | 도메인 무관 하네스(에이전트 팀 + 스킬 + 오케스트레이터) 자동 생성 메타 플러그인 |
| [`git-harness`](#plugin-git-harness) | Git 워크플로우 멀티 에이전트 스킬 모음 (한국어 커밋 메시지 작성, 다각도 PR 리뷰) |
| [`doc-harness`](#plugin-doc-harness) | 코드베이스 + 브랜치(git diff) 기준 기술 문서 자동 생성 하네스 (수집 → 섹션 분석 병렬 → 조립 → 완성도 검증 루프) |
| [`harness-evolver`](#plugin-harness-evolver) | 사용자가 사용 중인 임의의 하네스 스킬에서 보고된 문제를 진단·개선하는 메타-개선 플러그인 (Evolver 루프 + skill-creator eval iteration 결합) |

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
| **PR Review** | `/pr-review` | 변경된 코드를 코드 품질·버그·보안·테스트·코드 간소화(`/simplify`) 관점으로 다각도 리뷰하고 통합 리포트를 생성합니다. 신뢰도 80 이상 이슈만 보고하며, `[must]`/`[want]`/`[imo]`/`[ask]`/`[nits]`/`[info]` 라벨로 분류된 리뷰 코멘트를 만듭니다 |

---

## Plugin: `doc-harness`

코드베이스와 현재 브랜치(git diff)를 기준으로 배경·목차·기술스펙·변경사항·테스트·영향을 포함한 단일 기술 문서를 자동 생성하고 완성도를 검증하는 하네스입니다. `agents/` 정의 파일을 사용하는 첫 플러그인으로, 4명의 에이전트가 서브에이전트로 동작합니다 (모두 `model: "opus"`).

### Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **Branch Doc Orchestrator** | `/branch-doc-orchestrator` | 진입점 오케스트레이터. 수집 → 섹션 분석(배경·기술스펙·변경사항·테스트·영향) 병렬 → 조립 → 완성도 검증 루프(최대 2회). 산출: `_docs/branch-doc-{branch}-{date}.md` + 완성도 요약 |
| **Branch Context Collection** | `/branch-context-collection` | 현재 브랜치 ↔ 기본 브랜치 자동 감지 + git diff·커밋·코드 구조·테스트 현황을 단일 컨텍스트(`context.md` + `meta.json`)로 수집 |
| **Doc Section Writing** | `/doc-section-writing` | 수집 컨텍스트 기반 개별 섹션(배경/기술스펙/변경사항/테스트/영향) 작성 방법론 — 섹션별 필수 요소·형식·흔한 실패 정의 |
| **Doc Completeness Check** | `/doc-completeness-check` | 생성 문서를 필수 목차·충실도·정합성 루브릭으로 채점하고 `grading.json`(`verdict: pass/revise`) 산출 |

### Agents

| Agent | Description |
|-------|-------------|
| **context-collector** | git diff·브랜치 비교·코드 구조 수집 |
| **doc-section-writer** | 단일 섹션 작성 (병렬 호출 대상) |
| **doc-assembler** | 섹션 통합 + 요약/목차 생성 |
| **doc-verifier** | 완성도 채점 (컨텍스트 격리, `grading.json`) |

---

## Plugin: `harness-evolver`

사용자가 사용 중인 **임의의 하네스 스킬**에서 트리거 누락·반복 우회·에이전트 실패 등 문제가 보고되면, 대상 하네스를 진단하고 자율 개선하는 메타-개선 플러그인입니다. **특정 플러그인이나 도메인에 종속되지 않으며**, 사용자가 지목한 어떤 하네스든 입력으로 받습니다.

설계는 Evolver 루프(`trajectory → curated memory → autonomous skill refinement`)와 skill-creator의 eval-driven iteration을 결합한 형태이며, **결함 1건 = 진단 1건 = 패치 1건** 단위로 분리해 추적합니다. 모든 patch는 사용자 승인 게이트 통과 후에만 적용됩니다 (자동 적용 금지).

### Skills

| Skill | Command | Description |
|-------|---------|-------------|
| **Harness Evolver** | `/harness-evolver` | 진입점 오케스트레이터. 캡처 → 결함별 병렬 진단 → 진단별 순차 개선(patch + 트리거/회귀 평가) → 사용자 게이트 → 적용 → `evolution-memory/` 누적. 같은 표적 3회 누적 시 본문 patch 거절 + 구조 재설계(`harness-generator`) 권고 |
| **Trajectory Capture** | `/trajectory-capture` | 하네스 실행의 도구 호출·산출물·상태를 시간순 정규화(`*.jsonl` + 표). 사실/해석 분리, payload 적재 금지 |
| **Failure Diagnosis** | `/failure-diagnosis` | 결함의 root cause 진단 루브릭 — 5신호(재요청/반복 우회/에이전트 실패/스키마 불일치/Why 부재) → 5표적(description/skill body/agent/orchestrator/skill body 재작성) 매핑, 증거 인용 + severity/confidence |
| **Eval-Driven Refinement** | `/eval-driven-refinement` | skill-creator 4원칙(generalize/lean/why-first/bundle) 기반 patch 생성. description 수정 시 should-trigger/should-not-trigger 8–10개씩 동봉, Risks 필수, 자동 적용 금지 |

### Agents

| Agent | Description |
|-------|-------------|
| **trajectory-analyst** | 실행 궤적 정규화 (사실/해석 분리, payload 적재 금지) |
| **failure-diagnostician** | 결함 1건당 root cause 진단 (5신호 → 5표적 매핑, 증거 인용 필수) |
| **skill-refiner** | skill-creator 원칙 기반 patch 생성 (직접 파일 수정 금지, patch 안만 생성) |
| **evolution-historian** | `evolution-memory/` 큐레이션 + 반복 패턴 nudge (임계치 3회 시 구조 재설계 신호) |

### 진화 영속 메모리

대상 하네스의 플러그인 루트에 `evolution-memory/` 디렉토리가 생성되어 회차 간 패턴이 누적됩니다:

- `history.jsonl` — 회차별 진단/패치/결정 ledger
- `recurring-patterns.md` — 표적별 카운트 + `needs_attention` 섹션
- `patches/{date}-{target-slug}.md` — 적용된 패치 사본

> `harness-evolver`와 `harness-generator`의 책임 경계: 신규 하네스 구축은 `harness-generator`, 이미 사용 중인 하네스의 문제 개선은 `harness-evolver`. 단발 스킬 작성/평가는 마켓플레이스 공식 `skill-creator` 사용.

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
/branch-doc-orchestrator (doc-harness)    # 브랜치 기준 기술 문서 자동 생성
```

### 메타 워크플로우 — 하네스 자체를 다루기

```
/harness-generator           # 0. 신규 도메인용 하네스(에이전트+스킬+오케스트레이터) 한 묶음 생성
    ↓ (사용 중 문제 발견 시)
/harness-evolver             # N. 대상 하네스를 캡처·진단·개선 + evolution-memory/ 누적
                             #    동일 표적 3회 누적 시 → /harness-generator 재실행 권고
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
      pr-review/                                         # PR 통합 리뷰 스킬 (코드/버그/보안/테스트/간소화)
  doc-harness/                                           # [독립 플러그인] 코드베이스+브랜치 기준 문서 자동 생성 하네스
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 변경 이력
    agents/
      context-collector.md                               # git diff·브랜치 비교·코드 구조 수집
      doc-section-writer.md                              # 단일 섹션 작성 (병렬 호출)
      doc-assembler.md                                   # 섹션 통합 + 요약·목차 생성
      doc-verifier.md                                    # 완성도 채점 (컨텍스트 격리, grading.json)
    skills/
      branch-doc-orchestrator/                           # 진입점 오케스트레이터 (수집→팬아웃→조립→검증 루프)
      branch-context-collection/                         # 브랜치 컨텍스트 수집 방법론
      doc-section-writing/                               # 섹션별 작성 방법론
      doc-completeness-check/                             # 완성도 검증 루브릭 (+ references/)
  harness-evolver/                                       # [독립 플러그인] 사용자가 사용 중인 임의의 하네스 스킬에서 보고된 문제를 진단·개선하는 메타-개선 플러그인 (특정 플러그인/도메인 비종속)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 변경 이력
    agents/
      trajectory-analyst.md                              # 실행 궤적 정규화 (사실/해석 분리)
      failure-diagnostician.md                           # 결함 1건당 root cause 진단 (5신호 → 5표적)
      skill-refiner.md                                   # skill-creator 원칙 기반 patch 생성 (자동 적용 금지)
      evolution-historian.md                             # evolution-memory/ 큐레이션 + 반복 패턴 nudge
    skills/
      harness-evolver/                                   # 진입점 오케스트레이터 (캡처→팬아웃 진단→순차 개선→게이트→적용→메모리) (+ references/)
      trajectory-capture/                                # 궤적 정규화 방법론
      failure-diagnosis/                                 # 결함 진단 루브릭
      eval-driven-refinement/                            # patch + 트리거/회귀 평가 생성 방법론
```

## License

MIT
