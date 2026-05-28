---
name: trajectory-capture
description: 하네스 실행 1회차의 도구 호출·산출물·상태를 시간순으로 캡처해 정규화된 trajectory(`*.jsonl` + 표)로 만드는 방법론 스킬. 주로 harness-evolver Phase 2-1에서 trajectory-analyst 에이전트가 따른다. raw trace가 없을 때 사용자 묘사를 정규화하는 패스도 포함. 사용자가 "하네스 실행 기록 정리", "오케스트레이터 trace 정규화", "하네스 trajectory 만들어", "진화 회차용 trajectory 정리" 등을 말할 때 트리거된다. 일반 애플리케이션 로그 분석에는 사용하지 않는다.
---

# Trajectory Capture — 하네스 실행 궤적 캡처/정규화 방법론

`trajectory-analyst` 에이전트가 본 스킬을 따른다. 직접 사용자 요청에 답하는 일은 거의 없고, `harness-evolver` Phase 2-1 에서 호출된다.

## 왜 trajectory가 필요한가

- 결함 진단의 근거가 사실이어야 한다. 사람이 묘사한 결함은 증상에 치우치고 원인을 가린다.
- 같은 결함이 다음 회차에도 재발하는지를 측정하려면 회차 간 비교가 가능한 정규화된 표가 필요하다.
- Trajectory는 단순 로그가 아니라 **진단의 입력 스키마**다.

## 캡처 단위와 우선순위

| 우선순위 | 필드 | 설명 |
| ------ | ---- | ---- |
| 1 | `step` | 1부터 단조 증가 |
| 1 | `phase` | 오케스트레이터의 Phase id (`phase2-2`) |
| 1 | `agent` | 호출된 subagent_type 또는 `orchestrator` |
| 1 | `tool` | 호출 도구명 (`Agent`, `Edit`, `Bash`, ...) |
| 1 | `status` | `ok | error | truncated | unknown` |
| 2 | `input_summary` | 1줄 요약, raw payload 금지 |
| 2 | `output_ref` | 산출물 파일 경로 또는 해시. 본문 적재 금지 |
| 3 | `wall_ms` | 알 수 있을 때만 |
| 3 | `note` | trajectory-analyst의 사실적 비고 (해석 금지) |

**규칙:**
- 도구 호출 1개당 1행. Phase 단위로 묶지 않는다.
- `input_summary` 와 `output_ref` 는 진단가가 trajectory를 읽고도 컨텍스트가 넘치지 않게 압축한다.
- "왜" 는 적지 않는다. 사실만.

## 입력 형태별 처리

### A. raw trace (jsonl)

- `_workspace/trajectories/{session}.jsonl` 형식.
- 한 줄 = 한 도구 호출. 도구가 자체 페이로드를 잘랐을 경우 `status: truncated`.
- 그대로 시간순 단일 패스로 표로 변환.

### B. 사용자 자연어 묘사

- 사용자가 "이런 흐름으로 돌았어요" 를 자연어로 묘사한 경우.
- 표 행마다 `confidence: low` 마크 + `~` 접두로 표시 (예: `~Agent`).
- 진단가가 가중치를 낮추도록 메타에 `derived_from: user_description` 기록.

### C. 부분 trace + 묘사 혼합

- 가능한 trace를 우선 채우고, 갭(gap)은 자연어 보충. 갭 행에는 `confidence: low` 마크.

## 출력 스키마

### `{phase}_trajectory_normalized.md`

```markdown
# Trajectory: {session-id} / {phase}

| step | phase | agent | tool | input_summary | output_ref | status | wall_ms |
| ---- | ----- | ----- | ---- | ------------- | ---------- | ------ | ------- |
| 1 | phase1 | orchestrator | AskUserQuestion | 대상 하네스 선택 | – | ok | 1200 |
| 2 | phase2-1 | trajectory-analyst | – | trace 1건 | _workspace/phase2_trajectory_facts.json | ok | 4800 |
```

### `{phase}_trajectory_facts.json`

```json
{
  "session": "sess-YYYYMMDD-NNN",
  "phase": "phase2",
  "derived_from": "raw_trace | user_description | mixed",
  "rows": [
    {"step": 1, "phase": "phase1", "agent": "orchestrator", "tool": "AskUserQuestion",
     "input_summary": "...", "output_ref": null, "status": "ok", "wall_ms": 1200, "confidence": "high"},
    ...
  ]
}
```

## 흔한 실패 패턴

- **해석 섞기** — `note: "이 호출이 결함의 원인"` 같은 줄. 절대 쓰지 않는다.
- **payload 적재** — `input_summary` 에 1KB 넘는 본문 박기. 1줄로 압축한다.
- **Phase 묶음 행** — "Phase 3 전체" 한 행으로 압축. 진단가가 인과를 못 찾는다.
- **빈 표 출력** — trace가 없으면 한 줄짜리 `output_ref: null` 행을 두고 그 사실만 기록.

## 협업

- 본 스킬 산출물 → `failure-diagnosis` 의 입력.
- raw trace가 없으면 `harness-evolver` Phase 1에서 사용자 묘사를 받아 본 스킬로 정규화.
