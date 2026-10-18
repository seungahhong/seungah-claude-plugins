# backend-harness

백엔드/API를 **실행 기반 검증**으로 구현하는 멀티 에이전트 하네스.
범위/계약 → 설계 → **환경 구성(1급 시민)** → 구현 → **실행 검증**의 5단계를 매 단계 승인 게이트로 묶는다.
두 차별점: ① 에이전트 자기보고를 불신하고 *빌드·테스트의 실제 통과*로만 PASS를 인정(reward-hacking 가드),
② 환경 구성이 최대 병목이라는 근거로 env-provisioner를 독립 Phase로 둔다. 같은 플러그인에 기존 코드의
실행기반 테스트를 generate→compile→execute→repair로 생성·수리하는 `test-generator` 스킬을 둔다(QA 탈-FE편중).

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/backend-harness/SKILL.md)(테스트 생성·수리 스킬은 [test-generator](skills/test-generator/SKILL.md)), 방법론·근거는 [references/](skills/backend-harness/references/)다.

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

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
