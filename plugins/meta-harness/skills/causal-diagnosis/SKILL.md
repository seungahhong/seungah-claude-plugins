---
name: causal-diagnosis
description: full-trace 기반 causal 진단 루브릭. experience-store의 원본 raw trace를 grep/cat로 직접 선택 조회해 하네스 결함의 root cause를 인과적으로 진단한다. 사용자가 "왜 이렇게 동작했는지 진단해줘", "이 결함의 근본 원인 찾아줘", "어느 표적을 고쳐야 하는지 진단" 등을 언급하거나, meta-harness 오케스트레이터의 Phase 3에서 failure-diagnostician가 호출될 때 사용한다. confound(공통 변경) 격리 → 단독 검증 → 위험 평가 → why-first 인과사슬 기술이 핵심 절차다. 요약을 근거로 쓰지 않고 trace의 step 번호·파일 경로를 직접 인용한다.
---

# Causal Diagnosis — full-trace 인과 진단

## 왜 이 스킬인가 (제1원칙)

하네스 결함을 "그게 실패했다(that-failed)"로만 적으면 동일 결함이 반복된다. **why를 잡아야** 패치가 root cause를 끊는다. 그리고 why는 **압축 요약에서 나오지 않는다** — 요약은 진단 정보를 뭉개므로(full-trace가 summary보다 우월하다는 것이 이 플러그인의 제1원칙), 진단은 항상 experience-store의 **원본 raw trace를 직접 조회**해서 step 번호와 파일 경로를 인용한 인과사슬로 기술한다.

이 스킬은 **산출물(diagnosis JSON)·금지·목표만 제약하고 진단 절차 자체는 자유롭게 둔다.** 아래 5신호→5표적 표는 **고정 critique 포맷이 아니라 navigation 힌트**다. 표를 체크리스트처럼 기계적으로 채우는 순간, 신호에 안 맞는 진짜 root cause를 놓친다(GEPA식 고정 비판의 함정 — 정해진 항목만 보고 실제 원인을 못 본다). 표는 "어디부터 trace를 읽을지" 안내일 뿐, 결론은 trace가 정한다.

## 진단 절차 (순서 고정, 내부 판단은 자유)

### 1. raw trace 선택 조회 — grep/cat 직접
experience-store에서 해당 결함과 연관된 step만 골라 읽는다. 전체를 요약본으로 읽지 말고, 신호 키워드로 좁혀 원본 jsonl을 본다.

```
# 결함 후보가 적재된 위치
.claude/experience-store/{run}/{candidate}/traces/*.jsonl   # repo-wide(기본)
plugins/{target}/experience-store/{run}/{candidate}/traces/*.jsonl  # plugin(opt-in)

# 예: redirect 발화·스키마 불일치·에이전트 실패 step만 발췌
grep -n "redirect\|user_redirect\|schema_mismatch\|agent_error" \
  .claude/experience-store/{run}/{candidate}/traces/*.jsonl
cat .claude/experience-store/{run}/{candidate}/traces/0003.jsonl   # 해당 step 원문 확인
```

원본을 본다 = step의 입력/산출물 payload를 그대로 본다. **요약을 근거로 인용하지 않는다.**

### 2. confound 먼저 의심 (가장 중요)
여러 실패가 함께 나타나면, 각 실패를 따로 진단하기 전에 **두 실패의 *공통* 변경/공통 입력이 진범인지** 먼저 가설한다. 표면 증상이 다르더라도 같은 SKILL.md 한 줄, 같은 description 트리거, 같은 agent 정의가 공통 원인일 수 있다. confound를 격리하지 않으면 증상마다 패치를 쏟아 본문비용만 늘고 root cause는 살아남는다.

→ `confound_hypothesis` 필드에 "이 결함과 묶일 수 있는 공통 변경 가설"을 명시한다(없으면 `null`).

### 3. 단독 검증 (격리)
공통 변경 가설을 세웠다면, 그 변경 **하나만** 두고 다른 요인을 배제한 채 "이 변경이 단독으로 이 증상을 내는가"를 trace로 확인한다. 한 step 안에서 원인 후보가 둘 이상이면, 각각을 분리해 어느 것이 증상에 선행했는지 step 순서로 가린다.

### 4. 위험 평가
root cause를 끊는 변경이 다른 동작을 깨뜨릴 위험을 본다. 특히 description 트리거를 좁히면 정상 호출까지 막는지, 본문 규칙을 추가하면 다른 시나리오와 충돌하는지. severity(증상의 파급)와 confidence(인과 확신)를 분리해 매긴다.

### 5. why-first 인과사슬 기술
"무엇이 → 무엇을 → 어떻게 야기했나"를 한 사슬로 적고, **각 고리마다 trace step 번호 또는 파일 경로를 인용**한다. evidence는 "요약문"이 아니라 `trace_ref`(step id / 파일경로:라인)다.

## 5신호 → 5표적 매핑 (navigation 힌트 — 고정 포맷 금지)

아래는 trace를 어디부터 읽을지 가리키는 **출발점**이다. 신호가 보이면 그 표적 정의를 먼저 펼쳐 보되, 결론은 trace가 정한다. 신호에 안 맞으면 표를 버리고 trace를 따라간다.

| 신호 (trace에서 관찰) | 1차 의심 표적 | kind |
|---|---|---|
| 재요청 — 사용자가 "다시/말고/그게 아니라"로 같은 작업 재지시 | description 트리거 부정확 OR 본문 지침 누락 | `description` / `skill-body` |
| 우회 — 사용자가 스킬을 안 쓰고 직접 지시하거나 좁은 우회책 요구 | description 트리거 OR 본문이 케이스 누락 | `description` / `skill-body` |
| 에이전트 실패 — spawn된 agent가 stall·잘못된 산출·범위 이탈 | agent 정의(역할/입출력/재호출 가이드) | `agent` |
| 스키마 불일치 — 산출물이 약속한 JSON/형식과 어긋남 | 산출 형식을 정의한 본문 OR orchestrator 조립 단계 | `skill-body` / `orchestrator` |
| Why 부재 — 규칙은 있는데 이유가 없어 LLM이 오판 | 루트 CLAUDE.md OR 해당 SKILL 본문 | `claude-md` / `skill-body` |

> kind 후보 전체: `description` | `skill-body` | `agent` | `orchestrator` | `claude-md` | `plugin-metadata`.

## scope_status 판정 (패치 경계)

표적이 패치 경계 안인지 함께 판정한다.

- `in-boundary` — repo-wide(기본)에서 표적이 **루트 CLAUDE.md 또는 임의 SKILL.md**. plugin(opt-in)이면 지목 플러그인 내 모든 파일.
- `scope-escalation` — repo-wide인데 표적이 agents/·commands/·hooks/·plugin.json·플러그인별 CLAUDE.md. 패치 불가, plugin 모드 재실행이 필요하다고 표시.
- `out-of-scope` — 레포 루트 메타(.claude-plugin/marketplace.json 등). 사용자 직접 수정 영역.

## 결함 아님 — no-op 규칙

trace를 읽어 보니 **하네스 결함이 아니라 사용자의 단순 변심**(요구 자체가 바뀐 것이지 하네스가 틀린 게 아님)이라면, 패치 표적을 만들지 않는다. 이때 diagnosis를 강제로 짜내면 frontier만 후퇴시킨다.

→ `root_cause`에 "결함 아님: 사용자 요구 변경(하네스 동작은 의도대로)"를 적고, `target`은 `null`, `severity: "none"`, `needs_user_input: false`로 두어 후속 패치 단계가 건너뛰게 한다.

## 출력 — diagnosis_{N}.json

결함 1건당 파일 1개. 스키마:

```json
{
  "defect_id": "string",
  "target": {
    "path": "string | null",
    "kind": "description | skill-body | agent | orchestrator | claude-md | plugin-metadata | null",
    "scope_status": "in-boundary | scope-escalation | out-of-scope"
  },
  "root_cause": "string — why-first 인과사슬 (무엇이→무엇을→어떻게)",
  "evidence": [
    { "trace_ref": "string — step id 또는 파일경로:라인", "note": "string — 이 근거가 사슬의 어느 고리인지" }
  ],
  "confound_hypothesis": "string | null — 다른 결함과 묶일 공통 변경 가설",
  "severity": "critical | high | medium | low | none",
  "confidence": "high | medium | low",
  "needs_user_input": true
}
```

### 예시 (1건)

```json
{
  "defect_id": "D-2026-0603-01",
  "target": {
    "path": "plugins/frontend-harness/skills/a11y/SKILL.md",
    "kind": "description",
    "scope_status": "in-boundary"
  },
  "root_cause": "a11y SKILL의 description이 '컴포넌트 리뷰' 일반어를 포함해, 사용자가 보안 리뷰를 요청한 step에서도 a11y가 잘못 트리거됨 → 사용자가 'a11y 말고 보안 보라'고 재지시(재요청 신호). 트리거 경계가 넓어 의도와 어긋난 호출을 야기.",
  "evidence": [
    { "trace_ref": "0007.jsonl#step12", "note": "사용자 발화 '보안 보라고 했잖아, a11y 말고' — 재요청 신호 원문" },
    { "trace_ref": "plugins/frontend-harness/skills/a11y/SKILL.md:3", "note": "description의 광범위한 '컴포넌트 리뷰' 문구가 보안 요청을 흡수" }
  ],
  "confound_hypothesis": null,
  "severity": "medium",
  "confidence": "high",
  "needs_user_input": true
}
```

## 흔한 실패와 대응

| 실패 | 증상 | 대응 |
|---|---|---|
| that-failed만 보고 why 누락 | "스킬이 틀린 산출을 냄"에서 멈춤 | root_cause를 인과사슬로 강제 — 각 고리에 trace_ref 인용. why 없는 진단은 미완성으로 반려. |
| confound 무시 | 증상마다 별도 패치 → 본문비용만 증가, root cause 잔존 | 2단계를 건너뛰지 않는다. 동시 결함은 confound_hypothesis 먼저 채운다. |
| 요약을 근거로 인용 | evidence가 "대략 ~한 것 같다" 같은 가공문 | evidence는 trace_ref(step/파일경로)만 허용. 요약본 인용 금지 — 원본 jsonl을 cat해 확인. |
| 고정 포맷 강제 | 5신호 표에 안 맞는 root cause를 표에 끼워맞춤 | 표는 navigation 힌트다. 안 맞으면 표를 버리고 trace를 따른다. |
| 변심을 결함으로 처리 | 사용자 요구 변경인데 패치 표적 생성 | no-op 규칙 적용 — target null, severity none. |
