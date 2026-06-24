---
name: spec-driven-development
description: 엔지니어용 실행 가능 명세(spec)를 source of truth로 작성하고 에이전트가 명세대로 코드를 생성→자기검증하게 하는 도메인 무관 멀티 에이전트 오케스트레이터. 사용자가 "이 기능 구현 전에 실행 가능한 명세부터 작성해줘", "spec을 source of truth로 두고 코드는 그걸로 생성·검증되게", "코딩 에이전트가 따라 구현할 구조화된 명세(contract) 만들어줘", "명세 쓰고 인수기준·테스트 계획·자기검증까지 붙여 명세대로 구현·검증해줘", "spec-driven development로 진행", "명세 우선으로 짜고 코드가 명세를 충족하는지 조항별로 검증", "구현 명세 contract 작성하고 명세 대비 검증 + diff 이해 게이트까지"를 언급하며 코드보다 *실행 가능 명세*를 먼저 세워 그 명세대로 생성·검증하려 할 때 발동한다. 명세=1차 산출물, 코드=2차 산출물로 워크플로를 역전하고(spec-as-contract), 인수기준·테스트 계획·자기검증을 명세 안에서 설계하며, 마지막에 comprehension 게이트(diff를 읽고 무엇이 왜 바뀌었는지 확인)로 comprehension debt를 막는다. 발동하지 않는다 — 기획자용 PRD·사용자 스토리(문제정의·비즈니스 요구) 작성, AI 생성물·에이전트 출력을 평가할 judge(LLM-as-a-Judge) 구성·평가 하네스 운영, 모델에 넣을 컨텍스트 페이로드 조립·압축·관리, 이미 완성된 코드의 리뷰·커밋 메시지·PR 리뷰, 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선, 반복·검증이 필요 없는 단발성 한 번 수정, settings.json 설정 변경.
---

# Spec-Driven Development — 실행 가능 명세를 source of truth로 둔 생성·검증 오케스트레이터

코드보다 **실행 가능 명세(spec)를 먼저 source of truth로 작성**하고, 에이전트가 그 명세대로 코드를 생성한 뒤
**명세 대비 자기검증**하게 한다. 즉 워크플로를 역전한다 — "명세를 source of truth로 취급하고, 코드를 *생성되거나 검증되는
2차 산출물*로 다룬다"(arXiv:2602.00180, "From Code to Contract"). 사람에게 명세는 *이해의 앵커*이고, 에이전트에게 명세는
*지시서이자 검증 기준*이다.

## 워크플로 역전 (핵심 전환)

보통은 코드를 먼저 짜고 문서를 사후에 붙인다. SDD는 이를 뒤집는다.

- **명세 = 1차 산출물(source of truth)** — 구조화된 contract(목표·범위·인터페이스·동작·제약·엣지케이스).
- **코드 = 2차 산출물** — 명세로부터 *생성*되거나 명세에 *대해 검증*된다.
- **좋은 명세는 self-verification·LLM-as-a-Judge·test plan을 포함**한다 — 단순 기술이 아니라 *구조·계획·반복*으로 쓴다
  (Osmani, "How to write a good spec for AI agents", 2026-01-19).

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'엔지니어용 실행 가능 구현 명세를 source of truth로 세워 명세대로 생성·검증한다'**. 다음은 명시적으로 범위 밖이다.

- **기획자용 PRD·사용자 스토리 작성** — 문제정의·비즈니스 요구·사용자 스토리를 담는 *제품 기획 문서*는 범위 밖이다. 이 하네스는
  에이전트가 코드를 생성할 *실행 가능한 구현 명세(contract)*에 특화한다.
- **AI 출력 평가 judge 구성·평가 하네스 운영** — AI 생성물·에이전트 출력을 일반적으로 평가하는 judge(LLM-as-a-Judge) 구성·
  다중표본 평가 하네스는 범위 밖이다. 이 하네스의 인수 점검은 *명세 부합 판정 전용*이지 일반 출력 평가기가 아니다.
- **컨텍스트 페이로드 조립·압축·관리** — 모델에 넣을 컨텍스트 페이로드를 조립·압축·큐레이션하는 것은 범위 밖이다.
- **완성 코드 리뷰·커밋/PR** — 이미 완성된 코드의 일반 리뷰, 커밋 메시지·PR 작성/리뷰는 범위 밖이다(이 하네스의 검증은 *명세 부합*이지 일반 코드 리뷰가 아니다).
- **하네스 자체 진단·개선** — CLAUDE.md/SKILL.md/agents의 결함을 trace로 진단·고도화하는 것은 범위 밖이다.
- **단발성 한 번 수정** — 명세·생성·검증 단계가 필요 없는 one-off 요청.

경계가 모호하면 한 질문으로 확인한다 — "에이전트가 구현할 *실행 가능한 구현 명세*를 먼저 세우는 건가요, 아니면 *기획/평가/리뷰/단발 수정*인가요?"

## 내재화 원칙 (모든 단계가 따른다)

- **명세=source of truth(코드 우선 역전)** — 코드를 먼저 짜고 명세를 사후 작성하지 않는다. 명세가 1차, 코드는 명세로부터 생성/검증되는 2차 산출물이다.
- **구조화된 contract** — 명세는 산문이 아니라 목표·범위 In/Out·인터페이스·동작·제약·엣지케이스의 *구조화된 contract*다. 에이전트가 해석 없이 구현·검증하게 쓴다.
- **명세 승인 게이트(항상)** — Phase 0 명세를 사용자가 승인하기 전에 구현(Phase 2)을 시작하지 않는다(잘못된 명세로 코드 생성 비용을 낭비하지 않기 위함).
- **인수기준 + 자기검증 내재화** — acceptance-designer가 인수기준·테스트 계획·자기검증 체크·인수 점검 루브릭을 *명세 안에서 자족적으로* 설계한다. 명세를 falsifiable하게 덮는다.
- **명세 대비 생성(추적성)** — 구현은 "잘 만들기"가 아니라 "명세대로 만들기"다. 어느 spec 조항을 어디서 구현했는지 추적성을 남기고, 명세에 없는 동작을 임의 확장하지 않는다(확장은 명세 보정으로 되돌린다).
- **generator/checker 분리** — 만든 에이전트(spec-implementer)와 판정하는 에이전트(spec-verifier)를 분리한다. 자기 산출물을 자기가 평가하지 않는다.
- **명세 대비 검증(spec-conformance)** — 검증 기준은 "잘 도나"가 아니라 "*명세대로* 도나"다. 조항별 충족/미충족 + 증거. 증거 없는 충족 금지, green CI ≠ 명세 구현 완료(reward-hacking 경계).
- **comprehension 게이트(comprehension debt 방지)** — 완료 선언 전에 실제 diff를 읽고 "무엇이 왜 바뀌었고 명세를 구현하는가"를 확인한다. 생성(쓰기)과 식별(읽기)은 다른 인지 능력이며, 읽기가 출력 속도를 못 따라가면 "엔지니어링이 아니라 희망"이다. 명세가 이 확인의 *앵커*다.
- **과장 금지(정직성)** — SDD는 워크플로 역전이지 "효율 보장"이 아니다. 정량 수치는 vote/CAVEAT와 함께만 인용하고, 효율·non-determinism 비판은 references에 함께 둔다.

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Author Spec | `spec-author` | 실행 가능 명세를 source of truth로 작성(구조화된 contract — 구조·계획·반복) |
| 1 Acceptance | `acceptance-designer` | 인수기준 + 테스트 계획 + 자기검증 체크 + 인수 점검 루브릭을 명세 안에서 설계 |
| 2 Generate | `spec-implementer` | 명세대로 코드 생성(또는 구현 가이드) + 조항 추적성 + 자기검증 선실행 |
| 3 Verify | `spec-verifier` | 코드가 *명세대로* 도는지 조항별 검증 + reward-hacking 점검 + comprehension 게이트 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 명세 작성·인수 설계·명세 대비 검증의 추론 품질이 산출물 정합성을 좌우한다.

## 참조 문서

- 명세 우선 원리·spec 구성요소·anti-pattern·comprehension 게이트 설계: [references/spec-driven-development-principles.md](./references/spec-driven-development-principles.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도·caveat): [references/spec-driven-development-research.md](./references/spec-driven-development-research.md)

## 산출물 배치

기본 `.claude/specs/{spec-slug}/`(사용자 지정 가능)에 다음을 둔다. 문서 언어는 **한국어**.

```
.claude/specs/{spec-slug}/
  spec.md            # 승인된 Executable Spec + Acceptance Plan (source of truth)
  conformance.md     # 명세 대비 검증 Verdict + comprehension 게이트 결과
```

---

# 인터랙티브 플로우

## Phase 0 — 명세 작성 (Author Spec) · 명세 승인 게이트

`spec-author`를 호출해 모호한 요청을 **Executable Spec**(slug·목표·범위·인터페이스·동작·제약·엣지케이스)으로 변환한다.

```
Agent(
  subagent_type="spec-author", model="opus",
  prompt="""
  [역할] 모호한 요청을 코딩 에이전트가 그대로 구현·검증할 실행 가능 명세(Executable Spec)로 변환한다.
  [입력] 사용자 요청: {사용자 발화}
  [규칙] 명세=source of truth(코드 우선 역전). 산문이 아니라 구조화된 contract로 작성한다 —
         목표·범위(In/Out)·인터페이스·동작(관찰 가능한 입력→출력)·제약/불변·엣지케이스.
         구조·계획·반복으로 다듬되, 사용자가 말하지 않은 요구는 발명하지 말고 가정으로 분리해 단일 질문으로 확인한다.
         명세 한 줄을 kebab-case slug로 정규화해 최상단에 둔다(산출물 디렉토리 키).
  [출력] slug를 포함한 Executable Spec.
  """
)
```

Executable Spec(slug 포함)을 사용자에게 보여주고 **명세 승인 게이트**:

`[Phase 0] 실행 가능 명세 확정 — 다음: 인수기준·자기검증 설계(Phase 1). 승인할까요?`

승인 전에는 다음 단계로 진행하지 않는다(명세=source of truth이므로 잘못된 명세로 인수 설계·코드 생성 비용을 낭비하지 않기 위함). 승인된 명세 원문을 `.claude/specs/{slug}/spec.md`로 write한다(없을 때만 디렉토리 생성).

## Phase 1 — 인수 설계 (Acceptance)

`acceptance-designer`를 호출해 명세를 falsifiable하게 만드는 **인수기준 + 테스트 계획 + 자기검증 체크 + 인수 점검 루브릭**을 명세 안에서 설계한다.

```
Agent(
  subagent_type="acceptance-designer", model="opus",
  prompt="""
  [역할] 승인된 실행 가능 명세를 falsifiable하게 만드는 인수기준·테스트 계획·자기검증·인수 점검 루브릭을 *이 플러그인 안에서* 설계한다.
  [입력] Executable Spec: {Phase 0 산출물}
  [규칙] 각 spec 조항(동작 B*/제약/엣지케이스)에 인수기준(A*)을 추적 가능하게 귀속한다(A1 ← B1).
         각 인수기준에 *실제로 돌릴 수 있는* 확인 방법(단위테스트/명령/입력→기대출력)을 붙인다(자동/수동 표기).
         구현자가 완료 주장 전 실행할 자기검증 체크를 적되, 기계 검증 가능한 증거(종료코드·diff·카운트)를 surface하게 한다.
         자동 단위테스트로 덮기 어려운 질적 조항은 명세 부합 판정 전용 인수 점검 루브릭(J*)으로 환산한다(일반 AI 출력 평가기 아님).
         명세에 없는 새 요구를 인수기준으로 추가하지 않는다(over-spec 금지 — 확장은 명세 보정으로 되돌린다).
  [출력] 명세에 이어 붙인 Acceptance Plan(인수기준·테스트 계획·자기검증·인수 점검 루브릭·커버리지 노트).
  """
)
```

인수기준이 명세 조항을 falsifiable하게 덮는지 확인하고, `spec.md`에 Acceptance Plan을 이어 붙인다. 미커버 조항이 있으면 `spec-author`로 명세 보정을 요청한다(거짓 완료 방지).

## Phase 2 — 명세 대비 구현 (Generate-against-spec)

`spec-implementer`를 호출해 명세대로 코드를 생성(또는 구현 가이드 작성)하고, 조항 추적성과 자기검증 결과를 남긴다.

```
Agent(
  subagent_type="spec-implementer", model="opus",
  prompt="""
  [역할] 승인된 명세와 인수기준대로 코드를 생성(또는 구현 가이드)하고 조항 추적성을 남긴다.
  [입력] Executable Spec + Acceptance Plan: {Phase 0·1 산출물}
  [규칙] 명세가 지시서다 — 인터페이스·동작·제약·엣지케이스를 그대로 구현하고, 명세에 없는 동작을 임의 확장하지 않는다
         (명세와 다르게 만들 필요가 있으면 임의 변경 대신 명세 보정을 요청한다 — 명세=source of truth).
         각 spec 조항을 코드의 어디서 구현했는지 매핑(B1 → 파일/함수/테스트)을 남긴다.
         완료를 주장하기 전에 명세의 자기검증 체크를 스스로 실행하고 기계 검증 가능한 증거를 surface한다(최종 PASS 선언은 하지 않는다 — Phase 3 독립 검증).
         관련 없는 리팩터링을 끼워 넣지 않는다(검증 표적을 좁게).
  [출력] Implementation(구현·조항 추적·자기검증 결과·변경 요약·명세 보정 요청).
  """
)
```

## Phase 3 — 명세 대비 검증 (Verify-against-spec) + comprehension 게이트

구현 에이전트와 **분리된** `spec-verifier`를 호출해 코드가 *명세대로* 도는지 조항별로 적대 검증하고, comprehension 게이트를 통과시킨다.

```
Agent(
  subagent_type="spec-verifier", model="opus",
  prompt="""
  [역할] 구현 에이전트와 분리된 독립 검증자로서 코드가 *명세대로* 도는지 조항별로 적대 검증하고 comprehension 게이트를 통과시킨다.
  [입력] Executable Spec + Acceptance Plan + Implementation(조항 추적 포함): {Phase 0·1·2 산출물}
  [규칙] 검증 기준은 "잘 도나"가 아니라 "명세대로 도나"다. 인수기준·테스트 계획을 실제로 실행해
         각 spec 조항·인수기준에 충족/미충족 + 증거를 귀속한다. 증거 없는 충족 금지, 적대적으로.
         green CI ≠ 명세 구현 완료 — 테스트 약화·조항 우회·하드코딩으로 통과한 흔적(reward-hacking)을 의심하고 역점검한다.
         모든 조항이 충족돼도 완료 선언 전에 실제 diff를 읽고 무엇이 왜 바뀌었고 명세를 구현하는지 확인한다(comprehension 게이트) —
         각 변경을 명세 조항으로 설명할 수 있어야 통과. 설명 불가 변경이 있으면 미통과.
         인수기준을 실행할 수 없거나 증거 확보가 불가하면 미충족이 아니라 검증불가(BLOCKED)로 분리해 테스트 계획·환경 보정을 요청한다.
         검증자가 임의로 코드를 고치지 않는다(역할 분리) — 미충족은 구현 보완(Phase 2) 또는 명세 보정(Phase 0)으로 라우팅한다.
  [출력] Conformance Verdict(조항별 충족/미충족·증거 + reward-hacking 점검 + comprehension 게이트 결과 + 결론·라우팅).
  """
)
```

검증 결과 분기:

- **모든 조항 충족 + comprehension 게이트 통과** → `conformance.md`에 Verdict를 write하고 **완료 종료**.
- **미충족 조항 존재** → 어느 조항이 왜 미충족인지에 따라 라우팅한다 — 구현 결함이면 `spec-implementer`(Phase 2) 재호출, 명세 자체가 틀렸으면 `spec-author`(Phase 0) 명세 보정 후 다시 진행. 명세를 source of truth로 유지한 채 보정한다.
- **검증불가(BLOCKED)** → 미충족으로 두지 말고, `acceptance-designer`/`spec-author`로 테스트 계획·검증 환경을 보정한다(거짓 미충족 방지). 이 점검은 미충족 카운트에 산입하지 않는다.
- **comprehension 게이트 미통과** → 완료를 선언하지 않고, 설명 불가 변경의 명세 근거를 `spec-implementer`에 요구하거나 명세 보정으로 되돌린다.

## 마무리 — 결과 보고

플로우가 끝나면 다음을 요약 보고한다.

- **결과**: 완료(모든 조항 충족 + comprehension 통과) / 보정 필요(미충족 조항·라우팅).
- **명세 조항 충족 현황**: 충족 N / 전체 M, 미충족 조항 목록.
- **comprehension 게이트**: 통과/미통과와 사유.
- **산출물 경로**: `.claude/specs/{spec-slug}/`(spec.md·conformance.md).

보고 형식(최종): `[SDD 완료] 명세 {조항 수}개 중 {충족}/{전체} 충족 — comprehension 게이트 {통과|미통과} → .claude/specs/{spec-slug}/`
