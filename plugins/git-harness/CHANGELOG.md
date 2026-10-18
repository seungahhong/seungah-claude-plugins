# git-harness 변경 이력

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-03 | 플러그인 CLAUDE.md/README.md 신설 | 플러그인 단위 문서·사용법 분리 |
| 2026-08-02 | `commit`·`review-to-pr` 삭제, `commit-pr` 단일 스킬로 통합 (v0.3.0) | 커밋~PR은 한 줄기 작업인데 스킬이 쪼개져 매번 다음 스킬을 다시 불러야 했다. 상태 기반 진입점 추천 + 진입점 승인 원칙 + 커밋 차단 게이트를 도입 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.3.1. (1) 스킬 description 유지(`commit-pr` 489자) — 이미 600자 이하. (2) plugin.json description 유지(208자), marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 1,734자 → 1,098자 — `Structure` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. (4) allowed-tools를 본문이 실제로 쓰는 명령으로 한정: `skills/commit-pr/SKILL.md` → `Bash(git status:*), Bash(git branch:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(gh pr:*), Bash(gh auth:*), Bash(which:*), Read, Grep, Glob, Agent, Skill`. 트리거 평가 재실행은 미수행 |
