# 데이터 적재·지침 보강 기준 (C1~C9 + 메커니즘 선택)

> meta-harness의 **데이터 적재**(신호 캡처·experience-store)와 **지침 보강**(patch 설계)은 이 기준을 따른다.
> **자족 문서다** — 외부(.claude-local 생성물·Downloads) 파일을 포인터로 참조하지 않는다(다른 프로젝트 설치 시 깨짐). 모든 1차 출처는 항목별 인라인 표기한다.
> 적재 = "AI가 잘못 갔을 때의 교정 신호와 그 전후 맥락을 store에 남기는 일". 기록 단계에서 **놓친 정보는 나중에 되살릴 수 없다** — 그래서 기록의 첫 목표는 "원인을 짚을 수 있을 만큼 충분히, 있는 그대로" 남기는 것이다.

## 목차
1. 제1원칙 — 요약 금지 (C2)
2. 3층 적재 모델 (C3) — 사건 → 교훈 → 장치
3. C1~C9 적재 기준
4. 지침 보강 — 메커니즘 선택 (결정 절차: enforcement 분류 → CLAUDE.md / Skill / hook / permission / rule → lifecycle event → 스코프 배치)
5. 점검표
6. 정직성 단서
7. 근거 자료

---

## 1. 제1원칙 — 요약 금지, 기록은 원본 (C2)

Meta-Harness(arXiv 2603.28052v1) Table 3: 동일 결함을 고치게 했을 때 **full-trace 56.7 > scores-only 41.3 > summary 38.7**(셋 다 같은 Table 3 보고값). 즉 **요약(38.7)은 점수만 주는 것(41.3)보다도 못하다** — 요약은 "어느 step에서 무엇이 무엇을 야기했나"라는 인과 사슬을 뭉갠다. 기록 단계에서 잃은 단서는 복구 불가다.

- `traces/*.jsonl`·`signals/*.jsonl` 은 **항상 원문**(발화·diff·.md 전문). 요약·절단·payload 누락 금지.
- 요약은 **navigation 보조물에만**(`index.json`·`recurring-patterns.md`) — "어디를 grep할지" 가리키는 포인터이지 진단 근거가 아니다.
- 이는 이 플러그인의 기존 제1불변식과 동일하다 — 본 기준은 이를 **강화**할 뿐 바꾸지 않는다.

## 2. 3층 적재 모델 (C3) — 사건 → 교훈 → 장치

기록을 한 종류(원시 로그)만 쌓지 않는다. 사건/교훈/절차로 분화하는 이 3층은 **플러그인 설계 선택**으로, 에이전트 기억 3종 분류(arXiv 2603.07670)에 느슨히 동기를 둔다 — 단 그 논문은 여기서 **재검증하지 않았다**(§6).

| 층 | 비유 | 무엇 | meta-harness 위치 | 메커니즘 |
|----|------|------|-------------------|----------|
| ① 사건 기록 | 블랙박스 | 발화·직전 산출물·쓰던 스킬을 원형으로 | `signals/`·`{run}/{candidate}/traces/` | UserPromptSubmit 훅 **exit 0 = "record an event"**(비차단 로깅) |
| ② 교훈 정리 | 사고분석 보고서 | 반복되는 원인·패턴 | `recurring-patterns.md` | experience-historian 큐레이션 + **사람 검토 .md는 R3로 ingest** |
| ③ 장치화 | 안전벨트 경고음 | 다음엔 자동으로 막기 | hook / permission / 필수 입력칸 | **"반복 무시되는 규칙은 hook로 전환"** — advisory 규칙은 guardrail이 아니다 |

- **③ 장치화 핵심**: prompted 규칙은 advisory라 압박(긴 세션·모호한 상황·prompt injection) 하에 건너뛸 수 있다. "절대 ~해야/하면 안 된다"가 **반드시** 지켜져야 하면 instruction이 아니라 **deterministic enforcement(hook·permission)** 로 둔다. 근거가 **본질적으로 결정론(매번 강제)** 이면 hook/permission은 ≥3회 반복 뒤의 폴백이 아니라 **첫 발생부터의 1급 선택**이다 — 반복 무시는 advisory로는 부족하다는 *추가* 신호일 뿐이다. 반복적으로 무시되는 규칙의 처방은 "ruthlessly prune → hook로 전환". 어느 lifecycle event로 장치화할지는 자족 reference [hook-lifecycle.md](./hook-lifecycle.md)로 고른다. (근거: 스티어링 가이드 / best-practices / hooks doc)
- **사람의 교훈 정리**(검토·회고 .md)는 자동 기록과 따로 놀지 않게 한다 — R3 경로로 ingest해 ②(교훈)·③(장치)로 승격한다. 최고의 수정은 흔히 사람의 정리에서 나온다. **단, 입력 성격이 다르다**: R3의 기본 의도는 "그 .md를 *생성한* 에이전트/skill을 3단 폴백으로 역추적"이지만, 사람이 손으로 쓴 회고에는 생성 skill이 없다 → 이때는 역추적을 강제하지 말고 `provenance: human-authored`(생성 주체 없음)로 표기하고 **교훈 소스로 원형 적재**한다(C2). 역추적 대상은 그 회고가 *지목하는* 결함 표적이지, 회고 .md 자체의 생산자가 아니다.

## 3. C1~C9 적재 기준

| # | 한 줄 | meta-harness 적용 | 근거 |
|---|-------|-------------------|------|
| **C1** | 한 줄 말고 **한 묶음** | 〔발화〕+〔직전 AI 산출물〕+〔그때 active SKILL〕을 한 묶음으로 캡처(trace-capturer). 증상만으론 원인을 못 짚는다 | full-trace 우월(Table 3) |
| **C2** | 요약 말고 **원문** | §1 제1원칙 | Table 3 |
| **C3** | 사람 정리도 **데이터** | §2 3층 모델 | arXiv 2603.07670 |
| **C4** | **그 순간**에 기록 | 발화 순간 lightweight identifier(`transcript_path`·`cwd`·`session_id`·active-skill)를 함께 적재. transcript는 immutable persistent storage라 `transcript_path` 역추적이 견고하다(JIT 패턴) — §6 단서 참조 | JIT / structured note-taking |
| **C5** | **같은 한 곳**에 | store-root = **프로젝트 최상단**(git root, 없으면 cwd). 어느 하위 폴더에서 캡처/실행해도 한 곳에 모인다. `signals/`는 훅이 캡처 시점에 스코프를 모르므로 **항상 repo-wide `.claude/experience-store/signals/`** 단일 레인(plugin 스코프 회차도 여기서 읽음) | 흩어진 기록은 조용히 사라짐 |
| **C6** | 안 버림 **≠ 무한정** | 신호에 `status`(new\|deferred\|consumed) 상태 전이 + 오래된 신호는 **압축 보관**(삭제 금지, **선택·수동 권고** — experience-historian이 Phase 8에서 후보로 보고만 함) | 정리 규칙 부재 시 비용 무한 증가 |
| **C7** | 많이 잡되 **등급** | `strength`(strong\|weak) 구분. 단순 재실행("다시 빌드/실행")=weak, 교정("틀렸/아니/바꿔/빼줘/빠졌")=strong. 흔한 한국어 교정어를 놓치지 않게 패턴 확장 | 헛잡음은 지울 수 있지만 놓친 건 흔적 없이 사라짐 |
| **C8** | **고칠 곳**까지 + 이름 통일 | `target.kind`에 claude-md·skill-body·agent·orchestrator·plugin-metadata·**hook·permission·rule**(결정론 장치) + **global-memory**(전역 메모리) 칸 + `enforcement_class`. `cause_class`(예: `primary-source-substitution`). 경로는 **canonical로 통일**(이름 쪼개짐 방지 → recurring 카운트 정확) | 갈 곳 없는 신호는 멈추고, 이름이 쪼개지면 반복 감지 실패 |
| **C9** | 기록 **≠ 정답**, 검증 후 재사용 | proposer(만든 쪽)의 self-report(Pareto 좌표·trigger_eval 통과율)는 **검증 대상 주장**이다 — Phase 5/독립 단계가 재확인하고 **사람 승인 후에만** 재사용 | 미검증 경험 재사용은 오류를 퍼뜨림(arXiv 2505.16067 — §6 재검증 안 함) |

## 4. 지침 보강 — 메커니즘 선택 (결정 절차)

보강(patch)을 **어디**에 둘지는 표적 kind 선택과 직결된다. **표적 kind를 고르기 전에 먼저 근거의 *enforcement 성격*을 분류**한다 — 결정론적 근거를 advisory 본문(CLAUDE.md/Skill)에만 적으면 압박 하에 무시될 수 있기 때문이다(advisory ≠ guardrail). 이 분류는 같은 표적이 ≥3회 반복된 뒤의 폴백이 아니라, **첫 발생부터** 적용하는 1급 선택이다.

### 4-1. 1단계 — enforcement 성격 분류

| 성격 | 판정 질문 | 매핑 메커니즘 |
|------|----------|---------------|
| **deterministic-enforce** | LLM 판단으로 **건너뛰면 안 되는** 강제(매번 반드시 일어나거나 막혀야)인가? | **hook(command/http/mcp_tool)** 또는 **`permissions`(allow/deny/ask)** |
| **deterministic-record** | 매번 **반드시 기록/캡처**(비차단)되어야 하는가? | **hook(exit 0 = record-an-event)** |
| **judgment** | 모델이 **맥락을 해석**해 판단해야 하는가? | `CLAUDE.md`(항상 로드 사실)·`Skill`(절차)·판단형 hook(prompt/agent) |

> **정정 — `.claude/rules`는 결정론이 아니다.** rules도 CLAUDE.md처럼 **advisory(모델 해석 컨텍스트)** 다(공식 [memory](https://code.claude.com/docs/en/memory): "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a `PreToolUse` hook instead"). 결정론적 강제 수단은 **hook(command/http/mcp_tool) + permissions** 뿐이다. rules의 올바른 쓰임은 **path-scoped 컨텍스트 비용 최적화**(필요할 때만 로드)이지 enforcement가 아니다.

### 4-2. 2단계 — 표적 본문(advisory) 매트릭스

`judgment`로 분류됐을 때 본문을 어디에 둘지.

- **루트 CLAUDE.md** — 매 세션 로드되므로 **넓게 적용되는 안정적 사실·원칙만**. removal test: *"이 줄을 빼면 Claude가 실수하나? 아니면 잘라라."* 비대해지면 진짜 규칙이 노이즈에 묻혀 무시된다(목표 <~200줄). (근거: [best-practices](https://code.claude.com/docs/en/best-practices), [memory](https://code.claude.com/docs/en/memory))
- **Skill** — 가끔만 쓰는 **절차적** 워크플로(배포/리뷰/릴리스 등). on-demand 로드(progressive disclosure). description은 **3인칭 + what(무엇) + when(언제 트리거)**. (근거: [steering blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more), [skills best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices))
- **path-scoped rule(`.claude/rules/*.md` + `paths:`)** — 특정 파일/경로에서만 로드되어야 하는 **advisory** 컨텍스트(비용 최적화). unscoped rule은 CLAUDE.md에 넣는 것과 기계적으로 동일하다. (근거: [memory](https://code.claude.com/docs/en/memory), steering blog)
- **right altitude / 최소·고신호** — brittle 하드코딩과 vague 추상 사이의 골디락스. "기대 동작을 온전히 그리는 최소 정보"를 노린다. (근거: [context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents))

### 4-3. 3단계 — hook이면 **라이프사이클 event를 고른다**

`deterministic-*`로 분류돼 hook으로 장치화하기로 했으면, **상황에 맞는 event**(UserPromptSubmit/PreToolUse/PostToolUse/Stop/SessionStart/PreCompact…)와 exit/제어(record=exit 0 / enforce=exit 2·`permissionDecision:"deny"`)를 **자족 reference [hook-lifecycle.md](./hook-lifecycle.md)** 의 §3 상황→event 선택 표로 고른다. 하드 금지/허용은 hook보다 `permissions.deny/allow`가 견고(우선순위 최상). 막되 판단이 필요하면 prompt/agent type hook.

### 4-4. 4단계 — 스코프에 맞게 **배치**

메커니즘 선택은 스코프 무관, 배치는 패치 경계를 따른다([hook-lifecycle.md §6](./hook-lifecycle.md)):
- **plugin 모드** → 플러그인 hook(`plugins/<p>/hooks/hooks.json`+스크립트)·rule은 in-boundary → 정상 patch.
- **repo-wide** → 플러그인 hook 표적은 경계 밖 → `scope-escalation` **+ 제안 hook_spec 동봉**(event·matcher·exit·스크립트 스케치)로 plugin 모드 재실행 권고.
- **프로젝트 `.claude/settings.json`(hooks/permissions)** → meta-harness는 settings.json을 **직접 수정하지 않는다**(P2; `update-config` 스킬·사용자 영역) → 구체 spec을 담아 **update-config 핸드오프**로 권고.

→ 본문 비대·중복(제품 기본 동작과 겹침)은 **제거 후보**(rule-body-cost↓ = Pareto 승리, P1). 같은 표적 **반복(≥3)** 이면 본문을 더 더하지 말고 **Skill 추출**(절차) 또는 **hook/permission 전환**(반복 무시 규칙 = ③ 장치화)을 권고한다. **단, 안전장치(승인 게이트·Pareto 비후퇴·full-trace)는 제거·약화 표적으로 삼지 않는다(P2).**

## 5. 점검표 (적재·patch 설계 시 자가 점검)

- [ ] **C1** 이 기록만으로 "무엇이 무엇 때문에"를 짚을 수 있나? (발화+직전결과+active SKILL)
- [ ] **C2** 원문을 자르거나 요약하지 않았나? 요약은 navigation에만 있나?
- [ ] **C3** 사람의 교훈 정리를 담을 자리(R3 ingest)와 장치화 경로가 있나?
- [ ] **C4** 그 순간 lightweight identifier를 함께 고정했나?
- [ ] **C5** 프로젝트 최상단 한 곳에 모이나?
- [ ] **C6** status가 전이되나? 오래된 건 압축 보관(삭제 아님) 규칙이 있나?
- [ ] **C7** 많이 잡되 strong/weak를 구분하나? 흔한 교정어를 놓치지 않나?
- [ ] **C8** 고칠 수 있는 모든 종류(전역 메모리 포함)에 칸이 있나? 경로를 canonical로 세나?
- [ ] **C9** 기록과 판단을 분리했나? self-report를 검증 없이 재사용하지 않나?

## 6. 정직성 단서 (verbatim 미확보·간접 도출 명시)

- **promotion threshold(≥3)와 capture record schema는 공식 출처가 명시하지 않는다** — 플러그인 자체 휴리스틱(간접 도출). 안전선은 사람 승인 게이트다. (deep-research open question으로 확인)
- **C4 재해석**: JIT/lightweight-identifier 원칙상 immutable transcript의 `transcript_path` 역추적은 견고하다 → 기준 문서의 "나중 복원은 거의 실패"는 **코드/스킬 상태가 바뀌는 경우**에 한한다. 따라서 meta-harness는 발화 순간 식별자를 적재(C4 충족)하되, 직전 산출물·active SKILL은 transcript 역추적으로 복원하는 하이브리드를 정상 경로로 둔다.
- **수치**(56.7/41.3/38.7)는 Meta-Harness 논문 Table 3 인용치(논문 보고값).
- arXiv **2606.13174**(사용자 교정 강제 장치화 TRACE)·**2505.16067**(미검증 경험 재사용 위험)·**2603.07670**(에이전트 기억 3종)은 **데이터 적재 기준 문서의 검증 근거를 그대로 인용**한 것으로, 여기서 재검증하지 않았다.
- **3-0 만장일치 확인의 범위 한정** — "독립 리서치 3-0 만장일치 확인(과정 보고 — 재현 불가)"은 **v0.3.0 advisory 메커니즘 매트릭스의 Anthropic 출처(context-engineering·best-practices·steering blog)에만** 해당한다. v0.4.0에서 추가된 hooks 라이프사이클·rules(memory·hooks·hooks-guide·skills·settings) 사실은 `/deep-research` 워크플로 실패 후 **단일 에이전트 직접 fetch**로 grounding했고 3-0 투표를 거치지 않았다 — 대신 등급(VERBATIM/요약/추론)을 붙여 [hook-lifecycle.md](./hook-lifecycle.md) §7·§8 + [hooks-grounding.md](./hooks-grounding.md)에 보존했다(§4-1의 "rules=advisory" 정정은 memory 페이지 VERBATIM 근거).

## 7. 근거 자료 (1차 출처)

- 최소·고신호 / right altitude / JIT / structured note-taking: <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- 메커니즘 선택 / removal test / over-specified→hook 전환: <https://code.claude.com/docs/en/best-practices>
- 스티어링(절차→Skill, guardrail=hook·permission, 압박 하 규칙 실패, name+description만 로드): <https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more>
- hook 이벤트·exit code(exit 0 로깅 / exit 2 차단)·UserPromptSubmit·라이프사이클 전체: <https://code.claude.com/docs/en/hooks> · <https://code.claude.com/docs/en/hooks-guide> (event별 선택·exit/제어·config·matcher 정리는 자족 [hook-lifecycle.md](./hook-lifecycle.md))
- rules는 advisory(결정론 아님) / 결정론 강제는 hook·permission뿐 / "must run at a specific point → hook": <https://code.claude.com/docs/en/memory>
- Skill description 3인칭·what+when·conciseness: <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- CLAUDE.md <200줄 목표: <https://code.claude.com/docs/en/memory>
- full-trace 우월(Table 3): "Meta-Harness: End-to-End Optimization of Model Harnesses", arXiv 2603.28052v1
- (기준 문서 근거, 재검증 안 함) 사용자 교정 강제 장치화: arXiv 2606.13174 · 미검증 경험 재사용 위험: arXiv 2505.16067 · 에이전트 기억 3종: arXiv 2603.07670
