# ai-readiness-cartography

git 저장소가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스**인지를 **측정하고(결정론 스코어러) 승인 게이트 뒤에 개선을 적용하는(멀티 에이전트)** 도메인 무관 단일 스킬(**3 모드·자유 조합**). **① 측정**은 100점·9 카테고리 + 3 gate로 채점해 JSON 점수표·HTML 대시보드·ROI 가이드를 낸다(코드 수정 없음). **② 진단·개선**은 그 측정을 센서로 2축(Q/A) 진단 → 빌드 가드레일 → standalone → **계획·개별 승인 뒤 코드 적용**(S/M/L·고위험 구조 리팩터 opt-in) → 수용 증명·재측정을 4 에이전트로 수행한다. **③ 코드 본문**은 `legibility_scan.py` census를 seed로 주석·명명·구조를 진단하고 **3게이트 승인 뒤에만** 단계별 수정한다(C0→C2→C1→C3). 여러 모드를 고르면 **①→②→③ 순**으로 이어 수행하고 `score.py`는 ①②가 1회 공유하며, ②+③이면 구조 리팩터는 ②가 소유하고 ③의 C3는 끈다. ③은 저장소 층 등급을 만들지 않고(census만), ②③ 모두 커밋하지 않는다(git-harness 핸드오프).

사용자용 개요·사용법은 [README.md](README.md), 모드·Phase 흐름·게이트·에이전트 팀의 정본은 [SKILL.md](skills/ai-readiness-cartography/SKILL.md), 루브릭·원칙·근거는 [references/](skills/ai-readiness-cartography/references/)(등급표는 [scoring-rubric.md](skills/ai-readiness-cartography/references/scoring-rubric.md))다.

## Conventions

- **모드 선택 먼저(자유 조합) · 문의는 한 번에 하나씩**: 발동 시 ①/②/③ 중 원하는 **부분집합**을 한 질문으로 고르고(다중 선택 허용), 모드를 확정한 *뒤에* 세부 스코프(경로→축→개입 클래스→고위험 opt-in)를 **하나씩** 묻는다(직전 답이 다음 질문을 결정). 여러 개면 ①→②→③ 순, `score.py`는 ①②가 **1회만** 공유 실행(③은 `legibility_scan.py` 별도), ②가 함께 돌면 Gate-3 판정이 측정의 "미평가"를 대체, ②+③이면 구조 리팩터는 ②가 소유하고 ③의 C3는 끈다.
- **결정론 우선, 사람 보강**: score.py(stdlib only, Python 3.10+)가 자동 채점하고 LLM은 heuristic/manual 항목·E1 dangling 후보 확인·Gate-3 강제 판단을 보강한다. 손채점부터 하지 않는다.
- **gating(blocking > 가산)** · **근거 서열 = 가중치 서열**: blocking 결함이 등급 상한을 씌우고(Gate-1/2→AI-Fragile, Gate-3→AI-Assisted), 실행·검증(E) ≫ 의존 구조(D) > 문맥 문서(B/C) 서열은 ORACLE-SWE ablation에서 온다.
- **A축 ≠ Q축 · 구조가 프롬프트보다 먼저 · 빌드가 강제하고 문서가 설명한다**: 코드 품질과 AI 접근성은 별개 축. 빌드로 잡을 수 있는 것을 산문에 맡기지 않고, 가장 중요한 규칙을 가장 빠른 계층(컴파일)에서 잡는다.
- **문서 존재 ≠ 좋음**: 컨텍스트 보유율은 점수화하지 않는다(ETH Zurich 2602.11988 반증). novelty·비중복·command-first만 가점. **god-file=결합도**(fan-in/out 1급, 라인 수는 근거 약한 보조).
- **설계 원칙은 진단만, 점수화 안 함**: SOLID·응집/결합·복잡도·LCOM·중복은 `extras.design_signals`(report-only)로만 표면화하고 100점 등급에 넣지 않는다 — 고전 구조 지표는 코드 길이 통제 시 LLM 성능과 무상관(session-6)이고 준수도 점수화는 Goodhart를 부른다. 진단 대상: 식별자 명료성(R12)·모듈 순환 의존·정확 중복(Type-1/2)·과대추상·결합 hotspot. `test_score.py`가 "총점=9카테고리 합" 불변식을 고정한다.
- **generator/checker 분리**: 설계(Phase 1/2)·적용(Phase 3)과 재측정 검증자(Phase 4)를 분리하고, 센서는 `behavior-guard`가 실행 관측한다(자기보고 불신).
- **승인 게이트 뒤에만 수정**: ①은 측정·시각화만. ②③은 제안·설계 후 승인 게이트(②=계획·개별, ③=3게이트) 뒤에 코드를 수정하고(고위험 opt-in·리네임=AST/LSP 위임·"테스트 통과≠동작 보존"), 커밋은 하지 않는다.
- **결정 권한(위험은 경고, 수용은 사용자)**: 고위험 변경(②의 L·③의 C3) 위험은 *경고*하되 감수는 *사용자*가 결정한다. opt-in·개별 승인된 항목을 회귀 위험을 이유로 **조용히 보류·강등하지 않고**(승인 게이트 ≠ veto), 새 차단 요인은 **execute-or-escalate**. **자동 테스트 부재는 거부 사유가 아니라 행위 센서 승격 사유**다(UNVERIFIED는 관측 한계 라벨·red 센서만 롤백). "리팩토링" 요청을 S 툴링으로 대체 충족하지 않고, 인도분이 요청 클래스와 다르면 정직히 밝힌다.
- **본문 층은 등급을 만들지 않고 볼륨에 가점하지 않는다(③)**: census는 report-only이고, **마크업 시맨틱(MK*)·테스트 설명(TL*)은 census 전용 축**이다 — 이들을 격리해 LLM 이해 델타를 잰 연구가 없고(O-6) 접근성 개선은 이 하네스의 표적이 아니므로 **개입 카드를 두지 않는다**(자동 ARIA/alt/어서션 생성 금지). comment-gap(C7~C9)도 결함이 아니라 '왜' 주석 추가 후보(opt-in·사람 검증·볼륨 무점수).
- **과장 금지**: 외부 정량 수치는 근거 등급·CAVEAT와 함께만, "개선 N% 보장" 금지. 구조 리팩터 효과는 추론(측정 아님).
- **경계**: 한 기능 구현·검증(backend-harness), 상류 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인(cicd-harness), 명세 작성(spec-driven-development), 컨텍스트 조립(context-engineering), 평가 judge(eval-harness), 병렬화·협업 토폴로지(agent-orchestration), 완성 코드 리뷰·PR(frontend/git-harness)은 범위 밖.
- SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**하고, 선택된 축·클래스에 해당하는 에이전트만 호출한다(스코프 가드).

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 위에 행을 추가한다.
