# Code as Agent Harness — 원칙·anti-pattern·결정 신호표

> `code-as-harness` 하네스의 설계 헌법. 모든 Phase가 따른다. 근거는 [code-as-harness-research.md](./code-as-harness-research.md)
> (§N은 그 dossier의 절). 핵심 전제: **코드는 산출물이 아니라 운영 기반(operational substrate)** — *executable·inspectable·
> stateful*. 본 하네스는 이 기반 위에서 **거버넌스된 Plan→Execute→Verify 제어 사이클 한 번**을 운영한다(research §1·§3).

---

## §1. 코드 = 운영 기반 (executable · inspectable · stateful)

코드를 *최종 산출물*이 아니라 에이전트가 *추론·행동·검증*하는 매체로 다룬다(research §1·§4). 세 성질을 설계에 활용한다.

- **executable** — 출력은 *형식적으로 검증 가능한 결과를 갖는 연산*이다 → 검증은 의견이 아니라 *실행*이다(§4·Phase 2).
- **inspectable** — 중간 계산은 *harness가 읽고·저장하고·행동에 쓰는 구조화된 trace*다 → 진행과 진단의 단위다(§3.5.1·Phase 1·3).
- **stateful** — 진화하는 프로그램이 *단계 너머 영속하는 진행 상태*를 표상한다 → 무엇이 됐고 안 됐는지가 코드/trace에 남는다.

## §2. 계획 = 변경 계약 (plan-as-contract)

실행 전에 **의도한 변경을 계약으로 못 박는다**(research §3 "plans form contracts over intended changes"). 계약은 *사전
약속*이라 drift를 탐지 가능하게 만든다. 계약에 들어가는 것:

- **의도한 변경**: 어떤 파일·동작·불변식을 바꾸는가(그리고 *바꾸지 않을* 것).
- **판정 센서**: 성공을 판정할 **결정적 센서**를 *미리* 명시한다 — 테스트·빌드·타입체크·린트·실행/스모크(§3·§8). "무엇이
  이 변경을 *반증*하는가"를 앞에서 적는다.
- **행동 위험 분류**: 각 행동을 *가역(reversible)* vs *안전임계/비가역(safety-critical/irreversible)* 으로 분류한다 —
  삭제·마이그레이션·스키마 변경·네트워크 egress·시크릿·프로덕션 접촉은 안전임계(§5(e)·§12(b)).

## §3. 권한·샌드박스 실행 (permissioned / sandboxed state transition)

실행은 *권한·샌드박스 경계* 안에서 한다(research §3 "sandboxed and permissioned environments"; §12(b) sandbox=격리 경계).

- **가역 우선**: 같은 결과면 더 가역적인 경로를 택한다. 최소 변경으로 계약 한 조항씩 실현한다.
- **안전임계 행동은 사람 게이트**: 비가역·고위험 행동(§2 분류)은 *실행 전 사람 승인*을 받는다 — 서베이의 "human oversight
  for safety-critical actions"(§5(e))를 운영화. 프로는 에이전트가 설치한 의존성을 거부하고 직접 디버깅한다(§7).
- **trace 적재**: 계획조항 → diff → 행동 → 관측 피드백을 **구조화된 실행 trace**로 남긴다(inspectable, §1·§3.5.1).

## §4. 실행 기반 검증 (execution-based verification) — *자기보고 불신*

검증은 **결정적 센서를 실제로 돌려** 한다 — "다 됐다"는 자기보고가 아니라 *실행 결과*가 판정한다(research §4·§8).

- 계약(§2)의 센서를 돌리고, 계약 조항별로 **부합/위반**을 *증거(센서 출력)와 함께* 판정한다.
- 프로의 검증 전술을 따른다 — 요구 대비 line-by-line·터미널 기능 테스트·린트/테스트 실행(§8).
- 코드↔테스트는 함께 진화한다(§9 ReVeal: generation-verification 공진화) — 단, 테스트를 통과시키려 *약화*하지 않는다(§5).

## §5. reward-hacking · verifier-gaming 가드

센서를 *게이밍*하지 않는다(research §5(a) "evaluation beyond final task success"; §12(a) verifier gaming).

- **금지**: 테스트를 삭제·약화·skip, 기대값을 출력에 맞춰 바꾸기, 입력 하드코딩(extensional shortcut), 형식만 맞춘 우회.
- **불완전 verifier 경계**: *extensional correctness만 보는 센서*는 task 요구를 포착 못 해 shortcut을 허용한다(§12(a)).
  센서가 약하면 *센서를 보강*하거나 *한계를 명시*하지, 약한 센서를 통과했다고 PASS로 단정하지 않는다.
- **최종 성공 너머**: 최종 task 성공만 보지 말고 *불변식·부작용·인접 회귀*도 본다(§5(a)).

## §6. 불완전 피드백 하의 검증 (verification under incomplete feedback)

센서가 부분적이면 **PASS를 단정하지 않는다**(research §5(b)). 판정은 셋이다 — **PASS**(센서가 충분히 덮고 통과), **FAIL**
(센서가 위반을 드러냄), **UNVERIFIED**(센서 사각·부분 피드백으로 단정 불가). UNVERIFIED는 *솔직한 결과*이며 confidence를
강등하고 무엇이 안 덮였는지 명시한다. **증거 없는 PASS를 만들지 않는다.**

## §7. 검사 가능 trace = 텔레메트리 최적화 substrate

구조화된 실행 trace를 *진단·개선의 입력*으로 쓴다(research §3.5.1 "Deep Telemetry as the Optimization Substrate").

- 실패 진단은 *추측*이 아니라 **trace 인용**(어느 조항·어느 diff·어느 센서 출력)으로 한다.
- 차기 계획계약 수정안을 trace 근거로 제안한다(§9·§11 reflection/self-improvement 어휘).

## §8. regression-free 개선

차기 수정은 **이미 통과한 것을 깨지 않아야 한다**(research §5(c) "regression-free harness improvement"). 수정안은 통과한
센서를 회귀시키지 않음을 명시 점검하고, 무진전(같은 실패 반복·진동)을 감지하면 ITERATE 대신 **ESCALATE**(사람)로 보낸다.

## §9. 사람 감독은 안전임계에 집중 (전수 승인 아님)

모든 행동을 일일이 승인받지 않는다 — *가역 행동은 진행*, **안전임계/비가역 행동·계획 계약·최종 수렴 판정에 사람 게이트**를
둔다(research §5(e)·§7). 감독을 *필요한 곳*에 집중해 마찰을 줄이되, 비가역 손상을 막는다.

## §10. 정직성·falsifiability

- 대상 서베이(2605.18747)는 **개념 프레임**이지 벤치마크 결과가 아니다 — 설계 스캐폴드로 쓰고 "N% 우월"로 인용하지 않는다.
- **인접 논문 기법을 대상 서베이에 귀속하지 않는다**(ReVeal TAPO·AgentFlow DSL은 각 출처에만, research §머리말).
- 'several-fold(4x)' harness 민감도는 *특정 세팅값*이지 보편 법칙이 아니다(§10 CAVEAT). 반박된 AgentFlow 4-phase 루프는
  쓰지 않는다(research 반박된 주장). 수치는 *코호트·시점 관찰값*으로만, "개선 N% 보장" 금지.

## §11. 승인 게이트·관찰성

Phase 0(계획 계약) 직후 승인 게이트는 항상. Phase 1의 안전임계 행동·Phase 3의 최종 수렴 판정도 사람 게이트. 각 Phase는
1줄로 보고하고, *요청되지 않은 사이드 에이전트나 중복 실행*을 만들지 않는다.

---

## Anti-pattern (하지 말 것)

| Anti-pattern | 왜 나쁜가 | 올바른 패턴 | 근거 |
|---|---|---|---|
| 계획 없이 바로 변경 | drift·범위 폭주 탐지 불가 | 계획=계약 먼저(의도·센서·위험) | §2·research §7 |
| 비가역 행동을 사람 없이 실행 | 복구 불가 손상 | 안전임계는 실행 전 사람 게이트 | §3·§9·research §5(e) |
| "다 됐다" 자기보고로 통과 | 미검증 회귀·환각 | 결정적 센서 실행 결과로 판정 | §4·research §8 |
| 테스트 약화/하드코딩으로 통과 | reward hacking·가짜 성공 | 센서 게이밍 금지·센서 보강 | §5·research §12(a) |
| 부분 센서로 PASS 단정 | 불완전 피드백 은폐 | UNVERIFIED·confidence 강등 | §6·research §5(b) |
| 최종 성공만 보고 부작용 무시 | 인접 회귀·불변식 깨짐 | 최종 너머 불변식·부작용 검증 | §5·research §5(a) |
| 추측으로 실패 진단 | 잘못된 수정 | trace 인용 진단 | §7·research §3.5.1 |
| 통과한 것 깨는 수정 | 회귀 | regression-free 점검 | §8·research §5(c) |
| 무진전인데 계속 반복 | 무한 루프·비용 | 무진전 감지 → ESCALATE | §8 |
| 인접 논문 기법을 서베이에 귀속 | 부정확·과장 | 각 기법은 출처에만 귀속 | §10·research 반박 |

## 결정 신호표 — 이 하네스인가, 인접 도메인인가?

| 신호 | 이 하네스(code-as-harness) | 인접 도메인 |
|---|---|---|
| "코드를 실행·검증 가능한 하네스로 다뤄 계획→실행→검증으로 안전하게 바꿔줘" | ✅ | — |
| "계획을 변경 계약으로 못 박고 센서로 검증, 안전임계는 사람 게이트" | ✅ | — |
| "검증 가능한 목표로 *통과까지 자율 반복*하고 교훈을 메모리에 distill" | ❌ | 자율 반복 루프(loop) |
| "백엔드/API 구현 + *환경 provisioning을 1급 단계*로" | ❌ | 백엔드 구현 |
| "에이전트가 코드 생성할 *실행 가능 명세를 source of truth*로 작성" | ❌ | 명세 우선(spec) |
| "여러 AI 에이전트로 *병렬화할지·토폴로지* 결정" | ❌ | 멀티 에이전트 오케스트레이션 |
| "모델에 넣을 *컨텍스트 페이로드 조립·압축*" | ❌ | 컨텍스트 설계 |
| "AI 출력을 *judge로 채점·benchmark validity* 감사" | ❌ | 평가 |
| "*하네스 자체* 결함을 trace로 진단·개선(루트 CLAUDE.md/스킬)" | ❌ | 메타 |
| "완성된 *상류 산출물(기획·계약)* 핸드오프 게이트 검수" | ❌ | 핸드오프 리뷰 |
| "프로덕션 *장애 탐지·RCA·완화*" | ❌ | 운영 |

경계가 모호하면 한 질문으로 확인한다 — "*코드 변경을 거버넌스된 Plan→Execute→Verify 사이클로 안전·검증 가능하게
수행*하려는 건가요, 아니면 *다른 것*(통과까지 자율 반복·환경 구성 구현·실행 명세 작성·에이전트 병렬화·컨텍스트 조립·
산출물 채점·하네스 진단·상류 핸드오프 검수·장애 대응)인가요?"
