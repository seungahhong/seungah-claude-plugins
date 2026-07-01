# agent-authorization-harness

> 에이전트가 다른 **에이전트·MCP 도구·A2A 시스템을 만들거나 배선할 때**, 그 *행동 아래*에 깔린 **머신 아이덴티티·인가
> (authorization) 아키텍처를 벤더 무관하게 설계하고 적대적으로 red-team**하는 도메인 무관 멀티 에이전트 하네스.

근거: **published RFC 8707(Resource Indicators)·RFC 8693(Token Exchange)·OWASP LLM06:2025(Excessive Agency)**(discipline
HIGH) + **ID-JAG draft-04·MCP Authorization draft·A2A spec·OWASP Agentic ASI01/ASI03**(framing MEDIUM, in-flux 초안).

## 핵심 아이디어

AI 에이전트가 도구를 쓰고 다른 에이전트와 협업하는 시스템을 만들 때, **접근을 결정하는 근거로 *네트워크·공유 API 키·LLM의
자체 판단*을 신뢰하면 안 된다.** 행동 *아래*에 깔린 아이덴티티·인가 아키텍처를 설계해야 한다.

- **누가(subject)** — 누구를 대신해 접근하는가.
- **어떤 스코프로(scope)** — 이 상호작용이 필요로 하는 *최소* 권한은 무엇인가(과대 기능·권한·자율 아님).
- **누구를 대신해(on-behalf-of)** — 위임은 어떻게 흐르고, 매 신뢰 경계에서 토큰이 어떻게 교환되는가.

이 위에서 본 하네스는 **단명·audience-bound 스코프 토큰**(RFC 8707), **토큰 교환 위임**(RFC 8693 `may_act`), **인증/인가
분리·deny-by-default·동의 게이트·감사**를 설계하고, **confused-deputy·토큰 재생·스코프 크리프·무제한 위임**을 적대적으로
검증한다. 산출물은 *인가 설계 + 위협 분석*(advisory + 설계 산출물)이지 특정 IdP/PDP 배포가 아니다.

## 언제 쓰나

- "내 **MCP 도구**에 **최소 권한 OAuth 스코프**를 설계해줘"
- "**A2A**(에이전트간) 호출에 **on-behalf-of 위임 인가**를 붙여줘"
- "**confused-deputy·토큰 재생** 관점으로 내 에이전트 인가를 **위협 모델링**해줘"
- "민감 도구 스코프에 **사람 동의 게이트**를 설계해줘"
- "에이전트의 **인증과 인가를 분리**해줘"
- "**공유 API 키**를 **단명·audience-bound 토큰**으로 바꿔줘 / **RFC 8707 audience 검증**을 강제해줘"
- "내 에이전트 인가/아이덴티티 모델을 **red-team**해줘"

## 4단계

| Phase | 이름 | 하는 일 | 게이트 |
|-------|------|---------|--------|
| 0 | 신뢰·스코프 모델링 (Trust & Scope Modeling) | 참여자(subject/actor/client/resource + authN vs authZ authority) 열거·접촉 도구/리소스/에이전트 매핑·최소 스코프·신뢰 경계 | 승인 게이트 |
| 1 | 그랜트·위임 설계 (Grant & Delegation Design) | 단명 audience-bound 토큰(RFC 8707)·토큰 교환 위임(RFC 8693 `may_act`)·매 경계 fresh exchange·no passthrough·표준 그랜트 | 1줄 보고 |
| 2 | 동의·집행 설계 (Consent & Enforcement Design) | 인증/인가 분리·deny-by-default·민감 스코프 사람 동의 게이트·end-to-end audience 검증·감사 로깅 | 민감 스코프 동의 게이트 |
| 3 | 적대적 인가 검증 (Adversarial Authorization Verification) | confused-deputy·토큰 재생/passthrough·스코프 크리프·무제한 위임 상대 적대 검증·위협 분석 | 1줄 보고 |

> **산출물은 설계 + red-team 분석이지 배포가 아니다.** Keycloak/Athenz/Kubernetes를 세우는 것은 인프라 작업으로 범위 밖이다.
> red-team은 위험을 *줄이지 제거하지 않는다* — 완벽한 최소권한 설계도 *부여된 스코프 안에서* prompt injection으로 무기화될
> 수 있어(confused deputy), 런타임 콘텐츠·행동 레일 도메인과 *합성*한다(대체 아님).

## 사용법

스킬을 발동시키는 발화(위 "언제 쓰나")를 입력하면 오케스트레이터가 Phase 0부터 진행한다. Phase 0(신뢰·스코프 모델링) 직후
승인 게이트, Phase 2의 민감/비가역 스코프에 사람 동의 게이트가 있다.

## 언제 다른 도구를 쓰나 (도구 경계)

이 하네스는 **'만들어지는 에이전트/도구/A2A 시스템의 머신 아이덴티티·인가 모델을 설계하고 적대적으로 검증'** 하는
사전예방 설계+red-team에 특화한다. 다음은 범위 밖이다(일반 도메인 개념으로 서술 — 특정 플러그인에 의존하지 않는다).

- **런타임 콘텐츠·행동 레일을 요청 시점에 집행**(jailbreak·PII·toxicity·출력 필터·과대행위 행동 제한) → 런타임 가드레일 도메인.
  *공유 이음새 = 과대행위(OWASP LLM06)*: 가드레일은 *행동 한계를 요청 시점에 집행*하고 이 하네스는 *그 한계가 존재·최소권한이
  되게 하는 자격/스코프/위임을 설계*한다 — 합성하되 중복 아님.
- **사람↔에이전트 업무 분업·감독·핸드오프** → 사람↔에이전트 협업 도메인 (이 하네스는 *일*이 아니라 *도구·리소스 접근의 머신 인가*를 설계)
- **파이프라인/릴리스 인프라 policy-as-code**(OPA·`terraform plan`·trust-tier) → CI/CD 도메인
- **코딩 에이전트 자신의 파일수정 권한·샌드박스 거버넌스** → 코딩 에이전트 실행 도메인 (이 하네스는 *만들어지는 시스템*의 인가)
- **일반 API/엔드포인트 구현·실행검증** → 백엔드 구현 도메인 (이 하네스는 authZ *모델* 설계이지 일반 API 구현이 아님)
- **사후 프로덕션 인시던트 탐지·RCA** → 운영 도메인 (이 하네스는 피해/배포 *이전*의 설계+red-team)
- **상류 산출물 핸드오프 게이트 검수 · 오프라인 출력 채점 · 병렬화 토폴로지 결정** → 각각 핸드오프 리뷰·평가·멀티 에이전트 오케스트레이션 도메인
- **특정 IdP/PDP 배포·인프라 provisioning**(Keycloak/Athenz/Kubernetes) → 인프라 작업(범위 밖). 벤더는 구현 세부이지 설계가 아님.

## 근거 자료

설계는 *published 표준을 load-bearing 근거로, in-flux 초안을 framing으로* 등급 분리해 접지한다. 상세 인용·등급·CAVEAT는
[skills/agent-authorization-harness/references/agent-authorization-harness-research.md](skills/agent-authorization-harness/references/agent-authorization-harness-research.md) 참조.

- **1차(discipline, HIGH·published)**: RFC 8707 "Resource Indicators for OAuth 2.0"(`resource`→audience 제한, 크로스-리소스
  재생 방지) · RFC 8693 "OAuth 2.0 Token Exchange"(`subject_token`/`actor_token`/`may_act`, delegation vs impersonation) ·
  OWASP Top 10 for LLM Applications 2025 **LLM06:2025 Excessive Agency**(excessive functionality/permissions/autonomy·JIT
  ephemeral·HITL·"authorize in external systems, not the LLM").
- **framing(MEDIUM, in-flux 초안)**: ID-JAG `draft-ietf-oauth-identity-assertion-authz-grant-04`(active IETF Internet-Draft,
  **NOT a finalized RFC**) · MCP Authorization spec(OAuth 2.1 for MCP; RFC 8707/9728 MUST; audience 검증 MUST; draft revision) ·
  A2A Protocol spec(Agent Card auth 스킴) · OWASP Top 10 for Agentic Applications **ASI01 Goal Hijack / ASI03 Identity &
  Privilege Abuse**(confused deputy; "token exchange at every trust boundary; never pass through").
- **보강/예시**: Okta "Cross App Access (XAA)"(vendor, illustrative — 필수 아님) · LY Corp tech blog / Tech-Verse S07 deck
  (출발점) · AIP "Agent Identity Protocol"(arXiv:2603.24775, academic).

> **정직성**: RFC 8707·8693·LLM06은 published(HIGH)로, ID-JAG·MCP auth·A2A·OWASP Agentic은 in-flux 초안(MEDIUM)으로
> 등급·명시했으며, 벤더(Okta/Auth0/Keycloak/Athenz)는 *illustrative일 뿐 필수가 아니다*. **"개선 N% 보장"을 쓰지 않는다** —
> red-team은 위험을 *줄이지 제거하지 않는다*. 완벽한 최소권한 설계도 스코프 내 prompt injection엔 뚫릴 수 있어 런타임 레일과 합성한다.

## 독립성

다른 마켓플레이스 플러그인에 의존하지 않는 **독립 플러그인**이다. 경계의 '범위 밖'은 일반 도메인 개념으로 서술하며,
모든 근거는 1차 자료(RFC·OWASP·프로토콜 스펙·IETF 초안)를 직접 인용한다.
