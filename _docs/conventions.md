# Conventions

- 마켓플레이스 등록은 `.claude-plugin/marketplace.json`의 `plugins` 배열에서 관리 (각 플러그인은 `source`/`version`/`tags`/`category` 명시)
- 각 플러그인은 `plugins/<plugin-name>/.claude-plugin/plugin.json`을 가지며 독립적으로 버전 관리
- 각 스킬은 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`에 정의 (frontmatter는 `name`/`description` 필수 + 필요 시 `allowed-tools`(도구 최소권한 스코핑)·`disable-model-invocation`(자동 트리거 방지, 명시 호출 전용)만 추가 허용 — 그 외 키 금지)
- 각 커맨드는 `plugins/<plugin-name>/commands/<command-name>.md`에 정의
- 커맨드에서 스킬 사용 시 Agent 도구로 서브에이전트를 spawn하여 실행 (모든 spawn에 `model: "opus"` 명시)
- 참고 자료는 `plugins/<plugin-name>/skills/<skill-name>/references/` 하위에 배치
- 훅 스크립트는 `plugins/<plugin-name>/hooks/` 하위에 배치하고 `hooks.json`에서 참조
- 스킬/커맨드 설명은 한국어로 작성
- 스킬 간 교차 참조 시 파일 기준 상대 경로 사용 (예: `../a11y/SKILL.md`). 단 **커맨드 파일**은 플러그인 루트 기준 `./skills/...`·`./commands/...` 표기를 공인 스타일로 사용한다(frontend-harness·review-harness 커맨드 전반의 기존 일관 표기)
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리 (예: `harness-generator`, `git-harness`, `meta-harness`)
- 4개 이상의 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md` 정의 파일을 두고 모든 Agent 호출에 `model: "opus"` 명시. 예외: 커맨드가 *스킬*을 서브에이전트로 spawn하는 legacy 패턴(`frontend-harness` commands)은 `agents/` 정의 없이 허용하되, spawn 지시에 `model: "opus"`를 명시한다. 예외 2: 하네스 규칙이 결과에 새어 들면 안 되는 **의도적 무정의 호출**(예: `ux-ai-workflow-harness` Phase 3 경로 (b) — 사용자 채팅 AI 조건을 흉내 내 프롬프트 본문만 주는 초안 생성)은 `general-purpose`로 spawn하되 `model: "opus"`를 명시하고, 정의 파일을 두지 않는 이유를 SKILL.md에 적는다
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 세부 내용은 `_docs/` 하위 특징별 .md 파일로 분리해 참조
- 새 하네스(플러그인) 도입·트리거 표현 변경 시, 트리거가 인접한 자매 플러그인들의 `evals/trigger-eval.json`에도 상호(reciprocal) should-not 경계 케이스를 함께 갱신한다(양방향 오발동 가드). 예: `loop-engineering` ↔ `meta-harness`/`harness-generator`/`product-spec-harness`. 알려진 예외: `frontend-harness`·`git-harness`는 `evals/`가 아직 없어 역방향 가드가 없다(추가 시 이 규칙 적용) — 대신 해당 플러그인 스킬 본문의 "인접 하네스 역방향 배제 문구"로 보완한다
- 플러그인 `CLAUDE.md`는 소개 문단·README/SKILL.md/references 포인터·**핵심 불변식(Conventions)** 만 둔다. Structure 트리·Phase 요약 표처럼 `ls`나 SKILL.md가 이미 보여주는 내용은 적지 않고, 변경 이력은 `CHANGELOG.md`(표, 기존 행 순서 유지)에 쌓는다. 플러그인 루트 CLAUDE.md는 설치한 프로젝트에는 로드되지 않고 이 저장소에서 그 플러그인을 고칠 때만 로드되는 유지보수 문서다
- 스킬 `description`은 한 문장 정의 + 발동 문구(따옴표) + 범주로만 적은 비발동 경계로 300~600자 안에 쓰고, `: `·` #`가 없는 YAML 평문 스칼라로 둔다(strict 파서 호환). 절차·근거 서술은 본문에 둔다. 트리거 실측 기록이 있는 스킬(예: `aeo-harness`, CHANGELOG 참조)은 재측정 없이 description을 바꾸지 않는다. plugin.json `description`은 마켓플레이스 카드용 소개(~350자)로 두고 marketplace.json 항목과 같은 문구로 유지하며, `tags`는 plugin.json이 아니라 marketplace.json 항목에만 둔다
