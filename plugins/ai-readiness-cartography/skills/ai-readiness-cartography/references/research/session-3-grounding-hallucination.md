# 세션 3 — hallucinated reference/grounding 검증·stale 문서의 코드 생성 위험

> 조사 렌즈: E(E1 Reference Accuracy·hallucinated path 0)·F(Freshness). E1을 왜 최우선 가중, stale drift를 어떻게 측정·가중할지.
> 상태: deep-research 각도 3, 적대 검증 완료 (2026-07-03). **핵심 플래그: C7의 "LibEvoBench arXiv:2606.25402"는 존재하지 않는 허구 인용 → 제거하고 실재 근거(RustEvo² 2503.16922, LibEvolutionEval 2412.04478)로 대체.** (조사 주제 자체가 hallucinated reference인데 dossier 스스로 허구 인용을 낸 아이러니 → 검증 단계에서 적발.)

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | package hallucination 전체 19.7%, commercial 5.2% vs open-source 21.7% |
| C2 | **CONFIRMED** | 205,474개 고유 허구 package명, 43% 10회 전부·58% 2회+ 재등장(결정론적 artifact) |
| C3 | **CONFIRMED** | 허구명 38%가 실재 package명과 유사 |
| C4 | PLAUSIBLE | slopsquatting 공급망 공격 벡터(huggingface-cli 사례는 재인용) |
| C5 | PLAUSIBLE | 비존재 file·초과 line range 인용, interval arithmetic 검증(단일 저자 preprint) |
| C6 | **CONFIRMED** | 부실 context가 실행가능성 42.55%로 낮춤, context-memory conflict self-reflection +11%만 회복 |
| C7 | **REFUTED(부분)** | 인용 "LibEvoBench 2606.25402" **비존재** → RustEvo²·LibEvolutionEval로 대체 |
| C8 | PLAUSIBLE | code·tool-output·document span-level hallucination 벤치 부상 |
| C9 | **CONFIRMED** | hallucination 위협 "범위 축소·잔존"(2026 frontier 4.62~6.10%) → 절대 임계값 고정 금지 |

## 검증된 핵심 발견

2025+ 근거는 "검증되지 않은 context는 없는 것보다 위험하다"를 두 축으로 뒷받침한다.

1. **package hallucination**: LLM 코드 생성은 존재하지 않는 package를 상당 비율(전체 19.7%, commercial 5.2%~open-source 21.7%, 205,474개 고유 허구명)로 지어내며, 이는 무작위 noise가 아니라 **재현되는 결정론적 artifact**(2회+ 재등장 약 58%, 10회 전부 43%)여서 **slopsquatting 공급망 공격**의 안정적 표적이 된다(Spracklen et al., USENIX Security 2025 best paper). 허구명 38%가 실재명과 유사해 casual 검토를 우회.
2. **stale/부실 context의 능동적 오도**: 충분한 문서 없이 실행 가능 코드가 42.55%에 그치고(구조화 시 66.36%), 낡은 문서·parametric 지식이 현행 API와 충돌하는 "context-memory conflict"는 self-reflection으로도 +11%밖에 회복 안 됨(Ashik et al. 2026) → **틀린 context가 모델을 능동적으로 오도**.
3. **grounding 검증**: 허구 file 인용·파일 길이 초과 line range 인용은 흔한 실패 모드이며, citation을 retrieved context와 기계적으로(interval arithmetic) 대조하면 차단 가능(Arafat 2025 preprint, 외부 재현 미확인).

**반증/한계**: hallucination 비율은 모델·언어·연도에 강하게 의존(2026 frontier 4.62~6.10%로 압축, 그러나 모델 공통 허구·미등록 잔존으로 위협 지속) → **절대 수치를 rubric 임계값으로 고정하면 안 된다**(C9).

### 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** package hallucination 전체 19.7%, Python commercial 5.2% vs open-source 21.7%(4배+ 차이) — Spracklen et al., USENIX Security 2025(16 LLM family, 576k 샘플, 온도 무관).
- **[C2 · CONFIRMED]** 재현되는 artifact — 205,474개 고유 허구명, 43% 10회 전부·58% 2회+ 재등장 — 동.
- **[C3 · CONFIRMED]** 허구명 38%가 실재명과 유사 — 동.
- **[C4 · PLAUSIBLE]** slopsquatting = LLM 반복 허구명 선점 등록 악성코드 주입 벡터. huggingface-cli는 Bar Lanyado 실험 재인용(1차 재현 미확인) — Socket.dev·DevOps.com·Help Net Security, 2025.
- **[C5 · PLAUSIBLE]** LLM은 비존재 file·초과 line range 인용, citation-context 겹침을 interval arithmetic으로 검증 제안. 정확도 수치(92% vs dense 78%/sparse 74%)는 단일 저자 preprint 자기보고 — Arafat, **arXiv:2512.12117**(30 repos·180 queries).
- **[C6 · CONFIRMED]** 부실/낡은 context가 실행가능성 42.55%로 낮춤(구조화 시 66.36%), context-memory conflict self-reflection +11%만 회복 — Ashik et al., **arXiv:2604.09515**(270 real updates·8 Python libs·11 models).
- **[C7 · REFUTED→대체]** ~~LibEvoBench(2606.25402)~~ 허구 인용 제거. API 진화 하 version-specific 코드 생성 취약 방향성만 실재 근거로 — RustEvo²(**arXiv:2503.16922**), LibEvolutionEval(**arXiv:2412.04478**, NAACL 2025). 구체 수치("GPT-4 50점 하락")는 미검증이라 미인용.
- **[C8 · PLAUSIBLE]** code·tool output·document span-level grounding 검증이 별도 연구 축으로 부상 — Kovács et al., **arXiv:2607.00895**.
- **[C9 · CONFIRMED]** 위협은 2026 frontier에서 범위 축소(4.62~6.10%)되나 모델 공통 허구·미등록 잔존으로 지속 — **arXiv:2605.17062**. 함의: 절대 임계값 rubric 고정 금지.

## Rubric v3 함의

- **E1을 grounding 검증으로 재정의(측정식 변경)**:
  - (a) context 문서(CLAUDE.md/AGENTS.md/ADR)가 인용하는 모든 파일 경로를 `git ls-files` 대조.
  - (b) 인용 line range가 파일 길이 이내인지 interval 검사.
  - (c) 문서가 명시한 명령어·script 경로가 package.json/Makefile에 실재하는지.
  - **하나라도 dangling이면 E1=0 (binary gate)**. 특정 accuracy % 임계값은 고정하지 말 것(C9).
- **신규 E 하위지표 "package/dependency reference integrity"**(C1~C4) — 문서/예제가 언급하는 import·package가 lock 파일·의존 그래프에 실재하는지. 미해결 참조 감점.
- **F를 stale-drift 정량 신호로**(C6) — mtime 비교를 넘어 "문서가 언급한 심볼/파일이 코드에서 사라졌는데 문서 미갱신"인 stale drift 카운트 + `git log` 문서 vs 소스 마지막 수정 Δ. CI/hook path·package validation 강제 여부를 명시 채점.
- **B의 "quick commands·key files"를 "존재"가 아니라 "실재하며 검증됨"으로 상향**(C6과 E1 교차 연결).
- **바꾸지 말 것**: A·B·C·D·G 축소 정당화 이 각도엔 없음. 절대 임계값 고정 금지 — dangling reference 절대 0이라는 불변식으로 채점.

## 소스 (검증 상태)

- We Have a Package for You! — Spracklen et al., USENIX Security 2025(best paper) (PDF 403이나 다중 요약·GitHub 상호 확인) [C1·C2·C3]
- Citation-Grounded Code Comprehension — Arafat, arXiv:2512.12117, 2025-12 (실재, 단일 저자) [C5]
- When LLMs Lag Behind: Knowledge Conflicts from Evolving APIs — Ashik et al., arXiv:2604.09515, 2026-04 [C6]
- The Range Shrinks, the Threat Remains — arXiv:2605.17062, 2026 [C9]
- Beyond Document Grounding: Span-Level Hallucination Detection — Kovács et al., arXiv:2607.00895, 2026-07 [C8]
- RustEvo² — arXiv:2503.16922, 2025-03 / LibEvolutionEval — arXiv:2412.04478, NAACL 2025 (C7 대체 근거)
- Importing Phantoms — arXiv:2501.19012, 2025
- The Rise of Slopsquatting — Socket.dev, 2025 [C4]
- **제거**: ~~LibEvoBench, arXiv:2606.25402~~ — 존재 확인 불가한 허구 인용(실재는 LibEvolutionEval 2412.04478). 본 dossier 주제에 대한 반례이므로 삭제.
