# ai-readiness-cartography

> 임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 개선을 설계하는(멀티 에이전트)** Claude Code 스킬. 100점·9 카테고리 + 3 blocking gate로 채점해 **JSON 점수표 · HTML 대시보드 · ROI 가이드**를 내고, 그 측정을 센서로 삼아 **빌드 가드레일·standalone·수용 증명** 개선을 설계한다.

## 두 모드 (발동 시 먼저 확정)

| | **① 측정 모드** | **② 진단·개선 모드** |
|---|---|---|
| 표적 | 점수·시각화 산출물 | 구조 개선 설계 |
| 엔진 | `score.py` 1회(결정론) | score.py(센서) + 4 에이전트(model:opus) |
| 산출 | JSON 점수표 · HTML 대시보드 · ROI 가이드 | 2축 진단 · 빌드 가드레일 · standalone · 수용 증명·재측정 |
| 비용 | python 1회 | python + opus 4회 |
| 언제 | "점수·등급·대시보드로 *측정*" | "구조를 *진단하고 개선까지 설계*" |

측정이 개선의 seed다 — 개선 모드는 score.py를 Phase 0 진단 seed·Phase 3 재측정 델타로 쓴다. **잘못된 모드는 비싼 오라우팅**(python 원했는데 opus 4회, 또는 반대)이라 발동 시 한 질문으로 모드를 확정한다.

## 빠른 시작

```bash
# 측정 모드: 자동 채점 (JSON + stdout markdown 요약)
python3 skills/ai-readiness-cartography/scripts/score.py /path/to/repo \
  --json /path/to/repo/.claude/ai-readiness-score.json
```

또는 Claude Code에서 자연어로 — **측정**: *"이 레포 AI-readiness 점수 매기고 대시보드 만들어줘"* / *"리팩토링 우선순위를 ROI로"*. **개선**: *"AI 접근성(A축) 낮은 격차 찾아 빌드 가드레일·standalone·수용 증명으로 개선 설계해줘"* / *"의존 방향을 빌드에서 물리적으로 강제하게"*.

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

## 진단·개선 모드 (4 에이전트)

측정 위에서 구조 개선을 설계한다 — 두 전제 **"구조가 프롬프트보다 먼저다"**, **"코드 품질(Q축)과 AI 접근성(A축)은 다른 차원이다"**.

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Assess | `accessibility-assessor` | score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정 (진단 승인 게이트) |
| 1 Guardrails | `guardrail-architect` | 빌드 가드레일(의존 방향 물리 강제 + 피드백 3차원) |
| 2 Standalone | `standalone-designer` | 도메인 슬라이스 독립 실행(port/adapter·use-case seed) |
| 3 Acceptance & Re-grade | `acceptance-verifier` | 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 재측정 |

**빌드가 강제하고 문서가 설명한다** — 빌드로 잡을 수 있는 아키텍처 규칙을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.

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
- "개선 N% 보장" 같은 과장 금지. 코드를 자동 수정하지 않는다(측정·시각화·설계 제안만).

## 파일

- `skills/ai-readiness-cartography/SKILL.md` — 오케스트레이터(모드 게이트 → 측정 / 진단·개선 4-Phase)
- `skills/ai-readiness-cartography/scripts/score.py`·`test_score.py` — v3 스코어러 + 회귀 테스트
- `skills/ai-readiness-cartography/references/scoring-rubric.md` — v3 루브릭(9 카테고리 + 3 gate)
- `skills/ai-readiness-cartography/references/ai-readable-codebase-principles.md` — 개선 모드 원리
- `skills/ai-readiness-cartography/references/research/` — 근거 dossier
- `skills/ai-readiness-cartography/assets/template.html` — 대시보드 템플릿
- `agents/{accessibility-assessor,guardrail-architect,standalone-designer,acceptance-verifier}.md` — 개선 모드 4 에이전트
