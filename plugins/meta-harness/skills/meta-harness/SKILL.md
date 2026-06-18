---
name: meta-harness
description: >-
  하네스(루트 CLAUDE.md + 각 SKILL.md + agents/*.md + commands/*.md + hooks = "LLM 주위의 코드")의 결함을
  full-trace experience store로 진단·개선하는 메타 오케스트레이터. 다음 트리거에 반드시 발동한다 —
  (R1 현세션) "방금 그 방향 말고 다시 해줘, 왜 그랬는지 보고 지금 쓰던 스킬 고도화", "이거 보강해줘, 왜 부족했는지
  루트 CLAUDE.md/스킬 고도화", "이 실수 반복 안 하게 지금 스킬 고쳐", "지금 세션 동작 보고 루트 지침 업데이트해줘";
  (R2 plugin) "이 플러그인 자체가 잘못 가고 있어 plugin.json까지 고쳐"; (R3 외부 .md 역추적)
  "이 _docs/xxx.md 부실한데 만든 에이전트/skill 고쳐", "이 산출물 만든 skill 고도화". 또
  "이전 후보들 source/score/trace 파일로 깔아두고 grep해서 다음 후보 제안", "정합 올리되 본문비용 안 늘리게
  Pareto 유지하며 후보 뽑아", "왜 이렇게 동작했는지 진단하고 하네스 고도화"에 발동한다. 모든 패치는 사용자 승인
  게이트 통과 후에만 적용한다(자동 적용 금지). 발동하지 않는다 — 새 하네스/에이전트 팀을 처음부터 만들기, 스킬 하나
  새로 작성·벤치마크, PR/앱 코드 리뷰·버그 찾기, 기술 문서 새로 생성, settings.json 설정 변경, OKR/비-하네스 자산
  평가, trajectory를 시간순 표로 정규화만, 함수 리팩터링, 깨진 테스트 수정, 커밋 메시지 작성.
---

# Meta-Harness — 하네스 엔지니어링 메타 오케스트레이터

## 왜 full-trace인가

하네스 결함을 압축 요약으로 진단하면 진범을 놓친다. "Meta-Harness: End-to-End Optimization of Model Harnesses"(arXiv 2603.28052v1) Table 3은 동일 조건에서 **full-trace 56.7 vs summary 38.7**로, 원형 궤적을 보존한 진단이 요약 기반 진단을 압도함을 보였다. 요약은 "어느 step에서 어떤 도구가 무엇을 반환했는가"라는 인과 사슬을 뭉갠다. 따라서 이 플러그인의 제1원칙은 **traces/는 항상 원본, 요약은 navigation(index/recurring)에만**이다. 진단 에이전트는 store의 raw trace를 grep/cat으로 직접 선택 조회하여, evidence를 요약문이 아닌 **trace의 step 번호·파일 경로**로 인용한다.

하네스란 LLM 주위의 코드 — 무엇을 저장/검색/제시할지 결정하는 층 — 이다. 이 레포에선 루트 CLAUDE.md / 각 SKILL.md / agents / commands / hooks가 그 최적화 대상이다.

## 실행 모드

- **서브에이전트 + 하이브리드.** 캡처·진단·개선·큐레이션은 전용 에이전트로 spawn한다. 오케스트레이터는 Phase 5 lightweight validation과 Phase 7 적용(Edit/Write)을 직접 수행한다.
- **모든 Agent 호출에 `model: "opus"` 명시.**
- **stall 방지.** 병렬 팬아웃(Phase 3) 한 배치는 결함 **4~6건 이하**. 각 진단 에이전트의 read 범위를 표적 자산으로 축소해 stall을 막는다.
- **outer loop 최소화.** 무엇을/어떻게 고칠지를 하드코딩하지 않고 proposer 에이전트에게 위임한다. 더 강한 모델이 오면 자동으로 좋아진다.
- **조건부 병렬 — 독립=병렬 / 의존=순차 / 공유상태=단건 (F1 근거).** 단계 내 항목이 **독립적**일 때만 병렬 팬아웃한다(Phase 3 진단이 canonical — 워커 수는 결함 수로 런타임 결정). 직전 산출에 의존하면 순차(Phase 4), append-only 공유 상태면 단건(Phase 8). 병렬은 기본값이 아니라 독립성·작업가치 게이트를 통과할 때만 — 멀티에이전트는 토큰 비용이 크므로 저가치 단건엔 순차가 낫다. 이는 새 기능이 아니라 초기 빌드부터의 실행 모델을 뒷받침하는 근거다. (근거: *Building effective agents* / *multi-agent research system*)

## 평가 스코프

| 모드 | 발동 | 패치 표적 경계 | experience-store 위치 |
|------|------|----------------|----------------------|
| `repo-wide`(기본) | 기본값 | 루트 CLAUDE.md + 임의 SKILL.md **만** | `.claude/experience-store/` |
| `plugin`(opt-in) | 명시 요청 시 | 지목 플러그인의 **모든** 파일 | `.claude/plugin-store/{target}/` |

repo-wide 경계 밖(agents/·commands/·hooks/·plugin.json·플러그인별 CLAUDE.md)은 patch 없이 `scope-escalation`(plugin 모드 재실행 권고). 레포 루트 메타(`.claude-plugin/marketplace.json` 등)는 `out-of-scope` → `blocked`(사용자 직접). 상세는 [references/scope-and-targets.md](./references/scope-and-targets.md).

## 핵심 원칙

- **full-trace 보존** — store에 요약을 넣는 순간 Table 3의 Scores+Summary로 퇴화한다. traces/는 원본.
- **자동 적용 금지** — 모든 patch는 Phase 6 사용자 승인 게이트 통과 후에만 오케스트레이터가 적용한다.
- **결함 1건 = 진단 1건 = 패치 1건** — 진단·개선 단위를 결함 단위로 고정한다.
- **additive-first** — 본문을 덜어내기보다 더하는 변경을 먼저 시도하고, 직교 승리만 compose한다.
- **3회 누적 → 구조 재설계** — 같은 표적이 3회 누적되면 본문 patch를 거절하고 `structural-redesign-required`를 권고한다.
- **Pareto 비후퇴** — 채택 후보는 4축(behavior-alignment·rule-body-cost·trigger-precision·generalization) 어느 것도 frontier를 후퇴시키지 않는다. 상세는 [references/pareto-axes.md](./references/pareto-axes.md).
- **outer-loop 최소화** — parent/mutation 선택을 proposer에게 위임한다.

## 연구 근거 원칙 (claude 특화 — 진단·개선에 적용)

아래는 1차 출처(Anthropic 엔지니어링 문서 / peer-reviewed 논문)에 근거해 도입한 운영 원칙이다. 기존 안전장치를 우회하지 않으며, 적용은 항상 승인 게이트·Pareto 비후퇴를 거친다. 각 원칙의 1차 출처는 항목별 괄호에 인라인 표기한다.

- **P1 중복 규칙 제거 = Pareto 승리.** 제품 기본 동작과 겹치거나 모델이 이미 하는 걸 또 지시하는 잉여 규칙(over-prompting)은 정합 이득 없이 rule-body-cost만 올린다 → 제거 후보로 진단한다(삭제는 승인 게이트 필수). (근거: context engineering — 최소·고신호·"Claude는 이미 똑똑하다"; '모델 향상→중복 제거' 프레이밍은 직접 문장이 아니라 **간접 도출**)
- **P2 안전장치 보호.** 승인 게이트·Pareto 비후퇴·full-trace 보존·검증 Phase·경계 재확인은 patch로 **삭제·약화하지 않는다**(자기개선 효능엔 반례·수렴보장 부재). (근거: arXiv 2303.11366 / 2507.19457)
- **P3 경량 경로(작은 작업).** 단건·저위험 변경(예: description 오타 1건)은 전체 Phase 0~8을 강제하지 않고 필요한 Phase만 거친다(progressive disclosure). (근거: Agent Skills — conditional details / just-in-time)
- **P4 반복 절차 → Skill.** 같은 절차가 누적(≥3 needs_attention)되면 본문 규칙을 더하기보다 Skill 추출을 권고한다(사실은 지침에·절차는 Skill에). (근거: Agent Skills best-practices)
- **P5 전역 지침은 최소·고신호.** 루트 CLAUDE.md/전역 지침엔 **안정적인 사실·원칙만** 두고 절차·가변 세부는 Skill/reference로 내린다(*최소 ≠ 짧게* — minimal does not necessarily mean short). (근거: context engineering — optimal token set / right altitude)

## 산출물 배치 규약

- **experience-store**(영속) — `.claude/experience-store/`(repo-wide) 또는 `.claude/plugin-store/{target}/`(plugin). `history.jsonl`·`index.json`·`pareto.json`·`recurring-patterns.md`·`patches/`·`{run}/{candidate}/{harness,score.json,traces/}`.
- **_workspace**(휘발) — `.claude/_workspace/{run}/{phase}_*.json`·`*_decisions.json`·`{run}_summary.md`. 새 실행 시 직전 회차는 `.claude/_workspace_prev/`로 이동.

상세 스키마는 [references/experience-store-schema.md](./references/experience-store-schema.md), 실행 유형 판별은 [references/execution-types.md](./references/execution-types.md).

---

## Phase 0 — 컨텍스트 확인

`experience-store/`와 `.claude/_workspace/`를 검사해 실행 유형을 자동 판별한다.

- store·workspace 모두 없음 → **초기**
- store 있고 workspace 비었음 → **신규 회차**
- 진행 중 workspace 잔존 → **부분 재실행**
- 명시적 새 실행 요청 → **새 실행**(직전 workspace를 `.claude/_workspace_prev/`로 이동)

판별 후 1줄로 보고한다. 예: `[Phase 0] 신규 회차 (run-2026-06-03-01). 직전 store 3 candidate 존재.`

## Phase 1 — 트리거 유형 + 스코프 확정

1. **트리거 유형 판별** — R1(현세션 redirect·보강) / R2(plugin 심층) / R3(외부 .md 역추적) 중 무엇인지 결정한다. 모호하면 한 번에 한 질문으로 확인한다.
2. **스코프 확정** — repo-wide(기본) / plugin(opt-in). R2거나 사용자가 특정 플러그인 심층을 명시하면 plugin. 한 번에 한 질문.
3. **warm-start** — `recurring-patterns.md`의 `needs_attention`(≥3) 표적을 먼저 읽어 이번 회차 경고 후보로 적재한다. 추가로 **`signals/*.jsonl`(UserPromptSubmit 훅이 과거 세션에 적재한 미소비 redirect/fix/augment 발화)** 을 읽어 이번 회차 결함 후보로 끌어온다 — 사용자가 지금 명시 트리거하지 않아도, 누적 신호가 있으면 "이전에 '…수정해줘'라고 하신 N건을 지금 진단할까요?"로 1줄 제안한다. 소비한 신호는 Phase 8에서 `index.json`에 소비 회차 포인터를 남겨 중복 재진단을 막는다(원본 signals 줄은 보존).
4. **fast-path 판정 (P3 경량 경로)** — 결함이 **단건·저위험**(예: description 오타 1건, 상호참조 경로 한 줄)이면 경량 경로로 라우팅한다: Phase 3 병렬 팬아웃을 **단건 진단**으로 축약하고 Phase 8 큐레이션·warm-start를 생략 가능으로 둔다. **단, 안전장치는 fast-path에서도 생략 금지** — Phase 5 검증·Phase 6 승인 게이트·Phase 7 경계 재확인은 항상 거친다(P2). (근거: progressive disclosure / just-in-time)

## Phase 2 — 신호 캡처 (trace-capturer 1회)

R1: redirect 발화 **원문** + 직전 AI 산출물 + active SKILL을 시간순 원형 trace로 정규화한다. R3: 대상 .md 전문 + 3단 폴백 출처 역추적(① 산출 경로 규약 매칭 high → ② 파일 내 generated-by/메타마커 high → ③ 구조·문체 + git blame medium/low). raw trace를 `traces/*.jsonl`에 **원형 적재(요약·payload 누락 금지)**.

> **signals 레인 소비(cross-session)** — Phase 1 warm-start가 `signals/*.jsonl`의 미소비 발화를 이번 회차 후보로 끌어온 경우, trace-capturer에 그 signal의 `raw`(발화 원문)와 `transcript_path`를 함께 넘긴다. trace-capturer는 `transcript_path`를 역추적해 그 시점의 직전 산출물·active SKILL을 `traces/*.jsonl`로 정규화한다(원형 보존). 즉 훅이 적재한 신호는 **회차를 시작시키는 입력**일 뿐, 그 자체로 진단·패치가 아니다 — 진단은 Phase 3, 적용은 Phase 6 승인 게이트 통과 후 Phase 7에서만. 스키마는 [references/experience-store-schema.md](./references/experience-store-schema.md)의 `signals/*.jsonl` 참조.

```
Agent(
  subagent_type="trace-capturer",
  model="opus",
  prompt="""
  [스킬 경로] plugins/meta-harness/skills/session-signal-capture/SKILL.md 방법론을 따른다.
  [평가 스코프] {repo-wide|plugin:{target}}
  [트리거 유형] {R1|R3}
  [입력] R1: redirect 발화 원문 + 직전 산출물 경로 + active SKILL 경로
         R3: 대상 .md 경로(전문) — 3단 폴백으로 출처 에이전트/skill 역추적 + confidence 부여
  [산출] {store-root}/{run}/{candidate}/traces/*.jsonl 에 원형 raw trace 적재(요약 금지).
         출처 역추적 결과는 .claude/_workspace/{run}/phase2_origin.json 에 confidence와 함께 기록.
  """
)
```

## Phase 3 — 진단 (failure-diagnostician, 병렬 팬아웃)

결함별 **병렬** 팬아웃 — 한 메시지에서 동시 spawn, **한 배치 ≤4~6건**. 각 에이전트는 read 범위를 표적 자산으로 축소한다. proposer는 experience-store를 grep/cat으로 직접 조회하고, confound를 먼저 의심하며, evidence를 trace step 번호/파일 경로로 인용한다. 표적 kind(`description|skill-body|agent|orchestrator|claude-md|plugin-metadata`)와 `scope_status`(in-boundary|scope-escalation|out-of-scope), severity/confidence를 판정한다.

```
# 한 메시지에서 결함 수만큼 동시 spawn (배치 ≤ 4~6)
Agent(
  subagent_type="failure-diagnostician", model="opus", run_in_background=true,
  prompt="""
  [스킬 경로] plugins/meta-harness/skills/causal-diagnosis/SKILL.md 루브릭을 따른다.
  [평가 스코프] {repo-wide|plugin:{target}}  ← 경계 밖 표적은 scope_status로 표시만, 패치 금지.
  [결함] defect-{n}: {한 줄 요약}
  [조회] {store-root}/{run}/{candidate}/traces/*.jsonl 를 grep/cat 직접 선택 조회.
         confound(두 실패의 공통 변경) 먼저 의심.
  [산출] .claude/_workspace/{run}/phase3_diag_{n}.json
         {target_kind, target_path, scope_status, root_cause, evidence:[step/path], severity, confidence}
  """
)
Agent(subagent_type="failure-diagnostician", model="opus", run_in_background=true, prompt="...defect-2...")
Agent(subagent_type="failure-diagnostician", model="opus", run_in_background=true, prompt="...defect-3...")
```

## Phase 4 — 개선 (pareto-refiner, 순차)

진단별 **순차** — 직전 patch 결과를 다음 호출 프롬프트에 노출한다. additive-first → compose(직교 승리만) → transfer(과거 회차 교훈을 raw trace 재확인 후). 산출 `patch.md`(unified-diff + 위아래 3줄) + Pareto 좌표 + (description 수정 시) trigger_eval(should-trigger/should-not 8~10개씩). **patch만 생성, 자동 적용 금지.** 같은 표적 3회 누적이면 본문 patch 거절 + `change_kind:"structural-redesign-required"`.

```
# 진단 순서대로 순차 호출 — 직전 patch 결과를 다음 prompt에 전달
Agent(
  subagent_type="pareto-refiner", model="opus",
  prompt="""
  [스킬 경로] plugins/meta-harness/skills/pareto-refinement/SKILL.md 방법론을 따른다.
  [평가 스코프] {repo-wide|plugin:{target}}  ← scope-escalation/out-of-scope 표적은 patch 대신 change_kind만.
  [진단] .claude/_workspace/{run}/phase3_diag_{n}.json
  [직전 patch 결과] .claude/_workspace/{run}/phase4_patch_{n-1}.json (없으면 생략)
  [전략] additive-first → compose(직교 승리만) → transfer(raw trace 재확인 후).
         같은 표적 3회 누적 → 본문 patch 거절, change_kind:"structural-redesign-required".
  [산출] .claude/_workspace/{run}/phase4_patch_{n}.json
         + {store-root}/{run}/{candidate}/ 후보 자산 + score.json(assertion + Pareto 좌표)
         patch.md = unified-diff(±3줄). description 수정 시 trigger_eval(should-trigger/should-not 8~10개).
  """
)
```

## Phase 5 — lightweight validation (오케스트레이터 직접)

비싼 적용 전 값싸게 거른다. **frontmatter 파싱**(name/description만 존재하는가), **상호참조 경로 존재**, **트리거 충돌**, **Why-없는 MUST/NEVER** 정적 점검. `interface-invalid` 후보는 탈락시키고 사유를 `.claude/_workspace/{run}/phase5_validation.json`에 남긴다.

## Phase 6 — 사용자 승인 게이트 (필수)

결함별로 **why를 먼저** 보여준 뒤 accepted/rejected/deferred를 수집한다(일부만 결정해도 진행). `confidence:low`(특히 R3 역추적)면 **출처 확인 질문을 선행**한다. `scope-escalation`·반복 패턴(≥3) 경고를 노출한다. 결정은 `.claude/_workspace/{run}/{run}_decisions.json`에 기록한다.

## Phase 7 — 적용 (accepted만)

적용 직전 **스코프 경계를 재확인**(방어선)한 뒤 Edit/Write로 적용한다. 동일 파일 다중 patch는 묶어 적용한다. 적용된 patch 사본은 `{store-root}/patches/{date}-{target-slug}.md`에 보관한다.

## Phase 8 — 큐레이션 (experience-historian 1회)

```
Agent(
  subagent_type="experience-historian", model="opus",
  prompt="""
  [평가 스코프] {repo-wide|plugin:{target}}  → store-root 결정.
  [입력] .claude/_workspace/{run}/ 전체 + 적용 결정.
  [산출] {store-root}/history.jsonl(append-only) + index.json(navigable 포인터)
         + pareto.json(빈도×severity frontier 재계산)
         + recurring-patterns.md(표적별 카운트 + needs_attention ≥3 nudge)
  [불변식] 요약은 index/recurring(navigation)에만. traces/는 절대 건드리지 않는다(원본 보존).
           이번 회차가 소비한 signals/*.jsonl 발화는 index.json에 소비 회차 포인터로 표시(중복 재진단 방지) — 단 원본 signals 줄은 보존, 삭제·수정 금지.
  """
)
```

## 마지막 — R4 최종 보고 (필수)

완료 후 무엇을/왜/어디를 고도화했는지 **3축 표**로 반드시 출력한다.

| 트리거(R) | 표적(kind·path) | 변경 종류 | 왜 문제였나 (+근거 step/path) | 결정(a/r/d) | 적용 |
|-----------|-----------------|-----------|------------------------------|-------------|------|
| R1 | skill-body · skills/.../SKILL.md | additive | redirect 발화가 트리거 미스 — trace step 4 | accepted | ✓ |

---

## 데이터 전달 전략 매트릭스

| 방식 | 용도 | 위치 |
|------|------|------|
| 파일 기반 | Phase 간 휘발 산출(진단/패치/결정) | `.claude/_workspace/{run}/*.json` |
| 반환 기반 | 에이전트 1회 호출 즉시 요약 회신(분기 판단용) | 에이전트 final message |
| 영속 store | 회차 간 transfer 대상(raw trace·ledger·frontier) | `{store-root}/...` |

원칙: raw trace·ledger·frontier는 **영속 store**, Phase 간 중간물은 **파일 기반**, 오케스트레이터의 즉시 분기 판단은 **반환 기반**.

## 에러 정책

- **진단 실패** — 해당 결함을 `confidence:low`로 격하하고 Phase 6에서 사용자에게 재확인. 배치 전체를 막지 않는다.
- **scope-escalation** — 경계 밖 표적은 patch 없이 plugin 모드 재실행을 권고(보고 표에 명시).
- **blocked** — 레포 루트 메타는 사용자 직접 수정 안내, 자동 patch 금지.
- **stall 폴백** — 병렬 배치에서 지연 에이전트는 read 범위를 더 축소해 단건 재spawn. 배치 크기 6 초과 금지.
- **patch 충돌** — 동일 파일 다중 patch는 Phase 7에서 묶어 적용. 충돌 시 후행 patch를 deferred로 돌리고 사용자에게 재진단 제안.
- **3회 누적** — 본문 patch 거절 + `structural-redesign-required` 권고를 Phase 6 경고로 노출.

## 테스트 시나리오

**정상 흐름 — R1 현세션 redirect → SKILL.md description 패치**
- Phase 0: store 존재·workspace 빔 → 신규 회차 보고.
- Phase 1: R1 판별, repo-wide 확정, recurring-patterns warm-start.
- Phase 2: trace-capturer가 redirect 원문 + 직전 산출물 + active SKILL을 traces/에 원형 적재.
- Phase 3: failure-diagnostician 1건 진단 → kind:description, in-boundary, confidence:high.
- Phase 4: pareto-refiner additive patch + should-trigger/should-not 8~10개 trigger_eval 생성.
- Phase 5: frontmatter·상호참조·트리거 충돌 통과.
- Phase 6: why 제시 → accepted.
- Phase 7: 스코프 재확인 후 SKILL.md description Edit 적용.
- Phase 8: history/index/pareto/recurring 갱신. → R4 3축 표 출력.

**에러 흐름 — R3 역추적 confidence:low → 출처 확인 선행 / scope-escalation**
- Phase 0~1: R3 판별, repo-wide.
- Phase 2: trace-capturer 3단 폴백 → ③ 구조·문체+git blame로만 매칭, confidence:low.
- Phase 3: 진단이 표적을 agent(.md)로 지목 → scope_status:scope-escalation.
- Phase 6: confidence:low → **출처 확인 질문 선행**. 사용자가 출처 확정하지 못하면 deferred. agent 표적은 plugin 모드 재실행 권고로 노출.
- Phase 7: accepted 없음 → 적용 0건. Phase 8: 결정 ledger에 deferred/scope-escalation 기록. → R4 표에 "적용: -" 명시.

## 참고 자료

- [references/execution-types.md](./references/execution-types.md) — 실행 유형 판별(초기/신규/부분/새)
- [references/scope-and-targets.md](./references/scope-and-targets.md) — 스코프·표적 kind·패치 경계
- [references/experience-store-schema.md](./references/experience-store-schema.md) — store 디렉토리·파일 스키마
- [references/pareto-axes.md](./references/pareto-axes.md) — 4축 정의·비후퇴 규칙
- [session-signal-capture](../session-signal-capture/SKILL.md) — R1/R3 신호 캡처 방법론
- [causal-diagnosis](../causal-diagnosis/SKILL.md) — full-trace causal 진단 루브릭
- [pareto-refinement](../pareto-refinement/SKILL.md) — Pareto/additive patch 생성 방법론
