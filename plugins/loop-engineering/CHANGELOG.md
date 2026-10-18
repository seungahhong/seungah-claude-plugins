# loop-engineering 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-14 | 플러그인 신설 | loop engineering(목표 기반 자율 반복 + 지속학습 메모리) 멀티 에이전트 하네스. deep-research(loop engineering 1차 자료) 근거 |
| 2026-06-15 | 2라운드 적대적 검증 후 29건 보강 | iterations.jsonl 단일 writer(memory-curator)·run-id/ts/goal.md/goal-slug 발급 주체 명시(SKILL Phase 1 초기화), BLOCKED verdict 분기 신설(검증 인프라≠작업 결함), consult-before-execute·재실행 1회차 consult, 무진전 단일 권위(failure-analyst)·예산 집행(SDK 캡/N 프록시), N/M 기호·중단조건·상태값(active/candidate/conflict/retired)·보고 문자열 정합, 인접 도메인 트리거 변별 강화 + native /goal 경계, evals.json 수용 평가 신설 |
| 2026-06-21 | 다른 플러그인 참조 제거·독립화 | 경계·마켓플레이스 네비·evals 진술에서 다른 플러그인명·상대경로 참조를 제거하고 일반 개념(범위 밖 진술)으로 일반화해 단독 사용 가능하게 정리 |
| 2026-06-23 | Loop Engineering 원전 심화 반영 (additive, 현재 기능 전부 보존) | Osmani substack "Loop Engineering" deep-research(62 confirmed/16 killed) 기반 비파괴 보강 — principles §1 포지셔닝(prompt→context→harness→loop, Cherny 앵커)·§5 이해/머지 게이트(green CI≠구현)·병렬 maker review-bandwidth·§6 사람-쪽 3결함(comprehension rot·cognitive surrender·orchestration tax)·§7 자동화 프론트엔드·act 레이어·**신규 §8 여섯 빌딩블록(factory model) 표** + research dossier §9. SKILL 내재화 원칙 stay-the-engineer + PASS 이해 게이트 + /loop 합성 명료화 + factory 전체그림. loop-verifier green-CI≠구현(reward-hacking) 가드, loop-executor worktree 격리 옵션, memory-format "state file is the spine". 코어 흐름(Phase 0/1)·기존 §1~§8 번호·evals 불변 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.2. (1) 스킬 description `loop-engineering` 890자 → 520자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 454자 → 271자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 4,677자 → 1,712자 — `Structure`·`루프 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
