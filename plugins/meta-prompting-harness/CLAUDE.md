# meta-prompting-harness

**메타 프롬프팅**(AI에게 입력할 프롬프트를 AI가 최적화해 생성하게 하고, 그 결과 프롬프트를 새 컨텍스트에 주입해 실제 작업을 돌리는 기법)을 4단계 인터랙티브 멀티 에이전트로 수행하는 도메인 무관 하네스. 널리 쓰이는 메타 프롬프팅 실천 방법론을, 각 기법을 `/deep-research`로 2023~2026 1차 문헌과 대조해 근거 등급을 붙여 재구성했다.

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/meta-prompting/SKILL.md), 근거 정본은 [evidence.md](skills/meta-prompting/references/evidence.md)다.

## Conventions (핵심 불변식)

규칙 본문은 SKILL.md와 `references/`에 있다. 여기에는 수정할 때 깨뜨리면 안 되는 불변식과 그 위치만 적는다.

- **절대 규칙** — 최적화 프롬프트를 보편 법칙으로 서술 금지 · 전부 위임 금지 · AI가 깎은 프롬프트는 사용자 도메인 검증 필수 · 프롬프트 생성만 하고 실행은 사용자 · 커밋 안 함 · 점수화 안 함.
- **경계** — 이미 목표가 있는 컨텍스트 페이로드 조립·압축·리트리벌·하네스 자체 생성/진단·기획문서(PRD)·사용자 스토리·계획/방법론 인터뷰·자율 반복 루프 실행·코드 구현/리뷰/커밋은 범위 밖(산출물이 프롬프트가 아님). 고유 판별자: *다른 도구에 주입할 지시 프롬프트 자체*를 질문 유도·성공조건·환경 맞춤으로 깎아냄. 다른 플러그인을 참조하거나 의존하지 않고 자족하는 독립 플러그인.
- **근거 등급**은 [evidence.md](skills/meta-prompting/references/evidence.md)가 정본이다(STRONG / report-only / REFUTED). report-only 기법에 "실증" 표현을 쓰지 않는다.
- 4개 에이전트 협업 하네스이므로 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시하고, 매 Phase 승인 게이트를 둔다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 목록 맨 아래에 항목을 추가한다.
