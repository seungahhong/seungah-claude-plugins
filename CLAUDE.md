# Frontend Harness - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스.

분석 → 설계 → 개발 → 리뷰 → 검증까지를 멀티 에이전트 스킬·커맨드·훅으로 묶고, 하네스 자체를 생성·개선하는 메타 플러그인을 포함한다.

## 플러그인 한눈에 보기

| Plugin | 역할 |
|--------|------|
| `frontend-harness` | 프론트엔드 개발 워크플로우 (계획·구현·품질·보안·성능·QA·검증·figma-extract 스킬 + 오케스트레이터 커맨드 + lint 훅) |
| `harness-generator` | 도메인 무관 하네스(에이전트팀+스킬+오케스트레이터) **수동·인터랙티브** 생성 메타 플러그인 |
| `git-harness` | Git 워크플로우 (한국어 커밋 메시지, 다각도 PR 리뷰) |
| `meta-harness` | full-trace experience store 기반 메타 하네스 엔지니어링 (causal 진단 + Pareto 비후퇴 패치, 사용자 승인 게이트) + self-heal 캡처 훅(UserPromptSubmit이 '수정/보강' 발화를 signals 레인에 원형 적재 → 추후 healer가 소비, 적용은 승인 게이트 후). 데이터 적재·지침 보강은 자족 reference의 데이터 적재 기준(C1~C9) + CLAUDE.md/Skill/hook/rule 메커니즘 선택을 따른다 |
| `product-spec-harness` | 기획자용 기획문서(PRD)+사용자스토리 5단계 인터랙티브 하네스 (기획안 인자 입력 → 카드 추출 → 생성 전 기획 완성도 점검(DoR) 내재화 → 보강점 반영 PRD·스토리 생성 → 적대적 검증; 기획 완성도 점검·적대적 검증 결과는 생성 후 opt-in으로 `.claude/_docs/<슬러그>/`에 저장, 기획자용 용어 순화) |
| `loop-engineering` | 검증 가능한 목표를 향한 자율 반복 루프(Goal→Execute→Verify→Diagnose→Improve) + 지속학습 메모리(Fail→Investigate→Verify→Distill→Consult) 멀티 에이전트 하네스 |
| `review-harness` | 코드 착수 *전* 상류 산출물(기획 DoR·디자인 핸드오프·API 계약·QA 인수조건) 핸드오프 게이트 검수 (4개 게이트 스킬 + handoff-review 오케스트레이터, 2025+ 근거·정직성 가드레일) |
| `ops-harness` | 프로덕션 운영·인시던트 대응·관측성 하네스 (AIOpsLab 4단계 탐지→국소화→RCA→완화 + 4개 에이전트, traces+logs+metrics 중재 읽기·휴먼-인-더-루프, RCA anti-anchoring 가드·Straight-Shot 폴백) |
| `backend-harness` | 백엔드/API 실행 기반 검증 구현 하네스 (설계→환경(1급)→구현→실행검증 5단계 + 4개 에이전트, 자기보고 불신·reward-hacking 가드 + 실행기반 test-generator 스킬) |
| `cicd-harness` | 코드 커밋→프로덕션 전달 파이프라인 하네스 (CI 파이프라인→IaC(terraform plan+OPA)→릴리스 결정(trust-tier)→전달 안정성(DORA 통제) 4단계 + 4개 에이전트, defense-in-depth·policy-as-code·사람 사전승인) |
| `context-engineering` | LLM·에이전트에 넣을 컨텍스트 페이로드를 체계적으로 조립·최적화하는 하네스 (Scope→Retrieve→Process→Manage 4단계 + 4개 에이전트, brevity bias·lost-in-the-middle·context-collapse 가드 + 멀티에이전트 per-agent 격리(REGISTRY/FOCUS). 근거 arXiv:2507.13334·2510.04618·2604.07911) |
| `agent-orchestration` | 작업을 여러 에이전트로 병렬화할지·어떻게 협업시킬지 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증하는 하네스 (분해평가→아키텍처결정→협업가드→검증 4단계 + 4개 에이전트, architecture-task alignment·45% capability ceiling·coordination 3실패모드. 근거 arXiv:2512.08296·2601.13295·2604.07911) |
| `eval-harness` | AI 생성물(코드·에이전트 출력)을 엄밀 평가하는 하네스 (정의·validity→judge 구성→validity 감사→실행·집계 4단계 + 4개 에이전트, LLM-as-a-Judge 다중표본≥3·ABC task/outcome validity·harness≠model 귀인. 근거 arXiv:2507.02825·2412.12509·2502.12468·2507.11538·2606.17799) |
| `spec-driven-development` | 엔지니어용 실행 가능 명세(spec=source of truth)를 작성하고 에이전트가 명세대로 코드 생성→명세 대비 자기검증하게 하는 하네스 (명세작성→인수설계→구현→검증 4단계 + 4개 에이전트, 명세 승인 게이트·comprehension 게이트. 근거 arXiv:2602.00180 + Osmani 2026-01 글) |
| `ai-readable-codebase` | 코드베이스의 구조적 AI 접근성(A축≠Q축)을 진단·개선하는 하네스 (진단(2축·L1~L5 증거기반)→빌드 가드레일(의존 방향 물리 강제·피드백 3차원)→standalone 독립 실행→수용 증명·등급 재측정 4단계 + 4개 에이전트, 빌드가 강제·문서가 설명·reward-hacking 가드. 근거 flex.team 5부작 + 2025+ 출처(arXiv:2602.11481·2306.09896·2505.10443 등), CodeScene 9.4/5.15 수치는 미입증으로 비인용) |
| `human-agent-teaming` | 사람과 AI 에이전트가 *한 팀으로* 협업하도록 분업·공통기반·감독/신뢰·검증을 설계하는 하네스 (분업·위임(human/agent/co-delegation·자율 수준·HITL/HOTL)→공통기반(온보딩 브리핑·AI 오류 경계·workspace awareness·재정렬 루프)→모니터링 기반 감독(전수 승인 아님·단계적 가역 권한·적절한 의존)→비례 검증(루브릭·Doer-Verifier)·핸드오프 연속성·책임 4단계 + 4개 에이전트. 축은 AI↔AI 토폴로지가 아니라 사람↔에이전트 분업·감독. 근거 Anthropic 'Building Effective Human-Agent Teams' 정독 + 1차 자료 + arXiv:2504.10918·2602.05987, 벤더=설계 의도·반박된 패턴(자기제한 1차 감독) 미사용) |
| `code-as-harness` | 코드를 *실행 가능·검사 가능·상태 보존* 한 운영 기반으로 다루고 한 번의 거버넌스된 Plan→Execute→Verify 제어 루프로 코드 변경을 안전·검증 가능하게 수행하는 하네스 (계획 계약(의도·결정적 센서·행동 위험 분류)→권한·샌드박스 실행(가역 우선·안전임계 사람 게이트·실행 trace)→실행 검증(자기보고 불신·결정적 센서 실행·reward-hacking·불완전 피드백 UNVERIFIED·최종 너머)→텔레메트리 진단·수렴(trace 인용 진단·regression-free 수정·CONVERGED/ITERATE/ESCALATE) 4단계 + 4개 에이전트. 근거 arXiv:2605.18747 'Code as Agent Harness' 정독 + 인접 1차(2604.08224·2506.11442·2604.20801·2508.00083·2512.14012)·보강(2604.15149·2603.07084), 서베이=개념 프레임·인접 기법 귀속 분리·반박된 AgentFlow 4-phase 미사용. 단일 거버넌스 사이클이지 통과까지 자율 반복(loop)이 아님) |

## 세부 문서 (`_docs/`)

루트 `CLAUDE.md`는 100줄 이내 인덱스로 유지하고, 세부 내용은 아래 특징별 문서에 둔다. 작업 전 관련 문서를 먼저 참조할 것.

- [`_docs/project-structure.md`](_docs/project-structure.md) — 전체 디렉토리 구조와 각 파일/스킬 역할 트리
- [`_docs/skills.md`](_docs/skills.md) — 플러그인별 스킬 목록·커맨드·설명 (frontend-harness / harness-generator / git-harness / meta-harness / product-spec-harness / loop-engineering / review-harness / ops-harness / backend-harness / cicd-harness / context-engineering / agent-orchestration / eval-harness / spec-driven-development / ai-readable-codebase / human-agent-teaming)
- [`_docs/commands-and-hooks.md`](_docs/commands-and-hooks.md) — frontend-harness 커맨드(orchestrator/research/prd/…/review) + Stop lint 훅
- [`_docs/conventions.md`](_docs/conventions.md) — 마켓플레이스 등록·플러그인/스킬/커맨드 배치·교차 참조·플러그인 분리 규칙

## 핵심 규칙 (전문은 `_docs/conventions.md`)

- 각 스킬은 `plugins/<plugin>/skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description`만 둔다.
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리한다.
- 4개 이상 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md`를 두고 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 스킬/커맨드 설명은 한국어로 작성하고, 스킬 간 교차 참조는 상대 경로를 사용한다.
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 늘어나는 내용은 `_docs/` 하위 특징별 .md로 분리해 참조한다.
