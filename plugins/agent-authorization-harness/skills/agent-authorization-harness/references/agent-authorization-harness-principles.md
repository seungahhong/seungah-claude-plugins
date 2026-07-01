# Agent Authorization Harness — 원칙·anti-pattern·결정 신호표

> `agent-authorization-harness` 하네스의 설계 헌법. 모든 Phase가 따른다. 근거는 [agent-authorization-harness-research.md](./agent-authorization-harness-research.md)
> (§N은 그 dossier의 절). 핵심 전제: **에이전트가 다른 에이전트/도구/A2A 시스템을 만들 때, 행동 *아래*에 깔린 머신
> 아이덴티티·인가를 설계로 못 박고 적대적으로 검증한다 — 네트워크·공유 키·LLM 판단을 접근 근거로 신뢰하지 않는다.**
> 산출물은 **인가 설계 + 위협 분석**(advisory + 설계 산출물)이지 특정 IdP/PDP 배포가 아니다(research §1·§5·§9).

---

## §1. 최소 권한 (least privilege across tools, scopes, autonomy)

에이전트는 *현재 task가 필요로 하는* 도구·권한·자율만 보유한다(research §3 OWASP LLM06:2025). LLM06은 과대행위를 세 축으로
분해한다 — **과대 기능(excessive functionality)·과대 권한(excessive permissions)·과대 자율(excessive autonomy)**. MCP는
`scopes_supported`/`WWW-Authenticate` 스코프 챌린지로 "scope minimization"을 스펙에 새긴다(research §2). 상호작용마다 필요한
최소 스코프를 배정하고 과대 권한을 이 세 축으로 태깅한다.

## §2. 단명·스코프 토큰 > 장수 마스터 자격증명

공유 API 키/서비스계정 시크릿(흔히 평문 config에 저장, *token sprawl*)을 *자주 갱신되는 좁은 스코프* 그랜트로 대체한다.
OWASP LLM06은 **JIT ephemeral 토큰**을 권고하고, ID-JAG의 설계는 **리프레시 토큰을 의도적으로 억제**해 유효기간을 짧게
유지한다(research §1·§3). 장수 마스터 자격증명은 모든 클라이언트가 상속하며 폐기·최소권한을 불가능하게 한다.

## §3. audience/resource 바인딩 (RFC 8707) — *end-to-end*

**가장 구체적인 resource URI**를 `resource` 파라미터로 요청해 발급 토큰의 `aud`가 *하나의 resource server*로 제한되게
한다(research §2 RFC 8707). 그리고 이를 *end-to-end*로 집행한다 — **모든 resource server가 `aud`≠자기 URI인 토큰을 거부**하고
AS(authorization server)만 믿지 않는다. MCP는 이를 MUST로 요구한다(`resource` MUST be sent; server MUST validate it is the
intended audience). audience 바인딩은 토큰 재생/passthrough를 막는 핵심 방어다.

## §4. 인증(authN) ≠ 인가(authZ) 분리

IdP는 *누구인가*(identity assertion / ID token)를 증명하고, **별개의** PDP/resource server가 *허가되는가*(scope/policy)를
결정한다(research §1 ID-JAG 역할 모델). OWASP LLM06은 **인가를 LLM에 위임하지 말고 외부 시스템에서** 하라고 명시한다
(research §3). 이 둘을 뭉치거나 인가를 에이전트 판단에 맡기면 이후 모든 방어가 무너진다.

## §5. 표준 on-behalf-of/토큰 교환 위임 + confused-deputy 방어

"에이전트가 사용자를 대신해" 접근하는 것을 **RFC 8693 토큰 교환**으로 모델링한다 — `subject_token`(누구를 대신)·
`actor_token`(누가 위임됨)·`may_act`(누가 대행 *허용*됨)(research §4 delegation vs impersonation). **매 신뢰 경계에서 토큰
교환(fresh exchange)** 하고 상류 토큰을 *절대 passthrough하지 않는다*(research §6 OWASP Agentic "never pass through received
tokens"). confused deputy는 authority가 요청자에 바인딩되지 않고 *ambient*할 때 발생한다(ASI01→ASI03).

## §6. 민감/비가역 스코프의 사람 동의

고영향·비가역 행동은 *명시적 동의 게이트*를 요구한다. 인가 authority는 *조직 정책*을 평가하며, 에이전트가 **요청한** 스코프와
조직이 **실제 허용한** 스코프를 분리한다(research §7 ID-JAG/XAA delegation; §3 LLM06 human-in-the-loop). 동의 없이 민감
스코프를 자동 부여하지 않는다.

## §7. deny-by-default + 감사성

그랜트가 *명시 허용*하지 않으면 거부한다(deny-by-default). 모든 인가 결정(**subject·actor·scope·resource·outcome**)을
로깅해 위임 체인·도구 호출을 *감사·재구성 가능*하게 한다. ambient allow와 로깅 부재는 사고 대응·최소권한을 불가능하게 한다.

## §8. 표준 준수 > 자체 구현

published/표준 메커니즘 — **OAuth 2.1·RFC 8707 Resource Indicators·RFC 8693 Token Exchange·RFC 9728 Protected Resource
Metadata·PKCE**, 그리고 emerging **ID-JAG 크로스앱 그랜트** — 을 자체 API-키 allowlist보다 우선한다(research §1·§2·§8). 단,
**특정 벤더/IdP(Okta/Auth0/Keycloak/Athenz)는 *구현 세부*이지 설계가 아니다** — 벤더는 예시일 뿐 필수가 아니다(§10).

## §9. 설계 + red-team이 산출물 (배포 아님)

산출물은 *인가 설계 + 위협/red-team 분석*이다 — 통과하는 라이브 IdP/PDP 배포가 아니다(research §9·CAVEAT). **Keycloak/Athenz/
Kubernetes를 세우는 것은 인프라 작업이고 명시적으로 범위 밖**이다(리프레임의 핵심). 이전 가능한 작업은 *액터/스코프 모델링 +
audience-bound 스코프 토큰 + on-behalf-of 위임 + 적대적 검증*이지 특정 스택이 아니다.

## §10. 정직성·falsifiability

- **published(HIGH) vs in-flux(MEDIUM) 구분**: RFC 8707·RFC 8693·OWASP LLM06:2025은 *published Standards-Track/안정
  기준*이라 discipline의 근거가 HIGH이다. **ID-JAG(draft-04)·MCP Authorization draft·A2A spec·OWASP Agentic(ASI01/ASI03)은
  in-flux 초안**이라 framing이 MEDIUM이다 — 등급을 표기하고 *설계 렌즈*로만 쓴다(research §5·CAVEAT).
- **벤더는 예시일 뿐 필수 아님** — Okta XAA 등은 illustrative이며 특정 배포를 요구하지 않는다.
- **"개선 N% 보장" 금지** — red-team은 위험을 *줄이지 제거하지 않는다*. 완벽한 최소권한·audience-bound 설계도 *부여된 스코프
  안에서* prompt injection으로 무기화될 수 있다(confused deputy) — 그래서 런타임 콘텐츠·행동 레일 도메인과 *합성*한다(대체 아님).

## §11. 승인 게이트·관찰성

Phase 0(신뢰·스코프 모델링) 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, *요청되지 않은 사이드 에이전트나 중복
실행*을 만들지 않는다. 민감 스코프의 사람 동의 게이트(Phase 2)와 잔여 위험 명시(Phase 3)는 정직성의 일부다.

---

## Anti-pattern (하지 말 것)

| Anti-pattern | 왜 나쁜가 | 올바른 패턴 | 근거 |
|---|---|---|---|
| 장수 마스터 자격증명 / 공유 API 키 | token sprawl·폐기 불가·최소권한 불가 | 단명·좁은 스코프·JIT 토큰 | §2·research §1·§3 |
| 과대·ambient 스코프 (범용 토큰 1개) | 여러 리소스에 재생 가능 | 좁은·audience-bound 토큰(RFC 8707) | §1·§3·research §2 |
| confused deputy (prompt injection→특권 도구 호출) | ambient authority가 요청자에 미바인딩 | authority를 요청자·스코프에 바인딩 + 런타임 레일 합성 | §5·research §5·§6 |
| audience 바인딩 부재 → 토큰 재생/passthrough | resource server가 exfiltration 프록시·감사 깨짐 | 모든 resource server가 aud 검증·no passthrough | §3·research §2·§6 |
| 무제한 위임 체인 (may_act·narrowing 부재) | 특권 누적·상승 | hop별 may_act 검사·스코프 narrowing | §5·research §4·§5 |
| 인가를 LLM/에이전트 판단에 위임 | 프롬프트로 우회·미감사 | 외부 PDP/resource server에서 인가 | §4·research §3 |
| 네트워크(또는 시스템 프롬프트)를 토큰 대신 신뢰 | 위치·지시는 인가 경계가 아님 | 토큰·스코프·정책으로 집행 | §9·research §5 |
| 인프라 배포를 인가 설계로 착각 | Keycloak/Athenz 세움 ≠ 모델 설계 | 액터/스코프/위임 모델링 + red-team | §9·research §9 |
| in-flux 초안을 안정 표준으로 인용 | 과신·표준 변경 시 붕괴 | published(HIGH) vs 초안(MEDIUM) 등급 표기 | §10·research §5 |
| red-team 후 "N% 안전 보장" | 위험은 감소지 제거 아님 | 잔여 위험 명시·런타임 레일 합성 | §10·research §5 |

## 결정 신호표 — 이 하네스인가, 인접 도메인인가?

| 신호 | 이 하네스(agent-authorization-harness) | 인접 도메인 |
|---|---|---|
| "MCP 도구에 최소 권한 OAuth 스코프를 설계해줘" | ✅ | — |
| "A2A 호출에 on-behalf-of 위임 인가를 붙여줘" | ✅ | — |
| "confused-deputy·토큰 재생 관점으로 인가를 위협 모델링해줘" | ✅ | — |
| "공유 API 키를 단명·audience-bound 토큰으로 바꿔줘 / RFC 8707 audience 검증 강제" | ✅ | — |
| "LLM *출력*에서 PII·toxicity 필터링 / jailbreak·prompt-injection *탐지*를 요청 시점에 집행" | ❌ | 런타임 콘텐츠·행동 가드레일 (llm-guardrails-harness) |
| "사람이 에이전트에 *일(work)*을 어떻게 위임·감독·핸드오프할지 설계" | ❌ | 사람↔에이전트 협업 (human-agent-teaming) |
| "Terraform plan·릴리스 파이프라인에 OPA policy-as-code 게이트" | ❌ | 파이프라인/인프라 policy-as-code (cicd-harness) |
| "이 리팩터 동안 *코딩 에이전트 자신*의 파일수정 권한·샌드박스 거버넌스" | ❌ | 코딩 에이전트 실행 거버넌스 (code-as-harness) |
| "/orders REST 엔드포인트를 구현하고 실행으로 검증" | ❌ | 백엔드 구현 (backend-harness) |
| "프로덕션 에이전트가 500을 던진다 — 로그·트레이스로 RCA" | ❌ | 운영 인시던트 대응 (ops-harness) |
| "코드 착수 전 API 계약·QA 인수조건 핸드오프 게이트 검수" | ❌ | 상류 핸드오프 리뷰 (review-harness) |
| "모델 답변을 오프라인 LLM-as-a-judge로 채점" | ❌ | 평가 (eval-harness) |
| "이 작업을 병렬 에이전트로 쪼갤지·토폴로지를 결정" | ❌ | 멀티 에이전트 오케스트레이션 (agent-orchestration) |

경계가 모호하면 한 질문으로 확인한다 — "*만들어지는 에이전트/도구/A2A 시스템의 인가 모델(누가·어떤 스코프로·누구를
대신해)을 설계하고 적대적으로 검증*하려는 건가요, 아니면 *다른 것*(요청 시점 콘텐츠/행동 레일 집행·사람↔에이전트 업무
분업·파이프라인 인프라 정책·코딩 에이전트 자신의 권한·일반 API 구현·장애 RCA·상류 핸드오프 검수·출력 채점·병렬화 결정·
특정 IdP 배포)인가요?"
