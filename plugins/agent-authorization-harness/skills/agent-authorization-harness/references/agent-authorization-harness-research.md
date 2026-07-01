# Agent Authorization Harness — 연구 dossier (cited)

> 이 문서는 `agent-authorization-harness` 하네스 설계의 근거가 된 조사 결과다. 출발점은 **LY Corporation Tech-Verse 2026
> S07 "ID-JAG: The Enterprise-Ready Standard for AI Agent Authorization in the MCP and A2A Era"** 세션이며, 거기서 발표된
> *배포 사례(Keycloak/Athenz/MCP 데모)* 가 아니라 그 아래 깔린 **이전 가능한 설계 규율** — 액터/스코프 모델링 +
> audience-bound 스코프 토큰 + on-behalf-of 위임 + 적대적 검증 — 을 벤더 무관하게 추출한 것이다.
> [agent-authorization-harness-principles.md](./agent-authorization-harness-principles.md)의 원칙과 상호 참조된다(§N은 이 dossier의 절 번호).
>
> **정직성 가드(머리말).** (1) **discipline은 HIGH, framing은 MEDIUM.** 최소권한 + audience-bound 스코프 토큰 +
> on-behalf-of 위임 + confused-deputy 방어라는 *이전 가능한 설계 규율*은 **published Standards-Track RFC 8707 / RFC 8693 +
> OWASP LLM06:2025** 에 접지되어 HIGH이다. 반면 **ID-JAG/XAA/MCP-auth *프레이밍*** 은 in-flux IETF 초안에 기반해 MEDIUM이다
> (아래 CAVEAT). (2) **ID-JAG는 finalized RFC가 아니라 active IETF Internet-Draft(draft-04)** 이다 — LY Corp 자체 블로그도
> "still an IETF Internet-Draft and not a finalized RFC"라고 명시한다. datatracker 소스는 authoritative하나 *표준 자체는
> 불안정*하며 바뀔 수 있다. (3) **이 하네스는 인가 모델을 설계·red-team한다(advisory + 설계 산출물). 특정 IdP/PDP를
> 배포하지 않는다** — Keycloak/Athenz/Kubernetes를 세우는 일(LY S07 데모)은 인프라 작업이고 *명시적으로 범위 밖*이다.
> **벤더 이름(Okta/Auth0/Keycloak/Athenz)은 illustrative일 뿐 필수가 아니다.** (4) **"개선 N% 보장"을 쓰지 않는다** —
> red-team은 위험을 *줄이지 제거하지 않는다*. 완벽한 최소권한·audience-bound 설계도 *부여된 스코프 안에서* prompt
> injection으로 무기화될 수 있어(confused deputy) 런타임 콘텐츠·행동 레일 도메인과 *합성*이 필요하다(대체 아님).

---

## §1. ID-JAG — 에이전트 인가의 subject/actor/client/resource 역할 모델 (in-flux 초안)

- **제목**: Identity Assertion JWT Authorization Grant (**ID-JAG**), `draft-ietf-oauth-identity-assertion-authz-grant-04`
- **출처**: https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/
- **신뢰도(등급)**: 소스 authority **HIGH** / 표준 maturity **LOW–MEDIUM** (active IETF OAuth WG Internet-Draft, **NOT a finalized RFC**)
- **핵심**: 크로스앱 인가를 위한 그랜트 — 중앙 IdP가 발급하는 *delegated·scoped·short-lived* 아이덴티티 어서션을 authorization
  grant로 교환한다. subject(누구를 대신)·actor(대행 에이전트)·client·resource의 역할 모델을 제공하며, 리프레시 토큰을
  의도적으로 억제해 유효기간을 짧게 유지한다. 본 하네스는 이를 **설계 렌즈**(delegated·scoped·short-lived·centrally-policied
  grant)로 쓰지 *필수 배포*로 두지 않는다.
- **CAVEAT**: **in-flux 초안**이다 — 절·요구사항이 개정될 수 있어 표준 maturity를 LOW–MEDIUM으로 등급한다. framing 근거이지
  discipline의 load-bearing 근거가 아니다(그건 §3·§4 published RFC).

## §2. MCP Authorization specification — OAuth 2.1 for MCP (evolving draft)

- **제목**: Model Context Protocol Authorization specification
- **출처**: https://modelcontextprotocol.io/specification/draft/basic/authorization
- **신뢰도(등급)**: **HIGH(권위) / SPEC EVOLVING(draft revision)**
- **핵심**: MCP는 인가에 **OAuth 2.1**을 채택하고 — **RFC 8707 Resource Indicators를 MUST 구현**(가장 구체적 resource URI
  요청→audience 제한), **RFC 9728 Protected Resource Metadata를 MUST**, **토큰 audience를 MUST 검증**(server MUST validate
  it is the intended audience), **PKCE** 요구, RFC 9207 `iss` 등을 명시한다. 이는 §1 "scope minimization"과 §3 audience
  바인딩을 스펙 수준에서 강제하는 근거다.
- **인용**: "the `resource` parameter ... MUST be sent" / "the server MUST validate that the token was issued for use with
  that server (audience validation)."
- **CAVEAT**: *draft revision*이라 진화 중 — 일부 요구는 아직 SHOULD(예: AS `iss` 포함은 향후 개정에서 SHOULD→MUST 승격
  예정). 그래서 framing을 MEDIUM으로 둔다. 대조적으로 §3·§4 RFC는 published·stable이다.

## §3. RFC 8707 "Resource Indicators for OAuth 2.0" — audience 바인딩 (published)

- **제목**: RFC 8707 "Resource Indicators for OAuth 2.0"
- **출처**: https://www.rfc-editor.org/rfc/rfc8707.html
- **신뢰도(등급)**: **HIGH — published Standards-Track RFC(안정)**
- **핵심**: `resource` 파라미터로 *가장 구체적인 resource URI*를 요청하면 발급 토큰의 `aud`가 그 resource server로 제한된다 —
  **크로스-리소스 토큰 재생을 방지**하는 표준 메커니즘. 본 하네스 audience-bound 스코프 토큰(Phase 1)과 end-to-end audience
  검증(Phase 2)의 *load-bearing 근거*.
- **CAVEAT**: 메커니즘은 안정이나 *end-to-end 집행*은 배포 책임 — 모든 resource server가 실제로 `aud`를 검증해야 효과가 있다(§2 MCP MUST와 결합).

## §4. RFC 8693 "OAuth 2.0 Token Exchange" — 위임 vs 위장 (published)

- **제목**: RFC 8693 "OAuth 2.0 Token Exchange"
- **출처**: https://www.rfc-editor.org/rfc/rfc8693.html
- **신뢰도(등급)**: **HIGH — published Standards-Track RFC(안정)**
- **핵심**: on-behalf-of 접근의 표준 — **`subject_token`**(누구를 대신)·**`actor_token`**(누가 위임됨)·**`may_act`**(누가
  대행 *허용*됨)으로 **delegation과 impersonation을 구분**해 표현한다. 본 하네스 위임 설계(Phase 1)와 무제한 위임 체인
  red-team(Phase 3)의 *load-bearing 근거*. 매 신뢰 경계에서 fresh exchange(§6)와 결합한다.
- **CAVEAT**: 메커니즘은 안정이나 *hop별 스코프 narrowing·may_act 검사*는 설계 책임 — 표준이 있다고 자동으로 위임이 감쇠하지 않는다.

## §5. OWASP Top 10 for LLM Applications 2025 — LLM06:2025 Excessive Agency (published) + Agentic ASI01/ASI03 (recent)

- **제목**: OWASP Top 10 for LLM Applications 2025 — **LLM06:2025 Excessive Agency**; OWASP Top 10 for Agentic Applications — **ASI01 Agent Goal Hijack, ASI03 Identity & Privilege Abuse**
- **출처**: https://genai.owasp.org/llm-top-10/ · https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/
- **신뢰도(등급)**: LLM06:2025 **HIGH** / Agentic ASI01·ASI03 **MEDIUM–HIGH(recent, 2025-12 — 신생 벤치마크)**
- **핵심**: **LLM06:2025**는 과대행위를 *excessive functionality / permissions / autonomy*로 분해하고 완화책으로 **최소권한·
  JIT ephemeral 토큰·HITL·"인가는 LLM이 아니라 외부 시스템에서"** 를 제시한다(§1·§4·§6의 근거). **ASI01 Goal Hijack →
  ASI03 Identity & Privilege Abuse**는 **confused deputy**(injection이 에이전트의 합법 자격증명으로 특권 도구 호출)를
  명명하고 "**token exchange at every trust boundary; never pass through received tokens**"를 권고한다(§6).
- **CAVEAT**: Agentic Top 10은 *recent(2025-12)* 로 신생이라 MEDIUM–HIGH로 등급한다. LLM06:2025는 확립되어 HIGH.

## §6. OWASP Agentic 위임 가이던스 — never pass through received tokens

- **출처**: §5 OWASP Agentic 소스 (ASI03)
- **신뢰도(등급)**: **MEDIUM–HIGH(recent)**
- **핵심**: 위임 hop에서 **매 신뢰 경계마다 토큰 교환**하고 *받은 토큰을 그대로 다운스트림으로 passthrough하지 않는다*.
  passthrough는 resource server를 exfiltration 프록시로 만들고 audit trail을 깬다 — 토큰 재생/passthrough red-team(Phase 3)의 근거.
- **CAVEAT**: recent 가이던스 — RFC 8693(§4, published)의 fresh exchange 메커니즘 위에 얹어 읽는다.

## §7. Okta "Cross App Access (XAA)" — 요청 스코프 vs 조직 허용 스코프 분리 (vendor, illustrative)

- **제목**: Okta "Cross App Access (XAA)" 개발자 블로그
- **출처**: https://developer.okta.com/blog/2025/09/03/cross-app-access
- **신뢰도(등급)**: **MEDIUM — vendor, illustrative only(필수 아님)**
- **핵심**: XAA = ID-JAG 그랜트의 *enterprise productization* — MCP를 위한 enterprise-managed auth를 제공하고, **IdP가
  에이전트가 *요청한* 스코프와 조직이 *허용한* 스코프를 분리**한다(§6 사람 동의·조직 정책 분리의 근거). 본 하네스는 이
  *분리 개념*만 차용하고 Okta 배포를 요구하지 않는다.
- **CAVEAT**: **벤더 소스 — illustrative일 뿐 필수가 아니다.** 특정 제품(Okta/Auth0)을 규정하지 않는다.

## §8. A2A (Agent2Agent) Protocol specification — 전송 계층 아이덴티티 (primary spec)

- **제목**: A2A (Agent2Agent) Protocol specification, security/identity model
- **출처**: https://a2a-protocol.org/latest/specification/
- **신뢰도(등급)**: **HIGH — primary protocol spec**
- **핵심**: **Agent Card**가 auth 스킴을 선언하고, 아이덴티티는 **HTTP 전송 계층**에서 처리하며(OAuth2/OIDC/API-key 스킴,
  TLS 1.3+) — agent→agent hop을 인벤토리하고 최소 스코프를 배정하는 Phase 0, 그리고 A2A 위임 red-team(Phase 3)의 근거.
- **CAVEAT**: 프로토콜 스펙 — 구체 스킴 선택·집행은 설계 책임이다(스펙이 auth를 강제하지 않는 지점을 red-team이 본다).

## §9. LY Corp Tech Blog + Tech-Verse S07 deck — 출발점(배포 사례는 범위 밖)

- **제목**: LY Corp Tech Blog "Why ID-JAG is the future of AI agent security" · Tech-Verse 2026 S07 deck "ID-JAG: The Enterprise-Ready Standard for AI Agent Authorization in the MCP and A2A Era"
- **출처**: https://techblog.lycorp.co.jp/en/20260417a · https://speakerdeck.com/lycorptech_jp/id-jag-the-enterprise-ready-standard-for-ai-agent-authorization-in-the-mcp-and-a2a-era
- **신뢰도(등급)**: **MEDIUM — vendor tech blog / 컨퍼런스 deck(설계 의도·출발점)**
- **핵심**: subject/actor/client/resource 역할·*token-sprawl* 프레이밍을 제공하고, **자체적으로 "still an IETF Internet-Draft,
  not a finalized RFC"라고 명시**한다. S07 발표는 구체적 **Keycloak/Athenz/MCP 데모**를 포함하지만 — 본 dossier는 그 배포
  스택이 아니라 *이전 가능한 설계 규율*(§1~§8)만 캡처한다.
- **CAVEAT**: **배포 사례(Keycloak/Athenz/Kubernetes)는 인프라 작업이고 명시적으로 범위 밖**이다(리프레임의 핵심). LY의 특정
  스택을 규정하지 않는다.

## §10. AIP — Agent Identity Protocol (academic, supporting)

- **제목**: "AIP: Agent Identity Protocol for Verifiable Delegation Across MCP and A2A"
- **arXiv ID**: arXiv:2603.24775
- **신뢰도(등급)**: **MEDIUM — academic preprint(보강, 종합 외)**
- **핵심**: MCP와 A2A를 가로지르는 *검증 가능한 위임(verifiable delegation)* 을 위한 아이덴티티 프로토콜 제안 — 위임 체인
  검증(Phase 3)·크로스 프로토콜 아이덴티티(Phase 0)의 인접 각도 보강.
- **CAVEAT**: *preprint 보강 소스*(핵심 근거 아님). discipline의 load-bearing 근거는 §3·§4·§5의 published 자료이며, 이 절은 인접 프레이밍으로만 인용한다.

---

## 신뢰도 등급 요약

| 소스 | 등급 | 성격 |
|---|---|---|
| RFC 8707 (§3), RFC 8693 (§4) | **HIGH** | published Standards-Track RFC(안정) — discipline의 load-bearing 근거 |
| OWASP LLM06:2025 (§5) | **HIGH** | 확립된 Top 10 항목 |
| A2A spec (§8) | **HIGH** | primary protocol spec |
| MCP Authorization (§2) | HIGH(권위)/**EVOLVING** | draft revision — framing |
| OWASP Agentic ASI01/ASI03 (§5·§6) | **MEDIUM–HIGH** | recent(2025-12) 신생 |
| ID-JAG draft-04 (§1) | 소스 HIGH / 표준 **LOW–MEDIUM** | in-flux IETF Internet-Draft(NOT RFC) — framing |
| Okta XAA (§7), LY blog/deck (§9) | **MEDIUM** | vendor/illustrative — 필수 아님 |
| AIP arXiv:2603.24775 (§10) | **MEDIUM** | academic 보강(종합 외) |

## 정직성 / CAVEAT (요약)

- **ID-JAG는 in-flux IETF Internet-Draft(draft-04), finalized RFC가 아니다.** LY Corp 자체 블로그도 그렇게 명시한다.
  datatracker는 authoritative하나 표준은 불안정하다 — LOW–MEDIUM maturity로 등급하고 *설계 렌즈*로만 쓴다.
- **MCP Authorization은 evolving draft revision.** 일부 요구는 아직 SHOULD-not-yet-MUST(예: AS `iss` 포함). 대조적으로
  **RFC 8707·RFC 8693은 published·stable** — 그래서 *discipline* 신뢰도는 HIGH이고 *agentic framing*은 MEDIUM이다.
- **이 하네스는 인가 모델을 설계·red-team한다(advisory + 설계 산출물). 특정 IdP/PDP를 배포하지 않는다.** Keycloak/Athenz/
  Kubernetes(LY S07 데모)는 인프라이고 명시적으로 범위 밖 — 리프레임의 요점이다. **벤더(Okta/Auth0/Keycloak/Athenz)는
  illustrative일 뿐 필수가 아니다.**
- **"개선 N% 보장"을 쓰지 않는다.** red-team은 위험을 *줄이지 제거하지 않는다*. 특히 완벽한 최소권한·audience-bound 설계도
  *부여된 스코프 안에서* prompt injection으로 무기화될 수 있다(confused deputy) — 그래서 런타임 콘텐츠·행동 레일 도메인과
  *합성*하지 대체하지 않는다.

## 방법론 — 출처 기반 설계 규율 추출

- **출발점**: LY Tech-Verse 2026 S07 세션(§9) 정독 — 단, *배포 사례(Keycloak/Athenz/MCP 데모)* 가 아니라 그 아래 *이전
  가능한 설계 규율*을 추출.
- **근거 접지**: framing 소스(ID-JAG·MCP auth·A2A·OWASP Agentic·XAA)와 *구분해*, discipline의 load-bearing 근거를 **published
  Standards-Track RFC 8707·RFC 8693 + OWASP LLM06:2025**에 접지 → discipline HIGH / framing MEDIUM으로 등급 분리.
- **정직성·정확 귀속 가드**: published(안정) vs in-flux(초안) vs vendor(illustrative) vs academic(보강)을 절마다 등급 표기.
  벤더는 필수 배포로 규정하지 않고, 수치는 발명하지 않으며, "개선 N% 보장"을 금지하고, 잔여 위험(스코프 내 injection)을
  은폐하지 않는다. 시점 민감성(초안 소스 2025~2026, ID-JAG draft-04, Agentic 2025-12)을 명기한다.
