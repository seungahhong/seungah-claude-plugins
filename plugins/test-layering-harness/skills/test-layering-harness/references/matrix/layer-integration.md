# 계층 카드 — Integration

> **축 카드(계층)**. 방법론과 직교 — "어떤 AC 슬라이스가 **Integration 계층 테스트**가 되는가"만 정한다. 방법론 멤버십은 [`methodology-*.md`](_index.md#4-축-카드-목록), 조합·라우팅·스코프 가드는 [`_index.md`](_index.md), 근거는 [`../research/matrix-criteria-2025.md`](../research/matrix-criteria-2025.md) §1.

## 1. 정체 (scope + size/hermeticity)
- **scope**: 조합된 컴포넌트 간 **인터페이스·상호작용·데이터 교환**(모듈·컴포넌트·상태관리·API 엔드포인트 협업). narrow(경계 코드 + 외부 서비스 double) vs broad(live 서비스 필수) 구분 — broad는 사실상 system/e2e(Fowler). **한정어 없이 "integration"만 쓰지 말 것**.
- **size/hermeticity**: 단일 머신 내(멀티 프로세스/스레드 허용), 네트워크는 오직 localhost(SWE@Google "medium"). 외부 머신/백엔드로 나가면 자격 상실.
- 답하는 질문: "모듈·컴포넌트·API가 함께 동작하나?" 속도 분·비용 중간·RCA 양호.
- caveat: ISTQB CTFL v4.0은 integration을 component-integration + system-integration **2레벨**로 분리 — 단일 "Integration" 카드는 표준 대비 단순화.

## 2. AC 포함 기준 (이 슬라이스가 Integration이 되려면) — AND/우세
- [ ] 슬라이스가 **컴포넌트 간 인터페이스·데이터 교환·계약**을 검증한다(협업이 핵심).
- [ ] narrow integration(경계 코드 + 외부 서비스 double)으로 **단일 머신·localhost 경계** 안에서 검증 가능하다.
- [ ] 값·상태 접근성이 있어 **완전 행위 판정**(정확 pinning)이 실현 가능하다.

## 3. AC 제외 기준 (아니면 어느 계층으로)
- 계산·판정 **로직·단일 unit behavior**의 분기 → [`layer-unit.md`](layer-unit.md) (push-down).
- **live 다중 서비스 필수** / 브라우저 end-to-end 여정 → [`layer-e2e.md`](layer-e2e.md).
- 가드: 외부 머신/백엔드로 나가면 integration 아님(medium 초과). "acceptance" 의도가 계층을 강제하지 않는다(level≠type).

## 4. 오라클 프로필 (principles §5)
- **강함(완전 행위 보존)** — 통합 경계의 값·상태·계약을 명세(AC) 기준으로 단언. E2E보다 상태 접근성이 높아 정확 pinning 가능(E2E의 MR-옵션과 대비).
- implementation-bias 금지: 현재 구현이 내는 값을 그대로 굳힌 오라클 거부(§5-1).
- flaky baseline 선결(§5-3)·false-alarm 인지(§5-5)·실행 그라운딩(§5-2). 스모크/동어반복 어서션 금지(§5-4).

## 5. 테스트 배치 & mock 규약
- **배치(불변식·무조건 강제)**: 테스트 대상(컴포넌트/유틸/모듈) 파일이 있는 **바로 그 폴더**에 `__test__/` 디렉토리를 만들고(없으면 생성) 그 안에 테스트 파일을 둔다(co-locate). **파일명은 `*.test.*`/`*.spec.*` 접미사**(폴더명 무관하게 러너 기본 glob이 매칭 — Jest `testMatch`·Vitest `include`). **이 `__test__/` 규칙은 조건부가 아니다 — 저장소에 이미 다른 배치 관습(`__tests__` 복수·`test/`·bare `*.test.ts`)이 있어도 그것으로 대체하지 않고 항상 `__test__/`를 만들어 그 안에 둔다**(무조건 강제). 러너 config가 특정 폴더로만 매칭을 제한하면 testMatch/include 조정을 게이트 B에서 제안('확인 필요'). **작성 전(게이트 B): 경로가 `.../__test__/…`인지 검사 — 아니면 거부·교정**. 작성 후: `__test__/` 아래 생성 확인.
- **mock**: narrow integration이므로 경계의 외부 서비스는 **실제 API 응답을 캡처해 mock 데이터(fixture)로 주입**해 테스트한다(live API/외부 머신 호출 금지 — live로 나가면 medium 경계를 넘어 계층 자격 상실, §1). 캡처 응답은 fixture로 커밋하고, 계약·상태 오라클은 기대(AC) 기준으로(§4·§7).

## 6. 이 계층 × 방법론 조합 (선택된 방법론 안에서만 — 강도 값 단일 출처 _index §3 lookup)
- **Smoke × Integration = STRONG** — commit-stage smoke의 정본(Fowler CD "소수의 중요한 integration·acceptance 테스트로 이뤄진 작은 smoke suite"). 핵심 통합 지점 정상 경로·결정론·showstopper.
- **Regression × Integration = STRONG** — 미변경 통합 영역 비회귀. safe-RTS(변경 traverse·매핑 불가 시 full fallback).
- **Nightly × Integration = STRONG-ish** — 느린/외부의존 integration + 게이트 selection의 miss를 재검출하는 야간 안전망.
- **Sanity × Integration = DEGEN/WEAK** — smoke 동의어 or 변경 국소 confirmation(transient·무-태그).
- 선택 스코프에 없는 방법론과는 조합하지 않는다(_index §1).

## 7. 근거 & 정직성
- **SOURCE·TIER**: ISTQB Glossary(integration testing) — official-standard, HIGH. IEEE 829-2008 §3.1.8 — official-standard(철회·정의 유효). Fowler IntegrationTest(narrow/broad) — blog, MED. SWE@Google ch.11(medium·localhost 경계) — vendor-doc, MED.
- **caveat**: ISTQB CTFL v4.0은 integration 2레벨(component/system) — 단일 카드는 단순화임을 인지. **Integration 전용 오라클 강도의 2025+ 1차 근거는 못 찾음**(metamorphic·상태커버리지 일반론만) — 수치로 메우지 않는다. 비율% 하드코딩 금지.
