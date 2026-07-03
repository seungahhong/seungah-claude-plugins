# AI-Readiness Cartography — 근거 dossier (인덱스)

v3 루브릭은 2025~2026 1차 근거로 v2를 리팩토링한 것이다. 근거는 `deep-research` 커스텀 워크플로우(5개 조사 각도 병렬 WebSearch+WebFetch → 각도별 적대적 팩트체크)로 수집·검증됐다(2026-07-03). 검증 과정에서 **지어낸 인용 1건 적발**(가짜 "LibEvoBench arXiv:2606.25402" → 실재 RustEvo²·LibEvolutionEval로 대체)과 **과장 수치 다수 강등**. 각 claim에는 CONFIRMED/PLAUSIBLE/REFUTED/UNVERIFIABLE 판정이 붙어 있으며, 루브릭은 CONFIRMED·강한 PLAUSIBLE 근거만 반영한다.

## 세션 (상세는 [research/](research/))

| 세션 | 각도 | 핵심 근거 | 파일 |
|------|------|-----------|------|
| 0 | 합성·결정 서열(R1~R12) | 헤드라인 반전 7개 + 리팩토링 결정표 | [research/README.md](research/README.md) |
| 1 | 코드 이해도 메트릭 ↔ 성공률 | ORACLE-SWE(2604.07789), Nemotron-CORTEXA | [research/session-1-comprehension-metrics.md](research/session-1-comprehension-metrics.md) |
| 2 | 문맥 엔지니어링 실증 | ETH Zurich AGENTS.md(2602.11988), Context Rot, Lost-in-the-Middle | [research/session-2-context-engineering.md](research/session-2-context-engineering.md) |
| 3 | grounding·hallucination | USENIX slopsquatting(2025), Ashik(2604.09515) | [research/session-3-grounding-hallucination.md](research/session-3-grounding-hallucination.md) |
| 4 | repo 구조 ↔ localization | LocAgent(2503.09089), RepoMirage(2605.26177) | [research/session-4-repo-structure.md](research/session-4-repo-structure.md) |
| 5 | 벤치마크·조작화 방법론 | Factory Agent Readiness, Kenogami lowest-as-ceiling | [research/session-5-benchmark-operationalization.md](research/session-5-benchmark-operationalization.md) |

## 루브릭 → 근거 매핑 (요약)

- **E 최상위 가중(22) + Gate-2** ← S1 C1(ORACLE-SWE: reproduction +26~27pp), S5 C8.
- **Gate-1 Reference Integrity(dangling 0)** ← S3 C1·C5·C9(hallucinated path 능동 오도·모델 의존 → 절대 임계값 대신 불변식).
- **집계를 gating으로** ← S5 C8(Kenogami lowest-as-ceiling), C1(가중합 반증).
- **D 기계 판독 그래프(18)** ← S4 C2·C3(LocAgent 92.7%·multi-hop 우위).
- **god-file=결합도** ← S4 C7·C8(라인 수 임계값 근거 부재).
- **A 보유율 폐기→anchor(8)** ← S2 C1·C5(보유율 반증), S4 C4·C5(structure-first).
- **B redundancy·command-first(15)** ← S2 C3·C4·C6, S5 C4.
- **H·I 신규** ← S5 C6·C7(Factory 8-pillar·DevEx, 근거 등급 Med).
- **G success⁄efficiency 분리(3)** ← S5 C5(독립적 축).

## 정직성 노트

- Factory "Task Discovery"는 실제 Factory 8-pillar가 아니라 오픈소스 재현판 축(S5 C6 정정) → I 카테고리 근거 등급 Med.
- CoReEval LLM-judge readability(S1 C7)는 human-agreement 미확인 → score.py 필수 신호로 넣지 않음.
- 라인 수 god-file, hallucination % 임계값, human 포매팅 가점은 근거 부재로 **미채택**(scoring-rubric.md "넣지 말 것" 참조).
