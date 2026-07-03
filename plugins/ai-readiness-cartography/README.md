# ai-readiness-cartography

> 임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **결정론적으로 점수화·시각화**하는 Claude Code 스킬. 100점·9 카테고리 + 2 blocking gate로 채점하고 **JSON 점수표 · HTML 대시보드 · ROI 정렬 리팩토링 가이드**를 낸다.

## 무엇을 하나

`score.py`(stdlib only, Python 3.10+)가 저장소를 훑어 자동으로 점수를 내고, LLM이 heuristic/manual 항목을 보강해 대시보드와 리팩토링 우선순위를 만든다. **코드를 고치지 않는다 — 측정·시각화·제안만.**

세 가지 산출물:
1. **JSON 점수표** — 결정론적, 다른 도구가 소비 가능
2. **단일 HTML 대시보드** — 사람이 보고 의사결정 (Inter/JetBrains Mono, 인라인 SVG, 라이트)
3. **ROI 정렬 리팩토링 가이드** — 측정 기반 우선순위 (gate 해소 최우선)

## 빠른 시작

```bash
# 자동 채점 (JSON + stdout markdown 요약)
python3 skills/ai-readiness-cartography/scripts/score.py /path/to/repo \
  --json /path/to/repo/.claude/ai-readiness-score.json
```

또는 Claude Code에서 자연어로: *"이 레포 AI-readiness 점수 매기고 대시보드 만들어줘"* / *"codebase가 얼마나 agent-friendly한지 점수+시각화로"* / *"리팩토링 우선순위를 측정 기반 ROI로 뽑아줘"*.

## 루브릭 v3 (100pt · 9 카테고리 + 2 gate)

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

**Blocking gates (등급 상한)** — 하나의 blocking 결함이 다른 고득점에 희석되지 않게, 실패한 gate는 등급에 상한 AI-Fragile을 씌운다:
- **Gate-1 Reference Integrity**: 문서가 인용한 파일 경로·line range에 dangling(비존재) 0건
- **Gate-2 Executable Verification**: 실행 가능한 test/build 명령·하네스 존재

등급: `90+ AI-Native · 75+ AI-Ready · 60+ AI-Assisted · 40+ AI-Fragile · <40 AI-Hostile`.

## `ai-readable-codebase`와 무엇이 다른가 (상보 관계)

| | **ai-readiness-cartography** (이 플러그인) | **ai-readable-codebase** |
|---|---|---|
| 성격 | 결정론적 **측정·스코어·대시보드** | 정성적 **진단→개선 설계** 오케스트레이터 |
| 산출 | JSON 점수 + HTML + ROI | L1~L5 등급 + 빌드 가드레일 *설계안* |
| 스코어러 | ✅ 실행 가능한 `score.py` | ❌ 없음(사람 판단·멀티 에이전트) |
| 언제 | "점수·등급·대시보드로 *측정*" | "구조를 *진단하고 개선 설계*" |

먼저 이 스킬로 **측정**하고, 개선을 *설계*하려면 `ai-readable-codebase`로 넘어가는 흐름이 자연스럽다.

## 근거 (2025~2026 1차, 적대 검증)

v3 루브릭은 `deep-research`(5 세션 병렬 조사 → 각도별 적대적 팩트체크)로 조작화됐다. 핵심:
- **ORACLE-SWE(2604.07789)** — reproduction/test 신호가 성공률 최대 기여(+26~27pp) → **E 최상위 가중 + Gate-2**
- **ETH Zurich AGENTS.md(2602.11988)** — 컨텍스트 보유율≠성능, 중복은 순비용 → **A 보유율 폐기, B redundancy discipline**
- **LocAgent(2503.09089)** — 의존 그래프가 localization 예측(92.7%) → **D 기계 판독 그래프**
- **USENIX Security 2025 slopsquatting** — hallucinated path 위험 → **Gate-1 binary**
- **RepoMirage(2605.26177)** — structure-first anchor(파일 노출≠성능, A 근거); god-file=결합도는 defect-prediction 문헌(라인 수 근거 부재, session-4 C7·C8)
- **Factory·Kenogami readiness** — lowest-as-ceiling 게이팅, DevEx feedback loop → **gating 집계 + H/I 신규**

상세·판정은 [`skills/ai-readiness-cartography/references/research/`](skills/ai-readiness-cartography/references/research/). 검증 중 **지어낸 인용 1건 적발·과장 수치 강등**을 포함해, 루브릭은 CONFIRMED 근거만 반영한다.

## 정직성

- 모든 지표에 `auto / heuristic / manual` 라벨 + 근거 등급(auto-high…heuristic-low).
- score.py가 flag한 E1 dangling은 *후보* — LLM이 illustrative/placeholder를 걸러 실 dangling만 gate에 반영.
- 근거 부재 신호(라인 수 god-file 정량 감점·hallucination % 임계값·human 포매팅 가점)는 **미채택**.
- "개선 N% 보장" 같은 과장 금지.

## 파일

- `skills/ai-readiness-cartography/SKILL.md` — 오케스트레이터
- `skills/ai-readiness-cartography/scripts/score.py` — v3 스코어러
- `skills/ai-readiness-cartography/references/scoring-rubric.md` — v3 루브릭
- `skills/ai-readiness-cartography/references/research/` — 근거 dossier
- `skills/ai-readiness-cartography/assets/template.html` — 대시보드 템플릿
