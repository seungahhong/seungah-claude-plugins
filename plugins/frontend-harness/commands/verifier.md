---
name: verifier
description: "개발 완료 후 E2E 브라우저 검증을 실행하는 커맨드. Chrome MCP, Playwright MCP, Agent-Browser 중 선택하여 PRD의 E2E 레인 인수조건(AC-n.m) 단위로 실제 브라우저에서 기능 동작을 검증하고 E2E 자동 충족률을 산출합니다. 'E2E 검증', '브라우저 검증', '화면 테스트', '기능 검증', '동작 확인' 등의 키워드에 반응합니다. 독립 실행 또는 오케스트레이터의 Phase 5(Verify)로 호출됩니다."
---

# E2E 브라우저 검증 커맨드

e2e-verifier 스킬을 로드하여 개발 완료 후 E2E 브라우저 검증을 수행합니다.

## 실행 방법

`../skills/e2e-verifier/SKILL.md` 스킬의 지침을 따라 순차 실행합니다. **스킬을 로드할 때 `호출맥락`(orchestrated=오케스트레이터/verify 경유 / standalone=사용자가 직접 실행)을 명시 전달**해, 스킬이 결정 메뉴 억제 여부를 결정론적으로 판정하게 한다(전달이 없으면 스킬은 orchestrated로 기본 처리):

1. **Phase 0 — 도구 선택**: **사용자에게** Chrome MCP / Playwright MCP / Agent-Browser 중 어떤 도구를 사용할지 **반드시 질문하고 응답을 기다린다.** 사용자가 선택하기 전까지 다음 Phase로 진행하지 않는다.
2. **Phase 0-1 — 사전 조건 확인**: 선택된 도구의 MCP 연동, 브라우저, 개발 서버 확인
3. **Phase 1 — 검증 시나리오 생성**: PRD의 **E2E 레인 AC(§2.4)마다** 브라우저 검증 시나리오로 변환(TDD 레인·`[수동]` AC는 E2E 시나리오에서 제외)
4. **Phase 2 — 브라우저 검증 실행**: 각 시나리오를 실제 브라우저에서 실행, 결과 즉시 출력
5. **Phase 3 — 검증 결과 정리**: **AC별 PASS/FAIL** 종합, 실패 항목 상세, **E2E 자동 충족률(통과 E2E AC / 전체 E2E 레인 AC)** 보고. 오케스트레이터/verify로 호출된 경우(`호출맥락=orchestrated`) 다음 행동 결정은 상위 수렴 루프에 위임한다(리프 스킬 메뉴 억제)

**중요: Phase 0의 도구 선택을 포함하여, 각 Phase 완료 후 반드시 사용자에게 결과를 보여주고 승인/거절을 확인받은 뒤 다음 Phase로 진행합니다. 사용자 승인 없이 자동으로 다음 단계를 진행하지 않습니다. 도구를 임의로 선택하거나 기본값으로 자동 진행하지 않습니다.**

각 Phase의 상세 동작은 e2e-verifier 스킬의 SKILL.md를 참조합니다.
도구별 실행 패턴은 스킬의 `references/` 하위 파일을 참조합니다:
- `../skills/e2e-verifier/references/chrome-mcp.md`: Chrome DevTools MCP 실행 패턴
- `../skills/e2e-verifier/references/playwright-mcp.md`: Playwright MCP 실행 패턴
- `../skills/e2e-verifier/references/agent-browser.md`: Agent-Browser 실행 패턴