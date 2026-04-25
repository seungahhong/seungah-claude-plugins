# Chrome DevTools MCP 실행 패턴

Chrome DevTools Protocol 기반의 `chrome-devtools-mcp`를 사용하여 E2E 검증을 수행할 때의 상세 패턴.
이미 실행 중인 Chrome 브라우저에 연결하여 제어하는 방식이다.

## 사전 조건 확인 절차

### 1. MCP 연동 확인

`.mcp.json` 파일에 chrome-devtools 설정이 있는지 확인한다.

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

없으면 사용자에게 설정 추가와 Claude Code 재시작을 안내한다.

### 2. Chrome 디버깅 모드 확인

Chrome이 디버깅 포트로 실행되어 있어야 한다. 연결 실패 시:

```
Chrome 브라우저가 디버깅 모드로 실행되어 있는지 확인해 주세요.
다음 명령으로 Chrome을 실행할 수 있습니다:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

### 3. 개발 서버 확인

`mcp__chrome-devtools__navigate_page`로 개발 서버 URL에 접근하여 페이지가 정상 로드되는지 확인한다.
로드 실패 시 사용자에게 개발 서버 실행 상태를 확인하도록 안내한다.

## 도구 매핑

| 동작 | Chrome MCP 도구 | 주요 파라미터 |
|------|----------------|-------------|
| 페이지 이동 | `navigate_page` | `url` |
| 스크린샷 | `take_screenshot` | `fullPage` (선택) |
| 스냅샷 (접근성 트리) | `take_snapshot` | `verbose` (선택) |
| 요소 클릭 | `click` | `selector` (CSS 선택자) |
| 텍스트 입력 | `fill` | `selector`, `value` |
| 폼 입력 | `fill_form` | 요소 배열 (`uid`, `value`) |
| 키 입력 | `press_key` | `key` |
| 호버 | `hover` | `selector` |
| 조건 대기 | `wait_for` | `text` (배열) |
| JS 실행 | `evaluate_script` | `script` |
| 네트워크 요청 목록 | `list_network_requests` | `resourceTypes` (선택) |
| 네트워크 요청 상세 | `get_network_request` | `reqid` |
| 페이지 목록 | `list_pages` | 없음 |
| 새 페이지 | `new_page` | `url` |
| 페이지 닫기 | `close_page` | `pageId` |
| 디바이스 에뮬레이션 | `emulate` | `viewport`, `userAgent` 등 |

## 페이지 이동 패턴

### 핵심 원칙: 화면 UI 기반 이동

> `navigate_page`는 **최초 URL 진입 시에만** 사용한다.
> 이후 모든 페이지 이동은 화면에 보이는 링크, 버튼, 메뉴를 `click`하여 수행한다.
> URL을 임의로 구성하거나 추측하여 직접 이동하지 않는다.

**최초 진입:**
```
1. navigate_page(url: "개발서버URL") — 최초 1회만 허용
2. wait_for(text: ["페이지 로드 완료 텍스트"])
3. take_screenshot() — 초기 화면 확인
```

**페이지 내 이동:**
```
1. take_screenshot() — 현재 화면 확인
2. 이동할 링크/메뉴/버튼 식별
3. click(selector: "해당 요소") — UI 요소 클릭으로 이동
4. wait_for(text: ["이동 완료 텍스트"])
5. take_screenshot() — 이동 결과 확인
```

**이동할 요소를 찾을 수 없는 경우:**
- 사용자에게 해당 페이지로의 이동 경로(어떤 메뉴/링크를 클릭해야 하는지)를 문의한다
- URL을 추측하여 `navigate_page`로 이동하지 않는다

## 요소 인터랙션 패턴

### 클릭 (click)

```
1. take_screenshot() — 클릭 대상 요소 확인
2. click(selector: "대상 요소 CSS 선택자")
3. wait_for(text: ["클릭 결과 텍스트"]) — 1~3초
4. take_screenshot() — 클릭 결과 확인
```

선택자 우선순위:
1. `data-testid` 속성 (`[data-testid="submit-btn"]`)
2. 고유 ID (`#submit-button`)
3. 역할 기반 (`button[type="submit"]`)
4. 텍스트 기반 (최후 수단)

### 텍스트 입력 (fill)

```
1. take_screenshot() — 입력 필드 확인
2. click(selector: "입력 필드") — 포커스 이동
3. fill(selector: "입력 필드", value: "입력값")
4. take_screenshot() — 입력 결과 확인
```

### 스크롤 (evaluate_script)

```
1. evaluate_script(script: "window.scrollTo(0, document.body.scrollHeight)")
2. wait_for(text: ["스크롤 완료"]) — 0.5~1초
3. take_screenshot() — 스크롤 결과 확인
```

특정 요소까지 스크롤:
```javascript
document.querySelector("대상 선택자").scrollIntoView({ behavior: "smooth" })
```

### 호버 (hover)

```
1. hover(selector: "대상 요소")
2. wait_for(text: ["호버 효과"]) — 0.5초
3. take_screenshot() — 호버 결과 확인
```

## 상태 검증 패턴

### 요소 존재 확인

```javascript
// evaluate_script로 실행
JSON.stringify({
  exists: !!document.querySelector("대상 선택자"),
  count: document.querySelectorAll("대상 선택자").length
})
```

### 텍스트 내용 확인

```javascript
JSON.stringify({
  text: document.querySelector("대상 선택자")?.textContent?.trim(),
  expected: "기대 텍스트"
})
```

### 요소 가시성 확인

```javascript
(() => {
  const el = document.querySelector("대상 선택자");
  if (!el) return JSON.stringify({ visible: false, reason: "요소 없음" });
  const style = window.getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  return JSON.stringify({
    visible: style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0" && rect.height > 0,
    display: style.display,
    visibility: style.visibility
  });
})()
```

### CSS 클래스/스타일 확인

```javascript
JSON.stringify({
  classes: [...document.querySelector("대상 선택자").classList],
  hasClass: document.querySelector("대상 선택자").classList.contains("expected-class")
})
```

### 입력 필드 값 확인

```javascript
JSON.stringify({
  value: document.querySelector("input 선택자").value,
  expected: "기대값"
})
```

## 에러 복구 패턴

### 요소 미발견

```
1. take_screenshot() — 현재 화면 상태 확인
2. evaluate_script로 유사 요소 탐색:
   document.querySelectorAll("*[class*='keyword']")
3. 여전히 찾을 수 없으면:
   - 스크린샷과 함께 사용자에게 요소 위치/선택자를 문의
   - 사용자 안내를 받아 재시도
```

### 타임아웃

```
1. wait_for 시간을 2배로 증가하여 재시도 (최대 10초)
2. 여전히 타임아웃이면:
   - take_screenshot으로 현재 상태 캡처
   - 해당 시나리오를 FAIL로 기록
   - 다음 시나리오로 진행
```

### 연결 실패

```
1. Chrome 디버깅 모드 실행 여부 확인 안내
2. 사용자가 Chrome을 재시작한 후 재시도
3. 3회 재시도 실패 시 E2E 검증 전체를 SKIP으로 기록
```

### 페이지 로드 실패

```
1. 개발 서버 실행 상태 확인 안내
2. 사용자가 서버를 재시작한 후 재시도
3. URL이 변경되었을 수 있으므로 사용자에게 URL 재확인
```

## 증거 수집 패턴

모든 주요 동작 전후에 스크린샷을 캡처한다:
- **Before**: 동작 수행 직전 `take_screenshot()`
- **After**: 동작 수행 후 `take_screenshot()`
- **Evidence**: 검증 결과를 보여주는 `take_screenshot()`

각 시나리오가 완료될 때마다 결과를 즉시 출력한다.