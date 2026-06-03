# experience-store 스키마

experience-store는 meta-harness의 영속 기억이다. 과거 회차의 결함·진단·패치·궤적을 다음 회차가 grep/cat로 **직접 조회**할 수 있도록 보존한다. 이 스토어의 설계 원칙은 단 하나의 불변식에서 출발한다.

## 제1 불변식 — 요약 금지, traces는 항상 원본

**store에 요약을 넣는 순간 진단 능력은 퇴화한다.** 근거 논문(Meta-Harness, arXiv 2603.28052v1) Table 3은 full-trace를 보존한 경우(56.7)가 점수+요약만 보존한 경우(38.7)보다 우월함을 보였다. 따라서 다음을 강제한다.

- `traces/*.jsonl` 는 **항상 원본 raw trace**다. 도구 호출 payload·산출물 전문·redirect 발화 원문을 절대 압축·생략하지 않는다.
- **요약(summary)은 오직 navigation 보조물에만 둔다** — `index.json`, `recurring-patterns.md`. 이 둘은 "어디를 grep할지" 가리키는 포인터이지 진단 근거가 아니다.
- 진단 에이전트(failure-diagnostician)·개선 에이전트(pareto-refiner)는 index의 요약을 **신뢰 근거로 인용하지 않는다.** 요약으로 후보를 좁힌 뒤, 반드시 `traces/`의 원본을 cat/grep으로 다시 읽어 step 번호·파일 경로를 evidence로 인용한다.

> 왜: 요약은 "무엇이 일어났는가"의 인과 사슬(confound·순서·중간 상태)을 뭉갠다. confound 격리(두 실패의 *공통* 변경이 진범)는 원본 trace 없이는 불가능하다.

## 위치 분기 — repo-wide(기본) vs plugin(opt-in)

스토어 루트 `{store-root}`는 평가 스코프에 따라 갈린다.

- `repo-wide`(기본): `{store-root}` = `.claude/experience-store/`
  - 패치 표적이 루트 CLAUDE.md + 임의 SKILL.md로 한정되므로, 레포 루트의 단일 스토어가 모든 회차를 누적한다.
- `plugin`(opt-in): `{store-root}` = `plugins/{target}/experience-store/`
  - 지목된 플러그인 내부에 격리된 스토어를 둔다. 그 플러그인의 모든 파일이 패치 경계 안이므로, 회차 기억도 플러그인 단위로 묶는다.

> 왜: 스코프가 곧 패치 경계이고, 기억의 단위도 패치 경계와 일치해야 recurring 카운트가 의미를 가진다. repo-wide 회차와 plugin 회차의 기억을 섞으면 needs_attention(≥3) 판정이 오염된다.

## 디렉토리 트리

```
{store-root}/
  history.jsonl                       # append-only 결정 ledger (1줄 = 결함 1건의 결정 1건)
  index.json                          # navigable 포인터 (run/candidate 경로·카운트·최신갱신)
  pareto.json                         # Pareto frontier 좌표 (매 회차 재계산)
  recurring-patterns.md               # 표적별 카운트 + needs_attention ≥3 nudge
  patches/
    {date}-{target-slug}.md           # 적용된 patch 사본 (예: 2026-06-03-claude-md-why-first.md)
  {run}/                              # run = 회차 식별자 (예: run-2026-06-03-001)
    {candidate}/                       # candidate = 패치 후보 식별자 (예: cand-claude-md-1)
      harness/                         # 표적 자산 원본 스냅샷 (패치 전 상태)
        CLAUDE.md
        skills/.../SKILL.md
      score.json                       # assertion 통과 + Pareto 4축 좌표
      traces/
        *.jsonl                        # 원본 raw trace — 요약 금지

_workspace/                            # 회차 휘발물 (스토어와 분리, 다음 새 실행 시 _workspace_prev/로 이동)
  {run}/
    phase{n}_*.json                    # Phase별 중간 산출 (예: phase3_diagnoses.json)
    *_decisions.json                   # 사용자 승인 게이트 결정 스냅샷
    {run}_summary.md                   # 회차 1줄 요약 (navigation 용도)
```

> 용어: `{run}`은 한 번의 `/meta-harness` 실행. `{candidate}`는 그 안에서 진단 1건에 대응해 pareto-refiner가 만든 패치 후보 1건. 결함 1건 = 진단 1건 = candidate 1건이 기본 대응이다.

## 파일별 스키마 + 예시

### history.jsonl — append-only 결정 ledger

한 줄이 곧 결함 1건에 대한 최종 결정 1건이다. **append만 한다**(과거 줄을 수정·삭제하지 않는다 — ledger는 결정의 시간순 사실이다).

```json
{"ts":"2026-06-03T14:22:10Z","run":"run-2026-06-03-001","candidate":"cand-claude-md-1","trigger_r":"R1","target_kind":"claude-md","target_path":"CLAUDE.md","scope_status":"in-boundary","why":"redirect 발화에서 사용자가 '방향 다시'를 2회 요청, 직전 산출물이 Why 없는 MUST만 나열(trace step 7,11)","severity":"high","confidence":"high","decision":"accepted","applied":true,"patch_ref":"patches/2026-06-03-claude-md-why-first.md","pareto":{"behavior_alignment":0.82,"rule_body_cost":41,"trigger_precision":0.90,"generalization":0.78}}
```

- `decision` ∈ `accepted|rejected|deferred`. `applied`는 accepted+적용 완료일 때만 true.
- `scope_status` ∈ `in-boundary|scope-escalation|out-of-scope`.
- `why`는 trace의 step 번호/파일 경로를 인용한다(요약문 금지).

### index.json — navigable 포인터

"어디를 grep/cat할지" 가리키는 지도. 요약은 여기까지만 허용된다.

```json
{
  "store_root": ".claude/experience-store/",
  "scope": "repo-wide",
  "updated_at": "2026-06-03T14:25:00Z",
  "runs": [
    {
      "run": "run-2026-06-03-001",
      "trigger_r": "R1",
      "candidate_count": 3,
      "accepted": 2,
      "rejected": 1,
      "deferred": 0,
      "candidates": [
        {
          "candidate": "cand-claude-md-1",
          "target_kind": "claude-md",
          "target_path": "CLAUDE.md",
          "trace_glob": "run-2026-06-03-001/cand-claude-md-1/traces/*.jsonl",
          "score_path": "run-2026-06-03-001/cand-claude-md-1/score.json",
          "nav_summary": "Why-first 위반 진단 → CLAUDE.md에 이유-우선 규약 추가 (원본은 trace_glob 참조)"
        }
      ]
    }
  ],
  "totals": {"runs": 1, "candidates": 3, "applied_patches": 2}
}
```

- `nav_summary`는 **navigation 힌트일 뿐**이다. 끝에 "원본은 trace_glob 참조"를 붙여, 이것이 근거가 아님을 구조적으로 명시한다.
- `trace_glob`·`score_path`는 `{store-root}` 기준 상대경로.

### pareto.json — Pareto frontier 좌표 (매 회차 재계산)

빈도×severity로 가중한 frontier. 4축은 `pareto-axes.md` 참조.

```json
{
  "updated_at": "2026-06-03T14:25:00Z",
  "axes": ["behavior_alignment","rule_body_cost","trigger_precision","generalization"],
  "directions": {"behavior_alignment":"max","rule_body_cost":"min","trigger_precision":"max","generalization":"max"},
  "frontier": [
    {"candidate":"run-2026-06-03-001/cand-claude-md-1","behavior_alignment":0.82,"rule_body_cost":41,"trigger_precision":0.90,"generalization":0.78,"on_frontier":true},
    {"candidate":"run-2026-06-03-001/cand-skill-2","behavior_alignment":0.74,"rule_body_cost":28,"trigger_precision":0.95,"generalization":0.71,"on_frontier":true}
  ],
  "dominated": [
    {"candidate":"run-2026-06-03-001/cand-skill-3","behavior_alignment":0.70,"rule_body_cost":52,"trigger_precision":0.80,"generalization":0.60,"dominated_by":"cand-claude-md-1","reason":"본문비용 증가(52>41)에도 정합 이득 없음 → reject"}
  ]
}
```

- `dominated[].reason`은 비후퇴 규칙 위반 사유를 명시한다(예: 본문 길이↑인데 정합 이득 없음).

### score.json — assertion 통과 + Pareto 좌표

candidate 1건의 측정 결과. lightweight validation(Phase 5) 통과 여부와 4축 좌표를 담는다.

```json
{
  "candidate": "cand-claude-md-1",
  "run": "run-2026-06-03-001",
  "lightweight_validation": {
    "frontmatter_keys_ok": true,
    "crossref_paths_exist": true,
    "trigger_conflict": false,
    "why_missing_must": false,
    "verdict": "interface-valid"
  },
  "assertions": [
    {"id":"redirect-resolved","desc":"redirect 의도가 본문에 반영","pass":true},
    {"id":"why-first","desc":"새 규칙이 이유를 먼저 제시","pass":true}
  ],
  "pareto": {"behavior_alignment":0.82,"rule_body_cost":41,"trigger_precision":0.90,"generalization":0.78},
  "trigger_eval_ref": "run-2026-06-03-001/cand-claude-md-1/traces/trigger-eval.jsonl"
}
```

- `lightweight_validation.verdict` ∈ `interface-valid|interface-invalid`. invalid면 비싼 적용 전에 후보 탈락(Phase 5).

### traces/*.jsonl — 원본 raw trace (요약 금지)

시간순 한 줄 = 한 step. 도구 호출·산출물·redirect 발화·상태 전이를 **원형 그대로** 적재한다. payload를 잘라내지 않는다.

```json
{"step":7,"ts":"2026-06-03T14:18:03Z","actor":"user","kind":"redirect","raw":"방금 그 방향 말고 다시 해줘. 왜 그렇게 갔는지 보고 지금 쓰던 스킬 고쳐줘.","active_skill":"frontend-harness:planner","source":"current-session"}
```

```json
{"step":11,"ts":"2026-06-03T14:19:40Z","actor":"assistant","kind":"artifact","raw_path":"_docs/plan-draft.md","raw_excerpt_full":"<산출물 전문, 절단 없음>","tool":"Write","source":"current-session"}
```

- R3(외부 .md 역추적) 시에는 `.md` 전문과 3단 폴백 출처 단서를 별도 step으로 원형 적재하고 `confidence`를 부여한다.

```json
{"step":2,"ts":"2026-06-03T14:30:00Z","actor":"trace-capturer","kind":"md-provenance","md_path":"_docs/feat-x-spec.md","raw_full":"<md 전문>","fallback":{"tier":1,"signal":"산출 경로 규약 매칭 (_docs/*-spec.md)","confidence":"high"},"resolved_author":{"agent":"doc-writer","skill":"doc-writing"}}
```

## _workspace 휘발 규칙

`_workspace/`는 **회차 휘발물**이다 — 스토어(영속)와 분리한다.

- 같은 회차의 부분 재실행은 기존 `_workspace/{run}/`을 이어 쓴다.
- **새 실행을 시작하면 직전 `_workspace/`를 `_workspace_prev/`로 이동**한 뒤 새 `_workspace/`를 연다. 이전 회차의 중간 산출이 새 회차의 진단을 오염시키지 않게 하기 위함이다.
- 단, 영속 기억(history.jsonl·index.json·pareto.json·recurring-patterns.md·patches/·traces/)은 `{store-root}`에 남아 회차를 가로질러 누적된다.

> 왜: 휘발물(Phase 중간 JSON, 결정 스냅샷)과 영속 ledger를 한 곳에 두면, 새 실행이 옛 중간물을 사실로 오인한다. 물리적 분리가 가장 값싼 격리다.
