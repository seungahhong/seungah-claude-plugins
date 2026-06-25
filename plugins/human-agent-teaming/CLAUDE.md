# human-agent-teaming

사람과 AI 에이전트가 **한 팀으로** 효과적으로 협업하도록 **분업·공통기반·감독/신뢰·검증/지속**을 설계하는 도메인 무관 멀티 에이전트 하네스.
핵심 축은 *AI끼리의 병렬화·토폴로지*가 아니라 **사람↔에이전트의 분업과 감독**이고, 산출물은 프롬프트가 아니라 **협업 설계(teaming playbook)** 다.
핵심 메시지는 **"에이전트는 도구가 아니라 팀원이고, 자율성과 인간 통제의 균형을 작업 종류별로 잡는다"** 이다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
human-agent-teaming/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                          # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                          # 사용자용 개요·언제 쓰나·4단계 사용법·도구 경계·근거 자료
├── agents/                            # 모두 model: "opus"
│   ├── delegation-designer.md         # Phase 0 — 분업·위임·자율 수준·운영 모드·고위험 결정점·역할 경계
│   ├── common-ground-builder.md       # Phase 1 — 온보딩 브리핑·AI 오류 경계·workspace awareness·재정렬 루프
│   ├── oversight-designer.md          # Phase 2 — 모니터링 기반 감독·단계적 가역 권한·개입·신뢰 보정·실패모드/자동화 편향 가드
│   └── verification-designer.md       # Phase 3 — 비례 검증(루브릭·Doer-Verifier)·스캐폴딩·핸드오프 연속성·후속 재정렬·책임
├── skills/
│   └── human-agent-teaming/
│       ├── SKILL.md                   # 오케스트레이터(진입점, Phase 0 게이트 → 공통기반 → 감독 → 검증)
│       └── references/
│           ├── human-agent-teaming-principles.md   # 분업 규칙·감독 설계·검증 운영·anti-pattern·결정 신호표
│           └── human-agent-teaming-research.md      # 설계 근거 deep-research dossier(출처·인용·vote·CAVEAT·반박된 주장·방법론)
└── evals/
    ├── evals.json                     # 수용 평가(design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json              # 트리거 경계 평가(should_trigger 10 / should_not 12, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 분업·위임 (Charter & Delegate) | delegation-designer | Team Charter(분업·위임·자율 수준·운영 모드·고위험 결정점·역할 경계) | 승인 게이트 |
| 1 | 공통기반 (Establish Common Ground) | common-ground-builder | Common Ground Brief(온보딩 브리핑·AI 오류 경계·workspace awareness·재정렬 루프·working agreement) | 1줄 보고 |
| 2 | 감독·신뢰 보정 (Calibrate Oversight & Trust) | oversight-designer | Oversight & Trust Plan(모니터링 감독·단계적 권한·신뢰 보정·실패모드/자동화 편향 가드) | 1줄 보고 |
| 3 | 검증·지속 (Verify & Sustain) | verification-designer | Verification & Sustain Plan(검증 산출물·Doer-Verifier·핸드오프 연속성·재정렬·책임) | 1줄 보고 |

최종 보고: `[Teaming Playbook] 분업 {사람=…/에이전트=…} · 감독 {HITL|HOTL·모니터링} · 검증 {…} — 자율은 작업 종류별 반복 성공 후 확대`

## Conventions

- **에이전트는 도구가 아니라 팀원**: 팀(분업·역할)을 설계하지 한 에이전트에 프롬프트만 던지지 않는다. 사람은 전략·하드 트레이드오프·최종 검증·책임을, 에이전트는 전문 실행을 맡는다.
- **중심 긴장: 자율성 ⇄ 통제**: 에이전트는 자율이 필요하나(가치의 원천), 사람은 *목표가 어떻게 추구되는지*를 특히 고위험·비가역 결정 이전에 통제한다. 작업 종류별로 균형을 잡는다.
- **신뢰는 적절한 의존으로 보정**: 신뢰 *최대화*가 아니다(과신은 위험, 과소신은 무시). 작업 종류별 반복 성공 후 자율을 확대하고, 검증 강도는 stakes×uncertainty에 비례한다.
- **감독 = 모니터링 + 개입(전수 승인 아님)**: 모든 행동 승인 강제는 승인 피로·러버스탬프로 마찰만 늘 수 있다. 투명성·개입·단계적 가역 권한으로 *필요할 때 개입할 위치*에 두고, 자동화 편향도 가드한다.
- **공통기반은 만들고 지속 재협상**: "적혀 있지 않으면 에이전트엔 존재하지 않는다." 온보딩 브리핑 + AI 오류 경계 노출 + 재정렬 루프(SMM은 영속, 일회성 설정 아님).
- **명확한 역할 경계**: 흐릿하면 역할 혼동·무임승차·과신을 부른다. restrained 에이전트로 인간 주도성을 보존한다.
- **검증은 요구되는 마지막 층, 운영화**: 코드엔 테스트, 그 외엔 루브릭, Doer-Verifier(fresh-context·Write/Edit 없는 평가자). 검증 스캐폴딩은 *필요조건이지 충분조건이 아니다*.
- **책임은 사람**: 에이전트는 팀원이지 희생양(moral crumple zone)이 아니다.
- **정직성·falsifiability**: 벤더 1차 근거는 *설계 의도*로(크기 주장 미인용), 학술은 *권장 메커니즘*으로 인용. 수치는 vote/CAVEAT와 함께만, "개선 N% 보장" 금지, 반박된 패턴(에이전트 자기제한을 1차 감독으로) 미사용. 반례(METR RCT 경험 개발자 감속)도 정직히 기록.
- **승인 게이트·관찰성**: Phase 0 직후 승인 게이트는 항상. 각 Phase는 1줄로 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: 여러 AI 에이전트 병렬화·토폴로지 결정·컨텍스트 페이로드 조립·압축·AI 출력 평가(judge 구성)·단일 자율 반복 루프·상류 핸드오프 게이트 검수·새 하네스 생성·하네스 진단·PRD 작성·커밋/PR은 범위 밖이다.
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | 사람↔에이전트 협업 설계(분업·위임→공통기반→감독·신뢰→검증·지속) 하네스. Anthropic 'Building Effective Human-Agent Teams' 블로그 정독 + deep-research 3-vote 적대 검증(26 소스·130 주장·24 confirmed/1 refuted) 근거. 1차: Anthropic HAT 블로그·Building Effective Agents·safe-agents 프레임워크·Measuring Agent Autonomy·long-running-agents + arXiv:2504.10918·2602.05987 |
