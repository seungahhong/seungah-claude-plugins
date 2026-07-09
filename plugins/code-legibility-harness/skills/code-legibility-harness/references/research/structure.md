# 구조(structure) 축 — 근거 dossier

> 층위: 코드 **본문**의 함수·모듈 granularity(응집·경계·추출). 저장소 층(의존 그래프·디렉토리·CI)은 자매 플러그인 `ai-readiness-cartography` 소유 — 침범 금지.
>
> **이 문서의 목적 절반은 과장을 막는 것이다.** 구조 축은 이 근거 세트에서 정량 델타가 가장 화려해 보이지만, 그 델타는 전부 **본문 수정이 아닌 툴 측 표현**의 효과다. 아래 경계선을 넘는 주장은 산출물 폐기 사유다.

---

## E-S1 · 강한 정량 델타는 전부 "툴 측 그래프"의 효과다 `[PRIMARY-2025+]` `CONFIRMED (3-0 ×7)`

기존 코드를 **파싱해 만든 스캐폴드/인덱스**(그래프·임베딩)가 에이전트 국소화·이슈 해결을 끌어올린다는 1차 자료:

| 시스템 | 출처 · tier | 관측치 |
|--------|------------|--------|
| LocAgent | arXiv:2503.09089 (ACL 2025) `[PRIMARY-2025+ · 2025-03]` | `"up to 92.7% accuracy on file-level localization"` · 다운스트림 이슈 해결 **+12% (Pass@10)** |
| RepoGraph | arXiv:2410.14684 (ICLR 2025; preprint 2024-10=배경) `[PRIMARY-2025+ · ICLR 2025]` | line-level def/ref 노드 + invoke/contain 엣지, k=1~2 ego-graph. `"average relative improvement of 32.8%"` |
| CGM | arXiv:2505.16901 `[PRIMARY-2025+ · 2025-05]` | 의미+구조 결합 → SWE-bench Lite **43.00%** (Qwen2.5-72B, open-weight 1위) |
| ARISE | arXiv:2605.03117 `[PRIMARY-2025+ · 2026-05]` | statement-level + data-flow 그래프, SWE-agent 동일 백본 ablation **17.3%→22.0% (+4.7pp)** |
| SWE-Adept | arXiv:2603.01327 `[PRIMARY-2025+ · 2026-03]` | 의존성 유도 DFS → `"improving the end-to-end resolve rate by up to 4.3%"` |

**함께 옮겨야 하는 caveat (평균의 함정):**
- RepoGraph의 `+32.8%`는 **약한 RAG 스캐폴드(+99.63%)가 끌어올린 평균**이다. 강한 에이전트에선 modest — **Agentless는 +8.56%**. 델타 크기는 기저 스캐폴드가 약할수록 크다.
- 🚫 **ARISE의 `Function R@1 0.43→0.60 / Line R@1 0.26→0.41` 인용 금지** — 이번 적대 검증에서 **REFUTED (1-2)**. ARISE는 **`+4.7pp` end-to-end만** 인용한다.

---

## 🚨 이 플러그인의 가장 중요한 정직성 경계선

> 위 5개 델타는 **모두 "기존 코드를 파싱해 만든 스캐폴드/인덱스 측 표현"의 효과다.** 어느 것도 **소스 본문을 수정**하지 않았다.
>
> **"함수 응집도·모듈 경계·추출 granularity를 소스에서 바꾸면 에이전트 국소화·수정 성공률이 N% 오른다"를 직접 측정한 1차 자료는 이 근거 세트에 없다.**
>
> 따라서 본문 구조 개선의 효과는 **추론(inference)이지 측정(measurement)이 아니다.** 이 플러그인은 그 격차를 **미해결 질문 O-1**로 정직히 표기한다 — "소스-측 ablation으로 격리한 1차 자료 부재". 어떤 산출물도 구조 개입에 성공률 수치를 붙여선 안 된다.

---

## E-S2 · 구조/아키텍처는 에이전트의 최대 실패면 `[PRIMARY-2025+ · 2026-03]` `보강근거`

출처: arXiv:2603.27745 (2026-03) — 23개 GPT/Claude/Gemini/Qwen 구성, 유지보수성 probe.

- 평균 해결 **36.2%**, 최고 구성도 **57.1%**. 난도 상승 시 붕괴: micro **53.5%** → multi-step **20.6%** (설계 실수가 누적).
- verbatim: `"The hardest pressures are architectural rather than local edits, especially dependency control (4.3%) and responsibility decomposition (15.2%)."` — 국소 편집이 아니라 **아키텍처 압력에서 가장 약하다.**
- verbatim: `"64/483 outcomes (13.3%) pass all functional tests yet fail the structural oracle"` — **테스트 통과는 유지보수성의 신뢰할 수 없는 프록시**(§7-7과 정합; "테스트 통과=동작 보존" 주장 금지).
- verbatim: `"agent-mode configurations under our harness raises average performance from 28.2% to 45.0%, it does not eliminate these core failures"` — 스캐폴드는 돕지만 **핵심 구조 결함을 제거하지 못한다.**

**설계 함의:** 의존성 통제 통과율이 **4.3%**다. 구조 개입을 **에이전트 자율에 맡기면 안 된다.** → 사람 게이트(게이트 B·C) + 도구 강제(컴파일·참조 완전성)로 감싼다.

---

## 왜 P4(구조 리팩터)가 기본 OFF·opt-in인가

개입 우선순위(근거 시트 §6)에서 구조는 **P4(최하위)**이며, Phase 0에서 사용자가 명시적으로 켜야만 활성화된다.

- **효과 = 추론.** 위 경계선대로 본문 구조 수정→성공률의 직접 측정치가 없다(O-1).
- **위험 = 측정된 최대치.** 같은 재작성 계열의 실측 위험은 확정적이다:
  - E-A1(arXiv:2602.15761, 2026-02): `"19-35% functionally non-equivalent refactorings"` — **안전 재작성을 명시 지시했음에도** 발생.
  - E-A2(동일): `"test passing is an unreliable proxy for functional equivalence, as it fails to detect a significant fraction (≈ 21%) of non-equivalent refactorings"`.
- 즉 P4는 **효과는 불확실(추론)한데 위험은 확실(측정)**한 유일한 개입 클래스다. 기대이익 기준으로 P1(위험 0·효과 확실)의 정반대에 위치하므로 마지막이자 opt-in이다.
- 켜더라도 1급 센서는 테스트만으로 부족(E-A2 ≈21% 누락) → **테스트+컴파일 + 사람 diff 리뷰**를 붙이고, "등가성은 증명 불가"임을 명시한다.

---

## 함수 라인 수 임계값 금지 (스캐너 규약)

- 🚫 `"N줄 초과 = 나쁨"` 류 **함수 라인 수 임계값을 점수·게이트로 사용하지 않는다.** 에이전트 정확도로 검증된 임계값이 없다 — 자매 플러그인 `ai-readiness-cartography` session-4 C8과 **동일 판정**.
- 대신 결정론 스캔(census)은 함수·모듈 **크기를 진단 정보(diagnostic)로만** 보고한다: "이 함수가 크다"는 사실을 P4 후보 탐색의 *신호*로 표면화할 뿐, 자동 판정·자동 개입 근거로 삼지 않는다. 실제 개입 여부는 사람 게이트가 결정한다.
- 구조 축은 **등급을 산출하지 않는다**(§7-9: 0~100 단일 등급 금지). 산출물은 census(인벤토리) + P4 후보 제안 + 승인 후 적용뿐이다.

---

## 관련 미해결 질문

- **O-1**: 본문 구조(함수 granularity·모듈 경계·디렉토리 배치)를 실제로 리팩터하면 — 외부 그래프 인덱스 대비 — 에이전트 성공률이 정량적으로 얼마나 오르는가? **소스-측 ablation으로 격리한 1차 자료 부재.** (구조 축 델타를 주장할 때 반드시 이 질문으로 귀속.)
- **O-2**: 정적 타입 애노테이션의 **독립** 효과 크기? 단독 변수로 분리한 근거 미확보.
