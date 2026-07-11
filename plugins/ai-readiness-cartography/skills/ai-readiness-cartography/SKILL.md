---
name: ai-readiness-cartography
description: 임의 git 저장소가 "AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스"인지를 **측정하고(결정론 스코어러) 개선을 설계하는(멀티 에이전트)** 도메인 무관 단일 스킬. 세 모드를 가진다 — **① 측정 모드**: `score.py`(stdlib-only)로 100점·9카테고리 + 3 gate를 결정론 채점해 JSON 점수표 + HTML 대시보드 + ROI 리팩토링 가이드를 낸다. **② 진단·개선 모드**: score.py를 결정론 센서로 삼아 2축(Q 코드품질/A AI접근성) 진단(진단 승인 게이트) → 빌드 가드레일(의존 방향 물리 강제) → standalone 독립 실행 → 수용 증명·재측정을 4에이전트로 설계한다. **③ 코드 본문 층위 모드**: `legibility_scan.py` census(등급 없음)를 seed로 주석·독스트링·변수명/함수명/클래스·컴포넌트명·함수/모듈 granularity를 다각도 진단하고, **3게이트 인간 승인(계획→개별→최종) 뒤에만 단계별로 코드를 수정**한다(P1 오도·stale 주석 삭제→P2 안전 리네임(AST/LSP)→P3 검증된 계약 주석→P4 구조 리팩터 opt-in). 발동 — "이 레포 AI-readiness 점수/등급/대시보드"(①), "agent-friendly한지 정성 진단하고 빌드 가드레일·standalone·수용 증명으로 개선 설계"(②), "코드 품질(Q축)은 괜찮은데 AI 접근성(A축) 낮은 격차 찾아줘", "의존 방향을 빌드에서 물리적으로 강제하게", "AI가 만든 PR에 자동 수용 증명(E2E)", "리팩토링 우선순위를 ROI로", "AI가 읽기 좋게 주석·변수명·함수명 정리하고 승인하면 단계별로 적용"(③), "주석이 코드랑 안 맞는 것 찾아 고쳐줘"(③), "의미 없는 변수명·함수명 리네임 제안"(③), "컴포넌트/모듈명이 하는 일이랑 맞는지 봐줘"(③). 발동 시 **먼저 모드를 확정**한다 — 점수·대시보드로 *측정만*(①), 정성 진단 후 *구조 개선 설계*(②), 주석·명명·granularity를 *AI가 읽기 좋게 진단하고 승인 후 코드 수정*(③). **①②는 코드를 수정하지 않고(제안·설계만), ③만 승인 게이트 뒤에서 코드를 실제로 수정하며 저장소 층 등급을 만들지 않는다(census만).** 발동하지 않는다 — 한 기능의 실행 기반 구현·검증(backend-harness), 코드 착수 전 상류 산출물(기획·디자인·API 계약·QA 인수조건) 핸드오프 게이트 검수(review-harness), 하네스(CLAUDE.md/SKILL.md/agents) 자체를 trace로 진단·개선(meta-harness), 커밋→프로덕션 전달 파이프라인(CI/CD·릴리스·IaC, cicd-harness), 실행 가능 명세(spec) 작성(spec-driven-development), 컨텍스트 페이로드 조립·압축(context-engineering), AI 생성물 평가 judge 구성(eval-harness), 작업 병렬화·협업 토폴로지 설계(agent-orchestration), 완성 코드 리뷰·커밋/PR(frontend/git-harness), 검증 가능 목표 자율 반복 루프(loop-engineering), 새 하네스/에이전트 팀 생성(harness-generator), settings.json 설정 변경.
---

# AI-Readiness Cartography — 코드베이스 AI 준비도 측정·개선

임의 저장소를 **AI-Ready 코드베이스 v3 루브릭**(100점 · 9 카테고리 + 3 gate)으로 **측정**하고, 그 위에서 **구조 개선을 설계**한다. 두 전제 위에 선다 — **"구조가 프롬프트보다 먼저다(structure before prompt)"**, **"코드 품질(Q축)과 AI 접근성(A축)은 다른 차원이다"**. 사람에게 깨끗한 코드라도 패턴 비일관·빌드 피드백 약함·모듈 경계 모호로 에이전트에게는 적대적일 수 있다.

## 세 모드 + 모드 게이트 (먼저 확정하라)

이 스킬은 하나의 저장소 질문을 세 깊이로 다룬다. **발동하면 먼저 한 질문으로 모드를 확정한다.**

| | **① 측정 모드** | **② 진단·개선 모드** | **③ 코드 본문 층위 모드** |
|---|---|---|---|
| 표적 | *점수·시각화 산출물*(저장소 층) | *구조 개선 설계*(저장소 층) | *주석·명명·함수 granularity를 읽기 좋게* |
| 엔진 | `score.py` 1회(결정론) | score.py(센서) + 4 에이전트 | `legibility_scan.py` census + 4 에이전트 |
| 산출 | JSON 점수표·HTML 대시보드·ROI | 진단(2축)·가드레일·standalone·수용 증명 | census + 개입 제안 + **승인 후 단계별 적용(C0~C3)** |
| **코드 수정** | 안 함(제안만) | 안 함(설계만) | **함 — 단, 3게이트 승인 후에만** |
| 등급(0~100) | **낸다** | 낸다(seed) | **안 낸다**(본문층 등급 1차 근거 부재 — census만) |
| 실행 비용 | python 1회 | python + opus 4회 | python + opus 3~4회 |

`[모드 확인] (①) 점수·대시보드로 *측정*, (②) 정성 진단 후 *구조 개선 설계*, (③) *주석·변수명·함수명·granularity를 AI가 읽기 좋게 진단하고 승인하면 단계별로 수정* — 어느 것을 할까요?`

모호하면 물어서 확정한다 — 잘못된 모드는 비싼 오라우팅이다. **①②는 코드를 수정하지 않고(제안·설계만), ③만 승인 게이트 뒤에서 코드를 실제로 수정한다.** ③은 저장소 층 등급을 만들지 않는다(본문 층은 census + 개입 제안뿐).

## 경계 (범위 밖 — 인접 도메인)

한 기능의 실행 기반 구현·검증(backend-harness), 상류 산출물 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인 CI/CD·IaC(cicd-harness), 실행 가능 명세 작성(spec-driven-development), 컨텍스트 페이로드 조립(context-engineering), AI 생성물 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·커밋/PR(frontend/git-harness), settings.json 설정 변경은 범위 밖. 경계가 모호하면 "*코드베이스 자체*의 AI 준비도를 측정·개선하려는 건가요, 아니면 위의 다른 도메인인가요?"로 확인.

## 내재화 원칙 (두 모드 공통)

- **근거 기반 루브릭(evidence-graded)**: v3의 모든 카테고리·가중치는 2025~2026 1차 근거로 조작화됐고, 각 지표에 `auto / heuristic / manual` 라벨 + 근거 등급이 붙는다. 근거 없는 신호를 만점 근거로 쓰지 않는다.
- **gating(blocking > 가산)**: blocking 결함(dangling reference·미작동 test·아키텍처 미강제)이 다른 고득점에 희석되지 않게, 실패한 gate는 등급에 상한을 씌운다(순수 가중합의 오탐 회피).
- **실행·검증 우선**: 정적 문서(A~D)보다 실행 신호(E)가 성공률에 압도적 기여(ORACLE-SWE). 가중치 서열이 근거 서열을 따른다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율 자체는 가점하지 않는다(ETH Zurich 반증). novelty·비중복·command-first만 가점.
- **A축 ≠ Q축(분리)**: 코드 품질(테스트·복잡도·중복)과 AI 접근성(패턴 일관성·빌드 피드백·모듈 경계 예측성·의존 방향 강제·독립 실행·에이전트 가이드·자동 수용)을 별개 축으로 본다. 높은 Q축이 높은 A축을 보장하지 않는다.
- **구조가 프롬프트보다 먼저 · 빌드가 강제하고 문서가 설명한다**: (개선 모드) CLAUDE.md를 늘리는 대신 에이전트가 *틀린 방향으로 갈 수 없게* 구조를 먼저 만든다. 빌드는 "무엇이 불가능한지", 문서는 "무엇이 바람직한지/왜".
- **정직성(과장 금지)**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지. 자동이 flag한 E1 dangling *후보*는 LLM이 확인 후 실 dangling만 gate에 반영한다.
- **자동 우선, 사람 보강**: score.py가 잡는 것은 자동이 더 정확하다. 스크립트 실행 *후* 그 위에 heuristic/manual 항목·강제 판단을 보강한다(처음부터 손채점 금지).
- **제안만(사람 집행)**: 측정·시각화·설계 *제안*만 낸다. 코드를 자동 수정하지 않는다.

## 통합 등급 체계 (단일 — 100점 · 5밴드 · 3 gate)

**하나의 등급 어휘만 쓴다**(별도 L1~L5 수치 스케일은 폐기 — enforcement 축은 Gate-3로 흡수. `점수/20 = L` 같은 선형 변환은 거짓 정밀이라 금지).

| Score | Level | Badge |
|-------|-------|-------|
| 90-100 | **AI-Native** | green |
| 75-89 | **AI-Ready** | green |
| 60-74 | **AI-Assisted** | amber |
| 40-59 | **AI-Fragile** | amber |
| <40 | **AI-Hostile** | red |

**Gates(등급 상한)** — 하나라도 실패하면 총점이 높아도 상한이 씌워진다:
- **Gate-1 Reference Integrity** (dangling reference 0) — *Auto(score.py)*. 실패 시 상한 AI-Fragile.
- **Gate-2 Executable Verification** (실행 가능한 test/build 존재) — *Auto(score.py)*. 실패 시 상한 AI-Fragile.
- **Gate-3 Architecture Enforcement** (금지된 의존 경계 위반이 *실제로 빌드 실패를 일으키는가*) — *Heuristic(진단·개선 모드에서만 판정)*. score.py는 그래프 *가독성*만 재고 이 *강제*는 못 잰다 → **측정 모드에서는 "미평가"**로 표기하고, 개선 모드의 `acceptance-verifier`가 위반 probe로 판정한다. 실패 시 상한 AI-Assisted(구조가 legible해도 물리 강제 없이 AI-Ready 이상 불가).

> Gate-3는 codebase enforcement 축(구 L3 "빌드 통과·아키텍처 위반도 통과" vs L4 "빌드가 아키텍처 물리 강제")을 게이팅 구조로 흡수한 것이다. 측정 모드는 legibility(존재)를, 개선 모드는 그 위에 enforcement(강제)를 판정한다.

보고: `[AI-Readiness] {total}/100 · {grade}{ (gate 상한) } — 최약 {Cat}, Top ROI: {액션} → {산출물 경로}`

## 산출물 배치 (기본, 사용자 지정 가능)

- **측정 모드**: `docs/`가 있으면 `docs/ai-readiness-{map.html,score.json}`, `.claude/`가 있으면 `.claude/ai-readiness-{map.html,score.json}`, 둘 다 없으면 레포 루트.
- **진단·개선 모드**: `.claude/ai-readability/{대상-slug}/`(assessment.md·remediation-plan.md·acceptance-and-regrade.md). Phase 0의 `ai-readiness-score.json`도 여기 둔다.
- **코드 본문 층위 모드**: `.claude/ai-readability/`(census-before.json·census-after.json·proposals.md·verdicts.md). 커밋은 하지 않는다(git-harness 핸드오프).
- 사용자가 경로를 명시하면 그 경로 우선. 문서 언어는 **한국어**.

## 에이전트 팀 (진단·개선 모드)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Assess | `accessibility-assessor` | score.py seed 위에 2축(Q/A) 진단 + 등급(5밴드) + Gate-3 예비판정 + A축 격차·목표·백로그 |
| 1 Guardrails | `guardrail-architect` | 빌드 가드레일 설계(의존 방향 물리 강제 + 피드백 3차원 + 빌드/CLAUDE.md 역할 분담) |
| 2 Standalone | `standalone-designer` | 도메인 슬라이스 독립 실행 설계(port/adapter 치환·use-case seed·커버리지) |
| 3 Acceptance & Re-grade | `acceptance-verifier` | 수용 증명 인프라 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 적대 재측정 |

각 에이전트 정의는 `../../agents/{name}.md`. **모든 Agent 호출은 `model: "opus"`를 명시한다**(진단·설계·재측정의 추론 품질이 산출물 정합성을 좌우).

**코드 본문 층위 모드(③) 에이전트** — `comment-auditor`(주석 4분류→C0·C1)·`naming-analyst`(명명 3축→C2)·`structure-cartographer`(구조 후보→C3·opt-in)·`behavior-guard`(개입 클래스별 센서 실행·관측=checker). 모두 `model: "opus"`.

---

# 측정 모드 워크플로

## M1. 결정론 자동 채점

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <repo-path> \
  --json <output-path>/ai-readiness-score.json
```

스크립트(stdlib only, Python 3.10+)가 자동으로 잡는 것: **E** reference integrity + 실행 test/build/lint + CI · **D** import 그래프 + 결합도 hotspot + workspace · **B** context redundancy·command-first·non-obvious · **C** Five-Question + MEMORY/ADR · **H** pre-commit·타입·lint / **F** stale-drift·path validation / **I** devcontainer·template / **G** evals·telemetry · **Gate-1/2**.

자동이 못 잡는 것(LLM 보강): B command 실효·non-obvious 실제 유효성, C tribal knowledge 깊이, E4 critic 품질, A anchor 정확성. **E1 dangling 후보 확인**: score.py가 flag한 dangling path를 열어 실 dangling인지(placeholder/illustrative 아닌지) 확인 후 실 dangling만 gate에 반영. **Gate-3는 측정 모드에서 "미평가"**(개선 모드 필요).

## M2. JSON으로 HTML 대시보드 채우기

`assets/template.html`을 복사한 뒤 JSON 값을 끼워 넣는다(**처음부터 쓰지 말 것** — 복사 → 수정).

**이스케이프(non-negotiable·보안)**: 대시보드 채움에는 반드시 score.py가 함께 출력한 **`*.htmlsafe.json`**(모든 문자열 `html.escape` 사전 이스케이프 사본)만 사용한다 — 원본 JSON 문자열을 HTML에 직접 넣지 말 것. git 브랜치명·파일 경로·findings는 `<script>` 같은 문자를 합법적으로 포함할 수 있는 신뢰 불가 입력이라 이스케이프는 LLM 판단이 아닌 결정론 코드로 강제한다.

바꿀 블록: **헤더**(repo·날짜·branch·modules·context/code files·dangling_refs) · **Gate strip**(Gate-1/2 pass/fail + Gate-3 "미평가", 실패 시 빨간 배지 + "등급 상한") · **Score hero**(`total`·`grade`, capped면 `raw_grade` 병기·최약 2개) · **9 카테고리 막대차트**(근거 서열 E22·D18·B15·C12·H9·A8·F8·I5·G3, 색: ≥0.75 green·0.5-0.74 amber·<0.5 red) · **구조 맵(SVG)**(대형 파일은 *결합도* 우선, 라인 수는 보조) · **Wins/Top ROI**(`actions` 상위 5-7, gate 해소 최상단) · **푸터**.

## M3. 브라우저에서 열기

```bash
open <output-path>/ai-readiness-map.html    # macOS  (Linux: xdg-open)
```
사용자가 "열지 마라" 하면 경로만 알린다.

## M4. ROI 리팩토링 가이드 + 요약 보고

한 문단으로: ① 총점/등급(capped면 "gate 상한" 병기) ② 실패한 gate + 왜 blocking인지 ③ 최약 카테고리 1-2개 + 한 줄 진단(근거 인용) ④ Top 3 ROI 액션(effort·impact·evidence grade, gate 해소 우선) ⑤ 생성된 파일 경로. **구조 개선까지 원하면 진단·개선 모드로 이어진다**고 안내.

---

# 진단·개선 모드 워크플로

측정(score.py)을 seed로 삼아 4단계로 개선을 설계한다. 각 단계 보고: `[Phase n] {산출물}: {핵심} — {다음|보정}`.

## Phase 0 — 진단 (Assess) · 진단 승인 게이트

**결정론 측정 → 정성 보강** 순(손채점 금지).

### 0a. 결정론 측정 (score.py seed)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <대상 경로> \
  --json .claude/ai-readability/{대상-slug}/ai-readiness-score.json
```

이 `score.json`(categories E/D/B/C/H/A/F/I/G·gates·ROI `actions` 백로그)이 진단 seed이자 Phase 3 재측정 baseline. score.py가 결정론으로 잡는 것은 손으로 다시 추정하지 않는다.

### 0b. 정성 보강 진단 (accessibility-assessor)

```
Agent(
  subagent_type="accessibility-assessor", model="opus",
  prompt="""
  [역할] score.json을 seed로 삼아, score.py가 못 재는 A축 강제·행위 신호를 더해 2축(Q/A) 진단 + 등급(5밴드) + Gate-3 예비판정을 증거 기반으로 낸다.
  [입력] 진단 대상: {대상 경로/서비스/모듈}, 결정론 seed: {ai-readiness-score.json 경로/내용}, 빌드·언어·아키텍처: {있으면}
  [규칙] score.py가 결정론으로 잡은 legibility/존재 신호(참조 무결성·import 그래프·결합도·redundancy·pre-commit/타입/lint·devcontainer)는 다시 손으로 추정하지 말고 그 점수를 인용한다.
         이 에이전트가 더하는 것은 score.py가 못 재는 강제·행위 판단 — ★ Gate-3 의존 방향 *강제*("금지 경계 위반이 실제 빌드 실패를 일으키는가"; score.py는 그래프 가독성만 봄), 빌드 피드백 3차원 품질, 자동 수용 가능성. 위반 케이스나 빌드 설정을 file:line으로 인용(자기보고 불신).
         등급은 단일 5밴드(AI-Native/Ready/Assisted/Fragile/Hostile)로만 매긴다. Gate-3 실패(강제 없음)면 상한 AI-Assisted. 높은 Q축≠높은 A축을 드러낸다. score.json의 ROI `actions` 백로그를 담당 Phase(1/2/3)로 태깅한다. 증거 확보 불가는 '검증 불가'로 분리. 코드를 고치지 않는다(진단만).
  [출력] AI 접근성 진단 리포트(seed 인용·A축 강제/행위 지표별·5밴드 등급·Gate-3 판정·Phase 태깅 백로그·가정).
  """
)
```

진단 리포트를 보여주고 **진단 승인 게이트**:

`[Phase 0] AI 접근성 진단 — 현재 {grade}(Gate-3 {pass/fail}), 목표 {grade}, A축 격차 N개. 다음: 빌드 가드레일 설계(Phase 1). 승인할까요?`

승인 전에는 개선 설계로 진행하지 않는다. 승인된 진단을 `assessment.md`로 write(없을 때만 디렉토리 생성).

## Phase 1 — 구조·가드레일 (Guardrails)

```
Agent(
  subagent_type="guardrail-architect", model="opus",
  prompt="""
  [역할] 핵심 아키텍처 규칙을 빌드/컴파일 계층으로 옮겨 물리적으로 강제하고, 빌드 피드백을 에이전트가 학습하게 설계한다.
  [입력] Phase 0 진단(A축 격차·백로그·현재/목표 등급·Gate-3): {Phase 0 산출물}, 빌드·언어·모듈 구조: {있으면}
  [규칙] '빌드가 강제하고 문서가 설명한다' — 빌드는 무엇이 불가능한지(의존 방향·모듈 구조·스타일), CLAUDE.md는 무엇이 바람직한지/왜.
         가장 중요한 가드레일은 '금지된 의존을 빌드에서 불가능하게'(린트 통과 가능 < 빌드 통과 불가) — 이것이 Gate-3를 통과시킨다.
         빌드 피드백을 3차원(위치 특정성·원인 명확성·수정방향 추론가능성)으로 개선하고, 검증을 앞단으로(컴파일>런타임, 타입>컴파일 체크) 옮긴다.
         규칙별로 빌드 강제/문서 설명/둘 다를 분담표로 명시하고, 빌드로 못 잡는 것(설계 판단·맥락)은 문서/리뷰로 분리한다.
         Convention Plugin/Gradle은 예시 — 원리를 사용자 스택으로 환산한다. 코드를 자동 수정하지 않고 설계·제안만.
  [출력] 빌드 가드레일 설계(빌드 강제 규칙·의존 방향 강제·피드백 개선·앞단화·역할 분담표·미해결).
  """
)
```

설계를 검토하고 `remediation-plan.md`에 Phase 1 섹션으로 write/append.

## Phase 2 — 독립 실행 (Standalone)

```
Agent(
  subagent_type="standalone-designer", model="opus",
  prompt="""
  [역할] 도메인 슬라이스를 전체 시스템 없이 독립 실행·검증 가능한 self-contained 환경으로 설계한다.
  [입력] Phase 0 진단(독립 실행 격차) + Phase 1 가드레일 설계(모듈 경계·의존 방향): {Phase 0·1 산출물}
  [규칙] Port/Adapter 의존성 역전으로 운영 어댑터를 테스트 어댑터로 치환한다(도메인 로직 불변, 복잡성은 Filter/경계에 격리).
         필요한 도메인만 선택 조합하고 운영 전용 모듈은 전이 의존에서 명시적으로 제외한다.
         seed 데이터는 Repository 직접 호출이 아니라 UseCase 경유로 생성한다(비즈니스 검증 경로를 타게 — 지름길 금지).
         외부 의존은 컨테이너화하고 단일 명령으로 기동되게 한다. 독립 검증 커버리지(독립 실행 가능 슬라이스 비율)를 낸다.
         Hexagonal/Spring/Gradle은 예시 — 원리를 사용자 스택으로 환산한다. 코드를 자동 수정하지 않고 설계·제안만.
  [출력] Standalone 실행 설계(모듈 조합·어댑터 치환·UseCase seed·외부 의존·기동·커버리지).
  """
)
```

설계를 검토하고 `remediation-plan.md`에 Phase 2 섹션으로 append.

## Phase 3 — 수용 증명·재측정 (Acceptance & Re-grade)

재측정은 **결정론 델타 + 정성 강제 probe** 두 층.

### 3a. 결정론 재측정 (score.py 재실행)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <대상 경로> \
  --json .claude/ai-readability/{대상-slug}/ai-readiness-score.after.json
```

Phase 0의 `ai-readiness-score.json`과 diff해 `total`·`grade`·`gates`·카테고리 델타를 낸다. 이 수치는 재현 가능·협상 불가라 **등급을 자기보고로 부풀리지 못하게 하는 결정론 방어**다. 재실행 불가면 BLOCKED.

### 3b. 정성 강제 probe + 수용 증명 (acceptance-verifier)

```
Agent(
  subagent_type="acceptance-verifier", model="opus",
  prompt="""
  [역할] Phase 1·2 설계자와 분리된 독립 검증자로서 ① 수용 증명(자동 E2E·데모) 인프라를 설계하고 ② 결정론 델타(score.py 재실행) 위에 강제 probe를 얹어 Gate-3·등급을 적대 재측정한다.
  [입력] Phase 0 seed(ai-readiness-score.json) + Phase 3a 재실행 결과(ai-readiness-score.after.json) + Phase 1 가드레일 설계 + Phase 2 standalone 설계 (+ 개선 적용본 있으면): {산출물}
  [규칙] 결정론 델타(total·gate·카테고리 변화)를 인용하되, score.py는 구조의 *존재*만 재고 *강제*는 못 재므로 그것만으로 등급을 올리지 않는다.
         결정적 판정 '이제 금지 경계 위반이 실제 빌드 실패를 일으키는가'(Gate-3)는 위반 케이스를 직접 만들어 관측한다(score.py로 대체 불가). 결정론 델타가 올랐어도 강제 probe가 red build를 못 내면 Gate-3 실패로 상한 AI-Assisted 유지.
         수용 증명은 리뷰를 '동작하나→설계가 좋은가'로 옮긴다(문서가 아니라 빌드가 지킨다). 못 잡는 것(성능·보안 인가 우회·동시성 정합·가독성)은 사람 몫으로 반드시 명시(과신 금지). green ≠ 개선, reward-hacking 의심·역점검.
         Phase 0 백로그의 각 격차(G1, G2…) 해소를 증거와 함께 귀속하고, 미해소는 되돌릴 Phase로 라우팅. 증거 확보 불가는 '미달'이 아니라 '검증 불가(BLOCKED)'로 분리. 코드를 자동 수정하지 않고 설계·Verdict만.
  [출력] 수용 증명 설계 + 등급 재측정 Verdict(결정론 델타·Gate-3 강제 probe 증거·한계·격차 해소·BLOCKED·결론·라우팅).
  """
)
```

재측정 결과 분기:
- **목표 등급 도달 + Gate-3 통과 + 격차 증거 해소** → `acceptance-and-regrade.md`에 Verdict를 write하고 **완료 종료**.
- **격차 미해소** → 빌드 강제 미흡(Gate-3 실패)이면 `guardrail-architect`(Phase 1) 재호출, 격리 불가면 `standalone-designer`(Phase 2), 진단 자체가 틀렸으면 `accessibility-assessor`(Phase 0)로 라우팅.
- **검증불가(BLOCKED)** → 미달로 두지 말고 빌드·E2E 환경/위반 케이스 확보를 보정(거짓 미달 방지). 미달 카운트에 산입하지 않는다.
- **reward-hacking 의심(delta green인데 구조 미변경·Gate-3 미강제)** → 등급 상승을 거절하고 근거를 제시한 뒤 해당 Phase로 되돌린다.

## 개선 모드 마무리 — 결과 보고

보고 형식(최종): `[AIRC 완료] {grade before} → {grade after}(Gate-3 {pass/fail}), A축 격차 {해소}/{전체} — 재측정 {증거 PASS|미달|BLOCKED} → .claude/ai-readability/{대상-slug}/`

---

# 코드 본문 층위 모드 워크플로 (③ · 승인 후 코드 수정)

**이 모드만 코드를 실제로 수정한다 — 3게이트 승인 뒤에만.** 저장소 층 등급을 만들지 않는다(census + 개입 제안뿐). 개입 우선순위는 직관이 아니라 위험조정 근거다 — **P1 오도·stale 주석 삭제(효과 확실·위험 0) → P2 안전 리네임 → P3 검증된 계약 주석 추가 → P4 구조 리팩터(기본 OFF)**. 정본은 [`references/intervention-catalog.md`](references/intervention-catalog.md), 원리는 [`references/legibility-principles.md`](references/legibility-principles.md), 근거는 [`references/research/body-legibility/`](references/research/body-legibility/README.md).

| 클래스 | 개입 | 우선순위 | 동작 위험 | 기본값 |
|--------|------|---------|----------|--------|
| **C0** | 오도·stale 주석 삭제/수정 | **P1** | 없음 | ON |
| **C1** | 계약·불변식 주석 추가/수정 | P3 | 없음(사실성 ~20~45%) | ON |
| **C2** | 무의미·오도 식별자 안전 리네임 | **P2** | 참조·컴파일 깨짐 | ON |
| **C3** | 구조 리팩터(추출·이동·분할) | P4 | **높음**(19~35% 비등가) | **OFF·opt-in** |

## B0 — 초기 문의 (스코프 확정)
- **대상 경로**(스킵=레포 루트) + **개입 클래스 체크박스(C0/C1/C2/C3) = 구속 스코프**(밖은 "추가 안 함" 표기·확장 문의).
- **C3 켜면 경고**: "구조 리팩터가 에이전트 성공률을 올린다는 직접 측정 근거는 없습니다(추론). LLM 리팩터의 19~35%가 비등가, 그중 ≈21%는 테스트를 통과합니다." + **테스트 스위트 존재 확인**(없으면 C3 거부).
- **C2 선택 시 안전 리네임 도구 탐지**(rope·pyright / ts-morph·tsserver / gopls / rust-analyzer). 없으면 C2를 "제안만"으로 강등.

## B1 — census + 다각도 진단
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/legibility_scan.py <root> \
  --axes <naming,comments,structure 중 선택된 것> --out .claude/ai-readability/census-before.json
```
census(등급 없음·`auto-high/auto-med/heuristic/report-only` 라벨)를 seed로, 선택된 클래스에 해당하는 에이전트만 병렬 호출(모두 `model: "opus"`): [`comment-auditor`](../../agents/comment-auditor.md)(C0/C1)·[`naming-analyst`](../../agents/naming-analyst.md)(C2)·[`structure-cartographer`](../../agents/structure-cartographer.md)(C3만). `skipped`·`coverage`(미측정≠결함 없음)를 함께 읽는다. **에이전트는 파일을 수정하지 않는다.**

## B2 — 제안표 + 게이트 A (계획 승인)
[`references/intervention-catalog.md`](references/intervention-catalog.md) 랭킹(위험조정 기대이익)으로 제안표(#·클래스·위치·현재→제안·근거·동작위험·1급센서·판정상한 VERIFIED/FAILED/**UNVERIFIED**). **계획 승인 없이는 어떤 파일도 수정하지 않는다.**

## B3 — 개별 순차 적용 + 게이트 B (개별 승인)
한 건씩, **게이트 B 개별 승인 후에만** 적용. 리네임은 **AST/LSP 도구에 위임**(문자열 치환 금지). **generator≠checker**: 제안 에이전트가 아니라 [`behavior-guard`](../../agents/behavior-guard.md)가 개입 클래스별 센서(컴파일/타입체크·참조 완전성·테스트·사람 diff)를 **실행해 관측**. **"테스트 통과=동작 보존" 금지**(비등가 ≈21%가 테스트 통과) — C3는 최선에도 **UNVERIFIED** 상한.

## B4 — 재확인 + 게이트 C (최종 승인)
census 재측정(`census-after.json`) 델타로 개입 반영을 결정론 확인(에이전트 성공률 대리 지표 아님). **커밋하지 않는다** — `git-harness` 핸드오프 제안만. 산출물: `.claude/ai-readability/`(census-before/after·proposals·verdicts).

> **B-모드 불변식**: 3게이트(계획 A→개별 B→최종 C) 건너뛰지 않음 · 스코프 가드(선택 클래스 안에서만) · 등급 안 만듦(본문층 census만) · 자기보고 불신(센서 실행 관측) · 리네임=도구 위임 · 구조 효과=추론·수치 약속 없음.

## Style rules (측정 모드 대시보드 — non-negotiable)

- **폰트**: Inter(본문)·JetBrains Mono(숫자/코드). 오프라인/폐쇄망이거나 외부 요청을 원치 않으면 Google Fonts `<link>` 제거 + 시스템 폰트 폴백(`-apple-system, system-ui`).
- **색**: 템플릿 CSS 변수 팔레트 고정. 배경 `#fafafa` light. 다크 모드 만들지 않음.
- **장식 금지**: 컴퍼스 로즈·양피지·필기체·이모지·스탬프 없이. 이름이 cartography라고 지도 은유 강하게 쓰지 말 것.
- **차트 라이브러리 금지**: 모든 시각화는 인라인 SVG + CSS.

## Common pitfalls

- **모드 미확정** — 측정만 원하는데 opus 4회를 돌리거나 그 반대. 발동 시 모드 게이트 먼저.
- **루브릭이 v3임을 잊고 v2(7카테고리)로 채점** — 현재는 9 카테고리 + 3 gate / 100점, gating 집계.
- **gate를 가산 점수로 착각** — gate는 등급 *상한*이다(Gate-1/2 실패→AI-Fragile, Gate-3 실패→AI-Assisted). 카테고리 점수는 그대로 합산하되 등급만 캡.
- **Gate-3를 score.py가 잰다고 착각** — score.py는 그래프 *가독성*만 잰다(강제 미측정). Gate-3는 개선 모드의 위반 probe로만 판정, 측정 모드는 "미평가".
- **폐기된 L1~L5로 등급 매김** — 단일 5밴드만 쓴다. `점수/20=L` 선형 변환은 거짓 정밀(금지).
- **E1 dangling 후보 무비판 반영** — 자동 flag를 LLM이 확인(placeholder 제외).
- **"보유율"에 가점** — v3는 커버리지 %를 점수화하지 않는다(근거 반증). anchor 명시성에 점수.
- **god-file을 라인 수로 판정** — 결합도(fan-in/out)가 1급. 라인 수는 "근거 약함" 보조.
- **템플릿 무시하고 처음부터 쓰기** — 복사 → 수정.
- **정량 수치 과장** — 근거 등급·CAVEAT 없이 "개선 N% 보장" 금지.

## Files

- `scripts/score.py` — v3 결정론적 스코어러(gating·import 그래프·결합도·reference integrity, htmlsafe.json 동시 출력). stdlib only.
- `scripts/test_score.py` — 회귀 테스트(가중치 불변식·골든 픽스처·Gate-1 정밀도·htmlsafe).
- `references/scoring-rubric.md` — v3 루브릭(9 카테고리 + 3 gate, 근거 등급·auto/manual 라벨).
- `references/ai-readable-codebase-principles.md` — 개선 모드 원리(2축·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern).
- `references/research/`·`references/ai-readiness-cartography-research.md`·`references/ai-readable-codebase-research.md` — 2025~2026 1차 근거(적대 검증). 루브릭·원리 조작화의 출처.
- `assets/template.html` — 복사 후 채울 대시보드 원본.
- `../../agents/{accessibility-assessor,guardrail-architect,standalone-designer,acceptance-verifier}.md` — 개선 모드 4 에이전트(model: opus).
- `scripts/legibility_scan.py`·`scripts/test_legibility_scan.py` — **코드 본문 층위 모드(③)** census 스캐너(stdlib only·등급 없음·7 탐지기) + 회귀 테스트.
- `references/intervention-catalog.md`·`references/legibility-principles.md`·`references/research/body-legibility/` — 본문 층위 개입 카드(C0~C3)·원리·근거 dossier.
- `../../agents/{comment-auditor,naming-analyst,structure-cartographer,behavior-guard}.md` — 본문 층위 모드 4 에이전트(model: opus).
