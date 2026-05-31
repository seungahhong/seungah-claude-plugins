# harness-evolver Phase 시퀀스 dry-run 결과 (v0.2.0)

본 보고서는 `evals/evals.json` 의 5개 시나리오를 `skills/harness-evolver/SKILL.md` 본문(+ 보조 스킬/에이전트)에 매핑해 Phase 흐름과 assertion 통과 여부를 추적한 결과다. 실제 트리거/실행은 사용자 세션에서 검증되어야 하지만, 본 dry-run은 본문 자체의 논리 정합성을 확인한다.

> **버전:** v0.2.0 (평가 스코프 도입 — repo-wide 기본 / plugin opt-in). v0.1.0 스냅샷(3시나리오 8/8)을 갱신해 시나리오 #1의 스코프 반영 + 신규 #4(scope-escalation)·#5(plugin 모드)를 추가했다.

## 시나리오 #1 — 트리거-누락-단일-결함 (repo-wide)

**입력:** "어제 PR 리뷰 받을 때 doc-harness의 /branch-doc-orchestrator 가 '브랜치 문서 만들어줘' 라고 했는데 두 번이나 트리거 안 됐어. description부터 손보고 싶은데"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | `_workspace/` 없음 + `evolution-memory/` 없음 → 초기 실행 | 1줄 보고 |
| 1 | 스코프 질문(step 0) → repo-wide(기본) 선택. 결함/​trajectory 확보 | 대상 = `plugins/doc-harness/skills/branch-doc-orchestrator/SKILL.md`(SKILL.md=경계 안), 결함 1건, trajectory 없음(사용자 묘사) |
| 2-1 | `trajectory-analyst` 1회 — 사용자 묘사 경로 | `trajectory-capture` §B에 따라 `confidence: low` + `~` 접두로 정규화 |
| 2-2 | 결함 1건 → `failure-diagnostician` 1명 spawn (스코프 주입) | 신호 1(트리거 누락) → `target.kind: description`, `scope_status: in-boundary`, evidence 1건(사용자 인용) |
| 3 | `skill-refiner` 1회 순차 호출 (스코프 주입) | `change_kind: description`, `trigger_eval_1.json` 8/10 동봉, `risks` 1건 |
| 4 | 사용자 게이트 | `accepted` 가정 |
| 5 | 적용 직전 경계 재확인(SKILL.md→통과) 후 Edit 적용 | 표적이 경계 안 / 본문 < 500줄 / frontmatter 유효 / 트리거 충돌 없음 |
| 6 | description 수정이므로 트리거 충돌 검증 | `harness-generator` / `skill-creator` / 다른 진입 스킬과 키워드 충돌 점검 |
| 7 | `evolution-historian` 1회 (스코프 주입) | repo-wide → `.claude/evolution-memory/` 신규 생성, `history.jsonl` +1, `recurring-patterns.md` 카운트 1 |

**Assertion 결과 (7/7):**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| scope-resolved | PASS | Phase 1 step 0이 "매 회차 1회 명시 질문"으로 스코프 확정(SKILL.md Phase 1) |
| single-diagnosis | PASS | "결함 1건 = 진단 1건 = 패치 1건" 원칙 → 진단 1건 spawn |
| evidence-required | PASS | `failure-diagnosis` "모든 진단은 trajectory의 step 번호 1개 이상 인용" |
| in-boundary | PASS | SKILL.md 표적 → `scope_status: in-boundary`, patch 생성(scope 준수 체크) |
| trigger-eval-bundled | PASS | `eval-driven-refinement` "description 수정 시 트리거 평가 큐 동봉 필수" |
| no-auto-apply | PASS | Phase 5는 Phase 4 사용자 게이트 후 — "자동 적용 금지" |
| memory-location | PASS | repo-wide → Phase 7 누적 대상 `.claude/evolution-memory/` (산출물 배치 규약 + 역사가 분기) |

---

## 시나리오 #2 — 임계치-도달-구조-재설계-권고 (repo-wide)

**입력:** "frontend-harness의 review 스킬이 또 안 먹어. 이미 세 번째인데 본문 말고 구조를 봐야 할 거 같아"

**전제:** 스코프 = repo-wide(기본)이므로 `.claude/evolution-memory/recurring-patterns.md` 의 `needs_attention` 에 `plugins/frontend-harness/skills/review/SKILL.md` 가 3회 누적

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | `_workspace/` 없음, `evolution-memory/` 있음 → 신규 회차 | 1줄 보고 |
| 1 | 스코프 질문 → repo-wide. 스코프에 맞는 `.claude/evolution-memory/recurring-patterns.md` 읽음 → 임계치(≥3) 감지 → 옵션 제시 후 중단 | 사용자에게 "본문 패치 vs 구조 재설계" 옵션 제시 |
| (사용자 선택) | "구조 재설계" 선택 시 | `harness-generator` 호출 안내 후 종료. Phase 2 진입 안 함 |

**Assertion 결과 (2/2):**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| early-bail | PASS | Phase 1 마지막 단락 — needs_attention 임계치(≥3) 감지 시 옵션 제시. Phase 2-2 spawn 전 게이트 |
| redirect-suggestion | PASS | "구조 재설계(`harness-generator` 재실행)를 권고" 본문 직접 인용 |

---

## 시나리오 #3 — 증거-부족-skip

**입력:** "그냥 뭔가 느낌이 안 좋아. 우리 하네스 좀 고쳐줘"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | 초기 실행 | 1줄 보고 |
| 1 | 스코프 질문 → 애매 → repo-wide(기본). 대상/결함 묘사 빈약 | 대상은 스캔 후보 제시, 결함 묘사 "느낌이 안 좋다" |
| 2-1 | `trajectory-analyst` — 빈약한 입력 | `trajectory-capture` "빈 표 출력" — `output_ref: null` 1줄 |
| 2-2 | `failure-diagnostician` 1명 spawn | "근거 못 잡으면 `root_cause: insufficient evidence`, `severity: unknown`, `needs_user_input: true`" |
| 3 | `skill-refiner` 1회 호출 | "`severity: unknown` 또는 `needs_user_input: true` 면 patch 없이 `change_kind: skip`" |
| 4 | 사용자 게이트 | 추가 증거 요청. `decision: deferred` 또는 결정 없이 마감 |
| 5–6 | skip | patch 없음 → 적용/충돌 검증 skip |
| 7 | `evolution-historian` 1회 | "사용자 결정 누락 회차는 `decision: unknown`, 카운트 미포함" |

**Assertion 결과 (2/2):**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| no-fake-patch | PASS | `eval-driven-refinement` §"거절/보류 출력" — `change_kind: skip` |
| needs-user-input | PASS | `failure-diagnosis` `needs_user_input: true` 출력 필드, Phase 4 노출 |

---

## 시나리오 #4 — repo-wide-경계밖-scope-escalation

**입력:** "전체 점검해줘. /orchestrator 가 Phase 4 Review 단계에서 매번 멈춰"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 1 | 스코프 질문 → repo-wide(기본) | 결함 = `/orchestrator` Phase 4 실패 |
| 2-2 | 진단(스코프 주입) | 표적 = `plugins/frontend-harness/commands/orchestrator.md`(커맨드). `target.kind: orchestrator`, `scope_status: plugin-only` (repo-wide 경계 밖) |
| 3 | `skill-refiner` (스코프 준수 선체크) | `change_kind: scope-escalation`, patch 미생성, 표적 경로 보존 |
| 4 | 사용자 게이트 | "frontend-harness 단일 플러그인 평가 모드 재실행?" 선택지 노출 |
| (수락 시) | Phase 1 step 0 생략 + 보존 경로에서 plugin 자동 확정 | `plugin: frontend-harness` 로 재진입 → `commands/orchestrator.md` 패치 가능 |

**Assertion 결과 (4/4):**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| out-of-boundary-flagged | PASS | `failure-diagnosis`/diagnostician 경계표 — `commands/*.md` 오케스트레이터 → `scope_status: plugin-only` |
| no-patch-out-of-scope | PASS | `eval-driven-refinement` "scope_status: plugin-only → patch 없이 `scope-escalation`"; skill-refiner Error Handling |
| escalation-surfaced | PASS | Phase 4 — scope-escalation 항목을 "plugin 모드 재실행" 선택지로 노출 |
| no-boundary-bypass | PASS | `failure-diagnosis` 흔한 실패 "스코프 경계 왜곡"; diagnostician "패치 가능 표적으로 억지 매핑 안 함" |

---

## 시나리오 #5 — plugin-모드-단일-플러그인-심층

**입력:** "doc-harness 플러그인 전체 평가해줘. 에이전트들 사이에 스키마가 자꾸 안 맞아"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 1 | 스코프 질문 → 단일 플러그인 + `doc-harness` 확정 → `plugin: doc-harness` | 대상 = `plugins/doc-harness/` 전체 |
| 2-2 | 진단(스코프 주입) | 표적 `agents/*.md`/`plugin.json`/`SKILL.md` 모두 `scope_status: in-boundary` (그 플러그인 내부) |
| 3–5 | 경계 안이므로 정상 patch | `agents/*.md` 도 수정 가능, Phase 5 경계 재확인(플러그인 디렉토리 안→통과) |
| 7 | `evolution-historian` (스코프 주입) | plugin → `plugins/doc-harness/evolution-memory/` 누적 |

**Assertion 결과 (3/3):**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| plugin-scope-confirmed | PASS | Phase 1 step 0 — plugin 선택 + 대상 플러그인 확정 |
| agents-in-boundary | PASS | 평가 스코프 표 — plugin 스코프는 그 플러그인의 모든 파일이 경계 안 |
| plugin-local-memory | PASS | Phase 7 분기 — plugin → `plugins/doc-harness/evolution-memory/` (역사가 Input Protocol) |

---

## 최종 판정

- **18/18 assertion PASS** (5개 시나리오: 정상/임계치/증거 부족/scope-escalation/plugin 모드)
- **본문 흐름 정합성:** 5개 시나리오 모두 SKILL.md 본문 + 보조 스킬(trajectory-capture, failure-diagnosis, eval-driven-refinement) + 에이전트 정의로 처리 가능
- **스코프 정합성:** repo-wide 패치 경계(루트 CLAUDE.md + SKILL.md), 경계 밖 표적의 scope-escalation, evolution-memory 위치 분기(.claude/ vs 플러그인 루트)가 진단(diagnostician)·개선(skill-refiner)·메모리(historian) 전 계층에서 일관
