# ai-readiness-cartography

임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 개선을 설계하는(멀티 에이전트)** 도메인 무관 단일 스킬(2 모드). 측정 모드는 100점·9 카테고리 + 3 gate로 채점해 JSON 점수표 + HTML 대시보드 + ROI 가이드를 내고, 진단·개선 모드는 그 측정을 센서로 삼아 2축 진단 → 빌드 가드레일 → standalone → 수용 증명·재측정을 4에이전트로 설계한다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
ai-readiness-cartography/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 루브릭 요약 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·경계·근거
├── agents/                          # 진단·개선 모드 4 에이전트 (모두 model: "opus")
│   ├── accessibility-assessor.md    # Phase 0 — score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정
│   ├── guardrail-architect.md       # Phase 1 — 빌드 가드레일(의존 방향 물리 강제 + 피드백 3차원)
│   ├── standalone-designer.md       # Phase 2 — 도메인 슬라이스 독립 실행(port/adapter·use-case seed)
│   └── acceptance-verifier.md       # Phase 3 — 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe로 재측정
└── skills/
    └── ai-readiness-cartography/
        ├── SKILL.md                 # 오케스트레이터(모드 게이트 → 측정 워크플로 / 진단·개선 4-Phase)
        ├── scripts/score.py         # v3 결정론적 스코어러(stdlib only, gating·import 그래프·결합도, htmlsafe.json 동시 출력)
        ├── scripts/test_score.py    # 회귀 테스트(가중치 불변식·골든 픽스처·Gate-1 정밀도·htmlsafe)
        ├── assets/template.html     # 복사 후 채울 대시보드 원본(Inter/JetBrains Mono, 인라인 SVG)
        └── references/
            ├── scoring-rubric.md                    # v3 루브릭(9 카테고리 + 3 gate, 근거 등급·auto/manual 라벨)
            ├── ai-readable-codebase-principles.md   # 진단·개선 모드 원리(2축·빌드 가드레일·피드백 3차원·standalone·수용 증명)
            ├── ai-readiness-cartography-research.md  # 측정 근거 dossier 인덱스
            ├── ai-readable-codebase-research.md      # 개선 모드 근거 dossier(flex 5부작 + 2025+)
            └── research/                            # 2025~2026 1차 근거(합성 + 5 세션, 적대 검증)
└── evals/
    ├── evals.json                   # 수용 평가(루브릭·모드 불변식 file:section 인용 채점)
    └── trigger-eval.json            # 트리거 경계 평가(측정/개선 모드 + 인접 도메인 가드)
```

## 통합 등급 체계 요약 (100pt · 5밴드 · 3 gate)

등급은 **단일 5밴드**만 쓴다(별도 L1~L5 수치 스케일 폐기, `점수/20=L` 선형 변환 금지 — 거짓 정밀):

| Score | Level | | Score | Level |
|-------|-------|-|-------|-------|
| 90+ | **AI-Native** | | 40+ | **AI-Fragile** |
| 75+ | **AI-Ready** | | <40 | **AI-Hostile** |
| 60+ | **AI-Assisted** | | | |

**Gates(등급 상한)**: Gate-1 Reference Integrity(dangling 0)·Gate-2 Executable Verification(test/build)은 *Auto(score.py)*, 실패 시 상한 AI-Fragile. **Gate-3 Architecture Enforcement**(위반→빌드실패)는 *Heuristic·진단·개선 모드 전용*, 실패 시 상한 AI-Assisted. score.py는 Gate-3를 계산하지 않는다(측정 모드 "미평가").

카테고리 서열: E22·D18·B15·C12·H9·A8·F8·I5·G3.

보고: `[AI-Readiness] {total}/100 · {grade}{ (gate 상한) } — 최약 {Cat}, Top ROI: {액션} → {산출물 경로}`

## Conventions

- **모드 게이트 먼저**: 발동 시 *측정만*(python 1회) vs *개선까지 설계*(python + opus 4회)를 한 질문으로 확정한다 — 잘못된 모드는 비싼 오라우팅.
- **결정론 우선, 사람 보강**: score.py(stdlib only, Python 3.10+)가 자동 채점하고 LLM은 heuristic/manual 항목·E1 dangling 후보 확인·Gate-3 강제 판단을 보강한다. 손채점부터 하지 않는다.
- **gating(blocking > 가산)**: blocking 결함이 등급에 상한을 씌운다(Gate-1/2→AI-Fragile, Gate-3→AI-Assisted). 순수 가중합의 오탐을 피한다.
- **근거 서열 = 가중치 서열**: 실행·검증(E) ≫ 의존 구조(D) > 문맥 문서(B/C). ORACLE-SWE ablation 서열을 루브릭에 이식.
- **A축 ≠ Q축 · 구조가 프롬프트보다 먼저 · 빌드가 강제하고 문서가 설명한다**: (개선 모드) 코드 품질과 AI 접근성은 별개 축. 빌드로 잡을 수 있는 것을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율은 점수화하지 않는다(ETH Zurich 2602.11988 반증). novelty·비중복·command-first만 가점.
- **god-file=결합도**: fan-in/out가 1급, 라인 수(>500)는 "근거 약함" 보조 신호(session-4 C8).
- **generator/checker 분리**: 개선 모드에서 가드레일·standalone을 *설계*한 에이전트(Phase 1/2)와 등급을 *재측정*하는 검증자(Phase 3)를 분리한다.
- **제안만(사람 집행)**: 코드를 자동 수정하지 않는다. 측정·시각화·설계 제안만.
- **과장 금지**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지.
- **경계**: 한 기능 구현·검증(backend-harness), 상류 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인(cicd-harness), 명세 작성(spec-driven-development), 컨텍스트 조립(context-engineering), AI 생성물 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·PR(frontend/git-harness)은 범위 밖.
- 진단·개선 모드는 4 에이전트 협업이므로 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-07 | 신뢰 불가 repo 하드닝 (v0.2.1) | 보안 검토(재현 검증) 발견 4건 수정 — **(1) RE_LINE_RANGE ReDoS**: 좌측 경계 lookbehind 부재로 긴 문자 런에서 O(n²) 백트래킹(5MB 한 줄 README로 수 분 CPU, 재현) → 형제 regex(RE_PATH_REF)와 동일한 `(?<![A-Za-z0-9_/])` 추가. **(2) 최상위 심링크 path traversal**: `is_dir()`가 심링크를 따라가 repo 밖을 가리키는 최상위 심링크가 모듈로 채택·repo 밖 파일 읽음(재현) → `is_symlink()` 선제 배제(모듈 탐색 + apps/packages/services/plugins 하위). **(3) Gate-1 거짓 실패**: MAX_READ_BYTES 초과 파일의 count_lines=0을 "0줄"로 오독해 정상 대형 파일(schema.sql 등) range 참조가 전부 dangling→등급 오상한(재현) → 측정 불가면 판정 안 함(스코어러 정직성). **(4) null byte .py**: ast.parse가 SyntaxError 아닌 ValueError를 던져 전체 스캔 중단 → parse 실패로 처리. test_score.py 11→15건(4건 모두 회귀 핀) |
| 2026-07-05 | ai-readable-codebase 흡수 (v0.2.0) | 별도 플러그인 `ai-readable-codebase`(2축 진단→빌드 가드레일→standalone→수용 증명 4에이전트 하네스)를 이 플러그인의 **진단·개선 모드**로 흡수. 단일 스킬 2모드(측정/개선)로 통합, 4 에이전트(agents/) + 원리·근거 dossier 이관. **등급 단일화**: 폐기된 L1~L5 대신 score.py 5밴드로 통합하고 enforcement 축을 신규 **Gate-3 Architecture Enforcement**(Heuristic·개선 모드 전용)로 흡수(2→3 gate). score.py를 개선 모드의 결정론 센서(Phase 0 seed·Phase 3 재측정 델타)로 배선 — codebase가 LLM 판단으로만 주장하던 "계산적 통제·reward-hacking 가드"를 실제 코드로 충족. "단일 스킬이므로 에이전트 팀 없음" 정체성 규칙 제거. |
| 2026-07-03 | 다각도 검토 반영 (v0.1.1) | score.py 보강 — E1↔Gate-1 비대칭 해소·Gate-2 관대함 축소·`*.htmlsafe.json` 동시 출력(대시보드 XSS 차단을 결정론 코드로)·main() 예외 가드·read_text lru_cache. test_score.py 신설(11건). |
| 2026-07-03 | 플러그인 신설 | ai-readiness-cartography(코드베이스 AI 준비도 결정론적 측정·시각화). 외부 스킬 v2를 deep-research(5 세션 적대 검증) 2025~2026 1차 근거로 v3 리팩토링 — gating 집계·실행 검증 최상위 가중·기계 판독 의존 그래프·결합도 god-file·보유율 폐기→anchor·신규 H/I 카테고리·auto/manual 라벨. 근거: ORACLE-SWE·LocAgent·ETH Zurich·USENIX slopsquatting·RepoMirage·Factory/Kenogami. |
