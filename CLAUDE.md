# Frontend Harness - Dev Workflow Multi-Agent Skills

소프트웨어 개발 전 과정을 지원하는 Claude Code 스킬 플러그인 마켓플레이스(30개 플러그인, `seungahhong/seungah-claude-plugins`).

분석 → 설계 → 개발 → 리뷰 → 검증까지를 멀티 에이전트 스킬·커맨드·훅으로 묶고, 하네스 자체를 생성·개선하는 메타 플러그인을 포함한다.

## 플러그인 한눈에 보기

한 줄 역할만 둔다. 확장 설명은 [`_docs/plugin-overview.md`](_docs/plugin-overview.md), 스킬 단위 상세는 [`_docs/skills.md`](_docs/skills.md), 마켓플레이스 카드 문구·버전은 `.claude-plugin/marketplace.json`이 정본이다.

| Plugin | 역할 (한 줄) |
|--------|------|
| `frontend-harness` | 프론트엔드 개발 워크플로우 — 13 스킬 + 오케스트레이터 커맨드 7종 + 가드·lint 훅 6종 |
| `harness-generator` | 도메인 무관 하네스(에이전트팀+스킬+오케스트레이터) **수동·인터랙티브** 생성 메타 플러그인 |
| `git-harness` | `/commit-pr` 단일 파이프라인 — 상태 기반 진입점 → 커밋 전 리뷰 차단 게이트 → 한국어 커밋 → push → PR → PR 리뷰 |
| `meta-harness` | 하네스 결함을 full-trace experience store로 causal 진단, Pareto 비후퇴 패치를 **승인 게이트 뒤에만** 적용 + 캡처 훅 2종 |
| `product-spec-harness` | 기획자용 PRD+스토리+인수조건 7단계 인터랙티브 하네스(산출 파일 4개·점수 금지·재갱신 경로) |
| `loop-engineering` | 검증 가능한 목표를 향한 자율 반복 루프 + 지속학습 메모리 멀티 에이전트 하네스 |
| `review-harness` | 코드 착수 *전* 상류 산출물(기획 DoR·디자인·API 계약·QA 인수조건) 핸드오프 게이트 검수 |
| `ops-harness` | 프로덕션 인시던트 탐지→국소화→RCA→완화 4단계 운영·관측성 하네스(휴먼-인-더-루프) |
| `backend-harness` | 백엔드/API 설계→환경(1급)→구현→실행검증 하네스 + 실행기반 `test-generator` 스킬 |
| `cicd-harness` | CI 파이프라인→IaC(plan+OPA)→릴리스 결정(trust-tier)→전달 안정성(DORA) 4단계 전달 하네스 |
| `context-engineering` | LLM·에이전트 컨텍스트 페이로드 Scope→Retrieve→Process→Manage 조립·최적화 하네스 |
| `agent-orchestration` | 작업 병렬화·협업 구조를 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증 |
| `eval-harness` | AI 생성물 엄밀 평가 — 정의·validity→judge 구성→validity 감사→실행·집계 |
| `spec-driven-development` | 실행 가능 명세(spec=source of truth) 작성→인수설계→구현→명세 대비 자기검증 |
| `human-agent-teaming` | 사람↔에이전트 분업·위임→공통기반→모니터링 감독·신뢰 보정→비례 검증·책임 설계 |
| `code-as-harness` | Plan→Execute→Verify 단일 거버넌스 제어 루프(권한·샌드박스 실행, 자기보고 불신, 수렴 판정) |
| `llm-guardrails-harness` | LLM 앱 런타임 외부 가드레일 — 위협모델·정책→입력 레일→출력·검색 레일→행동 강제·적대검증 |
| `qa-agent-harness` | 리스크 기반 전략→오라클 명시 시나리오→게이트된 자가치유 실행→결함 vs 플래키 트리아지 |
| `agent-authorization-harness` | 에이전트/MCP/A2A 머신 아이덴티티·인가 설계 + red-team(설계 산출물, IdP 배포 아님) |
| `ai-readiness-cartography` | 저장소 AI 준비도 결정론 스코어러(`score.py`) 측정 + 승인 게이트 뒤 개선(3모드 자유 조합) |
| `token-efficiency` | Claude Code 세션 JSONL 로그로 토큰/컨텍스트 효율 측정·시각화·$ 절감안(측정·제안만) |
| `test-layering-harness` | 인수조건을 방법론×계층 축 카드로 조합해 3단계 승인 게이트로 테스트를 하나씩 생성·적용 |
| `methodology-advisor` | 현행 프로세스 진단 + 문진 뒤 방법론 카탈로그 14종으로 순위 shortlist 제안(우열·은탄환 금지) |
| `meta-prompting-harness` | 메타 프롬프팅 4단계(인테이크→질문 유도→성공조건→환경 맞춤·적대 점검), 프롬프트 생성만 |
| `org-transformation-harness` | 목적조직·AI native 전환 인터뷰→진단→목표→간극·실행계획→적대 검증(제안만) |
| `spec-to-figma-harness` | 유저스토리·인수조건을 Figma 상태 프레임·레이어 어노테이션 스펙으로 변환(Figma 쓰기 금지) |
| `agentic-code-review-harness` | 코드 변경(특히 AI 작성)을 리뷰어 자리에서 읽고 머지 가능성 판정(판정만·실행은 사람) |
| `comprehension-harness` | 에이전트 변경을 사람이 실제로 이해하는지 실측하고 자산으로 남김(결함·머지 판정 없음) |
| `aeo-harness` | AEO — 기술 문서를 AI 코딩 에이전트가 찾고·읽고·정확히 쓰게 결정론 센서로 재고 개선(SEO/GEO 아님) |
| `ux-ai-workflow-harness` | UX 작업 단계별 생성형 AI 위임 수준(L1~L4) 판정→맥락 설계→초안 점검→사람 체크포인트 |

## 세부 문서 (`_docs/`)

루트 `CLAUDE.md`는 100줄 이내 인덱스로 유지하고, 세부 내용은 아래 특징별 문서에 둔다. 작업 전 관련 문서를 먼저 참조할 것.

- [`_docs/plugin-overview.md`](_docs/plugin-overview.md) — 30개 플러그인 「한눈에 보기」 확장 설명(단계·에이전트 수·가드·근거)
- [`_docs/project-structure.md`](_docs/project-structure.md) — 전체 디렉토리 구조와 각 파일/스킬 역할 트리(파일 추가·삭제 시 같은 커밋에서 갱신)
- [`_docs/skills.md`](_docs/skills.md) — 플러그인별 스킬·커맨드·에이전트 설명 + 2026-10-18 축약 전 「한눈에 보기」 원문
- [`_docs/commands-and-hooks.md`](_docs/commands-and-hooks.md) — 커맨드(frontend-harness 7종·review-harness `/handoff-review`) + 훅(frontend-harness 6종·meta-harness 2종)
- [`_docs/conventions.md`](_docs/conventions.md) — 마켓플레이스 등록·플러그인/스킬/커맨드 배치·교차 참조·description 길이·README 설치 줄·버전 bump 규칙
- [`_docs/self-healing-harness-research.md`](_docs/self-healing-harness-research.md) — 자가치유 하네스(meta-harness 라이프사이클 훅) 설계 근거 조사(2026-06-18)

## 핵심 규칙 (전문은 `_docs/conventions.md`)

- 각 스킬은 `plugins/<plugin>/skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description` 필수 + 필요 시 `allowed-tools`/`disable-model-invocation`만 추가 허용한다.
- 메타/도메인 무관 스킬은 `frontend-harness`에 두지 않고 별도 플러그인으로 분리한다.
- 4개 이상 에이전트가 협업하는 하네스(예: `meta-harness`)는 `agents/{name}.md`를 두고 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 스킬/커맨드 설명은 한국어로 작성하고, 스킬 간 교차 참조는 상대 경로를 사용한다.
- 플러그인 `CLAUDE.md`는 소개·포인터·핵심 불변식만 두고(Structure 트리·이력 금지) 변경 이력은 `CHANGELOG.md`에 쌓는다. 플러그인 루트 CLAUDE.md는 설치본에는 로드되지 않는 유지보수 문서다.
- 스킬 `description`은 발동 문구+범주 경계로 300~600자·YAML 안전 평문으로 쓰되, 트리거 실측이 있거나 conventions에 예외로 기록된 스킬은 재측정 없이 바꾸지 않는다. plugin.json `description`은 marketplace.json 항목과 같은 문구로 유지하고 `tags`는 marketplace.json에만 둔다.
- 플러그인 README `## 설치`에는 원스텝 설치 줄 `/plugin install <plugin> --marketplace seungahhong/seungah-claude-plugins`을 둔다(`claude plugin add`는 존재하지 않는 명령). 기능 변경 시 plugin.json·marketplace.json 버전을 함께 올리고 CHANGELOG 행을 추가한다.
- 루트 `CLAUDE.md`는 100줄 이내로 유지하고, 늘어나는 내용은 `_docs/` 하위 특징별 .md로 분리해 참조한다.
