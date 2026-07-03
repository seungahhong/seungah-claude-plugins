# AI-Readiness Cartography — 2025+ 근거 리서치 (합성)

> 목적: 외부 스킬 `ai-readiness-cartography`(임의 repo를 100점·7카테고리로 채점하는 결정론적 스코어러 + HTML 대시보드)의 **rubric·score.py를 2025년 이후 1차 근거로 리팩토링**하기 위한 딥리서치.
> 방법: `deep-research` 커스텀 워크플로우 — 5개 조사 각도 병렬 WebSearch+WebFetch → 각도별 **적대적 팩트체크**(claim refute·출처 실재/연도 확인) → 인용 dossier.
> 수행일: 2026-07-03. 에이전트 10개(연구 5 + 검증 5), 도구 호출 100회.
> **정직성 주의**: 검증 과정에서 **지어낸 인용 1건 적발**(가짜 "LibEvoBench arXiv:2606.25402" → 실재 RustEvo²·LibEvolutionEval로 대체)과 **과장 수치 다수 강등**. 각 claim에는 CONFIRMED/PLAUSIBLE/REFUTED/UNVERIFIABLE 판정이 붙어 있으며, 아래 리팩토링은 **CONFIRMED·강한 PLAUSIBLE 근거만** 반영한다.

## 세션 인덱스

| 세션 | 조사 각도 | 겨냥 카테고리 | 파일 |
|------|-----------|---------------|------|
| 1 | LLM 코드 이해도·readability 메트릭 ↔ agentic task 성공률 | G·A·E | [session-1-comprehension-metrics.md](session-1-comprehension-metrics.md) |
| 2 | repo 문맥 엔지니어링(CLAUDE.md/AGENTS.md) 실증 효과·실패 모드 | B·C·A | [session-2-context-engineering.md](session-2-context-engineering.md) |
| 3 | hallucinated reference/grounding 검증·stale 문서 위험 | E·F | [session-3-grounding-hallucination.md](session-3-grounding-hallucination.md) |
| 4 | repo 구조(모듈 경계·의존 그래프·god file) ↔ 편집 정확도·localization | D·A | [session-4-repo-structure.md](session-4-repo-structure.md) |
| 5 | agentic 벤치마크 ↔ repo readiness 정량 조작화 방법론 | 전체 집계 구조 | [session-5-benchmark-operationalization.md](session-5-benchmark-operationalization.md) |

---

## 헤드라인 반전 (rubric의 암묵 전제를 뒤집는 근거)

1. **"컨텍스트 문서가 많을수록 agent가 낫다"는 거짓이다.** ETH Zurich 통제 실험(arXiv:2602.11988, 2026)은 LLM 생성 AGENTS.md/CLAUDE.md류가 SWE-bench Lite 성공률을 −0.5%, 자체 AGENTBENCH를 −2% *낮추고* 추론 비용을 20%+ 올렸음을 보였다(개발자 손수 작성본조차 +4%에 비용 +19%). 이득은 **다른 문서가 전혀 없는 undocumented repo에서만** 났다 → **보유율(존재율) 자체 가점은 근거에 반한다.**
2. **실행·검증 신호가 정적 문서보다 압도적으로 성공률에 기여한다.** ORACLE-SWE(arXiv:2604.07789, 2026) ablation: reproduction test +26~27pp > execution +14 > edit location +12 > API +8 > 문서. → **E(검증 게이트)를 최상위 가중 + gate로.**
3. **순수 가중합 100점은 잘못된 집계다.** 산업 프레임워크(Factory.ai 8-pillar/5-level 80% 게이팅, Kenogami 9-dim **lowest-as-ceiling** + blocking/constraining)는 공통적으로 **하나의 blocking 결함이 전체 등급에 상한을 씌우는** 구조를 쓴다. → **가산 점수를 gate·ceiling 구조로.**
4. **파일 라인 수 임계값(300/500)은 agent 성능으로 검증된 적이 없다.** 그 값은 전통 defect-prediction(god class)에서 차용됐다. agent 관점에선 **결합도(fan-in/fan-out)·의존 그래프·lost-in-the-middle**이 더 나은 설명이다(LocAgent arXiv:2503.09089; RepoMirage arXiv:2605.26177). → **라인 수는 "휴리스틱, 근거 약함"으로 강등, 결합도·의존 그래프로 재조작화.**
5. **hallucination 비율은 모델·언어·연도 의존이라 절대 임계값을 고정하면 안 된다**(arXiv:2605.17062). 대신 **repo 내 dangling reference 절대 0**이라는 검증 가능한 불변식으로 채점. package hallucination은 재현되는 결정론적 artifact(205,474개 고유 허구명, USENIX Security 2025 best paper) → **slopsquatting 공급망 위험**.
6. **success ≠ efficiency.** 문서가 성공률은 그대로 두고 runtime −28.64%·token −16.58%만 바꾼 사례(arXiv:2601.20404, ICSE 2026). → **G를 "task success"와 "cost/efficiency" 두 축으로 분리.**
7. **human readability ≠ LLM readability.** human 지향 포매팅(들여쓰기·공백)은 LLM에 무익하고 토큰만 쓴다(arXiv:2508.13666). poor-readability(난독화·식별자 변형)는 comprehension을 떨어뜨린다(arXiv:2601.05485). → readability 지표는 포매팅이 아니라 **식별자 명료성·낮은 난독도**로.

---

## Rubric v3 리팩토링 결정 (근거 → 변경)

| # | 변경 | 근거(세션·claim) | 성격 |
|---|------|------------------|------|
| R1 | **집계를 가산합 → gate + lowest-as-ceiling.** E(검증)를 blocking gate로 승격: hallucinated path ≠0 또는 build/test 미작동이면 전체 등급에 상한(예: 최대 AI-Fragile). | S5 C1·C8, S3 C1 | 구조 |
| R2 | **E(Verification & Quality Gates) 배점 상향(15→20~25) + 실행 신호 최상위.** reproduction/build/test 실행 가능성·CI를 E1과 함께 최상위 하위지표로. | S1 C1, S5 C8 | 가중치 |
| R3 | **A(Navigation): 보유율 만점 신호 폐기 → novelty 게이트.** 문서 내용이 코드/README에서 이미 discoverable하면 감점. "CLAUDE.md 존재"가 아니라 "의존 이웃·진입점을 명시하는가". | S2 C1·C5, S5 C3·C4, S1 C2 | 측정식 |
| R4 | **B(Context Quality): 절대 line 목표 삭제 → redundancy ratio·command-first.** 문서 bullet을 repo grep으로 대조해 중복률 산출(높으면 감점), 산문 overview 최소화 가점, exact command·done 기준 최고 배점. | S2 C3·C4·C6, S5 C4 | 측정식 |
| R5 | **D(Dependency): "mermaid 존재" → 기계 판독 의존 그래프.** import/module graph 파싱 가능성·연결성·경계 명확성. 가중치 상향. | S4 C2·C3·C9 | 측정식+가중치 |
| R6 | **god-file: 라인 수 단독 → 결합도 기반.** fan-in/fan-out·export 심볼 수 대비 응집. 라인 수는 보조·"근거 약함" 라벨. | S4 C7·C8 | 측정식 |
| R7 | **E1: %정확도 임계값 → binary dangling-reference gate + package integrity.** 문서 인용 경로 `git ls-files` 대조, line range 파일 길이 이내 검사, import/package가 lock 파일에 실재하는지. | S3 C1·C5·C9 | 측정식 |
| R8 | **F(Freshness): mtime → stale-drift 방향성.** 문서가 언급한 심볼/파일이 코드에서 사라졌는데 문서 미갱신인 "stale drift" 카운트 + CI/hook path validation 강제 여부. | S3 C6 | 측정식 |
| R9 | **G(Outcomes): success vs cost/efficiency 분리.** task success telemetry / runtime·token·step telemetry 두 지표. | S5 C5, S1 C1 | 구조 |
| R10 | **신규 축(근거 등급 표기): Feedback-loop latency, Env reproducibility, Task Discovery.** pre-commit/CI 속도·devcontainer/.env.example·issue/PR template. Factory/DevEx 근거이므로 CONFIRMED보다 낮은 등급 라벨. | S5 C6·C7·C9 | 신규 |
| R11 | **모든 지표에 auto / heuristic / manual·LLM-judgment 라벨.** score.py 자동화 범위를 명확히. LLM-judge readability는 옵션이되 human-agreement 미확인이므로 필수화 금지. | S5 C9, S1 C7 | 정직성 |
| R12 | **readability 지표: human 포매팅 가점 금지 → 식별자 명료성·난독도.** | S1 C3·C4·C5 | 측정식 |

### 바꾸지 말 것 (근거 부재로 보류)
- "N줄 초과 = agent 정확도 X% 하락" 형태의 정량 감점 — **1차 근거 부재**(S4 C8).
- readability를 성공률 인과로 직접 연결 — S1 C5는 "패턴 차이"만 확인, 성공률 인과는 Low.
- 특정 hallucination % 임계값을 rubric에 고정 — 모델·연도 의존(S3 C9).
- Factory "Task Discovery" 를 CONFIRMED 등급으로 — 실제 Factory 8-pillar가 아니라 오픈소스 재현판 축(S5 C6 정정).

---

## 근거 우선순위 서열 (ORACLE-SWE ablation을 rubric 우선순위로 이식)

```
reproduction test(+26~27pp) > execution context(+14) > edit location(+12) > API 문서(+8) > 정적 산문 문서
```

이 서열이 v3 카테고리 가중치의 뼈대다: **실행·검증(E) ≫ 의존 구조·localization(D/A) > 컨텍스트 문서(B/C) — 단, 문서는 novelty·비중복일 때만.**
