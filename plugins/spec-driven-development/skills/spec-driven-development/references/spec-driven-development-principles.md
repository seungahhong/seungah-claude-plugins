# Spec-Driven Development — 원리 · spec 구성요소 · comprehension 게이트 · anti-pattern

> 이 문서는 spec-driven-development 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.
> 출처·인용·신뢰도·caveat은 [spec-driven-development-research.md](./spec-driven-development-research.md)에 정리되어 있다.

## 1. 무엇이 spec-driven development인가

프롬프트 엔지니어링은 *한 번의 입력*을 다듬는다. spec-driven development(SDD)는 *무엇을 만들지의 명세 자체*를 1차 산출물로 둔다.

핵심은 **워크플로의 역전**이다. SDD는 "명세를 source of truth로 취급하고, 코드를 *생성되거나 검증되는 2차 산출물*로 다루어
전통 워크플로를 역전한다"(arXiv:2602.00180, "Spec-Driven Development: From Code to Contract in the Age of AI Coding
Assistants"). 즉 코드를 먼저 짜고 문서를 사후에 붙이는 대신, **명세(contract)를 먼저 세우고 코드를 그로부터 끌어낸다.**

이 역전이 코딩 에이전트 시대에 중요한 이유:
- 에이전트는 *지시*가 모호하면 산출도 모호하다. 명세는 에이전트에게 *명확한 지시서*다.
- 에이전트는 *검증 기준*이 없으면 "됐다"를 자기보고로 주장한다. 명세는 에이전트에게 *검증 기준*이다.
- 사람은 에이전트의 출력 속도를 *읽기*로 따라가지 못한다. 명세는 사람에게 *이해의 앵커*다(§5).

> 정직성 주의 — SDD는 정의상 워크플로 *역전*이며 "보장된 개선/효율"이 아니다. non-determinism·MDD 유사·overhead 등에 대한
> 비판이 존재한다(research dossier §2 CAVEAT). 정의적 프레이밍은 채택하되 "이렇게 하면 N% 빨라진다"는 식으로 과장하지 않는다.

## 2. 좋은 명세(spec)의 구성요소

좋은 명세 작성은 단순 기술이 아니라 *구조·계획·반복*("How to structure, plan, and iterate for high-performance coding
agents", Osmani 2026-01-19)이며, 산문이 아니라 **구조화된 contract**다. 이 하네스의 Executable Spec은 다음을 명시 섹션으로 둔다.

- **목표(Goal)** — 이 명세가 구현하려는 단일 동작/능력, 한 문장.
- **범위(Scope) In/Out** — 다루는 것과 명시적으로 다루지 않는 것(명세 드리프트·over-build 방지).
- **인터페이스(Interface / Contract)** — 함수·API·CLI 시그니처, 입출력 타입·형식.
- **동작(Behavior)** — *관찰 가능한* 입력→출력·상태 전이로(B1, B2…). 판정 불가 표현("잘 된다") 금지.
- **제약·불변(Constraints / Invariants)** — 바뀌면 안 되는 것, 성능·호환·보안 제약.
- **엣지케이스(Edge Cases)** — 빈 입력·경계값·실패 경로.
- **가정(Assumptions)** — 사용자 확인이 필요한 가정(발명 금지 — 단일 질문으로 확인).
- **반복 메모(Iteration Notes)** — 이번 반복에서 좁힌 모호점(명세 자체가 반복 개선 대상).

> 핵심: 좋은 명세는 **self-verification, LLM-as-a-Judge, test plan**까지 포함한다(Osmani). 즉 "무엇을 만들지"뿐 아니라
> "그게 됐는지 어떻게 아는지"를 명세 안에 넣는다. 이것이 Phase 1 acceptance-designer가 채우는 부분이다.

## 3. 4단계 플로우와 역할 분리

| Phase | 에이전트 | 산출 | 핵심 |
|-------|----------|------|------|
| 0 Author Spec | spec-author | Executable Spec | 명세=source of truth, 구조화된 contract, **승인 게이트** |
| 1 Acceptance | acceptance-designer | 인수기준·테스트 계획·자기검증·인수 점검 루브릭 | 명세를 falsifiable하게 덮음(자족적) |
| 2 Generate | spec-implementer | 명세대로 코드 + 조항 추적성 | 명세대로 생성, 임의 확장 금지, 자기검증 선실행 |
| 3 Verify | spec-verifier | 조항별 부합 Verdict + comprehension 게이트 | 명세 대비 검증, generator/checker 분리 |

- **명세 승인 게이트(Phase 0 후)**: 명세가 source of truth이므로, 잘못된 명세로 인수 설계·코드 생성 비용을 낭비하지 않도록 사용자 승인 전에 진행하지 않는다.
- **generator/checker 분리(Phase 2 vs 3)**: 만든 에이전트가 자기 산출물을 평가하면 편향된다. 구현(spec-implementer)과 검증(spec-verifier)을 분리한다.
- **명세를 source of truth로 유지하는 보정 루프**: 미충족·모호·충돌이 발견되면 코드를 몰래 확장하지 않고 명세 보정(Phase 0)으로 되돌린다.

## 4. 명세 대비 검증 (spec-conformance, not just "works")

이 하네스의 검증 기준은 "코드가 잘 작동하나"가 아니라 "코드가 *명세를 충족하나*"다(arXiv:2602.00180 — 코드는 명세에 대해
검증되는 2차 산출물).

- **조항별 귀속(traceability)**: 각 spec 조항(동작·제약·엣지케이스)·인수기준에 충족/미충족 + 증거를 귀속한다. end-to-end 단일
  점수("됐다/안 됐다")는 *무엇이* 실패했는지 알려주지 않는다 — 조항 추적이 진단 표적을 좁힌다.
- **증거 필수·적대적**: 통과를 *주장*이 아니라 *증명*으로 본다. 증거(종료코드·출력·diff·카운트) 없는 충족은 무효.
- **green CI ≠ 명세 구현 완료(reward-hacking 경계)**: 테스트가 통과해도 그 테스트가 명세를 *덮지 않으면* 충족이 아니다.
  테스트 약화·조항 우회·하드코딩·범위 축소로 통과한 흔적을 의심하고, 인수기준이 명세를 falsifiable하게 덮는지 역점검한다.
- **검증불가(BLOCKED) 분리**: 인수기준을 실행할 수 없거나 증거 확보가 불가하면 미충족이 아니라 검증불가로 분리해 테스트 계획·환경 보정을 요청한다(거짓 미충족 방지).

## 5. comprehension 게이트 (comprehension debt 방지)

에이전트가 출력을 빠르게 늘릴수록, 사람이 그 코드를 *읽고 이해하는 능력*이 따라가지 못하면 위험이 누적된다 —
**comprehension debt**(Jeremy Twei의 용어, Osmani 인용).

- 근거 인용: "it's trivially easy to review code you can no longer write from scratch. If your ability to 'read'
  doesn't scale with the agent's ability to 'output,' you're not engineering anymore. You're hoping."
  (Osmani, "The 80% Problem in Agentic Coding", 2026-01-28).
- 핵심 명제: **생성(쓰기)과 식별(읽기)은 다른 인지 능력**이다("Generation (writing code) and discrimination (reading code)
  are different cognitive capabilities"). 읽기가 출력 속도를 못 따라가면 "엔지니어링이 아니라 희망"이 된다.

이 하네스의 대응(Phase 3 spec-verifier, 완료 선언 *전* 필수):
- 모든 조항이 충족돼도, 실제 diff를 읽고 "무엇이 왜 바뀌었고 명세를 *구현*하는가"를 확인한다.
- **명세가 이해의 앵커**다 — diff의 각 변경을 명세 조항에 대응시켜 설명할 수 있어야 게이트를 통과한다. 설명 불가 변경이 있으면 미통과.
- 즉 명세는 사후 문서가 아니라, *생성 전에는 지시*이고 *생성 후에는 이해의 기준*으로 두 번 쓰인다.

## 6. anti-pattern (이 하네스가 피하는 것)

1. **코드 우선·명세 사후(spec-as-afterthought)** — 코드를 먼저 짜고 명세를 나중에 끼워 맞추면 명세는 source of truth가 아니라
   장식이 된다. → 명세 승인 게이트로 차단(Phase 0 전에 구현 없음).
2. **산문 명세(prose-not-contract)** — 줄글 명세는 에이전트가 해석을 끼워 넣게 만든다. → 구조화된 contract(§2).
3. **명세 외 임의 확장(scope creep in code)** — 구현자가 명세에 없는 동작을 코드로 몰래 넣는다. → 명세=source of truth, 확장은 명세 보정으로 되돌림.
4. **over-spec(인수기준이 명세를 확장)** — acceptance-designer가 명세에 없는 요구를 인수기준으로 추가한다. → 인수기준은 명세를 *덮을* 뿐 확장하지 않음.
5. **self-grading(자기 채점)** — 만든 에이전트가 자기 산출물을 PASS로 선언한다. → generator/checker 분리.
6. **green washing(테스트 약화로 통과)** — 명세를 우회하거나 테스트를 약화해 green을 만든다. → green CI ≠ 명세 구현 완료(reward-hacking 점검).
7. **comprehension debt(이해 없는 수용)** — diff를 이해하지 않은 채 "통과했으니 됐다"로 종료한다. → comprehension 게이트(§5).

## 7. 인접 도메인 경계 (독립성 유지하며 변별)

이 하네스는 **엔지니어용 실행 가능 구현 명세**에 특화한다. 다음은 *일반 개념*으로 범위 밖이며, 이 하네스는 이들에 의존하지 않는다.

- **기획자용 PRD·사용자 스토리** — 문제정의·비즈니스 요구·사용자 스토리를 담는 *제품 기획 문서*는 별개 도메인이다. 이 하네스의 명세는
  "왜/누구를 위해"가 아니라 "에이전트가 무엇을 어떻게 구현·검증하는가"의 contract다.
- **AI 출력 평가(judge) 구성** — AI 생성물·에이전트 출력을 일반적으로 평가하는 LLM-as-a-Judge·다중표본 평가 하네스는 별개다.
  이 하네스의 인수 점검 루브릭은 *명세 부합 판정 전용*이지 일반 출력 평가기가 아니다.
- **컨텍스트 페이로드 조립·압축·관리** — 모델에 넣을 컨텍스트를 조립·압축·큐레이션하는 것은 별개 도메인이다.
- **완성 코드 리뷰·커밋/PR** — 이미 완성된 코드의 일반 리뷰, 커밋·PR 작성은 별개다(이 하네스의 검증은 *명세 부합*이다).
- **하네스 자체 진단·개선** — CLAUDE.md/SKILL.md/agents의 결함 진단·고도화는 별개 도메인이다.

## 8. 참고문헌

설계 근거의 출처·인용·신뢰도·caveat은 [spec-driven-development-research.md](./spec-driven-development-research.md)에 정리되어 있다.
이 문서의 모든 정량/정성 주장은 그 dossier의 검증된 인용에서만 끌어왔으며, *반박된 주장*은 본문 근거로 쓰지 않고 dossier 투명성 섹션에만 기록한다.
