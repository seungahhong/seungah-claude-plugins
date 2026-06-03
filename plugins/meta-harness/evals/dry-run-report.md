# meta-harness 드라이런 리포트 (독립 인수 검증 — 채점 완료)

본 리포트는 빌드에 참여하지 않은 **독립 인수 검증관**이 `plugins/meta-harness/`(18파일)를 회의적으로 채점한 결과다. 런타임 실행이 아니라 **설계 적합성(design-conformance) dry-run** — shipped SKILL.md/agents/references가 각 인수 동작을 강제·명세하는지를 file:line/섹션 인용으로 판정한다.

> 제1원칙: full-trace 보존이 압축 요약보다 우월(arXiv 2603.28052v1, Table 3: full 56.7 vs summary 38.7). 어느 Phase에서도 traces/가 요약으로 퇴화하지 않는지를 우선 확인했다 — 본문 다층(SKILL.md L43, trace-capturer L17-22, session-signal-capture L12-14, experience-store-schema L5-13, experience-historian L14)에서 일관되게 강제됨을 확인.

채점 기준 파일: `skills/meta-harness/SKILL.md`(226줄), 4 agents, 3 보조 skills, 4 references, `evals/evals.json`(12 assertion), `evals/trigger-eval.json`(20 쿼리).

---

## 1. Phase 0~8 + R4 시퀀스 논리 dry-run (입력→출력 매칭 · dead link)

| Phase | 기대 입력 | 기대 산출 | 본문 매핑(파일·줄) | 입출력 매칭 | dead link |
| ----- | -------- | -------- | ------------------- | ---------- | --------- |
| 0 컨텍스트 확인 | experience-store/·_workspace/ 유무 | 실행유형(초기/신규/부분/새) 1줄 보고 | SKILL.md L60-69 + references/execution-types.md 판별표 L7-12 | OK — 4유형 분기·보고형식 정의 | OK (execution-types.md 존재) |
| 1 트리거·스코프 확정 | 사용자 발화 / 외부 .md | R1·R2·R3 + repo-wide/plugin + warm-start | SKILL.md L71-75 + scope-and-targets.md L3 | OK — '한 번에 한 질문' 2회 명시 | OK |
| 2 신호 캡처 | redirect 원문·직전 산출물·active SKILL / .md 전문 | traces/*.jsonl 원형 + (R3)3단 폴백+confidence | SKILL.md L77-95 + trace-capturer.md + session-signal-capture.md | OK — Agent 프롬프트가 산출 경로·금지(요약) 명시 | OK (session-signal-capture/SKILL.md 존재) |
| 3 진단(병렬 ≤4~6) | raw trace(grep/cat 직접) | diagnosis: kind·scope_status·severity·confidence·evidence(step/경로) | SKILL.md L97-117 + failure-diagnostician.md + causal-diagnosis.md | OK — 한 메시지 동시 spawn·배치≤6 명시 | OK (causal-diagnosis/SKILL.md 존재) |
| 4 개선(순차) | diagnosis + 직전 patch 노출 | patch.md(diff+3줄)+Pareto 좌표+(desc)trigger_eval | SKILL.md L119-139 + pareto-refiner.md + pareto-refinement.md | OK — 순차·직전결과 노출·patch만 | OK (pareto-refinement/SKILL.md 존재) |
| 5 lightweight validation | 후보 patch | frontmatter/상호참조/트리거충돌/Why-없는 MUST 점검 → interface-invalid 탈락 | SKILL.md L141-143 + experience-store-schema.md L131-149 | OK — Phase 6·7(비싼 단계) 앞에 위치 | OK |
| 6 사용자 승인 게이트 | 검증 통과 후보 + why | accepted/rejected/deferred + (low/R3)출처확인 + escalation·반복(≥3) 경고 | SKILL.md L145-147 | OK — why-first·부분결정 허용·경고 노출 | OK (decisions.json 경로 일관) |
| 7 적용(accepted만) | accepted patch | 스코프 재확인 후 Edit/Write(묶음 적용)+patch 사본 | SKILL.md L149-151 + scope-and-targets.md L34-43 | OK — 이중 게이트(진단1차+적용직전2차) | OK (patches/ 경로 일관) |
| 8 experience 갱신 | 회차 결과 | history.jsonl+index.json+pareto.json+recurring-patterns.md | SKILL.md L153-167 + experience-historian.md + experience-store-schema.md | OK — append-only·요약 navigation 한정 | OK |
| R4 최종 보고 | 회차 전체 | '무엇/왜/어디' 3축 표 | SKILL.md L169-175 | OK — 표 헤더·예시행·필수 명시 | OK |

**Phase 연결 정합성**: Phase 2 산출(traces/) → Phase 3 입력(grep/cat 직접 조회) → Phase 4 입력(diagnosis_{N}.json) → Phase 5 게이트 → Phase 6 결정 → Phase 7 적용 → Phase 8 ledger. 데이터 전달 매트릭스(SKILL.md L179-187)가 휘발(_workspace)/영속(store)/반환을 분리해 누수 없음. `_workspace_prev/` 1세대 이동 규칙(execution-types.md L20-25)으로 회차 격리.

**dead link 점검 결과 (전부 OK):**

- [x] `references/execution-types.md` — 존재
- [x] `references/scope-and-targets.md` — 존재
- [x] `references/experience-store-schema.md` — 존재
- [x] `references/pareto-axes.md` — 존재
- [x] `agents/trace-capturer.md` / `failure-diagnostician.md` / `pareto-refiner.md` / `experience-historian.md` — 4개 존재
- [x] `skills/session-signal-capture/SKILL.md` / `causal-diagnosis/SKILL.md` / `pareto-refinement/SKILL.md` — 3개 존재
- [x] sibling 상대참조(`../session-signal-capture/SKILL.md` 등 SKILL.md L224-226) — 실파일 해석
- [x] `agents/failure-diagnostician.md` L14 `../skills/causal-diagnosis/SKILL.md` — agents/ 기준 상대해석 시 plugin-root/skills/... 로 정확히 해석됨
- [x] experience-store 경로 규약(`.claude/experience-store/` repo-wide / `plugins/{target}/experience-store/` plugin) — SKILL.md·4 agents·schema 전부 일치
- **dead link: 0건**

---

## 2. Acceptance assertion 채점 (12항목)

| # | Assertion id | verdict | 핵심 evidence(파일·줄) |
| - | ------------ | ------- | --------------------- |
| 1 | [R1/asset-target-declared] | **PASS** | SKILL.md L71-75 '한 번에 한 질문' ×2 + 평가스코프 표 L34-37 + scope-and-targets.md L9-10 패치허용표적 |
| 2 | [R2/full-trace-preserved] | **PASS** | SKILL.md L79,L43 + trace-capturer.md L17-22,L64 + session-signal-capture.md L12-14,L90 + schema L19 |
| 3 | [R2/prior-candidates-navigable] | **PASS** | schema L68-101 index.json(trace_glob/score_path)+L5-13 불변식 + experience-historian.md L14,L33,L52 |
| 4 | [R3/no-auto-apply] | **PASS** | SKILL.md L121,L44,L149 + pareto-refiner.md L12-13,L23 + pareto-refinement.md L14 'eval은 proposer 밖' |
| 5 | [R3/additive-first-on-regression] | **PASS** | pareto-refinement.md L29-47(3단계) + pareto-refiner.md L32-35 + SKILL.md L121,L132,L46 |
| 6 | [R3/single-defect-single-patch] | **PASS** | SKILL.md L45 + failure-diagnostician.md L10 + pareto-refiner.md L11 + trace-capturer.md L40 |
| 7 | [R4/proposer-owns-diagnosis] | **PASS** | SKILL.md L30,L49 + causal-diagnosis.md L12,L48,L126 + failure-diagnostician.md L14 + pareto-refiner.md L16 |
| 8 | [R4/lightweight-validation-precedes-eval] | **PASS** | SKILL.md L141-143(Phase5가 6·7 앞) + schema L131-149 verdict interface-valid/invalid |
| 9 | [Meta-Harness/pareto-not-regressed] | **PASS** | pareto-axes.md L11-16,L47-73(reject 예시) + pareto-refiner.md L37-42 + pareto-refinement.md L49-60 |
| 10 | [레포정합성/scope-and-trigger-eval-bundled] | **PASS** | scope-and-targets.md L16-20 + SKILL.md L39 + pareto-refinement.md L62-64 + pareto-refiner.md L46 |
| 11 | [R3R4-보고] | **PASS** | SKILL.md L169-175 3축 표 헤더+예시 + 테스트시나리오 L209,L216 |
| 12 | [R3/gate-decision] | **PASS** | SKILL.md L145-147 + 테스트시나리오 L215 + failure-diagnostician.md L67-68 + session-signal-capture.md L50,L100 |

**집계: 12/12 PASS.** (상세 evidence는 `evals/evals.json` 각 assertion의 `evidence` 필드에 file:line으로 인용.)

---

## 3. 트리거 채점 (`evals/trigger-eval.json` 20쿼리 vs description 경계)

description의 '반드시 발동한다' 절(SKILL.md L5-11)과 '발동하지 않는다' 절(L12-14)을 각 쿼리와 대조했다. 두 절이 20쿼리를 **거의 verbatim** 포섭한다.

### should-trigger (기대 true, 10건) — 전부 정분류

| # | query 요약 | description 포섭 절 | 결과 |
| - | --------- | ------------------ | ---- |
| 1 | 방향 되돌리기+세션 보고+쓰던 스킬 수정 | R1 '방금 그 방향 말고 다시 해줘...지금 쓰던 스킬 고도화' | PASS |
| 2 | 보강+왜 부족 진단+CLAUDE.md·스킬 | R1 '이거 보강해줘, 왜 부족했는지 루트 CLAUDE.md/스킬 고도화' | PASS |
| 3 | 실수 반복 방지+쓰던 스킬 본문 고도화 | R1 '이 실수 반복 안 하게 지금 스킬 고쳐' | PASS |
| 4 | 세션 동작 보고+루트 CLAUDE.md 업데이트 | R1 '지금 세션 동작 보고 루트 지침 업데이트해줘' | PASS |
| 5 | 외부 .md 부실+만든 에이전트/skill 역추적 수정 | R3 '이 _docs/xxx.md 부실한데 만든 에이전트/skill 고쳐' | PASS |
| 6 | 산출물 만든 skill 역추적 고도화 | R3 '이 산출물 만든 skill 고도화' | PASS |
| 7 | plugin 오작동+plugin.json 포함 수정 | R2 '이 플러그인 자체가 잘못 가고 있어 plugin.json까지 고쳐' | PASS |
| 8 | 이전 후보 trace 깔고 grep해 다음 후보 | '이전 후보들 source/score/trace 파일로 깔아두고 grep해서 다음 후보 제안' | PASS |
| 9 | 정합↑·본문비용 유지 Pareto 후보 | '정합 올리되 본문비용 안 늘리게 Pareto 유지하며 후보 뽑아' | PASS |
| 10 | 동작 원인 진단+하네스 고도화 | '왜 이렇게 동작했는지 진단하고 하네스 고도화' | PASS |

### should-not-trigger (기대 false, 10건) — 전부 정분류

| # | query 요약 | description 비발동 절 | 결과 |
| - | --------- | -------------------- | ---- |
| 1 | 새 하네스/에이전트 팀 신규 생성 | '새 하네스/에이전트 팀을 처음부터 만들기' | PASS |
| 2 | 스킬 단발 신규 작성·벤치마크 | '스킬 하나 새로 작성·벤치마크' | PASS |
| 3 | PR 앱 코드 리뷰/버그 찾기 | 'PR/앱 코드 리뷰·버그 찾기' | PASS |
| 4 | 기술 문서 신규 생성 | '기술 문서 새로 생성' | PASS |
| 5 | settings.json 설정 변경 | 'settings.json 설정 변경' | PASS |
| 6 | 분기 OKR 목표 평가 | 'OKR/비-하네스 자산 평가' | PASS |
| 7 | trajectory 시간순 표 정규화만 | 'trajectory를 시간순 표로 정규화만' | PASS |
| 8 | 함수 리팩터링 | '함수 리팩터링' | PASS |
| 9 | 깨진 테스트 수정(앱 코드) | '깨진 테스트 수정' | PASS |
| 10 | 커밋 메시지 작성 | '커밋 메시지 작성' | PASS |

**집계: should-trigger 10/10, should-not-trigger 10/10. 오분류 0건.**

**경계 주의 케이스(검증함)**: ST#5 'R3 외부 .md 역추적해 만든 주체 고도화' vs SNT#4 '기술 문서 신규 생성' — 전자는 *역추적→산출 주체(agent/skill) 고도화*, 후자는 *문서 자체 신규 생성*. description이 R3를 '만든 에이전트/skill 고쳐'로 한정해 두 의도를 분리하므로 충돌 위험 없음. SNT#7 '정규화만'은 trace-capturer 캡처와 어휘가 겹치나, description이 '정규화만'을 명시적 비발동으로 못박아 오발동 차단.

---

## 4. 구조 점검 (a~e)

| 항목 | 점검 | 결과 |
| ---- | ---- | ---- |
| (a) SKILL.md frontmatter = name/description만 | 4개 SKILL.md 전수 awk 파싱 | **PASS** — 4개 모두 name/description 2키만 (meta-harness description은 `>-` 블록 스칼라, 키는 동일) |
| (b) SKILL.md 본문 < 500줄 | wc -l | **PASS** — meta-harness 226 / causal-diagnosis 127 / pareto-refinement 140 / session-signal-capture 100 |
| (c) 오케스트레이터 Agent 호출에 model:"opus" | grep Agent( vs model="opus" | **PASS** — 6개 Agent() 호출(L82,103,115,116,125,156) 전부 model="opus" 동반. 추가로 실행모드 L28에 전역 규약 명시 |
| (d) references/·보조 스킬 상호참조 = 실파일(dead link 없음) | 경로 해석 | **PASS** — references 4 + sibling skill 3 + agent 상대참조 전부 해석. dead link 0 |
| (e) commands/·hooks/ 미생성 | ls | **PASS** — 둘 다 No such file. 총 18파일 (plugin.json, CLAUDE.md, README.md, 4 agents, 4 meta-harness 본체[SKILL+4 ref], 3 보조 skills, 3 evals) |

agents/*.md frontmatter도 name/description 2키만(인수 항목 밖이나 확인함). meta-harness는 `.claude-plugin/marketplace.json` L117-127에 정식 등록됨.

---

## 5. 최종 verdict

**PASS** — 12/12 assertion 충족(설계가 각 동작을 강제·명세, file:line 인용 가능), 트리거 should/should-not 20/20 정분류(오분류 0), Phase 0~8+R4 입출력 매칭·dead link 0, 구조 점검 a~e 전부 통과. 빌드에 비참여한 독립 검증관 기준으로 인수 기준을 만족한다.
