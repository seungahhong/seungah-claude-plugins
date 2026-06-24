# Eval Harness — 원리 · judge/validity 설계 · anti-pattern

> 이 문서는 eval-harness 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.
> 인용·신뢰도·CAVEAT의 출처별 상세는 [eval-harness-research.md](./eval-harness-research.md)를 본다.

## 1. 무엇이 eval engineering인가

평가의 표면 질문은 "점수가 몇 점인가"다. 엄밀한 평가의 진짜 질문은 **"이 점수를 믿어도 되는가"** 다.
AI 생성물(코드·에이전트 출력·산출 텍스트)을 채점할 때, *누가·어떻게·몇 번* 채점하면 결과를 신뢰할 수 있는지를
설계·감사·실행하는 것이 이 하네스의 일이다.

신뢰는 네 축에서 무너진다 — ① **validity**(엉뚱한 것을 재거나, 잰 것이 실제 성공을 안 가리킴), ② **judge 불안정**(단일
샷 판정이 표본마다 흔들림), ③ **shortcut**(과제를 풀지 않고도 만점), ④ **귀인 혼동**(점수가 model 탓인지 harness 탓인지
모름). 이 네 축이 각각 Phase 0~3과 내재화 원칙으로 들어간다.

## 2. 네 단계 흐름

1. **Define & Validity (Phase 0)** — 평가 대상과 관찰형 성공기준을 못 박고, task validity·outcome validity를 명세한다.
2. **Build Judge (Phase 1)** — judge를 단일 샷이 아니라 다중 표본(≥3)으로, 가능하면 다관점 분해 + 실행 grounding으로 구성한다.
3. **Audit Validity (Phase 2)** — judge를 *돌리기 전에* validity 위반·shortcut·귀인 혼동·instruction density를 적대적으로 감사한다(BLOCK 게이트).
4. **Run & Report (Phase 3)** — 다중 표본을 실행·집계하고 confidence·CAVEAT와 함께 보고한다.

게이트는 둘이다 — Phase 0 승인 게이트(잘못 정의된 평가로 비용 낭비 방지)와 Phase 2 BLOCK 게이트(거짓 결과 *생산 전* 차단).

## 3. validity — 측정이 능력을 가리키게 하라

> 근거: agentic benchmark의 validity 결함은 성능을 "상대적으로 최대 100%까지 과대/과소 추정"시킬 수 있다(Zhu et al., 2025).
> "up to 100%"는 조사된 표본 벤치마크들 중 *상한치*이지 일률 100%가 아니다(CAVEAT). 왜곡의 *존재·방향* 경고로 쓴다.

- **task validity** — "a task is solvable if and only if the agent possesses the target capability." 풀리는 과제는 *목표 역량*을
  가져야만 풀려야 한다. 역량 없이도 풀리는 우회로가 있으면(환경 악용·정답 누출·셋업 결함) 점수가 능력을 가리키지 않는다.
- **outcome validity** — "the evaluation result truly indicates task success." 채점기가 *task 성공이 아닌 것*을 성공으로 집계하지
  않아야 한다. 둘은 직교한다 — 과제가 타당해도 채점이 느슨하면(또는 그 반대) 결과가 왜곡된다.
- **ABC(Agentic Benchmark Checklist)** — "벤치마크 구축 경험·모범사례 서베이·기존 보고 이슈에서 합성한 가이드라인". 본 하네스의
  validity-auditor는 이 관점으로 task/outcome validity를 점검한다. (출처: Zhu et al., 2025 — research §E-1·E-2.)

## 4. judge 신뢰성 — single-shot은 신뢰가 아니다

> 근거: "a single sample from the model's probability distribution can still be misleading ... the potential risks associated with
> over-reliance on single-shot evaluations"(Schroeder & Wood-Doughty, 2024/2025).

- **다중 표본(≥3)이 기본** — 단일 표본 judge는 오도될 수 있다. 같은 입력을 최소 3회 표본해 표본 간 일치/불일치를 드러낸다.
  temperature 0이라도 *재현성 ≠ 정확성*이며 "facade of reliability"일 수 있다 — 매번 같은 답이 나온다고 그 답이 맞는 건 아니다.
  > CAVEAT: 가장 강한 판정 불안정은 작은 오픈 모델(약 7~8B급)에서 관찰됐고 frontier judge는 더 안정적일 수 있다. 그래도 단일 샷
  > 신뢰 금지는 hedged claim으로서 기본값으로 유지한다(안정적일 수 있다는 것이 단일 샷을 정당화하지 않는다).
- **다관점 분해(MCTS식)** — test-time computation을 LLM-as-a-Judge에 들여, 어려운 판정(코드 정확성 등)을 "더 단순하고 다관점인
  평가들"로 분해한다("decompose problems into simpler, multi-perspective evaluations" — Wang et al., 2025). 한 번에 "맞나?"가 아니라
  명세 충족·엣지 케이스·실패 모드 등 여러 관점의 부분 판정을 모은다(System-2식 숙고). 도메인 무관 소프트웨어 판정에 적용한다.
  > CAVEAT: 이 분해 *프레이밍*만 채택한다. 특정 구현의 정량 개선치는 dossier의 *반박된 주장* 섹션으로 분류되어 본 하네스가 근거로 쓰지 않는다.
- **실행 grounding 우선** — 가능하면 "그럴듯해 보이는가"를 묻지 말고 *실행 결과*에 닻 내린다(테스트 그린/레드·종료코드·출력 문자열·
  산출물 속성). 모델 의견 채점은 grounding이 불가능할 때의 보조 수단이고, 폴백 시 confidence를 하향한다.
- **judge ≠ generator** — 산출물을 만든 주체와 채점하는 judge를 분리한다(자기채점 편향 회피 — 신선한 평가자).

## 5. instruction density — 루브릭에 지시를 욱여넣지 마라

> 근거: 최상 frontier 모델도 "500개 동시 지시"의 최대 밀도에서 68% 정확도에 그친다("even the best frontier models only achieve 68%
> accuracy at the max density of 500 instructions" — Jaroslawicz et al., 2025). 지시 밀도↑에 따라 instruction-following이 측정 가능하게 degrade한다.
> CAVEAT: keyword-inclusion·단일 report-writing 도메인 scope(일반화 한계는 논문이 명시). 그래도 "밀도↑→degrade"의 *방향*은 채점 루브릭 설계에 직접 함의를 준다.

- 채점 루브릭/지시를 무한정 늘리지 않는다. 핵심 기준으로 추리거나, 기준별로 채점 호출을 분할한다.
- 한 채점 프롬프트가 과밀했다면 그 자체가 결과를 흔들 수 있음을 Phase 3 CAVEAT에 적는다.

## 6. harness ≠ model — 무엇을 고칠지를 남겨라

> 근거: "a coding agent in practice is not a model: it is a system harness." 같은 모델도 harness에 따라 단일 task type에서
> "20 percentage points or more — a range comparable to differences between model generations"만큼 갈린다. 그리고
> "An end-to-end score shows that something failed; it does not say what to fix"(Gorinova et al., 2026).

- 평가를 model·harness·environment를 *하나의 end-to-end 점수로 붕괴*시키지 않는다. 단일 점수는 *무언가 실패했다*는 신호만 주고
  *무엇을 고칠지*는 말하지 않는다. 가능하면 컴포넌트별 신호를 남긴다(어느 컴포넌트가 점수를 끌어내렸는지).
- 결과 해석에 "같은 모델도 harness에 따라 20+pp 갈릴 수 있음"을 명시한다 — 점수 차이를 곧장 모델 능력 차이로 읽지 않는다.
  > CAVEAT: 이 출처는 Position 논문(규범 프레이밍은 논증적)이나, *서술적 사실*(harness 변동·단일 점수의 신호 부재)은 정확·비반박이다.

## 7. anti-pattern (이 하네스가 명시적으로 막는 것)

- **single-shot 신뢰** — 한 번 채점하고 그 점수를 결과로 confidence 없이 제시. → 다중 표본(≥3) + 분산을 confidence로 환산.
- **temp-0를 정확성으로 착각** — 재현성을 신뢰로 오인("facade of reliability"). → 같은 답이 *맞는* 답이라는 보장은 아님을 명시.
- **shortcut/reward-hacking 방치** — 에이전트가 과제를 풀지 않고 만점(채점 파일시스템 악용·정답 누출·타임아웃=성공). → Phase 2에서 실행 전에 적대 감사.
- **validity 미점검** — 엉뚱한 것을 정확히 측정하거나(task validity), 거짓 성공을 집계(outcome validity). → ABC 관점 BLOCK 게이트.
- **harness≠model 귀인 붕괴** — 점수를 단일 end-to-end로만 보고해 고칠 곳을 모름. → 컴포넌트별 신호 보존.
- **instruction density 과밀** — 루브릭에 지시를 과도하게 넣어 채점 자체가 흔들림. → 기준 추림/분할.
- **수치 단정** — "개선 N% 보장". → baseline 대비로만, 표본·CAVEAT와 함께. 인용 수치는 검증된 값만 vote/CAVEAT와.
- **요약으로 재검증 차단** — 표본별 판정·근거를 압축/삭제. → 원본 보존(사람이 판정을 재검증할 수 있게).

## 8. 설계 함의 요약 (에이전트별 매핑)

| 원칙 | 강제하는 에이전트 | Phase |
|------|-------------------|-------|
| validity 우선(task/outcome) | eval-designer(명세) → validity-auditor(감사) | 0·2 |
| single-shot 금지(다중 표본 ≥3) | judge-builder(구성) → eval-runner(실행·집계) | 1·3 |
| 다관점 분해·실행 grounding | judge-builder | 1 |
| shortcut 적대 감사 | validity-auditor | 2 |
| harness≠model 귀인 | eval-designer(귀인 단위) → validity-auditor(혼동 차단) → eval-runner(해석 보존) | 0·2·3 |
| instruction density 절제 | judge-builder(루브릭) → eval-runner(CAVEAT) | 1·3 |
| confidence·CAVEAT·baseline 대비 | eval-runner | 3 |

## 9. 경계 (독립성 유지)

이 하네스는 *AI 생성물의 판정 신뢰성*에 특화한다. 아래는 일반 개념으로서 범위 밖이며, 특정 다른 도구에 의존하지 않는다.

- 모델에 넣을 **컨텍스트 페이로드 조립·압축·정렬**(컨텍스트 최적화)은 범위 밖 — 이 하네스는 *나온 결과를 채점*한다.
- 한 작업을 **여러 에이전트로 병렬화할지/어떤 토폴로지로** 묶을지 판단은 범위 밖.
- **엔지니어용 실행가능 구현 명세 작성**은 범위 밖(그건 명세 작성 도메인).
- **기존 코드의 일반 실행 테스트 생성**(평가 신뢰성 설계가 아닌 단순 테스트 작성)은 범위 밖. 단, judge가 실행 grounding으로 테스트를 *돌려* 채점에 쓰는 것은 Phase 1·3의 일부다.
- **커밋 메시지·PR 코드 리뷰**는 범위 밖.
