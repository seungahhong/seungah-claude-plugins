---
name: llm-guardrails-harness
description: LLM/에이전트 애플리케이션의 안전을 모델의 자기 정렬이나 시스템 프롬프트에 대한 신뢰가 아니라 모델 바깥을 감싸는 외부·인라인 제어 평면으로 요청 시점에 강제하는 도메인 무관 멀티 에이전트 런타임 가드레일 하네스. 사용자가 "내 챗봇 입력 파이프라인에 jailbreak·prompt-injection 탐지를 붙여줘", "LLM 응답이 사용자에게 가기 전에 PII 리댁션·독성 필터를 걸어줘", "내 LLM 앱을 OWASP LLM Top 10에 위협 모델링하고 알맞은 가드레일을 설계해줘", "에이전트가 아무 tool이나 호출해 — excessive agency 가드레일과 파괴적 행동 사람 승인 게이트를 붙여줘", "우리 내부 LLM 게이트웨이에 입력·출력 콘텐츠 레일을 둘러줘", "RAG 출력에 grounding/환각 점검과 untrusted 컨텍스트 필터링을 추가해줘", "내 가드레일을 red-team하고 ASR 대 FPR을 보고해줘", "외부 정책 엔진으로 내 에이전트가 호출 가능한 tool을 스코핑해줘"를 언급하며 LLM I/O·tool 호출에 런타임 가드레일을 설계·강제하려 할 때 발동한다. 앱을 OWASP LLM Top 10 2025에 매핑해 fail-closed 정책과 레일 배치를 정하고(Phase 0, 승인 게이트), 모델 호출 전 jailbreak/injection 탐지·Llama-Guard 스타일 입력 분류·요청 검증으로 거부/재작성하며(Phase 1), 생성 후 PII 리댁션·독성/정책 필터·grounding 점검과 검색 시점 untrusted 청크 필터링을 별도 계층으로 두고(Phase 2), 최소 권한 tool 스코핑·비가역 행동 사람 게이트로 excessive agency를 강제한 뒤 전체 레일을 red-team해 ASR·FPR을 함께 측정한다(Phase 3). 근거는 OWASP Top 10 for LLM Applications 2025·NVIDIA NeMo Guardrails(5 rail types)·Llama Guard(arXiv:2312.06674)·SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597). 발동하지 않는다 — 오프라인으로 AI 출력 품질을 LLM judge로 사후 채점·평가하는 일, 프로덕션 LLM 서비스의 사후 장애 탐지·국소화·RCA, 코드 착수 전 상류 산출물(PRD·디자인·API 계약·QA) 핸드오프 게이트 검수, 사람↔에이전트 분업·공통기반·감독 설계, 작업을 여러 에이전트로 병렬화할지·토폴로지 결정, 일반 API/백엔드 기능 구현·실행 검증, 코딩 에이전트 자신의 코드 변경 권한·샌드박스 거버넌스, 프런트엔드 소스 코드의 웹 취약점(XSS/CSRF) 스캔, 토큰·스코프·위임·동의 등 아이덴티티/인가 아키텍처 설계.
---

# LLM Guardrails — 외부·인라인 런타임 가드레일 오케스트레이터

LLM/에이전트 앱의 안전을 모델의 정렬·시스템 프롬프트 신뢰가 아니라 모델 바깥을 감싸는 **외부·인라인 제어 평면
(external control plane)** 으로 *요청 시점에* 강제한다. input·dialog·output·retrieval·execution의 **레일 taxonomy**로
요청 라이프사이클의 각 지점을 지키고, 레일 어셈블리를 적대적으로 **red-team**해 ASR·FPR을 함께 측정한다.

핵심 메시지: **"안전은 모델을 믿는 게 아니라 모델 주위에 별도의 정책 계층을 두고 요청 시점에 입력·출력·검색·행동을
검사·거부·재작성하는 것이다 — prompt injection은 LLM의 근본 설계를 악용하므로 정렬·지시만으로는 닫히지 않고,
가드레일 자체도 공격 가능한 LLM이라 단일 레일은 충분치 않다."**

> 이 하네스는 *런타임 인라인 강제*를 설계한다(레일은 라이브 요청 경로에서 텔레메트리와 함께 실행). *오프라인으로 AI
> 출력을 사후 채점·감사하지 않는다* — 그건 평가 도메인이다(아래 경계). Phase 3의 red-team은 레일을 *검증*할 뿐
> 산출물이 아니다.

## 무엇을 하는가 (네 단계)

1. 앱을 *OWASP LLM Top 10*에 매핑하고 *fail-closed 정책·레일 배치*를 정하는가? (Phase 0 — Threat-Model & Policy Definition)
2. *모델 호출 전* jailbreak/injection 탐지·입력 분류·요청 검증으로 거부/재작성하는가? (Phase 1 — Input Rails)
3. *생성 후·검색 시점* PII 리댁션·독성/정책·grounding·untrusted 청크 필터링을 별도 계층으로 두는가? (Phase 2 — Output & Retrieval Rails)
4. *최소 권한·사람 게이트*로 excessive agency를 강제하고 레일을 *red-team*해 ASR·FPR을 함께 보는가? (Phase 3 — Agent-Action Enforcement & Adversarial Verification)

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'런타임에 LLM I/O와 tool 호출의 콘텐츠·행동 정책을 외부에서 인라인 강제하는 방어심층'** 에 특화한다.
다음은 명시적으로 범위 밖이다.

- **오프라인 AI 출력 평가(judge 구성)** — LLM-as-a-Judge로 산출물 품질을 *사후 채점*하고 benchmark validity를 감사하는
  것은 평가 도메인이다. 이 하네스의 red-team은 *런타임 레일을 검증*하지 산출물을 채점하지 않는다(가장 날카로운 경계).
- **프로덕션 장애 탐지·RCA** — traces+logs+metrics로 *사후* 인시던트를 탐지·국소화·완화하는 것은 운영 도메인이다. 이
  하네스는 피해 *발생 전* 선제적 콘텐츠/행동 정책을 LLM I/O·tool 경계에 건다.
- **상류 산출물 핸드오프 게이트 검수** — 완성된 PRD·디자인·API 계약·QA를 코드 착수 *전* 검수하는 것은 핸드오프 리뷰
  도메인이다. 이 하네스는 *돌아가는 LLM 앱*에 실행 가능한 런타임 레일을 붙인다.
- **사람↔에이전트 협업 설계** — 사람↔에이전트 분업·공통기반·감독/신뢰를 설계하는 것은 사람-에이전트 협업 도메인이다.
  이 하네스의 사람 승인 게이트는 *강제 메커니즘 하나*이지 협업 모델 설계가 아니다.
- **에이전트 병렬화·토폴로지 결정** — 작업을 여러 에이전트로 나눌지·어떤 토폴로지인지는 멀티 에이전트 오케스트레이션
  도메인이다. 이 하네스는 *한 에이전트의* 위험 콘텐츠·행동을 정책으로 제약한다(직교).
- **일반 백엔드/API 구현** — API 기능 구현·실행 검증은 백엔드 구현 도메인이다. 이 하네스는 *기능*이 아니라 LLM 특화
  콘텐츠/행동 안전 계층을 더한다.
- **코딩 에이전트 코드 변경 거버넌스** — 코딩 에이전트 자신의 파일 편집 권한·샌드박스를 다루는 것은 코드 변경 거버넌스
  도메인이다. 이 하네스는 *빌드된 앱*의 서빙 시점 LLM 런타임 I/O·tool 호출을 다룬다.
- **웹 소스 취약점 스캔 · 아이덴티티/인가 아키텍처** — 프런트엔드 소스의 XSS/CSRF 스캔은 웹 보안 감사 도메인이고,
  토큰·스코프·위임·동의 등 아이덴티티/인가 설계는 인가 도메인이다. excessive agency(LLM06)가 인가와 *공유 이음매*지만,
  이 하네스는 *런타임 콘텐츠·행동 레일*이고 인가는 그 아래 *자격증명·스코프 계층*이다.

경계가 모호하면 한 질문으로 확인한다 — "*돌아가는 LLM 앱의 입력·출력·검색·행동에 런타임 가드레일을 외부에서
인라인 강제*하려는 건가요, 아니면 *다른 것*(오프라인 출력 채점·장애 RCA·상류 핸드오프 검수·사람-에이전트 협업 설계·
에이전트 병렬화·백엔드 기능 구현·코딩 에이전트 코드 거버넌스·웹 소스 취약점 스캔·아이덴티티/인가 설계)인가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **외부 강제 우선(시스템 프롬프트 신뢰 금지)** — 안전은 모델 바깥의 별도 제어 평면이다. prompt injection은 정렬·지시로
  닫히지 않는다(references §1).
- **전체 레일 taxonomy 커버** — input·dialog·output·retrieval·execution이 요청 라이프사이클의 각 지점을 지킨다. 레일은
  pass/block뿐 아니라 재작성/마스킹도 한다(references §2).
- **fail-closed 기본값** — 레일 오류·타임아웃·분류기 불확실 시 통과가 아니라 차단·강등. 부하·공격 시 fail-open 금지(references §3).
- **가드레일 자체가 공격 가능한 LLM** — 단일 분류기를 은탄환으로 두지 않고 input/output/retrieval/execution + 사람 승인
  으로 다층화한다(references §4).
- **excessive agency 최소 권한 + 사람 게이트(LLM06)** — tool마다 스코프를 좁히고 인자/결과를 검증하며 비가역·파괴적
  행동은 사람 승인. raw LLM 출력이 고폭발 반경 행동을 직접 트리거하지 않게 한다(LLM05→LLM06, references §5).
- **검색/도구 반환 콘텐츠 불신(LLM08)** — retrieval 레일이 청크를 필터/검증해 indirect prompt injection과 벡터/임베딩
  약점 악용을 막는다(references §6).
- **safety-utility 트레이드오프 명시** — ASR(놓친 공격)과 FPR(과차단)을 *둘 다* 측정한다. 과차단은 사용자가 레일을
  우회·비활성화하게 만든다(references §7).
- **런타임·인라인·관측** — 레일은 라이브 요청 경로에서 텔레메트리와 함께 실행된다(오프라인 판정과 구분). 고정 벤치마크
  정확도가 아니라 미지 공격 일반화를 평가한다(references §8).
- **정직성·falsifiability** — 세션 사례는 전이 가능한 코어만 일반화하고 특정 사내 구현은 비귀속, ASR/FPR은 세팅별 값,
  "개선 N% 보장" 금지, 가드레일은 위험 감소지 제거가 아님(references §9).
- **관찰 가능성·승인** — Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나
  중복 실행을 만들지 않는다(references §3·§9).

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Threat-Model & Policy Definition | `threat-modeler` | 앱 → OWASP LLM Top 10 매핑·콘텐츠/행동 카테고리 목록화·fail-closed 정책·레일 배치 결정 |
| 1 Input Rails | `input-rail-engineer` | 모델 호출 전 jailbreak/injection 탐지·Llama-Guard 스타일 입력 분류·요청 거부/재작성 |
| 2 Output & Retrieval Rails | `output-rail-engineer` | 생성 후 PII 리댁션·독성/정책·grounding 점검 + 검색 시점 untrusted 청크 필터링 |
| 3 Agent-Action Enforcement & Adversarial Verification | `enforcement-redteamer` | 최소 권한 tool 스코핑·비가역 행동 사람 게이트 + red-team(ASR/FPR) |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 위협 매핑·정책
정의·레일 설계·적대 검증의 품질이 가드레일의 실제 안전성과 utility를 좌우한다.

## 참조 문서

- 원칙·anti-pattern·결정 신호표: [references/llm-guardrails-harness-principles.md](./references/llm-guardrails-harness-principles.md)
- 설계 근거 연구 dossier(출처·신뢰도·인용·CAVEAT·정직성·방법론): [references/llm-guardrails-harness-research.md](./references/llm-guardrails-harness-research.md)

---

# 인터랙티브 플로우

## Phase 0 — 위협 모델링·정책 정의 (Threat-Model & Policy Definition) · 승인 게이트

`threat-modeler`를 호출해 앱을 OWASP LLM Top 10에 매핑하고 fail-closed 정책·레일 배치를 정한다.

```
Agent(
  subagent_type="threat-modeler", model="opus",
  prompt="""
  [역할] 대상 LLM/에이전트 앱을 OWASP LLM Top 10 2025에 매핑하고 fail-closed 정책·레일 배치를 정의한다.
  [입력] 앱/에이전트 맥락: {사용자 발화} / (선택) 시스템 프롬프트·tool 카탈로그·검색소스·규제 요건.
  [규칙] 진입점·데이터 흐름·tool 권한을 OWASP LLM Top 10(LLM01 injection·LLM02 sensitive disclosure·LLM05 improper
         output·LLM06 excessive agency·LLM08 vector/embedding)에 매핑한다. 콘텐츠 카테고리(PII 클래스·독성/폭력/불법·
         off-policy)와 행동 위험(excessive agency·시스템 프롬프트/데이터 유출)을 분류기가 판정 가능한 카테고리 ID로
         내린다. 각 위험을 어느 레일(input/dialog/output/retrieval/execution)이 pass/block/재작성 중 무엇으로 강제할지
         결정하고 단일 레일 의존이 아닌 다층 배치를 명시한다. fail-closed 기본값(오류/타임아웃/불확실 시 차단·강등)을
         못 박고 fail-open을 금지로 표시한다. 레일을 구현하거나 red-team하지 않는다(정책만). 관찰 가능한 근거로만 적고
         수치를 발명하지 않는다(모르면 '미상'), 특정 사내 구현을 귀속하지 않는다.
  [출력] Guardrail Policy(OWASP 매핑·콘텐츠/행동 카테고리·fail-closed 정책·레일 배치·미상/가정).
  """
)
```

Guardrail Policy를 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 위협 모델링·정책 정의 완료 — 다음: 입력 레일. 진행할까요?`

승인 전에는 다음 단계를 시작하지 않는다(잘못된 정책으로 잘못된 레일을 설계하지 않기 위함).

## Phase 1 — 입력 레일 (Input Rails)

`input-rail-engineer`를 호출해 모델 호출 전 pre-model 레일을 설계한다.

```
Agent(
  subagent_type="input-rail-engineer", model="opus",
  prompt="""
  [역할] Phase 0 정책이 input 레일에 배치한 위험을 모델 호출 전 pre-model 레일로 설계한다.
  [입력] Guardrail Policy: {Phase 0 산출} / (선택) 입력 파이프라인·게이트웨이·분류기 자원.
  [규칙] 사용자·상류 입력을 LLM 호출 전에 검사한다. jailbreak/prompt-injection(역할극·명령 덮어쓰기·인코딩 우회)을
         탐지하고, 정책 taxonomy 대비 입력을 Llama-Guard 스타일 SAFE/UNSAFE + 카테고리 ID로 분류하며, 요청 검증으로
         거부하거나 재작성/마스킹한다(pass/block뿐 아니라 재작성). 분류기 오류·타임아웃·불확실 시 fail-closed(차단·강등),
         부하 시 fail-open 금지. 가드레일 LLM 자체가 injectable이므로 단일 분류기를 은탄환으로 두지 않고 정책이 지정한
         다층 배치(output/retrieval/execution·사람 게이트와 겹침)를 전제로 설계한다. 정책이 정의한 카테고리만 강제하고
         새 정책을 발명하지 않는다. ASR/FPR 측정·우회 탐색은 하지 않는다(Phase 3).
  [출력] Input Rail Design(injection 탐지·입력 분류·요청 검증/재작성·다층 fail-closed 배치·미상/가정).
  """
)
```

1줄 보고: `[Phase 1] 입력 레일 설계 완료 — 다음: 출력·검색 레일. 진행할까요?`

## Phase 2 — 출력·검색 레일 (Output & Retrieval Rails)

`output-rail-engineer`를 호출해 생성 후·검색 시점 레일을 설계한다.

```
Agent(
  subagent_type="output-rail-engineer", model="opus",
  prompt="""
  [역할] Phase 0 정책이 output·retrieval 레일에 배치한 위험을 모델 생성 후와 검색 시점에 설계한다.
  [입력] Guardrail Policy: {Phase 0} / Input Rail Design: {Phase 1} / (선택) RAG 파이프라인·검색소스·출력 sink.
  [규칙] 생성 결과에 PII 리댁션·독성/폭력/불법·off-policy 필터·정책 대비 출력 검증을 적용하고, raw LLM 출력이 그대로
         사용자/sink로 흐르지 않게 한다(LLM05). 출력이 제공 소스에 근거하는지 grounding/환각을 점검하고 근거 없는 주장은
         강등·표시한다. 검색된 청크·도구 반환 값을 untrusted로 다뤄 모델/사용자 도달 전에 필터·정화한다(indirect prompt
         injection·벡터/임베딩 약점, LLM08). 레일은 pass/block뿐 아니라 재작성/마스킹도 하며 정책 카테고리 규칙을 따른다.
         레일 오류·불확실 시 fail-closed, 입력 레일과 별개 계층으로 겹쳐 단일 신뢰점을 피한다(입력에서 놓친 것을 잡음).
         정책이 정의한 카테고리만 강제하고 red-team·ASR/FPR 측정은 하지 않는다(Phase 3).
  [출력] Output & Retrieval Rail Design(출력 레일·retrieval 레일·fail-closed 다층·미상/가정).
  """
)
```

1줄 보고: `[Phase 2] 출력·검색 레일 설계 완료 — 다음: 행동 강제·적대 검증. 진행할까요?`

## Phase 3 — 행동 강제·적대 검증 (Agent-Action Enforcement & Adversarial Verification) · 배포 사람 게이트

`enforcement-redteamer`를 호출해 excessive agency를 강제하고 레일을 red-team한다.

```
Agent(
  subagent_type="enforcement-redteamer", model="opus",
  prompt="""
  [역할] excessive agency(LLM06)를 외부 정책 엔진으로 강제하고 전체 레일 어셈블리를 적대적으로 red-team한다.
  [입력] Guardrail Policy(Phase 0) / Input Rail Design(Phase 1) / Output & Retrieval Rail Design(Phase 2) /
         (선택) tool 카탈로그·정책 엔진·red-team 자원·트래픽 샘플.
  [규칙] tool마다 최소 권한으로 스코핑하고 인자/결과를 검증하며(execution rails), raw LLM 출력이 고폭발 반경 행동을
         직접 트리거하지 않게 한다(LLM05→LLM06). 비가역/파괴적 행동(삭제·전송·결제·외부 egress·프로덕션)은 실행 전
         사람 승인 게이트(전수 승인 아님·비가역에 집중). 그런 다음 input·output·retrieval·execution 레일 전체를 적대적
         으로 공격해 ASR(놓친 공격)과 FPR(과차단)을 함께 측정한다. 알려진 jailbreak만 테스트해 정확도를 보고하지 말고
         미지·적응형 공격 일반화를 평가한다(오염된 정적 벤치마크 불신). 이 red-team은 레일을 검증하지 산출물을 채점하지
         않는다. "안전 달성"으로 단정하지 말고 잔여 위험(residual ASR)·과차단을 정직하게 보고하며, ASR/FPR은 세팅별
         관찰값·"개선 N% 보장" 금지·가드레일=위험 감소지 제거 아님을 명시한다. red-team 자원 부재 시 UNVERIFIED로 표시한다.
  [출력] Enforcement + Red-Team Report(최소 권한 스코핑·사람 게이트·ASR/FPR·발견 우회·잔여 위험·미상/가정).
  """
)
```

배포 사람 게이트: `[Phase 3] 행동 강제·적대 검증 완료(ASR/FPR·잔여 위험) — 종합 보고로 마무리할까요?`

> 발견된 우회가 *비가역 행동*에 도달하면 그 tool을 최소 권한으로 좁히거나 사람 게이트를 강제하기 전까지 *배포를 보류*
> 권고한다(비가역 손상 금지). 가드레일은 위험을 *줄이는* 방어심층이지 제거가 아니다.

## 마무리 — 종합 보고

플로우가 끝나면 네 단계 산출물을 하나로 종합 보고한다.

- **정책**: OWASP LLM Top 10 매핑·콘텐츠/행동 카테고리·fail-closed 정책·레일 배치.
- **입력 레일**: jailbreak/injection 탐지·Llama-Guard 스타일 분류·요청 거부/재작성·다층 fail-closed.
- **출력·검색 레일**: PII 리댁션·독성/정책 필터·grounding 점검·untrusted 청크 필터링(indirect injection).
- **행동 강제·검증**: 최소 권한 tool 스코핑·비가역 행동 사람 게이트·red-team ASR/FPR·발견 우회.
- **잔여 위험·가정**: residual ASR·과차단(FPR)·UNVERIFIED 영역·사람 판단 필요 항목(가드레일=위험 감소지 제거 아님).

보고 형식(최종): `[LLM-Guardrails] 정책 {OWASP매핑·카테고리수} · 입력레일 {탐지/분류/검증} · 출력·검색레일 {PII/독성/grounding/untrusted} · 강제·검증 {최소권한·사람게이트 · ASR/FPR}`

> 정직성: Tech-Verse S04 세션은 일부 사내 게이트웨이 사례이며 본 하네스는 전이 가능한 코어(레일 taxonomy + OWASP
> 매핑 + 외부강제 원칙)만 일반화하지 특정 구현을 귀속하지 않는다. ASR/FPR은 세팅별 관찰값이고 "개선 N% 보장"을 쓰지
> 않으며, 가드레일은 위험을 줄이는 방어심층이지 제거가 아니다(적응형 공격자는 개별 레일을 우회). 상세는 research dossier 참조.
