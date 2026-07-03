# 세션 5 — agentic 코딩 벤치마크 ↔ repo readiness 정량 조작화 방법론

> 조사 렌즈: 전체 rubric 타당성·가중치·카테고리 구성. 추가/삭제 카테고리, 자동 측정 가능 신호 근거, 점수 조작화 best practice.
> 상태: deep-research 각도 5, 적대 검증 완료 (2026-07-03). arXiv ID 실존 확인. C6 정정: "Task Discovery"는 Factory 8-pillar가 아니라 오픈소스 재현판 축. SetupBench·"AI Codebase Maturity Model"(2604.09388)은 UNVERIFIABLE — claim 승격 금지.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | LLM 생성 context가 성공률 −0.5%/−2%(원문 "0.5%·2%") |
| C2 | **CONFIRMED** | 비용 +20%/+23%, step +2.45/+3.92(agent가 과잉 탐색 준수) |
| C3 | **CONFIRMED** | 이득은 다른 문서 없을 때만(LLM +2.7%, human +4%) |
| C4 | **CONFIRMED** | context는 "minimal requirements"만 — compass-not-encyclopedia 실증 지지 |
| C5 | **CONFIRMED** | AGENTS.md runtime −28.64%·token −16.58%, completion 대등(success≠efficiency) |
| C6 | PLAUSIBLE | Factory.ai 8-pillar/5-level, "80% 게이팅"(Task Discovery 귀인·"60+" 미확인) |
| C7 | **CONFIRMED** | jpequegn/agent-readiness-score 실존(Factory+DevEx, Task Discovery) |
| C8 | **CONFIRMED** | Kenogami 9-dim **lowest-as-ceiling** + blocking/constraining 이분 |
| C9 | PLAUSIBLE | auto vs manual/LLM-judgment 신호 구분(축 정합, 개별 대응 부분 확인) |

## 검증된 핵심 발견

2025~2026 근거는 "context 문서를 붙이면 agent 성능이 오른다"는 직관을 정면 반증한다. ETH Zurich/LogicStar.ai 대조 실험(arXiv:2602.11988)은 **LLM 생성 AGENTS.md가 SWE-bench Lite resolution을 평균 0.5%·AGENTbench 2% 떨어뜨리고 추론 비용을 각각 20%·23% 증가**시켰고, 이득은 오직 "다른 문서가 전혀 없을 때"만 났다(LLM +2.7%, human +4%) — **문서의 존재가 아니라 내용의 정확성·간결성·불필요 지시 배제가 성능을 가른다**.

별도 연구(arXiv:2601.20404, 10 repo·124 PR)는 AGENTS.md가 task completion은 대등하게 두되 runtime −28.64%·output token −16.58%로 **효율을 개선** → "success"와 "efficiency"는 분리된 축.

**집계 구조의 반증**: 산업 프레임워크가 공통적으로 순수 가중합이 아니라 **게이팅(Factory.ai 레벨별 80% 통과)/최저점-천장(Kenogami lowest-as-ceiling)**을 채택 — 하나의 blocking 결함이 전체 agent 작업을 무너뜨린다는 관찰 때문. → **현행 순수 가산 100점 구조에 대한 직접 반증.**

### 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** LLM 생성 context 파일이 성공률 개선 못하고 SWE-bench Lite −0.5%·AGENTbench −2% — **arXiv:2602.11988**, Gloaguen 외(ETH Zurich/LogicStar.ai), 2026(4 frontier 모델·3 setting).
- **[C2 · CONFIRMED]** 비용 +20%/+23%, trajectory +2.45/+3.92 step(agent가 지시된 과잉 테스트·탐색 준수) — 동.
- **[C3 · CONFIRMED]** 이득은 조건부 — 다른 문서 없을 때만 LLM +2.7%·human +4%. "존재"가 아니라 "정확성·중복 제거·불필요 요구 배제"가 결정 변수 — 동.
- **[C4 · CONFIRMED]** overview/아키텍처 개요는 (개발자 작성본조차) 비효과적, human-written은 "minimal requirements(비추론 세부: 특수 tooling·custom build command)"만 담아야 — 동. compass-not-encyclopedia 실증 지지.
- **[C5 · CONFIRMED]** AGENTS.md가 completion 대등·runtime −28.64%·token −16.58% — **arXiv:2601.20404**, Lulla 외, 2026(10 repo·124 PR, Codex+Claude Code). success와 efficiency/cost는 별도 카테고리.
- **[C6 · PLAUSIBLE]** Factory.ai가 8 pillar(Style&Validation, Build, Testing, Documentation, Dev Environment, Code Quality, Observability, Security&Governance)×5 level로 조작화, LLM binary 평가를 "이전 레벨 80% 통과" 게이팅(Level 3=프로덕션 자율 최소 바) — Factory.ai "Introducing Agent Readiness", 2026. ※ "Task Discovery"·"60+ 기준"은 Factory 8-pillar 아님(재현판 축, 미확인).
- **[C7 · CONFIRMED]** 오픈소스 재현판(jpequegn/agent-readiness-score)이 Factory 방법론 + DevEx 3차원(Forsgren et al., feedback loops)을 근거로 Task Discovery(issue/PR template, CONTRIBUTING) 명시 — GitHub, 2026.
- **[C8 · CONFIRMED]** Kenogami-AI/codebase-readiness가 9차원 1~5 채점하되 **평균이 아니라 최저 점수를 천장**(lowest-as-ceiling), 차원을 blocking(dim 1·2·5)/constraining으로 구분 — GitHub, 2026(DORA·Fowler "Agent=Model+Harness"). 함의: **순수 가중합 100점은 blocking 결함을 희석해 오탐**.
- **[C9 · PLAUSIBLE]** auto 신호(coverage·CI latency, type config·`any` 수, 파일 크기 분포, lint 기반 boundary violation, telemetry, dependency currency) vs manual/LLM-judgment 신호(API directness, ADR 품질) 구분 — Kenogami. 함의: 각 지표에 auto/manual 라벨.

## Rubric v3 함의

**집계 구조 변경 (가장 중요, C1·C8)** — 현행 "7카테고리 가중합 100점"은 하나의 blocking 결함(E1 hallucinated path·미작동 build/test)이 다른 고득점에 희석된다. Kenogami **lowest-as-ceiling + blocking/constraining** + Factory **레벨별 80% 게이팅** 도입. 최소한 **E를 blocking gate로 승격** — E1·task validation 실패 시 전체 등급에 상한(예: 최대 AI-Fragile) 씌우는 게이팅 룰을 score.py에.

**신규 카테고리 추가**
- **Feedback-loop latency/quality**(C6·C7·DevEx) — pre-commit hook·CI 소요시간·static type·fast lint. 현행엔 F만 있고 feedback 속도 축 없음.
- **Environment/Dev setup reproducibility**(C6·C7) — devcontainer·.env.example·setup script·문서화된 env var. 현행 D에 흡수돼 있으나 분리.
- **Task Discovery**(C7) — issue/PR template·CONTRIBUTING. (근거 등급은 C6보다 낮음.)

**기존 카테고리 재정의 (반증 반영)**
- **A(/15) 보유율 측정 약화**(C1·C3·C4) — 단순 파일 수 카운트에 15점은 근거에 반함.
- **B(/20) compass-not-encyclopedia 유지·강화**(C4 직접 지지) — "overview 존재"→"비자명 패턴·quick command·key file 밀도 vs 산문 분량 비율"로 conciseness 정량화.

**success vs efficiency 분리**(C5) — 현행 G(/5)의 pass rate·tool calls·tokens를 "task success"와 "cost/efficiency(runtime·token·step)" 두 지표로 쪼개 각각 telemetry.

**score.py 자동 신호**(C9)
- auto: test coverage·CI 소요시간, type strict config·`any`/`# type: ignore` 수, 파일 line 분포, lint 기반 boundary violation, dependency currency, pre-commit·telemetry lib 존재, hallucinated-path 검증.
- manual/LLM-judgment 라벨: API directness, ADR 품질, non-obvious pattern 유효성.

## 소스 (검증 상태)

- Evaluating AGENTS.md — Gloaguen 외(ETH Zurich/LogicStar.ai), 2026, arXiv:2602.11988 (VERIFIED, 수치 정확 일치)
- On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents — Lulla 외, 2026, arXiv:2601.20404 (VERIFIED)
- Introducing Agent Readiness — Factory.ai, 2026, factory.ai/news/agent-readiness (VERIFIED — 8 pillar/5 level/80% 게이팅; "Task Discovery" 귀속 정정, "60+" 미확인)
- agent-readiness-score — jpequegn(GitHub), 2026 (VERIFIED — 실존)
- codebase-readiness (9-dim, lowest-as-ceiling) — Kenogami-AI(GitHub), 2026 (VERIFIED — blocking/constraining 확인)
- SetupBench, "The AI Codebase Maturity Model"(arXiv:2604.09388) — **UNVERIFIABLE, 맥락 참조만, claim 승격 금지**
