# harness-evolver

## 하네스: 하네스 자체를 진화시키는 메타 하네스

**Goal:** 사용자가 사용 중인 임의의 하네스 스킬에서 문제가 보고됐을 때, 그 대상 하네스의 실행 궤적을 캡처·진단해 결함의 근본 원인을 식별하고 skill-creator 방식의 eval-driven iteration으로 자율 개선한다. 특정 하네스/도메인에 종속되지 않는다.

**평가 스코프:** 기본은 현재 적용 중인 프로젝트(이 레포) 전역 — 루트 `CLAUDE.md` + 모든 플러그인의 스킬(`SKILL.md`)을 진단하고 **패치는 `CLAUDE.md`/`SKILL.md` 로 한정**한다(repo-wide, 기본). 단일 플러그인 전체(`plugin.json`·`agents`·`hooks`·`commands` 포함) 심층 평가는 사용자가 "OO 플러그인 평가/점검"처럼 **명시 요청할 때만**(plugin, opt-in). 스코프는 매 회차 Phase 1에서 확정하고, repo-wide에서 경계 밖 표적이 나오면 patch 대신 `scope-escalation`(plugin 모드 재실행 권고)으로 처리한다.

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
| 2026-05-31 | 평가 스코프 도입 (repo-wide 기본 / plugin opt-in) | orchestrator·failure-diagnosis·eval-driven-refinement·4 agents·README·evals·root CLAUDE.md·plugin.json | "평가해줘" 한마디에 패키징·에이전트·훅까지 광범위 변경되는 것 방지. 기본 패치 경계를 루트 CLAUDE.md + SKILL.md로 좁히고(repo-wide), 단일 플러그인 전체 파일 심층 평가는 명시 요청(plugin)으로만. 경계 밖 표적은 `scope-escalation` 으로 plugin 모드 재실행 권고. `marketplace.json`(레포 루트 메타)은 `out-of-scope`(어느 모드에서도 비패치) |
| 2026-05-31 | 환경 robustness 보강 (병렬 fan-out stall 방지) | orchestrator Phase 2-2 + 에러 정책 | 검증 회차 중 다수 에이전트 동시 spawn + 무거운 일괄 read로 stall 발생 → 배치 spawn(한 번에 ≤4~6건) + 에이전트별 read 범위 축소 가이드 추가 |
