# Spec-Driven Development — 연구 dossier (cited)

> 이 문서는 `spec-driven-development` 하네스 설계의 근거가 된 1차/2차 자료 조사 결과다(deep-research: 다각도 팬아웃 →
> 소스 fetch → 주장 추출 → 3-vote 적대적 교차검증 → confirmed/refuted 분류, 2026-06-25 기준).
> [spec-driven-development-principles.md](./spec-driven-development-principles.md)의 원칙과 상호 참조된다.
> 빠르게 변하는 분야이므로 각 출처에 신뢰도(vote)와 caveat을 함께 표기한다. 정량 수치는 vote/CAVEAT와 함께만 인용하고,
> "개선 N% 보장"식 진술은 쓰지 않는다.

---

## 출처 1 — Osmani, "How to write a good spec for AI agents"

- **제목**: How to write a good spec for AI agents
- **저자**: Addy Osmani (Elevate)
- **출처·연도**: addyo.substack.com, 2026-01-19 (O'Reilly Radar 재게재)
- **URL**: https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: 코딩 에이전트용 명세를 *구조화·계획·반복*하는 법. PRD식 구조화에 더해 self-verification, LLM-as-a-Judge,
  test plan을 포함한다. post-Aug-2025 원천 글로 "2025-08+ 글" 제약을 충족한다.
- **인용문(아카이브)**: "How to structure, plan, and iterate for high-performance coding agents"
- **하네스 반영**: spec-author의 "구조화된 contract"·"구조·계획·반복", acceptance-designer의 "self-verification·
  LLM-as-a-Judge·test plan을 명세 안에서 자족적으로" 설계(principles §2·§3).
- **CAVEAT**: 실무 가이드(2차 성격)이며 단일 저자 의견 글이다. 정의·실천 지침으로 인용하되 정량 효과 주장에는 쓰지 않는다.

## 출처 2 — Piskala, "Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants"

- **제목**: Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants
- **저자**: Deepak Babu Piskala
- **출처·연도**: arXiv:2602.00180, submitted 2026-01-30
- **보강**: Thoughtworks · Martin Fowler · GitHub Blog
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: SDD = 코드 우선 워크플로의 역전. 명세를 source of truth로 두고, 코드를 그로부터 생성되거나 검증되는 2차 산출물로
  다룬다. 제목대로 "From Code to Contract".
- **인용문**: "Spec-driven development (SDD) inverts the traditional workflow by treating specifications as the source
  of truth and code as a generated or verified secondary artifact."
- **하네스 반영**: 전체 워크플로 역전(명세=1차, 코드=2차)과 "명세 대비 검증" 기준의 정의적 근거(principles §1·§4, SKILL 내재화 원칙).
- **CAVEAT**: Martin Fowler는 SDD의 *실효성·효율*(non-determinism, MDD 유사, overhead)을 비판한다 — 정의적 프레이밍은
  비반박이나, "보장된 개선"으로 과장하지 않는다. 정의로 인용하고 효율 주장에는 쓰지 않는다.

## 출처 3 — Osmani, "The 80% Problem in Agentic Coding"

- **제목**: The 80% Problem in Agentic Coding
- **저자**: Addy Osmani
- **출처·연도**: addyo.substack.com, 2026-01-28
- **URL**: https://addyo.substack.com/p/the-80-problem-in-agentic-coding
- **신뢰도(vote)**: 3-0 (high)
- **핵심**: comprehension debt(Jeremy Twei 용어) — AI 의존이 깊어지면 코드를 *읽고 이해하는 능력*이 출력 속도를 못 따라간다.
  생성(쓰기)과 식별(읽기)은 다른 인지 능력이다. → spec-verifier의 comprehension 게이트 동기(명세가 *이해의 앵커*).
- **인용문**: "it's trivially easy to review code you can no longer write from scratch. If your ability to 'read'
  doesn't scale with the agent's ability to 'output,' you're not engineering anymore. You're hoping."
- **보조 명제**: "Generation (writing code) and discrimination (reading code) are different cognitive capabilities."
- **하네스 반영**: Phase 3 comprehension 게이트(완료 선언 전 diff를 읽고 명세 조항에 대응시켜 설명, principles §5).
- **CAVEAT**: 의견 글(2차)이며 정성적 주장이다. comprehension 게이트의 *동기*로 인용하고 정량 효과로 쓰지 않는다.

---

## 반박된 주장 (투명성 — 본문 근거로 사용 금지)

이 하네스는 3-vote 적대 검증에서 **반박(refuted)된 주장**을 본문·원칙·에이전트 지침의 근거로 쓰지 않는다. 투명성을 위해 여기에만 기록한다.

- **"super-prompts" 주장 (refuted, vote 0-3)** — "Specifications function as 'super-prompts' that decompose complex
  problems into modular components..."라는 취지의 주장은 3-vote 검증에서 반박됐다(0-3). 출처 2(arXiv:2602.00180) 관련
  논의에서 등장하나 검증을 통과하지 못했으므로, 명세를 "super-prompt"로 프레이밍하는 근거로 사용하지 않는다.
- (참고) SDD의 *효율 보장* 주장 — 출처 2 CAVEAT에 적은 대로, SDD가 워크플로 효율을 보장한다는 주장은 비판(Martin Fowler:
  non-determinism·overhead)에 부딪힌다. 정의적 프레이밍만 채택하고 효율 보장은 주장하지 않는다.

## 방법론 — deep-research 3-vote 적대 검증

- **팬아웃**: SDD 정의·명세 구성요소·명세 대비 검증·comprehension debt 등 다각도로 검색·소스 수집.
- **추출·검증**: 각 주장을 인용 단위로 추출하고 **3-vote 적대적 교차검증**으로 confirmed/refuted를 분류했다(독립성 보존을 위해
  각 논문·글은 primary로 직접 인용).
- **신뢰도 표기**: high(3-0) / medium 등 vote를 출처별로 명시하고, 단일 저자 의견 글·position·정의적 프레이밍에는 CAVEAT를 붙였다.
- **정직성 규칙**: 정량 수치는 vote/CAVEAT와 함께만 인용하고 "개선 N% 보장"은 쓰지 않는다. 반박된 수치·주장은 본문 근거에서 배제하고 위 *반박된 주장* 섹션에만 기록한다.
