---
name: harness-evolver
description: 사용자가 사용 중인 임의의 하네스 스킬에서 오동작/반복 실수/트리거 누락 등 문제가 보고되면, 대상 하네스의 실행 궤적(trajectory)을 캡처·진단해 결함의 근본 원인을 식별하고 skill-creator 방식의 eval-driven iteration으로 자율 진화시키는 메타 오케스트레이터. 특정 플러그인이나 도메인에 종속되지 않으며, 사용자가 지정하거나 본 오케스트레이터가 식별한 어떤 하네스든 대상이 된다. 사용자가 "하네스 고도화", "오케스트레이터 개선", "이 스킬이 안 먹는다", "트리거 누락", "스킬 자동 개선", "harness evolve", "재실행해도 같은 실수", "왜 이 스킬이 트리거 안 되지", "이 하네스 진화시켜줘", "이전 실행 결과를 바탕으로 개선" 등을 말할 때 반드시 이 스킬을 사용한다. 신규 하네스 구축은 harness-generator, 단발성 스킬 작성은 skill-creator를 쓰고, 이 스킬은 "이미 사용 중인 하네스의 문제 개선" 영역만 담당한다. 부분 재실행/추가 개선 요청에도 사용한다.
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

## 핵심 원칙

- **결함 1건 = 진단 1건 = 패치 1건** — 묶지 않는다. 한 회차에 여러 결함이 발견되면 각자 별도 파일로 추적한다. 묶으면 어느 결정이 어느 변화에 책임이 있는지 추적 불가.
- **자동 적용 금지** — 모든 patch는 사용자 승인 후 오케스트레이터가 적용한다. 자동 적용은 신뢰를 깨고, 진화 자체를 망친다.
- **반복 패턴은 표면 수정이 아니라 구조 재설계 신호** — 같은 표적에 3회째 패치 권고가 나오면 본문 패치를 거절하고 `change_kind: "structural-redesign-required"` 로 사용자에게 보고한다.
- **description을 건드릴 땐 트리거 평가 동봉** — skill-creator의 should-trigger / should-not-trigger 8–10개씩을 함께 제시해 검증한다.
- **트리거 충돌 검증 필수** — `harness-generator`, `skill-creator` 와 트리거가 겹치지 않게 한다. 이 스킬은 "이미 있는 하네스를 개선" 영역만.

## 산출물 배치 규약

```
{대상 플러그인 또는 .claude/}/
  evolution-memory/                     # 영속 메모리 (커밋 대상)
    history.jsonl                       # 회차별 결정 ledger
    recurring-patterns.md               # 표적별 카운트 + needs_attention
    patches/{date}-{target-slug}.md     # 적용된 패치 사본

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

`evolution-memory/` 는 대상 하네스의 플러그인 루트 또는 `.claude/` 하위에 둔다. `_workspace/` 는 회차마다 새로 만든다.

---

## Phase 0 — 컨텍스트 확인

`_workspace/` 와 `evolution-memory/` 를 검사해 실행 유형을 자동 판별하고 1줄 보고 후 진행한다.

- `_workspace/` 없음 + `evolution-memory/` 없음 → **초기 실행**.
- `evolution-memory/` 있음, `_workspace/` 없음 → **신규 회차** (이전 회차의 nudge를 입력으로 활용).
- `_workspace/` 있음, 같은 회차 재요청 → **부분 재실행** (실패한 진단·refinement만 재실행).
- 입력(대상 하네스/결함 묘사) 변경 → **새 실행** (`_workspace/` → `_workspace_prev/` 이동 후 재생성).

## Phase 1 — 대상 하네스 식별 및 결함 수집

다음 3가지를 1회 인터뷰로 확보한다(한 번에 한 질문씩).

1. **대상 하네스** — 어떤 플러그인의 어떤 스킬/오케스트레이터인가. 모르면 `agents/`, `skills/`, `commands/` 디렉토리를 스캔해 후보 제시.
2. **결함 묘사** — "무엇이 일어났고 무엇을 기대했는가" 식으로 결함별로 묘사받는다. 결함이 여러 개면 각자 1줄로 분리해 받는다.
3. **trajectory 가용 여부** — raw trace 파일이 있으면 경로, 없으면 사용자 묘사로 대체 (이 경우 진단 신뢰도 표시 `~confidence: low` 가 따라붙음).

이 단계 결과를 `_workspace/{phase}_intake.md` 에 1회 기록.

`evolution-memory/recurring-patterns.md` 의 `needs_attention` 섹션을 읽어 같은 표적이 누적 임계치(≥3) 도달했다면 사용자에게 먼저 알리고 "본문 패치 대신 구조 재설계를 권고합니다" 라고 옵션을 제시한다.

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

```
# 결함 N건 → 단일 메시지에서 N개 동시 spawn
Agent(
  subagent_type="failure-diagnostician",
  model="opus",
  run_in_background=true,
  prompt="failure-diagnosis 스킬에 따라 결함 1건을 진단하라.
          결함 #N: {결함 N의 자연어 묘사}
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
            이전 패치 (있다면): _workspace/phase2_patch_{N-1}.md
            반복 패턴: evolution-memory/recurring-patterns.md
            산출: _workspace/phase2_refinement_{N}.json,
                  _workspace/phase2_patch_{N}.md,
                  (description 수정 시) _workspace/phase2_trigger_eval_{N}.json"
  )
```

`change_kind: "structural-redesign-required"` 또는 `"blocked"` 가 나오면 patch를 만들지 않고 그 사실을 보고에 포함시킨다.

## Phase 4 — 사용자 게이트 (필수)

모든 refinement를 1회 묶어 사용자에게 보여주고 결함별로 `accepted | rejected | deferred` 를 받는다. 답을 강제로 모두 받지 않는다 — 일부만 결정해도 진행 가능하게 한다 (deferred 는 다음 회차로 넘김).

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

오케스트레이터가 직접 Edit/Write로 patch를 적용한다. 적용 순서는 동일 파일이 여러 patch 대상이면 한 번에 묶어 적용 (충돌 최소화). description을 건드린 경우 `trigger_eval_{N}.json` 도 함께 적용 결과 디렉토리(`evolution-memory/trigger-evals/`)로 보존.

적용 후 1회 자체 점검:
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
          입력: _workspace/phase2_diagnosis_*.json,
                _workspace/phase2_refinement_*.json,
                _workspace/phase2_decisions.json
          누적 대상: {대상 플러그인 루트}/evolution-memory/
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
- patch 적용 실패 (Edit 충돌) → 자동 재시도 1회. 그래도 실패하면 결정 ledger에 `decision: "apply-failed"` 로 기록하고 사용자 개입 요청.
- 같은 표적 4회 이상 패치 권고 → patch 거절 + 사용자에게 "구조 재설계 권고" 보고 (`harness-generator` 재실행으로 redirect).

## 테스트 시나리오

(아래 예시의 `{대상-플러그인}` / `{대상-스킬}` 자리에는 사용자가 그 회차에 지목한 어떤 하네스의 경로든 들어간다. 본 스킬은 특정 플러그인에 종속되지 않는다.)

### 정상 흐름

1. 사용자: "{어떤 하네스}의 {어떤 스킬}이 자꾸 트리거 안 됨. '{사용자가 실제로 쓴 표현}' 이라고 해도 안 잡힘."
2. Phase 0: `_workspace/` 없음 → 초기 실행 1줄 보고.
3. Phase 1: 대상 = `plugins/{대상-플러그인}/skills/{대상-스킬}/`, 결함 = 트리거 누락 1건.
4. Phase 2-1: trajectory 없음 → 사용자 묘사를 정규화. Phase 2-2: 진단 1건 spawn → `target: description`, `evidence: "사용자 표현이 description의 키워드 풀과 매칭 안 됨"`.
5. Phase 3: refinement 1건 — description에 누락된 표현 클래스(공식/캐주얼) 추가 + trigger_eval JSON 8/10.
6. Phase 4: 사용자 `accepted`.
7. Phase 5: patch 적용. Phase 6: 충돌 검증 (다른 스킬 description과 키워드 겹침 점검).
8. Phase 7: `evolution-memory/history.jsonl` 신규 1줄, `recurring-patterns.md` 카운트 1.

### 에러 흐름 — 반복 패턴 임계치 도달

1. 사용자: "또 같은 스킬이 안 먹어요."
2. Phase 0: `evolution-memory/recurring-patterns.md` 의 `needs_attention` 에 해당 표적이 이미 3회 누적.
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
