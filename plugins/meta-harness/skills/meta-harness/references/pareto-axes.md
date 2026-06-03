# Pareto 축 — 패치 후보 평가의 4차원

meta-harness는 패치 후보를 단일 점수로 줄세우지 않는다. 4개 축으로 동시에 평가하고, **어느 축도 frontier를 후퇴시키지 않는 후보만** 채택한다. 이것이 pareto-refiner의 채택 규칙이다.

## 논문의 accuracy↔context Pareto를 이 도메인으로 번역

근거 논문(Meta-Harness, arXiv 2603.28052v1)은 하네스를 정확도(accuracy)와 컨텍스트 비용(context)의 Pareto frontier 위에서 최적화한다 — 정확도를 올리되 컨텍스트를 무한히 부풀리는 후보는 frontier를 지배(dominate)하지 못하므로 버려진다. 이 플러그인은 그 frontier를 하네스 엔지니어링 도메인으로 옮긴다. "정확도"는 **하네스가 사용자 의도대로 동작하는가(behavior-alignment)**와 **트리거가 정확한가(trigger-precision)**·**hold-out에서도 견고한가(generalization)**로 분해되고, "컨텍스트 비용"은 이 레포의 규약(본문 <500줄, Why-first, MUST/NEVER 남용 금지)과 직결된 **rule-body-cost**가 된다. 즉, 정합을 사기 위해 본문을 부풀리는 거래를 frontier가 자동으로 거절한다.

## 4축 정의

| 축 | 방향 | 무엇을 측정하나 |
|----|------|----------------|
| behavior-alignment (동작정합) | max | 패치 후 하네스가 사용자가 의도한 동작을 내는가 |
| rule-body-cost (규칙본문비용) | min | 본문 줄 수 + MUST/NEVER 결박 수 |
| trigger-precision (트리거정밀도) | max | should-trigger/should-not의 정확도 |
| generalization (일반화) | max | hold-out 시나리오에서의 견고성 |

### 1. behavior-alignment (max)

패치를 적용한 하네스가 사용자가 redirect/보강으로 요구한 동작을 실제로 내는지.

- 측정: Phase 2에서 캡처한 redirect 발화·보강 요구를 assertion으로 환원한다(예: "redirect 의도가 본문에 반영", "보강이 요청한 누락 요소를 채움"). 통과 assertion / 전체 assertion 비율을 [0,1]로 기록.
- 근거 인용: trace의 step 번호로 "원래 잘못 간 동작"을 지목하고, 패치된 본문이 그 동작을 어떻게 교정하는지 보인다.

### 2. rule-body-cost (min)

패치가 하네스 본문에 부과하는 비용. **줄 수 + 결박(MUST/NEVER) 수**로 계량한다.

- 측정: 패치 후 대상 파일의 본문 줄 수(frontmatter·references 제외) + `MUST`/`NEVER`/`반드시`/`절대` 류 무조건 결박 카운트.
- 이 레포의 규약(본문 <500줄, Why-first)과 정합한다. MUST/NEVER 남용은 yellow flag이므로 결박 수 증가 자체가 비용으로 잡힌다.
- 줄이는 방향이 선(min)이다 — 같은 정합을 더 적은 줄·더 적은 결박으로 달성하는 후보가 우월하다.

### 3. trigger-precision (max)

description 수정 시 트리거의 정확도. should-trigger를 잡고 should-not-trigger를 거르는가.

- 측정: pareto-refiner가 동봉한 trigger_eval(should-trigger 8~10 + should-not-trigger 8~10)을 돌려 (정답/전체)로 산출. should-not을 잘못 트리거하면 정밀도가 깎인다.
- description을 건드리지 않는 패치는 이 축을 직전 값으로 carry(후퇴 아님)한다.

### 4. generalization (max)

패치가 본 시나리오뿐 아니라 hold-out 시나리오에서도 견고한가. **좁은 우회책(narrow workaround)을 배격**하는 축이다.

- 측정: 진단에 쓰지 않은 hold-out 트리거/상황을 후보에 적용해 동작정합이 유지되는 비율.
- 한 redirect 사례에만 들어맞고 유사 사례에 깨지는 후보는 이 축에서 낮다 → frontier 진입 실패.

## 비후퇴(non-regression) 채택 규칙

**채택 후보는 4축 중 어느 축도 현 frontier를 후퇴시키지 않아야 한다.**

- max 축(alignment·trigger·generalization)은 frontier 값 이상.
- min 축(rule-body-cost)은 frontier 값 이하.
- 한 축을 후퇴시키며 다른 축을 올리는 trade는 **자동 채택하지 않는다** — 사용자 승인 게이트(Phase 6)에서 명시적 trade로 보고하고, 승인 없이는 적용하지 않는다.
- pareto.json의 `frontier`/`dominated`에 좌표를 기록하고, dominated 후보는 `reason`에 후퇴 사유를 남긴다.

> 왜: 단일 점수 최적화는 "정합을 위해 본문을 부풀리는" 국소 최적에 빠진다. 4축 동시 비후퇴는 그 거래를 구조적으로 막는다.

## reject 예시 — 본문비용↑인데 정합 이득 없음

채택 거절이 발동하는 전형은 **본문 길이·MUST 결박이 늘었는데 동작정합 이득이 없는** 후보다.

예시 — cand-skill-3 vs frontier(cand-claude-md-1):

| 후보 | behavior-alignment | rule-body-cost | trigger-precision | generalization | 판정 |
|------|--------------------|----------------|--------------------|----------------|------|
| cand-claude-md-1 (frontier) | 0.82 | 41 | 0.90 | 0.78 | on frontier |
| cand-skill-3 | 0.70 | 52 (MUST 3개 추가) | 0.80 | 0.60 | **reject** |

- cand-skill-3은 rule-body-cost가 41→52로 **증가**(MUST 3개 추가)했는데 behavior-alignment는 0.82→0.70으로 **하락**, generalization도 0.78→0.60으로 하락했다.
- 어느 max 축도 frontier를 못 넘고, min 축은 후퇴 → frontier에 cand-claude-md-1에 의해 지배됨(dominated).
- pareto.json에 `"reason":"본문비용 증가(52>41)에도 정합 이득 없음 → reject"`로 기록하고 채택하지 않는다.

> 규칙 한 줄: **본문 길이·결박 수 증가가 정합 이득 없이 들어오면 reject.** "더 많은 규칙"은 더 나은 하네스가 아니다 — 이유로 설득되는 더 적은 규칙이 우월하다.

## 같은 표적 3회 누적 — 구조 재설계 권고

recurring-patterns.md에서 같은 표적이 needs_attention(≥3)에 도달하면, pareto-refiner는 본문 patch를 거절하고 `change_kind:"structural-redesign-required"`를 낸다. 같은 표적을 본문 수정으로 3번 두드렸다는 것은 frontier가 본문 비용 축에서 막혔다는 신호이며, 더 부풀리기보다 구조(표적 자체의 분해·역할 재배치)를 바꾸라는 뜻이다.
