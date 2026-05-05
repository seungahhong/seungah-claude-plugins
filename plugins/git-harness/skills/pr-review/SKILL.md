---
name: pr-review
description: "PR 리뷰 통합 스킬. 변경된 코드에 대해 다각도 리뷰(코드 품질, 버그, 보안, 테스트, 코드 간소화)를 수행하고 결과를 통합 보고한다. 사용자가 'PR 리뷰', 'pull request', '코드 리뷰', '리뷰해줘', 'review', 'PR 검토', '머지 전 검토' 등을 언급할 때 사용한다. /simplify 코드 간소화를 포함한다."
allowed-tools: Bash, Read, Grep, Glob, Agent
---

# PR Review — PR 리뷰 통합

변경된 코드에 대해 다각도 리뷰를 수행하고 통합 리포트를 생성한다.

## 리뷰 관점

| 관점 | 설명 | 자동 적용 |
|------|------|----------|
| **code** | CLAUDE.md 준수, 코딩 컨벤션, 코드 품질 | 항상 |
| **bugs** | 로직 에러, null 처리, 경쟁 조건, 메모리 누수 | 항상 |
| **security** | 보안 취약점 (XSS, Injection, 인증 누락) | 항상 |
| **tests** | 테스트 커버리지 품질, 누락된 케이스 | 테스트 파일 변경 시 |
| **simplify** | 불필요한 복잡도 제거, 가독성 개선 | 항상 |

## 실행 절차

### Phase 0: 변경 사항 파악

```bash
# 변경 파일 목록
git diff --name-only HEAD

# 변경 통계
git diff --stat HEAD

# 상세 diff
git diff HEAD

# 기존 PR 확인
gh pr view 2>/dev/null
```

변경 파일 유형에 따라 적용할 리뷰 관점을 자동 결정:
- **항상 적용**: code, bugs, security, simplify
- **테스트 파일 변경 시 추가**: tests
- **타입 추가/수정 시 추가**: type design

### Phase 1: 코드 품질 리뷰

CLAUDE.md와 프로젝트 컨벤션 기준으로 점검:

**점검 항목:**
- import 패턴 및 정렬
- 함수 선언 스타일 (function vs arrow)
- React 컴포넌트 패턴 (Props 타입, 명명 규칙)
- 에러 핸들링 패턴
- 명명 규칙 일관성
- 코드 중복

**이슈 신뢰도 점수 (0-100):**
- 0-25: 거짓 양성 또는 기존 이슈 → 보고 안 함
- 26-50: 사소한 지적 → 보고 안 함
- 51-75: 유효하지만 영향 낮음 → 보고 안 함
- 76-89: 중요한 이슈 → **Important**로 보고
- 90-100: 치명적 버그 또는 명시적 규칙 위반 → **Critical**로 보고

**신뢰도 80 이상만 보고한다.** 품질 > 양.

### Phase 2: 버그 탐지

실제 기능에 영향을 미치는 버그만 탐지:
- 로직 에러, 잘못된 조건문
- null/undefined 미처리
- 경쟁 조건 (race condition)
- 메모리 누수
- 무한 루프/재귀

### Phase 3: 보안 점검

변경된 코드에 한정하여 보안 취약점 점검:
- XSS (dangerouslySetInnerHTML, innerHTML)
- Injection (SQL, Command)
- 인증/인가 누락
- 시크릿 하드코딩
- CSRF 보호

### Phase 4: 코드 간소화 (/simplify)

변경된 코드의 명확성, 일관성, 유지보수성을 개선:

**수행 항목:**
- 불필요한 복잡도와 중첩 줄이기
- 중복 코드와 불필요한 추상화 제거
- 변수/함수명 가독성 개선
- 관련 로직 통합
- 불필요한 주석 제거
- 중첩 삼항 연산자 → switch/if-else 변환

**원칙:**
- 기능은 절대 변경하지 않는다
- 명확성 > 간결성 (한 줄로 줄이는 것보다 읽기 쉬운 것이 우선)
- 과도한 간소화로 유지보수성을 해치지 않는다
- 최근 변경된 코드만 대상 (기존 코드를 건드리지 않음)

### Phase 5: 테스트 리뷰 (해당 시)

테스트 파일이 변경된 경우:
- 행위 기반 테스트 커버리지 확인
- 누락된 중요 테스트 케이스 식별
- 테스트 품질 평가 (구현 세부 결합도, 취약한 assertion)
- 엣지 케이스 커버리지

### Phase 6: 통합 리포트

```markdown
# PR Review Summary

## Critical Issues (N건)
- [관점] 이슈 설명 [파일:라인] (신뢰도: N)

## Important Issues (N건)
- [관점] 이슈 설명 [파일:라인] (신뢰도: N)

## Suggestions (N건)
- [관점] 제안 [파일:라인]

## Strengths
- 이 PR에서 잘된 점

## Simplify 개선사항
- 적용된 간소화 항목

## Recommended Action
1. Critical 이슈 먼저 수정
2. Important 이슈 해결
3. Suggestions 검토
4. 수정 후 재리뷰 실행
```

### Phase 7: 리뷰 코멘트 생성

리뷰 결과를 바탕으로 리뷰어가 PR에 남길 코멘트를 라벨별로 분류하여 생성한다.

**코멘트 라벨:**

| 라벨 | 의미 | 용도 |
|------|------|------|
| `[must]` | 수정 필수 | 버그, 보안 문제, 기능 오동작 |
| `[want]` | 수정 권장 | 코드 품질, 유지보수성 개선 |
| `[imo]` | 개인 의견 | 대안 제시, 스타일 선호 |
| `[ask]` | 질문 | 의도 확인, 설계 이유 질문 |
| `[nits]` | 사소한 지적 | 오타, 포맷팅, 명명 |
| `[info]` | 정보 공유 | 관련 문서, 참고 사항 |

**코멘트 구조:**
```
[must] 파일명:라인 — 이슈 설명
  → 수정 제안 (코드 예시)

[want] 파일명:라인 — 개선 제안
  → 이유 설명

[ask] 파일명:라인 — 질문
  → 맥락 설명
```

사용자가 승인하면 `gh pr review` 또는 `gh pr comment`로 코멘트를 PR에 게시할 수 있다.

## 사용자 소통

- 리뷰 완료 후 통합 리포트를 제시한다
- Critical 이슈가 없으면 "머지 가능" 판정을 내린다
- 사용자가 수정을 원하면 구체적인 코드 변경을 제안한다
- 수정 후 재리뷰를 권장한다

## 사용 예시

**전체 리뷰 (기본):**
```
/pr-review
```

**특정 관점만:**
```
/pr-review security    # 보안만 점검
/pr-review simplify    # 코드 간소화만
/pr-review bugs tests  # 버그 + 테스트만
```

## PR 생성 워크플로우 연동

커밋 전:
1. 코드 작성
2. `/pr-review code bugs` 실행
3. Critical 이슈 수정
4. `/commit` 실행

PR 생성 전:
1. 모든 변경 스테이징
2. `/pr-review` 전체 리뷰 실행
3. Critical + Important 이슈 해결
4. 재리뷰로 확인
5. PR 생성
