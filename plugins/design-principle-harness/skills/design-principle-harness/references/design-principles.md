# Design Principles — 참조 카탈로그 (Tier B의 원전과 한계)

Tier B가 다루는 설계 원칙의 **정의 · 결정론적으로 잴 수 있는 것 · 잴 수 없는 것 · 개선 시 주의**. 판정이 아니라 사람이 볼 후보를 만들기 위한 지식이다. 1차 근거는 `research/evidence-dossier.md`.

## SOLID (Robert C. Martin)

| 원칙 | 뜻 | 정적 측정 | 이 하네스 |
|------|----|-----------|-----------|
| **S**RP 단일 책임 | 한 모듈은 한 이유로만 변함 | ✗ '변하는 이유'는 못 잼 → **결합도(fan-in/out)로 근사** | B2 후보 목록 |
| **O**CP 개방-폐쇄 | 확장엔 열리고 수정엔 닫힘 | ✗ | report-only note |
| **L**SP 리스코프 치환 | 하위형은 상위형 자리에 | ✗(런타임 계약) | report-only note |
| **I**SP 인터페이스 분리 | 안 쓰는 메서드 강요 금지 | ✗ | report-only note |
| **D**IP 의존 역전 | 추상에 의존, 구체 아님 | △ 단일 구현 인터페이스=과적용 신호 | B5 후보 |

**정직성**: SOLID는 **맥락 의존 가이드라인이지 점수 목표가 아니다**. 과적용(single-implementation interface, 불필요한 간접참조)은 오히려 가독성을 낮춘다 — B5는 그 "반대편(과대구조)" 신호를 본다.

## 응집(Cohesion)·결합(Coupling)

- **결합(Coupling)**: 모듈 간 의존. `fan-in/fan-out`으로 결정론 측정 가능(CK 메트릭 계열의 CBO에 해당). god-file은 **라인 수가 아니라 결합도**로 정의한다(에이전트 편집 정확도로 검증된 라인 수 임계값은 없다).
- **응집(Cohesion)**: 모듈 내부 요소의 관련성. **LCOM(Lack of Cohesion of Methods)은 8+ 변종이 같은 클래스에 다른 값**을 주고 `<5 메서드는 전부 0`으로 축퇴 → **신뢰 불가라 채택 안 함**. B2는 결합도만 신뢰 신호로 쓴다.

## 복잡도(Complexity) — KISS

- **Cyclomatic Complexity(McCabe)**: 분기 경로 수. `1 + 분기 수`. Python은 AST로 정확, JS는 근사.
- **한계(핵심)**: 코드 **길이(SLOC)와 강상관**이라 길이 통제 시 정보량이 준다. Cognitive Complexity·V(g)는 EEG 인지부하와 **비단조**. **전부 사람 대상 검증** — LLM 가독성 근거로는 외삽. → B1은 weak, hotspot은 후보.
- **KISS**(Keep It Simple): 복잡도가 낮을수록 좋다는 휴리스틱. 점수 목표화 금지.

## 중복(Duplication) — DRY

- **클론 타입(Roy & Cordy)**: Type-1(완전 동일)·Type-2(식별자/리터럴만 다름)·Type-3(구문 유사·추가/삭제)·Type-4(의미 동일·구문 상이).
- **잴 수 있는 것**: Type-1/2는 토큰/정규화로 신뢰 측정. **Type-3은 열화·Type-4는 정적 측정 불가**(ML 의미 클론 벤치마크는 상당 비율 오라벨). → B3은 Type-1/2만, "누락≠없음".
- **DRY 정직성**: **중복이 항상 해로운 것은 아니다**(Kapser & Godfrey). "잘못된 추상화보다 중복이 싸다"(Sandi Metz) — 3곳+·같은 이유로 변하는 것만 제거 후보.

## DI/IoC (Dependency Injection / Inversion of Control)

- 의존을 **밖에서 주입**(생성자·컨테이너)해 결합을 낮추고 테스트를 쉽게. Fowler.
- **정적 측정 불가**: DI/IoC 준수도는 런타임 배선 판정이 필요하고 과적용 위험이 커, **점수화하지 않는다**. B5는 '과대추상(단일 구현 인터페이스)' 근사만 본다.

## YAGNI (You Aren't Gonna Need It)

- 지금 필요 없는 기능/추상을 미리 만들지 말라. Fowler.
- **근사**: 미참조 파일·단일 구현 인터페이스=speculative generality 후보. 단 공개 API·엔트리·동적 로드 오탐이 잦아 **report-only**.

## Tier C — AI-맥락 신호 카탈로그 (report-only · 총점 미합산)

사용자 요청으로 추가한 프론트엔드·테스트 특화 신호. 1차 근거는 `research/semantic-a11y-test-dossier.md`. **셋 다 직접 개입 근거가 없어 점수화하지 않고 census/결함 후보로만 본다.**

### 시맨틱 마크업 (Semantic HTML5)
- **뜻**: `<button>/<nav>/<main>/<article>/<label>/<h1-6>` 같은 native 시맨틱 요소로 UI 의미를 표현(“div soup” 대신).
- **잴 수 있는 것**: native 시맨틱 vs `<div/span onClick>` 비율, native 대체 가능한 `role=`, `alt` 없는 `<img>` — 전부 정규식 census.
- **한계(핵심)**: LLM/에이전트 이해 이득은 **모델 역량 조건부**(강한 모델=full HTML 유리 +11~17.5pp WorkArena L1 / 약한 모델=a11y-tree 유리 −8~−19pp; 저자 동일군 2604.01535·2605.29397). **landmark/heading/button-vs-div를 격리 측정한 직접 연구는 없다.** → C1 report-only.

### 웹 접근성 (ARIA / WCAG)
- **뜻**: role·accessible name·상태를 노출해 보조기술(과 에이전트 accessibility tree)이 UI를 이해.
- **정직성(중요)**: **ARIA 볼륨은 위험 신호다** — 페이지의 ARIA가 많을수록 감지 오류가 더 많다(WebAIM Million: 2026년 59.1 vs 42.0/page, 방향성만·상관≠인과·WebAIM 자체 caveat). **bad ARIA is worse than none**('First rule of ARIA': native 우선). WCAG의 **~25~40%만 자동 검사 가능**. 자동/LLM 생성 ARIA·alt·overlay는 confident-but-wrong·harm·Goodhart 벡터. → 존재 가점 금지, native 대체가능 role만 결함 후보, 자동 생성 금지.

### 테스트 설명 (Descriptive names · GWT/BDD · accessible selectors)
- **뜻**: 테스트 제목/설명이 대상·동작·기대결과를 담아 사람·AI가 본문 없이 의도를 파악하도록. accessible 셀렉터(getByRole)로 의도 표현.
- **정직성(핵심 비대칭)**: 통제 연구상 **올바른/누락 문서는 LLM 이해에 유의한 이득이 없고, 오도 문서만 측정 가능하게 해롭다**(2404.03114). 테스트를 LLM 오라클로 쓰면 구현을 굳혀 버그를 은폐한다(overfitting·2511.16858; 오라클은 expected 아닌 actual 인코딩 2410.21136). 제목↔본문 괴리는 컴파일러 미검증. accessible selector는 refactor-robust(MEDIUM·vendor idiom)이나 **AI 이해 향상 근거는 없다**. → C2 report-only, 오도/모호만 삭제·리네임, 자동 어서션 금지.

## 한 줄 요약

> Tier B는 **결정론적으로 신뢰 가능한 것(결합도·Type-1/2 중복·순환 의존)** 만 점수 신호로, **약하거나 못 재는 것(LCOM·의미 중복·DI/IoC·SRP '이유')** 은 report-only/근사로 다룬다. Tier C(시맨틱 마크업·a11y·테스트 설명)는 **직접 개입 근거가 없어 총점에 넣지 않는 report-only census**다. 모든 점수는 **진단이지 목표가 아니다.**
