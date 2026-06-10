# 빌딩블록 (Building Blocks) — 탐색공간 카탈로그

후보 하네스를 조립하는 단위. harness-proposer가 후보를 제안할 때, harness-evaluator가 후보를 채점할 때 공통으로 참조하는 lookup. SKILL.md Phase 2·3의 보충 자료.

## 목차
1. [탐색공간 3축](#1-탐색공간-3축)
2. [모듈 축 — Planning/Reasoning/Tool Use/Memory](#2-모듈-축--planningreasoningtool-usememory)
3. [패턴 축 — Anthropic 5 ↔ harness-generator 6](#3-패턴-축--anthropic-5--harness-generator-6)
4. [실행모드 축](#4-실행모드-축)
5. [lens 카탈로그 (다양성)](#5-lens-카탈로그-다양성)

---

## 1. 탐색공간 3축

후보 하나 = (모듈 구성) × (패턴) × (실행모드)의 한 점. proposer는 배정된 lens가 미는 방향으로 이 3축에서 한 점을 고른다.

- **모듈 축** — 각 에이전트/단계가 어떤 역량(Planning/Reasoning/Tool Use/Memory)을 갖는가. (AgentSquare)
- **패턴 축** — 에이전트들이 어떻게 연결되는가(순차/병렬/라우팅/생성-검증/감독자). (Anthropic 5 ∪ harness-generator 6)
- **실행모드 축** — 팀(직접 통신) / 서브에이전트(결과 핸드오프) / 하이브리드.

## 2. 모듈 축 — Planning/Reasoning/Tool Use/Memory

AgentSquare(MoLAS, [arXiv 2410.06153](https://arxiv.org/abs/2410.06153))의 4모듈 + uniform IO. 후보 설계 시 각 에이전트가 어떤 모듈을 켜는지 명시한다.

| 모듈 | 역할 | 켜는 신호 |
|------|------|-----------|
| **Planning** | 큰 작업을 하위 단계로 분해·계획 | 다단계·의존성 강함 |
| **Reasoning** | 단계별 추론(CoT·debate·reflection) | 정답이 추론에 민감 |
| **Tool Use** | 외부 도구·API·검색 호출 | 외부 상태 의존 |
| **Memory** | 회차/단계 간 상태·스킬 누적 | 재실행·전이 필요 |

- **evolution** — 약한 모듈을 더 강한 구현으로 교체(예: Reasoning을 CoT→debate).
- **recombination** — 다른 후보의 우수 모듈을 이식(예: cand_2의 Memory를 cand_3에).

무제약 코드합성(ADAS)은 이 4모듈 밖의 임의 구조를 허용하지만 탐색비용이 비현실적이므로 **코드확장 opt-in 신호**("4모듈 밖 구조도 탐색"·"비표준/자유 구조 허용"·"코드 수준 자유 설계" 등 사용자 명시)가 있을 때만 연다. 열렸을 때 '대담한 구조' lens의 proposer는 design.json의 `custom_structure` 필드에 4모듈 밖 구조를 기술한다(닫혀 있으면 이 필드 생략 = 모듈러). **v0.1 기본 구현은 모듈러이며, 코드확장은 opt-in 경로**다.

## 3. 패턴 축 — Anthropic 5 ↔ harness-generator 6

두 카탈로그는 대부분 직접 매핑된다. proposer는 익숙한 쪽 이름을 쓰되 매핑을 인지한다.

| Anthropic 5패턴 ([building-effective-agents](https://www.anthropic.com/research/building-effective-agents)) | harness-generator 6패턴 | 적합 |
|------|------|------|
| prompt chaining | 파이프라인 | 순차 의존 강함 |
| routing | 전문가 풀 | 입력 종류별 분기 |
| parallelization (sectioning/voting) | 팬아웃/팬인 | 다각 분석 후 결합 |
| evaluator-optimizer | 생성-검증 | 품질 게이트 |
| orchestrator-workers | 감독자 | 동적 작업 분배 |
| *(없음)* | 계층적 위임 | 복잡 문제 재귀 분해 |

> 불일치: harness-generator의 **계층적 위임**은 Anthropic 5패턴에 명시적으로 없다. 후보가 이를 쓰면 "harness-generator 고유 패턴"으로 표기한다.

**복합 패턴:** 실전은 단일 패턴이 드물다 — 팬아웃+생성검증, 파이프라인+팬아웃 등. 복합은 기본 팀, 100% 독립 단계만 서브로 강등(하이브리드).

## 4. 실행모드 축

| 모드 | 통신 | 비용 | 적합 |
|------|------|------|------|
| **에이전트 팀** | 팀원 간 직접(SendMessage) + 공유 작업목록 | 큼 | 다각 분석/생성-검증 루프/감독자 |
| **서브에이전트** | 결과만 반환(clean context, 1~2k 토큰 요약) | 효율적 | 독립 병렬/단발 |
| **하이브리드** | Phase별 모드 명시 | 중간 | Phase 특성 차이 큼 |

**선택 기준:** "에이전트 간 실시간 발견 공유가 품질의 핵심인가?" → 그렇다면 팀, 아니면 서브. (clean-context 서브에이전트 규약은 Anthropic context-engineering 근거)

## 5. lens 카탈로그 (다양성)

proposer는 동일 프롬프트 N회가 아니라 **서로 다른 lens**로 spawn돼 Pareto front를 펼친다. 기본 3-lens(N=3):

| lens | 미는 방향 | 전형적 선택 |
|------|-----------|-------------|
| **최소 토큰비용** | 에이전트·단계 최소화, 모듈 최소 | 서브에이전트 + 파이프라인, Reasoning 경량 |
| **최대 품질** | 다각 검증·생성-검증 허용 | 팀 + 팬아웃/생성-검증, Reasoning 강화 |
| **균형 (Pareto knee)** | 품질/비용 무릎점 겨냥 | 하이브리드 + orchestrator-workers |

고가치(N=5) 추가 lens:

| lens | 미는 방향 |
|------|-----------|
| **대담한 구조** | ADAS식 비표준 구조(코드확장 opt-in 시) |
| **전이 우선** | Memory·일반화 모듈 강화로 cross-domain 견고성 |
