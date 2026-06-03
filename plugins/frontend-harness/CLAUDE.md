# frontend-harness

프론트엔드 개발 전 과정(Research → PRD → Develop → Review → Verify)을 지원하는 멀티 에이전트 스킬·커맨드·훅 플러그인. 사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
.claude-plugin/plugin.json     # 플러그인 메타데이터
commands/                      # 상위 워크플로우 커맨드 (스킬을 서브에이전트로 spawn)
  orchestrator.md              # research → prd → develop → review → verify 6단계
  research.md prd.md frontend-guidelines.md review.md verifier.md verify.md
hooks/                         # PreToolUse·PostToolUse·Stop·FileChanged 훅
  hooks.json                   # 훅 설정
  guard.sh write-guard.sh skill-dedup.sh stop-lint.sh package-changed.sh
skills/                        # 12개 스킬 (각 SKILL.md, 일부 + references/)
  planner architecture critic grill-me tdd
  a11y semantic-html seo-geo-optimizer
  e2e-verifier lighthouse-performance qa-inspector security-audit
```

## Conventions

- 각 스킬은 `skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description`만 둔다.
- 커맨드는 스킬을 직접 실행하지 않고 Agent 도구로 서브에이전트를 spawn한다.
- 스킬 간 교차 참조는 상대 경로(예: `../a11y/SKILL.md`)를 쓴다.
- 참고 자료는 `skills/<skill>/references/` 하위에 배치한다.
- Review 단계는 사용자가 선택한 관점만 단일 메시지에서 동시 spawn한다(병렬).

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-03 | 플러그인 CLAUDE.md/README.md 신설 | 플러그인 단위 문서·사용법 분리 |
