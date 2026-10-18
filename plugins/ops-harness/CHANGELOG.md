# ops-harness 변경 이력

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-19 | 플러그인 신설 | ops-harness(프로덕션 운영·인시던트 대응·관측성) 멀티 에이전트 하네스. AIOpsLab 4단계(L1–L4) 오케스트레이션 + 4개 전문 에이전트(detector/localizer/root-cause-analyst/mitigation-planner). RCA anti-anchoring 가드레일·Straight-Shot 폴백, DQ 품질 게이트, 중재 읽기 액션·휴먼-인-더-루프. 근거: AIOpsLab(arXiv:2501.06706)[GOLD/SILVER]·역할분리 오케스트레이션(arXiv:2511.15755)[SILVER]·RCA 추론 실패모드(arXiv:2601.22208)[SILVER], CAVEAT 동반 |
| 2026-06-21 | 독립화 | 다른 플러그인 참조를 제거하고 경계/네비게이션 진술을 '이 하네스 범위 밖' 일반 표현으로 일반화해 단독 사용 가능하게 정리(plugin.json description·SKILL.md·README.md·CLAUDE.md). 범위/비범위 의미는 보존 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.1. (1) 스킬 description `ops-harness` 1,004자 → 538자 — 발동 문구와 범주 경계만 남기고 절차 서술은 본문에 맡김. (2) plugin.json description 780자 → 285자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 3,468자 → 1,382자 — `Structure`·`단계 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. 트리거 평가 재실행은 미수행 |
