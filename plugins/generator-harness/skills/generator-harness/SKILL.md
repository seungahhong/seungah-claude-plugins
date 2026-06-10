---
name: generator-harness
description: >-
  사용자 도메인 요구를 입력받아 '에이전트팀 + 스킬 + 오케스트레이터' 하네스를 자동으로 탐색·평가·생성하는 메타
  오케스트레이터. 다음에 발동한다 — "근거(논문) 기반으로 최적 하네스를 탐색해서 만들어줘", "후보 하네스 여러 개
  뽑아 점수 매기고 제일 나은 걸로", "정확도-비용 Pareto로 하네스 골라줘", "이 도메인용 하네스를 자동 설계·평가해서
  생성", "하네스 후보들 비교·채점해서 최적안 실체화", "여러 설계 중 비용 대비 가장 나은 하네스 자동 선택". 모듈러
  탐색공간(Planning/Reasoning/Tool Use/Memory)에서 후보 N개를 제안 → Pareto(품질×토큰비용)+전이성으로
  채점 → 사용자 승인 → 실체화한다. 모든 후보 실체화는 자동 적용 금지 — 승인 게이트 통과 후에만 적용한다.
  발동하지 않는다 — 사람이 단계별로 직접 같이 만드는 수동 생성(→ harness-generator), 이미 존재하는 하네스의
  결함 진단·trace 기반 개선(→ meta-harness), 단일 스킬 하나 새로 작성·벤치마크(→ skill-creator), 앱/PR
  코드 리뷰·버그 찾기, 기술 문서 새로 작성, settings.json 설정 변경.
---

# Generator Harness — 하네스 자동 탐색·평가·생성 오케스트레이터

## 왜 탐색·평가형 생성인가

하네스 한 묶음을 *한 번에 손으로* 설계하면, 그것이 그 도메인에서 *비용 대비 최선*인지 확인할 길이 없다. 자동 에이전트 설계 연구는 다른 길을 보였다 — 하네스를 코드/모듈 spec으로 정의하면(ADAS, arXiv 2408.08435) 후보 여러 개를 제안·채점해 더 나은 것을 **탐색**할 수 있고(AFlow의 MCTS+execution feedback, arXiv 2410.10762; AgentSquare의 evolution/recombination, arXiv 2410.06153), 그 평가 신호는 단일 정확도가 아니라 **정확도-토큰비용 Pareto**여야 하며(AFlow는 GPT-4o 비용의 4.55%로 특정 태스크 우위), 도메인/모델 **전이성**이 곧 "도메인 무관성"의 검증축이다(MaAS, arXiv 2502.04180). 본 오케스트레이터는 이 네 갈래를 *경량 탐색 루프*로 묶는다 — 후보 제안 → Pareto 채점 → 승인 → 실체화. 출처·반증 caveat는 [references/research-foundations.md](./references/research-foundations.md).

**정직한 주장 범위.** "자동 탐색이 *모든 도메인에서* 수동 설계를 이긴다"는 일반화는 적대적 검증에서 탈락했다. 본 도구는 "*특정 도메인·태스크에서* 후보를 탐색·평가해 비용효율적 하네스를 찾는다"까지만 주장한다. 정답·자동채점기가 없는 개방형 도메인에서는 LLM-as-judge 신뢰성 한계를 명시하고(채점 confidence를 낮춰 보고), 사용자 승인 게이트가 최종 안전망이다.

## 세 도구 분담 (트리거 경계)

| 도구 | 역할 | 본 도구와의 경계 |
|------|------|------------------|
| `harness-generator` | 수동·인터랙티브 7단계 생성 | 사용자가 단계별로 *직접 같이* 만들고 싶어하면 그쪽 |
| `meta-harness` | 기존 하네스 trace 기반 진단·개선 | *이미 있는* 하네스를 고치는 거면 그쪽 |
| **generator-harness** | 후보 자동 탐색 → Pareto 채점 → 승인 → 실체화 | 후보를 *탐색·채점*해 최적안을 *생성*하면 본 도구 |

본 도구는 실체화(Phase 7)에서 harness-generator의 작성 규약(에이전트 정의/스킬/오케스트레이터 형식)을 재사용한다 — 바퀴를 다시 만들지 않는다.

## 실행 모드

- **서브에이전트 + 하이브리드.** 도메인 분석·실체화는 순차 전용 에이전트로, 후보 제안·채점은 병렬 팬아웃으로 spawn한다. 오케스트레이터는 Phase 0 감사, Phase 2 탐색공간 확정, Phase 6 승인 게이트, Phase 8 이력을 직접 수행한다.
- **모든 Agent 호출에 `model: "opus"` 명시.** 추론 품질이 탐색 품질을 좌우한다.
- **조건부 병렬.** 후보 제안(Phase 3)·채점(Phase 4)은 항목이 **독립**이므로 병렬. 도메인 분석(Phase 1)·실체화(Phase 7)는 단건 순차. 진화(Phase 5)는 직전 라운드 결과에 **의존**하므로 라운드 단위 순차. 병렬은 기본값이 아니라 독립성·작업가치 게이트를 통과할 때만 — 멀티에이전트는 토큰 비용이 크다. (근거: Anthropic *Building effective agents* / *multi-agent research system*)
- **비용 게이트.** 탐색 자체의 비용(후보 수 × 라운드 × 채점)은 정량 선례가 없다(open question). 따라서 **경량 탐색이 기본** — 후보 N=3(기본)~5(고가치), 진화 라운드 ≤2. 풀스케일 MCTS/supernet은 사용자가 "철저히 탐색" 명시 시에만.

## 핵심 원칙

- **Pareto가 1차 신호.** 후보는 품질(assertion pass) **단독이 아니라** 품질×토큰비용 좌표로 비교한다. 비용 차원이 빠진 채점은 거절한다. (근거: AFlow 4.55%, MaAS 6~45%)
- **전이성 = 도메인 무관성 검증.** 채택 후보는 최소 1개 인접 도메인/모델 전이 시나리오에서 성능 유지 여부를 함께 본다. 전이가 무너지면 "이 도메인 전용"으로 명시한다. (근거: MaAS cross-dataset/backbone)
- **자동 적용 금지.** 어떤 후보도 Phase 6 승인 게이트 통과 전에는 실체화(파일 생성)하지 않는다. (meta-harness와 동일 DNA, 사용자 메모리 "안전장치 보존")
- **경량 탐색 우선.** 풀스케일 자동탐색은 비용·개방형 평가신호 한계 때문에 디폴트가 아니다. "후보 N개 → 채점 → 승인" 경량 루프로 시작한다.
- **다양성으로 frontier를 넓힌다.** 후보 제안은 동일 프롬프트 N회가 아니라 서로 다른 **lens**(최소비용/최대품질/균형/대담한 구조)로 spawn해 Pareto front를 펼친다. (판단: 동질 후보는 frontier를 못 넓힌다)
- **작성 규약 재사용.** 실체화는 harness-generator의 에이전트·스킬·오케스트레이터 규약과 데이터 스키마를 그대로 따른다(필드명 변형 금지).
- **현황 우선.** 새로 만들기 전에 기존 하네스/스킬과의 트리거 충돌을 먼저 차단한다(Phase 0).

## 산출물 배치 규약

- **탐색 산출(_workspace, 휘발/재실행용)** — `.claude/_workspace/{run}/`:
  - `phase1_domain_spec.json` — 도메인 카드 + 평가셋 + Pareto 축 + 전이 시나리오 (domain-analyst)
  - `candidates/cand_{k}/design.json` — 후보 하네스 설계 (harness-proposer)
  - `candidates/cand_{k}/score.json` — Pareto 좌표 + 전이 + dry-run 채점 (harness-evaluator)
  - `phase6_decisions.json` — 사용자 승인 결정
  - 새 실행 시 직전 회차는 `.claude/_workspace_prev/`로 이동.
- **실체화 산출(영속, 사용자 자산)** — 사용자가 지정한 하네스 위치(플러그인 안이면 `plugins/{plugin}/...`, 레포 루트면 `.claude/{agents,skills}/...`). agents/ · skills/{step}/SKILL.md · 오케스트레이터 · CLAUDE.md 포인터.

평가 데이터 스키마(`eval_metadata.json`/`grading.json`/`timing.json`)는 harness-generator의 표준을 그대로 쓴다 — 상세는 [harness-eval](../harness-eval/SKILL.md).

---

## Phase 0 — 현황 감사 (Audit)

설계 전에 충돌을 차단한다. **확인:** 대상 위치의 `agents/`·`skills/`·`commands/` 존재와 목록, 루트 CLAUDE.md의 기존 하네스 포인터, 동일 도메인 키워드를 쓰는 기존 스킬, `.claude/_workspace/` 잔존 여부.

**분기:**
- `_workspace/` 없음 + 신규 도메인 → **초기 탐색** (Phase 1로)
- `_workspace/` 있음 + 입력 동일 → **부분 재실행** (변경된 Phase만)
- `_workspace/` 있음 + 입력 변경 → **새 실행** (`_workspace_prev/`로 이동 후 재생성)
- 기존 하네스 *개선* 요청 → **meta-harness로 위임 권고** (본 도구는 신규 생성 전용)

감사 결과를 1줄 보고하고 진행 승인을 받는다. 예: `[Phase 0] 초기 탐색 (run-2026-06-10-01). 대상 plugins/research-harness/ 없음, 트리거 충돌 없음.`

## Phase 1 — 도메인 분석 + 평가셋 (domain-analyst, 순차 1회)

도메인 spec과 **평가셋**을 함께 만든다. 평가셋이 본 도구의 키스톤이다 — 채점할 기준이 없으면 탐색이 무의미하다. 모호하면 **한 번에 한 질문**으로 명확화한다(목록 나열 금지).

```
Agent(
  subagent_type="domain-analyst", model="opus",
  prompt="""
  [스킬 경로] plugins/generator-harness/skills/harness-eval/SKILL.md 의 '평가셋 구축' 절을 따른다.
  [입력] 사용자 도메인 요구 원문: {요구}
  [산출] .claude/_workspace/{run}/phase1_domain_spec.json
    { domain_card{purpose, task_types, constraints, recurrence, user_expertise},
      eval_set:[{eval_id, eval_name, prompt, assertions:[...]}],   # 대표 태스크 3~5건
      pareto_axes:{quality:"assertion pass_rate", cost:"total_tokens"},
      transfer_scenarios:[{name, kind:"cross-domain|cross-model", probe}] }  # 1~2건
  [규칙] 정답·자동채점기가 없는 개방형 도메인이면 assertion을 '검증 가능한 관찰'로 쓰고
         eval_set에 그 한계를 notes로 남긴다(LLM-judge confidence 하향 신호).
  """
)
```

**산출 확인:** eval_set이 비었거나 assertion이 검증 불가하면 Phase 1을 반복한다 — 빈 평가셋으로 다음 Phase 진행 금지.

## Phase 2 — 탐색공간 확정 (오케스트레이터 직접)

후보가 탐색될 공간을 정한다. 상세 카탈로그는 [references/building-blocks.md](./references/building-blocks.md).

1. **모듈 축(기본)** — AgentSquare식 Planning / Reasoning / Tool Use / Memory 4모듈 조합. **v0.1 디폴트는 모듈러**다. 무제약 코드합성(ADAS식)은 **코드확장 opt-in 신호**(사용자가 "4모듈 밖 구조도 탐색", "비표준/자유 구조 허용", "코드 수준 자유 설계" 등을 명시)가 있을 때만 연다 — 이 경우에만 후보 design.json의 `custom_structure` 필드를 채워 4모듈 밖 구조를 기술한다. 신호가 없으면 모듈러로 제한한다(말뿐인 옵션 방지).
2. **패턴 축** — Anthropic 5패턴(prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer) ∪ harness-generator 6패턴(+계층적 위임). 둘은 대부분 매핑된다.
3. **실행모드 축** — 에이전트팀 / 서브에이전트 / 하이브리드.
4. **예산** — 후보 수 N(기본 3, 고가치 5), 진화 라운드 상한(기본 2). 작업 가치가 낮으면 N=2로 줄인다.

사용자에게 탐색공간 요약 1줄 + 예산을 보고한다. 예: `[Phase 2] 모듈러 공간, 후보 N=3 (lens: 최소비용/최대품질/균형), 진화 ≤2라운드.`

## Phase 3 — 후보 제안 (harness-proposer, 병렬 팬아웃)

후보 N개를 **서로 다른 lens로** 한 메시지에서 동시 spawn한다(배치 ≤5). 각 proposer는 후보 *설계*만 산출한다(아직 실제 파일 아님).

```
# 한 메시지에서 N개 동시 spawn — 각자 다른 lens
Agent(
  subagent_type="harness-proposer", model="opus", run_in_background=true,
  prompt="""
  [스킬 경로] plugins/generator-harness/skills/harness-search/SKILL.md 방법론을 따른다.
  [탐색공간] .claude/_workspace/{run}/phase1_domain_spec.json + Phase 2 결정(모듈/패턴/모드 축).
  [lens] cand_1 = '최소 토큰비용' (에이전트·단계 최소화, 서브에이전트 선호)
  [산출] .claude/_workspace/{run}/candidates/cand_1/design.json
    { lens, modules{planning,reasoning,tool_use,memory}, pattern, exec_mode,
      agents:[{name, role, io}], orchestrator_phases:[...], data_flow, rationale }
  [규칙] 동질 후보 금지 — 배정된 lens의 trade-off를 끝까지 밀어붙인다.
  """
)
Agent(subagent_type="harness-proposer", model="opus", run_in_background=true,
  prompt="...cand_2 = '최대 품질' (다각 검증·생성-검증 루프 허용, 팀 모드)...")
Agent(subagent_type="harness-proposer", model="opus", run_in_background=true,
  prompt="...cand_3 = '균형' (Pareto knee 겨냥)...")
```

## Phase 4 — 채점 (harness-evaluator, 병렬 팬아웃)

후보별로 **독립** 병렬 채점한다(배치 ≤5). 각 evaluator는 평가셋으로 품질×비용 Pareto 좌표 + 전이성 + dry-run을 산출하고, **적대적으로** 실패 모드를 찾는다.

```
# 후보 수만큼 동시 spawn
Agent(
  subagent_type="harness-evaluator", model="opus", run_in_background=true,
  prompt="""
  [스킬 경로] plugins/generator-harness/skills/harness-eval/SKILL.md 의 'Pareto 채점' 절을 따른다.
  [후보] .claude/_workspace/{run}/candidates/cand_1/design.json
  [평가셋] .claude/_workspace/{run}/phase1_domain_spec.json 의 eval_set + transfer_scenarios
  [산출] .claude/_workspace/{run}/candidates/cand_1/score.json
    { grading{expectations:[{text,passed,evidence}], summary{passed,failed,total,pass_rate}},
      cost{est_total_tokens, agent_count, phase_count},
      pareto_coord{quality:pass_rate, cost:est_total_tokens},
      transfer_score{scenario, held:true|false, note},
      adversarial_failure_modes:[...], dry_run_findings:[...], confidence }
  [규칙] 정답 없는 개방형 도메인이면 confidence를 낮추고 그 이유를 명시한다(LLM-judge 한계).
  """
)
Agent(subagent_type="harness-evaluator", model="opus", run_in_background=true, prompt="...cand_2...")
Agent(subagent_type="harness-evaluator", model="opus", run_in_background=true, prompt="...cand_3...")
```

채점 회신을 모아 **Pareto frontier**를 만든다 — 다른 후보에게 품질·비용 모두에서 지지 않는(비지배) 후보 집합. 지배된 후보는 frontier에서 제외하되 점수는 보존한다.

## Phase 5 — 진화 (선택, 라운드 순차)

frontier에 **acceptance bar(평가셋 pass_rate 임계 + 전이 유지)** 를 넘는 후보가 있으면 **건너뛴다**. 없으면 Pareto-best를 골라 recombination(다른 후보의 우수 모듈 이식)/mutation(약한 모듈 교체)을 적용해 **1라운드 더** 제안·채점한다. 진화 근거·연산자는 harness-search 스킬. **라운드 상한(기본 2) 도달 시 멈추고** 현재 frontier로 Phase 6에 간다 — 무한 탐색 금지(비용 게이트).

## Phase 6 — 사용자 승인 게이트 (필수)

Pareto frontier를 사용자에게 제시한다 — 각 후보의 (품질, 비용, 전이) trade-off + **추천 1개와 그 이유(why-first)**. 사용자가 선택/승인/반려한다. 결정을 `.claude/_workspace/{run}/phase6_decisions.json`에 기록한다.

- **자동 실체화 금지** — 승인 없이는 Phase 7로 가지 않는다.
- 개방형 도메인이라 채점 confidence가 낮으면 그 사실을 먼저 알리고, 사용자가 평가셋/추천을 조정할 기회를 준다.
- 어떤 후보도 bar를 못 넘으면 그대로 보고하고(억지 추천 금지), 탐색공간/예산 확장 또는 harness-generator 수동 생성을 제안한다.

표 형식 예:

| 후보 | lens | 품질(pass_rate) | 비용(토큰) | 전이 | 추천 |
|------|------|-----------------|-----------|------|------|
| cand_3 | 균형 | 0.92 | ~38k | 유지 | ★ (Pareto knee) |
| cand_2 | 최대품질 | 0.96 | ~120k | 유지 | 품질 최우선 시 |
| cand_1 | 최소비용 | 0.80 | ~14k | 부분 | 비용 최우선 시 |

## Phase 7 — 실체화 (harness-materializer, 순차 1회)

승인된 후보 **하나만** 실제 파일로 작성한다. harness-generator의 작성 규약(에이전트 정의 형식, 스킬 < 500줄·Why-First, 오케스트레이터 골격, 데이터 스키마)을 그대로 따른다.

```
Agent(
  subagent_type="harness-materializer", model="opus",
  prompt="""
  [작성 규약] harness-generator 플러그인의 규약을 재사용한다 —
    plugins/harness-generator/skills/harness-generator/references/{agent-design,skill-guide,orchestrator-generate}.md
  [승인 후보] .claude/_workspace/{run}/candidates/{approved}/design.json
  [대상 위치] {사용자 지정 하네스 루트}
  [산출] agents/{name}.md (모두 model:"opus") + skills/{step}/SKILL.md + 오케스트레이터 스킬
         + 대상 CLAUDE.md 하네스 포인터(트리거 규칙 + 변경 이력 1줄)
  [검증] 작성 후 구조 검증(frontmatter name/description, 상호참조, 트리거 should/should-not 8~10개,
         dry-run 1정상+1에러)을 수행하고 결과를 회신한다.
  [금지] commands/ 자동 생성 금지. 기존 스킬과 트리거 충돌 금지.
  """
)
```

## Phase 8 — 이력/진화 (오케스트레이터 직접)

후보·점수·결정을 `.claude/_workspace/{run}/`에 보존한다(재실행·전이용). 실체화한 하네스의 CLAUDE.md Change History에 1줄(절대 날짜)을 남긴다. 사용자에게 1회 피드백을 요청하고, 일반화 가능한 피드백은 해당 표적(평가셋/탐색공간/proposer lens)에 매핑해 다음 실행에 반영한다.

**진화 트리거:** 사용자 명시 재실행, 동일 피드백 2회 반복, 동일 후보가 매번 bar를 못 넘김(→ 평가셋·탐색공간 재검토).

---

## 데이터 전달 전략 매트릭스

| 방식 | 용도 | 위치 |
|------|------|------|
| 파일 기반 | Phase 간 휘발 산출(spec/design/score/결정) | `.claude/_workspace/{run}/...` |
| 반환 기반 | 에이전트 1회 호출 즉시 요약 회신(분기 판단용) | 에이전트 final message |
| 영속 산출 | 실체화된 하네스 자산 | 사용자 지정 하네스 루트 |

## 에러 정책

- **제안/채점 실패** — 해당 후보를 `confidence:low`로 격하하고 frontier 산출 시 제외 후보로 표시. 배치 전체를 막지 않는다(1회 재시도 후 누락 처리, 출처 태그 보존).
- **모든 후보 bar 미달** — 억지 추천 금지. Phase 6에서 그대로 보고 + 탐색공간/예산 확장 또는 harness-generator 수동 생성 제안.
- **평가셋 부재/검증불가** — Phase 1로 회귀. 빈 평가셋으로 탐색 진행 금지.
- **개선 요청 오인** — 기존 하네스 개선이면 meta-harness 위임 권고(본 도구는 신규 생성 전용).
- **비용 초과** — 진화 라운드 상한 도달 시 멈추고 현재 frontier로 승인 게이트 진입.

## 테스트 시나리오

**정상 흐름 — 리서치 보고서 도메인 자동 탐색**
- Phase 0: `_workspace/` 없음 → 초기 탐색 보고.
- Phase 1: domain-analyst가 평가셋 4건 + Pareto 축 + 전이 시나리오 1건 산출.
- Phase 2: 모듈러 공간, N=3(최소비용/최대품질/균형), 진화 ≤2.
- Phase 3: proposer 3명 병렬 → cand_1~3 design.json.
- Phase 4: evaluator 3명 병렬 → score.json. cand_3가 Pareto knee.
- Phase 5: cand_3가 bar 통과 → 진화 건너뜀.
- Phase 6: frontier 표 + cand_3 추천(why) → 사용자 승인.
- Phase 7: materializer가 agents+skills+orchestrator 실체화 + 구조 검증 통과.
- Phase 8: 이력 기록 + CLAUDE.md 1줄. 피드백 요청.

**에러 흐름 — 개방형 도메인 bar 미달**
- Phase 1: 정답 없는 도메인 → assertion '관찰형' + notes 한계, confidence 하향 신호.
- Phase 4: 전 후보 pass_rate < bar, confidence:low.
- Phase 5: 진화 1라운드 → 여전히 bar 미달, 라운드 상한 도달.
- Phase 6: 억지 추천 금지 → "bar 미달" 보고 + 평가셋 조정 또는 harness-generator 수동 생성 제안.
- Phase 7: 승인 없음 → 실체화 0건. Phase 8: 결정 ledger에 미달 기록.

## 참고 자료

- [references/research-foundations.md](./references/research-foundations.md) — ADAS/AFlow/AgentSquare/MaAS/GPTSwarm/Anthropic 인용 + 반증 caveat + 미해결 질문
- [references/building-blocks.md](./references/building-blocks.md) — 모듈러 탐색공간(P/R/T/M) + 패턴 카탈로그(Anthropic 5 ↔ harness-generator 6) + 실행모드
- [harness-search](../harness-search/SKILL.md) — 후보 제안 + evolution/recombination 방법론
- [harness-eval](../harness-eval/SKILL.md) — 평가셋 구축 + Pareto 채점 + 전이성 측정
