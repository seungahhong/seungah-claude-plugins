# loop-engineering

검증 가능한 목표를 향해 한 작업을 **자율 반복(loop)으로 완성**하는 도메인 무관 멀티 에이전트 하네스입니다.
사람이 매번 프롬프트를 고치는 대신, **에이전트가 실행 → 스스로 검증 → 실패 원인 진단 → 다음 접근 작성 → 검증된 교훈을
메모리에 distill → 통과할 때까지 반복**합니다. 이것이 "loop engineering"입니다.

## 두 개의 루프

- **실행 루프** — ① 목표를 정한다 → ② 에이전트가 실행한다 → ③ 에이전트가 검증한다 → ④ 실패하면 다시 고친다 → ⑤ 통과하면 종료한다.
- **지속학습 루프** — 실패(기록) → 조사(원인 파악) → 검증(사실로 전환) → 정립(일반 규칙화) → 참조(정립된 규칙 재참조).

핵심은 **사람이 프롬프트를 직접 쓰기보다 에이전트가 개선 프롬프트를 쓰게 하고, 검증된 교훈을 메모리에 쌓아
같은 실수를 반복하지 않으며, 위 과정을 계속 반복**하는 것입니다.

> **전체 그림(factory model)**: loop engineering의 큰 그림은 여섯 빌딩블록(automations·worktrees·skills·plugins/connectors·
> sub-agents·external memory)으로 *소프트웨어를 만드는 시스템*을 설계하는 것입니다. 이 하네스는 그중 **검증 루프 엔진**
> (sub-agents 분리 + 메모리 + 검증기)을 기본으로 구현하고, 나머지는 코어 흐름을 바꾸지 않는 선택 레인으로 둡니다. 그리고
> 루프가 좋아질수록 날카로워지는 사람-쪽 결함(코드 이해 부패·인지적 항복·리뷰 대역폭)을 막기 위해, **검증·이해·판단은 끝까지
> 사람이 쥡니다** — *"build it like someone who intends to stay the engineer, not just the person who presses go."*

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `loop-engineering` 플러그인을 활성화하면,
`loop-engineering` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `loop-engineering` | 오케스트레이터(진입점). 목표 설계(Goal Card) → 실행 → 검증 → 진단 → 메모리 distill의 루프를 중단조건까지 자율 반복하며, 각 단계에서 전용 에이전트(goal-setter / loop-executor / loop-verifier / failure-analyst / memory-curator)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| Goal | `goal-setter` | 모호한 요청 → 검증 가능한 목표(관찰형 성공기준 + 실행 가능한 검증 방법 + 중단조건) |
| Execute | `loop-executor` | 목표를 향한 1회 반복 (메모리 consult + 직전 개선안 적용, 최소 변경) |
| Verify | `loop-verifier` | 검증 방법 실행 → 엄격 PASS/FAIL + 증거 (적대적, 증거 없는 PASS 금지) |
| Investigate | `failure-analyst` | FAIL 시 root cause 진단(사실로 전환) + 다음 접근 작성 + 무진전 감지 |
| Distill/Consult | `memory-curator` | 검증된 교훈 distill → lessons.md, 관련 규칙 surface, raw trace 보존 |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- 검증 가능한 목표를 정해 **통과할 때까지 자율 반복**으로 완성하고 싶을 때
- 실패하면 **원인을 진단해 접근을 바꿔가며** 목표에 수렴시키고 싶을 때
- 회차를 거듭하며 **같은 실수를 반복하지 않도록 메모리를 누적**하고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖)**
- 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선 — 이 하네스는 *작업 산출물*을 개선하지 *하네스*를 개선하지 않는다
- 새 하네스/에이전트 팀 생성
- 기획문서(PRD)·사용자 스토리 작성
- 커밋 메시지·PR 리뷰 — 커밋이 필요하면 별도 커밋 워크플로를 사용한다 (단, 검증 PASS 하류의 opt-in act 레이어가 PR을 *열* 수는 있습니다 — PR *리뷰*가 아니라 검증된 결과의 행동)
- *시간 간격* 반복 실행(폴링) → native `/loop`
- 진단·학습·비반복이 필요 없는 *단순 목표 지향 자율 진행* → native `/goal`
- 반복·검증 루프가 필요 없는 단발성 처리 → 일반 요청

> native `/goal`과의 관계: `/goal`은 기본 제공 목표 지향 자율 진행입니다. 이 하네스는 그 위에 **검증기 설계 +
> 재시도 전 root-cause 진단 + 지속학습 메모리 + 무진전 감지**를 멀티 에이전트로 구조화해 얹은 버전입니다.

## 진행 방식

| Phase | 단계 | 핵심 산출물 |
|-------|------|-------------|
| 0 | 목표 설계 (Goal) | Goal Card (성공기준·실행 가능한 검증 방법·중단조건·범위 In/Out) — 승인 게이트 |
| 1 | 루프 (Execute→Verify→Diagnose→Distill) | 반복별 verdict·진단·distill된 교훈, 중단조건까지 자율 반복 |

- 시작 전 Goal Card **승인 게이트**(잘못된 검증기로 반복 비용을 낭비하지 않기 위함). 여기서 자율 모드(**auto** 또는 **gated**)를 확정합니다.
- 매 반복 후 `[Iter n] {PASS|FAIL}: {증거/원인} — {계속|종료}` 1줄 보고. gated 모드면 반복 사이마다 승인.
- 중단조건: **통과 / 최대 반복(기본 5) / 무진전(같은 원인 M회, 기본 2) / 예산** — 무한 루프를 구조적으로 차단.

## 루프 메모리

기본 `.claude/loop-memory/{goal-slug}/`에 누적됩니다.

- `goal.md` — 확정 Goal Card
- `iterations.jsonl` — 반복별 raw trace (append-only, 요약 금지)
- `lessons.md` — distill된 재사용 규칙 (다음 실행에서 consult)

같은 목표 슬러그로 재실행하면 과거 교훈을 먼저 참조해 같은 실수를 반복하지 않습니다(continual learning).

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger)와 발동하면 안 되는 경우
(should-not-trigger — 하네스 진단/개선·하네스 생성·PRD·커밋/리뷰·native `/loop`·단발성 처리)를 정의해 트리거 정확도를 점검합니다.
