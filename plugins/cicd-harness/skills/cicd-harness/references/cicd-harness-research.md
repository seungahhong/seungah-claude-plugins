# CICD Harness — 연구 dossier (cited · graded)

> 이 문서는 `cicd-harness` 하네스 설계의 근거가 된 자료 조사 결과다.
> [cicd-harness-principles.md](./cicd-harness-principles.md)의 원리와 상호 참조된다.
> 빠르게 변하는 분야이므로 각 절에 **출처·등급([GOLD]/[SILVER]/[BRONZE])·날짜·CAVEAT**를 함께 표기한다.
> 정량 수치는 등급·CAVEAT 없이 인용하지 않으며, '개선 N%' 약속은 하지 않는다(baseline-before-target).

## 출처 등급 정의

- **[GOLD]** — 피어리뷰 또는 대규모 검증 자료.
- **[SILVER]** — 방법론이 공개된 업계 리포트·preprint(미피어리뷰 포함).
- **[BRONZE]** — 블로그·일화적 근거.

---

## 1. DORA 2025 — AI는 amplifier, 전달 안정성은 통제가 필요

**주장**: AI 도입은 **전달 처리량(throughput)·제품 성과와 양(+)** 의 관계이나, **전달 안정성(delivery stability)과는
음(-)** 의 관계다. 핵심 프레이밍은 **AI=amplifier** — AI가 변경량을 키우면, *통제 시스템(강한 자동화 테스트·빠른
피드백)이 없으면* 그 변경량 증가가 불안정으로 이어진다.

- 출처: **DORA 2025**(dora.dev / cloud.google.com, 2025).
- 등급: **[GOLD]** (대규모 산업 조사).
- **CAVEAT(필수)**: DORA 페이지에서 *그대로 인용 가능한 AI-불안정 통제책은 **small batches + robust test
  automation 두 가지뿐***이다. 그 외에 흔히 떠도는 통념은 **검증에서 반증됐다** — 사실로 인용하지 않는다(신화로만):
  - ✗ "버전관리·느슨한 결합도 DORA가 AI 통제요소로 지목" → **신화(반증)**.
  - ✗ "긴밀결합(tightly coupled) 팀은 AI로 무이득" → **신화(반증)**.
  - ○ "AI=amplifier" 프레이밍은 인용 가능.
- **설계 함의**: delivery-verifier(Phase 4)가 **강한 테스트 자동화 + 작은 배치** 두 통제책만 핵심 점검 축으로 둔다.
  AI로 변경량이 느는 만큼 통제가 비례하는지 *방향성*으로 진단하고(인과 단정 아님), '안정성 N% 개선'을 약속하지 않는다.

## 2. DORA AI Capabilities Model — AI 가치를 증폭하는 7개 역량

**주장**: AI의 가치를 증폭하는 7개 역량 — **platform engineering · version control · working in small batches ·
AI-accessible internal data · healthy data ecosystems · clear AI stance · user-centric focus**.

- 출처: **DORA AI Capabilities Model**(dora.dev/ai/capabilities-model). ※ 이 리스트는 dora-report-2025 *메인*이 아니라 **companion**에 있다.
- 등급: **[GOLD]**.
- **CAVEAT**: 이 7개는 *AI 가치를 증폭하는 역량* 목록이지, §1의 *AI-불안정 통제책*(small batches + test automation 두 가지)과 혼동하지 않는다. 두 목록을 섞어 "버전관리가 AI 불안정 통제요소"라고 쓰지 않는다(그것은 §1의 신화). 채택하는 것은 *AI 가치 증폭 역량의 존재*이고, 그중 small batches는 §1의 통제책과 겹친다.
- **설계 함의**: small batches를 통제책으로 인용하는 근거를 §1과 함께 보강한다. 나머지 역량은 *좋은 관행*으로 권할 수 있으나 AI-불안정 통제요소로 단정하지 않는다.

## 3. AI-Augmented CI/CD — policy-bounded co-pilot + trust-tier 단계적 자율

**주장**: LLM/에이전트를 CI/CD의 **"policy-bounded co-pilot"** 로 두는 프레임워크 — reference architecture +
decision taxonomy + **policy-as-code guardrail** + **trust-tier framework for staged autonomy**. 자율 처리 후보
의사결정 지점은 **flaky 테스트 해석 · rollback 전략 선택 · feature-flag 튜닝 · canary 승격 타이밍**.

- 출처: **arXiv:2508.11867 (2025-08)**.
- 등급: **[SILVER]** (방법론 공개 preprint).
- **CAVEAT**: 프레임워크 제안 성격으로, 특정 효과크기를 약속하지 않는다. 채택하는 것은 *구조*(policy-bounded co-pilot + trust-tier 단계적 자율 + policy-as-code guardrail)와 *자율 처리 후보 의사결정 지점 4종*이다.
- **설계 함의**: release-gatekeeper(Phase 3)에 **trust-tier 단계적 자율**(낮은 위험=제안+자동 게이트, 높은 위험=사람 필수)을 1급 원칙으로 내장하고, flaky·rollback·feature-flag·canary를 그 적용 대상으로 둔다.

## 4. GitHub Agentic Workflows — defense-in-depth(읽기전용·사람 사전승인)

**주장**: 수기 YAML이 아닌 **plain Markdown(YAML frontmatter) 워크플로우**를 GitHub Actions에서 코딩 에이전트가
실행한다. 보안 모델은 **defense-in-depth** — 기본 읽기전용·샌드박스·도구 allowlist·네트워크 격리·**쓰기 작업 전
safe-outputs 사전승인**.

- 출처: **github.blog (2025)**.
- 등급: **[SILVER]** (벤더 기술 블로그/방법론 공개).
- **CAVEAT**: CI 실패 상시 조사·테스트 커버리지 개선·코드 단순화 PR 등은 글이 든 **6개 예시**(닫힌 범주가 아니라 "just a few examples")이지, 이 하네스가 그 6개에 한정된다는 뜻이 아니다. 채택하는 것은 *defense-in-depth 보안 모델*(기본 읽기전용 + 쓰기 작업 전 사람 사전 승인)이다.
- **설계 함의**: 전 단계에 defense-in-depth를 적용 — 에이전트는 인프라를 직접 변경하거나 배포를 자동 실행하지 않고, 모든 쓰기/apply/deploy는 사람 사전 승인(safe-outputs) 후 *제안→사람 집행*. delivery-verifier가 승인 목록을 최종 정리한다.

## 5. MACOG — IaC 멀티에이전트 + terraform plan + OPA 결정론적 검증

**주장**: IaC 멀티에이전트가 **Terraform Plan(실행 검증) + OPA(policy-as-code) 결정론적 검증을 내재화**할 때
단일패스보다 낫다. 구조는 8개 전문 에이전트 + 공유 블랙보드 FSM 오케스트레이터.

**정량(방향성으로만, 효과크기 단정 금지)**: IaC-Eval에서 GPT-5 **54.90 → 74.02**, Gemini-2.5 Pro **43.56 → 60.13**.

- 출처: **arXiv:2510.03902 (MACOG)**.
- 등급: **[SILVER]** (방법론 공개 preprint).
- **CAVEAT(필수)**: 절대수치는 **모델 세대 의존**이다 — "54.90→74.02"를 이 하네스가 그만큼 올린다는 보장으로 읽지 않는다. 채택하는 것은 *방향성*(결정론적 검증 내재화가 단일패스보다 낫다)이고, 효과크기를 단정하지 않는다.
- **설계 함의**: iac-reviewer(Phase 2)가 **terraform plan(실행 검증) + OPA(policy-as-code)** 를 결정론적 게이트로 내재화하고, LLM 판단만으로 통과시키지 않는다. 결정론적 게이트가 없으면 BLOCKED로 분리해 게이트 구축을 요청한다.

---

## 6. 종합 — 설계로의 매핑

| 근거 | 등급 | cicd-harness 반영 |
|------|------|------------------|
| DORA 2025(AI=amplifier, 안정성 음의 관계, 통제=small batches+test automation 두 가지뿐) | [GOLD] | Phase 4 delivery-verifier: 두 통제책만 핵심 축, 나머지는 신화 분리 |
| DORA AI Capabilities Model(7개 역량, companion) | [GOLD] | small batches 통제 근거 보강, 나머지 역량은 관행으로만 |
| AI-Augmented CI/CD(policy-bounded co-pilot + trust-tier) | [SILVER] | Phase 3 release-gatekeeper: trust-tier 단계적 자율(flaky/rollback/flag/canary) |
| GitHub Agentic Workflows(defense-in-depth) | [SILVER] | 전 단계: 읽기전용·쓰기 작업 전 사람 사전 승인·제안→사람 집행 |
| MACOG(terraform plan + OPA 결정론적 검증) | [SILVER] | Phase 2 iac-reviewer: terraform plan + OPA 결정론적 게이트(둘 다 통과해야 PASS) |

## 7. caveats (신뢰도 한계 — 본문에 함께 인용)

1. **DORA 통제책은 small batches + robust test automation 두 가지만 사실 인용** — "버전관리·느슨한 결합이 AI 통제요소"·"긴밀결합 팀 무이득"은 **반증된 신화**로, 사실로 인용하지 않는다(신화로만). AI=amplifier 프레이밍·7개 역량(companion)은 인용 가능하되 통제책과 혼동하지 않는다.
2. **MACOG 절대 수치는 모델 세대 의존** — 54.90→74.02·43.56→60.13은 *결정론적 검증 내재화가 단일패스보다 낫다*는 방향성 증거이지 이 하네스의 성능 보장이 아니다. 효과크기 단정 금지.
3. **AI-Augmented CI/CD·GitHub Agentic Workflows는 SILVER** — 프레임워크/벤더 블로그 성격. 채택은 *구조*(trust-tier·defense-in-depth)이지 정량 약속이 아니다. Agentic Workflows의 6개 사용처는 닫힌 범주가 아닌 예시다.
4. **DORA는 상관/관측이지 인과 보장이 아님** — "통제를 넣으면 안정성이 그만큼 오른다"로 읽지 않는다. 본 하네스는 *통제 구조의 정당성*을 제공하며 안정성 향상을 수치로 약속하지 않는다(baseline-before-target).
5. **환경마다 스택·정책·규모가 다름** — IaC 부재·OPA 정책 부재·trace/메트릭 가용성 차이를 Phase 0에서 명시 점검하고(없는 단계는 건너뜀), 결정론적 게이트가 없으면 BLOCKED로 신뢰도를 낮춘다.

## 8. open questions (후속)

- trust-tier 위험도 경계의 조작적 정의(어떤 blast radius/가역성부터 '높은 위험=사람 필수'인지) — 현 근거는 프레임워크 방향만 제시.
- terraform plan + OPA 외에 결정론적으로 강제 가능한 IaC 정책 게이트의 범위(비용·드리프트·컴플라이언스)와 그 캘리브레이션.
- DORA 두 통제책(small batches·test automation)의 *조직별* 충분 임계 — 근거는 통제 존재의 방향만 제시, 운영 중 튜닝 대상.
