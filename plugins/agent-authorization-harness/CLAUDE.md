# agent-authorization-harness

에이전트가 다른 **에이전트·MCP 도구·A2A 시스템을 만들거나 배선할 때**, 그 *행동 아래*에 깔린 **머신 아이덴티티·인가
(authorization) 아키텍처를 벤더 무관하게 설계하고 적대적으로 red-team**하는 도메인 무관 멀티 에이전트 하네스.
핵심 메시지는 **"누가·어떤 스코프로·누구를 대신해 접근하는가를 토큰·스코프·`aud`·동의·위임 체인으로 설계하고,
confused-deputy·토큰 재생·스코프 크리프·무제한 위임을 적대적으로 검증한다 — 인가는 LLM이 아니라 외부 시스템에서
deny-by-default로 일어난다"** 이다. 산출물은 *인가 설계 + 위협 분석*(advisory + 설계 산출물)이지 특정 IdP/PDP 배포가 아니다.
근거: **published RFC 8707(Resource Indicators)·RFC 8693(Token Exchange)·OWASP LLM06:2025(Excessive Agency)**(discipline HIGH)
+ **ID-JAG draft-04·MCP Authorization draft·A2A spec·OWASP Agentic ASI01/ASI03**(framing MEDIUM, in-flux).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
agent-authorization-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                              # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                             # 사용자용 개요·언제 쓰나·4단계 사용법·도구 경계·근거 자료
├── agents/                               # 모두 model: "opus"
│   ├── trust-scope-modeler.md            # Phase 0 — 참여자·authN vs authZ authority·접촉면 인벤토리·최소 스코프·신뢰 경계
│   ├── grant-delegation-designer.md      # Phase 1 — 단명 audience-bound 토큰(RFC 8707)·토큰 교환 위임(RFC 8693 may_act)·no passthrough
│   ├── consent-enforcement-designer.md   # Phase 2 — 인증/인가 분리·deny-by-default·동의 게이트·end-to-end audience 검증·감사 로깅
│   └── authorization-redteamer.md        # Phase 3 — confused-deputy·토큰재생·스코프크리프·무제한위임 적대 검증·위협 분석
├── skills/
│   └── agent-authorization-harness/
│       ├── SKILL.md                      # 오케스트레이터(진입점, Phase 0 모델링 게이트 → 그랜트·위임 → 집행 → red-team)
│       └── references/
│           ├── agent-authorization-harness-principles.md   # 원칙·anti-pattern·결정 신호표
│           └── agent-authorization-harness-research.md      # 설계 근거 deep-research dossier(출처·인용·신뢰도 등급·CAVEAT·정직성·방법론)
└── evals/
    ├── evals.json                        # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json                 # 트리거 경계 평가(should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 신뢰·스코프 모델링 (Trust & Scope Modeling) | trust-scope-modeler | Actor & Scope Model(역할별 참여자·authN vs authZ·접촉면 인벤토리·최소 스코프·신뢰 경계) | 승인 게이트 |
| 1 | 그랜트·위임 설계 (Grant & Delegation Design) | grant-delegation-designer | Grant & Delegation Design(단명 aud 토큰·토큰 교환 위임·경계별 fresh exchange·표준 그랜트) | 1줄 보고 |
| 2 | 동의·집행 설계 (Consent & Enforcement Design) | consent-enforcement-designer | Consent & Enforcement Design(authN/authZ 분리·deny-by-default·audience 검증·동의 게이트·감사) | 민감 스코프 동의 게이트 / 1줄 보고 |
| 3 | 적대적 인가 검증 (Adversarial Authorization Verification) | authorization-redteamer | Authorization Threat Analysis(공격면별 RESISTS/PARTIAL/FAILS·잔여 위험·런타임 레일 합성 권고) | 1줄 보고 |

최종 보고: `[Agent-Auth-Harness] 액터/스코프 {참여자·최소스코프} · 그랜트/위임 {단명 aud토큰·may_act} · 집행 {deny-by-default·audience검증·동의} · red-team {RESISTS|PARTIAL|FAILS}`

## Conventions

- **머신 아이덴티티·인가 = 행동 아래 층**: 접근 근거로 네트워크·공유 키·LLM 판단을 신뢰하지 않는다. 누가·어떤 스코프로·누구를 대신해를 토큰·스코프·`aud`·동의·위임으로 설계한다.
- **최소 권한**: 과대 기능·과대 권한·과대 자율(OWASP LLM06)을 태깅하고 상호작용별 최소 스코프만 배정한다.
- **단명·audience-bound 토큰**: 장수 공유 자격증명 대신 단명·좁은 스코프·`aud` 제한 토큰(RFC 8707). 모든 resource server가 `aud`≠자기 URI면 거부(end-to-end).
- **표준 on-behalf-of 위임**: RFC 8693 토큰 교환(`subject_token`/`actor_token`/`may_act`), 매 신뢰 경계 fresh exchange, 상류 토큰 no passthrough.
- **인증 ≠ 인가**: IdP는 누구인가, 별개 PDP/resource server가 허가되는가. 인가를 LLM에 위임하지 않는다(외부 시스템에서).
- **deny-by-default + 동의 + 감사**: 명시 허용 없으면 거부, 민감/비가역 스코프는 사람 동의 게이트, 모든 인가 결정 로깅(재구성 가능).
- **표준 준수 > 자체 구현**: OAuth 2.1·RFC 8707·RFC 8693·RFC 9728·PKCE·ID-JAG 크로스앱 우선. 특정 벤더/IdP는 구현 세부.
- **설계 + red-team이 산출물(배포 아님)**: Keycloak/Athenz/Kubernetes를 세우는 것은 인프라 작업으로 범위 밖. 벤더는 illustrative일 뿐 필수 아님.
- **정직성·falsifiability**: RFC 8707·8693·LLM06은 published(HIGH), ID-JAG/MCP auth/A2A/OWASP Agentic은 in-flux 초안(MEDIUM)으로 등급·명시. "개선 N% 보장" 금지 — red-team은 위험을 줄이지 제거하지 않는다.
- **런타임 레일과 합성(대체 아님)**: 최소권한 설계도 스코프 내 prompt injection엔 뚫릴 수 있어(confused deputy) 런타임 콘텐츠·행동 레일 도메인과 합성한다.
- **승인 게이트·관찰성**: Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: 런타임 콘텐츠·행동 레일 집행·사람↔에이전트 업무 분업·파이프라인 인프라 policy-as-code·코딩 에이전트 자신 권한·일반 API 구현·장애 RCA·상류 핸드오프 검수·출력 채점·병렬화 결정·특정 IdP 배포는 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 다른 마켓플레이스 플러그인에 의존하지 않는 독립 플러그인이다(경계의 형제 플러그인명은 변별용으로만 명시).

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | 에이전트/MCP 도구/A2A 시스템의 머신 아이덴티티·인가 모델을 벤더 무관하게 설계·red-team하는 하네스. LY Corporation Tech-Verse 2026 S07 "ID-JAG: The Enterprise-Ready Standard for AI Agent Authorization in the MCP and A2A Era" 세션에서 *배포 사례(Keycloak/Athenz/MCP 데모)* 가 아니라 *이전 가능한 설계 규율*을 추출해 접지. 1차 근거(discipline HIGH): published RFC 8707(Resource Indicators)·RFC 8693(Token Exchange)·OWASP LLM06:2025(Excessive Agency). framing(MEDIUM, in-flux): ID-JAG draft-ietf-oauth-identity-assertion-authz-grant-04·MCP Authorization draft·A2A spec·OWASP Agentic ASI01/ASI03. 벤더(Okta XAA)·LY blog/deck은 illustrative, AIP arXiv:2603.24775는 academic 보강. "개선 N% 보장" 금지·스코프 내 injection은 런타임 레일과 합성 명시. |
