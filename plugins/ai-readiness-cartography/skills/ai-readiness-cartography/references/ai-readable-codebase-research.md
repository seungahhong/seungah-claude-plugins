# AI-Readable Codebase — 연구 dossier (cited)

> 이 문서는 `ai-readable-codebase` 하네스 설계의 근거가 된 1차/2차 자료 조사 결과다(deep-research: 6각도 팬아웃 →
> 23개 소스 fetch → 109개 주장 추출 → 상위 25개 3-vote 적대적 교차검증 → confirmed 13 / killed 12, 2026-06-25 기준).
> [ai-readable-codebase-principles.md](./ai-readable-codebase-principles.md)의 원칙과 상호 참조된다.
> 빠르게 변하는 분야이므로 각 출처에 신뢰도(vote)와 CAVEAT를 함께 표기한다. 정량 수치는 vote/CAVEAT와 함께만 인용하고,
> "개선 N% 보장"식 진술은 쓰지 않는다.

---

## A. 1차 출처 — flex.team "AI가 읽을 수 있는 코드베이스" 5부작 (설계의 토대)

- **출처·연도**: flex.team 기술 블로그, 2026-05~06 (한국어 산업 글)
- **신뢰도**: 산업 실무 글(1차 경험 보고). 이 모드의 *프레임워크 정의*(2축·접근성 등급·빌드 가드레일·standalone·수용 증명)는 여기서 끌어왔다(원 출처는 5단계 L1~L5를 썼으나 현 하네스는 단일 5밴드+Gate-3로 통합). 정량 효과 주장에는 쓰지 않고 *설계 원리*로 인용한다.
- **글 목록·URL**:
  1. [1/5] 프롬프트보다 구조가 먼저다 — https://flex.team/blog/2026/05/20/backend15
  2. [2/5] 빌드 피드백이 AI를 가르친다 — https://flex.team/blog/2026/05/22/backend16
  3. [3/5] Standalone App: 도메인 슬라이스 독립 실행 — https://flex.team/blog/2026/05/27/backend17
  4. [4/5] Acceptance 증명이 리뷰를 바꾼다 — https://flex.team/blog/2026/05/29/backend18
  5. [5/5] AI 접근성 등급으로 보는 코드베이스 — https://flex.team/blog/2026/06/04/backend19
- **하네스 반영**: 전체 5단계 플로우(진단→가드레일→standalone→적용(계획·개별 승인)→수용·재측정)와 2축/등급 밴드(5밴드+Gate-3)/피드백 3차원/어댑터 치환/수용 증명 한계의 정의적 근거.
- **CAVEAT**: 단일 팀의 실무 경험 글이며 구현 예시가 특정 스택(Kotlin/Gradle/Spring/Hexagonal)에 묶여 있다. 이 하네스는 *원리만 스택 무관*으로 일반화하고, 글에 등장하는 외부 정량 수치(특히 CodeScene 관련, §D 참조)는 그대로 인용하지 않는다.

---

## B. 확증된 학술 출처 (3-vote 적대 검증 통과)

### 출처 1 — Robustness under semantics-preserving mutations (GOLD, 3-0)
- **URL**: https://arxiv.org/html/2505.10443v3 (2025)
- **핵심**: SOTA LLM은 *의미 보존* 구문 변형만으로도 코드 이해(출력 예측)가 최대 70% 흔들린다. 가장 깊은 구조적 추론을 요구하는 변형(loop unrolling)에서 가장 크게 무너진다(Qwen2.5-Coder −44.3pt).
- **인용**: "LLMs often change predictions in response to our code mutations, with performance drops reaching up to 70% ... even when initial accuracy is high." / "Loop unrolling, which requires deeper structural reasoning, produces the most severe instability across models."
- **하네스 반영**: A축의 "패턴 일관성/구조"가 AI 이해 안정성에 실제로 영향을 준다는 근거(principles §1·§2).

### 출처 2 — 27 transformations × 25 LLMs robustness benchmark (GOLD, 3-0)
- **URL**: https://dl.acm.org/doi/10.1007/s10664-026-10856-w (Empirical Software Engineering, Vol 31 Issue 4)
- **핵심**: 27개 의미 보존 변형 × 25개 LLM × 4개 언어의 대규모 robustness 벤치마크. instruction-tuned 모델이 base 모델보다 *동치 코드 변형에 더 강건*하다.
- **인용**: "today's LLMs still suffer from robustness issues in code generation ... with base models being less robust compared to instruction-tuned models."
- **하네스 반영**: "구조·일관성이 AI 코드 신뢰성에 영향을 준다"의 peer-reviewed 보강. *주의*: 같은 논문에서 "제어구조 변형에 가장 민감"(0-3 반박), "코드 표준화로 robustness 개선"(1-2 반박)은 §D로 분리.

### 출처 3 — Execution trace length dominates (GOLD, 3-0)
- **URL**: https://arxiv.org/html/2602.13962 (2026)
- **핵심**: 동적 실행 특성(특히 *실행 트레이스 길이*)이 정적 속성보다 LLM 코드 추론에 더 큰 영향을 준다. 20스텝 내 성능 30%+ 급락 후 계속 하락.
- **인용**: "Execution trace length emerges as the dominant factor. Performance drops sharply for 30+% within 20 steps ..."
- **하네스 반영**: 짧고 격리된 실행 경로(작은 standalone 슬라이스)가 에이전트 추론에 유리(principles §5). *주의*: "순환복잡도는 영향 미미"(1-2)는 §D.

### 출처 4 — Iterative refactoring "restructure-then-stabilize" & style normalization (GOLD, 3-0 ×2)
- **URL**: https://arxiv.org/html/2602.21833v1 (2026)
- **핵심**: LLM 반복 리팩터링은 첫 회차에 가장 크게 바뀌고 이후 1% 미만으로 수렴(인접 버전 유사도 0.86→0.90, 미변경 라인 76%→92%). 또한 *구조적으로 다양한 코드(식별자 손상·주석 제거 포함)를 일관 스타일로 신뢰성 있게 정규화*한다(변형 무관 ≈73 LOC·≈6 메서드로 수렴).
- **인용**: "LLMs can reliably normalize diverse code snippets toward consistent coding style."
- **하네스 반영**: "패턴 일관성은 학습·정규화 가능하다"의 근거 — 일관 구조가 에이전트에 더 다루기 쉽다(principles §2).

### 출처 5 — Self-repair gains concentrate early (GOLD, 3-0)
- **URL**: https://arxiv.org/abs/2604.10508 (2026)
- **핵심**: 실행 피드백 self-repair의 정확도 이득은 *첫 2라운드*에 집중된다(이후 수확 체감).
- **인용**: "Most gains concentrate in the first two rounds."
- **하네스 반영**: 빌드 피드백 루프는 유효하나 *무한 반복은 금물*(principles §4·§7 anti-pattern 9). *주의*: 같은 소스의 "모든 모델에서 보편적으로 +Xpt 개선"(0-3)은 §D.

### 출처 6 — Self-repair is not a silver bullet; feedback quality is the bottleneck (GOLD/SILVER)
- **URL**: https://arxiv.org/pdf/2306.09896 (Olausson et al., ICLR 2024)
- **핵심**: ① 비용을 따지면 self-repair 이득은 작거나 없을 수 있다(2-1). ② 병목은 생성이 아니라 *피드백의 질*(모델이 자기 버그를 정확히 진단하는 능력)이다 — 더 강한 모델로 피드백 질을 올리면 이득이 크게 는다(3-0).
- **인용**: "when the cost of carrying out repair is taken into account, performance gains are often modest ... sometimes not present at all." / "using a stronger model to artificially boost the quality of the feedback ... yielded substantially larger performance gains."
- **하네스 반영**: flex의 **"피드백 3차원(위치·원인·수정방향)"**과 정확히 일치 — *피드백의 질*이 핵심이라는 직접 근거(principles §4). 동시에 self-repair 과신을 경계.
- **CAVEAT**: 2024 출간(2023 제출)으로 "2025+" 우선 기준보다 앞서나, *피드백 질 = 병목* 명제는 후속 연구와 일관돼 핵심 근거로 채택.

### 출처 7 — Compiler-in-the-loop refinement; local compile errors are the strongest signal (GOLD/SILVER)
- **URL**: https://arxiv.org/pdf/2602.11481 (2026)
- **핵심**: 구조화된 오류 안내(컴파일러-인-더-루프) 루프가 GPT-5의 Idris 해결을 22/56→54/56(96%)로 끌어올렸다(3-0). *로컬 컴파일 에러* 피드백이 가장 큰 개선을 냈고(2-0), 컴파일 진단+실패 테스트를 다음 프롬프트에 직접 주입하는 루프를 최대 20회 사용(2-0).
- **인용**: "Using this structured, error-guided refinement loop, GPT-5's performance increased to ... 54 solved problems out of 56." / "incorporating local compilation errors yields the most substantial improvements."
- **하네스 반영**: flex의 **"가장 중요한 아키텍처 규칙을 가장 빠른 계층(컴파일)에서"**·"빌드 피드백이 AI를 가르친다"의 직접 학술 근거(principles §4).

---

## C. 산업·아키텍처 맥락 (BRONZE — 보강용, 정량은 CAVEAT)

- **"Architecture Without Architects: How AI Coding Agents Shape Software Architecture"** — https://arxiv.org/html/2604.04990v1 (2026). 에이전트가 5개 메커니즘으로 암묵적 아키텍처 결정을 내린다 → *구조를 명시·강제하지 않으면 에이전트가 임의로 정한다*는 보강(angle 3).
- **"The codebase is the prompt — Wolverine, vertical slices, and AI-assisted development"** — https://jeremydmiller.com/2026/06/04/... (블로그, 2026-06). "코드베이스가 곧 프롬프트"·vertical slice = 독립 슬라이스 — flex의 "구조가 먼저다"·standalone과 동형. *블로그(2차)*이므로 방향성 보강으로만.
- **"AI Coding Agents Are Hitting a Wall and the Wall Is Your Architecture"** — https://medium.com/@nitinsgavane/... (블로그). "구조 먼저"의 대중적 corroboration.
- **Faros AI Engineering Report 2026: The Acceleration Whiplash** — https://pages.faros.ai/.../AI_Engineering_Report_2026...pdf (산업 telemetry, 22,000 devs/4,000+ teams). AI 코드 acceptance rate 상승·"리뷰 없이 머지되는 PR" 증가 경향 → *자동 수용 증명 + 설계 중심 리뷰*의 필요성 보강(angle 4). 산업 리포트이므로 정량 수치는 CAVEAT와 함께만.
- **DORA 2025 / DORA-ROI 보도** — https://www.faros.ai/blog/key-takeaways-from-the-dora-report-2025 · https://www.infoq.com/news/2026/05/dora-roi-ai-assisted-dev-report/ (2차). AI 도입과 전달 안정성 맥락(배경).

---

## D. 반박·미검증 주장 (투명성 — 본문 근거로 사용 금지)

이 하네스는 3-vote 적대 검증에서 **반박(refuted)되거나 미검증(abstain/출처 부재)된 주장**을 본문·원칙·에이전트 지침의 근거로 쓰지 않는다. 투명성을 위해 여기에만 기록한다.

### D-1. ★ CodeScene "Code Health 9.4/10 / 업계 평균 5.15/10" 수치 — **미입증 (본문 사용 금지)**
- flex 5/5는 "CodeScene 연구가 안전한 AI 운용에 Code Health 9.4/10 이상을 요구하고 업계 평균은 5.15/10"이라는 취지의 수치를 인용한다.
- **적대 검증 결과**: 그 배경의 peer-reviewed 1차 논문 **"Code for Machines, Not Just Humans: Quantifying AI-Friendliness with Code Health Metrics"**(Borg, Hagatulah, Söderberg, Tornhill — FORGE 2026, https://arxiv.org/abs/2601.02200)에는 **그 headline 수치(9.4/5.15)가 없다.** 논문의 실제 발견은 *"건강하지 않은 코드에 AI를 적용하면 건강한 코드 대비 AI 유발 결함 위험이 최소 60% 높다"*이며, **연구는 Code Health ≥ 7.0 코드만 포함**했으므로 7.0 미만 수치는 *측정이 아니라 외삽(projection)*이다.
- 관련 마케팅/PR(예: https://www.prnewswire.com/.../ai-coding-assistants-increase-defect-risk-by-30-in-unhealthy-code... 의 "30%"; CodeScene 화이트페이퍼 "AI-Ready Code")은 1차 논문과 수치가 엇갈린다(30% vs 60%).
- **결론**: 9.4/10·5.15/10을 *사실로 인용하지 않는다*. 인용 가능한 안전한 명제는 **"코드 건강도/AI-친화성은 중요하며, 건강하지 않은 코드는 AI 유발 결함 위험이 더 높다(arXiv:2601.02200) — 단 구체 임계치(9.4)·업계 평균(5.15)은 peer-reviewed 출처에 없고, 7.0 미만은 외삽이다"**까지다.

### D-2. "에이전트는 9개 예시에서 패턴을 내재화하고 10번째에서 따른다" — **미검증 휴리스틱**
- flex 5/5의 "9개 일관 예시 → 10번째 자동 추종"은 *예시 기반 직관*이며 특정 수치(9/10)를 검증한 연구를 찾지 못했다.
- 인접 근거(arXiv:2602.21833 — LLM이 일관 스타일로 정규화; arXiv:2505.10443 — 일관성이 이해 안정성에 영향)는 **"패턴 일관성은 학습 가능하다"**는 *정성적 방향*만 지지한다.
- **결론**: "패턴 일관성이 에이전트 행동을 유도한다"는 정성 명제로만 쓰고, "9개→10번째" 같은 *구체 임계치*는 주장하지 않는다.

### D-3. "자연어 가이드(CLAUDE.md)는 구조 강제 없이는 실패한다" — **설계 명제(직접 측정 아님)**
- 이를 직접 측정한 연구는 확인되지 않았다. 단, *컴파일러 피드백이 가장 강한 신호*(arXiv:2602.11481)이고 *self-repair 병목은 피드백의 질*(arXiv:2306.09896)이라는 확증 근거가 "구조·빌드 강제 > 산문 지시"라는 방향을 **간접 지지**한다.
- **결론**: "빌드가 강제하고 문서가 설명한다"는 *설계 원칙*으로 채택하되, "자연어 가이드는 반드시 실패한다"는 식의 절대 명제로 과장하지 않는다.

### D-4. 기타 반박된 주장 (vote)
- "LLM이 *제어구조* 변형에 가장 민감"(0-3) · "코드 표준화로 robustness 개선"(1-2) — 출처 2 관련.
- "네이밍이 LLM식으로 수렴: snake_case 40.7%→49.8%"(0-3, arXiv:2506.12014).
- "프롬프트 컨텍스트 구성요소(repo info·DFG·식별자)가 코드 이해를 좌우"(0-3) · "GenAI 코드 설명은 자주 부정확(50% 오류 포함)"(0-3) — arXiv:2510.17894.
- "순환복잡도는 LLM 추론에 영향 미미"(1-2, arXiv:2602.13962).
- "self-repair가 모든 모델에서 보편적으로 +4.9~17.1pt 개선"(0-3, arXiv:2604.10508).
- LLMLOOP(+14pt)·다도구 self-repair(보안결함 −96%)·GCC+KLEE+CodeQL(−54.37pt) 류 — 모두 **0-0 (3 abstain, 세션 한도로 검증 미완)**. 검증 미완이므로 본문 근거로 쓰지 않는다.

---

## E. 방법론 — deep-research 6각도 3-vote 적대 검증

- **팬아웃(6각도)**: ① 코드 이해/일관성 ② 컴파일러/실행 피드백 ③ 에이전트 아키텍처 패턴 ④ AI 코드 수용/리뷰 ⑤ Code Health/기술부채(적대) ⑥ flex 주장 반증.
- **규모**: 23개 소스 fetch → 109개 주장 추출 → 상위 25개 검증 → **confirmed 13 / killed 12**.
- **검증**: 각 주장을 인용 단위로 추출하고 **3-vote 적대적 교차검증**으로 confirmed/refuted를 분류(독립성 보존을 위해 각 논문은 primary로 직접 인용).
- **한계(정직성)**: 워크플로의 *합성(synthesize) 단계*와 일부 self-repair 주장 검증은 세션 토큰 한도(2026-06-25 09:40 KST 리셋)로 미완됐다. 미완 검증 주장(0-0 abstain)은 §D-4로 분리하고 본문 근거에서 배제했다. 정량 수치는 vote/CAVEAT와 함께만 인용하고 "개선 N% 보장"은 쓰지 않는다.
