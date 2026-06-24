---
name: context-engineering
description: LLM·에이전트에 전달할 컨텍스트 페이로드를 체계적으로 조립·최적화하는 도메인 무관 멀티 에이전트 오케스트레이터. 사용자가 "이 작업에 줄 컨텍스트를 예산 안에서 조립해줘", "프롬프트/에이전트 호출에 넣을 컨텍스트를 설계·압축·정렬해줘", "컨텍스트 윈도우 예산 안에서 무엇을 넣고 뺄지 근거 두고 정해줘", "context engineering으로 페이로드 최적화", "RAG식으로 후보 컨텍스트 모아 중복제거하고 핵심만 남겨줘", "반복 재작성으로 디테일 잃지 않게 컨텍스트 관리해줘(context collapse 방지)", "핵심이 중간에 묻히지 않게 정렬해줘(lost-in-the-middle)", "여러 에이전트가 한 윈도우 공유해 서로 오염되는 걸 막게 컨텍스트 격리 설계해줘", "재사용할 컨텍스트 playbook으로 큐레이션해줘"를 언급하며 모델에 들어갈 정보 페이로드를 조립·최적화하려 할 때 발동한다. Scope(예산·도달 정보·retrieval need) → Retrieve/Generate(후보 수집) → Process(압축·정렬·중복제거, brevity bias·lost-in-the-middle 대응) → Manage(playbook 큐레이션·context-collapse 가드·격리·검증·조립)의 4단계로 운영하고, 멀티 에이전트면 per-agent 격리(REGISTRY/FOCUS)를 설계하며, Scope 승인 게이트로 시작한다. 발동하지 않는다 — 작업을 여러 에이전트로 병렬화할지/어떻게 할지 판단하는 오케스트레이션 설계, AI 산출물(코드·에이전트 출력)을 엄밀히 평가하는 judge 구성·벤치마크 validity, 엔지니어용 실행 명세(spec=source of truth) 작성·검증, 기획자용 PRD·사용자 스토리 작성, 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선, 컨텍스트 설계가 필요 없는 단발성 한 줄 답변·단순 코드 수정, settings.json 설정 변경.
---

# Context Engineering — 컨텍스트 페이로드 조립 오케스트레이터

모델·에이전트에 전달할 **컨텍스트 페이로드를 체계적으로 조립·최적화**한다. 프롬프트 한 줄을 다듬는 대신,
**무엇을 왜 넣을지 정하고(Scope) → 후보를 모으고(Retrieve) → 압축·정렬하고(Process) → playbook으로
큐레이션해 최종 페이로드를 검증·조립(Manage)**한다. 이것이 "context engineering" — 단순 프롬프트 설계를
넘어선 *정보 페이로드의 체계적 최적화*다(arXiv:2507.13334).

## 핵심 프레이밍

Context Engineering은 "더 많이 채우기"가 아니라 **필요한 정보가 모델에 정확히 닿게 하는 것**이다. 컨텍스트 윈도우는
유한하고, 무턱대고 채우면 핵심이 중간에 묻히고(lost-in-the-middle), 요약하다 통찰을 잃고(brevity bias), 반복
재작성으로 디테일이 침식되고(context collapse), 여러 에이전트가 한 윈도우를 공유하다 서로를 오염(context pollution)시킨다.
이 하네스는 그 실패모드를 **단계별 역할과 가드**로 구조화한다.

arXiv:2507.13334의 분류 체계가 이 하네스 4단계의 근거다 — 세 foundational component(context **retrieval and
generation** · **processing** · **management**)에 그 앞단의 **Scope**(retrieval need·예산 정의)를 게이트로 얹었다.

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'모델에 들어갈 정보 페이로드를 조립·최적화한다'**. 다음은 명시적으로 범위 밖이다(일반 개념으로만 변별하며 타 도메인 도구에 의존하지 않는다).

- **작업 병렬화 판단·에이전트 오케스트레이션 설계** — 한 작업을 *몇 개 에이전트로 어떻게 나눌지* 결정하는 것은 범위 밖이다.
  이 하네스는 페이로드 *조립*이지 작업 *분배 판단*이 아니다. (단, 이미 멀티 에이전트로 결정된 컨텍스트의 *격리 설계*는 Phase 3 범위 안이다.)
- **AI 산출물 평가(judge 구성·벤치마크 validity)** — 코드·에이전트 출력을 *엄밀히 평가*하는 judge 구성·다중표본·validity 감사는 범위 밖이다(그건 평가 도메인).
- **엔지니어용 실행 명세 작성** — spec=source of truth로 코드를 생성·검증하게 하는 실행 명세 작성은 범위 밖이다.
- **기획자용 PRD·사용자 스토리** — 문제정의·비즈니스 요구를 담은 제품 기획문서 작성은 범위 밖이다.
- **하네스 자체 진단·개선** — 루트 CLAUDE.md/SKILL.md/agents를 trace로 진단·고도화하는 것은 범위 밖이다.
- **단발성 한 줄 답변·단순 코드 수정** — 컨텍스트 페이로드 설계가 필요 없는 one-off 요청.

경계가 모호하면 한 질문으로 확인한다 — "모델에 *넣을 컨텍스트를 조립·최적화*하는 건가요, 아니면 *다른 작업*(병렬화 판단·산출물 평가·명세 작성)인가요?"

## 내재화 원칙 (모든 단계가 따른다)

- **Scope 우선(retrieval need 먼저)** — 수집·압축 전에 "어떤 정보가 *반드시* 모델에 도달해야 하고 예산은 얼마인가"를 Phase 0에서 못 박는다. 정당화되지 않는 정보는 넣지 않는다(컨텍스트는 많을수록 좋은 게 아니다).
- **체계적 최적화 ≠ 더 채우기** — 목표는 더 많은 토큰이 아니라 *필요한 정보가 모델에 닿는 것*이다(arXiv:2507.13334의 "정보 페이로드의 체계적 최적화").
- **구조적 증분(collapse·brevity 가드)** — 압축·재작성은 전면 재작성이 아니라 "detailed knowledge를 보존하는 구조적·증분적" 업데이트로 한다(arXiv:2510.04618). brevity bias(간결 위해 도메인 통찰 누락)와 context collapse(반복 재작성이 디테일 침식)를 구조적으로 막는다.
- **위치 인지 배치** — 가장 중요한 컨텍스트를 페이로드 앞·뒤로 배치해 lost-in-the-middle을 완화한다(처리 단계 책임).
- **playbook 큐레이션** — 컨텍스트를 일회성 system prompt가 아니라 *진화하는 playbook*으로 다루고 generation/reflection/curation으로 검증된 항목만 누적한다(arXiv:2510.04618 ACE).
- **사실 보존·출처 추적(생성 금지)** — 처리·큐레이션은 선별·조직·압축이지 새 사실 추가가 아니다. 후보에 없던 내용을 만들어 넣지 않고, 모든 조각의 출처를 페이로드까지 보존한다. 빈 must-have를 그럴듯한 생성으로 메우지 않는다(환각 컨텍스트 금지).
- **멀티 에이전트 격리(opt-in)** — 여러 에이전트가 한 오케스트레이터 컨텍스트를 공유하면 cross-agent 오염(context pollution, arXiv:2604.07911)이 생긴다. per-agent 격리(가벼운 REGISTRY + 필요 시 한 에이전트 FOCUS)로 막는다. 이 격리 패턴은 벤더 비종속 오케스트레이션 패턴이며 *멀티 에이전트 컨텍스트일 때만* 활성화하는 선택 레인이다. (CAVEAT: DACS의 정량 이득은 합성 벤치 비중이 커 단정하지 않고 질적 격리 메커니즘으로 적용한다.)
- **검증 없는 출하 금지** — 최종 페이로드는 예산·must-have 충족·중복/충돌·출처 추적·위치 배치를 context-curator가 검증한 뒤에만 출하한다.
- **관찰 가능성·승인** — 시작 전 Context Brief 승인 게이트는 항상. 매 단계 토큰 사용/예산을 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.

## 에이전트 팀

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| Scope | `context-scoper` | 도달해야 할 정보 + 토큰 예산 + retrieval need 명세(무엇을 왜 넣는가) |
| Retrieve | `context-retriever` | 후보 컨텍스트 수집·생성(RAG식 retrieval and generation), 출처·relevance 표기 |
| Process | `context-processor` | 압축·정렬·중복제거 — brevity bias·lost-in-the-middle 대응, 구조적 증분 |
| Manage | `context-curator` | playbook 큐레이션·context-collapse 가드·멀티 에이전트 격리·최종 조립·검증 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 무엇을 넣고 뺄지의 판단·검증 품질이 페이로드 품질을 좌우한다.

## 참조 문서

- 컨텍스트 엔지니어링 원리·anti-pattern(brevity bias·context collapse·lost-in-the-middle·context pollution)·격리 패턴(REGISTRY/FOCUS)·설계 지침: [references/context-engineering-principles.md](./references/context-engineering-principles.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도·caveat·반박된 주장): [references/context-engineering-research.md](./references/context-engineering-research.md)

## 산출물 배치

기본 `.claude/context-engineering/{slug}/`(사용자 지정 가능)에 다음을 둔다. 문서 언어는 **한국어**.

```
.claude/context-engineering/{slug}/
  context-brief.md   # 확정 Context Brief(도달 정보·예산·retrieval need·범위)
  payload.md         # 검증된 최종 페이로드(출처 표기, 위치 인지)
  playbook.md        # 진화하는 재사용 컨텍스트 규칙(generation/reflection/curation으로 증분 누적)
```

같은 slug로 다시 실행하면 playbook.md를 먼저 참조해 이전에 효과적이었던 컨텍스트 전략을 재사용한다.

---

# 인터랙티브 플로우

## Phase 0 — 범위 설계 (Scope) · 승인 게이트

`context-scoper`를 호출해 작업을 **Context Brief**(slug·목적·토큰 예산·retrieval need·컨텍스트 유형·범위)로 변환한다.

**재참조 감지(호출 전)**: 요청에서 임시 slug를 도출해 `.claude/context-engineering/*` 중 동일 작업 디렉토리가 있으면 그 `playbook.md` 요약을 context-scoper 입력에 포함한다(과거에 효과적이었던 컨텍스트 전략이 범위·예산 *설계*에 반영되게).

```
Agent(
  subagent_type="context-scoper", model="opus",
  prompt="""
  [역할] 작업을 받아 컨텍스트 페이로드의 범위(Context Brief)를 정의한다.
  [입력] 사용자 작업: {사용자 발화}
  [가용 출처] {코드베이스 경로·문서·이전 대화·외부 지식 등 또는 '미지정'}
  [과거 playbook(재참조 시)] {playbook digest 또는 '없음(최초 실행)'}
  [규칙] retrieval need를 must/nice/out으로 분류하고 각 need에 '왜 필요한가'를 붙인다.
         전체 토큰 예산을 정한다(모르면 보수적 상한 추정·표기). 단일 호출용인지 멀티 에이전트 공유인지 판정한다.
         범위(In/Out)를 명시하고, 작업 한 줄을 kebab-case slug로 정규화해 Brief 최상단에 부여한다(산출물 디렉토리 키).
  [출력] slug를 포함한 Context Brief.
  """
)
```

Context Brief(slug 포함)를 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 도달 정보·예산·retrieval need 확정 — 다음: 수집(예산 {N} 토큰, {단일|멀티 에이전트}). 진행할까요?`

승인 전에는 수집을 시작하지 않는다(잘못된 범위로 수집·압축 비용을 낭비하지 않기 위함). 멀티 에이전트 공유 컨텍스트로 판정되면 Phase 3에서 격리 설계가 추가됨을 함께 고지한다.

## Phase 1 — 수집·생성 (Retrieve/Generate)

**초기화(1회, 오케스트레이터 책임)**: 승인된 Context Brief에서 `slug`·토큰 예산 N·retrieval need 우선순위·멀티 에이전트 플래그를 읽어 이후 단계 placeholder에 바인딩한다. `.claude/context-engineering/{slug}/`를 확정·초기화/로드하고(같은 slug 디렉토리가 있으면 재사용), 승인된 Brief를 `{slug}/context-brief.md`로 write한다.

`context-retriever`를 호출해 retrieval need를 충족하는 후보 컨텍스트 풀을 모은다(출처·relevance·토큰·충돌 플래그 표기).

```
Agent(subagent_type="context-retriever", model="opus",
  prompt="[Brief] {Context Brief}\n[가용 출처] {출처}\n각 retrieval need(특히 must-have)를 충족하는 컨텍스트를 retrieve하거나 generate하라(생성물은 명시). 각 후보에 출처·어느 need·relevance·~토큰을 붙이고, 충돌·중복은 해소하지 말고 표시만 하라. must-have 미충족은 생성으로 메우지 말고 보고하라. 누적 토큰과 예산 대비 압축 필요량을 내라.")
```

## Phase 2 — 처리 (Process)

`context-processor`를 호출해 후보 풀을 예산 안으로 압축·정렬·중복제거한다.

```
Agent(subagent_type="context-processor", model="opus",
  prompt="[후보 풀] {Candidate Context Pool}\n[Brief 예산·우선순위] {예산 N·need 우선순위}\n예산 안으로 압축하되 전면 재작성 금지 — detailed knowledge(수치·식별자·예외)를 보존하는 구조적 증분으로만 줄여라(brevity bias·context collapse 방지). 가장 중요한 컨텍스트를 페이로드 앞·뒤로 배치하라(lost-in-the-middle 대응). 의미 중복만 제거하고 충돌(다른 값)은 둘 다 보존·표시하라. 무엇을 왜 줄였는지 압축 로그를 남기고 출처를 보존하라. must-have가 예산을 초과하면 임의 절삭 말고 우선순위 충돌로 상향 보고하라.")
```

## Phase 3 — 관리·조립 (Manage)

`context-curator`를 호출해 처리된 컨텍스트를 playbook으로 큐레이션하고, (멀티 에이전트면) 격리를 설계하고, 최종 페이로드를 검증·조립한다.

```
Agent(subagent_type="context-curator", model="opus",
  prompt="[처리된 컨텍스트] {Processed Context}\n[Brief] {예산 N·must-have·멀티 에이전트 플래그}\n[기존 playbook] {playbook 또는 '없음'}\n컨텍스트를 진화하는 playbook으로 큐레이션하라(generation/reflection/curation) — 전면 재작성 금지, 증분 추가/표시만(context-collapse 방지). 보존된 충돌은 근거로 해소하거나 둘 다 표시하라. 멀티 에이전트 공유 컨텍스트면 per-agent 격리를 설계하라 — REGISTRY(에이전트당 ≤200토큰 상태요약)로 평상시 운영하고, 한 에이전트 풀 컨텍스트가 필요하면 FOCUS(a_i)로 그 에이전트만 풀 주입·나머지는 registry로 압축(context pollution 방지; 정량 이득은 단정 말고 질적 메커니즘으로). 최종 페이로드를 검증하라 — 예산 준수·must-have 충족·충돌 해소/표시·출처 추적·위치 배치. 하나라도 어기면 출하 말고 상향 보고하라. 검증 통과분만 payload.md로, playbook 증분은 playbook.md로 낸다.")
```

## 마무리 — 결과 보고

파이프라인이 끝나면 다음을 요약 보고한다.

- **결과**: 출하(검증 통과) / 보류(사유: 예산 초과·must-have 미충족·출처 결손 → 어느 단계로 되돌릴지).
- **페이로드 규모**: 토큰 {사용}/{예산}, 출처 {k}건, 해소한 충돌 {c}건.
- **멀티 에이전트면**: 격리 설계(REGISTRY 스키마 + FOCUS 전환 규칙) 요약.
- **playbook 업데이트**: 이번에 효과적이었던 컨텍스트 전략(다음 실행에서 재참조될 자산)과 메모리 경로.

보고 형식(최종): `[Context 조립 완료] 페이로드 {n}/{N} 토큰, 출처 {k}건, 충돌 {c}건 해소 → .claude/context-engineering/{slug}/`
