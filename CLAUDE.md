# Frontend Harness - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인.

## Project Structure

```
.claude-plugin/                                          # 마켓플레이스 등록 메타데이터
  marketplace.json                                       # 리스팅 정보 (owner, metadata, plugins)
plugins/
  frontend-harness/                                      # 플러그인 루트
    .claude-plugin/
      plugin.json                                        # 플러그인 메타데이터 (이름, 버전, 키워드, 스킬/에이전트 경로)
    commands/                                            # 커스텀 커맨드 디렉토리
      orchestrator.md                                    # 전체 워크플로우 오케스트레이터 (research → prd → develop → review → verify)
      research.md                                        # 요구사항 분석 (grill-me 서브에이전트 활용)
      prd.md                                             # PRD 작성 (planner → architecture → critic 서브에이전트 루프)
      frontend-guidelines.md                             # Develop 단계 — 프론트엔드 가이드라인 (a11y + semantic-html + seo-geo + tdd 서브에이전트)
      review.md                                          # Review — /simplify + /review + security-audit + lighthouse + qa-inspector 5개 관점 병렬 + 재리뷰 루프
      verifier.md                                        # E2E 브라우저 검증 (e2e-verifier 스킬 기반)
      verify.md                                          # Verify 통합 — E2E 브라우저 검증 + 타입/빌드 검사
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
      lighthouse-performance/                            # Lighthouse 기반 Core Web Vitals 측정
      qa-inspector/                                      # 모듈 간 경계면 불일치 검증 (+ references/)
      security-audit/                                    # OWASP Top 10 보안 감사 (+ references/)
  harness-generator/                                     # [독립 플러그인] 도메인 무관 하네스 자동 생성 메타 플러그인
    .claude-plugin/
      plugin.json
    skills/
      harness-generator/                                 # 하네스(에이전트팀+스킬+오케스트레이터) 자동 생성 메타 스킬 (+ references/)
  git-harness/                                           # [독립 플러그인] Git 워크플로우 멀티 에이전트 스킬 모음
    .claude-plugin/
      plugin.json
    skills/
      commit/                                            # 한국어 커밋 메시지 작성 스킬 (`이슈번호 type: 제목` 형식)
      pr-review/                                         # PR 통합 리뷰 스킬 (코드 품질, 버그, 보안, 테스트, 코드 간소화)
  doc-harness/                                           # [독립 플러그인] 코드베이스+브랜치 기준 문서 자동 생성 하네스
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 변경 이력
    agents/                                              # 에이전트 정의 (서브에이전트 spawn 대상, model: opus)
      context-collector.md                               # git diff·브랜치 비교·코드 구조 수집
      doc-section-writer.md                              # 단일 섹션(배경/기술스펙/변경사항/테스트/영향) 작성, 병렬 호출
      doc-assembler.md                                   # 섹션 통합 + 요약·목차 생성
      doc-verifier.md                                    # 완성도 채점 (컨텍스트 격리, grading.json)
    skills/
      branch-doc-orchestrator/                           # 진입점 오케스트레이터 (수집→팬아웃→조립→검증 루프)
      branch-context-collection/                         # 브랜치 컨텍스트 수집 방법론
      doc-section-writing/                               # 섹션별 작성 방법론 (배경·기술스펙·변경사항·테스트·영향)
      doc-completeness-check/                             # 완성도 검증 루브릭 (+ references/)
```

## Skills

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
| PR Review | `/pr-review` | PR 통합 리뷰 — 코드 품질, 버그, 보안, 테스트, 코드 간소화(`/simplify`)를 다각도로 점검하고 `[must]`/`[want]`/`[imo]`/`[ask]`/`[nits]`/`[info]` 라벨 코멘트 생성 |

### Plugin: `doc-harness`

| Skill | Command | Description |
|-------|---------|-------------|
| Branch Doc Orchestrator | `/branch-doc-orchestrator` | 코드베이스 + 브랜치(git diff) 기준 문서 자동 생성 진입점. 수집 → 섹션 분석(배경·기술스펙·변경사항·테스트·영향) 병렬 → 조립 → 완성도 검증 루프(최대 2회). 산출: `_docs/branch-doc-{branch}-{date}.md` + 완성도 요약 |
| Branch Context Collection | `/branch-context-collection` | 현재 브랜치 ↔ 기본 브랜치 자동 감지 + git diff·커밋·코드 구조·테스트 현황을 단일 컨텍스트(`context.md` + `meta.json`)로 수집 |
| Doc Section Writing | `/doc-section-writing` | 수집 컨텍스트 기반으로 개별 섹션(배경/기술스펙/변경사항/테스트/영향) 작성 방법론 — 섹션별 필수 요소·형식·흔한 실패 정의 |
| Doc Completeness Check | `/doc-completeness-check` | 생성 문서를 필수 목차·충실도·정합성 루브릭으로 채점, `grading.json`(`verdict: pass/revise`) 산출 |

> `doc-harness`는 에이전트 정의 파일(`agents/`)을 사용하는 첫 플러그인이다 — `context-collector`, `doc-section-writer`, `doc-assembler`, `doc-verifier`를 서브에이전트로 spawn한다(모두 `model: "opus"`).

## Commands

| Command | File | Description |
|---------|------|-------------|
| Orchestrator | `/orchestrator` | research → prd → develop → **review → verify** 6단계 순차 실행 후 통합 리포트 생성. Review는 /simplify + /review + security-audit + lighthouse + qa-inspector 5개 관점 중 사용자 선택 항목만 병렬 + 재리뷰 루프. Verify는 E2E + 타입/빌드. 정적 분석을 먼저 끝낸 뒤 비싼 E2E를 실행. 커밋은 git-harness로 별도 진행 |
| Research | `/research` | grill-me 스킬을 서브에이전트로 실행하여 요구사항 분석 및 명세 도출 |
| PRD | `/prd` | planner → architecture → critic 서브에이전트 루프로 개발 요구사항 정의서 작성 |
| Frontend Guidelines | `/frontend-guidelines` | a11y, semantic-html, seo-geo, tdd 스킬을 서브에이전트로 병렬 실행하여 가이드라인 기반 개발(Develop) 진행 |
| Verifier | `/verifier` | e2e-verifier 스킬을 로드하여 PRD 인수 조건 기반 E2E 브라우저 검증 수행 |
| Verify | `/verify` | E2E 브라우저 검증(verifier.md 활용) + 타입/빌드 검사(`tsc --noEmit`, `npm run build`)를 통합 실행 |
| Review | `/review` | /simplify(간소화) + 빌트인 /review(PR 리뷰) + security-audit(보안) + lighthouse-performance(성능) + qa-inspector(정합성) 5개 관점 중 **사용자가 선택한 항목만 병렬 spawn**(단일 메시지 동시 실행) → 통합 결과 통보 → 수정 적용 → 재리뷰 루프(최대 3회). 커밋은 git-harness `/commit` |

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
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리 (예: `harness-generator`, `git-harness`)
