# AEO 근거 정본 (evidence)

이 하네스의 모든 판단·문안·금지 규칙은 이 파일을 근거로 한다. 여기 없는 수치는 하네스 산출물에 쓰지 않는다.

**검증 방법** — 출발점 글(Addy Osmani, "Agentic Engine Optimization")의 주장을 그대로 옮기지 않고, 인용된 1차 출처를 전부 직접 페치해 대조했다. arXiv 문헌은 abs 페이지 + 본문(HTML/PDF 추출)에서 인용 문장을 원문 검색해 확인했고, 벤더 문서는 4사 전수 확인 후에만 "유일하게 ~한다"류 서술을 남겼다. 실재하지 않는 문헌을 만들지 않는지 통제하기 위해 날조 ID(`2605.99999`)를 함께 조회해 404를 확인했다.

## 등급 체계

등급은 **증거의 강도가 아니라 제공자 유형**이다. 강도는 각 항목의 DV(결과변수)·표본·한계로 판단한다.

| 등급 | 뜻 |
|---|---|
| `[PRIMARY]` | 학술 문헌 본문에서 확인한 측정 |
| `[VENDOR-DOC]` | 벤더 공식 문서 — **규범·명세이지 측정이 아니다** |
| `[VENDOR-MEASURE]` | 벤더가 자사 제품을 자기 측정한 것(이해상충 명시) |
| `[INDEP-MEASURE]` | 제3자 로그·프로빙 측정 |
| `[FOLKLORE]` | 널리 반복되지만 1차 근거가 없는 것 |

**모든 항목에 DV(결과변수)를 적는다.** DV가 다른 항목을 하나의 "문서를 잘 쓰면 N% 좋아진다" 서사로 합산하는 것이 이 분야의 지배적 오류다.

---

## A. 이 하네스가 존재하는 이유 — 근거가 두 덩어리로 끊겨 있다

**F1 [구조적 공백]** 이 주제의 근거는 두 덩어리이고 **그 사이가 비어 있다.**

- **발행 측**(llms.txt·robots.txt·마크다운 서빙·HTTP 지문)은 전부 **도달·효율**만 측정했고 **정확도 측정은 0건**이다.
- **정확도 측**(API 문서 RAG·예제 코드)은 전부 **문서를 이미 손에 쥐여준 조건**에서 측정해 **발견(discovery) 단계를 우회**했다.

즉 **"에이전트가 스스로 문서를 발견해서 코드가 더 맞아졌다"를 측정한 연구가 확인 범위 안에 하나도 없다.** 가장 가까운 것(F23)조차 자사 플랫폼에서 효율만 측정했고 정확도는 불변이라고 스스로 적었다. 그리고 현실 검색으로 가면 부호가 뒤집히기까지 한다(F3).

→ **이 공백이 INV-1의 근거다.** 하네스는 발행 측 개입을 **"도달·효율" 언어로만** 서술하고 정확도 개선으로 팔지 않는다.

---

## B. 문서 내용 → 코드 정확도 (정확도 레인)

**F2 `[PRIMARY]`** arXiv:2503.15231 "When LLMs Meet API Documentation" (Chen et al., HKUST, 2025-03-19)
> "(1) RAG helps improve LLMs' performance by 83%-220%. (2) Example code contributes the most to advance LLMs, instead of the descriptive texts and parameter lists in the API documentation."

ablation(§4.2.2): 예제 코드만 제거했을 때 낙폭이 가장 크다 — "the pass rates of LLMs decrease most after we remove example codes (DelExmpl) ... Qwen32B decrease from 0.66~0.82 to 0.22~0.39".
저자 권고는 "설명을 더 써라"가 아니라 **"다양한 예제 코드를 준비하라"** 이며, 빈약한 예제는 오히려 LLM을 오도한다고 적는다.
**DV**: 실행 기반 pass rate(생성 코드를 실행해 정답과 결과 일치 여부).
**조건**: 덜 알려지도록 의도 선정된 Python 라이브러리 4종(Polars·Ibis·GeoPandas·Ivy, "GitHub 코드 파일 10만 개 미만" 필터) 1,017 API, 모델 4종.
⚠ **중요한 교정**: 같은 논문 RQ4는 **인기 라이브러리 Pandas에서도 이득을 보고한다**(무문서 56.29% → top5/target 문서로 상승, "RAG together with well-prepared examples also effectively helps LLMs use APIs from well-learned libraries"). 따라서 **"문서는 저빈도 API에서만 효과가 있다"는 이분법으로 이 논문을 인용하면 MISSTATED다.** 83~220%는 덜 알려진 4개 라이브러리 한정 수치이며 Pandas를 포함하지 않는다.

**F3 `[PRIMARY]`** arXiv:2407.09726 "On Mitigating Code LLM Hallucinations with API Documentation" (Jain et al., AWS, 2024-07-13)
> "Documentation Augmented Generation (DAG) significantly improves performance for low frequency APIs (increase to 47.94% with DAG) but negatively impacts high frequency APIs **when using sub-optimal retrievers** (a 39.02% absolute drop)."

**DV**: **valid API invocation**(구문 규격 준수 여부의 정적 검증). F2의 실행 기반 pass rate와 **결과변수가 다르므로 두 수치를 나란히 놓고 비교하면 안 된다.**
**조건**: CloudAPIBench 622 태스크, 빈도 3분류(Low 0–10 / Medium 11–100 / High ≥101), 인용 수치는 전부 GPT-4o 기준.
⚠ **"차선 리트리버 사용 시"라는 조건절을 떼고 인용하면 MISSTATED다.** 이 항목이 말하는 것은 "고빈도 API에 문서를 주면 나빠진다"가 아니라 **"검색 품질이 나쁘면 이미 잘 아는 API에서 해가 된다"** 이다.

**F4 `[PRIMARY]`** arXiv:2207.05987 DocPrompting (Zhou et al., CMU, 2022)
> "improves strong base models such as CodeT5 by 2.85% in pass@1 (52% relative gain)"

**DV**: 실행 기반 pass@1/pass@10(CoNaLa). 2.85는 **절대 포인트**, 52%는 그에 대응하는 상대값 — 둘을 섞어 "52% 향상"만 단독 인용하면 오도.

**F5 `[PRIMARY]`** arXiv:2604.09515 "When LLMs Lag Behind: Knowledge Conflicts from Evolving APIs" (2026-04-10)
> "without comprehensive documentation, LLMs struggle to prioritize external context, averaging only 42.55% of generated code examples are executable in the target environment. While structured documentation and larger model scales improve LLMs' ability to update adoption, they do not fully resolve executability issues with a low 66.36% executable rate."

**DV**: 실행 가능률. **분모가 전체 생성물이 아니라 "업데이트된 API를 채택한 케이스"** 다.
**조건**: Python 라이브러리 8종의 실제 API 업데이트 270건, 모델 11종. 42.55%=설명만, 66.36%=설명+API 문서.

**F6 `[PRIMARY]`** arXiv:2604.24222 "Learning from Execution" (2026-04-27)
> "documentation mainly helps models identify what APIs to use and remains insufficient for teaching how to use them correctly. Even with oracle API-document retrieval, LLMs still make recurring errors at the API, cross-API, and task levels"

**DV**: pass@1. **조건**: 사설·저노출 라이브러리 벤치 2종(ndonnx·numba-cuda), 7B급 모델 3종. **오라클 검색을 줘도 개선이 미미**(NumbaEval Qwen2.5-Coder 26.15% → 27.70%).
→ 문서를 완벽히 찾아 주는 것만으로는 부족하다는 반대 방향 근거다. F2와 나란히 놓고 한쪽만 채택하지 말 것.

**F7 `[PRIMARY]`** arXiv:2605.31478 (2026-05-29) — "improves every evaluated open-weight model of at least 7B parameters and every commercial API by 32 to 56 accuracy points".
**DV**: 실행 검증형 정확도. **조건**: **pandapower 단일 라이브러리·전력계통 단일 도메인·저자 자신의 개입 기법 전후 비교**(문서 유무 대조가 아님). 일반 문서화 효과로 확장 인용 금지.

**F8 `[PRIMARY]`** arXiv:2404.03114 "Testing the Effect of Code Documentation on LLM Code Understanding" (MITRE, 2024-04-03)
> "providing an LLM with \"incorrect\" documentation can greatly hinder code understanding, while incomplete or missing documentation does not seem to significantly affect an LLM's ability to understand code."

**DV**: **LLM의** 코드 이해 — 조작적으로는 LLM이 생성한 단위테스트의 통과 비율. **사람의 이해도, 코드 생성 정확도도 아니다.**
⚠ **두 가지 필수 한정**: ① 뒷부분은 **null 결과이지 동등성 검정이 아니다**(bootstrap NHST 기각 실패일 뿐, TOST·동등성 마진 없음). 저자 스스로 "We therefore cannot currently conclude whether or not partial comments can significantly hurt"라 유보한다. ② GPT-4에서는 docstring 10/25/50% 유지 조건이 전체 대비 **유의하게 나빴다** — 논문 내부에서도 깨끗하지 않다.
→ 그래도 **앞부분(틀린 문서의 해악)은 강한 결과**다: random comments 조건이 GPT-3.5 22.1% / GPT-4 68.1%로 모든 조건 중 최악이며 α=0.05에서 유의.

**F9 `[PRIMARY]`** arXiv:2404.10155 (v3 "The Fault in our Stars") — 프롬프트 품질 결함 수정 시 Python은 개선, Java는 유의 개선 없음.
⚠ **"significant"를 통계적 유의성으로 읽으면 MISSTATED** — 전문에 통계 검정이 **0건**이고 "significant"는 초록에만 나온다. 본문 표현은 더 약하다("there was not a consistent trend across models and languages").

**F10 `[PRIMARY]`** arXiv:2604.06793 (2026-04-08) — "documentation from the best-performing method improves the issue-solving rate of SWE-Agent by 20.00%".
⚠ **세 가지 한정**: ① `best-performing method`는 저자 제안이 아니라 **제3자 베이스라인 RepoAgent**다(이 논문은 벤치마크만 제안). ② **20.00%는 상대값**(43.86% → 52.63%, 절대 +8.77pp). ③ 상대 개선 범위 **8.00~20.00%의 상단**이고 표본은 **57건**(25건→30건, 실질 5건 차이).
**DV**: SWE-Agent 이슈 해결률. → 이 항목이 지지하는 것은 "**문서 품질을 점수화하지 말고 다운스트림 태스크로 재라**"는 방법론이지, 특정 개선폭이 아니다.

---

## C. 저장소 컨텍스트 파일 (인접 — 이 하네스의 표적 아님)

이 하네스는 `AGENTS.md`/`CLAUDE.md`를 **만들거나 고치지 않는다**(INV-4). 아래는 경계를 긋기 위한 근거다.

**F11 `[PRIMARY]`** arXiv:2602.11988 "Evaluating AGENTS.md" (ETH Zurich, 2026-02-12/06-23) — "providing context files does not generally improve task success rates, while increasing inference cost by over 20% on average".
⚠ **출처별 차등이 핵심**: developer-provided 파일은 평균 +2.4%(p=0.21)로 LLM 생성본을 유의하게 앞서고, 저자 결론은 "**LLM-generated** 컨텍스트 파일을 생략하라"다. "컨텍스트 파일은 도움이 안 된다"로 뭉뚱그리면 MISSTATED.

**F12 `[PRIMARY · 저검정력]`** arXiv:2607.27250 (단독 저자, 2026-07-28) — TOST로 전략 간 차이를 <10~15pp로 묶었다.
⚠ **"효과 없음"으로 인용 금지.** 저자가 명시한다 — "**not a powered equivalence claim** given n=15–17 clusters", "MDE >30pp; **a 10pp effect is undetectable**". 30pp급 대형 효과조차 57%만 잡는 설계다. 정확한 인용은 **"이 표본에서 10~15pp보다 큰 효과는 관측되지 않았으나 그 이하는 배제하지 못한다"** 이다.

**F13 `[PRIMARY]`** arXiv:2606.20512 "Probe-and-Refine Tuning of Repository Guidance" (2026-06-18) — probe-and-refine 33.0% vs **static KB 28.3%** vs 무가이드 25.5%(p<0.001).
⚠ 중간 조건(28.3%)을 생략부호로 지우면 효과가 부풀려진다. 무가이드 대비 +7.5pp이지만 **이미 정적 가이던스가 있는 상태 대비는 +4.7pp**다.
이득의 성격을 저자가 명시한다 — 정밀도 향상이 아니라 **커버리지 확대**("evaluable patches for 14.5 percentage points more instances while per-patch precision remains statistically constant (~59%, p = 0.119)").
⚠ **F11과 반박 관계**이므로 두 편을 같은 방향 근거로 병렬 인용하면 안 된다.
→ 이 항목이 지지하는 것은 **"수정안 채택 판정은 문서 점수가 아니라 재측정된 태스크 결과"**(INV-6)다.

**F14 `[PRIMARY]`** arXiv:2606.09090 "Context Rot in AI-Assisted Software Development" (Treude & Baltes, 2026-06-08) — 356 저장소 중 **23.0%**에서 stale 코드 요소 참조 플래그.
⚠ **유병률이 아니라 체커의 플래그율**이다. 수동 검수 50건 중 32건(64%)만 진짜였고, 저자가 "we therefore read 23.0% as a **feasibility signal** rather than a precise prevalence"라 못박았다. 도구는 README/wiki용 체커를 AI 설정 파일에 **재활용**한 것이다.
→ 지지되는 것은 수치가 아니라 **"문서의 코드 참조 무결성은 기존 도구로 이미 검사 가능하다"** 는 방향이다.

**F15 `[PRIMARY]`** arXiv:2603.00822 ContextCov (단독 저자, 2026-02-28) — 제약 준수율 88.3% vs 67.0% vs 50.3%.
⚠ **채점 도구 = 처치 도구**다(자기 오라클을 인루프로 강제하고 같은 오라클을 베이스라인에 사후 적용). 게다가 AGENTS.md는 실제 개발자 작성물이 아니라 **저자가 LLM으로 합성**한 것이다. 독립적 준수율 비교로 인용 금지. **DV는 코드 정확도가 아니라 자체 정의 제약 준수율**이다.

---

## D. 컨텍스트 길이·위치 (인접 — 전이 제한)

**F16 `[PRIMARY]`** arXiv:2307.03172 "Lost in the Middle" (TACL) — U자 곡선.
> "We experiment with input contexts containing 10, 20, and 30 total documents." / "performance is higher when relevant information occurs at the beginning or end ... as opposed to the middle"

**DV**: multi-document QA 정확도·key-value 검색 정확도. **조건**: 총 컨텍스트가 대략 2K~6K 토큰, **2023년 모델 6종**(GPT-3.5-Turbo, Claude-1.3 등).
⚠ **문서를 어떻게 쪼갤지를 조작한 arm이 없다.** 조작한 것은 이미 조립된 컨텍스트 안 정답 문서의 **위치**다. 여기서 "그러므로 문서를 N토큰 이하로 쪼개라"로 직행할 수 없다(→ 인용 금지 #1).

**F17 `[PRIMARY]`** arXiv:2605.04763 "How Does Chunking Affect Retrieval-Augmented Code Completion?" (KCL, 2026-05-06)
> "Contrary to intuition, chunking based on functions underperforms all other strategies by 3.57--5.64 percentage points on RepoEval (Cliff's delta = -1.0)" / "cross-file context length is the dominant parameter: doubling from 2,048 to 8,192 tokens yields up to 4.2 percentage points of improvement, whereas chunk size has a weaker, non-monotonic effect."

⚠ **자른 대상은 문서가 아니라 저장소 소스 코드**다(전문에 "documentation" 0건). 문서 코퍼스로의 전이는 **유추이지 측정이 아니다.**
→ 인용 가능한 것은 방향성뿐: **"청킹 경계 선택은 유의한 효과를 갖고, 의미 단위 청킹이 자동으로 우월하지 않다"**, **"컨텍스트 총량 > 청크 크기"**.

---

## E. 발행 측 — 에이전트의 HTTP 행동

**F18 `[PRIMARY · 단일 엔드포인트]`** arXiv:2604.02544 "Developer Experience with AI Coding Agents: HTTP Behavioral Signatures in Documentation Portals" (Oleksii Borysenko, Cisco DevNet, v1 2026-04-02 / v2 2026-07-24)
> "Table 3 summarizes the stability assessment. **No tool requested llms.txt**; access to robots.txt occurred only for Claude and MistralAI."

엔드포인트는 실제로 두 파일을 서빙했고("exposed robots.txt (permitting crawlers) and llms.txt"), **llms.txt 요청 여부는 측정 설계에 포함된 분석 항목**이었다(Table 3 전용 열, Table 4의 Basis="Measured"). 즉 "측정하지 않았다"가 아니라 **"측정했고 0이었다"** 이다.
⚠ 여기서 robots.txt를 읽은 "Claude"는 **어시스턴트 웹서비스이고 Claude Code가 아니다**(Claude Code 행은 `No`). **코딩 에이전트 9종은 robots.txt도 llms.txt도 요청하지 않았다.**
⚠ **결정적 조건**: 프롬프트가 URL을 직접 지정했다("Get developer documentation from this URL"). 따라서 이것은 **발견이 필요 없는 과제**에서의 결과이지 "에이전트가 스스로 문서를 찾아야 하는 상황"의 결과가 아니다.
**DV**: HTTP 접근 행위(요청 수·UA·헤더·pre-fetch·discovery 파일 접근). **조건**: 자체 구축 단일 Node.js/Express 엔드포인트 1개, 코딩 에이전트 9 + 어시스턴트 6, 각 3회. 저자가 "does not claim statistical representativeness" 명시.
⚠ **같은 논문 §8은 0회를 관측하고도 llms.txt를 "발견 메커니즘"으로 권고한다.** 그 결론 문장은 측정이 아니라 규범 서술이므로 **근거로 인용 금지**(저자도 "require independent evaluation"을 달았다).

**F19 `[PRIMARY]`** 같은 논문 Table 1 — 코딩 에이전트 UA
`Claude Code = axios/1.8.4` · `Cline = curl/8.4.0` · **`Junie = curl/8.4.0`(동일)** · `Cursor = got (sindresorhus/got)` · `Windsurf = colly` · `Antigravity = Go-http-client/2.0`. 명시적 제품 식별자를 담은 것은 Aider와 GitHub Copilot뿐이고, 9종 중 헤드리스 Chromium은 2종이다.
저자 한계 명시: "our measurements are **point-in-time snapshots tied to specific software versions** ... may shift substantially across releases".
→ **UA로 도구를 귀속할 수 없다는 근거**(INV-5). 두 도구가 같은 문자열을 쓰고, 값 자체가 릴리스마다 바뀐다.

**F20 `[PRIMARY]`** 같은 논문 §5.2 — "**Illustrative example, not an empirical finding. This study did not measure token consumption or documentation sizes across portals.**" / "Because this is a single document rather than a multi-portal sample, it does not establish a general distribution of documentation sizes or context-window impact."
→ 널리 인용되는 **193,217 토큰** 수치는 저자가 명시적으로 **비-실측 예시**라 라벨한 것이다.

**F21 `[PRIMARY · 측정 없음]`** arXiv:2601.02371 "Permission Manifests for Web Agents" (Marro et al. 15인, Lightweight Agent Standards Working Group, v1 제출 2025-12-07 → 2026-01 공개)
> "it is **non-enforceable by design**: it functions as a signaling and coordination tool rather than as an enforcement mechanism. Nothing prevents a malicious agent from disregarding the file entirely."

**DV 없음 — 측정·실험이 없는 표준 제안서**다. 효과 수치 인용 불가.
⚠ 원문은 하이픈 결합 `non-enforceable by design`이다(`not enforceable by design`이라는 문자열은 전문에 없음). 저자들은 이 성질을 **약점이자 강점으로 양면 서술**하므로 한쪽만 떼면 의도 왜곡이다.

---

## F. 발행 측 — 독립·벤더 측정

**F22 `[INDEP-MEASURE]`** Ahrefs, "We Analyzed 137K Sites: 97% of llms.txt Files Never Get Read" (2026-06-15)
- 모집단: Ahrefs Web Analytics에서 2026년 5월 트래픽이 있었던 **137,210 도메인**. llms.txt 보유 **~38,000**.
- > "Of the ~38,000 domains with a valid file, **97% saw no requests for it whatsoever** in May." — 분모는 **파일 보유 38K**이지 137K가 아니다. 분자는 "AI가 안 읽음"이 아니라 **아무것도(사람 포함) 안 읽음**이다.
- 실제 분석 풀: **~1.1K 도메인 / ~22K 요청**, 저자 표현 "**a tiny pool**".
- 봇 카테고리: **AI agents & agentic infrastructure는 5위(10.5%)** 이고 그 위 4개는 전부 비-AI(SEO audit 21.7% · Other/unidentified 14.9% · General web crawlers 13.1% · Tech profiling 11.6%). 1위 카테고리의 절반가량이 **Ahrefs 자사 크롤러**(10.6%p).
- 개별 봇 실측 순위: GPTBot 4.51% > **statespace-indexer 3.52%(운영자만 식별, IP 대역 미확인)** > Claude-Code 3.03%. **"Claude-Code 2위"는 원문 요약 불릿의 오기**이므로 쓰지 말 것.
- 저자 한정 2개(필수 병기): "**treat the 28% adoption figure as an upper bound**", "Every figure in this study is therefore a **ceiling** on actual llms.txt consumption."
- **DV = fetch 수.** 저자 명시 — "'fetched' doesn't mean 'read'."

**F23 `[VENDOR-MEASURE]`** Mintlify, "Docs URL Benchmark: Markdown & llms.txt > HTML" (2026-07-17)
- 설계: Claude Code + Codex(Sonnet 5·GPT-5.5) × **Mintlify 호스팅 20개 사이트** × 질문 5개 × 3회 × 4포맷 = 2,400런, 모든 fetch를 로컬 프록시로 관측. 복제는 Opus 4.8·Fable 5·GPT-5.6로 같은 20개 사이트.
- **가장 중요한 결과 — 정확도는 안 변했다**: "Accuracy stayed in the mid-to-high 90s across every format ... **The win was efficiency, not correctness.**"
- 404/태스크: **2.23(HTML) → 1.42(plain markdown) → 0.11(markdown + llms.txt 링크)**.
- **가장 실무적인 발견 — 포맷이 아니라 지도(map)가 문제였다**: "**Plain markdown was arguably the worst of the four formats.** Without a map to point to, agents started building `.md` paths on their own and **guessed more wrong URLs than they had on HTML**. Hand them the llms.txt and that stops."
- 원인: "we served a stripped-down markdown, but in doing so we **stripped out the navigation too**. The agents were left exploring blind, with no map of what pages existed, so they guessed, and fetched paths that were never real."
- ⚠ 이해상충: 자사 플랫폼·자사 기본 기능 측정이며 글에 고지 문구가 없다. 20개 사이트는 단일 생성기를 쓰는 **단일 플랫폼**이라 독립 표본이 아니다. 신뢰구간·유의성 없음. 다만 벤치마크 코드가 공개되어 있다(github.com/mintlify/url-discovery-bench).
- **DV = 태스크당 404·낭비 fetch·토큰**(도달 효율). 코드 정확도가 아니다.

**F24 `[교차 판정]`** F22와 F23은 **모순이 아니라 DV·모집단이 다르다.**
Ahrefs는 서버 로그의 전체 트래픽 분포(일반 웹 대상 봇 포함), Mintlify는 **docs를 지목받은 CLI 코딩 에이전트의 태스크 내 프록시 관측**이다.
- F23은 "**에이전트는 llms.txt를 절대 찾지 않는다**"는 전칭 주장을 반증한다(에이전트가 `/llms.txt`를 요청해 404가 났다).
- F22는 "**llms.txt가 널리 소비된다**"를 반증한다(97% 무읽힘, AI agents 5위, 전부 ceiling).
→ 정직하게 말할 수 있는 것은 **"docs를 지목받은 코딩 에이전트 맥락에서는 llms.txt/.md 경로 요청이 관측되며, 일반 웹 트래픽 분포에서는 소비가 거의 없다"** 까지다.

**F25 `[VENDOR-DOC]`** Cloudflare "Markdown for Agents" (docs, 2026-07-13 갱신)
- 메커니즘: `Accept: text/markdown` **콘텐츠 협상** → 엣지에서 오리진 HTML을 가져와 실시간 변환.
- **존 단위 옵트인**이며 **Pro/Business/Enterprise 한정**(같은 문서 안에서 플랜 서술이 불일치하므로 Availability 절을 인용하고 불일치를 병기할 것). **Free 제외** → "Cloudflare 뒤 모든 사이트가 마크다운을 준다"는 서술은 틀렸다.
- 제약: **HTML만 변환**, 오리진 응답 **2MB 상한**, **`ETag`·`Last-Modified` 제거**("conditional requests ... cannot be honored") → 조건부 요청·캐시 재검증을 포기한다.
- **`x-original-tokens` / `x-markdown-tokens` 헤더 제공** → 절감률을 **남의 수치를 옮기지 말고 자기 페이지에서 직접 측정**할 수 있다.
- ⚠ **공식 문서에 절감률 수치가 없다**(백분율 문자 0회). 문서 예시의 725/12345는 **예시 값이지 측정 평균이 아니다.**
- ⚠ **비콘텐츠 요소(헤더·푸터·내비게이션·스크립트)가 전처리 단계에서 제거된다** — F23이 관측한 실패 원인(맵 소실)과 **같은 구조**다. 단 "Cloudflare 변환이 404를 유발한다"는 어느 소스에도 없는 추론이므로 단정 금지.

**F26 `[INDEP-MEASURE · 라이브 프로빙]`** `.md` 접미사·`Accept` 협상 지원은 플랫폼마다 **비대칭**이다(관행이 표준화되지 않았다는 직접 증거).
접미사만 — VitePress·react.dev·Stripe·Vercel / 헤더만 — GitHub Docs / 둘 다 — Mintlify·GitBook·Cloudflare 계열 / **둘 다 없음 — Docusaurus·Nextra·Starlight 기본값**.
그리고 **`.md`가 `text/markdown` MIME을 보장하지 않는다** — react.dev·Stripe는 `text/plain`으로 서빙한다.

**F27 `[INDEP-MEASURE · n=7 개인 사이트]`** dacharycarey (2026-04-04)
> "Out of seven coding agents tested, **only three are identifiable from standard access logs**. Two more require the signal tracker or behavioral heuristics. And **two are effectively invisible** through server-side detection alone."

Codex CLI는 아예 방문하지 않는다 — "It never visited the site at all. ... It appears to read from a cached content index ... **You literally cannot detect it because it never comes to you.**"
가장 강한 단일 신호: "**A browser never sends `Accept: text/markdown`. That's an agent that wants markdown.**"
⚠ 저자 개인 사이트 7개, 자체 큐레이션 봇 DB, 절대 수치 없이 자릿수 대비만 제시, 자기 CI 도구를 에이전트로 오분류한 자기오염 사례도 기록. **백분율·비율로 옮기지 말 것.**

---

## G. 벤더 공식 규정 — robots.txt와 검증 채널 (4사 전수 확인)

아래 "유일하게 ~한다"류 서술은 **네 벤더 문서를 모두 확인한 뒤에만** 기재했다.

**F28 `[VENDOR-DOC]`** 사용자 트리거 페치의 robots.txt 취급이 **벤더마다 다르다.**

| 벤더 | 원문 | 강도 |
|---|---|---|
| Google | "Because the fetch was requested by a user, these fetchers **generally ignore** robots.txt rules." | 단정 |
| Perplexity | "Since a user requested the fetch, this fetcher **generally ignores** robots.txt rules." | 단정 |
| OpenAI | "Because these actions are initiated by a user, robots.txt rules **may not apply**." | 약한 표현 |
| Anthropic | **면제 문장 없음.** 봇 3종 포괄 준수 선언 "Anthropic's Bots respect 'do not crawl' signals by honoring industry standard directives in robots.txt." + "Claude-User allows site owners to control which sites can be accessed through these user-initiated requests." | 반대 방향의 명시 |

→ **"robots.txt 오설정이 AI 에이전트를 조용히 차단한다"는 단일 명제는 성립하지 않는다.** 벤더마다 규칙이 다르고, 애초에 측정된 코딩 에이전트 9종은 robots.txt를 **요청조차 하지 않았다**(F18).

**F29 `[VENDOR-DOC]`** UA 위조 경고는 **Google만** 명시한다 — "**Caution: The user agent string can be spoofed.**" 나머지 3사는 명시가 없다. ⚠ 이 침묵을 "위조가 없다/괜찮다"는 벤더 입장으로 승격하면 안 된다.

**F30 `[VENDOR-DOC]`** 진위 검증 채널
- **Google만** rDNS 마스크(`***.gae.googleusercontent.com` / `google-proxy-***.google.com`)와 정·역방향 2단계 절차를 제공한다.
- IP 목록 JSON: **Anthropic은 단일 통합 파일**(봇별 분리 불가 → "Anthropic에서 왔다"까지만 증명), OpenAI 4개(봇별), Perplexity 2개(봇별), Google 3개(소유주체별).
- 전체 UA 문자열은 OpenAI·Perplexity·Google이 게시하고, **Anthropic은 토큰만** 제공한다.

**F31 `[VENDOR-DOC]`** Perplexity WAF 권고 — "combine both **User-Agent string matching and IP address verification** for enhanced security". 벤더 자신이 UA 단독으로는 부족하다고 적는다.

---

## H. Google의 llms.txt 입장 — 세 소스의 스코프가 다르다

**F32 `[VENDOR-DOC]`** Google Search Central "AI features and your website" (2025-12-10)
> "You don't need to create new machine readable files, AI text files, or markup **to appear in these features**. There's also no special schema.org structured data that you need to add."

⚠ 두 가지 흔한 오인용: ① **"or Markdown"은 원문에 없다**(페이지에 "Markdown" 0회). ② 범위는 Google Search 전반이 아니라 바로 앞 문맥이 정의한 **AI Overviews와 AI Mode**다. 그리고 **이 페이지는 llms.txt를 한 번도 언급하지 않는다.** 최대로 말할 수 있는 것은 "llms.txt가 속할 수 있는 범주를 불필요하다고 서술"까지다.

**F33 `[개인 발화]`** John Mueller, Bluesky 2025-06-17 — "FWIW no AI system currently uses llms.txt."
⚠ 개인 계정(프로필에 "Skeets my own")의 답글이며 **Google 공식 입장이 아니다.** 방법론 미공개(본인 서버 로그, n 미상). DV는 서버 로그 fetch 발생 여부. 본인이 시간 한정을 자인했다("Maybe they will tomorrow?") → **2026년 상태의 근거로 전이 불가.**

**F34 `[VENDOR-DOC]`** Lighthouse `agentic-browsing` llms.txt 감사(PR 머지 2026-04-20, 문서 2026-05-05)
**부재는 감점이 아니라 N/A**다 — "If the file is not provided by the server (resulting in a 404), the audit is marked as **Not Applicable (N/A)**, as providing the file is **optional at the moment**." 소스 코드상 4xx는 `notApplicable`, 5xx만 `score: 0`이고, 검사 실체는 정규식 3개(H1 존재·링크 존재·50자 이상)다. 카테고리 자체가 "still under development".
⚠ "Lighthouse가 llms.txt를 권장한다"로 요약하면 MISSTATED. 정확한 요약은 **"있으면 형식을 검사하고, 없으면 해당없음 처리한다"**.
⚠ 감사 문서의 "Without this file, agents may spend more time crawling"은 **측정이 아니라 서술된 메커니즘**이다(`may`, 데이터 없음). 효과 근거로 인용 금지.

**F35 `[판정]`** 위 셋은 **소유 제품·결과변수·시점이 모두 달라 상충이 아니라 병존**한다(Search 노출 자격 / 서버 로그 fetch / 파일 형식 린트, 2025-06 ↔ 2026-04~05). **"Google이 llms.txt를 지지한다"와 "부정한다" 양쪽 다 이 세 소스로는 만들 수 없다.** 특히 Lighthouse는 **소비자가 아니라 감사자**다 — 린터가 llms.txt를 검사한다는 사실은 어떤 AI 시스템이 그것을 읽는다는 증거가 전혀 아니다.

---

## I. 보안 — 외부 문서는 신뢰할 수 없는 입력이다

**F36 `[사건 기록]`** 이 근거를 수집하는 과정에서 페치한 **공개 프로필 문구 안에 프롬프트 인젝션형 지시문**이 포함되어 있었다(조사 에이전트는 데이터로만 취급하고 따르지 않았다).
→ 이 하네스가 읽는 대상(문서 사이트·README·예제 코드·llms.txt)은 전부 **정의상 신뢰 경계 밖**이다. 그 안의 명령형 문장은 **지시가 아니라 발견으로 보고**한다(INV-7).

---

## 인용 금지 목록 (do-not-cite)

하네스 산출물에 아래 형태로 쓰지 않는다. 각 항목은 "왜 금지인가"와 "대신 말할 수 있는 것"을 함께 둔다.

| # | 금지 주장 | 왜 | 대신 |
|---|---|---|---|
| 1 | **토큰 상한 권고 수치**(quick start <15,000 / API reference <25,000 / 개념 가이드 <20,000) | 인용된 논문에 그 문자열이 **존재하지 않는다**. 논문은 "문서 크기 효과 평가는 별도 연구가 필요하다"고 적는다(F20). 컨텍스트 연구에도 임계값이 없고 분할 arm 자체가 없다(F16) | "컨텍스트 안 정보의 **위치**가 성능을 바꾼다(U자)" / 상한이 필요하면 **"우리 환경에서 측정해 정한 운영 기준이며 문헌 근거는 없다"**고 표기 |
| 2 | **"100K~200K가 실사용 한도"** | 1차 출처 없음. F16은 2K~6K 총 컨텍스트·2023년 모델이다 | "컨텍스트 창이 크다는 것이 그 컨텍스트를 잘 쓴다는 뜻은 아니다" |
| 3 | **"llms.txt가 AI 가시성/인용을 올린다"** | 97% 무읽힘(F22), Google 문서는 llms.txt를 언급조차 안 함(F32), Lighthouse는 부재를 감점 안 함(F34) | **"AI 노출 때문이 아니라, 우리 문서를 페치하는 코딩 에이전트에게 링크 지도를 주기 위해서"** 로 목적을 바꿔 말한다(F23) |
| 4 | **"agent-permissions.json은 신흥 표준"** | 측정 없는 제안서이고 저자가 **`non-enforceable by design`**을 명시(F21) | "제안된 매니페스트 포맷(프리프린트, 저자가 비집행성 명시)" — 신뢰 경계 강제의 근거로 사용 금지 |
| 5 | **"robots.txt 오설정이 에이전트를 조용히 차단한다"** | 코딩 에이전트 9종이 robots.txt를 **요청조차 하지 않았고**(F18), 사용자 트리거 페치의 취급은 벤더마다 다르다(F28) | "robots.txt는 학습·색인 크롤러 통제 수단이며, 측정된 범위에서 코딩 에이전트는 이를 요청하지 않는다. 실제 차단은 WAF/IP 계층에서 일어난다" |
| 6 | **UA 문자열로 에이전트를 식별·귀속** | `curl/8.4.0`을 Cline·Junie가 공유하고(F19), 값이 릴리스마다 바뀌며(F19), Google은 위조 가능을 경고하고(F29), 7종 중 2종은 서버측 탐지 자체가 불가하다(F27) | **선언된 벤더 봇 한정으로 UA+공개 IP AND 결합**(F30·F31), 코딩 에이전트에는 **행동 신호**(`Accept: text/markdown` 등) |
| 7 | **"HTML→Markdown이 토큰 N% 절감"** | 공식 문서에 수치가 없고(F25), 유일한 구체 수치는 벤더 블로그의 자기 글 1건 자기측정이다 | **`x-original-tokens`/`x-markdown-tokens`로 자기 페이지에서 직접 측정**하고, 베이스라인 정의(원시 HTML 통째 대비인지)를 함께 적는다 |
| 8 | **"GEO로 가시성 40% 향상"을 기술 문서로 전이** | GEO(arXiv:2311.09735)의 DV는 저자들이 새로 정의한 **Position-Adjusted Word Count**와 GPT-3.5가 채점하는 **Subjective Impression**이고, 주 실험은 상용 엔진이 아니라 저자가 만든 모사 엔진이다. 최고 성능 기법 중 하나가 **출처 없는 통계 삽입**이라 기술 문서에 적용하면 에이전트에게 허위를 먹인다 | 전이 가능한 것은 방향성 하나뿐 — "정보량을 늘리지 않고 표현·구조만 바꿔도 LLM이 그 소스를 더 쓴다". 크기·지표는 전이 불가 |
| 9 | **"컨텍스트 파일은 도움이 안 된다"** | F11은 **LLM 생성본**에 대한 결론이고 developer-provided는 +2.4%였다. F12는 저검정력이라 효과를 배제하지 못한다 | "LLM이 생성한 컨텍스트 파일은 생략을 권고받았다"(출처·조건 병기) |
| 10 | **"문서를 잘 쓰면 LLM이 코드를 더 잘 짠다"**(뭉뚱그린 형태) | 근거가 셋으로 갈린다(F2·F3·F6·F8) | ① 모델이 모르는 API 문서는 큰 효과가 있고 **그 효과의 대부분은 예제 코드가 낸다** ② 검색 품질이 나쁘면 잘 아는 API에서 해가 된다 ③ **틀린 문서는 없는 문서보다 나쁘다** |
| 11 | **문서 품질 점수 → 정확도 함수** | 연속적 품질↔정확도 함수를 측정한 연구가 확인되지 않았다. 확인된 것은 전부 이산 조건 대조다 | 점수 대신 **다운스트림 태스크로 재라**(F10·F13) |
| 12 | **"Claude-Code가 llms.txt 소비 2위"** | 원문 요약 불릿의 오기이며 실측은 3위, 2위는 **IP 미확인** 봇이다(F22) | 순위를 인용하지 말고 "전체 22K 요청의 tiny pool 안 분포"라고 적는다 |
| 13 | **"193,217 토큰 문서" 를 실측 근거로** | 저자가 "Illustrative example, **not an empirical finding**"이라 라벨(F20) | "한 벤더 문서가 그 정도 규모라고 **인용된** 예시가 있다"까지 |
| 14 | **"개선 N% 보장" / 성숙도 등급 / 종합 점수** | F1의 공백이 메워지지 않았다 | 하네스가 주장할 수 있는 것은 **"에이전트가 낭비하는 왕복을 줄인다"**와 **"거짓으로 판정되는 서술을 제거한다"** 둘뿐 |

## 확인하지 못한 것 (UNVERIFIED — 단정 금지)

- 에이전트가 llms.txt를 페치한 뒤 **그 안의 링크를 실제로 따라가는지** — 어느 소스에도 측정 없음.
- HTML→Markdown 절감률의 **독립 3자 실측** 존재 여부 — 도달하지 못함("전무"로 단정 금지, 정확한 표현은 "벤더 자체계측 외 확인된 것 없음").
- 각 벤더 robots.txt 준수 **선언의 실제 이행 실적** — 3자 측정 미대조. "선언했다"와 "준수한다"를 구분해 쓸 것.
- Mintlify·GitBook·VitePress의 `.md`/Accept 지원이 **공식 문서에 명문화**됐는지 — 동작만 프로빙 확인(예고 없이 바뀔 수 있음).
- 문서의 **구조·서식**(헤딩 깊이·목차·섹션 순서)이 정확도에 미치는 영향을 분리 측정한 연구 — 찾지 못함.
- 인용 문헌 대부분이 **동료심사 미통과 프리프린트**다(F12·F15는 단독 저자). F16은 TACL, F2·F4는 학회 게재본이 있다.
