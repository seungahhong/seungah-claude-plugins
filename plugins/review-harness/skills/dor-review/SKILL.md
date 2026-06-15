---
name: dor-review
description: "기획 산출물(PRD/유저스토리/인수조건/Jira 티켓/요구사항 문서)을 '착수 게이트(Definition of Ready)' 관점에서 리뷰하고, 무엇이 모호하거나 빠졌는지 구체적으로 짚어 기획에 되돌리는 스킬. FE/BE 착수 전, QA 막바지 재작업 전에 모호성과 누락을 잡는 것이 목적이다. 사용자가 'DoR', 'Definition of Ready', '착수 준비', '착수 게이트', '인수조건 리뷰', '기획 리뷰', 'PRD 점검', '유저스토리 검토', '요구사항 모호성', '스토리 준비됐나', 'INVEST', 'Given-When-Then', 'GWT', '인수조건 검수', '요구사항 검토' 등을 언급할 때 사용한다."
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# DoR Review — 착수 게이트(Definition of Ready) 리뷰

기획 산출물(PRD, 유저스토리, 인수조건, Jira 티켓, 요구사항 문서)을 **착수(Definition of Ready)** 관점에서 리뷰한다. FE/BE가 코드를 시작하기 전, QA가 막바지에 받기 전에 모호성과 누락을 잡아 다운스트림 재작업을 줄이는 것이 목적이다. 이 스킬은 코드가 아니라 **상류 산출물**을 핸드오프 시점에 게이트로 검수한다.

## 핵심 원칙

**원칙 1 — 모호한 요구사항은 곧 다운스트림 재작업이다.** 명확성은 착수 전에 강제한다. "빠르게", "쉽게", "적절히" 같은 표현은 구현자와 QA에게 서로 다른 해석을 남기고, 그 차이는 QA 막바지나 릴리스 후에 재작업으로 청구된다. 불완전·은닉 요구사항은 요구공학에서 가장 많이 지목되는 문제이며(NaPiRE 설문 228명 중 109명=48%, Méndez Fernández et al. 2017 [GOLD]), 회피 가능한 재작업은 프로젝트 노력의 상당 부분을 차지한다(Boehm & Basili 2001 [GOLD]). 모호성을 발견하면 구체적 재작성안을 제시하고, 의도를 알 수 없으면 지어내지 말고 기획에 되돌릴 질문으로 만든다.

**원칙 2 — 인수조건은 테스트 가능해야 하고 정상경로만으로는 부족하다.** 모든 인수조건은 Given-When-Then으로 표현 가능해야 하며, 정상경로(happy path)뿐 아니라 엣지/에러/빈 상태/권한 경로를 포함해야 한다. 음성 경로(negative path)가 없는 인수조건은 미완성으로 본다.

**원칙 3 — 자동 탐지(LLM)는 사람 검토를 보조하지, 그 자체로 게이트를 통과시키지 않는다.** LLM·NLP는 유저스토리 품질 결함과 모호성을 탐지하는 데 도움이 되지만(in-context 예시로 모호 요구사항 분류 성능이 0-shot 대비 평균 20.2% 향상 — Bashir/Ferrari et al., ICSME 2025 [GOLD]), 한계가 분명하다. 최신 LLM은 '이상적 템플릿'에서 벗어났다는 이유로 전문가가 acceptable로 본 스토리를 과대탐지하고 환각·불안정성을 보이며(GPT-5; 룰 기반 AQUSA가 정밀도 0.61로 false positive가 더 적음 — Perkusich et al. 2025 [SILVER]), '무엇이 결함인가'는 프로젝트·도메인·이해관계자 해석에 따라 달라지는 맥락 의존 개념이다(Unterbusch & Vogelsang, ICSE-NIER 2026 [SILVER]). 따라서 LLM은 초안·후보 발굴 도구로 쓰고, 도메인·맥락 판정은 사람이 한다(assist-not-replace).

## 실행 절차

### Phase 0: 입력 수집 및 모드 선택

리뷰 대상 산출물을 식별하고 어떤 깊이로 검수할지 정한다.

1. **대상 식별** — 사용자가 제시한 입력을 분류한다.
   - 로컬 문서: PRD/요구사항 마크다운, `*.feature`, 스펙 파일 등 (`Read`, `Glob`로 수집)
   - Jira 티켓/유저스토리: 본문에 붙여넣은 텍스트 또는 티켓 키
   - 인수조건 단편: 메시지에 직접 붙여넣은 스토리/AC

2. **리뷰 모드 선택** — 사용자에게 확인한다. 답변 전에는 다음 Phase로 진행하지 않는다.

   ```text
   [DoR Review] 리뷰 모드를 선택해주세요.

   1. 단일 스토리 — 유저스토리/티켓 1건을 DoR + INVEST + GWT로 정밀 검수 (기본)
   2. 문서 전체 — PRD/요구사항 문서 전체를 DoR 게이트로 점검
   3. 인수조건만 — AC의 Given-When-Then 완결성과 모호성만 빠르게 점검
   ```

3. **컨텍스트 보강(선택)** — 스토리가 참조하는 자료(API 계약, Figma 링크, 용어집)가 저장소에 있으면 함께 읽어 일관성을 본다. 단, 산출물에 없는 의도를 추론으로 채우지 않는다.

### Phase 1: DoR 게이트 점검

산출물이 착수 가능한 상태인지 항목별로 PASS/FAIL을 매긴다. 각 FAIL에는 **위반한 라인/문장을 인용**한다.

| DoR 항목 | 통과 기준 |
| --- | --- |
| 표준 포맷 | `As a / I want / so that` (또는 동등) 구조로 사용자·목적이 명시됨 |
| 인수조건 측정 가능 | AC가 Given-When-Then으로 표현 가능하고 관찰 가능한 결과를 명시 |
| 비즈니스 규칙 | 계산·제약·우선순위 등 규칙이 문서화됨 |
| 엣지/에러/권한 | 빈 상태, 실패 응답, 권한 없음 경로가 기술됨 |
| 디자인 참조 | Figma/디자인 링크가 있고 대상 화면과 매칭됨 |
| 의존성 식별 | 참조하는 API 계약·타 팀·선행 작업이 명시됨 |
| 크기·추정 | 1스프린트 내로 분할 가능하고 추정이 있음 |
| QA 시나리오 | 테스트 시나리오가 식별됨(Three Amigos 관점) |
| 공유된 이해 | 열린 질문(open question)이 0건 |

판정 규칙:

- 하나라도 FAIL이면 종합 판정은 **착수 보류**로 시작한다.
- "디자인 참조" 또는 "의존성 식별" FAIL은 병목 (a)(c) 직결 신호이므로 우선 표기한다.

### Phase 2: INVEST 스코어카드

유저스토리 품질을 INVEST 6축으로 채점한다. 각 축 **0~2점**(0=없음/위반, 1=부분, 2=충족), 총 12점 만점.

| 축 | 의미 | 0점 예 | 2점 예 |
| --- | --- | --- | --- |
| **I**ndependent | 독립적으로 착수·릴리스 가능 | 다른 미정 스토리에 강결합 | 선행 의존이 명시·해소됨 |
| **N**egotiable | 구현 방식이 강제되지 않음 | 해법까지 못박음 | 무엇/왜 중심, 어떻게는 협상 가능 |
| **V**aluable | 사용자/비즈니스 가치가 분명 | 가치 진술 없음 | so that 절에 가치 명시 |
| **E**stimable | 추정 가능 | 정보 부족으로 추정 불가 | 규모 추정에 합의됨 |
| **S**mall | 스프린트 내 완료 가능 | 에픽 규모 | 분할된 작은 단위 |
| **T**estable | 테스트 가능한 AC 존재 | AC 없음/검증 불가 | GWT로 검증 가능 |

**차단 규칙(Blocking):**

- `Testable = 0` 또는 `Independent = 0`이면 총점과 무관하게 **착수 차단**으로 판정한다. 테스트할 수 없는 스토리는 완료를 정의할 수 없고, 독립적이지 않은 스토리는 착수 자체가 다른 미정에 묶인다.
- 그 외 총점 가이드: 0~6 차단 / 7~9 보완 후 착수 / 10~12 착수 가능. 단 점수는 신호이며, 차단 규칙과 Phase 1 FAIL이 우선한다.

### Phase 3: 인수조건 Given-When-Then 완결성

각 인수조건을 Given-When-Then으로 매핑하고, 경로 커버리지를 점검한다.

1. **GWT 매핑** — AC를 `Given <전제> / When <행동> / Then <관찰 가능한 결과>`로 재구성한다. 재구성이 불가능하면 그 AC는 테스트 불가로 표기한다.
2. **경로 커버리지** — 다음 경로가 누락되지 않았는지 확인한다.

   | 경로 | 점검 |
   | --- | --- |
   | 정상(happy) | 기대 입력 → 기대 결과 |
   | 엣지(edge) | 경계값, 최대/최소, 동시성, 중복 제출 |
   | 에러(error) | API 실패, 검증 실패, 타임아웃 시 사용자 피드백 |
   | 빈 상태(empty) | 데이터 0건일 때 화면/문구 |
   | 권한(authz) | 비로그인·권한 없음·만료 상태의 처리 |

3. **음성 경로 요구** — 정상경로만 있는 AC는 미완성으로 본다. 빠진 경로마다 확인 필요 질문을 생성한다(예: 결제 API가 타임아웃되면 사용자에게 무엇을 보여주는가?).

### Phase 4: 모호성 린트

문장 단위로 약한 표현을 탐지하고 구체적 재작성안을 제시한다. 의도를 알 수 없으면 재작성하지 말고 질문으로 돌린다.

- **약한 단어**: "빠르게", "쉽게", "적절히", "등등", "해야 함", "유연하게", "최적화", "사용자 친화적"
- **대명사 모호**: "그것", "해당", "이 값"이 무엇을 가리키는지 불명확
- **정량자 없는 주장**: "많은", "대부분", "충분히" 처럼 기준 수치가 없는 표현

검색 보조(로컬 문서일 때):

```bash
grep -rniE "빠르게|쉽게|적절히|유연하게|사용자 친화|등등|최적화|충분히|대부분|해야 ?함" --include="*.md" --include="*.feature" <대상경로>
```

각 발견 항목은 Before(모호) → After(명확) 형태로 재작성안을 적는다. 단, 수치를 임의로 지어내지 않는다. 기준이 필요하면 "기획이 임계값을 지정해야 함"으로 표기한다.

### Phase 5: 의존성 / 계약 참조 점검 (병목 (a) 예방)

이 스토리가 착수되려면 필요한 외부 참조가 명시됐는지 본다. 미명시는 FE가 BE 계약을 기다리며 멈추는 병목 (a)로 이어진다.

| 점검 | 통과 기준 |
| --- | --- |
| API 계약 참조 | 호출할 엔드포인트/스키마(OpenAPI 등)가 합의·링크됨. 미합의면 Contract-First(선합의 → mock 병렬) 권고 |
| 디자인 링크 | 대상 화면의 Figma 노드가 링크되고 상태(빈/에러)별 시안 존재 |
| 타 팀 의존성 | 선행/병행 작업과 담당, 완료 기준이 명시됨 |
| 용어 일관성 | 도메인 용어가 저장소 `GLOSSARY.md`/`NAMING_CONVENTIONS.md`와 충돌하지 않음 |

저장소에 용어집이 있으면 대조한다:

```bash
find . -maxdepth 3 \( -iname "GLOSSARY.md" -o -iname "NAMING_CONVENTIONS.md" \)
```

### Phase 6: 결과 보고

아래 템플릿으로 통합 보고한다. 점수·PASS/FAIL을 표로 제시하고, 마지막에 기획으로 되돌릴 질문 목록을 둔다.

```markdown
# DoR Review 결과

## 대상
- 모드: 단일 스토리 / 문서 전체 / 인수조건만
- 산출물: <티켓 키 또는 파일 경로>

## 1. DoR 게이트

| DoR 항목 | 결과 | 위반/근거 (인용) |
| --- | --- | --- |
| 표준 포맷 | ✅/❌ | "..." |
| 인수조건 측정 가능 | ✅/❌ | "..." |
| 엣지/에러/권한 | ❌ | "정상 결제만 기술, 실패 경로 없음" |
| 디자인 참조 | ❌ | Figma 링크 없음 |
| 의존성 식별 | ❌ | 결제 API 계약 미참조 |

## 2. INVEST 스코어카드

| 축 | 점수(0~2) | 근거 |
| --- | --- | --- |
| Independent | 1 | ... |
| Negotiable | 2 | ... |
| Valuable | 2 | ... |
| Estimable | 1 | ... |
| Small | 2 | ... |
| Testable | 0 | AC가 검증 불가 → 차단 |
| **총점** | **8 / 12** | Testable=0 → **착수 차단** |

## 3. 인수조건 GWT 완결성

| AC | Given-When-Then | 정상 | 엣지 | 에러 | 빈 화면 | 권한 |
| --- | --- | --- | --- | --- | --- | --- |
| AC1 | Given .. When .. Then .. | ✅ | ⚠️ | ❌ | ❌ | ❌ |

## 4. 모호성 린트

| 위치(라인) | Before (모호) | After (명확) |
| --- | --- | --- |
| L12 | "빠르게 로딩" | "초기 콘텐츠 표시(임계값은 기획 지정 필요)" |
| L20 | "적절히 처리" | "결제 실패 시 토스트 노출 + 재시도 버튼" |

## 5. 확인 필요 (기획에 되돌릴 질문)

- ❓ 결제 API 타임아웃 시 사용자에게 무엇을 보여주는가?
- ❓ 권한 없는 사용자가 진입하면 차단 화면인가, 리다이렉트인가?
- ❓ 목록 0건일 때 빈 상태 문구/CTA가 있는가?

## 6. 종합 판정

| 항목 | 결과 |
| --- | --- |
| DoR 게이트 | ✅ PASS / ⚠️ 보완 후 착수 / ❌ 착수 보류 |
| INVEST | N / 12 (차단축 여부) |
| GWT 완결성 | 음성 경로 누락 N건 |
| 모호성 | 발견 N건 |
| **착수 가능** | **YES / 보완 후 / NO** |
```

## 체크리스트

- [ ] 표준 포맷(`As a / I want / so that`)을 갖췄다
- [ ] 모든 인수조건이 Given-When-Then으로 표현 가능하다
- [ ] 정상경로 외 엣지/에러/빈 상태/권한 경로가 기술됐다
- [ ] 비즈니스 규칙(계산·제약·우선순위)이 문서화됐다
- [ ] 디자인/Figma 링크가 있고 상태별 시안이 있다
- [ ] 참조 API 계약이 합의·링크됐다 (없으면 Contract-First 권고)
- [ ] 타 팀/선행 의존성이 담당·완료 기준과 함께 식별됐다
- [ ] 1스프린트 단위로 분할·추정됐다
- [ ] QA 테스트 시나리오가 식별됐다(Three Amigos)
- [ ] 열린 질문이 0건이다
- [ ] INVEST의 Testable·Independent가 모두 1점 이상이다
- [ ] 약한 단어·모호 대명사·정량자 없는 주장에 대한 재작성안 또는 질문이 달렸다

## Honesty Guardrail

이 스킬이 출력에 정량 수치를 인용할 때는 반드시 (1) 출처 등급 [GOLD/SILVER/BRONZE], (2) 출처명/링크, (3) 가능하면 반대증거를 함께 표기한다.

- 등급 정의: **GOLD** = 피어리뷰·정부·DORA 등 대규모 연구 / **SILVER** = 방법론이 공개된 업계 리포트(벤더 자기보고 포함) / **BRONZE** = 벤더 블로그·일화.
- **개선 N%를 약속하지 않는다.** 검증된 소수 수치만 인용하고, 목표 수치는 조직이 직접 baseline을 측정해 정한다(baseline-before-target). 이 스킬은 "DoR를 도입하면 재작업 N% 감소" 같은 약속을 하지 않는다.
- 다음 수치는 출처 추적 실패 또는 반증되었으므로 **사실로 인용 금지**(신화로만 언급): IBM '결함비용 1→100배', Crosstalk '결함비용의 64%가 요구·설계'. '늦게 고치면 100배' 류의 정확한 지연 배수도 약속하지 않는다 — 171개 프로젝트 분석에서 일관된 지연효과가 확인되지 않았다(Menzies et al. 2017 [GOLD]).
- Standish CHAOS의 '불완전 요구사항이 실패요인 12.3%'는 수치 자체는 1994 원본에 실재하나 정의·방법론이 강하게 비판받았으므로(Eveleens & Verhoef, IEEE Software 2010 — "misleading, one-sided … meaningless") **단정 인용을 피하고 '논쟁적 통념'으로만** 표기한다. 본문 주장은 NaPiRE(2017)·Boehm & Basili(2001)로 떠받친다.
- LLM/NLP로 유저스토리 품질 결함을 탐지할 수 있다는 것은 근거가 있으나(룰 기반 AQUSA: 재현율 97.9% / 정밀도 84.8% — Lucassen et al. RE 2016 [GOLD]; 단 AQUSA는 NLP 룰 기반이며 LLM이 아니고, 정밀도는 데이터셋에 의존해 다른 산업 데이터셋에선 0.61로 보고됨 — Perkusich et al. 2025 [SILVER]), '>90% 정밀도'를 일반값으로 인용하지 않는다. 최신 LLM은 멀쩡한 산출물을 과대탐지하는 경향이 있으므로(GPT-5의 환각·불안정성), 이 스킬의 자동 탐지는 사람의 검토를 대체하지 않고 보조한다.

## 참고 / 근거

수치를 인용할 때는 효과크기가 아니라 정성근거로만 쓴다(Honesty Guardrail). 표본·자기보고·preprint 한계를 함께 적는다.

**2025+ 근거 (LLM 시대의 요구사항·유저스토리 품질)**

- LLM in-context learning(10-shot)이 모호 요구사항 분류 성능을 0-shot 대비 평균 20.2% 향상시키고 설명 품질이 전문가 평가 3.84/5에 이르나, 도메인 특화 용어 이해 부족이 한계로 지적됨(철도 산업 3개 데이터셋) — Bashir, Ferrari et al., "Requirements Ambiguity Detection and Explanation with LLMs: An Industrial Study", ICSME 2025 (Industry Track) [GOLD]. <https://conf.researchr.org/details/icsme-2025/icsme-2025-industry-track/8/Requirements-Ambiguity-Detection-and-Explanation-with-LLMs-An-Industrial-Study>
- 룰 기반 AQUSA와 GPT-5·GPT-5-mini·GPT-4 비교(산업 3개 데이터셋·유저스토리 182건): GPT-5-mini가 최고 재현율(0.81)·F1(0.62), AQUSA가 최고 정밀도(0.61)·현저히 적은 false positive. GPT-5는 환각·불안정성, GPT-4는 과소탐지 → 구조검증(룰)+경량 LLM 맥락보강의 'Dual-gate' 권고 — Perkusich et al., "Evaluating the Quality of User Stories: An Extended Comparative Study of Multiple LLMs and Rule-Based Tools", Springer, 2025 [SILVER, 표본 182·소중규모]. DOI 10.1007/978-3-032-22375-3_10
- QUS 8개 품질 기준으로 GPT-4o·GPT-4-Turbo·GPT-3.5-Turbo의 유저스토리 품질 평가 역량 비교(합성 스토리 960건, 대학원생 69명 채점 대조): GPT-4o/4-Turbo가 구문·화용에 우수, GPT-3.5-Turbo는 맥락이 풍부할수록 저하 — 모델·기준별 편차가 커 LLM 자동평가의 일관성 한계 — "Evaluating user story quality with LLMs: a comparative study", Journal of Intelligent Information Systems, vol.63 pp.1423–1451, 2025 [GOLD, 대학원생 평가·합성 스토리]. DOI 10.1007/s10844-025-00939-3
- 분석가가 쓴 유저스토리가 GPT-4 산출물보다 언어 명확성에서 덜 모호하며, LLM은 초안 도구로 두고 사람이 맥락·기술 감수를 제공하는 시너지를 권고(IT 컨설팅사 현장) — "Exploring the Use of LLMs for Requirements Specification in an IT Consulting Company", arXiv:2507.19113, 2025 [SILVER, preprint·단일 기업].
- '무엇이 결함인가'는 프로젝트·도메인·이해관계자 해석에 따라 달라지는 맥락 의존 개념이며, 사람이 검증한 소수 예시(20건)를 되먹이는 Human-LLM 협업이 표준 few-shot·fine-tuned BERT를 능가(Mercedes-Benz 요구사항 1,266건) — Unterbusch & Vogelsang et al., "Context-Adaptive Requirements Defect Prediction through Human-LLM Collaboration", arXiv:2601.01952, ICSE-NIER 2026 [SILVER, preprint·NIER·단일 기업].

**고전 기반 (정성·방향 참고, 효과크기 아님)**

- 불완전·은닉 요구사항이 요구공학(RE)에서 가장 많이 지목된 문제(응답자 228명 중 109명=48%) — Méndez Fernández et al., "Naming the Pain in Requirements Engineering", Empirical Software Engineering, vol.22(5) pp.2298–2338, **2017** [GOLD]. DOI 10.1007/s10664-016-9451-7
- 회피 가능한 재작업이 프로젝트 노력의 약 40~50%를 차지하며, 재작업의 약 80%가 결함의 약 20%에서 비롯됨 — Boehm & Basili, "Software Defect Reduction Top 10 List", IEEE Computer 34(1):135–137, 2001 [GOLD]. DOI 10.1109/2.962984
- 결함을 늦게 고칠수록 비싸진다는 통설의 정확한 배수는 일반화할 수 없음(171개 프로젝트에서 일관된 지연효과 미확인) — Menzies et al., "Are Delayed Issues Harder to Resolve?", Empirical Software Engineering, 2017 [GOLD]. DOI 10.1007/s10664-016-9469-x
- 룰 기반 NLP 도구 AQUSA가 유저스토리 품질결함을 탐지(QUS 프레임워크, 18개 회사 1,023개 스토리, 재현율 97.9%/정밀도 84.8%) — Lucassen et al., "Improving agile requirements: the Quality User Story framework and tool", Requirements Engineering 21(3):383–403, 2016 [GOLD]. ※ AQUSA는 LLM이 아니라 NLP 룰 기반이며, 정밀도는 데이터셋 의존(다른 데이터셋 0.61).
- 초기(2023) ChatGPT의 유저스토리 품질 평가가 사람 평가와 대체로 일치하나 불안정해 'best of three'를 제안하고 비전문가의 미가공 출력 신뢰 위험을 경고 — Ronanki et al., "ChatGPT as a tool for User Story Quality Evaluation: Trustworthy Out of the Box?", arXiv:2306.12132, 2023 [SILVER, 보조·구버전 모델].
- Standish CHAOS의 '불완전 요구사항이 challenged 요인 12.3%'는 정의·방법론 논쟁이 커 단정 인용하지 않음(논쟁적 통념) — Eveleens & Verhoef, IEEE Software 27(1):30–36, 2010 비판 참조.
- DoR/INVEST/Given-When-Then 정의 — Bill Wake, "INVEST in Good Stories, and SMART Tasks"(2003); North, "Introducing BDD"(2006). [BRONZE, 정의·관행 출처]
