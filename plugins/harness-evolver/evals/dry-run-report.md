# harness-evolver Phase 시퀀스 dry-run 결과

본 보고서는 `evals/evals.json` 의 3개 시나리오를 `skills/harness-evolver/SKILL.md` 본문에 매핑해 Phase 흐름과 assertion 통과 여부를 추적한 결과다. 실제 트리거/실행은 사용자 세션에서 검증되어야 하지만, 본 dry-run은 본문 자체의 논리 정합성을 확인한다.

## 시나리오 #1 — 트리거-누락-단일-결함

**입력:** "어제 PR 리뷰 받을 때 doc-harness의 /branch-doc-orchestrator 가 '브랜치 문서 만들어줘' 라고 했는데 두 번이나 트리거 안 됐어. description부터 손보고 싶은데"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | `_workspace/` 없음 + `evolution-memory/` 없음 → 초기 실행 | 1줄 보고 |
| 1 | 인터뷰 1회로 3가지 확보 | 대상 = `plugins/doc-harness/skills/branch-doc-orchestrator/SKILL.md`, 결함 1건, trajectory 없음 (사용자 묘사) |
| 2-1 | `trajectory-analyst` 1회 — 사용자 묘사 경로 | `trajectory-capture` §B에 따라 `confidence: low` + `~` 접두로 정규화 |
| 2-2 | 결함 1건 → `failure-diagnostician` 1명 spawn | `failure-diagnosis` 신호 1(트리거 누락) → 표적 `description`, evidence 1건(사용자 인용) |
| 3 | `skill-refiner` 1회 순차 호출 | `change_kind: description`, `trigger_eval_1.json` 8/10 동봉, `risks` 1건 |
| 4 | 사용자 게이트 | `accepted` 가정 |
| 5 | Edit으로 patch 적용 + 자체 점검 | 본문 < 500줄 / frontmatter 유효 / 트리거 충돌 없음 |
| 6 | description 수정이므로 트리거 충돌 검증 | `harness-generator` / `skill-creator` / 다른 진입 스킬과 키워드 충돌 점검 |
| 7 | `evolution-historian` 1회 | `plugins/doc-harness/evolution-memory/` 신규 생성, `history.jsonl` +1, `recurring-patterns.md` 카운트 1 |

**Assertion 결과:**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| single-diagnosis | PASS | Phase 2-2에서 결함 1건 → 진단 1건 spawn (본문 "결함 1건 = 진단 1건 = 패치 1건" 원칙) |
| evidence-required | PASS | `failure-diagnosis` 본문 "모든 진단은 trajectory의 step 번호 1개 이상을 인용해야 한다" |
| trigger-eval-bundled | PASS | `eval-driven-refinement` 본문 "description 수정 시 트리거 평가 큐 동봉 필수" |
| no-auto-apply | PASS | Phase 5는 Phase 4 사용자 게이트 후 — 본문에 명시 ("자동 적용 금지") |

---

## 시나리오 #2 — 임계치-도달-구조-재설계-권고

**입력:** "frontend-harness의 review 스킬이 또 안 먹어. 이미 세 번째인데 본문 말고 구조를 봐야 할 거 같아"

**전제:** `plugins/frontend-harness/evolution-memory/recurring-patterns.md` 의 `needs_attention` 에 동일 표적 3회 누적

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | `_workspace/` 없음, `evolution-memory/` 있음 → 신규 회차 | 1줄 보고 |
| 1 (조기 중단) | "`evolution-memory/recurring-patterns.md` 의 `needs_attention` 섹션을 읽어 같은 표적이 누적 임계치(≥3) 도달했다면 사용자에게 먼저 알리고 '본문 패치 대신 구조 재설계를 권고합니다' 라고 옵션을 제시한다." | 사용자에게 옵션 제시 |
| (사용자 선택) | "구조 재설계" 선택 시 | `harness-generator` 호출 안내 후 종료. Phase 2 진입 안 함 |

**Assertion 결과:**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| early-bail | PASS | Phase 1 본문 마지막 단락에 needs_attention 임계치 감지 → 옵션 제시 명시. Phase 2-2 spawn 전 게이트 발생 |
| redirect-suggestion | PASS | 본문에 "구조 재설계(`harness-generator` 재실행)를 권고" 직접 인용 |

---

## 시나리오 #3 — 증거-부족-skip

**입력:** "그냥 뭔가 느낌이 안 좋아. 우리 하네스 좀 고쳐줘"

| Phase | 본문 매핑 | 동작 |
| ----- | -------- | ---- |
| 0 | 초기 실행 | 1줄 보고 |
| 1 | 인터뷰 (대상 식별 단계에서 사용자가 결함 구체화 못함) | 대상은 디렉토리 스캔으로 후보 제시 받아 1개 선택. 결함 묘사는 빈약("느낌이 안 좋다") |
| 2-1 | `trajectory-analyst` — 빈약한 입력 | `trajectory-capture` §"빈 표 출력" — `output_ref: null` 1줄로 사실만 기록 |
| 2-2 | `failure-diagnostician` 1명 spawn | `failure-diagnosis` 본문 "trajectory 표가 비었거나 step이 너무 적어 근거를 못 잡으면 `root_cause: 'insufficient evidence'`, `severity: unknown`, `needs_user_input: true` 로 응답하고 종료" |
| 3 | `skill-refiner` 1회 호출 | `eval-driven-refinement` 본문 "진단에서 `severity: unknown` 또는 `needs_user_input: true` 면 patch를 만들지 말고 `change_kind: 'skip'`, `rationale: 'diagnosis lacks evidence'` 로 출력" |
| 4 | 사용자 게이트 | 사용자에게 추가 증거 요청. `decision: deferred` 또는 결정 없이 회차 마감 |
| 5–6 | skip | patch 없음 → 적용/충돌 검증 모두 skip |
| 7 | `evolution-historian` 1회 | 본문 "사용자 결정이 누락된 회차는 `decision: 'unknown'` 으로 기록하되 카운트에는 포함시키지 않는다" — 패턴 집계 오염 방지 |

**Assertion 결과:**

| Assertion | 결과 | 근거 |
| --------- | ---- | ---- |
| no-fake-patch | PASS | `eval-driven-refinement` §"거절/보류 출력" — `change_kind: skip` 명시 |
| needs-user-input | PASS | `failure-diagnosis` 본문에 `needs_user_input: true` 출력 필드 명시, Phase 4에서 사용자에게 노출 |

---

## 잠재 gap (개선 여지)

dry-run 중 발견한 명시적이지 않은 부분:

1. **시나리오 #3 Phase 1에서 사용자가 결함을 구체화 못할 때의 명시적 처리** — 본문은 자연스럽게 다음 Phase로 흘러가 진단가가 `unknown` 으로 처리하지만, "Phase 1에서 결함 묘사가 비면 Phase 2로 그대로 보내 진단가가 unknown 처리" 라는 명시적 가이드가 없음. 현재 본문도 동작은 하지만, 향후 회차에서 사용자가 회피 우회를 만들 수 있어 추적 대상.
2. **시나리오 #1 trajectory-analyst 호출 시 사용자 묘사가 1–2문장으로 매우 짧을 때** — `trajectory-capture` §B(사용자 자연어 묘사)는 정규화 규칙을 정의하지만, 묘사가 1행에 그칠 때 step 번호 부여 규칙이 명시적이지 않음. 현재는 step 1 한 줄로 처리하면 되지만 향후 명시화 검토.

위 2건은 본 회차 첫 진화 대상으로 적합 — `evolution-memory/` 에 첫 reading 으로 누적되어도 OK.

## 최종 판정

- **8/8 assertion PASS** (모든 시나리오)
- **본문 흐름 정합성:** 3개 시나리오 모두 SKILL.md 본문 + 보조 스킬(trajectory-capture, failure-diagnosis, eval-driven-refinement) 본문으로 처리 가능
- **잠재 gap 2건 식별:** 첫 진화 회차 대상으로 적합
