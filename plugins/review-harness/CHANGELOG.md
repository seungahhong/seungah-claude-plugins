# review-harness 변경 이력

| 날짜 | 변경 | 내용 |
| --- | --- | --- |
| 2026-06-15 | 플러그인 신설 | 상류 산출물(기획·디자인·계약·QA) 핸드오프 게이트 4개 스킬 + `handoff-review` 오케스트레이터 등록 |
| 2026-06-15 | 2025+ 근거 재작성 | 4개 스킬의 '핵심 원칙'·'참고/근거'를 검증된 2025+ 논문 근거로 재정렬(적대적 인용 검증 후 반영) |
| 2026-06-21 | 독립화 | 다른 플러그인 참조·경로를 제거하고 경계 진술을 일반 개념으로 일반화해 단독 사용 가능하게 정리 |
| 2026-07-07 | 컨벤션 정합 (v0.1.1) | handoff-review 오케스트레이터의 Agent spawn에 `model: "opus"` 명시(마켓플레이스 컨벤션 — 레포 내 유일한 누락 오케스트레이터였음) + 게이트 스킬 경로를 커맨드 파일 기준 상대 경로(`../skills/...`)로 정정 |
| 2026-10-18 | **/doctor 점검 — 설명 축약·CLAUDE.md 경량화** | v0.1.2. (1) 스킬 description 유지(`contract-review` 369자 · `design-handoff-review` 347자 · `dor-review` 356자 · `test-coverage-review` 360자) — `disable-model-invocation`이라 모델 목록에 상주하지 않음. (2) plugin.json description 538자 → 339자, marketplace.json 항목을 같은 문구로 통일, 미사용 `tags` 제거. (3) 플러그인 CLAUDE.md 3,118자 → 1,282자 — `Structure`·`4개 게이트 요약` 절 삭제(SKILL.md·references·README가 정본), 변경 이력은 이 파일로 이관. (4) allowed-tools를 본문이 실제로 쓰는 명령으로 한정: `skills/contract-review/SKILL.md` → `Bash(find:*), Bash(grep:*), Read, Grep, Glob` · `skills/dor-review/SKILL.md` → `Bash(find:*), Bash(grep:*), Read, Grep, Glob` · `skills/test-coverage-review/SKILL.md` → `Bash(grep:*), Bash(git ls-files:*), Read, Grep, Glob` · `skills/design-handoff-review/SKILL.md` → `Read, Grep, Glob` · `commands/handoff-review.md` → `Bash(find:*), Bash(grep:*), Bash(git ls-files:*), Read, Grep, Glob, Agent`. 트리거 평가 재실행은 미수행 |
| 2026-11-08 | /doctor 전수 점검 — README 설치 줄 + 리스팅 아이콘 | (1) README `## 설치`에 원스텝 설치 줄 `/plugin install review-harness --marketplace seungahhong/seungah-claude-plugins` + 2단계(marketplace add → install) 추가 — 기존 `claude plugin add`는 존재하지 않는 명령이라 교체. (2) 디렉터리 리스팅 아이콘 `.claude-plugin/icon.png`(1024×1024 PNG, 기존 frontend-harness·test-layering-harness 아이콘과 같은 톤: 네이비 그라데이션 + 밝은 도형 + #3D5AFE 포인트) 추가 — 기본 경로라 plugin.json `icon` 불필요. 기능 변경 없음·버전 유지 |
