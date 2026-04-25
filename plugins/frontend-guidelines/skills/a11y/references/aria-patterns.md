# ARIA 패턴 상세 가이드

WAI-ARIA 1.2 기반 인터랙티브 컴포넌트 패턴입니다.

## 목차

1. [아코디언](#아코디언)
2. [드롭다운 메뉴](#드롭다운-메뉴)
3. [탭 인터페이스](#탭-인터페이스)
4. [모달 다이얼로그](#모달-다이얼로그)
5. [토스트/알림](#토스트알림)
6. [툴팁](#툴팁)
7. [브레드크럼](#브레드크럼)
8. [페이지네이션](#페이지네이션)
9. [검색 자동완성](#검색-자동완성)
10. [캐러셀/슬라이더](#캐러셀슬라이더)

---

## 아코디언

```tsx
interface AccordionItemProps {
  id: string;
  title: string;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const AccordionItem = ({ id, title, isOpen, onToggle, children }: AccordionItemProps) => (
  <>
    <h3>
      <button
        aria-expanded={isOpen}
        aria-controls={`panel-${id}`}
        id={`header-${id}`}
        onClick={onToggle}
      >
        {title}
      </button>
    </h3>
    <div
      id={`panel-${id}`}
      role="region"
      aria-labelledby={`header-${id}`}
      hidden={!isOpen}
    >
      {children}
    </div>
  </>
);
```

키보드: Enter/Space로 토글, 화살표 키로 항목 간 이동

---

## 드롭다운 메뉴

```tsx
const DropdownMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(prev => Math.min(prev + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  };

  return (
    <div onKeyDown={handleKeyDown}>
      <button
        aria-haspopup="true"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
      >
        메뉴
      </button>
      {isOpen && (
        <ul role="menu" aria-label="메뉴 옵션">
          {items.map((item, i) => (
            <li
              key={item.id}
              role="menuitem"
              tabIndex={i === activeIndex ? 0 : -1}
            >
              {item.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

키보드: 화살표 키로 항목 이동, Enter로 선택, Escape로 닫기

---

## 탭 인터페이스

```tsx
const Tabs = ({ tabs }: { tabs: TabItem[] }) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    let newIndex = activeTab;
    if (e.key === 'ArrowRight') newIndex = (activeTab + 1) % tabs.length;
    if (e.key === 'ArrowLeft') newIndex = (activeTab - 1 + tabs.length) % tabs.length;
    if (newIndex !== activeTab) {
      setActiveTab(newIndex);
      // 새 탭에 포커스 이동
    }
  };

  return (
    <>
      <div role="tablist" aria-label="콘텐츠 탭" onKeyDown={handleKeyDown}>
        {tabs.map((tab, i) => (
          <button
            key={tab.id}
            role="tab"
            id={`tab-${tab.id}`}
            aria-selected={activeTab === i}
            aria-controls={`panel-${tab.id}`}
            tabIndex={activeTab === i ? 0 : -1}
            onClick={() => setActiveTab(i)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.map((tab, i) => (
        <div
          key={tab.id}
          role="tabpanel"
          id={`panel-${tab.id}`}
          aria-labelledby={`tab-${tab.id}`}
          hidden={activeTab !== i}
          tabIndex={0}
        >
          {tab.content}
        </div>
      ))}
    </>
  );
};
```

키보드: 좌우 화살표로 탭 이동 (로빙 tabIndex 패턴)

---

## 모달 다이얼로그

```tsx
const Modal = ({ isOpen, onClose, title, children }: ModalProps) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      previousFocus.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();
    } else {
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  // 포커스 트랩
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
      return;
    }
    if (e.key === 'Tab') {
      const focusable = modalRef.current?.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusable?.length) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* 배경 오버레이 */}
      <div aria-hidden="true" onClick={onClose} />
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        onKeyDown={handleKeyDown}
      >
        <h2 id="modal-title">{title}</h2>
        {children}
        <button onClick={onClose} aria-label="닫기">X</button>
      </div>
    </>
  );
};
```

핵심: 포커스 트랩, Escape 닫기, 닫힌 후 이전 포커스 복원

---

## 토스트/알림

```tsx
// 상태 변경 알림용 라이브 영역
const ToastContainer = ({ messages }: { messages: Toast[] }) => (
  <div
    role="status"
    aria-live="polite"
    aria-atomic="true"
  >
    {messages.map(msg => (
      <div key={msg.id}>{msg.text}</div>
    ))}
  </div>
);

// 긴급 에러 알림
const ErrorAlert = ({ message }: { message: string }) => (
  <div role="alert" aria-live="assertive">
    {message}
  </div>
);
```

- `aria-live="polite"`: 현재 작업 완료 후 알림 (토스트, 성공 메시지)
- `aria-live="assertive"`: 즉시 알림 (에러, 긴급 메시지)
- `role="status"`: 암묵적으로 `aria-live="polite"`
- `role="alert"`: 암묵적으로 `aria-live="assertive"`

---

## 툴팁

```tsx
const Tooltip = ({ text, children }: TooltipProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const id = useId();

  return (
    <div
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
    >
      <span aria-describedby={isVisible ? id : undefined}>
        {children}
      </span>
      {isVisible && (
        <div id={id} role="tooltip">
          {text}
        </div>
      )}
    </div>
  );
};
```

키보드: 포커스로 표시, Escape로 숨기기

---

## 브레드크럼

```tsx
const Breadcrumb = ({ items }: { items: BreadcrumbItem[] }) => (
  <nav aria-label="현재 위치">
    <ol>
      {items.map((item, i) => (
        <li key={item.href}>
          {i < items.length - 1 ? (
            <a href={item.href}>{item.label}</a>
          ) : (
            <span aria-current="page">{item.label}</span>
          )}
        </li>
      ))}
    </ol>
  </nav>
);
```

---

## 페이지네이션

```tsx
const Pagination = ({ current, total, onChange }: PaginationProps) => (
  <nav aria-label="페이지 이동">
    <ul>
      <li>
        <button
          onClick={() => onChange(current - 1)}
          disabled={current === 1}
          aria-label="이전 페이지"
        >
          이전
        </button>
      </li>
      {pages.map(page => (
        <li key={page}>
          <button
            onClick={() => onChange(page)}
            aria-current={page === current ? 'page' : undefined}
            aria-label={`${page}페이지`}
          >
            {page}
          </button>
        </li>
      ))}
      <li>
        <button
          onClick={() => onChange(current + 1)}
          disabled={current === total}
          aria-label="다음 페이지"
        >
          다음
        </button>
      </li>
    </ul>
  </nav>
);
```

---

## 검색 자동완성

```tsx
const Autocomplete = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const listboxId = useId();

  return (
    <div>
      <input
        type="text"
        role="combobox"
        aria-expanded={suggestions.length > 0}
        aria-controls={listboxId}
        aria-activedescendant={activeIndex >= 0 ? `option-${activeIndex}` : undefined}
        aria-autocomplete="list"
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
      {suggestions.length > 0 && (
        <ul id={listboxId} role="listbox" aria-label="검색 제안">
          {suggestions.map((item, i) => (
            <li
              key={item}
              id={`option-${i}`}
              role="option"
              aria-selected={i === activeIndex}
            >
              {item}
            </li>
          ))}
        </ul>
      )}
      <div aria-live="polite" className="sr-only">
        {suggestions.length > 0 && `${suggestions.length}개의 검색 제안이 있습니다`}
      </div>
    </div>
  );
};
```

---

## 캐러셀/슬라이더

```tsx
const Carousel = ({ slides }: { slides: Slide[] }) => {
  const [current, setCurrent] = useState(0);

  return (
    <div
      role="region"
      aria-roledescription="캐러셀"
      aria-label="프로젝트 이미지"
    >
      <div aria-live="polite">
        {slides.map((slide, i) => (
          <div
            key={slide.id}
            role="group"
            aria-roledescription="슬라이드"
            aria-label={`${slides.length}개 중 ${i + 1}번째`}
            aria-hidden={i !== current}
          >
            <img src={slide.src} alt={slide.alt} />
          </div>
        ))}
      </div>
      <button
        aria-label="이전 슬라이드"
        onClick={() => setCurrent(prev => Math.max(0, prev - 1))}
      >
        이전
      </button>
      <button
        aria-label="다음 슬라이드"
        onClick={() => setCurrent(prev => Math.min(slides.length - 1, prev + 1))}
      >
        다음
      </button>
    </div>
  );
};
```

---

## 참고 문서

- [WHATWG HTML Living Standard](https://html.spec.whatwg.org/)
- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/)
- [ARIA Authoring Practices Guide](https://www.w3.org/WAI/ARIA/apg/)
- [React 접근성 문서](https://legacy.reactjs.org/docs/accessibility.html)
