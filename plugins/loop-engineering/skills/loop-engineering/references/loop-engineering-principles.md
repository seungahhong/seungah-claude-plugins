# Loop Engineering — 원리 · 검증기/중단조건 설계 · anti-pattern

> 이 문서는 loop-engineering 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.

## 1. 무엇이 loop engineering인가

프롬프트 엔지니어링은 *한 번의 입력*을 다듬는다. 컨텍스트 엔지니어링은 *모델 주변에 채울 정보*를 다듬는다.
**loop engineering은 에이전트가 도는 *반복 루프 그 자체*를 설계한다** — 목표·실행·검증·진단·개선·메모리·중단조건을.

전환점은 이것이다: **사람이 프롬프트를 직접 작성하기보다, 에이전트가 프롬프트를 작성하게 해야 하는 시점.**
루프를 구성하고 → 명확한 목표를 주고 → 스스로 테스트하게 하고 → 실패하면 개선 프롬프트를 쓰게 하고 →
개선 결과를 검증하고 → 다음에 실패하지 않도록 메모리에 쌓고 → **위 과정을 계속 반복**한다.

> **포지셔닝 — 레버리지가 위로 이동한다.** prompt → context → harness → **loop** 순으로 레버리지 지점이 올라간다.
> loop engineering은 "하네스 한 층 위"에 있다 — *타이머로 돌고, 헬퍼를 띄우고, 스스로를 먹인다*("sits one floor above the
> harness ... runs on a timer, spawns little helpers, and feeds itself", Osmani). 이 전환의 정식 표현은 Boris Cherny(head of
> Claude Code): *"I don't prompt Claude anymore. I have loops running that prompt Claude ... My job is to write loops."*
> 주의 — 이건 일이 *쉬워졌다*는 뜻이 아니다. **"loop 설계는 prompt engineering보다 더 *어렵다*, 더 쉬운 게 아니다 — 레버리지
> 지점이 옮겨갔을 뿐"**(Osmani). prompt·context engineering은 사라지지 않고 *루프의 매 turn 안에* 그대로 보존된다 —
> loop engineering은 그것들을 *대체*하지 않고 *감싼다*. (근거: addyo.substack.com/p/loop-engineering, productmarketfit.tech Cherny 인용 — research dossier §9.)

## 2. 두 개의 루프

### 실행 루프 (한 작업을 통과시키는 사이클)
1. **목표를 정한다** — 검증 가능한 단일 목표.
2. **에이전트가 실행한다** — 목표를 향한 최소 변경 1회.
3. **에이전트가 검증한다** — 검증 방법을 실제로 돌려 PASS/FAIL.
4. **실패하면 다시 고친다** — 단, *원인을 먼저 파악한 뒤*.
5. **통과하면 종료한다** — 중단조건 충족 시에도 종료.

### 지속학습 루프 (루프가 회차마다 똑똑해지는 사이클)
- **실패(Fail)** — 실수를 하고 *기록*한다.
- **조사(Investigate)** — 다음 단계로 넘어가기 전에 *원인을 파악*한다.
- **검증(Verify)** — 진단을 *확인된 사실*로 전환한다.
- **정립(Distill)** — 검증 결과를 *일반적인 규칙*으로 정리한다.
- **참조(Consult)** — 규칙을 다시 도출하는 대신 *이미 정립된 규칙을 참고*한다.

두 루프는 한 사이클로 맞물린다 — 실행 루프의 "검증/고치기"가 곧 지속학습 루프의 "조사/검증/정립"을 낳고,
정립된 규칙은 다음 실행 루프의 "실행"에서 참조된다.

## 3. 좋은 루프의 7원칙

1. **검증기 우선(verifier-first)** — 루프는 검증기만큼만 좋다. 관찰형 성공기준 + *실행 가능한* 검증 방법을 시작 전에 못 박는다. 검증기가 약하면 거짓 PASS로 잘못 종료하거나, 무엇이 통과인지 몰라 영원히 돈다.
2. **자가 검증(self-verification)** — 통과 판정을 사람이 아니라 에이전트가, 증거로 한다. 추정 PASS 금지.
3. **재시도 전 진단(diagnose-before-retry)** — 실패하면 곧장 다시 시도하지 않는다. 증상이 아닌 root cause를 먼저 확정한다.
4. **에이전트가 개선안을 쓴다(agent-authored next step)** — 다음 반복의 접근을 사람이 아니라 에이전트가 작성한다.
5. **최소 변경(one hypothesis per iteration)** — 한 반복에 가장 작은 변경 하나. 변경이 섞이면 원인 격리가 불가능(confound).
6. **지속학습 메모리 — 단, quality-gated(continual learning, fragile)** — 검증된 교훈만 distill해 쌓고 다음에 관련 규칙만 consult한다. 같은 실수를 두 번 하지 않는 것이 루프의 복리 효과다. **단, 순진한 distill은 성능을 *악화*시킬 수 있다**(§6 anti-pattern, faulty-memory 연구). 그래서 distill은 자유로운 자기개선 엔진이 아니라 *검증 게이트가 달린 fragile 메커니즘*으로 다룬다 — verbatim rewrite보다 추상 통찰을 적고, raw 원본을 경쟁 baseline으로 보존하며, 나쁜 규칙은 폐기·롤백 가능해야 한다.
7. **명시적 중단조건(explicit stopping)** — 통과·최대 반복·무진전·예산. 무한 루프와 비용 폭주를 구조적으로 막는다. (검증 가능한 목표·하드 중단·메모리가 없으면 루프는 "그냥 cron job"이다 — Osmani.)

## 4. 검증기(verifier) 설계

> 근거: "잘 설계된 루브릭이 모델보다 더 많은 일을 한다. 자가수정은 환경 피드백이 정직할 때만 의미가 있다"(Lance Martin).
> 검증기가 약하면 좋은 모델이라도 *확신에 차서 틀린 루프*가 된다. 검증기 품질이 모델 능력보다 한계 병목이다.

- **generator/checker 분리(핵심)**: 만드는 에이전트(`loop-executor`)와 판정하는 에이전트(`loop-verifier`)를 *다른 컨텍스트로 분리*한다. 같은 컨텍스트에서 자기 산출물을 평가하면 "확신에 차서 자기 작업을 칭찬"하는 편향이 생긴다(Anthropic harness-design). self-critique 금지. 회의적인 독립 평가자를 튜닝하는 게 생성자를 자기비판적으로 만드는 것보다 쉽다. (`/goal`은 이를 별도 Haiku 평가자로 구조적으로 구현한다.)
- **기계검증 증거를 출력에 surface**: 평가자가 transcript만 보는 경우(`/goal`)를 대비해, 실행자는 테스트 종료코드·diff·카운트 같은 *기계검증 가능한 증거*를 출력에 드러내야 판정이 자기보고가 아닌 근거를 갖는다. 본 하네스의 `loop-verifier`는 한 발 더 나아가 검증 방법을 *실제로 실행*하는 강한 버전이다.
- **실행 가능성**: 각 성공기준은 "어떻게 확인하나"를 *실제로 돌릴 수 있는* 방법으로 가져야 한다 — 명령의 종료코드, 출력에 특정 문자열, 테스트 그린, 파일/심볼 존재, HTTP 200, 산출물의 관찰 가능한 속성.
- **관찰형만**: "좋다 / 자연스럽다 / 직관적이다"는 판정 불가 → 관찰형으로 환산하거나 제외.
- **기준별 분해**: 큰 목표를 C1, C2…로 쪼개 각각 PASS/FAIL을 내면 진단 표적이 좁아진다.
- **적대성**: 검증기는 통과를 의심한다. 먼저 실패할 이유를 찾고, 못 찾을 때만 PASS.
- **검증 인프라 ≠ 작업 결함**: 검증 방법 자체가 안 돌면(환경 문제) 작업 실패와 분리한다(거짓 FAIL 방지).
- **자동 불가 시**: 정말 자동 검증이 불가능하면 사람이 판정할 체크리스트로 대체하고 "수동 검증"임을 명시(자율 신뢰도 한계 표시).

## 5. 중단조건(stopping) 설계

좋은 중단조건은 **출력만으로 확인 가능**해야 하며, 내구적 조건은 보통 3요소를 갖는다(/goal docs):
① **측정 가능한 end state**(테스트 결과·빌드 종료코드·파일 수·빈 큐), ② 그것을 **어떻게 증명하는지 명시한 체크**("npm test가 0 종료", "git status가 clean"), ③ **바뀌면 안 되는 제약**("다른 테스트 파일은 수정 금지"). goal-setter의 Goal Card가 이 형태를 따른다.

- **성공**: 모든 성공기준 PASS — 유일한 "좋은" 종료.
- **최대 반복(N)**: 기본 5. 작업 난도·예산에 따라 조정. 도달 시 멈추고 부분 결과·교훈을 보고. (조건에 "or stop after N turns"를 넣어도 되지만 이는 *모델 판단*이지 하드 정지가 아니다 — 보장된 경계가 필요하면 SDK `max_turns`(도구 사용 turn만 카운트)·`max_budget_usd` 하드 캡을 쓴다.)
- **무진전(no-progress)**: 같은 root cause가 M회(기본 2) 반복되면 단순 재시도를 멈춘다. 같은 곳을 더 돌아도 통과하지 못한다 — 구조 변경(목표 재정의·접근 전면 교체·사람 개입)이 답이다.
- **예산**: 토큰/시간/달러 상한. 기본값은 보통 "무제한"이라 캡은 opt-in 안전장치다. 초과 시 멈추고 현황 보고.

### 이해/머지 게이트 — green CI ≠ 구현 완료 (코드 산출 루프, opt-in)

검증기 PASS는 *기계적 통과*지 *구현 완료의 증명*이 아니다 — 에이전트는 **기능을 구현하지 않고도 테스트를 통과**시킬 수 있다
(테스트를 약화시키거나, 빈 구현으로 우회하거나, 무관한 변경으로 초록을 만든다). 그래서 코드를 산출하는 루프는 성공 종료 선언 전에
실제 diff(`git diff main..<branch>`)를 **사람(또는 쓰기 권한 없는 comprehension 서브에이전트)이 읽고** "무엇이 왜 바뀌었고 그게
목표를 *구현*하는가"를 확인하는 게이트를 옵션으로 둔다. 이것은 loop-verifier의 증거 기반 PASS를 *대체*하지 않고 그 위에 사람의 이해
확인을 *얹는다*. (근거: Osmani "Verification is still on you ... 'done' is a claim and not a proof ... your job is to ship code
you confirmed works" — research dossier §9.)

### 병렬 maker와 review bandwidth (opt-in)

한 목표에 maker를 둘 이상 병렬로 돌릴 때는 ① **git worktree로 격리**(`--worktree` / 서브에이전트 `isolation: worktree`)해
체크아웃 충돌을 원천 차단하고(상태를 가진 MCP 서버도 worktree별 격리), ② **동시 maker 수를 사람이 실제로 코드리뷰할 수 있는 수로
제한**한다("the right number of parallel agents is how many you can actually code review properly" — 실무 상한 ~4–5, 그 이상은
원격 실행+리뷰가 병목). worktree는 *기계적* 충돌만 없앨 뿐 **review bandwidth가 진짜 상한**이다(orchestration tax, §6). 기본
흐름은 단일 직렬 maker이며, 이 레인은 사용자가 병렬을 택할 때만 활성화된다.

## 6. anti-pattern (피해야 할 것)

- **검증기 없는 루프** — "잘 됐나?"를 사람이 매번 눈으로 보는 루프는 loop engineering이 아니다.
- **진단 없는 재시도** — 같은 실패를 원인도 모른 채 다시 시도(가장 흔한 실패).
- **거대 변경** — 한 반복에 여러 가설을 한꺼번에 → 실패해도 원인을 못 가린다.
- **메모리 미적재** — 회차마다 같은 실수를 반복. distill/consult가 없으면 루프가 똑똑해지지 않는다.
- **순진한 distill(역효과 메모리)** — 검증 게이트 없이 경험을 텍스트 규칙으로 마구 distill하면 성능이 *오히려 악화*된다. faulty-memory 연구: GPT-5.4가 메모리 없이 100% 풀던 문제가 *자기 정답에서* consolidate한 뒤 54%로 붕괴("trajectory는 완벽한데 rewrite 단계가 망가뜨린다"). CL-Bench: 전용 메모리 시스템보다 순진한 ICL이 총합 성능이 낫다. → distill은 검증된 것만, 추상 통찰 우선, raw 보존, 가역적으로(§3 원칙 6). *단, consolidation 전면 폐기도 틀렸다*("raw-only가 최고"는 반박 0-3) — 핵심은 quality-gated distillation.
- **요약으로 진단** — raw trace를 버리고 요약만 남기면 root cause 증거가 사라진다. trace는 보존, 교훈만 distill.
- **무한 루프** — 중단조건 부재. 통과 못 하는 목표를 영원히 돈다.
- **낙관 PASS** — 증거 없이 "통과한 것 같다"로 종료.
- **목표 드리프트** — 반복을 거듭하며 검증기와 무관한 변경으로 새는 것.

### 사람-쪽 결함 (루프가 *좋아질수록* 더 날카로워진다)

기계 검증을 아무리 잘해도 막지 못하는, 자율성이 커질수록 *커지는* 세 결함이다. 이 하네스의 stay-the-engineer 원칙이 겨냥한다.

- **comprehension rot(이해 부패)** — 루프가 사람이 안 읽은 코드를 빨리 칠수록 "존재하는 것"과 "사람이 이해하는 것"의 격차가 커진다.
  매끄러운 루프는 이 격차를 *더 빨리* 키운다. 완화: merge/성공 종료 전 diff를 *읽고* "무엇이 왜 바뀌었나"를 한 줄로 explain-back
  하게 한다(침묵 승인 버튼 금지). (근거: Osmani comprehension debt; Anthropic skill-formation RCT 52명 — *수동* "그냥 되게 해줘"
  위임이 이해도를 가장 크게 떨어뜨림(AI 보조군 이해 퀴즈 ~17%p↓). "Making code cheap to generate doesn't make understanding cheap to skip.")
- **cognitive surrender(인지적 항복)** — 루프가 알아서 돌면 의견 형성을 멈추고 주는 대로 받게 된다. 같은 행동(루프 설계)이 *이해를
  가속*하는 데 쓰면 약, *이해를 회피*하는 데 쓰면 독이다 — 루프는 그 차이를 모른다, 사람만 안다. 완화: 자동화 불가능한 operator intent
  self-check("이 루프를 *이해를 더 빨리 하려고* 쓰는가, *피하려고* 쓰는가?"). 시스템 안전장치가 아니라 *사람이 쥔 통제점*이다.
- **orchestration tax 무시** — review bandwidth가 병렬의 한계다. agent 수는 생산자, review 속도는 소비자이고 시스템 처리량은
  정확히 *리뷰 단계* 처리량과 같다. 리뷰 가능 수를 넘겨 agent를 늘리면 얕은 리뷰(=cognitive surrender)로 샌다. 완화: 동시 루프/agent를
  사람이 제대로 리뷰할 수 있는 수로 캡하고, 리뷰는 한 자리에서 배치로(매번 cold reload 비용 회피).

> 한 줄 정리: **검증·이해·판단·병렬 상한은 자동화로 넘길 수 없다.** *"Build the loop. But build it like someone who intends to
> stay the engineer, not just the person who presses go."*(Osmani)

## 7. Claude Code에서의 실행 토대

- **`/goal`(native)** — 기본 제공 목표 지향 자율 진행. 이 하네스는 그 위에 검증기 설계·재시도 전 진단·지속학습 메모리·무진전 감지를 멀티 에이전트로 구조화해 얹는다.
- **`/loop`(native)** — *시간 간격* 재실행(폴링). 이 하네스의 *목표 기반 자가수정 반복*과 구분된다.
- **subagent(model:opus)** — 실행/검증/진단/메모리를 역할별 에이전트로 분리해 각자 한 가지를 잘하게 한다.
- **파일 기반 메모리** — `.claude/loop-memory/`에 trace(원본)와 lessons(distill)를 분리 보관해 회차·세션을 넘어 학습을 누적한다.
- **자동화 프론트엔드(opt-in, 선택적 합성)** — 코어 루프는 *목표 기반*(사람이 목표를 준다)으로 유지하되, 그 *앞단*에 스케줄 티어를
  합성할 수 있다: `/loop`(세션 스코프 간격 폴링), Desktop task(로컬 파일 접근), Cloud Routine(머신 꺼져도/세션 없이). 스케줄된 triage
  프롬프트가 일을 *발견*해 상태/triage-inbox 파일에 적고, 발견된 목표를 Phase 0로 넘긴다. 즉 native `/loop`는 이 자가수정 루프를
  *대체*하는 게 아니라 그 *앞에 합성*된다(시간 기반 재실행 = 발견 프론트엔드, 목표 기반 자가수정 = 코어). 스케줄 티어 자체의 런타임
  폭주 가드(예: 작업 자동 만료·`CLAUDE_CODE_DISABLE_CRON` 킬 스위치 — Claude Code scheduled-tasks 공식 docs 기준; 구체 만료
  기간·플래그명은 버전 가변이라 docs로 확인)를 함께 켜 둔다.
- **act 레이어(connectors, opt-in)** — 증거 기반 PASS와 이해/머지 게이트(§5)를 통과한 *뒤에만*, MCP connectors로 PR 열기·티켓
  링크·채널 알림 같은 실제 행동을 옵션으로 수행한다("here is the fix"에 그치는 에이전트 vs CI 그린 시 스스로 PR을 여는 루프). 반드시
  검증 게이트 *하류*에 두어 자기보고 불신 원칙을 보존한다.

## 8. 여섯 빌딩블록 (factory model) — 각 레인이 막는 자율성 결함

loop engineering의 전체 그림은 한 작업을 통과시키는 단일 루프보다 크다 — Osmani는 그것을 **factory model**(소프트웨어를 *만드는*
시스템)로 본다. 루프는 6개의 독립 토글 가능한 레인으로 구성되고, **각 레인은 자율 운용의 *서로 다른* 결함 하나를 막는다.**

| 빌딩블록 | 막는 결함 | Claude Code 1차 매핑 | 본 하네스 |
|----------|-----------|----------------------|-----------|
| **automations**(heartbeat) | 사람이 매번 수동 확인 / 루프가 한 번 돌고 끝남 | `/loop`(세션 간격)·Desktop task·Cloud Routine·`/goal`(매 turn 별도 Haiku 평가자) | 선택 레인(앞단 합성, §7) |
| **worktrees**(병렬 격리) | 병렬 maker의 파일 충돌(같은 파일 동시 수정) | `git worktree`·`--worktree`·서브에이전트 `isolation: worktree`·`.worktreeinclude`·`worktree.baseRef` | 선택 레인(병렬 시, §5) |
| **skills**(외부에 적힌 의도) | intent debt — 매 세션 cold start, 빈 의도를 *자신감 있는 추측*으로 메움 | `SKILL.md`(name/description 트리거 + `scripts/`·`references/`) | **체현됨** — 본 하네스 자체가 skill(+lessons.md로 교훈 codify) |
| **plugins/connectors**(act 레이어) | 파일시스템만 보는 에이전트 — 제안만 하고 행동 못 함 | MCP servers/connectors, 플러그인으로 번들 | 선택 레인(PASS 하류, §7) |
| **sub-agents**(maker≠checker) | 자기 산출물을 너무 후하게 채점("too nice grading its own homework") | `.claude/agents/*.md`(역할별 시스템 프롬프트·도구권한·모델) | **구현됨** — loop-executor(maker) / loop-verifier(checker) 분리 |
| **external memory**(디스크 상태) | run 사이 컨텍스트 소실 — "the agent forgets, the repo doesnt" | 대화 밖 on-disk 마크다운(또는 MCP 보드) | **구현됨** — `.claude/loop-memory/{slug}/`(goal·iterations·lessons) |

핵심 정리:

- **본 하네스가 이미 구현/체현하는 레인은 3개다** — skills(이 하네스 자체가 SKILL.md로 루프 절차·검증 원칙을 외부화하고 검증 교훈을
  lessons.md로 codify), sub-agents(generator/checker 분리 = loop-executor/loop-verifier), external memory(loop-memory). 특히
  sub-agents 레인은 `/goal`식 신선한 checker를 *실제로 검증 방법을 실행*하는 강한 verifier(loop-verifier)로 구현한다(verifier-first
  원칙, §4). 이것이 "현재 기능 = 기본".
- **automations · worktrees · connectors는 선택 add-on 레인**이다. 코어 흐름(Phase 0 목표 게이트 → Phase 1 자가수정 루프)을
  바꾸지 않고, 사용자가 발견 자동화·병렬·자동 행동을 원할 때만 켠다.
- **"the state file is the spine of the whole thing"** — 상태 파일이 전체의 등뼈다. 본 하네스에선 `goal.md`/`iterations.jsonl`/
  `lessons.md`가 그 등뼈다(요약·삭제 금지 — [loop-memory-format.md](./loop-memory-format.md)).

> **그러나 — factory가 좋아질수록 사람 쪽 결함은 *더 날카로워진다*.** 여섯 레인이 자율성을 키울수록 §6의 세 결함(comprehension
> rot · cognitive surrender · orchestration tax)이 커진다. 그래서 이 하네스의 제1 운용 원칙은 **stay-the-engineer**다 —
> 검증·이해·판단·병렬 상한은 자동화로 넘길 수 없는, 사람이 *엔지니어로 남기 위한* 통제점이다.

## 참고 문헌

출처별 구체 인용·신뢰도·caveat·반박 주장은 **[loop-engineering-research.md](./loop-engineering-research.md)**(deep-research dossier: 1차 라운드 23소스→110주장→23 confirmed; **2026-06-23 심화 라운드** 13소스→78 load-bearing 주장→62 confirmed/16 killed — §9 여섯 빌딩블록·세 결함)에 정리되어 있고, 이 문서의 원칙과 상호 참조된다.

1차(primary): Claude Code `/goal`·`worktrees`·`scheduled-tasks`·`sub-agents`·Agent SDK `agent-loop`·`memory` 공식 문서 · Anthropic "Harness design for long-running application development"(generator/checker 분리)·"Agent Skills"·skill-formation RCT(comprehension ~17%p↓) · CL-Bench(arXiv:2606.05661) · AgentCL(arXiv:2606.02461) · SEA(arXiv:2604.07269) · faulty-memory(dylanzsz.github.io/faulty-memory) · OpenAI parameter-golf.
2차/blog(verbatim 교차검증): **Addy Osmani "Loop Engineering"(addyo.substack.com/p/loop-engineering — 정의·여섯 빌딩블록·세 결함·worked example·"stay the engineer")** · Osmani orchestration-tax·comprehension-debt·intent-debt·code-agent-orchestra·agentic-code-review·agent-harness-engineering · **Boris Cherny "I write loops"(productmarketfit.tech, head of Claude Code)** · Lance Martin "Designing loops with Fable 5"(rubric>model, verifier 분리, 5단계 지속학습 루프) · Peter Steinberger(@steipete) · theneuron.ai(Cherny/Wu 해설).

> 핵심 caveat(dossier 참조): "verifier 89%/62%" 수치는 1차 미확인(과장 추정); "순진한 ICL이 메모리를 이긴다"는 CL-Bench 한정(보편 아님); faulty-memory는 격리 스트레스 테스트; /goal 평가자는 transcript만 보고 도구 미사용 → 보장 경계는 SDK 캡.
