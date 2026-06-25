# loop-engineering

검증 가능한 목표를 향해 한 작업을 **자율 반복(loop)으로 완성**하는 도메인 무관 멀티 에이전트 하네스.
실행 루프(Goal→Execute→Verify→Diagnose→Improve)와 지속학습 루프(Fail→Investigate→Verify→Distill→Consult)를
결합해, 에이전트가 스스로 검증·진단·개선하고 검증된 교훈을 메모리에 쌓아 같은 실수를 반복하지 않는다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
loop-engineering/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + 루프 요약 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·도구 경계
├── agents/                         # 모두 model: "opus"
│   ├── goal-setter.md              # Goal — 검증 가능한 목표 + 검증 방법 + 중단조건 설계
│   ├── loop-executor.md            # Execute — 목표를 향한 1회 반복(메모리 consult + 최소 변경)
│   ├── loop-verifier.md            # Verify — 검증 방법 실행 → 엄격 PASS/FAIL + 증거
│   ├── failure-analyst.md          # Investigate — root cause 진단 + 다음 접근 작성 + 무진전 감지
│   └── memory-curator.md           # Distill/Consult — 검증된 교훈 distill, 관련 규칙 surface, raw trace 보존
├── skills/
│   └── loop-engineering/
│       ├── SKILL.md                # 오케스트레이터(진입점, Goal 게이트 → 자율 반복 루프)
│       └── references/
│           ├── loop-engineering-principles.md   # 두 루프·7원칙·검증기/중단조건 설계·anti-pattern·여섯 빌딩블록(factory §8)·참고문헌
│           ├── loop-memory-format.md            # goal.md / iterations.jsonl / lessons.md 포맷
│           └── loop-engineering-research.md     # 설계 근거 deep-research dossier (출처·인용·신뢰도·caveat)
└── evals/
    ├── evals.json                  # 수용 평가 (design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json           # 트리거 경계 평가 (should_trigger 10 / should_not 19, 인접 도메인 경계 가드)
```

## 루프 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 목표 설계 (Goal) | goal-setter | Goal Card (성공기준·검증 방법·중단조건·범위) | 승인 게이트 + 자율모드(auto/gated) 확정 |
| 1 | 루프 (Execute→Verify→Diagnose→Distill) | loop-executor → loop-verifier →(FAIL) failure-analyst → memory-curator | 반복별 verdict·진단·distill된 교훈 | 매 회 verdict 보고, gated면 반복 사이 승인 |

매 반복 보고: `[Iter n] {PASS|FAIL}: {증거/원인} — {계속|종료 사유}`. 최종: `[Loop 종료] {성공|중단:사유} — 반복 {n}/{N}, 교훈 {k}건 → .claude/loop-memory/{goal-slug}/`

## Conventions

- **검증기 우선**: 루프는 검증기만큼만 좋다. Phase 0에서 관찰형 성공기준 + *실행 가능한* 검증 방법을 못 박는다.
- **자가 검증**: 통과 판정은 loop-verifier가 증거로 한다. 증거 없는 PASS 금지.
- **재시도 전 진단**: FAIL 시 곧장 재시도하지 않고 failure-analyst가 root cause를 먼저 확정한다(증상 ≠ 원인).
- **에이전트가 개선안을 쓴다**: 다음 반복의 접근을 사람이 아니라 failure-analyst가 작성한다.
- **최소 변경**: 반복당 가장 작은 변경 1개(confound 격리).
- **지속학습 메모리**: 검증된 교훈만 distill해 lessons.md에 쌓고 관련 규칙만 consult한다. raw trace(iterations.jsonl)는 보존(요약 금지).
- **명시적 중단조건**: 통과·최대 반복·무진전·예산. 무한 루프 차단.
- **승인 게이트·관찰성**: Phase 0 Goal Card 승인은 항상. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **stay-the-engineer(사람 통제점)**: 검증·이해(merge 전 diff 읽기, green CI ≠ 구현 완료)·판단(cognitive surrender 자가점검)·병렬 상한(orchestration tax)은 자동화로 넘기지 않는다. 루프가 좋아질수록 이 결함들이 *더 날카로워진다*.
- **factory model(선택 레인)**: 여섯 빌딩블록(automations·worktrees·skills·plugins/connectors·sub-agents·external memory) 중 skills(하네스 자체)·sub-agents·external memory가 *기본 구현*이고(sub-agents는 실제 검증을 실행하는 강한 verifier로), automations·worktrees·connectors는 코어 흐름을 바꾸지 않는 *opt-in 레인*이다(상세 SKILL §8 / principles §8).
- **경계**: 작업 산출물(코드·문서)을 검증 루프로 완성한다. 하네스 자체 진단·개선·새 하네스 생성·기획문서(PRD)·커밋/PR 리뷰·native `/loop`(시간 간격 폴링)은 범위 밖이다.
- 5개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-14 | 플러그인 신설 | loop engineering(목표 기반 자율 반복 + 지속학습 메모리) 멀티 에이전트 하네스. deep-research(loop engineering 1차 자료) 근거 |
| 2026-06-15 | 2라운드 적대적 검증 후 29건 보강 | iterations.jsonl 단일 writer(memory-curator)·run-id/ts/goal.md/goal-slug 발급 주체 명시(SKILL Phase 1 초기화), BLOCKED verdict 분기 신설(검증 인프라≠작업 결함), consult-before-execute·재실행 1회차 consult, 무진전 단일 권위(failure-analyst)·예산 집행(SDK 캡/N 프록시), N/M 기호·중단조건·상태값(active/candidate/conflict/retired)·보고 문자열 정합, 인접 도메인 트리거 변별 강화 + native /goal 경계, evals.json 수용 평가 신설 |
| 2026-06-21 | 다른 플러그인 참조 제거·독립화 | 경계·마켓플레이스 네비·evals 진술에서 다른 플러그인명·상대경로 참조를 제거하고 일반 개념(범위 밖 진술)으로 일반화해 단독 사용 가능하게 정리 |
| 2026-06-23 | Loop Engineering 원전 심화 반영 (additive, 현재 기능 전부 보존) | Osmani substack "Loop Engineering" deep-research(62 confirmed/16 killed) 기반 비파괴 보강 — principles §1 포지셔닝(prompt→context→harness→loop, Cherny 앵커)·§5 이해/머지 게이트(green CI≠구현)·병렬 maker review-bandwidth·§6 사람-쪽 3결함(comprehension rot·cognitive surrender·orchestration tax)·§7 자동화 프론트엔드·act 레이어·**신규 §8 여섯 빌딩블록(factory model) 표** + research dossier §9. SKILL 내재화 원칙 stay-the-engineer + PASS 이해 게이트 + /loop 합성 명료화 + factory 전체그림. loop-verifier green-CI≠구현(reward-hacking) 가드, loop-executor worktree 격리 옵션, memory-format "state file is the spine". 코어 흐름(Phase 0/1)·기존 §1~§8 번호·evals 불변 |
