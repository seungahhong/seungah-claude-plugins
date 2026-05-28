# harness-evolver

## 하네스: 하네스 자체를 진화시키는 메타 하네스

**Goal:** 사용자가 사용 중인 임의의 하네스 스킬에서 문제가 보고됐을 때, 그 대상 하네스의 실행 궤적을 캡처·진단해 결함의 근본 원인을 식별하고 skill-creator 방식의 eval-driven iteration으로 자율 개선한다. 특정 하네스/도메인에 종속되지 않는다.

**Trigger:** "하네스 고도화", "오케스트레이터 개선", "스킬이 안 먹는다", "하네스 오동작", "트리거 누락 진단", "스킬 자동 개선", "harness evolve", "재실행해도 같은 실수" 등에 `harness-evolver` 스킬을 사용한다. 사용자가 어떤 플러그인의 하네스를 가리키든 무관하다 — 대상 경로만 Phase 1에서 식별한다. 단순 스킬 작성/추가는 `skill-creator` 또는 `harness-generator`를 사용하고, 신규 하네스 구축은 `harness-generator`를 사용한다.

**실행 모드:** 서브에이전트 + 하이브리드 — Phase 2 진단은 팬아웃 병렬, Phase 3 개선은 순차. 모든 Agent 호출은 `model: "opus"`.

**핵심 아이디어 (Evolver 루프 ↔ skill-creator):**

| 출처 | 차용 개념 | 본 하네스에서의 적용 |
| ---- | -------- | ------------------ |
| Evolver 루프 | Trajectory capture | `_workspace/trajectories/*.jsonl` 로 단계별 실행 기록 |
| Evolver 루프 | Curated memory + nudges | `evolution-memory/` 에 반복 패턴 누적, 임계치 도달 시 자동 제안 |
| Evolver 루프 | Autonomous skill refinement | `skill-refiner` 에이전트가 진단 결과를 받아 수정안 생성 |
| skill-creator | Eval-driven iteration | with/without 비교 + assertion + iteration loop |
| skill-creator | Description optimization | should-trigger / should-not-trigger 큐에 의한 description 재작성 |
| skill-creator | Progressive disclosure | references/ 분리, 본문 < 500줄 유지 |

**Change History:**

| Date | Change | Target | Reason |
| ---- | ------ | ------ | ------ |
| 2026-05-28 | Initial build | All | Evolver 닫힌 학습 루프 + skill-creator eval 루프 결합으로 하네스 자체를 진화시키는 메타 플러그인 신설 |
