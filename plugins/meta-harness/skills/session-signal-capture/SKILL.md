---
name: session-signal-capture
description: meta-harness Phase 2에서 trace-capturer 에이전트가 따르는 신호 캡처 방법론 스킬. 현 세션의 redirect/보강 발화 원문·직전 AI 산출물·active SKILL(R1)과 세션 외부 .md 산출물(R3)을 요약 없이 원형 trace(JSONL)로 적재한다. R3는 .md 출처 에이전트/skill을 3단 폴백으로 역추적하고 confidence를 부여한다. 사용자가 "방금 발화·산출물 원형으로 캡처", "이 .md 만든 에이전트/skill 역추적", "redirect 신호 trace로 적재" 등을 말할 때 따른다. 일반 애플리케이션 로그 분석에는 사용하지 않는다.
---

# Session Signal Capture — 원형 신호 캡처 방법론

`trace-capturer` 에이전트가 본 스킬을 따른다. `meta-harness` Phase 2에서 호출되며, 직접 사용자 요청에 답하는 일은 거의 없다.

## 왜 원형 보존인가 (제1원칙)

Meta-Harness 논문(arXiv 2603.28052v1) Table 3은 full-trace 보존(56.7)이 압축 요약(38.7)을 크게 앞선다는 것을 보여준다. 진단가가 root cause를 causal-reasoning으로 짚으려면 발화 원문·코드 본문·파일 경로의 **원형**이 필요하다. 요약은 증상을 남기고 원인을 지운다. 따라서 본 스킬의 규칙은 단 하나로 수렴한다 — **신호를 요약하지 말고 원형으로 적재한다.**

이 규칙은 정규화 스킬류의 'payload 적재 금지' 관행을 **의도적으로 뒤집는다**. 그쪽은 인덱스/표가 산출물이라 payload를 경로로 날려도 됐지만, 여기서 traces/는 진단의 1차 증거다. 경로로 날린 순간 Table 3의 Scores+Summary 퇴화가 일어난다.

## 데이터 적재 기준 준수 (C1·C2·C4·C7)

본 스킬의 캡처는 [meta-harness/references/data-capture-criteria.md](../meta-harness/references/data-capture-criteria.md)의 적재 기준을 따른다. 캡처 단계에서 직접 작동하는 항목:

- **C1 묶음** — 〔발화〕+〔직전 AI 산출물〕+〔active SKILL〕을 한 묶음으로. 증상(발화)만으론 원인을 못 짚는다.
- **C2 원문** — 위 제1원칙(요약·절단 금지).
- **C4 그 순간** — 발화 시점에 lightweight identifier(`transcript_path`·`ref`·active-skill)를 함께 고정한다. transcript는 immutable이라 `transcript_path` 역추적으로 직전 산출물·active SKILL을 복원하는 하이브리드가 정상 경로다(JIT 패턴) — "지금 캡처 + 나중 견고한 복원"이 둘 다 성립한다.
- **C7 등급** — 신호는 강도를 구분해 싣는다. 단순 재실행("다시 빌드/실행")은 weak, 실질 교정("틀렸/아니/바꿔/빼줘/빠졌")은 strong. 약한 신호도 버리지 말고 등급만 낮춰 적재한다(놓친 신호는 흔적 없이 사라진다).

## 캡처 대상 (트리거 유형별)

### R1 — 현 세션 redirect/보강

다음 세 신호를 **시간순으로** 원형 적재한다.

| 신호 | 원형으로 보존할 것 |
| ---- | ----------------- |
| redirect/보강 발화 | 사용자 메시지 **원문 전체**. "다시 해줘/보강해줘" 같은 의도 단어 포함, 줄바꿈·인용 유지. 패러프레이즈 금지 |
| 직전 AI 산출물 | 사용자가 문제 삼은 직전 AI 응답의 **코드/메시지 본문**. diff·파일이면 해당 hunk 전체 |
| active SKILL | 그 산출을 만든 시점에 로드돼 있던 skill 식별자(예: `<plugin>:<skill>`). 미상이면 `unknown`으로 명시(누락 금지) |

active SKILL 식별 단서: 직전 응답이 따른 절차/포맷, 사용자가 거명한 스킬, 세션에서 직전에 트리거된 스킬. 단정 불가하면 후보를 나열하고 `confidence: low`.

### R3 — 외부 .md 역추적 (세션 외)

1. 대상 .md **전문**을 읽어 `raw`에 적재(요약 금지).
2. 그 .md를 만든 **에이전트/skill을 식별**한다 — 3단 폴백.

## R3 출처 역추적 — 3단 폴백

상위 단계에서 확정되면 하위는 보조 근거로만 쓴다. 단계가 곧 confidence 상한이다.

| 단계 | 방법 | confidence |
| ---- | ---- | ---------- |
| ① 산출 경로 규약 매칭 | 파일이 놓인 경로가 특정 하네스의 산출 규약과 일치하는가. 예: `_docs/*-spec.md`, `.claude/_workspace/*`, `experience-store/*` — 어느 하네스/스킬이 그 경로에 쓰는지 CLAUDE.md/SKILL.md 규약으로 대조 | **high** |
| ② 파일 내 메타마커 | 파일 안 `generated-by:`, frontmatter, 푸터 서명, 섹션 템플릿 등 생성 주체를 명시한 마커 | **high** |
| ③ 구조·문체 + git 이력 | 섹션 구성·어조·표 포맷을 후보 스킬의 출력 스키마와 비교 + `git log`/`git blame`으로 생성 커밋·작성자 추적 | **medium / low** |

확정 절차:
- ① 또는 ②가 단독으로 잡히면 `confidence: high`, `source_evidence`에 매칭된 규약/마커를 그대로 인용.
- ③만으로 추정하면 `confidence: medium`(강한 구조 일치) 또는 `confidence: low`(약한 추정).
- 후보가 둘 이상 경합하면 모두 `candidates[]`에 싣고 최상위만 `best_guess`로, `confidence`는 경합 시 한 단계 낮춘다.

**confidence: low면 캡처를 끝내지 말고 오케스트레이터에 "출처 확인 질문 선행" 플래그를 올린다.** 잘못 짚은 출처로 엉뚱한 agent/skill을 고치는 것이 가장 비싼 실패다(Phase 6 게이트에서 사용자 확인).

## 출력 — trace JSONL 1줄 스키마

`trace-capturer`는 신호 1건당 1줄을 `.claude/experience-store/{run}/{candidate}/traces/{signal}.jsonl`(repo-wide) 또는 `.claude/plugin-store/{target}/...`(plugin)에 append한다.

```
{ts, actor, kind, ref, raw, confidence?, source_evidence?, candidates?}
```

| 필드 | 의미 |
| ---- | ---- |
| `ts` | ISO8601 또는 세션 내 단조 step. 시간순 정렬 키 |
| `actor` | `user` \| `assistant` \| `agent:{name}` \| `skill:{id}` \| `file` |
| `kind` | `redirect-utterance` \| `prior-output` \| `active-skill` \| `external-md` \| `source-trace` |
| `ref` | 출처 포인터 — 파일 절대경로 / 메시지 step / `git` 커밋 해시. raw를 **대체하지 않는다**(둘 다 적재) |
| `raw` | **원형 본문 전체**. 발화·코드·.md 전문. 요약·경로치환 금지 |
| `confidence` | R3 역추적 시 `high\|medium\|low` |
| `source_evidence` | R3에서 매칭된 경로 규약·메타마커·구조 단서 인용(요약문 아님) |
| `candidates` | R3 경합 시 후보 배열 |

예시(R1 redirect + 직전 산출물 + active skill):

```jsonl
{"ts":"2026-06-03T10:12:04Z","actor":"user","kind":"redirect-utterance","ref":"msg#41","raw":"방금 그 방향 말고 다시 해줘. 그리고 왜 이렇게 갔는지 보고 지금 쓰던 스킬 고쳐줘."}
{"ts":"2026-06-03T10:11:50Z","actor":"assistant","kind":"prior-output","ref":"msg#40","raw":"export function Button({label}:Props){\n  return <div onClick={...}>{label}</div>\n}  // 직전 응답 전체"}
{"ts":"2026-06-03T10:11:50Z","actor":"skill:<plugin>:<skill>","kind":"active-skill","ref":"loaded@msg#38","raw":"active skill: <skill> (직전 산출이 따른 절차/포맷 근거)","confidence":"high"}
```

예시(R3 외부 .md 역추적, ① 경로 규약 high):

```jsonl
{"ts":"2026-06-03T11:02:00Z","actor":"file","kind":"external-md","ref":"/abs/_docs/feat-x-spec.md","raw":"# feat-x 명세 문서\n## 배경\n...(.md 전문 그대로)..."}
{"ts":"2026-06-03T11:02:01Z","actor":"agent:doc-writer","kind":"source-trace","ref":"path-rule:_docs/*-spec.md","raw":"경로 _docs/{feature}-spec.md 규약은 spec-orchestrator 산출. 섹션(배경/기술스펙/변경사항/테스트/영향)을 doc-writer가 작성","confidence":"high","source_evidence":"path-rule:_docs/{feature}-spec.md + 5섹션 템플릿 일치"}
```

## 흔한 실패와 대응

| 실패 | 증상 | 대응 |
| ---- | ---- | ---- |
| 요약으로 뭉갬 | `raw`에 "버튼 컴포넌트 코드" 같은 한 줄 요약 | 본문 전체 적재. 길어도 traces/에는 원형이 규칙(Table 3) |
| 경로로 날림 | `raw` 대신 `ref`만 채움 | `ref`는 포인터, `raw`는 본문 — 둘 다 채운다 |
| 출처 오판 | ③ 약한 추정을 high로 단정 | 단계=confidence 상한 준수. ③만이면 medium/low, low는 사용자 확인 선행 플래그 |
| active skill 누락 | R1에서 active SKILL 행을 빠뜨림 | 미상이면 `unknown`으로라도 한 줄 남긴다. 진단가가 표적(어느 SKILL을 고칠지)을 잃는다 |
| 시간 역전 | redirect만 적재하고 직전 산출물 누락 | redirect 발화와 그것이 가리키는 직전 산출물은 **쌍**으로 적재해야 causal 진단이 선다 |

## 협업

- 본 스킬 산출물(traces/*.jsonl) → `causal-diagnosis`(failure-diagnostician)의 1차 증거. 진단가는 이를 grep/cat로 **직접 선택 조회**한다.
- raw 신호가 부분적이면 `meta-harness` Phase 1에서 사용자에게 발화/파일을 받아 본 스킬로 원형 적재한다.
- R3 `confidence: low`는 Phase 6 게이트의 "출처 확인 질문"으로 이어진다.
