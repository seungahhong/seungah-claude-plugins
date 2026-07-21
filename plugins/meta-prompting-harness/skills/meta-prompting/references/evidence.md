# 근거 Dossier — 메타 프롬프팅 기법별 학술 검증

이 문서는 플러그인의 각 기법이 **1차 문헌에서 지지되는지**를 정직하게 등급화한다. 출처는 `/deep-research`(6각도 검색 → 25소스 fetch → 99주장 추출 → 25주장 3표 적대 검증, 23 confirmed/2 refuted)로 수집했다.

## 등급 정의

- **STRONG** — 1차 문헌·공식 문서가 직접 지지(단, 대부분 **모델·과제 조건부**·저자 자기보고이므로 "보편 법칙" 아님).
- **report-only** — 그럴듯하고 널리 쓰이지만 **이번 조사에서 1차 근거가 생존하지 못함**. 실무 관행으로만 제시하고 "실증됐다"고 말하지 않는다.
- **REFUTED** — 적대 검증에서 기각. **플러그인에 넣지 않는다.**

---

## 기법별 판정

### T1. 메타 프롬프팅 = "AI가 프롬프트를 최적화 생성 → 새 컨텍스트에 주입" — **STRONG (조건부)**
- **지지**: Suzgun & Kalai *Meta-Prompting*(arXiv:2401.12954, 2024) 표준 프롬프팅 대비 +17.1%(GPT-4, Game of 24 등). OPRO(arXiv:2309.03409, 2023) 이전 해답+점수 궤적을 메타프롬프트로 넣어 사람 설계 프롬프트를 GSM8K 최대 8%·BBH 최대 50% 상회. PromptAgent(arXiv:2310.16427, ICLR 2024) 프롬프트 최적화를 MCTS 전략 탐색으로 정식화, CoT·기존 최적화기 상회.
- **한계(반드시 동반)**: 수치는 **저자 자기보고·모델/과제 특이적·전이 불안정**. OPRO의 'Take a deep breath'는 후속/타 모델에서 재현 안 됨. PromptAgent는 LLM 비결정성으로 ~20% 변동·소형 모델에서 급락. Meta-Prompting +17%는 GPT-4 한정·도구(인터프리터) 의존. → **"보편 법칙"으로 쓰지 말 것.**
- **REFUTED(사용 금지)**: "메타프롬프팅 = 한 LM이 지휘자가 되어 전문가 LM 인스턴스들을 생성·통합"이라는 Suzgun식 프레이밍은 이 하네스의 정의를 지지하지 **않음**(0-3 기각). 우리 정의는 "프롬프트를 만드는 프롬프트"이지 멀티-전문가 오케스트레이션이 아니다.

### T2. 생성 전에 AI가 "빠진 요소"를 먼저 질문하게 하라 — **STRONG**
- **지지**: ClarifyGPT(FSE 2024 / arXiv:2310.10996, dl.acm.org/10.1145/3660810) GPT-4 Pass@1 MBPP-sanitized 70.96%→80.80%(사람 평가), 4벤치 평균 GPT-4 68.02%→75.75%. Orchid 벤치(arXiv:2604.21505, 6모델·1,304과제) 요구 모호성이 Pass@1을 일관되게 저하(GPT-4 28~31pp) → 해소하면 정확도 회복. Li *LLMs Should Ask Clarifying Questions*(arXiv:2308.13507) — 포지션 페이퍼(제안).
- **정직성 뉘앙스(반드시 동반)**: 명확화는 **코딩/추론 능력과 분리된 별개의 모델 의존적 역량**이다(ClarifyCodeBench arXiv:2607.00711: "capability decoupling"·"reasoning paradox"; ClarEval arXiv:2603.00187 교차확인). 즉 **강한 모델이라고 자동으로 잘 묻지 않는다** → 프롬프트로 "먼저 질문하라"고 **명시적으로 유도**해야 한다.
- **REFUTED(사용 금지)**: "LLM은 모호성을 스스로 식별/해소할 수 없다"는 강한 주장은 기각(1-2). 명확화는 **프롬프팅으로 이끌어낼 수 있다**(불가능이 아님). ClarifyGPT 수치는 저자 보고·시뮬레이션 사용자 오라클 기반이라는 caveat.

### T3. 성공 조건 + 검증 조건을 명시하라 — **STRONG (Anthropic 공식)**
- **지지**: Anthropic 공식 프롬프트 엔지니어링 가이드 — 전제조건이 "성공 기준의 명확한 정의" + "그 기준으로 경험적 테스트할 방법"이며 "없으면 먼저 그것부터 확립하라". Best-practices: *"Before you finish, verify your answer against [test criteria]."* → "특히 코딩·수학에서 오류를 잡는다". Anthropic Console은 prompt generator·improver를 **1급 제품으로 제공**(= AI 보조 메타프롬프팅을 공식 지지).
- **정직성 뉘앙스**: "reliably catches errors"는 **벤치마크 없는 벤더 주장**이고, 순진한 자기수정(self-correction) 효과는 학계에서 논쟁적(Huang et al. 2023 "LLMs cannot self-correct reasoning yet"). 단 Anthropic 문구는 **외부 기준(external criteria) 대비 검증**을 말하며, 이것이 지지되는 형태다(순진한 자기수정이 아님). → 우리는 "검증을 **외부 성공 기준에 걸어라**"로만 권한다.

### T4. 실행 환경/대상 도구에 맞게 프롬프트를 변환하라 — **report-only (근거 약함)**
- **판정**: 환경/도구 특이적 변환이 **품질을 높인다는 1차 근거가 이번 조사에서 생존하지 못함**. OPRO/PromptAgent가 과제/모델별 최적화를 하므로 **간접적으로 그럴듯**하지만 직접 소스 없음.
- **플러그인 취급**: 실무 관행으로 제시(환경별 하드 제약·엔딩 조건을 넣는 것은 상식적으로 유용). 단 **"실증된 효능"이라 말하지 않는다.** `execution-environments.md`의 수치는 도구 문서로 그때그때 확인.

### T5. 완성된 프롬프트만 fresh(짧은) 컨텍스트에 주입하라 — **STRONG (방향성)**
- **지지**: Liu et al. *Lost in the Middle*(arXiv:2307.03172, TACL 2024) — 관련 정보가 처음/끝에 있을 때 성능 최고, 중간에서 급락(U자), GPT-3.5/4·Claude 1.3 등 재현. 확장 컨텍스트 모델이라고 낫지 않음(위치 문제). Chroma *Context Rot*(2025, 18개 프런티어 모델) — 사소한 과제에서도 입력 길이가 늘면 성능 일관 저하. NoLiMa(arXiv:2502.05167) 보강.
- **한계**: 어느 연구도 "완성 프롬프트만 fresh context 주입 vs 누적 컨텍스트 반복"을 **직접 비교하지 않음** — 건전한 **방향성 추론**이다. Chroma는 리트리벌 판매사(방법론은 공개). → "긴/오염된 컨텍스트는 공짜가 아니다"까지가 확실, 정확한 개입 효과는 미검증.

### T6. 큰 그림 먼저 펼친 뒤 요약·축소가 더 디테일하다 — **report-only (근거 약함)**
- **판정**: expansion-then-compression / outline-conditioned generation을 지지하는 주장이 **검증 생존 못 함**. Self-Refine(arXiv:2303.17651)은 인접하나 "확장 후 압축이 더 낫다"는 특정 주장은 미지지.
- **플러그인 취급**: 실무 관행으로만(특히 길이 상한이 있는 환경에서 유용). **"실증됐다"고 말하지 않는다.**

### T7. 메타프롬프팅은 은탄환이 아니다 — **STRONG**
- **지지**: Anthropic 공식 — "모든 성공 기준·실패가 프롬프트 엔지니어링으로 최선 해결되진 않는다. 예: 지연/비용은 다른 모델 선택이 더 쉬울 수 있다." 여기에 T1의 불안정성 근거(OPRO 전이 실패·PromptAgent ~20% 변동·소형 모델 붕괴)가 더해져 **"도움되지만 제한적·불안정·모델 의존적"**을 정당화.
- **scope caveat**: Anthropic 문구 자체는 "일부 목표엔 틀린 도구"까지만 지지. 더 넓은 불안정성/과적합 우려는 OPRO·PromptAgent 근거로 뒷받침.

---

## 1차 소스 목록 (인용용)

| # | 소스 | 지지 기법 |
|---|------|-----------|
| 2401.12954 | Suzgun & Kalai, Meta-Prompting (2024) | T1 |
| 2309.03409 | Yang et al., OPRO (2023) | T1·불안정성 |
| 2310.16427 | Wang et al., PromptAgent (ICLR 2024) | T1·불안정성 |
| 2405.10276 | Revisiting OPRO: Small-Scale LLM Limits | T1 한계 |
| 2308.13507 | Li, LLMs Should Ask Clarifying Questions (2023) | T2 |
| 2310.10996 / 10.1145/3660810 | ClarifyGPT (FSE 2024) | T2 |
| 2604.21505 | Orchid: requirement ambiguity benchmark | T2 |
| 2607.00711 | ClarifyCodeBench | T2 뉘앙스 |
| 2603.00187 | ClarEval | T2 뉘앙스 |
| Anthropic Docs | prompt-engineering overview·best-practices (platform/docs.claude.com) | T3·T7 |
| Huang et al. 2023 | LLMs cannot self-correct reasoning yet | T3 caveat |
| 2307.03172 | Liu et al., Lost in the Middle (TACL 2024) | T5 |
| trychroma.com/context-rot | Chroma Context Rot (2025) | T5 |
| 2502.05167 | NoLiMa: long-context degradation | T5 |
| 2303.17651 | Madaan et al., Self-Refine (2023) | T6 인접(미지지) |

**조사 메타**: 시점 민감(2604.21505·2607.00711은 2026 프리프린트·미피어리뷰, 수치 변동 가능). 저자 자기보고 편향·모델/과제 조건부성이 만연 → 어떤 기법도 보편 법칙으로 서술하지 않는다.
