# eval-harness

AI 생성물(코드·에이전트 출력·산출 텍스트)을 **엄밀하게 평가**하는 도메인 무관 멀티 에이전트 하네스.
핵심 질문은 "점수가 몇 점인가"가 아니라 **"이 점수를 믿어도 되는가"** 다. LLM-as-a-Judge를 단일 샷이 아니라
다중 표본(≥3)으로 돌리고, ABC 체크리스트로 task/outcome validity·shortcut·harness≠model 귀인을 감사한 뒤,
집계 결과를 confidence·CAVEAT와 함께 보고한다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
eval-harness/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                       # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                       # 사용자용 개요·사용법·도구 경계·근거 논문 목록
├── agents/                         # 모두 model: "opus"
│   ├── eval-designer.md            # Phase 0 — 평가 대상·관찰형 성공기준 + task/outcome validity 명세 + 귀인 단위
│   ├── judge-builder.md            # Phase 1 — judge 구성(다중 표본 ≥3 + 다관점 분해 + 실행 grounding), single-shot 금지
│   ├── validity-auditor.md         # Phase 2 — ABC 관점 감사(validity·shortcut·harness≠model 귀인·instruction density), BLOCK 게이트
│   └── eval-runner.md              # Phase 3 — 다중 표본 실행·집계 + confidence + CAVEAT 보고
├── skills/
│   └── eval-harness/
│       ├── SKILL.md                # 오케스트레이터(진입점, Define → Build Judge → Audit → Run & Report)
│       └── references/
│           ├── eval-harness-principles.md   # 네 신뢰 축·judge/validity 설계지침·anti-pattern·경계
│           └── eval-harness-research.md      # 설계 근거 deep-research dossier (출처·인용·신뢰도·CAVEAT·반박된 주장)
└── evals/
    ├── evals.json                  # 수용 평가 (design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json           # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 경계 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 정의·validity (Define & Validity) | eval-designer | Eval Spec(평가 대상·관찰형 성공기준·task/outcome validity·귀인 단위·범위) | 승인 게이트 |
| 1 | judge 구성 (Build Judge) | judge-builder | Judge 구성서(표본 ≥3·다관점 분해·실행 grounding·기준별 루브릭) | single-shot 금지 |
| 2 | validity 감사 (Audit Validity) | validity-auditor | Validity 감사 보고(PASS/BLOCK + 위반·수정안 + 잔여 위험) | BLOCK 게이트(실행 전) |
| 3 | 실행·집계·보고 (Run & Report) | eval-runner | Eval 결과(기준별 결과 + confidence + CAVEAT + baseline 대비 비교) | — |

최종 보고: `[Eval 종료] 결과 {요약} — confidence {high|medium|low}(표본 {k}/{N} 일치), CAVEAT {n}건, validity 감사 {PASS}.`

## Conventions

- **validity 우선**: 측정 대상이 측정 가능하게 정의되고(task validity) 그 측정이 실제 능력을 가리켜야 한다(outcome validity). validity 결함은 성능을 상대 최대 100%까지 왜곡할 수 있다(연구 근거, 상한치 — 일률 100% 아님). Phase 2를 게이트로 둔다.
- **single-shot 금지(다중 표본 ≥3)**: 단일 표본 judge는 오도될 수 있다. temp-0의 재현성을 정확성으로 착각하지 않는다("facade of reliability"). 최소 3회 표본하고 분산을 confidence로 환산한다.
- **다관점 분해·실행 grounding**: 어려운 판정을 "더 단순하고 다관점인 평가들"로 분해하고(MCTS식 프레이밍만 채택), 가능하면 실행 결과(테스트·종료코드·산출물 속성)에 닻 내린다.
- **shortcut 적대 감사**: 과제를 풀지 않고 만점 받는 우회로(파일시스템 악용·정답 누출·타임아웃=성공)를 judge를 돌리기 *전에* 막는다.
- **harness≠model 귀인**: "a coding agent in practice is not a model: it is a system harness." 점수를 단일 end-to-end로 붕괴시키지 않고 컴포넌트별 신호를 남긴다(같은 모델도 harness에 따라 단일 task type에서 20+pp 갈릴 수 있음).
- **instruction density 절제**: 채점 루브릭에 지시를 과밀하게 넣으면 따르기 정확도가 떨어진다(연구 근거). 핵심 기준으로 추리거나 분할한다.
- **confidence·CAVEAT·baseline 대비**: 결과는 항상 confidence와 CAVEAT(validity 잔여 위험·grounding 유무·귀인 한계)와 함께 낸다. "개선 N% 보장" 단정 금지 — 비교는 baseline 대비로만, 인용 수치는 검증된 값만 vote/CAVEAT와.
- **관찰 가능성·승인**: Phase 0 Eval Spec 승인 게이트는 항상. 요청되지 않은 사이드 에이전트나 중복 실행을 만들지 않는다.
- **경계**: AI 생성물의 *판정 신뢰성*을 설계·감사·실행한다. 컨텍스트 페이로드 조립·압축, 작업의 에이전트 병렬화 판단, 엔지니어용 구현 명세 작성, 기존 코드의 일반 실행 테스트 생성, 커밋 메시지·PR 코드 리뷰는 범위 밖이다(일반 개념으로만 서술, 타 도구 비의존).
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 모든 Agent 호출에 `model: "opus"`를 명시한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | AI 생성물 엄밀 평가(LLM-as-a-Judge 다중 표본 + benchmark validity 감사 + harness≠model 귀인) 멀티 에이전트 하네스. deep-research 3표 적대검증으로 confirmed된 2024+ 1차 논문 출처(arXiv:2507.02825·2412.12509·2502.12468·2507.11538·2606.17799) 근거 |
