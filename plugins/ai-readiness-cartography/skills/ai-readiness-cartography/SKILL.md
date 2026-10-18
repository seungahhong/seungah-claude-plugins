---
name: ai-readiness-cartography
description: git 저장소가 AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스인지를 측정하고 개선하는 스킬. 자유 조합하는 세 모드 — ① 측정(score.py로 100점·9카테고리·3 gate 결정론 채점 → JSON 점수표·HTML 대시보드·ROI 가이드, 코드 수정 없음) ② 진단·개선(측정을 센서로 코드품질/AI접근성 2축 진단 → 빌드 가드레일 → standalone → 승인 게이트 뒤 코드 적용 → 재측정) ③ 코드 본문(legibility_scan.py census를 seed로 주석·명명·구조를 진단하고 3게이트 승인 뒤 단계별 수정). "이 레포 AI-readiness 점수/등급/대시보드 만들어줘", "agent-friendly한지 진단하고 빌드 가드레일·standalone으로 개선해줘", "의존 방향을 빌드에서 물리적으로 강제하게 해줘", "AI가 읽기 좋게 주석·변수명·함수명 정리하고 승인하면 단계별로 적용해줘", "주석이 코드랑 안 맞는 것 찾아 고쳐줘"처럼 요청할 때 사용한다. 발동하면 실행할 모드를 먼저 확정하고 세부는 한 번에 한 질문씩 묻는다. 한 기능의 구현·검증, 상류 산출물 검수, 완성 코드 리뷰·커밋에는 쓰지 않는다.
---

# AI-Readiness Cartography — 코드베이스 AI 준비도 측정·개선

임의 저장소를 **AI-Ready 루브릭 v3**(100점 · 9 카테고리 + 3 gate)으로 **측정**하고, 그 위에서 개선을 **설계·적용**한다. 두 전제 위에 선다 — **"구조가 프롬프트보다 먼저다"**, **"코드 품질(Q축)과 AI 접근성(A축)은 다른 차원이다"**. 사람에게 깨끗한 코드라도 패턴 비일관·빌드 피드백 약함·모듈 경계 모호로 에이전트에게는 적대적일 수 있다.

## 세 모드 (자유 조합 · 먼저 스코프 확정)

| | **① 측정** | **② 진단·개선** | **③ 코드 본문** |
|---|---|---|---|
| 표적 | 점수·시각화(저장소 층) | 구조 개선(저장소 층) | 주석·명명·구조를 읽기 좋게(본문 층) |
| 엔진 | `score.py` 1회 | score.py(센서) + 4 에이전트 | `legibility_scan.py` census + 4 에이전트 |
| 산출 | JSON 점수표·HTML 대시보드·ROI | 진단(2축)·가드레일·standalone·수용 증명 + 적용 | census + 개입 제안(C0~C3) + 적용 |
| 코드 수정 | 안 함(측정만) | **계획·개별 승인 후** | **3게이트 승인 후** |
| 등급(0~100) | 낸다 | 낸다(seed) | **안 낸다**(본문층 등급 1차 근거 부재) |
| 비용 | python 1회 | python + opus 4~5회 | python + opus 3~4회 |

`[모드 확인] 무엇을 할까요? (복수 선택 가능) — (①) 점수·대시보드로 *측정*, (②) 정성 진단 후 *구조 개선 설계·적용*, (③) *주석·명명·구조를 진단하고 승인 후 단계별 수정*. 여러 개면 ①→②③ 순으로 이어 수행합니다.`

**문의는 한 번에 하나씩** — 모드를 확정한 *뒤에* 세부 스코프(대상 경로 → 축 → 개입 클래스 → 고위험 opt-in)를 하나씩 묻는다. 한꺼번에 나열해 던지면 사용자가 고르지 못한 채 넘어가고, 그게 곧 잘못된 스코프다. 직전 답이 다음 질문을 결정한다(예: ③에서 구조 축을 안 골랐으면 고위험 opt-in은 묻지 않는다).

### 조합 실행 규약
- **순서 고정 ①→②→③** — 측정 → 구조 적용(계획·개별 승인) → 본문 수정(3게이트). ②가 구조를 먼저 바꾸고 ③이 그 위에서 본문을 정리한다(③은 ② 이후 census 재실행).
- **score.py는 한 번만** — ①의 산출물과 ②의 Phase 0 seed는 같은 실행을 공유한다(재실행 금지). ①+②면 ②는 ①의 `score.json`을 seed로 삼고, Gate-3 상한이 반영된 ②의 등급이 최종이다. ③은 `legibility_scan.py`를 별도로 한 번 돌린다.
- **Gate-3 표기 일원화** — ②가 함께 돌면 Gate-3는 ②의 위반 probe 판정이 최종이고 측정 산출물의 "미평가"를 덮어쓴다.
- **②+③ 겹침 제거** — 둘 다 고르면 구조 리팩터는 **②가 설계·적용으로 소유**하고 ③의 **C3는 끈다**(이중 처리 금지). ③은 C0·C1·C2만 적용한다.
- **등급은 합치지 않는다** — 저장소 층 등급은 score.py에서만 나온다. ③의 census는 등급이 아니며 총점에 접붙이지 않는다. ①이 낸 등급은 ②③ 적용 *이전* 스냅샷이고, 적용 효과를 강제 probe 없이 등급 델타·툴그래프 수치로 귀속하지 않는다(오귀속·Goodhart 금지). ②의 재측정은 Phase 4 score.py 델타 + 강제 probe로만.
- **산출물 경로 분리** — ①은 `docs/`·`.claude/`의 `ai-readiness-*`, ②③은 `.claude/ai-readability/{대상-slug}/`(②=assessment·remediation·score, ③=census·proposals·verdicts). 한 실행에서 서로 덮어쓰지 않는다.

모호하면 물어서 확정한다 — 스코프를 틀리면 비싼 오라우팅이다. ②③ 모두 **커밋하지 않는다**(git-harness 핸드오프).

## 경계 (범위 밖)

한 기능의 실행 기반 구현·검증(backend-harness), 상류 산출물 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인 CI/CD·IaC(cicd-harness), 실행 가능 명세 작성(spec-driven-development), 컨텍스트 페이로드 조립(context-engineering), AI 생성물 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·커밋/PR(frontend/git-harness), settings.json 설정 변경은 범위 밖. 모호하면 "*코드베이스 자체*의 AI 준비도를 측정·개선하려는 건가요, 아니면 위의 다른 도메인인가요?"로 확인.

## 내재화 원칙 (세 모드 공통)

- **근거 기반 루브릭**: 카테고리·가중치는 2025~2026 1차 근거로 조작화됐고 각 지표에 `auto / heuristic / manual` 라벨 + 근거 등급이 붙는다. 근거 없는 신호를 만점 근거로 쓰지 않는다.
- **gating(blocking > 가산)**: blocking 결함(dangling reference·미작동 test·아키텍처 미강제)이 다른 고득점에 희석되지 않게, 실패한 gate는 등급에 **상한**을 씌운다(순수 가중합의 오탐 회피).
- **실행·검증 우선**: 정적 문서(A~D)보다 실행 신호(E)가 성공률에 압도적으로 기여한다(ORACLE-SWE). 가중치 서열이 근거 서열을 따른다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율 자체는 가점하지 않는다(ETH Zurich 반증). novelty·비중복·command-first만 가점.
- **A축 ≠ Q축**: 코드 품질(테스트·복잡도·중복)과 AI 접근성(패턴 일관성·빌드 피드백·모듈 경계 예측성·의존 방향 강제·독립 실행·자동 수용)은 별개 축이다. 높은 Q축이 높은 A축을 보장하지 않는다.
- **빌드가 강제하고 문서가 설명한다**: CLAUDE.md를 늘리는 대신 에이전트가 *틀린 방향으로 갈 수 없게* 구조를 먼저 만든다. 빌드는 "무엇이 불가능한지", 문서는 "무엇이 바람직한지/왜".
- **자동 우선, 사람 보강**: score.py가 잡는 것은 자동이 더 정확하다. 스크립트 실행 *후* 그 위에 heuristic/manual 항목을 보강한다(처음부터 손채점 금지). 자동이 flag한 E1 dangling은 *후보*이므로 LLM이 확인 후 실 dangling만 gate에 반영한다.
- **정직성**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지.
- **승인 게이트 뒤에만 수정**: ①은 측정만. ②③은 제안·설계 후 승인 게이트(②=계획·개별, ③=3게이트) 뒤에 코드를 수정하며, 고위험 변경은 opt-in·리네임은 AST/LSP 위임·센서는 `behavior-guard`가 실행 관측·**"테스트 통과 ≠ 동작 보존"**을 지키고 커밋하지 않는다.
- **결정 권한 — 위험은 경고, 수용은 사용자**: 고위험 변경(②의 L 구조 리팩터·③의 C3)의 위험을 *경고*하는 것은 에이전트 몫이지만 그 위험을 *감수할지 결정*하는 것은 사용자 몫이다. 사용자가 경고를 보고 opt-in 했고 개별 승인했으면 **가용한 최강 센서를 돌려 적용한다** — 자기 위험 판단으로 조용히 보류·강등·"제안만"으로 되돌리지 않는다(승인 게이트는 무단 실행을 막는 장치이지 승인된 실행의 veto가 아니다). 적용 중 *새로운* 차단 요인이 드러나면 **execute-or-escalate**로 사용자에게 결정을 되돌린다. **자동 테스트 부재는 거부 사유가 아니라 행위 센서(실제 실행·렌더로 baseline 대조) 승격 사유**다. "리팩토링" 요청을 안전 추가형 툴링으로 대체 충족하지 않는다(과소 인도 금지).

## 등급 체계 (100점 · 5밴드 · 3 gate)

**하나의 등급 어휘만 쓴다**(별도 L1~L5 수치 스케일은 폐기 — enforcement 축은 Gate-3로 흡수. `점수/20 = L` 같은 선형 변환은 거짓 정밀이라 금지).

| Score | Level | Badge |
|-------|-------|-------|
| 90-100 | **AI-Native** | green |
| 75-89 | **AI-Ready** | green |
| 60-74 | **AI-Assisted** | amber |
| 40-59 | **AI-Fragile** | amber |
| <40 | **AI-Hostile** | red |

**Gates(등급 상한)** — 하나라도 실패하면 총점이 높아도 상한이 씌워진다:
- **Gate-1 Reference Integrity**(dangling reference 0) — *Auto(score.py)*. 실패 시 상한 AI-Fragile.
- **Gate-2 Executable Verification**(실행 가능한 test/build 존재) — *Auto(score.py)*. 실패 시 상한 AI-Fragile.
- **Gate-3 Architecture Enforcement**(금지된 의존 경계 위반이 *실제로 빌드 실패를 일으키는가*) — *Heuristic(개선 모드에서만 판정)*. score.py는 그래프 *가독성*만 재고 이 *강제*는 못 잰다 → **측정 모드에서는 "미평가"**, 개선 모드의 `acceptance-verifier`가 위반 probe로 판정. 실패 시 상한 AI-Assisted(구조가 legible해도 물리 강제 없이 AI-Ready 이상 불가).

보고: `[AI-Readiness] {total}/100 · {grade}{ (gate 상한) } — 최약 {Cat}, Top ROI: {액션} → {산출물 경로}`

## 산출물 배치 (기본, 사용자 지정 가능)

- **①**: `docs/`가 있으면 `docs/ai-readiness-{map.html,score.json}`, `.claude/`가 있으면 `.claude/ai-readiness-*`, 둘 다 없으면 레포 루트.
- **②**: `.claude/ai-readability/{대상-slug}/`(assessment.md · remediation-plan.md(Applied 섹션 포함) · acceptance-and-regrade.md · ai-readiness-score.json).
- **③**: 같은 `.claude/ai-readability/{대상-slug}/`(census-before/after.json · proposals.md · verdicts.md). 단독 실행이면 slug 없이 `.claude/ai-readability/`.
- 사용자가 경로를 명시하면 그 경로 우선. 문서 언어는 **한국어**.

## 에이전트 팀

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| ② 0 Assess | `accessibility-assessor` | score.py seed 위에 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정 + A축 격차·백로그 |
| ② 1 Guardrails | `guardrail-architect` | 빌드 가드레일 **설계**(의존 방향 물리 강제 + 피드백 3차원 + 빌드/CLAUDE.md 역할 분담) |
| ② 2 Standalone | `standalone-designer` | 도메인 슬라이스 독립 실행 **설계**(port/adapter 치환·use-case seed·커버리지) |
| ② 3 Apply | 오케스트레이터 + `behavior-guard` | 설계를 위험 등급별(S/M/L) 계획표로 전개 → 계획 승인 → 개별 승인 후 적용 |
| ② 4 Acceptance | `acceptance-verifier` | 수용 증명 인프라 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 적대 재측정 |
| ③ | `comment-auditor` · `naming-analyst` · `structure-cartographer` · `behavior-guard` | 주석 4분류→C0/C1(+comment-gap) · 명명 3축→C2 · 구조 후보→C3(opt-in) · 센서 실행 관측 |

각 정의는 `../../agents/{name}.md`. **모든 Agent 호출에 `model: "opus"`를 명시한다**(진단·설계·재측정의 추론 품질이 산출물 정합성을 좌우). **선택된 축·클래스에 해당하는 에이전트만 호출한다**(스코프 가드). `behavior-guard`는 ②의 적용과 ③ 양쪽에서 재사용한다(generator≠checker).

---

# ① 측정 모드 워크플로

## M1. 결정론 자동 채점

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <repo-path> \
  --json <output-path>/ai-readiness-score.json
```

스크립트(stdlib only, Python 3.10+)가 자동으로 잡는 것: **E** reference integrity + 실행 test/build/lint + CI · **D** import 그래프 + 결합도 hotspot + workspace · **B** context redundancy·command-first·non-obvious · **C** Five-Question + MEMORY/ADR · **H** pre-commit·타입·lint / **F** stale-drift·path validation / **I** devcontainer·template / **G** evals·telemetry · **Gate-1/2**.

자동이 못 잡는 것(LLM 보강): B command 실효·non-obvious 실제 유효성, C tribal knowledge 깊이, E4 critic 품질, A anchor 정확성, **E1 dangling 후보 확인**(placeholder/illustrative 걸러 실 dangling만 gate 반영), **Gate-3**(개선 모드 필요 — 단독 실행이면 "미평가").

## M2. JSON으로 HTML 대시보드 채우기

`assets/template.html`을 **복사한 뒤** JSON 값을 끼워 넣는다(처음부터 쓰지 말 것).

**이스케이프(non-negotiable·보안)**: 대시보드 채움에는 score.py가 함께 출력한 **`*.htmlsafe.json`**(모든 문자열 `html.escape` 사전 이스케이프 사본)만 사용한다. git 브랜치명·파일 경로·findings는 `<script>` 같은 문자를 합법적으로 포함할 수 있는 신뢰 불가 입력이라, 이스케이프는 LLM 판단이 아닌 결정론 코드로 강제한다.

바꿀 블록: **헤더**(repo·날짜·branch·modules·context/code files·dangling_refs) · **Gate strip**(Gate-1/2 pass/fail + Gate-3 "미평가" — **①+② 조합이면 ②의 probe 판정을 채우고 대시보드는 그 확정 후 렌더**, 실패 시 빨간 배지 + "등급 상한") · **Score hero**(`total`·`grade`, capped면 `raw_grade` 병기·최약 2개) · **9 카테고리 막대차트**(E22·D18·B15·C12·H9·A8·F8·I5·G3, 색: ≥0.75 green·0.5-0.74 amber·<0.5 red) · **구조 맵(SVG)**(대형 파일은 *결합도* 우선, 라인 수는 보조) · **Wins/Top ROI**(`actions` 상위 5-7, gate 해소 최상단) · **푸터**.

**대시보드 스타일(고정)**: 템플릿의 CSS 변수 팔레트·폰트(Inter/JetBrains Mono, 오프라인이면 시스템 폰트 폴백)를 그대로 쓰고 다크 모드를 만들지 않는다. 모든 시각화는 **인라인 SVG + CSS**(차트 라이브러리 금지). 이름이 cartography라고 지도 은유 장식(컴퍼스 로즈·양피지·이모지)을 넣지 않는다.

## M3. 브라우저에서 열기

```bash
open <output-path>/ai-readiness-map.html    # macOS  (Linux: xdg-open)
```
사용자가 "열지 마라" 하면 경로만 알린다.

## M4. ROI 리팩토링 가이드 + 요약 보고

한 문단으로: ① 총점/등급(capped면 "gate 상한" 병기) ② 실패한 gate + 왜 blocking인지 ③ 최약 카테고리 1-2개 + 한 줄 진단(근거 인용) ④ Top 3 ROI 액션(effort·impact·evidence grade, gate 해소 우선) ⑤ 생성된 파일 경로. **②③이 스코프에 있으면 재문의 없이 이어서 수행**하고, ①만 했으면 원하면 ②/③로 확장할 수 있다고 opt-in 안내한다(이미 고른 선택을 다시 묻지 않는다).

---

# ② 진단·개선 모드 워크플로

측정을 seed로 5단계 — 측정(Phase 0) → 설계(1·2) → **적용(3, 계획·개별 승인)** → 수용 증명·재측정(4). 각 단계 보고: `[Phase n] {산출물}: {핵심} — {다음|보정}`. **승인 없이는 어떤 파일도 수정하지 않는다.**

## Phase 0 — 진단 (Assess) · 진단 승인 게이트

### 0a. 결정론 측정 (score.py seed)

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <대상 경로> \
  --json .claude/ai-readability/{대상-slug}/ai-readiness-score.json
```

이 `score.json`(categories·gates·ROI `actions` 백로그)이 진단 seed이자 Phase 4 재측정 baseline이다. score.py가 결정론으로 잡은 것은 손으로 다시 추정하지 않는다. **①+② 조합이면 여기서 재실행하지 않고** ①의 실행에 `--json`을 이 slug 경로로 지정해 대시보드 소스와 seed를 한 파일로 공유한다.

### 0b. 정성 보강 진단 (accessibility-assessor)

```
Agent(
  subagent_type="accessibility-assessor", model="opus",
  prompt="""
  [역할] score.json을 seed로 삼아, score.py가 못 재는 A축 강제·행위 신호를 더해 2축(Q/A) 진단 + 등급(5밴드) + Gate-3 예비판정을 증거 기반으로 낸다.
  [입력] 진단 대상: {대상 경로/서비스/모듈}, 결정론 seed: {ai-readiness-score.json 경로/내용}, 빌드·언어·아키텍처: {있으면}
  [규칙] score.py가 결정론으로 잡은 legibility/존재 신호(참조 무결성·import 그래프·결합도·redundancy·pre-commit/타입/lint·devcontainer)는 다시 손으로 추정하지 말고 그 점수를 인용한다.
         이 에이전트가 더하는 것은 score.py가 못 재는 강제·행위 판단 — ★ Gate-3 의존 방향 *강제*("금지 경계 위반이 실제 빌드 실패를 일으키는가"; score.py는 그래프 가독성만 봄), 빌드 피드백 3차원 품질, 자동 수용 가능성. 위반 케이스나 빌드 설정을 file:line으로 인용(자기보고 불신).
         등급은 단일 5밴드로만 매긴다. Gate-3 실패(강제 없음)면 상한 AI-Assisted. 높은 Q축≠높은 A축을 드러낸다. score.json의 ROI `actions` 백로그를 담당 설계 Phase(1/2)로 태깅한다(적용은 Phase 3). 증거 확보 불가는 '검증 불가'로 분리. 이 에이전트는 코드를 고치지 않는다(진단만).
  [출력] AI 접근성 진단 리포트(seed 인용·A축 강제/행위 지표별·5밴드 등급·Gate-3 판정·Phase 태깅 백로그·가정).
  """
)
```

진단 리포트를 보여주고 **진단 승인 게이트**: `[Phase 0] AI 접근성 진단 — 현재 {grade}(Gate-3 {pass/fail}), 목표 {grade}, A축 격차 N개. 다음: 빌드 가드레일 설계(Phase 1). 승인할까요?` 승인 전에는 진행하지 않고, 승인된 진단을 `assessment.md`로 write한다.

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
         Convention Plugin/Gradle은 예시 — 원리를 사용자 스택으로 환산한다. **이 에이전트는 파일을 직접 수정하지 않는다**(설계·제안만) — 적용은 Phase 3.
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
         Hexagonal/Spring/Gradle은 예시 — 원리를 사용자 스택으로 환산한다. **이 에이전트는 파일을 직접 수정하지 않는다**(설계·제안만) — 적용은 Phase 3.
  [출력] Standalone 실행 설계(모듈 조합·어댑터 치환·UseCase seed·외부 의존·기동·커버리지).
  """
)
```

설계를 검토하고 `remediation-plan.md`에 Phase 2 섹션으로 append.

## Phase 3 — 적용 (Apply) · 계획 승인 → 개별 적용

Phase 1·2 설계를 실제 코드로 반영한다(③과 동형의 게이트된 적용). **승인 없이는 어떤 파일도 수정하지 않는다.**

### 3a. 변경 계획표 + 계획 승인 게이트 (Gate A)

| 등급 | 예 | 동작 위험 | 기본값 |
|------|-----|----------|--------|
| **S 안전 추가형** | 빌드 가드레일 설정·수용 E2E 테스트·CI 규칙 *추가* | 없음(추가만) | ON |
| **M 설정 변경** | 기존 빌드/타입 설정 강화·경계 lint 규칙 | 낮음(빌드 실패 가능) | ON |
| **L 구조 리팩터** | standalone 추출·의존 방향 재작성·모듈 분할·파일 이동 | **높음**(19~35% 비등가·효과=추론) | **opt-in** |

- **L 켜면 경고(경고이지 거부가 아니다)**: "구조 리팩터가 에이전트 성공률을 올린다는 직접 측정 근거는 없습니다(추론). LLM 리팩터의 19~35%가 비등가, 그중 ≈21%는 테스트를 통과합니다." — 감수 여부는 **사용자 결정**('결정 권한' 불변식).
- **센서 확인 = 등가성 관측 수단 확인**(테스트 스위트 유무가 아니다): 자동 테스트가 없어도 L을 거부하지 않고 **센서를 행위 관측으로 승격**한다 — 영향받는 표면을 실제 실행·렌더해(standalone 슬라이스/MSW/dev 서버/CLI, [`verify`]·[`run`] 스킬) baseline과 대조한다. Phase 2의 standalone 슬라이스가 그 센서 기반이므로 먼저 세운다. 테스트·컴파일·행위 실행·**사람 diff 리뷰** 어느 것으로도 관측할 수 없을 때만, 그조차 조용히 거부하지 말고 "관측 센서 없음 — 미관측 진행/센서 먼저 구축/건너뛰기?"로 사용자에게 넘긴다(*센서* 부재 판단이지 *적용 도구*(LSP extract/move) 유무가 아니다). 판정 상한은 어느 경우든 **UNVERIFIED**.
- **리팩토링 요청이면 L을 1급 지렛대로 전면화**: 요청이 구조·본문 변경이면 S 툴링만 적용하고 "리팩토링 완료"로 보고하지 않는다. **사용자가 지목한 구조 대상(파일·모듈·god-file)은 계획표에서 누락하지 않는다** — 누락은 곧 사전 단계 권한 전도다.
- 계획표(#·등급·위치·현재→변경·근거·동작위험·1급 센서·판정상한 VERIFIED/FAILED/**UNVERIFIED**)를 보이고: `[Phase 3] 변경 N건(S:· M:· L:·) — 적용할 등급/항목을 고르세요. 승인 없이는 수정하지 않습니다.`

### 3b. 개별 순차 적용 + 개별 승인 게이트 (Gate B)

한 건씩, **개별 승인 후에만** 적용한다. 승인된 항목은 **적용하거나(가용 최강 센서와 함께) 새 차단 요인을 escalate 한다 — 조용히 보류·강등하지 않는다**.
- **추가형(S)**: 새 파일·설정을 직접 write(기존 코드 불변).
- **리네임·시그니처 변경**: **AST/LSP 도구에 위임**(문자열 치환 금지) — rope/pyright · ts-morph/tsserver · gopls · rust-analyzer. 도구 없으면 "제안만"으로 강등(safe by construction 불가).
- **추출·이동·모듈 분할(L)**: LSP extract/move가 있으면 그것으로, **없으면 최소 단위 수작업 편집**(통짜 재작성 금지·한 번에 한 단계). 리네임과 달리 도구 부재는 강등 사유가 **아니다** — 대신 행위 센서를 필수로 건다(무테스트 god-file 분할이 정확히 이 경로).
- **generator≠checker**: 설계 에이전트가 아니라 [`behavior-guard`](../../agents/behavior-guard.md)가 변경 클래스별 센서를 **실행해 관측**한다. 센서가 **red(실제 회귀)면 되돌리고**, UNVERIFIED(센서 부재)는 라벨일 뿐 조용한 보류 근거가 아니다.
- 커밋하지 않는다. 적용 내역을 `remediation-plan.md`의 Applied 섹션에 기록.

## Phase 4 — 수용 증명·재측정 (Acceptance & Re-grade)

### 4a. 결정론 재측정

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <대상 경로> \
  --json .claude/ai-readability/{대상-slug}/ai-readiness-score.after.json
```

Phase 0 seed와 diff해 `total`·`grade`·`gates`·카테고리 델타를 낸다. 재현 가능·협상 불가한 수치라 **등급을 자기보고로 부풀리지 못하게 하는 결정론 방어**다. 재실행 불가면 BLOCKED.

### 4b. 정성 강제 probe + 수용 증명 (acceptance-verifier)

```
Agent(
  subagent_type="acceptance-verifier", model="opus",
  prompt="""
  [역할] Phase 1·2 설계자와 분리된 독립 검증자로서 ① 수용 증명(자동 E2E·데모) 인프라를 설계하고 ② 결정론 델타(score.py 재실행) 위에 강제 probe를 얹어 Gate-3·등급을 적대 재측정한다.
  [입력] Phase 0 seed + Phase 4a 재실행 결과 + Phase 1 가드레일 설계 + Phase 2 standalone 설계 + **Phase 3 적용본**(remediation-plan.md Applied 섹션): {산출물}
  [규칙] 결정론 델타(total·gate·카테고리 변화)를 인용하되, score.py는 구조의 *존재*만 재고 *강제*는 못 재므로 그것만으로 등급을 올리지 않는다.
         결정적 판정 '이제 금지 경계 위반이 실제 빌드 실패를 일으키는가'(Gate-3)는 위반 케이스를 직접 만들어 관측한다(score.py로 대체 불가). 결정론 델타가 올랐어도 강제 probe가 red build를 못 내면 Gate-3 실패로 상한 AI-Assisted 유지.
         수용 증명은 리뷰를 '동작하나→설계가 좋은가'로 옮긴다. 못 잡는 것(성능·보안 인가 우회·동시성 정합·가독성)은 사람 몫으로 반드시 명시(과신 금지). green ≠ 개선, reward-hacking 의심·역점검.
         Phase 0 백로그의 각 격차(G1, G2…) 해소를 증거와 함께 귀속하고, 미해소는 되돌릴 Phase로 라우팅. 증거 확보 불가는 '미달'이 아니라 '검증 불가(BLOCKED)'로 분리. **이 에이전트는 파일을 직접 수정하지 않는다**(설계·Verdict만).
  [출력] 수용 증명 설계 + 등급 재측정 Verdict(결정론 델타·Gate-3 강제 probe 증거·한계·격차 해소·BLOCKED·결론·라우팅).
  """
)
```

분기: **목표 도달 + Gate-3 통과 + 격차 증거 해소** → `acceptance-and-regrade.md`에 Verdict write·완료. **격차 미해소** → 빌드 강제 미흡이면 Phase 1 재설계 후 재적용, 격리 불가면 Phase 2, 센서 red면 Phase 3에서 해당 변경 되돌림, 진단이 틀렸으면 Phase 0. **BLOCKED** → 미달로 두지 말고 환경·위반 케이스 확보를 보정(미달 카운트 미산입). **reward-hacking 의심**(delta green인데 구조 미변경·Gate-3 미강제) → 등급 상승 거절 + 근거 제시 후 해당 Phase로 되돌림.

## ② 마무리 보고

`[AIRC 완료] {grade before} → {grade after}(Gate-3 {pass/fail}), A축 격차 {해소}/{전체}, 적용 {N}건(S/M/L·UNVERIFIED {k}) — 재측정 {증거 PASS|미달|BLOCKED} → .claude/ai-readability/{대상-slug}/`

**인도 정합 점검**: 보고 전에 *요청한 변경 클래스*와 *실제 적용한 클래스*를 대조한다. 요청이 구조 리팩토링(L)이었는데 적용분이 S 툴링·설정에 치우쳤으면 `"요청은 구조 변경(L), 실제 적용은 대부분 툴링/설정 — 요청을 충족하지 못함"`을 명시한다. opt-in된 L을 에이전트 판단으로 보류했으면 사유를 밝히고 재개 여부를 묻는다. **툴링 적용을 "리팩토링 완료"로 포장하지 않는다.**

---

# ③ 코드 본문 층위 모드 워크플로 (3게이트 승인 후 수정)

본문 층은 **등급을 만들지 않는다**(census + 개입 제안뿐 — 본문층 등급의 1차 근거 부재). 개입 우선순위는 직관이 아니라 위험조정 근거다 — **P1 오도 제거(C0·위험 0) → P2 안전 교정(C2 리네임) → P3 검증된 계약 주석(C1·'왜' 주석 opt-in) → P4 고위험 opt-in(C3 구조)**. 정본은 [`references/intervention-catalog.md`](references/intervention-catalog.md), 원리는 [`references/legibility-principles.md`](references/legibility-principles.md), 근거는 [`references/research/body-legibility/`](references/research/body-legibility/README.md).

| 클래스 | 개입 | 축 | 우선순위 | 동작 위험 | 기본값 |
|--------|------|-----|---------|----------|--------|
| **C0** | 오도·stale 주석 삭제/수정 | comments | **P1** | 없음 | ON |
| **C1** | 계약·불변식 주석 추가/수정 **+ '왜/맥락' 주석(comment-gap)** | comments | P3 | 없음(사실성 ~20~45%) | ON(gap 추가는 opt-in) |
| **C2** | 무의미·오도 식별자 안전 리네임 | naming | **P2** | 참조·컴파일 깨짐 | ON |
| **C3** | 구조 리팩터(추출·이동·분할) | structure | P4 | **높음**(19~35% 비등가) | **OFF·opt-in** |

> **markup·tests 축은 census 전용(개입 없음)**: census는 마크업 시맨틱(`MK*`)·테스트 설명(`TL*`) 결함 후보도 셀 수 있지만 **대응 개입 클래스가 없다** — 이들을 격리해 LLM 이해 델타를 잰 연구가 없고(O-6) 접근성 개선은 이 하네스의 표적이 아니다. 후보는 "참고(개입 없음)"로만 보고하고, 고치려면 접근성 도구·사람 리뷰로 별도 작업하라고 안내한다. **자동 ARIA/alt/어서션 생성은 금지**(confident-but-wrong·green-locks-bug)이고 볼륨은 어떤 수치에도 가점하지 않는다.

## B0 — 초기 문의 (스코프 확정 · **한 번에 한 질문**)

아래 순서로 **하나씩** 묻고, 직전 답이 다음 질문을 결정한다(모르면 기본값을 제시하고 넘어간다).

1. **대상 경로** — 채점·개입할 저장소/디렉터리 (스킵 = 레포 루트).
2. **다룰 축** — 주석 / 명명 / 구조. (마크업·테스트 파일이 있으면 census에 참고 항목으로 함께 실을지만 확인한다 — 개입 대상이 아니다.)
3. **선택한 축 안에서 개입 클래스** — 그 축의 카드만 제시한다(주석 → C0/C1, 명명 → C2, 구조 → C3). **선택된 클래스 = 구속 스코프**이며 밖은 "추가 안 함(스코프 밖)"으로 표기하고 확장은 문의한다.
4. **C3 opt-in 확인**(구조 축을 골랐을 때만) — 아래 경고를 보이고 감수 여부를 묻는다.

각 단계 확정 후 한 줄로 되짚는다: `[B0] 경로 {경로}·축 {…}·클래스 {…} — 다음: census. 진행할까요?`

- **②와 조합 실행이면 C3는 기본 억제** — 구조 리팩터는 ②가 소유하므로 ③의 C3/`structure-cartographer`를 끄고 나머지만 남긴다. 산출물도 ②와 같은 slug 하위에 둔다.
- **C3 켜면 경고(경고이지 거부가 아니다)**: "구조 리팩터가 에이전트 성공률을 올린다는 직접 측정 근거는 없습니다(추론). LLM 리팩터의 19~35%가 비등가, 그중 ≈21%는 테스트를 통과합니다." — 감수 여부는 사용자 결정. + **등가성 센서 확인**: 자동 테스트가 없어도 거부하지 않고 **행위 센서로 승격**한다(영향 표면 실제 실행·렌더로 baseline 대조, [`verify`]/[`run`]). 어떤 센서도 불가할 때만 "미관측 진행/센서 먼저/건너뛰기?"로 결정을 넘긴다. 판정 상한은 UNVERIFIED.
- **C2 선택 시 안전 리네임 도구 탐지**(rope·pyright / ts-morph·tsserver / gopls / rust-analyzer). 없으면 C2를 "제안만"으로 강등.

## B1 — census + 다각도 진단

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/legibility_scan.py <root> \
  --axes <naming,comments,structure 중 선택분(+참고용 markup,tests)> --out {출력 경로}/census-before.json
```

census(등급 없음·`auto-high/auto-med/heuristic/report-only` 라벨)를 seed로, 선택된 클래스에 해당하는 에이전트만 병렬 호출(모두 `model: "opus"`): [`comment-auditor`](../../agents/comment-auditor.md)(C0/C1 + comment-gap C7~C9)·[`naming-analyst`](../../agents/naming-analyst.md)(C2)·[`structure-cartographer`](../../agents/structure-cartographer.md)(C3만). `skipped`·`truncated`·`coverage`(**미측정≠결함 없음**)를 함께 읽는다. **에이전트는 파일을 수정하지 않는다.**

## B2 — 제안표 + 게이트 A (계획 승인)

[`references/intervention-catalog.md`](references/intervention-catalog.md) 랭킹(위험조정 기대이익)으로 제안표(#·클래스·위치·현재→제안·근거·동작위험·1급센서·판정상한 VERIFIED/FAILED/**UNVERIFIED**). **계획 승인 없이는 어떤 파일도 수정하지 않는다.**

## B3 — 개별 순차 적용 + 게이트 B (개별 승인)

한 건씩, **개별 승인 후에만** 적용한다(②의 3b와 동형 — 리네임=AST/LSP 위임, C3는 도구 부재도 강등 사유 아님·행위 센서 필수, `behavior-guard`가 센서 실행 관측, C3 판정 상한 UNVERIFIED, red 센서만 롤백, 승인된 항목의 조용한 보류 금지).

## B4 — 재확인 + 게이트 C (최종 승인)

census 재측정(`census-after.json`) 델타로 개입 반영을 결정론 확인한다(에이전트 성공률 대리 지표 아님). **커밋하지 않는다** — `git-harness` 핸드오프 제안만. 산출물: census-before/after·proposals·verdicts.

> **③ 불변식**: 3게이트(계획 A→개별 B→최종 C) 건너뛰지 않음 · **B0는 한 번에 한 질문** · 스코프 가드(선택 축·클래스 안에서만) · 결정 권한(위험은 경고·수용은 사용자) · 등급 안 만듦 · 자기보고 불신(센서 실행 관측) · 리네임=도구 위임 · markup/tests는 census 전용 · 구조 개입 효과=추론·수치 약속 없음.

## Common pitfalls

- **스코프 미확정·과실행** — 측정만 원했는데 ②③까지 돌리거나 그 반대. 고른 것을 함께 돌리는 것은 정상, 묻지 않은 확대는 금지.
- **문의 덤프** — 경로·축·클래스·opt-in 경고를 한 번에 나열하면 사용자가 실제로 고르지 못한다.
- **승인된 고위험 변경을 조용히 보류(권한 전도)** — 무테스트는 거부 사유가 아니라 행위 센서 승격 사유다. 새 차단 요인은 escalate.
- **리팩토링 요청을 S 툴링으로 대체 충족** — 구조 변경(L)이 요청의 핵심이면 전면화하고, 인도분이 요청 클래스와 다르면 정직히 밝힌다.
- **gate를 가산 점수로 착각** — gate는 등급 *상한*이다(Gate-1/2 실패→AI-Fragile, Gate-3 실패→AI-Assisted). 카테고리 점수는 그대로 합산하되 등급만 캡.
- **Gate-3를 score.py가 잰다고 착각** — score.py는 그래프 *가독성*만 잰다. Gate-3는 개선 모드의 위반 probe로만 판정.
- **본문 수정 효과를 저장소 층 수치로 귀속** — 툴그래프 델타(LocAgent·RepoGraph)는 인덱스 효과지 본문 수정 효과가 아니다.
- **god-file을 라인 수로 판정** — 결합도(fan-in/out)가 1급, 라인 수는 "근거 약함" 보조.
- **폐기된 L1~L5로 등급 매김 / "보유율" 가점 / 템플릿 무시하고 처음부터 쓰기 / 근거 등급 없는 "개선 N%" 서술** — 모두 금지.

## Files

- `scripts/score.py`·`test_score.py` — ① v3 결정론 스코어러(gating·import 그래프·결합도·reference integrity·`*.htmlsafe.json` 동시 출력, stdlib only) + 회귀 테스트 25건.
- `scripts/legibility_scan.py`·`test_legibility_scan.py` — ③ 본문 census 스캐너(등급 없음·5축: naming N1~N4 · comments C1~C9 · structure(report-only) · **markup MK1~MK4·tests TL1~TL2는 census 전용**) + 회귀 테스트 68건.
- `references/scoring-rubric.md` — ① v3 루브릭(9 카테고리 + 3 gate, 근거 등급·auto/manual 라벨).
- `references/ai-readable-codebase-principles.md` — ② 개선 모드 원리(2축·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern).
- `references/intervention-catalog.md`·`references/legibility-principles.md` — ③ 개입 카드(C0~C3)·본문 층위 원리 8.
- `references/research/`(+ `ai-readiness-cartography-research.md`·`ai-readable-codebase-research.md`) — 2025~2026 1차 근거(적대 검증). 루브릭·원리 조작화의 출처.
- `assets/template.html` — 복사 후 채울 대시보드 원본.
- `../../agents/*.md` — ② 4 에이전트(accessibility-assessor·guardrail-architect·standalone-designer·acceptance-verifier) · ③ 3 에이전트(comment-auditor·naming-analyst·structure-cartographer) · 공용 `behavior-guard`. 모두 `model: "opus"`.
