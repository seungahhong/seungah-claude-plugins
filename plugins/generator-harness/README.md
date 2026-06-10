# generator-harness

도메인 무관 멀티 에이전트 하네스(에이전트팀 + 스킬 + 오케스트레이터)를 **자동으로 탐색·평가·생성**하는 Claude Code 메타 플러그인입니다. 사용자가 도메인 요구를 주면, 후보 하네스 여러 개를 제안하고 **정확도-토큰비용 Pareto + 도메인 전이성**으로 채점한 뒤, **사용자 승인**을 거쳐 최적 후보만 실제 파일로 실체화합니다.

자동 에이전트 설계 연구(ADAS, AFlow, AgentSquare, MaAS)와 Anthropic의 컨텍스트/오케스트레이션 모범사례에 근거합니다.

## 설치

```bash
claude plugin add seungahhong/seungah-claude-plugins
```

## 스킬

| Skill | Command | 설명 |
|-------|---------|------|
| Generator Harness | `/generator-harness` | 후보 하네스 자동 탐색 → Pareto 채점 → 승인 → 실체화 진입 오케스트레이터 |
| Harness Search | `/harness-search` | 모듈러 탐색공간에서 후보 하네스 제안 + evolution/recombination 방법론 |
| Harness Eval | `/harness-eval` | 평가셋 구축 + Pareto(품질×비용) 채점 + 전이성 측정 방법론 |

## 언제 쓰나 — 그리고 언제 다른 도구를 쓰나

`generator-harness`는 **자동 탐색·채점 기반 생성**에 특화되어 있습니다.

| 원하는 것 | 쓸 도구 |
|-----------|---------|
| 후보를 자동 탐색·채점해 **최적 하네스를 뽑아** 만들기 | **`generator-harness`** (본 플러그인) |
| 사람이 단계별로 **직접 같이** 하네스 만들기 | `harness-generator` |
| **이미 있는** 하네스의 결함 진단·개선 | `meta-harness` |
| **단일 스킬** 하나 작성·벤치마크 | `skill-creator` |

## 사용법

만들고 싶은 도메인/워크플로우를 설명하며 호출합니다.

```
/generator-harness
```

예시 입력:

> "리서치 보고서 작성 도메인용 하네스를 근거 기반으로 자동 탐색해서, 후보 몇 개 점수 매기고 비용 대비 제일 나은 걸로 만들어줘."

또는 자연어로: "최적 하네스 탐색해서 생성해줘", "하네스 후보들 Pareto로 비교·채점해줘", "이 도메인 하네스를 자동 설계·평가해서 실체화해줘".

## 동작 — 8단계 자동 탐색·생성

| Phase | 단계 | 하는 일 |
|-------|------|---------|
| 0 | 현황 감사 | 기존 하네스/에이전트 충돌·재실행 여부 자동 판별 |
| 1 | 도메인 분석 + **평가셋** | 도메인 spec + 대표 평가 프롬프트·assertion + Pareto 축 + 전이 시나리오 구축 (domain-analyst) |
| 2 | 탐색공간 확정 | 모듈러(Planning/Reasoning/Tool Use/Memory) × 패턴 × 실행모드, 후보 수 N·라운드 예산 결정 |
| 3 | 후보 제안 | lens별 병렬 팬아웃으로 후보 하네스 설계 N개 제안 (harness-proposer) |
| 4 | 채점 | 후보별 정확도-비용 Pareto + 전이성 + dry-run 채점, Pareto frontier 산출 (harness-evaluator) |
| 5 | 진화(선택) | 합격 후보 없으면 Pareto-best를 recombination/mutation해 1라운드 더 (비용 상한) |
| 6 | **승인 게이트** | Pareto frontier·추천안·근거(why)를 제시하고 사용자 선택 (자동 실체화 금지) |
| 7 | 실체화 | 승인 후보를 agents/skills/orchestrator 파일로 작성 (harness-generator 규약 재사용) + 구조 검증 |
| 8 | 이력/진화 | 후보·점수·결정을 기록(재실행·전이용), 생성 하네스 CLAUDE.md에 변경 이력 |

## 핵심 차별점

- **단일 정확도가 아니라 Pareto** — 품질만이 아니라 토큰비용까지 동시에 본다(AFlow·MaAS 근거).
- **전이성 = 도메인 무관성 검증** — 인접 도메인/모델로 옮겨도 성능을 유지하는지 측정한다(MaAS 근거).
- **승인 게이트 + 비후퇴** — 자동 생성물을 사람이 승인하기 전엔 실체화하지 않는다(meta-harness와 동일 DNA).
- **정직한 주장 범위** — "모든 도메인에서 수동 설계를 이긴다"고 주장하지 않는다(해당 일반화는 검증에서 탈락).

## 산출물

승인된 최적 후보가 대상 위치에 아래 구조로 실체화됩니다(harness-generator와 동일 형식).

```
{harness-root}/
  agents/{agent}.md            # 에이전트 정의 (모두 model: "opus")
  skills/{step}/SKILL.md       # 단계별 스킬
  (오케스트레이터 스킬)         # 전체 흐름 진입점
  CLAUDE.md                    # 하네스 포인터 + 변경 이력
```

탐색 과정의 후보·점수·결정 이력은 `.claude/_workspace/{run}/`에 보존되어 재실행·전이에 쓰입니다.

## 라이선스

MIT
