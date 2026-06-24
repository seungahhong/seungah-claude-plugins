# context-engineering

LLM·에이전트에 전달할 **컨텍스트 페이로드를 체계적으로 조립·최적화**하는 도메인 무관 멀티 에이전트 하네스입니다.
프롬프트 한 줄을 다듬는 대신, **무엇을 왜 모델에 넣을지 정하고(Scope) → 후보를 모으고(Retrieve) →
압축·정렬하고(Process) → 진화하는 playbook으로 큐레이션해 최종 페이로드를 검증·조립(Manage)**합니다.
이것이 "context engineering" — 단순 프롬프트 설계를 넘어선 *정보 페이로드의 체계적 최적화*입니다.

## 왜 별도의 하네스인가

좋은 결과는 "더 똑똑한 프롬프트"가 아니라 **모델에 닿는 정보가 정확하고, 충분하고, 군더더기 없을 때** 나옵니다.
하지만 컨텍스트 윈도우는 유한하고, 무턱대고 채우면 핵심이 중간에 묻히거나(lost-in-the-middle), 요약하다 도메인 통찰을
잃거나(brevity bias), 반복 재작성으로 디테일이 침식되거나(context collapse), 여러 에이전트가 한 윈도우를 공유하다
서로를 오염(context pollution)시킵니다. 이 하네스는 그 실패모드를 **단계별 역할과 가드**로 구조화합니다.

## 두 개의 축

- **조립 파이프라인** — ① 범위(예산·도달 정보) → ② 수집·생성(후보 컨텍스트) → ③ 처리(압축·정렬·중복제거) → ④ 관리·조립(playbook 큐레이션·검증).
- **격리 패턴(멀티 에이전트일 때만)** — 여러 에이전트가 한 오케스트레이터 컨텍스트를 공유하면, 가벼운 per-agent 상태요약(REGISTRY)만 상시 유지하고 필요한 한 에이전트만 풀 컨텍스트로 끌어올려(FOCUS) cross-agent 오염을 막습니다.

핵심은 **"많이 넣기"가 아니라 "필요한 정보를 정확히 닿게 하기"** 입니다.

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `context-engineering` 플러그인을 활성화하면,
`context-engineering` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `context-engineering` | 오케스트레이터(진입점). 범위 설계(Context Brief) → 수집 → 처리 → 관리·조립의 파이프라인을 운영하며, 각 단계에서 전용 에이전트(context-scoper / context-retriever / context-processor / context-curator)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| Scope | `context-scoper` | 모델에 *반드시 도달해야 할 정보* + 토큰 예산 + retrieval need 명세 (무엇을 왜 넣는가) |
| Retrieve | `context-retriever` | 후보 컨텍스트 수집·생성(RAG식 retrieval and generation), 출처·relevance 표기 |
| Process | `context-processor` | 압축·정렬·중복제거 — brevity bias·lost-in-the-middle 대응, 전면 재작성 아닌 구조적 증분 |
| Manage | `context-curator` | playbook 큐레이션(generation/reflection/curation), context-collapse 가드, 멀티 에이전트면 격리 설계, 최종 페이로드 조립·검증 |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- 에이전트·LLM 호출에 넣을 **컨텍스트 페이로드를 체계적으로 설계·압축·조립**하고 싶을 때
- 컨텍스트 윈도우 예산 안에서 **무엇을 넣고 무엇을 뺄지** 근거를 두고 정하고 싶을 때
- 반복 재작성으로 디테일을 잃거나(context collapse), 핵심이 묻히는(lost-in-the-middle) 문제를 막고 싶을 때
- 여러 에이전트가 한 윈도우를 공유해 서로 오염시키는 **멀티 에이전트 컨텍스트 격리**를 설계하고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖)**
- 작업을 **여러 에이전트로 병렬화할지/어떻게 할지 판단**하는 오케스트레이션 설계 — 그건 *에이전트 오케스트레이션* 도메인 (이 하네스는 페이로드 *조립*이지 *분배 판단*이 아님)
- **AI 산출물(코드·에이전트 출력)을 엄밀히 평가**하는 judge 구성·벤치마크 validity — 그건 *평가* 도메인
- **엔지니어용 실행 명세(spec=source of truth)** 작성·검증 — 그건 *명세 주도 개발* 도메인
- **기획자용 PRD·사용자 스토리** 작성 — 그건 *제품 기획* 도메인
- 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선
- 컨텍스트 설계가 필요 없는 **단발성 한 줄 답변·단순 코드 수정**

경계가 모호하면 한 질문으로 확인합니다 — "모델에 *넣을 컨텍스트를 조립·최적화*하는 건가요, 아니면 *다른 작업*(병렬화 판단·산출물 평가·명세 작성)인가요?"

## 진행 방식 (5단계 사용법)

1. **요청을 던집니다** — "이 작업에 줄 컨텍스트를 예산 안에서 조립해줘" / "이 멀티 에이전트 컨텍스트 격리 설계해줘" 등.
2. **범위 설계 (Scope, 승인 게이트)** — `context-scoper`가 도달해야 할 정보·토큰 예산·retrieval need·범위 In/Out을 담은 **Context Brief**를 만듭니다. 여기서 승인하면 시작합니다(잘못된 범위로 수집 비용을 낭비하지 않기 위함).
3. **수집·생성 (Retrieve)** — `context-retriever`가 출처를 표기한 후보 컨텍스트 풀을 모읍니다.
4. **처리 (Process)** — `context-processor`가 압축·정렬·중복제거해 핵심을 예산 안에 위치 배치합니다(구조적 증분).
5. **관리·조립 (Manage)** — `context-curator`가 playbook으로 큐레이션하고 collapse·예산·근거를 검증해 **최종 페이로드 + 재사용 playbook**을 냅니다. 멀티 에이전트 컨텍스트면 per-agent 격리(REGISTRY/FOCUS) 설계를 함께 출력합니다.

각 단계 후 `[Phase n] {산출 요약} — 토큰 {사용/예산}` 1줄 보고, 최종 `[Context 조립 완료] 페이로드 {토큰}/{예산}, 출처 {k}건, playbook → {경로}`.

## 산출물 배치

기본 `.claude/context-engineering/{brief-slug}/`(사용자 지정 가능)에 다음을 둡니다. 문서 언어는 **한국어**.

- `context-brief.md` — 확정 Context Brief(도달 정보·예산·retrieval need·범위)
- `payload.md` — 검증된 최종 컨텍스트 페이로드(출처 표기)
- `playbook.md` — 진화하는 재사용 컨텍스트 규칙(generation/reflection/curation으로 누적, 다음 실행에서 재참조)

## 도구 경계 (요약)

| 한다 | 안 한다 (범위 밖) |
|------|-------------------|
| 컨텍스트 페이로드 조립·압축·정렬·검증 | 작업을 몇 개 에이전트로 나눌지 *병렬화 판단* |
| retrieval need·토큰 예산 설계 | AI 산출물 *평가*(judge·벤치마크 validity) |
| playbook 큐레이션·context-collapse 가드 | 엔지니어용 *실행 명세*·기획자용 *PRD* 작성 |
| 멀티 에이전트 per-agent 격리 설계 | 하네스 자체 trace 진단·단발 코드 수정 |

## 근거 논문 (전문은 references/context-engineering-research.md)

- **arXiv:2507.13334** — *A Survey of Context Engineering for Large Language Models* (Lingrui Mei et al., 2025-07). Context Engineering의 정의(정보 페이로드의 체계적 최적화)와 3대 foundational component(retrieval and generation·processing·management) 분류 — 이 하네스 Phase 구조의 근거. 신뢰도 high(3-0). CAVEAT: "formal discipline" 프레이밍은 저자들의 것이며 일부는 prompt engineering 리브랜딩이라 비판.
- **arXiv:2510.04618** — *Agentic Context Engineering (ACE): Evolving Contexts for Self-Improving Language Models* (Zhang et al., Stanford/SambaNova/UC Berkeley, 2025-10, ICLR 2026 채택). 컨텍스트를 진화하는 playbook으로 다루는 generation/reflection/curation 구조 + brevity bias·context collapse 실패모드와 구조적 증분 대응. 신뢰도 high(3-0).
- **arXiv:2604.07911** — *Dynamic Attentional Context Scoping (DACS)* (Nickson Patel, 2026-04). 멀티 에이전트 context pollution 실패모드 + REGISTRY/FOCUS per-agent 격리 패턴. CAVEAT: 단독저자·비피어리뷰 preprint, 정량수치는 합성 벤치 비중이 커 신중히 인용(질적 메커니즘만 채택). 격리 메커니즘은 멀티 에이전트 시스템에서 subagent별 독립 컨텍스트를 두는 업계 실천과 context-rot 문헌이 독립 보강.

빠르게 변하는 분야라 각 출처에 신뢰도·CAVEAT를 함께 표기했습니다. 반박된(refuted) 주장은 dossier의 *반박된 주장(투명성)* 절에만 기록하고 본문 근거로 쓰지 않습니다.

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger)와 발동하면 안 되는 경우
(should-not-trigger — 병렬화 판단·AI 산출물 평가·실행 명세 작성·기획 PRD·하네스 진단·단발 수정)를 정의해 트리거 정확도를 점검합니다.
`evals/evals.json`은 shipped 파일이 핵심 불변식(Scope 우선·구조적 증분·격리·검증·승인 게이트·경계)을 명세·강제하는지 file:section 인용으로 채점합니다.
