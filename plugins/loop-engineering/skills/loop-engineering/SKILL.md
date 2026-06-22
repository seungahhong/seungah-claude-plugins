---
name: loop-engineering
description: 검증 가능한 목표를 향해 작업을 자율 반복(loop)으로 완성하는 도메인 무관 멀티 에이전트 오케스트레이터. 사용자가 "통과할 때까지 반복해줘", "실행-검증-수정 루프로 끝까지", "실패하면 원인 진단하고 접근 바꿔가며 목표 달성할 때까지", "에이전트가 스스로 검증·개선하는 루프", "성공 기준 정하고 자율 반복으로 충족", "loop engineering으로 자동화", "이전 실패에서 배워 작업 산출물(코드·테스트·문서)의 같은 실수를 반복 않게 루프 메모리에 쌓으며 통과까지 반복", "이 빌드 그린 될 때까지 자율 루프"를 언급하며 한 작업을 목표가 통과할 때까지 반복 수행하려 할 때 발동한다. 실행 루프(Goal→Execute→Verify→Diagnose→Improve)와 지속학습 루프(Fail→Investigate→Verify→Distill→Consult)를 결합하고, 사람이 아니라 에이전트가 실패 원인을 진단해 다음 시도의 접근을 직접 작성하며, 검증된 교훈을 루프 메모리에 distill해 같은 실수를 반복하지 않는다. 명시적 중단조건(통과·최대 반복·무진전·예산)으로 무한 루프를 막는다. 발동하지 않는다 — 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선, 새 하네스/에이전트 팀 생성, 기획문서(PRD)·사용자 스토리 작성, 커밋 메시지·PR 리뷰, 일정 간격 반복 실행(native /loop), 진단·학습·비반복이 필요 없는 단순 목표 지향 자율 진행(native /goal), 단발성 한 번 수정(반복·검증 루프가 아닌 요청), settings.json 설정 변경.
---

# Loop Engineering — 검증 가능한 목표를 향한 자율 반복 오케스트레이터

한 작업을 **검증 가능한 목표가 통과할 때까지** 자율적으로 반복 수행한다. 사람이 매번 프롬프트를 고치는 대신,
에이전트가 실행하고 → 스스로 검증하고 → 실패하면 원인을 진단해 다음 접근을 직접 작성하고 → 검증된 교훈을
메모리에 쌓아 같은 실수를 반복하지 않으며 → 통과하면 종료한다. 이것이 "loop engineering"이다.

## 두 개의 루프

이 하네스는 두 루프를 한 사이클로 묶는다.

- **실행 루프** — ① 목표를 정한다 → ② 에이전트가 실행한다 → ③ 에이전트가 검증한다 → ④ 실패하면 다시 고친다 → ⑤ 통과하면 종료한다.
- **지속학습 루프** — 실패(기록) → 조사(원인 파악) → 검증(진단을 사실로 전환) → 정립(일반 규칙화) → 참조(정립된 규칙을 다시 참조).

핵심 전환: **사람이 프롬프트를 직접 작성하기보다, 에이전트가 개선 프롬프트를 작성하게 하는 것** — 루프를 구성하고,
명확한 목표를 전달하고, 스스로 테스트하게 하고, 실패하면 개선안을 쓰게 하고, 검증하고, 메모리에 쌓아두고,
**위 모든 과정을 계속 반복하기**.

> **전체 그림(factory model)**: loop engineering의 큰 그림은 6개 빌딩블록(automations·worktrees·skills·plugins/connectors·
> sub-agents·external memory)으로 *소프트웨어를 만드는 시스템*을 설계하는 것이다("하네스 한 층 위"). 이 하네스는 그중 **검증 루프
> 엔진**을 구현한다 — skills(하네스 자체)·sub-agents(maker/checker 분리)·external memory(loop-memory)가 *기본 구현*이고
> (sub-agents 레인은 실제로 검증 방법을 실행하는 강한 verifier로), automations·worktrees·connectors는 코어 흐름을 바꾸지 않는
> *선택 레인*이다. 매핑·근거는
> [references/loop-engineering-principles.md](./references/loop-engineering-principles.md) §8(여섯 빌딩블록 표).

## 경계 (먼저 읽고 발동 여부를 판단하라)

이 하네스는 **'주어진 작업을 검증 루프로 완성한다'**. 다음은 명시적으로 범위 밖이다.

- **하네스 자체 진단·개선** — 루트 CLAUDE.md/SKILL.md/agents/hooks의 결함을 trace로 진단·고도화하는 것은 범위 밖이다.
  loop-engineering은 *작업 산출물*(코드·문서 등)을 개선하지 *하네스*를 개선하지 않는다.
- **새 하네스/에이전트 팀 생성** — 범위 밖이다.
- **기획문서(PRD)·사용자 스토리 작성** — 개발 전 기획문서·사용자 스토리 산출은 범위 밖이다.
- **커밋 메시지·PR 리뷰** — 범위 밖이다. 커밋이 필요하면 별도 커밋 워크플로를 사용한다. (단, 검증 PASS *하류*의 opt-in act 레이어가 PR을 *열* 수는 있다 — PR *리뷰*가 아니라 검증된 결과의 행동이다. §7·마무리.)
- **일정 간격 반복 실행** — native `/loop`(N분마다 폴링)은 *시간 기반 재실행*이다. 이 하네스는 *목표 기반 자가수정 반복*이다. (단, 둘은 *합성*된다 — `/loop`·Desktop task·Cloud Routine이 발견 *프론트엔드*로 앞단에서 일을 찾아 목표를 만들고, 그 목표를 이 코어 루프 Phase 0로 넘길 수 있다. 자동화는 코어를 *대체*하지 않고 *앞에 붙는다*. references §7·§8.)
- **단발성 한 번 수정** — 반복·검증 루프가 필요 없는 one-off 요청.

경계가 모호하면 한 질문으로 확인한다 — "검증 가능한 목표를 정해 *통과할 때까지 자율 반복*하는 건가요, 아니면 *한 번만* 처리하면 되나요?"

> native `/goal`과의 관계: `/goal`은 Claude Code 기본의 목표 지향 자율 진행이다. 이 하네스는 그 위에 **명시적 검증기 설계 +
> 재시도 전 root-cause 진단 + 검증된 교훈의 지속학습 메모리 + 무진전 감지**를 구조화해 얹은 멀티 에이전트 버전이다.
> 단순 자율 진행이면 `/goal`로 충분하고, *진단·학습·비반복*이 필요한 반복 작업이면 이 하네스를 쓴다.

## 내재화 원칙 (모든 반복이 따른다)

- **검증기 우선** — 루프는 검증기만큼만 좋다. 시작 전에 관찰형 성공기준 + *실행 가능한* 검증 방법을 못 박는다.
- **자가 검증** — 통과 판정은 사람이 아니라 loop-verifier가 증거로 한다. 증거 없는 PASS 금지.
- **재시도 전 진단** — 실패하면 곧장 다시 시도하지 않는다. *다음 단계로 넘어가기 전에 원인을 파악*한다(failure-analyst).
- **에이전트가 개선 프롬프트를 쓴다** — 다음 반복의 접근을 사람이 아니라 에이전트가 작성한다.
- **최소 변경(반복당 한 가설)** — confound를 막기 위해 한 반복에선 가장 작은 변경 하나만.
- **지속학습 메모리(quality-gated, 게이트하되 폐기 금지)** — 검증된 교훈만 distill해 lessons.md에 쌓고, 다음 반복에 관련 규칙만 consult한다. raw trace는 보존. *순진한 distill은 성능을 악화시킬 수 있으므로*(연구 근거) verbatim rewrite보다 추상 통찰을 적고 가역적으로 관리하되, *raw-only가 최고라는 가설은 반박(0-3)됐으므로* 검증된 교훈은 반드시 distill한다 — consolidation 전면 폐기는 과교정이다.
- **명시적 중단조건** — 통과 / 최대 반복 / 무진전(같은 원인 반복) / 예산. 무한 루프를 구조적으로 막는다.
- **관찰 가능성·승인** — 시작 전 Goal Card 승인 게이트는 항상. 반복 중에는 매 회 verdict를 보고하고, gated 모드면 반복 사이에도 승인을 받는다. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **stay-the-engineer(사람이 엔지니어로 남는다)** — 루프가 좋아질수록 사람 쪽 결함이 *더 날카로워진다*. ① 검증은 사람 책임이고 PASS는 *주장*이지 *증명*이 아니다("verification is still on you"). ② 코드 산출 루프는 성공 선언 전 실제 diff를 읽고 "무엇이 왜 바뀌었나"를 확인한다(comprehension rot 방지 — green CI ≠ 구현 완료). ③ 루프를 *이해 가속*에 쓰는지 *이해 회피*에 쓰는지 스스로 점검한다(cognitive surrender 방지 — 자동화 불가). ④ 병렬은 사람이 리뷰할 수 있는 수까지만(orchestration tax). 이 넷은 자동화로 넘길 수 없는 사람의 통제점이다. (상세: [references/loop-engineering-principles.md](./references/loop-engineering-principles.md) §6·§8)

## 에이전트 팀

| 단계 | 에이전트 | 루프 역할 |
|------|----------|-----------|
| Goal | `goal-setter` | 검증 가능한 목표 + 실행 가능한 검증 방법 + 중단조건 설계 |
| Execute | `loop-executor` | 목표를 향한 1회 반복(메모리 consult + 직전 개선안 적용, 최소 변경) |
| Verify | `loop-verifier` | 검증 방법 실행 → 엄격 PASS/FAIL + 증거 |
| Investigate | `failure-analyst` | FAIL 시 root cause 진단(사실로 전환) + 다음 접근 작성 + 무진전 감지 |
| Distill/Consult | `memory-curator` | 검증된 교훈 distill → lessons.md, 관련 규칙 surface(consult), raw trace 보존 |

각 에이전트 정의는 `../../agents/{name}.md`에 있다. **모든 Agent 호출은 `model: "opus"`를 명시한다** — 진단·검증 추론 품질이 루프 수렴을 좌우한다.

## 참조 문서

- 루프 엔지니어링 원리·anti-pattern(comprehension rot·cognitive surrender·orchestration tax 포함)·검증기/중단조건 설계·**여섯 빌딩블록(factory model, §8)**: [references/loop-engineering-principles.md](./references/loop-engineering-principles.md)
- 루프 메모리 on-disk 포맷(goal.md / iterations.jsonl / lessons.md): [references/loop-memory-format.md](./references/loop-memory-format.md)
- 설계 근거 연구 dossier(출처·인용·신뢰도·caveat): [references/loop-engineering-research.md](./references/loop-engineering-research.md)

## 루프 메모리 배치

기본 `.claude/loop-memory/{goal-slug}/`(사용자 지정 가능)에 다음을 둔다. 문서 언어는 **한국어**.

```
.claude/loop-memory/{goal-slug}/
  goal.md            # 확정 Goal Card
  iterations.jsonl   # 반복별 raw trace (attempt·verdict·diagnosis) — append-only, 요약 금지
  lessons.md         # distill된 재사용 규칙 (Consult 대상)
```

같은 목표 슬러그로 다시 실행하면 lessons.md를 먼저 consult해 과거 실수를 반복하지 않는다(continual learning).

---

# 인터랙티브 플로우

## Phase 0 — 목표 설계 (Goal) · 승인 게이트

`goal-setter`를 호출해 모호한 요청을 **Goal Card**(slug·성공기준·검증 방법·중단조건·범위)로 변환한다.

**재실행 감지(호출 전)**: 요청에서 임시 slug를 도출해 `.claude/loop-memory/*` 중 정규화된 slug가 일치/동일 목표인 디렉토리가 있으면 그 `lessons.md` 요약을 goal-setter 입력에 포함한다(과거 교훈이 목표·검증기 *설계*에 반영되게 — continual learning을 실행뿐 아니라 재설계에도 적용).

```
Agent(
  subagent_type="goal-setter", model="opus",
  prompt="""
  [역할] 모호한 요청을 검증 가능한 목표(Goal Card)로 변환한다.
  [입력] 사용자 요청: {사용자 발화}
  [과거 교훈(rerun 시)] {lessons digest 또는 '없음(최초 실행)'}
  [규칙] 성공기준은 관찰형. 각 기준에 *실행 가능한* 검증 방법(명령/관찰)을 붙인다.
         중단조건(성공·최대 반복 N·무진전 M회·예산)과 범위(In/Out)를 명시한다.
         목표 한 줄을 소문자 kebab-case로 정규화한 slug를 Goal Card 최상단에 부여한다(메모리 디렉토리 키).
  [출력] slug를 포함한 Goal Card.
  """
)
```

Goal Card(slug 포함)를 사용자에게 보여주고 **승인 게이트**:

`[Phase 0] 목표·검증기·중단조건 확정 — 다음: 루프 시작(최대 N회, gated/auto). 진행할까요?`

여기서 자율 모드를 확정한다 — **auto**(중단조건까지 자율 반복, 매 회 verdict 보고) 또는 **gated**(반복 사이마다 승인). 기본 auto. 승인 전에는 루프를 시작하지 않는다(잘못된 검증기로 반복 비용을 낭비하지 않기 위함).

## Phase 1 — 루프 (Consult → Execute → Verify → Diagnose → Distill)

**초기화(1회, 오케스트레이터 책임)**: 승인된 Goal Card에서 `slug`·N(최대 반복, 기본 5)·M(무진전 임계, 기본 2)·예산을 읽어 이후 단계의 N·M·예산 placeholder에 그 확정값을 바인딩한다(이후 `n=1..N`, 무진전 M, 게이트 문구의 "최대 N회"가 실제 숫자로 렌더된다). 그다음:

1. `.claude/loop-memory/{slug}/`를 확정·초기화/로드한다. 같은 slug 디렉토리가 이미 있으면 새로 만들지 말고 재사용한다(없을 때만 생성).
2. 승인된 Goal Card 원문을 `{slug}/goal.md`로 **write**한다. 기존 goal.md가 있고 목표가 다르면 수정하지 말고 새 slug 분기를 권고한다(불변 규칙).
3. 이번 실행의 **run-id를 1개 발급**한다(기존 iterations.jsonl이 있으면 마지막 run 다음 순번, 없으면 1 또는 타임스탬프). 이후 모든 iterations.jsonl 줄과 lessons 역참조에 이 run-id를 전달한다.

각 반복 `n = 1..N`:

0. **Consult** — `memory-curator`로 이번 목표·직전 증상에 관련된 lessons.md 규칙 digest를 surface한다. **재실행이면 1회차(iter 1)부터** 과거 run의 교훈을 consult하고(continual learning), 같은 run 내 직전 반복의 next-approach·교훈은 2회차+에 적용한다. (digest를 이번 Execute 입력에 싣는다 — consult-before-execute.)
1. **Execute** — `loop-executor`(model:opus). 입력: Goal Card + consult digest + (2회차+) 직전 next-approach. 산출: Iteration Attempt(기계검증 증거 surface).
2. **Verify** — `loop-verifier`(model:opus). 입력: Goal Card + Attempt. 산출: **Verdict(PASS/FAIL/BLOCKED + 기준별 증거)**.
3. 분기:
   - **PASS** → (코드 산출 루프면 opt-in) **이해/머지 게이트** — 성공 종료 선언 전에 실제 diff(`git diff`)를 사람(또는 쓰기권한 없는 comprehension 서브에이전트)이 읽고 "무엇이 왜 바뀌었고 목표를 *구현*하는가"를 확인한다(green CI ≠ 구현 완료 — loop-verifier의 증거 기반 PASS 위에 사람의 *이해 확인*을 얹을 뿐, 대체하지 않는다). 이어 `memory-curator`로 execute·verify 줄을 iterations.jsonl에 append(run-id·ts 포함)하고 "무엇이 통과시켰는가"를 distill → **성공 종료**. (gated 모드면 이 게이트는 사람 승인과 합쳐진다.)
   - **FAIL** → `failure-analyst`(model:opus)로 root cause 진단 + 다음 접근 작성 + 무진전 판정(같은 root cause 누적 k/M). 이어 `memory-curator`로 execute·verify·diagnose 줄을 iterations.jsonl에 append하고 *확정된* 교훈만 distill(다음 반복이 consult하도록). 다음 반복 입력에 next-approach와 consult digest를 싣는다.
   - **BLOCKED**(검증 불가/검증 인프라 문제) → failure-analyst를 호출하지 **않는다**(환경 문제는 작업 결함이 아님). `goal-setter`를 재호출해 Goal Card 검증 방법을 보정하고(사용자 승인) 같은 반복 번호로 재검증한다. **이 반복은 무진전·최대 반복 카운트에 산입하지 않는다**(거짓 FAIL 방지).
4. **중단조건 점검** — 성공(PASS) / 반복 N 도달 / 무진전(**failure-analyst가 반환한 무진전 판정**을 단일 권위로 신뢰) / 예산 소진 중 하나면 멈춘다. 예산은 SDK 실행 시 Goal Card 예산값을 `max_turns`/`max_budget_usd` 하드캡으로 집행하고(에러 시 중단), 모델이 토큰/달러를 측정 못 하는 인터랙티브 실행에선 **최대 반복 N이 유일한 하드 경계**다(BLOCKED 반복 제외). BLOCKED는 중단조건이 아니라 Goal Card 보정 게이트다.
5. **보고** — 매 반복 후 1줄: `[Iter n] {PASS|FAIL|BLOCKED}: {핵심 증거/원인} — {계속|종료 사유}`. gated 모드면 다음 반복 전 승인을 받는다.

에이전트 호출 예(Consult → Execute → Verify → …):

```
# Consult (매 반복 직전)
Agent(subagent_type="memory-curator", model="opus",
  prompt="[메모리] .claude/loop-memory/{slug}/\n[consult 대상] 이번 목표·직전 증상\n관련 규칙만 관련성 순 상위 N개 digest로 surface하라(메모리 전체 투하 금지). 재실행이면 과거 run 교훈도 포함.")

# Execute
Agent(subagent_type="loop-executor", model="opus",
  prompt="[목표] {Goal Card}\n[교훈(consult digest)] {관련 규칙}\n[직전 개선안] {next-approach 또는 '없음'}\n[반복] {n}\n최소 변경 1개로 검증기를 통과시킬 시도를 하고, 기계검증 증거(종료코드·diff·카운트)와 무엇을 왜 바꿨는지 기록하라.")

# Verify
Agent(subagent_type="loop-verifier", model="opus",
  prompt="[목표·검증방법] {Goal Card}\n[이번 시도] {Attempt}\n검증 방법을 실제로 실행해 기준별 PASS/FAIL과 증거를 내라. 증거 없는 PASS 금지, 적대적으로. 검증 방법 실행 불가/증거 확보 불가면 FAIL이 아니라 BLOCKED로 분리하고 Goal Card 검증 방법 보정안을 제시하라.")

# (FAIL이면) Investigate
Agent(subagent_type="failure-analyst", model="opus",
  prompt="[목표] {Goal Card}\n[FAIL 증거] {Verdict}\n[이번/이전 trace] {iterations 발췌}\n[누적 진단] {직전 diagnose 줄들의 root_cause 목록 + 현재 same-cause 누적 k/M}\n증상이 아닌 root cause를 trace 증거로 확정하고, 다음 반복의 접근을 직접 작성하라. 같은 원인 {M}회면 무진전으로 판정해 구조 변경을 권고하라(이 판정이 오케스트레이터의 단일 무진전 권위다).")

# Distill + 반복 기록 (append)
Agent(subagent_type="memory-curator", model="opus",
  prompt="[메모리] .claude/loop-memory/{slug}/\n[run-id] {이번 run-id}\n[기록 대상] execute·verify(FAIL이면 diagnose 포함) 줄\n[distill 대상] {확정 진단 또는 PASS}\n각 줄을 run-id·ts와 함께 iterations.jsonl에 append하고(요약·삭제 금지, 원본 보존), 검증된 교훈만 lessons.md에 distill하라.")
```

## 마무리 — 결과 보고

루프가 멈추면(성공/중단) 다음을 요약 보고한다.

- **결과**: 성공(검증기 PASS) / 중단(사유: 최대 반복·무진전·예산).
- **반복 수**와 각 반복의 verdict 요약.
- **distill된 교훈**(lessons.md)과 메모리 경로 — 다음 실행에서 consult될 자산.
- 중단이 **무진전**이면 failure-analyst의 구조 변경 권고(목표 재정의·접근 전면 교체·사람 개입)를 함께 제시한다.
- (opt-in) **act 레이어** — 증거 기반 PASS와 이해/머지 게이트를 통과한 *뒤에만*, MCP connectors로 PR 열기·티켓 링크·채널 알림 등 실제 행동을 수행할 수 있다(검증 게이트 *하류*에만 — 자기보고 불신 보존). references §7.

보고 형식(최종): `[Loop 종료] {성공|중단:사유} — 반복 {n}/{N}, 교훈 {k}건 → .claude/loop-memory/{goal-slug}/`
