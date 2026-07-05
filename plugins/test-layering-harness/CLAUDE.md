# test-layering-harness

인수조건(AC, Given-When-Then)을 **방법론(Smoke/Sanity/Regression/nightly) × 계층(Unit/Integration/E2E)** 택소노미로 계층별 테스트 스위트로 계획하고, **계획→개별→최종 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정하는 도메인 무관 인터랙티브 **단일 스킬** 독립 플러그인.

사용자용 개요·사용법은 [README.md](README.md), 원리는 [principles](skills/test-layering-harness/references/test-layering-principles.md), 근거는 [research dossier](skills/test-layering-harness/references/research/test-strategy-research.md) 참조.

## Structure

```
test-layering-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 원칙 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·경계
├── skills/test-layering-harness/
│   ├── SKILL.md                     # 오케스트레이터(Phase 0 초기문의 → 1 적응형 구성 → 2 계획+게이트A → 3 개별 적용+게이트B → 4 반영+게이트C)
│   └── references/
│       ├── test-layering-principles.md   # 방법론×계층 매트릭스·AC 분해 규칙·오라클 가드·3 프리셋·감지 신호·anti-pattern·경계
│       └── research/
│           └── test-strategy-research.md # 2025+ 근거 dossier(A~G, 신뢰도·folklore·모순 표기)
└── evals/
    ├── evals.json                   # 수용 평가(핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json            # 트리거 경계(should/should-not, 인접 하네스 reciprocal 가드)
```

## 5-Phase · 3-Gate 요약

| Phase | 내용 | 게이트 |
|-------|------|--------|
| 0 초기 문의 | AC **3지선다 명시 프롬프트**((a)붙여넣기 (b)파일·링크 경로 (c)없음→저장소 후보 채굴; 채굴은 사용자 명시 선택·곧장 건너뛰기 금지) · 개발 환경(스킵 가능·미입력 시 현재 경로·부재 러너 보고) | — |
| 1 적응형 구성 | 저장소 감지 → 3 프리셋 중 근거와 함께 추천 → **방법론 스위트(Smoke/Sanity/Regression/nightly)·계층(Unit/Integration/E2E) 체크박스 다중선택**(프리셋 기본체크·러너 부재 계층 '추가 필요' 명시) → 스코프 고정 | (스코프 확정) |
| 2 AC→계획 | AC를 tier로 분해(GWT→AAA)·오라클 부착·계획표 | **게이트 A: 계획 승인** |
| 3 개별 적용 | 오라클 오검증·draft 제시·적용·실행 그라운딩 (순차) | **게이트 B: 개별 적용 승인** |
| 4 반영 | 적용 요약·전체 실행·확정 | **게이트 C: 최종 반영 재확인** |

## Conventions (핵심 불변식)

- **3개 게이트를 건너뛰지 않는다** — 계획 승인 없이 개별 적용 없음, 개별 승인 없이 파일 쓰기 없음, 최종 승인 없이 반영 없음.
- **비율% 하드코딩 금지** — 70/20/10은 folklore(Fowler 본인 상대화). 무게중심은 프리셋으로 제안, 비율은 안 박음.
- **오라클 강도가 최대 리스크** — LLM은 구현(실제 동작)을 굳혀 버그를 초록으로 은폐. 기대(AC) 기준 오검증 + 실행 그라운딩 + flaky baseline 선결 + 스모크/동어반복 어서션 금지.
- **AC ≠ E2E** — AC 한 건은 여러 tier로 분해. E2E는 핵심 여정 소수로 절제(ice-cream-cone 방지).
- **정직성** — smoke=sanity ISTQB 동의어 caveat 병기, 근거 없는 효과 수치 인용 금지, 신뢰도(HIGH/MED/LOW)·모순·folklore 표기 계승.
- **적응형 추천** — 저장소 감지로 프리셋 추천 후 사용자 확정(고정 강제 아님).
- **CI 배치 원리** — tier는 파이프라인 뒤로 갈수록 넓어짐(Google presubmit/postsubmit·Fowler DeploymentPipeline). 선택·배치 > 우선순위. unknown 커밋엔 전체 폴백.
- **커밋 직접 안 함** — 최종 반영은 유지·정리까지, 커밋/PR은 git-harness로 핸드오프 제안만.
- 단일 스킬 플러그인이므로 에이전트 팀(agents/)을 두지 않는다 — 인터랙티브 오케스트레이터 본성에 충실.
- **경계**: 리스크 기반 오라클·자가치유·트리아지 QA(qa-agent-harness), 백엔드 실행기반 test-generator(backend-harness), AC↔테스트 커버리지 읽기전용 검수(review-harness/test-coverage-review), FE 흐름 내 TDD(frontend-harness), 실행 명세 작성(spec-driven-development), 커밋/PR(git-harness)은 범위 밖.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-05 | 플러그인 신설 (v0.1.0) | test-layering-harness(AC→방법론×계층 택소노미 테스트 계획·3게이트 순차 적용). deep-research(plain-text fan-out 5각도 적대 검증, 내장 deep-research schema 즉사 회피)의 2025+ 근거로 설계 — 방법론 스코프·트리거·CI 배치(ISTQB·Fowler·CircleCI·Google), 계층 비율 folklore 정직성(Fowler·Dodds·web.dev), 방법론×계층 매트릭스(Google presubmit/postsubmit·Fowler DeploymentPipeline), AC→tier 분해(GWT→AAA), LLM 생성 오라클 강도 최대 리스크(arXiv:2410.21136·2601.05542·2504.07244·2601.08998), flaky systemic 클러스터·선택>우선순위 CI 비용(arXiv:2504.16777·Meta). 적응형 3 프리셋(Trophy-lean/Google-pipeline/Contract-honeycomb)·비율 미하드코딩·3 승인 게이트·오라클 오검증+실행 그라운딩. 측정·제안·게이트만·자동 커밋 없음. |
| 2026-07-05 | Phase 0 개선 | 라이브 실행(seungahhong.github.io)에서 드러난 편차(실행자가 사용자 문의 생략 후 곧장 저장소 후보 채굴로 진행) 수정 — **Phase 0 AC 입력을 3지선다 명시 프롬프트로 못박음**((a)붙여넣기 (b)파일·링크 경로 (c)없음→저장소 후보 채굴; 채굴(c)은 묵시적 기본값이 아니라 사용자가 명시적으로 고른 선택, 최초 요청에 AC 인라인이면 재질문 금지). 개발 환경 항목도 부재 러너 보고를 명시(Phase 1 프리셋·tier 선택 반영). evals 초기문의 assertion 2건으로 분리(ac-3choice·env-skippable). |
| 2026-07-05 | Phase 1 개선 | **방법론×계층 체크박스 다중선택 동선 추가** — 프리셋 추천 뒤 Smoke/Sanity/Regression/nightly 방법론 스위트와 Unit/Integration/E2E 계층을 각각 `AskUserQuestion` multiSelect(체크박스)로 제시(프리셋 기준 기본체크, 사용자 가감), 러너 부재 계층은 '추가 필요' 명시, smoke=sanity ISTQB 동의어 caveat 병기, 선택된 스위트×계층만 Phase 2 계획 스코프로 고정. evals에 methodology-tier/multiselect assertion 추가. (실행계획 표시→승인 게이트는 이미 Phase 2 게이트 A로 존재.) |
