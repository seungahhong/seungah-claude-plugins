---
name: semantic-html
description: React/JSX 코드에서 시맨틱 HTML 태그 사용을 점검하고 개선하는 스킬. 사용자가 "시맨틱", "semantic", "시맨틱 태그", "HTML 구조", "div 남용", "제목 계층", "heading", "랜드마크" 등을 언급하거나, 페이지 레이아웃/컴포넌트의 HTML 구조를 작성/리뷰할 때 이 스킬을 사용합니다. div/span을 시맨틱 태그로 변환하거나, 페이지 구조의 의미적 마크업을 개선하는 작업에 적용합니다.
---

# 시맨틱 HTML 가이드

React/JSX 코드의 시맨틱 HTML(WHATWG HTML Living Standard) 준수를 돕는 스킬입니다.

## 핵심 원칙

HTML 요소는 시각적 표현이 아닌 콘텐츠의 **의미**에 따라 선택합니다. 시맨틱 태그를 올바르게 사용하면 스크린리더 내비게이션, 검색엔진 최적화, 코드 가독성이 모두 향상됩니다.

## 페이지 구조 태그

| 태그 | 용도 | 규칙 | 암묵적 ARIA 역할 |
|------|------|------|-----------------|
| `<header>` | 페이지/섹션 헤더 | 페이지당 여러 개 가능, `<main>` 안밖 모두 사용 가능 | `banner` (최상위일 때) |
| `<nav>` | 주요 내비게이션 | 주요 내비게이션에만 사용, 모든 링크 목록에 남용하지 않음 | `navigation` |
| `<main>` | 페이지 고유 콘텐츠 | **문서당 1개만**, `<header>`, `<footer>`, `<nav>` 외부 | `main` |
| `<article>` | 독립적 콘텐츠 | 단독 배포/재사용 가능한 콘텐츠 (블로그 글, 카드 등) | `article` |
| `<section>` | 주제별 콘텐츠 그룹 | 제목(`<h2>`~`<h6>`)과 함께 사용, 단순 스타일링용은 `<div>` | `region` (이름 있을 때) |
| `<aside>` | 보조 콘텐츠 | 메인 콘텐츠와 간접적으로 관련된 내용 (사이드바 등) | `complementary` |
| `<footer>` | 페이지/섹션 푸터 | 페이지당 여러 개 가능 | `contentinfo` (최상위일 때) |

## 텍스트/콘텐츠 태그

| 태그 | 용도 | 잘못된 사용 |
|------|------|------------|
| `<h1>`~`<h6>` | 제목 계층 | 레벨 건너뛰기 금지 (h1 -> h3), 스타일링 목적으로 사용 금지 |
| `<p>` | 문단 | 레이아웃 간격용으로 사용 금지 |
| `<ul>`, `<ol>` | 목록 | 내비게이션 메뉴도 목록으로 마크업 가능 |
| `<figure>` + `<figcaption>` | 캡션이 있는 콘텐츠 | 이미지, 코드 블록, 차트 등에 사용 |
| `<time>` | 날짜/시간 | `datetime` 속성으로 기계 판독 가능한 값 제공 |
| `<address>` | 연락처 정보 | 물리적 주소뿐 아니라 이메일, 링크 등 포함 |
| `<small>` | 부가 정보 | 저작권, 법적 고지 등 |

## div/span 대신 시맨틱 태그를 써야 하는 경우

- 레이아웃 영역 구분: `<div>` 대신 `<header>`, `<main>`, `<footer>`, `<aside>`
- 내비게이션 링크 그룹: `<div>` 대신 `<nav>`
- 독립 콘텐츠 블록: `<div>` 대신 `<article>`
- 주제별 그룹핑 (제목 포함): `<div>` 대신 `<section>`
- 클릭 가능한 요소: `<div onClick>` 대신 `<button>` 또는 `<a>`

## div/span이 적절한 경우

- 순수 스타일링/레이아웃 래퍼 (CSS Grid, Flexbox 컨테이너)
- 의미적 구분이 불필요한 인라인 텍스트 강조
- JavaScript 이벤트 핸들러용 래퍼 (단, 인터랙티브 요소는 `<button>` 등 사용)

## 제목 계층 규칙

```tsx
// 올바른 예시: 순차적 계층
<h1>메이커 홈</h1>
  <h2>대시보드</h2>
    <h3>매출 현황</h3>
    <h3>프로젝트 현황</h3>
  <h2>내 프로젝트</h2>

// 잘못된 예시: 레벨 건너뛰기
<h1>메이커 홈</h1>
  <h3>매출 현황</h3>  // h2를 건너뜀
```

- 페이지당 `<h1>`은 1개를 권장합니다
- 시각적 크기가 아닌 콘텐츠 계층에 따라 레벨을 결정합니다
- CSS로 시각적 크기를 조정하되 태그 레벨은 구조에 맞춥니다

## 코드 리뷰 시 점검 항목

1. **div 남용 여부**: 의미가 있는 영역에 `<div>` 대신 적절한 시맨틱 태그를 사용했는지
2. **제목 계층**: `<h1>`~`<h6>` 순서가 올바른지 (건너뛰기 금지)
3. **인터랙티브 요소**: `<div onClick>`이 아닌 `<button>` 또는 `<a>` 사용 여부
4. **랜드마크 구조**: 페이지에 `<header>`, `<main>`, `<footer>`, `<nav>` 등 기본 랜드마크가 있는지
5. **목록 마크업**: 나열형 콘텐츠에 `<ul>`, `<ol>` 사용 여부

## 흔한 안티패턴

| 안티패턴 | 개선 방법 |
|----------|-----------|
| `<div className="header">` | `<header>` |
| `<div className="nav">` | `<nav>` |
| `<div className="footer">` | `<footer>` |
| `<div className="sidebar">` | `<aside>` |
| `<div className="card">` (독립 콘텐츠) | `<article>` |
| `<div className="title">제목</div>` | `<h2>제목</h2>` (적절한 레벨) |
| `<div onClick={fn}>` | `<button onClick={fn}>` |
| `<a onClick={fn}>` (href 없음) | `<button onClick={fn}>` |
| `<b>` (의미 없이 굵게) | `<strong>` (중요성 강조) |
| `<i>` (의미 없이 기울임) | `<em>` (강세 강조) |

## 변환 예시

```tsx
// 변환 전
const Layout = ({ children }) => (
  <div className="page">
    <div className="top-bar">
      <div className="logo">TEST</div>
      <div className="nav-links">
        <a href="/test1">test1</a>
        <a href="/test2">test2</a>
      </div>
    </div>
    <div className="content">{children}</div>
    <div className="sidebar">
      <div className="widget">인기 프로젝트</div>
    </div>
    <div className="bottom">
      <div>© 회사</div>
    </div>
  </div>
);

// 변환 후
const Layout = ({ children }) => (
  <div className="page">
    <header className="top-bar">
      <div className="logo">TEST</div>
      <nav className="nav-links">
        <a href="/test1">test1</a>
        <a href="/test2">test2</a>
      </nav>
    </header>
    <main className="content">{children}</main>
    <aside className="sidebar">
      <section className="widget">
        <h2>인기 프로젝트</h2>
      </section>
    </aside>
    <footer className="bottom">
      <p>© 회사</p>
    </footer>
  </div>
);
```

## 관련 스킬

- 시맨틱 태그의 접근성 속성(ARIA)에 대해서는 [a11y 스킬](../a11y/SKILL.md)을 참조합니다.
- 시맨틱 구조는 접근성의 기반이 됩니다 — 두 스킬을 함께 적용하면 가장 효과적입니다.

## 참고 문서

- [WHATWG HTML Living Standard](https://html.spec.whatwg.org/)
