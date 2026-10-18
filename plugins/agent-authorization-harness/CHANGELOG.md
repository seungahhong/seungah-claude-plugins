# agent-authorization-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | 에이전트/MCP 도구/A2A 시스템의 머신 아이덴티티·인가 모델을 벤더 무관하게 설계·red-team하는 하네스. LY Corporation Tech-Verse 2026 S07 "ID-JAG: The Enterprise-Ready Standard for AI Agent Authorization in the MCP and A2A Era" 세션에서 *배포 사례(Keycloak/Athenz/MCP 데모)* 가 아니라 *이전 가능한 설계 규율*을 추출해 접지. 1차 근거(discipline HIGH): published RFC 8707(Resource Indicators)·RFC 8693(Token Exchange)·OWASP LLM06:2025(Excessive Agency). framing(MEDIUM, in-flux): ID-JAG draft-ietf-oauth-identity-assertion-authz-grant-04·MCP Authorization draft·A2A spec·OWASP Agentic ASI01/ASI03. 벤더(Okta XAA)·LY blog/deck은 illustrative, AIP arXiv:2603.24775는 academic 보강. "개선 N% 보장" 금지·스코프 내 injection은 런타임 레일과 합성 명시. |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `agent-authorization-harness` 1,340자 → 546자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 2,575자 → 352자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 5,182자 → 2,404자 — `Structure`·`Phase 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
