# loop-engineering

검증 가능한 목표를 향해 한 작업을 **자율 반복(loop)으로 완성**하는 도메인 무관 멀티 에이전트 하네스.
실행 루프(Goal→Execute→Verify→Diagnose→Improve)와 지속학습 루프(Fail→Investigate→Verify→Distill→Consult)를
결합해, 에이전트가 스스로 검증·진단·개선하고 검증된 교훈을 메모리에 쌓아 같은 실수를 반복하지 않는다.

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/loop-engineering/SKILL.md), 방법론·근거는 [references/](skills/loop-engineering/references/)다.

## Conventions

- **검증기 우선**: 루프는 검증기만큼만 좋다. Phase 0에서 관찰형 성공기준 + *실행 가능한* 검증 방법을 못 박는다.
- **자가 검증**: 통과 판정은 loop-verifier가 증거로 한다. 증거 없는 PASS 금지.
- **재시도 전 진단**: FAIL 시 곧장 재시도하지 않고 failure-analyst가 root cause를 먼저 확정한다(증상 ≠ 원인).
- **에이전트가 개선안을 쓴다**: 다음 반복의 접근을 사람이 아니라 failure-analyst가 작성한다.
- **최소 변경**: 반복당 가장 작은 변경 1개(confound 격리).
- **지속학습 메모리**: 검증된 교훈만 distill해 lessons.md에 쌓고 관련 규칙만 consult한다. raw trace(iterations.jsonl)는 보존(요약 금지).
- **명시적 중단조건**: 통과·최대 반복·무진전·예산. 무한 루프 차단.
- **승인 게이트·관찰성**: Phase 0 Goal Card 승인은 항상. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **stay-the-engineer(사람 통제점)**: 검증·이해(merge 전 diff 읽기, green CI ≠ 구현 완료)·판단(cognitive surrender 자가점검)·병렬 상한(orchestration tax)은 자동화로 넘기지 않는다. 루프가 좋아질수록 이 결함들이 *더 날카로워진다*.
- **factory model(선택 레인)**: 여섯 빌딩블록(automations·worktrees·skills·plugins/connectors·sub-agents·external memory) 중 skills(하네스 자체)·sub-agents·external memory가 *기본 구현*이고(sub-agents는 실제 검증을 실행하는 강한 verifier로), automations·worktrees·connectors는 코어 흐름을 바꾸지 않는 *opt-in 레인*이다(상세 SKILL §8 / principles §8).
- **경계**: 작업 산출물(코드·문서)을 검증 루프로 완성한다. 하네스 자체 진단·개선·새 하네스 생성·기획문서(PRD)·커밋/PR 리뷰·native `/loop`(시간 간격 폴링)은 범위 밖이다.
- 5개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
