# 계층 카드 — Unit

> **축 카드(계층)**. 방법론과 직교 — 이 카드는 "어떤 AC 슬라이스가 **Unit 계층 테스트**가 되는가"만 정한다. 방법론 멤버십은 [`methodology-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 2025+ 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §1.

## 1. 정체 (scope + size/hermeticity)
- **scope**: 개별 컴포넌트/함수/연관 클래스 묶음의 **내부 로직**. solitary(모든 협력자 double)든 sociable(실제 협력자 동반)든 "단일 unit의 behavior"를 검증하면 unit — 실제 협력자를 쓴다는 사실만으로 자동 integration이 되지 않는다(Fowler UnitTest).
- **size/hermeticity**: 단일 프로세스(대개 단일 스레드), sleep·I/O·blocking·네트워크·디스크 없음(SWE@Google "small"). 네트워크/디스크 차단 sandbox에서 통과.
- 답하는 질문: "이 함수/판정 로직이 맞나?" 속도 초·비용 쌈·RCA 정확.

## 2. AC 포함 기준 (이 슬라이스가 Unit이 되려면) — AND/우세
- [ ] 슬라이스가 **계산·판정·검증 로직**(단일 unit behavior)이다.
- [ ] 협력자를 실제로 쓰든 double하든 **단일 unit의 동작**을 격리 검증한다.
- [ ] 자원이 **단일 프로세스·외부의존 0**(네트워크/디스크/프로세스 경계 없음)이다.
- [ ] 경계값·에러·edge 분기까지 **값 수준으로 단언** 가능하다.

## 3. AC 제외 기준 (아니면 어느 계층으로)
- 컴포넌트 간 **인터페이스·데이터 교환** 협업(단일 머신·localhost) → [`layer-integration.md`](layer-integration.md).
- live 다중 서비스 필수 / 핵심 사용자 여정 → [`layer-e2e.md`](layer-e2e.md) (단 하위에서 잡히면 push-down).
- **가드**: `small=unit` 1:1 매핑 금지 — out-of-process 의존을 전부 double하면 broad-scope도 small일 수 있다(SWE@Google 반박). 계층은 scope+size **결합**으로 판정.

## 4. 오라클 프로필 (principles §5)
- **강한 값-동등(S1) 오라클이 실현 가능**하고 정밀하다(RCA 정확). 기대 상태·불변식을 값 수준에서 단언한다.
- ⚠️ **Regression과 조합 시 최고위험 오라클**: LLM이 명세가 아니라 현재 구현을 굳혀 버그를 초록으로 은폐(green-locks-bug) — [`methodology-regression.md`](methodology-regression.md)의 완화(AC 기준 오검증·실행 그라운딩)를 반드시 적용.
- 스모크·동어반복 어서션 금지(§5-4): 틀렸을 때 실제로 실패해야 한다.

## 5. 이 계층 × 방법론 조합 (선택된 방법론 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Regression × Unit = STRONG(멤버십)·최고위험 오라클** — 경계/에러/edge 회귀의 정본. unit은 cheap → retest-all 종종 충분.
- **Smoke × Unit = WEAK** — unit은 게이트 전량 실행이라 별도 smoke 선별 저부가. showstopper 저수준 단위(인증 토큰 파싱 등)일 때만.
- **Sanity × Unit = DEGEN/WEAK** — ISTQB상 smoke 동의어 → transient change-scope(confirmation)로만, `@sanity` 안 심음.
- **Nightly × Unit = DEGEN(빈셀)** — unit은 빠르고 싸서 게이트 소속, 이연 근거 없음.
- 선택 스코프에 없는 방법론과는 조합하지 않는다(_index §1).

## 6. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(component testing) — official-standard, HIGH. IEEE 829-2008 §3.1.7(개별 컴포넌트 격리) — official-standard(문서 철회·정의 어휘 유효). Fowler UnitTest(solitary/sociable) — blog, MED. SWE@Google ch.11(small·size⊥scope·hermeticity) — vendor-doc, MED.
- **caveat**: `small=unit` 1:1은 folklore(SWE@Google 반박). green-locks-bug 전이율·오라클 강도 정밀수치는 특정 벤치마크 산물 → 하드코딩 금지. 비율% 하드코딩 금지.
