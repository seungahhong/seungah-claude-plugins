# ops-harness

개발 하류의 **'운영' 단계**를 담당하는 프로덕션 운영·인시던트 대응·관측성 멀티 에이전트 하네스.
traces+logs+metrics 3종 텔레메트리를 기반으로 인시던트 전 생애주기를 **AIOpsLab 4단계(Detection L1 →
Localization L2 → Root Cause Analysis L3 → Mitigation L4)** 로 분해해 오케스트레이션한다. 인프라는
중재된 읽기 액션으로만 관측하고 직접 변경하지 않으며, 완화는 사람 승인 후 *제안* 형태로만 낸다(휴먼-인-더-루프).

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/ops-harness/SKILL.md), 방법론·근거는 [references/](skills/ops-harness/references/)다.

## Conventions

- **읽기 전용·중재 관측**: `get_logs`/`get_metrics`/`get_traces`/`exec_shell`(읽기)로만 접근. 인프라 직접 변경 금지. 완화는 사람 승인 후 제안.
- **단계 분해(L1→L4)**: 각 단계는 직전 단계의 *증거*만 입력으로 받고 건너뛰지 않는다(단순 케이스만 Phase 0 Straight-Shot 예외).
- **역할 분리**: 진단(L1–L3) ≠ 조치계획·위험평가(L4). 한 에이전트가 진단과 완화 정당화를 겸하지 않는다.
- **DQ 품질 게이트**: 완화·권고는 `DQ=0.40·타당성+0.30·구체성+0.30·정확성`로 자가 채점, 임계 미달 보강.
- **RCA 가드레일**: anchoring·정체·임의 증거선택·신념 미갱신을 경계. 단순 케이스/작은 모델엔 Straight-Shot 폴백.
- **휴먼-인-더-루프**: 운영 자율화는 미성숙 영역(§research) — 매 Phase 승인 게이트, 완화는 사람 집행. 요청되지 않은 사이드 에이전트·중복 실행 금지.
- **정직성**: 정량 수치는 출처 등급·CAVEAT와 함께만 인용. '개선 N%' 약속 금지. 역할분리 100%/1.7%·RCA 15%p/45%는 한계 동반 인용(일반화·인과 단정 금지).
- **경계**: 하네스 자체 진단·개선·검증 루프 완성·완성 코드 리뷰·상류 핸드오프 게이트·PRD 작성은 범위 밖(개발-타임 산출물). ops-harness는 *배포 이후 런타임* 인시던트에 특화.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
