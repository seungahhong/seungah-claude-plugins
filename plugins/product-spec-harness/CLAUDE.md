# product-spec-harness

기획자(PM)가 요구·문제(또는 기획안 초안)로부터 **PRD·사용자 스토리·인수조건**을 7단계 인터랙티브로 작성·검증하는 도메인 무관 멀티 에이전트 하네스(개발 착수 *전* 단계).

사용자용 개요·사용법은 [README.md](README.md), 흐름·게이트·입력 모드(R/A/B)의 정본은 [SKILL.md](skills/product-spec/SKILL.md), 재갱신 경로(마무리 §1 R0~R7)는 [regeneration-path.md](skills/product-spec/references/regeneration-path.md)다.

## Conventions (핵심 불변식)

규칙 본문은 SKILL.md와 `references/`에 있다. 여기에는 수정할 때 깨뜨리면 안 되는 불변식과 그 위치만 적는다. **규칙을 바꾸면 `references/`(방법론 정본) → SKILL.md·`agents/` → evals → README 순으로 맞춘다.**

- **산출 파일은 정확히 4개** — `PRD.md`·`user-stories.md`·`acceptance-criteria.md`·`product-spec-review.md`(opt-in). 1·2차 검증 리포트·카드·대장·이력은 파일로 만들지 않고, 재갱신해도 수는 늘지 않는다(SKILL.md "산출물 배치").
- **승인 게이트** — 매 Phase 산출물을 보여주고 승인 후 진행, 파일은 쓰기 전 미리보기 승인. PRD 루프는 회차당 게이트 1개 + 확인 질문 최대 1개(Phase 2 "이 루프의 불변식").
- **네 점검은 대상·축이 다르다** — Phase 1(원본 기획안)·2.3(PRD 초안)·4(PRD↔스토리)·6(스토리↔인수조건). 보완 문답·재갱신은 수집·배선이지 다섯 번째 점검이 아니다(SKILL.md "네 번의 점검").
- **인수조건 단일 원본** — Given-When-Then 문장은 `acceptance-criteria.md`에만, `user-stories.md`는 `[인수조건 인계]` 메모만.
- **발명 금지** — 기획안·카드에 없는 정책·수치는 `[확인필요]`로 되돌린다. 건너뜀을 '보완됨'으로 승격하지 않는다(§1.1).
- **ID 동결** — `FR-n`/`NFR-n`/`US-n`/`AC-n.m`은 주소라 재번호·재사용하지 않는다. 현재 출처는 `출처: US-n`이 정본(regeneration-path R3).
- **비평·게이트에 거부권 없음** — 사용자가 확정·진행을 고르면 따르고 잔존은 부록 B에 기록한다.
- **정직성** — 점수·백분율·성숙도 등급 금지(유일 예외 = Phase 1 INVEST 점수표와 3단 착수 판정). 보완 후 재채점 금지, `기준 입력 v{N}`은 식별자. PRD 본문의 성공지표 수치는 이 금지 대상이 아니다.
- **기획 설계 ≠ 기술 설계** — API·데이터 모델·컴포넌트 등은 산출하지 않는다(`references/prd-design-checklist.md`).
- **독립성** — 다른 마켓플레이스 플러그인을 참조·의존하지 않는다. 방법론은 `references/`에 내재화한다.
- 8개 에이전트 협업 하네스이므로 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
