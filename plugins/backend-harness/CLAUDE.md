# backend-harness

백엔드/API를 **실행 기반 검증**으로 구현하는 멀티 에이전트 하네스.
범위/계약 → 설계 → **환경 구성(1급 시민)** → 구현 → **실행 검증**의 5단계를 매 단계 승인 게이트로 묶는다.
두 차별점: ① 에이전트 자기보고를 불신하고 *빌드·테스트의 실제 통과*로만 PASS를 인정(reward-hacking 가드),
② 환경 구성이 최대 병목이라는 근거로 env-provisioner를 독립 Phase로 둔다. 같은 플러그인에 기존 코드의
실행기반 테스트를 generate→compile→execute→repair로 생성·수리하는 `test-generator` 스킬을 둔다(QA 탈-FE편중).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
backend-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + 5단계 요약 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·도구 경계
├── agents/                         # 모두 model: "opus"
│   ├── be-architect.md             # 설계 — 서비스 경계·API 계약·데이터 모델/마이그레이션 + 검증 후크·환경 요구사항
│   ├── env-provisioner.md          # 환경 — 빌드·실행·테스트 가능 상태 확보(최대 병목, 독립 1급 단계)
│   ├── be-implementer.md           # 구현 — API·서비스 로직·DB 스키마/마이그레이션(계약 준수, 자기보고≠통과)
│   └── be-verifier.md              # 검증 — 실행 기반 PASS/FAIL, 빌드·테스트 직접 재실행, 고커버리지·reward-hacking 가드
├── skills/
│   ├── backend-harness/
│   │   ├── SKILL.md                # 오케스트레이터(진입점, Phase 0~4 + 승인 게이트)
│   │   └── references/
│   │       ├── backend-harness-principles.md   # 6원칙·anti-pattern·env 독립 근거·인접 하네스 경계
│   │       └── backend-harness-research.md      # 설계 근거 dossier (출처·등급·CAVEAT)
│   └── test-generator/
│       ├── SKILL.md                # 실행기반 테스트 생성+수리 루프 스킬(model-invocable)
│       └── references/
│           └── test-generator-guide.md          # 공진화 루프·5 경험적 수리 템플릿·커버리지 게이트·judge 캘리브레이션
└── evals/
    └── trigger-eval.json           # 트리거 경계 평가 (should_trigger 11 / should_not 12, 인접 하네스 reciprocal 가드)
```

## 5단계 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 범위/계약 입력 | (오케스트레이터) | 기능 범위·주어진 계약·기술 제약 | 승인 게이트 |
| 1 | 설계 | be-architect | Design Spec(서비스 경계·API 계약·데이터 모델·검증 후크·환경 요구사항) | 승인 게이트 |
| 2 | 환경 구성 (1급) | env-provisioner | Environment Readiness(준비 절차 + 실제 통과 증거) | 승인 게이트, BLOCKED면 범위·설계로 되먹임 |
| 3 | 구현 | be-implementer | Implementation 리포트(변경·계약 대비·로컬 확인 증거) | 승인 게이트 |
| 4 | 실행 검증 (핵심) | be-verifier | Verdict(빌드·마이그레이션·테스트·커버리지·계약 인수·reward-hacking 점검) | PASS=마무리 / FAIL=되돌림 / BLOCKED=env 보정 |

매 Phase 1줄 보고: `[Phase N] {핵심결정/증거} — 다음: {다음}. 진행할까요?`. 최종: `[Backend 종료] {PASS|미완:되돌린 Phase} — 엔드포인트 {수}, 테스트 {통과/전체}, 커버리지 {수치|미측정}.`

## Conventions

- **실행 기반 검증**: 통과는 자기보고·commit이 아니라 빌드·테스트의 실제 통과로만. 증거 없는 PASS 금지(be-verifier).
- **환경 우선(1급 시민)**: 환경이 안 서면 이후 신호가 모두 거짓. 구현 전에 빌드·실행 가능 상태를 독립 Phase로 확보하고 헬스체크·스모크 실제 통과로 닫는다.
- **generator/checker 분리**: 구현(be-implementer)과 검증(be-verifier)을 분리한다. 검증자는 코드를 고치지 않는다.
- **reward-hacking 가드**: 테스트 무력화·스킵·우회, 마이그레이션 우회를 diff로 적대적 점검 + 고커버리지 게이트.
- **계약 준수**: API 계약·데이터 모델을 구현으로 임의 우회하지 않는다. 못 맞추면 설계로 되먹임.
- **Honesty Guardrail**: 정량 수치는 출처·등급([GOLD]/[SILVER]/[BRONZE])·날짜·CAVEAT와 함께만. '개선 N%' 약속 금지. baseline-before-target.
- **승인 게이트·관찰성**: 매 Phase 산출물 미리보기 후 1줄 보고로 승인. 요청되지 않은 사이드 에이전트·중복 실행 금지.
- **경계**: 완성된 API spec *검수*(일관성·breaking change 점검), FE 화면 구현, PRD 작성, 커밋/PR, 하네스 자체 진단, 단발 목표 지향 자율 반복 루프는 이 플러그인의 범위 밖이다(이 플러그인은 *구현*이다). test-generator는 *기존 코드*의 실행기반 테스트 생성·수리(test-after)로, test-first(Red-Green-Refactor) TDD와 구분한다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | backend-harness(실행 기반 검증 + 환경 1급 시민) 백엔드/API 구현 멀티 에이전트 하네스 + test-generator 스킬. 근거: arXiv:2510.04852·2505.09569·2505.07473·2512.06915[GOLD], TestART arXiv:2408.03095[SILVER] |
