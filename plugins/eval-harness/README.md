# eval-harness

AI 생성물(코드·에이전트 출력·산출 텍스트)을 **믿을 수 있게 평가**하는 도메인 무관 멀티 에이전트 하네스입니다.
핵심 질문은 "점수가 몇 점인가"가 아니라 **"이 점수를 믿어도 되는가"** 입니다 — *누가·어떻게·몇 번* 채점하면
결과를 신뢰할 수 있는지를 설계하고, 평가가 진짜 능력을 재는지 감사한 뒤, 다중 표본을 집계해 신뢰도와 함께 보고합니다.

## 평가의 네 가지 신뢰 축

- **validity(타당성)** — 측정하려는 것이 측정 가능하게 정의돼 있고(task validity), 그 측정이 실제 성공을 가리키는가(outcome validity).
- **judge 신뢰성** — 단일 샷 판정은 오도될 수 있습니다. 다중 표본(≥3)·다관점 분해·실행 grounding으로 판정을 강화합니다.
- **shortcut 내성** — 에이전트가 과제를 *실제로 풀지 않고도* 만점을 받는 우회로(환경 악용·정답 누출)를 막습니다.
- **귀인(attribution)** — 점수가 model 때문인지 harness 때문인지. 단일 end-to-end 점수는 *무엇이 실패했는지*만 알려주고 *무엇을 고칠지*는 말하지 않습니다.

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `eval-harness` 플러그인을 활성화하면,
`eval-harness` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `eval-harness` | 오케스트레이터(진입점). 평가 대상·validity 정의(Eval Spec) → judge 구성(다중 표본) → validity 감사 → 실행·집계·보고의 4단계를 진행하며, 각 단계에서 전용 에이전트(eval-designer / judge-builder / validity-auditor / eval-runner)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Define & Validity | `eval-designer` | 평가 대상·관찰형 성공기준 정의 + task/outcome validity 명세 + 귀인 단위 |
| 1 Build Judge | `judge-builder` | judge 구성(다중 표본 ≥3 + 다관점 분해 + 가능하면 실행 grounding), single-shot 금지 |
| 2 Audit Validity | `validity-auditor` | ABC 관점 감사(validity·shortcut·harness≠model 귀인·instruction density), BLOCK 게이트 |
| 3 Run & Report | `eval-runner` | 다중 표본 실행·집계 + confidence + CAVEAT 보고(단일 샷 신뢰 금지) |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- LLM/에이전트 출력이나 코드 정확성을 **신뢰할 수 있게 채점**하고 싶을 때(judge가 한 번 매긴 점수를 못 믿겠을 때)
- 평가/벤치마크가 **진짜 능력을 재는지**(task validity·outcome validity) 점검하고, 과제를 풀지 않고 만점 받는 shortcut을 막고 싶을 때
- 점수가 **모델 때문인지 harness 때문인지** 분리하고, 결과를 confidence·CAVEAT와 함께 받고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖 — 일반 개념으로만 서술합니다)**
- 모델에 넣을 **컨텍스트 페이로드 조립·압축·정렬**(컨텍스트 최적화) — 이 하네스는 *나온 결과를 채점*합니다
- 한 작업을 **여러 에이전트로 병렬화할지/어떻게 묶을지** 판단(토폴로지 설계)
- **엔지니어용 실행가능 구현 명세 작성**(에이전트가 코드 생성할 contract)
- 기존 코드의 **일반 실행 테스트 생성**(평가 신뢰성 설계가 아닌 단순 테스트 작성) — 단, judge가 실행 grounding으로 테스트를 *돌려* 채점에 쓰는 것은 이 하네스의 일부입니다
- **커밋 메시지 작성·PR 코드 리뷰**

경계가 모호하면 한 질문으로 확인합니다 — "점수를 *신뢰할 수 있게 채점·감사*하려는 건가요(이 하네스), 아니면 *컨텍스트 구성/병렬화 판단/구현 명세 작성* 같은 다른 단계가 필요한가요?"

## 5단계 사용법

1. **정의·validity (Phase 0)** — `eval-designer`가 "이거 평가해줘"를 Eval Spec(평가 대상·관찰형 성공기준·task/outcome validity·귀인 단위·범위)으로 변환합니다. **승인 게이트**: 잘못 정의된 평가로 비용을 낭비하지 않기 위해 여기서 한 번 멈춥니다.
2. **judge 구성 (Phase 1)** — `judge-builder`가 judge를 단일 샷이 아니라 **다중 표본(≥3)**으로, 가능하면 다관점 분해 + 실행 grounding으로 구성합니다.
3. **validity 감사 (Phase 2)** — `validity-auditor`가 judge를 *돌리기 전에* task/outcome validity 위반·shortcut·harness≠model 귀인 혼동·instruction density 과다를 적대적으로 감사합니다. 위반이 있으면 **BLOCK**(거짓 결과를 생산하기 전에 차단)하고 수정 후 재감사합니다.
4. **실행·집계 (Phase 3)** — `eval-runner`가 감사를 통과한 judge를 **다중 표본으로 실행·집계**하고, 표본 분산을 confidence로 환산합니다.
5. **보고** — 결과를 **confidence와 CAVEAT**(validity 잔여 위험·grounding 유무·harness≠model 귀인 한계·instruction density)와 함께 받습니다. 비교는 *baseline 대비*로만 제시하고 "개선 N% 보장" 같은 단정은 하지 않습니다.

## 도구 경계 (요약)

이 하네스는 **AI 생성물의 판정 신뢰성**(누가·어떻게·몇 번 채점하면 결과를 믿을 수 있는가)에 특화합니다.
컨텍스트 최적화·병렬화 판단·구현 명세 작성·일반 테스트 생성·커밋/PR 리뷰는 *다른 단계*이며 일반 개념으로만 언급하고
특정 다른 도구에 의존하지 않습니다. 평가의 *신뢰성*이 아니라 *다른 작업*이 필요하면 그 단계에 맞는 도구를 쓰세요.

## 근거 논문 (deep-research dossier)

설계 근거는 2024+ 1차 논문에서 3표 적대 검증으로 confirmed된 주장만 채택했습니다(상세·인용·신뢰도·CAVEAT는
[skills/eval-harness/references/eval-harness-research.md](skills/eval-harness/references/eval-harness-research.md)).

- **arXiv:2507.02825** — "Establishing Best Practices for Building Rigorous Agentic Benchmarks" (Zhu et al., 2025) — task/outcome validity, ABC 체크리스트, validity 결함의 상대 최대 100% 왜곡(상한치).
- **arXiv:2412.12509** — "Can You Trust LLM Judgments? Reliability of LLM-as-a-Judge" (Schroeder & Wood-Doughty, 2024/2025) — single-shot 오도 위험, 다중 표본(≥3) 권고, temp-0의 "facade of reliability".
- **arXiv:2502.12468** — "MCTS-Judge: Test-Time Scaling in LLM-as-a-Judge for Code Correctness Evaluation" (Wang et al., 2025) — 판정을 단순·다관점 평가로 분해하는 *프레이밍*(정량 개선치는 반박되어 미사용).
- **arXiv:2507.11538** — "How Many Instructions Can LLMs Follow at Once?" (Jaroslawicz et al., 2025) — 지시 밀도↑ → instruction-following degrade(최상 모델도 500개 지시에서 68%).
- **arXiv:2606.17799** — "Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering" (Gorinova et al., 2026) — harness≠model 귀인, 같은 모델도 harness에 따라 20+pp 변동, 단일 end-to-end 점수는 *무엇을 고칠지* 신호 없음.

## evals

- `evals/evals.json` — 수용 평가(design-conformance dry-run): shipped 파일이 핵심 불변식(validity 우선·single-shot 금지·shortcut 감사·harness≠model 귀인·confidence/CAVEAT·승인 게이트·경계)을 명세·강제하는지 file:section 인용으로 점검합니다.
- `evals/trigger-eval.json` — 트리거 경계 평가: 발동해야 하는 경우(should-trigger)와 인접 도메인(컨텍스트 최적화·병렬화 판단·구현 명세 작성·일반 테스트 생성·커밋/PR 리뷰 등)에서 발동하면 안 되는 경우(should-not-trigger)를 정의해 트리거 정확도를 점검합니다.
