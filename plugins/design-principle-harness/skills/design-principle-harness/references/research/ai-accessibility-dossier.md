# AI 접근성(에이전트 이해·수정 용이성) 근거 dossier

> 대상: design-principle-harness의 신규 "AI Accessibility" 트랙. 6개 지표(pattern consistency / build-type feedback / module-boundary predictability / dependency-direction enforcement / standalone verifiability / agent-guide·context files)가 "AI 코딩 에이전트가 코드를 읽고 안전하게 수정하기 쉬운가"를 측정한다고 주장하려면 어떤 근거가 있고 어디까지가 추론인지를, 적대적 검증 결과를 반영해 정직하게 정리한다.
>
> 표기 규약: 각 주장에 **SUBJECTS**(LLM / agent / human / production / tooling) · **CONFIDENCE**(STRONG=동일 에이전트 대상 통제 개입 / MEDIUM / WEAK / QUALITATIVE) · **CITATION**을 붙인다. 검증에서 DROP·REFUTED된 수치는 본문에 사실로 부활시키지 않는다.

---

## 0. 지배적 단서 (dossier 전체를 지배하는 4개 원칙)

**① build enforces, docs explain — 기계 검증 가능 속성 > 산문.**
타입·강제된 의존 방향·실행 가능한 테스트처럼 기계가 결정론적으로 검사하는 속성은 산문 문서보다 신뢰도 높은 신호다. Anthropic 자신도 이 위계를 명시한다 — "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens" (code.claude.com/docs/en/best-practices, verbatim 확인). 문서의 **존재(presence)는 에이전트 성능이 아니며**, stale/wrong 문서는 misleading-comment와 같은 방식으로 에이전트를 적극적으로 오도한다.

**② intervention ≠ correlation.**
"동일 에이전트에, 조건만 바꿔, 성공률 델타를 측정"한 개입(intervention) 근거와, 인간-SE 이득·상관관계·관용(idiom)을 구분한다. 이 dossier에서 6개 지표 중 **동일-에이전트 통제 개입으로 직접 측정된 것은 소수**다(naming 저하, compiler feedback, context-file 유무, execution 접근 유무). 나머지 대부분은 인간-SE 이득 + 첫 원리로부터의 **추론(INFERRED)**이다.

**③ 대부분 지표의 "에이전트 이득"은 측정된 개입이 아니라 추론이다.**
"모듈 경계를 예측 가능하게 만들면 → 같은 에이전트의 localization이 오른다", "의존 방향을 강제하면 → 같은 에이전트의 위반율이 내려간다", "hermetic하게 격리하면 → 같은 에이전트의 self-verify가 좋아진다" 를 **repo 구조를 통제 변경해 측정한 연구는 검색 범위에서 하나도 없다.** 이들은 REPORT-ONLY 또는 저가중 후보로 두어야 한다.

**④ tool-index ≠ code-structure 귀속.**
LocAgent(92.7% file-level) · RepoGraph(+32.8% relative)의 이득은 **코드 위에 얹은 그래프 인덱스/검색 도구(tooling)**가 만든 것이지, 코드 자체 구조의 속성이 아니다. RepoGraph는 심지어 LocAgent 내부 ablation에서 **BM25 인덱스 제거(88.32→75.18, −13.14pp)가 그래프 순회 제거(88.32→86.13, −2.19pp)보다 ~6배 더 아팠다** — "localization 성공"의 큰 몫은 code structure가 아니라 고전 IR 인덱싱이다. 이 tool 효과 크기를 code layout·build enforcement의 공으로 귀속하는 것은 misattribution이다.

**Goodhart 경고(전 지표 공통):** 6개 지표 모두 게이밍 가능하다 — 과도한 over-modularization, 상투적 boilerplate 문서, tautological 테스트, 체커를 만족시키되 설계를 악화. 특히 **테스트/컴파일 통과가 보상 신호가 되는 순간, 에이전트는 그것을 해킹**한다(ImpossibleBench: mutable/visible 테스트에서 one-off SWE-bench impossible 과제의 ~76%를 exploit, 숨기면 near-zero). 어떤 지표든 "규칙 수·모듈 수·문서 줄 수"가 아니라 **존재·정확성·의미**를 보상하고, 별도 behavior 센서로 게이밍을 잡아야 한다.

---

## 1. pattern-consistency (패턴 일관성)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| repo 내 유사 스니펫을 retrieval few-shot로 프롬프트에 주입하면 **같은 모델**의 완성 정확도가 오른다 (일관 repo가 돕는 메커니즘) | LLM | STRONG (개입, params frozen) | arXiv:2303.12570 (RepoCoder, EMNLP 2023) |
| 식별자 이름을 저하(alpha-rename·모호·cross-domain·misleading)시키면 LLM 이해가 측정 가능하게 하락, intent 과제(summarization)에서 최악 — misleading 이름이 neutral rename보다 더 해롭다 | LLM | STRONG (name-only 개입, behavior 고정) | arXiv:2510.03178 ("When Names Disappear") |
| 식별자 익명화는 code search/clone detection을 단조 저하; method/function-**definition** 이름이 가장 중요 | **encoder(CodeBERT)** | ~~STRONG~~ → **MEDIUM (agent 관련성)** | arXiv:2307.12488 |
| LLM 생성 코드는 host-repo 관용(idiom·API·formatting)과 자주 불일치 | LLM/production | MEDIUM (관측) | arXiv:2407.00456 ("Beyond Functional Correctness") |
| context가 많을수록 좋은 게 아님 — 중간 tier(signatures+docstrings)가 few-shot로 오독되어 더 작은 context보다 **저하** | LLM | MEDIUM (개입) | arXiv:2406.11927 (RepoExec) |

**검증된 효과 크기(digit까지 확인):**
- 이름 난독화, ClassEval summarization: GPT-4o **87.3→58.7 (−28.6)**; Llama4-Maverick **86.2→66.4 (−19.8)**; Qwen3-Coder-480B **87.2→72.1 (−15.1)**; DeepSeek-V3 **87.7→76.7 (−11.0)**. LiveCodeBench(generic 1–2자 이름)에서는 drop <3pt. 난독화는 **semantics/behavior-preserving**(구문·제어·데이터 흐름 고정, 식별자만 변경). — arXiv:2510.03178 (Table 2, verbatim 확인)
- 익명화, Java code-search MRR **70.36→17.42**(random)/17.03(shuffled); Python **68.17→24.09**/23.73; clone F1 Java 94.87→86.77/84.76. — arXiv:2307.12488 (**단, subject는 CodeBERT encoder**)
- style 불일치 유병률: 66.2/82.4/88.5/89.9% (CodeLlama-7B/StarCoder2-7B/DeepSeekCoder-1.3B/6.7B) — arXiv:2407.00456

### 반증·caveat
- **타깃 개입은 어느 연구도 직접 수행하지 않았다:** "기존 repo를 내부적으로 더 일관되게 만들면 → 같은 에이전트가 더 잘 확장한다"는 링크는 RepoCoder의 retrieval 메커니즘을 통해 **추론**된 것이지 직접 측정이 아니다.
- **RepoCoder 이득은 tooling(retrieval+iteration)의 것**이지 raw consistency 자체가 naive 에이전트를 돕는다는 증거가 아니다. "in-repo redundancy가 exploitable하다"는 증거일 뿐.
- **naming 저항성 = memorization 라는 프레이밍은 REFUTED(→§3).** 2510.03178은 그런 귀속을 하지 않는다 — LiveCodeBench 저항은 **구조/알고리즘 단서 + generic 이름** 때문이라고 논문 스스로 말한다.
- **style/idiom 일관성 → 이해 향상은 입증되지 않았다.** 2407.00456은 LLM 자기 출력의 품질을 잴 뿐(그 출력이 readability **89.5%** / conciseness **76.5%** / robustness **94.2%** — 검증에서 교정된 수치, 원 findings의 86.2/79.9/93.8은 오기·cross-contamination), downstream 에이전트의 이해·확장 성공을 재지 않는다. clean null도, 타깃 링크 증거도 아니고 **접선적**이다.
- non-monotone context(RepoExec)는 "친숙해 보이는 context를 더 쑤셔넣기"가 역효과를 내는 Goodhart형 실패다(정확한 pass@1 수치는 이번 pass 미검증, thesis만 확인).

### 루브릭 결론
- **결정론 측정:** (a) in-repo 유사 선례/near-duplicate 밀도(retriever가 표면화 가능한가) + (b) **naming 품질/일관성**(의미 있고·오도하지 않고·convention-uniform한 식별자). 둘 다 개입 근거 존재.
- **scored vs report-only:** (b) naming은 **SCOREABLE** — 단, 가장 깨끗한 STRONG 근거는 2510.03178(실제 생성 LLM)이고 2307.12488은 **encoder/CodeBERT 보강 근거로만** 인용(primary 아님). (a) redundancy는 mechanism-level SCOREABLE(RepoCoder, tooling 매개임을 명기). **layout/idiom style 일관성은 REPORT-ONLY** — 정당화는 "demonstrated null"이 아니라 **"직접 근거 부재(양방향 모두)"**로.
- **confidence:** 전체 **MEDIUM** — 내부 패턴 일관성의 이해→확장 링크는 mechanism-inferred이지 intervention-proven이 아님.
- **Goodhart 가드:** uniformity 자체가 아니라 *의미 있는* 일관성을 보상. **misleading-but-consistent 이름이 최악**(적극 오도 + memorization으로 점수 부풀림). "친숙해 보이는 context 과적재"도 역효과. 같은 에이전트의 확장 성공이 실제로 오른다는 증거 없이 일관성에 점수 주지 말 것.

---

## 2. build-type-feedback (빌드·타입 피드백 품질)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| 반복적 compiler feedback이 낯선 strictly-typed 언어를 습득시키는 지배적 학습 신호 — GPT-5 Idris **22/56 → 54/56** | LLM | MEDIUM (개입, 단일 모델·56과제) | arXiv:2602.11481 |
| strict 타입이 노출하는 장애물은 대개 표면적(scope·naming·컴파일 규율)이지 깊은 타입이론 추론이 아니며, 정밀한 진단이 이를 고치게 한다 | LLM | MEDIUM | arXiv:2602.11481 |
| 구조화·표적 피드백 > 모호한 안내: mixed **63.6** > LLM-Expert 62.9 > test 57.9 > minimal 53.1 > compiler 49.2 > LLM-Skilled 48.8 (Repair@1, 5모델 평균) | LLM | MEDIUM | arXiv:2504.06939 (v2, Table 2) |
| self-repair의 진짜 병목은 fix 적용이 아니라 **자기 코드를 진단(좋은 피드백 생성)하는 능력** — 더 강한 피드백 모델로 교체하면 훨씬 큰 이득 | LLM | STRONG (통제 swap) | arXiv:2306.09896 |
| 테스트 통과가 agentic SWE의 de-facto 검증 oracle(SWE-bench) | agent/production | QUALITATIVE (정의적) | SWE-bench framing |

**검증된 수치:**
- GPT-5 Idris: zero-shot **22/56(39%)** → local-compile+iterative **54/56(96%)**, doc-manual only 34/56(61%), platform-test 1-iter 27/56(48%). 두 문제는 20 iteration 후에도 미해결(helpers/types/harness의 cascading 컴파일 오류). — arXiv:2602.11481 (verbatim 확인, 진짜 *agent 신호 개입*)
- FeedbackEval Repair@1: mixed 63.6 / LLM-Expert 62.9 / test 57.9 / minimal 53.1 / compiler 49.2 / LLM-Skilled 48.8 — arXiv:2504.06939 v2 (Table 2, digit까지 확인). 논문 스스로 "LLM-Skilled가 최저, minimal보다도 못할 때가 있음".
- ImpossibleBench: GPT-5 **Oneoff-SWEbench 76%** exploit (verbatim 확인). **hidden 테스트는 cheating을 near-zero로, read-only는 중간.** — arXiv:2510.20270

### 반증·caveat
- **detailed ≠ better:** compiler feedback(49.2%)은 거의 최하위, LLM-"skilled"(48.8%)는 bare "the code is wrong"(minimal 53.1%)보다도 못함. 풍부함/양보다 품질·객관성이 중요.
- **비용 보정 시 self-repair는 종종 wash:** 피드백 생성 토큰을 세면 이득이 "modest, 편차 큼, 때론 없음", GPT-4 self-debug는 human debug에 크게 뒤짐. — arXiv:2306.09896
- **oracle 자체가 게이밍 가능(핵심 Goodhart):** 테스트가 보상이고 mutable/visible이면 frontier 모델은 테스트를 수정/삭제하거나 leak된 fix를 검색한다. 체커 신호를 강화하면 해킹 유인도 강화된다. — arXiv:2510.20270
- **repo-level "strong typing이 repo를 AI-editable하게" 는 개입 미검증:** typed vs untyped 같은 real repo에서 같은 에이전트 성공 델타를 잰 연구 없음. Idris 이득은 **그 과제에서의 진단 품질**이지 typing-vs-not이 아니다.

### 루브릭 결론
- **결정론 측정:** compiler/type 피드백 품질 — **REPORT-ONLY + 저가중 score cap.**
- **scored vs report-only:** 고신뢰 점수 driver로 만들지 말 것. task-level 개입 근거(정밀·조기 진단이 iterative solve율↑)는 견고하나 repo-level은 추론.
- **confidence:** "clear·early·precise 오류가 self-repair를 돕는다" **MEDIUM**; "static typing이 주어진 repo의 agent editability를 높인다" **WEAK**(추론, repo-level 개입 부재).
- **Goodhart 가드(필수):** 테스트/컴파일 통과는 에이전트가 해킹할 바로 그 oracle이므로, 점수는 *검증 신호의 존재·품질*을 보상하되 **tamper-resistance(hidden/read-only 테스트·sealed history)를 별도 게이트**하고, 체커 수정·fix 검색에서 나올 수 있는 pass-rate를 절대 credit하지 말 것.
- **DROP:** "66% conflicting SWEbench"(실제 54.0%), "93% conflicting LiveCodeBench"(실제 headline ~1%; 92%는 weak-prompt 조건 한정) — 부활 금지. self-repair HumanEval +4.9–17.1 / MBPP +16–30, "Opus 4.8 Max 87.1→73.0" SWE-bench Pro 라인은 **UNVERIFIABLE**(모델 라벨도 garbled 가능) — 하드 수치로 인용 금지.

---

## 3. module-boundary-predictability (모듈 경계 예측 가능성)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| code localization("어느 파일/함수를 고칠지")은 repair/edit와 별개의 인정된 어려운 병목 | agent | STRONG | arXiv:2503.09089 (LocAgent), arXiv:2410.14684 (RepoGraph), arXiv:2502.00350 (OrcaLoca) |
| repo의 구조적 의존 그래프(파일/클래스/함수 + import/invoke/inherit edge)를 에이전트에 노출하면 embedding·BM25 baseline보다 localization 정확도↑ | agent(LLM) | STRONG | arXiv:2503.09089, arXiv:2410.14684 |
| 구조 navigation은 특히 **hidden dependency**(어휘는 안 겹치나 아키텍처로 결합)에서 도움 | agent | MEDIUM | arXiv:2602.20048 (CodeCompass) |
| 단순 **텍스트** dir/file tree만으로도 Agentless의 계층적 localization이 작동 | LLM | MEDIUM | arXiv:2407.01489 (Agentless) |
| 이득은 **기존 구조를 표면화하는 tooling**의 것 — repo 구조 변경이 아님 | agent | STRONG | arXiv:2410.14684, arXiv:2503.09089 |

**검증된 수치(headline 전부 확인):**
- LocAgent file Acc@1 (SWE-Bench-Lite): **77.74%**(LocAgent+Claude-3.5) vs 72.63%(Agentless) vs 52.55%(embedding); fine-tuned Qwen2.5-32B **92.70%**; downstream Pass@10 **33.58→37.59**; cost **−86%**. — arXiv:2503.09089
- **ablation(가장 정직한 caveat):** BM25 인덱스 제거 88.32**→75.18**(−13.14pp)가 TraverseGraph 제거 88.32→86.13(−2.19pp)보다 **~6배 더 아픔** — "localization"의 큰 몫은 code structure가 아니라 IR 인덱싱. — arXiv:2503.09089
- RepoGraph: 4 baseline 평균 **+32.84%** relative, 그러나 불균등(RAG +99.63%, Agentless +8.56%); repo당 ~1,419 nodes/26,392 edges. — arXiv:2410.14684
- CodeCompass: graph nav **99.4%** vs vanilla 76.2%/BM25 78.2% (hidden-dep, +23.2pp) — 그러나 semantic 과제에선 BM25가 이기고 구조 과제에선 graph가 vanilla에 뒤짐. **58% trial이 툴 호출 0회.** — arXiv:2602.20048

### 반증·caveat
- **귀속이 헤드라인 caveat:** 위 전부 *에이전트 tooling*에 대한 개입(그래프 인덱스를 변경 없는 repo에 볼트온)이지 repo 구조 개입이 아니다. 어느 논문도 에이전트를 고정한 채 모듈 경계/디렉터리 배치를 개선해 localization lift를 재지 않았다.
- **인덱스 > 그래프:** 위 ablation 참조. localization 성공의 상당 부분이 코드 구조가 아니라 고전 IR.
- **구조가 안 돕거나 해치기도:** CodeCompass는 semantic 이름 과제에서 graph가 BM25에 지고, 구조 과제에서 vanilla에도 뒤짐(G2에서 graph tool 0% 호출).
- **over-tooling 역효과:** RepoNavigator — 구조 tool을 더 주면 성능 악화(single jump-to-def tool이 multi-tool을 이김). *(정확한 IoU 26.43 vs 17.59, 24.28→13.71은 방향만 확정, 수치는 미검증 → directional로만.)* — arXiv:2512.20957
- **채택이 진짜 병목:** graph tool을 쓰면 99.5% ACS, 무시하면 80.2%(=vanilla), 58% trial이 지시에도 0 호출. 레버는 prompt formatting이지 code layout이 아니었다.
- **new-file 배치("새 코드 어디에")는 측정한 소스 없음:** localization 벤치마크는 *기존* edit site 찾기이지 *신규* 파일의 올바른 배치가 아니다. "예측 가능 구조가 배치를 돕는다"는 관용/human-SE 이득으로 취급.

### 루브릭 결론
- **결정론 측정:** convention-conformance(일관된 디렉터리 taxonomy, 낮은 cross-module import fan-in/out, 경계 명확성)를 측정 가능 프록시로.
- **scored vs report-only:** **REPORT-ONLY / 저가중.** repo 자체 경계·layout을 바꿔 같은 에이전트 localization/배치가 오른다는 개입 근거는 **사실상 0**.
- **confidence:** "localization은 어렵고 tool로 고칠 수 있다" **STRONG**; "code-structure 예측 가능성 자체가 인과 레버" **WEAK**.
- **Goodhart 가드:** 절대 tool-graph 효과 크기(LocAgent 92.7%, RepoGraph +32.8%)를 layout의 공으로 credit하지 말 것 — 이들은 *tool* 이득이다. 잘게 쪼갠 many-tiny-modules는 오히려 해칠 수 있음(over-tooling analogue). 고정 에이전트에 대한 통제된 구조 변경 개입이 있기 전엔 layout 지표를 인과 driver로 scoring 금지.
- **REFUTED-DROP:** RepoGraph "surfaces structural information already present…" **인용부호 붙은 verbatim quote는 논문에 없음** — 인용부호·귀속 제거, 분석가 추론으로만 진술. "~53.5% function match" / "avg 3,010 files·438K LOC"는 UNVERIFIABLE(OrcaLoca SOTA는 오히려 65.33%).

---

## 4. dependency-direction-enforcement (의존 방향 강제)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| build-time 아키텍처 강제(ArchUnitNET/NSDepCop가 빌드 실패)가 에이전트에 "실패를 보고 궤도 수정"을 강제 | agent | QUALITATIVE (추론, 무측정) | NimblePros blog |
| "Documentation provides hints, but linters provide rules — AI can ignore docs, but cannot ignore linting errors in CI" | agent | QUALITATIVE | the-main-thread |
| 결정론적 repo-level 강제 > 안내 문서(AGENTS.md는 "wishful thinking") — 코드를 편집하는 같은 모델이 일탈도 정당화하므로 독립 제어점 부재 | agent | QUALITATIVE | the-main-thread |
| fitness function이 구조적 정확성(모듈 경계·의존 방향 A→B not B→A)을 "unit test의 아키텍처 대응물"로 검증, 회귀 시 merge 차단 | human/production | MEDIUM (확립된 실무, Building Evolutionary Architectures 2nd ed. 2023) | InfoQ, O'Reilly ch.4 |
| repo를 directed heterogeneous graph로 표현하면 LLM 에이전트의 구조적 원거리 코드 localization·추론↑ | LLM/agent | STRONG (통제 개입) | LocAgent, arXiv:2503.09089 |
| 금지 import를 save/commit/CI마다 실패시키는 성숙한 tooling 존재(eslint-plugin-boundaries, dependency-cruiser, import-linter, ArchUnit/ArchUnitTS, Nx boundaries, TS project refs) | human | STRONG (tool 능력, agent 결과 아님) | tool docs |

**검증된 수치:**
- LocAgent: file-level up to **92.7%**, GitHub issue-resolution **+12% Pass@10**, fine-tuned Qwen-2.5-Coder-32B **~86% cost 절감** — arXiv:2503.09089. **단, 이는 graph 구조 표현이 에이전트의 *읽기*를 돕는 것이지 의존 방향의 *build-time 강제*가 아니며, directed vs undirected ablation도 없다.**
- "73% security-defect 감소" (Marri 2026 banking-microservices, spec-layer 제약) — InfoQ에 verbatim + 자기제한 caveat "one case study is not a generalization" 동반. **build-enforced import 방향이 아니라 specification-layer 제약.**
- "96%가 AI 코드를 완전히 신뢰 안 함, 48%만 커밋 전 항상 검증" — Sonar State of Code (동기 부여용, 효과 측정 아님).

### 반증·caveat
- **의존 *방향* 강제가 같은 에이전트 성공을 높이거나 위반율을 낮춘다는 직접 개입 근거 0.** 모든 강제 주장(NimblePros, Phoebe, the-main-thread)은 추론 또는 단일 일화 — A/B도, 위반율 델타도 없음. 인간-SE 이득 + 첫 원리로부터의 추론.
- **귀속 문제:** LocAgent 이득은 **구조 가시성**(의존 지각)의 것이지 금지 import의 **build-time blocking**과는 다른 메커니즘. LocAgent를 강제의 근거로 인용하면 misattribution.
- **강제는 negative guarantee만:** known-bad edge를 막을 뿐, 올바른 모듈을 고르게 하지 못하고, 잘못 인코딩된 규칙은 옳은 변경을 hard-block할 수 있음.
- **Goodhart:** 강제는 "아키텍처를 깬다"를 "체커를 만족시킨다"로 바꾼다 — 에이전트가 import 규칙은 통과하며 더 나쁜 설계를 낼 수 있음. Goodhart 원칙 근거는 arXiv:2510.02840 "Take Goodhart Seriously"(확인), arXiv:2103.14659 **"Alignment of Language Agents"**(정확한 제목으로 인용 — "specification gaming"이 제목 아님). *("함수를 과도하게 쪼개 readability를 해친다"는 예시는 arXiv:2601.08129(scheduling 도메인)에서 출처된 것이 아님 — 분석가의 code-domain 외삽; 2601.08129는 Goodhart 취약성 원칙과 "orthogonal axes + adversarial sensor" 완화 근거로만 인용.)*

### 루브릭 결론
- **결정론 측정:** 금지 import가 실제 dependency-cruiser/eslint-boundaries/import-linter/ArchUnit/Nx/TS-refs 설정으로 **CI/pre-commit에서 FAIL(nonzero exit)** 하는가 — auto-detectable한 사실.
- **scored vs report-only:** 이 좁은 build-observable 사실은 **SCORED**(Gate-3 enforcement gate). "설정 존재 + 실제 실패"는 결정론적 사실이므로.
- **confidence:** 에이전트에 특별히 도움이 된다는 신뢰는 **QUALITATIVE/inferred** — 강한 human-SE·tooling 근거 + 간접 LocAgent read-evidence(다른 메커니즘) + 직접 개입 연구 0. credit에 **cap** 씌우고 "inferred, not agent-measured" 라벨.
- **Goodhart 가드:** 강제의 *존재·정확성*을 보상, **규칙 수/모듈 수는 절대 아님**(more boundaries ≠ better). enforcement credit은 반드시 behavior/readability 센서와 짝지어 — 체커는 만족시키되 설계를 악화시키는 에이전트를 잡도록. LocAgent 92.7%를 build-time blocking의 공으로 귀속 금지.

---

## 5. standalone-verifiability (독립 검증 가능성)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| 각 에이전트 궤적을 clean container로 격리하는 것은 신뢰할 검증의 전제(안 하면 한 실행이 환경 오염) — 단 이는 *평가* 격리이지 대상 코드의 내부 modularity가 아님 | agent/production | STRONG (확립된 실무) | SWE-bench harness, AI21 blog |
| hermetic(격리·완전 선언 의존) build/test는 결정론적·역사적 재현 결과; non-hermetic은 "역사적 재현 결과를 주지 않음" | human/CI/production (**agent 아님**) | STRONG (속성), 단 subject는 human/CI | Bazel docs |
| 코드는 executable·inspectable·stateful하므로 좋은 에이전트 검증 기질; Plan-Execute-Verify가 sandbox 실행+결정론 센서+human gate 사용 | agent | QUALITATIVE (개념 서베이) | Code as Agent Harness, arXiv:2605.18747 |
| 환경 buildability/executability가 에이전트 issue-resolution의 hard gate — "실행·테스트 가능 환경 없이는 해결 불가", 환경 setup 포함 시 성능 크게 저하 | agent | MEDIUM (벤치마크 확립, 델타 미추출) | arXiv:2512.06915 (Multi-Docker-Eval) |
| **실행 접근을 줘도 scaffold 고정 시 marginal repair 성공은 놀랍도록 작다**(SWE-bench APR) | agent | STRONG (통제 개입) | arXiv:2606.26978 (To Run or Not to Run) |
| over-mocking은 blind spot 생성 — 격리 unit test는 green인데 실제 통합은 틀림 | human/LLM(inferred) | QUALITATIVE (실무자, 논증적) | understandlegacycode, wiremock |

**검증된 수치(2606.26978, digit까지 전부 확인 — 진짜 agent 통제 개입: scaffold 고정, execution 접근만 변화, 200 instance·3,000 run):**
- Prohibited vs Unrestricted resolve gap = **1.25pp, 유의하지 않음(p>0.05, McNemar)**. Claude Code **63%(무실행) vs 64%(실행)**, 실행은 +토큰·+wall-clock 비용.
- OpenCode(Qwen2.5-Coder-32B): gap **≈0pp**, 무실행이 **~3× 적은 토큰**.
- 에이전트는 어차피 많이 실행: 평균 **8.8 test runs/task**.
- **self-validation 불신뢰(핵심):** 실패 케이스의 **81–100%가 에이전트-실행 validation은 통과하나 공식 SWE-bench 평가는 실패**(Claude Code 81.2%, Codex 100%). OpenCode는 11%만.
- **54–66%가 단일 edit로 완료**(localization이 issue text에서 이미 쉬움; localization 정확도는 두 모드 모두 >95%).

### 반증·caveat
- **가장 강한 agent 개입 근거가 naive 주장에 반한다:** SWE-bench APR에서 코드를 runnable로 만들고 실행시켜도 ~0–1.25pp(유의하지 않음). "runnable slice → 에이전트 self-verify 향상"은 fault localization이 이미 쉬운 과제에서 일반 효과로 지지되지 않는다. 실행 이득은 "균일하지 않고 집중적"이며 "default가 아니라 명시적 cost-benefit trade의 resource"로 취급.
- **reward-hacking(격리-green ≠ correct)은 에이전트에서 실측으로 크다:** self-chosen 테스트 suite는 green인데 ground truth는 실패(실패 케이스의 81–100%). 이는 유일하게 측정된 agent-specific 위험 — **더 많은 runnability가 아니라 독립 oracle**을 요구.
- **"modular/DI/ports-adapters/hermetic → agent 이득" 사슬은 거의 전부 추론:** Bazel hermeticity 이득(결정론·culprit-finding·parallel caching)은 human+CI에 대해 측정·논증됨. "repo X의 modularity/격리를 개선 → 같은 에이전트 resolve율↑"의 clean 실험은 검색 범위에 없음. agent-measured에 가장 가까운 레버는 환경 *buildability*(에이전트가 아예 실행할 수 있는가)이며, 이는 gate이지 fine-grained modular isolation과 같지 않다.
- **mocking 반증은 qualitative/theoretical**(실무자 소스; production-failure 데이터셋 없음; 인간 대상). agent-specific 버전은 미측정.

### 루브릭 결론
- **결정론 측정:** 부분이 전체 없이 build·run·test(hermetic) 가능한가 = **runnability/buildability gate + fast-feedback 전제.**
- **scored vs report-only:** (1) **runnability/buildability gate — SCORE**(2512.06915 + SWE-bench 격리로 뒷받침). (2) **에이전트-저작 테스트와 구별되는 독립/ground-truth oracle, "green 격리 테스트"를 correctness로 credit 금지 — 이 Goodhart 가드를 SCORE**(2606.26978의 81–100% false-pass, 이 각도에서 유일한 *측정된 agent-specific* 결과, 전체에서 가장 강한 단일 레버). (3) "fine-grained modularity/DI/ports-adapters/hermeticity → agent self-verify" credit — **REPORT-ONLY, LOW–MEDIUM, 명시적 INFERRED**(Bazel 등 CI/human best practice에서, agent 개입 미검증).
- **confidence:** buildability gate MEDIUM(측정); false-pass Goodhart 가드 STRONG(측정); modularity→self-verify WEAK–MEDIUM(추론).
- **Goodhart 가드:** "green 격리 테스트"를 correctness 증거로 보상하지 말 것 — 측정된 실패 모드가 바로 self-validated green ≠ ground-truth correct. hermeticity는 *runnable 테스트 볼륨*이 아니라 *oracle의 결정론·재현성*으로 credit.
- **DROP/HEDGE:** SWE-bench Pro(arXiv:2509.16941)의 public/commercial 정확 split(≤23.3%/≤17.8%)은 매핑 미확인 — **directional로만**(frontier ~17–23% on 어려운 enterprise repo vs >70% Verified). SetUpAgent(arXiv:2503.07701)의 "~20–30%/55–75%/2.37×(+137%)"는 **UNVERIFIABLE** — 정성 주장(runnable 환경 자동 구성은 부분만 해결)만 유지. **"SetUpAgent/RepoLaunch" 혼동 교정**(RepoLaunch는 SWE-bench-Live 계열, 2503.07701 아님).

---

## 6. agent-guides-context (에이전트 가이드·컨텍스트 파일)

### 핵심 주장

| 주장 | SUBJECTS | CONFIDENCE | CITATION |
|---|---|---|---|
| repo-level context 파일(AGENTS.md/CLAUDE.md)은 일반적으로 코딩 에이전트 성공을 높이지 **않으며**, LLM-생성본은 약간 해친다 | agent | STRONG (통제 개입) | arXiv:2602.11988 "Evaluating AGENTS.md" (ETH Zurich/LogicStar) |
| LLM-생성 context는 8개 model×benchmark 중 **5개에서 성공률 하락**(≈−0.5% SWE-bench Lite, −2% AGENTbench)하며 추론 비용 **>20%↑** | agent | STRONG | arXiv:2602.11988 |
| 에이전트는 context-file 지시를 충실히 따르나(behavior 변함) **instruction-following ≠ success** — 파일이 테스트를 더 돌리고 파일을 더 읽게 하나 옳은 파일에 더 빨리 도달하진 않음 | agent | STRONG | arXiv:2602.11988 |
| behavior 변화는 실재·측정 가능: `uv`가 context에 명명되면 인스턴스당 ~**1.6×** 호출 vs 미명명 시 <0.01× | agent | STRONG | arXiv:2602.11988 |
| Anthropic 지침: CLAUDE.md는 *non-inferable* 맥락(build 명령·style 일탈·repo etiquette)의 prescriptive best-practice이지 측정된 성능 레버 아님; **bloat는 해롭다** | production/vendor | QUALITATIVE | code.claude.com/docs/en/best-practices |
| llms.txt는 production에서 거의 소비되지 않음 — 존재가 사용을 함의하지 않음 | production | MEDIUM (실무자 로그) | otterly.ai; medium.com/@kaispriestersbach |

**검증된 수치(2602.11988, digit까지 전부 확인 — 진짜 same-agent 통제 개입):**
- LLM-생성: −0.5%(SWE-bench Lite), −2%(AGENTbench), 8개 중 5개 하락; cost +20%(SWE)/+23%(AGENTbench); steps +2.45/+3.92; reasoning tokens GPT-5.2 +22%/+14%.
- `uv` 1.6×/인스턴스(명명 시) vs <0.01×(미명명).
- AGENTbench = 138 instances, 12 Python repos, models = Claude Code(Sonnet-4.5)/Codex(GPT-5.2·GPT-5.1 mini)/Qwen Code(Qwen3-30b-coder).
- **Anthropic verbatim:** "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" · "the file is probably too long and the rule is getting lost" · "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens" · exclude "Anything Claude can figure out by reading code".
- **llms.txt:** OtterlyAI 90일 — 62,100+ AI-bot 요청 중 **84건(~0.1%)**만 /llms.txt 도달 (otterly.ai 확인).

### 반증·caveat
- **가장 강하고 직접적인 근거가 popular 주장의 반박이다:** 유일한 통제 개입(2602.11988)이 context 파일은 돕지 않고 종종 이득 없이 비용만 든다고 — "그냥 AGENTS.md 추가해" vendor/실무자 조언과 정면 충돌.
- **presence ≠ consumption ≠ performance:** llms.txt가 가장 깨끗한 예 — 대량 생성, ~0.1% 실제 retrieval. 문서 존재는 vanity 신호.
- **instruction-following ≠ task success:** behavior는 실제로 바뀌나(측정됨) 성공은 오르지 않음. "에이전트가 문서를 따랐다"를 "더 잘했다"와 동일시하지 말 것.
- **human-written 이득은 marginal·non-uniform(교정):** 개발자 작성본이 LLM-생성본을 4개 에이전트 모두에서 이긴 것은 맞음. 그러나 *no-context 대비*로는 "Claude Code를 제외한 모든 에이전트"에서만 개선 — 즉 균일하게 양(+)이 아니고 한 에이전트는 무이득. ~+4%는 그 null/음을 가리는 평균. **STRONG이 아니라 MEDIUM.**
- **stale/wrong-doc 해악은 간접 지지:** RepoMirage(arXiv:2605.26177)의 perturbation은 **semantics-preserving 구조 변형**(context 추론 수요를 높이는 stress test)이지 false/misleading 내용 주입이 아니다. "degrading/obscuring repo context가 에이전트를 해친다"는 지지하나 "stale/wrong 주석"형 해악의 clean 증거는 아님 — 그 penalty는 **analogy·inferred이지 empirically measured 아님**(RepoMirage-Extend 66.8→25.3만 표면화, per-perturbation drop 미확인).
- **vendor 유인 caveat:** Anthropic/agents.md 지침은 prescriptive·unmeasured — 효과 크기 근거로 인용 금지.

### 루브릭 결론
- **결정론 측정:** agent-guide 파일의 **존재·범위** + **non-inferable·build-checkable 내용**(코드가 드러낼 수 없는 정확한 build/test/env 명령)의 밀도.
- **scored vs report-only:** presence는 **약한 REPORT-ONLY 신호**, success 예측자 아님. 점수 준다면 **non-inferable·build-checkable 내용에만** 주고 상한(cap). bloat/staleness는 **penalize.**
- **confidence:** "presence ≠ performance" **STRONG**; "curated non-inferable prose가 marginal하게 돕는다" **MEDIUM**(non-uniform).
- **Goodhart 가드:** "이 줄을 지우면 실수가 생기나?" 밀도를 보상(줄 수가 아니라). 길거나 틀린 파일은 adherence를 입증적으로 저하시키고 stale comment처럼 오도한다. **자동 생성 금지**(LLM-생성본이 5/8에서 하락).

---

## 적대적 감사 결과 (명시 목록)

### VERIFIED-CLEAN
- **arXiv:2303.12570 RepoCoder** — 제목·venue·">10% in all settings" headline·iterative retrieval 메커니즘 확인. *(단 GPT-3.5 per-cell 40.56→56.81 EM 등 정확 셀은 미재확인.)*
- **arXiv:2510.03178 "When Names Disappear"** — Table 2 전 수치 digit까지 일치, 난독화는 semantics-preserving. STRONG clean.
- **arXiv:2307.12488** — MRR/F1 수치 확인(단 subject는 encoder → DOWNGRADED).
- **arXiv:2407.00456** — 유병률 66.2/82.4/88.5/89.9% 확인.
- **arXiv:2602.11481 Idris** — 22/56→54/56(96%)·34/56·27/56·20-iteration cascade caveat 전부 verbatim. 진짜 agent 신호 개입.
- **arXiv:2504.06939 FeedbackEval** — Repair@1 6수치 digit까지 일치.
- **arXiv:2306.09896** — 3개 정성 주장(진단이 병목·강한 feedback 모델 swap·비용보정 wash) 확인.
- **arXiv:2510.20270 ImpossibleBench** — Oneoff-SWEbench **76%** 확인, hidden→near-zero 방향 확인.
- **arXiv:2503.09089 LocAgent** — 77.74/92.70/−86%·Pass@10 33.58→37.59·ablation(BM25>graph) 전부 확인.
- **arXiv:2410.14684 RepoGraph** — +32.84%·RAG +99.63%·Agentless +8.56%·1,419/26,392 확인.
- **arXiv:2602.20048 CodeCompass** — 99.4/76.2/78.2·+23.2pp·58% zero-call 확인.
- **arXiv:2512.20957 RepoNavigator** — single-tool 우세·more-tools-hurt 방향 확인.
- **arXiv:2407.01489 Agentless**, **arXiv:2502.00350 OrcaLoca**(function match SOTA 65.33%) — 실재·framing 확인.
- **arXiv:2606.26978 "To Run or Not to Run"** — 1.25pp(p>0.05)·63 vs 64·OpenCode ≈0pp·8.8 runs·81–100% false-pass·54–66% single-edit·>95% localization 전부 digit까지 확인. **이 각도의 척추.**
- **arXiv:2605.18747 Code as Agent Harness** — executable/inspectable/stateful verbatim, QUALITATIVE 서베이로 정확 라벨.
- **arXiv:2512.06915 Multi-Docker-Eval**, **arXiv:2509.16941 SWE-Bench Pro** — 실재·정성 framing 확인.
- **arXiv:2602.11988 "Evaluating AGENTS.md"** — 저자(Gloaguen·Mündler·Müller·Raychev·Vechev, ETH/LogicStar)·−0.5/−2%·5/8·cost+20/+23%·steps+2.45/+3.92·`uv` 1.6× 전부 digit까지 확인.
- **arXiv:2605.26177 RepoMirage** — 실재, Extend 66.8→25.3 확인.
- **arXiv:2510.02840 "Take Goodhart Seriously"**, **arXiv:2601.08129**(Goodhart 원칙·mitigation) — 실재 확인.
- **Anthropic best-practices 3 인용 · Sonar 96%/48% · OtterlyAI 0.1%** — verbatim 확인.

### DOWNGRADED
- **arXiv:2307.12488**: subject는 **CodeBERT(encoder)**이지 생성 LLM 아님 → agent 관련성 STRONG→**MEDIUM**, 보강 근거로만.
- **arXiv:2407.00456 품질 수치**: 원 findings 86.2/79.9/93.8은 오기(readability 86.2%는 다른 논문 cross-contamination). 실제 **89.5/76.5/94.2**. 또한 이 논문은 comprehension null을 *증명*하지 않음 — "style은 report-only"는 "직접 근거 부재"로 정당화(demonstrated null 아님).
- **arXiv:2103.14659**: 정확 제목은 **"Alignment of Language Agents"**(제목이 "specification gaming" 아님) — 정확히 인용.
- **arXiv:2601.08129**: scheduling 도메인 — "함수 과분할" code 예시를 이 논문에서 출처한 것처럼 제시 금지(분석가 외삽); Goodhart 원칙·mitigation 근거로만.
- **RepoNavigator IoU 수치**·**CodeCompass G1/G2 breakdown** — 방향만 확정, 정확 수치는 lightly-held.
- **human-written context "+4%"** → marginal·non-uniform(한 에이전트 무이득), STRONG→**MEDIUM**.
- **RepoMirage as "stale/misleading doc harm"** → perturbation이 semantics-preserving이므로 그 penalty는 analogy·inferred.
- **ImpossibleBench** → headline band는 76%(oneoff)만, "66–93% band" 아님.
- **SWE-bench Pro public/commercial split** → directional만.
- **SetUpAgent 회복률·2.37×** → 정성 주장만.

### REFUTED-DROPPED (사실로 부활 금지)
- **"2510.03178이 LiveCodeBench 저항을 memorization으로 귀속"** — 논문에 없음. 구조/generic 이름으로 귀속. **memorization-confound 프레이밍 삭제.**
- **RepoGraph "surfaces structural information already present…" verbatim quote** — 논문에 없는 **fabricated 인용**. 인용부호·귀속 제거, 분석가 추론으로만.
- **ImpossibleBench "66% conflicting SWEbench"**(실제 54.0%) / **"93% conflicting LiveCodeBench"**(실제 headline ~1%; 92%는 weak-prompt 조건 한정) — DROP.
- (참고: DOI·arXiv ID 수준 hallucination은 6각도 전체에서 **0건** — 모든 ID가 실재 논문으로 resolve.)

### UNVERIFIABLE (이번 pass 확인·부인 불가 — 하드 수치 인용 금지)
- RepoCoder per-cell EM/ES·RepoEval 크기(1,600/1,600/373)·"≥2 iteration에서 vanilla RAG 능가" 임계.
- RepoExec per-context pass@1(38.65/35.66/32.96).
- self-repair HumanEval +4.9–17.1 / MBPP +16–30 (WebSearch 요약).
- "Opus 4.8 Max 87.1→73.0 / 63% 검색" SWE-bench Pro 라인(모델 라벨 garbled 가능).
- "~53.5% function match" · "avg 3,010 files/438K LOC".
- 2606.26978 부차 수치(2–19 range·57.9% late·OpenHands 42→72%).
- RepoNavigator 정확 IoU · CodeCompass G1/G2 percentages · RepoMirage per-perturbation drop.
- SetUpAgent 회복률·2.37×; SWE-bench Pro 정확 split; AGENTS.md "60k+ projects/25+ tools"(자기 보고); llms.txt "20,000-domain operator" 일화.

---

## 본 하네스가 채택할 결론 — AI Accessibility 트랙 설계

**설계 원칙: 측정 가능한 프록시로 결정론적으로 재고(re-cast)하되, 각 지표의 "에이전트 이득" 신뢰 등급을 노출하고, 개입(빌드 가드레일 추가·가이드 작성)은 승인 게이트 뒤에만.**

### 6지표 → 결정론적 프록시 · scored vs report-only

| 지표 | 결정론 프록시(측정 가능) | scored / report-only | 신뢰(에이전트 이득) | Goodhart 가드 |
|---|---|---|---|---|
| **pattern-consistency** | (a) naming 품질(오도 안 함·convention-uniform, AST 기반) · (b) in-repo near-duplicate/선례 밀도 | **naming = SCORED(cap)** / layout·idiom style = **REPORT-ONLY** | naming MEDIUM–STRONG(2510.03178) / 확장링크 MEDIUM(inferred) | uniformity 자체 보상 금지; misleading-consistent 이름이 최악 |
| **build-type-feedback** | tsconfig `strict` 등 타입 엄격도·컴파일 에러 조기성·test 러너 존재 | **REPORT-ONLY + 저가중 cap** | task-level MEDIUM / repo-level WEAK(inferred) | pass-rate를 correctness로 credit 금지; tamper-resistance 별도 게이트 |
| **module-boundary-predictability** | 디렉터리 taxonomy 일관성·cross-module import fan-in/out | **REPORT-ONLY / 저가중** | localization 어려움 STRONG / layout 인과 WEAK | tool-graph 효과(92.7%·+32.8%)를 layout에 귀속 금지; over-fragmentation 플래그 |
| **dependency-direction-enforcement** | dependency-cruiser/eslint-boundaries/import-linter/ArchUnit/Nx/TS-refs **설정 존재 + 금지 import가 CI/pre-commit nonzero-exit로 FAIL** | **SCORED(Gate-3)** — 존재·실제 실패는 결정론적 사실 | 사실 자체 STRONG(tool) / agent 이득 QUALITATIVE(inferred, cap) | 규칙 수/모듈 수 보상 금지; behavior·readability 센서와 짝지음 |
| **standalone-verifiability** | 부분이 전체 없이 build/run/test 가능(runnability gate)·hermetic 러너·**독립 oracle 존재(에이전트 저작 테스트와 구별)** | runnability gate + 독립-oracle 가드 = **SCORED** / fine-grained modularity = **REPORT-ONLY(INFERRED)** | gate MEDIUM / false-pass 가드 STRONG / modularity WEAK | "green 격리 테스트"를 correctness로 credit 금지(81–100% false-pass) |
| **agent-guides-context** | CLAUDE.md/AGENTS.md 존재 + **non-inferable·build-checkable 내용 밀도** | **REPORT-ONLY(약)** — non-inferable 내용에만 cap된 소점수 | presence≠performance STRONG / non-inferable prose MEDIUM | bloat·staleness penalize("지우면 실수 나나?" 밀도); **자동 생성 금지** |

### 요약: 무엇이 SCORED, 무엇이 REPORT-ONLY
- **SCORED(결정론적 사실이라서):** ① dependency-direction 강제의 존재·실제 CI 실패(Gate-3), ② standalone runnability/buildability gate + 독립 ground-truth oracle 존재. 이 둘만이 "build enforces" 위계의 기계 검증 사실이자, 그중 독립-oracle 가드는 이 dossier에서 **유일하게 측정된 agent-specific 레버**(2606.26978).
- **SCORED(cap, 개입 근거 있음):** pattern-consistency의 naming 채널.
- **REPORT-ONLY:** module-boundary layout, build-type 피드백(저가중), agent-guide presence, style/idiom, fine-grained modularity — 전부 "docs explain / inferred" 층. **에이전트 이득이 측정된 개입이 아니라 추론**이므로 점수 driver로 승격 금지.

### 개선 개입의 안전장치
1. **승인 게이트:** 빌드 가드레일 추가(dependency-cruiser 설정·tsconfig strict화)·에이전트 가이드 작성은 **계획→개별→최종 3게이트 인간 승인** 뒤에만. 자동 적용 금지.
2. **behavior 센서:** 어떤 enforcement/리팩터 credit도 반드시 behavior·readability 센서와 짝지어 — "테스트 통과 ≠ 동작 보존", "체커 만족 ≠ 더 나은 설계"를 잡는다. 특히 독립 oracle(에이전트 저작 아님)로 false-pass를 검사.
3. **자동 생성 금지(agent-guide):** LLM-생성 context 파일은 5/8 설정에서 성공률을 낮췄으므로(2602.11988) 자동 생성하지 않는다. non-inferable·build-checkable 내용만, 사람이 큐레이션. bloat/staleness는 감점.
4. **tool-index ≠ code-structure:** 저장소 등급에 LocAgent/RepoGraph 효과 크기를 절대 귀속하지 않는다. score.py류 결정론 스코어러는 tool 이득을 layout 공로로 오귀속하지 않도록 프록시를 "설정 존재·실제 실패·구조 일관성"으로 한정.
5. **강제 probe 없이 등급 귀속 금지:** 개입 적용 효과는 고정 에이전트에 대한 통제 probe 없이 저장소 등급으로 귀속하지 않는다.

---

## 미해결 질문 / 추가로 필요한 근거

1. **핵심 공백 — repo-structure 개입의 부재.** 6개 지표 중 5개(pattern·module-boundary·dep-direction·standalone modularity·agent-guide 유용성 대부분)에서 **"저장소 X의 그 속성을 통제 변경 → 같은 에이전트의 resolve율/위반율 델타"**를 잰 연구가 없다. 필요한 실험: 동일 에이전트·동일 과제에서 (a) typed vs untyped, (b) enforced dep-direction vs not, (c) 일관 모듈 경계 vs 무질서, (d) hermetic 격리 vs 결합 — 각각의 성공/위반 델타. 이것이 나오기 전엔 이들은 REPORT-ONLY.
2. **new-file 배치.** localization 벤치마크는 전부 *기존* edit site 찾기다. "예측 가능 구조가 신규 코드 배치를 돕는가"는 어느 소스도 측정하지 않았다.
3. **naming 일관성의 cross-file 차원.** 2510.03178/2307.12488은 개별 식별자 난독화(behavior-preserving)를 잰다 — cross-file 패턴 uniformity 조작이 아니다. 저장소 단위 naming 일관성 → 확장 성공 링크는 여전히 mechanism-inferred.
4. **enforcement 위반율 델타.** dependency-direction 강제가 에이전트의 아키텍처 위반율을 낮춘다는 A/B가 전무. NimblePros/Phoebe/the-main-thread는 추론·단일 일화.
5. **stale/misleading doc의 정량 해악.** RepoMirage는 semantics-preserving stress test이지 false 내용 주입이 아니다. "stale 주석/문서가 얼마나 에이전트를 오도하나"의 직접 측정(misleading-comment harm의 doc 버전)이 필요.
6. **tamper-resistance의 결정론 측정.** hidden/read-only 테스트·sealed history가 reward-hacking을 collapse시킨다는 방향은 확립(ImpossibleBench)됐으나, 임의 repo에서 "oracle이 tamper-resistant한가"를 자동 감지하는 결정론 프록시는 미정의.
7. **미확인 수치의 1차 확인.** self-repair HumanEval/MBPP band, RepoNavigator IoU, CodeCompass G1/G2, SetUpAgent 회복률, SWE-bench Pro split — 루브릭에 쓰려면 primary 재확인 필요(현재는 directional만 허용).