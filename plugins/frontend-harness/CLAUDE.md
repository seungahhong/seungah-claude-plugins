# frontend-harness

프론트엔드 개발 전 과정(Research → PRD → Develop → Review → Verify)을 지원하는 멀티 에이전트 스킬·커맨드·훅 플러그인(13 스킬 · 7 커맨드 · 6 훅). 사용자용 개요·사용법은 [README.md](README.md), 변경 이력은 [CHANGELOG.md](CHANGELOG.md), 커맨드·훅 한눈에 보기는 [`_docs/commands-and-hooks.md`](../../_docs/commands-and-hooks.md) 참조. 구성 목록은 `ls skills commands hooks`와 `hooks/hooks.json`이 정본이라 여기 적지 않는다.

## Conventions

- 각 스킬은 `skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description` 필수 + 필요 시 `allowed-tools`/`disable-model-invocation`만 추가 허용한다.
- 커맨드는 스킬을 직접 실행하지 않고 Agent 도구로 서브에이전트를 spawn한다(모든 spawn에 `model: "opus"` 명시).
- 스킬 간 교차 참조는 상대 경로(예: `../a11y/SKILL.md`)를 쓴다.
- 참고 자료는 `skills/<skill>/references/` 하위에 배치한다.
- Review 단계는 사용자가 선택한 관점만 단일 메시지에서 동시 spawn한다(병렬).
- 훅은 advisory·비차단이 기본이다. 차단하는 것은 `guard.sh`(PreToolUse Bash 위험 명령)·`write-guard.sh`(PreToolUse Write 민감 파일)·`skill-dedup.sh`(PreToolUse Write SKILL.md 중복)와 `incremental-lint.sh`의 잔여 lint 에러(exit 2)뿐이고, `stop-lint.sh`·`package-changed.sh`는 best-effort다. stdin 파서는 `lib.sh`(jq→python3 폴백, 부재 시 경고 후 통과) 공용.
- `commands/*.md`는 플러그인 루트가 아닌 **파일 기준** 상대 경로(`../skills/...`, `./x.md`)로 참조한다(2026-07-07 교정).
