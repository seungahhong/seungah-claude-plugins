# cicd-harness

**코드 커밋 → 프로덕션**의 전달(delivery) 파이프라인을 오케스트레이션하는 CI/CD·DevOps·릴리스·IaC 멀티 에이전트 하네스.
CI 파이프라인(build/test 게이트) → IaC·환경(**terraform plan + OPA policy-as-code 결정론적 검증**) →
릴리스·배포 결정(canary·rollback·feature-flag·flaky, **trust-tier 단계적 자율**) → 전달 안정성 가드(**DORA 통제**)의
4단계를 매 단계 승인 게이트로 묶는다. **defense-in-depth** — 기본 읽기 전용, 어떤 쓰기/apply/deploy도 사람 사전
승인 후 *제안→사람 집행*. 에이전트가 인프라를 직접 변경하거나 배포를 자동 실행하지 않는다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
cicd-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + 4단계 요약 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·도구 경계
├── agents/                         # 모두 model: "opus"
│   ├── pipeline-architect.md       # Phase 1 — CI 파이프라인·릴리스 전략 설계/검수(build/test 게이트, 제안만)
│   ├── iac-reviewer.md             # Phase 2 — IaC 검증(terraform plan 실행검증 + OPA policy-as-code 결정론적 게이트)
│   ├── release-gatekeeper.md       # Phase 3 — 배포/릴리스 결정(flaky·rollback·feature-flag·canary, trust-tier 단계적 자율)
│   └── delivery-verifier.md        # Phase 4 — 전달 안정성 가드(DORA 통제: 테스트 자동화·작은 배치, defense-in-depth 승인)
├── skills/
│   └── cicd-harness/
│       ├── SKILL.md                # 오케스트레이터(진입점, Phase 0 범위·trust-tier 확보 → P1→P4 게이트 진행)
│       └── references/
│           ├── cicd-harness-principles.md   # 4단계·defense-in-depth·policy-as-code·trust-tier·DORA·anti-pattern
│           └── cicd-harness-research.md      # 설계 근거 dossier (출처·등급·CAVEAT·DORA 반증 nuance)
└── evals/
    └── trigger-eval.json           # 트리거 경계 평가 (should_trigger / should_not, 인접 하네스 reciprocal 가드)
```

## 4단계 요약

| Phase | 단계 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 범위·trust-tier 확보 | (오케스트레이터) | 대상 파이프라인·산출물 유무·trust-tier·슬러그 | 승인 게이트(없는 단계는 건너뜀) |
| 1 | CI 파이프라인 | pipeline-architect | Pipeline Plan(build/test 게이트·릴리스 전략, 제안) | 승인 게이트 |
| 2 | IaC·환경 | iac-reviewer | IaC Verdict(terraform plan + OPA 결정론적 통과/실패) | PASS=다음 / FAIL=결정론적 게이트 차단 |
| 3 | 릴리스·배포 결정 | release-gatekeeper | Release Decision(승격/보류·trust-tier·safe-outputs 대기) | 승인 게이트, 고위험=사람 필수 |
| 4 | 전달 안정성 가드 | delivery-verifier | Delivery Guard(DORA 통제 점검·defense-in-depth 승인 목록) | 승인 게이트(사람 집행 대기) |

매 Phase 보고: `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?`. 최종: `[CICD 종료] {파이프라인·게이트 요약} → 배포 결정 {승격|보류}(trust-tier {tier}, 사람 집행 대기) → .claude/cicd-delivery/{slug}/`

## Conventions

- **defense-in-depth(핵심)**: 기본 읽기 전용. 어떤 쓰기/apply/deploy도 사람 사전 승인(safe-outputs) 후에만 *제안→사람 집행*. 에이전트가 인프라를 직접 변경하거나 배포를 자동 실행하지 않는다(GitHub Agentic Workflows 보안 모델 차용).
- **policy-as-code 결정론적 게이트**: IaC는 terraform plan(실행 검증) + OPA(정책 강제)처럼 결정론적 검증을 통과해야 한다. LLM 판단만으로 통과시키지 않는다(MACOG 차용).
- **trust-tier 단계적 자율**: 의사결정 위험도별로 자율 수준을 단계화(낮은 위험=제안+자동 게이트, 높은 위험=사람 필수). flaky/rollback/feature-flag/canary 의사결정 지점에 적용(AI-Augmented CI/CD 차용).
- **DORA 통제 프레이밍**: AI가 변경량을 키우면(amplifier) 통제 시스템 없이는 전달 안정성이 떨어진다. **강한 테스트 자동화·작은 배치(small batches)** 를 전달 안정성 가드의 핵심으로 둔다(delivery-verifier 점검).
- **역할 분리**: 파이프라인 설계 ≠ IaC 결정론적 검증 ≠ 릴리스 결정 ≠ 안정성 가드. 한 에이전트가 설계와 통과 판정을 겸하지 않는다.
- **Honesty Guardrail**: 정량 수치는 출처 등급([GOLD]/[SILVER]/[BRONZE])·출처명·날짜·CAVEAT와 함께만. '개선 N%' 약속 금지. baseline-before-target. 반증·미검증은 '신화'로만(특히 DORA 통제책은 small batches + robust test automation 두 가지만 사실 인용).
- **승인 게이트·관찰성**: 매 Phase 산출물 미리보기 후 1줄 보고로 승인. 요청되지 않은 사이드 에이전트·중복 실행 금지.
- **경계(범위 밖)**: 배포 *이후* 의 런타임 인시던트, BE 코드 *구현*, 빌드 그린까지 자율 반복, 커밋/PR, 완성된 API 계약 검수, PRD 작성, FE 화면·컴포넌트, 하네스 자체 진단, 새 하네스 생성은 이 하네스의 범위가 아니다. cicd-harness는 *코드 커밋→프로덕션*의 전달 파이프라인에 특화.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | cicd-harness(코드 커밋→프로덕션 전달 파이프라인) CI/CD·DevOps·릴리스·IaC 멀티 에이전트 하네스. 4단계(CI 파이프라인 → IaC·환경 → 릴리스·배포 결정 → 전달 안정성 가드) 오케스트레이션 + 4개 전문 에이전트(pipeline-architect/iac-reviewer/release-gatekeeper/delivery-verifier). defense-in-depth(읽기전용·사람 사전승인), policy-as-code 결정론적 게이트(terraform plan + OPA), trust-tier 단계적 자율, DORA 통제 프레이밍. 근거: DORA 2025[GOLD]·DORA AI Capabilities Model[GOLD]·AI-Augmented CI/CD(arXiv:2508.11867)[SILVER]·GitHub Agentic Workflows[SILVER]·MACOG(arXiv:2510.03902)[SILVER], CAVEAT·DORA 반증 nuance 동반 |
