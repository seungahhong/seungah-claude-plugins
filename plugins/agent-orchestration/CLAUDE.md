# agent-orchestration

한 작업을 **여러 에이전트로 병렬화할지·어떻게 협업시킬지**를 판단 규칙으로 결정하고,
그 협업이 **단일 에이전트 baseline을 실제로 능가하는지** 적대적으로 검증하는 도메인 무관 멀티 에이전트 하네스.
핵심 메시지는 **"에이전트를 더 붙인다고 항상 이득이 아니다"** — 성패는 에이전트 수가 아니라 architecture-task alignment가 결정한다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
agent-orchestration/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                       # 사용자용 개요·언제 쓰나·5단계 사용법·도구 경계·근거 논문
├── agents/                         # 모두 model: "opus"
│   ├── task-decomposer.md          # Phase 0 — 분해 가능성·도구 밀도·의존 구조 평가 + 단일 baseline 추정
│   ├── architecture-selector.md    # Phase 1 — 선택 규칙(alignment·capability ceiling) → single/multi + 토폴로지 권고
│   ├── coordination-designer.md    # Phase 2 — communication/commitment/expectation 가드 + context-pollution 격리
│   └── orchestration-verifier.md   # Phase 3 — baseline 능가 적대 검증, 병렬화 금지면 단일 권고(reject)
├── skills/
│   └── agent-orchestration/
│       ├── SKILL.md                # 오케스트레이터(진입점, Phase 0 게이트 → 결정 → 설계 → 검증)
│       └── references/
│           ├── agent-orchestration-principles.md   # 선택 규칙·토폴로지·협업 가드·anti-pattern·결정 신호표
│           └── agent-orchestration-research.md      # 설계 근거 deep-research dossier(출처·인용·vote·CAVEAT·반박된 주장·방법론)
└── evals/
    ├── evals.json                  # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json           # 트리거 경계 평가(should_trigger 9 / should_not 13, 인접 도메인 경계 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 작업 분해·평가 (Decompose & Assess) | task-decomposer | Task Assessment(분해 가능성·도구 밀도·의존 구조·단일 baseline 추정) | 승인 게이트 |
| 1 | 아키텍처 결정 (Decide Architecture) | architecture-selector | Architecture Recommendation(single/multi·토폴로지·falsifiability·병렬화 금지 플래그) | 1줄 보고, single이면 Phase 2 skip |
| 2 | 협업 가드 설계 (Design Coordination) | coordination-designer | Coordination Design(세 실패 가드·컨텍스트 격리·가드 비용) | 멀티일 때만, 1줄 보고 |
| 3 | baseline 능가 검증 (Verify-or-Reject) | orchestration-verifier | Verification Verdict(PASS 멀티 / REJECT 단일 / REVISE) + 순이득 분석 | 1줄 보고 |

최종 보고: `[Orchestration 결정] {단일 | 멀티:토폴로지} — 순이득 {양/음/경계}, 근거 {핵심 신호}`

## Conventions

- **에이전트 수 ≠ 이득**: 멀티의 성패는 architecture-task alignment가 결정한다. 같은 작업도 토폴로지에 따라 단일 대비 큰 이득·큰 손해로 갈린다.
- **capability ceiling**: 단일 에이전트가 이미 잘 푸는 작업은 에이전트 추가가 음의 수익일 수 있다. 단 *경험적 임계*지 결정론 rule이 아니다(over-rule 금지).
- **협업에는 비용**: curse of coordination — 에이전트 협업은 '인원 추가 = 생산성 증가'가 보장되지 않는다. 멀티는 비용을 정당화할 때만 채택.
- **실패는 root-cause로**: communication/commitment/expectation 세 메커니즘으로 가드를 조직화한다(expectation 우선). 컨텍스트는 per-agent로 격리해 cross-agent 오염을 막는다.
- **baseline 대비 순이득으로 검증**: 마지막 게이트는 'multi라서 좋다'가 아니라 단일 baseline 대비 순이득이 양인가다. 증명 못 하면 단일 권고(REJECT)가 정당한 결과.
- **falsifiable·over-rule 금지**: 모든 휴리스틱은 관찰 가능한 입력으로 적어 반증 가능하게 하되 단정적 법칙으로 과강화하지 않는다. 정량 수치는 vote/CAVEAT와 함께만 인용("개선 N% 보장" 금지).
- **승인 게이트·관찰성**: Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: 컨텍스트 페이로드 조립·압축, AI 출력 평가(judge 구성), 엔지니어용 구현 명세 작성, 단일 자율 반복 루프, 새 하네스 생성, 프로덕션 장애 대응은 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | 멀티 에이전트 결정·설계·검증(분해 평가→아키텍처 결정→협업 가드→baseline 능가 검증) 하네스. deep-research 3-vote 적대 검증 근거 + 2025+ 논문 출처(2512.08296·2601.13295·2604.07911) |
