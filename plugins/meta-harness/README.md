# meta-harness

## 무엇인가

`meta-harness`는 하네스(루트 CLAUDE.md + 각 SKILL.md + agents/*.md + commands/*.md + hooks, 즉 "LLM 주위의 코드")를 스스로 개선하는 메타 하네스 엔지니어링 플러그인이다. 압축 요약이 아니라 **full-trace experience store**를 grep/cat로 직접 조회해 결함의 root cause를 causal reasoning(confound 격리 → 단독검증 → 위험평가)으로 진단하고, behavior-alignment·rule-body-cost·trigger-precision·generalization 4축 Pareto frontier를 후퇴시키지 않는 패치를 **사용자 승인 게이트** 하에서만 제안·적용한다.

## 언제 쓰나

- **R1 (현 세션)**: 사용자가 다른 방향 개발을 요청하거나 산출물 보강을 원할 때 → 왜 문제였는지 현 세션 신호로 검토 → 루트 CLAUDE.md 업데이트 + 사용 중이던 SKILL.md 고도화.
- **R2 (plugin 심층)**: AI 동작이 잘못된 방향으로 갔을 때 → plugin 자체(plugin.json·agents·commands·hooks·SKILL.md)까지 고도화.
- **R3 (외부 .md 역추적)**: 에이전트가 만든 .md 산출물에 수정이 필요할 때 → 그 .md를 읽고 → 산출 주체(에이전트/skill)를 3단 폴백으로 식별 → 정의(agents/{name}.md)와 SKILL.md를 고도화.

## 어떻게 동작하나

- **Phase 0 — 컨텍스트 확인**: experience-store/ 와 .claude/_workspace/ 검사로 실행유형(초기/신규회차/부분재실행/새실행) 자동 판별 후 1줄 보고.
- **Phase 1 — 트리거·스코프 확정**: R1/R2/R3 판별 + repo-wide(기본)/plugin(opt-in) 스코프 확정 + recurring-patterns.md의 needs_attention warm-start 조회.
- **Phase 2 — 신호 캡처**: trace-capturer 1회. R1=redirect 발화 원문 + 직전 산출물 + active SKILL, R3=.md 전문 + 3단 폴백 출처 역추적. raw trace를 원형 적재(요약 금지).
- **Phase 3 — 진단**: failure-diagnostician 결함별 **병렬** 팬아웃(배치 ≤4~6). experience-store를 grep/cat 직접 조회, confound 먼저 의심, why-first(증거는 step 번호/파일 경로 인용).
- **Phase 4 — 개선**: pareto-refiner 진단별 **순차**. additive-first → compose(직교 승리만) → transfer. patch만 생성(자동 적용 금지).
- **Phase 5 — lightweight validation**: frontmatter 파싱, 상호참조 경로 존재, 트리거 충돌, Why-없는 MUST/NEVER 정적 점검으로 interface-invalid 후보 탈락.
- **Phase 6 — 사용자 승인 게이트(필수)**: 결함별 accepted/rejected/deferred 수집(일부만 결정해도 진행). why 먼저 제시, confidence:low면 출처 확인 선행, scope-escalation/반복패턴(≥3) 경고 노출.
- **Phase 7 — 적용**: accepted만, 스코프 경계 재확인 후 Edit/Write. 동일 파일 다중 patch는 묶어 적용.
- **Phase 8 — experience-historian**: history.jsonl + index.json + pareto.json + recurring-patterns.md 갱신.
- **R4 최종 보고(필수)**: '무엇 / 왜 / 어디' 3축 표(트리거R · 표적 · 변경종류 · 왜문제였나+근거 · 결정 a/r/d · 적용✓).

## 산출물

- **experience-store**: `.claude/experience-store/`(repo-wide) 또는 `.claude/plugin-store/{target}/`(plugin) — history.jsonl(append-only ledger), index.json(navigable 포인터), pareto.json(frontier 좌표), recurring-patterns.md(표적별 카운트), patches/(적용 patch 사본), {run}/{candidate}/traces/*.jsonl(원본 raw trace).
- **patch**: unified-diff(위아래 3줄) + Pareto 좌표 + (description 수정 시) should-trigger/should-not 8~10개씩.
- **보고**: R4 3축 표.

## 트리거 예시

- "방금 그 방향 말고 다시 해줘 — 왜 그랬는지 보고 지금 쓰던 스킬이랑 CLAUDE.md 고쳐."
- "이 `_docs/spec.md` 부실한데, 이거 만든 에이전트/skill을 고도화해줘."
- "이 플러그인이 자꾸 엉뚱하게 가 — plugin.json까지 들어가서 고쳐줘."
- "정합 올리되 본문비용 안 늘리게 Pareto 유지하면서 다음 후보 뽑아."

## 실제 사용 예 (Walkthrough)

별도 명령어가 아니라 **자연어 트리거**로 발동한다(스킬 description이 트리거를 잡는다). 아래는 트리거 → 동작 → 산출물의 실제 흐름이다.

### 예 1 — R1: 현 세션에서 "이 실수 반복 안 하게 하네스 고쳐"

**입력 (사용자):**
> "방금 빌드에서 생성 파일들이 플러그인 폴더가 아니라 레포 루트에 떨어졌어. 왜 그랬는지 보고, 이 실수 반복 안 하게 하네스를 고쳐줘."

**플러그인 동작:**
1. **Phase 1** — 트리거 `R1` / 스코프 `repo-wide` 확정.
2. **Phase 2** — `trace-capturer`가 redirect 발화 원문 + 직전 빌드 산출물 + active skill을 **원형 trace**(`.claude/experience-store/{run}/cand-0000/traces/*.jsonl`)로 적재(요약 금지).
3. **Phase 3** — `failure-diagnostician`가 raw trace를 `grep`/`cat`로 조회 → root cause를 "하네스 생성 방법론에 '생성·참조 경로를 플러그인 루트 기준 절대경로로 못 박는' 규칙이 부재"로 진단(증거는 trace step 직접 인용). 두 증상이 한 원인임을 **confound 격리**로 확인.
4. **Phase 4** — `pareto-refiner`가 기존 본문을 덜어내지 않고 규칙 + Why만 더하는 **additive patch**를 `patch.md`로 생성. **표적 파일은 건드리지 않는다.**
5. **Phase 6** — 게이트에서 patch를 보여주고 결함별 `accepted`/`rejected`/`deferred`를 물음. **승인 전까지 어떤 파일도 바뀌지 않는다.**
6. **R4** — '무엇/왜/어디' 3축 표로 보고.

**R4 보고(발췌):**

| 트리거 | 표적 | 변경 | 왜 문제였나 (+근거) | 결정 | 적용 |
|--------|------|------|---------------------|------|------|
| R1 | `harness-generator/SKILL.md` | additive · 경로 절대화 규약 | 팬아웃 writer에 루트 누락 경로 전달 → cwd 기준 해석되어 레포 루트에 파일 생성 (trace step2~4) | 사용자 결정 | – |

> 이 예는 **실제로 실행된 회차** `run-2026-06-03-01`의 요약이다. 전체 산출물은 `.claude/experience-store/run-2026-06-03-01/`(traces·patch·score·pareto)와 `.claude/_workspace/run-2026-06-03-01/`(진단 JSON·Phase5 검증·게이트 결정·3축 보고)에서 확인할 수 있다.

#### 예 1-적용판 — 현재 프로젝트의 루트 `CLAUDE.md` + 사용 중이던 `SKILL.md`를 실제로 변경

R1의 정의 그대로의 경우다 — "왜 문제였는지 검토 → **루트 CLAUDE.md 업데이트** + **사용 중이던 skill 고도화**". `repo-wide`에서 루트 `CLAUDE.md`와 임의 `SKILL.md`는 둘 다 **패치 경계 안**이라, 게이트에서 승인하면 현재 작업 중인 프로젝트의 파일이 실제로 바뀐다.

**입력 (사용자):**
> "방금 컴포넌트 만들 때 아이콘 버튼에 접근 가능한 이름을 자꾸 빠뜨리네. 이 방향 말고 — 이 실수 반복 안 하게 루트 `CLAUDE.md`랑 지금 쓰던 a11y 스킬을 고쳐줘."

**동작:** Phase 2에서 `trace-capturer`가 redirect 발화 + 직전 생성 컴포넌트(aria-label 누락) + active skill(`a11y`)을 trace로 적재 → Phase 3 진단이 표적 **2건**을 지목: 루트 `CLAUDE.md`(프로젝트 규약 부재, kind=`claude-md`)와 `a11y/SKILL.md`(점검 규칙 부재, kind=`skill-body`) → Phase 4 **additive** patch 2건 → Phase 6 게이트에서 사용자가 `accepted` → **Phase 7 적용**.

**적용 결과 (additive — 기존 줄 삭제 없음):**

루트 `CLAUDE.md` (프로젝트 규약 1줄 추가):
```diff
+ - 인터랙티브 요소(button·a·아이콘 버튼)에는 접근 가능한 이름(aria-label 또는 연결된 label)을 항상 부여한다 — 누락 시 스크린리더가 "버튼"으로만 읽어 조작 의도를 잃는다.
```

`plugins/frontend-harness/skills/a11y/SKILL.md` (점검 항목 + Why 추가):
```diff
+ - **인터랙티브 요소 이름 점검(필수)** — button·a·input·role="button" 각각에 접근 가능한 이름이 있는지 확인한다.
+   - **Why:** 아이콘 전용 버튼은 보이는 텍스트가 없어, aria-label이 없으면 스크린리더가 역할만 읽고 무엇을 하는 버튼인지 전달하지 못한다.
```

**R4 보고(발췌):**

| 트리거 | 표적 (kind · path) | 변경 | 왜 문제였나 (+근거) | 결정 | 적용 |
|--------|--------------------|------|---------------------|------|------|
| R1 | claude-md · 루트 `CLAUDE.md` | additive · 프로젝트 규약 1줄 | 생성 컴포넌트가 aria-label 반복 누락, 프로젝트 차원 규약 부재 (trace step2) | accepted | ✓ |
| R1 | skill-body · `a11y/SKILL.md` | additive · 점검 항목+Why | a11y 스킬에 인터랙티브 요소 이름을 강제하는 점검 규칙 부재 (trace step3) | accepted | ✓ |

> 적용 후: 두 patch 사본이 `.claude/experience-store/patches/`에 보관되고, `history.jsonl`에 `applied=2`로 기록된다. 다음에 같은 컴포넌트 작업을 하면 갱신된 규약·스킬이 트리거된다. **승인하지 않으면(또는 `deferred`) 두 파일 모두 변경되지 않는다.**

#### 예 1-자동탐색 — 파일을 지정하지 않아도 관련 파일을 **알아서** 찾는다

위 적용판은 사용자가 "루트 `CLAUDE.md`랑 a11y 스킬"을 **거명**한 경우다. 그러나 거명하지 않아도 된다 — **현 세션의 AI 실수만으로 plugin이 고칠 파일을 자율 탐색**한다(사용자가 `CLAUDE.md`/`SKILL.md`를 짚어주지 않아도 됨).

**입력 (파일 미지정):**
> "또 아이콘 버튼에 접근 가능한 이름을 안 넣었네. 이 실수 반복 안 하게 고쳐줘." *(어떤 파일을 고치라고는 말하지 않음)*

**plugin이 표적을 찾는 방법:**
1. **Phase 2** — `trace-capturer`가 직전 AI 산출물(aria-label 누락 컴포넌트)과 redirect 발화를 원형 trace로 적재하고, 직전 산출이 따른 절차로 **active skill을 추론**한다.
2. **Phase 3** — `failure-diagnostician`가 표적을 외부에서 받지 않고 **레포를 직접 스캔**한다: `plugins/*/skills/*/SKILL.md` 전체를 결함 키워드(`aria-label`·`접근 가능한 이름`·`아이콘 버튼`)로 grep → 후보를 정독·대조해 표적을 확정한다.
3. **판정** — 표적 = `frontend-harness/skills/a11y/SKILL.md`(skill-body, in-boundary). **배제**: 루트 `CLAUDE.md`(a11y를 구조로만 언급 — 잘못된 altitude), `semantic-html/SKILL.md`(요소 선택만 관할 — confound 격리).
4. 이후 Phase 4~7은 위 적용판과 동일(게이트 → 승인 시 적용). **confidence가 낮을 때만** 게이트 전에 "이 파일이 맞나요?" 출처 확인이 선행된다.

> **검증됨:** 이 자동 탐색은 실제로 실행해 확인했다(회차 `verify-autodiscover-01`). 사용자가 파일을 한 개도 지정하지 않은 입력에서, 진단가가 **27개 `SKILL.md`를 스캔해 `a11y/SKILL.md`를 자율 표적으로 확정**하고 무관한 후보(`CLAUDE.md`·`semantic-html`)를 근거와 함께 배제했으며, root cause를 '규칙 부재'가 아니라 '생성 시점 **enforcement 부재**'로 구분했다 — `.claude/_workspace/verify-autodiscover-01/diagnosis.json` 참조.

### 예 2 — R3: 외부 .md 산출물의 생산 주체 고도화

**입력:**
> "이 `_docs/feature-x-spec.md` 가 변경사항 섹션이 비어 있어. 이거 만든 에이전트랑 skill을 고쳐줘."

**동작:** `trace-capturer`가 .md 전문을 적재하고 **3단 폴백**(① 산출 경로 규약 매칭 → ② 파일 내 `generated-by` 메타마커 → ③ 구조·문체 + `git blame`)으로 산출 주체를 역추적해 confidence를 매긴다 → 진단이 표적을 산출 에이전트(`agents/*.md`)와 해당 SKILL로 지목 → patch 제안 → 게이트.
> `repo-wide`에서 `agents/*.md`는 패치 경계 밖이라 **scope-escalation**(단일 플러그인 평가 모드 재실행 권고)으로 안내된다. confidence가 낮으면 게이트 전에 **출처 확인 질문**이 선행된다.

### 예 3 — R2: 플러그인 자체 심층 개선

**입력:**
> "frontend-harness 플러그인이 자꾸 엉뚱한 스킬을 트리거해. 플러그인 전체(plugin.json·agents 포함) 들어가서 고쳐줘."

**동작:** Phase 1에서 스코프를 `plugin: frontend-harness`로 확정 → 그 플러그인의 **모든 파일이 패치 경계 안** → 진단·patch가 `agents/`·`plugin.json`까지 표적 가능 → 게이트 → 적용 시 회차가 `.claude/plugin-store/frontend-harness/`에 누적된다.

### 적용까지 가려면 (Phase 7)

게이트에서 `"1번 적용해줘"` 또는 `"전부 accepted"`처럼 답하면, 스코프 경계를 재확인한 뒤 patch를 적용하고 `experience-store/patches/`에 사본을 남긴다. 반려는 `"2번은 reject — 의도된 동작이야"`처럼 결함별로 답하면 되고, 미정은 `deferred`로 다음 회차에 넘어간다. **이 플러그인은 절대 먼저 적용하지 않는다.**

### 후속 회차

같은 표적이 반복되면 `recurring-patterns.md` 카운트가 오르고, **3회 누적 시** 본문 패치 대신 "구조 재설계"를 권고한다. "지난 회차 이어서", "또 같은 문제"처럼 말하면 이전 `experience-store/`를 warm-start로 읽어 이어간다.

## 구성 요약

| 구분 | 이름 | 역할 |
|------|------|------|
| Agent | trace-capturer | 현세션 신호 + 외부 .md를 원형 trace로 정규화, R3 3단 폴백 역추적 |
| Agent | failure-diagnostician | 결함 1건당 root cause 진단(병렬), confound-first, why-first |
| Agent | pareto-refiner | 진단별 순차 patch 생성(proposer), additive-first → compose → transfer |
| Agent | experience-historian | experience-store 큐레이션(history/index/pareto/recurring) |
| Skill | meta-harness | 진입 오케스트레이터(Phase 0~8 + R4) |
| Skill | session-signal-capture | R1/R3 신호 캡처 방법론(원본 보존) |
| Skill | causal-diagnosis | full-trace 기반 causal 진단 루브릭 |
| Skill | pareto-refinement | Pareto/additive patch 생성 방법론 |

## claude 특화된 기능 (연구 근거 기반)

아래는 meta-harness에 더할 **claude 특화된 기능·원칙**으로, "개인 의견"이 아니라 인용된 1차 출처(Anthropic 엔지니어링 문서 / peer-reviewed 논문)에 근거해 도입한다. 모두 기존 안전선(사용자 승인 게이트 · Pareto 비후퇴 · full-trace 보존)을 거쳐 **phase 단위**로 적용한다. 이 원칙들은 SKILL.md의 `연구 근거 원칙` 섹션과 진단·개선 스킬(causal-diagnosis · pareto-refinement · experience-historian)에 **operative하게 반영**돼 있다. 각 항목의 1차 출처는 아래에 인라인 표기한다.

**claude 특화된 기능 2종**

- **F1. 단계별 동적 워크플로우 병렬화 (조건부)** — 단계 진행 중 **독립적으로 병렬 가능한 항목**은 orchestrator-workers 동적 워크플로우로 fan-out한다(Phase 3 진단이 canonical 대상; Phase 4는 의존성 때문에 순차 유지). 병렬은 **기본값이 아니라** 독립성·작업가치 게이트(멀티에이전트는 토큰 비용이 큼 — 벤더 self-report 기준 약 15×, 비공개 internal eval)를 통과할 때만. 근거: *Building effective agents*, *multi-agent research system*.
- **F2. 생성 산출물 `.claude/` 외부 메모리 통합** — 진행 중 생성되는 문서/파일(휘발 `.claude/_workspace/`·plugin store·리서치/보고)을 작업 디렉토리 외부 메모리 `.claude/` 하위로 통합 적재한다(스코프별 기억 격리 불변식 보존). 근거: *Effective context engineering*(file-based memory), *Agent Skills*. ※ '`.claude`' 경로는 출처에 verbatim 없는 합리적 확장.

**개선 원칙 5종** (모두 기존 Pareto 4축·게이트로 매핑)

- **P1** 모델 향상으로 제품 기본기능과 **중복된 규칙**을 탐지 → 개선/삭제(= `rule-body-cost`↓ & `behavior-alignment` 유지인 Pareto 승리). 근거: context engineering '최소·고신호 / Claude는 이미 똑똑하다'(간접 도출).
- **P2** **안전장치는 함부로 삭제하지 않는다** — 자기개선의 효능 한계(Reflexion 수렴 보장 부재, GEPA prompt bloat)가 가드레일 유지의 근거. 근거: arXiv 2303.11366 / 2507.19457.
- **P3** 작은 작업을 느리게 하는 규칙 → **조건부 규칙**(progressive disclosure / 경량 경로). 근거: Agent Skills 'Pattern 3: Conditional details', just-in-time.
- **P4** **반복 절차는 Skill로** — 'CLAUDE.md 섹션이 사실이 아니라 절차로 커지면 스킬화'. `recurring-patterns.md`(≥3)로 반복 근거 확인 후 추출. 근거: Agent Skills best practices.
- **P5** 전역 지침은 **최소·고신호**(안정적 사실·원칙만; 절차는 Skill로 — *minimal ≠ short*). 근거: context engineering 'optimal set of tokens / right altitude'.

---

[^1]: 근거 논문 — "Meta-Harness: End-to-End Optimization of Model Harnesses", arXiv 2603.28052v1. claude 특화된 기능·원칙은 SKILL.md `연구 근거 원칙` 섹션 및 진단·개선 스킬에 operative하게 반영되며, 1차 출처는 각 항목에 인라인 표기한다.
