# test-layering-harness

인수조건(AC, Given-When-Then)을 **방법론(Smoke/Sanity/Regression/nightly) × 계층(Unit/Integration/E2E)** 택소노미로 계층별 테스트 스위트로 계획하고, **계획→개별→최종 3단계 인간 승인 게이트**로 테스트를 하나씩 순차 생성·적용·확정하는 도메인 무관 인터랙티브 **단일 스킬** 독립 플러그인.

사용자용 개요·사용법은 [README.md](README.md), 원리는 [principles](skills/test-layering-harness/references/test-layering-principles.md), 근거는 [research dossier](skills/test-layering-harness/references/research/test-strategy-research.md) 참조.

## Structure

```
test-layering-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 원칙 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·경계
├── skills/test-layering-harness/
│   ├── SKILL.md                     # 오케스트레이터(Phase 0 초기문의 → 1 적응형 구성 → 2 축 카드 조합 라우팅 계획+게이트A → 3 개별 적용+게이트B → 4 반영+게이트C)
│   └── references/
│       ├── test-layering-principles.md   # 방법론×계층 매트릭스·AC 분해(§4)·축 카드 조합 라우팅(§4.5)·오라클 가드·실체화(§3.5)·3 프리셋·감지 신호·anti-pattern·경계
│       ├── matrix/                        # 방법론·계층 축 카드 7개 (12개 셀로 미리 물질화하지 않고 라우팅 시 조합)
│       │   ├── _index.md                  # 축 직교성·라우팅 절차·**스코프 가드**·조합 강도 lookup·정직성 불변식
│       │   ├── methodology-{smoke,sanity,regression,nightly}.md  # 방법론 카드 4개 (suite 멤버십·실체화·CI배치·오라클 기대)
│       │   └── layer-{unit,integration,e2e}.md                   # 계층 카드 3개 (scope+size 판정·AC 포함/제외·오라클 프로필)
│       └── research/
│           ├── test-strategy-research.md  # 2025+ 상위 근거 dossier(A~G, 신뢰도·folklore·모순 표기)
│           └── matrix-criteria-2025.md    # 조합 라우팅 기준 근거 dossier(직교성·계층/방법론 판정·조합 강도 lookup·소스 인덱스)
└── evals/
    ├── evals.json                   # 수용 평가(핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json            # 트리거 경계(should/should-not, 인접 하네스 reciprocal 가드)
```

## 5-Phase · 3-Gate 요약

| Phase | 내용 | 게이트 |
|-------|------|--------|
| 0 초기 문의 | AC **3지선다 명시 프롬프트**((a)붙여넣기 (b)파일·링크 경로 (c)없음→저장소 후보 채굴; 채굴은 사용자 명시 선택·곧장 건너뛰기 금지) · 개발 환경(스킵 가능·미입력 시 현재 경로·부재 러너 보고) | — |
| 1 적응형 구성 | 저장소 감지 → 3 프리셋 중 근거와 함께 추천 → **방법론 스위트(Smoke/Sanity/Regression/nightly)·계층(Unit/Integration/E2E) 체크박스 다중선택**(프리셋 기본체크·러너 부재 계층 '추가 필요' 명시) + **조합 강도 lookup**(STRONG/WEAK/DEGENERATE) 안내 → 스코프 고정 | (스코프 확정) |
| 2 AC→축 카드 조합 계획 | 각 AC를 **7개 축 카드 조합**으로 라우팅(Step0 스코프 확정→슬라이스→**선택된 계층만**→**선택된 방법론만**→조합 강도 lookup으로 상황 선택→계획행)·결합 오라클 프로필·계획표(계층·방법론·조합강도 열)·**스코프 밖은 '추가 안 함' 표기** | **게이트 A: 계획 승인** |
| 3 개별 적용 | 오라클 오검증·draft 제시·적용·실행 그라운딩 (순차) **+ durable 스위트 태그 물리 부여·분리 스크립트 추가·셀렉터 실행 분리 검증**(sanity는 무-태그 변경-스코프 선택) | **게이트 B: 개별 적용 승인** |
| 4 반영 | 적용 요약·전체 실행·확정 | **게이트 C: 최종 반영 재확인** |

## Conventions (핵심 불변식)

- **3개 게이트를 건너뛰지 않는다** — 계획 승인 없이 개별 적용 없음, 개별 승인 없이 파일 쓰기 없음, 최종 승인 없이 반영 없음.
- **비율% 하드코딩 금지** — 70/20/10은 folklore(Fowler 본인 상대화). 무게중심은 프리셋으로 제안, 비율은 안 박음.
- **오라클 강도가 최대 리스크** — LLM은 구현(실제 동작)을 굳혀 버그를 초록으로 은폐. 기대(AC) 기준 오검증 + 실행 그라운딩 + flaky baseline 선결 + 스모크/동어반복 어서션 금지.
- **AC ≠ E2E** — AC 한 건은 여러 tier로 분해. E2E는 핵심 여정 소수로 절제(ice-cream-cone 방지).
- **축 카드 = 두 축(12셀 미리 물질화 안 함)** — `matrix/`에 방법론 카드 4개 + 계층 카드 3개(7개)를 두고 **라우팅 시점에 조합**한다. 조합은 **다중 멤버십**(한 테스트가 여러 방법론 suite 소속 가능). 계층=durable 속성, 방법론=selection/tag(sanity=transient). AC는 `matrix/_index.md` §2 절차로 조합 라우팅한다.
- **스코프 가드(핵심 불변식)** — 테스트는 **사용자가 Phase 1에서 선택한 방법론·계층 안에서만** 추가한다. 스코프 밖은 임의 추가 금지 — "추가 안 함" 표기 후 확장 문의(3게이트와 동급 불변식).
- **배치·mock 규약(계층 카드 §5)** — unit/integration은 테스트 대상(컴포넌트/유틸) 파일이 있는 **바로 그 폴더에 `__test__/`를 무조건 만들어**(없으면 생성) `*.test.*`로 둔다. **⚠️ `__test__/` 강제는 조건부가 아니다(3게이트·스코프 가드와 동급 불변식) — 저장소에 이미 다른 배치 관습(`__tests__` 복수·`test/`·bare `*.test.ts`)이 있어도 대체하지 않고 항상 `__test__/`에 둔다.** 작성 전 경로가 `.../__test__/…`인지 검사(아니면 거부·교정)·작성 후 경로 확인을 게이트 B에서 강제한다. 외부 API는 **실제 응답을 캡처한 mock(fixture)**로 double한다(live 호출 금지·결정론). E2E는 Phase 1에서 **테스트 경로를 초기에 문의**해 그 경로에 여정 스펙을 둔다(E2E는 `__test__/` 강제 대상 아님). nightly full-suite도 캡처 mock로 결정론 실행(cross-browser/real-device는 실제·API는 mock).
- **조합 강도 정직성** — Sanity 전 조합·Nightly×Unit·Smoke×Unit은 WEAK/DEGENERATE(ISTQB상 sanity=smoke 동의어, unit은 게이트 전량 실행)이므로 있는 척 채우지 않고 스코프 내 STRONG 조합으로 라우팅한다.
- **nightly는 방법론 아님** — CI-stage/스케줄 지연 축(ISTQB/ISO에 nightly test type 없음). **prioritization은 CI 비용을 못 줄임**(latency만, 정의상(재정렬=총실행량 불변)).
- **정직성** — smoke=sanity ISTQB 동의어 caveat 병기, 근거 없는 효과 수치 인용 금지, 신뢰도(HIGH/MED/LOW)·모순·folklore 표기 계승.
- **적응형 추천** — 저장소 감지로 프리셋 추천 후 사용자 확정(고정 강제 아님).
- **CI 배치 원리** — tier는 파이프라인 뒤로 갈수록 넓어짐(Google presubmit/postsubmit·Fowler DeploymentPipeline). 선택·배치 > 우선순위. unknown 커밋엔 전체 폴백.
- **커밋 직접 안 함** — 최종 반영은 유지·정리까지, 커밋/PR은 git-harness로 핸드오프 제안만.
- 단일 스킬 플러그인이므로 에이전트 팀(agents/)을 두지 않는다 — 인터랙티브 오케스트레이터 본성에 충실.
- **경계**: 리스크 기반 오라클·자가치유·트리아지 QA(qa-agent-harness), 백엔드 실행기반 test-generator(backend-harness), AC↔테스트 커버리지 읽기전용 검수(review-harness/test-coverage-review), FE 흐름 내 TDD(frontend-harness), 실행 명세 작성(spec-driven-development), 커밋/PR(git-harness)은 범위 밖.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-14 | `__test__/` 무조건 강제 (v0.4.1) | 라이브 사용에서 **간헐적으로 `__test__/` 폴더 없이 소스 폴더에 바로 테스트가 추가되는 편차**가 관찰됨(사용자 보고). 원인 = (1) 규칙이 Phase 3 긴 문단에 조건부로 묻혀 있고(별도 강제 스텝 아님), (2) "저장소에 이미 co-location 관습이 감지되면 그 관습을 따른다"는 **예외 경로**가 escape hatch로 작동. 사용자 결정("항상 `__test__/` 강제")대로 **예외 제거 + 검증 스텝 승격** — layer-unit/integration §5를 "무조건 강제(다른 관습 감지돼도 대체 않고 항상 `__test__/`)"로 재작성하고 작성 전 경로 검사(`.../__test__/…` 아니면 거부·교정)·작성 후 경로 확인을 명문화, SKILL Phase 3 항목 2에 **배치 강제 검사 (a)작성 전 (b)작성 시 mkdir (c)작성 후 확인** 3스텝 신설, 정직성 체크리스트에 '배치 강제' 항목 추가, CLAUDE.md Conventions·evals placement-mock assertion을 무조건 강제로 갱신. 러너 config가 특정 폴더로만 매칭 제한하면 관습 교체가 아니라 testMatch/include 조정을 게이트 B에서 제안('확인 필요'). E2E는 별도 경로라 `__test__/` 강제 대상 아님. 배치·mock·오라클·스코프 가드 계승. |
| 2026-07-07 | 배치·mock 규약 + E2E 경로 초기 문의 (v0.4.0) | 사용자 요청으로 계층/방법론 카드에 **테스트 배치·mock 규약**을 명문화 — (1) **unit/integration**은 테스트 대상(컴포넌트/유틸) 파일이 있는 폴더에 `__test__/`를 만들고 `*.test.*` 접미사로 두며(러너 기본 glob이 폴더명 무관하게 매칭; `__tests__` 복수 요구 러너는 '확인 필요'), 외부 API는 **실제 응답을 캡처한 mock(fixture)로 double**(live 호출 금지·결정론), (2) **E2E**는 Phase 1에서 계층 선택 시 **테스트 경로를 초기에 문의**(별도 러너·디렉토리 관습)해 Phase 3 스펙 위치로 사용, (3) **nightly** full-suite도 캡처 mock로 결정론 실행(cross-browser/real-device는 실제·API는 mock). layer-unit/integration §5 신설(배치&mock)·layer-e2e §5 신설(경로 규약)·methodology-nightly §3 mock 규약 추가, SKILL Phase 1(E2E 경로 문의)·Phase 3(배치·mock 규약) 배선, plugin CLAUDE.md Conventions·evals assertion 추가. 스코프 가드·조합 라우팅·인용 교정 계승. |
| 2026-07-06 | 12셀 → 7 축 카드 + 스코프 가드 (v0.3.0) | 사용자 요청("12개 셀 구조 말고 각 방법론별/계층별 카드로, 필요 시점에 상황 맞는 테스트 선택 추가, 단 사용자가 선택한 것 안에서만")으로 **12개 교집합 셀 파일 → 7개 축 카드로 재구성** — `matrix/`에 방법론 카드 4개(`methodology-{smoke,sanity,regression,nightly}.md`) + 계층 카드 3개(`layer-{unit,integration,e2e}.md`). 12개 셀로 미리 물질화하지 않고 **라우팅 시점에 두 축을 조합**(직교성 finding에 더 충실). `_index.md` 재작성: **스코프 가드(§1)**·조합 라우팅 절차(§2)·조합 강도 lookup(§3). **핵심 신규 불변식 = 스코프 가드**: 테스트는 사용자가 Phase 1에서 선택한 방법론·계층 안에서만 추가(밖은 '추가 안 함' 표기+확장 문의, 3게이트와 동급). SKILL Phase 1(선택=구속 스코프)·Phase 2(Step0 스코프 확정·선택된 계층/방법론만·조합 선택)·Phase 3(스코프 재확인) 배선, principles §4.5·§3 포인터·§8 anti-pattern 갱신. 인용은 2번째 검증에서 교정한 형태 계승(2509.10279=Targeted Test Selection·2308.13129=Parallel Batch Testing·2507.17542=AssertFlip 인접·2510.16433=Fuzzing MED). |
| 2026-07-05 | 플러그인 신설 (v0.1.0) | test-layering-harness(AC→방법론×계층 택소노미 테스트 계획·3게이트 순차 적용). deep-research(plain-text fan-out 5각도 적대 검증, 내장 deep-research schema 즉사 회피)의 2025+ 근거로 설계 — 방법론 스코프·트리거·CI 배치(ISTQB·Fowler·CircleCI·Google), 계층 비율 folklore 정직성(Fowler·Dodds·web.dev), 방법론×계층 매트릭스(Google presubmit/postsubmit·Fowler DeploymentPipeline), AC→tier 분해(GWT→AAA), LLM 생성 오라클 강도 최대 리스크(arXiv:2410.21136·2601.05542·2504.07244·2601.08998), flaky systemic 클러스터·선택>우선순위 CI 비용(arXiv:2504.16777·Meta). 적응형 3 프리셋(Trophy-lean/Google-pipeline/Contract-honeycomb)·비율 미하드코딩·3 승인 게이트·오라클 오검증+실행 그라운딩. 측정·제안·게이트만·자동 커밋 없음. |
| 2026-07-05 | Phase 0 개선 | 라이브 실행(seungahhong.github.io)에서 드러난 편차(실행자가 사용자 문의 생략 후 곧장 저장소 후보 채굴로 진행) 수정 — **Phase 0 AC 입력을 3지선다 명시 프롬프트로 못박음**((a)붙여넣기 (b)파일·링크 경로 (c)없음→저장소 후보 채굴; 채굴(c)은 묵시적 기본값이 아니라 사용자가 명시적으로 고른 선택, 최초 요청에 AC 인라인이면 재질문 금지). 개발 환경 항목도 부재 러너 보고를 명시(Phase 1 프리셋·tier 선택 반영). evals 초기문의 assertion 2건으로 분리(ac-3choice·env-skippable). |
| 2026-07-05 | Phase 1 개선 | **방법론×계층 체크박스 다중선택 동선 추가** — 프리셋 추천 뒤 Smoke/Sanity/Regression/nightly 방법론 스위트와 Unit/Integration/E2E 계층을 각각 `AskUserQuestion` multiSelect(체크박스)로 제시(프리셋 기준 기본체크, 사용자 가감), 러너 부재 계층은 '추가 필요' 명시, smoke=sanity ISTQB 동의어 caveat 병기, 선택된 스위트×계층만 Phase 2 계획 스코프로 고정. evals에 methodology-tier/multiselect assertion 추가. (실행계획 표시→승인 게이트는 이미 Phase 2 게이트 A로 존재.) |
| 2026-07-06 | 방법론×계층 12셀 카드 (v0.2.0) | 사용자 요청("각 방법론×계층마다 따로 .md·명확한 기준으로 AC 분해·2025+ 공식근거")으로 **12개 교집합 셀 카드 신설** — `references/matrix/`에 `_index.md`(축 직교성·AC 라우팅 5단계 절차·셀 강도 지도·카드 템플릿·정직성 불변식) + 12개 셀(smoke/sanity/regression/nightly × unit/integration/e2e), 각 셀에 AC 포함/제외 체크리스트·오라클 프로필·실체화·근거. deep-research(8각도 fan-out WebSearch/WebFetch → 3렌즈 적대 감사 → 합성, plain-text·schema 미사용)로 2025+ 공식표준/논문 근거화 → `references/research/matrix-criteria-2025.md`. **핵심 정직성 소득**: ① 계층⊥방법론 직교(ISO/IEC/IEEE 29119-1:2022 §4.4.6 regression=design/execution choice)이므로 셀=교집합·다중 멤버십(4번째 유형 아님) ② **nightly는 방법론이 아니라 CI-stage/스케줄 축**(ISTQB/ISO에 test type 없음) ③ ISTQB상 **sanity≡smoke 동의어** → Sanity 3셀 DEGENERATE, Nightly×Unit 빈 셀 → 정직히 비움 ④ **prioritization은 CI 비용 못 줄임**(latency만, 정의상(재정렬=총실행량 불변); batching 무손실 근거 ESEC/FSE 2023 arXiv:2308.13129)·safe-RTS full fallback ⑤ Regression×Unit=최고위험 오라클 셀(LLM green-locks-bug, arXiv:2410.21136·2606.18168). SKILL Phase 1(셀 강도 지도)·Phase 2(5단계 셀 라우팅·계획표 셀 열)·Phase 3(셀 오라클 프로필) 배선, principles §4.5(라우팅)·§8(셀 anti-pattern) 신설, evals 셀 라우팅 assertion 추가. 비율 미하드코딩·smoke=sanity caveat·근거 없는 수치 금지 계승. **2번째 적대 검증 패스**(4차원 리뷰→차원별 재검증·논문 WebFetch)로 인용 정직성 교정 — **Sanity 셀 수 4→3**(방법론1×계층3), **arXiv:2509.10279=Targeted Test Selection**(nightly 안전망은 파생 추론)·**2308.13129=Parallel Batch Testing**(TCP-비용불변은 정의상 별개)·**2507.17542=AssertFlip**(green-locks 인접·직접 앵커 아님)·**2510.16433=Continuous Fuzzing 실증**(property-based/스케줄링 미다룸→MED)으로 relabel, 셀 카드 XML 잔재 제거·강도라벨 입도 정합. |
| 2026-07-05 | 스위트 실체화 | 라이브 검증에서 방법론 스위트가 계획 라벨로만 존재하고 코드 분리가 안 됨(phantom suite)을 확인 → **실행 가능한 분리로 실체화** — durable(Smoke/Regression/nightly)은 러너 네이티브 태그(Playwright `{tag}`·`--grep` v1.42+ / Vitest `{tags}`·`--tags-filter` v4.1.0+ / Jest 네이티브 부재→`-t`·`--selectProjects`·`--testPathPatterns` 30+ / 파일명 컨벤션)로 코드에 **물리 부여 + 분리 스크립트 추가 + 셀렉터 실행 검증**, sanity는 태그 아닌 **변경-스코프 선택 레시피**(`@sanity` 태그 금지·무-태그 가드). principles §3.5 신설(durable/transient 비대칭·프레임워크별 문법·membership 대수·분리 검증·CI 매핑·anti-pattern), Phase 2 계획표에 태그 토큰+셀렉터+분리 스크립트+대수(게이트 A 승인 확장), Phase 3 물리 태깅·스크립트 추가·분리 실행 검증, evals `methodology/materialized-separation` 추가(총 15). 비율 미하드코딩·folklore·smoke=sanity 동의어 caveat 계승. 검증 안 된 러너 change-selection 플래그는 '확인 필요' 표기. |
