---
name: contract-review
description: "BE의 API 계약(OpenAPI/스키마)을 FE 착수 전에 완결성·호환성·소비자 요구 충족 관점으로 리뷰하는 게이트 스킬. 계약을 구현 후 산출물이 아니라 선합의 SoT로 끌어올려 FE가 mock으로 병렬 착수하게 한다. 사용자가 '계약 리뷰', 'OpenAPI 점검', 'API 계약', '스펙 완결성', 'breaking change', '계약 깨짐', 'Pact', '소비자 계약', 'consumer-driven', 'FE 착수 준비', 'contract-first', '계약 우선', 'API 스펙 검수', 'oasdiff', 'spectral' 등을 언급할 때 사용한다. 읽기 위주 정적 분석이며, 실제 API 호출·계약 합의 자체는 범위 밖이다."
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Contract Review — API 계약 핸드오프 게이트

BE가 FE에 넘기는 API 계약(OpenAPI/스키마)을 **FE 착수 전에** 완결성·호환성·소비자 요구 충족 관점으로 검수한다. 이 스킬은 코드가 아니라 **상류 산출물(계약)**을 핸드오프 시점에 게이트로 리뷰한다. 코드 대상 리뷰는 형제 스킬 qa-inspector(경계면 정합성)·security-audit(보안)이 담당하므로 중복하지 않는다.

## 핵심 원칙

**1. 계약은 BE 구현의 산출물이 아니라 선행 합의물(SoT)이다.**
계약을 구현이 끝난 뒤 추출하면 FE는 BE가 끝날 때까지 기다린다. 계약을 먼저 합의하고 공유하면 FE는 그 계약으로 mock을 세워 병렬로 착수한다 — "Nobody waits for the other team to finish." 이 스킬의 PASS는 "구현이 맞다"가 아니라 "FE가 이 계약만 보고 mock으로 착수해도 안전하다"를 뜻한다.

**2. 완전 디커플링은 신화다.**
계약만 공유한다고 통합이 저절로 맞아떨어지지 않는다. 계약 우선 공유 + CI 계약검증(소비자주도 계약 테스트) + 정기 통합 체크포인트를 **함께** 둘 때만 mock과 실제 구현이 어긋나지 않는다. 따라서 게이트 판정은 계약 문서 단독이 아니라 소비자 기대(Phase 3)와 코드 drift(Phase 4)를 함께 본다.

## Honesty Guardrail

이 스킬이 정량 수치를 출력에 인용할 때는 반드시 (1) 출처 등급, (2) 출처명/링크, (3) 가능하면 반대증거를 함께 적는다.

- 등급 정의: **GOLD** = 피어리뷰·정부·DORA 등 대규모 연구 / **SILVER** = 방법론이 공개된 업계 리포트(벤더 자기보고 포함) / **BRONZE** = 벤더 블로그·일화.
- '개선 N%'를 약속하지 않는다. 검증된 소수 수치만 등급과 함께 인용하고, 효과의 크기는 조직이 직접 baseline을 측정하게 한다(baseline-before-target).
- 아래는 출처 추적 실패 또는 반증되었으므로 **사실로 인용 금지**(설명·주의용 '신화'로만 표기): IBM '결함비용 1→100배', NIST 표의 '결함수정 1/5/10/15/30배'(표 제목에 'Example Only' 명기), 'Crosstalk 결함비용 64%가 요구·설계', Flow Efficiency '보통 15~25%', DORA 'Elite 182배/127배/2293배'(DORA가 폐기한 프레이밍), Code Connect 'AI 코드생성 85~90% 정확'(Figma 자체 데이터는 'AI 코드 신뢰 32%').
- 출처를 댈 수 없는 수치는 표·본문에 쓰지 말고 "조직이 측정"으로 남긴다.

## 도구 안내

- OpenAPI 린트: 가능하면 `spectral`로 스펙 위생을 점검한다. 미설치 시 Phase 1의 수동 규칙으로 대체한다.
- breaking-change diff: 가능하면 `oasdiff`로 배포된 계약 대비 변경을 분류한다(`oasdiff`는 470+ 개의 서로 다른 변경을 breaking/non-breaking으로 탐지 — oasdiff 공식 문서 [SILVER]; breaking/non-breaking 각각의 정확한 개수 분할은 문서에 명시되지 않음). 미설치 시 Phase 2의 수동 규칙으로 대체한다.
- 소비자 계약: Pact 등 CDC 산출물(pact 파일·기대 정의)이 있으면 Phase 3에서 공급자 spec과 대조한다.

```bash
# 도구 가용성 확인 (없으면 수동 규칙으로 진행)
command -v spectral || npx --no-install @stoplight/spectral-cli --version 2>/dev/null || echo "spectral 없음 → 수동 점검"
command -v oasdiff || echo "oasdiff 없음 → 수동 diff"
```

## 실행 절차

### Phase 0: 계약 파일 식별 및 모드 선택

1. **계약 파일 탐색**:

```bash
# OpenAPI/스키마 파일 탐색
find . -type f \( -name "openapi.*" -o -name "swagger.*" -o -name "*.openapi.yaml" -o -name "*.openapi.yml" \) -not -path "*/node_modules/*"
grep -rln 'openapi:\s*3\.\|"openapi"\s*:\s*"3' --include="*.yaml" --include="*.yml" --include="*.json" . | grep -v node_modules | head -20
```

2. **검수 모드 선택**:

```text
[Contract Review] 검수 모드를 선택해주세요.

1. 신규 계약 — 처음 합의하는 계약. 완결성 중심(Phase 1, 3) 검수 (기본)
2. 변경 계약 — 배포된 계약이 있고 그 대비 변경을 검수. breaking-change 중심(Phase 1~4)
3. drift 점검 — 구현 코드와 문서 계약의 불일치만 점검(Phase 4)
```

3. **소비자·기준 계약 위치 확인**:
   - FE가 소비하는 데이터 shape의 근거(FE 타입, mock, Pact 기대 등) 위치
   - 변경 모드면 비교 기준이 되는 배포된 계약 파일/버전(태그, 별도 파일, npm 패키지 등)

### Phase 1: 엔드포인트 완결성 점검

FE가 mock으로 착수하려면 각 엔드포인트가 "추측 없이 구현 가능한" 수준으로 닫혀 있어야 한다. 엔드포인트별로 아래를 점검한다.

```bash
# 엔드포인트·메서드 추출 (yaml 기준 예시)
grep -nE '^\s{2,}(get|post|put|patch|delete):' <계약파일>
# 응답 상태코드 분포
grep -nE '^\s+("?[1-5][0-9]{2}"?):' <계약파일>
```

엔드포인트별 완결성 항목:

| 항목 | 점검 내용 |
|------|-----------|
| 요청 shape | 요청 바디·쿼리·경로 파라미터의 스키마가 모두 정의됨 |
| 응답 shape | 성공 응답 바디 스키마가 `$ref` 등으로 정의됨(빈 객체·미정의 금지) |
| 응답 상태코드 | 성공 + 주요 실패(400/401/403/404/409/422/500 중 해당) 명시 |
| 에러 스키마 | 에러 응답에 타입이 있는 공통 에러 스키마(`code`/`message` 등) 사용 |
| 예시 | 요청·응답 각 1개 이상의 `example`/`examples` 제공 |
| required/nullable | 각 필드의 `required` 여부와 `nullable` 명시(둘 다 미정의 금지) |
| 인증 스킴 | `security`/`securitySchemes`로 인증 방식 명시(공개 엔드포인트면 명시적 비움) |
| 페이지네이션 | 목록 응답에 페이지네이션 규약(cursor/offset, `total` 등) 정의 |
| 빈/에러 응답 | 빈 목록·없음(404 vs 빈 배열)·부분 실패의 shape이 구분되어 정의 |

- `spectral` 사용 시 `oas` 룰셋으로 위 다수를 자동 검출한다.
- 미설치 시 위 표를 수동으로 엔드포인트별 PASS/FAIL 판정한다.

### Phase 2: 배포된 계약 대비 breaking-change diff

변경 모드에서만 수행한다. 배포된 계약을 기준으로 이번 변경이 기존 클라이언트(FE)를 깨는지 분류한다.

```bash
# oasdiff 사용 시 (기준=배포 계약, 수정=현재 계약)
oasdiff breaking <기준계약> <현재계약>
# 미설치 시: 두 파일을 직접 대조하여 아래 규칙으로 분류
```

변경 유형 분류:

| 변경 | breaking 여부 | 클라이언트 영향(한국어) |
|------|---------------|--------------------------|
| 응답 필드 삭제 | breaking | FE가 읽던 필드가 사라져 런타임 undefined |
| 필드 타입 변경 | breaking | 파싱·렌더 로직이 깨짐(예: string→number) |
| 요청 필드 필수화 | breaking | 기존 FE 요청이 422로 거부됨 |
| enum 값 제거 | breaking | 기존 분기·표시가 깨짐 |
| 엔드포인트/메서드 제거 | breaking | 호출 자체가 404/405 |
| 응답에 선택 필드 추가 | non-breaking | FE는 무시 가능(단, 필수로 가정하지 않을 것) |
| 신규 엔드포인트 추가 | non-breaking | 기존 FE 영향 없음 |
| 선택 요청 파라미터 추가 | non-breaking | 기존 FE 영향 없음 |

- breaking 변경이 1건 이상이면 **SemVer major** bump를 권고한다. non-breaking 추가만 있으면 minor, 문서·예시 잔수정만이면 patch를 권고한다.
- 각 breaking 항목에 영향을 받는 소비자(FE 화면·훅)를 가능한 범위에서 함께 적는다.

### Phase 3: 소비자(consumer-driven) 커버리지

FE가 실제로 필요로 하는 데이터를 계약이 충족하는지, 공급자 관점이 아니라 소비자 관점에서 본다.

- FE 타입/mock/화면 요구에서 도출되는 데이터 shape·필터·정렬·엣지(빈/에러/부분)를 계약이 모두 제공하는가.
- Pact 등 CDC 기대가 있으면, **소비자 기대가 공급자 spec에 전부 커버되는가**를 대조한다(기대에는 있는데 spec에 없는 필드·상태는 통합 시 깨진다).
- 과다 제공(FE가 안 쓰는 필드)은 차단 사유가 아니라 정리 권고로만 표기한다.

```bash
# Pact 산출물 탐색
find . -type d -name "pacts" -not -path "*/node_modules/*"
find . -type f \( -name "*.pact.json" -o -name "*-pact.json" \) -not -path "*/node_modules/*"
```

소비자주도 계약(CDC) 테스트의 결함 검출 근거: 한 산업 액션리서치에서 CDC 테스트가 주입된 인터페이스 결함 53건 중 41건(77%)을 검출했다 — Schwarz, Quast, Riehle, "Ensuring Syntactic Interoperability Using Consumer-Driven Contract Testing", Software Testing, Verification and Reliability (Wiley) 2025; 35:e70006 [GOLD, **단일 사례 참여형 액션리서치 + SLR**]. **단, 미검출 12건 중 11건은 속성·쿼리·경로 파라미터의 값 범위(value range) 변경이었다 — CDC는 값 범위에서 단일 값만 spot-check하기 때문이다.** 따라서 CDC는 구조적 인터페이스 결함 탐지에는 유효하지만 값 범위·제약 변경은 놓치므로, 이런 변경은 계약 문서·예시값 합의와 별도 소통으로 보완해야 한다. 단일 사례이므로 일반 효과로 과장하지 말고('전부 잡는다'로 쓰지 말 것) 정성 근거로만 쓴다.

### Phase 4: 코드 ↔ spec drift

구현 코드와 문서 계약이 어긋나면, FE가 본 계약이 거짓이 된다. 가능하면 구현에서 spec을 재생성해 문서 계약과 비교한다.

```bash
# 라우트 핸들러 추출 (스택에 맞게 조정)
grep -rnE '@(Get|Post|Put|Patch|Delete)\(|router\.(get|post|put|patch|delete)\(|app\.(get|post|put|patch|delete)\(' --include="*.ts" src/ | grep -v node_modules | head -40
```

점검:
- 코드에 있으나 계약에 없는 **미문서 엔드포인트**가 있는가.
- 계약에 있으나 코드에 없는 **유령 엔드포인트**가 있는가.
- 응답 타입·필드명이 코드 구현과 계약 간 일치하는가(snake/camel 변환 포함).

AI가 코드에서 계약을 추론하는 작업의 타당성 근거: 한 연구에서 LLM 에이전트 워크플로가 코드→OpenAPI를 추론할 때 평균 F1이 엔드포인트(메서드) >98%, 요청 파라미터·응답 각 97%, 파라미터 제약(constraint) 92%에 달했다(n=12 실세계 API, 5개 언어·8개 프레임워크) — "OOPS: Automated generation of REST API specification via LLMs", Journal of Systems and Software vol.239 (2026), article 112914 (arXiv:2601.12735) [SILVER, n=12 소표본]. 추론 결과는 제안으로 다루고 사람 리뷰로 확정한다(제약 추론이 상대적으로 낮음). 정밀 소수점값이 아니라 abstract 반올림값으로 인용한다.

### Phase 5: 결과 보고

```markdown
# Contract Review 결과

## 검수 범위
- 모드: 변경 계약
- 계약 파일: <경로>
- 기준 계약(변경 모드): <태그/파일/버전>
- 도구: spectral=있음/없음, oasdiff=있음/없음

## 1. 엔드포인트 완결성

| # | 엔드포인트 | 요청 | 응답 shape | 상태코드 | 에러 스키마 | 예시 | required/nullable | 인증 | 결과 |
|---|-----------|------|-----------|---------|------------|------|-------------------|------|------|
| 1 | GET /campaigns | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | PASS |
| 2 | POST /campaigns | ✅ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | ✅ | FAIL |

## 2. Breaking-change diff (변경 모드)

| # | 변경 | 영향(소비자) | breaking |
|---|------|--------------|----------|
| 1 | response.status 필드 삭제 | 캠페인 상세 배지 렌더 깨짐 | breaking |
| 2 | response.tags 선택 필드 추가 | 영향 없음 | non-breaking |

- SemVer 권고: **major / minor / patch** 중 ___ (사유: ___)

## 3. 소비자 커버리지

| 소비자 기대(FE/Pact) | 계약 커버 | 비고 |
|----------------------|-----------|------|
| campaign.thumbnailUrl | ✅ | |
| campaign.dDay | ❌ | spec 미정의 — 통합 시 깨짐 |

## 4. 코드 ↔ spec drift (해당 시)

| 유형 | 위치 | 상세 |
|------|------|------|
| 미문서 엔드포인트 | POST /campaigns/{id}/close | 코드에만 존재 |
| 필드명 불일치 | GET /campaigns | 코드 created_at ↔ 계약 createdAt |

## 5. FE 착수 판정

| 항목 | 결과 |
|------|------|
| 완결성 FAIL 엔드포인트 | N건 |
| breaking 변경 | N건 |
| 소비자 미커버 항목 | N건 |
| drift(미문서/유령/불일치) | N건 |
| **FE 착수** | **차단(BLOCKED) / 해제(UNBLOCKED)** |

판정 기준:
- 완결성 FAIL 0건 + 소비자 미커버 0건 → 신규 계약 UNBLOCKED
- 위 + breaking 변경에 SemVer/소비자 통지 합의 완료 → 변경 계약 UNBLOCKED
- 하나라도 미충족 → BLOCKED, 미해결 항목을 아래에 명시

## 6. FE-unblock 체크리스트 (미해결 항목)

- [ ] POST /campaigns: 에러 스키마·예시·required 보강
- [ ] response.dDay 필드 계약에 추가 또는 FE 요구 철회 합의
- [ ] 필드명 표기(snake/camel) 한쪽으로 통일
```

> 수치 인용 시 Honesty Guardrail을 따른다. 보고서에 '개선 N%' 같은 약속을 쓰지 않으며, 효과는 조직 baseline 측정으로 남긴다.

## 체크리스트

### 완결성
- [ ] 모든 엔드포인트에 요청·응답 shape이 `$ref`로 정의됨
- [ ] 성공 + 주요 실패 상태코드가 명시되고 에러는 공통 에러 스키마 사용
- [ ] 각 엔드포인트에 요청·응답 예시가 1개 이상 존재
- [ ] 모든 필드에 required·nullable이 명시됨
- [ ] 인증 스킴이 명시(공개 엔드포인트는 명시적으로 비움)
- [ ] 목록 응답에 페이지네이션·빈·에러 shape이 구분되어 정의됨

### 호환성 (변경 모드)
- [ ] 배포 계약 대비 breaking/non-breaking이 분류됨
- [ ] breaking 변경 각각에 영향 소비자가 한국어로 설명됨
- [ ] 변경 성격에 맞는 SemVer bump가 권고됨

### 소비자 커버리지
- [ ] FE 요구 shape·필터·엣지가 계약에 전부 존재함
- [ ] Pact 등 CDC 기대가 공급자 spec에 모두 커버됨

### drift
- [ ] 미문서 엔드포인트 없음
- [ ] 유령 엔드포인트 없음
- [ ] 코드↔계약 간 응답 타입·필드명 일치

## 사용자 소통

- Phase 0에서 검수 모드를 반드시 확인한다.
- 완결성 FAIL·breaking 변경 발견 시 즉시 사용자에게 알린다.
- 이 스킬은 계약 자체를 수정하지 않는다(읽기 위주). 보강 항목은 구체적으로 제시하고 합의·수정은 BE/FE가 수행한다.
- breaking 변경이 있으면 SemVer 권고와 소비자 통지를 함께 안내한다.

## 참고 / 근거

수치는 효과크기가 아니라 정성근거로만 인용한다(Honesty Guardrail). 표본·자기보고·preprint 한계를 함께 적는다.

**2025+ 근거**

- CDC 테스트가 주입 인터페이스 결함 53건 중 41건(77%)을 검출. 단 미검출 12건 중 11건은 값 범위(value range) 변경으로 CDC가 단일 값만 spot-check하기 때문 — Schwarz, Quast, Riehle, "Ensuring Syntactic Interoperability Using Consumer-Driven Contract Testing", Software Testing, Verification and Reliability (Wiley) 2025; 35:e70006 [GOLD, 단일 사례 참여형 액션리서치 + SLR]. DOI 10.1002/stvr.70006
- LLM 에이전트 워크플로의 코드→OpenAPI 추론에서 평균 F1 엔드포인트 >98%, 요청 파라미터·응답 각 97%, 파라미터 제약 92%(n=12 실세계 API, 5개 언어·8개 프레임워크); 추론은 제안으로 두고 사람 리뷰로 확정 — "OOPS: Automated generation of REST API specification via LLMs", Journal of Systems and Software vol.239 (2026), article 112914 (arXiv:2601.12735) [SILVER, n=12 소표본·LLM 비결정성].
- API-first 채택 74%(2023년 66%에서 상승), 개발자 63%가 1주 이내 API 생산(전년 47%) — Postman, "2024 State of the API Report" (Business Wire 보도자료, 2024-10-15) [SILVER, 벤더 자기보고·상관이며 인과 아님 / 효과는 조직이 baseline으로 측정]. ※ postman.com/state-of-api 는 최신 연도 리포트를 서빙하므로 2024 수치는 2024 아카이브를 출처로 한다.

**도구·표준 문서**

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Spectral — OpenAPI/AsyncAPI 린터](https://docs.stoplight.io/docs/spectral)
- [oasdiff — OpenAPI breaking-change diff](https://www.oasdiff.com/) — 470+ 개의 서로 다른 변경 유형을 breaking/non-breaking으로 분류 탐지(각 부류의 정확한 개수는 문서 미명시) [SILVER, 벤더 문서]
- [Pact — Consumer-Driven Contract Testing](https://docs.pact.io/)
