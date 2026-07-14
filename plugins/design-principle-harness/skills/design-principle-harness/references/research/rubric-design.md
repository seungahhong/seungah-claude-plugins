# Legibility & Design Diagnostic (LDD): Two-Tier Scoring Rubric + Staged-Improvement Design

*surface-legibility + design-principle scoring/improvement 층위의 설계 문서. 스코어러는 `score.py`이며 — stdlib-only(`ast`, `tokenize`, `re`, `hashlib`, `difflib`, `collections`, `os`, `json`). grade가 아니라 0–100 **diagnostic panel**을 낸다. 이 panel은 repo scorer가 이미 돌리는 executable-verification과 dependency-integrity gate보다 의도적으로 **낮게** 가중된다 — 근거(ORACLE-SWE: reproduction test +26.4pp, execution context +14.1pp vs edit-location +12pp; slopsquatting ≥5.2%/21.7% hallucinated packages)는 runnable-test path와 resolving lockfile이 어떤 cosmetic 또는 structural 신호만큼은 중요하다고 말한다. 이 panel이 그것들을 out-vote 하게 두지 말 것.*

---

## 0. The governing distinction: two confidence axes, not one

아래 모든 신호는 **두 개의 직교하는 등급**을 갖는다. 문서의 핵심 실패 모드가 *measurement precision*을 *implied validity*로 새어 들어가게 하는 것이기 때문이다(MI와 SonarQube TD-Ratio는 정밀 계산 가능하면서도 raw-LoC baseline보다 near-random-to-worse — Ghost Echoes 2408.10754).

- **M — Measurement confidence**: `score.py`가 이를 신뢰성 있고 결정론적으로 계산할 수 있는가? (High / Med / Low / None)
- **V — Validity confidence**: 신호가 *AI-agent legibility 또는 safe contribution*을 예측하는가? **모든 structural (Tier B) 하위 점수에 대해 이는 `EXTRAPOLATED`다** — 이를 올리는 것이 특정 agent의 성공을 개선하는지 측정한 연구는 찾을 수 없었다(`structural-metrics-validity`, `solid-coupling-di`, `rubric-and-judge-methodology`, `goodhart-reward-hacking`, `safe-staged-refactoring` 전반에서 만장일치). Tier A의 경우, *misleading/stale* 하위 신호만 `V-Med`에 도달하고; descriptive-naming은 `V-Weak`다(human ~14–19% faster이지만 LLM 효과는 sign-unstable: 2504.10557에서 −18.6pp, 2606.31725에서 ≈−1.8pp/때때로-도움, 2505.10443에서 모델별 +14.4/−31.9pp — **어떤 단일 "naming이 LLM comprehension을 X% 바꾼다" 숫자도 합성해서는 안 된다**).

Extrapolated V를 가진 high M은 **구성상 report-only다**. 이 규칙이 한 렌즈가 만든 STRONG coupling 등급을 금지한다(아래 재채점).

---

## 1. The two-tier rubric

### TIER A — Surface legibility (higher-confidence, ACT-FIRST)

여기서 act-first인 이유는 agent에 대한 comprehension 이점이 입증돼서가 **아니다** — 이 신호들이 **gaming surface가 가장 낮고 고치는 데 behavioral risk가 가장 낮으며**, model judgment를 *움직인다*는 직접적 LLM-subject 근거를 가진 유일한 axis이기 때문이다(2507.05289). 그것이 이 순서의 정직한 정당화다.

| ID | Signal | Deterministic stdlib approximation | Points | M | V | Disposition |
|----|--------|-------------------------------------|--------|---|---|-------------|
| **A1** | **Misleading / stale / inconsistent comments & docstrings** (the one cross-cutting harm: Wen 2019 ~1.5× human bug-rate, iComment Tan 2007, LLM mis-steering 2512.16790) | Deterministic subset only: (a) docstring `:param`/`Args:` names vs actual `ast.FunctionDef.args` → mismatch = stale; (b) docstring "Returns…" on a function with no `Return` node; (c) **commented-out code**: strip `#`, attempt `ast.parse` on the body — if it parses as a statement, it's dead-code-comment; (d) comment naming an identifier absent from the enclosing scope's symbol table. Everything softer (semantic wrongness) is **flag-for-human**, never auto-scored. | **0 to −25** | Med | **Med** (only convergent human+LLM harm) | **ACT — delete/repair only** |
| **A2** | **SATD markers** (TODO / FIXME / HACK / XXX / BUG / WORKAROUND) — self-admitted debt (Maldonado 2015: 2,457/33,093) | `tokenize.COMMENT` tokens matched against a fixed marker regex; density = markers / KLOC | **0 to −6** | High | Weak | **FLAG** (warn agent; don't auto-remove — the debt is real) |
| **A3** | **Identifier descriptiveness + convention conformance** | `ast` walk collects `Name`/`arg`/`FunctionDef`/`ClassDef`. Compute: single-char ratio **excluding** conventional loop/lambda idioms (`i,j,k,_,e` in comprehensions — caveat: this exclusion is itself a heuristic); camel/snake split then check tokens against a **bundled small word list** (ship the file; stdlib has none); PEP8 conformance (`snake_case` funcs, `PascalCase` classes) via regex. **"Misleading" names are NOT deterministically detectable** — only descriptiveness + convention proxies are. | **0 to −20** | Med–High | Weak | **ACT only on clearly non-descriptive/non-conforming, via AST/LSP** |
| **A4** | Comment / docstring **presence & density** | `tokenize` comment-line ratio; docstring coverage via `ast.get_docstring` | **0 (report-only)** | High | Weak | **REPORT-ONLY — never reward volume, never auto-generate** (auto-comments are frequently wrong and wrong comments actively harm LLMs — 2512.16790; docstrings compress 25–40% at no loss — 2410.22793) |
| **A5** | Visual formatting / indentation / whitespace | Computable, but **do not** | **0 (excluded)** | High | **None (LLM-invisible)** | **HUMAN-ONLY REPORT** — 2508.13666: layout removal saves 24.5% tokens at no accuracy loss; scoring it would conflate "pretty" with "AI-readable" |

**Tier A hard cap: −45.** Point가 아니라 band로 보고.

### TIER B — Design principles (lower-confidence DIAGNOSTIC, DEFER)

이 tier 전체는 **size-normalized, report-heavy advisory panel**이며 **hard −20 cap**을 두어 structural metric에 대한 높은 measurement precision이 band를 지배하지 못하게 한다. AI-agent legibility에 대한 validity는 일률적으로 `EXTRAPOLATED`이며; length-controlled 하면 고전 structural metric은 LLM task success와의 모든 안정적 association을 잃고(Xie 2602.07882: *"None … after controlling for code length"*), 에이전트를 바로 이 oracle에 겨누는 것은 경험적으로 net-negative다(SmellBench 2605.07001: best resolves 47.7%, aggressive introduces 140 new, oracle 63.1% false-positive).

| ID | Signal | Deterministic stdlib approximation | Points | M | V | Disposition |
|----|--------|-------------------------------------|--------|---|---|-------------|
| **B1** | **Duplication — Type-1 / Type-2** (the kind AI inflates: 1.87× AMR 2601.21276; ≤7.50% generators) | `tokenize` each file → normalize (T1: strip comments/whitespace; T2: additionally replace `NAME`/`NUMBER`/`STRING` with placeholders) → k-token sliding windows (k≈50) → `hashlib` window hashes → cross-file matches → clone coverage % | **0 to −6** | High | Extrap | small-weight number |
| **B1′** | **Inconsistent clones** (the real hazard — Mondal/Islam: a fix landed in one copy not its sibling) | For candidate clone pairs, `difflib.SequenceMatcher.ratio` in **[0.90, 1.0)** → "divergent — possible missed fix" | **0 (flag)** | Med | Weak | **FLAG → ACT-FIRST-SAFE** (bug repair, not de-dup) |
| **B2** | Duplication — Type-3 (gapped) | Same windows with a Levenshtein/`SequenceMatcher` threshold; noisy | **0 (report-only)** | Med | Extrap | REPORT-ONLY count + tuning caveat |
| **B3** | Duplication — Type-4 / "DRY violation" | — | **0** | **None** (93% of semantic-clone ground truth mislabeled — 2505.04311) | n/a | **NEVER A NUMBER** — narrate "verify manually" |
| **B4** | **Complexity** — prefer **nesting depth, param count, # locals** over McCabe (Peitek fMRI: McCabe null on cognitive load; nesting/params/data-flow have the measured footprint) | `ast` walk: CC = 1 + branch nodes (`If/For/While/BoolOp/except/assert/IfExp/comprehension-if`); nesting = max control-node depth; params = `len(node.args.args)`; **always paired with SLOC** and reported per-function as top-N hotspots | **0 to −6** | High | Extrap | REPORT-LEANING, size-normalized |
| **B5** | **Coupling** — fan-in / fan-out / cross-file imports / cycles | `ast.Import`/`ImportFrom` → module dependency graph; efferent = distinct imports; afferent = importers; cycles via DFS | **0 to −4** | High | Extrap **as legibility** | **REPORT-ONLY, framed as CHANGE-RISK / blast-radius, NOT readability** (see §1 regrade) |
| **B6** | Cohesion — LCOM | Per class: method→`self.attr` access sets; LCOM4 = connected components of the method-sharing graph. **Name the variant** (variants disagree, up to strong-negative) | **0 (report-only)** | Low | Extrap | REPORT-ONLY |
| **B7** | SOLID adherence (SRP/OCP/LSP/ISP/DIP) | No construct-valid metric exists; TensorFlow/scikit-learn violate SOLID *deliberately*. Approximate SRP via class fan-out/size, DIP via injected-vs-`new` ratio — **as narration only** | **0** | **None** | Extrap | **NEVER "SOLID = N/100"** — heuristic narration via already-scored proxies |
| **B8** | **DI/IoC presence + over-abstraction NEGATIVE** | Injected-vs-direct-instantiation ratio (soft/hard coupling, DCBO-style); **single-implementation ABC/Protocol** and **pass-through/wrapper classes** (methods only delegate to one wrapped object) → detect as needless indirection | **0 to −4** | Med | Extrap | **REPORT ratio as context; PENALIZE single-impl interfaces & pass-throughs as NEGATIVE** — DI presence is *not* a positive; it can be "architectural mimicry" (Modular Imperative) — the exact AI output we are trying to catch |
| **B9** | KISS / YAGNI / dead code | Build repo-wide reference set (`Name`/`Attribute` nodes); defs never referenced & not in `__all__`/not dunder → dead-code candidate; unused imports; unused exports | **0 to −4** | High (dead code) | Extrap | **FLAG**; dead-code + unused-import removal is **ACT-FIRST-SAFE**; single-impl interface = intentional-seam caveat (Fowler) |

**Tier B hard cap: −20, labeled "advisory — does not move the safe-contribution claim."**

> **§1 regrade (반드시 실릴 것 — 문서의 내부 모순 해소).** 한 렌즈가 **coupling STRONG**과 **complexity STRONG**을 채점했고; 세 자매 렌즈가 이들을 weak/report-only로 채점했으며, 그 렌즈 자신의 *Could-NOT-source*가 "coupling/DI가 LLM/agent 기여 성공에 미치는 영향에 대한 통제 연구 없음"을 인정한다. 위에 실린 조정: **coupling은 강한 *change-risk/blast-radius* 진단자이자 약한 *legibility* 신호이며; 그 fix는 플러그인에서 가장 위험한 단일 행동이다.** Complexity는 **human reading-*time* meta-analysis**로 채점된다(time에 r=0.54이지만, correctness에 r=−0.13 — 그리고 "safely contribute"가 필요로 하는 것은 correctness다). 둘 다 agentic axis에 대해 STRONG이 아니다. *diagnosis*를 채점하되, *fix*는 결코 채점하지 말 것.

---

## 2. The composite as a PRIORITIZATION diagnostic (anti-Goodhart framing)

`LDD = 100 − min(Σ Tier-A deductions, 45) − min(Σ Tier-B deductions, 20)`, **sensitivity annotation과 함께 band로 보고**하며 결코 bare number로 보고하지 않는다. 그것은 하나의 질문에 답한다: *"human이 먼저 어디를 봐야 하는가?"* 그것은 agent가 안전하게 기여할 수 있다는 certification이 **아니며**, optimization target이 **아니다**.

human이 보는 숫자는 agent가 올리라고 지시받는 무엇과도 구조적으로 분리되어야 한다(Goodhart/Strathern 1997; Campbell 1976 — *"when a measure becomes a target it ceases to be a good measure"*). 구체적으로, 각각 source에 traceable한 일곱 메커니즘:

1. **Never close the loop.** 개선 에이전트는 "LDD가 올랐는지"가 아니라 **human approval + held-out behavioral verification**으로 채점된다. Composite는 human-facing prioritization map일 뿐. (Goodhart/Campbell.)
2. **Harden the oracle.** `score.py`는 **개선 에이전트에 read-only**; re-scoring은 별도의 un-writable pass로 실행된다. Environment hardening은 가장 leverage 높은 경험적 방어다(RHB 2605.02964: −87.7% relative exploits, no task-success loss). 에이전트가 rubric을 *볼* 수 있다고(benchmark leakage) 가정하고, 봐도 게임에 도움이 안 되도록 설계한다 — 그래서 visible-metric maximization이 아니라 behavior sensor와 held-out probe.
3. **Net-delta, not gross-resolved.** smells removed **minus** smells introduced를 보고(SmellBench의 요지). "5 고치고 8 추가"하는 섹션은 **regression**으로 읽히고 gate에서 거부된다.
4. **Refuse to reward volume.** LOC ↔ architectural-smell ρ=0.94 (2605.02741) — 추가된 file/LOC/structure는 **결코** LDD를 올려서는 안 된다. 부채 모델이 deduction-from-baseline인 것은 바로 "cohesion score를 올리려고 abstraction을 추가"하는 것이 불가능하게 하기 위함이다.
5. **Findings are candidates until human-triaged.** 비교 가능한 oracle은 **63% false-positive**다(SmellBench). 모든 finding을 *candidate*로 제시; human의 accept/reject를 기록(human κ-agreement는 높음)하고, 결코 auto-act 하지 말 것.
6. **Decompose into binary/thresholded checks, never a holistic LLM gestalt.** CheckEval (2403.18771): binary decomposition은 Likert 대비 +0.45 inter-rater agreement와 ~5× lower variance를 산다. **LLM을 legibility oracle로 결코 쓰지 말 것** — CoReEval (2510.16579): LLM-vs-human readability r=0.25 (Java) / 0.02 (Python) / 0.00 (CUDA), *2018 static model에 진다*, "readable"을 65% vs 43.7%로 부풀린다. 이것이 deterministic `score.py` + human gate의 직접적 정당화다.
7. **Bands + sensitivity analysis.** Weight는 설계 선택이며; sensitivity analysis 없는 index는 "can tell any story"(OECD/Saltelli). ±weight perturbation을 실어 band가 견디는지 보고; false-precision point가 아니라 range를 보고(human readability ground truth 자체가 20–30% self-inconsistent).

**Composite와 함께 다니는 verbatim caveat:**
> "This is a **diagnostic, not a certification.** These sub-scores are size-normalized proxies validated on **human** maintainability/defect data; their transfer to **AI-agent legibility or safe contribution is an extrapolation, not a measurement** — no located study shows that raising this score improves an agent's comprehension or edit-safety on *this* repo. Every proxy degrades when optimized (Goodhart). Improvements are credited only after human approval + held-out behavioral verification, never because this number rose."

**The central risk, stated plainly:** AI는 duplication(1.87×)과 smells(ρ=0.94)를 부풀리고 *동시에* 에이전트는 이를 수리하는 데 net-negative다(SmellBench). 따라서 개선 에이전트를 design score에 겨누는 것은 design을 *더 나쁘게* 만드는 경향이 있다. 위의 일곱 메커니즘은 장식이 아니라 load-bearing이다.

---

## 3. Easiest-first improvement sequence (with per-section safety mechanism)

이 순서는 단지 편의적인 것이 아니라 **근거 기반**이다: confidence가 가장 높고 behavioral risk가 가장 낮은 곳에서 먼저 act하고, measurement가 가장 약하고 restructuring이 가장 위험한 곳에서 정확히 defer한다(compound LLM refactor 성공 <40% — 2602.03712; reward-hacking은 chain-length ≥5에서 급증 — RHB). 각 섹션은 **three-gate human approval**을 통과한다: plan gate → per-change gate → final gate.

| Order | Section | What is applied | Safety mechanism | Evidence anchor |
|-------|---------|-----------------|------------------|-----------------|
| **P0** | **Dependency-manifest integrity** (safe-contribution, not legibility) | Confirm every imported/added package resolves in lockfile/registry; flag hallucinated deps | Deterministic check; **no code rewrite** | Slopsquatting ≥5.2%/21.7%, 43% recur-all-runs (2406.10279). The one STRONG, act-first, deterministic safe-contribution signal — sits **above** the whole design axis |
| **P1** | **Delete/repair misleading & stale comments; fix inconsistent clones; remove dead code + unused imports** | Delete stale docstrings/param-mismatches, commented-out code (A1); repair divergent clones (B1′); delete unreferenced defs/imports (B9) | **DELETE-ONLY / behavior-neutral.** A confirmed-wrong comment's deletion cannot change behavior. Inconsistent-clone repair is a *bug fix*, human-confirmed per instance. Dead-code removal gated on the repo-wide reference set (guard against dynamic/`getattr`/reflection reachability → those are FLAG-not-delete) | Wen 2019, Tan 2007, 2512.16790; Mondal/Islam; near-zero risk |
| **P2** | **Renames** — local variables + Extract Variable first, then methods/params | Apply clearly non-descriptive/non-conforming renames (A3) | **AST/LSP scope-aware rename ONLY — never regex.** Renames the *binding*, not the string. Caveat travels: "still risks reflection / serialization keys / DI-by-name / public-API references the language server cannot see — **public identifiers are opt-in.**" | Local rename/Extract-Variable near-100% safe for LLMs; broader renames 6–8% behavior-change baseline, 80%+ silent (2411.04444, 2510.03914) |
| **P3** | **DEFER → explicit opt-in only:** Extract Method, Move, Inline, all SOLID / coupling / cohesion / DI restructuring, de-duplication via extraction | Nothing auto-applied. Each is **one-at-a-time, human-designed, never bundled** | **External behavior sensor + human gate, mandatory:** (a) run existing suite over the *impacted slice*; (b) when coverage is thin, **generate & run characterization tests on the touched region**; (c) optionally confirm *only the intended* refactoring occurred (RefactoringMiner-style); (d) **if the touched region has no executable coverage → mark `UNVERIFIED`, escalate — do NOT claim "safe."** The producing agent's self-review is **not** a safety net (endorses ~1/3 of its own silent drifts — 2605.21537). Mandatory net-delta re-score; "fixes 5, adds 8" is rejected. | Compound LLM refactor <40% (2602.03712); Extract/Inline/Move top the engine-bug charts (2409.14610); wrong-abstraction cost > duplication (Metz); de-dup only past Rule-of-Three |

**모든 tier의 모든 적용 변경에 다니는 traveling caveat (non-negotiable):**
> "**Tests passing ≠ behavior preserved** — only ~22% of refactored code is covered in practice (Rachatasumrit & Kim). Every green result ships with the *coverage over the touched slice*; low coverage **downgrades trust**, it does not certify safety. The agent's own confidence is not evidence."

---

## 4. What the comprehensive final report must contain

리포트는 honesty firewall다. 가장 어려운 임무는 **re-score delta**다: 실제로 이루어진 cosmetic edit에 대한 주장으로 무관한 agentic/tool-graph 숫자를 세탁하지 않으면서 개선을 보고하는 것.

**Required sections:**

1. **Construct statement (Messick).** LDD가 측정하는 것("size-normalized surface + structural *proxies* for AI-legibility")과 측정하지 **않는** 것("code quality writ large; agent contribution success; certification of safety")을 명시. One paragraph, up top.

2. **Two-axis confidence per finding.** 모든 라인은 M과 V, 그 disposition(ACT/FLAG/REPORT-ONLY/NEVER-NUMBER), 그리고 traveling caveat를 지닌다. Tier B 라인은 `V-EXTRAPOLATED — advisory`로 눈에 띄게 스탬프된다.

3. **Net-delta accounting, not gross.** 섹션별·전체: smells **removed − introduced**. Net-negative 섹션은 여러 finding을 "resolve" 했더라도 regression으로 보고된다.

4. **Re-score delta honesty — the load-bearing section.** 규칙:
   - **deterministic `score.py` delta만** 보고하며, *"rubric-score change, verified by re-running the scorer — this is a **score delta, not an agent-capability delta**."*로 라벨.
   - **tool-graph 또는 agentic 이득을 cosmetic edit에 귀속하지 말 것.** LocAgent 92.7% file-localization, RepoGraph +32.8%, ORACLE-SWE edit-location +12pp 같은 숫자는 **cross-repo / perturbation / tool-built-at-query-time** 결과다 — *어느 것도 same-repo before/after intervention이 아니다*. 리포트는 "우리가 식별자를 rename했으니 당신의 agent-navigation이 N점 개선됐다" 형태의 어떤 문장도 **금지**해야 한다. 명시: *"No located study shows that raising this score raises a specific agent's contribution success on this repo; that causal link is a reasoned heuristic, not a measured predictor."*
   - naming effect size는 **un-aggregated**로 유지 — divergence를 인용(−18.6pp vs ≈−1.8pp vs 모델별 ±14–32pp), 결코 합성된 "naming +X%"가 아니라.
   - 오직 **opt-in agentic probe**가 실행된 경우에 한해, 그것을 **held-out behavior**(에이전트가 테스트를 저작하지 않음)를 가진 same-repo before/after로 **별도로** 보고하고, 그 자체의 caveat와 함께 — 결코 LDD delta에 접어 넣지 말 것.

5. **Behavioral-verification evidence per applied change.** touched slice별 coverage; 모든 `UNVERIFIED` 표시를 눈에 띄게 표면화(thin coverage는 trust를 downgrade할 뿐 결코 certify하지 않음).

6. **Deferred queue.** opt-in되지 *않은* 모든 P3 항목을, change-risk 근거와 함께 — 그래서 deferral이 누락이 아니라 문서화된 결정이 되도록.

7. **Human triage record.** human이 **reject**한 findings(63% false-positive base rate를 고려하면, reject list 자체가 deliverable이자 calibration signal).

8. **Sensitivity analysis.** ±weight perturbation 결과와 보고된 band가 그것을 견디는지 여부(OECD/Saltelli).

9. **Global provenance caveat + the 2026-preprint caveat.** 한 번, 눈에 띄게 명시: headline LLM-subject effect size는 **unreplicated, single-team 2026 preprint**(SmellBench, SpecBench, RHB, Xie, RepoMirage 등)에서 도출됨 — 크기를 잠정치로 취급; 그리고 *"nearly all LLM evidence here is perturbation or production, not same-repo before/after intervention."*

**The report must never say:** "certified AI-ready," "SOLID score N/100," "we improved agent comprehension by X," "duplication removed → DRY-compliant," 또는 어떤 localization/navigation 이득을 rename이나 comment edit에 귀속. same-repo, held-out behavioral before/after를 보일 수 없으면, **score delta 그 이상은 아무것도** 보고하지 않는다.
