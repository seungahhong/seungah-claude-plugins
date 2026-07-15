# AI Accessibility Rubric — Track B 루브릭 (정본)

`ai_access.py`가 구현하는 6지표 루브릭의 정본. **이 assessment는 '에이전트 성공률 인증'이 아니다** — 개선 후보를 잡기 위한 진단이다. 1차 근거는 `research/ai-accessibility-dossier.md`.

## 왜 대부분 report-only인가 (지배적 단서)

1. **intervention ≠ correlation** — 6지표 중 5개(패턴 일관성·모듈 경계·의존 방향·fine-grained modularity·가이드 유용성 대부분)에서 "저장소의 그 속성을 통제 변경 → 같은 에이전트의 resolve/위반율 델타"를 잰 연구가 **없다**. 대부분의 '에이전트 이득'은 인간-SE 이득 + 첫 원리로부터의 **추론(inferred)**이다.
2. **build enforces, docs explain** — 타입·강제된 의존 방향·실행 테스트처럼 기계가 결정론적으로 검사하는 속성이 산문 문서보다 신뢰도 높다. 그래서 **기계 검증 가능한 사실만 SCORED**. (Anthropic: "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens.")
3. **tool-index ≠ code-structure** — LocAgent(92.7% file-level)·RepoGraph(+32.8% relative)의 localization 이득은 **코드 위에 얹은 그래프 인덱스/검색 도구**의 것이지 저장소 layout의 공로가 아니다. LocAgent ablation: BM25 인덱스 제거 −13.14pp ≫ 그래프 순회 제거 −2.19pp — "localization"의 큰 몫은 code structure가 아니라 고전 IR.
4. **유일하게 측정된 agent-specific 레버 = 독립 oracle** — 에이전트가 스스로 작성/선택한 테스트의 격리-green이 실제 정답이 아닌 경우가 실패의 **81~100%**(arXiv:2606.26978, scaffold 고정·execution만 변화한 통제 개입). 이것이 이 dossier에서 유일하게 *측정된* 레버다.

## 6지표 → 결정론 프록시 · SCORED vs report-only

| 지표 | 결정론 프록시(측정 가능) | 유형 | 신뢰(에이전트 이득) | Goodhart 가드 |
|------|--------------------------|------|--------------------|---------------|
| **M1 의존성 방향 강제** | dependency-cruiser·eslint-boundaries·import-linter·ArchUnit·Nx·TS project refs **설정 존재 + 금지 import가 CI/pre-commit nonzero-exit로 FAIL** | **SCORED**(Gate) | 사실 STRONG(tool) / agent 이득 QUALITATIVE·inferred·**cap** | 규칙 수/모듈 수 보상 금지; behavior·readability 센서와 짝지음 |
| **M2 독립 실행 가능성** | 부분이 전체 없이 build/run/test(runnability gate)·hermetic 러너·**독립 oracle 존재(에이전트 저작과 구별)** | **SCORED**(gate + 독립-oracle 가드) | gate MEDIUM / **false-pass 가드 STRONG** / modularity WEAK | "green 격리 테스트"를 correctness로 credit 금지(81~100% false-pass) |
| **M3 빌드 피드백 품질** | tsconfig `strict`·typecheck·lint·CI 존재·엄격도 | **report-only + 저가중 cap** | task-level MEDIUM / repo-level WEAK(inferred) | pass-rate를 correctness로 credit 금지; tamper-resistance(hidden/read-only 테스트) 별도 확인 |
| **M4 모듈 경계 예측 가능성** | 디렉터리 taxonomy 일관성·cross-module import fan-in/out | **report-only / 저가중** | localization 어려움 STRONG / layout 인과 WEAK | tool-graph 효과(92.7%·+32.8%)를 layout에 귀속 금지; over-fragmentation 플래그 |
| **M5 패턴 일관성** | 모듈 시스템 혼용(ESM/require) 등 (식별자 명명은 Track A A1/A2) | **report-only** | mechanism-inferred(RepoCoder retrieval) | uniformity 자체 보상 금지; misleading-but-consistent가 최악 |
| **M6 에이전트 가이드** | CLAUDE.md/AGENTS.md 존재 + **non-inferable·build-checkable 내용 밀도** | **report-only(약)** | presence≠performance STRONG / non-inferable prose MEDIUM(non-uniform) | bloat·staleness penalize("이 줄 지우면 실수 나나?" 밀도); **자동 생성 금지** |

## 요약: 무엇이 SCORED, 무엇이 REPORT-ONLY

- **SCORED(기계 검증 가능한 사실이라서):** ① M1 의존 방향 강제의 존재·실제 CI fail, ② M2 runnability/buildability gate + 독립 ground-truth oracle 존재. 이 둘만이 "build enforces" 위계의 결정론 사실이자, 그중 독립-oracle 가드는 **유일하게 측정된 agent-specific 레버**.
- **REPORT-ONLY:** M3(저가중)·M4·M5·M6 — 전부 "docs explain / inferred" 층. **에이전트 이득이 측정된 개입이 아니라 추론**이므로 점수 driver로 승격 금지.
- `ai_access.py`의 `enforced_score/enforced_max`는 **SCORED 지표(M1·M2)만의 소계**이며, 100점 인증 등급을 만들지 않는다.

## 넣지 않은 것 (경계)

- **단일 'AI-readiness 인증 등급'을 만들지 않는다** — 대부분 지표가 추론이라 하나의 등급으로 합치면 거짓 정밀. build-enforced 사실 소계 + report-only census로만.
- **tool-index 이득(LocAgent·RepoGraph)을 저장소 등급에 귀속하지 않는다** — 그건 툴 이득이다.
- **에이전트 가이드 자동 생성 금지** — presence≠performance이고 LLM-생성본은 성공률을 낮췄다. 사람 큐레이션 non-inferable 내용만.
- **강제 probe 없이 등급 귀속 금지** — 개입 효과는 고정 에이전트에 대한 통제 probe 없이 저장소 등급/에이전트 성공률로 귀속하지 않는다.

## 개선 순서 (Step B2 입력 · build enforces 우선)

M1(의존 방향 강제) → M2(독립 실행·독립 oracle) → M3(빌드 피드백·opt-in) → M4(모듈 경계·opt-in) → M6(에이전트 가이드·사람 큐레이션). 상세 메커니즘·안전장치는 `ai-accessibility-playbook.md`.
