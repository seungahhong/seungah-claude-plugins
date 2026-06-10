# generator-harness Dry-Run Report

`generator-harness` 오케스트레이터의 Phase 0~8 흐름을 두 시나리오(정상 1 + 에러 1)로 논리 점검한 리포트. 런타임 실행이 아니라 **설계 정합(design-conformance)** 점검이다 — 각 Phase가 입출력 계약을 만족하고 dead link/누락 단계가 없는지 확인한다.

## 시나리오 A — 리서치 보고서 도메인 자동 탐색 (정상)

**입력:** "리서치 보고서 작성 도메인 하네스를 근거 기반으로 자동 탐색해서, 후보 몇 개 점수 매기고 비용 대비 제일 나은 걸로 만들어줘."

| Phase | 동작 | 입력 → 산출 | 점검 |
|-------|------|-------------|------|
| 0 감사 | `.claude/_workspace/` 없음 → 초기 탐색. 대상 위치 트리거 충돌 검사 | 사용자 요구 → 분기 보고 | 충돌 없음, 1줄 보고 후 승인 |
| 1 분석 | domain-analyst 1회 | 요구 → `phase1_domain_spec.json` (eval_set 4건 + pareto_axes + transfer 1건) | eval_set 비어있지 않음 → 통과 |
| 2 탐색공간 | 오케스트레이터 직접 | spec → 모듈러 공간, N=3(최소비용/최대품질/균형), 진화 ≤2 | 예산 1줄 보고 |
| 3 제안 | harness-proposer 3명 **병렬** | spec → `cand_1~3/design.json` | lens 3종 상이, 동질 아님 |
| 4 채점 | harness-evaluator 3명 **병렬** | design + eval_set → `cand_1~3/score.json` | pareto_coord(품질,비용) 동일 단위, frontier 산출 |
| 5 진화 | (건너뜀) | cand_3 bar 통과 | acceptance bar 충족 → skip |
| 6 게이트 | 오케스트레이터 직접 | frontier 표 + cand_3 추천(why) → 사용자 승인 | **자동 실체화 없음**, 승인 수집 |
| 7 실체화 | harness-materializer 1회 | 승인 cand_3 → agents/skills/orchestrator + CLAUDE.md | harness-generator 규약 재사용, 구조 검증 통과 |
| 8 이력 | 오케스트레이터 직접 | 결정 → `_workspace` 보존 + CLAUDE.md 1줄 | 피드백 요청 |

**Phase 간 데이터 흐름:** `phase1_domain_spec.json`이 Phase 3·4의 공유 입력 → 정합. `candidates/cand_{k}/design.json`(Phase 3 산출)이 Phase 4·7 입력 → 정합. dead link 없음.

## 시나리오 B — 개방형 도메인 bar 미달 (에러)

**입력:** "UI 컴포넌트 구현 도메인 하네스 자동 탐색해서 만들어줘." (정답·자동채점기 없는 개방형)

| Phase | 동작 | 분기 |
|-------|------|------|
| 1 분석 | domain-analyst | assertion '관찰형' + notes "LLM-judge — confidence 하향" |
| 4 채점 | harness-evaluator | 전 후보 pass_rate < bar, `confidence:low` |
| 5 진화 | harness-proposer/evaluator 1라운드 | recombination → 여전히 bar 미달, **라운드 상한(2) 도달 → 정지** |
| 6 게이트 | 오케스트레이터 | **억지 추천 금지** → "bar 미달" 보고 + 평가셋 조정 또는 harness-generator 수동 생성 제안 |
| 7 실체화 | — | 승인 없음 → 실체화 0건 |
| 8 이력 | 오케스트레이터 | 결정 ledger에 미달·미해결 기록 |

**점검:** 개방형 도메인에서 confidence 하향(Phase 1·4) → 억지 추천 회피(Phase 6) → 무한 탐색 방지(Phase 5 상한) → 자동 실체화 금지(Phase 7) 4중 안전망이 모두 작동. meta-harness 위임 경로(기존 하네스 개선 시)도 Phase 0에서 분기됨.

## dead link / 누락 점검

- 오케스트레이터 → references 2개(research-foundations, building-blocks) · sibling skill 2개(harness-search, harness-eval): 실파일 해석.
- agents → `../skills/harness-eval/SKILL.md`, `../skills/harness-search/SKILL.md`: 해석.
- harness-search/harness-eval → `../generator-harness/references/*.md`: 해석.
- harness-materializer → `plugins/harness-generator/skills/harness-generator/references/{agent-design,skill-guide,orchestrator-generate}.md`: 교차참조 3파일 실재.
- 4 에이전트(domain-analyst/harness-proposer/harness-evaluator/harness-materializer) ↔ 오케스트레이터 Phase 1/3/4/7 spawn 1:1 대응.

**Verdict:** PASS — Phase 시퀀스 논리 정합, 입출력 매칭, 4중 안전망 작동, dead link 0건.
