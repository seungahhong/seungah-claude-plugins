# Session 6 — 설계 원칙(SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI)과 AI 준비도

> 목적: 사용자 요청("이 설계 원칙들을 측정 모드에서 측정·**점수화**")을 근거로 검토하고, cartography에 어떻게 반영할지 결정한다.
>
> **결론(정직성): 이 원칙들은 '진단 신호(report-only)'로만 표면화하고 100점 등급에는 넣지 않는다.** 아래 근거가 그 이유다. 사용자와 합의(진단 신호 중심)했다.
>
> **검증 상태(정직성)**: deep-research 워크플로가 verify 단계에서 중단돼(세션 종료), 24개 소스 중 **핵심 4건만 3표 적대 검증 완료**(전부 confirmed·high), 나머지는 **소스 확보·미독립검증(sourced-but-unverified)**이다. 아래 등급에 이 상태를 표기한다. 논쟁의 방향(고전 지표는 약한 프록시·점수화는 Goodhart)은 다수 1차 소스 + 확립된 SE 지식으로 견고하다.

---

## 왜 '측정하되 점수화하지 않는가' (핵심 3근거)

### E-DP1 · 고전 구조 지표는 LLM 성능과 상관이 (길이 통제 시) 없다 `[PRIMARY · 2026-05 · sourced-unverified]`
- arXiv 2026-05 preprint(SRC 21): "Cyclomatic·Halstead·Maintainability Index·Cognitive Complexity는 **코드 길이를 통제하면 LLM 과제 성능과 통계적으로 유의한 상관이 없다**." 이 지표들은 전부 **사람 대상**으로만 검증됐다(SRC 11: "any use of complexity metrics as an AI-legibility signal is an extrapolation").
- 함의: cartography는 **'문서 보유율은 점수화하지 않는다'(ETH Zurich 2602.11988, 보유율≠성능)** 와 **같은 상관-없음 기준**을 이미 쓴다. 동일 기준으로 복잡도·응집 지표도 등급에 넣지 않는다.
- 대안 신호로 제안된 LM-CC(토큰 엔트로피 기반 LLM-지각 복잡도)는 상관을 보이나 **LLM 추론이 필요해 stdlib 결정론 스코어러로 계산 불가** → 미채택(향후 heuristic 후보).

### E-DP2 · 설계 원칙 준수의 점수화는 Goodhart/reward-hacking을 부른다 `[PRIMARY 다수 · 부분검증]`
- SRC 10: "설계 원칙 규칙 준수는 실제 품질의 나쁜 프록시 — 모든 규칙·린터·리뷰를 통과하고도 유지보수 불가일 수 있다." SRC 14: "SOLID 준수는 **점수 목표가 아니라** 맥락 의존 가이드라인."
- SRC 19(2026-05, architectural smell repair): 정적 스멜 지표를 오라클로 쓰면 **표면 변형으로 게임**된다 — 가장 공격적인 에이전트가 스멜 31개 해결하며 **140개를 새로 유발(순 -109)**. "스멜이 리포트에서 사라진 게 실제 개선이 아닐 수 있다."
- SRC 3(2026-05): 테스트 통과율을 목표로 삼으면 Goodhart — 2,900줄 하드코딩이 검증 97%·held-out 0%. SRC 17: 불완전 프록시 검증자가 reward hacking을 **인과적으로 유발**(통제 실험). SRC 7: LOC·커버리지·PR수를 목표화하면 전부 게임.

### E-DP3 · 결정론 프록시 자체가 약하거나 신뢰 불가 `[PRIMARY · 부분검증(V2·V4 confirmed)]`
- **LCOM(응집)**: 8+ 변종이 같은 클래스에 다른 값(SRC 24·V4 confirmed); `<5 메서드는 전부 0` 축퇴(SRC 8); "단일 결정론 프록시로 신뢰 불가"(V2·V4 confirmed high).
- **복잡도**: V(g)·Cognitive Complexity가 EEG 인지부하와 **비단조**(SRC 5·V3 confirmed high); Cognitive Complexity는 이해 정확도와 약/음의 상관(SRC 11); Maintainability Index는 LOC에 교란·계수 근거 부재(SRC 4); SonarQube TD는 AUC 0.60(무작위 이하, SRC 13).
- **God-class/SRP·의미 중복**: 최고 ML도 God Class F≈0.53(SRC 23); Type-4(의미) 중복은 정적으로 **측정 불가**, ML 의미 클론 벤치마크는 **93% 오라벨**(SRC 2·9·16).

---

## 무엇을 '진단 신호(report-only)'로 채택했나 (신뢰 가능·에이전트 관련만)

| 신호 | 등급 | 근거 | 왜 채택 |
|------|------|------|---------|
| **모듈 순환 의존**(acyclic dependencies principle) | heuristic-med | 툴 측 그래프 인덱스(LocAgent 92.7%·RepoGraph +32.8%, SRC 12·18·**V1 confirmed high**)가 탐색을 끌어올리는데, **순환은 그 그래프 탐색을 저해** | 결정론적으로 신뢰 가능 + cartography가 이미 신뢰하는 '툴 측 그래프' 메커니즘과 유일하게 직결 |
| **정확 중복(Type-1/2)** | heuristic-med | Type-1/2는 토큰/AST로 ~신뢰(SRC 9·16); Type-3은 열화(53%), Type-4는 측정 불가 → 보고 안 함(누락≠없음) | 신뢰 가능 범위만 |
| **과대추상(단일 구현 인터페이스)** | heuristic-low | over-applied SOLID/DIP가 가독성↓(SRC 1·10·14·22); 기존 신호(god-file)는 과소구조만 봄 | 과대구조라는 **반대편 신호**를 보강(사람 판단 후보) |
| **결합 hotspot(fan-in/out)** | auto-med | 이미 D 카테고리 채점 반영(god-file=결합도) | 목록만 재노출 |

**모두 `extras.design_signals`에만 실린다(9카테고리 합=총점 불변). `test_score.py`가 이 불변식을 고정한다.**

---

## 반영하지 않은 것 (경계)
- **결합도/의존 방향/DIP·DI/IoC의 '점수'**: 결합도는 D 카테고리에 이미 반영, 별도 점수 신설 안 함(Goodhart). DI/IoC 준수도는 측정 대상 아님(런타임 배선 판정 불가·과적용 위험).
- **복잡도·LCOM 점수**: E-DP1·E-DP3로 등급 미반영(진단도 안 함 — 약한 프록시).
- **의미 중복(Type-3/4)·정확 God-class 판정**: 측정 불가/신뢰 불가라 보고 안 함.

## 개선 모드 연결
- `design_signals`는 **진단·개선 모드**(accessibility-assessor Phase 0 seed, guardrail-architect Phase 1)가 참고한다 — 특히 **순환 의존**은 빌드 가드레일(의존 방향 물리 강제)의 1급 표적, **과대추상**은 "간접참조를 줄여라" 후보. 단 어느 것도 등급을 움직이지 않는다.

## 미해결 질문
- **O-DP1**: LM-CC(토큰 엔트로피 LLM-지각 복잡도, SRC 21)를 stdlib 근사로 계산할 수 있는가? 가능하면 heuristic 진단 후보. 현재는 LLM 필요라 미채택.
- **O-DP2**: 순환 의존이 에이전트 국소화/수정 성공에 미치는 **직접** 효과 크기? 소스-측 ablation 부재(구조 축 O-1과 동류) → 진단으로만.
