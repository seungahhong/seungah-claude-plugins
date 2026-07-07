# review-harness

개발 착수 *전* 상류 산출물(기획·디자인·API 계약·QA 인수조건)을 **핸드오프 시점에 '착수 게이트'로 검수**하는 도메인 무관 멀티 에이전트 하네스. AI가 코드 작성을 자동화할수록 결함은 '작성'이 아니라 **상류 스펙 품질과 리뷰**로 이동한다는 전제에서 출발한다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
review-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                          # (이 문서) 하네스 포인터 + 게이트 요약 + 변경 이력
├── README.md                          # 사용자용 개요·사용법·도구 경계
├── commands/
│   └── handoff-review.md              # 오케스트레이터(진입점) — 해당 게이트 선택→병렬 실행→착수 준비도 통합 리포트
├── skills/
│   ├── dor-review/                    # 기획 산출물 착수 준비도(Definition of Ready) 게이트
│   ├── design-handoff-review/         # 디자인 핸드오프 사각지대(상태 누락·토큰·매핑) 게이트
│   ├── contract-review/               # API 계약(OpenAPI) 완결성·breaking change·소비자 커버리지 게이트
│   └── test-coverage-review/          # 인수조건↔테스트 커버리지·음성/엣지 시나리오 게이트
└── evals/
    └── trigger-eval.json              # 트리거 경계 평가(인접 도구와 reciprocal should-not 가드)
```

## 4개 게이트 요약

| 게이트 | 스킬 | 대상 산출물 | 핵심 점검 | PASS 의미 |
| --- | --- | --- | --- | --- |
| 기획 DoR | `dor-review` | PRD·유저스토리·인수조건·티켓 | DoR 게이트 · INVEST 스코어카드 · GWT 완결성 · 모호성 린트 · 의존성/계약 참조 | FE/BE/QA가 추측 없이 착수 가능 |
| 디자인 핸드오프 | `design-handoff-review` | Figma 프레임·스펙·토큰·Code Connect | 사각지대 커버리지(에러/로딩/빈/요소 상태) · 토큰 바인딩 · 컴포넌트↔코드 매핑 · 상태별 oracle | 디자이너 의도 추측 없이 구현 가능 |
| API 계약 | `contract-review` | OpenAPI/스키마·Pact | 엔드포인트 완결성 · breaking-change diff · 소비자(CDC) 커버리지 · 코드↔spec drift | FE가 계약만 보고 mock 병렬 착수 가능 |
| 테스트 커버리지 | `test-coverage-review` | 인수조건↔테스트(Gherkin/feature) | 인수조건 테스트가능성 · AC↔테스트 매핑 · 커버리지 채점 · 누락 시나리오 발굴 | 인수조건이 실행가능 스펙으로 정의됨 |

오케스트레이터 `handoff-review`는 넘어온 산출물에 해당하는 게이트를 선택받아 **병렬 실행**하고, 게이트별 판정을 **착수 준비도(Readiness) 통합 리포트**로 묶는다. 하나라도 Blocker(착수 차단/BLOCKED)면 종합은 착수 보류로 시작한다.

## Conventions

- **상류 산출물 게이트**: 이 하네스는 *코드가 아니라* 코드 착수 전 상류 산출물을 핸드오프 시점에 검수한다. 완성된 코드 리뷰, PRD·스토리 *작성*, 커밋/PR 리뷰는 이 하네스의 범위 밖이며 별도 워크플로로 처리한다.
- **읽기 위주**: 게이트 스킬은 산출물(PRD/디자인/계약/AC)을 직접 수정하지 않는다(`allowed-tools`에 Edit/Write 없음). 보강 항목은 구체적으로 제시하되 합의·수정은 해당 팀이 한다.
- **Honesty Guardrail (전 스킬 공통)**: 정량 수치는 검증된 근거만 등급(GOLD/SILVER/BRONZE)·출처와 함께 인용한다. '개선 N%'를 약속하지 않고 효과는 조직이 baseline으로 측정한다(baseline-before-target). 출처 추적 실패·반증된 수치(IBM 1→100배, NIST 'Example Only' 표, Code Connect 85~90% 등)는 사실로 인용하지 않고 '신화'로만 표기한다.
- **2025+ 근거 우선**: 각 스킬의 '참고/근거'는 2025년 이후 동료심사/학회/arXiv 근거를 우선하고, 인용한 수치는 실재·연도·venue를 확인해 적는다. preprint·벤더 자기보고·소표본은 caveat로 명시한다.
- **disable-model-invocation**: 게이트 스킬은 모델 자동 발동을 끄고 `/dor-review` 등으로 명시 호출하거나 `handoff-review` 오케스트레이터가 spawn한다.
- **트리거 가드**: 새 트리거 표현 변경 시 인접 도구(코드 리뷰·PRD 작성 등)와의 경계 케이스와 reciprocal하게 `evals/trigger-eval.json`을 갱신한다.

## Change History

| 날짜 | 변경 | 내용 |
| --- | --- | --- |
| 2026-06-15 | 플러그인 신설 | 상류 산출물(기획·디자인·계약·QA) 핸드오프 게이트 4개 스킬 + `handoff-review` 오케스트레이터 등록 |
| 2026-06-15 | 2025+ 근거 재작성 | 4개 스킬의 '핵심 원칙'·'참고/근거'를 검증된 2025+ 논문 근거로 재정렬(적대적 인용 검증 후 반영) |
| 2026-06-21 | 독립화 | 다른 플러그인 참조·경로를 제거하고 경계 진술을 일반 개념으로 일반화해 단독 사용 가능하게 정리 |
| 2026-07-07 | 컨벤션 정합 (v0.1.1) | handoff-review 오케스트레이터의 Agent spawn에 `model: "opus"` 명시(마켓플레이스 컨벤션 — 레포 내 유일한 누락 오케스트레이터였음) + 게이트 스킬 경로를 커맨드 파일 기준 상대 경로(`../skills/...`)로 정정 |
