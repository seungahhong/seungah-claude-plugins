# org-transformation-harness

회사/팀을 **목적조직·AI native** 방향으로 바꾸려는 실무자·리더를 인터뷰해, **현행을 먼저 진단**하고 **목표를 질문으로 함께 구체화**한 뒤 **"무엇부터 시작할지"를 단계별 할 일**로 정리하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. **첫 행동은 반드시 현행 진단**이다(목표를 먼저 그리지 않음).

사용자용 개요·사용법은 [README.md](README.md), 근거는 [references/research/](skills/org-transformation/references/research/README.md) 참조.

## Structure

```
org-transformation-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                       # (이 문서) 포인터 + 4 Phase 요약 + 원칙 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·산출물·경계
├── agents/
│   ├── org-cartographer.md         # Phase 0 현행 조직 진단(관측·발명 금지, 강점도 관측)
│   ├── vision-elicitor.md          # Phase 1 목표 구체화 문진(목적조직·일하는 방식·AI native, 임의 정의 금지)
│   ├── gap-planner.md              # Phase 2 간극 진단표 + 우선순위 할 일 + 로드맵(quick-wins·additive-first)
│   └── plan-critic.md              # Phase 3 적대적 검증 + 경영진/팀 공유용 요약
├── skills/org-transformation/
│   ├── SKILL.md                    # 오케스트레이터(진입점, 4 Phase 인터랙티브, 승인 게이트)
│   └── references/
│       ├── interview-pillars.md        # 4기둥 질문뱅크(현재/목표/간극·한 번에 한 질문·충돌 감지)
│       ├── transformation-frames.md    # 목적조직·AI native·일하는 방식 정의 렌즈(트레이드오프·안티패턴·등급)
│       ├── prioritization.md           # 영향·노력·의존성·quick-wins·additive-first·로드맵
│       └── research/README.md          # 2023-2026 1차 조사 dossier(등급·출처·REFUTED 교정)
└── evals/
    ├── evals.json                  # 수용 평가(design-conformance, 13 불변식 file:섹션 인용)
    └── trigger-eval.json           # 트리거 경계(should/should-not, 인접 도메인 역방향 가드)
```

## 4단계 Phase 요약

| Phase | 이름 | 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|----------|-------------|--------|
| 0 | 현행 조직 진단 (**가장 먼저**) | org-cartographer | 현행 진단 카드(구조·일하는 방식·페인·강점·미확인) | 첫 질문=현행 개괄, 관측만·발명 금지 → 승인 |
| 1 | 목표 구체화 문진 | vision-elicitor | 목표 정의 표(기둥 ②③④ 목표상태·동인·트레이드오프·confidence) + 충돌 | 한 번에 한 질문·임의 정의 금지·충돌 감지 → 승인 |
| 2 | 간극 진단·실행계획 | gap-planner | 간극 진단표 + 우선순위 할 일(영향·노력·의존성) + 3~4단계 로드맵 | quick-wins·additive-first·발명 금지 → 승인 |
| 3 | 적대적 검증·공유 요약 | plan-critic | 검증 리포트(일반론·지어낸 사실·은탄환·우선순위·숨은 가정) + 공유용 요약 | 칭찬 금지·결함 보완 → 승인 |
| 마무리 | 산출물 저장 (opt-in) | (오케스트레이터) | `.claude/_docs/<슬러그>/` 4개 파일 | **각 파일 저장 여부 개별 확인** |

매 Phase 종료 보고 형식: `[Phase N] {핵심결정} — 다음: {다음}. 진행할까요?`

## Conventions (핵심 불변식)

- **첫 행동=현행 진단** — 사용자가 목표(AI native 등)를 먼저 지목해도 현행을 먼저 진단한 뒤 목표 구체화(명시적 "진단 생략" 요구 시에만 축약).
- **목표 임의 정의 금지** — 목적조직·AI native를 AI가 단정하지 않고 한 번에 한 질문으로 함께 정의(렌즈는 정답 틀 아님).
- **승인 게이트** — 매 Phase 종료 시 핵심 산출물 + 1줄 보고 제시 후 승인받고 진행.
- **한 번에 한 질문(짧게)** — 문진은 하나씩·번호 선택지·답변 분기·충돌 즉시 감지. 어려운 용어는 1줄 정의.
- **현행 먼저·발명 금지** — 관측 안 된 조직/역할/도구를 지어내지 않고 '미확인'으로 남긴다. 지금 할 수 있는 업무·강점도 함께 관측(보존 대상).
- **정직성 가드레일** — ① 은탄환·'N% 개선' 약속 금지(수치는 출처·등급과 함께 관찰값으로만; AI 도입은 DORA상 체감≠시스템 성과) ② 모든 목표·할 일에 트레이드오프+안티패턴 동반 ③ **제안만**·조직 변경 자동 실행 안 함(도입은 사람 결정) ④ **점수화 안 함**·커밋 안 함.
- **quick-wins·additive-first** — '지금 바로 시작 가능한 것'을 맨 위로, 잘 되는 현행 보존, 되돌리기 쉬운 개입 우선. 전면 전환은 명시 승인 시만.
- **영향·노력·의존성 우선순위** — 신호 + 이 순서인 이유 1줄, 의존성 선행. 점수 공식을 절대 진리로 포장 금지(RICE/WSJF는 report-only).
- **근거 등급으로 근거화** — 주장은 research/README.md 등급(STRONG 조건부 / MEDIUM 컨센서스 / report-only folklore)을 지킨다. REFUTED('95% 실패' 등)는 교정본으로만.
- **파일 저장 opt-in** — 산출물은 채팅 제시 기본, 저장 선택 시만 `.claude/_docs/<슬러그>/`(각 파일 개별 확인).
- **독립성** — 단독 설치로 동작, 다른 마켓플레이스 플러그인에 의존하지 않는다(프레임·근거 모두 내재화).
- **경계** — 개발 방법론(Scrum/Kanban) 선택·추천, PRD/스토리 작성, 하네스 자체 생성·진단, 사람↔AI 협업 토폴로지 설계, 작업을 여러 AI 에이전트로 병렬화, CI/CD·IaC 구축, 코드 구현/리뷰/커밋은 범위 밖. **인접 이음매**: *명명된 개발 방법론 선택*(현행 진단+카탈로그 매칭)과 달리, 이 하네스는 *조직 목표(목적조직·AI native) 전환 + 실행 할 일 정리*(스프린트/일하는 방식은 다루되 방법론 매칭 아님)에 특화. '사람 조직의 목적조직·AI native 전환 실행계획'이 고유 판별자.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-21 | 플러그인 신설 (v0.1.0) | 조직 전환 진단·실행계획 인터랙티브 하네스. 4단계(현행 진단 → 목표 구체화 문진 → 간극·실행계획 → 적대적 검증·공유 요약) + 4 에이전트(opus). 메타 프롬프팅 기법으로 시드 인터뷰 프롬프트를 깎아낸 뒤 그 프롬프트를 하네스로 승격. `/deep-research`(6각도)로 2023~2026 1차 문헌 적대 검증 — DORA 2024/2025(PRIMARY)·조직 진단 학술지·Cagan Transformed/Team Topologies·Kotter·WSJF/RICE. 정직성: 은탄환/'N% 개선' 금지·목표 임의 정의 금지·AI 도입 체감≠시스템 성과(DORA)·'GenAI 파일럿 95% 실패' 반박 수치 미인용·quick-wins/additive-first는 report-only 정직 표기·제안만·점수화 안 함. deep-research synthesize 에이전트 중단으로 dossier는 검증 통과 claim(6 소스 블록)으로 직접 구성. |
