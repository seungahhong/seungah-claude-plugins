# 세션 1 — 컨텍스트 엔지니어링·압축·관측치 프루닝·folding

> 조사 렌즈: context-bloat / giant-tool-outputs 탐지기의 임계값과 처방을 실증 근거로 교정. "큰 컨텍스트는 비용만이 아니라 품질 문제인가", "잘라내기·요약·folding 중 무엇을 권해야 하나".
> 상태: deep-research 각도 1, 적대 검증 완료 (2026-07-04). 지어낸 출처 없음. 주요 교정: ACON "정확도 손실 없이" claim 3건 REFUTED, Context-Folding "10× 무손실" 강등.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | 무한 컨텍스트 증가 = 2개 병목: 추론 메모리 비용 + 무관정보로 인한 추론 저하(ACON) |
| C2 | **REFUTED(강등)** | ACON "26~54% 절감하며 성공률 개선"의 개선은 *다른 압축 baseline* 대비 — full-context 대비는 3개 중 2개 벤치에서 정확도 하락 |
| C3 | **CONFIRMED** | 작은 모델에서 압축이 distraction 완화로 최대 46% 성능↑(단 최상 케이스·같은 모델 무압축 대비) |
| C4 | **CONFIRMED** | Squeez: tool 관측치의 ~92%가 프루닝 가능(recall 0.86 유지) |
| C5 | **CONFIRMED** | naive 절단 실패: First-N 0.14 / **Last-N 0.05** / BM25 0.22 / Random 0.10 recall @ ~10% 보존 |
| C6 | **CONFIRMED** | folding(branch→fold)이 관측치 요약보다 우수 — 단 "유의미" 격차는 RL 학습 시 |
| C7 | **REFUTED(부분)** | Context-Folding "10× 작은 활성 컨텍스트·무손실"은 RL(FoldGRPO) 학습 전제. 프롬프트-only는 327k ReAct 대비 ~6pt 하락 |
| C8 | **CONFIRMED** | 관측치 마스킹(stale 제거)이 요약과 동등·~52% 저렴(Complexity Trap) |

## 검증된 핵심 발견

2025~2026 근거는 **큰 지속 컨텍스트가 비용만이 아니라 추론 품질을 해친다**는 점(context distraction / lost-in-the-middle)을 일관되게 지지한다(ACON, Chroma context-rot 18개 프론티어 모델, EMNLP 2025 "Context Length Alone Hurts" 13.9~85% 저하). 이는 스킬의 context-bloat 탐지기가 "낭비"라 부르는 것이 실제로 품질 리스크라는 근거다.

그러나 **처방**에서 사람 직관과 어긋나는 반증이 크다:
- **압축은 공짜가 아니다.** ACON 저자는 history 압축이 KV/prompt 캐시를 깨 재계산을 강제하고 "일부 경우 총비용을 올린다"고 명시. gpt-4.1 압축기는 $0.045/예제. → **/compact 무조건 권고는 위험**(session-2 캐시 축과 상충).
- **잘라내기가 최악의 처방일 수 있다.** Squeez의 heuristic baseline에서 **Last-N(tail 절단)이 0.05 recall로 가장 나쁘다**. 관련 줄은 관측치의 처음·중간·끝 어디에나 있어(paper 명시) head/tail 절단은 load-bearing 증거를 버린다.
- **folding > 요약**이지만 그 격차는 대부분 RL 학습이 만든다. 프롬프트-only 대조(Claude Code에 해당)에서 SWE-bench 격차는 +0.4pt(사실상 무). → **folding을 "10× 절감"으로 인용 금지**, "위임 시 요약 반환"이라는 방향성만 취함.

## 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** "unbounded context growth in long-horizon agentic tasks makes two critical bottlenecks: prohibitive inference memory costs and reasoning degradation due to irrelevant information." — ACON, Kang et al., Microsoft/KAIST, **arXiv:2510.00615** (ICML 2026). 독립 보강: Chroma context-rot(18 모델 전부 저하), lost-in-the-middle(TACL 2024, 중간 위치 ~30% 하락).
- **[C2 · REFUTED]** ACON "26~54% peak-token 절감하며 성공률 개선" — 개선 대상은 **기존 압축 baseline**이지 full-context가 아니다. 저자 tables: OfficeBench 72.63% vs 무압축 76.84%(−4.2pp), Multi-obj QA 0.336 vs 0.366; AppWorld만 ~동률. → "정확도 손실 없이 압축"으로 쓰면 안 됨. 26~54% 절감 *수치 자체*는 유효.
- **[C3 · CONFIRMED]** "enables smaller LMs to function effectively as long-horizon agents, achieving up to 46% performance improvement by mitigating context distraction." — ACON. 단 46%는 Multi-obj QA에서 Qwen3-14B 0.158→0.23의 최상 케이스, 압축기 호출 비용 별도.
- **[C4 · CONFIRMED]** LoRA Qwen 3.5 2B가 tool 출력의 92%를 제거하며 recall 0.86 / F1 0.80 유지, 18× 큰 zero-shot 모델을 recall 11pt 앞섬 — "Squeez: Task-Conditioned Tool-Output Pruning for Coding Agents", Kovács/KR Labs, **arXiv:2604.04979**(2026-04, Apache-2.0 공개). 단 span 단위 증거보존이지 end-to-end 성공률은 미측정.
- **[C5 · CONFIRMED]** ~10% 보존에서 heuristic recall: BM25 0.22 / First-N 0.14 / Random 0.10 / **Last-N 0.05** vs Squeez-2B 0.86. "relevant lines may occur at the beginning, middle, or end of an observation." — Squeez Table 4.
- **[C6·C7 · CONFIRMED/부분REFUTED]** "context folding agent matches or outperforms ReAct baselines while using an active context 10× smaller" — "Scaling Long-Horizon LLM Agent via Context-Folding", Sun et al., ByteDance/CMU, **arXiv:2510.11967**. 단 10×·무손실은 FoldGRPO **RL 학습** 결과. 무학습 folding은 SWE-bench에서 요약 대비 +0.4pt, 327k ReAct 대비 −6pt. "10× 활성 컨텍스트"는 *총 토큰*이 아니라 peak working-context(브랜치 합계는 327k에 근접).
- **[C8 · CONFIRMED]** naive placeholder 마스킹(오래된 tool 출력 생략)이 5개 모델 설정에서 LLM 요약과 동등·솔브레이트 매칭, ~52% 저렴(raw agent 대비 $1.29→$0.61) — "The Complexity Trap", JetBrains Research, **arXiv:2508.21433**(NeurIPS 2025 DL4Code workshop).

## 이 스킬에 반영 (매핑)

- **giant-tool-outputs 탐지기의 fix 교정(C4·C5)**: "head/grep/wc로 자르라"(원본) → "작게 요청(grep/라인범위/`wc -l` 먼저), 이미 받은 큰 결과는 blind-truncate 금지". research 필드에 Squeez 인용.
- **stale-observation 탐지기 신설(C8)**: 서브태스크 완료 후 10턴 이상 잔존하는 20~50k chars 관측치 플래그, fix는 "서브태스크 경계에서 /compact 또는 새 세션 분기".
- **context-bloat 임계값은 HEURISTIC 유지(C1)**: 품질 harm은 CONFIRMED지만 "100k/20턴"의 정확도-하락 정량은 근거 없음. 낭비는 세션 실제 모델의 cache_read 가로 계산.
- **compact 권고에 캐시-깨짐 caveat(C2·ACON)**: 대시보드 개선카드에 "과도한 compact는 캐시를 깬다" 명시.
- **subagent-overuse 프레이밍(C6·C7)**: "folded(요약 반환) vs unfolded 위임" 구분을 research 필드에 반영. 단 10× 절감 수치는 미인용.

## 소스 (검증 상태)
- ACON — arXiv:2510.00615 (원문·tables 확인; "무손실" claim 강등)
- Squeez — arXiv:2604.04979 (Apache-2.0 모델/데이터 공개, 수치 재현 가능)
- Context-Folding — arXiv:2510.11967 (code 공개; RL 전제 확인, 10× 강등)
- The Complexity Trap — arXiv:2508.21433 (JetBrains, NeurIPS 2025 workshop)
- SWE-Pruner — arXiv:2601.16746 (task-aware 프루닝, session-3에서 상술)
- 보강: Chroma context-rot 2025, lost-in-the-middle TACL 2024, EMNLP 2025 "Context Length Alone Hurts"
