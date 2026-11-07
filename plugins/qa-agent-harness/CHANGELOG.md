# qa-agent-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | 리스크 기반 전략→오라클 명시 시나리오→오라클 우선 생성·게이트된 자가치유 실행→결함 vs 플래키 지능형 트리아지의 독립 end-to-end 에이전틱 QA 하네스. Tech-Verse 2026 S06 "10x Speed With QA Agent Platform" 세션의 harnessable core만 추출(조직 도입·성숙도 모델·변경관리 층은 제외). 1차 근거: arXiv:2601.02454(Agentic Testing)·arXiv:2506.02943(CANDOR)·arXiv:2606.18168(All Smoke, No Alarm)·arXiv:2504.16777(Systemic Flakiness), 보강: arXiv:2601.05542(LLM 오라클)·Requirements-based test prioritization 산업연구·Katalon Agentic QA 운영모델 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `qa-agent-harness` 1,286자 → 557자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 2,293자 → 273자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 4,342자 → 2,089자 — `Structure`·`Phase 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
| 2026-11-08 | /doctor 전수 점검 — README 설치 줄 + 리스팅 아이콘 | (1) README `## 설치`에 원스텝 설치 줄 `/plugin install qa-agent-harness --marketplace seungahhong/seungah-claude-plugins` + 2단계(marketplace add → install) 추가 — 기존 `claude plugin add`는 존재하지 않는 명령이라 교체. (2) 디렉터리 리스팅 아이콘 `.claude-plugin/icon.png`(1024×1024 PNG, 기존 frontend-harness·test-layering-harness 아이콘과 같은 톤: 네이비 그라데이션 + 밝은 도형 + #3D5AFE 포인트) 추가 — 기본 경로라 plugin.json `icon` 불필요. 기능 변경 없음·버전 유지 |
