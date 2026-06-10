---
name: harness-eval
description: 하네스 후보를 채점할 '평가셋'(대표 태스크 + 검증 가능한 assertion + Pareto 축 + 전이 시나리오)을 구축하고, 후보를 정확도(pass_rate)와 토큰비용의 '독립 축'으로 채점해 Pareto 좌표·전이성·적대적 실패모드를 산출하는 방법론. domain-analyst와 harness-evaluator 에이전트가 따르며, 사용자가 "하네스 평가셋 만들기", "후보 Pareto 채점", "전이성 측정"을 언급할 때도 적용한다. 단일 정확도 점수로 뭉개지 않고, 개방형 도메인은 confidence를 낮춘다.
---

# Harness Eval — 평가셋 구축 · Pareto 채점 방법론

후보 하네스를 *무엇으로 어떻게* 채점할지 정의한다. 핵심 원칙: **품질 단독이 아니라 품질×비용 Pareto** + **전이성**. AFlow(execution feedback·비용 4.55%)·MaAS(전이성·6~45% 비용)에 근거한다. 출처는 [../generator-harness/references/research-foundations.md](../generator-harness/references/research-foundations.md).

---

## A. 평가셋 구축 (domain-analyst)

### 1. 대표 태스크 3~5건
그 도메인에서 *실제로 자주 들어올* 요청으로 고른다. 엣지 케이스가 아니라 **분포의 중심**을 덮는다. 너무 적으면(1~2건) 우연이, 너무 많으면 채점 비용이 문제다.

### 2. 검증 가능한 assertion
각 태스크에 **관찰로 판정 가능한** assertion을 붙인다.

| 좋은 assertion | 나쁜 assertion |
|----------------|----------------|
| "산출에 X 섹션이 포함된다" | "좋은 결과를 낸다" |
| "Y 형식 파일이 생성된다" | "사용자가 만족한다" |
| "에러 흐름에서 누락 처리 후 진행한다" | "잘 동작한다" |

### 3. Pareto 축 분리
`quality`(assertion pass_rate)와 `cost`(total_tokens)를 **독립 축**으로 둔다. 한 점수로 뭉개지 않는다 — 뭉개면 frontier를 못 만든다.

### 4. 전이 시나리오 1~2건
인접 도메인 또는 다른 모델로 옮기는 probe. "전이 후에도 성립해야 할 관찰"을 적는다. 이것이 도메인 무관성의 조작적 정의다.

### 5. 개방형 도메인 처리
정답·자동채점기가 없으면(UI 구현, 문서 작성 등) assertion을 '관찰형'으로 쓰고 `notes`에 "LLM-judge 채점 — confidence 하향"을 남긴다. 없는 정답을 지어내지 않는다.

---

## B. Pareto 채점 (harness-evaluator)

### 1. 품질 — assertion pass_rate
평가셋의 각 태스크를 후보 설계로 **dry-run**(논리적 실행)한다. Phase 시퀀스가 그 태스크를 실제로 푸는가? dead link·누락 단계는? 각 assertion을 `{text, passed, evidence}`로 채점하고 `pass_rate`를 낸다. harness-generator의 `grading.json` 스키마를 그대로 쓴다(필드명 `text`/`passed`/`evidence`, `summary` 정확히 — 변형 금지).

### 2. 비용 — 추정 total_tokens
후보 구조에서 토큰비용을 추정한다.

| 비용 요인 | 영향 |
|-----------|------|
| 에이전트 수 | 각 spawn은 컨텍스트 비용 |
| 단계(phase) 수 | 단계마다 호출 |
| 팀 통신(SendMessage) | 메시지마다 비용 |
| 생성-검증 루프 | 반복 횟수 × 비용 |
| 다각 팬아웃 | 병렬 워커 수 × 비용 |

Anthropic 보고: 멀티에이전트는 단일 대비 ~15배 토큰. 비용을 "모른다"로 비우지 않고 **구조에서 추정**한다.

### 3. Pareto 좌표
`pareto_coord{quality: pass_rate, cost: est_total_tokens}`. 모든 후보가 **동일 단위**여야 직접 비교된다 — 후보마다 다른 척도 금지. 오케스트레이터는 이 좌표로 비지배(non-dominated) 후보 집합 = frontier를 만든다.

### 4. 전이성
transfer_scenario를 후보에 적용해 `{scenario, held, note}`를 낸다. 무너지면 `held:false` + 이유 → "이 도메인 전용"으로 표시.

### 5. 적대적 실패 모드
"이 후보는 어디서 무너지는가?" — 컨텍스트 오염(검증자가 생성자 의도를 봄), 특정 입력에서 오답, dead link, 비용 폭발 등을 능동적으로 캔다. `adversarial_failure_modes`에 나열한다. 칭찬이 아니라 약점을 찾는 게 채점자의 일이다.

### 6. confidence
개방형 도메인이라 assertion 판정이 주관적이면 `confidence:low` + 이유. LLM-as-judge 신뢰성은 미확정이므로(research-foundations.md §5) 높은 확신을 가장하지 않는다.

---

## acceptance bar

후보가 "합격"하려면: (a) pass_rate가 도메인 임계(기본 0.8, 개방형은 사용자 합의) 이상이고, (b) 최소 1개 transfer_scenario에서 `held:true`. bar를 넘는 후보가 frontier에 있으면 Phase 5 진화를 건너뛴다. 아무도 못 넘으면 **억지 추천 금지** — Phase 6에서 그대로 보고하고 평가셋·탐색공간 조정 또는 harness-generator 수동 생성을 제안한다.

## 안티 패턴

- **단일 점수 뭉개기** — 품질·비용을 가중합으로 합치면 frontier가 사라진다.
- **비용 비우기** — "모른다"로 두면 Pareto가 무의미해진다. 구조에서 추정하라.
- **개방형 도메인 과신** — 정답 없는데 pass_rate를 확신. confidence를 낮춰라.
- **칭찬형 채점** — 좋은 점만 보고 실패 모드를 안 캠. 적대적이어야 한다.
- **척도 불일치** — 후보마다 다른 단위로 채점해 비교 불가.
