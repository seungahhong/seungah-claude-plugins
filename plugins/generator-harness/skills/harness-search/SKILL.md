---
name: harness-search
description: 모듈러 탐색공간(Planning/Reasoning/Tool Use/Memory) × 패턴 × 실행모드에서 후보 하네스를 lens 기반으로 제안하고, 합격 후보가 없을 때 recombination(우수 모듈 이식)·mutation(약한 모듈 교체)으로 진화시키는 방법론. harness-proposer 에이전트가 따르며, 사용자가 "하네스 후보 제안", "탐색공간에서 설계 뽑기", "후보 진화·재조합"을 언급할 때도 적용한다. 후보 채점(→ harness-eval)이나 실체화(→ harness-materializer)는 하지 않는다.
---

# Harness Search — 후보 제안·진화 방법론

후보 하네스를 *탐색공간의 한 점*으로 보고, 배정된 lens가 미는 방향으로 점을 고른 뒤, 필요하면 진화시킨다. ADAS(코드/모듈 정의)·AgentSquare(모듈 evolution/recombination)·GPTSwarm(노드·엣지 분리)에 근거한다. 출처는 [../generator-harness/references/research-foundations.md](../generator-harness/references/research-foundations.md), 탐색공간 카탈로그는 [../generator-harness/references/building-blocks.md](../generator-harness/references/building-blocks.md).

## 왜 lens로 펼치는가

후보는 Pareto front를 *펼치기* 위해 존재한다. 동일 프롬프트로 N개를 뽑으면 거의 같은 점 N개가 나와 채점 비용만 쓴다. 서로 다른 lens(최소비용/최대품질/균형/대담한구조/전이우선)로 뽑아야 frontier가 넓어지고, 사용자가 trade-off를 실제로 고를 수 있다.

## 후보 제안 절차

### 1. lens 해석
배정 lens가 미는 축을 먼저 못 박는다.

| lens | 최적화 축 | 전형적 선택 |
|------|-----------|-------------|
| 최소 토큰비용 | 비용↓ | 에이전트 최소, 서브에이전트, 파이프라인, Reasoning 경량 |
| 최대 품질 | 품질↑ | 팀, 팬아웃/생성-검증, Reasoning 강화 |
| 균형 | Pareto knee | 하이브리드, orchestrator-workers |
| 대담한 구조 | 탐색 다양성 | ADAS식 비표준(코드확장 opt-in 시) |
| 전이 우선 | 일반화↑ | Memory·일반화 모듈 강화 |

### 2. 3축에서 점 고르기
- **모듈** — 각 에이전트가 Planning/Reasoning/Tool Use/Memory 중 무엇을 켜는가. domain_spec의 task_types가 요구하는 모듈만 켠다(불필요 모듈은 비용).
- **패턴** — building-blocks.md의 패턴 카탈로그에서 도메인 작업 흐름에 맞는 것. 순차 의존→파이프라인, 다각 분석→팬아웃, 품질 게이트→생성-검증, 동적 분배→감독자.
- **실행모드** — "에이전트 간 실시간 발견 공유가 품질의 핵심인가?" Yes→팀, No→서브, Phase별 차이 큼→하이브리드.

### 3. 평가셋 적합성 자문
설계가 domain_spec의 eval_set 태스크를 *실제로* 수행할 수 있는가? 못 푸는 후보는 무의미하다 — 평가셋을 못 푸는 설계는 내지 않는다.

### 4. rationale 작성
왜 이 (모듈·패턴·모드)가 *이 lens와 이 도메인*에 맞는지 why를 남긴다. 채점자·사용자가 trade-off를 이해해야 한다.

## 과도 분리 방지

분리해도 매번 둘이 동시에 호출된다면 한 에이전트로 통합한다. 에이전트 수는 곧 토큰비용이다. lens가 비용을 미는 게 아니어도, 정당화되지 않는 에이전트는 늘리지 않는다.

| 분리 신호 | 통합 신호 |
|-----------|-----------|
| 전문성/도구가 다름 | 항상 같이 호출됨 |
| 동시 실행 가능(병렬 이득) | 컨텍스트 공유가 필수 |
| 컨텍스트 격리 필요(검증자 객관성) | 분리해도 핸드오프만 |

## 진화 절차 (Phase 5, 합격 후보 없을 때만)

frontier에 acceptance bar를 넘는 후보가 **없을 때만** 진화한다. Pareto-best를 부모로:

- **recombination** — 다른 후보의 *우수 모듈*을 부모에 이식한다(예: cand_2의 강한 Memory를 cand_3에). 직교 승리만 합성한다 — 서로 충돌하는 선택을 섞지 않는다.
- **mutation** — 부모의 *약한 모듈*을 더 강한 구현으로 교체한다(예: Reasoning을 CoT→debate). 채점에서 약점으로 지적된 모듈을 표적한다.

**라운드 상한(기본 2)을 지킨다.** 무한 탐색은 비용 게이트 위반이다(탐색 비용은 미해결 — research-foundations.md §5). 상한 도달 시 현재 frontier로 승인 게이트에 간다. 부모 대비 무엇을 바꿨는지 rationale에 남긴다.

## 안티 패턴

- **동질 후보** — 같은 점 N개. frontier를 못 넓힌다.
- **미지근한 중간** — 모든 후보가 '균형'. 최소비용·최대품질 극단이 없으면 사용자가 고를 게 없다.
- **평가셋 무시** — 멋진 구조지만 eval_set을 못 푸는 후보.
- **무한 진화** — bar에 집착해 라운드 상한을 넘김. 비용 폭발.
- **만능 에이전트** — 모든 책임을 한 정의에 몰아넣어 컨텍스트 오염.
