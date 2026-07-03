# ai-readiness-cartography

임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **결정론적 스코어러로 정량 측정·시각화**하는 도메인 무관 단일 스킬. 100점·9 카테고리 + 2 blocking gate로 채점하고 JSON 점수표 + HTML 대시보드 + ROI 리팩토링 가이드를 낸다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
ai-readiness-cartography/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 루브릭 요약 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·경계·근거
├── skills/
│   └── ai-readiness-cartography/
│       ├── SKILL.md                 # 오케스트레이터(스코어러 실행 → 대시보드 → ROI 가이드)
│       ├── scripts/score.py         # v3 결정론적 스코어러(stdlib only, gating·import 그래프·결합도)
│       ├── assets/template.html     # 복사 후 채울 대시보드 원본(Inter/JetBrains Mono, 인라인 SVG)
│       └── references/
│           ├── scoring-rubric.md    # v3 루브릭(9 카테고리 + 2 gate, 근거 등급·auto/manual 라벨)
│           ├── ai-readiness-cartography-research.md  # 근거 dossier 인덱스
│           └── research/            # 2025~2026 1차 근거(합성 + 5 세션, 적대 검증)
└── evals/
    ├── evals.json                   # 수용 평가(루브릭 불변식 file:section 인용 채점)
    └── trigger-eval.json            # 트리거 경계 평가(should/should-not, 인접 도메인 가드)
```

## 루브릭 v3 요약 (100pt · 9 카테고리 + 2 gate)

| 순위 | Cat | 이름 | Pts | Label |
|------|-----|------|-----|-------|
| 1 | E | Verification & Executable Signals | 22 | Auto |
| 2 | D | Dependency & Structure Mapping | 18 | Auto |
| 3 | B | Context Quality: Novelty & Discipline | 15 | Heuristic |
| 4 | C | Tribal Knowledge Externalization | 12 | Heuristic |
| 5 | H | Feedback-Loop Latency & Quality | 9 | Auto |
| 6 | A | Navigation & Structure-First Anchors | 8 | Heuristic |
| 7 | F | Freshness & Self-Maintenance | 8 | Auto |
| 8 | I | Environment & Task-Discovery Reproducibility | 5 | Auto |
| 9 | G | Agent Performance Outcomes (success ⁄ efficiency) | 3 | Auto |

**Gates(등급 상한)**: Gate-1 Reference Integrity(dangling reference 0) · Gate-2 Executable Verification(실행 가능한 test/build). 실패 시 등급 상한 AI-Fragile.

등급: 90+ AI-Native · 75+ AI-Ready · 60+ AI-Assisted · 40+ AI-Fragile · <40 AI-Hostile.

보고: `[AI-Readiness] {total}/100 · {grade}{ (gate 상한) } — 최약 {Cat}, Top ROI: {액션} → {산출물 경로}`

## Conventions

- **결정론 우선, 사람 보강**: score.py(stdlib only, Python 3.10+)가 자동 채점하고 LLM은 heuristic/manual 항목·E1 dangling 후보 확인을 보강한다. 손채점부터 하지 않는다.
- **gating(blocking > 가산)**: 하나의 blocking 결함이 등급에 상한을 씌운다(Kenogami lowest-as-ceiling·Factory 게이팅). 순수 가중합의 오탐을 피한다.
- **근거 서열 = 가중치 서열**: 실행·검증(E) ≫ 의존 구조(D) > 문맥 문서(B/C). ORACLE-SWE ablation 서열을 루브릭에 이식.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율은 점수화하지 않는다(ETH Zurich 2602.11988 반증). novelty·비중복·command-first만 가점.
- **god-file=결합도**: fan-in/out가 1급, 라인 수(>500)는 "근거 약함" 보조 신호(session-4 C8).
- **auto/heuristic/manual 라벨 + 근거 등급**: 모든 지표에 자동화 범위·근거 강도를 표기(정직성).
- **제안만(사람 집행)**: 코드를 자동 수정하지 않는다. 측정·시각화·ROI 제안만.
- **과장 금지**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지. 근거 부재 신호(라인 수 god-file·hallucination % 임계값·human 포매팅 가점)는 미채택.
- **경계**: 구조적 AI 접근성 정성 진단·개선 설계(ai-readable-codebase), 한 기능 구현·검증(backend-harness), 하네스 자체 진단(meta-harness), AI 생성물 평가 judge(eval-harness), 컨텍스트 조립(context-engineering), 완성 코드 리뷰·PR(frontend/git-harness)은 범위 밖. **ai-readable-codebase와는 상보**(측정 vs 정성 진단→개선).
- 단일 스킬 플러그인이므로 에이전트 팀(agents/)을 두지 않는다 — 스코어러 본성에 충실.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-03 | 플러그인 신설 | ai-readiness-cartography(코드베이스 AI 준비도 결정론적 측정·시각화). 외부 스킬 `ai-readiness-cartography`(v2 7카테고리 스코어러+대시보드)를 기반으로, deep-research(5 세션 적대 검증)로 수집한 2025~2026 1차 근거로 v3 리팩토링 — gating 집계 신설(2 blocking gate)·실행 검증 최상위 가중·기계 판독 의존 그래프·결합도 기반 god-file·보유율 폐기→anchor·redundancy discipline·신규 H/I 카테고리·success⁄efficiency 분리·auto/manual 라벨. 근거: ORACLE-SWE(2604.07789)·LocAgent(2503.09089)·ETH Zurich AGENTS.md(2602.11988)·USENIX slopsquatting(2025)·RepoMirage(2605.26177)·Factory/Kenogami readiness. |
