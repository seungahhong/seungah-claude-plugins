# Research — 근거 dossier (design-principle-harness)

이 폴더는 플러그인의 채점·개선 결정을 뒷받침하는 **1차 근거**다. `/deep-research`로 **8개 렌즈 sweep → 4개 적대 검증(인용 무결성·수치 정확도·human→LLM 외삽·점수화 긴장) → 2개 synthesis**로 2023~2026 소스를 검증했다(에이전트 14·live arXiv 38건 확인·조작 0건).

- **[evidence-dossier.md](evidence-dossier.md)** — 정본(Tier A/B). 8렌즈별 소스 표(provenance 태그·subjects·수치) + Signal→Score 결정 마스터 표 + 정직성 가드레일 16 + 미검증/삭제 수치 목록.
- **[rubric-design.md](rubric-design.md)** — 근거 기반 루브릭·staged 개선 설계 문서(synthesis 산출).
- **[semantic-a11y-test-dossier.md](semantic-a11y-test-dossier.md)** — **Tier C 정본(v0.2.0)**. 시맨틱 HTML·ARIA/WCAG·테스트 설명·accessible 셀렉터 5렌즈 + 적대 감사(VERIFIED/DOWNGRADED/DROPPED/UNVERIFIABLE·인용 제목·수치 교정) + score.py Tier C(C1/C2) 매핑. `/deep-research` 5렌즈 plain-text 워크플로(10 조사/검증 에이전트).
- **[semantic-a11y-test-raw-findings.md](semantic-a11y-test-raw-findings.md)** — 위 dossier의 원자료(10 에이전트 조사·검증 원문·투명성용).
- **[ai-accessibility-dossier.md](ai-accessibility-dossier.md)** — **Track B 정본(v0.4.0)**. AI 접근성 6지표(패턴 일관성·빌드 피드백·모듈 경계·의존 방향 강제·독립 실행·에이전트 가이드) + 적대 감사. 지배 원칙: build-enforces-docs-explain·intervention≠correlation·tool-index≠code-structure·유일 측정 레버=독립 oracle. `/deep-research` 6렌즈·13에이전트(synthesis 성공).
- **[ai-accessibility-raw-findings.md](ai-accessibility-raw-findings.md)** — 위 dossier의 원자료(13 에이전트 조사·검증 원문).

## 이 dossier가 플러그인에 강제한 정직성 교정 (반드시 준수)

deep-research는 **초기 설계의 과장을 실제로 교정했다**. 아래는 그 결과이며 SKILL·README·score.py·루브릭 전반에 반영돼 있다:

1. **명명 효과에 단일 수치를 만들지 않는다 (가드레일 #14).** "구조보존 난독화 -11~-29pt"는 *특정* 연구(arXiv:2510.03178, **intent/summarization** 과제·GPT-4o 채점)의 값일 뿐이다. LLM 대상 식별자 리네임 효과는 **부호가 불안정**(모델별 +14.4 ~ -31.9, arXiv:2505.10443)하고 **과제 의존적**(알고리즘 실행 코드엔 ≈-3pp). **사람 대상** 근거(서술적·일관 명명이 이해를 돕는다)는 견고하나, **믿을 만한 교차 신호는 '오도/불일치/stale 명명·주석'의 해악뿐**이다. 구조/제어흐름 변경이 LLM엔 식별자 변경보다 **훨씬 더** 해롭다.

2. **개입(intervention) 연구는 없다 (§0.4·가드레일 #10).** *어떤 점수를 올리면 같은 저장소에서 같은 에이전트의 성공률이 오른다*는 연구는 **존재하지 않는다**. 모든 LLM 근거는 **perturbation**(코드를 망가뜨리고 점수 하락 관측)이나 **production**(AI가 뱉는 것 측정)이지 개입이 아니다. → 모든 구조/설계 하위 점수는 **측정된 예측자가 아니라 추론된 휴리스틱**이다. 점수 델타를 리팩터의 성과로 귀속하려면 같은 저장소의 **재측정 행위 probe**가 있어야 한다.

3. **두 축 등급 (§0.2).** 신뢰도는 **측정 신뢰도**(결정론적으로 잴 수 있나)와 **타당도 신뢰도**(그게 AI 가독성을 실제로 예측하나)로 분리된다. 후자는 **모든 구조/설계 신호에서 '외삽'**이다. 경고 사례: Maintainability Index·SonarQube TD-Ratio는 정밀하게 계산되지만(측정 High) 원시 LoC baseline보다 **못한**(타당도 ≈0) 예측력이다. **측정 정밀도가 타당도를 함의하게 두지 말 것.**

4. **결합도·순환은 가독성 신호가 아니라 변경 위험(blast-radius) 신호 (Lens 3·8 재등급).** "acyclic → 더 나은 LLM 내비게이션"은 **미측정 외삽**이다(순환 인접 클래스가 변경 잦음은 **사람** 연구). LocAgent(92.7%)·RepoGraph(+32.8%)의 이득을 **순환 제거나 본문 편집의 효과로 귀속하면 안 된다**(그건 툴 측 그래프 인덱스 효과). RepoGraph는 acyclicity를 주장하지 않는다.

5. **총점은 '안전 기여' 인증이 아니다 (Lens 8 가중 교정).** 에이전트 기여 성공의 **가장 강한 신호는 실행 가능(재현 실패 테스트 +26.4pp)·의존성 무결성(manifest↔lockfile·hallucinated 패키지 없음)**인데, 이는 **이 플러그인의 범위 밖**(코드 본문 설계 품질이 아님)이다. 따라서 이 하네스의 점수는 **설계 부채 hotspot 지도**이지 "에이전트가 안전하게 기여할 수 있다"는 인증이 아니다.

6. **점수를 닫힌 루프로 최적화하지 않는다 (Goodhart·Lens 5).** 설계 스멜 오라클을 목표로 최적화한 에이전트는 **순-음성**(SmellBench: 31 해결하며 140 유발·63% 오탐; SpecBench: 가시 97%·held-out 0%). 개선 에이전트는 "점수가 올랐나"가 아니라 **사람 승인 + held-out 행위 검증**으로 평가한다. 볼륨(LOC↔스멜 ρ=0.94) 가점 금지.

7. **LLM은 가독성 오라클로 부적합 (Lens 7).** CoReEval에서 LLM-사람 가독성 상관 0.00~0.25(2018 정적 모델 0.31에 짐). 점수는 **결정론**이고 LLM 판단은 advisory. 판단 불가피하면 이분/임계 체크로 분해.

8. **테스트 통과 ≠ 동작 보존 (Lens 6).** 리팩터 코드의 실측 커버리지 ~22%·LLM 자기리뷰가 자기 silent drift의 ~1/3 승인. AST/LSP 리네임도 리플렉션·직렬화·DI-by-name·공개 API를 놓친다. 커버리지 없으면 **UNVERIFIED**(≠safe).

## Tier C(v0.2.0) 정직성 교정 (semantic-a11y-test-dossier)

9. **시맨틱 마크업·a11y·테스트 설명은 report-only·총점 미포함.** 셋 다 직접 개입 근거가 없다 — 시맨틱 HTML 이득은 **모델 역량 조건부**(WorkArena L1: 강한 모델 full HTML +11~17.5pp / 약한 모델 a11y-tree 우세; arXiv:2604.01535·2605.29397 **저자 동일군**이라 독립 삼각검증 아님)·landmark-vs-divsoup 격리 연구 부재; **ARIA 볼륨은 오히려 오류와 상관**(WebAIM·방향성만·고정 배수 금지·상관≠인과·bad ARIA worse than none·WCAG ~25~40%만 자동검사); **올바른 테스트 설명의 LLM 이해 이득은 미미하고 오도 설명만 해악**(arXiv:2404.03114 비대칭)·tests-as-oracle overfitting(2511.16858)·오라클=actual 인코딩(2410.21136). → 존재/볼륨 가점 금지·**자동 ARIA/alt/어서션 생성 금지**·오도/모호/native-대체가능만 개선.

## 주석 '삭제 우선' vs '왜 주석 추가'의 화해 (v0.3.0)

10. **주석은 삭제 우선이 원칙이되, 코드로 파생 불가한 '왜/맥락'은 opt-in 추가한다 — 근거 정합.** 통제 연구(arXiv:2404.03114)의 핵심은 *비대칭*이다: 올바른/누락 문서는 LLM 이해에 **유의한 이득 없음**, 오도 문서만 **측정 가능한 해악**. 이 null 결과는 *모델이 이미 읽을 수 있는* 코드(HumanEval 짧은 함수)에 대한 것이다. 반면 침묵 예외·매직 넘버·정규식·비자명 우회 같은 지점은 **의도·외부 제약·우회 이유가 코드에 아예 없다** — 여기에 다는 '왜' 주석은 *중복 what*이 아니라 **코드로 얻을 수 없는 정보를 보충**한다(별개 사례). 그래서: (a) 추가는 **why-not-what**·**opt-in**·**점수 무관(볼륨 가점 없음)**, (b) **사람이 정확성 검증**(오도 주석이 유일하게 실증된 해악이므로 정확성 게이트가 핵심·자동 생성 주석 사실 단정 금지), (c) 이득 프레이밍은 *사람 이해 + 비파생 맥락*이지 "LLM 성공률 +N%"가 아니다(개입 근거 없음). 삭제(오도 제거)는 여전히 위험 0의 기본, 추가는 신중한 보완.

## 소스 신뢰도 주의

- 결정적 LLM 효과크기 다수가 **2026 단일팀·미재현 preprint**(SmellBench·SpecBench·RHB·SWE-Refactor·RepoMirage 등) — 크기는 **잠정**.
- **삭제된 수치(인용 금지)**: "자동 주석 20~45% 부정확"(무출처)·"클론 71% 유익"(검색 혼동)·"SonarQube AUC 50.9%"(무출처)·순환 "76.3%/94%"(위키). dossier §Open questions 참조.
- **Tier C 삭제/교정 수치**: "~10× DOM reduction"(citation 미근거·drop)·WebAIM 고정 배수(연도별 불안정·방향성만)·arXiv:2504.04372 "81%"→**78%**·제목 교정(2504.04372·2511.16858). semantic-a11y-test-dossier §적대적 감사 참조.
