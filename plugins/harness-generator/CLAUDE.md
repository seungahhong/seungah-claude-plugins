# harness-generator

도메인 무관 하네스(에이전트 팀 + 스킬 + 오케스트레이터)를 7단계 프로세스(Phase 0~7)로 **사람이 단계별로 직접 같이(수동·인터랙티브)** 설계·생성하는 메타 플러그인. 후보 N개 자동 탐색·Pareto 채점 생성과 기존 하네스의 trace 기반 진단·개선은 모두 이 플러그인의 범위가 아니다(각각 자동 탐색·Pareto 도메인 / trace 진단 도메인).

사용자용 개요·사용법은 [README.md](README.md), 7단계 프로세스(Phase 0~7)의 정본은 [SKILL.md](skills/harness-generator/SKILL.md), 참고 자료는 [references/](skills/harness-generator/references/)다.

## Conventions

- 특정 기술 스택·도구에 종속되지 않는 공통 메타 절차만 다룬다.
- 생성 결과는 에이전트 정의 + 스킬 + 오케스트레이터를 한 묶음으로 산출한다.
- 재실행·보완·기존 하네스 감사에도 같은 스킬을 사용한다(Phase 0에서 분기).
- 매 Phase 종료 시 핵심 산출물을 보여주고 사용자 확인 후 진행한다(수동·인터랙티브 정체성).
- SKILL.md description·트리거 표현을 바꾸면 `evals/trigger-eval.json`을 함께 갱신한다(자동 탐색·Pareto 도메인·trace 진단 도메인과의 cross-plugin 동시발동 가드).
- 스킬·references의 외부 인용은 2025년 이후 발표 자료만 사용하고, 인용 추가·교체 시 발표일을 확인해 링크 직후 (YYYY-MM) 형식으로 병기한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
