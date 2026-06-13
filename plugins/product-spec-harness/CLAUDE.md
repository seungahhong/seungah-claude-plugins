# product-spec-harness

기획자(PM)가 요구·문제로부터 **제품 기획문서(PRD)와 사용자 스토리**를 4단계 인터랙티브로 작성·검증하는 도메인 무관 멀티 에이전트 하네스 (개발 착수 *전* 단계).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
product-spec-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                      # (이 문서) 하네스 포인터 + 4단계 요약 + 변경 이력
├── README.md                      # 사용자용 개요·사용법·도구 경계
├── agents/
│   ├── requirements-analyst.md    # Phase 0 요구/문제/사용자 정의
│   ├── prd-writer.md              # Phase 1 기획문서(PRD) 작성
│   ├── story-writer.md            # Phase 2 사용자 스토리 + 수용기준
│   └── spec-reviewer.md           # Phase 3 적대적 검증
├── skills/
│   └── product-spec/
│       ├── SKILL.md               # 오케스트레이터(진입점, 4 Phase 인터랙티브)
│       └── references/
│           ├── prd-template.md        # PRD 표준 구조 + 작성기준
│           └── user-story-guide.md    # As a/I want/so that + Gherkin + INVEST
└── evals/
    └── trigger-eval.json
```

## 4단계 Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 요구/문제 정의 (Discovery) | requirements-analyst | 문제 정의 카드 (problem / target_users / goals / constraints / success_metrics) | 한 번에 1질문 인터뷰 → 승인 |
| 1 | 기획문서(PRD) 작성 | prd-writer | PRD (배경·문제 / 목표·성공지표 / 범위 In·Out / 핵심 요구사항(기능·비기능) / 가정·리스크 / 마일스톤) | 쓰기 전 미리보기 승인 |
| 2 | 사용자 스토리 도출 | story-writer | 스토리("…로서 …하고 싶다, 왜냐하면 …") + 수용기준(Given/When/Then) + INVEST 자가점검 | 승인 |
| 3 | 검증 | spec-reviewer | 검증 리포트 (요구↔스토리 추적 매트릭스 / INVEST / 수용기준 관찰성 / 일관성 / 모호·판정불가 색출) | 검증 리포트 + 승인 (보완 시 additive-first) |

매 Phase 종료 시 보고 형식: `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?`

## Conventions

- **승인 게이트**: 매 Phase 종료 시 핵심 산출물 + 1줄 보고를 제시하고, 파일을 쓰기 전 미리보기로 사용자 승인을 받은 뒤에만 진행한다.
- **관찰형 수용기준**: 사용자 스토리 수용기준과 success_metrics는 제3자가 관찰로 판정 가능한 Given/When/Then으로 작성한다. "좋다/만족" 같은 판정불가 문장 금지.
- **완전성·추적**: 모든 PRD 핵심 요구가 ≥1개 스토리로 커버되는지 요구↔스토리 매트릭스로 추적한다.
- **적대적 검증**: Phase 3는 칭찬형 금지 — 누락·모호·비일관을 능동적으로 캔다.
- **additive-first**: 합의된 PRD/스토리를 보완할 때 기존 항목을 뒤엎기 전에 비파괴 추가·완화를 먼저 제안한다.
- **인터뷰성**: 한 번에 한 질문. jargon은 1줄 정의를 곁들인다.
- **경계**: 이 하네스는 '기획자의 제품 기획(도메인 무관, 개발 전)'이다. 프론트엔드 개발용 PRD·구현 요구사항·코드 작성(frontend-harness의 prd/planner 영역)이나 코드/하네스/커밋 작업은 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-13 | 플러그인 신설 | 기획자용 기획문서·사용자스토리 4단계 인터랙티브 하네스 |
