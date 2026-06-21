---
name: cicd-harness
description: 코드 커밋→프로덕션 전달(delivery) 파이프라인 오케스트레이터. CI 파이프라인(build/test 게이트) → IaC·환경(terraform plan + OPA policy-as-code 결정론적 검증) → 릴리스·배포 결정(canary 승격·rollback·feature-flag·flaky, trust-tier 단계적 자율) → 전달 안정성 가드(DORA 통제)의 4단계로 진행한다. 사용자가 "CI 파이프라인 설계/검수해줘", "배포 파이프라인·릴리스 전략 구성해줘", "Terraform/IaC 변경 정책 검증(OPA)해줘", "카나리 승격·롤백 전략 게이트 잡아줘", "feature-flag·flaky 테스트 의사결정 도와줘", "AI로 변경량 느는데 전달 안정성 통제(테스트 자동화·작은 배치) 점검해줘", "build/test 게이트로 머지 막는 파이프라인 만들어줘"를 언급하며 *코드 커밋→프로덕션*의 전달 파이프라인(CI/CD·릴리스·IaC·배포 게이트)을 다루려 할 때 발동한다. 기본 읽기 전용이며 어떤 쓰기/apply/deploy도 사람 사전 승인(safe-outputs) 후 제안→사람 집행 형태로만 낸다(defense-in-depth). IaC는 terraform plan + OPA처럼 결정론적 검증으로만 통과시키고, 의사결정은 위험도별 trust-tier로 단계화한다. 매 Phase 승인 게이트·1줄 보고. 발동하지 않는다(범위 밖) — 배포 *이후* 프로덕션 런타임 인시던트 탐지·RCA·완화, 백엔드/API 코드 *구현*, 검증 가능한 목표를 통과까지 자율 반복(빌드 그린까지 반복), 커밋 메시지·PR 리뷰, 완성된 API 계약 검수·breaking change, 기획문서(PRD)·사용자 스토리 작성, 프론트엔드 화면·컴포넌트, 하네스(CLAUDE.md/SKILL.md/agents) 자체 진단·개선, 새 하네스/에이전트 팀 생성, 시간 간격 폴링 재실행, settings.json 설정 변경.
---

# CICD Harness — 코드 커밋→프로덕션 전달 파이프라인 오케스트레이터

코드가 커밋된 뒤 프로덕션에 닿기까지의 **전달(delivery) 파이프라인**을 **CI 파이프라인 → IaC·환경 →
릴리스·배포 결정 → 전달 안정성 가드**의 4단계로 끌고 간다. 사람이 매 게이트를 손으로 엮는 대신, 단계별 전문
에이전트가 파이프라인을 분석·검증하고 증거 기반으로 다음 단계 입력을 만든다. 단, **인프라를 직접 바꾸거나 배포를
자동 실행하지 않는다** — 어떤 쓰기/apply/deploy도 사람 사전 승인 후 *제안* 형태로만 낸다.

## 세 가지 안전장치 (이 하네스의 골격)

- **defense-in-depth** — 기본 읽기 전용. 파이프라인 YAML 수정·`terraform apply`·배포 트리거 같은 쓰기 작업은 모두 *제안*이고, 어떤 안을 누가 언제 집행/롤백할지는 사람이 사전 승인(safe-outputs) 후 사람이 집행한다. 에이전트가 인프라를 직접 변경하거나 배포를 자동 실행하지 않는다(GitHub Agentic Workflows 보안 모델 차용).
- **policy-as-code 결정론적 게이트** — IaC는 LLM의 "괜찮아 보임" 판단으로 통과시키지 않는다. `terraform plan`(실행 검증)과 OPA(정책 강제)처럼 *결정론적으로* 검증 가능한 게이트를 통과해야 한다(MACOG 차용 — 결정론적 검증 내재화가 단일패스보다 낫다는 방향성).
- **trust-tier 단계적 자율** — 의사결정마다 자율 수준을 위험도로 단계화한다. 낮은 위험(예: flaky 격리 제안)은 제안+자동 게이트, 높은 위험(예: 프로덕션 승격·전면 rollback)은 사람 필수(AI-Augmented CI/CD 차용).

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'코드 커밋 → 프로덕션의 전달 파이프라인(CI/CD·릴리스·IaC·배포 게이트)을 다룬다'**. 다음은 명시적으로 범위 밖이다.

- **배포 *이후* 런타임 인시던트** — 프로덕션 장애·SLO 위반·에러율 스파이크의 탐지·RCA·완화는 범위 밖이다. cicd-harness는 배포 *까지*/배포 게이트이고, 배포 *이후* 의 장애 대응은 다루지 않는다.
- **백엔드/API 코드 *구현*** — 서비스 로직·DB 스키마를 설계·구현하는 것은 범위 밖이다. cicd-harness는 *그 코드의* 빌드·테스트·배포 파이프라인을 다룬다.
- **검증 가능한 목표를 통과까지 자율 반복** — "빌드 그린 될 때까지 반복"처럼 자가수정 루프로 완성하는 것은 범위 밖이다. cicd-harness는 파이프라인 *구성·검수·게이트*까지이고, 통과까지 자율 반복하지 않는다.
- **커밋 메시지·PR 리뷰** — 범위 밖(필요하면 별도 커밋/리뷰 워크플로를 사용한다). **완성된 API 계약 검수·breaking change** — 범위 밖(이 하네스는 구현이 아니라 *그 코드의 전달 게이트*를 다룬다).
- **기획문서(PRD)·사용자 스토리** — 범위 밖. **FE 화면·컴포넌트** — 범위 밖.
- **하네스 자체 진단** — 범위 밖. **새 하네스 생성** — 범위 밖. **시간 간격 폴링** — 범위 밖(시간 간격 반복 실행은 native `/loop` 같은 별도 폴링 메커니즘을 쓴다).

경계가 모호하면 한 질문으로 확인한다 — "배포 *까지* 의 파이프라인/게이트(CI/CD·IaC·릴리스)를 다루는 건가요, 아니면 배포 *이후* 의 장애(ops)나 그 안의 *코드 구현*(backend)인가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **defense-in-depth(읽기 전용·사람 사전 승인)** — 인프라 직접 변경·배포 자동 실행 금지. 쓰기/apply/deploy는 모두 사람 사전 승인 후 *제안→사람 집행*.
- **policy-as-code 결정론적 게이트** — IaC는 terraform plan + OPA 같은 결정론적 검증으로만 통과. LLM 판단을 게이트로 두지 않는다(§research).
- **trust-tier 단계적 자율** — flaky·rollback·feature-flag·canary 같은 결정 지점에 위험도별 trust-tier를 적용한다(낮은 위험=제안+자동 게이트, 높은 위험=사람 필수).
- **DORA 통제 프레이밍** — AI는 변경량을 키우는 amplifier이고, 통제(강한 테스트 자동화·작은 배치) 없이는 전달 안정성이 떨어진다(§research, 방향성·인과 단정 아님). delivery-verifier가 이를 점검한다.
- **역할 분리** — 파이프라인 설계 ≠ IaC 결정론적 검증 ≠ 릴리스 결정 ≠ 안정성 가드. 한 에이전트가 설계와 통과 판정을 겸하지 않는다.
- **단계 분해(P1→P4)** — 각 단계는 직전 단계의 *산출물*만 입력으로 받는다. 대상 산출물이 없는 단계(예: IaC 없음)는 Phase 0에서 건너뛸 수 있다.
- **정직성** — 정량 수치는 출처 등급·날짜·CAVEAT와 함께만. '개선 N%' 약속 금지. baseline-before-target. **DORA 통제책은 small batches + robust test automation 두 가지만 사실 인용**하고, 버전관리·느슨한 결합·긴밀결합 무이득은 신화로만(반증됨).
- **승인 게이트·관찰성** — 매 Phase 산출물 미리보기 후 승인으로 진행. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 1 CI 파이프라인 | `pipeline-architect` | build/test 게이트·릴리스 전략 설계·검수(YAML 변경은 제안만) |
| 2 IaC·환경 | `iac-reviewer` | IaC 변경을 terraform plan + OPA 결정론적 게이트로 통과/차단 판정 |
| 3 릴리스·배포 결정 | `release-gatekeeper` | flaky·rollback·feature-flag·canary를 trust-tier 단계적 자율로 결정 |
| 4 전달 안정성 가드 | `delivery-verifier` | DORA 통제(테스트 자동화·작은 배치) 점검 + defense-in-depth 승인 목록 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 결정론적 검증·릴리스 위험 판단의 추론 품질이 전달 안정성을 좌우한다.

## 참조 문서

- 전달 파이프라인 원리·defense-in-depth·policy-as-code·trust-tier·DORA·anti-pattern: [references/cicd-harness-principles.md](./references/cicd-harness-principles.md)
- 설계 근거 연구 dossier(출처·등급·인용·CAVEAT·DORA 반증 nuance): [references/cicd-harness-research.md](./references/cicd-harness-research.md)

## 산출물 배치

기본 `.claude/cicd-delivery/{slug}/`(사용자 지정 가능)에 단계별 산출물을 둔다. 문서 언어는 **한국어**.

```
.claude/cicd-delivery/{slug}/
  pipeline.md        # Phase 1 — CI 파이프라인·릴리스 전략(제안)
  iac.md             # Phase 2 — terraform plan + OPA Verdict
  release.md         # Phase 3 — 릴리스·배포 결정(trust-tier·safe-outputs 대기)
  delivery-guard.md  # Phase 4 — DORA 통제 점검·defense-in-depth 승인 목록
```

---

# 인터랙티브 플로우

## Phase 0 — 범위·trust-tier 확보 · 승인 게이트

전달 파이프라인의 범위와 자율 정책을 확정한다(에이전트 호출 없이 오케스트레이터가 직접).

1. 사용자에게 대상을 확인한다 — 어떤 저장소/파이프라인인가, 기술 스택·환경 흐름(dev→stg→prod).
2. **대상 산출물 유무를 선택**한다 — CI 파이프라인 / IaC(Terraform 등) / 릴리스·배포 결정 중 *무엇을 다루는지*. **없는 단계는 건너뛴다**(예: IaC를 안 쓰면 Phase 2 생략).
3. **trust-tier 정책**을 확정한다 — 어떤 결정을 낮은/중간/높은 위험으로 볼지, 높은 위험(프로덕션 승격·전면 rollback 등)은 사람 필수임을 확인한다.
4. **defense-in-depth 확인** — 이 하네스는 쓰기/apply/deploy를 직접 하지 않고 *제안*만 함을 사용자에게 명시한다(집행은 사람).
5. `{slug}`를 도출하고 `.claude/cicd-delivery/{slug}/`를 초기화한다.

`[Phase 0] 범위 {다룰 단계 CI/IaC/릴리스}·trust-tier 정책 확정·슬러그 {slug} — 다음: Phase 1 CI 파이프라인(또는 다룰 첫 단계). 진행할까요?`

승인 전에는 다음 단계를 시작하지 않는다.

## Phase 1 — CI 파이프라인 (pipeline-architect)

```
Agent(
  subagent_type="pipeline-architect", model="opus",
  prompt="""
  [역할] 코드 커밋→프로덕션 전달의 CI 파이프라인(build/test 게이트)과 릴리스 전략을 설계/검수한다.
  [입력] 대상 저장소/기존 워크플로: {정보}, 스택·환경 흐름: {dev→stg→prod}, 범위·trust-tier: {Phase 0}
  [규칙] 파이프라인을 단계(build·lint·test·scan·package)로 분해하고 각 게이트의 통과 기준·실패 처리·캐싱/병렬화를 명세.
         통과는 실제 실행 결과로(자기보고≠통과). 작은 배치·빠른 피드백을 1급 원칙으로(DORA 통제).
         YAML/워크플로 변경은 *제안* diff로만 — 직접 적용·커밋·푸시 금지(defense-in-depth).
  [출력] Pipeline Plan(단계·게이트 명세·릴리스 전략 골격·작은 배치 점검·제안 변경 diff). 검수 모드면 누락/중복/과결합 지적.
  """
)
```

산출물을 `pipeline.md`로 저장 후 게이트: `[Phase 1] CI 파이프라인 — 게이트 {수}개·릴리스 전략 {골격} — 다음: Phase 2 IaC·환경(없으면 Phase 3). 진행할까요?`

## Phase 2 — IaC·환경 (iac-reviewer · terraform plan + OPA 결정론적 게이트)

(Phase 0에서 IaC를 다루지 않기로 했으면 이 Phase를 건너뛴다.)

```
Agent(
  subagent_type="iac-reviewer", model="opus",
  prompt="""
  [역할] IaC(Terraform 등) 변경을 결정론적 검증으로 통과/차단 판정한다.
  [입력] IaC 변경(plan 산출 또는 diff): {변경}, 적용 환경: {환경}, OPA 정책 번들: {정책 또는 '없음'}
  [규칙(필수)] terraform plan(실행 검증)으로 생성/변경/파괴 리소스를 적고(destroy·force-replace 위험 강조),
         OPA(policy-as-code)로 정책을 강제해 위반 항목별로 판정한다. 둘 다 통과해야 PASS.
         LLM 판단("안전해 보임")을 게이트로 두지 않는다. 결정론적 게이트가 없으면 BLOCKED로 분리해 게이트 구축 요청.
         어떤 리소스도 직접 apply·파괴하지 않는다 — apply는 사람 사전 승인 후 사람 집행 제안(defense-in-depth).
  [출력] IaC Verdict(plan 요약·OPA 위반 목록·위험 변경·드리프트·PASS/FAIL/BLOCKED·apply 안내).
  """
)
```

`iac.md` 저장 후 게이트: `[Phase 2] IaC 검증 — terraform plan {요약}·OPA {통과/위반 n} → {PASS/FAIL/BLOCKED} — 다음: Phase 3 릴리스·배포 결정. 진행할까요?`
(FAIL이면 결정론적 게이트가 차단 — 위반 해소 전 다음 단계로 가지 않는다. BLOCKED면 게이트 구축 후 재검증.)

## Phase 3 — 릴리스·배포 결정 (release-gatekeeper · trust-tier 단계적 자율)

```
Agent(
  subagent_type="release-gatekeeper", model="opus",
  prompt="""
  [역할] canary 승격·rollback·feature-flag·flaky 해석 같은 배포 결정을 trust-tier 단계적 자율로 판단한다.
  [입력] Pipeline Plan + IaC Verdict + 배포 신호(canary 메트릭·테스트·flaky 이력·플래그 상태) + trust-tier 정책: {Phase 0}
  [규칙(필수)] 각 결정에 위험도(blast radius·가역성·영향)를 매겨 trust-tier를 배정한다 —
         낮은 위험=제안+자동 게이트, 중간=사람 확인, 높은 위험(프로덕션 승격·전면 rollback·비가역 플래그)=사람 필수.
         flaky를 통과로 반올림 금지(재현성 확인 후 격리 제안+근본 추적). 불확실하면 가역·저위험 안 우선.
         배포를 자동 실행하지 않는다 — 모든 결정은 사람 사전 승인(safe-outputs) 후 사람 집행 제안(defense-in-depth).
  [출력] Release Decision(결정별 trust-tier·근거·rollback 준비·flaky 처리·safe-outputs 사전 승인 대기 목록).
  """
)
```

`release.md` 저장 후 게이트: `[Phase 3] 릴리스 결정 — {top 결정}(trust-tier {tier}) — 다음: Phase 4 전달 안정성 가드. 진행할까요?`

## Phase 4 — 전달 안정성 가드 (delivery-verifier · DORA 통제 · defense-in-depth)

```
Agent(
  subagent_type="delivery-verifier", model="opus",
  prompt="""
  [역할] 전달 파이프라인에 안정성 통제가 갖춰졌는지 DORA 프레이밍으로 점검하고, 쓰기/배포 제안을 사람 승인 목록으로 정리한다.
  [입력] Pipeline Plan + IaC Verdict + Release Decision + (있으면) 변경량/배포 빈도 신호 + trust-tier·범위: {Phase 0}
  [규칙(필수)] DORA에서 사실 인용 가능한 AI-불안정 통제책은 small batches + robust test automation 두 가지뿐 —
         이 둘을 핵심 축으로 점검한다(강한 테스트 자동화: 게이트가 변경을 실제로 막는가; 작은 배치: 배포 단위가 작고 자주인가).
         AI=amplifier 프레이밍으로 변경량 대비 통제가 비례하는지 본다(방향성·인과 단정 아님).
         '버전관리·느슨한 결합이 AI 통제요소'·'긴밀결합 팀 무이득'은 반증된 신화 → 사실 인용 금지(신화로만).
         defense-in-depth 최종 게이트로 Phase 1~3의 쓰기/apply/deploy 제안을 사람 사전 승인 목록으로 정리(자동 집행 없음 확인).
         '개선 N%' 약속 금지(baseline-before-target). 인프라 직접 변경 금지(점검·정리 전용).
  [출력] Delivery Guard(테스트 자동화·작은 배치 점검·amplifier 위험·승인 목록·보완 권고·신화 분리).
  """
)
```

`delivery-guard.md` 저장 후 게이트: `[Phase 4] 안정성 가드 — 통제 {충분/결핍}·승인 대기 {n}건 — 다음: 마무리 보고·사람 집행 승인. 진행할까요?`

## 마무리 — 결과 보고

다룬 단계가 끝나면 다음을 요약 보고한다.

- **파이프라인 요약**: CI 게이트 → IaC 결정론적 검증 결과 → 릴리스 결정(trust-tier) → 안정성 통제 점검.
- **단계별 산출물 경로**(pipeline/iac/release/delivery-guard.md — 다룬 단계만).
- **사람 사전 승인 대기 목록**: 모든 쓰기/apply/deploy는 *제안*이며, 어떤 안을 누가 언제 집행/롤백할지는 사람이 결정한다(defense-in-depth).
- IaC가 **BLOCKED**(결정론적 게이트 부재)이면 게이트 구축 권고를, 통제가 **결핍**이면 강한 테스트 자동화·작은 배치 보완 방향을 함께 제시한다(수치 약속 금지).

보고 형식(최종): `[CICD 종료] {파이프라인·게이트 요약} → 배포 결정 {승격|보류}(trust-tier {tier}, 사람 집행 대기) — 산출물 → .claude/cicd-delivery/{slug}/`
