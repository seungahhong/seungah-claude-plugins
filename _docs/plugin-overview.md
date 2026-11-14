# 플러그인 한눈에 보기 (확장 설명)

루트 `CLAUDE.md`의 표는 2026-11-07부터 **한 줄 역할**만 남기고, 31개 플러그인의 확장 설명(단계 구성·에이전트 수·가드·근거)은 여기에 둔다. 마켓플레이스 카드 문구는 `.claude-plugin/marketplace.json`, 스킬 단위 설명과 2026-10-18 축약 전 원문은 [`skills.md`](skills.md), 디렉토리 구조는 [`project-structure.md`](project-structure.md) 참조.

| Plugin | 역할 |
|--------|------|
| `frontend-harness` | 프론트엔드 개발 워크플로우 (계획·구현·품질·보안·성능·QA·검증·figma-extract 스킬 + 오케스트레이터 커맨드 + lint 훅) |
| `harness-generator` | 도메인 무관 하네스(에이전트팀+스킬+오케스트레이터) **수동·인터랙티브** 생성 메타 플러그인 |
| `git-harness` | Git 워크플로우 단일 파이프라인 `/commit-pr` (상태 기반 진입점 commit/push/pr 추천·선택 → 커밋 전 리뷰 + correctness·CONFIRMED 차단 게이트 → 한국어 커밋 메시지 → push → PR 생성 → PR 리뷰. 진입점 선택 = 이후 단계 승인) |
| `meta-harness` | 하네스(루트 CLAUDE.md·SKILL.md·agents·commands·hooks) 결함을 full-trace experience store로 causal 진단하고 Pareto 비후퇴 패치를 **승인 게이트 뒤에만** 적용하는 메타 하네스 엔지니어링. 라이프사이클 훅 2종(UserPromptSubmit 신호 캡처·SessionStart 미소비 신호 표면화)은 캡처·주입 전용. 결정론적 근거는 advisory 본문이 아니라 hook/permission으로 라우팅하되 `.claude/settings.json`은 직접 수정 않고 update-config 핸드오프 |
| `product-spec-harness` | 기획자용 PRD+사용자 스토리+**인수조건** 7단계 인터랙티브 하네스 — 기획안 카드 추출 → 기획 완성도 점검(DoR) → **생성 전 보완 문답** → PRD(계획→설계→비평 루프) → 스토리 → 1차 적대 검증 → 인수조건(단일 원본) → 2차 적대 검증, 생성 후 **재갱신 경로**(입력 모드 R·ID 동결). 산출 파일은 정확히 4개, 점수·등급 금지(INVEST 점수표만 예외) |
| `loop-engineering` | 검증 가능한 목표를 향한 자율 반복 루프(Goal→Execute→Verify→Diagnose→Improve) + 지속학습 메모리(Fail→Investigate→Verify→Distill→Consult) 멀티 에이전트 하네스 |
| `review-harness` | 코드 착수 *전* 상류 산출물(기획 DoR·디자인 핸드오프·API 계약·QA 인수조건) 핸드오프 게이트 검수 (4개 게이트 스킬 + handoff-review 오케스트레이터, 2025+ 근거·정직성 가드레일) |
| `ops-harness` | 프로덕션 운영·인시던트 대응·관측성 하네스 (AIOpsLab 4단계 탐지→국소화→RCA→완화 + 4개 에이전트, traces+logs+metrics 중재 읽기·휴먼-인-더-루프, RCA anti-anchoring 가드·Straight-Shot 폴백) |
| `backend-harness` | 백엔드/API 실행 기반 검증 구현 하네스 (설계→환경(1급)→구현→실행검증 5단계 + 4개 에이전트, 자기보고 불신·reward-hacking 가드 + 실행기반 test-generator 스킬) |
| `cicd-harness` | 코드 커밋→프로덕션 전달 파이프라인 하네스 (CI 파이프라인→IaC(terraform plan+OPA)→릴리스 결정(trust-tier)→전달 안정성(DORA 통제) 4단계 + 4개 에이전트, defense-in-depth·policy-as-code·사람 사전승인) |
| `context-engineering` | LLM·에이전트에 넣을 컨텍스트 페이로드를 체계적으로 조립·최적화하는 하네스 (Scope→Retrieve→Process→Manage 4단계 + 4개 에이전트, brevity bias·lost-in-the-middle·context-collapse 가드 + 멀티에이전트 per-agent 격리(REGISTRY/FOCUS). 근거 arXiv:2507.13334·2510.04618·2604.07911) |
| `agent-orchestration` | 작업을 여러 에이전트로 병렬화할지·어떻게 협업시킬지 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증하는 하네스 (분해평가→아키텍처결정→협업가드→검증 4단계 + 4개 에이전트, architecture-task alignment·45% capability ceiling·coordination 3실패모드. 근거 arXiv:2512.08296·2601.13295·2604.07911) |
| `eval-harness` | AI 생성물(코드·에이전트 출력)을 엄밀 평가하는 하네스 (정의·validity→judge 구성→validity 감사→실행·집계 4단계 + 4개 에이전트, LLM-as-a-Judge 다중표본≥3·ABC task/outcome validity·harness≠model 귀인. 근거 arXiv:2507.02825·2412.12509·2502.12468·2507.11538·2606.17799) |
| `spec-driven-development` | 엔지니어용 실행 가능 명세(spec=source of truth)를 작성하고 에이전트가 명세대로 코드 생성→명세 대비 자기검증하게 하는 하네스 (명세작성→인수설계→구현→검증 4단계 + 4개 에이전트, 명세 승인 게이트·comprehension 게이트. 근거 arXiv:2602.00180 + Osmani 2026-01 글) |
| `human-agent-teaming` | 사람과 AI 에이전트가 *한 팀으로* 협업하도록 분업·위임 → 공통기반 → 모니터링 기반 감독·신뢰 보정(전수 승인 아님) → 비례 검증·핸드오프·책임을 설계하는 하네스(4 에이전트). 축은 AI↔AI 토폴로지가 아니라 사람↔에이전트 분업·감독. 근거 Anthropic 'Building Effective Human-Agent Teams' + arXiv:2504.10918·2602.05987 |
| `code-as-harness` | 코드를 *실행 가능·검사 가능·상태 보존* 운영 기반으로 다루는 **단일 거버넌스** Plan→Execute→Verify 제어 루프 하네스 — 계획 계약 → 권한·샌드박스 실행(안전임계 사람 게이트) → 실행 검증(자기보고 불신·UNVERIFIED) → 텔레메트리 진단·수렴(CONVERGED/ITERATE/ESCALATE) + 4 에이전트. 근거 arXiv:2605.18747. 통과까지 자율 반복(loop)이 아님 |
| `llm-guardrails-harness` | LLM/에이전트 앱의 **런타임 외부 가드레일** 하네스 — 위협모델·정책(OWASP LLM Top 10 2025) → 입력 레일 → 출력·검색 레일 → 행동 강제·적대검증(ASR/FPR) 4단계 + 4 에이전트. 외부강제>시스템프롬프트·fail-closed·다층방어. 오프라인 채점(eval-harness)이 아닌 인라인 집행 |
| `qa-agent-harness` | 리스크 기반 전략 → 오라클 명시 시나리오 → 오라클 우선 생성·게이트된 자가치유 실행 → 결함 vs 플래키 트리아지의 에이전틱 QA 하네스(4 에이전트). 커버리지≠결함탐지·오라클 강도·점진 자율성·HITL. 근거 arXiv:2601.02454·2506.02943·2606.18168·2504.16777 |
| `agent-authorization-harness` | 에이전트/MCP 도구/A2A의 머신 아이덴티티·인가를 벤더 무관 설계·red-team하는 하네스 — 신뢰·스코프 → 그랜트·위임(단명 audience-bound 토큰·on-behalf-of) → 동의·집행(deny-by-default·audience 검증) → 적대 검증(confused-deputy·토큰 재생·스코프 크리프) + 4 에이전트. 설계+red-team 산출물이지 IdP 배포 아님. 근거 RFC 8707·8693·OWASP LLM06 |
| `ai-readiness-cartography` | 저장소가 AI 코딩 에이전트가 안전하게 기여할 코드베이스인지 **결정론 스코어러**(score.py 100점·9카테고리·3 gate)로 측정하고 승인 게이트 뒤 개선하는 단일 스킬 — ① 측정 ② 진단·개선(빌드 가드레일 → standalone → 개별 승인 적용) ③ 코드 본문(주석·명명·구조, 3게이트) 자유 조합. 위험은 경고·수용은 사용자, 커밋 안 함 |
| `token-efficiency` | Claude Code **세션 JSONL 로그**를 파싱해 레포 단위 토큰/컨텍스트 효율을 측정·시각화하고 $ 절감안을 내는 결정론 단일 스킬 — 4축 점수(cache·redundancy·density·tool) + 8개 탐지기 + 세션별 모델가 낭비 추정 + 오프라인 대시보드. 측정·제안만. ai-readiness-cartography와 상보(런타임 로그 vs 정적 구조) |
| `test-layering-harness` | 인수조건(Given-When-Then)을 **방법론×계층 축 카드**로 조합해 테스트를 계획하고 **계획→개별→최종 3단계 승인 게이트**로 하나씩 생성·적용하는 단일 스킬. 스코프 가드(선택한 방법론·계층 안에서만), unit/integration은 실제 API 호출 금지, E2E는 smoke·regression만(smoke는 live 전용·수동 체크포인트), AC-ID 표기, 셀렉터 사다리. 정본은 principles |
| `methodology-advisor` | 팀의 **현행 개발·회사·사업 프로세스를 먼저 진단**하고 다각도 문진(3축·한 번에 한 질문) 뒤 내장 방법론 카탈로그 14종 + 컨틴전시 프레임워크(Cynefin·Stacey·Boehm-Turner)로 **순위 shortlist + 1순위**를 제안하는 하네스(4 에이전트). 우열·은탄환·N% 금지, 제안만 |
| `meta-prompting-harness` | 메타 프롬프팅(AI가 최적화한 프롬프트를 새 컨텍스트에 주입)을 인테이크 → 질문 유도(한 번에 하나씩) → 성공·검증 조건 → 환경 맞춤 깎아내기 → 적대 점검 4단계로 수행하는 하네스(4 에이전트). 근거 등급 STRONG/report-only/REFUTED, 프롬프트 생성만·실행은 사용자 |
| `org-transformation-harness` | 목적조직·AI native 전환을 원하는 실무자·리더를 인터뷰해 현행 진단 → 목표 구체화(임의 정의 금지) → 간극·실행계획(quick-wins 맨 위) → 적대 검증·공유 요약 4단계로 "무엇부터 시작할지"를 정리하는 하네스(4 에이전트). 은탄환·N%·점수화 금지, 제안만. 근거 DORA 2024/2025(조건부) |
| `spec-to-figma-harness` | 유저스토리·인수조건을 **"시나리오는 상태 프레임으로, 규칙은 레이어 어노테이션으로"** 옮겨 FE가 되묻지 않을 Figma 반영 설계도·어노테이션 스펙을 내는 하네스 — AC 분해·상태 카탈로그 역방향 호명 → 반영 설계도 → 어노테이션 → FE 1인칭 적대 검증 + 4 에이전트. 발명 금지·Figma 쓰기 금지·되물음은 1급 산출물 |
| `agentic-code-review-harness` | 이미 만들어진 코드 변경(특히 AI 작성)을 **리뷰어 자리에서 읽고 머지 가능성을 판정**하는 하네스 — 리스크 티어링 → 증거 감사(오라클 강도·게이트 완화·결함 서명) → 직교 렌즈 병렬 리뷰 → 발견별 반증(CONFIRMED/PLAUSIBLE/DROPPED) → 트리아지·판정 + 5 에이전트. 판정만·실행은 사람, 차단은 재현 근거로만, 인용 금지 수치는 evidence.md |
| `review-pipeline-harness` | AI가 코드를 많이 쓰는 팀의 **코드 리뷰 시스템**을 설계하는 하네스 — 인테이크·기준선(`pr_baseline.py`) → 방어 계층 지도(L1~L7 있음/약함/없음/미확인) → 변경 기반 위험 등급 승인 정책(결정론 바닥+판단 상향·에이전트 승인 불인정·지휘한 사람 필수·커밋 단위 승인·정책 파일 always-human) → AI 리뷰어 구성(REVIEW.md 초안·깊이·신뢰 경계·차단 게이트) → 수렴·노이즈(라운드 상한·diff-only·응답 4분류) → 지표·인시던트 eval·circuit breaker → 적대 검증(A1~A12) + 5 에이전트. 사람 시간 절감은 revert 가드레일과 짝, 사내 운영·호스티드 제품·오픈소스 플러그인 구분, 설계만·적용은 사람. 근거 Anthropic "Solving code review at Anthropic"(2026-10) + 제품 문서, `/deep-research` 3표 검증 |
| `comprehension-harness` | 에이전트가 쓴 변경을 **사람이 실제로 이해하는지 실측**하고 자산으로 남기는 하네스 — 이해 부채 지도·설명 전 예측 → 검증 훅 설명서 → 자유서술 회상·교정 피드백(묻지 않은 범위 열거) → (opt-in) 마이크로월드 → (opt-in) 공유 이해 + 5 에이전트. 결함·머지 판정 안 함, 점수·등급 금지, 효과 약속 안 함 |
| `aeo-harness` | **AEO(Agentic Engine Optimization)** — 기술 문서를 AI 코딩 에이전트가 찾고·적은 왕복으로 읽고·정확히 쓰게 결정론 센서로 재고 승인 게이트 뒤 개선하는 하네스(도달 조사 → 내용 조사 → 개입 계획 T-A/T-B/T-C → 재측정 수용 + 4 에이전트). SEO/GEO 아님, 도달≠정확도, 틀린 문서>없는 문서, 점수·등급 금지 |
| `ux-ai-workflow-harness` | UX 실무자가 UX 작업 하나에 생성형 AI를 **단계별로 어디까지 쓸지** 정하는 하네스 — 위임 지도(7개 테스트로 L1~L4 판정) → 맥락·지시 설계 → AI 초안 점검(방법론별 점검표) → 사람 체크포인트·인계 + 4 에이전트. 학습 단계는 기본 사람, 합성 데이터를 실제 결과로 표기 금지, 참가자 데이터 보호, 효과 수치·점수 금지. 근거 NN/g 스터디 가이드 + 1차 연구 대조 |
