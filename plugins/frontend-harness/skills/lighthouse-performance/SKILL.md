---
name: lighthouse-performance
description: "Lighthouse 기반 웹 성능 검사 스킬. Core Web Vitals(LCP, CLS, INP, TTFB, FCP)와 성능 점수를 측정하고 개선 방안을 제시한다. 사용자가 '성능 검사', 'lighthouse', 'performance', 'Core Web Vitals', 'LCP', 'CLS', '페이지 속도', '로딩 속도', '성능 최적화', '웹 성능' 등을 언급할 때 사용한다. 개발 완료 후 오케스트레이터의 Review 단계(`/review`)에서 다른 정적 분석 스킬과 병렬로 실행되거나, 독립적으로 호출할 수 있다."
allowed-tools: Bash, Read, Grep, Glob, WebFetch
---

# Lighthouse Performance — 웹 성능 검사

Lighthouse CLI를 사용하여 웹 페이지의 성능을 측정하고, Core Web Vitals 기준으로 개선 방안을 제시한다.

## 측정 항목

### Core Web Vitals

| 지표 | 설명 | 좋음 | 개선 필요 | 나쁨 |
|------|------|------|----------|------|
| LCP (Largest Contentful Paint) | 최대 콘텐츠 렌더링 | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| CLS (Cumulative Layout Shift) | 누적 레이아웃 이동 | ≤ 0.1 | ≤ 0.25 | > 0.25 |
| INP (Interaction to Next Paint) | 입력 응답 지연 | ≤ 200ms | ≤ 500ms | > 500ms |
| TTFB (Time to First Byte) | 첫 바이트 수신 | ≤ 800ms | ≤ 1.8s | > 1.8s |
| FCP (First Contentful Paint) | 첫 콘텐츠 렌더링 | ≤ 1.8s | ≤ 3.0s | > 3.0s |

### 성능 점수 등급

| 등급 | 점수 범위 | 판정 |
|------|----------|------|
| 우수 | 90-100 | 배포 가능 |
| 양호 | 50-89 | 개선 권장 |
| 미흡 | 0-49 | 개선 필수 |

## 실행 절차

### Phase 0: 사전 조건 확인

1. **Lighthouse CLI 확인**:

```bash
npx lighthouse --version 2>/dev/null || echo "NOT_INSTALLED"
```

설치되어 있지 않으면 `npx lighthouse`로 실행 가능함을 안내한다.

2. **대상 URL 확인**:
   - 사용자에게 검사할 URL을 확인한다
   - 개발 서버가 실행 중인지 확인한다 (`localhost:3000` 등)
   - URL이 제공되지 않으면 `package.json`의 `dev` 스크립트에서 포트를 추론한다

3. **검사 모드 선택**:

```
[Lighthouse 성능 검사] 검사 모드를 선택해주세요.

1. 빠른 검사 — 단일 페이지 성능 측정 (기본)
2. 주요 페이지 검사 — 지정된 페이지들을 순회하며 측정
3. 비교 검사 — 변경 전후 성능 비교 (브랜치 간)
```

### Phase 1: Lighthouse 실행

#### 단일 페이지 검사

```bash
npx lighthouse <URL> \
  --output=json \
  --output-path=./lighthouse-report.json \
  --chrome-flags="--headless --no-sandbox" \
  --only-categories=performance \
  --quiet
```

#### 주요 페이지 순회 검사

사용자가 지정한 페이지 목록 또는 자동 감지된 라우트를 순회한다:

```bash
# 라우트 자동 감지 (Next.js)
find src/app -name "page.tsx" -o -name "page.jsx" | head -10

# 각 페이지별 실행
for url in $URLS; do
  npx lighthouse "$url" --output=json --output-path="./lighthouse-${slug}.json" --chrome-flags="--headless --no-sandbox" --only-categories=performance --quiet
done
```

#### 변경 전후 비교 검사

```bash
# 현재 브랜치 측정
npx lighthouse <URL> --output=json --output-path=./lighthouse-current.json --chrome-flags="--headless --no-sandbox" --only-categories=performance --quiet

# main 브랜치 측정 (git stash 활용)
git stash && git checkout main
npx lighthouse <URL> --output=json --output-path=./lighthouse-baseline.json --chrome-flags="--headless --no-sandbox" --only-categories=performance --quiet
git checkout - && git stash pop
```

### Phase 2: 결과 분석

Lighthouse JSON 결과에서 핵심 지표를 추출한다:

```bash
cat lighthouse-report.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
audits = data['audits']
categories = data['categories']

score = categories['performance']['score'] * 100
lcp = audits['largest-contentful-paint']['numericValue'] / 1000
cls = audits['cumulative-layout-shift']['numericValue']
fcp = audits['first-contentful-paint']['numericValue'] / 1000
tbt = audits['total-blocking-time']['numericValue']
si = audits['speed-index']['numericValue'] / 1000

print(f'Performance Score: {score:.0f}')
print(f'LCP: {lcp:.2f}s')
print(f'CLS: {cls:.4f}')
print(f'FCP: {fcp:.2f}s')
print(f'TBT: {tbt:.0f}ms')
print(f'Speed Index: {si:.2f}s')
"
```

### Phase 3: 개선 기회 분석

Lighthouse가 제안하는 개선 기회(opportunities)와 진단(diagnostics)을 분석한다:

**주요 점검 항목:**

| 카테고리 | 점검 항목 |
|---------|----------|
| 리소스 최적화 | 미사용 JS 제거, 이미지 최적화, CSS 최소화 |
| 렌더링 최적화 | 렌더 차단 리소스 제거, DOM 크기 축소 |
| 네트워크 최적화 | 요청 수 감소, 프리로드/프리페치 활용 |
| 코드 최적화 | 코드 분할, 트리 쉐이킹, 지연 로딩 |

**프레임워크별 최적화 가이드:**

| 프레임워크 | 주요 최적화 |
|-----------|-----------|
| Next.js | `next/image`, `next/font`, 동적 import, ISR/SSG |
| React | `React.lazy`, `Suspense`, `useMemo`, 번들 분석 |
| Vue | 비동기 컴포넌트, `v-once`, 가상 스크롤 |

### Phase 4: 결과 보고

```markdown
# Lighthouse 성능 검사 결과

## 성능 점수

| 페이지 | 점수 | 등급 |
|--------|------|------|
| / (홈) | 85 | 양호 |
| /products | 72 | 양호 |

## Core Web Vitals

| 지표 | 측정값 | 기준 | 판정 |
|------|--------|------|------|
| LCP | 2.1s | ≤ 2.5s | 좋음 |
| CLS | 0.05 | ≤ 0.1 | 좋음 |
| FCP | 1.5s | ≤ 1.8s | 좋음 |
| TBT | 350ms | ≤ 200ms | 개선 필요 |

## 개선 기회 (예상 절감)

| 항목 | 예상 절감 | 우선순위 |
|------|----------|---------|
| 미사용 JavaScript 제거 | 1.2s | 높음 |
| 이미지 최적화 | 0.8s | 높음 |
| 렌더 차단 리소스 제거 | 0.5s | 중간 |

## 구체적 개선 방안

1. **[높음]** ...
2. **[중간]** ...

## 변경 전후 비교 (해당 시)

| 지표 | Before | After | 변화 |
|------|--------|-------|------|
| Score | 72 | 85 | +13 |
```

## Lighthouse 실행 불가 시 대체 방안

Lighthouse CLI를 실행할 수 없는 환경(CI, headless 미지원)에서는 **코드 기반 정적 분석**으로 대체한다:

1. **번들 크기 분석**: `npm run build` 후 빌드 산출물 크기 확인
2. **이미지 최적화 점검**: `next/image` 사용 여부, 미최적화 이미지 탐지
3. **코드 분할 점검**: 동적 import 사용 여부, 큰 번들 탐지
4. **렌더링 패턴 점검**: SSR/SSG/CSR 적절성, 데이터 페칭 패턴

```bash
# 빌드 산출물 크기 분석
npm run build 2>&1 | tail -30

# 큰 JS 번들 탐지 (Next.js)
find .next/static -name "*.js" -size +100k -exec ls -lh {} \;

# 미최적화 이미지 탐지
grep -rn '<img ' --include="*.tsx" --include="*.jsx" | grep -v 'next/image'
```

## 사용자 소통

- Phase 0에서 URL과 검사 모드를 반드시 확인한다
- 검사 완료 후 결과표와 개선 방안을 함께 제시한다
- 개선 방안은 예상 효과가 큰 순서로 정렬한다
- 사용자가 수정을 원하면 구체적인 코드 변경을 제안한다
