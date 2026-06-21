# ops-harness

개발 하류의 **'운영' 단계**를 담당하는 프로덕션 운영·인시던트 대응·관측성 멀티 에이전트 하네스.
traces+logs+metrics 3종 텔레메트리를 기반으로 인시던트 전 생애주기를 **AIOpsLab 4단계(Detection L1 →
Localization L2 → Root Cause Analysis L3 → Mitigation L4)** 로 분해해 오케스트레이션한다. 인프라는
중재된 읽기 액션으로만 관측하고 직접 변경하지 않으며, 완화는 사람 승인 후 *제안* 형태로만 낸다(휴먼-인-더-루프).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
ops-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + 단계 요약 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·도구 경계
├── agents/                         # 모두 model: "opus"
│   ├── incident-detector.md        # L1 Detection — 이상 탐지·트리아지(RED/USE, 범인 지목 아님)
│   ├── incident-localizer.md       # L2 Localization — traces 우선으로 범인 후보 국소화
│   ├── root-cause-analyst.md       # L3 RCA — 인과사슬 확정(anti-anchoring 가드레일 + Straight-Shot 폴백)
│   └── mitigation-planner.md       # L4 Mitigation — 완화안 + 위험/롤백/blast radius + DQ 채점(제안·사람 집행)
├── skills/
│   └── ops-harness/
│       ├── SKILL.md                # 오케스트레이터(진입점, Phase 0 substrate 확보 → L1→L4 게이트 진행)
│       └── references/
│           ├── ops-harness-principles.md          # 4단계·역할분리·DQ·RCA 가드레일·anti-pattern
│           └── incident-response-research.md       # 설계 근거 dossier (출처·등급·인용·CAVEAT)
└── evals/
    └── trigger-eval.json           # 트리거 경계 평가 (should_trigger / should_not, 인접 하네스 reciprocal 가드)
```

## 단계 요약

| Phase | 단계 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 텔레메트리 입력 확보 | (오케스트레이터) | substrate 확정·슬러그·Straight-Shot 판정 | 승인 게이트 |
| 1 | L1 Detection | incident-detector | 증상·영향·심각도·시작시각(RED/USE) | 승인(이상 없으면 종료) |
| 2 | L2 Localization | incident-localizer | 범인 후보 순위·traces/metrics/logs 증거 | 승인 |
| 3 | L3 RCA | root-cause-analyst | 인과사슬·확정 근거·경쟁 가설(확정/가설) | 승인 |
| 4 | L4 Mitigation+위험 | mitigation-planner | 완화안·위험/롤백·DQ 점수(사람 집행 대기) | 승인 |

매 Phase 보고: `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?`. 최종: `[Ops 종료] {원인 확정|가설}: {root cause} → 완화 {top1}(DQ {점수}, 사람 집행 대기) → .claude/ops-incidents/{slug}/`

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

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | ops-harness(프로덕션 운영·인시던트 대응·관측성) 멀티 에이전트 하네스. AIOpsLab 4단계(L1–L4) 오케스트레이션 + 4개 전문 에이전트(detector/localizer/root-cause-analyst/mitigation-planner). RCA anti-anchoring 가드레일·Straight-Shot 폴백, DQ 품질 게이트, 중재 읽기 액션·휴먼-인-더-루프. 근거: AIOpsLab(arXiv:2501.06706)[GOLD/SILVER]·역할분리 오케스트레이션(arXiv:2511.15755)[SILVER]·RCA 추론 실패모드(arXiv:2601.22208)[SILVER], CAVEAT 동반 |
| 2026-06-21 | 독립화 | 다른 플러그인 참조를 제거하고 경계/네비게이션 진술을 '이 하네스 범위 밖' 일반 표현으로 일반화해 단독 사용 가능하게 정리(plugin.json description·SKILL.md·README.md·CLAUDE.md). 범위/비범위 의미는 보존 |
