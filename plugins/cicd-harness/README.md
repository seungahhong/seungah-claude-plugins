# cicd-harness

**코드 커밋 → 프로덕션**의 전달(delivery) 파이프라인을 오케스트레이션하는 CI/CD·DevOps·릴리스·IaC 멀티 에이전트 하네스입니다.
빌드·테스트 게이트(CI) → 인프라 코드(IaC)·환경 → 릴리스·배포 결정 → 전달 안정성 가드의 4단계로 끌고 가되,
**인프라를 직접 바꾸거나 배포를 자동 실행하지 않습니다** — 어떤 쓰기/apply/deploy도 사람 사전 승인 후 *제안* 형태로만 냅니다(defense-in-depth).

## 전달 파이프라인 4단계

1. **CI 파이프라인** — build/test 게이트와 릴리스 전략을 설계·검수한다(`pipeline-architect`, 제안만).
2. **IaC·환경** — IaC 변경을 **terraform plan(실행 검증) + OPA(policy-as-code)** 결정론적 검증으로 통과시킨다(`iac-reviewer`).
3. **릴리스·배포 결정** — canary 승격·rollback·feature-flag·flaky 해석을 **trust-tier 단계적 자율**로 판단한다(`release-gatekeeper`).
4. **전달 안정성 가드** — AI로 변경량이 느는 만큼 **강한 테스트 자동화·작은 배치(DORA 통제)** 가 갖춰졌는지 점검한다(`delivery-verifier`).

대상 산출물이 없는 단계(예: IaC를 안 다룸)는 Phase 0에서 건너뛸 수 있습니다.

## 세 가지 안전장치

- **defense-in-depth** — 기본 읽기 전용입니다. 파이프라인 YAML 수정·`terraform apply`·배포 트리거 같은 쓰기 작업은 모두 *제안*이며, 어떤 안을 누가 언제 집행/롤백할지는 사람이 사전 승인(safe-outputs) 후 사람이 집행합니다. 에이전트는 인프라를 직접 변경하거나 배포를 자동 실행하지 않습니다(GitHub Agentic Workflows 보안 모델 차용).
- **policy-as-code 결정론적 게이트** — IaC는 LLM의 "괜찮아 보임" 판단으로 통과시키지 않습니다. `terraform plan`(실제 변경 미리보기·실행 검증)과 OPA(정책 강제)처럼 *결정론적으로* 검증 가능한 게이트를 통과해야 합니다(MACOG 차용 — 결정론적 검증 내재화가 단일패스보다 낫다는 방향성).
- **trust-tier 단계적 자율** — 의사결정마다 자율 수준을 위험도로 단계화합니다. 낮은 위험(예: flaky 격리 제안)은 제안 + 자동 게이트로, 높은 위험(예: 프로덕션 배포 승격·전면 rollback)은 사람 필수로(AI-Augmented CI/CD 차용).

## 왜 이렇게 하나 (근거)

DORA 2025[GOLD, dora.dev/cloud.google.com 2025]는 AI 도입이 **전달 처리량·제품 성과와 양(+)**, 그러나 **전달 안정성과 음(-)** 의 관계를 보고합니다 — "통제 시스템이 없으면 변경량 증가가 불안정으로 이어진다(AI=amplifier)". 그래서 이 하네스는 전달 안정성 가드를 마지막 단계로 둡니다.

> **CAVEAT(중요)**: DORA 페이지에서 *그대로 인용 가능한 AI-불안정 통제책은 small batches + robust test automation 두 가지뿐*입니다. "버전관리·느슨한 결합도 AI 통제요소"라거나 "긴밀결합 팀은 AI로 무이득"이라는 통념은 **검증에서 반증되어 사실로 인용하지 않습니다**(신화로만). AI=amplifier 프레이밍과, AI 가치를 증폭하는 7개 역량(platform engineering·version control·small batches·AI-accessible internal data·healthy data ecosystems·clear AI stance·user-centric)은 companion인 DORA AI Capabilities Model[GOLD]에서 인용합니다.

수치·근거의 등급과 한계는 [skills/cicd-harness/references/cicd-harness-research.md](skills/cicd-harness/references/cicd-harness-research.md) 참조.
이 하네스는 '배포 안정성을 N% 올린다'고 약속하지 않습니다 — 위 근거는 *통제 구조의 정당성*을 보일 뿐입니다(baseline-before-target).

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `cicd-harness` 플러그인을 활성화하면,
`cicd-harness` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `cicd-harness` | 오케스트레이터(진입점). 범위·trust-tier 확보(Phase 0) → CI 파이프라인 → IaC·환경 → 릴리스·배포 결정 → 전달 안정성 가드의 4단계를 매 단계 승인 게이트와 함께 진행하며, 각 단계에서 전용 에이전트(pipeline-architect / iac-reviewer / release-gatekeeper / delivery-verifier)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| CI 파이프라인 | `pipeline-architect` | build/test 게이트·릴리스 전략 설계·검수(YAML 변경은 제안만, 직접 적용 안 함) |
| IaC·환경 | `iac-reviewer` | IaC 변경을 terraform plan(실행 검증) + OPA(policy-as-code) 결정론적 게이트로 통과/차단 판정 |
| 릴리스·배포 결정 | `release-gatekeeper` | flaky·rollback·feature-flag·canary 승격을 trust-tier 단계적 자율로 결정(고위험=사람 필수) |
| 전달 안정성 가드 | `delivery-verifier` | DORA 통제(테스트 자동화·작은 배치) 점검 + defense-in-depth 쓰기 작업 승인 목록 정리 |

## 언제 쓰나 / 무엇이 범위 밖인가

**이 하네스를 쓰세요**
- CI 파이프라인(build/test 게이트)을 **설계하거나 검수**하고, 배포 파이프라인·릴리스 전략을 구성하고 싶을 때
- Terraform/IaC 변경을 **terraform plan + OPA 정책**으로 결정론적으로 검증하고 싶을 때
- **카나리 승격·롤백·feature-flag·flaky 테스트** 의사결정을 위험도에 맞춰 게이트하고 싶을 때
- AI로 변경량이 느는데 **전달 안정성 통제(테스트 자동화·작은 배치)** 가 갖춰졌는지 점검하고 싶을 때

**이 하네스의 범위 밖 (다루지 않음)**
- *배포 이후* 프로덕션 장애·SLO 위반·런타임 인시던트 탐지·RCA·완화
- 백엔드/API 코드를 *설계부터 실행 검증까지 구현*
- 검증 가능한 목표를 통과까지 *자율 반복*(빌드 그린 될 때까지 반복)
- 커밋 메시지·PR 리뷰
- 완성된 API 계약 *검수*·breaking change 점검
- 기획문서(PRD)·사용자 스토리
- 프론트엔드 화면·컴포넌트
- 하네스(CLAUDE.md/SKILL.md/agents) 자체 진단·개선
- 새 하네스/에이전트 팀 생성
- *시간 간격* 반복 실행(폴링) — native `/loop` 같은 별도 폴링 메커니즘을 사용

> 한 줄 구분: cicd-harness는 **코드 커밋 → 프로덕션의 전달(delivery) 파이프라인**(CI/CD·릴리스·IaC·배포 게이트)을 다룹니다.
> 배포 *까지* 의 파이프라인·게이트가 이 하네스의 범위이고, 배포 *이후* 의 장애 대응이나 그 안에서 도는 *코드 구현* 은 범위 밖입니다.
> 경계가 모호하면 "배포 *까지* 의 파이프라인/게이트를 다루는 건가요, 배포 *이후* 의 장애를 다루는 건가요?"로 확인하세요.

## 진행 방식

| Phase | 단계 | 핵심 산출물 |
|-------|------|-------------|
| 0 | 범위·trust-tier 확보 | 대상 파이프라인·산출물 유무(CI/IaC/릴리스)·trust-tier·슬러그 — 승인 게이트(없는 단계 건너뜀) |
| 1 | CI 파이프라인 (pipeline-architect) | Pipeline Plan(build/test 게이트·릴리스 전략, 제안) |
| 2 | IaC·환경 (iac-reviewer) | IaC Verdict(terraform plan + OPA 결정론적 통과/실패·정책 위반 목록) |
| 3 | 릴리스·배포 결정 (release-gatekeeper) | Release Decision(승격/보류·trust-tier 배정·safe-outputs 사전승인 대기) |
| 4 | 전달 안정성 가드 (delivery-verifier) | Delivery Guard(DORA 통제 점검·defense-in-depth 쓰기 작업 승인 목록) |

- 매 Phase 후 `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?` 1줄 보고 + 승인 게이트.
- 쓰기/apply/deploy는 *제안*이며 집행은 사람이 합니다(defense-in-depth). 대상 산출물이 없는 단계는 건너뜁니다.

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger — CI 파이프라인·배포 전략·IaC/OPA 검증·canary/rollback/feature-flag/flaky·DORA 통제)와
발동하면 안 되는 경우(should-not-trigger — 프로덕션 장애 RCA·BE 구현·빌드 그린까지 반복·PR 리뷰·완성된 계약 검수·PRD·하네스 진단 등 범위 밖)를
정의해 트리거 정확도와 범위 경계를 점검합니다.
