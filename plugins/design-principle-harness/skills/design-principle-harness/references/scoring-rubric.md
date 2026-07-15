# Scoring Rubric — 코드 설계 품질 (Step 1)

`score.py`가 구현하는 루브릭의 정본. 총점은 **개선 우선순위용 진단 지표(prioritization index)**이지 인증·최적화 목표가 아니다.

## 왜 두 층위인가 (Tier A vs Tier B)

근거는 `research/evidence-dossier.md`. 핵심:

- **명명·주석은 사람 comprehension 근거가 견고**하고, 오도/불일치/stale한 이름·주석은 LLM에도 해롭다. 단 **LLM 대상 식별자 리네임의 효과는 부호가 불안정·과제 의존적**(intent/요약 -11~-29pp·알고리즘 실행 ≈0·모델별 +14~-32pp)이라 단일 수치로 못 쓴다(가드레일 #14). 구조/제어흐름 변경이 LLM엔 식별자 변경보다 **더** 해롭다.
- **고전 구조 지표(cyclomatic·cognitive complexity·Halstead·Maintainability Index·LCOM)는 약한 프록시**다 — (1) 코드 **길이를 통제하면** LLM 과제 성능과 통계적으로 유의한 상관이 없고, (2) 전부 **사람 대상**으로만 검증돼 AI 가독성으로의 외삽이며, (3) LCOM은 8+ 변종이 같은 클래스에 다른 값을 준다.
- **설계 원칙 준수를 점수·게이트로 만들면 Goodhart/reward-hacking**을 부른다 — 정적 스멜을 오라클로 쓰면 표면 변형으로 게임된다(스멜 리포트에서 사라진 게 실제 개선이 아닐 수 있다).
- **개입(intervention) 연구는 없다** — *어떤 점수를 올리면 같은 저장소에서 같은 에이전트의 성공률이 오른다*는 연구는 존재하지 않는다(모든 근거는 perturbation/production). 따라서 모든 구조/설계 하위 점수는 **측정된 예측자가 아니라 추론된 휴리스틱**이고, 총점은 **'안전 기여' 인증이 아니라 설계 부채 hotspot 지도**다(가장 강한 기여 신호=실행 가능 재현 테스트·의존성 무결성은 이 하네스 범위 밖).
- **두 축 등급** — 신뢰도는 **측정 신뢰도**(결정론적으로 잴 수 있나)와 **타당도**(AI 가독성을 실제로 예측하나)로 분리된다. 후자는 **모든 구조/설계 신호에서 외삽**이다. 정밀 계산(예: Maintainability Index)이 타당도를 함의하지 않는다(MI는 원시 LoC보다 못한 예측력).

→ 그래서 사용자의 요청("설계 원칙을 점수화")을 **점수화하되**, 명명/주석(Tier A)은 **높은 가중·act-first**로, 설계 원칙(Tier B)은 **낮은 가중·낮은 confidence·진단 성격·defer**로 싣는다. 사용자의 "쉬운 것부터, 무거운 SOLID는 추후에"라는 순서 요구가 이 근거와 정확히 일치한다.

## Tier A — 표면 가독성 (act-first) /60

| 섹션 | 배점 | confidence | 근거대상 | 측정(결정론) |
|------|------|------------|----------|--------------|
| **A1 Identifier Clarity** (변수·함수·클래스·컴포넌트명) | 28 | medium | LLM | 선언 이름 중 무의미/난독형(tmp·data·foo·단일문자 비관용·무모음 약어) 비율. `clarity = 1 - bad/total`. |
| **A2 Naming Consistency** (규약 일관성) | 12 | weak | human | 언어 기본 관례(py=snake/Pascal, js=camel/Pascal) 위반 비율. 팀 규약 상이 시 오탐 → weak. |
| **A3 Comment Health** (주석 건강도) | 20 | medium | both | **감점식**: 커멘트아웃(죽은 코드) 주석·TODO/FIXME 마커 비율만 감점. **주석 밀도·볼륨은 report-only(많다≠좋다)**. 추가로 **comment-gap 후보**(침묵 예외·매직 넘버·정규식)를 report-only로 표면화 → 개선 모드에서 '왜/맥락' 주석 opt-in 추가 seed(점수 무관). |

A1 가중이 가장 큰 이유: 명명은 **사람 comprehension 근거가 견고**하고 '오도/무의미' 이름이 LLM에도 해롭기 때문이다. 단 LLM 대상 식별자 리네임 효과는 **부호가 불안정·과제 의존적**(intent 과제 -11~-29pp[2510.03178]·알고리즘 ≈0·모델별 +14~-32pp[2505.10443])이라 **단일 수치로 못 쓰고**(가드레일 #14), *어떤 점수를 올리면 같은 에이전트 성공률이 오른다는 개입 연구도 없다*(§0.4). act-first는 '명백히 오도하는 이름'에 한정한다.

## Tier B — 설계 원칙 (defer·진단) /40

각 8점. **전부 낮은 confidence·사람 대상 검증(외삽)·점수 목표 아님**.

| 섹션 | 매핑 | confidence | 측정(결정론) | caveat |
|------|------|------------|--------------|--------|
| **B1 Complexity** | KISS·복잡도 | weak | Python 함수 순환복잡도(AST·정확)·긴 함수; JS 파일 branch density·brace nesting(근사) | 길이 통제 시 LLM 무상관·사람 대상. hotspot=사람이 볼 후보. |
| **B2 Cohesion & Coupling** | SOLID(SRP)·응집/결합 | weak | god-file=fan-in/out 결합도(라인 수 아님). 대형 파일은 보조. | LCOM류 미채택(변종 불일치). SRP 직접 측정 불가. |
| **B3 Duplication** | DRY·중복 | medium | Type-1/2(공백·리터럴 무시) 정확 중복 클러스터 | Type-3/4 정적 측정 불가(누락≠없음). 중복이 항상 해롭진 않음. |
| **B4 Cyclic Dependencies** | 의존 방향·acyclic principle | medium | 모듈(디렉터리) 그래프 Tarjan SCC | Tier B 중 **상대적으로 근거 나음** — 순환은 툴 그래프 탐색을 저해. Python 중첩 패키지 과소탐지. |
| **B5 Over-abstraction** | SOLID(DIP)·DI/IoC·YAGNI·과대추상 | weak | 구현 1개뿐인 TS 인터페이스 + 미참조 파일(report-only) | DI/IoC 준수도 정적 측정 불가. 정당한 경계일 수 있음. |

**사용자 요청 항목 → 섹션 매핑**: SOLID→B2(SRP)·B5(DIP) / 응집·결합→B2 / 복잡도→B1 / 중복→B3 / DI·IoC→B5 / DRY→B3 / KISS→B1 / YAGNI→B5. (OCP/LSP/ISP는 정적 측정 불가 — B5 note에서 report-only.)

## Tier C — AI-맥락 신호 (report-only · 총점 미합산)

사용자 요청(시맨틱 태그·웹 접근성·테스트 설명으로 AI가 코드 맥락을 더 잘 파악)으로 추가한 **프론트엔드·테스트 특화 신호**다. **총점 100(A+B)에 합산하지 않는다** — 아래 근거상 셋 다 report-only가 정직하기 때문이다. 근거 정본은 `research/semantic-a11y-test-dossier.md`.

| 섹션 | 매핑 | confidence | 측정(결정론) | caveat |
|------|------|------------|--------------|--------|
| **C1 Semantic Markup & a11y** | 시맨틱 HTML5·ARIA·접근성 | report-only | JSX/.html/.vue/.svelte에서 native 시맨틱(`button/nav/main/label/h1-6…`) vs `<div/span onClick>`; native로 대체 가능한 `role=`; `alt` 없는 `<img>`; ARIA 속성 수(가점 안 함) | 이득이 **모델 역량 조건부**(강한 모델=full HTML 유리 +11~17.5pp / 약한 모델=a11y-tree 유리)·landmark/heading/button-vs-div 격리 연구 **없음**. **ARIA/role 볼륨 가점 금지**(WebAIM: ARIA 많을수록 오류↑·상관≠인과). |
| **C2 Test Legibility** | 테스트 설명·접근성 셀렉터 | report-only | 테스트 파일의 `it/test/describe` 제목·py `test_*` 명 중 모호/무의미 비율; getByRole/LabelText/Text vs testid/CSS/xpath 셀렉터 census | **올바른 설명은 LLM 이해 이득 미미·오도 설명만 측정 가능한 해악**(비대칭). 제목↔본문 괴리 컴파일러 미검증. accessible selector=refactor-robust(MEDIUM)이나 AI 이해 향상 근거 없음. |

**왜 report-only(총점 미포함)인가**: 세 신호(시맨틱 마크업·a11y·테스트 설명) 중 **직접 개입(intervention) 근거가 있는 것은 없다** — 명명/의미 단서 채널만 LLM 대상 causal 열화가 관측됐다(2504.04372, 78%). 시맨틱 HTML 이득은 역량 조건부이고, a11y-tree는 에이전트 *관측 공간*이라는 관용 사실이지 "ARIA를 더 쓰면 이해가 오른다"는 개입이 아니며, 올바른 테스트 설명의 이득은 통제 연구에서 유의하지 않았다(2404.03114). 그래서 **존재를 가점하지 않고**, 오도/모호/native-대체가능/무-alt 같은 **명백한 결함만 개선 후보 census**로 보고한다. 자동 ARIA/alt/어서션 생성은 confident-but-wrong·green-locks-bug라 **금지**.

## 밴드 (인증 아님·진단 지표)

| 총점 | 밴드 |
|------|------|
| 85+ | Strong (설계 부채 낮음) |
| 70+ | Fair (표면 개선 여지) |
| 50+ | Weak (표면+구조 개선 권장) |
| <50 | Fragile (우선순위 개선 필요) |

밴드는 "이 저장소는 X등급"이라는 **인증이 아니라** 개선 착수 우선순위를 잡기 위한 눈금이다.

## 넣지 않은 것 (경계)

- **복잡도/LCOM을 '준수 점수'로 게이트화**하지 않는다(Goodhart). B1/B2는 낮은 가중 진단.
- **의미 중복(Type-3/4)·정확 God-class 판정**: 정적 측정 불가/신뢰 불가 → 보고 안 함.
- **DI/IoC 준수도**: 런타임 배선이라 정적 판정 불가 → B5는 '과대추상' 근사만.
- **주석 밀도 가점**: 자동 주석 상당수 부정확·"많다≠좋다" → report-only.

## 개선 순서 (improvement_order — Step 2 입력)

스코어러는 각 섹션에 `act_order`를 부여한다: **A3(1) → A1(2) → A2(3) → B3(4) → B1(5) → B2(6) → B4(7) → B5(8)**. 쉽고 근거 강한 것(삭제·리네임) 먼저, 어렵고 근거 약한 구조(SOLID 등) 나중. Step 2가 이 순서대로 승인 게이트를 돈다.
