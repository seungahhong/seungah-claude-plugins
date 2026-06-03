# 실행유형 판별 (Phase 0)

오케스트레이터는 Phase 0에서 `experience-store/` 와 `_workspace/` 의 유무, 그리고 입력 신호(현 세션 redirect 발화·보강 요청·외부 .md)의 변화 여부만 보고 **실행유형을 자동 판별**한 뒤 1줄로 보고한다. 판별을 먼저 하는 이유는, 회차 간 누적 경험(full-trace experience store)을 어디서부터 warm-start 할지와 휘발성 작업물(`_workspace/`)을 보존할지 폐기할지가 유형마다 다르기 때문이다. 판별을 건너뛰면 과거 raw trace를 덮어쓰거나(데이터 손실) 이전 회차 결정을 중복 재실행한다.

## 판별 표

| 조건 (experience-store / _workspace 유무 · 입력변화) | 실행유형 | 동작 |
|---|---|---|
| `experience-store/` 없음 (history.jsonl·index.json 부재) | **초기실행** | store 디렉토리·ledger·index·pareto·recurring-patterns를 빈 상태로 생성. warm-start 없음. `_workspace/{run}/` 신규. Phase 1로 진행 |
| `experience-store/` 있음 + `_workspace/` 비어있음(직전 회차가 깔끔히 종료) + **새 입력 신호** | **신규회차** | 직전 회차 history/index/pareto/recurring 전부 **warm-start로 로드**(needs_attention 먼저 확인). 새 `_workspace/{run}/` 시작. 과거 traces/는 읽기 전용 참조 |
| `experience-store/` 있음 + `_workspace/{run}/` 잔존(phase 산출물 일부만 존재) + **입력 신호 동일** | **부분재실행** | 미완료 Phase부터 이어서 실행. 잔존 `_workspace/{run}/{phase}_*.json`·`*_decisions.json`을 그대로 재사용(이미 끝난 Phase 재실행 금지). store는 append-only이므로 손대지 않음 |
| `experience-store/` 있음 + `_workspace/{run}/` 잔존 + **입력 신호 바뀜**(다른 redirect/다른 .md/다른 스코프) | **새실행** | 잔존 `_workspace/{run}/`을 통째로 `_workspace_prev/`로 이동(증거 보존) 후 새 `_workspace/{run}/` 시작. store warm-start는 신규회차와 동일하게 수행 |

## warm-start 규칙 (유형별)

- **초기실행**: warm-start 대상 없음. 단, store 골격을 즉시 만들어 Phase 8 적재가 실패하지 않게 한다.
- **신규회차 / 새실행**: `recurring-patterns.md`의 `needs_attention(≥3)` 표적을 **가장 먼저** 읽어 이번 진단의 confound 후보로 깔아둔다. 이어 `pareto.json` frontier 좌표, `index.json`의 최신 run/candidate 포인터를 로드한다. 요약(index/recurring)은 **네비게이션용 힌트**일 뿐이며, 실제 진단 근거는 항상 `{run}/{candidate}/traces/*.jsonl` 원본을 grep/cat로 직접 조회한다. 요약만 보고 진단하면 Table 3의 Summary(38.7)로 퇴화한다.
- **부분재실행**: store warm-start를 **다시 하지 않는다**. 직전 회차에서 이미 로드·기록한 `_workspace/{run}/` 결정을 신뢰하고 끊긴 Phase만 이어 붙인다(중복 진단·중복 patch 방지).

## _workspace 이동 규칙

- `_workspace/`는 **회차 휘발물**(phase 중간 산출·decisions·summary)을 담는다. store(영속)와 분리되어, 회차가 바뀌면 정리 대상이다.
- **새실행**일 때만 잔존 `_workspace/{run}/`을 `_workspace_prev/`로 옮긴다. 덮어쓰지 않고 이동하는 이유는, 입력이 바뀐 직전 회차의 미완료 흔적도 추후 confound 분석에 쓰일 수 있어 증거로 보존해야 하기 때문이다.
- **부분재실행**은 이동하지 않는다(같은 입력의 연속이므로 잔존물이 곧 진행 상태다).
- `_workspace_prev/`는 1세대만 유지한다(다음 새실행 시 직전 prev는 폐기 가능). store traces/와 달리 이력 가치가 낮은 중간물이므로 무한 누적하지 않는다.

## 보고 형식 (1줄)

판별 직후 다음 형태로만 보고한다(여담 금지):

`Phase 0 — 실행유형: {초기실행|신규회차|부분재실행|새실행} / store: {신규생성|warm-start n건} / _workspace: {신규|이어서|prev 이동}`
