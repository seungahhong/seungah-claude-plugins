---
name: security-audit
description: "웹 애플리케이션 보안 감사 스킬. OWASP Top 10 기준 취약점 스캔, 코드 보안 분석, 의존성 취약점 점검, 보안 헤더 검증을 수행한다. 사용자가 '보안 감사', '보안 점검', '취약점 스캔', 'OWASP', 'XSS', 'SQL Injection', 'CSRF', '시큐어 코딩', '보안 리뷰', '의존성 취약점', 'CVE', '보안 헤더' 등을 언급할 때 사용한다. 코드 기반 정적 분석(SAST)과 설정 점검을 수행하며, 실제 네트워크 침투는 범위 밖이다. 오케스트레이터의 Review 단계(`/review`)에서 다른 정적 분석 스킬과 병렬로 실행되거나, 독립적으로 호출할 수 있다."
allowed-tools: Bash, Read, Grep, Glob, Write, Edit, WebSearch
---

# Security Audit — 보안 감사

OWASP Top 10 기준 취약점 스캔, 코드 보안 분석, 의존성 취약점 점검을 수행한다.

## 실행 모드

| 사용자 요청 | 모드 | 범위 |
|-----------|------|------|
| "보안 감사 전체" | 풀 감사 | 전체 프로젝트 |
| "변경 코드 보안 점검" | 변경 파일 감사 | git diff 기준 |
| "의존성 취약점 확인" | 의존성 스캔 | package.json 기준 |
| "보안 헤더 점검" | 헤더 점검 | 응답 헤더 기준 |

## 실행 절차

### Phase 0: 준비

1. **감사 범위 확인**:

```
[보안 감사] 감사 모드를 선택해주세요.

1. 전체 감사 — 프로젝트 전체 코드 보안 분석
2. 변경 파일 감사 — git diff 기준 변경된 파일만 분석 (기본)
3. 의존성 스캔 — npm/yarn 의존성 취약점만 점검
4. 보안 헤더 점검 — HTTP 응답 헤더 보안 설정 점검
```

2. **기술 스택 감지**:

```bash
# 프레임워크 감지
cat package.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
deps = {**d.get('dependencies',{}), **d.get('devDependencies',{})}
for key in ['next', 'react', 'vue', 'express', 'fastify', 'nestjs']:
    if key in deps or f'@{key}' in str(deps):
        print(f'DETECTED: {key}')
"
```

3. **대상 파일 수집**:

```bash
# 변경 파일 모드
git diff --name-only --diff-filter=ACMR HEAD | grep -E '\.(ts|tsx|js|jsx)$'

# 전체 모드
find src -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | grep -v node_modules
```

### Phase 1: 의존성 취약점 스캔

```bash
# npm audit
npm audit --json 2>/dev/null | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    vulns = d.get('vulnerabilities', {})
    for name, info in vulns.items():
        sev = info.get('severity', 'unknown')
        print(f'[{sev.upper()}] {name}: {info.get(\"title\", \"\")}')
except: print('audit 파싱 실패')
"

# yarn audit (yarn 프로젝트)
yarn audit --json 2>/dev/null | head -50
```

**CVSS 심각도별 대응 기한:**

| 등급 | 점수 | 대응 기한 |
|------|------|----------|
| Critical | 9.0-10.0 | 24시간 내 |
| High | 7.0-8.9 | 1주 내 |
| Medium | 4.0-6.9 | 1개월 내 |
| Low | 0.1-3.9 | 다음 릴리스 |

### Phase 2: OWASP Top 10 코드 분석

각 카테고리별로 코드를 정적 분석한다. 상세 테스트 방법은 `references/owasp-patterns.md`를 참조한다.

#### A01: Broken Access Control

```bash
# 권한 검증 누락 탐지
grep -rn 'router\.\(get\|post\|put\|delete\|patch\)' --include="*.ts" src/app/api/ | head -20
grep -rn 'getServerSession\|getSession\|auth\|middleware' --include="*.ts" src/app/api/ | head -20
```

점검 항목:
- [ ] 모든 API 라우트에 인증/인가 검증이 있는가
- [ ] IDOR (Insecure Direct Object Reference) 취약점이 없는가
- [ ] 수평적/수직적 권한 상승이 불가능한가

#### A03: Injection

```bash
# SQL Injection 위험 패턴 (raw query)
grep -rn 'raw\|query\|exec\|execute' --include="*.ts" src/ | grep -v node_modules | grep -i 'sql\|query\|prisma\.\$'

# XSS 위험 패턴
grep -rn 'dangerouslySetInnerHTML\|innerHTML\|document\.write\|eval(' --include="*.tsx" --include="*.ts" src/

# Command Injection 위험 패턴
grep -rn 'exec\|spawn\|execSync\|child_process' --include="*.ts" src/
```

점검 항목:
- [ ] 파라미터화 쿼리/ORM을 사용하고 raw SQL이 없는가
- [ ] `dangerouslySetInnerHTML` 사용 시 DOMPurify로 살균하는가
- [ ] 사용자 입력이 명령어 실행에 사용되지 않는가

#### A07: Authentication Failures

```bash
# JWT/세션 관련 패턴
grep -rn 'jwt\|token\|session\|cookie\|auth' --include="*.ts" src/ | grep -iv 'type\|interface\|import' | head -20

# 하드코딩된 시크릿
grep -rn 'secret\|password\|api_key\|apiKey\|API_KEY\|TOKEN\|Bearer' --include="*.ts" --include="*.env*" src/ | grep -v node_modules
```

점검 항목:
- [ ] 시크릿이 하드코딩되어 있지 않은가 (환경변수 사용)
- [ ] JWT 시크릿 키 강도가 충분한가
- [ ] 세션 만료/무효화가 구현되어 있는가
- [ ] 비밀번호 해싱에 bcrypt/argon2를 사용하는가

#### A05: Security Misconfiguration

```bash
# CORS 설정
grep -rn 'cors\|Access-Control-Allow' --include="*.ts" --include="*.js" src/ | head -10

# 디버그/개발 모드
grep -rn 'debug\|verbose\|devtool' --include="*.ts" --include="*.js" --include="*.json" src/ | grep -v node_modules
```

점검 항목:
- [ ] CORS가 `*`로 열려있지 않은가
- [ ] 프로덕션에서 디버그 모드가 비활성화되어 있는가
- [ ] 에러 메시지에 스택 트레이스가 노출되지 않는가

### Phase 3: 보안 헤더 점검

```bash
# Next.js 보안 헤더 설정 확인
grep -rn 'headers\|Content-Security-Policy\|X-Frame-Options\|X-Content-Type' --include="*.ts" --include="*.js" next.config.* src/middleware.* | head -20
```

**필수 보안 헤더 체크리스트:**

| 헤더 | 권장값 | 목적 |
|------|-------|------|
| Content-Security-Policy | script-src 'self' | XSS 방지 |
| X-Content-Type-Options | nosniff | MIME 스니핑 방지 |
| X-Frame-Options | DENY | 클릭재킹 방지 |
| Strict-Transport-Security | max-age=31536000; includeSubDomains | HTTPS 강제 |
| Referrer-Policy | strict-origin-when-cross-origin | 리퍼러 누출 방지 |
| Permissions-Policy | camera=(), microphone=() | 브라우저 API 제한 |

### Phase 4: 시크릿/민감정보 탐지

```bash
# .env 파일 검사
find . -name ".env*" -not -path "*/node_modules/*" -exec echo "Found: {}" \;

# 코드 내 시크릿 패턴 탐지
grep -rn 'AKIA\|AIza\|sk-\|ghp_\|gho_\|-----BEGIN' --include="*.ts" --include="*.js" --include="*.env*" . | grep -v node_modules | head -20

# .gitignore에 .env 포함 확인
grep -c '\.env' .gitignore 2>/dev/null || echo ".gitignore에 .env 미포함!"
```

### Phase 5: 결과 보고

```markdown
# 보안 감사 결과

## 감사 범위
- 모드: 변경 파일 감사
- 대상 파일: N개
- 기술 스택: Next.js, React, TypeScript

## 의존성 취약점

| 심각도 | 패키지 | CVE | 설명 | 수정 버전 |
|--------|-------|-----|------|----------|
| Critical | lodash | CVE-XXXX | ... | 4.17.21 |

## OWASP Top 10 코드 분석

| 카테고리 | 결과 | 발견 수 | 상세 |
|---------|------|--------|------|
| A01 Broken Access Control | ⚠️ | 2 | 권한 검증 누락 |
| A03 Injection | ✅ | 0 | |
| A05 Security Misconfiguration | ⚠️ | 1 | CORS 설정 |
| A07 Auth Failures | ✅ | 0 | |

## 보안 헤더

| 헤더 | 상태 | 권장 조치 |
|------|------|----------|
| CSP | ❌ 미설정 | script-src 'self' 추가 |
| X-Frame-Options | ✅ | - |

## 시크릿/민감정보

| 파일 | 유형 | 위험도 | 조치 |
|------|------|--------|------|
| .env.local | API 키 | - | .gitignore 확인 |

## 개선 권고 (우선순위순)

### 즉시 수정 (Critical)
1. ...

### 1주 내 수정 (High)
1. ...

### 1개월 내 수정 (Medium)
1. ...
```

## 사용자 소통

- Phase 0에서 감사 모드를 반드시 확인한다
- Critical/High 취약점 발견 시 즉시 사용자에게 알린다
- 수정 방안은 구체적인 코드 예시와 함께 제시한다
- 의존성 업데이트는 breaking change 여부를 함께 안내한다
