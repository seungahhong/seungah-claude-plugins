---
name: ai-readiness-cartography
description: 임의 git 저장소가 "AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스"인지를 **결정론적 스코어러(score.py, stdlib-only)로 정량 측정·시각화**하는 도메인 무관 단일 스킬. 사용자가 "이 레포 AI-readiness 점수 매겨줘", "agent-readiness 스코어링/등급/대시보드 만들어줘", "AI-ready 루브릭으로 감사하고 시각화", "codebase가 얼마나 agent-friendly한지 점수+HTML 대시보드로", "repo cartography / ai-readiness 지도", "Claude Code/코딩 에이전트가 이 레포를 잘 다룰 수 있는지 점수로 보여줘", "리팩토링 우선순위를 ROI로 뽑아줘(측정 기반)"를 언급하며 *코드베이스를 점수·등급·대시보드로 측정*하려 할 때 발동한다. 100점·9카테고리(E 검증·실행신호/D 의존그래프/B 문맥품질/C 암묵지/H 피드백루프/A 네비게이션/F 신선도/I 환경재현/G 성과) + 2개 blocking gate(Reference Integrity·Executable Verification, 실패 시 등급 상한)로 채점하고, JSON 점수표 + 단일 HTML 대시보드 + ROI 정렬 리팩토링 가이드를 산출한다. 루브릭은 2025~2026 1차 근거로 조작화됐다(ORACLE-SWE·LocAgent·ETH Zurich AGENTS.md·USENIX slopsquatting 등, references/research/). 발동하지 않는다 — 코드베이스의 구조적 AI 접근성을 *정성 진단하고 빌드 가드레일·standalone·수용 증명으로 개선 설계*(ai-readable-codebase: 이쪽은 스코어러 없이 L1~L5 등급+멀티 에이전트 개선), 한 기능의 실행 기반 구현·검증(backend-harness), 하네스(CLAUDE.md/SKILL.md) 자체 진단(meta-harness), AI 생성물 평가 judge 구성(eval-harness), 컨텍스트 페이로드 조립(context-engineering), 완성 코드 리뷰·커밋/PR(frontend/git-harness), settings.json 설정 변경. 이 스킬의 표적은 *점수·시각화 산출물*이지 개선 구현이 아니다.
---

# AI-Readiness Cartography — 코드베이스 AI 준비도 결정론적 측정·시각화

임의 저장소를 **AI-Ready 코드베이스 v3 루브릭**(100점 · 9 카테고리 + 2 blocking gate)으로 감사한다. 산출물은 **① JSON 점수표(결정론적, 다른 도구가 소비 가능) · ② 단일 HTML 대시보드(사람 의사결정용) · ③ ROI 정렬 리팩토링 가이드(측정 기반 우선순위)** 세 가지다. 이름은 "cartography"지만 톤은 판타지 지도가 아니라 **의사결정용 계기판**이다.

## 이 스킬이 다른 것 (경계 — 먼저 읽어라)

- **표적은 *측정·시각화 산출물*이다.** 결정론적 `score.py`가 자동으로 점수를 내고, LLM은 heuristic/manual 항목을 보강한 뒤 대시보드·ROI 가이드를 만든다. *코드를 자동 수정하지 않는다*(제안만).
- **`ai-readable-codebase`와 구분**: 그 하네스는 스코어러 없이 2축(Q/A) *정성 진단* + L1~L5 등급 + 빌드 가드레일·standalone·수용 증명 *개선 설계*(4-에이전트)를 한다. 이 스킬은 *결정론적 점수·대시보드*를 낸다. 경계가 모호하면 한 질문: "*점수·등급·대시보드로 측정*하려는 건가요(이 스킬), 아니면 *정성 진단 후 구조 개선을 설계*하려는 건가요(ai-readable-codebase)?"

## 내재화 원칙

- **근거 기반 루브릭(evidence-graded)**: v3의 모든 카테고리·가중치는 2025~2026 1차 근거로 조작화됐고, 각 지표에 `auto / heuristic / manual` 라벨과 근거 등급(auto-high…heuristic-low)이 붙는다. 근거 없는 신호를 만점 근거로 쓰지 않는다.
- **gating(blocking > 가산)**: 하나의 blocking 결함(dangling reference·미작동 test)이 다른 고득점에 희석되지 않게, 실패한 gate는 등급에 상한을 씌운다. 순수 가중합의 오탐을 피한다.
- **실행·검증 우선**: 정적 문서(A~D)보다 실행 신호(E)가 성공률에 압도적 기여(ORACLE-SWE). 가중치 서열이 근거 서열을 따른다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율 자체는 가점하지 않는다(ETH Zurich 반증). novelty·비중복·command-first만 가점.
- **정직성(과장 금지)**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만 인용, "개선 N% 보장" 금지. 자동이 flag한 E1 dangling *후보*는 LLM이 확인 후 실 dangling만 gate에 반영한다(placeholder·illustrative 제외).
- **자동 우선, 사람 보강**: score.py가 잡는 것은 자동이 더 정확하다. 스크립트 실행 *후* 그 위에 heuristic/manual 항목을 보강한다(처음부터 손채점 금지).

## 산출물 배치 (기본, 사용자 지정 가능)

- 레포에 `docs/`가 있으면 → `docs/ai-readiness-map.html`, `docs/ai-readiness-score.json`
- `.claude/`가 있으면 → `.claude/ai-readiness-{map.html,score.json}`
- 둘 다 없으면 레포 루트. 사용자가 경로를 명시하면 그 경로 우선. 문서 언어는 한국어.

---

# 워크플로

## 1. 결정론적 자동 채점

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ai-readiness-cartography/scripts/score.py <repo-path> \
  --json <output-path>/ai-readiness-score.json
```

스크립트(stdlib only, Python 3.10+)가 자동으로 잡는 것:
- **E** reference integrity(dangling path·line range) + 실행 가능한 test/build/lint + CI
- **D** import 그래프 파싱(Python AST·JS 상대 import) + 결합도 hotspot(fan-in/out) + workspace
- **B** context ↔ README/코드 redundancy + command-first + non-obvious 마커
- **C** Five-Question + MEMORY/ADR
- **H** pre-commit·static type·fast lint / **F** stale-drift·path validation / **I** devcontainer·template / **G** evals·telemetry
- **Gates** Reference Integrity / Executable Verification (실패 시 등급 상한)

자동이 못 잡는 것(LLM 보강):
- B의 command 실효·non-obvious 패턴의 *실제 유효성*, C의 tribal knowledge *깊이*, E4 critic *품질*, A anchor의 *정확성*.
- **E1 dangling 후보 확인**: score.py가 flag한 dangling path를 열어 실제 dangling인지(placeholder/illustrative 예시 아닌지) 확인하고, 실 dangling만 gate·점수에 반영한다.

## 2. JSON으로 HTML 대시보드 채우기

`assets/template.html`을 복사한 뒤 JSON 값을 끼워 넣는다. **처음부터 쓰지 말 것** — 복사 → 수정.

**이스케이프(non-negotiable·보안)**: JSON에서 온 **모든 문자열 값**(repo 이름·branch·파일 경로·findings·impact·insights)은 삽입 전 반드시 HTML 이스케이프한다 — `&`→`&amp;`, `<`→`&lt;`, `>`→`&gt;`, `"`→`&quot;`. git 브랜치명·경로는 `<script>` 같은 문자를 합법적으로 포함할 수 있어(신뢰 불가 입력), 이스케이프 없이는 저장된 대시보드가 열람 시 임의 스크립트를 실행한다.

바꿀 블록:
- **헤더**: repo 이름·오늘 날짜·branch·modules·context_files·code_files(parseable)·dangling_refs
- **Gate strip**: Gate-1/Gate-2 pass/fail (실패 시 빨간 배지 + "등급 상한 적용")
- **Score hero**: `total`, `grade`(capped면 `raw_grade`도 병기), grade_color, 최약 카테고리 2개
- **9 카테고리 막대차트**: 근거 서열(E22·D18·B15·C12·H9·A8·F8·I5·G3) 순, 각 행에 label(Auto/Heuristic)·evidence_grade·evidence 1-2개. 막대 색: score/max ≥0.75 green · 0.5-0.74 amber · <0.5 red
- **구조 맵(SVG)**: 대상 repo에 맞게 컬럼 재설정. 대형 파일은 *결합도(fan-in/out)* 우선 표시(라인 수는 보조). context 보유 module은 accent, dangling 있는 module은 빨간 점
- **Wins / Top ROI Actions**: `actions` 상위 5-7개. 각 행에 category·effort(S/M/L·시간)·impact·evidence_grade. gate 해소 액션을 최상단
- **푸터**: `{{REPO}} · AI-Readiness v3 (9 카테고리 + 2 gate / 100점) · scored {{YYYY-MM-DD}}`

## 3. 브라우저에서 열기

```bash
open <output-path>/ai-readiness-map.html    # macOS  (Linux: xdg-open)
```
사용자가 "열지 마라" 하면 경로만 알린다.

## 4. ROI 리팩토링 가이드 + 요약 보고

마지막으로 한 문단으로:
1. **총점 / 등급** (capped면 "gate 상한 적용 — 순수 점수 등급 X" 병기)
2. **실패한 gate**(있으면) + 그것이 왜 blocking인지
3. **최약 카테고리 1-2개** + 한 줄 진단(근거 인용)
4. **Top 3 ROI 리팩토링 액션**(effort·impact·evidence grade) — gate 해소 우선
5. 생성된 **파일 경로**

보고 형식: `[AI-Readiness] {total}/100 · {grade}{ (gate 상한) } — 최약 {Cat}, Top ROI: {액션1} → {산출물 경로}`

## Style rules (non-negotiable — 원본 스킬 정체성)

- **폰트**: Inter(본문)·JetBrains Mono(숫자/코드). 다른 폰트 금지. 단, **오프라인/폐쇄망 환경이거나 사용자가 외부 요청을 원치 않으면** 템플릿의 Google Fonts `<link>`를 제거하고 시스템 폰트 폴백(`-apple-system, system-ui`)으로 렌더한다 — 대시보드 열람이 외부 서버로 신호를 보내지 않게.
- **색**: 템플릿 CSS 변수 팔레트 고정. 배경 `#fafafa` light. 다크 모드 만들지 않음.
- **장식 금지**: 컴퍼스 로즈·양피지·필기체·이모지·스탬프 없이. 이름이 cartography라고 지도 은유 강하게 쓰지 말 것.
- **차트 라이브러리 금지**: 모든 시각화는 인라인 SVG + CSS.

## Common pitfalls

- **루브릭이 v3임을 잊고 v2(7카테고리)로 채점** — 현재는 **9 카테고리 + 2 gate / 100점**, gating 집계.
- **gate를 가산 점수로 착각** — gate는 등급 *상한*이다. 실패해도 카테고리 점수는 그대로 합산하되 등급만 AI-Fragile로 캡.
- **E1 dangling 후보를 무비판 반영** — 자동 flag를 LLM이 확인. placeholder(`_docs/feature-x-spec.md`)를 실 dangling으로 세면 등급을 잘못 캡한다.
- **"보유율"에 가점** — v3는 커버리지 %를 점수화하지 않는다(근거 반증). anchor 명시성에 점수.
- **god-file을 라인 수로 판정** — 결합도(fan-in/out)가 1급. 라인 수는 "근거 약함" 보조.
- **템플릿 무시하고 처음부터 쓰기** — 복사 → 수정.
- **정량 수치 과장** — 근거 등급·CAVEAT 없이 "개선 N% 보장" 금지.

## Files

- `scripts/score.py` — v3 결정론적 스코어러(gating·import 그래프·결합도·reference integrity). stdlib only.
- `references/scoring-rubric.md` — v3 루브릭(9 카테고리 + 2 gate, 근거 등급·auto/manual 라벨).
- `references/research/` — 2025~2026 1차 근거(5 세션 + 합성, 적대 검증됨). 루브릭 조작화의 출처.
- `references/ai-readiness-cartography-research.md` — 근거 dossier 인덱스.
- `assets/template.html` — 복사 후 채울 대시보드 원본.
