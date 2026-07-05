# Commands & Hooks

## Commands

| Command | File | Description |
|---------|------|-------------|
| Orchestrator | `/orchestrator` | research → prd → develop → **review → verify** 6단계 순차 실행 후 통합 리포트 생성. Review는 /simplify + /review + security-audit + lighthouse + qa-inspector 5개 관점 중 사용자 선택 항목만 병렬 + 재리뷰 루프. Verify는 **인수조건(AC) 단위 E2E** + 타입/빌드이며, **인수조건 충족률<100%면 Develop→Review→Verify 수렴 루프**(미충족 AC만 재구현, 매 라운드 사용자 게이트·소프트 캡 5회). 정적 분석을 먼저 끝낸 뒤 비싼 E2E를 실행. 커밋은 git-harness로 별도 진행 |
| Research | `/research` | grill-me 스킬을 서브에이전트로 실행하여 요구사항 분석 및 명세 도출 |
| PRD | `/prd` | planner → architecture → critic 서브에이전트 루프로 개발 요구사항 정의서 작성. 각 기능(FR)을 **사용자 스토리(US)+관찰형 인수조건(AC-n.m, Given/When/Then)**으로 전개하고 FR↔US↔AC 추적(개발·검증 공통 계약, product-spec 방법론 내재화) |
| Frontend Guidelines | `/frontend-guidelines` | a11y·semantic-html·seo-geo·tdd 스킬로 가이드라인 기반 개발(Develop). **TDD 선택 시 TDD 선행(AC를 RED 테스트로)→나머지 병렬**, 미선택 시 전체 병렬. 최종 점검은 **기능(FR/US) 단위 인수조건 충족**. 수렴 루프 재호출 시 미충족 AC만 재구현 |
| Verifier | `/verifier` | e2e-verifier 스킬을 로드하여 PRD **인수조건(AC) 단위** E2E 브라우저 검증 수행(AC별 PASS/FAIL·충족률) |
| Verify | `/verify` | **인수조건 단위 E2E**(verifier.md 활용) + 타입/빌드 검사(`tsc --noEmit`, `npm run build`) 통합 실행. 인수조건 충족률<100%면 Develop 회귀 수렴 루프로 안내 |
| Review | `/review` | /simplify(간소화) + 빌트인 /review(PR 리뷰) + security-audit(보안) + lighthouse-performance(성능) + qa-inspector(정합성) 5개 관점 중 **사용자가 선택한 항목만 병렬 spawn**(단일 메시지 동시 실행) → 통합 결과 통보 → 수정 적용 → 재리뷰 루프(최대 3회). 커밋은 git-harness `/commit` |

## Hooks

| Hook | Trigger | Description |
|------|---------|-------------|
| guard (frontend-harness) | `PreToolUse` (Bash) | 위험 명령 차단 — `git add .`/`-A`/`./`, force push, `--no-verify`, stash drop/clear, publish, 루트/홈 삭제(`rm -rf /`·`/*`·`~/`, 분리형 플래그 포함), DROP TABLE, `reset --hard`, `checkout/restore .`. regex 기반 advisory 가드(보안 경계 아님), 파서(jq→python3) 부재 시 stderr 경고 후 통과 |
| write-guard (frontend-harness) | `PreToolUse` (Write) | 민감 파일 생성 차단 — `.env*`, 인증서/키(`*.pem` 등), 자격증명 json. Write 도구만 가드(advisory) |
| skill-dedup (frontend-harness) | `PreToolUse` (Write) | 새 `SKILL.md` 생성 시 같은 이름의 스킬이 이미 존재하면 차단 |
| stop-lint (frontend-harness) | `PostToolUse` (Edit\|Write) + `Stop` | lint 체인(eslint --fix → stylelint --fix → prettier --write). PostToolUse는 방금 수정된 파일 1개만, Stop은 git 변경 파일 전체 (모노레포 지원, 도구 미설치 시 건너뜀, 신뢰 저장소 전제 — 가장 가까운 node_modules/.bin 자동 실행) |
| package-changed (frontend-harness) | `PostToolUse` (Edit\|Write) | 수정된 파일이 `package.json`이면 의존성 추가/제거를 요약해 알림 (advisory) |
| self-heal-capture (meta-harness) | `UserPromptSubmit` | 사용자의 '수정/고쳐/다시/틀렸/보강/방향 다시'(+ 영어) 발화를 감지해 `.claude/experience-store/signals/<날짜>.jsonl`에 발화 **원형 적재**(요약 금지·캡처 전용·항상 exit 0). 추후 `/meta-harness`(healer)가 누적 신호를 진단·패치에 사용(적용은 승인 게이트 후). 비매칭 프롬프트는 무시. 트리거 문구는 env `SELF_HEAL_PATTERNS`로 교체 가능 |
| warm-start-nudge (meta-harness) | `SessionStart` | 최근 7일 내 미소비 self-heal 신호가 있으면 세션 시작 시 건수를 표면화해 `/meta-harness` 실행을 넛지(비차단·읽기 전용) |
