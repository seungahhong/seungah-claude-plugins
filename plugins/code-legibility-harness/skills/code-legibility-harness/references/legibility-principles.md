# code-legibility-harness — 원리 문서 (legibility principles)

이 하네스가 왜 이 순서로 개입하는지의 근거를 7개 원리로 정리한다. 모든 인용은
정본 근거 시트(`EVIDENCE-SHEET.md`)에서만 가져오며, 각 항목에 SOURCE-TIER와
발표연월을 붙인다. 층위는 **코드 본문**(주석·독스트링 / 식별자 / 함수·모듈 granularity)이며,
저장소 층(README·CLAUDE.md·의존 그래프·CI·환경)은 자매 플러그인
`ai-readiness-cartography`가 소유한다 — 침범하지 않는다.

---

## 원리 1 — 삭제가 추가보다 안전하다

- **원리**: 틀린·오도·stale 주석을 **삭제/수정**하는 개입은 동작을 깨뜨릴 수 없고, 그 효과는 측정됐다. 반면 주석을 **추가**하는 개입은 사실성 위험을 스스로 들여온다.
- **왜**: 오도 주석 하나(MDC)는 출력 예측을 −13.47pp 떨어뜨리며, 이는 구조 변형 3종 결합(−14.04pp)에 맞먹는다. Chain-of-Thought로도 방어되지 않는다("13.8% drop due to distractibility and rationalization"). 주석은 실행되지 않으므로 삭제의 동작 위험은 0이다. 반대로 생성 주석은 최상위 모델도 약 20%가 검증가능하게 부정확하고(E-C5, 배경), 특화 파인튜닝 모델의 자동 주석 수정조차 35~45%가 틀린다(E-C4).
- **근거 ID**: E-C1 [PRIMARY-2025+ · 2025-04, NeurIPS 2025] · E-C4 [PRIMARY-2025+ · 2025, ICSE 2025] · E-C5 [PRIMARY-pre2025 · 2024-06 · 배경].
- **하네스에서의 귀결**: 개입 우선순위에서 P1(삭제/수정)이 P3(추가)보다 먼저다. 삭제는 Phase 3 게이트 B에서 코드 대조만으로 승인, 추가는 사실성 위험 때문에 뒤로 미룬다.

---

## 원리 2 — 이름은 채널이다

- **원리**: 식별자의 자연어 표면 단서는 모델이 실제로 의존하는 정보 채널이다. 채널을 끊으면 의도 수준 이해가 붕괴한다.
- **왜**: 동작을 보존한 채 명명 채널만 억제(alpha-rename)하는 통제된 ablation에서 클래스 수준 정확도가 11pt(DeepSeek V3 87.7→76.7)에서 거의 29pt(GPT-4o 87.3→58.7)까지 무너진다. CodeCrash는 "LLMs substantially rely on surface-level NL cues from identifiers"라고 관측한다. 단, 하락폭은 코드베이스에 이미 좋은 이름이 얼마나 있느냐에 의존하며(E-N3, LiveCodeBench −8.20pp vs CRUXEval −2.38pp), 제거 실험이 곧 "좋은 이름을 새로 붙이면 같은 크기로 오른다"는 뜻은 아니다 — 대칭 가정은 근거 없음(추론, 미해결 질문 O-3).
- **근거 ID**: E-N1 [PRIMARY-2025+ · 2025-10] · E-N3 [PRIMARY-2025+ · 2025-04, NeurIPS 2025].
- **하네스에서의 귀결**: 명명은 Phase 1 진단의 1급 축(3에이전트 중 명명 진단가 전담)이며, 안전 리네임은 P2로 배치한다.

---

## 원리 3 — 테스트는 등가성 오라클이 아니다

- **원리**: 테스트 통과는 동작 보존의 증명이 아니다. 비등가 리팩터의 상당 비율이 테스트를 통과한다.
- **왜**: "test passing is an unreliable proxy for functional equivalence, as it fails to detect a significant fraction (≈ 21%) of non-equivalent refactorings"(HumanEval 20.72% · MBPP 21.65% · APPS 22.41%). 기능 테스트를 전부 통과하고도 구조 오라클에 실패하는 사례가 13.3%(64/483)다. 그래서 "테스트 초록"을 동작 보존의 근거로 보고하는 순간 근거 시트 §7-7과 충돌한다.
- **근거 ID**: E-A2 [PRIMARY-2025+ · 2026-02] · E-S2 [PRIMARY-2025+ · 2026-03].
- **하네스에서의 귀결**: Phase 4 재확인은 "테스트 통과=등가"라고 말하지 않고, 등가 증명 불가를 명시한 채 diff를 사람에게 제시(게이트 C). P4 구조 개입은 이 한계 때문에 사람 diff 리뷰를 필수로 건다.

---

## 원리 4 — 리네임은 도구가 하고 판단은 사람이 한다

- **원리**: 리네임의 실제 파일 변경은 LLM이 직접 편집하지 않고 AST/LSP 기반 신뢰된 리팩터링 API에 위임하며, 최종 결정자는 사람이다.
- **왜**: CoRenameAgent는 소스를 직접 쓰는 것이 "strictly prohibited"이고 IDE의 "trusted refactoring APIs"만 호출한다 — 잘못된 연산은 그냥 실패한다(safe by construction). 사람 피드백을 제거하면 정밀도가 약 4배 하락한다("developer supervision is not optional but essential"). 그리고 자동 리팩터링의 주된 실패는 논리 오류가 아니라 컴파일/참조 깨짐이다("Tangled refactorings are strongly associated with reduced compilability, while exhibiting no significant association with functional correctness").
- **근거 ID**: E-A5 [PRIMARY-2025+ · 2026-01] · E-A4 [PRIMARY-2025+ · 2026-05].
- **하네스에서의 귀결**: P2 리네임의 1급 센서는 테스트가 아니라 컴파일·타입체크 + 참조 완전성이며, 적용은 도구 위임 후 Phase 3 게이트 B에서 사람이 개별 승인한다.

---

## 원리 5 — 구조 개선의 효과는 추론이다

- **원리**: 구조를 리팩터하면 에이전트 성공률이 오른다는 강한 정량 델타는 근거 세트에 존재하지 않는다. 반면 구조 개입의 위험은 측정됐다.
- **왜**: LocAgent·RepoGraph·CGM·ARISE·SWE-Adept의 수치는 전부 **기존 코드를 파싱해 만든 툴 측 그래프/인덱스**의 효과이지 코드 본문 수정의 효과가 아니다(E-S1). 소스-측 ablation으로 격리한 1차 자료는 없다(미해결 질문 O-1). 그러므로 본문 구조 개선의 효과는 추론(inference)이지 측정(measurement)이 아니다. 반면 LLM 리팩터의 19~35%가 기능적으로 비등가이고(E-A1, 안전 재작성을 지시했음에도), 단순화조차 ≈26% 비등가율을 보인다(E-A3). ARISE는 `+4.7pp` end-to-end만 인용하며, `+32.8%`(RepoGraph) 등은 본문 근거로 쓰지 않는다.
- **근거 ID**: E-S1 [PRIMARY-2025+] · O-1 · E-A1/E-A3 [PRIMARY-2025+ · 2026-02].
- **하네스에서의 귀결**: 구조 리팩터(P4)는 기본 OFF·opt-in이며, 어떤 절대 수치도 약속하지 않는다. Phase 0에서 사용자가 명시적으로 켜야만 스코프에 들어온다.

---

## 원리 6 — 자기보고를 신뢰하지 않는다

- **원리**: 에이전트가 "고쳤습니다"라고 말한 것은 증거가 아니다. 실행해서 관측한 것만 증거다.
- **왜**: 환경 하드닝은 정확도를 희생하지 않고(83.2% vs 82.8%, p>0.5) exploit을 6.5%→0.8%로 억제한다 — 즉 판정은 에이전트 밖의 hidden recomputation과 functional test로 해야 한다("Task success is computed via hidden recomputation and functional tests outside the agent sandbox"). 게다가 "The 28% of exploits without explicit rationale would evade trace-based detection" — trace 감시만으로도 부족하다.
- **근거 ID**: E-M2 [PRIMARY-2025+ · 2026-05].
- **하네스에서의 귀결**: Phase 3·4의 판정 센서는 에이전트의 서술이 아니라 컴파일·타입체크·테스트의 실제 실행 관측이며, 관측이 불완전하면 UNVERIFIED로 남기고 게이트 C에서 사람에게 넘긴다.

---

## 원리 7 — 사람 가독성 ≠ 에이전트 가독성

- **원리**: 사람이 읽기 좋게 만드는 개선과 모델이 읽기 좋게 만드는 개선은 다르다. 이 하네스는 후자만 다룬다.
- **왜**: 들여쓰기·공백 포매팅은 LLM에 무익하다(자매 플러그인 cartography session-1 C3). 반대로 오도 주석은 사람은 흘려 읽지만 모델은 지름길로 삼아 오답으로 끌려간다 — 그리고 이는 CoT로도 방어되지 않는다(E-C1). 즉 사람 눈에 대수롭지 않은 결함이 모델에게는 능동적 오도가 될 수 있다.
- **근거 ID**: E-C1 [PRIMARY-2025+ · 2025-04, NeurIPS 2025] · cartography session-1 C3.
- **하네스에서의 귀결**: census와 개입 클래스에서 포매팅(들여쓰기·공백)은 대상에서 제외하고, 개입 우선순위는 모델의 오도·이해 채널(주석·명명)에 집중한다.

---

## 이 문서가 주장하지 않는 것 (정직성 경계)

- 구조 리팩터 → 에이전트 성공률 향상의 정량 수치(추론이며 미측정, O-1).
- "좋은 이름·주석을 추가"하면 제거 실험과 같은 크기로 오른다는 대칭 효과(O-3).
- 함수 라인 수 임계값·주석 밀도 목표치·0~100 단일 등급(근거 없음; 저장소 층 등급은 cartography 소유).
- 테스트 통과 = 동작 보존(≈21% 누락, E-A2).
