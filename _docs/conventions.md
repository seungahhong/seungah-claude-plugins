# Conventions

- 마켓플레이스 등록은 `.claude-plugin/marketplace.json`의 `plugins` 배열에서 관리 (각 플러그인은 `source`/`version`/`tags`/`category` 명시)
- 각 플러그인은 `plugins/<plugin-name>/.claude-plugin/plugin.json`을 가지며 독립적으로 버전 관리
- 각 스킬은 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`에 정의 (frontmatter는 `name`/`description`만)
- 각 커맨드는 `plugins/<plugin-name>/commands/<command-name>.md`에 정의
- 커맨드에서 스킬 사용 시 Agent 도구로 서브에이전트를 spawn하여 실행
- 참고 자료는 `plugins/<plugin-name>/skills/<skill-name>/references/` 하위에 배치
- 훅 스크립트는 `plugins/<plugin-name>/hooks/` 하위에 배치하고 `hooks.json`에서 참조
- 스킬/커맨드 설명은 한국어로 작성
- 스킬 간 교차 참조 시 상대 경로 사용 (예: `../a11y/SKILL.md`)
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리 (예: `harness-generator`, `git-harness`, `meta-harness`)
- 4개 이상의 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md` 정의 파일을 두고 모든 Agent 호출에 `model: "opus"` 명시
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 세부 내용은 `_docs/` 하위 특징별 .md 파일로 분리해 참조
