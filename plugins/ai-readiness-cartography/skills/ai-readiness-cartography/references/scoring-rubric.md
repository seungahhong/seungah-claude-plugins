# AI-Ready Codebase Rubric · v3 (100 pt · 9 categories + 2 blocking gates)

이 문서는 자동/수동 채점의 단일 진실 기준이다. v2에서 2025~2026 1차 근거로 리팩토링됐다(근거·판정은 [research/](research/) 세션 md, 결정 서열은 [research/README.md](research/README.md) 참조).

## v2 → v3 요약 (무엇이 왜 바뀌었나)

| 변경 | 근거 |
|------|------|
| **집계: 순수 가중합 → 가중합 + blocking gate(등급 상한)** | Kenogami lowest-as-ceiling·Factory 게이팅 (session-5 C8) |
| E(검증) 15→**22**, 실행 신호 최상위 | ORACLE-SWE: reproduction/test +26~27pp (session-1 C1) |
| D(의존) 15→**18**, "mermaid 존재"→기계 판독 그래프 | LocAgent file-level 92.7% (session-4 C2) |
| A(navigation) 15→**8**, "보유율"→structure-first anchor | ETH Zurich 반증(2602.11988)·RepoMirage (session-2·4) |
| B(context) 20→**15**, 절대 line 수→redundancy·command-first | ETH Zurich·context rot (session-2 C3·C4·C6) |
| C(tribal) 20→**12** | 비discoverable 정보만 이득 (session-2 C5) |
| god-file: 라인 수 임계값→**fan-in/out 결합도** | 라인 수는 agent용 근거 부재 (session-4 C8) |
| **신규 H(feedback-loop /9)·I(env & task-discovery /5)** | DevEx·Factory 8-pillar (session-5 C6·C7) |
| G(outcomes) 5→**3**, success ⁄ efficiency 분리 | Lulla et al. (session-5 C5) |
| 모든 지표 **auto / heuristic / manual 라벨** | 자동화 범위 명확화 (session-5 C9) |

## 등급 밴드 + 게이팅

| Score | Level | Badge |
|-------|-------|-------|
| 90-100 | **AI-Native** | green |
| 75-89 | **AI-Ready** | green |
| 60-74 | **AI-Assisted** | amber |
| 40-59 | **AI-Fragile** | amber |
| <40 | **AI-Hostile** | red |

**게이팅(핵심)**: 하나의 blocking gate가 실패하면 등급에 **상한 AI-Fragile**을 씌운다 — 총점이 높아도 blocking 결함이 있으면 AI-Ready 이상으로 올라가지 못한다. 순수 가중합은 blocking 결함을 다른 고득점에 희석해 오탐을 낸다(session-5 C1·C8).

### Gate-1 · Reference Integrity *(Auto, 등급 상한)*
문서(CLAUDE.md/AGENTS.md/ADR)가 인용한 **파일 경로·line range**에 **dangling(비존재) 참조가 1건이라도 있으면 실패**. hallucinated path는 agent를 능동적으로 오도한다(session-3 C1·C5). 절대 % 임계값이 아니라 **dangling 0**이라는 검증 가능한 불변식(비율은 모델·연도 의존, session-3 C9). *명령 실재·패키지 lock 대조는 session-3의 함의이나 v3 스코어러 미구현 — 향후 확장 후보이며, 그때까지는 LLM 수동 보강 항목이다.*
> **정직성**: score.py는 dangling *후보*를 flag한다. 첫 세그먼트가 실제 top-level 엔트리이거나 `./`·`../`인 repo-상대 경로만 검증해 precision을 높였고(placeholder 제외), **repo 경계 밖으로 resolve되는 참조는 probe하지 않고 검증 대상에서 제외**한다(보안·traversal 가드). 그래도 illustrative 예시(`_docs/feature-x-spec.md`)를 flag할 수 있다 → 스킬 워크플로에서 LLM이 후보를 확인해 실 dangling만 gate에 반영한다.

### Gate-2 · Executable Verification *(Auto, 등급 상한)*
실행 가능한 **test/build/lint 명령이 하나도 없으면 실패**(package.json scripts·Makefile·pyproject/tox·CI + 실제 test 파일). reproduction/실행 신호는 agent 성공률 최대 기여자이므로 그 부재는 blocking(session-1 C1).

---

## 카테고리 (근거 서열: 실행·검증 ≫ 의존 구조 > 문서)

### E. Verification & Executable Signals · /22 *(Auto · auto-high)*
> 근거: ORACLE-SWE(2604.07789) — reproduction/test 신호가 성공률 최대 기여(+26~27pp).

| Sub | 항목 | Pts | 만점 기준 |
|-----|------|-----|-----------|
| E1 | Reference Accuracy | 6 | dangling path·line-range 0 (Gate-1 연동, 분모=검증한 path+range 참조) · 검증 대상 0건이면 중립 3점 |
| E2 | Executable Verification | 10 | test 명령 + 실제 test 하네스 + build (Gate-2 연동) · Go/Rust/JVM 매니페스트는 build만 자동 인정, test 명령은 실제 테스트 흔적(파일/디렉토리) 필요 |
| E3 | CI test pipeline | 4 | CI 워크플로가 test/build/lint 실행 |
| E4 | Independent critic | 2 | CODEOWNERS + PR template |

(하위합 6+10+4+2 = 22 = E max)

*E2가 최고 배점인 이유*: 정적 문서보다 실행·검증 신호가 성공률에 압도적 기여.

### D. Dependency & Structure Mapping · /18 *(Auto · auto-high)*
> 근거: LocAgent(2503.09089) — 기계 판독 의존 그래프가 embedding retrieval 대비 localization 우위.

| Sub | 항목 | Pts | 만점 기준 |
|-----|------|-----|-----------|
| D1 | 기계 판독 의존 그래프 | 8 | import 그래프 파싱 가능(Python AST·JS 상대 import) + workspace edges |
| D2 | 모듈 경계 명확성 | 4 | 2+ 모듈 + 명시적 cross-module edge |
| D3 | 결합도 기반 god-file | 4 | fan-in+fan-out hotspot 적음 (**라인 수 아님**) |
| D4 | Architecture doc/mermaid/deps 섹션 | 2 | (부차) 구조화된 의존 표현 |

*god-file은 결합도(fan-in/out)로 정의한다.* 라인 수(>500)는 "휴리스틱, 근거 약함"으로 보조 신호일 뿐 — agent 편집 정확도로 검증된 라인 임계값은 없다(session-4 C8).

### B. Context Quality: Novelty & Discipline · /15 *(Heuristic · heuristic-med)*
> 근거: ETH Zurich(2602.11988) — 문서 존재≠성능, 중복·산문 overview는 순비용(추론 token +20%).

| Sub | 항목 | Pts | 만점 기준 |
|-----|------|-----|-----------|
| B1 | Redundancy discipline | 5 | context가 README/코드와 중복 낮음 + 산문 overview 최소 |
| B2 | Command-first | 4 | exact runnable command + done 검증 기준 |
| B3 | Non-obvious patterns | 3 | Why/Note/Gotcha 등 실패 유발 hidden rule |
| B4 | Key files | 3 | 실제 수정 파일 3-5개 경로 |

*절대 line 수 목표(v2의 25-35줄)는 삭제*했다 — "150-200"은 지침 개수지 줄 수가 아니며(session-2 C9), conciseness는 redundancy discipline으로 조작화한다.

### C. Tribal Knowledge Externalization · /12 *(Heuristic · heuristic-med)*
> 근거: ETH Zurich — 이득은 비자명·비discoverable 정보에서만.

Five-Question(owns/patterns/non-obvious/deps, 각 2점) + MEMORY.md·ADR store(4점). "존재" 이진 가점이 아니라 **비discoverable 지식**에 방점.

### H. Feedback-Loop Latency & Quality · /9 *(Auto · auto-med)* — 신규
> 근거: DevEx(Forsgren et al.)·Factory Agent Readiness. **근거 등급 Med**(CONFIRMED보다 낮음).

| Sub | 항목 | Pts |
|-----|------|-----|
| H1 | pre-commit hook(husky/.pre-commit/lefthook) | 3 |
| H2 | static type config(tsconfig strict·mypy/pyright) | 3 |
| H3 | fast lint/format(ruff·eslint·biome·prettier) | 3 |

피드백을 앞단(컴파일·커밋 시점)으로 옮겨 위반이 PR 전까지 조용히 누적되지 않게.

### A. Navigation & Structure-First Anchors · /8 *(Heuristic · heuristic-med)*
> 근거: RepoMirage(2605.26177) — 파일 노출이 아니라 structure-first anchor가 레버. 보유율은 성능과 무관(2602.11988).

| Sub | 항목 | Pts |
|-----|------|-----|
| A1 | Root entry briefing(존재 + 진입점 명시) | 3 |
| A2 | Structure-first anchors(context가 의존 이웃·진입점 명시) | 5 |

**보유율(coverage %)은 점수화하지 않는다**(진단 정보로만 보고) — "CLAUDE.md 존재" 가점은 근거에 반한다(session-2 C1).

### F. Freshness & Self-Maintenance · /8 *(Auto · auto-med)*
> 근거: Ashik et al.(2604.09515) — stale context가 실행가능성 42.55%로 저하·능동적 오도.

| Sub | 항목 | Pts |
|-----|------|-----|
| F1 | Stale-drift(context mtime vs 코드 + dangling drift) | 4 |
| F2 | CI/hook path·reference validation | 4 |

### I. Environment & Task-Discovery Reproducibility · /5 *(Auto · auto-med)* — 신규
> 근거: Factory Agent Readiness·agent-readiness-score. **근거 등급 Med**.

| Sub | 항목 | Pts |
|-----|------|-----|
| I1 | Env repro(devcontainer·Dockerfile·.env.example·setup) | 3 |
| I2 | Task discovery(CONTRIBUTING·issue/PR template) | 2 |

### G. Agent Performance Outcomes (success ⁄ efficiency) · /3 *(Auto · auto-med)*
> 근거: Lulla et al.(2601.20404) — success와 efficiency는 독립적으로 움직임.

| Sub | 항목 | Pts |
|-----|------|-----|
| G1 | success telemetry(evals/benchmarks·결과 파일) | 2 |
| G2 | efficiency telemetry(token·latency·cost 단서) | 1 |

**합계 = 22+18+15+12+9+8+8+5+3 = 100** (+ 2 blocking gates)

---

## ROI 표기 규약

- **Effort**: S (<1h) / M (1-4h) / L (4h+)
- **Impact**: 정량 우선 — "task당 N min", "토큰 X% 절감", "회귀 Y건 catch". gate 관련 액션은 "등급 상한 해제"를 명시.
- **Evidence grade**: 각 액션에 auto-high / auto-med / heuristic-med 라벨(근거 강도).
- **Priority** = impact_score / effort_hours 로 자동 정렬. gate 실패 해소가 최상위.

## 넣지 말 것 (근거 부재 — 정직성)

- "N줄 초과 = agent 정확도 X% 하락" 형태 정량 감점 (session-4 C8: 1차 근거 부재).
- readability를 성공률 인과로 직접 연결 (session-1 C5: 패턴 차이만 확인).
- 특정 hallucination % 임계값 고정 (session-3 C9: 모델·연도 의존).
- human-oriented 포매팅(들여쓰기·공백) 가점 (session-1 C3: LLM에 무익).
