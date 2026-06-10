# generator-harness

## 하네스: 도메인 무관 하네스 자동 탐색·생성

**Goal**: 사용자 도메인 요구를 입력받아 후보 하네스(에이전트팀 + 스킬 + 오케스트레이터) 여러 개를 자동 제안하고, 정확도-토큰비용 Pareto + 도메인/모델 전이성으로 채점한 뒤, **사용자 승인 게이트**를 거쳐 최적 후보만 실체화한다. 단일 정확도가 아니라 Pareto trade-off를 1차 품질 신호로 삼는다.

**왜 별도 플러그인인가 (3-도구 분담)**

| 도구 | 역할 | 입력 → 출력 |
|------|------|------------|
| `harness-generator` | **수동·인터랙티브** 생성 (고정 패턴 선택) | 도메인 요구 → 1개 하네스 (탐색 없음) |
| `meta-harness` | **기존** 하네스 trace 기반 진단·개선 | 실행 trace → 비후퇴 패치 |
| `generator-harness`(본 플러그인) | **자동 탐색·평가**로 신규 하네스 생성 | 도메인 + 평가셋 → 후보 N개 탐색 → Pareto 최적 1개 |

세 도구는 경쟁이 아니라 보완이다 — 본 플러그인이 *탐색·생성*, meta-harness가 *진단·진화*, harness-generator가 *수동 정밀제어*를 담당한다. 본 플러그인은 실체화(Phase 7)에서 harness-generator의 작성 규약을 재사용한다.

**Trigger**: 사용자가 "근거(논문) 기반으로 최적 하네스를 탐색해서 만들어줘", "후보 하네스 여러 개 뽑아 점수 매기고 제일 나은 걸로", "정확도-비용 Pareto로 하네스 골라줘", "이 도메인용 하네스를 자동 설계·평가해서 생성"처럼 **자동 탐색·채점 기반 생성**을 요청할 때 발동한다. 사람이 단계별로 직접 같이 만드는 수동 생성은 `harness-generator`, 이미 존재하는 하네스 개선은 `meta-harness`로 보낸다. **모든 후보 실체화는 자동 적용 금지 — 사용자 승인 게이트 통과 후에만 적용한다.**

**실행 모드**: 서브에이전트 + 하이브리드 — 후보 제안은 lens별 **병렬** 팬아웃(harness-proposer), 채점은 후보별 **병렬**(harness-evaluator), 도메인 분석·실체화는 **순차**(domain-analyst, harness-materializer). 모든 Agent 호출에 `model: "opus"`를 명시한다.

**연구 근거 (검증된 1차 출처 매핑)**

| 연구 개념 | 본 플러그인 적용 |
|-----------|------------------|
| ADAS — 에이전트를 코드로 정의, 아카이브 기반 메타 탐색 (arXiv 2408.08435) | 후보를 코드/모듈 spec으로 정의, 진화 라운드에 직전 후보 노출 |
| AgentSquare — 모듈러 탐색공간(Planning/Reasoning/Tool Use/Memory) + evolution·recombination (arXiv 2410.06153) | 디폴트 탐색공간·진화 연산자로 채택 (무제약 코드합성은 상위옵션) |
| AFlow — 코드 워크플로 MCTS + execution feedback, 비용 4.55% (arXiv 2410.10762) | 채점에 execution feedback(dry-run) + 정확도-비용 Pareto |
| MaAS — agentic supernet, 질의별 동적 자원할당, cross-dataset/backbone 전이 (arXiv 2502.04180) | 전이성을 도메인 무관성의 검증축으로, 라운드 비용 게이트 |
| Anthropic — workflows vs agents + 5 오케스트레이션 패턴, clean-context 서브에이전트 1~2k 토큰 요약 | 후보 조립 빌딩블록 + 산출 하네스의 서브에이전트 규약 |

> ※ 본 도구의 **디폴트 탐색은 AgentSquare식 경량 evolution/recombination**(Phase 5, ≤2라운드)이다. AFlow의 MCTS·MaAS의 supernet *자체*가 아니라 그 **평가신호**(정확도-비용 Pareto·전이성·dry-run feedback)를 차용한다 — 풀스케일 MCTS/supernet은 opt-in 지향점이다.

**정직한 주장 범위(반증 caveat)**: "자동 탐색이 모든 도메인에서 수동 설계를 무조건 이긴다"는 일반화는 적대적 검증에서 탈락했다(ADAS cross-domain·AgentSquare +17.2% 일반화 모두 refuted). 따라서 본 플러그인은 "특정 도메인·태스크에서 후보를 탐색·평가해 비용효율적 하네스를 찾는다"까지만 주장하고, 단일 정답·자동채점기가 없는 개방형 도메인에서는 LLM-as-judge 신뢰성 한계를 명시한다.

**Change History**

| Date | Change | Target | Reason |
|------|--------|--------|--------|
| 2026-06-10 | Initial build | All | 자동 탐색·Pareto 평가·승인 게이트형 하네스 생성 플러그인 신설 (deep-research 근거: ADAS/AFlow/AgentSquare/MaAS + Anthropic 빌딩블록). harness-generator(수동)·meta-harness(진단)와 보완 관계로 분리 |
