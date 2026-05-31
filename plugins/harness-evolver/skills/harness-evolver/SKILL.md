---
name: harness-evolver
description: 사용자가 사용 중인 임의의 하네스 스킬에서 오동작/반복 실수/트리거 누락 등 문제가 보고되면, 대상 하네스의 실행 궤적(trajectory)을 캡처·진단해 결함의 근본 원인을 식별하고 skill-creator 방식의 eval-driven iteration으로 자율 진화시키는 메타 오케스트레이터. 기본 평가 스코프는 현재 적용 중인 프로젝트(이 레포) 전역 — 루트 CLAUDE.md와 모든 플러그인의 스킬(SKILL.md)을 대상으로 진단하며 패치는 CLAUDE.md/SKILL.md로 한정한다. 단일 플러그인 전체(plugin.json·agents·hooks·commands 포함) 심층 평가는 사용자가 "OO 플러그인 평가/점검"처럼 명시 요청할 때만 수행하고, 스코프는 매 회차 Phase 1에서 확정한다. 사용자가 "하네스 고도화", "하네스 평가", "전체 점검", "레포 평가", "플러그인 평가", "플러그인 점검", "오케스트레이터 개선", "이 스킬이 안 먹는다", "트리거 누락", "스킬 자동 개선", "harness evolve", "재실행해도 같은 실수", "왜 이 스킬이 트리거 안 되지", "이 하네스 진화시켜줘", "이전 실행 결과를 바탕으로 개선" 등을 말할 때 반드시 이 스킬을 사용한다. 신규 하네스 구축은 harness-generator, 단발성 스킬 작성은 skill-creator를 쓰고, 이 스킬은 "이미 사용 중인 하네스의 문제 개선" 영역만 담당한다. 부분 재실행/추가 개선 요청에도 사용한다.
---

# Harness Evolver — 하네스 자체를 진화시키는 메타 오케스트레이터

기존 하네스의 결함을 **수정 1건 = 진단 1건 = 패치 1건** 단위로 분리해 처리하고, 누적 패턴을 영속 메모리에 큐레이션한다. Evolver 루프(`trajectory → curated memory → autonomous refinement`)와 skill-creator의 eval-driven iteration을 결합한다.

## 왜 진화가 필요한가

`harness-generator` 가 만든 하네스는 처음에는 잘 동작하지만 시간이 지나면 다음 패턴이 누적된다.

1. **트리거 누락** — description이 실제 사용자 표현을 못 잡는다.
2. **반복 우회책** — 사용자가 매번 같은 수동 보정을 한다.
3. **데이터 흐름 불일치** — Phase A 출력과 Phase B 입력 스키마가 어긋난다.
4. **에이전트 역할 모호** — 동일 에이전트가 반복 실패한다.
5. **MUST/NEVER 과다 결박** — Why가 빠진 규칙이 LLM의 엣지 케이스 판단을 망친다.

이런 결함은 좁은 패치로 가리면 다음 회차에 다른 곳에서 또 터진다. **결함을 일반화된 원리로 재해석해 본문에 박는 것** 이 진화의 핵심이며, 그 책임을 명시적 단계로 분리한 것이 이 하네스다.

## 실행 모드

**서브에이전트 + 하이브리드** — Phase 2 진단은 **결함별 병렬 팬아웃**, Phase 3 개선은 **진단별 순차** (다른 진단의 결정이 같은 파일의 patch에 영향을 주기 때문). 모든 Agent 호출에 `model: "opus"` 명시.

**패턴:** 캡처 → 팬아웃 진단 → 순차 개선 → 사용자 게이트 → 적용 → 메모리 큐레이션.

## 평가 스코프 (Evaluation Scope)

이 하네스가 도는 **현재 적용 중인 프로젝트 = 이 레포(저장소 루트)** 다. 매 회차 Phase 1에서 스코프를 1회 확정한다.

| 스코프 | 기본 여부 | 진단 대상 | 패치 허용 표적 (엄격) |
| ----- | -------- | -------- | ------------------ |
| `repo-wide` (전체 레포) | **기본** | 루트 `CLAUDE.md` + 모든 플러그인의 `skills/*/SKILL.md` | **루트 `CLAUDE.md` 와 임의 플러그인의 `SKILL.md` 만** |
| `plugin` (단일 플러그인) | opt-in (명시 선택 시) | 지목한 플러그인 **하나의 모든 파일** | 그 플러그인의 모든 파일 (`plugin.json`·`agents/`·`hooks/`·`commands/`·`skills/`·플러그인별 `CLAUDE.md`·`README` 포함) |

**왜 스코프를 가르나:** 패치는 파일을 직접 바꾼다. 사용자가 "평가해줘"라고만 했을 때 패키징·에이전트·훅·커맨드까지 손대면 의도하지 않은 광범위 변경이 된다. 그래서 기본은 **프로젝트 지침(루트 CLAUDE.md)과 스킬 본문(SKILL.md)** 으로 패치 표적을 좁히고, 그 너머(`agents/`·`hooks/`·`commands/`·`plugin.json`·플러그인별 `CLAUDE.md`)는 **사용자가 단일 플러그인 평가를 명시 요청할 때만** 연다.

**경계 밖 표적 처리 (repo-wide 한정):** repo-wide 모드에서 진단이 패치 경계 밖 표적(`agents/*.md`·`commands/*.md`·`hooks/*`·`plugin.json`·플러그인별 `CLAUDE.md`)을 짚으면 — 진단은 그대로 보고하되 **패치하지 않고** `change_kind: "scope-escalation"` 으로 "이 결함은 단일 플러그인 평가 모드에서만 고칠 수 있습니다"를 Phase 4 게이트에 노출한다. 사용자가 plugin 모드 재실행을 선택하면 그때 해당 표적을 패치한다.

**out-of-scope (양 스코프 모두 patch 불가):** 레포 루트 메타데이터(`.claude-plugin/marketplace.json`)는 어떤 플러그인 디렉토리에도 속하지 않아 plugin 모드 재실행으로도 못 고친다 — 결함 원인이면 진단가는 `scope_status: "out-of-scope"` 로 표시하고, `scope-escalation` 이 아니라 `change_kind: "blocked"`(사용자 직접 수정)으로 보고한다.

**모드 판정:** Phase 1에서 매 회차 "전체 레포 vs 단일 플러그인"을 1회 명시 질문한다. 사용자가 특정 플러그인/스킬을 지목했더라도 자동 전환하지 않는다 — 애매하면 항상 `repo-wide`(기본).

## 핵심 원칙

- **기본 스코프는 프로젝트 전역, 단일 플러그인은 opt-in** — 패치 경계를 기본(루트 CLAUDE.md + SKILL.md)으로 좁히고, 패키징·에이전트·훅·커맨드는 사용자가 단일 플러그인 평가를 명시할 때만 연다. "평가해줘" 한마디에 광범위 자동 변경이 일어나면 신뢰를 깬다. 스코프는 Phase 1에서 확정하고 이후 모든 에이전트 프롬프트에 주입한다.
- **결함 1건 = 진단 1건 = 패치 1건** — 묶지 않는다. 한 회차에 여러 결함이 발견되면 각자 별도 파일로 추적한다. 묶으면 어느 결정이 어느 변화에 책임이 있는지 추적 불가.
- **자동 적용 금지** — 모든 patch는 사용자 승인 후 오케스트레이터가 적용한다. 자동 적용은 신뢰를 깨고, 진화 자체를 망친다.
- **반복 패턴은 표면 수정이 아니라 구조 재설계 신호** — 같은 표적에 3회째 패치 권고가 나오면 본문 패치를 거절하고 `change_kind: "structural-redesign-required"` 로 사용자에게 보고한다.
- **description을 건드릴 땐 트리거 평가 동봉** — skill-creator의 should-trigger / should-not-trigger 8–10개씩을 함께 제시해 검증한다.
- **트리거 충돌 검증 필수** — `harness-generator`, `skill-creator` 와 트리거가 겹치지 않게 한다. 이 스킬은 "이미 있는 하네스를 개선" 영역만.

## 산출물 배치 규약

```
{evolution-memory 루트}/                # 스코프별 위치: repo-wide → .claude/ , plugin → plugins/{대상 플러그인}/
  evolution-memory/                     # 영속 메모리 (커밋 대상)
    history.jsonl                       # 회차별 결정 ledger
    recurring-patterns.md               # 표적별 카운트 + needs_attention
    patches/{date}-{target-slug}.md     # 적용된 패치 사본
    trigger-evals/{date}-{target}.json  # description 회차의 트리거 평가 큐 보존

_workspace/                              # 회차별 작업 공간 (재실행 시 _workspace_prev/ 로 이동)
  trajectories/{session}.jsonl          # raw trace (있을 때만)
  {phase}_trajectory_normalized.md
  {phase}_trajectory_facts.json
  {phase}_diagnosis_{N}.json
  {phase}_refinement_{N}.json
  {phase}_patch_{N}.md
  {phase}_trigger_eval_{N}.json         # description 수정 시
  {phase}_decisions.json                 # 사용자 승인 결과
  {phase}_summary.md                     # 최종 리포트
```

`evolution-memory/` 는 **스코프에 따라 위치가 갈린다** — `repo-wide` 면 레포 전역 이력으로 `.claude/evolution-memory/`, `plugin` 이면 그 플러그인 이력으로 `plugins/{대상 플러그인}/evolution-memory/`. 이렇게 분리해야 회차별 패턴 집계가 스코프 단위로 격리된다. `_workspace/` 는 회차마다 새로 만든다.

---

## Phase 0 — 컨텍스트 확인

`_workspace/` 와 `evolution-memory/` 를 검사해 실행 유형을 자동 판별하고 1줄 보고 후 진행한다.

- `_workspace/` 없음 + `evolution-memory/` 없음 → **초기 실행**.
- `evolution-memory/` 있음, `_workspace/` 없음 → **신규 회차** (이전 회차의 nudge를 입력으로 활용).
- `_workspace/` 있음, 같은 회차 재요청 → **부분 재실행** (실패한 진단·refinement만 재실행).
- 입력(대상 하네스/결함 묘사) 변경 → **새 실행** (`_workspace/` → `_workspace_prev/` 이동 후 재생성).

## Phase 1 — 스코프 확정 + 대상 식별 + 결함 수집

한 번에 한 질문씩 인터뷰한다. **스코프를 가장 먼저 확정**한다 — 이후 질문·진단·패치 경계가 전부 여기서 갈린다.

0. **평가 스코프** (가장 먼저, 매 회차 1회 명시 질문) — "이번 평가를 **(1) 전체 레포**(기본: 루트 CLAUDE.md + 모든 플러그인의 스킬)로 할지, **(2) 단일 플러그인**(그 플러그인의 모든 파일 심층)으로 할지" 를 묻는다. 사용자가 특정 플러그인을 지목했더라도 자동으로 plugin 모드로 넘기지 않고 명시 선택을 받는다. 애매/무응답 → `repo-wide`. plugin 선택 시 어떤 플러그인인지 확정한다(모르면 `plugins/` 를 스캔해 후보 제시).
1. **결함 묘사** — "무엇이 일어났고 무엇을 기대했는가" 식으로 결함별로 묘사받는다. 결함이 여러 개면 각자 1줄로 분리해 받는다. `repo-wide` 면 표적이 레포 어디든(루트 CLAUDE.md / 어느 플러그인의 SKILL.md) 될 수 있고, `plugin` 이면 그 플러그인 안으로 한정된다.
2. **trajectory 가용 여부** — raw trace 파일이 있으면 경로, 없으면 사용자 묘사로 대체 (이 경우 진단 신뢰도 표시 `~confidence: low` 가 따라붙음).

이 단계 결과(확정 스코프 포함)를 `_workspace/{phase}_intake.md` 에 1회 기록한다. 확정 스코프는 이후 Phase 2-2 진단·Phase 3 개선 에이전트 프롬프트에 **반드시 주입**한다.

`evolution-memory/recurring-patterns.md` 의 `needs_attention` 섹션을 읽어 같은 표적이 누적 임계치(≥3) 도달했다면 사용자에게 먼저 알리고 "본문 패치 대신 구조 재설계를 권고합니다" 라고 옵션을 제시한다. (읽을 위치는 스코프에 따라 `repo-wide` → `.claude/evolution-memory/`, `plugin` → 해당 플러그인 루트의 `evolution-memory/`.)

## Phase 2 — 궤적 정규화 + 진단 (팬아웃 병렬)

### Phase 2-1 — Trajectory 정규화 (1회)

`trajectory-analyst` 를 1회 호출해 trajectory를 정규화한다.

```
Agent(
  subagent_type="trajectory-analyst",
  model="opus",
  prompt="trajectory-capture 스킬에 따라 다음 trace를 정규화하라.
          입력: _workspace/trajectories/{session}.jsonl (또는 사용자 묘사 본문)
          phase 식별자: phase2
          산출: _workspace/phase2_trajectory_normalized.md, _workspace/phase2_trajectory_facts.json"
)
```

### Phase 2-2 — 결함별 진단 (병렬, 한 메시지 동시 spawn)

결함 N개를 받아 N명의 `failure-diagnostician` 을 **단일 메시지에서 동시에** 띄운다 (`run_in_background=true`). 결함별로 입력을 격리해 컨텍스트 간섭을 막는다.

**환경 robustness (stall 방지):** 리소스 제약 환경에서는 동시 spawn이 많을수록 개별 에이전트가 무진행으로 멈출(stall) 수 있다. 결함이 많으면 **한 배치 ≤ 4~6건**으로 나눠 띄우고 나머지는 다음 배치로 순차 처리한다. 또 각 진단가는 **합의된 경로 파일만** 읽게 하고(디렉토리/다수 파일 일괄 적재 금지) 컨텍스트를 작게 유지한다 — 무거운 일괄 read가 stall의 주원인이다. `trajectory-analyst` 가 payload를 경로/요약으로 압축해 두는 것도 같은 이유다.

```
# 결함 N건 → 단일 메시지에서 N개 동시 spawn
Agent(
  subagent_type="failure-diagnostician",
  model="opus",
  run_in_background=true,
  prompt="failure-diagnosis 스킬에 따라 결함 1건을 진단하라.
          결함 #N: {결함 N의 자연어 묘사}
          평가 스코프: {repo-wide | plugin:<plugin>} — repo-wide 면 표적이 패치 경계(루트 CLAUDE.md + SKILL.md) 밖(agents/commands/hooks/plugin.json/플러그인별 CLAUDE.md)일 때 target.scope_status='plugin-only'. 레포 루트 marketplace.json 은 어느 모드에서도 못 고치므로 'out-of-scope'. plugin 면 그 플러그인의 모든 파일이 경계 안.
          입력: _workspace/phase2_trajectory_facts.json
          참고: evolution-memory/recurring-patterns.md (반복 패턴 가중치)
          산출: _workspace/phase2_diagnosis_{N}.json"
)
```

각 결함이 끝나면 알림을 받는다. 모든 진단이 끝날 때까지 기다린 뒤 결과를 사용자에게 1회 요약 보고. `severity: unknown` / `needs_user_input: true` 가 있으면 그것만 별도 질문으로 추출.

## Phase 3 — 개선안 생성 (진단별 순차)

진단 1건당 `skill-refiner` 1회 호출. **순차로 도는 이유:** 동일 파일에 여러 진단의 patch가 겹치면 충돌 가능 → 순차 처리 + 직전 patch 결과를 다음 호출에 노출.

```
for N in diagnoses:
  Agent(
    subagent_type="skill-refiner",
    model="opus",
    prompt="eval-driven-refinement 스킬에 따라 진단 1건의 수정안을 생성하라.
            입력: _workspace/phase2_diagnosis_{N}.json
            평가 스코프: {repo-wide | plugin:<plugin>} — diagnosis의 target.scope_status='plugin-only' 면 patch를 만들지 말고 change_kind='scope-escalation' 으로 보고(단일 플러그인 평가 모드 재실행 필요 사유 포함).
            이전 패치 (있다면): _workspace/phase2_patch_{N-1}.md
            반복 패턴: evolution-memory/recurring-patterns.md
            산출: _workspace/phase2_refinement_{N}.json,
                  _workspace/phase2_patch_{N}.md,
                  (description 수정 시) _workspace/phase2_trigger_eval_{N}.json"
  )
```

`change_kind: "structural-redesign-required"`, `"blocked"`, `"scope-escalation"` 이 나오면 patch를 만들지 않고 그 사실을 보고에 포함시킨다. `scope-escalation` 은 "repo-wide 패치 경계 밖 표적 → 단일 플러그인 평가 모드 재실행 필요" 신호다.

## Phase 4 — 사용자 게이트 (필수)

모든 refinement를 1회 묶어 사용자에게 보여주고 결함별로 `accepted | rejected | deferred` 를 받는다. 답을 강제로 모두 받지 않는다 — 일부만 결정해도 진행 가능하게 한다 (deferred 는 다음 회차로 넘김).

`change_kind: "scope-escalation"` 항목은 일반 patch처럼 accept/reject 받는 대신 **"단일 플러그인 평가 모드로 재실행"** 선택지로 노출한다. 사용자가 선택하면 그 결함을 `plugin` 스코프로 재진단한다 — 이때는 사용자가 escalation을 **명시 선택**한 경우이므로 Phase 1 step 0의 스코프 질문을 생략하고, skill-refiner가 보존한 표적 경로(`plugins/{plugin}/...`)에서 대상 플러그인을 plugin 스코프로 자동 확정해 Phase 1 이후 단계로 재진입한다(plugin 식별용 `plugins/` 스캔도 생략). 이 자동 확정은 사용자 명시 선택에 따른 것이라 핵심 원칙의 "자동 전환 금지(초기 모호 요청 한정)"와 충돌하지 않는다.

결과를 `_workspace/phase2_decisions.json` 에 기록.

```json
{
  "session": "sess-YYYYMMDD-NNN",
  "decisions": [
    {"diagnosis_id": "1", "decision": "accepted", "note": ""},
    {"diagnosis_id": "2", "decision": "rejected", "note": "false positive — Phase 3 의도된 동작"}
  ]
}
```

## Phase 5 — 적용 (accepted 만)

오케스트레이터가 직접 Edit/Write로 patch를 적용한다. **적용 직전 스코프 경계를 재확인한다(방어선):** `repo-wide` 면 patch 표적 경로가 루트 `CLAUDE.md` 이거나 `*/skills/*/SKILL.md` 인지 검사하고, 그 밖이면 적용하지 않고 `scope-escalation` 으로 되돌린다. `plugin` 이면 표적이 그 플러그인 디렉토리 안인지 검사한다. 적용 순서는 동일 파일이 여러 patch 대상이면 한 번에 묶어 적용 (충돌 최소화). description을 건드린 경우 `trigger_eval_{N}.json` 도 함께 적용 결과 디렉토리(`evolution-memory/trigger-evals/`)로 보존.

적용 후 1회 자체 점검:
- 적용된 모든 표적이 활성 스코프의 패치 경계 안 (repo-wide: 루트 CLAUDE.md + SKILL.md만)
- 본문 < 500줄 유지
- frontmatter는 `name`/`description` 만
- 트리거 충돌 없음 (Phase 6 참고)

## Phase 6 — 트리거 충돌 검증 (description을 바꿨을 때만)

`harness-generator`, `skill-creator`, 다른 하네스 진입 스킬과의 트리거 충돌을 확인한다.

- 새 description의 should-trigger 8–10개 / should-not-trigger 8–10개를 큐로 두고, 인접 영역(harness-generator 트리거, skill-creator 트리거, 다른 도메인 오케스트레이터 트리거) 키워드를 should-not-trigger에 포함시킨다.
- 충돌이 발견되면 다시 Phase 3로 (해당 refinement만) 회귀.

## Phase 7 — 메모리 큐레이션 + 회차 요약

`evolution-historian` 1회 호출.

```
Agent(
  subagent_type="evolution-historian",
  model="opus",
  prompt="다음 회차 결과를 evolution-memory/ 에 누적하라.
          평가 스코프: {repo-wide | plugin:<plugin>}
          입력: _workspace/phase2_diagnosis_*.json,
                _workspace/phase2_refinement_*.json,
                _workspace/phase2_decisions.json
          누적 대상: repo-wide 면 .claude/evolution-memory/, plugin 이면 plugins/{대상 플러그인}/evolution-memory/
          (없으면 새로 만들 것)"
)
```

`recurring-patterns.md` 의 `needs_attention` 섹션에 신규 항목이 추가됐다면 사용자에게 1회 보고. 회차 요약을 `_workspace/phase2_summary.md` 에 기록 + 사용자에게 핵심만 표로 보여준다.

회차 요약 표 형식:

| diagnosis_id | target | change_kind | decision | applied |
| ------------ | ------ | ----------- | -------- | ------- |
| 1 | plugins/foo/skills/bar/SKILL.md | description | accepted | ✓ |
| 2 | ... | body | rejected | – |

## Phase 8 — 회귀 평가 (선택, 권장)

진화한 하네스를 같은 결함 시나리오로 1회 재실행해 결함이 사라졌는지 사용자가 직접 확인하도록 안내. 자동 실행하지 않는다 — 진화는 사용자 행위와 결합돼야 신뢰가 유지된다.

회귀 평가 결과를 다음 회차의 진단 입력으로 쓸 수 있도록 `_workspace/` 보존을 사용자에게 1회 권고.

---

## 데이터 전달 전략 매트릭스

| 전략 | 도구 | 용도 |
| ---- | ---- | ---- |
| 파일 기반 | Read/Write 합의된 경로 | trajectory, diagnosis, refinement, patch — 큰 데이터 + 감사 |
| 반환 기반 | Agent 반환 메시지 | 진단가/refiner 완료 신호 + 1줄 요약 |
| 영속 메모리 | `evolution-memory/` | 회차 간 패턴 누적, 다음 진단의 가중치 |

## 에러 정책

- 진단 실패 (`severity: unknown`) → 해당 결함만 누락 처리하고 진행. 사용자에게 1회 보고.
- repo-wide 모드에서 표적이 패치 경계 밖(`scope-escalation`) → patch 없이 보고. 사용자가 "단일 플러그인 평가 모드 재실행"을 선택하면 같은 결함을 `plugin` 스코프로 재진단한다 (Phase 4 정의대로: Phase 1 step 0 스코프 질문·`plugins/` 스캔을 생략하고, 보존 표적 경로에서 plugin을 자동 확정한 뒤 Phase 1 이후 단계부터 재개). 선택하지 않으면 해당 결함은 deferred 로 다음 회차에 넘긴다.
- 표적이 레포 루트 메타데이터(`.claude-plugin/marketplace.json`, `scope_status: "out-of-scope"`) → scope-escalation도 plugin 모드 적용도 불가. patch 없이 `change_kind: "blocked"` 로 "사용자 직접 수정" 보고.
- 에이전트 stall (장시간 무진행) → 동시 spawn 배치 크기를 줄이고(≤ 4~6, 필요시 더 작게) 각 에이전트의 read 범위를 좁혀 재시도. 그래도 멈추면 순차 처리로 폴백한다.
- patch 적용 실패 (Edit 충돌) → 자동 재시도 1회. 그래도 실패하면 결정 ledger에 `decision: "apply-failed"` 로 기록하고 사용자 개입 요청.
- 같은 표적 3회째(누적 ≥3) 패치 권고 → 본문 patch 거절 + `change_kind: "structural-redesign-required"` 로 사용자에게 "구조 재설계 권고" 보고 (`harness-generator` 재실행으로 redirect). (임계치 3회는 핵심 원칙·Phase 1·concept-mapping과 동일.)

## 테스트 시나리오

(아래 예시의 `{대상-플러그인}` / `{대상-스킬}` 자리에는 사용자가 그 회차에 지목한 어떤 하네스의 경로든 들어간다. 본 스킬은 특정 플러그인에 종속되지 않는다.)

### 정상 흐름 (repo-wide 기본 — SKILL.md description 패치)

1. 사용자: "{어떤 하네스}의 {어떤 스킬}이 자꾸 트리거 안 됨. '{사용자가 실제로 쓴 표현}' 이라고 해도 안 잡힘."
2. Phase 0: `_workspace/` 없음 → 초기 실행 1줄 보고.
3. Phase 1: 스코프 질문 → 사용자가 "전체 레포"(또는 무응답) 선택 → `repo-wide`. 결함 = 트리거 누락 1건. 표적은 레포 전역에서 해소 → `plugins/{대상-플러그인}/skills/{대상-스킬}/SKILL.md` (SKILL.md = 패치 경계 안).
4. Phase 2-1: trajectory 없음 → 사용자 묘사를 정규화. Phase 2-2: 진단 1건 spawn → `target.kind: description`, `target.scope_status: in-boundary`, `evidence: "사용자 표현이 description의 키워드 풀과 매칭 안 됨"`.
5. Phase 3: refinement 1건 — description에 누락된 표현 클래스(공식/캐주얼) 추가 + trigger_eval JSON 8/10.
6. Phase 4: 사용자 `accepted`.
7. Phase 5: 경계 재확인(SKILL.md → 통과) 후 patch 적용. Phase 6: 충돌 검증 (다른 스킬 description과 키워드 겹침 점검).
8. Phase 7: `.claude/evolution-memory/history.jsonl` 신규 1줄, `recurring-patterns.md` 카운트 1.

### 흐름 — repo-wide에서 경계 밖 표적 (scope-escalation)

1. 사용자: "전체 점검해줘. `/orchestrator` 가 Phase 4에서 매번 멈춰."
2. Phase 1: 스코프 = `repo-wide`. 결함 = 오케스트레이터 커맨드 실패 1건.
3. Phase 2-2: 진단 → 표적 = `plugins/frontend-harness/commands/orchestrator.md` (커맨드 파일). `target.scope_status: plugin-only` (repo-wide 패치 경계 밖).
4. Phase 3: refiner → `change_kind: "scope-escalation"`, patch 미생성.
5. Phase 4: "이 결함은 `frontend-harness` 단일 플러그인 평가 모드에서만 고칠 수 있습니다 — 재실행할까요?" 노출.
6. 사용자가 수락 → Phase 4 정의대로(step 0 스코프 질문·`plugins/` 스캔 생략, 보존 경로에서 `plugin: frontend-harness` 자동 확정) Phase 1 이후 단계부터 재진입 → commands/orchestrator.md 패치 가능.

### 흐름 — plugin 모드 (단일 플러그인 심층)

1. 사용자: "`doc-harness` 플러그인 전체 평가해줘."
2. Phase 1: 스코프 질문 → "단일 플러그인" + `doc-harness` 확정 → `plugin: doc-harness`. 대상 = `plugins/doc-harness/` 전체.
3. Phase 2-2: 진단 표적이 `agents/doc-section-writer.md` 든 `plugin.json` 이든 `skills/.../SKILL.md` 든 모두 `target.scope_status: in-boundary` (그 플러그인 내부이므로).
4. Phase 3~5: 경계 안이므로 정상 patch.
5. Phase 7: `plugins/doc-harness/evolution-memory/` 에 누적.

### 에러 흐름 — 반복 패턴 임계치 도달

1. 사용자: "또 같은 스킬이 안 먹어요."
2. Phase 0/1: 스코프에 맞는 `evolution-memory/recurring-patterns.md` 의 `needs_attention` 에 해당 표적이 이미 3회 누적.
3. Phase 1 직후 즉시 사용자에게 보고: "이 표적은 이미 3회 본문 패치됐습니다. 본문 수정으로 더 가도 좋지만, 구조 재설계(`harness-generator` 재실행)를 권고드립니다. 어떻게 진행할까요?"
4. 사용자 선택에 따라: 본문 패치 진행 또는 `harness-generator` 호출 안내 후 종료.

---

## 후속 작업 키워드 (description 보강용)

이 스킬은 다음 후속 키워드에 반응한다: "다시 봐줘", "이전 회차 기반으로", "또 안 됨", "같은 실수 반복", "보완해줘", "재진화", "추가 결함 발견", "패치 거절했던 거 다시", "구조 재설계".

## 참고 자료

- [Trajectory 캡처 방법론](../trajectory-capture/SKILL.md)
- [결함 진단 루브릭](../failure-diagnosis/SKILL.md)
- [Eval-driven 개선 방법론](../eval-driven-refinement/SKILL.md)
- [Evolver ↔ skill-creator 매핑 상세](references/concept-mapping.md)
