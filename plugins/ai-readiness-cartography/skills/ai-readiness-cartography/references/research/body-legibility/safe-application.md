# 안전 적용(safe application) 축 — 근거 dossier

> 이 문서는 코드 본문 층위 모드 **게이트 설계의 근거**다.
> 왜 승인 없이 파일을 쓰지 않는가(게이트 A/B/C), 왜 리네임의 1급 센서가 테스트가 아니라 컴파일인가,
> 왜 구조 리팩터가 기본 OFF·opt-in인가를 여기서 증명한다.
> 인용은 전부 정본 근거 시트 §4(E-A1~E-A7)에서 온다. 시트에 없는 수치·논문은 쓰지 않는다.

핵심 명제 한 줄: **"안전하게 바꿔라"는 지시만으로는 LLM이 동작을 보존하지 못하고, 테스트 통과로도 그것을 증명할 수 없다.** 따라서 개입은 최소 단위로 쪼개고, 클래스별 1급 센서를 실행으로 통과시키고, 사람 승인 게이트를 거친다.

---

## E-A1 · "안전 재작성"을 명시해도 19~35%가 기능적으로 비등가 `[PRIMARY-2025+ · 2026-02]` 핵심 안전근거

- 출처: arXiv:2602.15761 — 6개 LLM(CodeLlama·Codestral·StarChat2·Qwen2.5-Coder·Olmo-3·GPT-4o) × 3 데이터셋(HumanEval/MBPP/APPS) × 2 리팩터링 유형.
- verbatim: `"we find that LLMs show a non-trivial tendency to alter program semantics, producing 19-35% functionally non-equivalent refactorings... raising concerns regarding the trustworthiness of LLM-generated code refactorings."`
- 결정적 조건: **안전 재작성을 프롬프트에서 명시적으로 지시했음에도** 이 비율이 나왔다. 지시는 센서가 아니다.
- 게이트 함의: 구조 리팩터(C3)를 에이전트 자율에 맡길 수 없다. 사람 diff 리뷰가 최종 관문이어야 한다.

## E-A2 · "테스트 통과"는 등가성의 신뢰할 수 없는 프록시(≈21% 누락) `[PRIMARY-2025+ · 2026-02]` 핵심 안전근거

- 출처: arXiv:2602.15761
- verbatim: `"test passing is an unreliable proxy for functional equivalence, as it fails to detect a significant fraction (≈ 21%) of non-equivalent refactorings. Thus, the findings of this paper emphasize the need to move beyond predefined test suites and adopt stronger equivalence-checking techniques, such as differential fuzzing"`
- 데이터셋별 누락률: HumanEval **20.72%** · MBPP **21.65%** · APPS **22.41%**. 즉 비등가 리팩터 5개 중 1개가 기존 테스트를 **전부** 통과한다.
- 저자 결론 verbatim: `"we cannot rely solely on LLMs to correctly refactor code, nor can we rely exclusively on given test suites to assess correctness."`
- 게이트 함의: **"테스트 통과 = 동작 보존"을 주장하지 않는다.** 테스트는 필요조건이지 등가성 증명이 아니다. C3 제안에는 반드시 이 한계를 명시하고 사람 판단을 청한다.

## E-A3 · 위험은 코드 단위 복잡도에 비례 — 큰 함수 통째 재작성 금지 `[PRIMARY-2025+ · 2026-02]`

- 출처: arXiv:2602.15761
- verbatim: `"APPS has the highest percentage (32.09%) of non-equivalent refactorings, compared to MBPP (25.33%) and HumanEval (22.10%)."`
- 단순화(simplification)조차 최적화와 거의 같은 **≈26%** 비등가율: verbatim `"even seemingly less complex refactorings can introduce substantial risk of semantic deviation."`
- 게이트 함의: 복잡도가 높은 단위(APPS 32.09%)일수록 위험이 크다. **큰 함수를 통째로 재작성하지 않는다. 개입을 최소 단위로 분할**하고 단위마다 센서를 통과·확정한다.

## E-A4 · 자동 리팩터의 주된 실패는 논리 오류가 아니라 컴파일/참조 깨짐 `[PRIMARY-2025+ · 2026-05]` 핵심 안전근거

- 출처: arXiv:2605.22526
- verbatim: `"Tangled refactorings are strongly associated with reduced compilability, while exhibiting no significant association with functional correctness."`
- refactoring-aware refinement로 컴파일 가능성 `"from 19.34% to 38.33%"`, 미해결 이슈 `"2.79%"` 추가 해결.
- 게이트 함의(중요): **리네임(C2)의 1급 센서는 테스트가 아니라 컴파일/타입체크 + 참조 완전성이다.** 심볼 개명이 깨뜨리는 것은 대개 로직이 아니라 참조 해석·컴파일이며, 이는 테스트를 돌리기 전에 컴파일러/타입체커/LSP로 결정론적으로 잡힌다.

## E-A5 · 동작 보존은 신뢰된 리팩터링 API에 위임, 사람이 최종 결정자 `[PRIMARY-2025+ · 2026-01]` CONFIRMED (3-0) · 신뢰도 medium

- 출처: CoRenameAgent, arXiv:2601.00482
- verbatim: 이 에이전트는 IDE의 신뢰된 리팩터링 API로만 변경을 실행하고 `"strictly prohibited from directly writing or editing the source code"`. 잘못된 연산은 그냥 실패한다(safe by construction).
- LLM 제안 단독은 `"incomplete suggestions due to limited context"`, 순수 휴리스틱은 `"overwhelming number of false positives"` — 어느 쪽도 단독으로는 부족하다.
- ablation: 사람 피드백을 비활성화하면 정밀도가 **약 4배 하락** → verbatim `"developer supervision is not optional but essential"`.
- 게이트 함의: C2 리네임은 에이전트가 임의 텍스트로 편집하지 않고 **도구(LSP/AST 리네임)에 위임**해 참조를 원자적으로 갱신한다. 사람 승인(게이트 B)은 선택이 아니라 필수다.

## E-A6 · 실행 가능한 동작 보존 루프(test+compile)는 작동하되 전문가와 20~27% 갈린다 `[PRIMARY-2025+ · 2025-11]` 보강근거

- 출처: RefAgent, arXiv:2511.03153
- 수치: 리팩터 코드 **중앙값 90% 단위테스트 통과율**; 단일 에이전트 대비 통과율 중앙값 **+64.7%**, 컴파일 성공률 중앙값 **+40.1%**. → test+compile 자기성찰 루프가 실효가 있음을 보인다.
- 단, 사람 개발자 리팩터링과의 정렬은 **F1 중앙값 79.15%**(탐색기반 도구와는 72.7%). 즉 **약 20~27%의 결정은 전문가 판단과 갈린다.**
- 게이트 함의: 실행 센서는 위험을 크게 줄이지만 전문가 판단을 대체하지 못한다. 그 20~27%의 간극이 곧 **사람 승인 게이트의 존재 이유**다.

## E-A7 · 반복 리팩터는 재구조화→안정화로 수렴, 타깃 프롬프팅 효과는 modest `[PRIMARY-2025+ · 2026-02]`

- 출처: arXiv:2602.21833 — GPT-5.1 × Java 230 스니펫 × 5회 반복 × 3 프롬프트 전략.
- verbatim: `"iterative code refactoring exhibits an initial phase of restructuring followed by stabilization"`
- verbatim: `"explicit prompting toward specific readability factors slightly influences the refactoring dynamics"` — **특정 가독성 요인을 프롬프트로 밀어붙이는 효과는 제한적.**
- 게이트 함의: 무한 반복을 금지한다. **반복 횟수 상한을 두고 수렴(안정화)을 관측**한다. 수렴 후에도 개선이 정체되면 프롬프트 튜닝으로 더 짜내려 하지 말고 사람에게 에스컬레이트한다.

---

## 개입 클래스별 위험·센서 표

각 개입은 Phase 0에서 사용자가 켠 클래스 안에서만 적용한다(스코프 가드). 표의 "1급 센서"는 적용 전 **실행으로** 통과해야 하는 결정론적 관문이다.

| 클래스 | 예 | 동작 위험 | 1급 센서 | 2급 센서 | 자동 적용 |
|--------|-----|----------|----------|----------|----------|
| **C0** 주석 삭제 | 오도·stale 주석 제거 | 없음(주석은 실행되지 않음) | 사람 확인 | — | 금지(게이트 B) |
| **C1** 주석 추가/수정 | 계약·불변식 명시 | 없음(단 사실성 위험 ~20~45%) | 코드 대조 | document testing | 금지 |
| **C2** 리네임 | 심볼 개명 | 참조·컴파일 깨짐(E-A4) | **컴파일/타입체크 + 참조 완전성** | 테스트 | 금지 · 도구(LSP/AST) 강제 |
| **C3** 구조 리팩터 | 추출·이동·분할 | **높음: 19~35% 비등가(E-A1)** | 테스트+컴파일 | 사람 diff 리뷰 | **기본 OFF · opt-in** |

- **C1 사실성 위험 ~20~45%**: 생성 주석의 약 20%가 검증가능하게 부정확(E-C5, 배경 tier), 특화 파인튜닝 주석 수정도 35~45% 오답(E-C4). 그래서 코드 대조 + document testing으로 그라운딩하고 자동 적용하지 않는다.
- **C2**: 위험은 로직이 아니라 참조/컴파일이므로(E-A4) 1급 센서를 테스트가 아닌 **컴파일·타입체크 + 참조 완전성**으로 둔다. 에이전트가 직접 텍스트 편집하지 않고 도구에 위임한다(E-A5).
- **C3 (⚠️ 등가성 증명 불가)**: **테스트로 등가성을 증명할 수 없다(≈21% 누락, E-A2).** 테스트+컴파일이 모두 초록이어도 비등가일 수 있으므로, 이 클래스는 기본 OFF이고 opt-in 시에도 사람 diff 리뷰(게이트 B)를 최종 관문으로 강제하며 제안에 "등가성 미증명"을 명시한다.

정직성 경계(근거 시트 §3·§7): C3의 효과 크기("구조를 바꾸면 성공률 N% 오른다")를 **직접 측정한 1차 자료는 근거 세트에 없다.** 본문 구조 개선의 이익은 **추론(inference)이며 측정이 아니다** — O-1 미해결 질문. 반면 위험(19~35%)은 측정되었다. 이 비대칭이 C3를 마지막·opt-in으로 두는 이유다.

---

## 롤백 규약

1. **최소 단위 원칙**: 한 개입 = 한 개의 되돌릴 수 있는 변경(주석 한 덩이, 심볼 하나, 추출 하나). E-A3에 따라 큰 재작성을 하나의 개입으로 묶지 않는다.
2. **적용 전 센서 게이팅**: 클래스별 1급 센서를 적용 *전*에 통과시킨다. C2는 컴파일/타입체크·참조 완전성, C3는 테스트+컴파일. 센서를 자기보고로 대체하지 않고 실행 관측만 신뢰한다(§7-12).
3. **센서 실패 시 즉시 되돌리기 제안**: 적용 후 센서(컴파일/타입/테스트)가 깨지면 그 개입을 **즉시 롤백 제안**하고 다음 개입으로 넘어가지 않는다. 부분 적용 상태로 두지 않는다.
4. **반복 상한 + 수렴 관측**: E-A7에 따라 같은 표적을 무한 반복하지 않는다. 상한 내에서 안정화가 오지 않으면 프롬프트 튜닝 대신 사람에게 에스컬레이트한다.
5. **커밋 경계**: 어떤 개입도 이 하네스가 직접 커밋하지 않는다. 확정된 변경은 git-harness로 핸드오프한다(근본 계약).
