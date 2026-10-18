# spec-driven-development

엔지니어용 **실행 가능 명세(spec)를 source of truth로 작성**하고, 에이전트가 그 명세대로 코드를
생성한 뒤 **명세 대비 자기검증**하게 하는 도메인 무관 멀티 에이전트 하네스.
워크플로를 *코드 우선*에서 *명세 우선*으로 역전한다 — 명세가 1차 산출물, 코드는 그로부터 생성·검증되는 2차 산출물이다.

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/spec-driven-development/SKILL.md), 방법론·근거는 [references/](skills/spec-driven-development/references/)다.

## Conventions

- **명세=source of truth**: 명세가 1차 산출물이고 코드는 그로부터 생성·검증되는 2차 산출물이다. 코드를 먼저 짜고 명세를 사후 작성하지 않는다.
- **명세 승인 게이트(항상)**: Phase 0 명세를 사용자가 승인하기 전에는 구현(Phase 2)을 시작하지 않는다 — 잘못된 명세로 코드 생성 비용을 낭비하지 않기 위함.
- **구조화된 contract**: 명세는 산문이 아니라 *구조화된 contract*다(목표·범위 In/Out·인터페이스·동작·제약·엣지케이스). 에이전트가 그대로 구현·검증할 수 있게 쓴다.
- **인수기준 + 자기검증 내재화**: acceptance-designer가 인수기준·테스트 계획·자기검증 체크를 명세 안에서 자족적으로 설계한다(LLM-as-a-Judge식 인수 점검을 이 플러그인 안에서 직접 기술 — 외부 의존 금지).
- **명세 대비 검증(추적성)**: spec-verifier는 "코드가 잘 도나"가 아니라 "코드가 *명세대로* 도나"를 조항별로 본다. 각 spec 조항에 충족/미충족과 증거를 귀속한다.
- **comprehension 게이트(comprehension debt 방지)**: 완료 선언 전에 실제 diff를 읽고 "무엇이 왜 바뀌었는지"를 확인한다. 읽기(이해)가 쓰기(생성)를 따라가지 못하면 "엔지니어링이 아니라 희망"이다 — 명세가 *이해의 앵커* 역할을 한다.
- **과장 금지(정직성)**: SDD는 정의상 워크플로 역전이며 "보장된 개선"이 아니다. non-determinism·overhead 등 비판도 dossier에 함께 기록한다. 정량 수치는 vote/CAVEAT와 함께만 인용한다.
- **경계**: 엔지니어용 *실행 가능 구현 명세*에 특화한다. 기획자용 PRD·사용자 스토리, AI 출력 평가 judge 구성, 컨텍스트 페이로드 조립, 완성 코드 리뷰·커밋/PR, 하네스 자체 진단은 범위 밖이다(일반 개념으로 변별, 타 플러그인 의존 금지).
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
