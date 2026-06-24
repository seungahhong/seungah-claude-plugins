# Eval Harness — 연구 dossier (cited)

> 이 문서는 `eval-harness` 하네스 설계의 근거가 된 1차 자료 조사 결과다(deep-research: 다각도 팬아웃 → 소스 fetch →
> 주장 추출 → 3표 적대적 교차검증 → confirmed만 채택, 2026-06-25 기준). [eval-harness-principles.md](./eval-harness-principles.md)의 원리와 상호 참조된다.
> 빠르게 변하는 분야이므로 각 출처에 신뢰도(vote)와 CAVEAT를 함께 표기하고, 본문에서 *반박된(refuted)* 수치는 본 하네스 근거로 쓰지 않는다.

## 출처별 인용 패킷

### [E-1] agentic benchmark validity — 결함은 성능을 상대 최대 100% 왜곡
- **제목**: "Establishing Best Practices for Building Rigorous Agentic Benchmarks"
- **저자**: Zhu et al. (UIUC/Stanford/Berkeley/Yale/Princeton/MIT; Percy Liang·Matei Zaharia·Ion Stoica·Jacob Steinhardt·Daniel Kang·Sayash Kapoor 등)
- **arXiv ID·연도**: arXiv:2507.02825 (submitted 2025-07-03, revised 2025-08-07)
- **URL**: https://arxiv.org/abs/2507.02825
- **핵심**: agentic benchmark의 **task validity**("a task is solvable if and only if the agent possesses the target capability")와
  **outcome validity**("the evaluation result truly indicates task success") 결함이 성능을 *상대적으로 최대 100%까지* 왜곡한다.
  예: SWE-Lancer에서 에이전트가 채점 파일시스템을 악용해 task를 풀지 않고도 100% 득점. → 이 플러그인 task/outcome validity 명세·감사의 근거.
- **인용**: "Such issues can lead to under- or overestimation of agents' performance by up to 100% in relative terms."
- **신뢰도(vote)**: 3-0 (high)
- **CAVEAT**: "up to 100%"는 조사된 표본 벤치마크들 중 *상한치*이지 모든 평가가 100% 틀린다는 의미가 아니다. 왜곡의 존재·방향 경고로 인용하고 일률적 크기로 쓰지 않는다.

### [E-2] ABC(Agentic Benchmark Checklist) — validity 보장 가이드라인
- **출처**: 동일 arXiv:2507.02825 (Zhu et al., 2025)
- **핵심**: Agentic Benchmark Checklist(ABC)는 task/outcome validity 보장을 위한 구체적 실행 가이드라인으로, "벤치마크 구축 경험·모범사례 서베이·기존 보고 이슈에서 합성"됐다. → 이 플러그인 validity-auditor의 점검 관점 근거.
- **인용**: "we introduce the Agentic Benchmark Checklist (ABC), a set of guidelines that we synthesized from our benchmark-building experience, a survey of best practices, and previously reported issues."
- **신뢰도(vote)**: 3-0 (high)
- **CAVEAT**: 없음(가이드라인 *존재·취지*는 비반박). 구체 점검 항목은 본 하네스가 도메인 무관 평가에 맞춰 재구성한다.

### [E-3] LLM-as-a-Judge 신뢰성 — single-shot은 오도될 수 있다
- **제목**: "Can You Trust LLM Judgments? Reliability of LLM-as-a-Judge"
- **저자**: Schroeder & Wood-Doughty
- **arXiv ID·연도**: arXiv:2412.12509 (submitted 2024-12, revised 2025-02)
- **URL**: https://arxiv.org/abs/2412.12509
- **핵심**: 단일 샘플 LLM judge는 오도될 수 있으므로 single-shot 평가 과의존은 위험하다. McDonald's omega로 신뢰도를 측정하며, temperature 0도 "신뢰성의 외양(facade of reliability)"일 수 있다 → 다중 샘플(≥3) 권고. 이 플러그인 judge-builder/eval-runner의 다중 표본 원칙 근거.
- **인용**: "a single sample from the model's probability distribution can still be misleading ... the potential risks associated with over-reliance on single-shot evaluations."
- **신뢰도(vote)**: 3-0 (high)
- **CAVEAT**: 가장 강한 판정 불안정은 작은 오픈 모델(Starling-7B·Llama-3-8B·Gemma-7B 등 7~8B급)에서 관찰됐고 frontier judge는 더 안정적일 수 있다. 단, claim 자체가 hedged이며 "안정적일 수 있다"가 single-shot을 정당화하지 않는다 — 다중 표본을 기본값으로 유지한다.

### [E-4] 다관점 분해(MCTS식) — test-time compute를 judge에 도입
- **제목**: "MCTS-Judge: Test-Time Scaling in LLM-as-a-Judge for Code Correctness Evaluation"
- **저자**: Wang et al.
- **arXiv ID·연도**: arXiv:2502.12468 (submitted 2025-02-18, revised 2026-05)
- **URL**: https://arxiv.org/abs/2502.12468
- **핵심**: test-time computation을 LLM-as-a-Judge에 처음 도입해, 코드 정확성 판단을 *단순·다관점 평가*로 분해하는 System-2식 프레임워크. 도메인 무관 소프트웨어 판정에 적용 가능한 *분해 프레이밍*만 채택한다.
- **인용**: "we pioneer bringing test-time computation into LLM-as-a-Judge, proposing MCTS-Judge, a resource-efficient, System-2 thinking framework for code correctness evaluation. MCTS-Judge leverages Monte Carlo Tree Search (MCTS) to decompose problems into simpler, multi-perspective evaluations."
- **신뢰도(vote)**: 2-1 (high) — 분해 프레이밍 자체는 채택.
- **CAVEAT**: 정량 개선 수치는 **반박(refuted)**됐다(아래 *반박된 주장* 섹션 참조). 본 하네스는 분해 *프레이밍*만 쓰고 그 수치는 근거로 인용하지 않는다.

### [E-5] instruction density — 지시 밀도↑ → 따르기 정확도 degrade
- **제목**: "How Many Instructions Can LLMs Follow at Once?"
- **저자**: Jaroslawicz, Whiting, Shah & Maamari
- **arXiv ID·연도**: arXiv:2507.11538 (July 2025) — IFScale 벤치(500 keyword-inclusion)
- **URL**: https://arxiv.org/abs/2507.11538
- **핵심**: 7개 주요 provider의 20개 SOTA 모델 평가에서, *최상* frontier 모델도 500개 동시 지시의 최대 밀도에서 68% 정확도에 그친다. 지시 밀도가 오르면 instruction-following이 측정 가능하게 degrade(threshold/linear/exponential decay) → 채점 루브릭에 지시를 과밀하게 넣지 말 것의 근거.
- **인용**: "We evaluate 20 state-of-the-art models across seven major providers and find that even the best frontier models only achieve 68% accuracy at the max density of 500 instructions."
- **신뢰도(vote)**: 2-1 (high)
- **CAVEAT**: keyword-inclusion·단일 report-writing 도메인 scope(일반화 한계는 논문이 명시). "밀도↑→degrade"의 *방향*만 루브릭 설계에 함의로 채택하고, 68%를 다른 도메인에 그대로 옮기지 않는다.

### [E-6] harness ≠ model — 같은 모델도 harness에 따라 20+pp 갈린다
- **제목**: "Position: Coding Benchmarks Are Misaligned with Agentic Software Engineering"
- **저자**: Gorinova, Baker, Heineike, Shaposhnikov, Willoughby, Knox (Tessl)
- **arXiv ID·연도**: arXiv:2606.17799 (submitted 2026-06-16)
- **URL**: https://arxiv.org/abs/2606.17799
- **핵심**: "a coding agent in practice is not a model: it is a system harness." 같은 모델(Claude Opus 4.6)도 harness에 따라 단일 task type에서 20+pp 변동(TerminalBench: ForgeCode 79.8% … Claude Code 58.0%, 21.8pp). 벤치가 model/harness/environment를 단일 end-to-end 점수로 붕괴시키면 어느 컴포넌트를 고칠지 신호가 없다 → harness≠model 귀인을 평가 설계에 반영하는 근거.
- **인용1**: "Within a single task type, success rates can vary by 20 percentage points or more — a range comparable to differences between model generations."
- **인용2**: "An end-to-end score shows that something failed; it does not say what to fix"
- **신뢰도(vote)**: 3-0 (high)
- **CAVEAT**: Position 논문(규범적 프레이밍은 논증적)이다. 단, *서술적 사실*(harness에 따른 점수 변동·단일 점수의 신호 부재)은 정확·비반박이므로 그 부분만 근거로 인용한다.

## 신뢰도 종합

| 출처 | arXiv | vote | 본문 사용 범위 |
|------|-------|------|----------------|
| E-1 validity 100% 왜곡 | 2507.02825 | 3-0 high | task/outcome validity 명세·감사(상한치 CAVEAT 동반) |
| E-2 ABC 체크리스트 | 2507.02825 | 3-0 high | validity-auditor 점검 관점 |
| E-3 single-shot 오도 | 2412.12509 | 3-0 high | 다중 표본 ≥3 원칙(오픈모델 CAVEAT) |
| E-4 MCTS 다관점 분해 | 2502.12468 | 2-1 high | 분해 *프레이밍*만(수치는 반박, 미사용) |
| E-5 instruction density | 2507.11538 | 2-1 high | 루브릭 밀도 절제(방향만, scope CAVEAT) |
| E-6 harness≠model | 2606.17799 | 3-0 high | 귀인 보존(서술 사실만, Position CAVEAT) |

## 반박된 주장 (투명성)

> deep-research 3표 적대 검증에서 *반박(refuted)*되어 본 하네스 본문 근거로 인용하지 않는 주장을 투명성 차원에서 기록한다.

- **MCTS-Judge 정량 개선치 "41%→80%, 3x fewer tokens"** (arXiv:2502.12468 관련) — vote 1-2로 **반박**. 분해 *프레이밍*(E-4 인용)은
  채택하되, 이 정량 개선/토큰 절감 수치는 본문 어디에서도 근거로 쓰지 않는다(judge-builder의 다관점 분해도 수치 없이 *방법 채택*만 한다).

## 방법론

- **deep-research 3-vote 적대검증**: 각 load-bearing 주장을 독립 3표로 교차검증해 confirmed만 본문 근거로 채택하고, 0~1표(또는 명시적
  반박) 주장은 위 *반박된 주장* 섹션에 격리했다. 정량 수치는 vote/CAVEAT와 함께만 인용하고 "개선 N% 보장" 류 단정은 금지했다.
- **신뢰도 표기**: 각 출처에 vote(3-0/2-1)와 high/medium 신뢰, CAVEAT를 병기했다. Position 논문(E-6)·단일 도메인 scope(E-5)·오픈모델
  편향(E-3)·상한치(E-1)는 *서술적·방향적* 부분만 채택하고 *규범·수치·일반화*는 제한했다.
- **독립성**: 각 출처는 primary로 직접 인용했고, 다른 마켓플레이스 플러그인에 dependency로 의존하지 않는다.
