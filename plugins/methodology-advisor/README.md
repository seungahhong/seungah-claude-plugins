# methodology-advisor

> 우리 팀에 **어떤 개발 방법론이 맞을까?** — 현행 프로세스를 먼저 진단하고, 개발·회사·사업을 다각도로 문진한 뒤, 근거로 방법론을 제안하는 인터랙티브 어드바이저.

`methodology-advisor`는 frontend-harness의 `grill-me` 인터뷰 스킬을 **개발 방법론 선택**에 특화·확장한 도메인 무관 멀티 에이전트 플러그인이다. "무조건 스크럼 쓰세요" 같은 은탄환을 팔지 않는다 — **방법론에는 우열이 없고 맥락 적합성만 있다**는 전제에서, 지금 팀 상황을 진단해 **상황에 맞는 방법론을 트레이드오프·안티패턴과 함께** 제안한다.

## 무엇을 하나

4단계로 진행하고, **매 단계 결과를 보여주고 승인받은 뒤에만** 다음으로 넘어간다.

1. **현행 프로세스 진단 (가장 먼저)** — "지금 개발/회사/사업 측면에서 어떻게 일하고 있나요?"부터 묻는다. 없는 프로세스를 가정하지 않고, 실제로 관측된 것만 지도화한다.
2. **다각도 문진 (grill-me)** — 한 번에 한 질문씩, 개발·회사·사업 3축으로 방법론 적합도를 가르는 인자를 캔다. 답변이 서로 충돌하면(예: "규제 감사 릴리스" + "하루 10회 배포") 즉시 알린다.
3. **방법론 매칭·제안** — 내장 카탈로그와 컨틴전시 프레임워크에 근거해 **2~3개 후보(순위) + 1순위 권고**를 낸다. 각 후보에 얻는 것/포기하는 것/이 팀이 빠질 오적용을 붙인다. 순수 방법론보다 **하이브리드 조합**(예: Scrumban + CD)이 맞으면 그걸 권한다.
4. **적대적 적합성 검증** — 제안을 스스로 반박한다. "이 방법론이 페인을 진짜 없애나, 이름만 바꾸나?", "숨은 전제가 현행에서 실제로 관측됐나?"를 캐고, 흔들리면 순위를 재정렬한다.

## 언제 발동하나

- "우리 팀에 맞는 개발 방법론 추천해줘 / 개발 방식 골라줘"
- "지금 프로세스 진단하고 스크럼·칸반 중 뭐가 맞을지 결정 도와줘"
- "규제 산업인데 애자일과 감사 릴리스를 어떻게 조화시킬지 문의받고 싶어"
- "팀이 커지는데 SAFe를 도입해야 할지 진단해서 제안해줘"

## 내장 방법론 (14)

계획주도(Waterfall·V-Model) · Scrum · Kanban · Scrumban · XP · Lean SD · Crystal · FDD · DSDM · Shape Up · 스케일드 애자일(SAFe·LeSS·Nexus) · Spotify "model"(복제 주의) · DevOps·CD·DORA · Wagile·하이브리드.

각 방법론은 **핵심 원칙 / 의식·아티팩트 / 적합 조건 / 안티패턴(오적용)** 으로 정리돼 있다 → [카탈로그](skills/methodology-advisor/references/methodology-catalog.md).

## 근거로 삼는 선택 프레임워크

- **Cynefin** — 문제가 Complex인지 Complicated인지에 따라 경험주도 vs 계획주도.
- **Stacey matrix** — 요구 확실성 × 기술 확실성.
- **Boehm & Turner home ground** — Size·Criticality·Dynamism·Personnel·Culture 5인자로 애자일↔규율 균형을 재단(위험 기반 5단계).

→ [선택 프레임워크](skills/methodology-advisor/references/selection-frameworks.md) · [질문뱅크](skills/methodology-advisor/references/interview-axes.md)

## 정직성 원칙

- **우열이 아니라 적합성** — "X가 낫다"고 말하지 않는다. "이 맥락에서 X가 적합, 이유는 …"만.
- **은탄환·수치 약속 없음** — "도입하면 N% 빨라진다"를 약속하지 않는다. DORA 등 수치는 출처·등급과 함께 **관찰값**으로만 인용한다(→ [근거](skills/methodology-advisor/references/research/README.md), 24소스 적대 검증, 70 confirmed / 5 refuted).
- **트레이드오프·안티패턴 동반** — 모든 권고에 "무엇을 포기하는가 + 흔한 오적용"을 붙인다.
- **제안만 한다** — 조직·프로세스 변경을 자동으로 실행하지 않는다. 도입은 팀의 결정이다.

## 산출물

산출물은 **저장을 선택할 때만** `.claude/_docs/<슬러그>/`에 남는다(기본은 채팅 제시): `current-process.md`(현행 진단) · `interview-log.md`(문진 로그) · `methodology-proposal.md`(제안서) · `fit-review.md`(검증 리포트).

## 경계 (다른 플러그인과 구분)

이 플러그인은 **사람 개발팀이 어떤 방법론/프로세스로 일할지**를 다룬다. 다음은 범위 밖이다.

| 하려는 일 | 맞는 플러그인 |
|-----------|---------------|
| 기획문서(PRD)·사용자 스토리 작성 | `product-spec-harness` |
| Claude 에이전트 하네스/스킬 생성·진단 | `harness-generator` · `meta-harness` |
| 상류 산출물(PRD·계약·디자인) 핸드오프 게이트 검수 | `review-harness` |
| 사람↔AI 에이전트 협업 설계 | `human-agent-teaming` |
| 작업을 여러 AI 에이전트로 병렬화 | `agent-orchestration` |
| 코드 구현·리뷰·커밋 | `frontend/backend/git-harness` |

독립 플러그인이다 — 단독 설치로 동작하며 다른 마켓플레이스 플러그인에 의존하지 않는다.
