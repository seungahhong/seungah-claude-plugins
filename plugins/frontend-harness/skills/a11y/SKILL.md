---
name: a11y
description: React/JSX 코드에서 웹접근성(a11y, WAI-ARIA)을 점검하고 개선하는 스킬. 사용자가 "웹접근성", "접근성", "a11y", "aria", "스크린리더", "alt 텍스트", "키보드 접근", "포커스 관리", "WCAG" 등을 언급하거나, 컴포넌트 작성/리뷰 시 접근성 관련 문제를 발견하면 이 스킬을 사용합니다. ARIA 속성 적용, 키보드 내비게이션, 포커스 관리, 스크린리더 대응 등에 적용합니다.
---

# 웹접근성(WAI-ARIA) 가이드

React/JSX 코드의 웹접근성(WAI-ARIA 1.2, WCAG 2.1) 준수를 돕는 스킬입니다.

## 핵심 원칙

**시맨틱 HTML 우선 (First Rule of ARIA)**
ARIA를 사용하기 전에 네이티브 HTML 요소로 해결할 수 있는지 먼저 확인합니다. `<button>`, `<nav>`, `<main>` 같은 네이티브 요소는 이미 접근성 의미를 내장하고 있어 ARIA가 불필요합니다.

```tsx
// 잘못된 예시
<div role="button" onClick={handleClick}>클릭</div>

// 올바른 예시
<button onClick={handleClick}>클릭</button>
```

## ARIA 속성 카테고리

**역할(Roles)**: 요소의 목적을 정의
- 랜드마크: `banner`, `navigation`, `main`, `complementary`, `contentinfo`
- 위젯: `dialog`, `tablist`, `tab`, `tabpanel`, `menu`, `menuitem`, `alert`
- 문서 구조: `heading`, `list`, `listitem`, `img`

**상태(States)**: 변경 가능한 현재 상태
- `aria-expanded`: 확장/축소 상태 (아코디언, 드롭다운)
- `aria-selected`: 선택 상태 (탭, 리스트 항목)
- `aria-checked`: 체크 상태 (체크박스, 토글)
- `aria-disabled`: 비활성 상태
- `aria-hidden`: 보조 기술에서 숨김

**속성(Properties)**: 요소의 특성을 정의
- `aria-label`: 접근 가능한 이름 제공
- `aria-labelledby`: 다른 요소의 텍스트로 이름 제공
- `aria-describedby`: 추가 설명 연결
- `aria-live`: 동적 콘텐츠 변경 알림 (`polite`, `assertive`)
- `aria-required`: 필수 입력 표시
- `aria-invalid`: 유효성 검사 실패 표시
- `aria-modal`: 모달 다이얼로그 표시

## React에서 ARIA 상태 동기화

ARIA 상태는 React 상태와 반드시 동기화해야 합니다.

```tsx
const [isOpen, setIsOpen] = useState(false);

<button aria-expanded={isOpen} onClick={() => setIsOpen(!isOpen)}>
  메뉴
</button>
<ul role="menu" aria-hidden={!isOpen}>
  {/* 메뉴 항목 */}
</ul>
```

## 컴포넌트별 접근성 체크리스트

### 이미지

```tsx
// 정보성 이미지: alt 필수
<img src={src} alt="프로젝트 대표 이미지" />

// 장식용 이미지: 빈 alt + aria-hidden
<img src={decorative} alt="" aria-hidden="true" />

// 아이콘 버튼: aria-label 필수
<button aria-label="닫기">
  <CloseIcon aria-hidden="true" />
</button>
```

### 폼 요소

```tsx
// label 연결 필수
<label htmlFor="email">이메일</label>
<input id="email" type="email" aria-required="true" />

// 에러 메시지 연결
<input id="email" aria-invalid={!!error} aria-describedby="email-error" />
{error && <span id="email-error" role="alert">{error}</span>}
```

### 모달/다이얼로그

```tsx
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-desc"
>
  <h2 id="modal-title">제목</h2>
  <p id="modal-desc">설명</p>
</div>
```

### 탭 패널

```tsx
<div role="tablist" aria-label="콘텐츠 탭">
  <button role="tab" aria-selected={activeTab === 0} aria-controls="panel-0">
    탭 1
  </button>
</div>
<div role="tabpanel" id="panel-0" aria-labelledby="tab-0">
  콘텐츠
</div>
```

## 키보드 접근성

- 모든 인터랙티브 요소는 키보드로 접근 가능해야 합니다
- Tab 순서가 시각적 순서와 일치해야 합니다
- 모달 오픈 시 포커스 트랩을 구현합니다
- Escape로 모달/드롭다운/컨텍스트 메뉴 닫기를 지원합니다

### tabIndex 사용 규칙

| 값 | 용도 | 규칙 |
|----|------|------|
| `tabIndex={0}` | 비인터랙티브 요소를 Tab 순서에 포함 | `<div>`, `<span>` 등에 키보드 접근이 필요할 때만 사용. 네이티브 인터랙티브 요소(`<button>`, `<a>`, `<input>`)에는 불필요 |
| `tabIndex={-1}` | Tab 순서에서 제외하되 프로그래밍적 포커스 허용 | 모달/다이얼로그 컨테이너, 포커스 이동 대상, 비활성 탭 패널 등에 사용 |
| `tabIndex > 0` | **사용 금지** | 양수 tabIndex는 Tab 순서를 예측 불가능하게 만듬. DOM 순서로 제어할 것 |

```tsx
// 올바른 예시: 프로그래밍적 포커스가 필요한 모달
<div ref={modalRef} tabIndex={-1} role="dialog">
  {/* 모달 내용 */}
</div>

// 잘못된 예시: 네이티브 요소에 불필요한 tabIndex
<button tabIndex={0}>클릭</button>  // button은 기본적으로 포커스 가능
<a href="/link" tabIndex={0}>링크</a>  // a[href]도 기본적으로 포커스 가능
```

### 키보드 인터랙션 패턴

**버튼/링크**: Enter 및 Space로 활성화
```tsx
// <button>은 Enter/Space를 네이티브로 지원합니다. 추가 핸들러 불필요.
<button onClick={handleClick}>클릭</button>

// <div onClick>을 부득이 사용하는 경우 (지양)
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }}
>
  클릭
</div>
```

**모달/다이얼로그**: Escape로 닫기 + 포커스 트랩
```tsx
const modalRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (isOpen) {
    modalRef.current?.focus();
  }
}, [isOpen]);

// Escape 키로 닫기
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === 'Escape') {
    onClose();
  }
};

<div
  ref={modalRef}
  role="dialog"
  aria-modal="true"
  tabIndex={-1}
  onKeyDown={handleKeyDown}
>
  {/* 모달 내용 */}
</div>
```

**메뉴 (role="menu")**: Arrow 키로 항목 탐색, Escape로 닫기
```tsx
const handleMenuKeyDown = (e: React.KeyboardEvent) => {
  switch (e.key) {
    case 'Escape':
      onClose();
      break;
    case 'ArrowDown':
      e.preventDefault();
      // 다음 menuitem으로 포커스 이동
      focusNextItem();
      break;
    case 'ArrowUp':
      e.preventDefault();
      // 이전 menuitem으로 포커스 이동
      focusPrevItem();
      break;
  }
};

<div role="menu" onKeyDown={handleMenuKeyDown}>
  <button role="menuitem" tabIndex={-1}>항목 1</button>
  <button role="menuitem" tabIndex={-1}>항목 2</button>
</div>
```

**탭 (role="tablist")**: Arrow 키로 탭 전환
```tsx
const handleTabKeyDown = (e: React.KeyboardEvent, index: number) => {
  let nextIndex = index;
  if (e.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
  if (e.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
  if (nextIndex !== index) {
    e.preventDefault();
    setActiveTab(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  }
};

<div role="tablist">
  {tabs.map((tab, index) => (
    <button
      role="tab"
      aria-selected={activeTab === index}
      tabIndex={activeTab === index ? 0 : -1}
      onKeyDown={(e) => handleTabKeyDown(e, index)}
    >
      {tab.label}
    </button>
  ))}
</div>
```

**내비게이션 탭바 (`<nav>` 기반)**: Arrow 키로 탭 이동, 선택된 탭만 Tab 순서에 포함

내비게이션 탭바는 `role="tablist"`가 아닌 `<nav>` 요소를 사용합니다. 페이지 라우팅을 전환하는 탭바에 적합합니다.

```tsx
const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

const handleTabKeyDown = (e: React.KeyboardEvent, index: number) => {
  let nextIndex = index;
  // 세로 탭바: ArrowUp/ArrowDown, 가로 탭바: ArrowLeft/ArrowRight
  if (e.key === 'ArrowDown') nextIndex = (index + 1) % items.length;
  if (e.key === 'ArrowUp') nextIndex = (index - 1 + items.length) % items.length;
  if (nextIndex !== index) {
    e.preventDefault();
    handleClick(items[nextIndex]);
    tabRefs.current[nextIndex]?.focus();
  }
};

<nav aria-label="메이커 메뉴">
  {items.map((item, index) => (
    <button
      aria-current={isSelected ? 'page' : undefined}
      tabIndex={isSelected ? 0 : -1}
      ref={(el) => { tabRefs.current[index] = el; }}
      onClick={() => handleClick(item)}
      onKeyDown={(e) => handleTabKeyDown(e, index)}
    >
      {item.label}
    </button>
  ))}
</nav>
```

> **`role="tablist"` vs `<nav>` 사용 기준**
> - `role="tablist"` + `role="tab"`: 같은 페이지 내에서 패널 콘텐츠를 전환하는 경우 (예: 문의/의견 탭)
> - `<nav>` + `aria-current="page"`: 페이지 라우팅을 전환하는 탭바 (예: 대시보드/광고/정산 탭바)
>
> 두 경우 모두 **선택된 탭만 `tabIndex={0}`**, 나머지는 `tabIndex={-1}`로 설정하여 Arrow 키로만 탐색하도록 합니다.

**드롭다운 트리거**: aria-expanded + aria-haspopup
```tsx
<button
  aria-expanded={isOpen}
  aria-haspopup="menu"
  onClick={() => setIsOpen(!isOpen)}
>
  설정
</button>
```

### 포커스 관리 원칙

1. **모달 열기**: 모달 내 첫 번째 포커스 가능한 요소로 포커스 이동
2. **모달 닫기**: 모달을 열었던 트리거 요소로 포커스 복귀
3. **포커스 트랩**: 모달 내에서 Tab/Shift+Tab으로 순환 (모달 외부로 나가지 않음)
4. **콘텐츠 삭제**: 삭제된 요소 다음 포커스 가능한 요소로 이동
5. **비활성 탭 패널**: `tabIndex={-1}`로 Tab 순서에서 제외

## 코드 리뷰 시 점검 항목

1. **이미지 alt**: 모든 `<img>`에 적절한 alt 텍스트가 있는지
2. **폼 레이블**: 모든 입력 필드에 `<label>` 또는 `aria-label`이 연결되었는지
3. **인터랙티브 요소**: `<div onClick>`이 아닌 `<button>` 또는 `<a>` 사용 여부
4. **ARIA 상태 동기화**: React 상태와 ARIA 속성 일치 여부
5. **키보드 접근**: Tab 키로 모든 기능에 접근 가능한지
6. **포커스 관리**: 모달, 라우트 전환 시 포커스 이동이 적절한지
7. **색상 대비**: 텍스트와 배경 간 충분한 대비 비율 (WCAG AA: 4.5:1)
8. **동적 콘텐츠**: 상태 변경 시 `aria-live` 영역으로 알림 제공 여부

## 흔한 실수와 안티패턴

| 안티패턴 | 개선 방법 |
|----------|-----------|
| `<div role="button">` | `<button>` (네이티브 HTML 우선) |
| `<img>` alt 누락 | `alt="설명"` 또는 `alt="" aria-hidden="true"` |
| `<input>` label 없음 | `<label htmlFor>` 연결 또는 `aria-label` |
| ARIA 남용 | 네이티브 HTML 요소 우선 사용 |
| `aria-hidden="true"` on focusable | 포커스 가능한 요소에 aria-hidden 사용 금지 |
| `tabIndex > 0` | 양수 tabIndex 사용 금지, DOM 순서로 제어 |
| ARIA 상태 미동기화 | React 상태 변경 시 aria-expanded 등 함께 갱신 |
| 아이콘 버튼 이름 없음 | `aria-label` 필수 제공 |

상세 컴포넌트 패턴은 `references/aria-patterns.md`를 참조합니다.

## 관련 스킬

- 시맨틱 HTML 태그 선택에 대해서는 [semantic-html 스킬](../semantic-html/SKILL.md)을 참조합니다.
- ARIA는 시맨틱 HTML로 해결할 수 없는 경우에만 사용합니다 (First Rule of ARIA).

## 참고 문서

- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [React 접근성 문서](https://legacy.reactjs.org/docs/accessibility.html)
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/)
