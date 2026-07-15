---
name: design-principle-harness
description: 임의 git 저장소를 'AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스'로 만들기 위해 **두 큰 틀(Track A 코드 품질 + Track B AI 접근성)**로 진단·개선하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. Phase 0에서 트랙을 선택하고(둘 다면 A→B), 각 틀 안에서 다시 단계별로 사용자에게 문의 후 선택한 방향으로 승인 개선한다. **Track B AI 접근성**은 독립 결정론 assessor(ai_access.py, stdlib only)가 6지표를 측정 — 패턴 일관성·빌드 피드백 품질·모듈 경계 예측 가능성·의존성 방향 강제(dependency-cruiser/eslint-boundaries/import-linter/ArchUnit/Nx/TS refs 설정 존재+CI fail=SCORED Gate)·독립 실행 가능성(runnability gate+독립 oracle 가드=SCORED)·에이전트 가이드(CLAUDE.md/AGENTS.md non-inferable 내용). 정직성(deep-research 근거): 6지표 중 5개의 '에이전트 이득'은 측정된 개입이 아니라 인간-SE 이득+첫 원리 추론이라 SCORED는 기계 검증 사실(강제 존재·실행 gate)뿐이고 나머지는 report-only, build enforces docs explain(가이드 존재≠성능·arXiv:2602.11988), tool-index≠code-structure(LocAgent 92.7%·RepoGraph +32.8%를 layout에 귀속 금지), 유일 측정 레버=독립 oracle(격리-green 81~100% false-pass·arXiv:2606.26978), 에이전트 가이드 자동 생성 금지, 개선은 승인 게이트 뒤에만·커밋 안 함. **Track A 코드 품질**은 결정론 스코어러(score.py)가 층위로 점수화 — Tier A 표면 가독성(변수명·함수명·클래스/컴포넌트명·주석)·Tier B 설계 원칙(SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI)이 총점 100, 그리고 Tier C AI-맥락 신호(시맨틱 HTML 태그·웹 접근성 ARIA/WCAG·테스트 설명/접근성 셀렉터)는 report-only로 총점 미포함. Step 2 스코어러가 매긴 개선 순서(쉬운 것부터: 주석→명명→중복→구조)를 따라 섹션마다 계획→개별 승인 게이트로 하나씩 개선하고 무거운 SOLID·구조 리팩터와 Tier C(시맨틱 마크업 승격·테스트 설명 정리)는 뒤로 미뤄 opt-in. Step 3 재측정 델타와 함께 종합 결과. 4개 에이전트(code-scorer/staged-refiner/behavior-guard/acceptance-reporter, 모두 opus). 총점은 인증이 아니라 개선 우선순위용 진단 지표(Goodhart 가드·개입 연구 없음이라 '안전 기여' 인증 아님)·명명/주석은 사람 근거 견고+오도/stale 신호가 LLM에도 해로워 Tier A 가중↑(LLM 리네임 효과는 부호 불안정)·구조 지표는 낮은 confidence 진단(타당도 외삽)·Tier C 시맨틱마크업/a11y/테스트설명은 이득이 모델 역량 조건부이거나 개입 근거 부재라 report-only·총점 미포함(ARIA/role 볼륨 가점 금지·WebAIM ARIA 많을수록 오류↑·자동 ARIA/alt/어서션 생성 금지·오도 테스트 설명만 삭제)·리네임은 AST/LSP 위임·'테스트 통과≠동작 보존'·측정은 코드 수정 없음·개선은 승인 뒤에만·커밋 안 함. 주석은 삭제 우선(오도·죽은 코드)이되 **코드만으로 문맥 파악이 어려운 곳(침묵 예외·매직 넘버·정규식 등 comment-gap 후보)엔 '왜/맥락' 주석을 opt-in으로 추가**한다(필수 아님·what 아닌 why·사람이 정확성 검증·자동 생성 주석 사실 단정 금지·주석 볼륨은 report-only로 점수 무관). "코드 설계 품질/SOLID/응집 결합/복잡도/중복/명명/주석을 점수화하고 쉬운 것부터 개선", "시맨틱 태그·웹 접근성·테스트 설명을 측정해서 AI가 코드를 더 잘 이해하게 섹션별로 승인받아 개선", "코드만으로 문맥 파악 어려운 곳에 설명 주석 추가해줘"(Track A), "AI 에이전트가 코드베이스를 이해·수정하기 쉬운지(패턴 일관성·빌드 피드백·모듈 경계·의존성 방향 강제·독립 실행·CLAUDE.md 가이드) 측정하고 승인받아 개선", "AI가 안전하게 기여하게 의존 방향 가드레일·에이전트 가이드 정비"(Track B) 같은 요청에 발동. 완성 코드 리뷰/PR/커밋·상류 핸드오프 게이트·하네스 자체 진단·한 기능 구현/실행검증은 범위 밖. 다른 플러그인에 의존하지 않는 독립 플러그인(score.py·ai_access.py·루브릭·근거 dossier 모두 내재화).
---

# Design Principle Harness — 코드 품질 · AI 접근성 2트랙 진단·개선

> **한 줄**: 저장소를 **두 큰 틀**로 다룬다 — **Track A 코드 품질**(명명·주석·설계 원칙·시맨틱/테스트)과 **Track B AI 접근성**(에이전트가 코드를 이해·안전하게 수정하기 쉬운가: 패턴 일관성·빌드 피드백·모듈 경계·의존 방향 강제·독립 실행·에이전트 가이드). 각 틀 안에서 **결정론 측정 → 사용자에게 문의 → 선택한 방향으로 단계별 승인 개선**을 한다.

이 하네스는 에이전트를 순차 spawn한다(**모든 Agent 호출에 `model: "opus"` 명시**). 발동 즉시 손채점·손수정부터 하지 않고, **결정론 스코어러(트랙 A `score.py` / 트랙 B `ai_access.py`)를 먼저** 돌린 뒤 그 위에 해석·개선을 얹는다.

## 언제 발동하나

- **Track A(코드 품질)**: "설계 품질 점수 매기고 개선", "SOLID·응집/결합·복잡도·중복 진단", "변수명/함수명/주석부터 정리", "시맨틱 태그·웹 접근성·테스트 설명 측정·개선", "코드만으로 문맥 파악 어려운 곳에 설명 주석 추가".
- **Track B(AI 접근성)**: "AI 에이전트가 코드베이스를 이해·수정하기 쉬운지 측정·개선", "의존성 방향 강제·모듈 경계·빌드 피드백·독립 실행·CLAUDE.md 가이드 점검", "AI가 안전하게 기여할 수 있게 가드레일·가이드 정비".
- **발동 안 함**: 완성 코드 리뷰·PR·커밋, 상류 산출물(기획/디자인/계약) 핸드오프 게이트, 하네스 자체 진단·생성, 한 기능 구현·실행검증. (→ 경계 절)

---

## Phase 0 — 트랙 선택 + 스코프 확인 (인터랙티브)

**한 번에 하나씩** 확정한다(모르면 기본값 제시). 먼저 **큰 틀(트랙)**을 고르고, 그 뒤 각 틀 안에서 다시 단계별로 문의한다.

1. **대상 경로** — 채점할 저장소/디렉터리(기본: 현재 경로).
2. **트랙 선택(큰 틀)** — **Track A 코드 품질** / **Track B AI 접근성** 중 **원하는 부분집합**(하나·둘 다). 배타 아님. 둘 다면 **A→B 순**으로 이어 수행한다(각 트랙은 자기 스코어러를 1회 실행).
3. **트랙별 세부 범위**(선택한 트랙에 한해, 큰 틀 하위 단계):
   - Track A: (a) 표면(주석·명명)만 / (b) +쉬운 구조(중복) / (c) +무거운 구조(SOLID·복잡도·순환·과대추상 opt-in) · Tier C(시맨틱/테스트) 포함 여부. 기본 (a)부터·뒤에서 확장 문의.
   - Track B: 6지표 중 어디까지 개선까지 갈지(측정만 / SCORED 지표(의존 방향 강제·독립 실행) 개선 / report-only 지표까지). 기본은 **측정 먼저 보고 지표별로 다시 문의**.
4. **개선 여부** — 측정만 볼지, 승인받아 개선까지 할지.

확정 후: `[Phase 0] 경로 {경로}·트랙 {A/B/A+B}·범위 {...} — 다음: {선택한 첫 트랙}. 진행할까요?`

> **핵심 상호작용 규약(사용자 지침)**: 큰 틀(트랙)에서 단계별로 진행하되, **큰 틀 하위에서도 매 단계 사용자에게 문의 후 선택한 방향으로만** 진행한다. 묶어서 자동 진행하지 않는다.

---

# ═══ Track A — 코드 품질 ═══

> `score.py`가 Tier A(표면 60)/Tier B(설계 40)=총점 100 + Tier C(AI-맥락 신호·report-only) 채점 → 쉬운 것부터 섹션별 승인 개선 → 종합. (선택 시에만 수행)

## Step A1 — 점수화 (code-scorer)

`code-scorer` 에이전트를 **`model: "opus"`** 로 spawn한다. 에이전트는:

1. `python3 skills/design-principle-harness/scripts/score.py <repo> --json .claude/design-principle/<slug>/scorecard.json` 실행.
2. JSON을 **섹션별 점수표 + 개선 순서**로 해석(Tier A 표면 60 / Tier B 설계 40 = 총점 100, Tier C AI-맥락 신호는 report-only·총점 미포함).

### 층위 (반드시 유지)

- **Tier A 표면 가독성 (act-first)** /60 — A1 명명 명료성(28) · A2 명명 규약 일관성(12) · A3 주석 건강도(20).
- **Tier B 설계 원칙 (defer·진단)** /40 — B1 복잡도/KISS(8) · B2 응집·결합/SRP(8) · B3 중복/DRY(8) · B4 순환 의존(8) · B5 과대추상/DIP·DI·IoC·YAGNI(8).
- **Tier C AI-맥락 신호 (report-only · 총점 100에 미포함)** — C1 Semantic Markup & a11y(시맨틱 HTML·ARIA) · C2 Test Legibility(테스트 설명·접근성 셀렉터). 사용자 요청(시맨틱 태그·웹 접근성·테스트 설명으로 AI가 코드 맥락 파악)으로 추가. **셋 다 직접 개입 근거가 없어 점수화하지 않고 개선 후보 census로만** 낸다(→ 정직성 절). 프론트엔드/테스트 저장소에만 적용, 아니면 N/A.

### 정직성 (Step 1)

- **총점은 인증이 아니라 개선 우선순위용 진단 지표**다. "점수를 목표로 최적화"를 권하지 않는다(설계 원칙 점수 목표화 = Goodhart/reward-hacking).
- **confidence·근거 대상(subjects)을 항상 표기.** 신뢰도는 두 축 — **측정 신뢰도**(결정론적으로 잴 수 있나)와 **타당도**(AI 가독성을 실제로 예측하나). Tier B는 타당도가 **전부 외삽**(사람 대상 검증·개입 연구 없음). Tier A(명명·주석)는 사람 근거가 견고하고 오도/stale 신호가 LLM에도 해로워 가중↑ — 단 **LLM 식별자 리네임 효과는 부호 불안정·과제 의존**(intent 과제 -11~-29pp·알고리즘 ≈0·모델별 +14~-32pp)이라 단일 수치로 못 쓴다.
- 스코어러 caveat(지역 변수 미측정·JS 복잡도 근사·Type-3/4 중복 측정 불가·DI/IoC 정적 측정 불가·팀 규약 상이 시 명명 오탐)을 그대로 전달.
- **Tier C(시맨틱 마크업·a11y·테스트 설명)는 report-only·총점 미포함**으로 보고한다. 근거: AI 이해 이득이 **모델 역량 조건부**(강한 모델=full HTML 유리·약한 모델=a11y-tree 유리)이거나 **개입 근거 부재**(관용/추론). **ARIA/role/셀렉터/설명 '볼륨'을 가점 금지**(WebAIM: ARIA 많을수록 오류↑·상관≠인과). 존재는 가점하지 않고 **오도/모호/native-대체가능/무-alt 같은 명백한 결함만** 후보로 낸다. [research/semantic-a11y-test-dossier.md]

게이트: 점수표 + `[Step 1] {total}/100 · 최약 {섹션} — 다음: Step 2 개선(쉬운 것부터). 진행할까요?`

---

## Step A2 — 단계별 개선 (staged-refiner + behavior-guard)

점수표의 **개선 순서**대로, **쉬운 것부터** 섹션을 하나씩 처리한다. 각 섹션은 **계획 제시(게이트 A) → 개별 승인 → 적용 → 행위 검증(게이트 B)**.

### 순서 (기본 easiest-first)

1. **A3 주석** — (1) 오도·stale·커멘트아웃(죽은 코드) 주석 **삭제**(위험 ~0·기본). (2) **코드만으로 문맥 파악이 어려운 곳**(스코어러가 낸 comment-gap 후보: 침묵 예외 처리·매직 넘버·정규식·비자명 우회)에 **'왜/맥락' 주석 opt-in 추가** — what이 아니라 why(의도·외부 제약·우회 이유). **사람이 정확성 검증**(자동 생성 주석을 사실로 단정 금지·오도 주석은 실측 해악). 필수 아님.
2. **A1 명명 명료성** — 무의미/난독 이름 **리네임**(AST/LSP 위임).
3. **A2 명명 규약** — casing 통일 리네임.
4. **B3 중복(DRY)** — Type-1/2 정확 중복 extract.
5. **B1 복잡도(KISS)** — 함수 분해. **opt-in 고위험**.
6. **B2 응집·결합(SRP)** — god-file 책임 분리. **opt-in 고위험**.
7. **B4 순환 의존** — 의존 역전. **opt-in 고위험**.
8. **B5 과대추상(DIP·DI/IoC·YAGNI)** — 간접참조 축소. **opt-in**.

> **무거운 작업(5~8)은 사용자 요청 시에만.** 기본은 1~4(쉬운 표면 개선)까지 제안하고 "여기까지 반영하고, SOLID·구조는 별도로 진행할까요?"를 묻는다. (사용자 지침: "무거운 작업은 추후에 진행하고 좀 더 쉬운 작업부터 단계별로 승인받아 개선")

### Tier C 개선 (opt-in · report-only · 총점 무관 · 프론트엔드/테스트 저장소)

시맨틱 마크업·테스트 설명 개선을 원할 때만, A/B와 **별도로** 제안한다. 셋 다 개입 효과가 입증되지 않아 **삭제/교정·명백한 결함만** 다룬다(존재 채우기·볼륨 늘리기 금지).

- **C-a. C2 테스트 설명** — 오도·모호 제목 **삭제/리네임**(위험 ~0). 오도 제목은 삭제 우선. **자동 어서션/오라클 생성 금지**(green-locks-bug).
- **C-b. C1 시맨틱 마크업** — native 대체 가능한 `role=` 제거·`alt` 누락 보완(사람이 의미 확인). **자동 ARIA/alt 생성 금지**.
- **C-c. C1 시맨틱 마크업** — `<div/span onClick>` → `<button>`/`<a>` 승격. **opt-in·행위 센서**(렌더·상호작용 관측).
- **C-d. C2 셀렉터** — testid/CSS/xpath → getByRole 이관. **opt-in·행위 센서**. getByRole=green이어도 a11y 깨질 수 있어 axe 대체 아님.

섹션 루프·게이트·안전 불변식은 A/B와 동일. 근거·메커니즘 상세는 [references/improvement-playbook.md] Tier C 절.

### 각 섹션 루프

- `staged-refiner`(**opus**)가 그 섹션의 개선안(변경 목록·위험·메커니즘)을 제시 → **게이트 A(계획 승인)**.
- 승인된 변경을 **하나씩** 적용 → 변경마다 `behavior-guard`(**opus**)가 클래스별 행위 센서 실행 → **게이트 B**.
- 섹션 종료 보고: `[Step 2·{섹션}] {적용 N건}·검증 {결과} — 다음 섹션 {다음}. 계속할까요?`

### 안전·결정 권한 불변식

- **리네임은 AST/LSP 위임**(수동 치환 금지). 동적 참조·직렬화·리플렉션·공개 API·파일 라우트는 격리 센서 요청.
- **구조 리팩터는 행위 센서 관측·opt-in**. **"테스트 통과 ≠ 동작 보존."** 자동 테스트 부재는 **거부 사유가 아니라 행위 센서(실제 실행·렌더) 승격 사유**. UNVERIFIED는 관측 한계 라벨이지 거부 신호 아님 — **red 센서만 롤백**.
- **위험은 경고, 수용은 사용자.** opt-in·개별 승인된 고위험 변경을 회귀 위험을 이유로 **조용히 보류·강등하지 않는다**(승인 게이트는 무단 실행 방지 장치이지 승인된 실행의 veto가 아니다). 새 차단 요인은 **execute-or-escalate**.
- **한 번에 한 섹션·한 승인.** 묶어 적용하지 않는다. **커밋하지 않는다.**

---

## Step A3 — 종합 결과 (acceptance-reporter)

`acceptance-reporter`(**opus**)를 spawn한다. 에이전트는 `score.py`를 **동일 스코프로 재실행**해 섹션별 before→after 델타 + 종합 결과 리포트를 낸다.

### 정직성 (Step 3)

- **표면 편집을 과대 귀속 금지** — 주석·명명 정리의 점수 상승을 "에이전트 성공률 +N%"·"툴그래프 이득"으로 연결하지 않는다(그 이득은 툴 측 그래프 인덱스 효과이지 본문 편집 효과 아님).
- **점수 상승 = 품질 인증 아님.** 오도/stale 삭제·명백히 오도하는 이름 교정만 자신 있게, 나머지는 "후보 정리·진단 지표 이동"으로만. **개입 연구가 없으므로** 점수 델타를 에이전트 성공률로 귀속하려면 같은 저장소 재측정 행위 probe가 필요하다.
- reward-hacking 점검(스코어러 만족용 의미 없는 표면 변형 색출).
- **Tier C 델타는 총점과 분리 보고**(report-only). 시맨틱 마크업·테스트 설명 개선을 "AI 성공률·이해 향상"으로 귀속 금지 — 이득이 모델 역량 조건부이거나 개입 근거가 없다. `<div>→<button>` 승격은 접근성·의미 개선으로만, 테스트 설명 정리는 사람 가독성 개선으로만 말한다.

마무리: 산출물은 사용자가 저장을 선택할 때만 `.claude/design-principle/<slug>/`(scorecard.json·before-after.md)에 모은다. **커밋은 하지 않는다.**

---

# ═══ Track B — AI 접근성 ═══

> **AI 코딩 에이전트가 코드베이스를 이해하고 안전하게 수정하기 쉬운가**를 6지표로 측정·개선한다(선택 시에만). `ai_access.py`(stdlib only, 독립)가 결정론 assessment를 내고, 지표별로 **문의 후 선택한 방향으로** 승인 개선한다. 정직성 정본: [references/research/ai-accessibility-dossier.md].

## Step B1 — AI 접근성 측정 (ai-access-assessor)

`ai-access-assessor`(**opus**)를 spawn한다. 에이전트는:

1. `python3 skills/design-principle-harness/scripts/ai_access.py <repo> --json .claude/design-principle/<slug>/ai-access.json` 실행.
2. JSON을 **6지표 assessment**로 해석. **SCORED(기계 검증 사실)와 REPORT-ONLY(추론)를 반드시 구분해 제시**한다.

### 6지표 (반드시 유지)

| 지표 | 유형 | 결정론 프록시 | 신뢰(에이전트 이득) |
|------|------|--------------|--------------------|
| **M1 의존성 방향 강제** | **SCORED**(Gate) | dependency-cruiser·eslint-boundaries·import-linter·ArchUnit·Nx·TS refs 설정 존재 + CI fail | 사실 STRONG / agent 이득 inferred(cap) |
| **M2 독립 실행 가능성** | **SCORED**(gate+독립 oracle 가드) | 테스트 러너·워크스페이스·buildability | gate MEDIUM / **독립-oracle 가드 STRONG(유일한 측정 레버)** |
| **M3 빌드 피드백 품질** | report-only | TS strict·typecheck·lint·CI | task-level MEDIUM / repo-level WEAK |
| **M4 모듈 경계 예측 가능성** | report-only | 디렉터리 택소노미 일관성·결합도 | localization 어려움 STRONG / layout 인과 WEAK |
| **M5 패턴 일관성** | report-only | 모듈 시스템 혼용 등(명명은 Track A 담당) | mechanism-inferred |
| **M6 에이전트 가이드** | report-only(약) | CLAUDE.md/AGENTS.md 존재 + non-inferable 내용 | presence≠performance STRONG |

### 정직성 (Step B1 — 반드시 전달)

- **이 assessment는 '에이전트 성공률 인증'이 아니다.** 6지표 중 5개의 '에이전트 이득'은 **측정된 개입이 아니라 인간-SE 이득+첫 원리로부터의 추론**이다(intervention≠correlation). SCORED는 '기계 검증 가능한 사실'(M1 강제 존재·실제 CI fail / M2 실행 가능 gate)뿐.
- **build enforces, docs explain** — 강제된 의존 방향·실행 테스트가 산문 문서보다 신뢰도 높다. **에이전트 가이드 '존재'는 성능 예측자 아님**(arXiv:2602.11988: context 파일이 성공을 안 높이고 LLM-생성본은 5/8에서 낮춤).
- **tool-index ≠ code-structure** — LocAgent(92.7%)·RepoGraph(+32.8%) 이득은 툴 그래프 인덱스의 것이지 layout 공로 아님 → 등급 귀속 금지.
- **유일하게 측정된 agent-specific 레버 = 독립 oracle** — 에이전트 저작 테스트의 격리-green이 실제 정답이 아닌 경우가 실패의 81~100%(arXiv:2606.26978).

게이트: assessment + `[Step B1] build-enforced {n}/{max} · SCORED {M1·M2}, 나머지 report-only — 다음: Step B2 개선(지표별 문의). 진행할까요?`

## Step B2 — 지표별 개선 (ai-access-improver + behavior-guard)

**지표별로 하나씩**, **문의 → 선택 → 계획(게이트 A) → 개별 승인 → 적용 → 검증(게이트 B)**. 큰 틀(Track B) 하위에서도 매 지표마다 사용자에게 문의한다.

### 개선 순서 (build-enforces 우선)

1. **M1 의존성 방향 강제** — dependency-cruiser/eslint-boundaries/import-linter 설정 **추가**(허용 안 된 의존을 물리 차단) + CI 배선. 순환 의존은 방향 정리 후보.
2. **M2 독립 실행 가능성** — 테스트 러너·격리 실행 슬라이스·**독립 ground-truth oracle** 도입(에이전트 저작 테스트와 구별).
3. **M3 빌드 피드백** — tsconfig strict 승격·typecheck 스크립트 추가. **opt-in**.
4. **M4 모듈 경계** — 관례적 택소노미로 재배치 제안. **opt-in·report-only**.
5. **M6 에이전트 가이드** — CLAUDE.md/AGENTS.md에 **non-inferable(빌드/테스트/env 명령·경계·규약)** 내용을 **사람이 작성**. **자동 생성 금지**.

### 각 지표 루프 + 안전 불변식

- `ai-access-improver`(**opus**)가 그 지표의 개선안(변경 목록·위험·근거·신뢰)을 제시 → **게이트 A**. → 개별 승인 → 적용 → `behavior-guard`(**opus**)가 검증 → **게이트 B**.
- **build enforces, docs explain**: 가능하면 산문 규칙이 아니라 **빌드 강제**(lint/CI)로. 설정 추가는 **빌드가 여전히 통과하는지**(기존 코드가 새 규칙에 걸리면 사용자에게 보고·범위 협의).
- **에이전트 가이드 자동 생성 금지**: LLM-생성 context 파일은 성공률을 낮춘다 → 사람이 non-inferable 내용만 큐레이션·bloat/staleness 금지.
- **독립 oracle 가드**: 어떤 개선도 '에이전트 저작 테스트 green'을 correctness로 credit하지 않는다 — 독립 oracle·behavior 센서로 확인.
- **tool-index 오귀속 금지**·**규칙 수/모듈 수/문서 줄 수 가점 금지**(존재·정확성·의미만).
- **위험은 경고, 수용은 사용자**·**execute-or-escalate**·**한 번에 한 지표·한 승인**·**커밋 안 함**.

## Step B3 — 종합 결과 (acceptance-reporter)

`ai_access.py`를 **동일 스코프로 재실행**해 지표별 before→after 델타 + 종합 결과. **정직성**: SCORED 사실 이동(강제 설정 추가·실행 gate)만 자신 있게, report-only 지표는 "개선 후보 이동"으로만. **개입 효과를 고정 에이전트 강제 probe 없이 저장소 등급/에이전트 성공률로 귀속 금지.** 가이드 추가를 "AI 성공률 +N%"로 말하지 않는다.

---

## 근거 (요약 — 전문은 references/)

- **명명·주석의 근거**: 사람 comprehension 근거는 견고하고, 오도/불일치/stale 명명·주석은 LLM에도 해롭다. 단 LLM 대상 식별자 리네임 효과는 부호 불안정·과제 의존이라 **단일 수치로 못 쓴다**(가드레일 #14). → Tier A 가중↑. [references/research/evidence-dossier.md]
- **개입 연구 부재**: 점수를 올리면 같은 에이전트 성공률이 오른다는 연구는 없다(추론 휴리스틱)·에이전트 기여의 가장 강한 신호(실행 가능·의존성 무결성)는 범위 밖 → 총점은 **안전 기여 인증이 아니라 설계 부채 hotspot 지도**. [references/research/README.md]
- **고전 구조 지표의 약함**: cyclomatic·LCOM·Maintainability Index는 코드 길이 통제 시 LLM 성능과 무상관·전부 사람 대상 검증 → Tier B 낮은 confidence·진단. [references/design-principles.md]
- **점수화의 Goodhart 위험**: 설계 스멜을 오라클로 쓰면 표면 변형으로 게임됨 → 총점은 우선순위 진단 지표. [references/scoring-rubric.md]
- **순환 의존만 구조 신호로 상대적 우위**: 툴 측 그래프 인덱스 탐색을 저해 → B4는 Tier B에서 근거가 낫다.
- **안전 개선**: 리네임 AST/LSP·중복은 "잘못된 추상화보다 쌀 수 있음"·구조는 opt-in·"테스트 통과≠동작 보존". [references/improvement-playbook.md]
- **Tier C(시맨틱 마크업·a11y·테스트 설명)는 report-only**: 시맨틱 HTML 이득은 **모델 역량 조건부**(강한 모델=full HTML 유리·약한 모델=a11y-tree 유리, WorkArena L1), landmark/heading/button-vs-div 격리 연구 부재; **ARIA 볼륨은 오히려 오류와 상관**(WebAIM·상관≠인과)이라 native 우선·자동 ARIA 금지; **올바른 테스트 설명의 이해 이득은 미미·오도 설명만 해로움**(비대칭)이고 tests-as-oracle는 overfitting → 삭제 우선·자동 어서션 금지. [references/research/semantic-a11y-test-dossier.md]
- **Track B AI 접근성 — build enforces, docs explain**: 기계 검증 가능 속성(강제된 의존 방향·실행 테스트)만 SCORED, 나머지 지표의 에이전트 이득은 **측정된 개입이 아니라 추론**(6지표 중 5개에 repo-구조 통제 개입 연구 0). **에이전트 가이드 존재≠성능**(arXiv:2602.11988: context 파일이 성공 안 높이고 LLM-생성본 5/8 하락 → 자동 생성 금지)·**tool-index≠code-structure**(LocAgent 92.7%·RepoGraph +32.8%는 툴 이득)·**유일 측정 레버=독립 oracle**(격리-green 81~100% false-pass·arXiv:2606.26978)·**테스트/컴파일 통과를 correctness로 credit 금지**(ImpossibleBench 76% exploit). [references/research/ai-accessibility-dossier.md]

## 경계 (역방향 배제)

- 이 하네스는 **두 축**을 다룬다 — **Track A 코드 본문 설계 품질**(명명·주석·설계 원칙·시맨틱 마크업·테스트 설명)과 **Track B AI 접근성**(의존 방향 강제·모듈 경계·빌드 피드백·독립 실행·에이전트 가이드 등 저장소 구조·강제 층위). 사용자가 선택한 트랙만 수행한다.
- **완성 코드 리뷰·PR·커밋**, **상류 산출물(기획/디자인/API 계약/QA) 핸드오프 게이트**, **하네스 자체 진단·생성**, **한 기능 구현·실행검증**은 범위 밖.
- 이 하네스는 **다른 마켓플레이스 플러그인을 참조·의존하지 않는다**(score.py·ai_access.py·루브릭·근거 모두 내재화·단독 설치로 동작).

## 산출물 배치

- Track A 점수표/재측정: `.claude/design-principle/<slug>/scorecard.json`·`before-after.md` (opt-in 저장).
- Track B assessment/재측정: `.claude/design-principle/<slug>/ai-access.json` (opt-in 저장).
- 스크립트: `skills/design-principle-harness/scripts/score.py`(Track A) · `ai_access.py`(Track B) (둘 다 stdlib only, Python 3.10+).
