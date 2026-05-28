---
name: eval-driven-refinement
description: 하네스 진화 회차에서 진단된 결함 1건에 대해 skill-creator의 eval-driven iteration 원칙을 적용해 patch와 트리거/회귀 평가를 함께 생성하는 방법론 스킬. 주로 harness-evolver Phase 3에서 skill-refiner 에이전트가 따른다. 좁은 패치 대신 일반화된 원리 수정을 만들고, description 변경 시 should-trigger/should-not-trigger 큐를 동봉한다. 사용자가 "하네스 스킬 patch 만들어", "진화 patch 작성", "이 진단으로 refinement 만들어" 등을 말할 때 트리거된다. 단순 단일 스킬 작성·평가는 skill-creator를 사용하고, 본 스킬은 하네스 진화 컨텍스트 한정.
---

# Eval-Driven Refinement — 진단 1건 → 패치 1건 생성 방법론

`skill-refiner` 에이전트가 본 스킬을 따른다. `harness-evolver` Phase 3 에서 진단 1건당 1회 호출된다.

## 핵심 원칙 (skill-creator 차용)

skill-creator의 §"How to think about improvements" 4원칙을 그대로 따른다 — 다만 대상이 **하네스 정의 파일들**이라는 점만 다르다.

### 1. Generalize from the feedback

좁은 케이스 한 개를 위한 patch는 다른 케이스를 깬다. 결함의 일반 원리를 본문에 박아야 한다.

**예시:** "사용자가 '리뷰 봐줘' 표현으로 트리거 못 함" → description에 그 표현 하나만 추가하지 말고, "캐주얼 한국어 요청 표현" 클래스를 식별해 그 클래스 전체를 추가 검토.

### 2. Keep the prompt lean

추가 전에 같은 효과를 내는 기존 줄을 더 명료히 고칠 수 있는지 검토. MUST/NEVER 결박형 추가는 가장 마지막 수단.

### 3. Explain the why

규칙만 박지 않고 **이유**를 박는다. LLM은 이유를 알면 엣지 케이스에서 옳게 판단한다. ALWAYS/NEVER 대문자 남용은 yellow flag.

### 4. Bundle repeated work

trajectory에서 동일 헬퍼/접근이 3회 이상 재현되면 본문이 아닌 `scripts/` 로 묶기 권고. 본문 추가가 아니라 `change_kind: "new-script"` 를 사용.

## 표적별 patch 가이드

### A. description 수정

- 키워드 추가 시 캐주얼/공식 양쪽 톤 포함.
- 후속 작업 키워드 ("다시", "재실행", "보완", "수정") 포함 검토.
- 트리거 충돌 가능성을 명시 — 인접 스킬과 키워드 겹침 발견 시 patch를 보류하고 사유 보고.
- **트리거 평가 큐 동봉 필수:** should-trigger 8–10개, should-not-trigger 8–10개. 형식은 skill-creator의 트리거 평가 JSON과 동일.

```json
[
  {"query": "현실적이고 구체적인 사용자 톤 자연 프롬프트 — 파일 경로/배경 포함", "should_trigger": true},
  ...
]
```

**should-not-trigger 작성 시:** 인접 도메인(harness-generator, skill-creator, 다른 하네스 진입 스킬)의 트리거 키워드를 의도적으로 포함시켜 near-miss를 만든다. "obviously irrelevant" 한 예시는 검증력이 약하다.

### B. 스킬 본문 수정

- 추가 절(section)은 본문 < 500줄 한도를 깨지 않는지 확인. 깬다면 `references/` 분리 권고.
- 새 절은 Why-First 구조: "왜 이게 필요한가" → "어떻게 한다" → "흔한 실패".
- 결박형 규칙은 일반 원리로 풀어쓴다.

### C. 에이전트 정의 수정

- Core Role 변경은 다른 에이전트의 책임과 겹치지 않는지 확인.
- Input/Output Protocol을 바꾸면 호출하는 오케스트레이터 Phase도 갱신 필요 — patch에 두 파일 변경을 함께 묶고 충돌 위험 명시.

### D. 오케스트레이터 Phase 수정

- 새 Phase 삽입 시 인접 Phase의 입출력 경로(`_workspace/...`) 와 일관성 확인.
- 데이터 전달 전략 매트릭스(파일/반환/메시지/작업)에서 어느 칸인지 명시.

### E. new-script (스크립트화)

- 본문 추가 대신 `scripts/{name}.{ext}` 신설 patch. 본문에는 "이 동작은 `scripts/{name}` 을 사용한다" 1줄만 추가.
- 권고 사유: trajectory에서 동일 헬퍼가 3회 이상 재현됨을 evidence로 인용.

## Risks 작성 (필수)

모든 refinement에는 "이 수정이 깰 수 있는 다른 케이스" 를 최소 1개 적는다.

- description 추가 시: 인접 스킬과의 트리거 충돌.
- 본문 결박형 → Why-First 전환 시: 일관성을 의도하던 케이스가 약해질 가능성.
- 에이전트 책임 변경 시: 다른 에이전트와의 인계 지점 변경.

Risks가 빈 patch는 의심하라 — 부작용이 정말 없을 수는 없다.

## Regression Eval 제안

진화 후 사용자가 직접 돌릴 자연 프롬프트 2–3개를 제안한다 (`regression_eval_suggestion`). 본 스킬이 그 평가를 실행하지는 않는다 — 진화 회차의 회귀 평가는 사용자가 직접.

## 출력 스키마 (재명시)

예시(특정 플러그인에 종속되지 않음 — 실제 회차에서는 사용자가 지목한 대상 하네스의 경로가 들어간다):

```json
{
  "diagnosis_id": "1",
  "target_path": "plugins/{대상-플러그인}/skills/{대상-스킬}/SKILL.md",
  "change_kind": "description",
  "summary": "누락된 표현 클래스를 식별해 트리거 키워드 풀 확장",
  "rationale": "단일 표현 추가 대신 '<누락된 표현 클래스>' 자체를 식별해 추가. skill-creator §generalize.",
  "patch_ref": "_workspace/phase2_patch_1.md",
  "trigger_eval_ref": "_workspace/phase2_trigger_eval_1.json",
  "risks": [
    "동일 플러그인 또는 인접 하네스의 다른 스킬과 키워드 겹침 가능"
  ],
  "regression_eval_suggestion": [
    "사용자가 실제로 쓴 자연 표현 1",
    "동일 의도의 변형 표현",
    "near-miss (해당 스킬이 잡혀야 함)"
  ]
}
```

## 거절/보류 출력

- `change_kind: "skip"` — 진단의 증거가 부족(`severity: unknown`), patch 만들지 않음.
- `change_kind: "blocked"` — 대상 파일 없음. 신규 파일 생성은 `harness-generator` 책임 영역.
- `change_kind: "structural-redesign-required"` — 같은 표적이 누적 3회 이상 패치 권고됨. 본문이 아닌 구조 재설계 필요.

이 세 가지 출력은 오케스트레이터가 Phase 4 사용자 게이트에 그대로 노출한다.

## 흔한 실패 패턴

- **좁은 패치** — 결함 케이스 1개만 잡는 키워드 추가. 일반 원리로 다시.
- **MUST 추가로 끝냄** — Why가 빠짐. Why를 함께 박지 않으면 다른 곳에서 또 미끄러진다.
- **Risks 빈칸** — 부작용 식별 없이 끝냄. 최소 1개 적는다.
- **Trigger eval 누락** — description 건드렸는데 평가 큐 없음. patch 자체를 보류해야 한다.
- **자동 적용 시도** — 직접 Edit/Write 호출. 본 스킬은 patch만 만든다 — 적용은 오케스트레이터의 책임.

## 협업

- **입력:** `failure-diagnosis` 산출물 1건.
- **출력:** `_workspace/{phase}_refinement_{N}.json` + `_workspace/{phase}_patch_{N}.md` + (선택) `_workspace/{phase}_trigger_eval_{N}.json` → 오케스트레이터 Phase 4.
