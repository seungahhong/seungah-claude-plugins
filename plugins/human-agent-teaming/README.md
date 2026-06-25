# human-agent-teaming

사람과 AI 에이전트가 **한 팀으로** 효과적으로 협업하도록 **분업·공통기반·감독/신뢰·검증/지속**을 설계하는
도메인 무관 멀티 에이전트 하네스입니다.

핵심 축은 *AI끼리의 병렬화·토폴로지*가 아니라 **사람 ↔ 에이전트의 분업과 감독**입니다.
산출물은 프롬프트가 아니라 **협업 설계(teaming playbook)** 입니다 — 분업·공통기반·감독·검증의 *working agreement* 집합.

핵심 메시지는 둘입니다 — **"에이전트는 도구가 아니라 팀원이다"**, 그리고 **"자율성과 인간 통제의 균형을 작업 종류별로 잡는다."**
일은 단일 플레이어에서 멀티플레이어로 옮겨갔습니다 — *사람이 전략을 세우고 에이전트가 실행*합니다.

> 이 하네스는 협업을 **설계**합니다(제안·playbook 산출). 실제 협업을 대신 실행하지 않습니다.

## 무엇을 설계하나 (네 질문)

1. 사람과 에이전트가 *무엇을 나눠 맡고*, 어디까지 위임하며, 자율은 얼마나 주는가? (Phase 0)
2. 에이전트가 팀원으로 일하게 할 *공통기반·working agreement*는 무엇인가? (Phase 1)
3. *모든 행동을 승인하지 않고* 어떻게 감독·신뢰 보정·개입하는가? (Phase 2)
4. 산출물을 *어떻게 검증*하고, 협업을 *어떻게 이어가며*, 책임은 누가 지는가? (Phase 3)

## 설치

이 저장소를 Claude Code 플러그인 마켓플레이스로 추가한 뒤 `human-agent-teaming` 플러그인을 활성화하면,
`human-agent-teaming` 스킬이 자동 트리거되거나 직접 호출할 수 있습니다. **다른 마켓플레이스 플러그인에 의존하지 않는 독립 플러그인**입니다.

## 스킬

| 스킬 | 역할 |
|------|------|
| `human-agent-teaming` | 오케스트레이터(진입점). 분업·위임(Team Charter) → 공통기반(Common Ground Brief) → 감독·신뢰 보정(Oversight & Trust Plan) → 검증·지속(Verification & Sustain Plan)의 흐름을 진행하며, 각 단계에서 전용 에이전트(delegation-designer / common-ground-builder / oversight-designer / verification-designer)를 호출한다. |

## 에이전트 팀 (모두 `model: opus`)

| Phase | 에이전트 | 역할 |
|-------|----------|------|
| 0 Charter & Delegate | `delegation-designer` | 분업(사람 vs 에이전트)·위임 메커니즘·자율 수준·운영 모드(HITL/HOTL)·고위험 결정점·역할 경계 |
| 1 Establish Common Ground | `common-ground-builder` | 팀원 온보딩 브리핑·AI 오류 경계 노출·workspace awareness·재정렬 루프·working agreement |
| 2 Calibrate Oversight & Trust | `oversight-designer` | 모니터링 기반 감독·단계적 가역 권한·개입/스티어링·신뢰 보정·실패모드/자동화 편향 가드 |
| 3 Verify & Sustain | `verification-designer` | 비례 검증(루브릭·Doer-Verifier)·검증 스캐폴딩·핸드오프 연속성·후속 재정렬(AAR)·책임 |

## 언제 쓰나 / 언제 다른 도구를 쓰나

**이 하네스를 쓰세요**
- 한 작업에서 **사람과 에이전트가 무엇을 나눠 맡을지**(분업·위임·자율 수준) 설계하고 싶을 때
- **모든 행동을 일일이 승인하지 않고** 모니터링 + 개입으로 에이전트를 감독하는 체계를 설계하고 싶을 때
- 에이전트에게 **얼마나 신뢰/자율을 줄지** 작업 종류별로 보정하고, 고위험·비가역 결정 전에 사람이 개입할 체크포인트를 두고 싶을 때
- 에이전트가 **멋대로 너무 많이 하거나 테스트도 없이 다 됐다고 할 때**, 범위/검증 가드를 구조적으로 두고 싶을 때
- 에이전트 산출물을 **사람이 어떻게 검증할지**(루브릭·Doer-Verifier·핸드오프 연속성) 설계하고 싶을 때
- 사람-에이전트 협업이 자꾸 어긋날 때 **공통기반·역할 경계·재정렬 루프**를 잡고 싶을 때

**이 하네스를 쓰지 마세요 (범위 밖)**
- **여러 *AI 에이전트*로 병렬화할지·토폴로지**(single/multi·centralized/independent) 결정 — *AI↔AI* 오케스트레이션 도메인. (이 하네스는 *사람↔에이전트* 분업·감독입니다. 에이전트가 여러 개여도 여기서 정하는 건 *사람의 역할·감독*입니다.)
- 모델에 넣을 **컨텍스트 페이로드 조립·압축**(retrieval·큐레이션) — 컨텍스트 설계 도메인. (Phase 1 공통기반은 *협업 수준의 working agreement·온보딩*이지 토큰 페이로드 최적화가 아닙니다.)
- **AI 출력의 엄밀한 평가**(LLM-as-a-Judge·benchmark validity 구성) — 산출물 채점 도메인. (Phase 3 검증은 *협업 안에서 사람이 하는 비례 검증·Doer-Verifier 설계*입니다.)
- **한 목표를 통과까지 한 흐름으로 자율 반복** — 단일 자율 반복 도메인. (이 하네스는 *사람이 줄곧 관여하는 협업 구조*를 설계합니다.)
- **상류 산출물 핸드오프 게이트 검수**(기획·디자인·API 계약) — 핸드오프 리뷰 도메인.
- **새 하네스/에이전트 팀 생성 · 하네스 자체 진단 · PRD 작성 · 커밋/PR 리뷰 · settings.json 설정 변경** — 범위 밖.

## 진행 방식 (4단계)

| 단계 | 무엇을 | 결과 |
|------|--------|------|
| 0 분업·위임 | delegation-designer가 사람/에이전트 분업·위임·자율·운영 모드·고위험 결정점·역할 경계 | Team Charter — **승인 게이트** |
| 1 공통기반 | common-ground-builder가 온보딩 브리핑·AI 오류 경계·workspace awareness·재정렬 루프 | Common Ground Brief |
| 2 감독·신뢰 보정 | oversight-designer가 모니터링 감독·단계적 가역 권한·개입·신뢰 보정·가드 | Oversight & Trust Plan |
| 3 검증·지속 | verification-designer가 비례 검증·Doer-Verifier·핸드오프 연속성·재정렬·책임 | Verification & Sustain Plan |
| — 마무리 | 네 산출물을 하나의 Teaming Playbook으로 종합 | `[Teaming Playbook] 분업 {사람=…/에이전트=…} · 감독 {HITL|HOTL·모니터링} · 검증 {…} — 자율은 작업 종류별 반복 성공 후 확대` |

- 시작 직후 Team Charter **승인 게이트**(잘못된 분업으로 잘못된 위임·감독을 설계하지 않기 위함).
- 자율은 *작업 종류별로 반복 성공 후* 확대합니다 — 미입증이면 초기엔 전수 검토가 기본입니다.

## 도구 경계 (한 줄 변별)

- "*사람과 에이전트가 어떻게 협업할지* 설계" → **이 하네스**.
- "*여러 AI 에이전트로 병렬화할지·토폴로지*" → 멀티 에이전트 오케스트레이션 도메인.
- "모델에 *무엇을 넣을지*(컨텍스트 조립·압축)" → 컨텍스트 설계 도메인.
- "산출물을 *엄밀히 채점*(judge·validity)" → 평가 도메인.
- "한 목표를 *통과까지 한 흐름으로 반복*" → 단일 자율 반복 도메인.

## 근거 자료 (deep-research dossier)

설계 근거는 Anthropic의 **["Building Effective Human-Agent Teams"](https://claude.com/blog/building-effective-human-agent-teams)** 블로그 정독을 출발점으로,
2025+ 1차 자료를 3-vote 적대 검증해 채택했습니다(26개 소스·130개 주장 → 24 confirmed/1 refuted → 13 종합).
출처·인용·신뢰도·CAVEAT·반박된 주장은 [references/human-agent-teaming-research.md](skills/human-agent-teaming/references/human-agent-teaming-research.md) 참조.

- **Anthropic, "Building Effective Human-Agent Teams"** (claude.com/blog) — 멀티플레이어 분업·4 fundamentals(공개 작업·역할+도구·북극성·시간 들인 신뢰)·역할 명문화(roster/skill 파일)·검증 산출물(루브릭/테스트). *벤더 1차 — 설계 의도로 인용*.
- **Anthropic, "Building Effective Agents"** — workflow vs agent·체크포인트(비가역 전)·인간 리뷰의 필요성.
- **Anthropic, "Our framework for safe and trustworthy agents"** — 중심 긴장(자율성⇄통제)·투명성·개입·단계적 가역 권한.
- **Anthropic, "Measuring Agent Autonomy"** — 감독=모니터링+개입(전수 승인 아님)·auto-approve 20%→40%/interrupt 5%→9% *관찰값*(코호트·시점 의존).
- **Anthropic, "Effective harnesses for long-running agents"** — 특징적 실패모드(over-reach·조기 완료)·한 번에 하나의 작업·핸드오프 연속성 산출물.
- **arXiv:2504.10918** — "Adaptive Human-Agent Teaming"(Wang et al., 2025; 133개 경험 연구 리뷰). 위임 메커니즘(human/agent/co-delegation)·conditional delegation·역할 경계 실패모드·신뢰≠의존·SMM 영속 협상. vote high.
- **arXiv:2602.05987** — "From Human-Human to Human-Agent Collaboration"(CHI EA '26 워크숍). 도구→팀원(mutual awareness·adaptivity·shared accountability)·CSCW 설계 질문. vote **medium**(비피어리뷰 제안서 — 설계 렌즈로만 채택).

> **정직성 가드**: Anthropic 소스는 *벤더 자기서술*(설계 의도·예시이지 독립 효과 연구 아님) — 크기 주장("dramatically improved")은 미인용. 모든 수치는 *특정 코호트·시점의 관찰값*("개선 N% 보장" 금지). 원전 hedge를 단정으로 굳히지 않음. **반박된 패턴**(에이전트 자기제한을 1차 감독으로)은 쓰지 않습니다. 반례로 **METR RCT**(경험 개발자 ~19% 감속)를 정직히 기록합니다.

## evals

`evals/trigger-eval.json`은 이 하네스가 발동해야 하는 경우(should-trigger)와 발동하면 안 되는 경우
(should-not-trigger — AI끼리 병렬화·토폴로지, 컨텍스트 조립, 산출물 채점 judge, 단일 자율 반복, 상류 핸드오프 검수 등 인접 도메인)를 정의해 트리거 정확도를 점검합니다.
`evals/evals.json`은 shipped 파일이 핵심 불변식(에이전트=팀원·자율성⇄통제·적절한 의존·모니터링 감독(전수 승인 아님)·역할 경계·검증 운영(Doer-Verifier)·검증 충분조건 아님·책임·정직성·경계)을 명세·강제하는지 file:section 인용으로 채점합니다.
