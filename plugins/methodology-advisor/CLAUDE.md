# methodology-advisor

팀의 **현행 개발·회사·사업 프로세스를 먼저 진단**하고, grill-me 스타일 **다각도 문진**(3축) 뒤, 내장 방법론 카탈로그 + 컨틴전시(맥락 적합) 프레임워크에 근거해 상황에 맞는 개발 방법론을 **순위 shortlist + 1순위**로 제안하는 도메인 무관 인터랙티브 멀티 에이전트 하네스. **첫 행동은 반드시 현행 진단**이다(발명 금지).

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/methodology-advisor/SKILL.md), 카탈로그·프레임워크·근거는 [references/](skills/methodology-advisor/references/)(연구 대장은 [research/README.md](skills/methodology-advisor/references/research/README.md))다.

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

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 위에 행을 추가한다.
