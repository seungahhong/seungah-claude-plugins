# human-agent-teaming 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | 사람↔에이전트 협업 설계(분업·위임→공통기반→감독·신뢰→검증·지속) 하네스. Anthropic 'Building Effective Human-Agent Teams' 블로그 정독 + deep-research 3-vote 적대 검증(26 소스·130 주장·24 confirmed/1 refuted) 근거. 1차: Anthropic HAT 블로그·Building Effective Agents·safe-agents 프레임워크·Measuring Agent Autonomy·long-running-agents + arXiv:2504.10918·2602.05987 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `human-agent-teaming` 1,115자 → 549자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 1,523자 → 292자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 4,007자 → 1,836자 — `Structure`·`Phase 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
