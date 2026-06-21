# ops-harness

개발 하류의 **'운영' 단계**를 담당하는 프로덕션 운영·인시던트 대응·관측성 멀티 에이전트 하네스입니다.
이미 배포돼 돌아가는 시스템의 이상을, traces+logs+metrics 텔레메트리를 기반으로 **탐지 → 국소화 →
근본 원인 분석 → 완화+위험평가**의 4단계로 끌고 갑니다. 단, **인프라를 직접 바꾸지 않습니다** —
관측은 중재된 읽기 액션으로만 하고, 완화는 사람 승인 후 *제안* 형태로만 냅니다(휴먼-인-더-루프).

## 인시던트 생애주기 4단계 (AIOpsLab L1–L4)

1. **L1 Detection** — 정상에서 벗어났는가? 무엇이·언제부터·얼마나? (트리아지)
2. **L2 Localization** — 어디서? traces 우선으로 범인 서비스/컴포넌트로 좁힘.
3. **L3 RCA** — 왜? root cause를 인과사슬로 확정(anti-anchoring 가드레일).
4. **L4 Mitigation** — 어떻게 멈추나? 완화안 + 위험·롤백·blast radius 평가(사람 집행 제안).

## 텔레메트리 substrate · 도구 경계

세 종류의 신호를 가정합니다 — **traces**(예: Jaeger) + **logs**(예: Filebeat/Logstash) + **metrics**(예: Prometheus).
도구는 **중재된 읽기 액션**으로만 접근합니다 — `get_logs` / `get_metrics` / `get_traces` / `exec_shell`(읽기 진단).

> **인프라를 직접 변경하지 않습니다.** 스케일·롤백·플래그 토글 같은 조치는 모두 mitigation-planner의 *제안*이며,
> 어떤 안을 누가 언제 집행/롤백할지는 사람이 결정합니다. 운영 자율화는 아직 미성숙·고난도 영역이기 때문입니다(연구 근거).

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `ops-harness` 플러그인을 활성화하면,
`ops-harness` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `ops-harness` | 오케스트레이터(진입점). 텔레메트리 substrate 확보(Phase 0) → L1 Detection → L2 Localization → L3 RCA → L4 Mitigation+위험평가의 4단계를 매 단계 승인 게이트와 함께 진행하며, 각 단계에서 전용 에이전트(incident-detector / incident-localizer / root-cause-analyst / mitigation-planner)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| L1 Detection | `incident-detector` | RED/USE로 이상 탐지·트리아지(증상·영향·심각도·시작시각). 범인 지목은 안 함 |
| L2 Localization | `incident-localizer` | traces 우선으로 범인 후보 국소화(가능성 순 + 지지/반증 증거). 원인 단정은 안 함 |
| L3 RCA | `root-cause-analyst` | root cause 인과사슬 확정. anchoring·정체·임의 증거·신념 미갱신 가드레일 + Straight-Shot 폴백 |
| L4 Mitigation+위험 | `mitigation-planner` | 완화안 + 위험/롤백/blast radius + 효과검증, DQ 채점(제안·사람 집행) |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- *이미 배포된* 프로덕션 시스템에 **장애/알람/SLO 위반**이 났고, 어디가 문제인지부터 좁히고 싶을 때
- 에러율·레이턴시 스파이크를 **traces·logs·metrics로 국소화**하고 **RCA·완화안**까지 받고 싶을 때
- 인시던트 **postmortem용 인과사슬·완화 권고**를 정리하고 싶을 때

**이 하네스 범위 밖 (다른 도구가 필요한 일)**
- 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선하는 일
- 검증 가능한 목표를 통과까지 자율 반복으로 완성하는 일
- 완성된 PR/코드 리뷰·정적 버그 찾기
- 코드 착수 *전* 상류 산출물(기획 DoR·디자인 핸드오프·API 계약·QA 인수조건) 핸드오프 게이트 검수
- 기획문서(PRD)·사용자 스토리 작성
- 새 하네스/에이전트 팀 생성
- *시간 간격* 반복 실행(폴링) → native `/loop`

> 한 줄 구분: ops-harness는 **배포 *이후* 런타임 신호**로 인시던트를 다룹니다. 코드 diff·기획·하네스 같은
> *개발-타임 산출물*을 다루는 게 아닙니다. 경계가 모호하면 "이미 돌아가는 시스템의 장애를 텔레메트리로
> 진단·완화하는 건가요?"로 확인하세요.

## 진행 방식

| Phase | 단계 | 핵심 산출물 |
|-------|------|-------------|
| 0 | 텔레메트리 입력 확보 | substrate 확정(traces/logs/metrics + 중재 액션)·슬러그·Straight-Shot 판정 — 승인 게이트 |
| 1 | L1 Detection | 증상·영향·심각도·시작시각(RED/USE) — 이상 없으면 종료 |
| 2 | L2 Localization | 범인 후보 순위 + 각 후보 증거(traces 우선) |
| 3 | L3 RCA | 인과사슬·확정 근거·경쟁 가설(확정/가설 라벨) |
| 4 | L4 Mitigation+위험 | 완화안·위험/롤백/blast radius·DQ 점수(사람 집행 대기) |

- 매 Phase 후 `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?` 1줄 보고 + 승인 게이트.
- 완화안은 *제안*이며 집행은 사람이 합니다(휴먼-인-더-루프).

## 품질·정직성 게이트

- 완화·권고 품질: `DQ = 0.40·타당성 + 0.30·구체성 + 0.30·정확성`. 임계 미달이면 보강.
- 정량 수치는 출처 등급·날짜·CAVEAT와 함께만 인용하고 '개선 N%'를 약속하지 않습니다. 설계 근거와 한계는
  [skills/ops-harness/references/incident-response-research.md](skills/ops-harness/references/incident-response-research.md) 참조.

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger — 프로덕션 장애·관측성·RCA·완화)와
발동하면 안 되는 경우(should-not-trigger — 하네스 진단/개선·검증 루프·코드 리뷰·상류 핸드오프 게이트·PRD·폴링)를
정의해 트리거 정확도와 인접 하네스 경계를 점검합니다.
