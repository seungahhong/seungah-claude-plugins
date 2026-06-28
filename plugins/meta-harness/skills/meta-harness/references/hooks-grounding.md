# hooks·rules grounding — 1차 출처 provenance + 신뢰 등급 (자족)

> meta-harness v0.4.0(결정론 근거 → hook/permission 1급 라우팅 + 라이프사이클-aware hook 선택)이 인용하는 Claude Code **hooks·rules 사실의 출처와 신뢰 등급**을 남기는 provenance reference다.
> **왜 플러그인 내부에 두나** — 근거를 `.claude/` 같은 로컬·휘발 경로(다른 프로젝트 설치 시 없음·정리 시 소실)가 아니라 **플러그인 안에** 두어, 어디에 설치해도 깨지지 않고 플러그인과 함께 버전관리된다(로컬 생성물 비참조 원칙).
> 운영 distillation(event 선택·exit·config·matcher·상황→event 표)은 [hook-lifecycle.md](./hook-lifecycle.md), 메커니즘 선택 절차는 [data-capture-criteria.md §4](./data-capture-criteria.md). 이 문서는 "그 사실들을 **어디서·어느 신뢰도로** 확보했나"만 기록한다(중복 distill 금지).

## 1. 신뢰 등급

- **[VERBATIM]** 공식 raw 페이지 직접 인용(hooks-guide·memory·skills 페이지는 raw 본문으로 확인).
- **[요약]** WebFetch 요약 경유(hooks reference·steering blog·permissions) — 필드명은 라이브 `/en/hooks#<event>`로 재확인 시 [VERBATIM] 승격 가능.
- **[추론]** 합성·비축자(공식 문서에 verbatim 없음).

## 2. 조사 경위 (정직성)

- 1차 조사로 `/deep-research` 워크플로를 돌렸으나 **내부 structured-output 재시도 한도(infra) 초과로 실패** → `claude-code-guide` 에이전트가 공식 문서를 **직접 fetch**해 재grounding했다(**단일 에이전트** 직접 확인 — 다관점 3-0 만장일치 투표가 아님).
- 따라서 v0.4.0 hooks/rules 사실의 검증 수준은 "단일 에이전트 직접 fetch + 등급 표기"다. v0.3.0 advisory 메커니즘 매트릭스 출처(context-engineering·best-practices·steering)의 "독립 리서치 3-0 확인"과는 **구분**된다(과대표기 금지).
- 독립 재검증 2회(서브에이전트)로 본 인코딩의 정합·안전·정직성을 점검했다(별도 — 위 grounding 자체의 재검증은 아님).

## 3. 핵심 사실 (등급별 — 상세 distillation은 hook-lifecycle.md)

**[VERBATIM]**
- hook 라이프사이클은 **~30개 event**(SessionStart·Setup·UserPromptSubmit·UserPromptExpansion·PreToolUse·PermissionRequest·PermissionDenied·PostToolUse·PostToolUseFailure·PostToolBatch·Notification·MessageDisplay·SubagentStart·SubagentStop·TaskCreated·TaskCompleted·Stop·StopFailure·TeammateIdle·InstructionsLoaded·ConfigChange·CwdChanged·FileChanged·WorktreeCreate·WorktreeRemove·PreCompact·PostCompact·Elicitation·ElicitationResult·SessionEnd). 각 "when fires"는 hook-lifecycle.md §2.
- **exit 0**=진행(UserPromptSubmit·UserPromptExpansion·SessionStart는 stdout이 컨텍스트에 추가) · **exit 2**=차단(SessionStart·Setup·Notification·PostToolUse·SessionEnd 등은 차단 불가) · **exit 1/기타**=비차단 에러.
- 제어 JSON: PreToolUse=`hookSpecificOutput.permissionDecision`(allow|deny|ask), PostToolUse·Stop=`decision:"block"`+reason, UserPromptSubmit·SessionStart=`additionalContext`/stdout.
- **matcher**: tool-name event(PreToolUse/PostToolUse/...)는 tool 이름; SessionStart는 `startup,resume,clear,compact`; UserPromptSubmit·Stop 등은 matcher 미지원(생략/`""`/`*`=전체). 대소문자 구분.
- 설정: settings.json / 플러그인 `hooks/hooks.json` = `{"hooks":{"<Event>":[{"matcher","hooks":[{"type":"command","command","timeout"}]}]}}`. env `$CLAUDE_PROJECT_DIR`·`${CLAUDE_PLUGIN_ROOT}`.
- **`.claude/rules`는 advisory(모델 해석 컨텍스트)이지 결정론이 아니다** — 결정론적 강제는 **hook(command/http/mcp_tool) + permissions(allow/deny/ask) + managed settings** 뿐. memory 페이지: "To block an action regardless of what Claude decides, use a `PreToolUse` hook instead."
- **slash command는 skill로 병합**됨(`disable-model-invocation:true` skill = `/명령` 형태).

**[요약]** per-event 입력/출력 세부 필드(`tool_response`·`updatedToolOutput`·`SessionEnd.reason`·exit-2 차단 event 분할 일부)는 라이브 `/en/hooks#<event>` 재확인 시 [VERBATIM] 승격 가능. meta-harness가 의존하는 load-bearing 사실(어느 event·차단 가능 여부·exit0/exit2·additionalContext/permissionDecision/decision:block·config·matcher)은 모두 [VERBATIM].

## 4. 1차 출처 (URL)

- hooks reference: <https://code.claude.com/docs/en/hooks>
- hooks guide(raw): <https://code.claude.com/docs/en/hooks-guide>
- skills(slash-commands redirect): <https://code.claude.com/docs/en/skills>
- memory(CLAUDE.md/rules/enforcement 표): <https://code.claude.com/docs/en/memory>
- settings/permissions: <https://code.claude.com/docs/en/settings> · <https://code.claude.com/docs/en/permissions>
- steering blog(메커니즘 역할 분담): <https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more>
