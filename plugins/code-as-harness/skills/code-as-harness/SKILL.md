---
name: code-as-harness
description: 코드를 단순 산출물이 아니라 실행 가능(executable)·검사 가능(inspectable)·상태 보존(stateful)한 운영 기반으로 다루고, 한 번의 거버넌스된 Plan→Execute→Verify 제어 루프로 코드 변경을 안전하고 검증 가능하게 수행하는 도메인 무관 멀티 에이전트 하네스. 사용자가 "코드를 실행·검증 가능한 하네스로 다뤄서 계획→실행→검증으로 안전하게 바꿔줘", "계획을 변경 계약으로 못 박고 결정적 센서(테스트·빌드·린트)로 검증해줘", "비가역·안전임계 행동은 사람 승인 게이트로 막고 가역 행동만 진행해줘", "자기보고 말고 실제 실행 결과로 검증하고 reward-hacking(테스트 약화) 가드해줘", "부분 센서면 PASS 단정 말고 UNVERIFIED로 처리해줘", "실행 trace 근거로 실패 진단하고 통과한 건 안 깨게 regression-free로 다음 수정 제안해줘"를 언급하며 코드 변경을 거버넌스된 실행 사이클로 수행하려 할 때 발동한다. 작업을 계획 계약으로 변환하고(Phase 0, 승인 게이트), 권한·샌드박스 경계에서 최소 변경을 적용하며 안전임계는 사람 게이트(Phase 1), 결정적 센서를 실제로 돌려 조항별로 검증하고 reward-hacking·불완전 피드백을 가드하며(Phase 2), trace로 진단하고 regression-free 수정안과 CONVERGED/ITERATE/ESCALATE를 결정한다(Phase 3). 근거는 arXiv:2605.18747 'Code as Agent Harness'(코드=operational substrate, Plan-Execute-Verify 제어 루프, sandboxed·permissioned 실행, 결정적 센서+사람 게이트, open challenge=가드레일). 발동하지 않는다 — 검증 가능한 목표로 통과까지 자율 반복하고 교차세션 학습 메모리에 distill하는 단일 자율 반복 루프, 백엔드/API 환경 provisioning을 1급으로 둔 구현, 실행 가능 명세를 source of truth로 작성하는 일, 여러 AI 에이전트로 병렬화할지·토폴로지 결정, 모델 컨텍스트 페이로드 조립·압축, AI 출력 judge 구성·평가, 하네스 자체 결함 진단·개선, 상류 산출물 핸드오프 게이트 검수, 프로덕션 인시던트 대응, PRD 작성·커밋/PR·settings 설정.
---

# Code as Agent Harness — 거버넌스된 Plan→Execute→Verify 오케스트레이터

코드를 **운영 기반(operational substrate)** 으로 다룬다 — *executable*(출력이 형식적으로 검증 가능한 연산), *inspectable*
(중간 계산이 구조화된 trace), *stateful*(진행 상태가 영속). 이 기반 위에서 **거버넌스된 Plan→Execute→Verify 제어 사이클
한 번**을 운영해 코드 변경을 *안전하고 검증 가능하게* 수행한다.

핵심 메시지: **"코드는 산출물이 아니라 에이전트가 추론·행동·검증하는 실행 기반이다 — 계획은 변경 계약이고, 실행은 권한·
샌드박스로 게이트되며, 검증은 자기보고가 아니라 결정적 센서(실행)로 한다."**

> 이 하네스는 *한 번의 거버넌스된 제어 사이클*을 운영한다(필요 시 사람 승인 하에 1회 더 ITERATE). *통과까지 무한
> 자율 반복하거나 교차세션 학습 메모리에 distill하지 않는다* — 그건 자율 반복 도메인이다(아래 경계).

## 무엇을 하는가 (네 단계)

1. 작업을 *변경 계약*으로 못 박는가? — 의도·센서·행동 위험 (Phase 0 — Plan Contract)
2. 변경을 *권한·샌드박스 경계*에서 적용하고 안전임계는 사람 게이트하는가? (Phase 1 — Permissioned Execute)
3. *결정적 센서를 실제로 돌려* 조항별로 검증하고 게이밍·불완전 피드백을 가드하는가? (Phase 2 — Execution Verify)
4. *trace로 진단*하고 regression-free 수정·수렴을 결정하는가? (Phase 3 — Telemetry Diagnose & Converge)

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'코드를 실행·검증 가능한 하네스로 다루는 거버넌스된 Plan→Execute→Verify 제어 사이클'** 에 특화한다. 다음은 명시적으로 범위 밖이다.

- **통과까지 자율 반복 + 교차세션 학습** — 검증 가능한 목표로 *통과까지 한 흐름으로 반복*하고 교훈을 *메모리에 distill*해
  같은 실수를 막는 것은 자율 반복 도메인이다. 이 하네스는 *한 번의 거버넌스된 사이클*(필요 시 사람 승인 하 1회 ITERATE)이지
  *수렴까지의 자율 루프·지속학습 메모리*가 아니다.
- **백엔드/API 구현 + 환경 provisioning 1급** — 서비스 경계·데이터 모델 구현과 *환경 구성을 독립 1급 단계*로 두는 것은
  백엔드 구현 도메인이다. 이 하네스는 *도메인 무관*하고 환경 구성을 별도 단계로 1급화하지 않는다(실행은 주어진 권한·샌드박스 경계 안).
- **실행 가능 명세를 source of truth로 작성** — *명세를 1차 산출물*로 작성하고 코드를 그로부터 생성하는 것은 명세 우선
  도메인이다. 이 하네스의 *계획 계약*은 한 사이클의 *변경 계약*이지 영속하는 source-of-truth 명세가 아니다.
- **여러 AI 에이전트 병렬화·토폴로지 결정** — single/multi·centralized/independent 같은 *AI↔AI* 오케스트레이션 결정은 멀티
  에이전트 오케스트레이션 도메인이다(서베이 Layer 3 scaling — 본 하네스는 단일 사이클로 한정).
- **컨텍스트 페이로드 조립·압축** — 모델 컨텍스트에 *무엇을 넣을지*는 컨텍스트 설계 도메인이다.
- **AI 출력 평가(judge 구성)** — LLM-as-a-Judge·benchmark validity는 평가 도메인이다. 이 하네스의 검증은 *계약 센서의 실제
  실행*이지 산출물 채점 시스템 구축이 아니다.
- **하네스 자체 결함 진단·개선** — 루트 CLAUDE.md/스킬 등 *하네스 자체*를 trace로 진단·개선하는 것은 메타 도메인이다. 이
  하네스의 텔레메트리 진단은 *작업의 실행 trace*를 읽지 *하네스 자산*을 고치지 않는다.
- **상류 산출물 핸드오프 게이트 검수 · 프로덕션 인시던트 대응 · PRD 작성 · 커밋/PR · settings 설정** — 각각 핸드오프 리뷰·
  운영·기획·git·설정 도메인이다.

경계가 모호하면 한 질문으로 확인한다 — "*코드 변경을 거버넌스된 Plan→Execute→Verify 사이클로 안전·검증 가능하게
수행*하려는 건가요, 아니면 *다른 것*(통과까지 자율 반복·환경 구성 구현·실행 명세 작성·에이전트 병렬화·컨텍스트 조립·
산출물 채점·하네스 진단·상류 핸드오프 검수·장애 대응)인가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **코드 = 운영 기반** — executable·inspectable·stateful. 검증은 의견이 아니라 *실행*이고, 진행·진단은 *구조화된 trace*다(references §1).
- **계획 = 변경 계약** — 실행 전에 *의도한 변경·판정 센서·행동 위험*을 못 박는다. 사전 약속이 drift를 탐지 가능하게 한다(references §2).
- **권한·샌드박스 실행** — 가역 우선, 안전임계/비가역(삭제·마이그레이션·스키마·네트워크·시크릿·프로덕션)은 *실행 전 사람 게이트*(references §3·§9).
- **실행 기반 검증(자기보고 불신)** — 결정적 센서를 *실제로 돌려* 조항별로 증거와 함께 판정한다(references §4).
- **reward-hacking·verifier-gaming 가드** — 테스트 약화·skip·기대값 맞추기·하드코딩·형식 우회 금지. 약한 센서 통과를 PASS로 단정하지 않는다(references §5).
- **불완전 피드백 정직성** — 부분 센서·사각이면 PASS 단정 금지, *UNVERIFIED*로 confidence 강등. 증거 없는 PASS 없음. 최종 성공 너머 불변식·부작용도 본다(references §6).
- **검사 가능 trace = 텔레메트리 substrate** — 실패 진단은 추측이 아니라 *trace 인용*으로(references §7).
- **regression-free 개선** — 차기 수정이 통과한 것을 깨지 않는다. 무진전이면 ESCALATE(references §8).
- **사람 감독은 안전임계에 집중(전수 승인 아님)** — 가역은 진행, 안전임계·계획계약·최종 수렴 판정에 사람 게이트(references §9).
- **정직성·falsifiability** — 서베이는 개념 프레임(벤치마크 결과 아님), 인접 논문 기법은 출처에만 귀속, 'several-fold'는 세팅값, 반박된 AgentFlow 4-phase 미사용, "개선 N% 보장" 금지(references §10).
- **관찰 가능성·승인** — Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다(references §11).

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Plan Contract | `plan-contractor` | 작업 → 변경 계약(의도한 변경·판정 센서·행동 위험 분류) |
| 1 Permissioned Execute | `permissioned-executor` | 권한·샌드박스 경계에서 최소 변경 적용·가역 우선·안전임계 사람 게이트·실행 trace 적재 |
| 2 Execution Verify | `execution-verifier` | 결정적 센서 실제 실행·조항별 PASS/FAIL/UNVERIFIED·reward-hacking·불완전 피드백·최종 너머 가드 |
| 3 Telemetry Diagnose & Converge | `telemetry-diagnostician` | trace 인용 진단·regression-free 수정안·무진전 감지·CONVERGED/ITERATE/ESCALATE |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 계획 계약·위험
분류·실행 기반 검증·trace 진단의 품질이 변경의 안전성과 검증 신뢰성을 좌우한다.

## 참조 문서

- 원칙·anti-pattern·결정 신호표: [references/code-as-harness-principles.md](./references/code-as-harness-principles.md)
- 설계 근거 연구 dossier(출처·인용·vote·CAVEAT·반박된 주장·방법론): [references/code-as-harness-research.md](./references/code-as-harness-research.md)

---

# 인터랙티브 플로우

## Phase 0 — 계획 계약 (Plan Contract) · 승인 게이트

`plan-contractor`를 호출해 작업을 *변경 계약*으로 변환한다 — 의도한 변경·판정 센서·행동 위험 분류.

```
Agent(
  subagent_type="plan-contractor", model="opus",
  prompt="""
  [역할] 작업을 변경 계약(Plan Contract)으로 변환한다.
  [입력] 작업/변경 맥락: {사용자 발화} / (선택) 대상 저장소·테스트·빌드·린트 구성.
  [규칙] 의도한 변경을 조항화하고(어떤 파일·동작·불변식을 바꾸고 무엇을 바꾸지 않을지) 최소 변경 단위로 적는다.
         성공을 판정할 결정적 센서(테스트·빌드·타입·린트·실행/스모크)를 미리 명시하고 각 조항에 '무엇이 반증인가'를 단다.
         센서 없음/약함은 센서 격차로 표시한다. 각 행동을 가역 vs 안전임계/비가역(삭제·마이그레이션·스키마·네트워크 egress·
         시크릿·프로덕션)으로 분류해 안전임계엔 '실행 전 사람 게이트 필요'를 단다. 변경을 직접 적용하거나 센서를 돌리지
         않는다(계약만). 관찰 가능한 근거로만 적고 수치를 발명하지 않는다(모르면 '미상').
  [출력] Plan Contract(의도한 변경·판정 센서·행동 위험 분류·미상/가정).
  """
)
```

Plan Contract를 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 계획 계약 완료 — 다음: 권한 실행. 진행할까요?`

승인 전에는 다음 단계를 시작하지 않는다(잘못된 계약으로 잘못된 변경·검증을 하지 않기 위함).

## Phase 1 — 권한 실행 (Permissioned Execute)

`permissioned-executor`를 호출해 계약을 권한·샌드박스 경계에서 실현하고 실행 trace를 남긴다.

```
Agent(
  subagent_type="permissioned-executor", model="opus",
  prompt="""
  [역할] Plan Contract를 권한·샌드박스 경계 안에서 실현하고 구조화된 실행 trace를 남긴다.
  [입력] Plan Contract: {Phase 0 산출} / (선택) 권한·샌드박스 제약.
  [규칙] 계약 조항을 하나씩 최소 변경으로 실현한다(over-reach 금지). 같은 결과면 더 가역적 경로를 택한다(가역 우선).
         계약이 안전임계/비가역으로 분류한 행동(삭제·마이그레이션·스키마·네트워크 egress·시크릿·프로덕션)은 실행 전 사람
         승인을 받는다(전수 승인이 아니라 안전임계에 집중 — 가역은 진행). 각 단계를 계획조항→diff/행동→관측 피드백으로
         실행 trace에 남겨 Phase 2·3가 직접 조회하게 한다. 센서를 돌려 판정하지 않는다(Phase 2의 일). 테스트 약화·하드코딩
         으로 통과를 만들지 않는다. drift 발견 시 임의 진행하지 않고 계약 수정 필요로 표시한다.
  [출력] Execution Trace + 적용 요약(적용/보류/미착수·사람 게이트 상태·미상/가정).
  """
)
```

1줄 보고: `[Phase 1] 권한 실행 완료(또는 안전임계 승인 대기) — 다음: 실행 검증. 진행할까요?`

> 안전임계 행동에 사람 승인이 필요하면 *그 행동을 보류*하고 승인을 요청한 뒤 진행한다(비가역 손상 금지).

## Phase 2 — 실행 검증 (Execution Verify)

`execution-verifier`를 호출해 계약의 결정적 센서를 실제로 돌려 조항별로 검증한다.

```
Agent(
  subagent_type="execution-verifier", model="opus",
  prompt="""
  [역할] Plan Contract의 결정적 센서를 실제로 실행해 계약 조항별로 부합을 판정한다.
  [입력] Plan Contract(센서·반증 조건): {Phase 0} / Execution Trace: {Phase 1} / (선택) 센서 실행 환경.
  [규칙] 센서(테스트·빌드·타입·린트·실행/스모크)를 실제로 돌리고 조항별로 PASS/FAIL/UNVERIFIED를 센서 출력 인용과 함께
         판정한다. 자기보고('다 됐다')를 불신한다. reward-hacking·verifier-gaming(테스트 삭제·약화·skip·기대값 맞추기·입력
         하드코딩·형식 우회)을 위반으로 잡고, extensional correctness만 보는 약한 센서 통과를 PASS로 단정하지 않는다.
         부분 센서·사각이면 PASS 단정 말고 UNVERIFIED로 confidence를 강등하며 무엇이 안 덮였는지 명시한다(증거 없는 PASS
         금지). 최종 task 성공만 보지 말고 불변식·부작용·인접 회귀도 본다. 코드를 고치지 않는다(검증 전용).
  [출력] Verification Report(조항별 판정+센서 증거·reward-hacking 가드·UNVERIFIED 영역·최종 너머·종합 PASS/FAIL/UNVERIFIED).
  """
)
```

1줄 보고: `[Phase 2] 실행 검증 완료(종합 {PASS|FAIL|UNVERIFIED}) — 다음: 텔레메트리 진단·수렴. 진행할까요?`

## Phase 3 — 텔레메트리 진단·수렴 (Telemetry Diagnose & Converge)

`telemetry-diagnostician`을 호출해 trace로 진단하고 regression-free 수정·수렴을 결정한다.

```
Agent(
  subagent_type="telemetry-diagnostician", model="opus",
  prompt="""
  [역할] 실행 trace와 Verification Report를 최적화 substrate로 읽어 진단하고 수렴을 결정한다.
  [입력] Execution Trace: {Phase 1} / Verification Report: {Phase 2} / Plan Contract: {Phase 0}.
  [규칙] FAIL/UNVERIFIED의 root cause를 trace 인용(어느 조항·diff·센서 출력)으로 진단한다(추측 금지). 차기 계획계약
         수정안은 통과한 센서를 회귀시키지 않음을 명시 점검한다(regression-free·최소 개입). 같은 실패 반복/진동이면
         ITERATE 대신 ESCALATE. CONVERGED(전부 PASS)/ITERATE(수정 후 Phase 1부터 1사이클 더, 사람 승인 하)/ESCALATE
         (무진전·안전임계 비가역·UNVERIFIED 지속은 사람)을 결정한다. 수정안이 센서를 약화하거나 최종만 맞추는 shortcut을
         권하지 않는다. 코드를 직접 고치지 않는다(진단·제안만).
  [출력] Diagnosis & Convergence(trace 인용 진단·regression-free 수정안·무진전 점검·결정 CONVERGED/ITERATE/ESCALATE·미상).
  """
)
```

1줄 보고: `[Phase 3] 진단·수렴 결정 완료({CONVERGED|ITERATE|ESCALATE}) — 종합 보고로 마무리할까요?`

> **ITERATE 결정 시**: 사람 승인 하에 수정안을 반영해 Phase 1부터 *한 사이클 더* 돈다. 무한 반복이 아니라 *명시적 결정·
> 사람 게이트*가 매 사이클을 통과시킨다. 무진전이면 ESCALATE한다.

## 마무리 — 종합 보고

플로우가 끝나면 네 단계 산출물을 하나로 종합 보고한다.

- **계획 계약**: 의도한 변경 조항·판정 센서·행동 위험 분류(가역/안전임계).
- **실행**: 권한·샌드박스 경계 적용·가역 우선·안전임계 사람 게이트 결과·실행 trace.
- **검증**: 조항별 PASS/FAIL/UNVERIFIED + 센서 증거·reward-hacking 가드·불완전 피드백·최종 너머.
- **진단·수렴**: trace 인용 root cause·regression-free 수정안·결정(CONVERGED/ITERATE/ESCALATE).
- **남은 불확실성·가정**: UNVERIFIED로 남은 부분·센서 격차·사람 판단 필요 항목.

보고 형식(최종): `[Code-as-Harness] 계획계약 {조항수} · 실행 {권한/샌드박스·안전임계 게이트} · 검증 {PASS/FAIL/UNVERIFIED} · 결정 {CONVERGED|ITERATE|ESCALATE}`

> 정직성: 대상 서베이(arXiv:2605.18747)는 개념 프레임으로 인용했고(벤치마크 결과 아님), 인접 논문 기법은 각 출처에만
> 귀속했으며, 'several-fold' 민감도는 특정 세팅값으로 한정하고 반박된 AgentFlow 4-phase 루프는 쓰지 않으며 "개선 N%
> 보장"을 쓰지 않는다. 상세는 research dossier 참조.
