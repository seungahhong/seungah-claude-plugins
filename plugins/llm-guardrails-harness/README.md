# llm-guardrails-harness

> LLM/에이전트 앱의 안전을 모델의 정렬·시스템 프롬프트 신뢰가 아니라 모델 바깥을 감싸는 **외부·인라인 제어 평면**으로
> *요청 시점에* 강제하는 도메인 무관 멀티 에이전트 런타임 가드레일 하네스.

근거: **OWASP Top 10 for LLM Applications 2025 · NVIDIA NeMo Guardrails(5 rail types) · Llama Guard(arXiv:2312.06674) ·
SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597)**.

## 핵심 아이디어

AI 에이전트가 LLM/에이전트 앱을 *만들거나 강화*할 때, 안전은 모델의 자기 정렬이나 시스템 프롬프트에 대한 신뢰가 아니라
**모델 주위를 감싸는 별도의 제어 평면(control plane)** 으로 추가되어야 한다.

- **외부 강제 > 시스템 프롬프트 신뢰** — prompt injection은 LLM의 근본 설계를 악용한다. "절대 유출하지 마" 같은 지시는
  강제 경계가 아니다 → 안전은 모델 바깥에서 검사·거부·재작성하는 *별도 계층*이다.
- **레일 taxonomy** — input·dialog·output·retrieval·execution 레일이 요청 라이프사이클의 서로 다른 지점을 지킨다. 각
  레일은 pass/block뿐 아니라 *재작성/마스킹*도 한다.
- **가드레일도 공격 가능한 LLM** — 단일 레일은 은탄환이 아니다. 다층 방어 + 최소 권한 + 사람 승인으로 겹친다.

이 위에서 본 하네스는 **위협 모델링 → 입력 레일 → 출력·검색 레일 → 행동 강제·적대 검증**의 4단계를 운영하며, 마지막에
레일 전체를 red-team해 **ASR(놓친 공격)** 과 **FPR(과차단)** 을 함께 측정한다.

## 언제 쓰나

- "내 챗봇 입력 파이프라인에 **jailbreak·prompt-injection 탐지**를 붙여줘"
- "LLM 응답이 사용자에게 가기 전에 **PII 리댁션·독성 필터**를 걸어줘"
- "내 LLM 앱을 **OWASP LLM Top 10**에 위협 모델링하고 알맞은 가드레일을 설계해줘"
- "에이전트가 아무 tool이나 호출해 — **excessive agency** 가드레일과 파괴적 행동 **사람 승인 게이트**를 붙여줘"
- "우리 내부 LLM 게이트웨이에 **입력·출력 콘텐츠 레일**을 둘러줘"
- "RAG 출력에 **grounding/환각 점검**과 **untrusted 컨텍스트 필터링**을 추가해줘"
- "내 가드레일을 **red-team**하고 **ASR 대 FPR**을 보고해줘"
- "외부 **정책 엔진**으로 내 LangChain 에이전트가 호출 가능한 tool을 스코핑해줘"

## 4단계

| Phase | 이름 | 하는 일 | 게이트 |
|-------|------|---------|--------|
| 0 | 위협 모델링·정책 정의 (Threat-Model & Policy Definition) | 앱 → OWASP LLM Top 10 2025 매핑·콘텐츠/행동 카테고리 목록화·fail-closed 정책·레일 배치 결정 | 승인 게이트 |
| 1 | 입력 레일 (Input Rails) | 모델 호출 전 jailbreak/injection 탐지·Llama-Guard 스타일 입력 분류(SAFE/UNSAFE+카테고리)·요청 거부/재작성 | 1줄 보고 |
| 2 | 출력·검색 레일 (Output & Retrieval Rails) | 생성 후 PII 리댁션·독성/정책 필터·grounding 점검 + 검색 시점 untrusted 청크 필터링(indirect injection) | 1줄 보고 |
| 3 | 행동 강제·적대 검증 (Agent-Action Enforcement & Adversarial Verification) | 최소 권한 tool 스코핑·인자/결과 검증·비가역 행동 사람 승인 게이트 + red-team(ASR/FPR) | 배포 사람 게이트 |

> 이 하네스는 **런타임 인라인 강제**를 설계한다 — 레일은 라이브 요청 경로에서 텔레메트리와 함께 실행되며, Phase 3의
> red-team은 레일을 *검증*할 뿐 산출물이 아니다(오프라인 채점과 구분).

## 사용법

스킬을 발동시키는 발화(위 "언제 쓰나")를 입력하면 오케스트레이터가 Phase 0부터 진행한다. Phase 0(정책 정의) 직후
승인 게이트가 있고, Phase 3의 파괴적/비가역 행동 강제와 배포 결정에 사람 게이트가 있다. 가드레일은 위험을 *줄이는*
방어심층이지 *제거*가 아니므로, 적대 검증에서 남은 우회(residual ASR)와 과차단(FPR)을 함께 보고한다.

## 언제 다른 도구를 쓰나 (도구 경계)

이 하네스는 **'런타임에 LLM I/O와 tool 호출의 콘텐츠·행동 정책을 외부에서 인라인 강제하는 방어심층'** 에 특화한다.
다음은 범위 밖이다(일반 도메인 개념으로 서술 — 특정 플러그인에 의존하지 않는다).

- **오프라인으로 AI 출력 품질을 LLM judge로 사후 채점·감사** → 평가 도메인 (여기 red-team eval은 레일을 *검증*하지 산출물을 채점하지 않음 — 가장 날카로운 경계)
- **프로덕션 LLM 서비스의 사후 장애 탐지·국소화·RCA** → 운영 도메인 (이 하네스는 피해 *발생 전* 선제적 콘텐츠/행동 정책)
- **코드 착수 전 상류 산출물(PRD·디자인·API 계약·QA) 핸드오프 게이트 검수** → 핸드오프 리뷰 도메인
- **사람↔에이전트 분업·공통기반·감독/신뢰 설계** → 사람-에이전트 협업 도메인 (사람 승인 게이트는 강제 메커니즘 하나이지 협업 설계가 아님)
- **작업을 여러 에이전트로 병렬화할지·토폴로지 결정** → 멀티 에이전트 오케스트레이션 도메인
- **일반 API/백엔드 기능 구현·실행 검증** → 백엔드 구현 도메인 (기능 정확성이 아니라 LLM 특화 콘텐츠/행동 안전 계층)
- **코딩 에이전트 자신의 코드 변경 권한·샌드박스 거버넌스** → 코드 변경 거버넌스 도메인 (빌드된 앱의 서빙 시점 LLM 런타임을 다룸)
- **프런트엔드 소스 코드의 웹 취약점(XSS/CSRF) 스캔** → 웹 보안 감사 도메인 (소스 결함이 아니라 LLM 생성 콘텐츠·행동 필터)
- **토큰·스코프·위임·동의 등 아이덴티티/인가 아키텍처 설계** → 인가/아이덴티티 도메인 (excessive agency가 공유 이음매지만, 이 하네스는 런타임 콘텐츠·행동 레일, 저쪽은 그 아래 자격증명·스코프 계층)

## 근거 자료

설계는 아래 1차 자료 정독에 기반한다. 상세 인용·신뢰도·CAVEAT는
[skills/llm-guardrails-harness/references/llm-guardrails-harness-research.md](skills/llm-guardrails-harness/references/llm-guardrails-harness-research.md) 참조.

- **[HIGH]** OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection … LLM06 Excessive Agency (콘텐츠/행동 위험 카탈로그).
- **[HIGH]** NVIDIA NeMo Guardrails — Guardrails Process / 5 rail types(input·dialog·output·retrieval·execution).
- **[HIGH]** Llama Guard(arXiv:2312.06674) — LLM 기반 input-output safeguard, SAFE/UNSAFE + 카테고리 분류.
- **[HIGH]** SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597) — ASR/FPR, adaptive-attack bypass.
- **[HIGH]** OWASP LLM Prompt Injection Prevention Cheat Sheet — 가드레일 LLM 자체가 injectable·방어심층·최소 권한·사람 승인.
- **[MEDIUM]** Adaptive Evaluation of Out-of-Band Defenses(arXiv:2606.26479) — 에이전트 prompt injection 대상 적응형 평가.

> **정직성**: Tech-Verse S04 발표는 일부 사내 게이트웨이 사례이며 본 하네스는 *전이 가능한 코어*(레일 taxonomy + OWASP
> 매핑 + 외부강제 원칙)만 일반화하지 특정 구현을 귀속하지 않는다. "개선 N% 보장"을 쓰지 않고 ASR/FPR은 세팅별
> 관찰값이며, 가드레일은 위험을 *줄이는* 방어심층이지 *제거*가 아니다(적응형 공격자는 개별 레일을 우회, SoK arXiv:2506.10597).

## 독립성

다른 마켓플레이스 플러그인에 의존하지 않는 **독립 플러그인**이다. 경계의 '범위 밖'은 일반 도메인 개념으로만 서술하며,
모든 근거는 1차 자료를 직접 인용한다.
