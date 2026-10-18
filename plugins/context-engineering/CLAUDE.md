# context-engineering

LLM·에이전트에 전달할 **컨텍스트 페이로드를 체계적으로 조립·최적화**하는 도메인 무관 멀티 에이전트 하네스.
단순 프롬프트 설계를 넘어 "무엇을 왜 모델에 넣는가"를 **Scope → Retrieve → Process → Manage**의 4단계로 설계하고,
멀티 에이전트 컨텍스트면 per-agent 격리 패턴으로 cross-agent 오염을 막은 뒤, 검증된 최종 페이로드와 재사용 playbook을 낸다.

사용자용 개요·사용법은 [README.md](README.md), Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/context-engineering/SKILL.md), 방법론·근거는 [references/](skills/context-engineering/references/)다.

## Conventions

- **Scope 우선(retrieval need 먼저)**: 수집·압축 전에 "어떤 정보가 *반드시* 모델에 도달해야 하고 토큰 예산은 얼마인가"를 Phase 0에서 못 박는다. 컨텍스트는 많을수록 좋은 게 아니다.
- **체계적 최적화 ≠ 더 채우기**: Context Engineering은 정보 페이로드의 *체계적 최적화*다(단순 프롬프트 설계를 넘어선다). 더 많은 토큰이 아니라 *필요한 정보가 모델에 닿는 것*이 목표다.
- **구조적 증분(collapse 가드)**: 압축·재작성은 전면 재작성이 아니라 디테일을 보존하는 *구조적·증분적* 업데이트로 한다. brevity bias(간결 위해 도메인 통찰 누락)와 context collapse(반복 재작성이 디테일 침식)를 구조적으로 막는다.
- **위치 인지 배치**: 가장 중요한 컨텍스트를 페이로드 앞·뒤로 배치해 lost-in-the-middle을 완화한다(처리 단계 책임).
- **playbook 큐레이션**: 컨텍스트를 *진화하는 playbook*으로 다루고 generation/reflection/curation 모듈로 누적·정련한다. 일회성 system prompt 덮어쓰기로 보지 않는다.
- **멀티 에이전트 격리(opt-in)**: 여러 에이전트가 한 오케스트레이터 컨텍스트를 공유하면 cross-agent 오염(context pollution)이 생긴다. per-agent 격리(가벼운 status REGISTRY + 필요 시 한 에이전트 FOCUS)로 막는다. 이 격리 패턴은 벤더 비종속 오케스트레이션 패턴이며 멀티 에이전트 컨텍스트일 때만 활성화하는 선택 레인이다.
- **출처·검증**: 모든 후보 컨텍스트는 출처를 표기하고, 최종 페이로드는 예산·중복·근거를 context-curator가 검증한다(검증 없는 페이로드 출하 금지).
- **승인 게이트·관찰성**: Phase 0 Context Brief 승인은 항상. 매 단계 토큰 사용/예산을 보고하고, 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: '모델에 들어갈 정보 페이로드의 조립·최적화'에 특화한다. 작업의 병렬화(에이전트 오케스트레이션 설계)·AI 산출물 평가(judge 구성)·엔지니어용 실행 명세 작성·기획자용 PRD·하네스 자체 진단·단발 코드 수정은 범위 밖이다(일반 개념으로만 변별하며 타 플러그인에 의존하지 않는다).
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
