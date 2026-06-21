---
name: pareto-refinement
description: full-trace 기반 진단 결과를 Pareto frontier를 후퇴시키지 않는 비파괴적 패치로 변환하는 보조 방법론. 진단 1건당 patch.md(unified-diff)와 refinement_{N}.json을 생성하되 자동 적용은 금지한다. additive-first(동작하던 트리거·제어흐름·스키마를 수정하기 전 비파괴 추가·완화 우선) → compose(검증된 직교 승리만 합성) → transfer(experience-store 과거 회차 교훈을 raw trace 재확인 후 적용) 순서를 따른다. description 수정 시 should-trigger/should-not-trigger 8~10개씩 trigger_eval을 동봉하고, 4축 Pareto 좌표로 비후퇴를 자가 점검한다. 같은 표적 3회 누적 시 본문 patch를 거절하고 structural-redesign-required를 권고한다. pareto-refiner 에이전트가 진단별 순차로 호출한다.
---

# Pareto Refinement — 비후퇴 patch 생성 방법론

## 왜 이 스킬이 필요한가 (Why-first)

진단(diagnosis)은 "어디가 왜 틀렸나"를 말할 뿐, "어떻게 고치면 frontier가 후퇴하지 않나"는 답하지 않는다. 순진한 개선은 한 결함을 고치면서 본문 길이를 부풀리고(rule-body-cost↑), 다른 트리거를 깨뜨리고(trigger-precision↓), 좁은 우회책으로 hold-out에서 무너진다(generalization↓). 이 스킬은 proposer(pareto-refiner)가 patch를 만들 때 **4축 어느 것도 후퇴시키지 않도록** 강제하는 절차다.

근거: Meta-Harness 논문의 causal reasoning over prior failures. regression이 반복되면 destructive 수정을 멈추고 additive로 전환한다. 직교 승리는 compose하고, 과거 run의 교훈은 raw trace 재확인 후 transfer한다. 이 세 동작이 frontier를 단조 전진시킨다.

이 스킬은 **patch만 만든다.** 적용은 사용자 승인 게이트(Phase 6)를 통과한 뒤 오케스트레이터가 한다. proposer가 직접 Edit/Write하면 안 된다 — eval은 proposer 밖에서 돌아야 confound가 안 생긴다.

## skill-creator 4원칙 재사용 (단, bundle 재정의)

모든 patch는 아래 4원칙을 통과해야 한다.

| 원칙 | 의미 | 점검 질문 |
|------|------|-----------|
| **generalize** | 좁은 우회책이 아니라 결함 모드 자체를 닫는다 | 이 patch가 hold-out 시나리오에서도 같은 실패를 막는가? 특정 입력 한 건만 패치하는 건 아닌가? |
| **lean prompt** | 본문은 최소·고신호여야 한다(*최소 ≠ 짧게* — 정합 이득 있는 사실·Why는 줄여 없애지 않는다). 추가 줄·결박은 정합 이득이 있을 때만 | 줄 수가 늘었다면 그만큼 behavior-alignment 이득이 있는가? Why 없는 MUST/NEVER를 더하지 않았는가? 본문을 줄이며 고신호 사실·Why를 잃지 않았는가? |
| **why-first** | 규칙보다 이유를 먼저 쓴다. 근거는 trace의 step/파일 경로 인용 | rationale이 "왜 이게 일반화 해결책인가"를 trace 증거로 설명하는가? |
| **bundle(재정의)** | **검증된 직교 패치만 compose한다** | 합치려는 두 patch가 서로 다른 결함 모드를 건드리며, 각각 단독 검증을 통과했는가? 같은 줄을 다투지 않는가? |

> bundle 주의: 일반 skill-creator의 bundle은 "관련 자료를 묶어라"지만, 여기선 **검증 안 된 패치 합성 금지**로 좁힌다. 두 patch가 같은 파일·같은 영역을 건드리거나 한쪽이 미검증이면 compose하지 말고 순차로 분리해 각각 게이트에 올린다.

## 핵심 전략 3단계 (순서 고정)

### 1단계 additive-first — 비파괴 우선

동작하던 트리거 문구·제어 흐름·스키마를 **수정하기 전에** 비파괴적 추가·완화를 먼저 시도한다. 특히 regression이 반복되는 표적이면 destructive edit을 기본 거절한다.

- 트리거 결함 → 기존 should-trigger 문구를 바꾸지 말고 **누락 케이스를 추가**하거나 should-not-trigger를 보강한다.
- 제어 흐름 결함 → 기존 Phase 순서를 갈아엎지 말고 **가드/폴백 분기를 덧댄다**.
- 스키마 결함 → 필드를 제거·개명하지 말고 **optional 필드 추가** 또는 기본값 명시로 완화한다.

additive로 결함을 닫을 수 없다고 trace 증거로 입증될 때만 destructive 수정을 제안하되, change_kind와 risks에 그 사실을 명시한다.

### 2단계 compose — 직교 승리만 합성

서로 다른 결함 모드의 patch 중, **각각 단독으로 검증(Phase 5 lightweight validation)을 통과한** 것만 합성한다. 직교성 판정: 두 patch가 (a) 다른 파일이거나, (b) 같은 파일이라도 겹치지 않는 영역이고, (c) 한쪽의 변경이 다른 쪽의 가정을 깨지 않는다. 셋 중 하나라도 불확실하면 compose하지 않는다.

### 3단계 transfer — 과거 교훈 이식 (raw trace 재확인 후)

experience-store(`recurring-patterns.md`, 과거 `traces/`)에서 같은 표적의 이전 교훈을 가져올 때, **요약(index/recurring)만 보고 옮기지 않는다.** 반드시 해당 회차의 `traces/*.jsonl` 원본을 grep/cat로 재확인한 뒤 적용한다. 요약은 navigation 포인터일 뿐 — 요약만 믿고 transfer하면 Table 3의 Scores+Summary 퇴화를 답습한다.

### 연구 근거 보강 — P1·P2·P4 (operative)

1차 출처에 근거해 patch 설계에 적용한다(출처는 항목별 괄호에 인라인 표기).

- **P1 중복 제거 = 비후퇴 승리.** 진단이 '중복·잉여 규칙(제품 기본 동작·모델 기본기능과 겹치는 over-prompting)'을 지목하면, 제거 patch는 `rule-body-cost`↓ + `behavior-alignment` 유지 → **Pareto 비후퇴 승리**다. 삭제도 자동 적용하지 않고 게이트 경유. (근거: context engineering 최소·고신호; '중복 제거' 프레이밍은 **간접 도출**)
- **P2 안전장치 불가침.** 승인 게이트·Pareto 비후퇴·full-trace·검증 Phase·경계 재확인을 **삭제·약화하는 patch는 만들지 않는다** — trace 근거가 강해도 기본 거절(deferred로 사용자 확인). (근거: 자기개선 효능 한계 arXiv 2303.11366 / 2507.19457)
- **P4 반복 절차 → Skill.** 같은 표적이 ≥3 누적(needs_attention)이고 내용이 '절차'면, 본문 patch 대신 `structural-redesign-required`와 함께 **Skill 추출**을 권고한다(사실은 지침에·절차는 Skill에). (근거: Agent Skills best-practices)

## 4축 Pareto 좌표 + 비후퇴 자가 점검

모든 patch는 아래 4축 좌표를 산출하고 직전 frontier(`pareto.json`)와 비교한다.

| 축 | 방향 | 측정 |
|----|------|------|
| **behavior-alignment** | max | 패치 후 하네스가 사용자 의도 동작을 내는가 (진단된 결함이 닫히는가) |
| **rule-body-cost** | min | 본문 줄 수 증가 + 새로 추가된 MUST/NEVER 결박 수 |
| **trigger-precision** | max | should-trigger/should-not 정확도 (trigger_eval 통과율) |
| **generalization** | max | hold-out/유사 시나리오 견고성 (좁은 우회책이면 하락) |

**비후퇴 규칙:** 채택 후보는 **어느 축도 직전 frontier를 후퇴시키지 않아야** 한다. 본문 길이·결박 수가 늘었는데(rule-body-cost↑) behavior-alignment 이득이 없으면 그 patch는 self-reject 후보로 표시한다(refinement json의 `pareto_coords.non_regression: false`). 한 축 이득이 다른 축 손실로 상쇄되면 additive 재설계로 되돌린다.

## description 수정 시 — trigger_eval 동봉 (필수)

description(트리거 표면)을 건드리는 patch는 **검증 없이 흔들면 안 된다.** should-trigger 8~10개, should-not-trigger 8~10개를 trigger_eval로 동봉하고 `trigger-eval.json`에 적재한다. 행위 기준으로 작성하며(플러그인명 거명 금지), 결함이 드러난 실제 trace 케이스를 should-trigger에 최소 1건 포함한다. trigger_eval 없는 description patch는 Phase 5에서 탈락시킨다.

## 3회 누적 → 구조 재설계 권고

같은 표적(target_path)에 본문 patch가 **3회 누적**되면(`recurring-patterns.md`의 카운트 ≥3, needs_attention), 4번째 본문 patch를 **거절**하고 `change_kind: "structural-redesign-required"`로 보고한다. 본문을 더 만지는 건 결함 모드가 본문 레벨이 아니라 구조 레벨임을 뜻한다 — 표적의 분할·재배치·상위 오케스트레이터 변경을 권고한다.

## 패치 경계 (scope)

- **repo-wide(기본):** patch 표적 = 루트 CLAUDE.md + 임의 SKILL.md 만. 그 밖(agents/·commands/·hooks/·plugin.json·플러그인별 CLAUDE.md)은 patch 없이 `change_kind: "scope-escalation"`(plugin 모드 재실행 권고)으로 보고한다. 레포 루트 메타(.claude-plugin/marketplace.json 등)는 `change_kind: "blocked"`(사용자 직접).
- **plugin(opt-in):** 지목 플러그인의 모든 파일이 경계 안.

## 산출물 (자동 적용 금지)

진단 1건당 두 파일을 만든다. **둘 다 patch일 뿐, 절대 직접 적용하지 않는다.**

### refinement_{N}.json 스키마

```json
{
  "diagnosis_id": "diag-003",
  "target_path": "plugins/<target-plugin>/skills/a11y/SKILL.md",
  "change_kind": "additive | destructive | compose | transfer | scope-escalation | blocked | structural-redesign-required",
  "summary": "should-not-trigger에 '단발 컴포넌트 작성' 케이스 1건 추가 (비파괴)",
  "rationale": "step 12에서 a11y 스킬이 신규 컴포넌트 작성 요청에 오발화. 기존 트리거 문구를 바꾸면 정상 케이스가 깨지므로(trace step 7~9), should-not-trigger 추가만으로 결함 모드를 닫는다. 특정 입력이 아닌 '작성 의도' 일반 패턴을 막으므로 hold-out에도 일반화된다.",
  "patch_ref": ".claude/experience-store/patches/2026-06-03-a11y-skill.md",
  "pareto_coords": {
    "behavior_alignment": "+1 (오발화 결함 닫힘)",
    "rule_body_cost": "+1 line, +0 MUST/NEVER",
    "trigger_precision": "+ (trigger_eval 18/18 통과)",
    "generalization": "유지 (작성-의도 일반 패턴)",
    "non_regression": true
  },
  "trigger_eval_ref": ".claude/experience-store/{run}/{candidate}/traces/trigger-eval.jsonl#diag-003",
  "risks": [
    "should-not 추가가 경계 케이스(작성 직후 점검 요청)를 과차단할 수 있음 — trigger_eval에 should-trigger로 1건 넣어 감시"
  ],
  "regression_eval_suggestion": "다음 회차에 '컴포넌트 작성 후 a11y 점검' 발화가 여전히 should-trigger인지 재확인"
}
```

- `change_kind`가 `scope-escalation`/`blocked`/`structural-redesign-required`면 `patch_ref`는 비우고 `rationale`에 사유와 권고를 적는다.
- `trigger_eval_ref`는 description을 건드릴 때만 채운다(그 외 생략).

### patch.md (unified-diff + 위아래 3줄)

```diff
# diag-003 — a11y/SKILL.md should-not-trigger 추가 (additive)
# change_kind: additive | non_regression: true

--- a/plugins/<target-plugin>/skills/a11y/SKILL.md
+++ b/plugins/<target-plugin>/skills/a11y/SKILL.md
@@ -3,6 +3,7 @@
 should-not-trigger:
   - "이 함수 리팩터링해줘"
   - "테스트 깨진 거 고쳐줘"
+  - "새 컴포넌트 처음부터 작성해줘"  # 작성 의도는 점검 스킬 트리거 아님 (diag-003, trace step 12)
   - "커밋 메시지 써줘"
 ...
```

- diff hunk는 변경 라인 **위아래 3줄 context**를 반드시 포함한다 — 적용 위치를 사람이 검증할 수 있게.
- 헤더 주석에 `diag-id`, `change_kind`, `non_regression`을 명시한다.
- patch 사본은 `{store-root}/patches/{date}-{target-slug}.md`에도 적재한다(experience-historian가 ledger와 대조).

## 흔한 실패 (이렇게 하지 마라)

- **요약만 보고 transfer** → 반드시 과거 `traces/*.jsonl` 원본 재확인 후 이식.
- **trigger_eval 없이 description 수정** → 트리거 표면을 검증 없이 흔드는 것은 금지, Phase 5 탈락.
- **본문 부풀리기** → rule-body-cost↑ + behavior-alignment 이득 없음 = self-reject.
- **미검증 패치 compose** → 직교성·단독검증 미통과 시 순차 분리.
- **destructive 우선** → additive로 닫을 수 있으면 additive. regression 반복 표적은 특히.
- **proposer가 직접 적용** → patch만 생성, 적용은 승인 게이트 후 오케스트레이터.
- **3회 누적 표적에 4번째 본문 patch** → structural-redesign-required로 거절.

## 재호출 가이드

pareto-refiner 에이전트가 진단별 **순차**로 이 방법론을 적용한다. 직전 patch 결과(채택/탈락, Pareto 좌표)를 다음 호출 입력에 노출해, compose 직교성 판정과 누적 카운트를 이어가게 한다. 동일 파일 다중 patch는 적용 시 묶이므로(Phase 7), 생성 단계에서 겹치는 영역이 없는지 미리 점검한다.
