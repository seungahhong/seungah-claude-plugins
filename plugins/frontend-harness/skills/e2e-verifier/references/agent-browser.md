# Agent-Browser 실행 패턴

AI 에이전트 특화 브라우저인 Agent-Browser를 사용하여 E2E 검증을 수행할 때의 상세 패턴.
자연어 기반 인터랙션과 비전 기반 요소 인식을 지원하여 에이전트 친화적인 브라우저 제어를 제공한다.

## 사전 조건 확인 절차

### 1. MCP 연동 확인

`.mcp.json` 파일에 agent-browser 설정이 있는지 확인한다.

```json
{
  "mcpServers": {
    "agent-browser": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/agent-browser@latest"]
    }
  }
}
```

> **참고:** Agent-Browser 패키지명은 프로젝트에 따라 다를 수 있다.
> 사용자에게 정확한 패키지명을 확인한 후 설정한다.

없으면 사용자에게 설정 추가와 Claude Code 재시작을 안내한다:

```
Agent-Browser MCP가 연동되어 있지 않습니다.
사용 중인 Agent-Browser 패키지명을 알려주세요.
(예: @anthropic-ai/agent-browser, browser-use-mcp 등)

패키지명을 확인한 후 `.mcp.json`에 설정을 추가하겠습니다.
```

### 2. 브라우저 환경 확인

Agent-Browser는 내장 브라우저를 사용하므로 별도의 Chrome 디버깅 모드가 필요 없다.
다만 환경에 따라 추가 의존성이 필요할 수 있다:

```bash
# 필요 시 Chromium 설치
npx playwright install chromium
```

### 3. 개발 서버 확인

Agent-Browser의 네비게이션 도구로 개발 서버 URL에 접근하여 페이지가 정상 로드되는지 확인한다.

## Chrome MCP / Playwright MCP와의 차이

| 항목 | Chrome MCP | Playwright MCP | Agent-Browser |
|------|-----------|---------------|--------------|
| 브라우저 관리 | 사용자 직접 실행 | 자동 실행 | 자동 실행 |
| 요소 식별 | CSS 선택자 | 접근성 스냅샷 + CSS | 비전 + 접근성 + CSS |
| 인터랙션 방식 | 저수준 API | 중간 수준 API | 자연어/고수준 API |
| 비전 활용 | 스크린샷 수동 분석 | 스크린샷 수동 분석 | 화면 인식 자동화 |
| 복잡한 흐름 | 스텝별 수동 구성 | 스텝별 수동 구성 | 목표 기반 자동 실행 |

## 도구 매핑

> **중요:** Agent-Browser의 도구명과 파라미터는 구현체에 따라 다를 수 있다.
> 아래는 일반적인 Agent-Browser MCP 인터페이스를 기준으로 작성했다.
> 실제 사용 시 `ToolSearch`로 사용 가능한 도구를 확인하고 매핑을 조정한다.

| 동작 | Agent-Browser 도구 (예시) | 주요 파라미터 |
|------|-------------------------|-------------|
| 페이지 이동 | `browser_navigate` | `url` |
| 스크린샷 | `browser_screenshot` | 없음 |
| 접근성 스냅샷 | `browser_snapshot` | 없음 |
| 요소 클릭 | `browser_click` | `element` 또는 `selector` |
| 텍스트 입력 | `browser_type` | `element`, `text` |
| 키 입력 | `browser_press_key` | `key` |
| 호버 | `browser_hover` | `element` |
| JS 실행 | `browser_evaluate` | `javascript` |
| 대기 | `browser_wait` | `condition` 또는 `text` |
| 탭 관리 | `browser_tab_*` | 탭 인덱스 |

### 도구 확인 절차

Agent-Browser 선택 시, 실제 사용 가능한 도구를 먼저 확인한다:

```
1. ToolSearch로 "agent-browser" 또는 "browser" 키워드로 사용 가능한 도구 검색
2. 검색된 도구의 파라미터 스키마 확인
3. 위 도구 매핑 표를 실제 도구명으로 갱신
4. 갱신된 매핑으로 시나리오 실행
```

## 페이지 이동 패턴

### 최초 진입

```
1. browser_navigate(url: "개발서버URL") — 최초 1회만 허용
2. browser_wait(text: "페이지 로드 완료 텍스트") 또는 적절한 대기
3. browser_snapshot() — 페이지 구조 파악
4. browser_screenshot() — 시각적 화면 확인
```

### 페이지 내 이동

```
1. browser_snapshot() — 현재 페이지 구조 확인
2. 이동할 요소 식별 (스냅샷 ref 또는 비전 기반)
3. browser_click(element: "대상 요소") — 클릭으로 이동
4. browser_wait(text: "이동 완료 텍스트")
5. browser_screenshot() — 이동 결과 확인
```

### URL 직접 이동 금지 원칙

Chrome MCP, Playwright MCP와 동일하게:
- `browser_navigate`는 **최초 URL 진입 시에만** 사용
- 이후 모든 이동은 화면 UI 클릭을 통해 수행
- URL을 추측하거나 직접 구성하지 않음

## 요소 인터랙션 패턴

### 클릭

```
1. browser_snapshot() — 대상 요소 확인
2. browser_click(element: "대상 요소")
3. browser_wait(text: "결과 텍스트")
4. browser_screenshot() — 결과 확인
```

### 텍스트 입력

```
1. browser_snapshot() — 입력 필드 확인
2. browser_click(element: "입력 필드") — 포커스
3. browser_type(element: "입력 필드", text: "입력값")
4. browser_screenshot() — 입력 결과 확인
```

### 스크롤

```
1. browser_evaluate(javascript: "window.scrollTo(0, document.body.scrollHeight)")
2. browser_snapshot() — 스크롤 후 구조 확인
3. browser_screenshot() — 스크롤 결과 확인
```

## 상태 검증 패턴

### 스냅샷 기반 검증

```
1. browser_snapshot() — 접근성 트리 조회
2. 스냅샷에서 기대 요소/텍스트 존재 여부 확인
3. 존재하면 PASS, 없으면 FAIL
```

### JavaScript 기반 검증

```javascript
// browser_evaluate로 실행
JSON.stringify({
  exists: !!document.querySelector("대상 선택자"),
  text: document.querySelector("대상 선택자")?.textContent?.trim(),
  count: document.querySelectorAll("대상 선택자").length
})
```

### 스크린샷 기반 시각적 검증

Agent-Browser의 비전 기능을 활용하여:
```
1. browser_screenshot() — 현재 화면 캡처
2. 스크린샷에서 시각적으로 기대 요소/텍스트 존재 여부 확인
3. 스냅샷과 교차 검증하여 정확도 향상
```

## 에러 복구 패턴

### 요소 미발견

```
1. browser_snapshot() — 접근성 트리에서 유사 요소 탐색
2. browser_screenshot() — 비전 기반으로 화면에서 요소 탐색
3. 여전히 찾을 수 없으면:
   - 스냅샷과 스크린샷을 함께 사용자에게 제시
   - 사용자 안내를 받아 재시도
```

### 타임아웃

```
1. 대기 시간을 2배로 증가하여 재시도
2. 여전히 타임아웃이면:
   - browser_screenshot으로 현재 상태 캡처
   - 해당 시나리오를 FAIL로 기록
   - 다음 시나리오로 진행
```

### 브라우저 시작 실패

```
1. Agent-Browser 패키지 설치 상태 확인
2. 필요 시 의존성 재설치
3. 3회 재시도 실패 시 E2E 검증 전체를 SKIP으로 기록
```

### 도구 호환성 문제

```
1. ToolSearch로 사용 가능한 도구 재확인
2. 도구명이 예상과 다르면 매핑 표 갱신
3. 대체 도구가 없는 경우 사용자에게 다른 도구(Chrome MCP, Playwright MCP) 전환을 제안
```

## 증거 수집 패턴

모든 주요 동작 전후에 스크린샷과 스냅샷을 캡처한다:
- **Before**: 동작 수행 직전 `browser_screenshot()` + `browser_snapshot()`
- **After**: 동작 수행 후 `browser_screenshot()`
- **Evidence**: 검증 결과를 보여주는 `browser_screenshot()`

각 시나리오가 완료될 때마다 결과를 즉시 출력한다.