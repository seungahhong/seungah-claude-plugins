# 명명(naming) 축 근거 dossier

> 층위: **코드 본문** 층 — 변수명·함수명·클래스/컴포넌트명. (저장소 층은 자매 플러그인 `ai-readiness-cartography` 소유. 침범 금지.)
> 인용 원천: 정본 근거 시트 §1(E-N1~E-N6). 여기 없는 수치·논문은 쓰지 않는다.
> 개입 위치: 우선순위 **P2**(무의미·오도 식별자 안전 리네임). 1급 센서는 테스트가 아니라 컴파일·타입체크 + 참조 완전성.

---

## E-N1 · 의미 단서 제거는 의도 수준 이해를 붕괴시킨다 `[PRIMARY-2025+ · 2025-10]` `CONFIRMED (3-0)`

- 출처: *When Names Disappear: Revealing What LLMs Actually Understand About Code*, arXiv:2510.03178 (2025-10)
- verbatim: `"class-level accuracy collapses after obfuscation, with drops ranging from 11 points (DeepSeek V3: 87.7 → 76.7) to almost 29 points (GPT-4o: 87.3 → 58.7)."`
- 방법: ClassEval-Obf — 동작을 보존한 채 명명 채널만 억제(alpha-rename 등). **통제된 perturbation ablation이므로 인과 주장이 정당**하다.
- 함의: 식별자는 LLM의 클래스 수준 의도 이해에서 장식이 아니라 **1차 채널**이다. 무의미 식별자를 유의미하게 바꾸는 것은 이 채널을 복구하는 방향의 개입이다(단 상향 델타의 대칭성은 아래 E-N3 참조).

## E-N2 · 실행 예측(구조만으로 풀려야 할 과제)조차 명명 제거로 하락한다 `[PRIMARY-2025+ · 2025-10]` `CONFIRMED (3-0)`

- 출처: arXiv:2510.03178
- verbatim: `"even execution-oriented tasks—ostensibly dependent only on program semantics—show non-trivial drops after obfuscation"`
- 수치: DeepSeek V3 90.0→69.3 (**−20.7pp**), Llama 4 Maverick 80.2→56.4 (**−23.8pp**). 조건에 따라 −7~9pp도 존재.
- 함의: 명명은 "사람 편의"가 아니라 모델의 실제 계산 경로에 개입한다. 원리적으로 이름과 무관해야 할 실행 예측조차 이름을 잃으면 무너진다 → 명명 품질은 코드 본문 층에서 다룰 실질 결함이지 미관 이슈가 아니다.

## E-N3 · REN(무의미 이름 리네이밍) 하락폭은 기존 명명 단서가 풍부할수록 크다 `[PRIMARY-2025+ · 2025-04, NeurIPS 2025]` `CONFIRMED (3-0)`

- 출처: *CodeCrash*, arXiv:2504.14119 (NeurIPS 2025) — 17개 모델·1,279문항
- verbatim: `"LLMs substantially rely on surface-level NL cues from identifiers to understand code"`
- 수치: LiveCodeBench 평균 **−8.20pp**(Claude-3.5-Sonnet −16.77pp). **CRUXEval에서는 −2.38pp에 불과** — 원래 의미 있는 함수명이 없는 벤치이기 때문.
- ⚠️ **효과 크기는 코드베이스에 이미 좋은 이름이 얼마나 있느냐에 의존한다.** LCB(이름 단서 풍부) vs CRUXEval(이름 단서 희박)의 −8.20 vs −2.38 격차가 그 증거다.
- ⚠️ **제거 ablation이므로 상향 델타는 대칭이 아니다(O-3)**: 이 실험들은 전부 "이미 있던 좋은 이름을 없애면 얼마나 떨어지나"를 잰다. "나쁜 이름을 좋게 바꾸면 같은 크기로 오른다"는 **대칭 가정은 근거 없음(추론)**이다. 이 dossier의 어떤 수치도 리네임 상향 효과의 크기 주장으로 재사용하지 마라 → 미해결 질문 **O-3**.

## E-N4 · 좋은 함수명 하나가 구현을 복원할 만큼의 의미를 운반한다 — 그러나 나쁜 이름도 메워서 맞춘다 `[PRIMARY-2025+ · 2025-03]` `보강근거`

- 출처: arXiv:2503.12207 (2025-03)
- verbatim(운반력): `"These results suggest that the combination of the student-provided function name along with the question author provided parameters and assumptions was sufficient for the LLM to accurately \"guess\" the correct code."`
- ⚠️ **반대 방향 관측(반드시 병기)**: `"count_strings is correct in that it describes the action being performed but fails to provide the necessary context of what is being counted... Such good guesswork on the part of the LLM was not limited to this question"` — LLM은 **부정확·불완전한 이름도 메워서 맞춰버린다**(false positive).
- 🚫 **설계 함의(중요)**: 따라서 **LLM이 코드를 이해했는지 여부를 명명 품질의 오라클로 쓰면 안 된다.** 나쁜 이름 `count_strings`도 통과하기 때문이다. 명명 판정은 "LLM이 맞췄나?"가 아니라 **이름↔본문 대조(구조적 검사)**로 한다(넣지 말 것 §7-6과 동일 판정).

## E-N5 · "최대 70%"는 리네이밍 효과가 아니다 — 오귀속 금지 `[PRIMARY-2025+ · 2025-05]` `귀속 주의`

- 출처: arXiv:2505.10443 (2025-05) — 5개 의미보존 변형(변수 리네이밍·비교 미러링·if-else 스왑·for→while·루프 언롤링)
- verbatim: `"LLMs often change their output predictions when code is mutated while preserving semantics, with performance drops reaching up to 70%"`
- 🚫🚫 **오귀속 금지(강조)**: "최대 70%"는 **루프 언롤링(구조 변형)**에서 나온 값이다. 리네이밍은 일부 모델에서 오히려 정확도를 **올리기도** 한다(단 예측을 뒤집음). **이 수치를 명명 근거로 인용하지 마라.** 명명 축의 정량 근거는 E-N1(11~29pt)·E-N2(−20.7/−23.8pp)·E-N3(−8.20pp)이지 70%가 아니다.

## E-N6 · 현행 벤치마크는 명명 패턴 암기를 보상한다 — 델타 측정 시 reward-hacking 차단 `[PRIMARY-2025+ · 2025-10]` `CONFIRMED (3-0)` · 신뢰도 medium

- 출처: arXiv:2510.03178
- verbatim: `"current benchmarks reward memorization of naming patterns rather than genuine semantic reasoning"`
- ⚠️ ClassEval-Obf의 "더 신뢰할 수 있는 기반"은 **저자 자평**, 2026-07 기준 독립 재현 미확인.
- 🚫 **함의(집행)**: 리네임 개입의 개선 델타를 잴 때 **명명이 정답 단서를 노출**하는 reward-hacking 경로를 차단해야 한다. 공개 벤치마크(SWE-bench류) 점수로 명명 개선 델타를 주장하지 마라(§7-11: 63%가 정답 회수, E-M1). 재측정은 결정론 센서(참조 완전성·컴파일)의 델타로만.

---

## 배경 정합 · 미해결 질문

- 이 축의 정량 근거는 **거의 전부 제거(obfuscation/REN) ablation**이다. 즉 "얼마나 나빠지나"는 측정되었고 "얼마나 좋아지나"는 **O-3(미해결)**이다. 문서 어디에서도 "리네임하면 성공률 N% 상승"을 주장하지 않는다 — 근거 없음(추론).
- 정적 타입 애노테이션의 독립 효과(**O-2**)와 명명·주석·구조 개입의 상호작용(**O-5**)도 이 근거 세트로는 답할 수 없다.

---

## 결정론 스캐너 vs LLM 판단 — 무엇을 무엇으로 잡나

명명 판정의 오라클은 LLM 이해가 아니다(E-N4). 결정론으로 잡히는 것은 결정론이 먼저 잡고, 남는 것만 LLM이 **제안**한다(적용은 게이트 후).

| 판정 항목 | 담당 | 근거·비고 |
|-----------|------|-----------|
| 무의미/단문자 식별자(`a`, `tmp`, `data2`, 시퀀스 `x1 x2`) | **결정론 스캐너** | census 인벤토리로 목록화. 도메인 판단 불요 |
| predicate 이름(`is_/has_/can_`)인데 반환이 bool 아님 | **결정론 스캐너** | 이름↔본문 대조(구조적 검사). 타입/AST로 확정 |
| `get_*` 인데 `return` 없음(부수효과만) | **결정론 스캐너** | 반환문 존재 여부는 AST로 결정 |
| 리네임 후 참조/컴파일/타입 깨짐 여부 | **결정론 센서(1급)** | E-A4: 리네임 실패의 주원인은 논리 오류가 아니라 컴파일/참조 깨짐 |
| 도메인 의미 적합성(`count_strings`가 *무엇을* 세는지) | **LLM 제안** | E-N4 반대 방향: 이름이 동작은 맞아도 문맥 부족일 수 있음. LLM 이해 성공을 오라클로 쓰지 말 것 |
| 약어·도메인 축약 해석(`ctx`, `usr`, `qty`가 적절/오도인지) | **LLM 제안** | 코드베이스 관례 대조 필요. 확정 아닌 제안, 게이트 B에서 사람 승인 |
| 오도 이름(동작과 어긋나는 이름) 식별 | **LLM 제안 + 사람 확인** | 자동 적용 금지. E-A5: 사람 감독은 선택이 아니라 필수 |

> 규칙: 결정론이 확정할 수 있는 것에 LLM 판단을 끼워 넣지 않는다(오검증 방지). LLM은 도메인 의미 적합성처럼 결정론이 못 잡는 곳에서만 **제안**하며, 리네임의 안전은 컴파일·타입체크·참조 완전성으로 검증한다(테스트 통과 = 동작 보존 주장 금지, §7-7).
