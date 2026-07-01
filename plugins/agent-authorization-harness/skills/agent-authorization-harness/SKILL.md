---
name: agent-authorization-harness
description: 에이전트/MCP 도구/에이전트간(A2A) 시스템을 만들거나 배선할 때, 행동 아래에 깔리는 머신 아이덴티티·인가(authorization) 아키텍처를 벤더 무관하게 설계하고 적대적으로 red-team하는 도메인 무관 멀티 에이전트 하네스. 사용자가 "내 MCP 도구에 최소 권한 OAuth 스코프를 설계해줘", "에이전트간(A2A) 호출에 on-behalf-of 위임 인가를 붙여줘", "confused-deputy·토큰 재생 공격 관점으로 내 에이전트 인가를 위협 모델링해줘", "민감 도구 스코프에 사람 동의 게이트를 설계해줘", "에이전트의 인증과 인가 정책을 분리해줘", "공유 API 키를 단명·audience-bound 토큰으로 바꿔줘", "내 에이전트 인가/아이덴티티 모델을 red-team해줘", "MCP 서버가 RFC 8707 resource indicator와 audience 검증을 강제하게 해줘"를 언급하며 만들어지는 에이전트/도구/A2A 시스템의 인가 모델을 설계·검증하려 할 때 발동한다. 참여자·신뢰 경계·최소 스코프를 모델링하고(Phase 0, 승인 게이트), 단명 audience-bound 스코프 토큰과 토큰 교환 위임을 설계하며(Phase 1), 인증/인가 분리·deny-by-default·사람 동의 게이트·end-to-end audience 검증·감사 로깅을 설계하고(Phase 2), confused-deputy·토큰 재생/passthrough·스코프 크리프·무제한 위임을 적대적으로 검증한다(Phase 3). 근거는 published RFC 8707(Resource Indicators)·RFC 8693(Token Exchange)·OWASP LLM06:2025(Excessive Agency)로 discipline은 HIGH이고, ID-JAG draft-04·MCP Authorization draft·A2A spec·OWASP Agentic ASI01/ASI03는 in-flux 초안이라 framing은 MEDIUM으로 명시한다. 발동하지 않는다 — 런타임 콘텐츠·행동 레일(jailbreak·PII·toxicity·출력·과대행위 행동 제한)을 요청 시점에 집행하는 일, 사람↔에이전트 업무 분업·감독·핸드오프 설계, 파이프라인/릴리스 인프라 policy-as-code(OPA·terraform plan·trust-tier), 코딩 에이전트 자신의 파일수정 권한·샌드박스 거버넌스, 일반 API 엔드포인트 구현·실행검증, 사후 프로덕션 인시던트 탐지·RCA, 상류 산출물 핸드오프 게이트 검수, 오프라인 LLM-as-a-judge 출력 채점, 작업 병렬화·토폴로지 결정, 특정 IdP/Keycloak/Athenz 배포·인프라 provisioning.
---

# Agent Authorization Harness — 에이전트 인가·머신 아이덴티티 설계·red-team 오케스트레이터

에이전트가 다른 **에이전트·MCP 도구·A2A 시스템을 만들거나 배선할 때**, 그 *행동 아래*에 깔리는 **머신 아이덴티티·인가
(authorization) 아키텍처를 설계**한다 — 접근을 결정하는 근거로 *네트워크·공유 API 키·LLM의 자체 판단*을 신뢰하지 않는다.
산출물은 **인가 설계 + 위협/red-team 분석**(advisory + 설계 산출물)이며, 특정 IdP/Keycloak/Athenz *배포*가 아니다.

핵심 메시지: **"누가(subject)·어떤 스코프로(scope)·누구를 대신해(on-behalf-of) 접근하는가를 토큰·스코프·`aud`·동의·위임
체인으로 설계하고, confused-deputy·토큰 재생·스코프 크리프·무제한 위임을 적대적으로 검증한다 — 인가는 LLM이 아니라
외부 시스템에서 deny-by-default로 일어난다."**

> 이 하네스는 *인가 모델을 설계하고 red-team*한다(advisory + 설계 산출물). *특정 IdP/PDP를 배포*하지 않는다 —
> Keycloak·Athenz·Kubernetes를 세우는 일은 인프라 작업이고 **명시적으로 범위 밖**이다(리프레임의 핵심). 벤더 이름
> (Okta/Auth0/Keycloak/Athenz)은 *예시일 뿐 필수가 아니다*. 완벽한 최소권한 설계도 *부여된 스코프 안에서* prompt
> injection으로 무기화될 수 있어(confused deputy), 이 하네스는 런타임 콘텐츠·행동 레일 도메인과 *대체가 아니라 합성*된다.

## 무엇을 하는가 (네 단계)

1. *참여자·신뢰 경계*를 열거하고 접촉하는 모든 도구·리소스·에이전트에 *최소 스코프*를 배정하는가? (Phase 0 — Trust & Scope Modeling)
2. *단명·audience-bound 스코프 토큰*과 *토큰 교환 위임*을 신뢰 경계마다 설계하는가? (Phase 1 — Grant & Delegation Design)
3. *인증/인가를 분리*하고 deny-by-default·동의 게이트·end-to-end audience 검증·감사를 설계하는가? (Phase 2 — Consent & Enforcement Design)
4. *canonical 인가 공격*으로 모델을 적대적으로 검증하고 위협 분석을 내는가? (Phase 3 — Adversarial Authorization Verification)

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'만들어지는 에이전트/도구/A2A 시스템의 머신 아이덴티티·인가 모델을 설계하고 적대적으로 검증'** 하는
사전예방 설계+red-team에 특화한다. 다음은 명시적으로 범위 밖이다(일반 도메인 개념으로 서술 — 특정 플러그인에 의존하지 않는다).

- **런타임 콘텐츠·행동 레일(요청 시점 집행)** — jailbreak·prompt-injection 탐지·PII·toxicity·출력 필터·과대행위 *행동
  한계를 요청 시점에 집행*하는 것은 런타임 가드레일 도메인이다. **공유 이음새 = 과대행위(OWASP LLM06)**: 가드레일은 *행동
  한계를 요청 시점에 집행*하고, 이 하네스는 *그 한계가 존재하고 최소권한이 되게 하는 자격/스코프/위임을 설계*한다 — 둘은
  합성되며 중복이 아니다.
- **사람↔에이전트 업무 분업·감독** — 사람이 에이전트에 *일(work)*을 어떻게 위임/감독/핸드오프하는지(HITL/HOTL, 자율 수준)는
  human-agent teaming 도메인이다. 이 하네스는 *도구·리소스 접근의 머신 인가*(자격·스코프·토큰·동의)를 설계하지 업무 분업이 아니다.
- **파이프라인/릴리스 인프라 policy-as-code** — OPA·`terraform plan`·릴리스 trust-tier 같은 *전달 파이프라인/인프라 게이트*는
  CI/CD 도메인이다. 이 하네스는 *만들어진 에이전트의 런타임 도구/리소스 인가*를 설계하지 배포 파이프라인 정책이 아니다.
- **코딩 에이전트 자신의 파일수정 권한·샌드박스** — Plan→Execute→Verify 편집 루프 동안 *코딩 에이전트 자신*의 권한을
  거버넌스하는 것은 코드 실행-기반 도메인이다. 이 하네스는 *만들어지는 시스템*의 agent→tool / agent→agent 인가를 설계한다.
- **일반 API/엔드포인트 구현·실행검증** — `/orders` 같은 REST 엔드포인트를 구현하고 실행으로 검증하는 것은 백엔드 구현
  도메인이다. 이 하네스는 authZ/아이덴티티 *모델*(스코프·토큰·위임)을 설계하지 일반 API 구현이 아니다.
- **사후 프로덕션 인시던트 대응** — traces+logs+metrics로 *장애를 탐지·국소화·RCA*하는 것은 운영 도메인이다. 이 하네스는
  피해/배포 *이전*의 인가 설계+red-team이다.
- **상류 산출물 핸드오프 게이트 검수 · 오프라인 출력 채점 · 병렬화 토폴로지 결정** — 각각 핸드오프 리뷰·평가·멀티 에이전트
  오케스트레이션 도메인이다.
- **특정 IdP/PDP 배포·인프라 provisioning** — Keycloak/Athenz/Kubernetes를 *세우는* 것은 인프라 작업이고 범위 밖이다.
  벤더는 구현 세부이지 설계가 아니다.

경계가 모호하면 한 질문으로 확인한다 — "*만들어지는 에이전트/도구/A2A 시스템의 인가 모델(누가·어떤 스코프로·누구를
대신해)을 설계하고 적대적으로 검증*하려는 건가요, 아니면 *다른 것*(요청 시점 콘텐츠/행동 레일 집행·사람↔에이전트 업무
분업·파이프라인 인프라 정책·코딩 에이전트 자신의 권한·일반 API 구현·장애 RCA·상류 핸드오프 검수·출력 채점·병렬화 결정·
특정 IdP 배포)인가요?"

## 내재화 원칙 (모든 Phase가 따른다)

- **최소 권한(least privilege)** — 에이전트는 현재 task가 필요로 하는 도구·권한·자율만 보유한다. OWASP LLM06:2025은 과대행위를
  *과대 기능·과대 권한·과대 자율*로 분해한다(references §1; research §3).
- **단명·스코프 토큰 > 장수 마스터 자격증명** — 공유 API 키/서비스계정 시크릿(token sprawl)을 자주 갱신되는 좁은 스코프
  그랜트로 대체한다. LLM06은 JIT ephemeral 토큰을 권고하고 ID-JAG는 리프레시 토큰을 의도적으로 억제한다(references §2).
- **audience/resource 바인딩(RFC 8707)** — 가장 구체적인 resource URI를 요청해 발급 토큰의 `aud`를 하나의 resource server로
  제한하고, *모든* resource server가 `aud`≠자기 URI인 토큰을 거부한다(end-to-end). MCP가 이를 MUST로 요구한다(references §3).
- **인증(authN) ≠ 인가(authZ)** — IdP는 *누구인가*를 증명하고, 별개 PDP/resource server가 *허가되는가*를 결정한다. LLM06은
  인가를 *LLM에 위임하지 말고 외부 시스템에서* 하라고 명시한다(references §4).
- **표준 on-behalf-of/토큰 교환 위임 + confused-deputy 방어** — RFC 8693(`subject_token`=누구를 대신해·`actor_token`=누가
  위임됨·`may_act`=누가 대행 *허용*됨)으로 위임을 모델링하고, *매 신뢰 경계에서* 토큰 교환하며 상류 토큰을 절대 passthrough
  하지 않는다(references §5).
- **민감/비가역 스코프의 사람 동의** — 고영향·비가역 행동은 명시적 동의 게이트를 요구하고, 에이전트가 *요청한* 스코프와 조직이
  *실제 허용한* 스코프를 분리한다(references §6).
- **deny-by-default + 감사성** — 그랜트가 명시 허용하지 않으면 거부하고, 모든 인가 결정(subject·actor·scope·resource·outcome)을
  로깅해 위임 체인·도구 호출을 재구성 가능하게 한다(references §7).
- **표준 준수 > 자체 구현** — OAuth 2.1·RFC 8707·RFC 8693·RFC 9728·PKCE·ID-JAG 크로스앱 등 published/표준 메커니즘을 자체
  API-키 allowlist보다 우선하되, 특정 벤더/IdP는 *구현 세부*로 다룬다(references §8).
- **설계 + red-team이 산출물(배포 아님)** — 산출물은 *인가 설계 + 위협 분석*이지 통과하는 라이브 IdP/PDP 배포가 아니다. Keycloak/Athenz는 범위 밖(references §9·anti-pattern).
- **정직성·falsifiability** — RFC 8707·8693·OWASP LLM06은 published(HIGH)이나 ID-JAG·MCP auth·OWASP Agentic은 in-flux 초안
  (MEDIUM)으로 등급·명시한다. 벤더는 예시일 뿐 필수 아님. "개선 N% 보장" 금지 — red-team은 위험을 *줄이지 제거하지 않는다*(references §10).
- **관찰 가능성·승인** — Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다(references §11).

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Trust & Scope Modeling | `trust-scope-modeler` | 참여자(subject/actor/client/resource + authN vs authZ authority) 열거·접촉 도구/리소스/에이전트 매핑·최소 스코프·신뢰 경계 |
| 1 Grant & Delegation Design | `grant-delegation-designer` | 단명 audience-bound 스코프 토큰(RFC 8707)·토큰 교환 위임(RFC 8693 `may_act`)·매 경계 fresh exchange·no passthrough·표준 그랜트 |
| 2 Consent & Enforcement Design | `consent-enforcement-designer` | 인증/인가 분리·deny-by-default·민감 스코프 사람 동의 게이트·end-to-end audience 검증·감사 로깅 |
| 3 Adversarial Authorization Verification | `authorization-redteamer` | confused-deputy·토큰 재생/passthrough·스코프 크리프·무제한 위임·네트워크 신뢰 상대 적대 검증·위협 분석 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 액터/스코프 모델링·
위임 설계·집행 설계·적대적 인가 검증의 품질이 만들어지는 시스템의 보안 자세를 좌우한다.

## 참조 문서

- 원칙·anti-pattern·결정 신호표: [references/agent-authorization-harness-principles.md](./references/agent-authorization-harness-principles.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도 등급·CAVEAT·정직성·방법론): [references/agent-authorization-harness-research.md](./references/agent-authorization-harness-research.md)

---

# 인터랙티브 플로우

## Phase 0 — 신뢰·스코프 모델링 (Trust & Scope Modeling) · 승인 게이트

`trust-scope-modeler`를 호출해 참여자·신뢰 경계를 열거하고 접촉하는 모든 도구/리소스/에이전트에 최소 스코프를 배정한다.

```
Agent(
  subagent_type="trust-scope-modeler", model="opus",
  prompt="""
  [역할] 만들어지는 에이전트/도구/A2A 시스템의 액터·신뢰 경계·최소 스코프를 모델링한다(토큰·그랜트 설계 이전).
  [입력] 시스템 맥락: {사용자 발화} / (선택) 구성 요소(에이전트·MCP 도구·리소스 서버·다운스트림 A2A)·기존 자격증명.
  [규칙] 참여자를 역할로 열거한다 — subject/resource-owner(누구를 대신), actor/agent(대행자), client, resource server, 그리고
         인증 authority(IdP=누구인가) vs 인가 authority(PDP/resource server=허가되는가)를 *분리*해 식별한다. 시스템이 접촉하는
         모든 도구·리소스·에이전트 hop을 열거하고, 상호작용마다 *실제로 필요한 최소 스코프*를 배정한다(과대 기능·권한·자율을
         표시). 신뢰 경계를 긋는다(어디서 토큰 교환이 필요한가). OWASP LLM06의 세 root cause(excessive functionality/
         permissions/autonomy)로 과대 권한을 태깅한다. 토큰·그랜트·정책을 아직 설계하지 않는다(모델만). 관찰 가능한 근거로만
         적고 벤더/IdP를 규정하지 않으며 수치를 발명하지 않는다(모르면 '미상').
  [출력] Actor & Scope Model(역할별 참여자·authN vs authZ authority·도구/리소스/에이전트 인벤토리·상호작용별 최소 스코프·신뢰 경계·과대권한 태그·미상/가정).
  """
)
```

Actor & Scope Model을 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 신뢰·스코프 모델링 완료 — 다음: 그랜트·위임 설계. 진행할까요?`

승인 전에는 다음 단계를 시작하지 않는다(잘못된 액터/스코프 모델 위에 잘못된 토큰·위임을 설계하지 않기 위함).

## Phase 1 — 그랜트·위임 설계 (Grant & Delegation Design)

`grant-delegation-designer`를 호출해 아이덴티티·권한이 체인을 따라 흐르는 방식을 설계한다.

```
Agent(
  subagent_type="grant-delegation-designer", model="opus",
  prompt="""
  [역할] 아이덴티티·권한이 agent→tool, agent→agent hop을 어떻게 흐르는지 설계한다(그랜트·위임·토큰).
  [입력] Actor & Scope Model: {Phase 0 산출} / (선택) 기존 그랜트·프로토콜(OAuth/OIDC/MCP/A2A).
  [규칙] 장수 공유 자격증명 대신 *단명·audience-bound(RFC 8707 resource/aud) 스코프 토큰*을 설계한다 — 가장 구체적인
         resource URI를 요청해 토큰을 하나의 resource server로 제한한다. 사용자 위임은 *토큰 교환(RFC 8693)* 으로 모델링한다
         — subject_token(누구를 대신)·actor_token(누가 위임됨)·may_act(누가 대행 허용됨)을 명시하고, *매 신뢰 경계에서 fresh
         exchange*하며 상류 토큰을 *절대 passthrough하지 않는다*. 표준 그랜트(OAuth 2.1·ID-JAG 크로스앱/XAA)를 자체 API 키보다
         우선하되 ID-JAG은 in-flux 초안임을 명시한다(설계 렌즈로만, 필수 배포 아님). 정책·동의·집행을 여기서 확정하지 않는다
         (Phase 2). 특정 IdP를 배포하거나 벤더를 규정하지 않는다(설계만). 근거를 표준 조항으로 인용하고 발명하지 않는다.
  [출력] Grant & Delegation Design(hop별 토큰 유형·스코프·aud·수명·토큰 교환 위임(subject/actor/may_act)·경계별 fresh exchange·표준 그랜트 선택·미상/가정).
  """
)
```

1줄 보고: `[Phase 1] 그랜트·위임 설계 완료 — 다음: 동의·집행 설계. 진행할까요?`

## Phase 2 — 동의·집행 설계 (Consent & Enforcement Design)

`consent-enforcement-designer`를 호출해 인증/인가 분리·deny-by-default·동의·audience 검증·감사를 설계한다.

```
Agent(
  subagent_type="consent-enforcement-designer", model="opus",
  prompt="""
  [역할] 인가가 어디서·어떻게 집행되는지 설계한다(인증/인가 분리·정책·동의·검증·감사).
  [입력] Actor & Scope Model: {Phase 0} / Grant & Delegation Design: {Phase 1} / (선택) 조직 정책 제약.
  [규칙] 인증(IdP=누구인가)과 인가(resource server/PDP=허가되는가)를 *분리*한다 — 인가를 LLM에 위임하지 말고 외부 시스템에서
         한다(OWASP LLM06). 정책은 *deny-by-default*(명시 허용 없으면 거부). *모든 resource server*에서 audience 검증을 집행한다
         (aud≠자기 URI면 거부; AS만 믿지 않음). 민감/비가역 스코프는 *사람 동의 게이트*를 요구하고, 에이전트가 *요청한* 스코프와
         조직이 *허용한* 스코프를 분리한다(ID-JAG/XAA delegation·LLM06 HITL). 모든 인가 결정(subject·actor·scope·resource·
         outcome)을 로깅해 위임 체인을 감사·재구성 가능하게 한다. 정책 엔진/벤더 제품을 배포하지 않는다(설계·규칙만). 근거를
         표준·OWASP 조항으로 인용한다.
  [출력] Consent & Enforcement Design(authN/authZ 분리 지점·deny-by-default 정책·resource server별 audience 검증·민감 스코프 동의 게이트·요청 vs 허용 스코프 분리·감사 로깅 스키마·미상/가정).
  """
)
```

1줄 보고: `[Phase 2] 동의·집행 설계 완료 — 다음: 적대적 인가 검증. 진행할까요?`

## Phase 3 — 적대적 인가 검증 (Adversarial Authorization Verification)

`authorization-redteamer`를 호출해 canonical 인가 공격으로 모델을 적대적으로 검증하고 위협 분석을 낸다.

```
Agent(
  subagent_type="authorization-redteamer", model="opus",
  prompt="""
  [역할] 완성된 인가 모델(Phase 0~2)을 canonical 에이전트-아이덴티티 공격으로 적대적으로 검증하고 위협 분석을 낸다.
  [입력] Actor & Scope Model: {Phase 0} / Grant & Delegation Design: {Phase 1} / Consent & Enforcement Design: {Phase 2}.
  [규칙] 다음 공격면을 하나씩 검증한다 — (1) confused deputy: prompt injection(직접·간접·도구 매개)이 에이전트의 *합법 자격증명*
         으로 특권 도구를 대신 호출(ASI01 Goal Hijack→ASI03 Identity & Privilege Abuse); (2) 토큰 재생/passthrough: aud 바인딩
         부재로 한 리소스 토큰이 다른 곳에서 수용되거나 상류 토큰이 다운스트림으로 전달; (3) 과대/ambient 스코프: 여러 리소스에
         재생 가능한 광범위 토큰; (4) 무제한 위임 체인: may_act 권한 검사·hop별 스코프 narrowing 부재로 특권 누적/상승; (5)
         네트워크(또는 시스템 프롬프트)를 토큰 대신 신뢰; (6) 인프라 배포를 설계로 착각(리프레임 안티패턴). 각 공격면에 대해 모델이
         *어디서 버티고 어디서 무너지는지*를 Phase 0~2 설계 조항 인용으로 판정한다. 산출물은 *위협/red-team 분석*이지 통과하는
         라이브 배포가 아니다. "개선 N% 보장"을 쓰지 않는다 — 최소권한 설계도 스코프 내 injection엔 뚫릴 수 있음을 정직하게
         명시한다(런타임 레일 도메인과 합성 필요). 설계를 직접 수정하지 않는다(검증·권고만).
  [출력] Authorization Threat Analysis(공격면별 RESISTS/PARTIAL/FAILS + 설계 조항 인용·잔여 위험·런타임 레일 합성 권고·미상/가정·종합 판정).
  """
)
```

1줄 보고: `[Phase 3] 적대적 인가 검증 완료(종합 {RESISTS|PARTIAL|FAILS}) — 종합 보고로 마무리할까요?`

> **red-team은 위험을 줄이지 제거하지 않는다.** 완벽한 최소권한·audience-bound 설계도 *부여된 스코프 안에서* prompt
> injection으로 무기화될 수 있다(confused deputy) — 그래서 이 하네스는 런타임 콘텐츠·행동 레일 도메인을 *대체가 아니라
> 보완*한다. 잔여 위험을 은폐하지 말고 명시한다.

## 마무리 — 종합 보고

플로우가 끝나면 네 단계 산출물을 하나로 종합 보고한다.

- **신뢰·스코프 모델**: 역할별 참여자·authN vs authZ authority·도구/리소스/에이전트 인벤토리·상호작용별 최소 스코프·신뢰 경계.
- **그랜트·위임 설계**: hop별 단명 audience-bound 토큰·토큰 교환 위임(subject/actor/may_act)·경계별 fresh exchange·표준 그랜트.
- **동의·집행 설계**: authN/authZ 분리·deny-by-default·resource server별 audience 검증·민감 스코프 동의 게이트·감사 로깅.
- **위협 분석**: 공격면별 RESISTS/PARTIAL/FAILS + 설계 조항 인용·잔여 위험·런타임 레일 합성 권고.
- **남은 불확실성·가정**: 미상 항목·in-flux 표준(ID-JAG/MCP auth) 의존·벤더 선택 필요 지점·사람 판단 항목.

보고 형식(최종): `[Agent-Auth-Harness] 액터/스코프 {참여자·최소스코프} · 그랜트/위임 {단명 aud토큰·may_act} · 집행 {deny-by-default·audience검증·동의} · red-team {RESISTS|PARTIAL|FAILS}`

> 정직성: RFC 8707·RFC 8693·OWASP LLM06:2025은 published 근거(HIGH)로 인용했고, ID-JAG(draft-04)·MCP Authorization
> draft·A2A spec·OWASP Agentic(ASI01/ASI03)은 in-flux 초안(MEDIUM)으로 등급·명시했으며, 벤더(Okta XAA 등)는 예시일 뿐
> 필수가 아니고, "개선 N% 보장"을 쓰지 않는다. 상세는 research dossier 참조.
