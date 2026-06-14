# Loop Engineering — 원리 · 검증기/중단조건 설계 · anti-pattern

> 이 문서는 loop-engineering 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.

## 1. 무엇이 loop engineering인가

프롬프트 엔지니어링은 *한 번의 입력*을 다듬는다. 컨텍스트 엔지니어링은 *모델 주변에 채울 정보*를 다듬는다.
**loop engineering은 에이전트가 도는 *반복 루프 그 자체*를 설계한다** — 목표·실행·검증·진단·개선·메모리·중단조건을.

전환점은 이것이다: **사람이 프롬프트를 직접 작성하기보다, 에이전트가 프롬프트를 작성하게 해야 하는 시점.**
루프를 구성하고 → 명확한 목표를 주고 → 스스로 테스트하게 하고 → 실패하면 개선 프롬프트를 쓰게 하고 →
개선 결과를 검증하고 → 다음에 실패하지 않도록 메모리에 쌓고 → **위 과정을 계속 반복**한다.

## 2. 두 개의 루프

### 실행 루프 (한 작업을 통과시키는 사이클)
1. **목표를 정한다** — 검증 가능한 단일 목표.
2. **에이전트가 실행한다** — 목표를 향한 최소 변경 1회.
3. **에이전트가 검증한다** — 검증 방법을 실제로 돌려 PASS/FAIL.
4. **실패하면 다시 고친다** — 단, *원인을 먼저 파악한 뒤*.
5. **통과하면 종료한다** — 중단조건 충족 시에도 종료.

### 지속학습 루프 (루프가 회차마다 똑똑해지는 사이클)
- **실패(Fail)** — 실수를 하고 *기록*한다.
- **조사(Investigate)** — 다음 단계로 넘어가기 전에 *원인을 파악*한다.
- **검증(Verify)** — 진단을 *확인된 사실*로 전환한다.
- **정립(Distill)** — 검증 결과를 *일반적인 규칙*으로 정리한다.
- **참조(Consult)** — 규칙을 다시 도출하는 대신 *이미 정립된 규칙을 참고*한다.

두 루프는 한 사이클로 맞물린다 — 실행 루프의 "검증/고치기"가 곧 지속학습 루프의 "조사/검증/정립"을 낳고,
정립된 규칙은 다음 실행 루프의 "실행"에서 참조된다.

## 3. 좋은 루프의 7원칙

1. **검증기 우선(verifier-first)** — 루프는 검증기만큼만 좋다. 관찰형 성공기준 + *실행 가능한* 검증 방법을 시작 전에 못 박는다. 검증기가 약하면 거짓 PASS로 잘못 종료하거나, 무엇이 통과인지 몰라 영원히 돈다.
2. **자가 검증(self-verification)** — 통과 판정을 사람이 아니라 에이전트가, 증거로 한다. 추정 PASS 금지.
3. **재시도 전 진단(diagnose-before-retry)** — 실패하면 곧장 다시 시도하지 않는다. 증상이 아닌 root cause를 먼저 확정한다.
4. **에이전트가 개선안을 쓴다(agent-authored next step)** — 다음 반복의 접근을 사람이 아니라 에이전트가 작성한다.
5. **최소 변경(one hypothesis per iteration)** — 한 반복에 가장 작은 변경 하나. 변경이 섞이면 원인 격리가 불가능(confound).
6. **지속학습 메모리 — 단, quality-gated(continual learning, fragile)** — 검증된 교훈만 distill해 쌓고 다음에 관련 규칙만 consult한다. 같은 실수를 두 번 하지 않는 것이 루프의 복리 효과다. **단, 순진한 distill은 성능을 *악화*시킬 수 있다**(§6 anti-pattern, faulty-memory 연구). 그래서 distill은 자유로운 자기개선 엔진이 아니라 *검증 게이트가 달린 fragile 메커니즘*으로 다룬다 — verbatim rewrite보다 추상 통찰을 적고, raw 원본을 경쟁 baseline으로 보존하며, 나쁜 규칙은 폐기·롤백 가능해야 한다.
7. **명시적 중단조건(explicit stopping)** — 통과·최대 반복·무진전·예산. 무한 루프와 비용 폭주를 구조적으로 막는다. (검증 가능한 목표·하드 중단·메모리가 없으면 루프는 "그냥 cron job"이다 — Osmani.)

## 4. 검증기(verifier) 설계

> 근거: "잘 설계된 루브릭이 모델보다 더 많은 일을 한다. 자가수정은 환경 피드백이 정직할 때만 의미가 있다"(Lance Martin).
> 검증기가 약하면 좋은 모델이라도 *확신에 차서 틀린 루프*가 된다. 검증기 품질이 모델 능력보다 한계 병목이다.

- **generator/checker 분리(핵심)**: 만드는 에이전트(`loop-executor`)와 판정하는 에이전트(`loop-verifier`)를 *다른 컨텍스트로 분리*한다. 같은 컨텍스트에서 자기 산출물을 평가하면 "확신에 차서 자기 작업을 칭찬"하는 편향이 생긴다(Anthropic harness-design). self-critique 금지. 회의적인 독립 평가자를 튜닝하는 게 생성자를 자기비판적으로 만드는 것보다 쉽다. (`/goal`은 이를 별도 Haiku 평가자로 구조적으로 구현한다.)
- **기계검증 증거를 출력에 surface**: 평가자가 transcript만 보는 경우(`/goal`)를 대비해, 실행자는 테스트 종료코드·diff·카운트 같은 *기계검증 가능한 증거*를 출력에 드러내야 판정이 자기보고가 아닌 근거를 갖는다. 본 하네스의 `loop-verifier`는 한 발 더 나아가 검증 방법을 *실제로 실행*하는 강한 버전이다.
- **실행 가능성**: 각 성공기준은 "어떻게 확인하나"를 *실제로 돌릴 수 있는* 방법으로 가져야 한다 — 명령의 종료코드, 출력에 특정 문자열, 테스트 그린, 파일/심볼 존재, HTTP 200, 산출물의 관찰 가능한 속성.
- **관찰형만**: "좋다 / 자연스럽다 / 직관적이다"는 판정 불가 → 관찰형으로 환산하거나 제외.
- **기준별 분해**: 큰 목표를 C1, C2…로 쪼개 각각 PASS/FAIL을 내면 진단 표적이 좁아진다.
- **적대성**: 검증기는 통과를 의심한다. 먼저 실패할 이유를 찾고, 못 찾을 때만 PASS.
- **검증 인프라 ≠ 작업 결함**: 검증 방법 자체가 안 돌면(환경 문제) 작업 실패와 분리한다(거짓 FAIL 방지).
- **자동 불가 시**: 정말 자동 검증이 불가능하면 사람이 판정할 체크리스트로 대체하고 "수동 검증"임을 명시(자율 신뢰도 한계 표시).

## 5. 중단조건(stopping) 설계

좋은 중단조건은 **출력만으로 확인 가능**해야 하며, 내구적 조건은 보통 3요소를 갖는다(/goal docs):
① **측정 가능한 end state**(테스트 결과·빌드 종료코드·파일 수·빈 큐), ② 그것을 **어떻게 증명하는지 명시한 체크**("npm test가 0 종료", "git status가 clean"), ③ **바뀌면 안 되는 제약**("다른 테스트 파일은 수정 금지"). goal-setter의 Goal Card가 이 형태를 따른다.

- **성공**: 모든 성공기준 PASS — 유일한 "좋은" 종료.
- **최대 반복(N)**: 기본 5. 작업 난도·예산에 따라 조정. 도달 시 멈추고 부분 결과·교훈을 보고. (조건에 "or stop after N turns"를 넣어도 되지만 이는 *모델 판단*이지 하드 정지가 아니다 — 보장된 경계가 필요하면 SDK `max_turns`(도구 사용 turn만 카운트)·`max_budget_usd` 하드 캡을 쓴다.)
- **무진전(no-progress)**: 같은 root cause가 M회(기본 2) 반복되면 단순 재시도를 멈춘다. 같은 곳을 더 돌아도 통과하지 못한다 — 구조 변경(목표 재정의·접근 전면 교체·사람 개입)이 답이다.
- **예산**: 토큰/시간/달러 상한. 기본값은 보통 "무제한"이라 캡은 opt-in 안전장치다. 초과 시 멈추고 현황 보고.

## 6. anti-pattern (피해야 할 것)

- **검증기 없는 루프** — "잘 됐나?"를 사람이 매번 눈으로 보는 루프는 loop engineering이 아니다.
- **진단 없는 재시도** — 같은 실패를 원인도 모른 채 다시 시도(가장 흔한 실패).
- **거대 변경** — 한 반복에 여러 가설을 한꺼번에 → 실패해도 원인을 못 가린다.
- **메모리 미적재** — 회차마다 같은 실수를 반복. distill/consult가 없으면 루프가 똑똑해지지 않는다.
- **순진한 distill(역효과 메모리)** — 검증 게이트 없이 경험을 텍스트 규칙으로 마구 distill하면 성능이 *오히려 악화*된다. faulty-memory 연구: GPT-5.4가 메모리 없이 100% 풀던 문제가 *자기 정답에서* consolidate한 뒤 54%로 붕괴("trajectory는 완벽한데 rewrite 단계가 망가뜨린다"). CL-Bench: 전용 메모리 시스템보다 순진한 ICL이 총합 성능이 낫다. → distill은 검증된 것만, 추상 통찰 우선, raw 보존, 가역적으로(§3 원칙 6). *단, consolidation 전면 폐기도 틀렸다*("raw-only가 최고"는 반박 0-3) — 핵심은 quality-gated distillation.
- **요약으로 진단** — raw trace를 버리고 요약만 남기면 root cause 증거가 사라진다. trace는 보존, 교훈만 distill.
- **무한 루프** — 중단조건 부재. 통과 못 하는 목표를 영원히 돈다.
- **낙관 PASS** — 증거 없이 "통과한 것 같다"로 종료.
- **목표 드리프트** — 반복을 거듭하며 검증기와 무관한 변경으로 새는 것.

## 7. Claude Code에서의 실행 토대

- **`/goal`(native)** — 기본 제공 목표 지향 자율 진행. 이 하네스는 그 위에 검증기 설계·재시도 전 진단·지속학습 메모리·무진전 감지를 멀티 에이전트로 구조화해 얹는다.
- **`/loop`(native)** — *시간 간격* 재실행(폴링). 이 하네스의 *목표 기반 자가수정 반복*과 구분된다.
- **subagent(model:opus)** — 실행/검증/진단/메모리를 역할별 에이전트로 분리해 각자 한 가지를 잘하게 한다.
- **파일 기반 메모리** — `.claude/loop-memory/`에 trace(원본)와 lessons(distill)를 분리 보관해 회차·세션을 넘어 학습을 누적한다.

## 참고 문헌

출처별 구체 인용·신뢰도·caveat·반박 주장은 **[loop-engineering-research.md](./loop-engineering-research.md)**(deep-research dossier: 23 소스 → 110 주장 → 25 적대적 교차검증 → 23 confirmed)에 정리되어 있고, 이 문서의 원칙과 상호 참조된다.

1차(primary): Claude Code `/goal`·Agent SDK `agent-loop`·`memory` 공식 문서 · Anthropic "Harness design for long-running application development"(generator/checker 분리) · CL-Bench(arXiv:2606.05661, 사용자 제공 "Continual Learning Bench") · AgentCL(arXiv:2606.02461) · SEA(arXiv:2604.07269) · faulty-memory(dylanzsz.github.io/faulty-memory) · OpenAI parameter-golf.
2차/blog(verbatim 교차검증): Addy Osmani "Loop Engineering"(정의·cron job 구분) · Lance Martin "Designing loops with Fable 5"(rubric>model, verifier 분리, Fail→Investigate→Verify→Distill→Consult 5단계, 402 paywall→다중 2차로 검증) · Peter Steinberger(@steipete) · Boris Cherny/Cat Wu(theneuron.ai 해설).

> 핵심 caveat(dossier 참조): "verifier 89%/62%" 수치는 1차 미확인(과장 추정); "순진한 ICL이 메모리를 이긴다"는 CL-Bench 한정(보편 아님); faulty-memory는 격리 스트레스 테스트; /goal 평가자는 transcript만 보고 도구 미사용 → 보장 경계는 SDK 캡.
