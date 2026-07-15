# AI Accessibility Playbook — Track B 안전 개선 (Step B2)

지표별 개입·메커니즘·안전장치의 정본. 원칙: **build enforces, docs explain** — 가능하면 산문 규칙이 아니라 lint/CI 강제로. 개선은 **계획→개별→검증** 승인 게이트 뒤에만·**커밋 안 함**.

## 개선 순서 (build enforces 우선)

| 순서 | 지표 | 개입 | 유형 | 위험 | 메커니즘 |
|------|------|------|------|------|----------|
| 1 | M1 의존 방향 강제 | 가드레일 설정 추가 + CI 배선 | SCORED | 중 | 설정 추가·빌드 통과 확인 |
| 2 | M2 독립 실행 | 러너·격리 슬라이스·독립 oracle | SCORED | 중 | 러너 도입·behavior 센서 |
| 3 | M3 빌드 피드백 | strict·typecheck·CI 게이트 | report-only | 낮음 | 설정 강화·opt-in |
| 4 | M4 모듈 경계 | 관례 택소노미 재배치 | report-only | 중 | AST/LSP·행위 센서·opt-in |
| 5 | M6 에이전트 가이드 | non-inferable 내용 사람 작성 | report-only | 낮음 | 사람 큐레이션(자동 생성 금지) |

## 지표별 상세

### 1. M1 의존성 방향 강제 — 허용 안 된 의존을 물리 차단
- **도구(택1 이상)**: `.dependency-cruiser.js` forbidden 규칙 · eslint `no-restricted-imports`/eslint-plugin-boundaries · import-linter contracts(`.importlinter`) · TypeScript project references · Nx `depConstraints` · ArchUnit(java/kotlin/csharp 테스트).
- **CI 배선**: 설정만으론 부족 — pre-commit/CI에서 **nonzero-exit로 fail**해야 실제 강제다. "설정 존재 ≠ 실제 강제."
- **핵심 안전장치**: 설정 추가 후 **빌드가 여전히 통과하는지** 확인. 기존 코드가 새 규칙에 걸리면 **hard-break 금지** — 위반 목록을 보고하고 범위를 협의한다(규칙 좁히기·기존 위반 baseline·점진 적용).
- **정직성**: 강제가 에이전트 아키텍처 위반율을 낮춘다는 통제 개입 근거는 **없다**(inferred). 존재·실제 fail만 사실. LocAgent 92.7%를 build-time blocking의 공으로 귀속 금지(다른 메커니즘=구조 가시성).

### 2. M2 독립 실행 가능성 — runnable + 독립 oracle
- **runnability gate**: 테스트 러너 도입, 워크스페이스/패키지 분리, port/adapter로 부분 실행 가능화.
- **독립 oracle(핵심)**: 에이전트가 **스스로 작성/선택한 테스트가 아니라** 사양·기대(ground truth) 기준의 독립 검증을 둔다. 격리-green을 correctness로 credit하지 않는다 — 실패의 81~100%가 self-validated green(arXiv:2606.26978).
- **주의**: over-mocking은 격리-green·통합-fail blind spot. fine-grained modularity/DI/hermeticity → agent self-verify 향상은 CI/human best-practice에서의 **추론**(agent 개입 미검증) → report-only.

### 3. M3 빌드 피드백 품질 — opt-in·저가중
- tsconfig `strict`/`noImplicitAny`/`strictNullChecks` 승격, `typecheck`(tsc --noEmit)/mypy/pyright, lint, CI 게이트.
- **정직성**: 정밀·조기 진단이 self-repair를 돕는다는 task-level MEDIUM 근거(arXiv:2306.09896·2602.11481)이나, "주어진 repo에 strong typing이 에이전트 editability를 높인다"는 repo-level 개입 부재(WEAK). **테스트/컴파일 통과를 correctness로 credit 금지**(ImpossibleBench: 76% exploit)·tamper-resistance(hidden/read-only 테스트) 별도 확인.

### 4. M4 모듈 경계 예측 가능성 — report-only·opt-in
- components/services/utils/domain/adapters/ports 등 관례 경계로 이동 제안(AST/LSP 위임·행위 센서).
- **정직성**: code localization은 확립된 어려운 병목(STRONG)이나 그 이득은 **툴 그래프 인덱스**의 것이지 layout 자체가 인과 레버라는 근거는 WEAK. **over-fragmentation(many-tiny-modules)은 오히려 해로울 수 있음**(over-tooling analogue). 강권하지 않는다.

### 5. M6 에이전트 가이드 — 사람 큐레이션·자동 생성 금지
- **넣을 것**: 코드로 알 수 없는(**non-inferable**) 것만 — 정확한 build/test/env 명령, 아키텍처 경계·의존 규칙, 팀 규약, 금지사항.
- **자동 생성 금지**: LLM-생성 context 파일은 5/8 설정에서 성공률을 낮췄다(arXiv:2602.11988). 사람이 작성·검증한다.
- **bloat/staleness 감점**: 400줄+ 비대 가이드는 adherence를 저하(Anthropic: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions"). "이 줄 지우면 실수 나나?" 밀도만 가치.
- **presence ≠ performance**: 존재 자체는 성능 예측자가 아니다. build로 잡을 수 있는 것을 산문에 맡기지 않는다.

## 안전·결정 권한 불변식 (요약)

1. **build enforces, docs explain** — 산문 규칙보다 lint/CI 강제 우선.
2. **독립 oracle 가드** — 격리-green ≠ correct. 에이전트 저작과 구별되는 독립 검증으로 확인.
3. **자동 생성 금지**(agent-guide)·**규칙/모듈/줄 수 가점 금지**(존재·정확성·의미만).
4. **tool-index 오귀속 금지** — LocAgent·RepoGraph 효과를 layout/설정 공로로.
5. **위험은 경고, 수용은 사용자** — 승인된 변경 조용한 보류 금지·**execute-or-escalate**.
6. **한 번에 한 지표·한 승인.** **커밋 안 함**(git-harness 핸드오프).
7. **강제 probe 없이 등급/성공률 귀속 금지** — "가드레일 추가로 AI 성공률 +N%" 금지.

## generator ≠ checker

개선안을 제안·적용하는 `ai-access-improver`와 행위를 검증하는 `behavior-guard`는 분리된다.
