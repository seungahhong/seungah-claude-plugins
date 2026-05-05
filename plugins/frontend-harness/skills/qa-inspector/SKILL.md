---
name: qa-inspector
description: "QA 통합 정합성 검증 스킬. 모듈 간 경계면 불일치를 체계적으로 탐지한다. API 응답↔프론트 훅 타입, 파일 경로↔라우터 경로, 상태 전이 맵↔코드 구현을 교차 비교하여 런타임 버그를 사전에 포착한다. 사용자가 'QA', '품질 검증', '통합 테스트', '정합성 검사', '경계면 검증', '교차 검증', '버그 찾기', 'integration test', '연결 확인' 등을 언급할 때 사용한다. 오케스트레이터의 Review 단계(`/review`)에서 다른 정적 분석 스킬과 병렬로 실행되거나, 독립적으로 호출할 수 있다."
allowed-tools: Bash, Read, Grep, Glob, Write, Edit
---

# QA Inspector — 통합 정합성 검증

스펙 대비 구현 품질과 **모듈 간 통합 정합성**을 검증한다. 각 모듈이 개별적으로 정상이어도 연결 지점에서 계약이 어긋나는 **경계면 불일치**를 체계적으로 잡는다.

## 핵심 원칙: "양쪽을 동시에 읽어라"

한쪽만 읽어선 경계면 버그를 잡을 수 없다. 반드시:
- API route **와** 대응 훅을 **같이** 읽고
- 상태 전이 맵 **와** 실제 업데이트 코드를 **같이** 읽고
- 파일 구조 **와** 링크 경로를 **같이** 읽어야 한다

## 검증 우선순위

1. **통합 정합성** (가장 높음) — 경계면 불일치가 런타임 에러의 주요 원인
2. **기능 스펙 준수** — API/상태머신/데이터모델
3. **디자인 품질** — 색상/타이포/반응형
4. **코드 품질** — 미사용 코드, 명명 규칙

## 실행 절차

### Phase 0: 검증 범위 결정

1. **변경 파일 수집**:

```bash
git diff --name-only --diff-filter=ACMR HEAD
```

2. **검증 모드 선택**:

```
[QA Inspector] 검증 모드를 선택해주세요.

1. 변경 파일 기반 — git diff 기준 변경된 파일의 경계면만 검증 (기본)
2. 모듈 전체 — 특정 모듈/기능 전체를 검증
3. 전체 검증 — 프로젝트 전체 통합 정합성 검증
```

3. **프로젝트 구조 파악**:
   - API route 디렉토리 위치 (`src/app/api/`, `pages/api/` 등)
   - 훅/서비스 디렉토리 위치 (`src/hooks/`, `src/services/` 등)
   - 타입 정의 위치 (`src/types/`, `src/interfaces/` 등)
   - 상태 관리 위치 (`src/store/`, `src/atoms/` 등)

### Phase 1: API ↔ 프론트엔드 연결 검증

**양쪽 동시 읽기**: API route의 응답 shape과 프론트 훅의 타입을 병행 검증한다.

#### Step 1: API 응답 shape 추출

```bash
# API route에서 응답 shape 추출
grep -rn 'NextResponse.json\|res.json\|res.send\|return.*json' --include="*.ts" --include="*.tsx" src/app/api/ | head -30
```

#### Step 2: 프론트 훅 타입 추출

```bash
# 훅에서 제네릭 타입 추출
grep -rn 'fetch\|useSWR\|useQuery\|axios' --include="*.ts" --include="*.tsx" src/hooks/ src/services/ | head -30
```

#### Step 3: 교차 비교

| 검증 항목 | 방법 |
|----------|------|
| 응답 shape ↔ 타입 일치 | API가 `{ data: [...] }` 반환 시 훅이 `.data`를 unwrap하는지 |
| snake_case ↔ camelCase | DB 필드명 → API 응답 → 프론트 타입 간 변환 일관성 |
| 페이지네이션 | `{ items, total, page }` vs 배열 직접 기대 |
| 즉시 응답 vs 비동기 | 202 Accepted의 shape과 최종 결과 shape 구분 |
| 엔드포인트 ↔ 훅 매핑 | 모든 API에 대응 훅이 있고 실제 호출되는지 |

**특히 주의할 패턴:**
- TypeScript 제네릭 캐스팅: `fetchJson<T>()`은 런타임 응답을 검증하지 않음
- `any` 타입 사용: 컴파일은 통과하지만 런타임에 실패
- `npm run build` 통과 ≠ 정상 동작

### Phase 2: 라우팅 정합성 검증

**양쪽 동시 읽기**: 파일 경로와 링크/라우터 경로를 대조한다.

#### Step 1: 페이지 경로 추출

```bash
# Next.js App Router 페이지 경로 추출
find src/app -name "page.tsx" -o -name "page.jsx" | sed 's|src/app||;s|/page\.\(tsx\|jsx\)||;s|/\(([^)]*)\)||g'
```

#### Step 2: 코드 내 링크 수집

```bash
# 모든 href, router.push, redirect 값 수집
grep -rn 'href=\|router\.push\|router\.replace\|redirect(' --include="*.tsx" --include="*.ts" src/ | grep -v node_modules | head -30
```

#### Step 3: 교차 비교

- 각 링크가 실제 존재하는 page 경로와 매칭되는지 확인
- route group `(group)`이 URL에서 제거되는 것을 고려
- 동적 세그먼트 `[id]`가 올바른 파라미터로 채워지는지 확인

### Phase 3: 상태 전이 완전성 검증

#### Step 1: 상태 전이 맵 추출

```bash
# 상태 전이 정의 탐색
grep -rn 'STATE_TRANSITIONS\|statusMap\|STATUS\|state.*machine\|transition' --include="*.ts" --include="*.tsx" src/ | head -20
```

#### Step 2: 상태 업데이트 코드 추출

```bash
# status 업데이트 패턴 검색
grep -rn "status.*[:=].*['\"]" --include="*.ts" --include="*.tsx" src/ | grep -v 'type\|interface\|import' | head -30
```

#### Step 3: 교차 비교

- 정의된 모든 상태 전이가 코드에서 실행되는지 (죽은 전이 없음)
- 코드의 모든 status 업데이트가 전이 맵에 정의되어 있는지 (무단 전이 없음)
- 중간 상태에서 최종 상태로의 전환이 누락되지 않았는지
- 프론트에서 상태 기반 분기의 조건값이 실제 도달 가능한지

### Phase 4: 데이터 흐름 정합성 검증

- DB 스키마 필드명과 API 응답 필드명의 매핑 일관성
- 프론트 타입 정의와 API 응답의 필드명 일치
- 옵셔널 필드에 대한 null/undefined 처리 양쪽 일관성
- enum 값의 프론트/백엔드 동기화

### Phase 5: 검증 결과 보고

```markdown
# QA 통합 정합성 검증 결과

## 검증 범위
- 모드: 변경 파일 기반
- 검증 파일: N개
- 검증 경계면: N개

## 통합 정합성 검증

### API ↔ 프론트엔드 연결

| # | API 엔드포인트 | 프론트 훅 | 결과 | 상세 |
|---|--------------|----------|------|------|
| 1 | GET /api/users | useUsers() | ✅ | shape 일치 |
| 2 | POST /api/orders | useCreateOrder() | ❌ | 응답 래핑 불일치 |

### 라우팅 정합성

| # | 링크 경로 | 대상 페이지 | 결과 | 상세 |
|---|----------|-----------|------|------|
| 1 | /dashboard | src/app/dashboard/page.tsx | ✅ | 매칭 |
| 2 | /create | (없음) | ❌ | 404 발생 |

### 상태 전이 완전성

| # | 전이 | 코드 | 결과 | 상세 |
|---|------|------|------|------|
| 1 | draft → submitted | ✅ | ✅ | 정상 |
| 2 | submitted → approved | ✅ | ❌ | 전이 코드 누락 |

## 요약

| 카테고리 | 통과 | 실패 | 경고 |
|---------|------|------|------|
| API ↔ 프론트 | N | N | N |
| 라우팅 | N | N | N |
| 상태 전이 | N | N | N |
| 데이터 흐름 | N | N | N |

## 발견된 이슈

### Critical (즉시 수정)
1. ...

### Warning (수정 권장)
1. ...
```

## 검증 체크리스트

### API ↔ 프론트엔드 연결
- [ ] 모든 API route의 응답 shape과 대응 훅의 제네릭 타입이 일치
- [ ] 래핑된 응답(`{ items: [...] }`)은 훅에서 unwrap하는지 확인
- [ ] snake_case ↔ camelCase 변환이 일관되게 적용
- [ ] 즉시 응답(202)과 최종 결과의 shape이 프론트에서 구분되는지 확인
- [ ] 모든 API 엔드포인트에 대응하는 프론트 훅이 존재하고 실제로 호출됨

### 라우팅 정합성
- [ ] 코드 내 모든 href/router.push 값이 실제 page 파일 경로와 매칭
- [ ] route group `(group)`이 URL에서 제거되는 것을 고려한 경로 검증
- [ ] 동적 세그먼트 `[id]`가 올바른 파라미터로 채워지는지 확인

### 상태 머신 정합성
- [ ] 정의된 모든 상태 전이가 코드에서 실행됨 (죽은 전이 없음)
- [ ] 코드의 모든 status 업데이트가 전이 맵에 정의됨 (무단 전이 없음)
- [ ] 중간 상태에서 최종 상태로의 전환이 누락되지 않음
- [ ] 프론트에서 상태 기반 분기(`if status === "X"`)의 X가 실제 도달 가능

### 데이터 흐름 정합성
- [ ] DB 스키마 필드명과 API 응답 필드명의 매핑이 일관됨
- [ ] 프론트 타입 정의와 API 응답의 필드명이 일치
- [ ] 옵셔널 필드에 대한 null/undefined 처리가 양쪽에서 일관됨

## 사용자 소통

- Phase 0에서 검증 모드를 반드시 확인한다
- 각 Phase 완료 시 발견된 이슈를 즉시 보여준다
- Critical 이슈 발견 시 즉시 사용자에게 알린다
- 검증 완료 후 수정 여부를 사용자에게 확인한다

## 점진적 QA (Incremental QA)

오케스트레이터에서 "Phase 4: 전체 완성 후"에만 실행하지 않는다. 각 모듈 완성 시 즉시 해당 모듈의 교차 검증을 수행하면 버그 누적과 전파를 방지할 수 있다.
