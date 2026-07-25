# ai-readiness-cartography

git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 승인 게이트 뒤에 개선을 적용하는(멀티 에이전트)** 도메인 무관 단일 스킬(**3 모드·자유 조합**). **① 측정**은 100점·9 카테고리 + 3 gate로 채점해 JSON 점수표·HTML 대시보드·ROI 가이드를 낸다(코드 수정 없음). **② 진단·개선**은 그 측정을 센서로 2축(Q/A) 진단 → 빌드 가드레일 → standalone → **계획·개별 승인 뒤 코드 적용**(S/M/L·고위험 구조 리팩터 opt-in) → 수용 증명·재측정을 4 에이전트로 수행한다. **③ 코드 본문**은 `legibility_scan.py` census를 seed로 주석·명명·구조를 진단하고 **3게이트 승인 뒤에만** 단계별 수정한다(C0→C2→C1→C3). 여러 모드를 고르면 **①→②→③ 순**으로 이어 수행하고 `score.py`는 ①②가 1회 공유하며, ②+③이면 구조 리팩터는 ②가 소유하고 ③의 C3는 끈다. ③은 저장소 층 등급을 만들지 않고(census만), ②③ 모두 커밋하지 않는다(git-harness 핸드오프).

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
ai-readiness-cartography/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 루브릭 요약 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·경계·근거
├── agents/                          # 8 에이전트 (모두 model: "opus")
│   ├── accessibility-assessor.md    # ②Phase 0 — score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정
│   ├── guardrail-architect.md       # ②Phase 1 — 빌드 가드레일(의존 방향 물리 강제 + 피드백 3차원)
│   ├── standalone-designer.md       # ②Phase 2 — 도메인 슬라이스 독립 실행(port/adapter·use-case seed)
│   ├── acceptance-verifier.md       # ②Phase 4 — 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe
│   ├── comment-auditor.md           # ③ — 주석 4분류(오도/stale/noise/유효) → C0·C1 후보
│   ├── naming-analyst.md            # ③ — 명명 3축(오도>무의미>모호) → C2 후보 + 도구·위험 판정
│   ├── structure-cartographer.md    # ③ — 구조 후보(opt-in·"효과=추론" 라벨 필수)
│   └── behavior-guard.md            # ②③ 공용 — 변경/개입 클래스별 센서 실행·관측 (generator≠checker·②Phase 3 적용 + ③ C0~C3)
└── skills/
    └── ai-readiness-cartography/
        ├── SKILL.md                 # 오케스트레이터(모드 선택=①②③ 부분집합 → 선택분을 ①→②→③ 순차; ② 5-Phase(0~4·Phase 3 Apply 게이트)·③ 5-Phase(B0~B4·3게이트))
        ├── scripts/score.py         # ① v3 결정론 스코어러(gating·import 그래프·결합도·design_signals report-only·htmlsafe)
        ├── scripts/test_score.py    # ① 회귀 테스트(가중치 불변식·골든·Gate-1·design_signals 불변)
        ├── scripts/legibility_scan.py       # ③ 코드 본문 census 스캐너(stdlib only·등급 없음·개입 축 3 + census 전용 축 2)
        ├── scripts/test_legibility_scan.py  # ③ 회귀 테스트(68건·불변식·독립성 핀)
        ├── assets/template.html     # ① 대시보드 원본
        └── references/
            ├── scoring-rubric.md                    # ① v3 루브릭(9 카테고리 + 3 gate)
            ├── ai-readable-codebase-principles.md   # ② 개선 모드 원리
            ├── intervention-catalog.md              # ③ 개입 카드 C0~C3 정본(근거·위험·센서·거부 조건)
            ├── legibility-principles.md             # ③ 본문 층위 원리 8(삭제>추가·이름은 채널·테스트≠등가성 오라클·존재 가점 금지)
            ├── ai-readiness-cartography-research.md  # 측정 근거 인덱스
            ├── ai-readable-codebase-research.md      # 개선 근거
            └── research/                            # 1차 근거(session 1~7 + body-legibility/ dossier, 적대 검증)
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

- **모드 선택 먼저(자유 조합) · 문의는 한 번에 하나씩**: 발동 시 ①/②/③ 중 원하는 **부분집합**을 한 질문으로 고르고(다중 선택 허용), 모드를 확정한 *뒤에* 세부 스코프(경로→축→개입 클래스→고위험 opt-in)를 **하나씩** 묻는다(직전 답이 다음 질문을 결정). 여러 개면 ①→②→③ 순, `score.py`는 ①②가 **1회만** 공유 실행(③은 `legibility_scan.py` 별도), ②가 함께 돌면 Gate-3 판정이 측정의 "미평가"를 대체, ②+③이면 구조 리팩터는 ②가 소유하고 ③의 C3는 끈다.
- **결정론 우선, 사람 보강**: score.py(stdlib only, Python 3.10+)가 자동 채점하고 LLM은 heuristic/manual 항목·E1 dangling 후보 확인·Gate-3 강제 판단을 보강한다. 손채점부터 하지 않는다.
- **gating(blocking > 가산)** · **근거 서열 = 가중치 서열**: blocking 결함이 등급 상한을 씌우고(Gate-1/2→AI-Fragile, Gate-3→AI-Assisted), 실행·검증(E) ≫ 의존 구조(D) > 문맥 문서(B/C) 서열은 ORACLE-SWE ablation에서 온다.
- **A축 ≠ Q축 · 구조가 프롬프트보다 먼저 · 빌드가 강제하고 문서가 설명한다**: 코드 품질과 AI 접근성은 별개 축. 빌드로 잡을 수 있는 것을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율은 점수화하지 않는다(ETH Zurich 2602.11988 반증). novelty·비중복·command-first만 가점. **god-file=결합도**(fan-in/out 1급, 라인 수는 근거 약한 보조).
- **설계 원칙은 진단만, 점수화 안 함**: SOLID·응집/결합·복잡도·LCOM·중복은 `extras.design_signals`(report-only)로만 표면화하고 100점 등급에 넣지 않는다 — 고전 구조 지표는 코드 길이 통제 시 LLM 성능과 무상관(session-6)이고 준수도 점수화는 Goodhart를 부른다. 진단 대상: 식별자 명료성(R12)·모듈 순환 의존·정확 중복(Type-1/2)·과대추상·결합 hotspot. `test_score.py`가 "총점=9카테고리 합" 불변식을 고정한다.
- **generator/checker 분리**: 설계(Phase 1/2)·적용(Phase 3)과 재측정 검증자(Phase 4)를 분리하고, 센서는 `behavior-guard`가 실행 관측한다(자기보고 불신).
- **승인 게이트 뒤에만 수정**: ①은 측정·시각화만. ②③은 제안·설계 후 승인 게이트(②=계획·개별, ③=3게이트) 뒤에 코드를 수정하고(고위험 opt-in·리네임=AST/LSP 위임·"테스트 통과≠동작 보존"), 커밋은 하지 않는다.
- **결정 권한(위험은 경고, 수용은 사용자)**: 고위험 변경(②의 L·③의 C3) 위험은 *경고*하되 감수는 *사용자*가 결정한다. opt-in·개별 승인된 항목을 회귀 위험을 이유로 **조용히 보류·강등하지 않고**(승인 게이트 ≠ veto), 새 차단 요인은 **execute-or-escalate**. **자동 테스트 부재는 거부 사유가 아니라 행위 센서 승격 사유**다(UNVERIFIED는 관측 한계 라벨·red 센서만 롤백). "리팩토링" 요청을 S 툴링으로 대체 충족하지 않고, 인도분이 요청 클래스와 다르면 정직히 밝힌다.
- **본문 층은 등급을 만들지 않고 볼륨에 가점하지 않는다(③)**: census는 report-only이고, **마크업 시맨틱(MK*)·테스트 설명(TL*)은 census 전용 축**이다 — 이들을 격리해 LLM 이해 델타를 잰 연구가 없고(O-6) 접근성 개선은 이 하네스의 표적이 아니므로 **개입 카드를 두지 않는다**(자동 ARIA/alt/어서션 생성 금지). comment-gap(C7~C9)도 결함이 아니라 '왜' 주석 추가 후보(opt-in·사람 검증·볼륨 무점수).
- **과장 금지**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지. 구조 리팩터 효과는 추론(측정 아님).
- **경계**: 한 기능 구현·검증(backend-harness), 상류 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인(cicd-harness), 명세 작성(spec-driven-development), 컨텍스트 조립(context-engineering), 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·PR(frontend/git-harness)은 범위 밖.
- SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**하고, 선택된 축·클래스에 해당하는 에이전트만 호출한다(스코프 가드).

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-25 | skill-creator 평가 → 군살 제거 (v0.6.0) | 사용자 요청(skill-creator 관점 평가 후 불필요 기능 삭제·description 축약). **삭제 ①** 모드 ③의 **C4(테스트 설명)·C5(마크업 시맨틱) 개입 경로 전면 제거** — 이 축들은 스스로 "AI 이해 개입 근거 부재(O-6)"를 명시하고 효과를 접근성·사람 가독성으로만 말하게 되어 있어, AI 준비도 하네스 안에서 개입 카드·전용 에이전트·센서 매트릭스·6개 파일에 반복되는 정직성 가드를 유지할 근거가 없었다. `MK*`·`TL*` 탐지기는 **census 전용 축**으로 남겨 결함 후보만 보여주고(코드 수정 경로 없음), 개입 카드 C4a/C4b/C5a/C5b·에이전트 `markup-test-auditor`·behavior-guard 4행 + 클래스별 맹점 문단을 제거. 개입 클래스는 **C0~C3**로 복귀. **삭제 ②** `legibility_scan.py`의 `--git-drift`(git blame 기반 주석 드리프트 ~130줄·`C6_COMMENT_DRIFT`·`git_available`/`_git_line_times`·CLI 플래그) — SKILL 워크플로 B1이 한 번도 켜지 않는 **도달 불가 기능**이었다. **축약** SKILL description 2,230→875자·plugin/marketplace description 3,314→1,312자(트리거와 무관한 등급표·gating 규칙·근거 논문·조합 규약·정직성 전문이 본문에 이미 있는 채로 중복), SKILL 본문 381→338줄(같은 불변식이 내재화 원칙·조합 규약·Phase 3·B-모드 불변식·pitfalls에 3~6회 중복 → 정본 1곳 + 참조, 대시보드 Style rules 4항목 → M2 한 문단, Common pitfalls 18→9), plugin CLAUDE.md Conventions·Change History 압축. **staleness 교정**: README 모드 ③ 절이 v0.5.0 이전(4 에이전트·C0~C3)으로 남아 있던 것. 테스트 legibility 69→**68**건(git-drift 1건 제거·나머지 불변)·score 25건 불변, `score.py` **불변**. 정직성 규약은 전부 보존(gating·근거 등급·auto/heuristic/manual·결정 권한·UNVERIFIED·테스트≠동작 보존·오귀속 금지). |
| 2026-07-25 | design-principle-harness 흡수 (v0.5.0) | DPH 기능의 ~80~85%가 이미 존재함을 확인(정체성 문장 동일·Track B 6지표 ≈ ②의 A축 진단·Tier A ≈ ③의 naming/comments·`behavior-guard` 이름까지 중복)해 **고유 3자산만 흡수하고 플러그인 제거**: Tier C → 모드 ③의 `markup`(MK1~MK4)·`tests`(TL1~TL2) 축, comment-gap 탐지기(C7 침묵 예외·C8 매직 넘버·C9 정규식) → C1의 '왜/맥락' 주석 opt-in 경로, **한 번에 한 질문** 인터랙션. DPH의 설계 원칙 40점 배점은 **미흡수**(report-only 정책 유지 — 고전 구조 지표는 LLM 성능과 무상관·준수도 점수화는 Goodhart). 흡수한 마크업·테스트 축은 근거 부재(O-6)를 명시 → v0.6.0에서 개입 경로를 걷어내고 census 전용으로 정리. 근거 dossier `research/body-legibility/semantic-markup-tests.md`·`legibility-principles.md` 원리 8 신설. describe 한 단어 제목 모호 오판 교정. |
| 2026-07-12 | 결정 권한·센서 승격 (v0.4.1) | 실측 결함 수정 — 사용자가 고위험 구조 리팩터(L/C3)를 opt-in 했는데도 에이전트가 회귀 위험을 이유로 **조용히 보류**해 툴링만 남은 **권한 전도** 교정. 4 불변식 신설: INV-1 결정 권한(위험은 경고·수용은 사용자·조용한 보류 금지·execute-or-escalate), INV-2 센서 승격(무테스트→행위 센서·거부 아님), INV-3 행위 센서 명명(`verify`/`run`·UNVERIFIED는 관측 한계 라벨), INV-4 인도 정합(리팩토링 요청에 L 전면화·과소 인도 금지). 적대 검증으로 격리 렌더 센서 맹점(라우트·직렬화·동적 import·외부 소비자)을 C2 거부 조건과 대칭 이식. 스코어러·스캐너 코드 불변. |
| 2026-07-12 | ②도 승인 후 코드 적용 (v0.4.0) | 통합 파이프라인 '측정 → 제안·설계 → 승인 → 코드 수정'. ② 진단·개선 모드를 설계 전용 → **게이트된 적용**으로 확장(Phase 3 신설: 계획 승인 → 개별 승인 → S/M/L 위험 등급·이동/리네임=AST/LSP 위임·`behavior-guard` 센서 관측·L은 UNVERIFIED 상한). 핵심 불변식 전환: '③만 코드 수정' → **'① 측정만·②③은 승인 게이트 뒤 수정'**. |
| 2026-07-12 | 모드 자유 조합 (v0.3.1) | 3분기 택일이던 모드 게이트를 **부분집합 다중선택**으로 전환(①→②→③ 순차·score.py는 ①②가 1회 공유·②가 함께 돌면 Gate-3 판정이 "미평가"를 대체·②+③이면 ③의 구조는 ②에 위임·본문 편집 효과의 등급 귀속 금지·산출물 같은 slug 하위 정렬). 함께 '2모드'로 남아 있던 README·marketplace·`_docs` staleness 교정. |
| 2026-07-12 | code-legibility-harness 흡수 → 모드 ③ 신설 (v0.3.0) | 별도 플러그인의 **코드 본문 층위 진단 + 승인 후 단계별 적용**을 모드 ③으로 흡수하고 플러그인 제거. 가져온 것: `legibility_scan.py` census 스캐너 + 회귀 테스트 + 4 에이전트 + intervention-catalog·legibility-principles·body-legibility dossier. **핵심 정직성**: ③은 저장소 층 등급을 만들지 않는다(본문 신호 거의 전부 report-only — 주석↔코드 정합성 정밀 0.39·자동 주석 ~20~45% 부정확·구조 리팩터 효과=추론). 명명 채널만 실측 인과(난독화 −11~−29pt), 오도 주석 삭제만 위험 0. 툴그래프 델타(LocAgent·RepoGraph)를 본문 수정 효과로 오귀속 금지. |
| 2026-07-11 | 식별자 명료성(R12) 내부 구현 (v0.2.3) | 자매 플러그인 의존 없이 자체 갭을 채움 — `compute_design_signals`에 `identifier_clarity`(report-only) 추가(선언 이름 기준 무의미·단일문자 비율). 등급 미반영(readability→성공 인과 미확립). 검증 중 발견·수정: 비-ASCII 미측정 명시, **순환 의존 모듈 granularity를 top-level → 디렉터리 수준으로 교정**(src/-루트 저장소에서 intra-src 순환을 놓치던 실측 결함). 엣지 배터리(빈 repo·바이너리·유니코드·ReDoS·손상 Python·htmlsafe XSS) 통과. |
| 2026-07-11 | 설계 원칙 진단 신호 추가 (v0.2.2) | SOLID·응집/결합·복잡도·중복 측정 요청을 deep-research로 검토 → **점수화가 아니라 진단(report-only)** 으로 반영. `extras.design_signals` 신설(모듈 순환 의존 Tarjan SCC·정확 중복 Type-1/2·과대추상·결합 hotspot), 전부 등급 미반영. 왜 점수화 안 하나(session-6): 고전 구조 지표는 코드 길이 통제 시 LLM 성능과 무상관·설계 원칙 점수화는 Goodhart·LCOM은 8변종 신뢰 불가. |
| 2026-07-07 | 신뢰 불가 repo 하드닝 (v0.2.1) | 보안 검토 발견 4건 수정 — RE_LINE_RANGE ReDoS(좌측 경계 lookbehind 부재로 O(n²)), 최상위 심링크 path traversal(repo 밖 파일 읽음), MAX_READ_BYTES 초과 파일의 count_lines=0 오독으로 인한 Gate-1 거짓 실패(측정 불가면 판정 안 함), null byte `.py`의 ValueError로 전체 스캔 중단. 4건 모두 회귀 핀. |
| 2026-07-05 | ai-readable-codebase 흡수 (v0.2.0) | 별도 플러그인(2축 진단→가드레일→standalone→수용 증명 4에이전트)을 **진단·개선 모드**로 흡수. 단일 스킬 2모드로 통합, 폐기된 L1~L5 대신 5밴드로 등급 단일화하고 enforcement 축을 **Gate-3**(Heuristic·개선 모드 전용)로 흡수(2→3 gate). score.py를 개선 모드의 결정론 센서(Phase 0 seed·재측정 델타)로 배선. |
| 2026-07-03 | 다각도 검토 반영 (v0.1.1) | score.py 보강 — E1↔Gate-1 비대칭 해소·Gate-2 관대함 축소·`*.htmlsafe.json` 동시 출력(대시보드 XSS 차단을 결정론 코드로)·main() 예외 가드·read_text lru_cache. test_score.py 신설(11건). |
| 2026-07-03 | 플러그인 신설 | 코드베이스 AI 준비도 결정론적 측정·시각화. 외부 스킬 v2를 deep-research(5 세션 적대 검증) 2025~2026 1차 근거로 v3 리팩토링 — gating 집계·실행 검증 최상위 가중·기계 판독 의존 그래프·결합도 god-file·보유율 폐기→anchor·신규 H/I 카테고리·auto/manual 라벨. 근거: ORACLE-SWE·LocAgent·ETH Zurich·USENIX slopsquatting·RepoMirage·Factory/Kenogami. |
