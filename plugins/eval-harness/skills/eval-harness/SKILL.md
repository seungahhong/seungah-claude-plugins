---
name: eval-harness
description: AI 생성물(코드·에이전트 출력·산출 텍스트)을 엄밀하게 평가하는 도메인 무관 멀티 에이전트 오케스트레이터. 사용자가 "이 LLM 출력 제대로 평가해줘", "judge가 한 번 채점한 거 못 믿겠어 여러 번 표본 떠서 신뢰도까지", "LLM-as-a-judge로 코드 정확성 엄밀하게 채점", "이 벤치마크/평가가 진짜 능력을 재는지(task validity·outcome validity) 점검", "에이전트가 과제 안 풀고 만점 받는 shortcut 있는지 감사", "이 점수가 모델 때문인지 harness 때문인지 분리(harness≠model 귀인)", "다관점으로 분해해서 채점하고 confidence·caveat까지", "single-shot 말고 다중 표본으로 평가 신뢰성 확보"를 언급하며 AI 생성물의 *판정 신뢰성*을 설계·감사·실행하려 할 때 발동한다. LLM-as-a-Judge를 다중 표본(≥3)으로 돌리고, ABC 체크리스트로 validity·shortcut·귀인을 감사한 뒤, 집계 결과를 confidence·CAVEAT와 함께 보고한다. 발동하지 않는다 — 모델에 넣을 컨텍스트 페이로드 조립·압축·정렬(컨텍스트 최적화), 한 작업을 여러 에이전트로 병렬화할지/어떤 토폴로지로 묶을지 판단, 엔지니어용 실행가능 구현 명세 작성, 기존 코드의 일반 실행 테스트 생성(평가 신뢰성 설계가 아닌 단순 테스트 작성), 커밋 메시지 작성·PR 코드 리뷰, 하네스 자체 trace 진단, 프로덕션 장애 대응, settings.json 설정 변경.
---

# Eval Harness — AI 생성물을 엄밀하게 평가하는 오케스트레이터

AI 생성물(코드·에이전트 출력·산출 텍스트)을 **믿을 수 있게 평가**한다. 핵심 질문은 "점수가 몇 점인가"가 아니라
**"이 점수를 믿어도 되는가"** 다 — *누가·어떻게·몇 번* 채점하면 결과를 신뢰할 수 있는지를 설계하고 감사한 뒤 실행한다.
그래서 ① 성공기준과 두 validity를 먼저 못 박고, ② judge를 단일 샷이 아니라 다중 표본으로 구성하고, ③ 과제를 풀지 않고
만점 받는 shortcut과 harness≠model 귀인 혼동을 감사한 뒤, ④ 다중 표본을 집계해 confidence·CAVEAT와 함께 보고한다.

## 무엇을 다루는가 — 평가의 네 가지 신뢰 축

- **validity(타당성)** — 측정하려는 것이 측정 가능하게 정의돼 있고(task validity), 그 측정이 실제 성공을 가리키는가(outcome validity).
- **judge 신뢰성** — 단일 샷 판정은 오도될 수 있다. 다중 표본(≥3)·다관점 분해·실행 grounding으로 판정을 강화한다.
- **shortcut 내성** — 에이전트가 과제를 *실제로 풀지 않고도* 만점을 받는 우회로(환경 악용·정답 누출)를 막는다.
- **귀인(attribution)** — 점수가 model 때문인지 harness 때문인지. 단일 end-to-end 점수는 *무엇이 실패했는지*만 알려주고
  *무엇을 고칠지*는 말하지 않는다. 컴포넌트별 신호를 남긴다.

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'AI 생성물의 판정 신뢰성을 설계·감사·실행한다'**. 다음은 명시적으로 범위 밖이다(일반 개념으로만 서술하며,
특정 다른 도구에 의존하지 않는다).

- **컨텍스트 페이로드 조립·압축·정렬** — 모델에 무엇을 넣을지(컨텍스트 최적화)는 범위 밖이다. 이 하네스는 *나온 결과를 채점*한다.
- **병렬화 판단·토폴로지 설계** — 한 작업을 여러 에이전트로 쪼갤지/어떻게 묶을지는 범위 밖이다.
- **엔지니어용 구현 명세 작성** — 에이전트가 코드 생성할 실행가능 명세(contract) 작성은 범위 밖이다(그건 명세 작성 도메인).
- **기존 코드의 일반 실행 테스트 생성** — 단순히 테스트를 *만드는* 것(평가 신뢰성 설계가 아닌)은 범위 밖이다. 이 하네스는
  *채점기를 어떻게 신뢰할지*를 설계·감사한다. (단, judge가 실행 grounding으로 테스트를 *돌려* 채점에 쓰는 것은 Phase 1·3의 일부다.)
- **커밋 메시지·PR 코드 리뷰** — 범위 밖이다. 완성 코드의 일반 리뷰가 아니라 *판정 신뢰성*을 다룬다.

경계가 모호하면 한 질문으로 확인한다 — "점수를 *신뢰할 수 있게 채점·감사*하려는 건가요(이 하네스), 아니면 *컨텍스트
구성/병렬화 판단/구현 명세 작성* 같은 다른 단계가 필요한가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **validity 우선** — 측정 대상이 *측정 가능하게* 정의되고 그 측정이 *실제 능력*을 가리켜야 한다. validity 결함은 성능을
  상대 최대 100%까지 왜곡할 수 있다(연구 근거, 상한치 — 일률 100% 아님). 그래서 Phase 2를 게이트로 둔다.
- **single-shot 금지(다중 표본 ≥3)** — 단일 표본 judge는 오도될 수 있다. temp-0의 재현성을 정확성으로 착각하지 않는다("facade
  of reliability"). 최소 3회 표본하고 분산을 confidence로 환산한다. (CAVEAT: 작은 오픈 모델에서 불안정이 가장 컸고 frontier judge는
  더 안정적일 수 있으나, 그것이 단일 샷을 정당화하지 않는다.)
- **다관점 분해** — 어려운 판정(코드 정확성 등)을 "더 단순하고 다관점인 평가들"로 분해한다(MCTS식 프레이밍만 채택, 특정 정량치는 비채택).
- **실행 grounding 우선** — 가능하면 모델 의견이 아니라 실행 결과(테스트·종료코드·산출물 속성)에 판정을 닻 내린다.
- **shortcut 적대 감사** — 과제를 풀지 않고 만점 받는 경로(파일시스템 악용·정답 누출·타임아웃=성공)를 *judge를 돌리기 전에* 막는다.
- **harness≠model 귀인** — "a coding agent in practice is not a model: it is a system harness." 점수를 단일 end-to-end로 붕괴시키지
  않고 컴포넌트별 신호를 남긴다. 같은 모델도 harness에 따라 단일 task type에서 20+pp 갈릴 수 있다.
- **instruction density 절제** — 채점 루브릭에 지시를 과밀하게 넣으면 따르기 정확도가 떨어진다(연구 근거). 핵심 기준으로 추리거나 분할한다.
- **confidence·CAVEAT 의무** — 결과는 항상 confidence와 CAVEAT(validity 잔여 위험·grounding 유무·귀인 한계)와 함께 낸다. "개선 N%
  보장" 같은 단정 금지 — 비교는 baseline 대비로만.
- **관찰 가능성·승인** — Phase 0 Eval Spec 승인 게이트는 항상. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Define & Validity | `eval-designer` | 평가 대상·관찰형 성공기준 정의 + task/outcome validity 명세 + 귀인 단위 |
| 1 Build Judge | `judge-builder` | judge 구성(다중 표본 ≥3 + 다관점 분해 + 가능하면 실행 grounding), single-shot 금지 |
| 2 Audit Validity | `validity-auditor` | ABC 관점 감사(task/outcome validity·shortcut·harness≠model 귀인·instruction density), BLOCK 게이트 |
| 3 Run & Report | `eval-runner` | 다중 표본 실행·집계 + confidence + CAVEAT 보고(단일 샷 신뢰 금지) |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — validity 감사·판정
추론의 품질이 평가의 신뢰성을 좌우하므로 약한 모델로 대체하지 않는다.

## 참조 문서

- 평가 원리·anti-pattern(single-shot 신뢰·shortcut·harness≠model 귀인 혼동·instruction density)·judge/validity 설계지침:
  [references/eval-harness-principles.md](./references/eval-harness-principles.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도·CAVEAT·반박된 주장): [references/eval-harness-research.md](./references/eval-harness-research.md)

---

# 인터랙티브 플로우

## Phase 0 — 평가 대상·성공기준·validity 명세 (Define & Validity) · 승인 게이트

`eval-designer`를 호출해 모호한 "이거 평가해줘"를 **Eval Spec**(slug·평가 대상·관찰형 성공기준·task/outcome validity·귀인 단위·범위)으로 변환한다.

```
Agent(
  subagent_type="eval-designer", model="opus",
  prompt="""
  [역할] 모호한 평가 요청을 Eval Spec으로 변환한다.
  [입력] 사용자 요청: {사용자 발화}, 평가 대상 산출물/시스템: {대상}
  [규칙] 성공기준은 관찰형으로(무엇을 보면 PASS). task validity(목표 역량 없이 통과 가능한 우회로 후보)와
         outcome validity(거짓 성공 집계 가능성)를 명세한다. 단일 모델인지 harness가 낀 시스템인지 구분하고
         컴포넌트별(model/harness/environment) 귀인 단위를 잡는다. 범위 In/Out과 slug를 부여한다.
  [출력] slug를 포함한 Eval Spec.
  """
)
```

Eval Spec을 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 평가 대상·성공기준·validity 확정 — 다음: judge 구성(다중 표본). 진행할까요?`

승인 전에는 judge를 구성하지 않는다(잘못 정의된 평가로 비용을 낭비하지 않기 위함).

## Phase 1 — judge 구성 (Build Judge)

`judge-builder`를 호출해 Eval Spec의 성공기준을 채점할 **Judge 구성**을 만든다 — 다중 표본(≥3)·(해당 시) 다관점 분해·가능하면 실행 grounding.

```
Agent(
  subagent_type="judge-builder", model="opus",
  prompt="""
  [역할] LLM-as-a-Judge를 다중 표본으로 구성한다.
  [입력] Eval Spec: {Phase 0 산출}, 평가 대상·실행 환경: {대상/명령}
  [규칙] 표본 수 ≥ 3(single-shot 금지 — 단일 표본은 오도될 수 있다). 어려운 판정은 단순·다관점 sub-평가로 분해한다.
         가능하면 실행 grounding(테스트·종료코드·산출물 속성)에 판정을 닻 내리고, 불가하면 모델 의견 폴백 + '신뢰도 하향' 플래그.
         루브릭은 기준별·관찰형, 근거 의무. instruction density 과밀 금지(핵심 기준으로 추리거나 분할). 표본별 판정·근거는 원본 보존.
  [출력] Judge 구성서(표본 수·grounding·관점·기준별 루브릭·집계 입력).
  """
)
```

## Phase 2 — validity 감사 (Audit Validity) · BLOCK 게이트

`validity-auditor`를 호출해 *judge를 돌리기 전에* task/outcome validity·shortcut·귀인·instruction density를 적대적으로 감사한다.

```
Agent(
  subagent_type="validity-auditor", model="opus",
  prompt="""
  [역할] ABC 관점으로 평가의 타당성을 적대적으로 감사한다(실행 전 게이트).
  [입력] Eval Spec + Judge 구성 + (가능하면) grading 환경/코드
  [규칙] task validity(목표 역량 없이 통과 가능 경로), outcome validity(거짓 성공 집계 경로),
         shortcut/reward-hacking(파일시스템 악용·정답 누출·타임아웃=성공으로 풀지 않고 만점), harness≠model 귀인 혼동
         (단일 end-to-end 점수로 붕괴해 '무엇을 고칠지' 신호 소실), instruction density 과다를 점검한다.
         위반 후보마다 악용 시나리오를 구체적으로 적고 수정안을 낸다. 위반이 있으면 PASS가 아니라 BLOCK.
  [출력] Validity 감사 보고(PASS|BLOCK + 위반·수정안 + 잔여 위험).
  """
)
```

- **PASS** → Phase 3로 진행하되, *배제하지 못한 잔여 위험*을 Phase 3 CAVEAT로 carry-forward한다.
- **BLOCK** → judge를 돌리지 않는다. 위반에 따라 Phase 1(루브릭·grounding) 또는 Phase 0(성공기준·validity 정의)로 환류해 수정 후 재감사한다(거짓 결과를 *생산하기 전에* 막는다).

`[Phase 2] validity 감사 {PASS|BLOCK} — {위반 요약/없음} → {실행 진행|수정 후 재감사}.`

## Phase 3 — 실행·집계·보고 (Run & Report)

`eval-runner`를 호출해 감사를 통과한 judge를 **다중 표본으로 실행·집계**하고, confidence·CAVEAT와 함께 보고한다.

```
Agent(
  subagent_type="eval-runner", model="opus",
  prompt="""
  [역할] 다중 표본으로 judge를 실행·집계하고 confidence·CAVEAT와 함께 보고한다.
  [입력] Judge 구성 + Validity 감사 보고(PASS + 잔여 위험) + 평가 대상·실행 환경
  [규칙] judge를 같은 입력에 최소 3회 표본하고 표본별 판정·근거를 원본 보존한다. 표본 분산을 confidence로 환산
         (일치↑→high, 갈림↑→low; temp-0 재현성을 정확성으로 오인 금지). grounding 없으면 confidence 하향.
         Phase 2 잔여 위험·harness≠model 귀인 한계·instruction density 영향을 CAVEAT로 명시. 비교는 baseline 대비로만,
         '개선 N% 보장' 단정 금지. 표본 전부 불일치면 붕괴 말고 low confidence로 보고하고 재설계 권고.
  [출력] Eval 결과 보고(기준별 결과 + confidence + CAVEAT + (있으면) baseline 대비 비교).
  """
)
```

## 마무리 — 결과 보고

평가가 끝나면 다음을 요약 보고한다.

- **결과**: 기준별 PASS/FAIL(또는 점수)과 표본 일치 수.
- **confidence**: high/medium/low + 근거(표본 분산·grounding 유무).
- **CAVEAT**: validity 잔여 위험·grounding·harness≠model 귀인 한계·instruction density — 결과 해석의 한계.
- (있을 때만) **baseline 대비 비교** — '보장' 표현 없이, 무엇 대비 무엇이 얼마.

보고 형식(최종): `[Eval 종료] 결과 {요약} — confidence {high|medium|low}(표본 {k}/{N} 일치), CAVEAT {n}건, validity 감사 {PASS}.`
