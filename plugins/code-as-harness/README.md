# code-as-harness

> 코드를 **실행 가능·검사 가능·상태 보존** 한 운영 기반으로 다루고, 한 번의 **거버넌스된 Plan→Execute→Verify 제어
> 루프**로 코드 변경을 *안전하고 검증 가능하게* 수행하는 도메인 무관 멀티 에이전트 하네스.

근거 논문: **arXiv:2605.18747 "Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems"**(2026-05).

## 핵심 아이디어

코드는 더 이상 *최종 산출물*만이 아니다 — 에이전트가 추론·행동·검증하는 **운영 기반(operational substrate)** 이다.

- **executable** — 출력이 *형식적으로 검증 가능한 결과를 갖는 연산*이다 → 검증은 의견이 아니라 *실행*이다.
- **inspectable** — 중간 계산이 *읽고·저장하고·행동에 쓰는 구조화된 trace*다 → 진행·진단의 단위다.
- **stateful** — 진화하는 프로그램이 *단계 너머 영속하는 진행 상태*를 표상한다.

이 기반 위에서 본 하네스는 **한 번의 거버넌스된 제어 사이클**을 운영한다 — 계획은 *변경 계약*, 실행은 *권한·샌드박스
게이트*, 검증은 *결정적 센서(실행)*, 진단은 *trace 기반 regression-free 수정*.

## 언제 쓰나

- "코드를 실행·검증 가능한 하네스로 다뤄서 **계획→실행→검증**으로 안전하게 바꿔줘"
- "계획을 **변경 계약**으로 못 박고 **결정적 센서**(테스트·빌드·린트)로 검증해줘"
- "**비가역·안전임계 행동**(삭제·마이그레이션·스키마·프로덕션)은 **사람 승인 게이트**로 막고 가역만 진행해줘"
- "**자기보고 말고 실제 실행 결과**로 검증하고 **reward-hacking**(테스트 약화) 가드해줘"
- "부분 센서면 PASS 단정 말고 **UNVERIFIED**로 처리해줘"
- "**실행 trace 근거**로 실패 진단하고 통과한 건 안 깨게 **regression-free**로 다음 수정 제안해줘"

## 4단계

| Phase | 이름 | 하는 일 | 게이트 |
|-------|------|---------|--------|
| 0 | 계획 계약 (Plan Contract) | 의도한 변경·판정 센서·행동 위험(가역/안전임계) 명문화 | 승인 게이트 |
| 1 | 권한 실행 (Permissioned Execute) | 권한·샌드박스 경계에서 최소 변경 적용·가역 우선·실행 trace 적재 | 안전임계 사람 게이트 |
| 2 | 실행 검증 (Execution Verify) | 결정적 센서 실제 실행·조항별 PASS/FAIL/UNVERIFIED·게이밍/불완전 피드백 가드 | 1줄 보고 |
| 3 | 텔레메트리 진단·수렴 (Telemetry Diagnose & Converge) | trace 인용 진단·regression-free 수정안·CONVERGED/ITERATE/ESCALATE | 수렴 사람 게이트 |

> **ITERATE**는 *사람 승인 하에 한 사이클 더* 도는 것이다 — 무한 자율 반복이 아니라 매 사이클이 명시적 결정·사람
> 게이트를 통과한다. 무진전이면 ESCALATE한다.

## 사용법

스킬을 발동시키는 발화(위 "언제 쓰나")를 입력하면 오케스트레이터가 Phase 0부터 진행한다. Phase 0(계획 계약) 직후
승인 게이트, Phase 1의 안전임계 행동·Phase 3의 최종 수렴 판정에 사람 게이트가 있다.

## 언제 다른 도구를 쓰나 (도구 경계)

이 하네스는 **'코드를 실행·검증 가능한 하네스로 다루는 거버넌스된 Plan→Execute→Verify 제어 사이클'** 에 특화한다.
다음은 범위 밖이다(일반 도메인 개념으로 서술 — 특정 플러그인에 의존하지 않는다).

- **통과까지 자율 반복 + 교차세션 학습 메모리** → 자율 반복 도메인 (이 하네스는 한 번의 거버넌스 사이클, 필요 시 사람 승인 하 1회 ITERATE)
- **백엔드/API 구현 + 환경 provisioning 1급 단계** → 백엔드 구현 도메인
- **실행 가능 명세를 source of truth로 작성** → 명세 우선 도메인 (계획 계약은 한 사이클의 변경 계약이지 영속 명세가 아님)
- **여러 AI 에이전트로 병렬화할지·토폴로지 결정** → 멀티 에이전트 오케스트레이션 도메인
- **모델 컨텍스트 페이로드 조립·압축** → 컨텍스트 설계 도메인
- **AI 출력 judge 구성·평가** → 평가 도메인 (검증은 계약 센서의 실제 실행이지 채점 시스템 구축이 아님)
- **하네스 자체 결함 진단·개선** → 메타 도메인 (텔레메트리 진단은 작업 trace를 읽지 하네스 자산을 고치지 않음)
- **상류 산출물 핸드오프 게이트 검수 / 프로덕션 인시던트 대응 / PRD 작성 / 커밋·PR / settings 설정** → 각 해당 도메인

## 근거 자료

설계는 deep-research 3-vote 적대 검증(5각도·20소스·96주장 → 24 confirmed/1 refuted)에 기반한다. 상세 인용·vote·CAVEAT는
[skills/code-as-harness/references/code-as-harness-research.md](skills/code-as-harness/references/code-as-harness-research.md) 참조.

- **1차(대상)**: arXiv:2605.18747 "Code as Agent Harness"(2026-05) — 코드=operational substrate, 3-layer, Plan-Execute-Verify 제어 루프, sandboxed·permissioned 실행, 결정적 센서+사람 게이트, open challenge=가드레일.
- **인접 1차**: arXiv:2604.08224 Externalization(weights→context→harness) · arXiv:2506.11442 ReVeal(generation-verification 공진화) · arXiv:2604.20801 AgentFlow(harness 민감도·사전 검증 게이트) · arXiv:2508.00083 code-gen taxonomy · arXiv:2512.14012 "developers don't vibe, they control"(plan-first·전 산출물 검증).
- **보강(failure-modes)**: arXiv:2604.15149 verifier reward-hacking · arXiv:2603.07084 sandbox 격리.

> **정직성**: 대상 서베이는 *개념 프레임*으로 인용(벤치마크 결과 아님), 인접 논문 기법은 *각 출처에만* 귀속, 'several-fold'
> 민감도는 *특정 세팅값*으로 한정, 반박된 AgentFlow 4-phase 루프는 미사용, "개선 N% 보장"을 쓰지 않는다.

## 독립성

다른 마켓플레이스 플러그인에 의존하지 않는 **독립 플러그인**이다. 경계의 '범위 밖'은 일반 도메인 개념으로만 서술하며,
모든 근거는 1차 자료를 직접 인용한다.
