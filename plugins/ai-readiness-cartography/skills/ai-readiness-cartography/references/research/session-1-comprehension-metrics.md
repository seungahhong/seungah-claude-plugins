# 세션 1 — LLM/코딩에이전트 코드 이해도·readability 메트릭 ↔ agentic task 성공률

> 조사 렌즈: G(Agent Performance Outcomes) 지표 타당성 + A(navigation) 조작화. 스코어러가 재는 프록시가 실제 agent 성공과 상관되는가.
> 상태: deep-research 각도 1, 적대 검증 완료 (2026-07-03). 지어낸 출처 없음(10개 소스 실재 확인). 주요 교정: C5 "사람보다 우월" → 초록은 "comparable" 이므로 강등.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | ORACLE-SWE: reproduction test 단일 최대 기여(+26~27pp), edit location +12(불충분) |
| C2 | **CONFIRMED** (세부 델타 PLAUSIBLE) | 컨텍스트 파일이 성공률 개선 못하고 추론비용 20%+ 증가 |
| C3 | PLAUSIBLE | human 포매팅은 LLM에 토큰만 소비(방향성) |
| C4 | **CONFIRMED** | poor-readability 코드에서 SOTA LLM comprehension 저하 |
| C5 | PLAUSIBLE (과장 강등) | LLM 코드 readability는 사람과 **대등**, 결함 패턴만 질적으로 다름 |
| C6 | PLAUSIBLE | localization 향상되나 최종 resolve 보장 못하는 ceiling |
| C7 | **CONFIRMED** | CoReEval — LLM readability judge 대규모 벤치(10 LLM·1.4M) |
| C8 | PLAUSIBLE | repository memory로 localization 개선, "+5.95pp" 수치 미확인 |
| C9 | **CONFIRMED** | SOTA SWE-bench Verified ~63~68%(Nemotron-CORTEXA 68.2%) |

## 검증된 핵심 발견

2025~2026 근거는 "코드 이해도"를 정적 readability가 아니라 **실행 가능한 신호(reproduction test·execution context)와 localization 정확도**로 조작화할 때 agentic 성공률과 가장 강하게 연결됨을 보여준다. ORACLE-SWE(arXiv:2604.07789)의 ground-truth 신호 ablation이 결정적이다 — **reproduction test가 단일 최대 기여(+26~27pp)**, edit location은 단독 +12pp로 **필요하지만 불충분**(test 신호와 결합해야 위력), 5개 결합 시 ≥97%. baseline은 GPT-4o ~38~40%.

사람 직관과 어긋나는 반증:
- human-oriented formatting(들여쓰기·공백)은 LLM 성능을 개선하지 않고 토큰만 소비한다(2508.13666, 방향성) — 사람 readability ≠ LLM-relevant readability.
- AGENTS.md류 컨텍스트 파일은 성공률을 **일반적으로 개선하지 못하면서 추론 비용을 20%+ 증가**시켰다(ETH Zurich 2602.11988) — "문서 많을수록 좋다" 전제 직접 반박.
- 그러나 localization 정확도조차 최종 resolve를 보장하지 못하는 "ceiling"이 반복 관측 → **어떤 단일 프록시도 성공을 완전 예측하지 못한다.**

### 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** 주입 가능한 5개 oracle 신호 중 reproduction test가 성공률 최대 기여(+26~27pp), edit location 단독 +12pp(불충분, test와 결합 시 위력) — "ORACLE-SWE", Li et al., 2026, **arXiv:2604.07789**. 수치: SWE-bench-Verified baseline(GPT-4o) ~38~40% → reproduction +26~27 / execution +14 / edit location +12 / API +8 / regression +4; 5개 결합 ≥97%. 신뢰도 High.
- **[C2 · CONFIRMED]** 저장소 루트 컨텍스트 파일(AGENTS.md/CLAUDE.md류)은 평균적으로 agent 성공률을 개선하지 못하고 추론 비용을 20%+ 증가 — Gloaguen et al., ETH Zurich, 2026, **arXiv:2602.11988**(438 tasks). 개별 델타는 미검증.
- **[C3 · PLAUSIBLE]** human-oriented 코드 포매팅은 LLM 성능 무개선·토큰 추가 소비 — Pan et al., Monash, 2025, **arXiv:2508.13666**. 정확한 델타 미확인.
- **[C4 · CONFIRMED]** SOTA LLM(GPT-4o·DeepSeek-V3)은 poor-readability(난독화·식별자 변경) 코드에서 comprehension 저하, prompt/reasoning 개선 제한 — 2026, **arXiv:2601.05485**.
- **[C5 · PLAUSIBLE(강등)]** LLM 생성 코드의 정량 readability는 사람과 **대등(comparable)**, 결함 패턴만 질적으로 다름(사람=누락형, LLM=과잉형) — Ye et al., 2026, **arXiv:2605.13280**(5,869 샘플). ※ 원 dossier의 "사람보다 높다"는 초록과 상충하여 강등. 성공률 인과는 Low.
- **[C6 · PLAUSIBLE]** localization 향상이 resolve rate를 올리나 강한 localization도 최종 resolve 보장 못하는 ceiling(파일 레벨은 "올바른 이웃 도달"만 포착) — C1과 정합. 개별 수치(SWE-Debate 81.67%·OrcaLoca 83.33%·SHERLOC 84.33%) 부분 확인.
- **[C7 · CONFIRMED]** LLM을 code readability judge로 검증한 대규모 벤치 CoReEval — Ouédraogo et al., **arXiv:2510.16579**, 2025(10 LLM·1.4M). 단 human-agreement 정량치 미확인 → rubric 필수화 근거로는 약함.
- **[C8 · PLAUSIBLE]** repository memory로 localization 주입 시 resolve·토큰 효율 개선, "강한 localization ≠ 자동 개선" — Boshi Wang et al., ICLR 2026, **arXiv:2510.01003**. "+5.95pp" 미확인.
- **[C9 · CONFIRMED]** SOTA SWE-bench Verified ~63~68%(Nemotron-CORTEXA 68.2% @ $3.28/문제) — NVIDIA ADLR, ICML **2025**.

## Rubric v3 함의

- **E 대폭 상향, A~D 정적 문서군 하향** (C1·C2). E를 /20~/25로, "task validation(build/test)·reproduction 스크립트 존재"를 E 최상위. score.py 자동 신호로 테스트 하네스·CI 실행 명령의 존재·pass 여부.
- **A·B 보유율 가점 폐기/조건부화** (C2). "CLAUDE.md/AGENTS.md 보유율" 자체 가점 위험 → minimal·repository-specific·비중복 측정.
- **G 확장 + localization 프록시 추가** (C6·C8). hallucinated-path 0(E1)을 넘어 localization/retrieval 정확도 프록시(파일-심볼 인덱스·정확 경로·evals localization@k). 단 ceiling 근거상 단독 만점 근거로 쓰지 말 것.
- **readability 지표: human 포매팅 가점 금지 → 식별자 명료성·낮은 난독도** (C3·C4·C5).
- **바꾸지 말 것**: F(freshness)는 이 각도 범위 밖. CoReEval(C7) LLM-judge readability는 옵션이되 human-agreement 미확인이므로 필수화 금지.

## 소스 (검증 상태)

- ORACLE-SWE — 2026, arXiv:2604.07789 (원문·수치 확인)
- Evaluating AGENTS.md — Gloaguen et al., ETH Zurich, 2026, arXiv:2602.11988 (원문 확인)
- The Readability Spectrum — Ye et al., 2026, arXiv:2605.13280 (확인; "사람보다 높다" 강등)
- The Hidden Cost of Readability — Pan et al., Monash, 2025, arXiv:2508.13666 (실재, 세부 미검증)
- Improving Code Localization with Repository Memory — Boshi Wang et al., ICLR 2026, arXiv:2510.01003 (실재, +5.95pp 미검증)
- Readability-Robust Code Summarization via Meta Curriculum Learning — 2026, arXiv:2601.05485 (실재, 방향 확인)
- CoReEval — Ouédraogo et al., arXiv:2510.16579, 2025 (실재, 1.4M·10 LLM 확인)
- SWE-Debate(2507.23348)·OrcaLoca(2502.00350)·SHERLOC(2606.24820)·Beyond Localization(2603.29067) (부분 교차확인)
- Nemotron-CORTEXA — NVIDIA ADLR, ICML 2025, 68.2% (공식 리포·GitHub 확인)
