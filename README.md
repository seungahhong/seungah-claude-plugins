# seungah-claude-plugins — Dev Workflow Multi-Agent Skills

분석 → 설계 → 개발 → 리뷰 → 검증까지, 소프트웨어 개발 전 과정을 지원하는 **Claude Code 플러그인 마켓플레이스**입니다. 31개 플러그인이 멀티 에이전트 스킬·커맨드·훅으로 개발 워크플로우, 기획·설계 상류 검수, 품질·검증, 에이전트/LLM 엔지니어링, 그리고 하네스 자체를 만들고 고치는 메타 도구를 제공합니다.

## 설치

```bash
# 마켓플레이스 등록 (한 번만)
/plugin marketplace add seungahhong/seungah-claude-plugins

# 원하는 플러그인 설치 (예: frontend-harness)
/plugin install frontend-harness@seungah-claude-plugins

# 또는 한 번에 (Claude Code 2.1.275+)
/plugin install frontend-harness --marketplace seungahhong/seungah-claude-plugins
```

터미널에서는 `claude plugin marketplace add …` / `claude plugin install …`로 동일하게 설치합니다. 설치 후 각 플러그인의 스킬은 자동 트리거되거나 `/<plugin>:<skill>`(예: `/git-harness:commit-pr`)로 직접 호출할 수 있습니다. 이미 설치한 플러그인은 `claude plugin update <plugin>@seungah-claude-plugins`로 최신 버전으로 갱신합니다.

## 플러그인 (31)

구성 열은 스킬 · 에이전트 · 커맨드 수입니다. 각 플러그인의 사용법·경계·근거는 링크된 README에 있습니다.

### 개발 워크플로우

| Plugin | 역할 | 구성 |
|--------|------|------|
| [`frontend-harness`](plugins/frontend-harness/README.md) | 프론트엔드 Research → PRD → Develop → Review → Verify 6단계 오케스트레이터 + 가드·lint 훅 | 13 · – · 7 (+훅 6) |
| [`backend-harness`](plugins/backend-harness/README.md) | 백엔드/API 설계→환경(1급)→구현→실행 기반 검증 + 실행기반 `test-generator` | 2 · 4 · – |
| [`git-harness`](plugins/git-harness/README.md) | `/commit-pr` 단일 파이프라인 — 상태 기반 진입점 → 커밋 전 리뷰 차단 게이트 → 한국어 커밋 → push → PR → PR 리뷰 | 1 · – · – |
| [`cicd-harness`](plugins/cicd-harness/README.md) | CI 파이프라인 → IaC(plan+OPA) → 릴리스 결정(trust-tier) → 전달 안정성(DORA) | 1 · 4 · – |
| [`ops-harness`](plugins/ops-harness/README.md) | 프로덕션 인시던트 탐지 → 국소화 → RCA → 완화(AIOpsLab 4단계, 휴먼-인-더-루프) | 1 · 4 · – |
| [`code-as-harness`](plugins/code-as-harness/README.md) | Plan → Execute → Verify 단일 거버넌스 제어 루프(권한·샌드박스 실행, 자기보고 불신, 수렴 판정) | 1 · 4 · – |
| [`spec-driven-development`](plugins/spec-driven-development/README.md) | 실행 가능 명세(spec=source of truth) 작성 → 인수설계 → 구현 → 명세 대비 자기검증 | 1 · 4 · – |
| [`test-layering-harness`](plugins/test-layering-harness/README.md) | 인수조건을 방법론×계층 축 카드로 조합해 3단계 승인 게이트로 테스트를 하나씩 생성·적용 | 1 · – · – |

### 기획·설계 상류

| Plugin | 역할 | 구성 |
|--------|------|------|
| [`product-spec-harness`](plugins/product-spec-harness/README.md) | 기획자용 PRD + 사용자 스토리 + 인수조건 7단계 인터랙티브 하네스(재갱신 경로, 점수 금지) | 1 · 8 · – |
| [`review-harness`](plugins/review-harness/README.md) | 코드 착수 *전* 상류 산출물(기획 DoR·디자인·API 계약·QA 인수조건) 핸드오프 게이트 검수 `/handoff-review` | 4 · – · 1 |
| [`spec-to-figma-harness`](plugins/spec-to-figma-harness/README.md) | 유저스토리·인수조건을 Figma 상태 프레임·레이어 어노테이션 스펙으로 변환(Figma 쓰기 금지) | 1 · 4 · – |
| [`ux-ai-workflow-harness`](plugins/ux-ai-workflow-harness/README.md) | UX 작업 단계별 생성형 AI 위임 수준(L1~L4) 판정 → 맥락 설계 → 초안 점검 → 사람 체크포인트 | 1 · 4 · – |
| [`methodology-advisor`](plugins/methodology-advisor/README.md) | 현행 프로세스 진단 + 문진 뒤 방법론 카탈로그 14종으로 순위 shortlist 제안(우열·은탄환 금지) | 1 · 4 · – |
| [`org-transformation-harness`](plugins/org-transformation-harness/README.md) | 목적조직·AI native 전환 인터뷰 → 진단 → 목표 → 간극·실행계획 → 적대 검증(제안만) | 1 · 4 · – |

### 품질·검증·리뷰

| Plugin | 역할 | 구성 |
|--------|------|------|
| [`eval-harness`](plugins/eval-harness/README.md) | AI 생성물 엄밀 평가 — 정의·validity → judge 구성 → validity 감사 → 실행·집계 | 1 · 4 · – |
| [`qa-agent-harness`](plugins/qa-agent-harness/README.md) | 리스크 기반 전략 → 오라클 명시 시나리오 → 게이트된 자가치유 실행 → 결함 vs 플래키 트리아지 | 1 · 4 · – |
| [`agentic-code-review-harness`](plugins/agentic-code-review-harness/README.md) | 코드 변경(특히 AI 작성)을 리뷰어 자리에서 읽고 머지 가능성 판정(판정만·실행은 사람) | 1 · 5 · – |
| [`review-pipeline-harness`](plugins/review-pipeline-harness/README.md) | 팀·저장소 코드 리뷰 시스템 설계 — 방어 계층·변경 기반 승인 등급·REVIEW.md·수렴·노이즈·가드레일·circuit breaker → 적대 검증(설계만) | 1 · 5 · – |
| [`comprehension-harness`](plugins/comprehension-harness/README.md) | 에이전트 변경을 사람이 실제로 이해하는지 실측하고 자산으로 남김(결함·머지 판정 없음) | 1 · 5 · – |
| [`ai-readiness-cartography`](plugins/ai-readiness-cartography/README.md) | 저장소 AI 준비도 결정론 스코어러(`score.py`) 측정 + 승인 게이트 뒤 개선(3모드 자유 조합) | 1 · 8 · – |
| [`aeo-harness`](plugins/aeo-harness/README.md) | AEO — 기술 문서를 AI 코딩 에이전트가 찾고·읽고·정확히 쓰게 결정론 센서로 재고 개선(SEO/GEO 아님) | 1 · 4 · – |
| [`token-efficiency`](plugins/token-efficiency/README.md) | Claude Code 세션 JSONL 로그로 토큰/컨텍스트 효율 측정·시각화·$ 절감안(측정·제안만) | 1 · – · – |

### 에이전트·LLM 엔지니어링

| Plugin | 역할 | 구성 |
|--------|------|------|
| [`context-engineering`](plugins/context-engineering/README.md) | LLM·에이전트 컨텍스트 페이로드 Scope → Retrieve → Process → Manage 조립·최적화 | 1 · 4 · – |
| [`agent-orchestration`](plugins/agent-orchestration/README.md) | 작업 병렬화·협업 구조를 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증 | 1 · 4 · – |
| [`human-agent-teaming`](plugins/human-agent-teaming/README.md) | 사람↔에이전트 분업·위임 → 공통기반 → 모니터링 감독·신뢰 보정 → 비례 검증·책임 설계 | 1 · 4 · – |
| [`llm-guardrails-harness`](plugins/llm-guardrails-harness/README.md) | LLM 앱 런타임 외부 가드레일 — 위협모델·정책 → 입력 레일 → 출력·검색 레일 → 행동 강제·적대검증 | 1 · 4 · – |
| [`agent-authorization-harness`](plugins/agent-authorization-harness/README.md) | 에이전트/MCP/A2A 머신 아이덴티티·인가 설계 + red-team(설계 산출물, IdP 배포 아님) | 1 · 4 · – |
| [`loop-engineering`](plugins/loop-engineering/README.md) | 검증 가능한 목표를 향한 자율 반복 루프 + 지속학습 메모리 | 1 · 5 · – |
| [`meta-prompting-harness`](plugins/meta-prompting-harness/README.md) | 메타 프롬프팅 4단계(인테이크 → 질문 유도 → 성공조건 → 환경 맞춤·적대 점검), 프롬프트 생성만 | 1 · 4 · – |

### 메타 — 하네스 자체를 다루기

| Plugin | 역할 | 구성 |
|--------|------|------|
| [`harness-generator`](plugins/harness-generator/README.md) | 도메인 무관 하네스(에이전트팀 + 스킬 + 오케스트레이터)를 사람이 단계별로 직접 생성하는 메타 플러그인 | 1 · – · – |
| [`meta-harness`](plugins/meta-harness/README.md) | 사용 중인 하네스의 결함을 full-trace experience store로 causal 진단하고 Pareto 비후퇴 패치를 승인 게이트 뒤에만 적용 + 신호 캡처 훅 2종 | 4 · 4 · – (+훅 2) |

> 책임 경계: 신규 하네스를 *사람이 직접* 만들면 `harness-generator`, *이미 사용 중인* 하네스의 진단·개선은 `meta-harness`, 단발 스킬 작성·평가는 공식 마켓플레이스의 `skill-creator`.

## 문서

- [`CLAUDE.md`](CLAUDE.md) — 저장소 작업용 인덱스(플러그인 한 줄 역할 + 핵심 규칙)
- [`_docs/plugin-overview.md`](_docs/plugin-overview.md) — 31개 플러그인 확장 설명
- [`_docs/skills.md`](_docs/skills.md) — 플러그인별 스킬·커맨드·에이전트 설명
- [`_docs/commands-and-hooks.md`](_docs/commands-and-hooks.md) — 커맨드·훅 한눈에 보기
- [`_docs/project-structure.md`](_docs/project-structure.md) — 전체 디렉토리 트리
- [`_docs/conventions.md`](_docs/conventions.md) — 플러그인·스킬·커맨드 작성 규칙

## 저장소 구조 (요약)

```
.claude-plugin/marketplace.json        # 마켓플레이스 리스팅 (plugins 배열 = 31개, 버전·태그·카테고리)
plugins/<plugin>/
  .claude-plugin/plugin.json           # 플러그인 메타데이터 (설명은 marketplace.json 항목과 동일)
  CLAUDE.md · CHANGELOG.md · README.md # 유지보수 문서 · 변경 이력 · 사용자용 개요
  skills/<skill>/SKILL.md (+references/ scripts/ assets/)
  agents/<name>.md                     # 4개 이상 에이전트 하네스 (모두 model: "opus")
  commands/<name>.md · hooks/          # frontend-harness·review-harness 커맨드, frontend-harness·meta-harness 훅
  evals/                               # 수용 평가·트리거 경계 평가
_docs/                                 # 세부 문서 (위 '문서' 절)
```

전체 트리는 [`_docs/project-structure.md`](_docs/project-structure.md)를 보세요.

## 라이선스

MIT
