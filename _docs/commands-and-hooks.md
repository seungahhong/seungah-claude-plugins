# Commands & Hooks

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
