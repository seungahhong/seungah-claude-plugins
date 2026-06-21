# CICD Harness — 원리 · 4단계 분해 · defense-in-depth/policy-as-code/trust-tier · anti-pattern

> 이 문서는 cicd-harness 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.
> 정량 수치는 [cicd-harness-research.md](./cicd-harness-research.md)의 등급·출처·CAVEAT와 함께만 인용한다.

## 1. 무엇이 cicd-harness인가

개발 워크플로우는 *코드를 작성하면* 절반이고, 그 코드가 안전하게 **프로덕션에 닿기까지의 전달(delivery)** 이
나머지 절반이다. cicd-harness는 **코드 커밋 → 프로덕션**의 전달 파이프라인 — CI 파이프라인(build/test 게이트)·
IaC·환경·릴리스·배포 게이트 — 을 오케스트레이션하는 것을 담당한다.

핵심 전제는 세 가지다.

1. **전달은 게이트의 사슬이다** — 코드 구현이 아니라 *그 코드가 통과해야 하는 게이트*(빌드·테스트·정책·릴리스 결정)가 1차 대상이다.
2. **AI는 amplifier다** — AI가 변경량·배포 빈도를 키우면 통제 시스템 없이는 *전달 안정성*이 떨어진다(§research). 그래서 이 하네스는 통제(테스트 자동화·작은 배치)를 마지막 단계로 못 박는다.
3. **운영 자율화는 위험하므로 defense-in-depth로 둔다** — 에이전트가 인프라를 직접 바꾸거나 배포를 자동 실행하면 잘못된 변경을 빠르게 증폭한다. 따라서 이 하네스는 *완전 자율*이 아니라 *읽기 전용 + 사람 사전 승인* 으로 설계한다 — 설계·검증·결정 *제안*까지가 에이전트의 일이고, 쓰기/apply/deploy 집행은 사람이 한다.

## 2. 전달 파이프라인 4단계

이 하네스의 오케스트레이션 골격은 코드 커밋→프로덕션의 4단계다.

1. **Phase 1 CI 파이프라인** — build/test 게이트와 릴리스 전략 설계·검수(pipeline-architect, 제안만).
2. **Phase 2 IaC·환경** — IaC 변경을 terraform plan + OPA 결정론적 게이트로 통과/차단(iac-reviewer).
3. **Phase 3 릴리스·배포 결정** — canary·rollback·feature-flag·flaky를 trust-tier 단계적 자율로 결정(release-gatekeeper).
4. **Phase 4 전달 안정성 가드** — DORA 통제(테스트 자동화·작은 배치) 점검 + defense-in-depth 승인 목록(delivery-verifier).

각 단계는 직전 단계의 *산출물*만 입력으로 받고, **대상 산출물이 없는 단계(예: IaC 없음)는 Phase 0에서 건너뛴다**.

## 3. defense-in-depth (핵심 안전장치 ①)

에이전트가 파이프라인 YAML을 직접 고치거나 `terraform apply`·배포를 자동 실행하면, 잘못된 변경을 사람보다 빠르게
증폭한다. 그래서 이 하네스는 **기본 읽기 전용**이고, 어떤 쓰기/apply/deploy도 *제안*에 그친다 — 사람이 사전
승인(safe-outputs)한 뒤 *사람이* 집행한다. 이는 GitHub Agentic Workflows의 보안 모델(기본 읽기전용·샌드박스·
도구 allowlist·네트워크 격리·쓰기 작업 전 safe-outputs 사전승인)을 차용한 것이다(§research).

> CI 실패 상시 조사·테스트 커버리지 개선·코드 단순화 PR 등은 GitHub Agentic Workflows가 든 **6개 예시**(닫힌 범주가
> 아니라 "just a few examples")이지, 이 하네스가 그 6개에 한정된다는 뜻이 아니다(§research CAVEAT).

## 4. policy-as-code 결정론적 게이트 (핵심 안전장치 ②)

IaC 변경을 LLM의 "안전해 보임" 판단으로 통과시키면, 환각·과신이 인프라 파괴로 이어진다. 그래서 IaC는 **결정론적
검증**을 통과해야 한다.

- **terraform plan(실행 검증)** — 실제로 무엇이 생성/변경/파괴되는지 리소스 단위 미리보기. destroy·force-replace를 위험 신호로.
- **OPA(policy-as-code 정책 강제)** — 태깅·암호화·퍼블릭 접근 금지·비용 가드 등 정책을 결정론적 룰로 강제, 위반 항목별 판정.

둘 다 통과해야 PASS다. 결정론적 게이트가 없으면 통과 대신 **BLOCKED**로 분리해 게이트 구축을 요청한다.
이는 MACOG(IaC 멀티에이전트)가 Terraform Plan + OPA를 결정론적 검증으로 내재화하는 구조를 차용한 것이다 —
*결정론적 검증 내재화가 단일패스보다 낫다는 방향성*을 채택하되, 절대 효과크기는 단정하지 않는다(§research CAVEAT).

## 5. trust-tier 단계적 자율 (핵심 안전장치 ③)

배포 의사결정은 위험도가 천차만별이다 — flaky 격리 제안과 프로덕션 전면 rollback은 같은 자율 폭으로 다루면 안 된다.
그래서 **각 결정에 위험도(blast radius·가역성·영향)를 매겨 자율 수준을 단계화**한다.

| trust-tier | 자율 폭 | 예시 |
|------------|---------|------|
| 낮은 위험 | 제안 + 자동 게이트 | flaky 테스트 격리 제안, 플래그 비율 소폭 조정 제안 |
| 중간 위험 | 제안 + 사람 확인 | canary 다음 단계 승격 |
| 높은 위험 | 사람 필수 | 프로덕션 전면 배포 승격·전면 rollback·비가역 플래그 변경 |

이는 AI-Augmented CI/CD가 LLM/에이전트를 "policy-bounded co-pilot"로 두고 자율 처리 후보 의사결정 지점
(flaky 해석·rollback 선택·feature-flag 튜닝·canary 승격 타이밍)에 trust-tier framework for staged autonomy를
적용하는 것을 차용한 것이다(§research).

## 6. DORA 통제 프레이밍 (전달 안정성 가드)

DORA 2025는 AI 도입이 **전달 처리량·제품 성과와 양(+)**, 그러나 **전달 안정성과 음(-)** 의 관계임을 보고한다 —
"통제 시스템이 없으면 변경량 증가가 불안정으로 이어진다(AI=amplifier)". 따라서 delivery-verifier는 변경량을
받아낼 **통제**가 갖춰졌는지를 마지막에 점검한다.

### DORA 반증 nuance (정직성 — 필수)
- **사실로 인용 가능한 AI-불안정 통제책은 두 가지뿐**: **small batches(작은 배치)** + **robust test automation(강한 테스트 자동화)**. 이 둘만 페이지에서 그대로 인용한다.
- **신화(사실 인용 금지)**: "버전관리·느슨한 결합도 DORA가 AI 통제요소로 지목"·"긴밀결합 팀은 AI로 무이득"은 **검증에서 반증됐다** — 좋은 일반 관행으로 권할 수는 있어도 *DORA가 AI 통제요소로 지목했다는 사실로 인용하지 않는다*(신화로만 표기).
- **AI=amplifier 프레이밍은 인용 가능**. AI 가치를 증폭하는 7개 역량(platform engineering·version control·small batches·AI-accessible internal data·healthy data ecosystems·clear AI stance·user-centric)은 메인 리포트가 아니라 companion인 **DORA AI Capabilities Model**에 있다(§research).

## 7. 역할 분리 오케스트레이션 (설계 ≠ 검증 ≠ 결정 ≠ 가드)

단일 에이전트가 파이프라인 설계·IaC 검증·릴리스 결정·안정성 가드를 다 하면, 자기 설계를 자기가 통과시키는 편향이
생긴다. 이 하네스는 **설계(P1) ≠ 결정론적 검증(P2) ≠ 릴리스 결정(P3) ≠ 안정성 가드(P4)** 를 다른 에이전트로
분리한다. 특히 IaC 검증자는 LLM 의견이 아니라 *결정론적 게이트의 출력*으로 판정하고, 안정성 가드는 앞 단계의
쓰기 제안을 *집행하지 않고* 사람 승인 목록으로만 정리한다.

> 본 저장소 컨벤션상 4개 협업 하네스이므로 `agents/*.md` 정의 + `model:"opus"`를 둔다.

## 8. anti-pattern (피해야 할 전달 행동)

1. **인프라 직접 변경·배포 자동 실행** — 에이전트가 `terraform apply`·배포를 자동 집행. → 읽기 전용 + 사람 사전 승인 제안으로 차단(defense-in-depth).
2. **LLM 판단으로 IaC 통과** — "안전해 보임"을 게이트로. → terraform plan + OPA 결정론적 게이트(없으면 BLOCKED).
3. **모든 결정을 같은 자율로** — flaky 격리와 프로덕션 rollback을 같은 폭으로. → trust-tier 단계화(고위험=사람 필수).
4. **flaky를 통과로 반올림** — 간헐 실패를 "어쩌다 빨강"으로 넘김. → 재현성 확인 + 격리 + 근본 추적.
5. **통제 없는 처리량 증가** — AI로 변경량만 키우고 테스트 자동화·작은 배치는 그대로. → DORA 통제 점검.
6. **신화를 사실로 인용** — "버전관리·느슨한 결합이 AI 통제요소"·"긴밀결합 무이득"을 근거로. → 신화로만, small batches + test automation만 사실 인용.
7. **단계 건너뛰기** — IaC 검증·릴리스 결정을 생략하고 배포로 점프. → P1→P4 순서(없는 단계만 Phase 0에서 건너뜀).

## 9. 정직성 가드레일 (전 산출물 공통)

- 정량 수치는 출처 등급([GOLD]/[SILVER]/[BRONZE])·출처명·날짜와 함께만 인용한다.
- '개선 N%' 같은 약속을 하지 않는다. baseline을 먼저 제시하고 방향을 말한다(baseline-before-target).
- 반증·미검증 수치는 '신화'로만 표기하고 사실로 쓰지 않는다 — **특히 DORA 통제책은 small batches + robust test automation 두 가지만 사실 인용**, 버전관리·느슨한 결합·긴밀결합 무이득은 신화로만.
- MACOG 절대 수치는 모델 세대 의존이므로 *방향성*(결정론적 검증 내재화가 단일패스보다 낫다)으로만 채택하고 효과크기를 단정하지 않는다.
- §research의 CAVEAT를 본문에서 그대로 동반 인용한다.
