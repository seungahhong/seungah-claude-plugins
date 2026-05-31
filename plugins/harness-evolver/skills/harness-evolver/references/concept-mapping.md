# Evolver 루프 ↔ skill-creator ↔ 본 하네스 개념 매핑

본 하네스가 어디서 무엇을 차용했는지, 그리고 왜 그 결합이 의미가 있는지를 정리한다. 진화 작업 중 "왜 이렇게 했지" 가 의심되면 이 문서를 참고한다.

## 1. 큰 그림: 닫힌 학습 루프

본 하네스의 출발점은 **에이전트가 자신의 경험에서 배워 다음 회차에 더 잘 한다**는 self-improving agent 개념이다. 구체적으로:

- Trajectory를 잡고
- 패턴을 추출해 메모리에 큐레이션하고
- 메모리를 다음 회차의 입력으로 다시 넣어
- 스킬/행동을 점진 개선한다

이것을 **하네스 단위에서 구현**한 것이 본 플러그인이다. 개별 응답을 개선하는 것이 아니라, **하네스 그 자체 (스킬·에이전트·오케스트레이터 정의 파일들)** 를 개선 대상으로 본다. 이 닫힌 루프 전체를 본 문서에서는 **Evolver 루프**라고 부른다.

## 2. 구성요소별 출처

| 본 하네스 구성 | Evolver 루프 대응 | skill-creator 대응 |
| ------------ | ----------------- | ----------------- |
| `trajectory-capture` 스킬 | Trajectory capture | (간접: 테스트 케이스 트랜스크립트 읽기) |
| `trajectory-analyst` 에이전트 | Trajectory compression / normalization | – |
| `failure-diagnosis` 스킬 | 사실에서 패턴 추출 | "Generalize from the feedback" |
| `failure-diagnostician` 에이전트 | – | "Read transcripts, not just outputs" |
| `eval-driven-refinement` 스킬 | Skills self-improve during use | iteration loop §"Improving the skill" |
| `skill-refiner` 에이전트 | Autonomous skill refinement | description optimization + body 개선 |
| `evolution-historian` + `evolution-memory/` | Curated memory with periodic nudges | – |
| Phase 6 트리거 충돌 검증 | – | should-trigger / should-not-trigger 평가 |
| Phase 4 사용자 게이트 | – | 인간 리뷰 루프 (viewer + feedback.json) |

## 3. 결합의 의의 — 왜 둘을 합쳤나

**Evolver 루프만 쓰면:** 자율 개선이지만 평가가 빠진다. 무엇이 더 나아졌는지 객관 측정이 약하다.

**skill-creator만 쓰면:** 평가는 강하지만 "언제 개선이 필요한가" 의 자동 감지 신호가 없다. 사용자가 매번 "이 스킬 개선해" 를 명시해야 한다.

**둘을 합치면:**

1. Trajectory 캡처로 **언제 개선이 필요한가** 의 신호를 얻고 (Evolver 루프)
2. 패턴 큐레이션으로 **무엇을 우선해 고칠까** 를 판단하고 (Evolver 루프)
3. eval-driven iteration으로 **고친 게 정말 나아졌나** 를 검증한다 (skill-creator)

## 4. 결정적 의도 차이

세 가지 의도적 차이가 있다 — 차용하지 않은 것들.

### 4-1. 완전 자율은 거절 — 사용자 게이트 필수

일반적인 self-improving agent는 자율 개선을 강조하지만, 본 하네스는 **Phase 4 사용자 게이트**를 필수로 둔다. 잘못된 자동 적용이 발생하면 진화 자체에 대한 사용자 신뢰가 깨지고, 그 순간 이 하네스는 죽은 도구가 된다. 신뢰가 자율보다 비싸다.

### 4-2. 회차 단위는 한 하네스, 결함 1건 단위가 진화 단위

skill-creator의 iteration은 전체 스킬을 한 단위로 본다. 본 하네스는 **결함 1건 = 진단 1건 = 패치 1건** 으로 분리한다. 이유: 하네스에는 결함이 동시 다발로 누적되므로, 묶으면 어느 결정이 어느 변화에 책임이 있는지 추적 불가.

### 4-3. 평가 viewer는 생략

skill-creator의 generate_review.py 같은 HTML viewer를 본 하네스는 만들지 않는다. 이유: 본 하네스의 산출물(diagnosis.json, refinement.json, patch.md)이 사람이 읽기 충분하고, 별도 viewer를 더하면 본문이 비대해진다. 회차당 5–10건 정도의 결정을 보는 데는 표 한 장이면 충분하다.

## 5. Nudge 임계치 근거

`recurring-patterns.md` 의 `needs_attention` 진입 임계치를 **3회** 로 잡은 이유:

- 1회 — 우연일 수 있다.
- 2회 — 같은 케이스의 반복일 수 있다 (다른 결함이 우연히 같은 표적에 떨어진 것).
- 3회 — 본문/구조 자체의 문제. skill-creator의 "Look for repeated work across test cases" 가 본문 추가가 아닌 스크립트화를 권고하는 임계 신호와 동일한 의도.

3회째에 도달하면(누적 ≥3) 패치 본문이 아니라 구조 자체(에이전트 분리, 오케스트레이터 흐름 재설계)를 건드려야 한다. 이때 본 하네스는 patch를 거절하고 `harness-generator` 호출로 redirect한다 — 진화의 책임 한계를 분명히 한다.

## 6. 메모리 영속 위치 결정 근거

`evolution-memory/` 위치는 **평가 스코프**에 따라 갈린다.

- `plugin` (단일 플러그인) → 그 플러그인 루트(`plugins/{plugin}/evolution-memory/`). 그 하네스 자체의 변천 이력이므로 같은 디렉토리에 묶이는 게 자연스럽고, 플러그인 단위 `git` 흐름에 자동으로 들어온다.
- `repo-wide` (전체 레포, 기본) → 레포 루트의 `.claude/evolution-memory/`. 특정 플러그인 하나가 아니라 프로젝트 전역(루트 CLAUDE.md + 여러 플러그인 스킬)을 가로지르는 이력이므로 특정 플러그인에 묶을 수 없다.

공통 의도: 회차별 큐레이션이 **스코프 단위로 격리**되어야 패턴 집계(같은 표적 3회 임계치 등)가 오염되지 않는다. repo-wide 이력과 plugin 이력을 섞으면 카운트가 뒤섞인다.

## 7. 본 하네스를 또 진화시킬 때 — Self-bootstrapping

이 메타 하네스도 결국 또 다른 하네스이므로, 본 하네스 자체의 결함도 본 하네스로 진화시킬 수 있다 (self-bootstrapping). 그 경우 (= `plugin: harness-evolver` 스코프):

- 대상 하네스 = `plugins/harness-evolver/`
- `evolution-memory/` 는 본 플러그인 루트에 만들어진다 (plugin 스코프이므로)
- 진화 회차의 trajectory가 곧 본 스킬의 메타-진화 입력이 된다

자기를 자기로 진화시키는 폐쇄 루프가 가능하다는 것이 본 설계의 의도된 결과다.

## 8. 평가 스코프 — repo-wide 기본 / plugin opt-in 결정 근거

본 하네스가 도는 **현재 적용 중인 프로젝트 = 이 레포**다. 매 회차 Phase 1에서 스코프를 확정한다.

- `repo-wide` (기본) — 루트 `CLAUDE.md` + 모든 플러그인의 `SKILL.md` 를 진단하되 **패치는 그 둘로만** 한정한다.
- `plugin` (opt-in) — 사용자가 명시 요청한 단일 플러그인의 **모든 파일**(`plugin.json`·`agents`·`hooks`·`commands`·`skills`·플러그인별 `CLAUDE.md`)을 심층 평가·패치한다.

**왜 기본을 좁게 잡았나:** 패치는 파일을 직접 바꾼다. "평가해줘" 한마디에 패키징·에이전트·훅까지 광범위하게 손대면, §4-1의 "신뢰가 자율보다 비싸다" 원칙이 깨진다 — 사용자가 의도하지 않은 변경은 자동 적용 금지만큼이나 신뢰를 무너뜨린다. 그래서 기본 패치 표적을 **프로젝트 지침(CLAUDE.md)과 스킬 본문(SKILL.md)** 으로 좁히고, 그 너머는 사용자가 단일 플러그인 평가를 명시할 때만 연다. repo-wide에서 경계 밖 표적이 나오면 patch 대신 `scope-escalation` 으로 plugin 모드 재실행을 권고한다 — 진단은 정직하게 하되 패치 권한은 스코프가 통제한다.
