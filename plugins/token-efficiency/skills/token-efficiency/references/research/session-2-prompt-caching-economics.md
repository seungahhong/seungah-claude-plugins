# 세션 2 — 프롬프트 캐싱·KV cache 경제학 (Anthropic 1차 문서)

> 조사 렌즈: cache 축(40%대)·poor-cache-util 탐지기·PRICING 테이블을 정확한 캐싱 경제학으로 교정. "캐시 read/write 배수는 얼마인가", "무엇이 캐시를 깨는가", "현행 모델 가격은".
> 상태: **각도 2의 arXiv 검증은 세션 한도로 중단**(caching 관련 에이전트 대량 실패). 캐싱 경제학·가격은 반증 가능한 arXiv claim보다 **Anthropic 공식 문서가 1차·권위 소스**이므로, claude-api 스킬(`shared/prompt-caching.md`·Current Models)로 직접 근거화했다. 검증일 2026-07-04.

## 검증된 핵심 발견 (1차 문서 인용)

**캐싱은 exact-prefix 매치다.** "Any change anywhere in the prefix invalidates everything after it." 렌더 순서는 `tools → system → messages`. 프리픽스의 1바이트만 바뀌어도 그 지점 이후 전체가 무효화된다. → 이것이 poor-cache-util·cache-invalidation-churn 탐지기의 이론적 근거다.

**캐시 비용 배수(입력가 기준, 모든 모델 공통):**
- **cache read ≈ 0.1× 입력**
- **cache write 5m = 1.25× 입력**
- **cache write 1h = 2.0× 입력**

원 스킬 PRICING의 Opus 배수(cw5 18.75/cw1h 30/cr 1.50 vs in 15)는 배수 비율(1.25/2.0/0.1)은 맞았으나 **base 입력가 $15가 폐기가**였다. 현행 Opus는 $5/$1M이므로 배수만 유지하면 cw5 6.25 / cw1h 10 / cr 0.5.

**손익분기:** 5m TTL은 2회 요청이면 break-even(1.25×+0.1× = 1.35× vs 2× 무캐시); 1h TTL은 3회 이상 필요(2×+0.2× = 2.2× vs 3×). → **단기 세션에 1h TTL은 순낭비**(TTL 개선카드 근거).

**최소 캐시 가능 프리픽스(모델 의존):** Opus 4.8/4.7/4.6/4.5·Haiku 4.5 = **4096 토큰**; Fable 5·Sonnet 4.6 = **2048**; Sonnet 4.5/4/3.7 = 1024. 그 미만은 마커가 있어도 조용히 캐시 안 됨(cache_creation_input_tokens=0). → 짧은 프리픽스 세션은 캐시 축에서 감점하기보다 "캐시 불가"로 취급해야 정직.

**20-block lookback:** 각 브레이크포인트는 뒤로 최대 20 콘텐츠 블록만 탐색. 에이전틱 루프에서 한 턴에 20+ 블록이 쌓이면 다음 브레이크포인트가 이전 캐시를 못 찾아 조용히 miss.

**캐시를 깨는 결정론적 원인(exact-prefix 위반):**
- 세션 도중 CLAUDE.md/system 수정 → 그 아래 전부 무효화
- 세션 도중 모델 전환 → 캐시는 모델-스코프
- 뒤늦은 이미지/스크린샷 첨부 → 프리픽스 흔들림
- system 프롬프트에 `datetime.now()`/UUID/미정렬 JSON → 매 요청 프리픽스 상이
→ 대응: **volatile 콘텐츠를 맨 뒤로**, stable(frozen system·결정론 tool 목록)을 앞으로.

## 현행 가격 (per 1M tokens, 2026-07 검증)

| Model | Input | Output | cache write 5m | cache write 1h | cache read |
|---|---|---|---|---|---|
| Claude Fable 5 (`claude-fable-5`) | 10.0 | 50.0 | 12.5 | 20.0 | 1.0 |
| Claude Opus 4.8/4.7/4.6 | 5.0 | 25.0 | 6.25 | 10.0 | 0.5 |
| Claude Sonnet 5 (`claude-sonnet-5`) | 3.0¹ | 15.0¹ | 3.75 | 6.0 | 0.3 |
| Claude Sonnet 4.6 | 3.0 | 15.0 | 3.75 | 6.0 | 0.3 |
| Claude Haiku 4.5 | 1.0 | 5.0 | 1.25 | 2.0 | 0.1 |

¹ Sonnet 5 인트로가 $2/$10(2026-08-31까지). 스크립트는 보수적으로 리스트가($3/$15) 사용.
※ 원 스킬은 Opus를 $15/$75(폐기가)로 하드코딩 → 비용 ~3× 과대계상. 이것이 C1 정확성 수정이다.
※ 스크립트 PRICING의 추가 행 — `claude-mythos-5`(Fable 5와 동일 $10/$50, Project Glasswing 전용) 및
legacy `claude-opus-4-5`($5/$25)·`claude-sonnet-4-5`($3/$15) — 는 위 표 밖이며 같은 1차 소스(claude-api 스킬)에서 직접 확인한 값이다.

**기타 1차 수치(이미지):** 고해상 이미지는 장당 최대 **~4,784 토큰**(Opus 4.7+ 고해상 vision, 구형 상한 ~1,568) — Anthropic 1차(claude-api). 대시보드 이미지 절감 카드의 장당 상한이 이 값이며, 회수율(50%)은 무근거 휴리스틱으로 라벨된다. detect_patterns의 관측치 내 이미지 추정치(1,500토큰/장)는 구형 상한 기준의 러프 값이다.

## 이 스킬에 반영 (매핑)

- **PRICING 현행화(C1)**: `_row(in, out)` 헬퍼가 cw5/cw1h/cr를 입력가에서 파생(1.25/2.0/0.1×). Fable 5/Opus 4.8/Sonnet 5 신규 행. `--pricing`으로 오버라이드 가능.
- **cache-invalidation-churn 탐지기 신설(C5)**: 고컨텍스트(30k+) 턴에서 cache_create가 입력의 30% 초과가 지속 = 프리픽스 흔들림. fix는 "프리픽스 동결(CLAUDE.md 확정·모델 선고정·이미지 조기 첨부)".
- **poor-cache-util 낭비를 (write−read) 스프레드로**: 보수적 5m 기준 cache_create × (1.25−0.1)=1.15× + 미캐시 입력 × (1.0−0.1)=0.9×, 세션 실제 모델가 사용(코드가 1h 2× 대신 5m 1.25×로 진화 — 과대계상 방지).
- **TTL 개선카드 근거**: 5m break-even 2회 / 1h 3회 → 단기 세션 1h는 낭비.
- **정직성**: 4096/2048 최소 프리픽스 미만 세션은 캐시 불가임을 SKILL.md·대시보드에 명시.

## 검증 안 된 채 폐기한 각도-2 arXiv claim (세션 한도로 미검증 → 미인용)
- "프롬프트 캐싱이 API 비용 41~80% 절감"(2601.06007) — errored 3표, 미검증. 인용하지 않음.
- OpenAI 캐싱 50% 할인·TTL 세부 — 미검증. Anthropic 문서 범위만 사용.

## 소스 (검증 상태)
- Anthropic prompt caching 문서 — claude-api 스킬 `shared/prompt-caching.md`(1차, exact-prefix·배수·최소 프리픽스·20-block·손익분기 전부 확인)
- Anthropic Current Models 가격표 — claude-api 스킬(2026-06-24 캐시, 2026-07 재확인)
- (미인용) arXiv:2601.06007 등 caching 경제학 논문 — 세션 한도로 적대검증 미완, 인용 보류
