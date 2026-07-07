# hook 라이프사이클 + 결정론적 메커니즘 선택 (자족 reference)

> meta-harness가 **결정론적 근거**(매번 반드시 일어나야/막아야 하는 것)를 `CLAUDE.md`/`Skill` 본문(advisory)이 아니라 **hook·permission**(deterministic)으로 보강하기로 했을 때, **어느 라이프사이클 event를 골라 hook을 추가/수정할지**를 정하는 reference다.
> **자족 문서다** — 외부 생성물(.claude 대장 등)을 포인터로 참조하지 않는다. 모든 1차 출처는 §8에 인라인. 다른 프로젝트에 설치해도 깨지지 않는다.
> 신뢰 등급 표기: **[V]**=공식 raw 페이지 verbatim · **[~]**=WebFetch 요약(필드명은 라이브 `/en/hooks#<event>` 재확인 권장) · **[추론]**=합성. load-bearing 사실(어느 event·차단 가능 여부·exit0/exit2·additionalContext/permissionDecision/decision:block·config 형식·matcher)은 모두 **[V]**다.

## 0. 제1 정정 — "rule"은 결정론이 아니다

사용자/직관은 흔히 "결정론적 규칙 → rules로 빼라"고 말하지만, Claude Code에서 **`.claude/rules/*.md`는 advisory(모델이 해석하는 컨텍스트)이지 강제 실행이 아니다**. [V](https://code.claude.com/docs/en/memory): rules도 CLAUDE.md처럼 "Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a `PreToolUse` hook instead."

따라서 보강 메커니즘은 **enforcement 성격**으로 갈린다.

| 성격 | 무엇 | **결정론적 강제 수단** | advisory 수단 |
|------|------|----------------------|---------------|
| **deterministic-enforce** | 매번 **반드시** 일어나야/막아야 함 (LLM이 건너뛸 수 없어야) | **hook(command/http/mcp_tool)** + **`permissions`(allow/deny/ask)** + 일부 managed settings | — |
| **deterministic-record** | 매번 **반드시 기록/캡처**(비차단) | **hook(exit 0 = record-an-event)** | — |
| **judgment** | 모델이 맥락을 **해석**해 판단 | 판단형 hook(prompt/agent type — 결정론 트리거 + 모델 판단) | `CLAUDE.md`(항상 로드 사실)·`Skill`(절차)·`.claude/rules`(path-scoped 컨텍스트) |

- 결정론 근거 [V](https://code.claude.com/docs/en/hooks-guide): "Hooks ... provide deterministic control ... ensuring certain actions always happen rather than relying on the LLM to choose to run them." PreToolUse deny는 "blocks the tool even in `bypassPermissions` mode."
- permission 근거 [V](https://code.claude.com/docs/en/memory): "Settings rules are enforced by the client regardless of what Claude decides to do." deny 우선: "deny rules ... always take precedence over hook approvals."
- advisory 근거 [V]: CLAUDE.md/rules는 "delivered as a user message ... no guarantee of strict compliance."
- **rules의 올바른 쓰임**: 결정론이 아니라 **path-scoped 컨텍스트 비용 최적화** — [V](https://code.claude.com/docs/en/memory) `paths:` frontmatter 규칙은 "only apply when Claude is working with files matching the specified patterns"(필요할 때만 로드). unscoped rule은 CLAUDE.md와 기계적으로 동등.

## 1. record vs enforce — hook의 두 역할

| 역할 | exit | 동작 | meta-harness 예 |
|------|------|------|------------------|
| **record**(사건 기록·3층 모델 ①) | **exit 0** | 차단하지 않고 로깅/컨텍스트 주입 | self-heal-capture(UserPromptSubmit) — redirect 발화 원형 적재 |
| **enforce**(안전벨트 경고음·③ 장치화) | **exit 2** 또는 `permissionDecision:"deny"` | 행동을 **차단**하고 이유를 Claude/사용자에 반환 | "X 경로에 쓰기 금지"를 PreToolUse로 차단 |

advisory 규칙이 압박(긴 세션·모호한 상황·prompt injection) 하에 **반복적으로 무시**되거나, 그 근거가 **본질적으로 불변(매번 강제)** 이면 instruction을 더 더하지 말고 enforce hook/permission으로 **장치화**한다.

## 2. lifecycle event 표 — when fires [V] · 차단 가능 · 주 제어

> 출처 [V] `/en/hooks-guide` "How hooks work". meta-harness 보강에 자주 쓰는 event를 위에, 나머지는 아래에 둔다.

| Event | When fires [V] | exit2 차단? | 주 제어/주입 | record/enforce |
|---|---|---|---|---|
| **UserPromptSubmit** | 프롬프트 제출 후, Claude 처리 전 | 차단O | exit0 stdout→컨텍스트; `additionalContext`; `decision:"block"` | 둘 다(보통 record) |
| **PreToolUse** | tool 실행 **전**. Can block | 차단O | `hookSpecificOutput.permissionDecision`=allow/deny/ask + reason; `updatedInput`[~] | **enforce** |
| **PostToolUse** | tool 성공 **후** | 불가(이미 실행) | `decision:"block"`+`reason`; `updatedToolOutput`[~] | record(사후 피드백) |
| **PostToolUseFailure** | tool 실패 후 | 불가 | `decision:"block"`+reason | record |
| **Stop** | Claude 응답 종료 시(완료만이 아님; 사용자 인터럽트엔 X) | 차단O | `decision:"block"`+reason로 계속시킴; `additionalContext`[~] | enforce(완료 게이트) |
| **SubagentStop** | subagent 종료 시 | 차단O | 위와 동일(+`agent_id`/`agent_type`[~]) | enforce |
| **SessionStart** | 세션 시작/재개 시 | 불가 | exit0 stdout→컨텍스트; `additionalContext`(매칭: startup/resume/clear/compact) | **record/주입** |
| **SessionEnd** | 세션 종료 시 | 불가 | 없음(정리·관측) | record |
| **PreCompact** | 컨텍스트 압축 전 | 차단O | `decision:"block"`(`trigger`=manual/auto) | enforce(압축 보호) |
| **InstructionsLoaded** | CLAUDE.md/`.claude/rules/*.md` 로드 시(세션시작+lazy) | 불가 | 관측(어떤 지침이 언제/왜 로드됐나 로깅) | record |
| **PermissionRequest** | 권한 다이얼로그 표시 시([추론] −p에선 X) | 차단O | `hookSpecificOutput.decision.behavior`[~]=allow/deny | enforce |
| **PermissionDenied** | auto classifier가 거부 시 | 불가 | `{retry:true}`[~]로 재시도 허용 | record/판단 |
| **Notification** | Claude Code 알림 시 | 불가 | 없음(부수효과) | record |

기타(필요 시): `Setup`(--init류 one-time), `UserPromptExpansion`(command 확장 전, 차단O), `PostToolBatch`(병렬배치 후 차단O), `MessageDisplay`, `SubagentStart`, `TaskCreated`/`TaskCompleted`(차단O), `StopFailure`(API에러), `TeammateIdle`(차단O), `ConfigChange`(차단O), `CwdChanged`, `FileChanged`(matcher=리터럴 파일명), `WorktreeCreate`(차단O=생성실패)/`WorktreeRemove`, `PostCompact`, `Elicitation`/`ElicitationResult`(MCP, 차단O).

## 3. 상황 → event 선택 표 (meta-harness 보강 시 핵심)

진단이 deterministic-* 로 분류한 근거를 hook으로 장치화할 때, **상황에 맞는 event**를 아래에서 고른다.

| 결정론적 근거(상황) | 고를 event | exit/제어 | 비고 |
|---|---|---|---|
| 특정 tool/명령/경로를 **무조건 막아야** | **PreToolUse** | exit2 또는 `permissionDecision:"deny"` | 하드 금지는 가능하면 `permissions.deny`(우선순위 최상, hook보다 견고) |
| 막되 **판단**이 필요("정말 끝났나?") | Stop/PreToolUse **prompt·agent type** hook | 모델 판단 `{ok:false,reason}` | 결정론 트리거 + 모델 판단 |
| tool 실행 **후 반드시 검사/포맷/로깅** | **PostToolUse** | exit0(또는 decision:block로 피드백) | 이미 실행됨 — 되돌리기 불가 |
| **사용자 발화를 매번 캡처/주입** | **UserPromptSubmit** | exit0(stdout/additionalContext) | self-heal-capture가 이 패턴 |
| **세션 시작마다 컨텍스트 주입**(누적 신호 nudge 등) | **SessionStart** | exit0 stdout/additionalContext (matcher: startup/resume/clear/compact 중 선택; meta-harness nudge는 matcher 생략=전체) | 차단 불가 — 주입 전용 |
| **응답 종료 전 완료 체크리스트 강제** | **Stop**(또는 SubagentStop) | exit2/decision:block + reason | 루프 캡 8회 주의 |
| **압축이 중요한 trace를 지우지 않게** | **PreCompact** | exit2/decision:block | |
| **어떤 지침/rule이 로드됐는지 관측** | **InstructionsLoaded** | exit0(로깅) | CLAUDE.md/rules 로드 추적 |

> 선택 원칙: ① **막아야 = 차단 가능한 event(PreToolUse/Stop/PreCompact 등) + exit2/deny**, ② **기록/주입 = exit0 event(UserPromptSubmit/PostToolUse/SessionStart 등)**, ③ **하드 금지는 hook보다 `permissions.deny`** 가 견고(managed scope·우선순위 최상). ④ 막되 판단 필요 = **prompt/agent type** hook.

## 4. exit code · JSON 제어 의미 [V]

- **exit 0** — 진행. UserPromptSubmit/UserPromptExpansion/SessionStart는 **stdout이 컨텍스트에 추가**. JSON 출력은 exit 0에서만 파싱.
- **exit 2** — 차단(차단 가능 event만). stderr가 Claude 피드백으로. exit 2면 JSON 무시. SessionStart/Setup/Notification/PostToolUse/SessionEnd 등은 **차단 불가**(stderr→user, 계속).
- **exit 1/기타** — 진행(비차단). transcript에 hook error notice.
- 보편 JSON[~]: `continue`(false→Claude 정지)·`stopReason`·`suppressOutput`·`systemMessage`.
- PreToolUse 예시[V]: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`. allow는 프롬프트만 생략하지 deny rule을 못 덮는다("tighten ... not loosen"). 다중 hook 병합: 가장 제한적 답 우선(deny>defer>ask>allow).
- `additionalContext`[V]: "injected as a system reminder that Claude reads as plain text" — UserPromptSubmit·SessionStart.

## 5. config 형식 [V]

settings.json / 플러그인 `hooks/hooks.json` 공통:
```json
{ "hooks": { "<Event>": [ { "matcher": "<see below>", "hooks": [ { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/x.sh", "timeout": 10 } ] } ] } }
```
- 플러그인 hook은 `hooks/hooks.json`(플러그인 enable 시 활성, 선택 `description`). skill/agent frontmatter `hooks:`도 가능(컴포넌트 활성 동안만).
- 타입: `command|http|mcp_tool`(결정론 실행) | `prompt|agent`(모델 판단). timeout 기본 command 10분(UserPromptSubmit 30초), prompt 30초, agent 60초.
- **matcher**: tool-name event(PreToolUse/PostToolUse/PostToolUseFailure/PermissionRequest/PermissionDenied)=tool 이름(`Bash`,`Edit|Write`,`mcp__.*`). SessionStart=`startup,resume,clear,compact`; PreCompact=`manual,auto`; InstructionsLoaded=`session_start,...`; SessionEnd=`clear,resume,logout,...`. **matcher 미지원(항상 발동)**: UserPromptSubmit·Stop·PostToolBatch·TeammateIdle·Task*·Worktree*·CwdChanged·MessageDisplay → `""` 또는 생략. `"*"`/`""`/생략=전체. **대소문자 구분**.
- env: `$CLAUDE_PROJECT_DIR`·`${CLAUDE_PLUGIN_ROOT}`·`${CLAUDE_PLUGIN_DATA}`[~]·`CLAUDE_ENV_FILE`.
- 하드 금지/허용은 `permissions`(settings.json): `{"permissions":{"deny":["Bash(curl *)","Read(./.env)"],"allow":["Bash(npm run test *)"]}}`. deny가 hook approve보다 우선.

## 6. 스코프 상호작용 — hook/permission/rule 보강을 **어디에** 둘까

메커니즘 **선택**(deterministic→hook/permission)은 스코프와 무관하지만, **배치**는 기존 패치 경계를 따른다(승인 게이트·경계 방어선 불변).

| 보강 위치 | repo-wide(기본) | plugin(opt-in) |
|---|---|---|
| **플러그인 hook**(`plugins/<p>/hooks/hooks.json`+스크립트) | 경계 밖 → `scope-escalation` **+ 제안 hook_spec 동봉**(event·matcher·exit·스크립트 스케치) → plugin 모드 재실행 권고 | **in-boundary** → hook 패치 정상 생성 |
| **프로젝트 hook/permission**(`.claude/settings.json`) | `out-of-scope` → **update-config 핸드오프**(meta-harness는 settings.json을 직접 쓰지 않는다) | 동일 |
| **`.claude/rules/*.md`**(path-scoped advisory) | 프로젝트 `.claude/rules`는 meta-harness가 직접 쓰지 않음 → `update-config-handoff`(권장 rule 본문+`paths:` 동봉) | 동일(`update-config-handoff`) — '가능'은 플러그인이 **자체 번들**하는 rule 자산에 한하며, 프로젝트 `.claude/rules`는 plugin 모드에서도 핸드오프(scope-and-targets.md와 일치) |

- **불변(P2)**: meta-harness는 `.claude/settings.json`(hooks/permissions)을 **직접 수정하지 않는다** — 이는 `update-config` 스킬·사용자 영역이고, 레포 루트 메타 보호 경계와 같은 선상이다. 대신 **구체적 spec(event/matcher/exit/명령)을 제안**하고 적용은 update-config + 사용자에게 넘긴다. "결정론으로 빼라"가 곧 "meta-harness가 settings를 임의로 고친다"가 되지 않게 한다.
- repo-wide에서 hook이 정답인 결함은 patch를 만들지 말고 `scope-escalation`으로 보고하되, **무엇을 어디에 어떻게**(hook_spec)까지 담아 사용자가 plugin 모드/​update-config로 바로 옮길 수 있게 한다.

## 7. 정직성 단서

- `.claude/rules`는 **advisory**(결정론 아님) — §0 [V]. 결정론 강제는 hook(command/http/mcp_tool)+permissions뿐.
- **slash command는 skill로 병합**됨[V](https://code.claude.com/docs/en/skills) — "command"는 `disable-model-invocation:true` skill의 한 형태. 본 플러그인 다른 .md의 "commands/*.md"는 레거시 `.claude/commands/*.md`(여전히 `/명령` 생성)를 가리키며 현대적 표현은 skill이다.
- **[~]** 표시 필드(per-event 입력/출력 세부, exit-2 차단 event 분할 일부)는 라이브 `/en/hooks#<event>` 재확인 시 verbatim 승격 가능. meta-harness 의존 사실은 모두 [V].
- 본 reference는 event를 **고르는** 판단 보조다. 실제 hook 본문·exit·matcher는 patch 시 §3·§5로 명시하고, 적용은 항상 **승인 게이트** 통과 후.

## 8. 근거 자료 (1차)

- hooks reference: <https://code.claude.com/docs/en/hooks>
- hooks guide: <https://code.claude.com/docs/en/hooks-guide>
- skills(slash-commands redirect): <https://code.claude.com/docs/en/skills>
- memory(CLAUDE.md/rules/enforcement 표): <https://code.claude.com/docs/en/memory>
- settings/permissions: <https://code.claude.com/docs/en/settings> · <https://code.claude.com/docs/en/permissions>
- steering(메커니즘 역할 분담): <https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more>
