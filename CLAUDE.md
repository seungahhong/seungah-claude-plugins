# Frontend Harness - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스.

분석 → 설계 → 개발 → 리뷰 → 검증까지를 멀티 에이전트 스킬·커맨드·훅으로 묶고, 하네스 자체를 생성·개선하는 메타 플러그인을 포함한다.

## 플러그인 한눈에 보기

| Plugin | 역할 |
|--------|------|
| `frontend-harness` | 프론트엔드 개발 워크플로우 (계획·구현·품질·보안·성능·QA·검증·figma-extract 스킬 + 오케스트레이터 커맨드 + lint 훅) |
| `harness-generator` | 도메인 무관 하네스(에이전트팀+스킬+오케스트레이터) **수동·인터랙티브** 생성 메타 플러그인 |
| `git-harness` | Git 워크플로우 (한국어 커밋 메시지, 다각도 PR 리뷰) |
| `meta-harness` | full-trace experience store 기반 메타 하네스 엔지니어링 (causal 진단 + Pareto 비후퇴 패치, 사용자 승인 게이트) + self-heal 캡처 훅(UserPromptSubmit이 '수정/보강' 발화를 signals 레인에 원형 적재 → 추후 healer가 소비, 적용은 승인 게이트 후) |
| `product-spec-harness` | 기획자용 기획문서(PRD)+사용자스토리 5단계 인터랙티브 하네스 (기획안 인자 입력 → 카드 추출 → 생성 전 기획안 DoR 평가 내재화 → 보강점 반영 PRD·스토리 생성 → 적대적 검증; DoR 결과는 생성 후 opt-in으로 `product-spec-review.md` 저장) |
| `loop-engineering` | 검증 가능한 목표를 향한 자율 반복 루프(Goal→Execute→Verify→Diagnose→Improve) + 지속학습 메모리(Fail→Investigate→Verify→Distill→Consult) 멀티 에이전트 하네스 |
| `review-harness` | 코드 착수 *전* 상류 산출물(기획 DoR·디자인 핸드오프·API 계약·QA 인수조건) 핸드오프 게이트 검수 (4개 게이트 스킬 + handoff-review 오케스트레이터, 2025+ 근거·정직성 가드레일) |
| `ops-harness` | 프로덕션 운영·인시던트 대응·관측성 하네스 (AIOpsLab 4단계 탐지→국소화→RCA→완화 + 4개 에이전트, traces+logs+metrics 중재 읽기·휴먼-인-더-루프, RCA anti-anchoring 가드·Straight-Shot 폴백) |
| `backend-harness` | 백엔드/API 실행 기반 검증 구현 하네스 (설계→환경(1급)→구현→실행검증 5단계 + 4개 에이전트, 자기보고 불신·reward-hacking 가드 + 실행기반 test-generator 스킬) |
| `cicd-harness` | 코드 커밋→프로덕션 전달 파이프라인 하네스 (CI 파이프라인→IaC(terraform plan+OPA)→릴리스 결정(trust-tier)→전달 안정성(DORA 통제) 4단계 + 4개 에이전트, defense-in-depth·policy-as-code·사람 사전승인) |

## 세부 문서 (`_docs/`)

루트 `CLAUDE.md`는 100줄 이내 인덱스로 유지하고, 세부 내용은 아래 특징별 문서에 둔다. 작업 전 관련 문서를 먼저 참조할 것.

- [`_docs/project-structure.md`](_docs/project-structure.md) — 전체 디렉토리 구조와 각 파일/스킬 역할 트리
- [`_docs/skills.md`](_docs/skills.md) — 플러그인별 스킬 목록·커맨드·설명 (frontend-harness / harness-generator / git-harness / meta-harness / product-spec-harness / loop-engineering / review-harness / ops-harness / backend-harness / cicd-harness)
- [`_docs/commands-and-hooks.md`](_docs/commands-and-hooks.md) — frontend-harness 커맨드(orchestrator/research/prd/…/review) + Stop lint 훅
- [`_docs/conventions.md`](_docs/conventions.md) — 마켓플레이스 등록·플러그인/스킬/커맨드 배치·교차 참조·플러그인 분리 규칙

## 핵심 규칙 (전문은 `_docs/conventions.md`)

- 각 스킬은 `plugins/<plugin>/skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description`만 둔다.
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리한다.
- 4개 이상 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md`를 두고 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 스킬/커맨드 설명은 한국어로 작성하고, 스킬 간 교차 참조는 상대 경로를 사용한다.
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 늘어나는 내용은 `_docs/` 하위 특징별 .md로 분리해 참조한다.
