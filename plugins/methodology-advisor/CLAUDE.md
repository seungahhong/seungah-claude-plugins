# methodology-advisor

팀의 **현행 개발·회사·사업 프로세스를 먼저 진단**하고, grill-me 스타일 **다각도 문진**(3축) 뒤, 내장 방법론 카탈로그 + 컨틴전시(맥락 적합) 프레임워크에 근거해 상황에 맞는 개발 방법론을 **순위 shortlist + 1순위**로 제안하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. **첫 행동은 반드시 현행 진단**이다(발명 금지).

사용자용 개요·사용법은 [README.md](README.md), 근거는 [references/research/](skills/methodology-advisor/references/research/README.md) 참조.

## Structure

```
methodology-advisor/
├── .claude-plugin/plugin.json
├── CLAUDE.md                       # (이 문서) 포인터 + 4 Phase 요약 + 원칙 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·방법론 목록·경계
├── agents/
│   ├── process-cartographer.md     # Phase 0 현행 진단(관측·발명 금지)
│   ├── context-interviewer.md      # Phase 1 grill-me 다각도 문진(3축·충돌 감지)
│   ├── methodology-matcher.md      # Phase 2 방법론 매칭(shortlist + 1순위 + 로드맵)
│   └── fit-critic.md               # Phase 3 적대적 적합성 검증(은탄환·숨은 가정·안티패턴)
├── skills/methodology-advisor/
│   ├── SKILL.md                    # 오케스트레이터(진입점, 4 Phase 인터랙티브, 승인 게이트)
│   └── references/
│       ├── methodology-catalog.md      # 14개 방법론(원칙·의식·아티팩트·적합 조건·안티패턴)
│       ├── selection-frameworks.md     # Cynefin·Stacey·Boehm-Turner home ground·컨틴전시 축 매핑
│       ├── interview-axes.md           # 개발/회사/사업 3축 질문뱅크(grill-me 전략)
│       └── research/README.md          # 2024-2026 1차 조사(70 confirmed / 5 refuted, SOURCE-TIER)
└── evals/
    ├── evals.json                  # 수용 평가(design-conformance + 불변식 file:함수 인용)
    └── trigger-eval.json           # 트리거 경계(should/should-not, 인접 도메인 역방향 가드)
```

## 4단계 Phase 요약

| Phase | 이름 | 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|----------|-------------|--------|
| 0 | 현행 프로세스 진단 (**가장 먼저**) | process-cartographer | 현행 진단 카드(개발/회사/사업 3축 + 페인 + unknowns) | 첫 질문=현행 개괄, 관측만·발명 금지 → 승인 |
| 1 | 다각도 문진 (grill-me) | context-interviewer | 결정 인자 표(3축 각 인자 값·근거·confidence) + 충돌 목록 | 한 번에 한 질문·답변 분기·충돌 감지 → 승인 |
| 2 | 방법론 매칭·제안 | methodology-matcher | 제안서(맥락 요약 / shortlist 2~3 / 1순위 / additive 로드맵 / 하지 말 것 / 재평가 트리거) | 우열 금지·트레이드오프+안티패턴 필수 → 승인 |
| 3 | 적대적 적합성 검증 | fit-critic | 검증 리포트(은탄환·숨은 가정·안티패턴·비가역·정직성) | 칭찬 금지·1순위 흔들면 재정렬 → 승인 |
| 마무리 | 산출물 저장 (opt-in) | (오케스트레이터) | `.claude/_docs/<슬러그>/` 4개 파일 | **각 파일 저장 여부 개별 확인** |

매 Phase 종료 보고 형식: `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?`

## Conventions (핵심 불변식)

- **첫 행동=현행 진단** — 사용자가 특정 방법론을 지목해도 먼저 개발/회사/사업 3축 현행을 진단한 뒤 제안한다(명시적 "진단 생략" 요구 시에만 축약).
- **승인 게이트** — 매 Phase 종료 시 핵심 산출물 + 1줄 보고 제시 후 승인받고 진행.
- **한 번에 한 질문** — 문진은 하나씩·번호 선택지·답변 분기·충돌 즉시 감지. 어려운 용어는 1줄 정의.
- **현행 먼저·발명 금지** — 관측 안 된 프로세스/역할/도구를 지어내지 않고 unknowns로 남긴다.
- **정직성 가드레일** — ① 방법론 우열 단정 금지(맥락 적합성으로만) ② 은탄환·'N% 개선' 약속 금지(수치는 SOURCE-TIER·출처와 함께 관찰값으로만) ③ 모든 권고에 트레이드오프+안티패턴 동반 ④ **제안만**·조직 변경 자동 실행 안 함(도입은 사람 결정).
- **컨틴전시로 근거화** — 제안은 직관이 아니라 selection-frameworks.md(Cynefin·Stacey·home ground 5인자)로 근거.
- **additive-first** — 잘 되는 현행 보존, 전면 전환보다 되돌리기 쉬운 최소 관행 시험 우선.
- **파일 저장 opt-in** — 산출물은 사용자가 저장을 선택할 때만 `.claude/_docs/<슬러그>/`에 기록(각 파일 개별 확인).
- **독립성** — 단독 설치로 동작, 다른 마켓플레이스 플러그인에 의존하지 않는다(방법론·프레임워크·근거 모두 내재화).
- **경계** — PRD/스토리 작성(product-spec-harness), 하네스 생성(harness-generator)·진단(meta-harness), 상류 핸드오프 게이트(review-harness), 사람↔AI 협업(human-agent-teaming), AI 에이전트 병렬화(agent-orchestration), 코드 구현/리뷰/커밋(frontend/backend/git-harness)은 범위 밖. **인접 이음매**: 방법론 진단·카탈로그 없는 일반 계획·설계 인터뷰는 frontend `grill-me`(방식만 상속, 판별자=현행 3축 진단+카탈로그), DevOps/CD를 *방법론으로 채택 결정*은 이 하네스이나 *파이프라인·IaC 구축*은 cicd-harness·*프로덕션 장애 대응*은 ops-harness. 이 하네스는 '사람 개발팀의 방법론/프로세스 선택'에 특화.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-11 | 플러그인 신설 (v0.1.0) | frontend-harness grill-me를 다각도 문진으로 확장한 도메인 무관 개발 방법론 어드바이저. 4단계(현행 진단 → 3축 문진 → 방법론 매칭 → 적대적 적합성 검증) + 4 에이전트(opus). 14개 방법론 카탈로그·컨틴전시 프레임워크(Cynefin·Stacey·Boehm-Turner home ground) 내재화. deep-research 하네스로 24소스·75주장 적대 검증(70 confirmed/5 refuted) — DORA 2025 채택률 90%(95% 교정)·Boehm-Turner 위험기반 5단계(4단계 교정) 반영. 정직성: 우열 금지·은탄환/'N% 개선' 금지·SOURCE-TIER 인용·트레이드오프+안티패턴 동반·제안만(도입은 사람 결정). skill-creator 규약으로 작성. |
| 2026-07-11 | 다각도 적대 검토 + skill-creator eval 루프 반영 | **(1) 4렌즈 적대 리뷰(honesty·boundary·convention·content)** 발견 수정 — BLOCKING 3건: Shape Up를 'PMF 탐색' 추천에서 삭제(연구가 'POC/MVP 부적합'으로 확정, selection-frameworks·interview-axes 2곳)·DSDM을 '요구 불확실성 낮음' 행에서 제거(DSDM=일정/예산 고정·스코프 가변)·'12팀→LeSS' 자기모순 예시 교정(LeSS 밴드 2~8). MED/LOW: SKILL 프롬프트 참조경로 bare `references/`로 통일(서브에이전트 grounding 소실 위험 제거)·경계에 grill-me/cicd/ops 이음매 명시·팀수 범위에 BLOG tier 태그·SOURCE-TIER PRIMARY 정의에 '1차 증언' 포함·DORA 2025 실제 제목·MTTR→failed deployment recovery time·Scrum 의식 개수/스프린트 길이 정합·Personnel 축 매핑행 추가·자기통계 '내부 조사' 완화. reciprocal should-not을 product-spec·harness-generator·human-agent-teaming·meta-harness에 추가, 자기 trigger-eval에 순수 grill-me should_not·방법론명사 없는 인터뷰 should_trigger 추가(10/10). **(2) skill-creator eval 루프**(3 페르소나 × with-skill/baseline) — with-skill 100% vs baseline 71%(Δ+29pp, +51k tok·+164s). 델타는 순위 shortlist·명명된 컨틴전시 근거·적대적 Phase 3(숨은 가정 포착)·no-invention·정직성에서 발생(강한 baseline 대비 구조·정직성·검증이 차별점). |
