# backend-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | backend-harness(실행 기반 검증 + 환경 1급 시민) 백엔드/API 구현 멀티 에이전트 하네스 + test-generator 스킬. 근거: arXiv:2510.04852·2505.09569·2505.07473·2512.06915[GOLD], TestART arXiv:2408.03095[SILVER] |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `backend-harness` 726자 → 456자 · `test-generator` 632자 → 374자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 673자 → 251자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 3,536자 → 1,605자 — `Structure`·`5단계 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
| 2026-11-08 | /doctor 전수 점검 — README 설치 줄 + 리스팅 아이콘 | (1) README `## 설치`에 원스텝 설치 줄 `/plugin install backend-harness --marketplace seungahhong/seungah-claude-plugins` + 2단계(marketplace add → install) 추가 — 기존 `claude plugin add`는 존재하지 않는 명령이라 교체. (2) 디렉터리 리스팅 아이콘 `.claude-plugin/icon.png`(1024×1024 PNG, 기존 frontend-harness·test-layering-harness 아이콘과 같은 톤: 네이비 그라데이션 + 밝은 도형 + #3D5AFE 포인트) 추가 — 기본 경로라 plugin.json `icon` 불필요. 기능 변경 없음·버전 유지 |
