# frontend-harness

분석 → 설계 → 개발 → 리뷰 → 검증까지 프론트엔드 개발 전 과정을 지원하는 Claude Code 멀티 에이전트 플러그인입니다. 12개 스킬, 7개 커맨드, 5개 훅으로 구성됩니다.

## 설치

```bash
claude plugin add seungahhong/seungah-claude-plugins
```

설치 후 모든 스킬·커맨드를 슬래시 커맨드로 사용할 수 있습니다.

## 스킬

| Skill | Command | 설명 |
|-------|---------|------|
| Planner | `/planner` | 인터뷰 → 조사 → 계획 생성 → 승인 4단계 PRD 작성 |
| Architecture | `/architecture` | 시스템 구조, API, 데이터 흐름 설계 |
| Critic | `/critic` | 설계의 약점·리스크·누락 분석 |
| Grill Me | `/grill-me` | 요구사항 명확화를 위한 집요한 질문 |
| TDD | `/tdd` | Red-Green-Refactor 루프 기반 개발 |
| A11y | `/a11y` | WAI-ARIA 기반 웹접근성 점검/개선 |
| Semantic HTML | `/semantic-html` | 시맨틱 태그 사용 점검/개선 |
| SEO/GEO | `/seo-geo-optimizer` | 검색엔진 + AI 검색 최적화 |
| E2E Verifier | `/e2e-verifier` | Chrome / Playwright MCP / Agent-Browser 브라우저 검증 |
| Lighthouse Performance | `/lighthouse-performance` | Core Web Vitals(LCP·CLS·INP·TTFB·FCP) 측정 및 개선 |
| QA Inspector | `/qa-inspector` | API↔훅 타입·라우팅·상태 전이 교차 비교로 경계면 불일치 탐지 |
| Security Audit | `/security-audit` | OWASP Top 10 코드 분석, npm audit, 보안 헤더·시크릿 탐지 |

## 커맨드

| Command | 설명 |
|---------|------|
| `/orchestrator` | research → prd → develop → review → verify 6단계 순차 실행 후 통합 리포트 |
| `/research` | grill-me로 요구사항 분석·명세 도출 |
| `/prd` | planner → architecture → critic 루프로 PRD 작성 |
| `/frontend-guidelines` | a11y·semantic-html·seo-geo·tdd 병렬 실행 (가이드라인 기반 개발) |
| `/review` | 5개 관점(/simplify·/review·security-audit·lighthouse·qa-inspector) 중 선택 항목 병렬 + 재리뷰 루프 |
| `/verifier` | e2e-verifier로 PRD 인수 조건 기반 E2E 검증 |
| `/verify` | E2E 검증 + 타입/빌드 검사(`tsc --noEmit`, `npm run build`) 통합 |

## 사용법

### 1. 전체 자동화 — 오케스트레이터

가장 빠른 시작 방법입니다. 새 기능을 처음부터 끝까지 개발할 때 사용합니다.

```
/orchestrator
```

실행 순서:

```
Phase 1. Research   # 요구사항 분석 (grill-me)
Phase 2. PRD        # planner → architecture → critic 루프
Phase 3. Develop    # a11y + semantic-html + seo-geo + tdd 병렬
Phase 4. Review     # 5개 관점 중 선택 항목 병렬 → 수정·재리뷰 루프 (최대 3회)
Phase 5. Verify     # E2E 검증 + 타입/빌드 검사
Phase 6. 통합 리포트
```

정적 분석(Review)을 먼저 끝낸 뒤 비싼 E2E(Verify)를 실행합니다. 커밋은 이 플러그인 범위 밖이며, 커밋이 필요하면 별도 커밋 워크플로를 사용합니다.

### 2. 스킬 단위 실행

필요한 단계만 골라 직접 호출할 수 있습니다.

```
/grill-me            # 요구사항 명확화
/planner             # 구현 계획(PRD)
/architecture        # 기술 아키텍처 설계
/critic              # 설계 검증·리스크 분석
/tdd                 # 테스트 주도 구현
/a11y                # 웹접근성 점검
/semantic-html       # 시맨틱 HTML 점검
/seo-geo-optimizer   # SEO/GEO 최적화
/review              # 통합 리뷰 (선택 관점 병렬 + 재리뷰 루프)
/verify              # 동작·빌드 검증
```

### 3. 자연어 호출

슬래시 커맨드 대신 자연어로도 트리거됩니다. 예: "이 컴포넌트 접근성 점검해줘"(a11y), "보안 감사해줘"(security-audit), "성능 검사"(lighthouse-performance), "QA 정합성 확인"(qa-inspector).

## 훅 (자동 동작)

설치만으로 아래 훅이 자동 작동합니다.

| Hook | Trigger | 동작 |
|------|---------|------|
| guard | PreToolUse(Bash) | 위험 명령 차단 |
| write-guard | PreToolUse(Write) | 민감 파일 생성 차단 |
| skill-dedup | PreToolUse(Write `**/SKILL.md`) | 스킬 중복 방지 |
| stop-lint | PostToolUse(Edit/Write), Stop | git 변경 파일에 eslint → stylelint → prettier 자동 수정 (모노레포 지원, 도구 미설치 시 건너뜀) |
| package-changed | FileChanged(`package.json`) | 의존성 변경 알림 |

## 라이선스

MIT
