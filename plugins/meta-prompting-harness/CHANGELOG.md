# meta-prompting-harness 변경 이력

- **v0.1.0** (2026-07-21) 신설. 메타 프롬프팅 실천 방법론을 `/deep-research`(6각도·25소스·23 confirmed/2 refuted)로 1차 문헌 대조·근거 등급 부여. 4에이전트(opus)·references 3종·evals.
- **v0.1.1** (2026-07-21) 사용자 요청: 사용자에게 문의 시 **덤프로 한꺼번에 묻지 않고 한 번에 한 질문씩 단계별**로 정리. Phase 0 인테이크를 목표→환경 순 한 질문씩 확정으로, 컨텍스트 덤핑은 *강요*에서 *선택지*(있으면 붙여넣기)로 완화. Phase 1 context-elicitor를 '번호 질문 한 화면 몰아 노출'에서 **중요도 순 질문 계획 → 오케스트레이터가 한 번에 하나씩·번호 선택지·직전 답이 다음 질문 결정**으로 재작성(수십 개 한꺼번에 노출 제거). 내재화 원칙에 '한 번에 한 질문' 불변식 추가. carving-principles 원칙 1·2·핵심 프로세스·description·root/docs 정합. 근거상으로도 명확화 질문(T2 STRONG)에 부합하고 덤핑(T1 조건부·관행)은 선택으로 남김.
- **v0.1.2** (2026-10-18) /doctor 점검: (1) 스킬 description 유지(`meta-prompting` 605자) — 이미 600자 이하. (2) plugin.json description 1,644자 → 245자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 2,947자 → 1,170자 — `Structure`·`4 Phase`·`근거 등급 (정직성 핵심)`·`경계` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관, 절대 규칙·경계는 Conventions로 승격. 트리거 평가 재실행은 미수행
