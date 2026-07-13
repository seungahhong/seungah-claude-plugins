# ai-readiness-cartography

임의 git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 개선을 설계·적용하며(멀티 에이전트) 승인 게이트 뒤에 구조·본문 코드를 수정하는** 도메인 무관 단일 스킬(**3 모드·자유 조합**). ① 측정 모드는 100점·9 카테고리 + 3 gate로 채점해 JSON 점수표 + HTML 대시보드 + ROI 가이드를 낸다. ② 진단·개선 모드는 그 측정을 센서로 2축 진단 → 빌드 가드레일 → standalone → **계획·개별 승인 게이트 뒤 코드 적용**(위험 등급 S/M/L·고위험 구조 리팩터 opt-in·AST/LSP 위임·behavior 센서) → 수용 증명·재측정을 4에이전트로 제안·설계·적용한다. **③ 코드 본문 층위 모드**(구 code-legibility-harness 흡수·v0.3.0)는 `legibility_scan.py` census(등급 없음)를 seed로 주석·명명·함수/모듈 granularity를 다각도 진단하고, **3게이트 승인(계획→개별→최종) 뒤에만 단계별로 코드를 수정**한다(P1 오도·stale 주석 삭제→P2 안전 리네임(AST/LSP)→P3 검증된 계약 주석→P4 구조 opt-in). **세 모드는 배타 택일이 아니라 자유 조합**이며(임의 부분집합), 여러 개를 고르면 **①→②→③ 순으로 이어 수행**한다(score.py는 ①②가 1회 공유·②+③이면 구조 리팩터는 ②가 적용하고 ③의 C3는 끔). **①은 측정만(코드 수정 안 함)·②③은 제안·설계 후 승인 게이트 뒤에 코드를 수정하며**(②=계획·개별 승인·고위험 opt-in, ③=3게이트), ③은 저장소 층 등급을 만들지 않는다(census만). ②③ 모두 커밋 안 함(git-harness 핸드오프).

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
│   └── behavior-guard.md            # ②③ 공용 — 변경/개입 클래스별 센서 실행·관측 (generator≠checker·②Phase 3 적용 + ③)
└── skills/
    └── ai-readiness-cartography/
        ├── SKILL.md                 # 오케스트레이터(모드 선택=①②③ 부분집합 → 선택분을 ①→②→③ 순차; ② 5-Phase(0~4·Phase 3 Apply 게이트)·③ 5-Phase(B0~B4·3게이트))
        ├── scripts/score.py         # ① v3 결정론 스코어러(gating·import 그래프·결합도·design_signals report-only·htmlsafe)
        ├── scripts/test_score.py    # ① 회귀 테스트(가중치 불변식·골든·Gate-1·design_signals 불변)
        ├── scripts/legibility_scan.py       # ③ 코드 본문 census 스캐너(stdlib only·등급 없음·7 탐지기)
        ├── scripts/test_legibility_scan.py  # ③ 회귀 테스트(49건·불변식·독립성 핀)
        ├── assets/template.html     # ① 대시보드 원본
        └── references/
            ├── scoring-rubric.md                    # ① v3 루브릭(9 카테고리 + 3 gate)
            ├── ai-readable-codebase-principles.md   # ② 개선 모드 원리
            ├── intervention-catalog.md              # ③ 개입 카드 C0~C3 정본(근거·위험·센서·거부 조건)
            ├── legibility-principles.md             # ③ 본문 층위 원리(삭제>추가·이름은 채널·테스트≠등가성 오라클)
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

- **모드 선택 먼저(자유 조합)**: 발동 시 ①측정/②진단·개선/③본문 중 원하는 **부분집합**을 한 질문으로 고른다(다중 선택 허용·기본은 물어봄). 여러 개면 ①→②→③ 순으로 이어 수행하고 `score.py`는 ①②가 **1회만** 공유 실행한다(③은 `legibility_scan.py` 별도). ②가 함께 돌면 Gate-3 판정이 측정의 "미평가"를 대체하고, ②+③이면 구조 리팩터는 ②가 설계·적용으로 소유하며 ③의 C3는 끈다(이중 처리 방지). 비용은 선택분의 가산 합 — 택일이 아니라 '불필요한 모드 미선택'으로 통제한다.
- **결정론 우선, 사람 보강**: score.py(stdlib only, Python 3.10+)가 자동 채점하고 LLM은 heuristic/manual 항목·E1 dangling 후보 확인·Gate-3 강제 판단을 보강한다. 손채점부터 하지 않는다.
- **gating(blocking > 가산)**: blocking 결함이 등급에 상한을 씌운다(Gate-1/2→AI-Fragile, Gate-3→AI-Assisted). 순수 가중합의 오탐을 피한다.
- **근거 서열 = 가중치 서열**: 실행·검증(E) ≫ 의존 구조(D) > 문맥 문서(B/C). ORACLE-SWE ablation 서열을 루브릭에 이식.
- **A축 ≠ Q축 · 구조가 프롬프트보다 먼저 · 빌드가 강제하고 문서가 설명한다**: (개선 모드) 코드 품질과 AI 접근성은 별개 축. 빌드로 잡을 수 있는 것을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율은 점수화하지 않는다(ETH Zurich 2602.11988 반증). novelty·비중복·command-first만 가점.
- **god-file=결합도**: fan-in/out가 1급, 라인 수(>500)는 "근거 약함" 보조 신호(session-4 C8).
- **설계 원칙은 진단만, 점수화 안 함**: SOLID·응집/결합·복잡도·LCOM·중복 등은 `extras.design_signals`(report-only)로만 표면화하고 **100점 등급에 넣지 않는다** — 고전 구조 지표는 코드 길이 통제 시 LLM 성능과 무상관(session-6·보유율 미점수화와 같은 기준)이고 준수도 점수화는 Goodhart/reward-hacking을 부른다. 신뢰 가능·에이전트 관련 신호만 진단: **식별자 명료성(R12: 무의미·난독형 선언 이름 비율 — 자기 갭을 내부에서 채움)**·모듈 순환 의존(acyclic dependencies)·정확 중복(Type-1/2)·과대추상(단일 구현 인터페이스)·결합 hotspot. 미채택: 복잡도/LCOM 점수·의미 중복·DI/IoC 준수도. `test_score.py`가 "총점=9카테고리 합" 불변식을 고정한다.
- **generator/checker 분리**: 개선 모드에서 가드레일·standalone을 *설계*한 에이전트(Phase 1/2)·*적용*(Phase 3)과 등급을 *재측정*하는 검증자(Phase 4)를 분리한다.
- **제안만(사람 집행) — ②③은 승인 후 적용**: ① 측정 모드는 코드를 자동 수정하지 않는다(측정·시각화 제안만). ②③은 제안·설계 후 승인 게이트(②=계획·개별, ③=3게이트) 뒤에 코드를 수정하고(고위험 변경=②의 구조 리팩터·③의 C3는 opt-in·AST/LSP 위임·behavior 센서 관측·"테스트 통과≠동작 보존"), 커밋은 하지 않는다(git-harness 핸드오프).
- **결정 권한(위험은 경고, 수용은 사용자)**: 고위험 변경(②의 L 구조 리팩터·③의 C3)의 위험은 *경고*하되 감수는 *사용자*가 결정한다. opt-in·개별 승인된 항목을 에이전트가 회귀 위험을 이유로 **조용히 보류·강등·"제안만"으로 되돌리지 않는다**(승인 게이트는 무단 실행 방지 장치이지 승인된 실행의 veto가 아니다). 적용 중 새 차단 요인은 **execute-or-escalate**로 사용자에게 되돌린다. **자동 테스트 부재는 L/C3 거부 사유가 아니라 행위 센서(실제 실행·렌더로 baseline 대조·`verify`/`run`) 승격 사유**다(UNVERIFIED는 관측 한계 라벨이지 거부 신호 아님·red 센서만 롤백). "리팩토링" 요청을 S 툴링으로 대체 충족하지 않고, 인도분이 요청 클래스와 다르면 정직히 밝힌다(과소 인도 금지).
- **과장 금지**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지.
- **경계**: 한 기능 구현·검증(backend-harness), 상류 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인(cicd-harness), 명세 작성(spec-driven-development), 컨텍스트 조립(context-engineering), AI 생성물 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·PR(frontend/git-harness)은 범위 밖.
- 진단·개선 모드는 4 에이전트(+ 적용 Phase 3에서 `behavior-guard` 재사용) 협업이므로 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-12 | 결정 권한·센서 승격 (v0.4.1) | 플러그인 테스트 실측 결함 수정 — 사용자가 고위험 구조 리팩터(L/C3)를 두 번 opt-in 했는데도 에이전트가 회귀 위험을 이유로 **조용히 보류**해 실제 코드 리팩토링이 거의 일어나지 않고 툴링(eslint·CI·설정)만 남은 **권한 전도(authority inversion)**를 교정. 근본 원인 3+1: (D1) 4곳의 "**테스트 스위트 부재 시 L/C3 거부**" 규칙이 무테스트 god-file 분할을 애초에 차단 — 테스트는 약한 오라클(≈21% 누락)인데 그 부재를 유일 실격 사유로 삼는 비정합; (D2) L/C3 프레이밍이 거부 일방 래칫(경고·거부조건·UNVERIFIED)뿐 **결정 권한 불변식 부재**(승인 게이트를 에이전트 veto로 오독); (D3) S 추가형 기본 ON이 "리팩토링" 요청을 툴링으로 대체 충족(인도 정합 점검 부재); (D4) 올바른 센서(**행위 실행·렌더**)를 하네스가 명명하지 않아 "무테스트=무센서=거부"로 붕괴. **수정 4 불변식**: INV-1 결정 권한(위험은 경고·수용은 사용자·승인된 고위험 변경 조용한 보류 금지·새 차단은 execute-or-escalate), INV-2 센서 승격(무테스트→행위 센서·거부 아님·모든 센서 불가 시에만 사용자에게 결정 escalate), INV-3 행위 센서 명명(behavior-guard 매트릭스에 행위 실행·렌더 추가·`verify`/`run` 연계·UNVERIFIED는 관측 한계 라벨이지 거부 신호 아님·red 센서만 롤백), INV-4 인도 정합(리팩토링 요청에 L 전면화·요청vs적용 클래스 정직 보고·과소 인도 금지). **정직성 전부 보존**(효과=추론 O-1·19~35% 비등가·UNVERIFIED 상한·테스트≠동작 보존·수치 약속 없음·AST/LSP 위임·승인 게이트 유지). 스코어러/스캐너 코드·테스트 **불변**(오케스트레이션·에이전트 계약만 변경). SKILL(내재화 원칙·Phase 3 3a/3b·마무리 인도 정합·③ B0/B3·B-모드 불변식·Common pitfalls 2)·intervention-catalog(C3 센서/도구/게이트/거부조건)·structure-cartographer(opt-in 결정 안 뒤집음·거부조건·schema)·behavior-guard(C3 행위 센서·UNVERIFIED 라벨·금지사항)·CLAUDE·README·evals 반영. **적대 검증 반영(4-lens 5-agent workflow, YES-WITH-FIXES)**: (H1) 무테스트 거부 제거가 벗겨낸 *격리 렌더 센서 맹점*(공개 API·파일 라우트·직렬화/lazy-chunk·동적/리플렉션 import·외부 소비자)을 C2 런타임 파괴 거부 조건과 대칭으로 3 C3 사이트(catalog 경계 주의·structure-cartographer 경계 노출 schema·behavior-guard 격리 센서 맹점)에 이식 — 거부가 아니라 *실제 라우트/소비자 구동 센서로 승격 + 사람 escalate*·격리 green을 VERIFIED로 안 올림(결정 권한 유지); (H2) SKILL 하드홀드 트리거가 *적용 도구*(LSP extract/move)를 *센서* 부재로 혼동하고 항상 가용한 사람 diff 리뷰를 누락하던 것을 정정; (H3) 사용자 지목 구조 대상의 계획표 누락 금지(사전 단계 권한 전도 차단). 정직성 8종(효과=추론·19~35% 비등가·UNVERIFIED 상한·테스트≠동작 보존·수치 약속 없음·리네임 AST/LSP·3승인 게이트·reward-hacking 불신) 전부 intact 확인. |
| 2026-07-12 | ②도 승인 후 코드 적용 (v0.4.0) | 사용자 요청 — 통합 파이프라인 **'측정 → 제안·설계 → 사용자 승인 → 코드 수정'**. ② 진단·개선 모드를 **설계 전용 → 게이트된 적용**으로 확장: Phase 0 진단 → 1·2 설계 → **Phase 3 적용(NEW·계획 승인 게이트→개별 승인 게이트→위험 등급 S/M/L·추가형 직접 write·이동/리네임=AST/LSP 위임·`behavior-guard` 센서 관측·고위험 구조 리팩터 opt-in·"테스트 통과≠동작 보존"·L은 UNVERIFIED 상한)** → Phase 4 수용 증명·재측정. `behavior-guard`를 ②③ 공용 검증자로 확장. **핵심 불변식 전환**: '①②는 코드 수정 안 함·③만 수정' → **'① 측정만·②③은 승인 게이트 뒤에만 수정'**. ②③ 모두 커밋 안 함(git-harness 핸드오프). **정직성 보존**: 구조 리팩터 효과=추론(직접 측정 근거 없음)·LLM 리팩터 19~35% 비등가·≈21%가 테스트 통과 → 고위험 opt-in·강제 probe로만 등급 상승 귀속·오귀속 금지. 스코어러/스캐너 코드·테스트(25+49) **불변**(오케스트레이션·에이전트 계약만 변경). SKILL·plugin.json·marketplace·README·CLAUDE·`_docs`×2·evals + 에이전트 5종(guardrail/standalone/acceptance/assessor/behavior-guard) 반영. |
| 2026-07-12 | 모드 자유 조합 (v0.3.1) | 사용자 요청 — 발동 시 세 모드를 **3분기 택일**로 확정하던 모드 게이트를 **부분집합 다중선택(자유 조합)**으로 전환. 선택분을 **①→②→③ 순차** 실행하고, `score.py`는 ①②가 **1회만 공유** seed(③은 `legibility_scan.py` 별도), **②가 함께 돌면 Gate-3 판정이 측정의 '미평가'를 대체**, **②+③이면 ③의 P4 구조 리팩터를 ②의 remediation-plan에 위임**(구조를 두 번 설계 안 함·코드를 쓰는 건 여전히 ③뿐·②는 쓰기 없음 유지), **③ 본문 편집 효과를 저장소 등급/툴그래프 델타에 귀속 금지**(오귀속·Goodhart), 산출물은 ②③가 같은 `.claude/ai-readability/{slug}/` 하위로 정렬. 스코어러(`score.py`)·census(`legibility_scan.py`) 코드·테스트(25+49)는 **불변**(오케스트레이션 계약만 변경). 함께 교정한 v0.3.0 staleness: README·marketplace.json·`_docs/skills.md`·`_docs/project-structure.md`·evals.json가 '2모드'로 남아 모드 ③를 누락하던 것, SKILL.md·README·CLAUDE의 전역 '코드 자동 수정 안 함' 규약이 ③와 모순되던 것을 '①②만 제안·③만 승인 후 수정'으로 정정. 적대 리뷰(4차원×verify 10에이전트)로 조합 실행 규약을 워크플로 명령까지 배선(census 출력 경로·Phase 0a 재실행 금지·대시보드 Gate-3 타이밍·②+③ C3 억제). |
| 2026-07-12 | code-legibility-harness 흡수 → 모드 ③ 신설 (v0.3.0) | 사용자 요청 — 별도 플러그인 `code-legibility-harness`의 **코드 본문 층위 진단 + 승인 후 단계별 적용**을 이 플러그인의 **모드 ③**으로 흡수하고 code-legibility 플러그인은 제거(마켓플레이스 단일화, ai-readable-codebase 흡수와 동형). `/deep-research`(104 에이전트·적대 검증 완료) 근거로 통합. **가져온 것**: `legibility_scan.py`(census 스캐너·등급 없음·7 탐지기) + `test_legibility_scan.py`(49건) + 4 에이전트(comment-auditor/naming-analyst/structure-cartographer/behavior-guard) + intervention-catalog·legibility-principles + research/body-legibility/ dossier. SKILL에 모드 ③ 워크플로(B0 스코프(C0~C3 체크박스)→B1 census+다각도 진단→B2 제안표+게이트 A→B3 개별 적용+게이트 B(behavior-guard 센서 실행)→B4 재확인+게이트 C) + 모드 게이트 3분기 추가. **핵심 정직성(session-7 근거)**: **모드 ③는 저장소 층 등급(0~100)을 만들지 않는다** — 본문 층 신호는 거의 전부 report-only(주석↔코드 정합성 현실분포 정밀 0.39·자동 주석 생성 ~20~45% 부정확·Type-4 클론 93% 오라벨·구조 리팩터 효과=추론 O-1). 명명 채널만 실측 인과(구조보존 난독화 -11~-29pt), 오도 주석 삭제(P1)만 위험 0. **저장소 층 델타(LocAgent 92.7%·RepoGraph +32.8%)는 툴 그래프 인덱스 효과지 본문 수정 효과 아님(오귀속·Goodhart 금지)**. ①②는 코드 수정 안 함·③만 3게이트 승인 후 수정·리네임=AST/LSP 위임·"테스트 통과≠동작 보존"·커밋 안 함. 테스트 25(score)+49(legibility)=74건. |
| 2026-07-11 | 식별자 명료성(R12) 자기 갭 내부 구현 (v0.2.3) | 사용자 요청 — code-legibility-harness의 이번 회차 수정은 롤백하고, cartography가 **자매 플러그인에 의존하지 않도록**(측정 결과: cartography→code-legibility 종속 패스는 애초에 없었음) cartography의 **자체 미구현 갭**을 내부에서 채움. score.py `compute_design_signals`에 **`identifier_clarity`**(report-only) 추가 — 선언(함수/클래스/최상위 변수) 이름 기준 무의미(tmp/data/foo…)·단일문자(비-관용) 식별자 비율. cartography 자신의 **R12/session-1 C3~C5**("readability 지표 = 식별자 명료성·낮은 난독도", 난독→comprehension 저하 arXiv:2601.05485 CONFIRMED)가 요구했으나 v3 9카테고리에 없던 빈칸(code-legibility가 채우던 것)을 흡수. **등급 미반영**(session-1 C5: readability→성공 인과 미확립 — 사용자와 report-only 합의). 지역 변수·파라미터·비-ASCII 식별자는 미측정(선언 수준 ASCII 근사·미측정≠명료함). rubric Design Signals 표·accessibility-assessor 반영. **검증 2회차 + 예상 시나리오 실행**으로 발견·수정: (1) `identifier_clarity` note에 비-ASCII 미측정 명시(honesty), (2) **순환 의존 모듈 granularity를 top-level 세그먼트 → 디렉터리 수준으로 교정** — src/-루트 저장소에서 모든 파일이 'src' 한 모듈로 붕괴해 intra-src 순환(services↔utils)을 놓치던 것을 실측으로 발견, 디렉터리 기준(예: src/services)으로 잡도록 수정(JS/TS·top-level Python 패키지 유효, Python 중첩 패키지는 과소탐지 명시). 엣지 배터리(빈 repo·바이너리·대용량·유니코드·ReDoS 0.003s·결정론·손상 Python·htmlsafe XSS) 통과. 테스트 21→25건(총점 불변 핀·src-nested 순환 회귀 핀 포함). |
| 2026-07-11 | 설계 원칙 진단 신호 추가 (v0.2.2) | 사용자 요청(SOLID·응집/결합·복잡도·중복 등을 측정·점수화)을 deep-research(24소스, 핵심 4건 적대 검증 완료·나머지 sourced)로 검토 → **점수화가 아니라 진단(report-only)** 으로 반영(사용자 합의). score.py에 `extras.design_signals` 신설 — **모듈 순환 의존**(Tarjan SCC, 기존 import 그래프 재사용·acyclic dependencies principle)·**정확 중복**(Type-1/2 정규화 라인 매칭, 문자열/숫자/공백 무시·의미 중복은 측정 불가라 미보고)·**과대추상**(단일 구현 TS 인터페이스, over-applied SOLID 반대편 신호)·**결합 hotspot**(재노출). 전부 등급/총점에 **미반영**(9카테고리 합 불변). **왜 점수화 안 하나**(session-6 신설): 고전 구조 지표(cyclomatic·LCOM·MI)는 코드 길이 통제 시 LLM 성능과 **무상관**(보유율 미점수화와 같은 기준)·설계 원칙 점수화는 **Goodhart/reward-hacking**(정적 스멜 오라클은 표면 변형으로 게임)·LCOM은 8변종 신뢰 불가. rubric '넣지 말 것'+Design Signals 절, 개선 모드 2에이전트(순환=가드레일 1급 표적·과대추상=간접참조 축소 후보) 반영. 테스트 15→21건(순환·중복·과대추상 탐지 + 총점 불변 핀). ReDoS-safe·비용 상한(윈도우·모듈 수). |
| 2026-07-07 | 신뢰 불가 repo 하드닝 (v0.2.1) | 보안 검토(재현 검증) 발견 4건 수정 — **(1) RE_LINE_RANGE ReDoS**: 좌측 경계 lookbehind 부재로 긴 문자 런에서 O(n²) 백트래킹(5MB 한 줄 README로 수 분 CPU, 재현) → 형제 regex(RE_PATH_REF)와 동일한 `(?<![A-Za-z0-9_/])` 추가. **(2) 최상위 심링크 path traversal**: `is_dir()`가 심링크를 따라가 repo 밖을 가리키는 최상위 심링크가 모듈로 채택·repo 밖 파일 읽음(재현) → `is_symlink()` 선제 배제(모듈 탐색 + apps/packages/services/plugins 하위). **(3) Gate-1 거짓 실패**: MAX_READ_BYTES 초과 파일의 count_lines=0을 "0줄"로 오독해 정상 대형 파일(schema.sql 등) range 참조가 전부 dangling→등급 오상한(재현) → 측정 불가면 판정 안 함(스코어러 정직성). **(4) null byte .py**: ast.parse가 SyntaxError 아닌 ValueError를 던져 전체 스캔 중단 → parse 실패로 처리. test_score.py 11→15건(4건 모두 회귀 핀) |
| 2026-07-05 | ai-readable-codebase 흡수 (v0.2.0) | 별도 플러그인 `ai-readable-codebase`(2축 진단→빌드 가드레일→standalone→수용 증명 4에이전트 하네스)를 이 플러그인의 **진단·개선 모드**로 흡수. 단일 스킬 2모드(측정/개선)로 통합, 4 에이전트(agents/) + 원리·근거 dossier 이관. **등급 단일화**: 폐기된 L1~L5 대신 score.py 5밴드로 통합하고 enforcement 축을 신규 **Gate-3 Architecture Enforcement**(Heuristic·개선 모드 전용)로 흡수(2→3 gate). score.py를 개선 모드의 결정론 센서(Phase 0 seed·Phase 3 재측정 델타)로 배선 — codebase가 LLM 판단으로만 주장하던 "계산적 통제·reward-hacking 가드"를 실제 코드로 충족. "단일 스킬이므로 에이전트 팀 없음" 정체성 규칙 제거. |
| 2026-07-03 | 다각도 검토 반영 (v0.1.1) | score.py 보강 — E1↔Gate-1 비대칭 해소·Gate-2 관대함 축소·`*.htmlsafe.json` 동시 출력(대시보드 XSS 차단을 결정론 코드로)·main() 예외 가드·read_text lru_cache. test_score.py 신설(11건). |
| 2026-07-03 | 플러그인 신설 | ai-readiness-cartography(코드베이스 AI 준비도 결정론적 측정·시각화). 외부 스킬 v2를 deep-research(5 세션 적대 검증) 2025~2026 1차 근거로 v3 리팩토링 — gating 집계·실행 검증 최상위 가중·기계 판독 의존 그래프·결합도 god-file·보유율 폐기→anchor·신규 H/I 카테고리·auto/manual 라벨. 근거: ORACLE-SWE·LocAgent·ETH Zurich·USENIX slopsquatting·RepoMirage·Factory/Kenogami. |
