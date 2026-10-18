# test-layering-harness

인수조건(AC, Given-When-Then)을 **방법론(Smoke/Sanity/Regression/nightly) × 계층(Unit/Integration/E2E)** 택소노미로 계층별 테스트 스위트로 계획하고, **계획→개별→최종 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정하는 도메인 무관 인터랙티브 **단일 스킬** 독립 플러그인.

사용자용 개요·사용법은 [README.md](README.md), 원리는 [principles](skills/test-layering-harness/references/test-layering-principles.md), 근거는 [research dossier](skills/test-layering-harness/references/research/test-strategy-research.md) 참조.

Phase 0~4 흐름과 게이트(A 계획 승인·B 개별 적용 승인·C 최종 반영 재확인)는 [SKILL.md](skills/test-layering-harness/SKILL.md)가 정본이다.

## Conventions (핵심 불변식)

규칙 본문의 단일 출처는 [principles](skills/test-layering-harness/references/test-layering-principles.md)와 [`matrix/`](skills/test-layering-harness/references/matrix/_index.md) 축 카드다. 여기에는 수정할 때 깨뜨리면 안 되는 불변식과 그 위치만 적는다. **규칙을 바꾸면 principles(정본) → SKILL.md·축 카드 → evals → README 순으로 맞춘다.**

- **3개 게이트를 건너뛰지 않는다** — 계획 승인 없이 개별 적용 없음, 개별 승인 없이 파일 쓰기 없음, 최종 승인 없이 반영 없음.
- **스코프 가드** — 테스트는 사용자가 Phase 1에서 선택한 방법론·계층 안에서만 추가한다. 밖은 "추가 안 함" 표기 후 확장 문의(§4.5).
- **unit/integration은 실제 API를 호출하지 않는다**(예외 없음 — 정의상 계층 자격 상실, §3.6). fixture는 3단 폴백, 하네스는 fixture 확보용 live 호출을 하지 않는다.
- **unit/integration 배치는 대상 파일 폴더의 `__test__/`가 무조건이다** — 저장소에 다른 관습이 있어도 대체하지 않는다(계층 카드 §5).
- **E2E는 smoke·regression만**, E2E smoke는 live 전용(`@e2e-mock` 금지·CI 스테이지 없음), 태그 사다리 smoke ⊆ regression, 모드는 기존 테스트의 태그로만(§3.6.5-a·§3.6.5-c).
- **live 실행은 하네스 live 호출의 유일한 예외** — 대상 환경·계정/시드·그 자리 승인이 모두 있을 때만, 아니면 UNVERIFIED(§3.6.5-b).
- **AC-ID 표기** — 테스트 제목 `[AC-1.2] …`, smoke·regression은 인수조건 기반만, nightly·sanity만 ID 없는 추가 허용(계획표엔 사유만, §4.6).
- **셀렉터 사다리**(§3.7)·**sanity = 변경-스코프 선택 레인**(§3.5.3)·**오라클 강도 가드**(§5)는 각 절이 정본이다.
- **정직성** — 비율%·효과 수치·준수율 점수화 금지, 신뢰도·folklore·모순 표기 계승, E2E smoke는 자동 배포 게이트가 아니라 수동 체크포인트로 적는다.
- 단일 스킬 플러그인이므로 에이전트 팀(agents/)을 두지 않는다 — 인터랙티브 오케스트레이터 본성에 충실.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 위에 행을 추가한다.
