# qa-agent-harness

에이전트가 *커버리지를 채우는* 것이 아니라 **리스크 노출(발생확률 × 영향)을 커버리지 우선순위로 변환**하고, 각
시나리오에 **진짜 판정 오라클**을 명시한 뒤, 테스트를 생성·실행하되 실패를 맹목 재시도하지 않고 **결함/플래키/환경으로
먼저 분류**하도록 묶은 도메인 무관(FE+API) 에이전틱 소프트웨어 QA 하네스.
핵심 메시지는 **"커버리지 극대화나 그린 신호 자체가 reward-hacking 가능한 대리지표다 — 오라클이 약하면 연기만 나고
경보는 울리지 않는다. 테스트의 가치는 실행 경로 수가 아니라 어서션(오라클)의 강도에 있다"** 이다.
근거: **arXiv:2601.02454 "The Rise of Agentic Testing" · arXiv:2506.02943 CANDOR · arXiv:2606.18168 "All Smoke, No Alarm" ·
arXiv:2504.16777 "Systemic Flakiness"**.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
qa-agent-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                          # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                          # 사용자용 개요·언제 쓰나·4단계 사용법·도구 경계·근거 자료
├── agents/                            # 모두 model: "opus"
│   ├── test-architect.md              # Phase 0 — 요구사항·변경·리스크 → 리스크 노출 등급·커버리지 우선순위 전략
│   ├── scenario-designer.md           # Phase 1 — 스토리/API → 리스크 매핑 시나리오 + 명시적 오라클(살아있는 라이브러리)
│   ├── test-engineer.md               # Phase 2 — 오라클 우선 생성·실행·로케이터/DOM 드리프트 점수화·로깅된 자가치유
│   └── failure-triager.md             # Phase 3 — 결함/플래키/환경 분류·공유 근본원인 클러스터링·변경 기반 재실행 우선순위
├── skills/
│   └── qa-agent-harness/
│       ├── SKILL.md                   # 오케스트레이터(진입점, Phase 0 전략 게이트 → 시나리오 → 실행 → 트리아지)
│       └── references/
│           ├── qa-agent-harness-principles.md   # 원칙·anti-pattern·결정 신호표
│           └── qa-agent-harness-research.md      # 설계 근거 deep-research dossier(출처·등급·인용·CAVEAT·제외 범위·방법론)
└── evals/
    ├── evals.json                     # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json              # 트리거 경계 평가(should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 리스크 기반 테스트 전략 (Risk-Driven Test Strategy) | test-architect | Test Strategy(리스크 노출 등급·커버리지 우선순위·판정 기준) | 승인 게이트 |
| 1 | 시나리오 설계·살아있는 라이브러리 (Scenario Design) | scenario-designer | Scenario Library(리스크 매핑 시나리오 + 명시적 오라클) | 1줄 보고 |
| 2 | 오라클 우선 생성 + 자가치유 실행 (Generation + Self-Healing Execution) | test-engineer | Execution Report(생성 테스트·실행 결과·점수화·로깅된 자가치유) | 파괴적/고위험 HITL 게이트 / 1줄 보고 |
| 3 | 실패 트리아지 & 근본원인 (Intelligent Failure Triage) | failure-triager | Triage Report(결함/플래키/환경 분류·클러스터·재실행 우선순위) | 트리아지 사람 게이트 |

최종 보고: `[QA-Agent-Harness] 리스크전략 {등급수} · 시나리오 {오라클수} · 실행 {PASS/FAIL·자가치유 게이트} · 트리아지 {결함|플래키|환경·클러스터수}`

## Conventions

- **리스크 노출이 노력을 배분한다**: 균일 커버리지가 아니라 발생확률×영향으로 테스트 깊이·순서를 정한다.
- **오라클 우선**: 테스트 가치는 어서션의 강도다. 커버리지는 결함 탐지력과 약하게만 상관하므로 스모크/동어반복을 금지하고 시나리오마다 기대 상태·불변식을 명시한다.
- **오라클 독립 검증**: 할루시네이션된 어서션은 모델 간 비일관적이라 다중 표본 합의(panel/consensus)로 거른다(CANDOR).
- **자가치유는 점수화·로깅·게이트**: role→data-testid→접근성 트리→가시 텍스트 우선순위로 후보를 비교하고, 치유가 실제 기능 변경/회귀를 초록으로 은폐하지 않게 로깅·검토한다.
- **재시도 전 트리아지**: 실패를 결함 vs 플래키 vs 환경으로 먼저 분류한다. 플래키는 공유 근본원인으로 클러스터링해 하나의 수정으로 다수를 해소한다.
- **변경 기반 우선순위화**: 회귀 전량 재실행이 아니라 코드 변경 영향+리스크로 테스트를 선택·정렬한다.
- **점진적 자율성 + HITL 게이트**: 행동 전 제안(suggest-before-act), 신뢰가 쌓이며 자율 범위를 넓히되 파괴적/고위험 행동은 사람 승인 게이트를 통과시킨다.
- **설명 가능한 로깅된 결정**: 전략 우선순위·치유 선택·트리아지 판정을 근거와 함께 기록해 감사·재현 가능하게 한다.
- **커버리지 연극·리워드 해킹 가드**: 그린 신호는 대리지표다. 실행 경로만 밟고 어서션이 약한 테스트, 자가치유가 회귀를 은폐하는 것, 그린까지 재시도, 현재 구현에 오버피팅한 오라클을 위반으로 잡는다.
- **정직성·falsifiability**: S06 세션의 조직 도입·AI 성숙도 5단계 모델·변경관리 층은 하네스화 불가로 제외, 회사별 수치(1.54x·49%·68%)와 CANDOR 0.834→0.971은 특정 세팅 관찰값, "개선 N% 보장" 금지.
- **승인 게이트·관찰성**: Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: FE 한정 QA 단계·구현 내 test-generator·오프라인 judge 채점·프로덕션 인시던트 RCA·상류 핸드오프 검수·도메인 무관 자율 반복 루프·에이전트 병렬화 판단·사람↔에이전트 분업·LLM 입출력 가드레일은 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 다른 마켓플레이스 플러그인에 의존하지 않는 독립 플러그인이다(경계의 '범위 밖'은 일반 도메인 개념으로만 서술).

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | 리스크 기반 전략→오라클 명시 시나리오→오라클 우선 생성·게이트된 자가치유 실행→결함 vs 플래키 지능형 트리아지의 독립 end-to-end 에이전틱 QA 하네스. Tech-Verse 2026 S06 "10x Speed With QA Agent Platform" 세션의 harnessable core만 추출(조직 도입·성숙도 모델·변경관리 층은 제외). 1차 근거: arXiv:2601.02454(Agentic Testing)·arXiv:2506.02943(CANDOR)·arXiv:2606.18168(All Smoke, No Alarm)·arXiv:2504.16777(Systemic Flakiness), 보강: arXiv:2601.05542(LLM 오라클)·Requirements-based test prioritization 산업연구·Katalon Agentic QA 운영모델 |
