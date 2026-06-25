# code-as-harness

코드를 단순 산출물이 아니라 **실행 가능(executable)·검사 가능(inspectable)·상태 보존(stateful)** 한 운영 기반
(operational substrate)으로 다루고, 한 번의 **거버넌스된 Plan→Execute→Verify 제어 루프**로 코드 변경을 *안전하고
검증 가능하게* 수행하는 도메인 무관 멀티 에이전트 하네스.
핵심 메시지는 **"코드는 산출물이 아니라 에이전트가 추론·행동·검증하는 실행 기반이다 — 계획은 변경 계약이고, 실행은
권한·샌드박스로 게이트되며, 검증은 자기보고가 아니라 결정적 센서(실행)로 한다"** 이다.
근거 논문: **arXiv:2605.18747 "Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems"**(2026-05).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
code-as-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                          # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                          # 사용자용 개요·언제 쓰나·4단계 사용법·도구 경계·근거 논문
├── agents/                            # 모두 model: "opus"
│   ├── plan-contractor.md             # Phase 0 — 작업 → 변경 계약(의도·센서·행동 위험 분류)
│   ├── permissioned-executor.md       # Phase 1 — 권한·샌드박스 실행·가역 우선·안전임계 사람 게이트·trace 적재
│   ├── execution-verifier.md          # Phase 2 — 결정적 센서 실행·조항별 PASS/FAIL/UNVERIFIED·reward-hacking·불완전 피드백 가드
│   └── telemetry-diagnostician.md     # Phase 3 — trace 인용 진단·regression-free 수정안·CONVERGED/ITERATE/ESCALATE
├── skills/
│   └── code-as-harness/
│       ├── SKILL.md                   # 오케스트레이터(진입점, Phase 0 계약 게이트 → 실행 → 검증 → 진단·수렴)
│       └── references/
│           ├── code-as-harness-principles.md   # 원칙·anti-pattern·결정 신호표
│           └── code-as-harness-research.md      # 설계 근거 deep-research dossier(출처·인용·vote·CAVEAT·반박된 주장·방법론)
└── evals/
    ├── evals.json                     # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json              # 트리거 경계 평가(should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 계획 계약 (Plan Contract) | plan-contractor | Plan Contract(의도한 변경·판정 센서·행동 위험 분류) | 승인 게이트 |
| 1 | 권한 실행 (Permissioned Execute) | permissioned-executor | Execution Trace + 적용 요약(가역 우선·안전임계 사람 게이트) | 안전임계 사람 게이트 / 1줄 보고 |
| 2 | 실행 검증 (Execution Verify) | execution-verifier | Verification Report(조항별 PASS/FAIL/UNVERIFIED + 센서 증거) | 1줄 보고 |
| 3 | 텔레메트리 진단·수렴 (Telemetry Diagnose & Converge) | telemetry-diagnostician | Diagnosis & Convergence(trace 진단·regression-free 수정·결정) | 수렴 사람 게이트 |

최종 보고: `[Code-as-Harness] 계획계약 {조항수} · 실행 {권한/샌드박스·안전임계 게이트} · 검증 {PASS/FAIL/UNVERIFIED} · 결정 {CONVERGED|ITERATE|ESCALATE}`

## Conventions

- **코드 = 운영 기반**: executable(검증 가능 연산)·inspectable(구조화 trace)·stateful(영속 진행). 검증은 의견이 아니라 실행이다.
- **계획 = 변경 계약**: 실행 전 의도한 변경·판정 센서·행동 위험을 못 박는다. 사전 약속이 drift를 탐지 가능하게 한다.
- **권한·샌드박스 실행**: 가역 우선, 안전임계/비가역(삭제·마이그레이션·스키마·네트워크·시크릿·프로덕션)은 실행 전 사람 게이트.
- **실행 기반 검증(자기보고 불신)**: 결정적 센서를 실제로 돌려 조항별로 증거와 함께 판정한다.
- **reward-hacking·verifier-gaming 가드**: 테스트 약화·skip·하드코딩·형식 우회 금지. 약한 센서 통과를 PASS로 단정하지 않는다.
- **불완전 피드백 정직성**: 부분 센서면 UNVERIFIED로 confidence 강등, 증거 없는 PASS 없음. 최종 성공 너머 불변식·부작용도 본다.
- **검사 가능 trace = 텔레메트리 substrate**: 실패 진단은 추측이 아니라 trace 인용으로 한다.
- **regression-free 개선**: 차기 수정이 통과한 것을 깨지 않는다. 무진전이면 ESCALATE.
- **사람 감독은 안전임계에 집중(전수 승인 아님)**: 가역은 진행, 안전임계·계획계약·최종 수렴 판정에 사람 게이트.
- **정직성·falsifiability**: 서베이는 개념 프레임(벤치마크 결과 아님), 인접 논문 기법은 출처에만 귀속, 'several-fold'는 세팅값, 반박된 AgentFlow 4-phase 미사용, "개선 N% 보장" 금지.
- **승인 게이트·관찰성**: Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: 통과까지 자율 반복+학습 메모리·백엔드 환경 provisioning 구현·실행 명세 작성·AI 에이전트 병렬화·컨텍스트 조립·AI 출력 평가·하네스 진단·상류 핸드오프 검수·장애 대응·PRD·커밋/PR은 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 다른 마켓플레이스 플러그인에 의존하지 않는 독립 플러그인이다(경계의 '범위 밖'은 일반 도메인 개념으로만 서술).

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | 코드를 operational substrate로 다루는 거버넌스된 Plan→Execute→Verify 하네스. arXiv:2605.18747 'Code as Agent Harness' 정독 + deep-research 3-vote 적대 검증(5각도·20소스·96주장·24 confirmed/1 refuted) 근거. 인접 1차: arXiv:2604.08224·2506.11442·2604.20801·2508.00083·2512.14012, 보강: 2604.15149·2603.07084 |
