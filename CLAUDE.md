# Frontend Guidelines - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인.

## Project Structure

```
.claude-plugin/                                          # 마켓플레이스 등록 메타데이터
  marketplace.json                                       # 리스팅 정보 (owner, metadata, plugins)
plugins/
  frontend-guidelines/                                   # 플러그인 루트
    .claude-plugin/
      plugin.json                                        # 플러그인 메타데이터 (이름, 버전, 키워드, 스킬/에이전트 경로)
    commands/                                            # 커스텀 커맨드 디렉토리
      orchestrator.md                                    # 전체 워크플로우 오케스트레이터 (research → prd → frontend-guidelines → verifier)
      research.md                                        # 요구사항 분석 (grill-me 서브에이전트 활용)
      prd.md                                             # PRD 작성 (planner → architecture → critic 서브에이전트 루프)
      frontend-guidelines.md                             # 프론트엔드 가이드라인 (a11y + semantic-html + seo-geo + tdd 서브에이전트)
      verifier.md                                        # E2E 브라우저 검증 (e2e-verifier 스킬 기반)
    hooks/                                               # 플러그인 훅 디렉토리
      hooks.json                                         # Stop 훅 설정 (lint 체인 자동 실행)
      stop-lint.sh                                       # eslint → stylelint → prettier 자동 수정 스크립트
    skills/                                              # 스킬 정의 디렉토리
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

## Skills

### Plugin: `frontend-guidelines`

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

### Plugin: `harness-generator`

| Skill | Command | Description |
|-------|---------|-------------|
| Harness Generator | `/harness-generator` | 도메인 무관 하네스(에이전트팀 + 스킬 + 오케스트레이터) 자동 생성 — 7단계 메타 프로세스 (감사 → 도메인 분석 → 아키텍처 → 에이전트 정의 → 스킬 작성 → 오케스트레이션 → 검증/진화) |

## Commands

| Command | File | Description |
|---------|------|-------------|
| Orchestrator | `/orchestrator` | research → prd → frontend-guidelines → verifier 순차 실행 후 통합 리포트 생성 |
| Research | `/research` | grill-me 스킬을 서브에이전트로 실행하여 요구사항 분석 및 명세 도출 |
| PRD | `/prd` | planner → architecture → critic 서브에이전트 루프로 개발 요구사항 정의서 작성 |
| Frontend Guidelines | `/frontend-guidelines` | a11y, semantic-html, seo-geo, tdd 스킬을 서브에이전트로 병렬 실행하여 가이드라인 제공 |
| Verifier | `/verifier` | e2e-verifier 스킬을 로드하여 PRD 인수 조건 기반 브라우저 검증 수행 |

## Hooks

| Hook | Trigger | Description |
|------|---------|-------------|
| stop-lint | `Stop` | Claude Code 응답 완료 시 git 변경 파일에 대해 eslint --fix → stylelint --fix → prettier --write 순으로 자동 수정 (모노레포 지원, 도구 미설치 시 건너뜀) |

## Conventions

- 마켓플레이스 등록은 `.claude-plugin/marketplace.json`의 `plugins` 배열에서 관리 (각 플러그인은 `source`/`version`/`tags`/`category` 명시)
- 각 플러그인은 `plugins/<plugin-name>/.claude-plugin/plugin.json`을 가지며 독립적으로 버전 관리
- 각 스킬은 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`에 정의 (frontmatter는 `name`/`description`만)
- 각 커맨드는 `plugins/<plugin-name>/commands/<command-name>.md`에 정의
- 커맨드에서 스킬 사용 시 Agent 도구로 서브에이전트를 spawn하여 실행
- 참고 자료는 `plugins/<plugin-name>/skills/<skill-name>/references/` 하위에 배치
- 훅 스크립트는 `plugins/<plugin-name>/hooks/` 하위에 배치하고 `hooks.json`에서 참조
- 스킬/커맨드 설명은 한국어로 작성
- 스킬 간 교차 참조 시 상대 경로 사용 (예: `../a11y/SKILL.md`)
- 메타/도메인 무관 스킬은 `frontend-guidelines`에 두지 않고 별도 플러그인으로 분리 (예: `harness-generator`)
