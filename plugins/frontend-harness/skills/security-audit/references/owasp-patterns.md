# OWASP Top 10 취약점 패턴 레퍼런스

OWASP Top 10 (2021) 기준 취약점별 탐지 패턴, 테스트 방법, 수정 가이드.

## A01: Broken Access Control

### 탐지 패턴

```bash
# 인증 없는 API 라우트 탐지
# 1. 모든 API 라우트 추출
find src/app/api -name "route.ts" | while read f; do
  HAS_AUTH=$(grep -c 'getServerSession\|getSession\|auth\|middleware\|verify' "$f")
  if [ "$HAS_AUTH" -eq 0 ]; then
    echo "NO_AUTH: $f"
  fi
done

# 2. IDOR 패턴 (사용자 ID 직접 참조)
grep -rn 'params\.\(id\|userId\)' --include="*.ts" src/app/api/ | grep -v 'session\|auth'
```

### 수정 가이드

```typescript
// Before (취약)
export async function GET(req: Request, { params }: { params: { id: string } }) {
  return Response.json(await db.user.findUnique({ where: { id: params.id } }));
}

// After (수정)
export async function GET(req: Request, { params }: { params: { id: string } }) {
  const session = await getServerSession(authOptions);
  if (!session) return new Response('Unauthorized', { status: 401 });
  if (params.id !== session.user.id && !session.user.isAdmin) {
    return new Response('Forbidden', { status: 403 });
  }
  return Response.json(await db.user.findUnique({ where: { id: params.id } }));
}
```

## A03: Injection

### SQL Injection 탐지

```bash
# Raw SQL 사용 탐지
grep -rn 'prisma\.\$queryRaw\|prisma\.\$executeRaw\|knex\.raw\|sequelize\.query' --include="*.ts" src/

# 문자열 연결 쿼리 (위험)
grep -rn "query.*\`.*\${" --include="*.ts" src/
grep -rn "query.*'.*\+" --include="*.ts" src/
```

### XSS 탐지

```bash
# React dangerouslySetInnerHTML
grep -rn 'dangerouslySetInnerHTML' --include="*.tsx" src/

# DOM 직접 조작
grep -rn 'innerHTML\|outerHTML\|document\.write' --include="*.ts" --include="*.tsx" src/

# eval 사용
grep -rn 'eval(\|new Function(' --include="*.ts" --include="*.tsx" src/
```

### 수정 가이드

```typescript
// SQL Injection 수정: 파라미터화 쿼리 사용
// Before (취약)
const user = await prisma.$queryRaw`SELECT * FROM users WHERE name = '${name}'`;

// After (수정)
const user = await prisma.$queryRaw`SELECT * FROM users WHERE name = ${name}`;
// 또는 ORM 사용
const user = await prisma.user.findFirst({ where: { name } });

// XSS 수정: DOMPurify 사용
// Before (취약)
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// After (수정)
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userContent) }} />
```

## A05: Security Misconfiguration

### 탐지 패턴

```bash
# CORS 와일드카드
grep -rn "origin.*['\"]\\*['\"]" --include="*.ts" --include="*.js" src/
grep -rn "Access-Control-Allow-Origin.*\\*" --include="*.ts" src/

# 디버그 모드 노출
grep -rn "NODE_ENV.*development\|debug.*true\|devtool.*source-map" --include="*.ts" --include="*.js" --include="*.json" .

# 상세 에러 메시지 노출
grep -rn "stack\|stackTrace\|err\.message" --include="*.ts" src/ | grep -i 'response\|json\|send'
```

## A07: Authentication Failures

### 탐지 패턴

```bash
# 하드코딩된 시크릿
grep -rn "secret.*=.*['\"]" --include="*.ts" --include="*.js" src/ | grep -iv 'process\.env\|import\|type'

# 약한 해싱 (MD5, SHA1)
grep -rn 'md5\|sha1\|createHash.*md5\|createHash.*sha1' --include="*.ts" src/

# JWT alg:none 취약점
grep -rn 'algorithms.*none\|verify.*false' --include="*.ts" src/
```

## A10: SSRF (Server-Side Request Forgery)

### 탐지 패턴

```bash
# 사용자 입력 URL로 서버 요청
grep -rn 'fetch(\|axios\.\|http\.get\|request(' --include="*.ts" src/app/api/ | head -20
# 위 결과에서 URL이 사용자 입력(req.body, params, query)인 경우 SSRF 위험
```

### 수정 가이드

```typescript
// SSRF 방지: URL 화이트리스트 + 내부 IP 차단
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];

function isSafeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    if (!['http:', 'https:'].includes(parsed.protocol)) return false;
    if (!ALLOWED_HOSTS.includes(parsed.hostname)) return false;
    // 내부 IP 차단
    const ip = parsed.hostname;
    if (ip.startsWith('10.') || ip.startsWith('192.168.') || ip.startsWith('172.') || ip === 'localhost' || ip === '127.0.0.1') {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}
```
