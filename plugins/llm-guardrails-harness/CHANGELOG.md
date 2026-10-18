# llm-guardrails-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | LLM I/O·tool 호출을 외부·인라인 제어 평면으로 런타임 강제하는 방어심층 가드레일 하네스(Phase 0 위협모델·정책 → Phase 1 입력 레일 → Phase 2 출력·검색 레일 → Phase 3 행동 강제·적대 검증). Tech-Verse 2026 S04 "Beyond Intelligence to Safety: External AI Guardrails" 세션의 전이 가능한 코어(레일 taxonomy+OWASP 매핑+외부강제 원칙)를 일반화하고, 1차 근거 OWASP Top 10 for LLM Applications 2025 · NVIDIA NeMo Guardrails(5 rail types) · Llama Guard(arXiv:2312.06674) · SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597) · OWASP LLM Prompt Injection Prevention Cheat Sheet · Adaptive Evaluation of Out-of-Band Defenses(arXiv:2606.26479)를 직접 인용. 사내 게이트웨이 구현 비귀속·보편 ASR/FPR·개선 N% 미주장 정직성 가드 포함 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `llm-guardrails-harness` 1,369자 → 505자(`: ` 제거로 strict YAML도 통과) — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 2,662자 → 309자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 4,834자 → 2,293자 — `Structure`·`Phase 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
