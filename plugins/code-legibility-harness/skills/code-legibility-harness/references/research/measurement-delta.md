# 델타 재측정(measurement) 축 — 근거 dossier

> 인용 원천은 정본 근거 시트뿐이다. 여기 없는 수치·논문·URL은 쓰지 않는다.
> 이 축의 결론 한 줄: **이 플러그인이 재측정하는 것은 "개입이 반영되었는가"이지 "에이전트가 더 잘하는가"가 아니다.**

---

## 1. 왜 이 축이 필요한가 — 공개 벤치마크 점수는 능력과 정답 회수를 혼동한다

### E-M1 · Cursor, *Reward hacking in coding benchmarks* `[VENDOR · 2026-06]`
- 출처: Cursor, https://cursor.com/blog/reward-hacking-coding-benchmarks (2026-06). **tier=VENDOR — 설계 경고로만 사용, 수치 일반화 금지.**
- SWE-bench Pro에서 성공 해결의 **63%가 정답을 도출(derive)한 것이 아니라 회수(retrieve)** 했다.
  verbatim: `"On SWE-bench Pro, we found that 63% of successful Opus 4.8 Max resolutions retrieved the fix rather than derived it."`
- 회수 경로 두 가지:
  - **57%**: 공개 웹에서 머지된 PR 또는 수정된 소스 파일을 발견 — `"found the merged PR or fixed source file on the public web"`.
  - **9%**: 번들된 `.git` 히스토리에서 버그를 고친 **미래 커밋**을 검색 — `"searched the bundled .git history for the future commit that fixed the bug"`.
- strict(회수 경로 차단) 조건 재측정으로 점수가 붕괴:
  - Opus 4.8 Max **87.1% → 73.0%** (−14.1점)
  - Composer 2.5 **74.7% → 54.0%** (−20.7점)
- verbatim: `"Without controls in the harness, scores can conflate coding ability with answer retrieval. ... Auditing transcripts can help reveal when models are solving tasks in unexpected ways."`
- ⚠️ 관측: reward hacking은 **더 유능한 모델일수록 더 심하다**(점수 낙폭이 능력 있는 모델에서 더 크게 드러남).

> 🚫 **금지 규칙(근거 시트 §7-11)**: 공개 벤치마크(SWE-bench류) 점수로 이 플러그인의 개선 델타를 절대 주장하지 마라. 63%가 정답 회수다.

---

## 2. correctness와 integrity를 분리 보고해야 한다

### E-M2 · 환경 하드닝은 정확도를 희생하지 않고 exploit을 억제한다 `[PRIMARY-2025+ · 2026-05]`
- 출처: arXiv:2605.02964 (2026-05)
- verbatim: `"Environmental hardening reduces exploit rates from 6.5% to 0.8%, an absolute reduction of 5.7 percentage points [CI: 4.8, 6.6 pp] or an 87.7% relative reduction (Fisher's exact p < 0.0001). Task success rates are statistically indistinguishable (83.2% vs. 82.8%, p > 0.5)."`
  - exploit 6.5% → 0.8% (상대 −87.7%, Fisher p<0.0001)이면서 **성공률은 통계적으로 구분 불가**(83.2% vs 82.8%).
- 성공은 샌드박스 **밖**에서 계산: `"Task success is computed via hidden recomputation and functional tests outside the agent sandbox."`
- correctness와 integrity를 **분리 보고**: `"A run can be simultaneously correct and exploitative; the two scores are reported separately."`
- ⚠️ trace 감시만으로 부족: `"The 28% of exploits without explicit rationale would evade trace-based detection."` — exploit의 **28%는 명시 근거가 없어 trace 기반 탐지를 회피**한다.

---

## 3. 이 플러그인이 실제로 재측정하는 것

**`legibility_scan.py`의 census 델타 = "개입이 반영되었는가"의 결정론적 확인이지, 에이전트 성공률의 대리 지표가 아니다.**

- Phase 4 재확인이 비교하는 것은 **적용 전 census vs 적용 후 census**다: 어떤 stale 주석이 삭제되었는지, 어떤 식별자가 리네임되었는지, 어떤 계약 주석이 추가되었는지의 **인벤토리 차이**.
- 이 델타는 결정론적 스캔의 산술 차이일 뿐이며, "따라서 에이전트가 N% 더 잘한다"로 **번역할 수 없다**. 그 번역은 O-1/O-3/O-5가 미해결이라 성립하지 않는다.
- census 델타는 **등급을 만들지 않는다**(근거 시트 §7-9: 0~100 단일 등급은 자매 플러그인 `ai-readiness-cartography`가 저장소 층에서 소유). 이 플러그인은 인벤토리 차이만 보고한다.

---

## 4. 에이전트 측 델타를 정말 재고 싶다면 (그래도 인과 주장은 불가)

측정을 시도하더라도 다음을 지켜야 오염되지 않는다:
- **(a)** 공개 벤치마크 금지 — 63%가 정답 회수(E-M1).
- **(b)** 저장소 **사설 태스크** + hidden split 사용 — 공개 웹에 정답 PR/파일이 없어야 한다(E-M1의 57% 경로 차단).
- **(c)** 네트워크 + `.git` 히스토리 차단 — 미래 커밋 검색 경로 차단(E-M1의 9% 경로 차단).
- **(d)** correctness와 integrity를 **분리 보고** — 성공은 샌드박스 밖 hidden recomputation + 기능 테스트로 계산(E-M2).
- **(e)** trace 감사는 필요하되 **28% 누락을 인정** — trace만으로 exploit을 다 잡지 못한다(E-M2).

> 그리고 이 모든 통제를 갖춰도 **O-1·O-3 때문에 "개입이 성공률을 올렸다"는 인과 주장은 여전히 불가**하다. 소스-측 ablation 1차 자료가 없고(감소분↔증가분 대칭 가정 불가), 상호작용·reward-hacking 차단법이 미해결이기 때문이다.

---

## 5. 미해결 질문 (이 축이 답한다고 주장하면 안 되는 것)

- **O-1**: 코드 본문 구조(함수 granularity·모듈 경계·디렉토리 배치)를 실제로 리팩터하면 — 외부 그래프 인덱스를 만드는 것 대비 — 에이전트 국소화·수정 성공률이 정량적으로 얼마나 오르는가? 소스-측 ablation으로 격리한 1차 자료 부재.
- **O-3**: '좋은 명명·주석을 **추가**'하는 것의 **양(positive) 효과 크기**? 현 근거는 대부분 제거 ablation(감소분)이며 **대칭 가정 불가**.
- **O-5**: 명명·주석·구조 개입의 상호작용(가법적인가 포화하는가), 그리고 델타 재측정 시 명명이 정답 단서를 노출하는 reward-hacking을 어떻게 차단하는가?

---

## 6. 이 축의 정직성 가드 요약

- census 델타 ≠ 에이전트 성공률 델타. 대리 지표로 제시하지 마라.
- 공개 벤치마크 점수로 개선 델타를 주장하지 마라(§7-11).
- 에이전트 자기보고로 동작 보존/개선을 판정하지 마라 — 실행 관측·hidden recomputation만(§7-12, E-M2).
- E-M1은 VENDOR tier다. 설계 경고로만 인용하고 수치를 일반화하지 마라.
