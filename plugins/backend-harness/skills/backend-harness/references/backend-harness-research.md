# Backend Harness — 연구 dossier (cited)

> 이 문서는 `backend-harness` 하네스 설계의 근거가 된 자료다. [backend-harness-principles.md](./backend-harness-principles.md)의 원칙과 상호 참조된다.
> **Honesty Guardrail**: 정량 수치는 출처 등급([GOLD]=피어리뷰/대규모, [SILVER]=방법론공개 업계리포트·preprint, [BRONZE]=블로그/일화)·출처명·날짜와 함께만 인용한다.
> '개선 N%' 약속은 하지 않는다 — 아래 baseline 수치는 *현재 한계*를 보여줄 뿐, 이 하네스가 그만큼 올린다는 보장이 아니다(baseline-before-target). 빠르게 변하는 분야이므로 각 절에 등급과 CAVEAT를 함께 표기한다.

## 1. 저장소 단위 BE 작업은 SOTA도 절반가량 실패 → 구조화 멀티에이전트 + 검증 정당화

- **FreshBrew (JDK17 마이그레이션)**: 최고 성능 Gemini 2.5 Flash가 **52.3%** 성공. 출처 arXiv:2510.04852 (2025-10) **[GOLD]**.
- **MigrationBench (Java 8→17)**: Claude-4.5-Sonnet **71.67%(minimal)** / **53.33%(maximal)**. 출처 arXiv:2505.09569 (2025-05) **[GOLD]**.
- **Web-Bench (full-stack Web-Agent)**: SOTA Claude 3.7 **Pass@1 25.1%** — 같은 모델의 SWE-bench Verified 65.4% 대비 급락. 출처 arXiv:2505.07473 (2025-05) **[GOLD]**.

→ 함의: 저장소 단위/풀스택 BE 작업은 단일 패스 자동완성으로는 절반 안팎이 실패한다. 단발 생성이 아니라 *설계·환경·구현·검증을 분리한 구조화 멀티에이전트 + 실행 기반 검증*이 정당화된다.
> CAVEAT: 벤치마크별 task 분포·성공 정의(minimal vs maximal)·언어(Java/Web)가 다르므로 수치를 단일 척도로 합산하지 말 것. "절반가량 실패"는 *복수 GOLD 벤치마크에서 공통적으로 SOTA가 절반 안팎에 머문다*는 정성 관찰이다.

## 2. 환경 구성이 최대 병목 → env-provisioner를 독립 Phase로

- **실행가능 환경(Docker) 구축의 F2P(Fail-to-Pass) ≤ 37.7%** — 실행 가능한 환경을 세우는 것 자체가 가장 낮은 통과율을 보이는 병목.
- **멀티에이전트 > 단일에이전트**: SWE-Builder(4-agent)가 RepoLaunch(단일에이전트)보다 환경 구축에 우월.
- 출처 arXiv:2512.06915 (2025-12) **[GOLD]**.

→ 함의: 환경 구성을 구현에 묻으면 가장 비싼 실패가 가장 늦게 터지고, FAIL이 코드 결함인지 환경 결함인지 구분되지 않아 검증 신호가 오염된다. 그래서 env-provisioner를 **독립 1급 Phase**로 두고, "준비됨"을 자기보고가 아니라 빌드·헬스체크·스모크의 실제 통과로만 닫는다. be-verifier가 환경 문제를 만나면 FAIL이 아니라 **BLOCKED**로 분리해 이 Phase로 되돌린다.
> CAVEAT: F2P 수치는 해당 벤치마크의 환경 구축 task에 대한 것이다. 절대치보다 *환경 구축이 다른 단계 대비 최저 통과율 병목이며 멀티에이전트 분리가 유리하다*는 정성 결론을 차용한다.

## 3. 에이전트 과신 → 실행 기반 검증·자기보고 불신 필수

- **Claude-Sonnet-4: 47.41% commit(성공 주장) vs 실제 F2P 35.53%** — 에이전트가 "성공했다"며 commit한 비율이 실제 통과율보다 약 12%p 높다. 자기평가는 과신한다.
- 출처 arXiv:2512.06915 (2025-12) **[GOLD]**.
- **reward hacking 방지엔 고커버리지 테스트가 필요** — 행복 경로만 덮인 테스트는 테스트 무력화·우회로 초록을 만드는 reward hacking에 취약. 출처 FreshBrew arXiv:2510.04852 (2025-10) **[GOLD]**.

→ 함의: 통과를 자기보고/commit으로 인정하면 거짓 PASS가 누적된다. be-implementer는 최종 PASS를 선언하지 않고, be-verifier가 빌드·테스트를 *직접 재실행*해 실제 출력으로만 판정하며, 커버리지(계약·에러·경계 경로)를 게이트하고 테스트 무력화 흔적을 diff로 적대적으로 점검한다.
> CAVEAT: commit-vs-F2P 격차의 절대 크기는 모델·벤치마크 의존이다. 차용하는 것은 *자기보고가 실제 통과를 과대평가하므로 독립 실행 검증이 필요하다*는 방향성이다.

## 4. test-generator — raw LLM 테스트의 한계와 공진화 수리 루프

- raw LLM이 생성한 테스트는 환각으로 **컴파일/런타임 오류**가 잦고 **커버리지가 낮다**. 이를 **5개 경험적(empirical) 수리 템플릿**(컴파일 오류 ~50% / 런타임 오류 ~75% 수리)과 **generate→compile→execute→repair 공진화(co-evolution) 루프**로 보완하면, baseline(ChatGPT/EvoSuite/A3Test) 대비 **pass +18% / coverage +20%** 보고.
- 출처 TestART, arXiv:2408.03095 (ACM TOSEM 2025) **[SILVER]**.
> **CAVEAT(필수)**: 2024-08 데이터라 최신 모델엔 수치가 안 맞을 수 있다. **효과크기(+18%/+20%, ~50%/~75%)를 단정하지 말 것** — 차용하는 것은 *패턴*(generate→compile→execute→repair 루프 + 오류 유형별 결정론적 수리 템플릿 + 커버리지 피드백 반복)이지 수치 약속이 아니다.

## 5. judge 캘리브레이션 — 자동 판정은 보조, 사람 검토 필수

LLM-as-judge/자동 테스트 판정은 캘리브레이션이 흔들릴 수 있어 *보조 신호*로만 쓰고, 통과/실패의 최종 책임은 실제 실행 결과와 사람 검토에 둔다. test-generator의 judge는 커버리지·컴파일·실행 결과 같은 *기계검증 가능한* 신호를 우선하고, 의미적 적절성 판정은 사람 검토로 닫는다.
> CAVEAT: 본 dossier는 정성 원칙으로만 채택한다 — 자동 judge의 신뢰도에 대한 단일 정량치를 약속으로 인용하지 않는다.

## 6. 자율 반복 루프와의 정합 (설계 원칙)

be-verifier의 **generator/checker 분리·증거 없는 PASS 금지**와 test-generator의 **루프 토폴로지**는 일반적인
목표 지향 실행 루프(Goal→Execute→Verify→Diagnose→Improve)·독립 검증자 원칙과 같은 형태를 따른다. 이 하네스는
그 토폴로지 위에 *BE 도메인의 실행 검증·환경 1급화·결정론적 수리 템플릿*을 얹은 자족적 워크플로이며, 어떤 외부
워크플로에도 런타임 의존하지 않는다 — 같은 원칙을 BE 구현·검증에 내재화했을 뿐이다.
