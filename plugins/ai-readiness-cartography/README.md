# ai-readiness-cartography

> 임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 개선을 설계·적용하며 승인 게이트 뒤에 구조·본문 코드를 수정하는(멀티 에이전트)** Claude Code 스킬. 100점·9 카테고리 + 3 blocking gate로 채점해 **JSON 점수표 · HTML 대시보드 · ROI 가이드**를 내고, 그 측정을 센서로 삼아 **빌드 가드레일·standalone·수용 증명** 개선을 설계해 **계획·개별 승인 뒤 적용**하며, 코드 본문(주석·명명·함수 granularity)을 census로 진단해 **3게이트 인간 승인 뒤 단계별로 수정**한다.

## 세 모드 (자유 조합 · 발동 시 스코프 확정)

세 모드는 **배타 택일이 아니다** — ① 측정은 값싼 측정 레인, ②·③은 두 개선 층(② 저장소/구조 · ③ 코드 본문). 원하는 **부분집합**을 골라 함께 돌릴 수 있고, 여러 개면 **①→②→③ 순**으로 이어 수행한다.

| | **① 측정 모드** | **② 진단·개선 모드** | **③ 코드 본문 층위 모드** |
|---|---|---|---|
| 표적 | 점수·시각화 산출물 | 구조 개선 설계 | 주석·명명·함수 granularity |
| 엔진 | `score.py` 1회(결정론) | score.py(센서) + 4 에이전트(opus) | `legibility_scan.py` census + 4 에이전트(opus) |
| 산출 | JSON 점수표 · HTML 대시보드 · ROI | 2축 진단 · 가드레일 · standalone · 수용 증명 | census + 개입 제안 + 승인 후 단계별 적용(C0~C3) |
| 코드 수정 | 안 함(측정만) | **함 — 계획·개별 승인 후(고위험 opt-in)** | **함 — 3게이트 승인 후에만** |
| 등급(0~100) | 낸다 | 낸다(seed) | 안 냄(census만) |
| 비용 | python 1회 | python + opus 4회 | python + opus 3~4회 |

**조합 규약**: ①의 산출물과 ②의 Phase 0 seed는 **같은 score.py 실행을 공유**한다(③은 `legibility_scan.py` 별도). ②가 함께 돌면 Gate-3 판정이 측정의 "미평가"를 대체하고, **②+③이면 구조 리팩터는 ②가 설계·적용으로 소유**하고 ③의 C3는 끈다(이중 처리 방지). 저장소 층 등급은 score.py(①②가 공유)에서만 나오고 ③의 census를 총점에 접붙이지 않으며(본문 신호 report-only), 본문 편집 효과를 저장소 등급에 귀속하지 않는다. 비용은 선택분의 가산 합이라 **원치 않는 모드만 안 고르면 되고, 함께 고르는 것은 정상**이다.

## 빠른 시작

```bash
# 측정 모드: 자동 채점 (JSON + stdout markdown 요약)
python3 skills/ai-readiness-cartography/scripts/score.py /path/to/repo \
  --json /path/to/repo/.claude/ai-readiness-score.json
```

또는 Claude Code에서 자연어로 — **측정**: *"이 레포 AI-readiness 점수 매기고 대시보드 만들어줘"* / *"리팩토링 우선순위를 ROI로"*. **개선**: *"AI 접근성(A축) 낮은 격차 찾아 빌드 가드레일·standalone·수용 증명으로 개선 설계해줘"* / *"의존 방향을 빌드에서 물리적으로 강제하게"*. **본문**: *"AI가 읽기 좋게 주석·변수명·함수명 정리하고 승인하면 단계별로 적용해줘"* / *"주석이 코드랑 안 맞는 것 찾아 고쳐줘"*. **조합**: *"점수도 매기고 약한 카테고리는 가드레일로 개선까지, 본문 주석·명명도 승인 후 정리해줘"*(①+②+③).

## 루브릭 v3 (100pt · 9 카테고리 + 3 gate)

근거 서열대로 가중(실행·검증 ≫ 의존 구조 > 문맥 문서):

| Cat | 이름 | Pts | 측정 |
|-----|------|-----|------|
| **E** | Verification & Executable Signals | 22 | reference integrity · 실행 가능한 test/build · CI (Auto) |
| **D** | Dependency & Structure Mapping | 18 | 기계 판독 import 그래프 · 결합도 god-file (Auto) |
| **B** | Context Quality: Novelty & Discipline | 15 | README 중복↓ · command-first · non-obvious (Heuristic) |
| **C** | Tribal Knowledge Externalization | 12 | Five-Question · MEMORY/ADR (Heuristic) |
| **H** | Feedback-Loop Latency & Quality | 9 | pre-commit · static type · fast lint (Auto) |
| **A** | Navigation & Structure-First Anchors | 8 | 진입점·의존 이웃 명시 (보유율 아님) (Heuristic) |
| **F** | Freshness & Self-Maintenance | 8 | stale-drift · path validation (Auto) |
| **I** | Environment & Task-Discovery Reproducibility | 5 | devcontainer·template (Auto) |
| **G** | Agent Performance Outcomes | 3 | success ⁄ efficiency telemetry (Auto) |

**Blocking gates (등급 상한)** — 실패한 gate는 등급에 상한을 씌운다:
- **Gate-1 Reference Integrity** *(Auto)*: 문서가 인용한 파일 경로·line range에 dangling 0건. 실패 시 상한 AI-Fragile.
- **Gate-2 Executable Verification** *(Auto)*: 실행 가능한 test/build 명령·하네스 존재. 실패 시 상한 AI-Fragile.
- **Gate-3 Architecture Enforcement** *(Heuristic · 진단·개선 모드 전용)*: 금지된 의존 경계 위반이 *실제로 빌드 실패를 일으키는가*. score.py는 그래프 *가독성*만 재고 이 *강제*는 못 잰다 → 측정 모드는 "미평가", 개선 모드의 `acceptance-verifier`가 위반 probe로 판정. 실패 시 상한 AI-Assisted.

등급(**단일 5밴드**): `90+ AI-Native · 75+ AI-Ready · 60+ AI-Assisted · 40+ AI-Fragile · <40 AI-Hostile`. 별도 L1~L5 수치 스케일은 폐기했고 `점수/20=L` 선형 변환은 거짓 정밀이라 쓰지 않는다.

## 진단·개선 모드 (4 에이전트 + behavior-guard)

측정 위에서 구조 개선을 **설계하고 승인 게이트 뒤에 적용**한다 — 두 전제 **"구조가 프롬프트보다 먼저다"**, **"코드 품질(Q축)과 AI 접근성(A축)은 다른 차원이다"**.

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Assess | `accessibility-assessor` | score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정 (진단 승인 게이트) |
| 1 Guardrails | `guardrail-architect` | 빌드 가드레일 **설계**(의존 방향 물리 강제 + 피드백 3차원) |
| 2 Standalone | `standalone-designer` | 도메인 슬라이스 독립 실행 **설계**(port/adapter·use-case seed) |
| **3 Apply** | 오케스트레이터 + `behavior-guard` | 설계를 위험 등급별(S/M/L) 계획표로 → 계획 승인 → 개별 승인 후 적용(이동/리네임=AST/LSP 위임·센서 관측·고위험 구조 리팩터 opt-in·L은 UNVERIFIED 상한) |
| 4 Acceptance & Re-grade | `acceptance-verifier` | 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 재측정(Phase 3 적용본 대상) |

**빌드가 강제하고 문서가 설명한다** — 빌드로 잡을 수 있는 아키텍처 규칙을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.

## 코드 본문 층위 모드 (③ · 4 에이전트 · 3게이트 승인 후 수정)

`legibility_scan.py` census(등급 없음·7 탐지기)를 seed로 주석·독스트링·변수명/함수명/클래스·컴포넌트명·함수/모듈 granularity를 다각도 진단하고, **계획→개별→최종 3게이트 인간 승인 뒤에만** 코드를 단계별로 수정한다. 개입 우선순위는 직관이 아니라 위험조정 근거다:

| 클래스 | 개입 | 우선순위 | 기본값 |
|--------|------|---------|--------|
| **C0** | 오도·stale 주석 삭제/수정 | **P1**(효과 확실·위험 0) | ON |
| **C2** | 무의미·오도 식별자 안전 리네임(AST/LSP 위임) | **P2** | ON |
| **C1** | 계약·불변식 주석 추가/수정 | P3 | ON |
| **C3** | 구조 리팩터(추출·이동·분할) | P4 | **OFF·opt-in** |

에이전트: `comment-auditor`(주석 4분류→C0·C1)·`naming-analyst`(명명 3축→C2)·`structure-cartographer`(구조 후보→C3)·`behavior-guard`(개입 클래스별 센서 실행·관측 — generator≠checker). **정직성**: 본문 신호는 거의 전부 report-only(주석↔코드 정합성 정밀 0.39·자동 주석 생성 ~20~45% 부정확·구조 리팩터 효과=추론)이고 **명명 채널만 실측 인과**(구조보존 난독화 −11~−29pt). 리네임=도구 위임(문자열 치환 금지), **"테스트 통과 ≠ 동작 보존"**(비등가 리팩터 ≈21%가 테스트 통과), 저장소 층 등급을 만들지 않는다(census만). 커밋은 하지 않는다(git-harness 핸드오프).

## 근거 (2025~2026 1차, 적대 검증)

측정 루브릭은 `deep-research`(5 세션 병렬 조사 → 각도별 적대적 팩트체크)로 조작화됐다:
- **ORACLE-SWE(2604.07789)** — reproduction/test 신호가 성공률 최대 기여 → **E 최상위 + Gate-2**
- **ETH Zurich AGENTS.md(2602.11988)** — 보유율≠성능 → **A 보유율 폐기, B redundancy discipline**
- **LocAgent(2503.09089)** — 의존 그래프 localization 예측 → **D 기계 판독 그래프**
- **USENIX 2025 slopsquatting** — hallucinated path → **Gate-1 binary**
- **RepoMirage(2605.26177)** — structure-first anchor; god-file=결합도(라인 수 근거 부재)

개선 모드 원리는 **flex.team 'AI가 읽을 수 있는 코드베이스' 5부작** + 2025+ 출처(arXiv:2505.10443 의미보존 변형·2602.11481 컴파일러-인-더-루프·2306.09896 피드백 병목)로 조작화됐다. 상세·판정은 [`skills/ai-readiness-cartography/references/`](skills/ai-readiness-cartography/references/)(`research/`·`ai-readable-codebase-research.md`). 검증 중 **지어낸 인용 적발·과장 수치 강등**을 포함해 CONFIRMED 근거만 반영한다.

## 정직성

- 모든 지표에 `auto / heuristic / manual` 라벨 + 근거 등급. **Gate-3는 heuristic**(행위 probe)이라 score.py 총점·Gate-1/2에 영향을 주지 않고 개선 모드 등급 상한으로만 작동한다.
- score.py가 flag한 E1 dangling은 *후보* — LLM이 illustrative/placeholder를 걸러 실 dangling만 gate에 반영.
- 근거 부재 신호(라인 수 god-file 정량 감점·hallucination % 임계값·human 포매팅 가점)는 **미채택**.
- "개선 N% 보장" 같은 과장 금지. **① 측정 모드는 코드를 자동 수정하지 않는다**(측정·시각화 제안만) — **②③은** 제안·설계 후 승인 게이트(②=계획·개별, ③=3게이트) 뒤 코드를 수정하며(고위험 변경 opt-in·AST/LSP 위임·behavior 센서 관측·"테스트 통과≠동작 보존"), 커밋은 하지 않는다(git-harness 핸드오프).

## 파일

- `skills/ai-readiness-cartography/SKILL.md` — 오케스트레이터(모드 선택=①②③ 부분집합 → 선택분을 ①→②→③ 순차; ② 5-Phase(0~4·Phase 3 Apply 게이트)·③ 5-Phase(B0~B4·3게이트))
- `skills/ai-readiness-cartography/scripts/score.py`·`test_score.py` — ① v3 스코어러 + 회귀 테스트(25)
- `skills/ai-readiness-cartography/scripts/legibility_scan.py`·`test_legibility_scan.py` — ③ 본문 census 스캐너(등급 없음·7 탐지기) + 회귀 테스트(49)
- `skills/ai-readiness-cartography/references/scoring-rubric.md` — ① v3 루브릭(9 카테고리 + 3 gate)
- `skills/ai-readiness-cartography/references/ai-readable-codebase-principles.md` — ② 개선 모드 원리
- `skills/ai-readiness-cartography/references/intervention-catalog.md`·`legibility-principles.md` — ③ 개입 카드(C0~C3)·본문 원리
- `skills/ai-readiness-cartography/references/research/` — 근거 dossier(session 1~7 + body-legibility/)
- `skills/ai-readiness-cartography/assets/template.html` — 대시보드 템플릿
- `agents/{accessibility-assessor,guardrail-architect,standalone-designer,acceptance-verifier}.md` — ② 개선 모드 4 에이전트
- `agents/{comment-auditor,naming-analyst,structure-cartographer,behavior-guard}.md` — ③ 본문 층위 4 에이전트
