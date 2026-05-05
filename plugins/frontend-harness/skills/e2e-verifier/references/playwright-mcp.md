# Playwright MCP 실행 패턴

Playwright 기반의 `@playwright/mcp`를 사용하여 E2E 검증을 수행할 때의 상세 패턴.
별도의 브라우저 인스턴스를 자동으로 실행하며, 접근성 스냅샷 기반으로 요소를 식별한다.

## 사전 조건 확인 절차

### 1. MCP 연동 확인

`.mcp.json` 파일에 playwright 설정이 있는지 확인한다.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

**헤드리스 모드** (브라우저 창 없이 실행):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--headless"]
    }
  }
}
```

없으면 사용자에게 설정 추가와 Claude Code 재시작을 안내한다.

### 2. Playwright 브라우저 설치 확인

Playwright가 브라우저를 자동으로 관리하므로 Chrome 디버깅 모드가 필요 없다.
다만 최초 사용 시 브라우저 바이너리가 필요할 수 있다:

```bash
npx playwright install chromium
```

설치되어 있지 않으면 사용자에게 안내한다.

### 3. 개발 서버 확인

`mcp__playwright__browser_navigate`로 개발 서버 URL에 접근하여 페이지가 정상 로드되는지 확인한다.

## Chrome MCP와의 차이

| 항목 | Chrome MCP | Playwright MCP |
|------|-----------|---------------|
| 브라우저 실행 | 사용자가 직접 Chrome 디버깅 모드 실행 | Playwright가 자동 실행/관리 |
| 요소 식별 | CSS 선택자 기반 | 접근성 스냅샷(ref) + CSS 선택자 |
| 스크린샷 | `take_screenshot` | `browser_screenshot` |
| JS 실행 | `evaluate_script` | `browser_evaluate` |
| 네트워크 분석 | `list_network_requests` | `browser_network_requests` |
| 헤드리스 지원 | 별도 설정 필요 | `--headless` 플래그 |

## 도구 매핑

| 동작 | Playwright MCP 도구 | 주요 파라미터 |
|------|-------------------|-------------|
| 페이지 이동 | `browser_navigate` | `url` |
| 스크린샷 | `browser_screenshot` | 없음 (현재 페이지 전체) |
| 스냅샷 (접근성 트리) | `browser_snapshot` | 없음 |
| 요소 클릭 | `browser_click` | `element` (스냅샷 ref) 또는 `selector` |
| 텍스트 입력 | `browser_type` | `element`, `text`, `submit` (선택) |
| 드롭다운 선택 | `browser_select_option` | `element`, `values` |
| 키 입력 | `browser_press_key` | `key` |
| 호버 | `browser_hover` | `element` |
| 드래그 | `browser_drag` | `startElement`, `endElement` |
| JS 실행 | `browser_evaluate` | `javascript` |
| 텍스트 대기 | `browser_wait_for_text` | `text`, `timeout` (선택) |
| 네트워크 요청 | `browser_network_requests` | 없음 |
| 콘솔 메시지 | `browser_console_messages` | 없음 |
| 파일 업로드 | `browser_file_upload` | `paths` |
| 다이얼로그 처리 | `browser_handle_dialog` | `accept`, `promptText` |
| 탭 목록 | `browser_tab_list` | 없음 |
| 새 탭 | `browser_tab_new` | `url` |
| 탭 선택 | `browser_tab_select` | `index` |
| 탭 닫기 | `browser_tab_close` | `index` (선택) |
| 브라우저 크기 조절 | `browser_resize` | `width`, `height` |
| PDF 생성 | `browser_generate_pdf` | 없음 |
| 브라우저 닫기 | `browser_close` | 없음 |

## 접근성 스냅샷 기반 요소 식별

Playwright MCP의 가장 큰 특징은 **접근성 스냅샷**을 사용하여 요소를 식별한다는 점이다.

### 스냅샷 활용 흐름

```
1. browser_snapshot() — 현재 페이지의 접근성 트리를 텍스트로 반환
2. 스냅샷에서 대상 요소의 ref 값 확인
3. browser_click(element: "ref값") — ref를 사용하여 요소 조작
```

**스냅샷 출력 예시:**
```
- navigation "Main Navigation"
  - link "홈" [ref=s1]
  - link "대시보드" [ref=s2]
  - button "메뉴" [ref=s3]
- main
  - heading "광고 성과" [ref=s4]
  - button "기간 선택" [ref=s5]
  - table "성과 테이블" [ref=s6]
    - row "캠페인 A | 1,234 | 5.6%" [ref=s7]
```

### CSS 선택자 대체 사용

스냅샷에서 요소를 찾을 수 없거나, CSS 선택자가 더 정확한 경우:
```
browser_click(selector: "[data-testid='submit-btn']")
```

스냅샷 ref와 CSS 선택자를 모두 지원하므로 상황에 맞게 선택한다.

## 페이지 이동 패턴

### 최초 진입

```
1. browser_navigate(url: "개발서버URL") — 최초 1회만 허용
2. browser_wait_for_text(text: "페이지 로드 완료 텍스트")
3. browser_snapshot() — 접근성 트리로 페이지 구조 파악
4. browser_screenshot() — 시각적 화면 확인
```

### 페이지 내 이동

```
1. browser_snapshot() — 현재 페이지의 접근성 트리 확인
2. 이동할 링크/메뉴의 ref 식별
3. browser_click(element: "ref값") — 스냅샷 ref로 클릭
4. browser_wait_for_text(text: "이동 완료 텍스트")
5. browser_screenshot() — 이동 결과 확인
```

## 요소 인터랙션 패턴

### 클릭

```
1. browser_snapshot() — 대상 요소 ref 확인
2. browser_click(element: "ref값")
3. browser_wait_for_text(text: "클릭 결과 텍스트")
4. browser_screenshot() — 결과 확인
```

### 텍스트 입력

```
1. browser_snapshot() — 입력 필드 ref 확인
2. browser_click(element: "입력필드 ref") — 포커스
3. browser_type(element: "입력필드 ref", text: "입력값")
4. browser_screenshot() — 입력 결과 확인
```

폼 제출과 함께 입력:
```
browser_type(element: "ref", text: "입력값", submit: true)
```

### 드롭다운 선택

```
1. browser_snapshot() — select 요소 ref 확인
2. browser_select_option(element: "ref", values: ["선택값"])
3. browser_screenshot() — 선택 결과 확인
```

### 스크롤

```
1. browser_evaluate(javascript: "window.scrollTo(0, document.body.scrollHeight)")
2. browser_snapshot() — 스크롤 후 접근성 트리 확인
3. browser_screenshot() — 스크롤 결과 확인
```

## 상태 검증 패턴

### 접근성 스냅샷 기반 검증

스냅샷에서 요소의 존재, 텍스트, 역할을 직접 확인할 수 있다:

```
1. browser_snapshot() — 접근성 트리 조회
2. 스냅샷 텍스트에서 기대 요소/텍스트 검색
3. 존재하면 PASS, 없으면 FAIL
```

### JavaScript 기반 검증

더 세밀한 검증이 필요한 경우:

```javascript
// browser_evaluate로 실행
JSON.stringify({
  exists: !!document.querySelector("대상 선택자"),
  text: document.querySelector("대상 선택자")?.textContent?.trim(),
  count: document.querySelectorAll("대상 선택자").length
})
```

## 에러 복구 패턴

### 요소 미발견

```
1. browser_snapshot() — 접근성 트리에서 유사 요소 탐색
2. browser_screenshot() — 시각적 확인
3. 여전히 찾을 수 없으면:
   - 스냅샷과 스크린샷을 함께 사용자에게 제시
   - 사용자 안내를 받아 재시도
```

### 타임아웃

```
1. browser_wait_for_text의 timeout 값을 2배로 증가하여 재시도
2. 여전히 타임아웃이면:
   - browser_screenshot으로 현재 상태 캡처
   - 해당 시나리오를 FAIL로 기록
   - 다음 시나리오로 진행
```

### 브라우저 시작 실패

```
1. Playwright 브라우저 설치 확인: npx playwright install chromium
2. 설치 후 Claude Code 재시작
3. 3회 재시도 실패 시 E2E 검증 전체를 SKIP으로 기록
```

## 증거 수집 패턴

모든 주요 동작 전후에 스크린샷과 스냅샷을 캡처한다:
- **Before**: 동작 수행 직전 `browser_screenshot()` + `browser_snapshot()`
- **After**: 동작 수행 후 `browser_screenshot()`
- **Evidence**: 검증 결과를 보여주는 `browser_screenshot()`

각 시나리오가 완료될 때마다 결과를 즉시 출력한다.