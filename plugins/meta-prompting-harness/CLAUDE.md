# meta-prompting-harness

**메타 프롬프팅**(AI에게 입력할 프롬프트를 AI가 최적화해 생성하게 하고, 그 결과 프롬프트를 새 컨텍스트에 주입해 실제 작업을 돌리는 기법)을 4단계 인터랙티브 멀티 에이전트로 수행하는 도메인 무관 하네스. 널리 쓰이는 메타 프롬프팅 실천 방법론을, 각 기법을 `/deep-research`로 2023~2026 1차 문헌과 대조해 근거 등급을 붙여 재구성했다.

사용자용 개요·사용법은 [README.md](README.md), 근거는 [evidence.md](skills/meta-prompting/references/evidence.md) 참조.

## Structure

```
meta-prompting-harness/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 4 Phase 요약 + 원칙 + 근거 등급
├── README.md                        # 사용자용 개요·사용법·경계
├── agents/
│   ├── context-elicitor.md          # Phase 1 질문 유도(빠진 요소 되묻기·전부위임 방지)
│   ├── success-definer.md           # Phase 2 성공·검증 조건(외부 기준 대비)
│   ├── prompt-carver.md             # Phase 3 환경 맞춤 깎아내기(큰그림→축소)
│   └── prompt-critic.md             # Phase 4 적대 점검 + fresh context 주입 안내
├── skills/meta-prompting/
│   ├── SKILL.md                     # 오케스트레이터(진입점, 4 Phase, 승인 게이트)
│   └── references/
│       ├── execution-environments.md  # 환경별 하드 제약·필수 변수·엔딩 조건
│       ├── carving-principles.md       # 깎아내기 8원칙(각 근거 등급)
│       └── evidence.md                 # 기법별 학술 검증·등급·1차 소스
└── evals/trigger-eval.json          # 발동/비발동 트리거 예시
```

## 4 Phase

- **Phase 0** 인테이크 — 목표 + 실행 환경을 **한 번에 한 질문씩** 확정. 컨텍스트는 있으면 정제 없이 붙여넣는 선택지(덤프 강요 안 함).
- **Phase 1** 질문 유도(context-elicitor) — 빠진 요소를 AI가 먼저 되묻되 **한 번에 하나씩·번호 선택지·직전 답이 다음 질문 결정**(한꺼번에 쏟지 않음), 전부위임 방지.
- **Phase 2** 성공·검증 조건(success-definer) — specific 성공 + 외부 기준 대비 검증.
- **Phase 3** 환경 맞춤 깎아내기(prompt-carver) — 환경 규약·길이 상한 반영, 큰그림→축소, 최종 프롬프트 산출.
- **Phase 4** 적대 점검·주입(prompt-critic) — 모호·과대·미검증 점검, 사용자 도메인 수정, fresh 창 주입 안내.

**모든 Agent 호출은 `model: "opus"` 명시. 매 Phase 승인 게이트.**

## 근거 등급 (정직성 핵심)

- **STRONG** — 메타프롬프팅>직접(2401.12954·2309.03409·2310.16427, 조건부)·명확화 질문(ClarifyGPT·Orchid)·성공+검증 명시(Anthropic 공식)·fresh context(2307.03172·context-rot)·은탄환 아님(Anthropic).
- **report-only(folklore)** — 환경 맞춤 변환·큰그림→축소(1차 근거 생존 못 함, "실증" 표현 금지).
- **REFUTED(미사용)** — "지휘자가 전문가 인스턴스 생성" 프레이밍(0-3)·"LLM 스스로 명확화 불가"(1-2).

절대 규칙: 최적화 프롬프트를 보편 법칙으로 서술 금지 · 전부 위임 금지 · AI가 깎은 프롬프트는 사용자 도메인 검증 필수 · 프롬프트 생성만 하고 실행은 사용자 · 커밋 안 함 · 점수화 안 함.

## 경계

이미 목표가 있는 컨텍스트 페이로드 조립·압축·리트리벌·하네스 자체 생성/진단·기획문서(PRD)·사용자 스토리·계획/방법론 인터뷰·자율 반복 루프 실행·코드 구현/리뷰/커밋은 범위 밖(산출물이 프롬프트가 아님). 고유 판별자: *다른 도구에 주입할 지시 프롬프트 자체*를 질문 유도·성공조건·환경 맞춤으로 깎아냄. 다른 플러그인을 참조하거나 의존하지 않고 자족하는 독립 플러그인.

## 변경 이력

- **v0.1.0** (2026-07-21) 신설. 메타 프롬프팅 실천 방법론을 `/deep-research`(6각도·25소스·23 confirmed/2 refuted)로 1차 문헌 대조·근거 등급 부여. 4에이전트(opus)·references 3종·evals.
- **v0.1.1** (2026-07-21) 사용자 요청: 사용자에게 문의 시 **덤프로 한꺼번에 묻지 않고 한 번에 한 질문씩 단계별**로 정리. Phase 0 인테이크를 목표→환경 순 한 질문씩 확정으로, 컨텍스트 덤핑은 *강요*에서 *선택지*(있으면 붙여넣기)로 완화. Phase 1 context-elicitor를 '번호 질문 한 화면 몰아 노출'에서 **중요도 순 질문 계획 → 오케스트레이터가 한 번에 하나씩·번호 선택지·직전 답이 다음 질문 결정**으로 재작성(수십 개 한꺼번에 노출 제거). 내재화 원칙에 '한 번에 한 질문' 불변식 추가. carving-principles 원칙 1·2·핵심 프로세스·description·root/docs 정합. 근거상으로도 명확화 질문(T2 STRONG)에 부합하고 덤핑(T1 조건부·관행)은 선택으로 남김.
