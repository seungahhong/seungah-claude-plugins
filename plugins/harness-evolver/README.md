# harness-evolver

사용자가 사용 중인 **임의의 하네스 스킬**에서 오동작·트리거 누락·반복 우회 같은 문제가 보고됐을 때, 그 대상 하네스를 캡처·진단·개선하는 메타-개선 플러그인입니다. 특정 플러그인이나 도메인에 종속되지 않으며, 사용자가 지목한 어떤 하네스든 입력으로 받습니다.

설계는 **Evolver 루프**(`trajectory → curated memory → autonomous skill refinement`)와 **skill-creator의 eval-driven iteration**을 결합한 형태입니다. 결함을 **1건 = 진단 1건 = 패치 1건** 단위로 분리해 추적하고, 모든 patch는 사용자 승인 게이트 통과 후에만 적용됩니다 (자동 적용 금지).

---

## 평가 스코프 (repo-wide 기본 / plugin opt-in)

이 플러그인이 도는 **현재 적용 중인 프로젝트 = 이 레포**입니다. 매 회차 Phase 1에서 스코프를 1회 확정합니다.

| 스코프 | 기본 | 진단 대상 | 패치 허용 표적 |
| ----- | --- | -------- | ------------- |
| `repo-wide` (전체 레포) | ✅ | 루트 `CLAUDE.md` + 모든 플러그인의 `SKILL.md` | **루트 `CLAUDE.md` + 임의 플러그인의 `SKILL.md` 만** |
| `plugin` (단일 플러그인) | 명시 요청 시 | 지목한 플러그인 **하나의 모든 파일** | 그 플러그인의 모든 파일 (`plugin.json`·`agents`·`hooks`·`commands`·`skills`·플러그인별 `CLAUDE.md`·`README`) |

- "평가해줘" 한마디로 패키징·에이전트·훅·커맨드까지 손대지 않습니다 — 기본 패치 경계를 프로젝트 지침과 스킬 본문으로 좁힙니다.
- `repo-wide` 에서 진단이 경계 밖 표적(`agents/`·`commands/`·`hooks/`·`plugin.json`·플러그인별 `CLAUDE.md`)을 짚으면 patch 대신 **`scope-escalation`** — "단일 플러그인 평가 모드로 재실행하세요" 를 Phase 4에 노출합니다.
- 사용자가 특정 플러그인을 지목해도 자동 전환하지 않고, Phase 1에서 명시 선택을 받습니다 (애매하면 `repo-wide`).
- `marketplace.json` 은 레포 루트(`.claude-plugin/marketplace.json`) 메타데이터로 어떤 플러그인 디렉토리에도 속하지 않으므로 `repo-wide`·`plugin` 어느 스코프에서도 patch 표적이 아닙니다 — 변경이 필요하면 사용자가 직접 수정합니다.

---

## 핵심 아이디어

| 차용 출처 | 가져온 개념 | 본 플러그인에서의 적용 |
| -------- | --------- | ------------------- |
| Evolver 루프 | Trajectory capture | `_workspace/trajectories/*.jsonl` 단계별 실행 기록 |
| Evolver 루프 | Curated memory + nudges | `evolution-memory/` 영속 디렉토리 + 임계치(3회) 도달 시 자동 권고 |
| Evolver 루프 | Autonomous skill refinement | `skill-refiner` 가 진단 결과 받아 patch 생성 |
| skill-creator | Eval-driven iteration | with/without 비교 + assertion + iteration loop |
| skill-creator | Description optimization | should-trigger / should-not-trigger 큐 동봉 |
| skill-creator | Progressive disclosure | `references/` 분리, 본문 < 500줄 |

자세한 결합 의도와 의도적으로 차용하지 않은 부분은 [`skills/harness-evolver/references/concept-mapping.md`](skills/harness-evolver/references/concept-mapping.md) 참고.

---

## 언제 쓰나

다음 5가지 신호 중 하나라도 보이면 트리거 대상입니다.

| 신호 | 사용자 관점 | 가능한 root cause | 수정 표적 |
| ---- | ---------- | --------------- | ------- |
| 1 | 같은 요청을 두 번 이상 던졌는데 스킬이 안 잡힘 | 트리거 키워드 풀 부족 | `description` |
| 2 | 매번 같은 수동 보정을 반복 | 본문에 해당 케이스 누락 | 스킬 본문 |
| 3 | 동일 에이전트가 반복 실패 | 책임 범위 모호 | `agents/{name}.md` |
| 4 | Phase A → Phase B에서 데이터가 사라짐 | 입출력 스키마 불일치 | 오케스트레이터 Phase 정의 |
| 5 | 결과가 의도와 빗나가고 본문은 MUST/NEVER 결박형 | Why 부재 | 본문 Why-First 재작성 |

> 위 5신호 외에, **프로젝트 전역 규칙(루트 `CLAUDE.md`)이 반복 오작동을 유발**하면 그것도 진단 대상입니다 — 5신호와 별개의 **추가 표적**(`kind: claude-md`, repo-wide 경계 안).

---

## 트리거 방법

`harness-evolver` 는 슬래시 커맨드가 아니라 **자연어 트리거**입니다. 다음 3요소만 자연어에 담으면 잡힙니다.

1. **대상 지목** — `{플러그인명}의 {스킬명}` 또는 `/{커맨드명}`
2. **증상 묘사** — "안 먹어", "같은 실수 반복", "Phase X에서 막힘", "트리거 누락"
3. (선택) **재현 예시** — 사용자가 실제로 쓴 표현 1–2줄

### 시나리오별 예시 프롬프트

#### 예시 1 — frontend-harness `/review` 트리거 누락

```text
frontend-harness 의 /review 가 자꾸 트리거 안 됨.
'코드 한 번 봐줘' 같은 표현으로 부르면 안 잡혀. 두 번째야.
description 손보자.
```

기대 동작:

- Phase 1: 스코프 질문 → "전체 레포"(기본) 선택 → `repo-wide`. 대상 = `plugins/frontend-harness/skills/review/SKILL.md`(SKILL.md = 경계 안), 결함 = 트리거 누락 1건
- Phase 2-2: `target.kind: "description"`, `target.scope_status: "in-boundary"`, `evidence: "'코드 한 번 봐줘' → no skill triggered"`
- Phase 3: `change_kind: "description"`, `trigger_eval_1.json` (should-trigger 8 + should-not-trigger 8) 동봉
- Phase 4: 사용자 승인
- Phase 5: 경계 재확인(SKILL.md → 통과) 후 `description` 패치 적용
- Phase 7: `.claude/evolution-memory/history.jsonl` 1줄 추가 (repo-wide → 레포 전역 이력)

#### 예시 2 — `/orchestrator` Phase 4에서 반복 실패

```text
/orchestrator 돌리니까 Phase 4 Review 단계에서 매번 멈춰.
어디가 문제인지 진단해서 고쳐줘.
```

기대 동작:

- Phase 1: 스코프 질문 → "전체 레포"(기본) 선택 → `repo-wide`. 결함 = `/orchestrator` Phase 4 실패
- Phase 2-2: 표적 = `plugins/frontend-harness/commands/orchestrator.md`(커맨드 파일). repo-wide 패치 경계 밖 → `target.scope_status: "plugin-only"`
- Phase 3: refiner → `change_kind: "scope-escalation"` (patch 미생성)
- Phase 4: "이 결함은 `frontend-harness` 단일 플러그인 평가 모드에서만 고칠 수 있습니다 — 재실행할까요?" 노출
- (사용자 수락 시) Phase 1부터 `plugin: frontend-harness` 로 재진입 → `commands/orchestrator.md` 패치 가능 (plugin 모드는 그 플러그인의 모든 파일이 경계 안)

#### 예시 3 — `/critic` 본문 누락 케이스 (같은 우회책 반복)

```text
/critic 이 보안 우려를 매번 medium 으로만 분류해서
내가 매번 수동으로 high로 올리고 있어. 본문에 박혀야 할 거 같은데.
```

기대 동작:

- Phase 2-2: 5신호 중 #2(반복 우회) → `target.kind: "skill"`, `target.section: "보안 우려 분류 기준"`
- Phase 3: 본문에 분류 기준 절 추가, `rationale` 에 "단일 케이스 추가가 아니라 분류 기준 일반화" 명시 (skill-creator §generalize)

#### 예시 4 — 후속 회차 (이전 결과 기반)

```text
frontend-harness 진화시켜줘. 지난번 회차 결과 바탕으로 보완 부탁.
```

기대 동작:

- Phase 0: `evolution-memory/` 발견 → "신규 회차" 보고
- Phase 1: `recurring-patterns.md` 읽고 `needs_attention` 표적 우선 제안
- (해당 표적이 3회째라면) Phase 1 직후 "구조 재설계 권고(`harness-generator` 재실행)" 옵션 제시 + 사용자 선택 대기

---

## Phase 0 → 7 흐름

| Phase | 사용자가 보는 것 | 내부 동작 |
| ----- | ------------- | -------- |
| 0 | "초기 실행" 또는 "신규 회차" 1줄 보고 | `_workspace/` + `evolution-memory/` 존재 여부 판별 |
| 1 | **스코프 질문(전체 레포/단일 플러그인) → 결함 → trajectory** 한 질문씩 | 스코프 확정 후 `_workspace/{phase}_intake.md` 기록 + 임계치 도달 표적 우선 알림 |
| 2-1 | `trajectory-analyst` 정규화 | raw trace 없으면 사용자 묘사 정규화 (`confidence: low` 마크) |
| 2-2 | **결함 N개 → `failure-diagnostician` N명 병렬 spawn** | 결함별 진단 격리. 모두 끝나면 1회 요약 보고 |
| 3 | 진단별 `skill-refiner` **순차 호출** | patch + (description 수정 시) trigger_eval 동봉 |
| 4 | **사용자 승인 게이트** | 결함별 `accepted / rejected / deferred` |
| 5 | accepted 만 Edit 적용 (적용 직전 스코프 경계 재확인) | 표적이 경계 안 / 본문 < 500줄 / frontmatter 유효 / 트리거 충돌 자체 점검 |
| 6 | (description 수정 시) 트리거 충돌 검증 | `harness-generator` / `skill-creator` / 다른 진입 스킬과 키워드 겹침 |
| 7 | 회차 요약 표 노출 | `evolution-memory/`(repo-wide→`.claude/`, plugin→플러그인 루트) `history.jsonl` + `recurring-patterns.md` 갱신 |
| 8 | (선택) 회귀 평가 권고 | 같은 결함 시나리오로 재실행 안내 — 자동 실행 안 함 |

---

## 안전장치

- **자동 적용 금지** — Phase 5는 반드시 Phase 4 사용자 승인 후. 잘못된 자동 적용이 신뢰를 깨면 진화 자체가 죽은 도구가 됩니다.
- **스코프 패치 경계** — `repo-wide`(기본)는 루트 `CLAUDE.md` + `SKILL.md` 만 패치합니다. `agents`·`hooks`·`commands`·`plugin.json`·플러그인별 `CLAUDE.md` 변경은 사용자가 단일 플러그인 평가를 명시할 때만(`scope-escalation` 으로 안내). 레포 루트 `marketplace.json` 은 어느 스코프에서도 patch 대상이 아님(`out-of-scope` → 사용자 직접 수정). 적용 직전(Phase 5)에도 경계를 재확인합니다.
- **임계치 3회** — 같은 표적이 누적 3회 patch 권고를 받으면 본문 patch를 거절하고 `change_kind: "structural-redesign-required"` 로 보고. `harness-generator` 재실행 권고로 redirect.
- **증거 없는 단정 금지** — `severity: unknown` + `needs_user_input: true` 는 정상적 출력. 추측 patch보다 보류가 안전.
- **결함 1건 = 진단 1건 = 패치 1건** — 묶지 않습니다. 묶으면 어느 결정이 어느 변화에 책임 있는지 추적 불가.

---

## 산출물

### 회차 작업 공간 (`_workspace/`)

회차마다 새로 만듭니다. 새 실행 시 이전 `_workspace/` 는 `_workspace_prev/` 로 이동.

```
_workspace/
  trajectories/{session}.jsonl              # raw trace (있을 때만)
  phase2_trajectory_normalized.md           # trajectory-analyst 산출
  phase2_trajectory_facts.json
  phase2_diagnosis_{N}.json                 # 결함별 진단
  phase2_refinement_{N}.json                # 결함별 patch 계획
  phase2_patch_{N}.md                       # unified-diff 패치
  phase2_trigger_eval_{N}.json              # description 수정 시
  phase2_decisions.json                     # 사용자 승인 결과
  phase2_summary.md                         # 최종 회차 리포트
```

### 영속 메모리 (`evolution-memory/`)

스코프에 따라 위치가 갈립니다 — `repo-wide` 면 레포 전역 이력으로 `.claude/evolution-memory/`, `plugin` 이면 그 플러그인 루트(예: `plugins/frontend-harness/evolution-memory/`). 회차 간 패턴 누적.

```
evolution-memory/
  history.jsonl                             # 회차별 진단/패치/결정 ledger (append-only)
  recurring-patterns.md                     # 표적별 카운트 + needs_attention 섹션
  patches/{date}-{target-slug}.md           # 적용된 패치 사본
  trigger-evals/{date}-{target}.json        # description 회차의 트리거 평가 큐 보존
```

---

## 디렉토리 구조

```
plugins/harness-evolver/
├── .claude-plugin/plugin.json
├── CLAUDE.md                                # 하네스 포인터 + 변경 이력
├── README.md                                # (본 문서)
├── agents/                                  # 모두 model: "opus"
│   ├── trajectory-analyst.md                # 사실/해석 분리, payload 적재 금지
│   ├── failure-diagnostician.md             # 5신호 → 5표적 매핑, evidence 인용 필수
│   ├── skill-refiner.md                     # skill-creator 4원칙, patch만 생성(자동 적용 금지)
│   └── evolution-historian.md               # evolution-memory/ 큐레이션 + 반복 패턴 nudge
├── skills/
│   ├── harness-evolver/                     # 진입점 오케스트레이터
│   │   ├── SKILL.md
│   │   └── references/concept-mapping.md    # Evolver 루프 ↔ skill-creator 결합 의도
│   ├── trajectory-capture/                  # 궤적 정규화 방법론
│   ├── failure-diagnosis/                   # 결함 진단 루브릭 (5신호 → 5표적)
│   └── eval-driven-refinement/              # patch + 트리거/회귀 평가 생성 방법론
└── evals/                                   # 평가 / 테스트 자료
    ├── trigger-eval.json                    # 트리거 평가 큐 24건 (harness-evolver 7 + 타 스킬 near-miss 10 + 무관 7)
    ├── evals.json                           # Phase dry-run 시나리오 5건 + assertion 18건
    └── dry-run-report.md                    # dry-run 결과 (v0.2.0: 5시나리오 18/18 assertion PASS)
```

---

## 책임 경계 (다른 메타 플러그인과의 분리)

| 도구 | 영역 | 트리거 |
| ---- | ---- | ----- |
| `harness-generator` | **신규** 하네스(에이전트팀 + 스킬 + 오케스트레이터) 자동 생성 | "하네스 만들어줘", "워크플로우 자동화", "오케스트레이터 작성" |
| `skill-creator` | **단발** 스킬 작성/평가/description 최적화 | "skill from scratch", "evals", "benchmark" |
| `harness-evolver` (본 플러그인) | **이미 사용 중인** 하네스의 문제 진단·개선 | "하네스 고도화", "오케스트레이터 개선", "스킬이 안 먹는다", "재실행해도 같은 실수" |

같은 표적에 본 플러그인이 3회 누적 patch 권고를 내면 자동으로 `harness-generator` 재실행 권고로 redirect합니다 — 본문 패치로 못 고치는 구조 문제라는 신호입니다.

---

## 평가 / 테스트 자료

- `evals/trigger-eval.json` — 24건의 자연어 쿼리에 대한 expected 트리거 표(harness-evolver 7 / 타 스킬 near-miss 10 / 무관 7). skill-creator §"description optimization" 의 should-trigger / should-not-trigger 패턴을 따르며, "평가/점검" 표면 키워드 과잉 트리거를 막는 near-miss 가드를 포함.
- `evals/evals.json` — 5개 시나리오(정상/임계치/증거 부족/scope-escalation/plugin 모드)의 Phase 흐름 예상 경로 + assertion 18건.
- `evals/dry-run-report.md` — `SKILL.md` 본문과 시나리오를 매핑한 dry-run 결과(v0.2.0). 평가 스코프 도입 반영 — 5개 시나리오(정상/임계치/증거 부족/scope-escalation/plugin 모드) **18/18 assertion PASS**.

---

## License

이 플러그인은 본 마켓플레이스의 라이선스(MIT)를 따릅니다.
