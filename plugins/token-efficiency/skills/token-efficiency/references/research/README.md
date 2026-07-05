# 토큰 효율 — 2025+ 근거 리서치 (합성)

> 목적: 외부 스킬 `improve-token-efficiency`(Claude Code 세션 JSONL을 파싱해 4축 점수 + 5개 비효율 탐지 + $ 절감 휴리스틱을 내는 스크립트군)를 **2025~2026 1차 근거로 보강·개선**하기 위한 딥리서치.
> 방법: `deep-research` 커스텀 워크플로우 — 5개 조사 각도 병렬 WebSearch+WebFetch → 각도별 **적대적 팩트체크**(claim refute·출처 실재/연도 확인, 3표 중 2표 refute 시 폐기) → 인용 dossier. 캐싱 경제학(각도 2)은 세션 한도로 arXiv 검증이 중단되어 **Anthropic 1차 문서(claude-api 스킬)로 직접 근거화**했다.
> 수행일: 2026-07-04. 검색·수집 에이전트 51개 완료 + 검증 52건(refuted 판정 포함).
> **정직성 주의**: 과장된 claim은 강등했다. 예 — ACON "정확도 손실 없이 압축"은 **REFUTED**(3개 벤치 중 2개에서 full-context 대비 정확도 하락, 개선은 *다른 압축 baseline* 대비였음). Context-Folding "10× 축소"는 **RL 학습 시에만** 성립하고 프롬프트-only(Claude Code에 해당)에선 성립 안 함 → 아래 개선은 **CONFIRMED·강한 PLAUSIBLE만** 반영한다.

## 세션 인덱스

| 세션 | 조사 각도 | 겨냥 컴포넌트 | 파일 |
|------|-----------|---------------|------|
| 1 | 컨텍스트 엔지니어링·압축·관측치 프루닝·folding | context-bloat / giant-tool 탐지기 | [session-1-context-engineering.md](session-1-context-engineering.md) |
| 2 | 프롬프트 캐싱·KV cache 경제학 (1차 문서) | cache 축(40%)·poor-cache 탐지기·PRICING | [session-2-prompt-caching-economics.md](session-2-prompt-caching-economics.md) |
| 3 | tool-call 궤적 효율·redundant action 탐지 | duplicate / subagent / read 탐지기·redundancy 축 | [session-3-trajectory-redundancy.md](session-3-trajectory-redundancy.md) |
| 4 | 비용 인지 모델 라우팅·캐스케이드 | model-routing 절감 휴리스틱 | [session-4-cost-aware-routing.md](session-4-cost-aware-routing.md) |
| 5 | cost-of-pass·토큰 예산·효율 벤치마크 | 점수 루브릭 프레이밍·정직성 | [session-5-cost-of-pass-budgets.md](session-5-cost-of-pass-budgets.md) |

---

## 헤드라인 반전 (스킬의 암묵 전제를 뒤집는 근거)

1. **거대 tool 출력의 올바른 처방은 head/tail 잘라내기가 아니다.** Squeez(arXiv:2604.04979)에서 naive 절단은 관측치의 78~95%를 잃는다(First-N 0.14, **Last-N 0.05**, BM25 0.22 recall @ ~10% 보존). 원 스킬의 giant-tool-output fix("head/grep/wc로 자르라")는 위험 — **잘라내기 전이 아니라 애초에 작게 요청**해야 하고, 이미 받은 큰 결과는 어느 줄이 중요한지 알 수 없으므로 blind-truncate 금지. (session-1/3)
2. **/compact를 무조건 권하면 캐시를 깬다.** history 압축은 KV/prompt 캐시를 깨 재계산을 강제하고 "일부 경우 총비용을 올린다"(ACON 2510.00615 저자 명시). 스킬의 40%대 캐시 축과 직접 상충 → **누적 낭비가 캐시 재예열 비용을 넘을 때만** compact. (session-1/2)
3. **비효율은 3종으로 분류된다 — useless / redundant / expired.** AgentDiet(arXiv:2509.23586)의 궤적-낭비 taxonomy. 원 스킬의 duplicate-tools는 "redundant"만 잡는다. **"expired"(서브태스크 완료 후에도 남는 관측치)는 신설 탐지기**로 포착 — 마스킹만으로 ~52% 비용 절감·동등 정확도(Complexity Trap 2508.21433). (session-1/3)
4. **읽기가 코딩 에이전트 토큰의 76.1%다.** (arXiv:2606.14066, read 76.1% vs execute 12.1% vs edit 11.8%) → **redundancy 축을 cache와 동급(0.30)으로 상향**, read-exploration 탐지기 신설. (session-3)
5. **저비용 압축은 작은 모델에서 최대 46% 성능을 올린다.** ACON — 압축이 컨텍스트 산만(distraction)을 줄여. 하지만 46%는 *같은 작은 모델 무압축 대비*이고 최상 케이스이며 압축기 호출 비용이 든다 → "압축=공짜 절감"으로 오귀속 금지. (session-1)
6. **success ≠ token count.** cost-of-pass(arXiv:2508.02694)는 성공-가중 비용을 옳은 지표로 정의. 로그로는 성공을 볼 수 없으므로 **점수는 효율 프록시일 뿐 cost-of-pass가 아님**을 명시하고, 저토큰=우수로 단정 금지. (session-5)
7. **모델 비용효율은 작업 의존이다.** 경량=저난도 정량, 대형=지식집약, 추론모델=복잡 정량(2508.02694). → 원 스킬의 "30% 플랫 Opus→Sonnet" 대신 **세션별 다운그레이드 후보 판별**로 재조작화. (session-4/5)

---

## 개선 결정 (근거 → 변경)

| # | 변경 | 근거(세션) | 성격 |
|---|------|-----------|------|
| C1 | **PRICING 현행화**: Opus $15/$75(폐기가) → $5/$25, Fable 5 $10/$50 추가, 캐시배수를 입력가에서 파생(read 0.1×/write5m 1.25×/write1h 2×) | S2 | 정확성(버그) |
| C2 | **낭비 $는 세션 실제 모델가로** 산정(플랫 Opus 폐기) | S2·S4 | 정확성 |
| C3 | **giant-tool fix 교정**: blind head/tail 절단 금지 → 작게 요청·stale 마스킹 | S1·S3 | 정직성/정확성 |
| C4 | **신규 탐지기 stale-observation**(AgentDiet "expired" + Complexity Trap 마스킹) | S1·S3 | 신규 |
| C5 | **신규 탐지기 cache-invalidation-churn**(exact-prefix 흔들림) | S2 | 신규 |
| C6 | **신규 탐지기 read-exploration-heavy** + redundancy 축 0.20→0.30 | S3 | 신규+가중치 |
| C7 | **subagent-overuse 프레이밍 개선**: folded vs unfolded 위임(요약 반환 여부) | S1 | 측정 프레이밍 |
| C8 | **compact 권고에 캐시-깨짐 caveat** | S1·S2 | 정직성 |
| C9 | **model-routing을 세션별 후보 판별로** 재조작화(플랫 30% 폐기) | S4·S5 | 측정식 |
| C10 | **점수는 효율 프록시(≠cost-of-pass) 명시** + 축별 근거 등급(CONFIRMED/PLAUSIBLE/HEURISTIC) | S5 | 정직성 |
| C11 | **대시보드 CDN 의존 제거**(인라인 SVG, 오프라인/CSP 안전) | 구현 품질 | 신규 |
| C12 | **테스트 신설**(test_efficiency.py — 가중치 합·가격 동기화·탐지기 회귀) | 구현 품질 | 신규 |

### 바꾸지 말 것 (근거 부재로 보류)
- 100k/20턴·50k chars·2% density 같은 절대 임계값을 "정확도 X% 하락"으로 정량화 — 1차 근거 없음(HEURISTIC 라벨 유지).
- Context-Folding 10× 축소를 절감 근거로 인용 — RL 학습 전제라 Claude Code(프롬프트-only)에 미적용.
- 특정 압축률/캐시-적중 임계값을 성공률 인과로 연결 — 모델·작업 의존.

---

## 근거 서열 (탐지기 우선순위로 이식)

```
읽기 재사용 규율(76.1% 토큰) ≈ 캐시 프리픽스 안정성  >  관측치 프루닝(expired/giant)  >  중복 제거  >  컨텍스트 부풀림 임계값(휴리스틱)
```
이 서열이 v2 가중치(cache 0.35 ≈ redundancy 0.30)와 신규 탐지기 배치의 뼈대다.
