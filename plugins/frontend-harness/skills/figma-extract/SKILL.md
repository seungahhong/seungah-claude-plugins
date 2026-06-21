---
name: figma-extract
description: Figma 링크를 받아 디자인 컨텍스트를 추출/파일화하는 스킬. 링크당 메타데이터로 노드 맵을 먼저 확인한 뒤 대상 노드만 상세 추출하고, raw는 파일로 내려 부모에는 경로와 요약만 반환합니다. 'Figma 추출', 'Figma 링크', '디자인 추출', '디자인 컨텍스트', 'Figma 스펙', 'Copy link to selection' 등의 키워드에 반응합니다.
disable-model-invocation: true
---

# Figma 디자인 컨텍스트 추출

Figma 링크를 받아 화면(노드)별 디자인 컨텍스트를 추출하고 파일로 내린다.
대형 프레임을 통째로 호출하면 토큰이 폭주(예: 351K > 25K 한도)하므로, **메타데이터로 노드 맵을 먼저 파악한 뒤 대상 노드만 상세 추출**하는 결정론적 순서를 따른다.
raw 데이터는 파일에 내리고, 부모(호출자)에는 **경로 + 1~2K 토큰 요약만** 반환한다.

## 입력

- **Figma 링크** — 화면별 노드 URL. 'Copy link to selection'으로 복사한 노드 단위 링크를 권장한다.
- **화면명(케밥)** — 산출물 파일명에 쓰일 화면 식별자. 미지정 시 노드 이름에서 추론하고 사용자에게 확인한다.
- **뷰포트 폭** — 캡처 기준 폭(예: 1440 / 390). 시각 정합 검증의 거짓 불일치를 막기 위해 `capturedViewportWidth`로 기록한다.

## MCP 도구

| 도구 | 데이터 성격 |
|------|------------|
| `mcp__claude_ai_Figma__get_metadata` | 희소 노드 맵(레이어 ID/이름/타입/위치/크기). 토큰 최소 — **항상 먼저** |
| `mcp__claude_ai_Figma__get_design_context` | 구조화 코드(레이아웃·컴포넌트). 토큰 최대 — 대상 노드만 |
| `mcp__claude_ai_Figma__get_variable_defs` | 변수/스타일 토큰(색·간격·타이포) |
| `mcp__claude_ai_Figma__get_screenshot` | PNG 스냅샷 |
| `mcp__claude_ai_Figma__get_code_connect_map` | 코드 컴포넌트 매핑(있을 때) |

> 폴백: 설치 환경의 `.mcp.json` 서버 별칭이 다르면(예: figma-dev-mode-mcp-server의 `get_code`) 해당 도구로 대체한다.

## 추출 순서 (결정론적)

링크당 아래 순서를 반드시 지킨다. 순서를 바꾸면 토큰이 폭주한다.

```
1. get_metadata          → 노드 맵 확보(먼저). 대상 노드(또는 하위 핵심 노드)를 식별
2. 대상 노드만 상세 추출   → get_design_context / get_variable_defs / get_screenshot
                            (페이지 통째 호출 금지. metadata로 좁힌 노드만)
3. raw를 파일로 내림      → .claude/design/{화면명}.json / -spec.md / -figma.png
4. 부모엔 경로 + 요약만   → 1~2K 토큰 이내 요약 + 산출물 경로 3종 반환 (raw verbatim 반환 금지)
```

**Step 1 — 노드 맵.** `get_metadata`로 레이어 트리를 받아 추출 대상 노드를 좁힌다. 화면이 크면 Card/Header/Sidebar 등 핵심 단위로 분해해 필요한 노드만 다음 단계로 넘긴다.

**Step 2 — 상세 추출.** 좁혀진 노드에 대해서만 호출한다.
- `get_design_context` → 레이아웃·컴포넌트 구조
- `get_variable_defs` → 디자인 토큰(색·간격·타이포)
- `get_screenshot` → PNG 스냅샷(지정 뷰포트 폭)

**Step 3 — 파일화.** 추출 결과를 산출물 경로에 저장한다(아래 산출물 표). 스키마와 spec 섹션 정의·예시는 [references/output-schema.md](references/output-schema.md) 참조.

**Step 4 — 반환.** 부모에는 **산출물 경로 3종 + 1~2K 토큰 요약**만 반환한다. design_context/variable_defs의 raw 응답을 그대로 부모로 올리지 않는다(컨텍스트 폭주 차단).

## 노력 배분

- **링크 1~2개** — fan-out 없이 **순차 추출**한다(멀티에이전트 토큰 비용 절약).
- **링크 3개 이상** — **화면당 서브에이전트로 fan-out**한다(최대 동시 ~6). 각 서브에이전트는 위 순서를 독립 수행하고 부모에는 경로+요약만 반환한다.

## 화면당 산출물 경로

| 파일 | 내용 |
|------|------|
| `.claude/design/{화면명-케밥}.json` | `tokens` / `layout` / `components` / `assets` / `capturedViewportWidth` |
| `.claude/design/{화면명-케밥}-spec.md` | 고정 섹션(개요·레이아웃·디자인토큰·컴포넌트·에셋·구현 메모) |
| `.claude/design/{화면명-케밥}-figma.png` | `get_screenshot` 스냅샷 |

스키마·섹션 정의·예시는 [references/output-schema.md](references/output-schema.md) 참조.

## 반환 형식 (부모에게)

```
[Figma 추출] {화면명}
산출물:
- .claude/design/{화면명}.json
- .claude/design/{화면명}-spec.md
- .claude/design/{화면명}-figma.png
캡처 뷰포트 폭: {capturedViewportWidth}px
요약(1~2K 토큰): 레이아웃 구조 / 핵심 디자인 토큰 / 주요 컴포넌트 / 에셋 / 구현 메모
```

## 주의사항

- **페이지/대형 프레임을 통째로 `get_design_context`에 넣지 않는다.** 반드시 `get_metadata`로 노드를 좁힌 뒤 호출한다.
- **raw 응답을 부모로 verbatim 반환하지 않는다.** 파일로 내리고 경로+요약만 올린다.
- **`capturedViewportWidth`를 반드시 기록한다.** 이후 시각 정합 검증의 거짓 불일치를 막는 전제다.
- **모든 메시지는 한국어 존댓말로 출력한다.**
- 추출만 수행한다. 코드 생성·구현은 이 스킬의 책임이 아니다(공통 컴포넌트는 spec을 식별·기록만 한다).
