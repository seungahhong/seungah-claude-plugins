# review-harness

개발 착수 *전* 상류 산출물(기획·디자인·API 계약·QA 인수조건)을 **핸드오프 시점에 '착수 게이트'로 검수**하는 도메인 무관 멀티 에이전트 하네스. AI가 코드 작성을 자동화할수록 결함은 '작성'이 아니라 **상류 스펙 품질과 리뷰**로 이동한다는 전제에서 출발한다.

사용자용 개요·사용법은 [README.md](README.md), 게이트 흐름의 정본은 [commands/handoff-review.md](commands/handoff-review.md)와 각 게이트 스킬([skills/](skills/))의 SKILL.md다.

## Conventions

- **상류 산출물 게이트**: 이 하네스는 *코드가 아니라* 코드 착수 전 상류 산출물을 핸드오프 시점에 검수한다. 완성된 코드 리뷰, PRD·스토리 *작성*, 커밋/PR 리뷰는 이 하네스의 범위 밖이며 별도 워크플로로 처리한다.
- **읽기 위주**: 게이트 스킬은 산출물(PRD/디자인/계약/AC)을 직접 수정하지 않는다(`allowed-tools`에 Edit/Write 없음). 보강 항목은 구체적으로 제시하되 합의·수정은 해당 팀이 한다.
- **Honesty Guardrail (전 스킬 공통)**: 정량 수치는 검증된 근거만 등급(GOLD/SILVER/BRONZE)·출처와 함께 인용한다. '개선 N%'를 약속하지 않고 효과는 조직이 baseline으로 측정한다(baseline-before-target). 출처 추적 실패·반증된 수치(IBM 1→100배, NIST 'Example Only' 표, Code Connect 85~90% 등)는 사실로 인용하지 않고 '신화'로만 표기한다.
- **2025+ 근거 우선**: 각 스킬의 '참고/근거'는 2025년 이후 동료심사/학회/arXiv 근거를 우선하고, 인용한 수치는 실재·연도·venue를 확인해 적는다. preprint·벤더 자기보고·소표본은 caveat로 명시한다.
- **disable-model-invocation**: 게이트 스킬은 모델 자동 발동을 끄고 `/dor-review` 등으로 명시 호출하거나 `handoff-review` 오케스트레이터가 spawn한다.
- **트리거 가드**: 새 트리거 표현 변경 시 인접 도구(코드 리뷰·PRD 작성 등)와의 경계 케이스와 reciprocal하게 `evals/trigger-eval.json`을 갱신한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
