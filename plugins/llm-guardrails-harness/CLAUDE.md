# llm-guardrails-harness

LLM/에이전트 애플리케이션의 안전을 모델의 자기 정렬이나 시스템 프롬프트에 대한 신뢰가 아니라, 모델 바깥을 감싸는
**외부·인라인 제어 평면(external control plane)** 으로 *요청 시점에* 강제하는 도메인 무관 멀티 에이전트 런타임
가드레일 하네스.
핵심 메시지는 **"안전은 모델을 믿는 게 아니라 모델 주위에 별도의 정책 계층을 두고 요청 시점에 입력·출력·검색·행동을
검사·거부·재작성하는 것이다 — prompt injection은 LLM의 근본 설계를 악용하므로 정렬·지시만으로는 닫히지 않고,
가드레일 자체도 공격 가능한 LLM이라 단일 레일은 충분치 않다"** 이다.
근거: **OWASP Top 10 for LLM Applications 2025 · NVIDIA NeMo Guardrails(input/dialog/output/retrieval/execution 5 rail
types) · Llama Guard(arXiv:2312.06674) · SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597)**.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
llm-guardrails-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                          # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                          # 사용자용 개요·언제 쓰나·4단계 사용법·도구 경계·근거 자료
├── agents/                            # 모두 model: "opus"
│   ├── threat-modeler.md              # Phase 0 — 앱 → OWASP LLM Top 10 매핑·fail-closed 정책·레일 배치 결정
│   ├── input-rail-engineer.md         # Phase 1 — 모델 호출 전 jailbreak/injection 탐지·Llama-Guard 분류·요청 검증
│   ├── output-rail-engineer.md        # Phase 2 — PII 리댁션·독성/정책 필터·grounding·untrusted 검색 청크 필터링
│   └── enforcement-redteamer.md       # Phase 3 — 최소 권한 tool 스코핑·사람 승인 게이트·red-team(ASR/FPR)
├── skills/
│   └── llm-guardrails-harness/
│       ├── SKILL.md                   # 오케스트레이터(진입점, Phase 0 정책 게이트 → 입력 → 출력/검색 → 행동/검증)
│       └── references/
│           ├── llm-guardrails-harness-principles.md   # 원칙·anti-pattern·결정 신호표
│           └── llm-guardrails-harness-research.md      # 설계 근거 deep-research dossier(출처·신뢰도·인용·CAVEAT·방법론)
└── evals/
    ├── evals.json                     # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json              # 트리거 경계 평가(should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 위협 모델링·정책 정의 (Threat-Model & Policy Definition) | threat-modeler | Guardrail Policy(OWASP 매핑·콘텐츠/행동 카테고리·레일 배치·fail-closed) | 승인 게이트 |
| 1 | 입력 레일 (Input Rails) | input-rail-engineer | Input Rail Design(jailbreak/injection 탐지·Llama-Guard 분류·거부/재작성) | 1줄 보고 |
| 2 | 출력·검색 레일 (Output & Retrieval Rails) | output-rail-engineer | Output/Retrieval Rail Design(PII 리댁션·독성/정책·grounding·untrusted 청크) | 1줄 보고 |
| 3 | 행동 강제·적대 검증 (Agent-Action Enforcement & Adversarial Verification) | enforcement-redteamer | Enforcement + Red-Team Report(최소 권한 스코핑·사람 게이트·ASR/FPR) | 배포 사람 게이트 |

최종 보고: `[LLM-Guardrails] 정책 {OWASP매핑·카테고리수} · 입력레일 {탐지/분류/검증} · 출력·검색레일 {PII/독성/grounding/untrusted} · 강제·검증 {최소권한·사람게이트 · ASR/FPR}`

## Conventions

- **외부 강제 우선(시스템 프롬프트 신뢰 금지)**: 안전은 모델 바깥을 감싸는 별도 제어 평면이다. "절대 유출하지 마" 같은 지시는 강제 경계가 아니다(prompt injection은 정렬·지시로 닫히지 않음).
- **전체 레일 taxonomy 커버**: input·dialog·output·retrieval·execution 레일이 요청 라이프사이클의 서로 다른 지점을 지킨다. 레일은 pass/block뿐 아니라 *재작성/마스킹*도 한다.
- **fail-closed 기본값**: 레일 오류·타임아웃·분류기 불확실 시 통과가 아니라 *차단·강등*한다. 부하·공격 트래픽이 가장 높을 때 fail-open 금지.
- **가드레일 자체가 공격 가능한 LLM**: 단일 분류기/레일을 은탄환으로 두지 않고 input/output/retrieval/execution + 사람 승인으로 다층화한다.
- **excessive agency 최소 권한 + 사람 게이트(LLM06)**: tool마다 스코프를 좁히고 인자/결과를 검증하며 비가역·파괴적 행동은 사람 승인. raw LLM 출력이 고폭발 반경 행동을 직접 트리거하지 않게 한다(LLM05→LLM06).
- **검색/도구 반환 콘텐츠 불신(LLM08)**: retrieval 레일이 청크를 필터/검증해 indirect prompt injection과 벡터/임베딩 약점 악용을 막는다.
- **safety-utility 트레이드오프 명시**: ASR(놓친 공격)과 FPR(과차단)을 *둘 다* 측정한다. 과차단은 사용자가 레일을 우회·비활성화하게 만든다.
- **런타임·인라인·관측**: 레일은 라이브 요청 경로에서 텔레메트리와 함께 실행된다 — 이는 오프라인 판정과 다르다. 고정 벤치마크 정확도가 아니라 미지 공격 일반화를 평가한다.
- **정직성·falsifiability**: 세션 사례는 전이 가능한 코어(레일 taxonomy·OWASP 매핑·외부강제 원칙)만 일반화하고 특정 사내 구현은 귀속하지 않으며, ASR/FPR은 세팅별 관찰값·"개선 N% 보장" 금지·가드레일은 위험 감소지 제거가 아님을 명시한다.
- **승인 게이트·관찰성**: Phase 0(정책) 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: 오프라인 AI 출력 평가·프로덕션 장애 RCA·상류 핸드오프 검수·사람↔에이전트 협업 설계·에이전트 병렬화 토폴로지·일반 백엔드 구현·코딩 에이전트 코드 변경 거버넌스·웹 소스 취약점 스캔·아이덴티티/인가 아키텍처 설계는 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.
- 다른 마켓플레이스 플러그인에 의존하지 않는 독립 플러그인이다(경계의 '범위 밖'은 일반 도메인 개념으로만 서술).

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-02 | 플러그인 신설 | LLM I/O·tool 호출을 외부·인라인 제어 평면으로 런타임 강제하는 방어심층 가드레일 하네스(Phase 0 위협모델·정책 → Phase 1 입력 레일 → Phase 2 출력·검색 레일 → Phase 3 행동 강제·적대 검증). Tech-Verse 2026 S04 "Beyond Intelligence to Safety: External AI Guardrails" 세션의 전이 가능한 코어(레일 taxonomy+OWASP 매핑+외부강제 원칙)를 일반화하고, 1차 근거 OWASP Top 10 for LLM Applications 2025 · NVIDIA NeMo Guardrails(5 rail types) · Llama Guard(arXiv:2312.06674) · SoK: Evaluating Jailbreak Guardrails(arXiv:2506.10597) · OWASP LLM Prompt Injection Prevention Cheat Sheet · Adaptive Evaluation of Out-of-Band Defenses(arXiv:2606.26479)를 직접 인용. 사내 게이트웨이 구현 비귀속·보편 ASR/FPR·개선 N% 미주장 정직성 가드 포함 |
