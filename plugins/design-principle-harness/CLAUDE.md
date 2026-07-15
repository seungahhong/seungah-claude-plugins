# design-principle-harness

임의 git 저장소를 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**로 만들기 위해 **두 큰 틀(Track A 코드 품질 + Track B AI 접근성)**로 진단·개선하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. Phase 0에서 트랙을 선택하고(둘 다면 A→B), 각 틀 안에서 다시 단계별로 사용자에게 문의 후 선택한 방향으로 승인 개선한다. 다른 마켓플레이스 플러그인에 **의존하지 않는다**(스코어러·루브릭·근거 내재화).

사용자용 개요는 [README.md](README.md), 근거는 [references/research/](skills/design-principle-harness/references/research/README.md) 참조.

## Structure

```
design-principle-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                       # (이 문서) 포인터 + 2트랙 요약 + 원칙 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·경계·근거
├── agents/                         # 6 에이전트 (모두 model: "opus")
│   ├── code-scorer.md              # [A] Step A1 — score.py 실행·층위 점수표 해석
│   ├── staged-refiner.md           # [A] Step A2 — 쉬운 것부터 섹션별 개선안 제안·승인 후 적용
│   ├── behavior-guard.md           # [A·B] generator≠checker, 변경마다 행위 센서 실행
│   ├── acceptance-reporter.md      # [A·B] 재측정 델타·종합 결과·정직성 가드
│   ├── ai-access-assessor.md       # [B] Step B1 — ai_access.py 실행·6지표 SCORED/report-only 해석
│   └── ai-access-improver.md       # [B] Step B2 — 지표별 개선안 제안·승인 후 적용(build enforces)
└── skills/design-principle-harness/
    ├── SKILL.md                    # 오케스트레이터(진입점, 2트랙 인터랙티브, 트랙별 승인 게이트)
    ├── scripts/
    │   ├── score.py                # [A] 결정론 스코어러(stdlib · Tier A/B 총점 + Tier C report-only)
    │   ├── test_score.py           # [A] 회귀 테스트(31건·불변식·탐지기·Tier C·comment-gap·하드닝)
    │   ├── ai_access.py            # [B] AI 접근성 결정론 assessor(stdlib · 6지표·SCORED=M1·M2만)
    │   └── test_ai_access.py       # [B] 회귀 테스트(21건·SCORED 불변식·탐지기·하드닝)
    └── references/
        ├── scoring-rubric.md            # [A] 루브릭 정본(Tier A/B/C)
        ├── design-principles.md         # [A] SOLID·…·Tier C 카탈로그·한계
        ├── improvement-playbook.md      # [A] 쉬운 것부터 안전 개선
        ├── ai-accessibility-rubric.md   # [B] 6지표 루브릭 정본(SCORED vs report-only)
        ├── ai-accessibility-playbook.md # [B] 지표별 안전 개선(build enforces·자동 생성 금지)
        └── research/                    # 1차 근거 dossier — evidence-dossier·rubric-design·semantic-a11y-test-dossier·ai-accessibility-dossier(+raw-findings)
```

## 2트랙 요약

| 트랙 | Step | 에이전트 | 산출물 | 게이트 |
|------|------|----------|--------|--------|
| — | Phase 0 | (오케스트레이터) | 트랙 선택(A/B/A+B)·경로·범위 | 한 번에 한 질문 → 승인 |
| **A 코드 품질** | A1 점수화 | code-scorer | 점수표(Tier A 60/Tier B 40=100)+Tier C report-only | 점수표 → 승인 |
| **A 코드 품질** | A2 개선 | staged-refiner + behavior-guard | 섹션별 적용 + 행위 검증 | 계획(A)→개별(B)·쉬운 것부터·구조/Tier C opt-in |
| **A 코드 품질** | A3 종합 | acceptance-reporter | 재측정 델타 + 리포트 | 정직성 가드 → 저장 opt-in |
| **B AI 접근성** | B1 측정 | ai-access-assessor | 6지표 assessment(SCORED M1·M2 / 나머지 report-only) | assessment → 승인 |
| **B AI 접근성** | B2 개선 | ai-access-improver + behavior-guard | 지표별 적용(가드레일·가이드) + 검증 | 지표별 문의→계획→개별·build enforces | 
| **B AI 접근성** | B3 종합 | acceptance-reporter | 재측정 델타 + 리포트 | 정직성 가드 → 저장 opt-in |

## Conventions (핵심 불변식)

- **결정론 먼저** — 손채점부터 하지 않고 `score.py`(stdlib only)를 먼저 돌린 뒤 LLM 해석을 얹는다.
- **두 층위 프레이밍** — Tier A 표면 가독성(명명·주석, act-first, 사람 근거 견고+오도/stale 신호가 LLM에도 해로워 가중↑·단 LLM 리네임 효과는 부호 불안정·과제 의존) vs Tier B 설계 원칙(SOLID·복잡도·중복·DI/IoC 등, defer, 사람 대상 검증·약한 프록시·타당도 외삽이라 낮은 confidence·진단). **두 축 등급**: 측정 신뢰도≠타당도(AI 가독성 예측).
- **총점 = 진단 지표, 인증·목표 아님** — 설계 원칙 점수를 목표화하면 Goodhart/reward-hacking. confidence·근거 대상 항상 표기.
- **Tier C(AI-맥락 신호)는 report-only·총점 미포함** — 시맨틱 마크업(C1)·테스트 설명(C2)은 사용자 요청으로 측정·개선 흐름을 제공하되, **직접 개입 근거가 없어**(시맨틱 HTML 이득은 모델 역량 조건부·ARIA 볼륨은 오류와 상관·올바른 테스트 설명 이득은 미미) **점수 100(A+B)에 합산하지 않는다**. 존재/볼륨 가점 금지, 오도·모호·native-대체가능·무-alt만 개선 후보. **자동 ARIA/alt/어서션 생성 금지**(confident-but-wrong·green-locks-bug).
- **쉬운 것부터·무거운 건 opt-in** — 주석 삭제 → 명명 리네임 → 중복 → (opt-in) 구조. 사용자 지침("무거운 작업 추후, 쉬운 것 먼저 승인 개선")을 순서로 강제.
- **안전 개선** — 리네임은 AST/LSP 위임(수동 치환 금지)·중복은 "잘못된 추상화보다 쌀 수 있음"·구조는 행위 센서 관측·**"테스트 통과≠동작 보존"**.
- **주석은 삭제 + '왜' 추가(v0.3.0)** — 삭제(오도·stale·죽은 코드·위험 ~0)가 기본이되, **코드만으로 문맥 파악이 어려운 곳**(스코어러 comment-gap 후보: 침묵 예외·매직 넘버·정규식·비자명 우회)엔 **'왜/맥락' 주석을 opt-in 추가**한다(필수 아님·what 아닌 why·사람이 정확성 검증·자동 생성 주석 사실 단정 금지). **주석 볼륨은 report-only(점수 무관·가점 없음 → Goodhart 방지)**. 이득 프레이밍: 올바른 주석의 LLM 이해 상승은 개입 근거 약함 → *사람 이해 + 코드로 파생 불가한 맥락 보충*으로만, "AI 성공률 +N%" 금지.
- **결정 권한(위험은 경고, 수용은 사용자)** — opt-in·개별 승인된 고위험 변경을 회귀 위험을 이유로 조용히 보류·강등 금지(승인 게이트는 무단 실행 방지이지 승인된 실행의 veto 아님). 무테스트→행위 센서 승격(거부 아님). UNVERIFIED는 관측 한계 라벨. execute-or-escalate.
- **generator ≠ checker** — 개선 적용(staged-refiner)과 행위 검증(behavior-guard) 분리.
- **정직성** — 표면 편집을 에이전트 성공률·툴그래프 이득으로 오귀속 금지·"개선 N% 보장" 금지·오도/stale 삭제와 명백히 오도하는 이름 교정만 자신, 나머지는 후보/진단·**개입 연구 없어 총점은 '안전 기여' 인증이 아니라 설계 부채 hotspot 지도**(가장 강한 기여 신호=실행 가능·의존성 무결성은 범위 밖).
- **측정만 vs 승인 후 수정** — Step 1은 코드 수정 없음(측정·시각화). Step 2·3은 승인 게이트 뒤에만 수정하고 **커밋 안 함**(git 워크플로 핸드오프).
- **독립성** — 다른 플러그인을 참조·의존하지 않는다(단독 설치 동작).
- **Track B AI 접근성(v0.4.0)** — 에이전트가 코드베이스를 이해·안전하게 수정하기 쉬운가를 6지표로 측정·개선(`ai_access.py`). **build enforces, docs explain**: 기계 검증 가능 속성(강제된 의존 방향·실행 테스트)만 **SCORED**(M1·M2), 나머지 지표의 에이전트 이득은 측정된 개입이 아니라 추론이라 **report-only**. **에이전트 가이드 존재≠성능**(자동 생성 금지·arXiv:2602.11988)·**tool-index≠code-structure**(LocAgent 92.7%·RepoGraph +32.8% 오귀속 금지)·**유일 측정 레버=독립 oracle**(격리-green 81~100% false-pass·arXiv:2606.26978)·규칙/모듈/줄 수 가점 금지·테스트 통과를 correctness로 credit 금지. 개입(가드레일·가이드)은 승인 게이트 뒤에만·커밋 안 함.
- **경계** — 완성 코드 리뷰·PR·커밋, 상류 핸드오프 게이트, 하네스 자체 진단·생성, 한 기능 구현·실행검증은 범위 밖. 이 하네스는 **Track A(코드 본문 설계 품질)와 Track B(AI 접근성: 저장소 구조·강제 층위)** 두 축을 사용자 선택으로 다룬다.
- 6개 에이전트 협업 하네스이므로 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-14 | 플러그인 신설 (v0.1.0) | 코드 설계 품질 3단계(점수화 → 쉬운 것부터 승인 개선 → 종합 결과) 하네스. `score.py`(stdlib only)가 두 층위로 채점 — Tier A 표면(명명·주석 /60)·Tier B 설계 원칙(SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI /40). 4 에이전트(opus). 정직성: 총점=진단 지표(Goodhart 가드·개입 연구 없어 '안전 기여' 인증 아님)·명명/주석은 사람 근거+오도/stale 신호가 LLM에도 해로워 Tier A 가중↑(LLM 리네임 효과는 부호 불안정)·구조 지표는 낮은 confidence 진단(타당도 외삽·두 축 등급)·리네임 AST/LSP·"테스트 통과≠동작 보존"·측정은 코드 수정 없음·개선은 승인 뒤·커밋 안 함. deep-research(8렌즈 sweep→4 적대 검증→2 synthesis)로 2023~2026 1차 소스 적대 검증(live arXiv 38건·조작 0·과장 교정 반영). 테스트 19건. 독립 플러그인(타 플러그인 비의존). |
| 2026-07-15 | Track B AI 접근성 신설·2트랙 재편 (v0.4.0) | 사용자 요청 — 코드 품질 외에 **AI 접근성(에이전트가 코드베이스를 이해·안전하게 수정하기 쉬운가)**도 측정·판단·승인 개선하고, **큰 틀(트랙)에서 단계별 + 큰 틀 하위에서도 지표별 문의**로 진행. **두 큰 틀 재편**: Track A(코드 품질, 기존 score.py) + **Track B(AI 접근성)**. 신규 독립 assessor `ai_access.py`(stdlib only)가 사용자 지정 6지표를 결정론 측정 — M1 의존성 방향 강제(dependency-cruiser/eslint-boundaries/import-linter/ArchUnit/Nx/TS refs 존재+CI fail)·M2 독립 실행 가능성(runnability+독립 oracle 가드)·M3 빌드 피드백·M4 모듈 경계 예측 가능성·M5 패턴 일관성·M6 에이전트 가이드. SKILL Phase 0 트랙 선택(A/B/A+B·둘 다면 A→B)→트랙별 Step(A1~A3/B1~B3)·각 트랙 하위 지표/섹션별 승인 게이트. 신규 에이전트 2종(ai-access-assessor/ai-access-improver, opus)·references 2종(ai-accessibility-rubric·playbook)·dossier. `/deep-research`(6지표·13에이전트·synthesis까지 성공)로 근거 수집·적대 검증. **정직성 핵심**: 6지표 중 5개의 '에이전트 이득'은 측정된 개입이 아니라 인간-SE 이득+첫 원리 추론이라 **SCORED는 기계 검증 사실(M1·M2)뿐·나머지 report-only**; **build enforces docs explain**(에이전트 가이드 존재≠성능·arXiv:2602.11988 LLM-생성본 5/8 하락→**자동 생성 금지**); **tool-index≠code-structure**(LocAgent 92.7%·RepoGraph +32.8%는 툴 이득·layout 귀속 금지·ablation BM25>graph); **유일 측정 레버=독립 oracle**(격리-green 81~100% false-pass·arXiv:2606.26978); 테스트/컴파일 통과를 correctness로 credit 금지(ImpossibleBench 76% exploit); 규칙/모듈/줄 수 가점 금지. 적대 감사: arXiv ID hallucination 0건·DROP(memorization 프레이밍·RepoGraph fabricated quote·ImpossibleBench 66/93% 오수치). 테스트 score 31 + ai_access 21 = 52건. plugin v0.3→v0.4.0·marketplace v1.34→v1.35.0. |
| 2026-07-15 | A3 '왜' 주석 추가 경로 (v0.3.0) | 사용자 피드백 — 현재 주석은 *삭제*만 다루는데, 코드만으로 문맥 파악이 어려운 곳엔 **설명 주석 추가**로 도움받고 싶다(필수 아님). score.py에 **comment-gap 후보 탐지기**(report-only) 신설 — 침묵 예외 처리(empty except/catch)·매직 넘버(3자리+/소수)·정규식 사용을 세어 "코드만으로 '왜'를 알기 어려운 지점"을 표면화(문자열·주석 내부는 제외·매직 파일당 캡). A3 개선 메커니즘을 **삭제 우선 + '왜/맥락' 주석 opt-in 추가**로 확장(SKILL Step 2·staged-refiner·behavior-guard 정확성 리뷰·improvement-playbook·scoring-rubric·research/README 반영). **정직성**: 추가는 **what 아닌 why**(코드로 파생 불가한 의도·외부 제약·우회 이유)·**opt-in·필수 아님**·**점수 무관(볼륨 가점 없음→Goodhart 방지)**·**사람이 정확성 검증**(자동 생성 주석 사실 단정 금지·오도 주석은 유일하게 실증된 해악). 근거 화해(research/README #10): 2404.03114의 null 결과는 *이미 읽히는* 코드 대상이고, comment-gap은 *코드에 없는 정보 보충*이라 별개 사례 — 이득은 사람 이해+비파생 맥락이지 "LLM 성공률 +N%" 아님. 테스트 28→31건. score.py v0.2→v0.3.0. |
| 2026-07-15 | Tier C 추가 (v0.2.0) | 사용자 요청(시맨틱 태그·웹 접근성·테스트 설명으로 AI 코드 맥락 파악)으로 **Tier C AI-맥락 신호**를 추가 — C1 Semantic Markup & a11y(native 시맨틱 vs `<div onClick>`·native 대체가능 `role=`·무-alt `<img>`·ARIA 볼륨 report-only)·C2 Test Legibility(모호/오도 테스트 제목·getByRole vs testid/CSS/xpath 셀렉터). **report-only·총점 100(A+B) 미포함**(존재/볼륨 가점 금지·오도/모호/native-대체가능만 개선 후보·자동 ARIA/alt/어서션 생성 금지). Step 2에 opt-in 개선 순서(C-a 테스트 제목 삭제/리네임 → C-b role 제거/alt 보완 → C-c `<div>`→`<button>` 승격 → C-d →getByRole 이관) 추가. `/deep-research`(5렌즈 plain-text 워크플로·10 조사/검증 에이전트·최종 synthesis는 연결 끊김으로 journal 복구 후 직접 종합)로 근거 수집·적대 검증. **정직성 핵심**: 시맨틱 HTML 이득은 **모델 역량 조건부**(WorkArena L1 강한 모델 full HTML +11~17.5pp/약한 모델 a11y-tree 우세, 저자 동일군 2604.01535·2605.29397 — 독립 삼각검증 아님)·landmark/heading/button-vs-div 격리 연구 부재; **ARIA 볼륨은 오류와 상관**(WebAIM 방향성만·고정 배수 금지·상관≠인과); **올바른 테스트 설명의 LLM 이해 이득은 유의하지 않고 오도 설명만 측정 가능한 해악**(2404.03114)·tests-as-oracle overfitting(2511.16858)·오라클은 actual 인코딩(2410.21136); accessible selector는 refactor-robust(MEDIUM·vendor idiom)이나 AI 이해 향상 근거 없음. 적대 감사 인용 교정: 2504.04372 제목·78%(≠81%)·750,013 tasks / 2511.16858 제목 / "~10×" drop / 2508.14727 STRONG. 테스트 19→28건. score.py v0.2.0. |
