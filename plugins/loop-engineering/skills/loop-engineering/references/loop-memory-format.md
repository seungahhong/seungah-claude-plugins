# Loop Memory — on-disk 포맷

지속학습 루프(Fail→Investigate→Verify→Distill→Consult)를 회차·세션을 넘어 누적하기 위한 파일 포맷.
**원본 trace는 보존(요약·삭제 금지)하고, 검증된 교훈만 distill**한다 — 진단의 근거는 항상 원본에 있다.

> **external memory = "무엇이 됐고 무엇이 남았나"(the state file is the spine).** 모델은 run 사이 모든 걸 잊지만("the agent
> forgets, the repo doesnt") 이 파일들은 디스크에 남아 다음 run이 멈춘 자리에서 이어가게 한다 — `goal.md`(목표)·`iterations.jsonl`
> (무엇을 시도했고 통과했나)·`lessons.md`(다음에 적용)가 그 등뼈다. (선택) 자동화 프론트엔드(principles §7)를 쓰면, 루프가 처리하지
> 못한 항목을 사람에게 넘기는 `triage-inbox.md`를 같은 디렉토리에 둘 수 있다(코어 루프 동작에는 영향 없음).

## 위치

기본 `.claude/loop-memory/{slug}/` (사용자가 다른 경로를 지정하면 그곳). `{slug}`는 목표를 식별하는
짧은 kebab-case(예: `auth-token-refresh-green`)로, **Phase 0에서 goal-setter가 목표 한 줄을 정규화해 Goal Card에 부여**한다.
재실행 시 오케스트레이터는 정규화된 slug가 일치/동일 목표인 기존 디렉토리가 있으면 새로 만들지 않고 그 slug를 재사용해 기존 lessons.md를 consult한다(없을 때만 신규 생성).

```
.claude/loop-memory/{goal-slug}/
  goal.md            # 확정 Goal Card (불변 — 목표가 바뀌면 새 슬러그)
  iterations.jsonl   # 반복별 raw trace (append-only)
  lessons.md         # distill된 재사용 규칙 (Consult 대상)
```

## goal.md

Phase 0에서 `goal-setter`가 확정한 Goal Card 원문. slug·목표·성공기준(관찰형)·검증 방법(실행 가능)·중단조건·범위(In/Out).
**Phase 1 초기화 때 오케스트레이터가 승인된 Goal Card를 이 파일로 write**한다(단일 writer). 기존 goal.md가 있고
목표가 다르면 이 파일을 수정하지 말고 **새 slug**로 분기한다(불변 규칙 — 메모리 정합성 유지).

## iterations.jsonl (append-only, 요약 금지)

반복 1건당 단계별 JSON 줄(execute/verify, FAIL이면 diagnose). **`memory-curator`가 단일 writer로 매 반복 끝에 append**하며,
`run`·`ts`는 오케스트레이터가 발급해 주입한다(memory-curator는 요약·삭제 없이 원본을 그대로 남긴다).

```jsonl
{"run":"<run-id>","iter":1,"phase":"execute","applied":"초기 시도","hypothesis":"...","change":"파일/명령 무엇을 왜","ts":"<stamp>"}
{"run":"<run-id>","iter":1,"phase":"verify","verdict":"FAIL","criteria":[{"id":"C1","result":"FAIL","evidence":"npm test: 2 failing — <발췌>"}]}
{"run":"<run-id>","iter":1,"phase":"diagnose","symptom":"...","root_cause":"...","confirmed":true,"evidence":"trace step/diff 인용","next_approach":"다음 반복 지시","progress":"new|same-cause(k/M)"}
```

- `phase` ∈ execute | verify | diagnose. PASS면 diagnose 줄은 생략하고 verify 줄의 verdict가 PASS. verdict는 PASS|FAIL|BLOCKED.
- `run`: 한 번의 루프 실행을 식별하는 run-id. **Phase 1 진입 시 오케스트레이터가 1회 mint**(기존 iterations.jsonl이 있으면 마지막 run 다음 순번, 없으면 1 또는 타임스탬프)해, 이 실행의 모든 줄과 lessons.md 역참조에 동일 값을 주입한다. 같은 slug로 재실행하면 새 run-id로 분기해 과거 run과 구분한다.
- `confirmed`: failure-analyst가 증거로 원인을 확정했는가(가설이면 false → distill 보류).
- `evidence`: 명령 출력·diff·step 인용 등 *관찰 가능한* 근거. 요약이 아니라 발췌.
- `ts`: 타임스탬프(오케스트레이터가 발급해 주입; 스크립트 컨텍스트에서 시간 함수가 막히면 호출 측에서 주입).

## lessons.md (Consult 대상)

`confirmed:true`인 진단, 또는 증거 있는 PASS에서만 distill된 **재사용 규칙**. 과잉일반화를 막기 위해 적용 조건을 함께 적고,
근거가 된 반복을 역참조한다. 중복 규칙은 빈도만 올리고, 모순되는 새 사실은 기존 규칙을 conflict로 표시한다.

```markdown
# Lessons — {goal-slug}

- [규칙] <재사용 가능한 일반 규칙 한 줄>
  - 적용 조건: <언제 이 규칙이 유효한가>
  - 근거: run <run-id> / iter <n> — <확정 증거 한 줄>
  - 빈도: <누적 관측 횟수>
  - 상태: active | candidate | conflict | retired
```

상태값 정의·전이:

- **active**: 회귀 점검 통과·정상 적용 규칙.
- **candidate**: 과거 통과 사례를 깰 위험이 있어 회귀 미확인인 신규 규칙(검증 후 active 승격).
- **conflict**: 모순되는 새 사실 발견 → 검토 필요(자동 삭제 금지).
- **retired**: 도입 후 성능 저하로 폐기·롤백된 규칙(역참조는 보존).

## Consult 규칙

- 실행/진단 **직전**에만, **현재 목표·증상에 관련된** 규칙을 관련성 순 상위 N개만 surface한다(메모리 전체 투하 금지 — 노이즈 차단).
- executor는 surface된 규칙을 읽고 과거 실패 접근을 반복하지 않는다.
- failure-analyst는 진단 시 관련 규칙을 참고해 같은 원인 재발을 빠르게 인지한다.

## 보존 원칙

- **iterations.jsonl은 절대 요약·압축·삭제하지 않는다.** 메모리가 커지면 오래된 run을 별도 파일로 롤오버하되 원본은 남긴다.
- **lessons.md만 distill의 결과물**이다. 거짓 규칙 누적을 막기 위해 검증된 것만 올리고, conflict는 자동 삭제하지 않고 표시해 사람·다음 진단이 판단하게 한다.
