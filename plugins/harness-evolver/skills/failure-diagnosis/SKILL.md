---
name: failure-diagnosis
description: 하네스(스킬·에이전트·오케스트레이터) 실행에서 발생한 결함을 정규화된 trajectory를 근거로 root cause로 식별·분류하는 진단 루브릭 스킬. 주로 harness-evolver Phase 2-2에서 failure-diagnostician 에이전트가 따른다. 5가지 결함 신호(트리거 누락/반복 우회/에이전트 실패/스키마 불일치/Why 부재)와 5가지 수정 표적의 매핑, 증거 인용 규칙, severity·confidence 기준을 정의한다. 사용자가 "하네스 결함 진단", "이 스킬 왜 안 트리거됐는지", "오케스트레이터 root cause", "하네스 패턴 분석" 등을 말할 때 트리거된다. 코드 자체의 일반 디버깅에는 사용하지 않는다.
---

# Failure Diagnosis — 결함 진단 루브릭

`failure-diagnostician` 에이전트가 본 스킬을 따른다. `harness-evolver` Phase 2-2 에서 결함 1건당 1회 호출된다.

## 진단의 원칙 — Why First

증상은 보이는 것, 원인은 그것을 일으킨 구조적 결함. 본 스킬은 **증상에서 원인을 분리**하는 것을 단일 목표로 한다.

- **증상으로 끝나면 다음 회차에 같은 문제가 재발한다.** 증상 위에 패치를 쌓으면 본문이 누더기가 된다.
- **원인은 항상 한 문장으로** 정리되어야 한다. 두 문장 이상이면 진단가가 두 결함을 묶은 것이다 — 분리하라.
- **모르면 모른다고 한다.** `severity: unknown` + `needs_user_input: true` 는 정상적 출력. 추측은 잘못된 patch로 이어진다.

## 5신호 → 5표적 매핑 (Why 포함)

### 신호 1: 사용자가 동일 요청을 재차 던짐

**Why:** description의 키워드 풀이 사용자의 실제 표현과 매칭되지 않거나, 트리거 신뢰도가 낮음.

**표적:** `skills/{name}/SKILL.md` 의 `description` 필드.
**진단 보고:** `target.kind: "description"`.

### 신호 2: 사용자가 같은 우회책(수동 보정)을 반복

**Why:** 스킬 본문에 해당 케이스 처리 원리가 빠짐. LLM이 매번 같은 곳에서 미끄러진다.

**표적:** `skills/{name}/SKILL.md` 본문의 누락된 절(section).
**진단 보고:** `target.kind: "skill"`, `target.section: "X 처리"`.

### 신호 3: 동일 에이전트가 반복 실패

**Why:** 에이전트의 책임 범위가 모호하거나 한 에이전트가 두 책임을 동시에 짊어짐.

**표적:** `agents/{name}.md`.
**진단 보고:** `target.kind: "agent"`.
**추가 권고:** 두 책임 발견 시 에이전트 분리 권고를 patch가 아닌 `structural-redesign-required` 로 표기.

### 신호 4: Phase A → Phase B 입력 불일치

**Why:** 오케스트레이터가 단계 간 입력/출력 스키마를 명시하지 않았거나, 변환 단계를 두지 않음.

**표적:** 오케스트레이터 스킬의 Phase 정의.
**진단 보고:** `target.kind: "orchestrator"`, `target.section: "Phase X → Y 데이터 전달"`.

### 신호 5: 도구 결과가 의도와 빗나감

**Why:** 본문이 MUST/NEVER 같은 결박형 지시에 의존, Why가 빠져 LLM이 엣지 케이스에서 잘못 판단함.

**표적:** 스킬 본문의 결박형 절. Why를 박은 일반 원리로 재작성 권고.
**진단 보고:** `target.kind: "skill"`, `change_kind_hint: "why-first-rewrite"`.

## 증거 인용 규칙 (Evidence)

- **모든 진단은 trajectory의 step 번호 1개 이상을 인용해야 한다.**
- 인용은 trajectory의 `input_summary` 또는 `output_ref` 또는 `note` 에서 직접 발췌. 자기 말로 다시 쓰지 않는다.
- 인용이 없으면 `severity: unknown` 으로 강등.

```json
"evidence": [
  {"step": 7, "quote": "doc-section-writer 호출 실패: schema mismatch (expected 'changes', got 'change_list')"}
]
```

## Severity 기준

| Severity | 기준 |
| -------- | ---- |
| high | 결함이 산출물의 정확성을 직접 깨뜨림 (예: 잘못된 데이터, 누락된 섹션) |
| medium | 산출물은 나오지만 추가 작업 필요 (예: 사용자가 매번 보정) |
| low | 미세 개선 여지 (예: description의 키워드 추가) |
| unknown | 증거 부족, `needs_user_input: true` 동봉 |

## Confidence (root_cause 후보가 2개 이상일 때)

- `confidence: high` — trajectory 증거가 단일 root cause를 강하게 지지
- `confidence: medium` — 후보 1번이 가장 유력하지만 다른 후보 배제 불가
- `confidence: low` — 추정에 가까움. 사용자에게 후보 모두 노출 권고

## 반복 패턴(recurring) 가중치

`evolution-memory/recurring-patterns.md` 가 있다면:

- 같은 표적이 누적 N≥2 이면 `severity` 를 한 단계 상승 (medium → high)
- 누적 N≥3 이면 `change_kind_hint: "structural-redesign-required"` 를 동봉. patch가 아니라 구조 재설계 신호.

## 출력 스키마 (재명시)

예시(특정 플러그인에 종속되지 않음 — 실제 회차에서는 사용자가 지목한 대상 하네스의 경로가 들어간다):

```json
{
  "diagnosis_id": "1",
  "symptom": "사용자가 자연어 표현으로 해당 스킬을 호출했으나 트리거되지 않았다",
  "root_cause": "대상 스킬 description의 트리거 키워드 풀이 사용자가 실제로 쓴 표현 클래스를 포함하지 않음",
  "target": {
    "kind": "description",
    "path": "plugins/{대상-플러그인}/skills/{대상-스킬}/SKILL.md",
    "section": "frontmatter.description"
  },
  "evidence": [
    {"step": 3, "quote": "user_input: '<사용자 표현>' → no skill triggered"}
  ],
  "severity": "high",
  "confidence": "high",
  "needs_user_input": false,
  "recurring_match": null,
  "change_kind_hint": "description-keyword-expansion"
}
```

## 흔한 실패 패턴

- **증상으로 끝남** — `root_cause: "오케스트레이터가 멈춤"`. 멈춘 이유까지 가야 한다.
- **두 결함 묶음** — 한 진단에 두 표적이 들어감. 분리 후 재호출.
- **증거 없는 단정** — `evidence: []` 인데 `severity: high`. 강등하라.
- **추측을 채움** — 모르면서 root cause를 채움. unknown + needs_user_input 으로 응답.

## 협업

- **입력:** `trajectory-capture` 산출물.
- **출력:** `_workspace/{phase}_diagnosis_{N}.json` → `eval-driven-refinement` 의 입력.
