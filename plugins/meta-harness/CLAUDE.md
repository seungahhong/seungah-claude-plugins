# meta-harness

## 하네스: 메타 하네스 엔지니어링

**Goal**: 하네스(루트 CLAUDE.md + 각 SKILL.md + agents/*.md + commands/*.md + hooks = "LLM 주위의 코드")의 결함을 full-trace experience store 기반 causal reasoning으로 진단하고, Pareto frontier를 후퇴시키지 않는 패치를 사용자 승인 게이트 하에서만 제안한다.

**평가 스코프**: 매 회차 Phase 1에서 한 번에 한 질문으로 확정한다. 기본은 `repo-wide` — 패치 표적이 루트 CLAUDE.md + 임의 SKILL.md 로 한정되고 experience-store는 `.claude/experience-store/`에 둔다. `plugin`(opt-in)은 지목된 단일 플러그인의 모든 파일(plugin.json·agents·commands·hooks·SKILL.md)을 경계 안으로 끌어들이고 experience-store를 `plugins/{target}/experience-store/`에 둔다. repo-wide 경계 밖(agents/·commands/·hooks/·plugin.json·플러그인별 CLAUDE.md)을 고치려면 `scope-escalation`으로 표시하고 plugin 모드 재실행을 권고하며, 레포 루트 메타(marketplace.json 등)는 out-of-scope로 `blocked` 처리한다.

**Trigger**: (R1) 현 세션에서 "방금 그 방향 말고 다시 해줘 + 왜 그랬는지 보고 스킬/CLAUDE.md 고쳐", "이거 보강해줘, 왜 부족했는지 고도화"처럼 redirect·보강을 요청할 때. (R2) "이 플러그인 자체가 잘못 가고 있어 plugin.json까지 고쳐"처럼 plugin 심층 개선을 요청할 때. (R3) "이 _docs/xxx.md 부실한데 만든 에이전트/skill 고쳐"처럼 외부 .md를 역추적해 그 산출 주체를 고도화하라고 할 때. **모든 patch는 자동 적용 금지 — 사용자 승인 게이트 통과 후에만 적용한다.**

**실행 모드**: 서브에이전트 + 하이브리드 — 진단은 결함별 **병렬** 팬아웃(failure-diagnostician), 개선은 진단별 **순차**(pareto-refiner, 직전 patch 결과를 다음 호출에 노출). 모든 Agent 호출에 `model: "opus"`를 명시한다.

**핵심 아이디어(논문 매핑)**

| 논문 개념 | 본 플러그인 적용 |
|-----------|------------------|
| harness = LLM 주위의 코드(무엇을 저장/검색/제시할지 결정) | 최적화 대상을 CLAUDE.md/SKILL.md/agents/commands/hooks로 고정 |
| full-trace 보존이 압축 요약보다 우월(Table 3: 56.7 vs 38.7) | experience-store의 traces/는 항상 원본, 요약은 navigation 포인터에만 |
| outer loop 최소화 — parent/mutation 하드코딩 금지, proposer 위임 | 무엇을/어떻게 고칠지를 pareto-refiner(proposer)에게 위임 |
| causal reasoning over prior failures | confound 격리 → 단독검증 → regression 시 additive-first → 직교 승리 compose → run 간 transfer |
| 비싼 eval 전 lightweight validation | Phase 5에서 frontmatter/상호참조/트리거충돌/Why-없는 MUST 정적 점검으로 거름 |

**Change History**

| Date | Change | Target | Reason |
|------|--------|--------|--------|
| 2026-06-03 | Initial build | All | Meta-Harness 논문 기반 full-trace 메타 하네스 엔지니어링 플러그인 신설 |
