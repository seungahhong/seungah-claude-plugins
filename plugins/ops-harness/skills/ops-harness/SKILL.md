---
name: ops-harness
description: 프로덕션 운영·인시던트 대응 멀티 에이전트 오케스트레이터. traces+logs+metrics 텔레메트리를 기반으로 인시던트 전 생애주기를 AIOpsLab 4단계(Detection → Localization → Root Cause Analysis → Mitigation+위험평가)로 분해해 진행한다. 사용자가 "프로덕션 장애 났는데 어디가 문제인지부터 봐줘", "이 알람/SLO 위반 트리아지하고 근본 원인 분석해줘", "에러율·레이턴시 스파이크 났는데 traces·logs·metrics로 localize하고 완화안 제안해줘", "인시던트 RCA 하고 롤백/완화 조치 위험까지 평가해줘", "온콜인데 무슨 서비스가 범인인지 좁히고 mitigation 플랜 줘", "장애 대응 런북 따라 탐지→국소화→원인→완화로 끌고 가줘", "postmortem용 인과사슬·완화 권고 정리해줘"를 언급하며 *이미 배포된 운영 시스템*의 이상을 탐지·국소화·원인분석·완화하려 할 때 발동한다. 인프라는 중재된 읽기 액션(get_logs/get_metrics/get_traces/exec_shell)으로만 관측하고 직접 변경하지 않으며, 완화는 사람 승인 후 제안 형태로만 낸다. RCA는 anchoring·정체·임의 증거선택·신념 미갱신을 경계하고 단순 케이스엔 Straight-Shot 폴백을 둔다. 매 Phase 승인 게이트·1줄 보고. 발동하지 않는다 — 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선, 검증 가능한 목표를 통과까지 자율 반복으로 완성, 완성된 PR/코드 리뷰·정적 버그 찾기, 코드 착수 전 상류 산출물(기획 DoR·디자인 핸드오프·API 계약·QA 인수조건) 핸드오프 게이트 검수, 기획문서(PRD)·사용자 스토리 작성, 새 하네스/에이전트 팀 생성, 시간 간격 폴링 재실행(native /loop), settings.json 설정 변경. 이들은 *개발-타임 산출물*을 다루므로 *배포 이후 런타임 인시던트*를 다루는 이 하네스의 범위가 아니다.
---

# Ops Harness — 인시던트 전 생애주기 운영 오케스트레이터

*이미 배포된* 프로덕션 시스템의 이상을 **탐지 → 국소화 → 근본 원인 분석 → 완화+위험평가**의 4단계로 끌고 간다.
사람이 매 단계 명령을 외우는 대신, 단계별 전문 에이전트가 텔레메트리를 중재된 읽기 액션으로 관측하고 증거 기반으로
다음 단계 입력을 만든다. 단, **인프라를 직접 바꾸지 않는다** — 완화는 사람 승인 후 *제안* 형태로만 낸다.

## 텔레메트리 substrate (Phase 0에서 확정)

이 하네스는 **로그만이 아니라 세 종류의 신호를 가정**한다(AIOpsLab 근거).

- **traces** — 분산 추적(예: Jaeger). 요청이 서비스 경계를 어떻게 넘는지 → 국소화의 1차 축.
- **logs** — 구조화 로그(예: Filebeat/Logstash). 에러 메시지·스택·이벤트.
- **metrics** — 시계열 지표(예: Prometheus). 에러율·레이턴시·포화도·트래픽(RED/USE).

도구는 **중재된 읽기 액션**으로만 접근한다 — `get_logs` / `get_metrics` / `get_traces` / `exec_shell`(읽기 진단용).
이 하네스의 에이전트는 인프라를 **직접 변경하지 않는다**(스케일·롤백·플래그 토글 등은 모두 mitigation-planner의 *제안*으로,
사람 승인 후 사람이 집행). 이것이 운영 자율화의 미성숙·고난도 특성에 대한 휴먼-인-더-루프 안전장치다.

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'이미 운영 중인 시스템의 인시던트를 진단·완화한다'**. 다음은 명시적으로 범위 밖이다.

- **하네스 자체 진단·개선** — 루트 CLAUDE.md/SKILL.md/agents/hooks의 결함을 trace로 진단·고도화하는 것은 이 하네스의 범위가 아니다.
  ops-harness가 보는 trace는 *프로덕션 텔레메트리*이지 *하네스 실행 trace*가 아니다.
- **검증 가능한 목표를 통과까지 자율 반복** — 작업 산출물을 검증 루프로 완성하는 일은 범위 밖이다. ops-harness는 인시던트 진단·완화 *제안*까지이고, 완화의 자율 반복 적용을 하지 않는다.
- **완성 코드 리뷰·정적 버그 찾기** — PR·diff 리뷰는 범위 밖이다. ops-harness는 *런타임 신호*로 진단하지 소스 diff를 리뷰하지 않는다.
- **상류 산출물 핸드오프 게이트 검수** — 코드 착수 *전* 기획 DoR·디자인 핸드오프·API 계약·QA 인수조건 검수는 개발-타임 활동으로 범위 밖이다. ops-harness는 *배포 이후* 런타임 단계다.
- **기획문서(PRD)·사용자 스토리 작성** — 범위 밖이다.
- **새 하네스/에이전트 팀 생성** — 범위 밖이다. **시간 간격 폴링 재실행** — native `/loop`.

경계가 모호하면 한 질문으로 확인한다 — "*이미 배포돼 돌아가는 시스템의 장애/이상*을 텔레메트리로 진단·완화하는 건가요, 아니면 *개발-타임 산출물(코드·기획·하네스)*을 다루는 건가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **중재된 읽기 전용 관측** — 인프라 직접 변경 금지. 완화는 사람 승인 후 제안. (운영 자율화는 미성숙 영역 — §research)
- **단계 분해(L1→L4)** — Detection → Localization → RCA → Mitigation. 단계를 건너뛰지 않고, 각 단계는 직전 단계의 *증거*만 입력으로 받는다.
- **역할 분리(진단 ≠ 조치계획 ≠ 위험평가)** — 한 에이전트가 진단과 완화 위험평가를 겸하지 않는다(자기 진단을 자기가 정당화하는 편향 차단). 단일 에이전트보다 역할 분리 오케스트레이션이 *실행 가능한* 권고를 낸다(§research, CAVEAT 동반).
- **DQ 품질 게이트** — 완화·권고의 품질을 `DQ = 0.40·타당성(Validity) + 0.30·구체성(Specificity) + 0.30·정확성(Correctness)`로 자가 채점하고 임계 미달이면 보강을 요구한다.
- **RCA 가드레일** — anchoring bias·반복 정체(stalled)·임의적 증거 선택·신념 미갱신을 명시적으로 경계한다. (각 실패모드는 정확도 하락과 *연관* — 인과 아님, §research)
- **Straight-Shot 폴백** — 단순/명백한 케이스나 작은 모델에선 agentic 다단계가 오히려 해로울 수 있다. 증거가 단일 원인을 명백히 가리키면 다단계를 *건너뛰고* 단일 직답으로 RCA를 마친다.
- **휴먼-인-더-루프·관찰성** — 매 Phase 산출물 미리보기 후 승인으로 진행. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.

## 에이전트 팀

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| L1 Detection | `incident-detector` | 텔레메트리에서 이상을 탐지·트리아지(증상·영향범위·심각도·시작시각) |
| L2 Localization | `incident-localizer` | 이상 신호를 traces 우선으로 범인 서비스/컴포넌트로 좁힘 |
| L3 RCA | `root-cause-analyst` | 국소화된 표적의 root cause를 인과사슬로 확정 (anti-anchoring 가드레일 내장) |
| L4 Mitigation+위험 | `mitigation-planner` | 완화안 + 각 안의 위험·롤백·blast radius 평가, DQ 채점 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 진단·위험평가 추론 품질이 인시던트 대응의 질을 좌우한다.

## 참조 문서

- 운영·인시던트 대응 원리·anti-pattern·DQ/가드레일 설계: [references/ops-harness-principles.md](./references/ops-harness-principles.md)
- 설계 근거 연구 dossier(출처·등급·인용·CAVEAT): [references/incident-response-research.md](./references/incident-response-research.md)

## 산출물 배치

기본 `.claude/ops-incidents/{incident-slug}/`(사용자 지정 가능)에 단계별 증거를 둔다. 문서 언어는 **한국어**.

```
.claude/ops-incidents/{incident-slug}/
  detection.md       # L1 — 증상·영향·심각도·텔레메트리 스냅샷
  localization.md    # L2 — 범인 후보·traces/metrics 증거
  rca.md             # L3 — 인과사슬·확정 근거·반증 시도
  mitigation.md      # L4 — 완화안·위험/롤백·DQ 채점·사람 승인 대기
```

---

# 인터랙티브 플로우

## Phase 0 — 텔레메트리 입력 확보 · 승인 게이트

인시던트 컨텍스트와 관측 substrate를 확정한다(에이전트 호출 없이 오케스트레이터가 직접).

1. 사용자에게 인시던트 진입점을 확인한다 — 무슨 증상/알람인가, 영향 서비스·시작 시각·심각도 가설.
2. 사용 가능한 텔레메트리를 확정한다 — **traces / logs / metrics 중 무엇을, 어떤 중재 액션(`get_traces`/`get_logs`/`get_metrics`/`exec_shell`)으로** 읽을 수 있는가. 셋 다 없고 로그만이면 그 한계를 명시한다(국소화 정밀도 저하).
3. `incident-slug`를 도출하고 `.claude/ops-incidents/{slug}/`를 초기화한다.
4. **Straight-Shot 판정**: 증상·영향이 단일 원인을 명백히 가리키고(예: 단일 배포 직후 단일 서비스 100% 5xx) 케이스가 단순하면, L2~L3 다단계 대신 단일 직답 RCA를 제안한다(§research — 단순 케이스에 다단계는 해로울 수 있음).

`[Phase 0] 텔레메트리 substrate {traces/logs/metrics} 확정·슬러그 {slug} — 다음: L1 Detection (또는 Straight-Shot). 진행할까요?`

승인 전에는 다음 단계를 시작하지 않는다.

## Phase 1 — L1 Detection (incident-detector)

```
Agent(
  subagent_type="incident-detector", model="opus",
  prompt="""
  [역할] 프로덕션 텔레메트리에서 이상을 탐지·트리아지한다.
  [입력] 인시던트 진입점: {증상/알람}, 가용 substrate: {traces/logs/metrics + 중재 액션}
  [규칙] 중재된 읽기 액션(get_metrics/get_logs/get_traces/exec_shell)으로만 관측. 인프라 변경 금지.
         RED/USE 관점으로 증상을 정량화하고(에러율·레이턴시·포화·트래픽), 영향 범위·심각도·시작 시각 추정을 증거와 함께 낸다.
  [출력] Detection 리포트(증상·영향·심각도·시작시각·관측 증거). 이상 없음이면 '정상' 판정 + 근거.
  """
)
```

산출물을 `detection.md`로 저장 후 게이트: `[Phase 1] L1 탐지 — {증상·영향·심각도} — 다음: L2 Localization. 진행할까요?`
(이상 없음이면 여기서 종료 보고.)

## Phase 2 — L2 Localization (incident-localizer)

```
Agent(
  subagent_type="incident-localizer", model="opus",
  prompt="""
  [역할] 탐지된 이상을 범인 서비스/컴포넌트로 좁힌다.
  [입력] Detection 리포트 + 가용 substrate.
  [규칙] traces를 1차 축으로(요청 경로의 어느 hop에서 오류/지연이 생기는지), metrics/logs로 교차 확인. 중재 읽기 액션만.
         단일 후보로 단정 말고 가능성 순 후보 목록 + 각 후보의 지지/반증 증거를 낸다(임의 증거선택 방지).
  [출력] Localization 리포트(범인 후보 순위·각 후보의 traces/metrics/logs 증거·배제된 후보와 사유).
  """
)
```

`localization.md` 저장 후 게이트: `[Phase 2] L2 국소화 — 범인 후보 {top1} 외 {n}개 — 다음: L3 RCA. 진행할까요?`

## Phase 3 — L3 RCA (root-cause-analyst · anti-anchoring)

```
Agent(
  subagent_type="root-cause-analyst", model="opus",
  prompt="""
  [역할] 국소화된 표적의 root cause를 인과사슬로 확정한다.
  [입력] Localization 리포트(후보 순위·증거) + 가용 substrate + (있으면) 최근 변경/배포 이력.
  [가드레일(필수)] anchoring bias(첫 가설에 고착) 금지 — 경쟁 가설 ≥2개를 동등하게 검토. 반복 정체(stalled) 감지 시 접근 전환.
         임의적 증거 선택 금지 — 가설을 *반증*할 증거를 먼저 찾는다. 새 증거가 나오면 신념을 갱신한다(belief update).
         단순/명백 케이스면 Straight-Shot(단일 직답)으로 마치고 다단계를 강요하지 않는다.
  [출력] RCA 리포트(증상→원인 인과사슬·확정 근거(trace step/로그/지표 인용)·검토한 경쟁 가설과 기각 사유·확정/가설 라벨).
  """
)
```

`rca.md` 저장 후 게이트: `[Phase 3] L3 RCA — root cause {확정/가설}: {한 줄} — 다음: L4 Mitigation+위험평가. 진행할까요?`

## Phase 4 — L4 Mitigation + 위험평가 (mitigation-planner · DQ 게이트)

```
Agent(
  subagent_type="mitigation-planner", model="opus",
  prompt="""
  [역할] 확정 RCA에 대한 완화안을 제안하고 각 안의 위험을 평가한다(진단과 분리된 역할).
  [입력] RCA 리포트(root cause·확정 근거) + 영향 범위/심각도.
  [규칙] 완화안은 즉시 완화(stop the bleeding)와 근본 수정을 분리해 제시. 각 안에 위험·롤백 절차·blast radius·검증 방법을 붙인다.
         인프라를 직접 바꾸지 않는다 — 모든 안은 *사람 승인 후 사람이 집행*하는 제안. 자동 적용 금지.
         각 안을 DQ = 0.40·타당성 + 0.30·구체성 + 0.30·정확성으로 자가 채점하고 임계 미달이면 보강한다.
  [출력] Mitigation 리포트(권고 순위·각 안의 위험/롤백/검증·DQ 점수·사람 승인 대기 표시).
  """
)
```

`mitigation.md` 저장 후 게이트: `[Phase 4] L4 완화 — 권고 {top1}(DQ {점수}) — 다음: 마무리 보고·사람 집행 승인. 진행할까요?`

## 마무리 — 결과 보고

4단계가 끝나면 다음을 요약 보고한다.

- **인시던트 요약**: 증상 → 국소화된 범인 → root cause(확정/가설) → 권고 완화안.
- **단계별 증거 경로**(detection/localization/rca/mitigation.md).
- **사람 집행 대기 항목**: 완화안은 *제안*이며, 어떤 안을 누가 언제 집행/롤백할지는 사람이 결정한다(휴먼-인-더-루프).
- RCA가 *가설* 라벨이면 추가로 확인할 관측·실험을 함께 제시한다(단정 금지).

보고 형식(최종): `[Ops 종료] {원인 확정|가설}: {root cause} → 완화 {top1}(DQ {점수}, 사람 집행 대기) — 증거 → .claude/ops-incidents/{slug}/`
