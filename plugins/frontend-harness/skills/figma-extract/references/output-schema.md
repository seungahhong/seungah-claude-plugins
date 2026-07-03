# figma-extract 산출물 스키마

`figma-extract` 스킬이 화면당 내리는 산출물의 스키마와 고정 섹션 정의, 예시를 담는다.
경로: `.claude/design/{화면명-케밥}.json` / `{화면명-케밥}-spec.md` / `{화면명-케밥}-figma.png`.

---

## 1. `{화면명}.json` 스키마

추출한 raw를 정규화해 저장한다. 최상위 5개 필드는 고정이다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `tokens` | object | 디자인 토큰. `get_variable_defs` 결과를 색/간격/타이포로 정리 |
| `layout` | object | 레이아웃 구조(정렬·순서·구조). `get_design_context` 기반 |
| `components` | array | 화면을 구성하는 컴포넌트 목록(이름·역할·상태) |
| `assets` | array | 이미지·아이콘 등 에셋 목록(이름·타입·참조) |
| `capturedViewportWidth` | number | 캡처 기준 뷰포트 폭(px). **시각 정합 검증의 거짓 불일치 방지 전제** |

### 필드 상세

- **`tokens`**: `{ "color": {...}, "spacing": {...}, "typography": {...} }`. 변수명→값 매핑을 보존한다(예: `"color/primary": "#3D5AFE"`).
- **`layout`**: 최상위 컨테이너의 방향(row/column)·정렬·간격, 자식 노드의 순서를 트리로 기술한다. 픽셀 좌표보다 **정렬·순서·구조**를 우선 기록한다.
- **`components`**: `{ "name", "role", "states": [...] }`. Code Connect 매핑이 있으면 `codeComponent` 필드로 코드 컴포넌트명을 함께 기록한다.
- **`assets`**: `{ "name", "type", "ref" }`. `ref`는 `get_screenshot`/다운로드 경로 또는 노드 ID.
- **`capturedViewportWidth`**: `get_screenshot` 캡처에 사용한 폭. spec.md·visual-diff와 동일 값을 공유한다.

### JSON 예시

```json
{
  "tokens": {
    "color": { "color/primary": "#3D5AFE", "color/text/strong": "#1A1A1A" },
    "spacing": { "spacing/md": 16, "spacing/lg": 24 },
    "typography": { "heading/lg": "Pretendard 24/32 700" }
  },
  "layout": {
    "direction": "column",
    "gap": 24,
    "children": [
      { "node": "Header", "direction": "row", "justify": "space-between" },
      { "node": "MetricCardList", "direction": "row", "gap": 16, "order": 2 }
    ]
  },
  "components": [
    { "name": "MetricCard", "role": "지표 카드", "states": ["default", "loading"], "codeComponent": "MetricCard" },
    { "name": "PeriodDropdown", "role": "기간 선택", "states": ["closed", "open"] }
  ],
  "assets": [
    { "name": "ic_arrow_down", "type": "icon", "ref": "node:124:88" }
  ],
  "capturedViewportWidth": 1440
}
```

---

## 2. `{화면명}-spec.md` 고정 섹션

사람이 읽고 구현에 just-in-time으로 참조하는 명세다. 아래 6개 섹션을 **고정 순서·고정 제목**으로 작성한다.

| 섹션 | 내용 |
|------|------|
| `## 개요` | 화면 목적, Figma 노드/링크, 캡처 뷰포트 폭 |
| `## 레이아웃` | 정렬·순서·구조(json `layout` 요약). 반응형 분기가 있으면 명시 |
| `## 디자인 토큰` | 색·간격·타이포 값(json `tokens` 요약). 변수명→값 |
| `## 컴포넌트` | 컴포넌트별 역할·상태·Code Connect 매핑(json `components` 요약) |
| `## 에셋` | 이미지·아이콘 목록과 참조(json `assets` 요약) |
| `## 구현 메모` | 구현 시 주의점, 누락 위험, 인터랙션·상태 전이 등 |

> spec.md는 json의 사람이 읽는 요약이다. raw를 중복 복사하지 않고 핵심 값만 정리한다.

### spec.md 예시

```markdown
# 광고 대시보드 — spec

## 개요
- 목적: 광고 성과 지표를 카드와 차트로 표시
- Figma: https://figma.com/file/.../?node-id=124-88
- 캡처 뷰포트 폭: 1440px

## 레이아웃
- 최상위 column, gap 24
- Header(row, space-between) → MetricCardList(row, gap 16) → Chart 순

## 디자인 토큰
- color/primary: #3D5AFE
- spacing/md: 16, spacing/lg: 24
- heading/lg: Pretendard 24/32 700

## 컴포넌트
- MetricCard (지표 카드): default / loading — 코드 컴포넌트 MetricCard 매핑
- PeriodDropdown (기간 선택): closed / open

## 에셋
- ic_arrow_down (icon): node:124:88

## 구현 메모
- 로딩 상태에서 스켈레톤 표시
- 기간 변경 시 카드·차트 동시 갱신
```

---

## 3. 참조 무결성

- json의 `capturedViewportWidth`, spec.md '개요'의 캡처 뷰포트 폭, `-figma.png` 캡처 폭은 **동일 값**이어야 한다.
- 세 산출물 파일명은 동일한 `{화면명-케밥}` 접두를 공유한다.
- 시각 정합 검증(`../../e2e-verifier/references/figma-visual-diff.md`)은 이 `capturedViewportWidth`를 동일 뷰포트 폭 전제로 사용한다.
