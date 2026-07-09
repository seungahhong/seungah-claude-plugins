# code-legibility-harness

AI 코딩 에이전트가 읽고·탐색하고·안전하게 수정하기 좋도록 **코드 본문 층위**(주석·독스트링 / 변수명·함수명·클래스·컴포넌트명 / 함수·모듈 granularity)를 다각도로 진단해 제안하고, **사용자 승인 후에만 단계별로 적용**하는 도메인 무관 인터랙티브 단일 스킬 + 4 에이전트.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
code-legibility-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                       # (이 문서) 포인터 + 불변식 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·경계·근거
├── agents/                         # 4 에이전트 (모두 model: "opus")
│   ├── comment-auditor.md          # Phase 1 — 주석 4분류(오도/stale/noise/유효) → C0·C1 후보
│   ├── naming-analyst.md           # Phase 1 — 명명 3축(오도>무의미>모호) → C2 후보 + 도구·위험 판정
│   ├── structure-cartographer.md   # Phase 1 — 구조 후보 (opt-in 기본 OFF, "효과=추론" 라벨 필수)
│   └── behavior-guard.md           # Phase 3/4 — 개입 클래스별 센서 실행·관측 + census 델타 (checker)
└── skills/
    └── code-legibility-harness/
        ├── SKILL.md                # 오케스트레이터(Phase 0~4 + 3 승인 게이트 + 스코프 가드)
        ├── scripts/legibility_scan.py       # 결정론 census 스캐너 (stdlib only, 등급 없음)
        ├── scripts/test_legibility_scan.py  # 회귀 테스트 49건 (불변식 핀 + 버그 회귀 핀 + 독립성 핀)
        └── references/
            ├── legibility-principles.md     # 7개 원리(삭제>추가·이름은 채널·테스트≠등가성 오라클…)
            ├── intervention-catalog.md      # 개입 카드 C0~C3 정본(근거·위험·센서·롤백·거부 조건)
            └── research/                    # 2025~2026 1차 근거 (적대 검증 24 confirmed / 1 refuted)
                ├── README.md                # 근거 서열·판정표·REFUTED 목록·미해결 질문·넣지 말 것
                ├── naming.md · comments.md · structure.md
                └── safe-application.md · measurement-delta.md
└── evals/
    ├── evals.json                  # 수용 평가(불변식 file:section 인용 채점)
    └── trigger-eval.json           # 트리거 경계 평가 (자매 플러그인 역방향 가드 포함)
```

## 개입 클래스 (정본: `references/intervention-catalog.md`)

| 클래스 | 개입 | 우선순위 | 동작 위험 | 1급 센서 | 기본값 |
|--------|------|---------|----------|---------|--------|
| **C0** | 오도·stale 주석 삭제/수정 | **P1** | 없음 | 사람 확인 + 코드 대조 | ON |
| **C1** | 계약·불변식 주석 추가/수정 | P3 | 없음 (사실성 ~20~45%) | 코드 대조 (+document testing) | ON |
| **C2** | 무의미·오도 식별자 안전 리네임 | **P2** | 참조·컴파일 깨짐 | **컴파일/타입체크 + 참조 완전성** | ON |
| **C3** | 구조 리팩터 (추출·이동·분할) | P4 | **높음** (19~35% 비등가) | 테스트+컴파일 + 사람 diff | **OFF · opt-in** |

**C0가 1순위인 이유는 효과가 가장 커서가 아니라 효과가 확실하고 위험이 0이기 때문이다.**
**C3가 마지막인 이유는 효과가 없어서가 아니라 효과가 추론이고 위험이 측정된 최대치이기 때문이다.**

## Conventions (불변식)

- **3 승인 게이트**: 계획(A) → 개별(B) → 최종(C). **승인 없이 어떤 파일도 쓰지 않는다.**
- **스코프 가드(게이트와 동급)**: Phase 0에서 선택된 개입 클래스 **안에서만** 제안·적용. 밖은 "추가 안 함" 표기 + 확장 문의.
- **등급을 만들지 않는다**: census(인벤토리)만. 0~100 등급은 `ai-readiness-cartography`(저장소 층) 소유이며,
  코드 본문 층 등급을 정당화할 1차 근거가 없다(O-1·O-3). `test_legibility_scan.py`가 이 불변식을 테스트로 고정한다.
- **테스트는 등가성 오라클이 아니다**: 비등가 리팩터의 ≈21%가 기존 테스트를 통과한다(E-A2). "테스트 초록 = 동작 보존"을 보고하지 않는다.
- **판정 어휘 3개**: `VERIFIED` / `FAILED` / `UNVERIFIED`. **C3는 최선에도 `UNVERIFIED`를 넘지 못한다.**
- **generator ≠ checker**: 제안한 에이전트가 자기 제안을 검증하지 않는다. `behavior-guard`가 센서를 **실행해 관측**한다.
- **리네임은 도구가, 판단은 사람이**: AST/LSP rename API에 위임. LLM 문자열 치환 금지. 도구 없으면 **제안만**.
- **결정론 우선, 사람 보강**: `legibility_scan.py`가 먼저 채점하고 LLM이 `auto-med`·`heuristic` 후보를 확인한다. 손진단부터 하지 않는다.
- **heuristic·report-only는 개입 후보로 승격 금지**: N4 심볼 충돌, 함수 크기, 산문 토큰 dangling.
- **측정 불가 ≠ 결함 없음**: `skipped`(too-large·symlink·parse-failed)를 반드시 함께 보고한다.
- **과장 금지**: 구조 개입에 성공률 수치를 약속하지 않는다. 공개 벤치마크 점수로 델타를 주장하지 않는다.
- **커밋하지 않는다**: 최종 승인 후 `git-harness` 핸드오프 제안만.
- **독립 실행(테스트로 고정)**: 이 플러그인은 단독 설치·실행된다.
  · 스캐너는 **stdlib만** import한다(`test_scanner_imports_are_stdlib_only`).
  · 문서 링크는 **플러그인 경계를 넘지 않는다**(`test_no_markdown_link_escapes_the_plugin`) — 자매 플러그인은 *이름으로만* 언급한다.
  · 스크립트는 `${CLAUDE_PLUGIN_ROOT}/skills/code-legibility-harness/scripts/…`로 호출해 위치·cwd에 의존하지 않는다.
  · `git`(`--git-drift`)·안전 리네임 도구·`git-harness`는 **선택적**이며, 없으면 해당 기능만 강등하고 계속 진행한다.
- 4 에이전트 협업이므로 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.
- **경계**: 저장소 준비도 측정·등급(ai-readiness-cartography), 세션 토큰 효율(token-efficiency), 테스트 계층 계획(test-layering-harness),
  자가치유 QA(qa-agent-harness), 하네스 자체 진단(meta-harness), 실행 명세(spec-driven-development),
  컨텍스트 조립(context-engineering), 코드 리뷰·PR·커밋(git-harness/frontend-harness)은 범위 밖.

## 정직성 가드 (위반 시 근거 충돌 — 전문은 `references/research/README.md`)

1. 🚫 "구조를 리팩터하면 에이전트 성공률이 N% 오른다" — 직접 측정 1차 자료 없음. '추론'으로만 표기(O-1).
2. 🚫 arXiv:2505.10443의 "최대 70%"를 리네이밍 효과로 인용 — 루프 언롤링 값이다.
3. 🚫 arXiv:2512.16790의 "−90%~+67%"를 주석 텍스트 추가/삭제 효과로 인용 — CAV 임베딩 개입치다.
4. 🚫 ARISE의 "Function R@1 0.43→0.60 / Line R@1 0.26→0.41" — 적대 검증에서 **REFUTED (1-2)**. `+4.7pp`만 인용.
5. 🚫 함수 라인 수 임계값을 판정·게이트로 사용 — 근거 없음(cartography session-4 C8과 동일 판정).
6. 🚫 **LLM의 코드 이해 성공을 명명 품질의 오라클로 사용** — 부정확한 이름도 메워서 맞춘다(arXiv:2503.12207 false positive).
7. 🚫 "테스트 통과 = 동작 보존" — ≈21% 누락(E-A2), 구조 오라클은 13.3% 누락(E-S2).
8. 🚫 주석 밀도 목표치 — 최적점 미상(O-4).
9. 🚫 0~100 단일 등급 — 근거 부재 + 자매 플러그인 소관.
10. 🚫 사람 가독성 포매팅(들여쓰기·공백) 개선을 AI 가독성 근거로 제시 — LLM에 무익.
11. 🚫 공개 벤치마크(SWE-bench류) 점수로 개선 델타 주장 — 성공의 63%가 정답 회수.
12. 🚫 자기보고로 동작 보존 판정 — 실행 관측만.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-09 | 플러그인 신설 (v0.1.0) | 코드 본문 층위 AI 가독성 진단·제안·승인 후 단계별 적용. deep-research(5각도·23소스·102주장 추출·25주장 3표 적대검증 → 24 confirmed / 1 refuted)로 2025+ 1차 근거 확보. 자매 플러그인 `ai-readiness-cartography`가 session-1 함의 4번에서 "식별자 명료성·낮은 난독도"를 요구했으나 v3 루브릭 9카테고리에 구현하지 않은 **빈칸을 채운다**. 결정론 스캐너 신설(7 탐지기 + 근거 등급 라벨, 회귀 테스트 49건, 자기 명명 스캔 0건 통과, 형제 플러그인 없는 격리 디렉토리에서 실행 검증). 적대 검토 4렌즈(날조 인용·금지 항목·불변식·경계) 중 1건 실제 결함(behavior-guard 센서 매트릭스 C1/C2 라벨 스왑) 교정. 개발 중 발견·회귀 고정한 스캐너 버그 3건: (1) `# noqa` 지시자 한 줄이 주석처리 코드 블록 전체를 무효화, (2) 무의미 이름 사전이 대소문자 구분이라 `class Foo` 누락, (3) 주석 속 산문 토큰(`tool_input`·`PreToolUse`)이 외부 스키마 키인데 개입 후보로 승격 → strong/weak 마커 분리로 거짓양성 100건→11건. |
