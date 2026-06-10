# Frontend Harness - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스.

분석 → 설계 → 개발 → 리뷰 → 검증까지를 멀티 에이전트 스킬·커맨드·훅으로 묶고, 하네스 자체를 생성·개선하는 메타 플러그인을 포함한다.

## 플러그인 한눈에 보기

| Plugin | 역할 |
|--------|------|
| `frontend-harness` | 프론트엔드 개발 워크플로우 (계획·구현·품질·보안·성능·QA·검증 스킬 + 오케스트레이터 커맨드 + lint 훅) |
| `harness-generator` | 도메인 무관 하네스(에이전트팀+스킬+오케스트레이터) **수동·인터랙티브** 생성 메타 플러그인 |
| `generator-harness` | 도메인 무관 하네스 **자동 탐색·평가** 생성 (후보 N개 제안 → Pareto 채점 → 승인 → 실체화, 연구 근거) |
| `git-harness` | Git 워크플로우 (한국어 커밋 메시지, 다각도 PR 리뷰) |
| `meta-harness` | full-trace experience store 기반 메타 하네스 엔지니어링 (causal 진단 + Pareto 비후퇴 패치, 사용자 승인 게이트) |

## 세부 문서 (`_docs/`)

루트 `CLAUDE.md`는 100줄 이내 인덱스로 유지하고, 세부 내용은 아래 특징별 문서에 둔다. 작업 전 관련 문서를 먼저 참조할 것.

- [`_docs/project-structure.md`](_docs/project-structure.md) — 전체 디렉토리 구조와 각 파일/스킬 역할 트리
- [`_docs/skills.md`](_docs/skills.md) — 플러그인별 스킬 목록·커맨드·설명 (frontend-harness / harness-generator / generator-harness / git-harness / meta-harness)
- [`_docs/commands-and-hooks.md`](_docs/commands-and-hooks.md) — frontend-harness 커맨드(orchestrator/research/prd/…/review) + Stop lint 훅
- [`_docs/conventions.md`](_docs/conventions.md) — 마켓플레이스 등록·플러그인/스킬/커맨드 배치·교차 참조·플러그인 분리 규칙

## 핵심 규칙 (전문은 `_docs/conventions.md`)

- 각 스킬은 `plugins/<plugin>/skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description`만 둔다.
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리한다.
- 4개 이상 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md`를 두고 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 스킬/커맨드 설명은 한국어로 작성하고, 스킬 간 교차 참조는 상대 경로를 사용한다.
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 늘어나는 내용은 `_docs/` 하위 특징별 .md로 분리해 참조한다.
