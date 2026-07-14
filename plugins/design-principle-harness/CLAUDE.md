# design-principle-harness

임의 git 저장소를 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**로 만들기 위해, 코드 설계 품질을 **3단계(① scoring-rubric 점수화 → ② 쉬운 것부터 섹션별 승인 개선 → ③ 종합 결과)**로 진단·개선하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. 다른 마켓플레이스 플러그인에 **의존하지 않는다**(스코어러·루브릭·근거 내재화).

사용자용 개요는 [README.md](README.md), 근거는 [references/research/](skills/design-principle-harness/references/research/README.md) 참조.

## Structure

```
design-principle-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                       # (이 문서) 포인터 + 3단계 요약 + 원칙 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·경계·근거
├── agents/                         # 4 에이전트 (모두 model: "opus")
│   ├── code-scorer.md              # Step 1 — score.py 실행·두 층위 점수표 해석
│   ├── staged-refiner.md           # Step 2 — 쉬운 것부터 섹션별 개선안 제안·승인 후 적용
│   ├── behavior-guard.md           # Step 2 — generator≠checker, 변경마다 행위 센서 실행
│   └── acceptance-reporter.md      # Step 3 — 재측정 델타·종합 결과·정직성 가드
└── skills/design-principle-harness/
    ├── SKILL.md                    # 오케스트레이터(진입점, 3단계 인터랙티브, 승인 게이트)
    ├── scripts/
    │   ├── score.py                # 결정론 스코어러(stdlib only, Python 3.10+ · Tier A/B 총점 + Tier C report-only)
    │   └── test_score.py           # 회귀 테스트(28건·불변식·탐지기·Tier C·하드닝)
    └── references/
        ├── scoring-rubric.md       # 루브릭 정본(Tier A/B 총점·Tier C report-only·배점·confidence·개선 순서)
        ├── design-principles.md    # SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI + Tier C(시맨틱 마크업·a11y·테스트 설명) 카탈로그·한계
        ├── improvement-playbook.md # 쉬운 것부터 안전 개선(메커니즘·불변식·Tier C opt-in 절)
        └── research/               # 1차 근거 dossier(2023~2026 적대 검증) — evidence-dossier·rubric-design·semantic-a11y-test-dossier(+raw-findings)
```

## 3단계 요약

| Step | 이름 | 에이전트 | 산출물 | 게이트 |
|------|------|----------|--------|--------|
| 0 | 스코프 확인 | (오케스트레이터) | 대상 경로·개선 범위·개선 여부 | 한 번에 한 질문 → 승인 |
| 1 | 점수화 | code-scorer | 점수표(Tier A 60/Tier B 40=총점 100) + Tier C AI-맥락 신호(report-only·미포함) + 개선 순서 | 점수표 제시 → 승인 |
| 2 | 단계별 개선 | staged-refiner + behavior-guard | 섹션별 적용 변경 + 행위 검증 | 계획(A)→개별(B) 승인, 쉬운 것부터·구조/Tier C opt-in |
| 3 | 종합 결과 | acceptance-reporter | 재측정 델타 + 종합 리포트 | 정직성 가드 → 저장 opt-in |

## Conventions (핵심 불변식)

- **결정론 먼저** — 손채점부터 하지 않고 `score.py`(stdlib only)를 먼저 돌린 뒤 LLM 해석을 얹는다.
- **두 층위 프레이밍** — Tier A 표면 가독성(명명·주석, act-first, 사람 근거 견고+오도/stale 신호가 LLM에도 해로워 가중↑·단 LLM 리네임 효과는 부호 불안정·과제 의존) vs Tier B 설계 원칙(SOLID·복잡도·중복·DI/IoC 등, defer, 사람 대상 검증·약한 프록시·타당도 외삽이라 낮은 confidence·진단). **두 축 등급**: 측정 신뢰도≠타당도(AI 가독성 예측).
- **총점 = 진단 지표, 인증·목표 아님** — 설계 원칙 점수를 목표화하면 Goodhart/reward-hacking. confidence·근거 대상 항상 표기.
- **Tier C(AI-맥락 신호)는 report-only·총점 미포함** — 시맨틱 마크업(C1)·테스트 설명(C2)은 사용자 요청으로 측정·개선 흐름을 제공하되, **직접 개입 근거가 없어**(시맨틱 HTML 이득은 모델 역량 조건부·ARIA 볼륨은 오류와 상관·올바른 테스트 설명 이득은 미미) **점수 100(A+B)에 합산하지 않는다**. 존재/볼륨 가점 금지, 오도·모호·native-대체가능·무-alt만 개선 후보. **자동 ARIA/alt/어서션 생성 금지**(confident-but-wrong·green-locks-bug).
- **쉬운 것부터·무거운 건 opt-in** — 주석 삭제 → 명명 리네임 → 중복 → (opt-in) 구조. 사용자 지침("무거운 작업 추후, 쉬운 것 먼저 승인 개선")을 순서로 강제.
- **안전 개선** — 리네임은 AST/LSP 위임(수동 치환 금지)·중복은 "잘못된 추상화보다 쌀 수 있음"·구조는 행위 센서 관측·**"테스트 통과≠동작 보존"**.
- **결정 권한(위험은 경고, 수용은 사용자)** — opt-in·개별 승인된 고위험 변경을 회귀 위험을 이유로 조용히 보류·강등 금지(승인 게이트는 무단 실행 방지이지 승인된 실행의 veto 아님). 무테스트→행위 센서 승격(거부 아님). UNVERIFIED는 관측 한계 라벨. execute-or-escalate.
- **generator ≠ checker** — 개선 적용(staged-refiner)과 행위 검증(behavior-guard) 분리.
- **정직성** — 표면 편집을 에이전트 성공률·툴그래프 이득으로 오귀속 금지·"개선 N% 보장" 금지·오도/stale 삭제와 명백히 오도하는 이름 교정만 자신, 나머지는 후보/진단·**개입 연구 없어 총점은 '안전 기여' 인증이 아니라 설계 부채 hotspot 지도**(가장 강한 기여 신호=실행 가능·의존성 무결성은 범위 밖).
- **측정만 vs 승인 후 수정** — Step 1은 코드 수정 없음(측정·시각화). Step 2·3은 승인 게이트 뒤에만 수정하고 **커밋 안 함**(git 워크플로 핸드오프).
- **독립성** — 다른 플러그인을 참조·의존하지 않는다(단독 설치 동작).
- **경계** — 저장소 *구조* AI 준비도 측정(references·실행검증·아키텍처 강제), 완성 코드 리뷰·PR·커밋, 상류 핸드오프 게이트, 하네스 자체 진단·생성, 한 기능 구현·실행검증은 범위 밖. 이 하네스는 **코드 본문의 설계 품질을 점수화하고 쉬운 것부터 승인 개선**하는 데 특화한다.
- 4개 에이전트 협업 하네스이므로 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-14 | 플러그인 신설 (v0.1.0) | 코드 설계 품질 3단계(점수화 → 쉬운 것부터 승인 개선 → 종합 결과) 하네스. `score.py`(stdlib only)가 두 층위로 채점 — Tier A 표면(명명·주석 /60)·Tier B 설계 원칙(SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI /40). 4 에이전트(opus). 정직성: 총점=진단 지표(Goodhart 가드·개입 연구 없어 '안전 기여' 인증 아님)·명명/주석은 사람 근거+오도/stale 신호가 LLM에도 해로워 Tier A 가중↑(LLM 리네임 효과는 부호 불안정)·구조 지표는 낮은 confidence 진단(타당도 외삽·두 축 등급)·리네임 AST/LSP·"테스트 통과≠동작 보존"·측정은 코드 수정 없음·개선은 승인 뒤·커밋 안 함. deep-research(8렌즈 sweep→4 적대 검증→2 synthesis)로 2023~2026 1차 소스 적대 검증(live arXiv 38건·조작 0·과장 교정 반영). 테스트 19건. 독립 플러그인(타 플러그인 비의존). |
| 2026-07-15 | Tier C 추가 (v0.2.0) | 사용자 요청(시맨틱 태그·웹 접근성·테스트 설명으로 AI 코드 맥락 파악)으로 **Tier C AI-맥락 신호**를 추가 — C1 Semantic Markup & a11y(native 시맨틱 vs `<div onClick>`·native 대체가능 `role=`·무-alt `<img>`·ARIA 볼륨 report-only)·C2 Test Legibility(모호/오도 테스트 제목·getByRole vs testid/CSS/xpath 셀렉터). **report-only·총점 100(A+B) 미포함**(존재/볼륨 가점 금지·오도/모호/native-대체가능만 개선 후보·자동 ARIA/alt/어서션 생성 금지). Step 2에 opt-in 개선 순서(C-a 테스트 제목 삭제/리네임 → C-b role 제거/alt 보완 → C-c `<div>`→`<button>` 승격 → C-d →getByRole 이관) 추가. `/deep-research`(5렌즈 plain-text 워크플로·10 조사/검증 에이전트·최종 synthesis는 연결 끊김으로 journal 복구 후 직접 종합)로 근거 수집·적대 검증. **정직성 핵심**: 시맨틱 HTML 이득은 **모델 역량 조건부**(WorkArena L1 강한 모델 full HTML +11~17.5pp/약한 모델 a11y-tree 우세, 저자 동일군 2604.01535·2605.29397 — 독립 삼각검증 아님)·landmark/heading/button-vs-div 격리 연구 부재; **ARIA 볼륨은 오류와 상관**(WebAIM 방향성만·고정 배수 금지·상관≠인과); **올바른 테스트 설명의 LLM 이해 이득은 유의하지 않고 오도 설명만 측정 가능한 해악**(2404.03114)·tests-as-oracle overfitting(2511.16858)·오라클은 actual 인코딩(2410.21136); accessible selector는 refactor-robust(MEDIUM·vendor idiom)이나 AI 이해 향상 근거 없음. 적대 감사 인용 교정: 2504.04372 제목·78%(≠81%)·750,013 tasks / 2511.16858 제목 / "~10×" drop / 2508.14727 STRONG. 테스트 19→28건. score.py v0.2.0. |
