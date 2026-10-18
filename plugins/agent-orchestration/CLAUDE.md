# agent-orchestration

한 작업을 **여러 에이전트로 병렬화할지·어떻게 협업시킬지**를 판단 규칙으로 결정하고,
그 협업이 **단일 에이전트 baseline을 실제로 능가하는지** 적대적으로 검증하는 도메인 무관 멀티 에이전트 하네스.
핵심 메시지는 **"에이전트를 더 붙인다고 항상 이득이 아니다"** — 성패는 에이전트 수가 아니라 architecture-task alignment가 결정한다.

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/agent-orchestration/SKILL.md), 방법론·근거는 [references/](skills/agent-orchestration/references/)다.

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

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
