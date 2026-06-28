# 평가 스코프와 패치 경계

진단은 넓게(하네스 전체를 읽어 root cause를 찾는다), 패치는 좁게(승인된 표적만 실제로 고친다) 가는 것이 이 플러그인의 안전선이다. 진단 대상과 패치 허용 표적을 분리하는 이유는, full-trace로 결함의 진짜 원인을 자유롭게 추적하되 사용자가 의도하지 않은 자산(에이전트·훅·메타데이터)을 임의로 바꾸지 않기 위해서다. 스코프는 Phase 1에서 **한 번에 한 질문**으로 확정한다.

## 스코프 2종 (진단대상 vs 패치허용표적)

| 스코프 | 기본/옵트인 | 진단대상(읽기·root cause 추적) | 패치허용표적(Edit/Write 가능) | experience-store 위치 |
|---|---|---|---|---|
| **repo-wide** | 기본 | 루트 CLAUDE.md + 모든 플러그인 SKILL.md + (맥락 이해용으로) agents/·commands/·hooks/·plugin.json 읽기 | **루트 CLAUDE.md + 임의 SKILL.md 만** | `.claude/experience-store/` |
| **plugin** | opt-in(명시 요청 시) | 지목 플러그인의 모든 파일 | 지목 플러그인의 **모든 파일**(plugin.json·agents/·commands/·hooks/·각 SKILL.md·플러그인별 CLAUDE.md) | `.claude/plugin-store/{target}/` |

repo-wide에서 agents/·hooks/ 등을 **읽되 패치하지 않는** 이유: 결함의 원인이 에이전트 정의에 있더라도, repo-wide 기본 모드에서 사용자가 승인한 건 "지침·스킬 본문 고도화"까지다. 더 깊은 자산 수정은 의도를 다시 확인(plugin 모드 재실행)해야 안전하다.

## 표적 판정 규칙 (change_kind / scope_status)

진단 시 표적 자산의 위치에 따라 `scope_status`와 `change_kind`를 부여한다. repo-wide 기준:

- **in-boundary** → 표적이 루트 CLAUDE.md 또는 임의 SKILL.md. 정상적으로 patch.md를 생성한다(`change_kind`는 description/skill-body/claude-md 중 하나).
- **scope-escalation** → 표적이 agents/·commands/·`hooks/`·plugin.json·플러그인별 CLAUDE.md. **patch를 만들지 않고** `change_kind:"scope-escalation"`으로 보고하며, "이 표적을 고치려면 plugin 모드로 재실행하라"고 권고한다. 경계 밖을 몰래 고치지 않는 이유: repo-wide 승인 범위를 넘어서기 때문이다. **표적 kind가 `hook`이면** 단순 권고가 아니라 **제안 `hook_spec`(event·matcher·exit·스크립트 스케치)을 동봉**해, 사용자가 plugin 모드로 바로 옮기게 한다(아래 §메커니즘 배치).
- **update-config-handoff** → 표적 kind가 `permission`(`.claude/settings.json` permissions)·프로젝트 `rule`(`.claude/rules/*.md`). meta-harness는 `.claude/settings.json`을 **직접 수정하지 않는다**(이는 `update-config` 스킬·사용자 영역이며, 레포 루트 메타 보호와 같은 선상). `change_kind:"update-config-handoff"`로 권장 spec을 담아 보고하고 적용은 사용자/​update-config에 넘긴다.
- **out-of-scope / blocked** → 표적이 레포 루트 메타(`.claude-plugin/marketplace.json` 등 마켓플레이스/레지스트리 메타)·`global-memory`(사용자 `~/.claude`). `change_kind:"blocked"`로 보고하고 **사용자 직접 수정**을 안내한다. 자동화가 손대면 배포 메타가 깨질 수 있어 의도적으로 막는다.

plugin 모드에서는 지목 플러그인 내부 표적이 전부 in-boundary이므로 scope-escalation이 발생하지 않는다. 단, 지목 플러그인 **밖**(다른 플러그인·레포 루트 메타)을 건드리려는 표적은 plugin 모드에서도 out-of-scope/blocked다.

## 메커니즘 배치 — 결정론(hook·permission)·advisory(rule)

진단이 근거를 `deterministic-enforce`/`deterministic-record`로 분류하면 보강 메커니즘은 advisory 본문(CLAUDE.md/Skill)이 아니라 **hook·permission**(결정론적 강제)이다. **메커니즘 선택은 스코프와 무관**하지만 **배치는 위 경계를 그대로 따른다** — 즉 "결정론으로 빼라"가 곧 "meta-harness가 어디든 hook/settings를 임의로 쓴다"가 되지 않는다(승인 게이트·경계 방어선 불변, P2).

| 표적 | repo-wide(기본) | plugin(opt-in) |
|---|---|---|
| 플러그인 `hook`(`plugins/<p>/hooks/`) | `scope-escalation` + 제안 `hook_spec` | **in-boundary** → hook patch 정상 |
| 프로젝트 `permission`/`rule`(`.claude/settings.json`·`.claude/rules`) | `update-config-handoff`(settings 직접수정 안 함) | 동일 |

- **정정**: `.claude/rules`는 결정론이 아니라 **advisory**(path-scoped 컨텍스트 비용 최적화)다 — 결정론 강제는 hook(command/http/mcp_tool)+permissions뿐. 어느 lifecycle event로 장치화할지는 자족 reference [hook-lifecycle.md](./hook-lifecycle.md)로 고른다.
- repo-wide에서 hook이 정답인 결함은 patch 대신 `scope-escalation`으로 보고하되 **무엇을 어디에 어떻게**(hook_spec)까지 담아, 사용자가 plugin 모드/​update-config로 즉시 옮길 수 있게 한다(C8: 갈 곳 없는 신호는 멈춘다).

## R2 — plugin 심층에서 표적이 열리는 조건

R2(AI 동작이 잘못된 방향으로 가서 plugin 자체를 고도화)는 **plugin 스코프를 명시적으로 선택**했을 때만 plugin.json·agents/·commands/·hooks/까지 패치 표적이 된다. 조건을 정리하면:

1. Phase 1에서 사용자가 plugin 스코프를 골랐고(opt-in), 대상 플러그인이 지목되었다.
2. 진단이 결함 root cause를 그 플러그인의 메타데이터/에이전트/훅/커맨드 정의에 귀착시켰다(why-first 근거를 trace step/파일 경로로 인용).
3. Pareto 4축에서 후퇴가 없다(특히 rule-body-cost: 메타데이터·에이전트 본문이 정합 이득 없이 길어지면 reject).

이 세 조건이 동시에 충족돼야 plugin.json/agents/hooks/commands를 patch 표적으로 연다. repo-wide에서 같은 표적이 나오면 위 scope-escalation 규칙에 따라 patch 없이 plugin 모드 재실행을 권고한다(R2를 우회로 끌어오지 않는다).

## 적용 직전 경계 재확인 (방어선, Phase 7)

승인된 patch를 Edit/Write로 적용하기 **직전에** 표적 경로가 현재 스코프 경계 안인지 다시 검사한다. Phase 1에서 한 번 판정했더라도 재확인하는 이유: 진단~승인 사이에 스코프가 바뀌었거나(다른 모드로 재실행), 표적 경로가 잘못 라벨링됐을 위험을 적용 직전에 마지막으로 거른다. 이중 게이트(진단 시 1차 + 적용 직전 2차)가 경계 위반을 구조적으로 차단한다.

방어선 재확인 절차:

1. 적용 대상 파일의 절대경로를 현재 스코프의 패치허용표적 집합과 대조한다.
2. repo-wide인데 경로가 루트 CLAUDE.md·SKILL.md가 아니면 적용을 **중단**하고 scope-escalation으로 되돌린다(승인이 있었더라도 적용하지 않는다).
3. 경계 안이면 동일 파일에 걸린 다중 patch를 **묶어** 한 번에 적용한다(부분 적용으로 인한 정합 깨짐 방지).
4. 적용된 patch 사본을 `{store-root}/patches/{date}-{target-slug}.md`로 남긴다(이력·재현용).
