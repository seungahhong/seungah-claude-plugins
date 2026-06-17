# Project Structure

```
.claude-plugin/                                          # 마켓플레이스 등록 메타데이터
  marketplace.json                                       # 리스팅 정보 (owner, metadata, plugins)
plugins/
  frontend-harness/                                      # 플러그인 루트
    .claude-plugin/
      plugin.json                                        # 플러그인 메타데이터 (이름, 버전, 키워드, 스킬/에이전트 경로)
    commands/                                            # 커스텀 커맨드 디렉토리
      orchestrator.md                                    # 전체 워크플로우 오케스트레이터 (research → prd → develop → review → verify)
      research.md                                        # 요구사항 분석 (grill-me 서브에이전트 활용)
      prd.md                                             # PRD 작성 (planner → architecture → critic 서브에이전트 루프)
      frontend-guidelines.md                             # Develop 단계 — 프론트엔드 가이드라인 (a11y + semantic-html + seo-geo + tdd 서브에이전트)
      review.md                                          # Review — /simplify + /review + security-audit + lighthouse + qa-inspector 5개 관점 병렬 + 재리뷰 루프
      verifier.md                                        # E2E 브라우저 검증 (e2e-verifier 스킬 기반)
      verify.md                                          # Verify 통합 — E2E 브라우저 검증 + 타입/빌드 검사
    hooks/                                               # 플러그인 훅 디렉토리
      hooks.json                                         # Stop 훅 설정 (lint 체인 자동 실행)
      stop-lint.sh                                       # eslint → stylelint → prettier 자동 수정 스크립트
    skills/                                              # 스킬 정의 디렉토리
      planner/                                           # 계획 수립 (+ references/)
      architecture/                                      # 아키텍처 설계
      critic/                                            # 설계 검증
      grill-me/                                          # 인터뷰
      tdd/                                               # 테스트 주도 개발 (+ references/)
      a11y/                                              # 웹접근성 점검 (+ references/)
      semantic-html/                                     # 시맨틱 HTML 점검
      seo-geo-optimizer/                                 # SEO/GEO 최적화 (+ references/)
      e2e-verifier/                                      # E2E 브라우저 검증 (+ references/)
      lighthouse-performance/                            # Lighthouse 기반 Core Web Vitals 측정
      qa-inspector/                                      # 모듈 간 경계면 불일치 검증 (+ references/)
      security-audit/                                    # OWASP Top 10 보안 감사 (+ references/)
  harness-generator/                                     # [독립 플러그인] 도메인 무관 하네스 수동·인터랙티브 생성 메타 플러그인
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 0~7 요약 + 변경 이력
    README.md                                            # 사용자용 개요 (도구 선택 가이드 포함)
    skills/
      harness-generator/                                 # 하네스(에이전트팀+스킬+오케스트레이터) 수동 생성 제너레이터 스킬 (+ references/)
    evals/                                               # 트리거 경계 평가 (자동 탐색·Pareto 도메인·meta-harness와 cross-plugin reciprocal 가드)
  git-harness/                                           # [독립 플러그인] Git 워크플로우 멀티 에이전트 스킬 모음
    .claude-plugin/
      plugin.json
    skills/
      commit/                                            # 한국어 커밋 메시지 작성 스킬 (`이슈번호 type: 제목` 형식)
      review-to-pr/                                      # 리뷰 → 커밋 → PR 생성 올인원 워크플로우 스킬 (/simplify + /review 내장)
  meta-harness/                                          # [독립 플러그인] Meta-Harness 논문(arXiv 2603.28052v1) 기반 메타 하네스 엔지니어링 — full-trace experience store + causal reasoning + Pareto 비후퇴, 사용자 승인 게이트 (R1 현세션 redirect/보강 · R2 plugin 개선 · R3 외부 .md 역추적)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 변경 이력
    README.md                                            # 사용자용 개요
    agents/                                              # 모두 model: "opus"
      trace-capturer.md                                  # 현세션 신호 + 외부 .md → 원형 trace 정규화 (요약 금지, R3 3단 폴백 출처 역추적)
      failure-diagnostician.md                           # 결함 1건당 root cause 진단 (병렬, raw trace grep/cat 직접 조회, confound 격리)
      pareto-refiner.md                                  # additive-first → compose → transfer patch 생성 (자동 적용 금지)
      experience-historian.md                            # experience-store 큐레이션 (history/index/pareto/recurring)
    skills/
      meta-harness/                                      # 진입점 오케스트레이터 (Phase 0~8 + R4 보고) (+ references/)
      session-signal-capture/                            # R1/R3 신호 캡처 방법론 (원본 보존)
      causal-diagnosis/                                  # full-trace 기반 causal 진단 루브릭
      pareto-refinement/                                 # Pareto/additive patch 생성 방법론
    evals/                                               # acceptance assertion + 트리거 평가 + dry-run 리포트
  product-spec-harness/                                  # [독립 플러그인] 기획자(PM)용 기획문서(PRD)+사용자 스토리 5단계 인터랙티브 하네스 + 기획안 DoR 평가(내재화·외부 의존 없음, 단독 동작) — 개발 착수 전, 도메인 무관 (입력 모드 A 기획안/B 인터뷰; 경계: 프론트엔드 화면 구현·기술 설계·코드/하네스/커밋·완성 산출물 핸드오프 게이트 검수 제외)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 5단계 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·입력 모드
    agents/                                              # 모두 model: "opus" (Phase 순차)
      requirements-analyst.md                            # Phase 0 요구/문제/사용자 정의 (Discovery) — 기획안 있으면 카드 추출, 없으면 인터뷰
      dor-evaluator.md                                   # Phase 1 원본 기획안 DoR 평가 (모드 A·조건부·생성 전 선행) — # DoR Review 결과 + 보강 체크리스트 채팅 제시, 보강점을 PRD·스토리에 반영 (저장은 마무리 opt-in)
      prd-writer.md                                      # Phase 2 기획문서(PRD) 작성 — 배경·목표·범위·요구사항·리스크·마일스톤 (Phase 1 보강점 반영)
      story-writer.md                                    # Phase 3 사용자 스토리 + 수용기준(Given/When/Then) + INVEST 자가점검 (Phase 1 보강점 반영)
      spec-reviewer.md                                   # Phase 4 적대적 검증 — 요구↔스토리 추적·INVEST·관찰성·일관성·모호 색출 (채팅만, 파일 저장 안 함)
    skills/
      product-spec/                                      # 진입점 오케스트레이터 (Phase 0~4 인터랙티브, 승인 게이트, 입력 모드 A/B, DoR 평가 결과 저장은 opt-in)
        SKILL.md                                         #   오케스트레이터 본문
        references/
          prd-template.md                                #   PRD 표준 구조 + 작성기준
          user-story-guide.md                            #   As a/I want/so that + Gherkin + INVEST
          dor-review-rubric.md                           #   DoR 평가 루브릭 내재화 (# DoR Review 결과·체크리스트·Honesty Guardrail·2025+ 근거)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger / should_not, 자매 하네스(review-harness) reciprocal 가드 포함)
  loop-engineering/                                      # [독립 플러그인] 검증 가능한 목표를 향한 자율 반복 루프 + 지속학습 메모리 멀티 에이전트 하네스 (실행 루프 Goal→Execute→Verify→Diagnose→Improve + 학습 루프 Fail→Investigate→Verify→Distill→Consult). 경계: 하네스 진단·개선(meta-harness)·하네스 생성(harness-generator)·PRD(product-spec/frontend)·커밋(git-harness)·native /loop 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 루프 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계
    agents/                                              # 모두 model: "opus"
      goal-setter.md                                     # Goal — 모호한 요청 → 검증 가능한 목표(관찰형 성공기준 + 실행 가능한 검증 방법 + 중단조건)
      loop-executor.md                                   # Execute — 목표를 향한 1회 반복 (메모리 consult + 직전 개선안 적용, 최소 변경)
      loop-verifier.md                                   # Verify — 검증 방법 실행 → 엄격 PASS/FAIL + 증거 (적대적, 증거 없는 PASS 금지)
      failure-analyst.md                                 # Investigate — root cause 진단(사실로 전환) + 다음 접근 작성 + 무진전 감지
      memory-curator.md                                  # Distill/Consult — 검증된 교훈 distill, 관련 규칙 surface, raw trace 보존
    skills/
      loop-engineering/                                  # 진입점 오케스트레이터 (Phase 0 Goal 게이트 → Phase 1 자율 반복 루프, auto/gated)
        SKILL.md
        references/
          loop-engineering-principles.md                #   두 루프·7원칙·검증기/중단조건 설계·anti-pattern·참고문헌
          loop-memory-format.md                          #   goal.md / iterations.jsonl / lessons.md on-disk 포맷
          loop-engineering-research.md                   #   설계 근거 deep-research dossier (출처·인용·신뢰도·caveat)
    evals/
      evals.json                                         # 수용 평가 (design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 13, 인접 하네스(meta/harness-generator/product-spec) reciprocal 가드)
  review-harness/                                        # [독립 플러그인] 코드 착수 *전* 상류 산출물(기획·디자인·API 계약·QA 인수조건) 핸드오프 게이트 검수. 경계: 완성 코드 리뷰(frontend-harness)·PRD/스토리 작성(product-spec)·커밋/PR(git-harness)·하네스 진단(meta-harness) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 4개 게이트 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·정직성 가드레일
    commands/
      handoff-review.md                                  # 오케스트레이터(진입점) — 게이트 선택 → 병렬 실행 → 착수 준비도(Readiness) 통합 리포트
    skills/                                              # 모두 disable-model-invocation: true · allowed-tools에 Edit/Write 없음(읽기 위주)
      dor-review/                                        # 기획 DoR 게이트 (DoR·INVEST·GWT 완결성·모호성 린트·의존성 참조)
      design-handoff-review/                             # 디자인 핸드오프 사각지대 (상태 누락·토큰 바인딩·컴포넌트↔코드 매핑·상태별 oracle, Figma MCP)
      contract-review/                                   # API 계약 게이트 (엔드포인트 완결성·breaking-change diff·소비자(CDC) 커버리지·코드↔spec drift)
      test-coverage-review/                              # 인수조건↔테스트 커버리지 (테스트가능성·AC↔테스트 매핑·커버리지 채점·누락 시나리오 발굴)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 14 / should_not 11, 자매 하네스(frontend/product-spec/git/meta) reciprocal 가드)
```
