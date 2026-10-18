# cicd-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | cicd-harness(코드 커밋→프로덕션 전달 파이프라인) CI/CD·DevOps·릴리스·IaC 멀티 에이전트 하네스. 4단계(CI 파이프라인 → IaC·환경 → 릴리스·배포 결정 → 전달 안정성 가드) 오케스트레이션 + 4개 전문 에이전트(pipeline-architect/iac-reviewer/release-gatekeeper/delivery-verifier). defense-in-depth(읽기전용·사람 사전승인), policy-as-code 결정론적 게이트(terraform plan + OPA), trust-tier 단계적 자율, DORA 통제 프레이밍. 근거: DORA 2025[GOLD]·DORA AI Capabilities Model[GOLD]·AI-Augmented CI/CD(arXiv:2508.11867)[SILVER]·GitHub Agentic Workflows[SILVER]·MACOG(arXiv:2510.03902)[SILVER], CAVEAT·DORA 반증 nuance 동반 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `cicd-harness` 974자 → 554자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 1,005자 → 311자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 4,188자 → 1,887자 — `Structure`·`4단계 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
