# Loop Engineering — 연구 dossier (cited)

> 이 문서는 `loop-engineering` 하네스 설계의 근거가 된 1차/2차 자료 조사 결과다(deep-research: 5각도 팬아웃 → 23개 소스 fetch
> → 110개 주장 추출 → 25개 적대적 교차검증 → 23개 confirmed / 2개 killed, 2026-06-14 기준). [loop-engineering-principles.md](./loop-engineering-principles.md)의 원칙과 상호 참조된다.
> 빠르게 변하는 분야이므로 각 절 끝에 신뢰도와 caveat을 함께 표기한다.

## 1. loop engineering이란 — 프롬프트/컨텍스트 엔지니어링과의 구분

**loop engineering = "에이전트에게 프롬프트를 주는 사람(나)을 대체하는 것 — 대신 그 일을 하는 *시스템*을 설계한다."**
루프는 "재귀적 목표(recursive goal)"로, 목적을 정의하면 AI가 완료될 때까지 자율 반복한다. 이것은 프롬프트 엔지니어링
(개별 프롬프트를 다듬기)과도, 컨텍스트 엔지니어링(윈도우에 무엇을 채울지 관리)과도 구분된다 — loop engineering은 *반복 시스템 자체*를 설계한다.

다만 "루프"라고 다 같은 게 아니다. **검증 가능한 목표 + 하드 중단조건 + 메모리**가 없으면 루프는 "그냥 cron job"으로 전락한다.
(신뢰도 high, 3-0) — Addy Osmani "Loop Engineering"(addyosmani.com/blog/loop-engineering), theneuron.ai의 Boris Cherny/Cat Wu 해설, Louis Bouchard "cron job" 구분.

## 2. 두 개의 루프 (control flow + 지속학습)

### 실행 루프 (Claude Code Agent SDK 표준)
공식 Agent SDK 문서의 "The loop at a glance": **프롬프트 수신 → 평가·응답 → 도구 실행 → (2~3 반복; 한 사이클=1 turn) → 결과 반환.**
자연스러운 **중단 신호 = 에이전트가 도구 호출 없이 텍스트 응답을 내놓는 순간.** 검증은 에이전트가 루프 안에서 *자기 테스트를 돌려*
결과에 따라 자가수정하는 것으로 이뤄진다. (워크드 예시: "auth.ts의 실패 테스트를 고쳐라" → npm test(3 실패) → 소스 읽기 →
수정+재실행(통과) → 텍스트 응답으로 종료.) (신뢰도 high, 3-0) — code.claude.com/docs/en/agent-sdk/agent-loop.

### 지속학습 루프 (5단계, 세션을 넘어 유지)
Lance Martin "Designing loops with Fable 5"가 명시한 5단계: **Fail(실수하고 기록) → Investigate(근본 원인 파악) →
Verify(진단을 확인된 사실로 전환) → Distill(재사용 가능한 일반 규칙으로 일반화) → Consult(다음엔 재도출 대신 저장된 규칙을 참조).**
각 실수를 *대화 밖*의 내구적 산출물(CLAUDE.md, skill, auto memory, 마크다운 상태 파일)로 바꿔 같은 실수를 반복하지 않게 한다.
공식 메모리 문서도 "Claude가 같은 실수를 *두 번째로* 했을 때 CLAUDE.md에 추가", "여러 단계 절차는 skill로" 로 보강한다.
(신뢰도 high, 3-0 / 일부 2-1) — Martin 기사(verbatim 인용, 다중 2차 출처), theneuron.ai, code.claude.com/docs/en/memory.
> caveat: 메모리는 "강제 설정이 아니라 context"이며 "엄격 준수 보장이 없다." 트리거는 보통 *반복된* 실수다("every mistake"는 이상화된 표현).

## 3. 좋은 루프 — 검증기·중단조건 설계

### 검증기(verifier): generator/checker 분리가 핵심
- **"잘 설계된 루브릭이 모델보다 더 많은 일을 한다." 자가수정은 환경 피드백이 정직할 때만 의미가 있다.** 고성능 모델일수록
  직접 프롬프팅·조종보다 *환경 피드백으로 자가수정하는 루프*를 설계하는 게 낫다. (신뢰도 medium, 3-0/2-1) — Lance Martin.
- **독립 verifier 서브에이전트를 써라(self-critique 금지).** 같은 컨텍스트에서 자기 산출물을 평가하면 "확신에 차서 자기 작업을
  칭찬"하는 편향이 생긴다. 만드는 에이전트와 판정하는 에이전트를 분리하는 것이 "강력한 레버"이고, *회의적인 독립 평가자를 튜닝하는 것이
  생성자를 자기비판적으로 만드는 것보다 훨씬 다루기 쉽다.* (신뢰도 high, 2-1 + 1차 보강) — Martin + Anthropic "Harness design for
  long-running application development"(Prithvi Rajasekaran). > caveat: 일부 2차가 붙인 "89% vs 62%" 수치는 1차에 없음(과장 추정) — 정성적 주장만 채택.
- **/goal은 이 분리를 구조적으로 구현한다.** 매 turn 후 *별도의 작은 빠른 모델*(기본 Haiku — 일하는 모델이 아닌 신선한 평가자)이
  대화 transcript를 보고 사용자가 작성한 boolean 완료조건이 성립하는지 yes/no + 사유를 낸다. "no"는 사유를 다음 turn 지침으로 실어
  루프 지속, "yes"는 목표 해제. (신뢰도 high, 3-0) — code.claude.com/docs/en/goal.
  > 중요: 이 평가자는 **도구를 못 쓰고 transcript만** 본다. 따라서 에이전트가 *기계 검증 가능한 증거(테스트 종료코드·diff·카운트)를
  > 출력에 surface*해야 yes/no가 근거를 갖는다. (Martin이 권한 "도구를 가진 verifier 서브에이전트" 패턴이 이를 보완 — 본 하네스의
  > `loop-verifier`는 검증 방법을 *실제로 실행*하는 강한 버전이다.)

### 중단조건(stopping): 무한 루프 방지
좋은 중단조건은 **출력만으로 평가자가 확인 가능**해야 하며 보통 3요소를 갖는다 — ① 측정 가능한 end state(테스트 결과·빌드 종료코드·파일 수·빈 큐),
② 그것을 어떻게 증명하는지 명시된 체크(예: "npm test가 0 종료", "git status가 clean"), ③ 바뀌면 안 되는 제약(예: "다른 테스트 파일은 수정 금지").
무한/폭주 방지: 조건에 turn/time 절을 넣고("or stop after 20 turns") 매 turn 진척을 보고하게 하거나, SDK 캡 `max_turns`(도구 사용 turn만 카운트)·
`max_budget_usd`를 쓴다. 기본값은 "무제한"이라 캡은 opt-in 안전장치다. (신뢰도 high, 3-0) — /goal docs + agent-loop docs.
> caveat: "or stop after 20 turns"는 평가자의 *모델 판단*이지 하드 정지가 아니다. 보장된 경계가 필요하면 SDK max_turns/max_budget_usd.

## 4. 메모리/지속학습 — 그리고 가장 중요한 caveat

지속학습은 단발 추론을 넘어선 **별도의 학습 가능 능력**으로, 2025–2026 분야 합의 문제다. 에이전트가 과제 스트림에서 재사용 경험을
누적하고, 시간이 지나며 개선하며, *무관한 경험의 간섭을 피해야* 한다. SEA(의료 진단), AgentCL 등은 경험을 에피소드를 넘는 재사용 지식으로
변환한다(=Distill-then-Consult의 기계적 구현). (신뢰도 high, 3-0/2-1) — AgentCL(arXiv:2606.02461), SEA(arXiv:2604.07269).

### ⚠️ 치명적 anti-pattern: 순진한 distill은 *성능을 떨어뜨릴 수 있다*
가장 엄밀한 1차 증거가 경고한다 — **경험을 텍스트 규칙으로 순진하게 distill/consolidate하면 fragile하고 성능을 오히려 악화시킬 수 있다.**
- **CL-Bench**(arXiv:2606.05661 — 사용자가 준 "Continual Learning Bench"와 동일, UC Berkeley/Snorkel, 최초의 전문가검증 벤치마크):
  에이전트가 즉시 관찰에 overfit하고 인스턴스 간 지식 재사용에 실패하며, **전용 메모리 시스템보다 순진한 in-context learning(ICL)이
  총합 성능에서 더 낫다.** (다만 특정 과제(예: Sales Prediction)에선 메모리가 도움.) (신뢰도 high, 3-0)
- **Faulty memory 연구**(dylanzsz.github.io/faulty-memory, arXiv:2605.12978, UIUC/Tsinghua): **메모리 효용은 처음 오르다가
  떨어져 no-memory baseline 아래로 간다.** GPT-5.4가 메모리 없이 100% 풀던 ARC-AGI 19문제가, *자기 자신의 정답 풀이*에서
  consolidate한 뒤 54%로 붕괴했다. "trajectory는 완벽한데, rewrite 단계가 망가뜨린다." 3대 실패모드: misgrouping·interference·overfitting. (신뢰도 high, 3-0)

### 그러나 — distill을 버리지는 말 것 (refuted)
"raw 에피소드만 보존하는 게 모든 consolidator를 이긴다"는 가설은 **반박됐다(0-3).** 즉 교훈은 *no distillation*이 아니라 **quality-gated distillation**이다.

### → 플러그인 설계 함의 (memory-curator가 따른다)
1. **검증 게이트**: 확정된(verified) 사실만 distill. 가설은 정립 금지.
2. **추상화 우선**: verbatim rewrite보다 *일반화된 통찰*을 적는다(rewrite 단계가 붕괴 원인).
3. **과거 에피소드 회귀 검증**: 새 규칙이 과거에 통과하던 사례를 깨지 않는지 점검 후 commit(가능하면).
4. **가역성·감사성**: 규칙은 근거 역참조와 함께 저장하고, 성능 저하 시 폐기/롤백 가능해야 한다(active/candidate/conflict/retired 상태로 표시).
5. **raw context를 경쟁 baseline으로 보존**: iterations.jsonl 원본은 절대 요약/삭제하지 않는다(순진한 ICL이 강한 baseline).
6. **선택적 consult**: 메모리 전부를 투하하지 말고 관련 규칙만 surface(간섭 회피).

## 5. Claude Code에서의 실행 토대

- **`/goal`** — 목표 지향 자율 루프 + 별도 평가자(Haiku) 완료 판정. `auto` 모드(도구별 프롬프트 제거)와 상보적(/goal은 turn별 프롬프트 제거). (요구: Claude Code v2.1.139+.)
- **Agent SDK** — 고정 루프 + `max_turns`/`max_budget_usd` 하드 캡(에러 `error_max_turns`/`error_max_budget_usd`).
- **memory(CLAUDE.md·auto memory·skill)** — 내구적 교훈 저장소.
- 본 하네스는 이 토대 위에 **검증기 설계·재시도 전 진단·quality-gated 지속학습·무진전 감지**를 멀티 에이전트로 구조화해 얹는다.

## 6. 출처 (quality 표기)

**1차(primary)**: code.claude.com/docs/en/goal · code.claude.com/docs/en/agent-sdk/agent-loop · code.claude.com/docs/en/memory ·
anthropic.com/engineering/harness-design-long-running-apps · arXiv:2606.05661(CL-Bench) · arXiv:2606.02461(AgentCL) ·
arXiv:2604.07269(SEA) · dylanzsz.github.io/faulty-memory(arXiv:2605.12978) · github.com/openai/parameter-golf(README).
**2차/blog(verbatim 교차검증)**: addyosmani.com/blog/loop-engineering · x.com/RLanceMartin/article(…2064397389189071163, 402 paywall) ·
theneuron.ai(Cherny/Wu 해설) · steipete.me/posts/just-talk-to-it · x.com/steipete/status/2063697162748260627 · explainx.ai · datasciencedojo.

## 7. caveats (신뢰도 한계)

1. Lance Martin 1차(x.com)는 paywall(HTTP 402) — 다중 2차의 verbatim 인용 + Anthropic 1차 보강으로 검증. 정확한 원문 직접 확인은 불가.
2. "verifier 89% vs self-critique 62%" 수치는 1차에 없음(2차 과장, 추정 fabricated) — 정성 주장만 채택.
3. Osmani 정의는 theneuron.ai 인용 경유 비중↑(직접 fetch 보강) — 다중 독립 출처로 near-verbatim 일치.
4. 메모리 결함 결과는 단일 미복제 preprint들(SEA=의료 단일도메인, faulty-memory=의도적 격리 스트레스 테스트) — 메커니즘/존재증명으론 견고하나 광범위 성능 보장은 아님.
5. **벤치마크 스코프**: Mem0·Reflexion·ReasoningBank 등은 *다른* 벤치마크에서 메모리가 ICL을 이긴다고 보고 — "순진한 ICL이 이긴다"는 CL-Bench 한정 결과지 보편 법칙 아님.
6. 요청 소스 중 OpenAI parameter-golf, steipete 포스트, Boris Cherny 직접 클립은 *독립 1차 주장*으로 별도 확정되진 않음(Cherny는 theneuron.ai 2차 경유 생존).
7. /goal·SDK 동작은 버전 고정(v2.1.139+). /goal 평가자는 transcript만 보고 도구 미사용 → "stop after N turns"는 모델 판단(하드 정지 아님). 보장 경계는 SDK 캡.
8. **설계 긴장(반박된 주장 carry-forward)**: "raw-only가 최고"는 반박(0-3). faulty-memory 결과를 과교정해 consolidation을 *전면 폐기*하지 말 것 — 교훈은 quality-gated distillation.

## 8. open questions (후속)

- parameter-golf가 실제로 무엇을 최적화하는가, 그리고 루프/파라미터 튜닝(중단 임계·turn 캡·루브릭 가중치의 반복 탐색)을 outer meta-loop로 플러그인에 넣을 가치가 있는가. (요청됐으나 미확정)
- CL-Bench(총합 ICL 승) vs 특정 과제(메모리 승)를 가르는 *언제 distill하고 언제 raw만 둘지* 운용 결정규칙. (어떤 소스도 operational gate 미제시)
- 100%→54% 붕괴를 막는 Distill quality-gate의 검증된 완화책(쓰기 전 검증 / 독립 verifier 승인 / 추상 통찰 선호 / 과거 에피소드 회귀 테스트). (faulty-memory는 진단만, 처방 미검증)
- 도구 못 쓰는 /goal 평가자가 근거를 갖도록 에이전트가 기계검증 증거를 출력에 surface하게 강제하는 best practice, 그리고 도구 가진 verifier 서브에이전트 패턴과의 상호작용.
