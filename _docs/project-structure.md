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
      figma-extract/                                     # Figma 링크→디자인 컨텍스트 추출/파일화 (metadata 노드맵 우선→대상 노드 상세 추출→.claude/design/ json·spec·png 산출, 부모엔 경로+요약만; 코드 생성 안 함, 단독 동작) (+ references/) 
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
  meta-harness/                                          # [독립 플러그인] Meta-Harness 논문(arXiv 2603.28052v1) 기반 메타 하네스 엔지니어링 — full-trace experience store + causal reasoning + Pareto 비후퇴, 사용자 승인 게이트 (R1 현세션 redirect/보강 · R2 plugin 개선 · R3 외부 .md 역추적). self-heal 캡처 훅(UserPromptSubmit)이 '수정/보강' 발화를 signals 레인에 원형 적재 → 추후 healer가 소비(적용은 승인 게이트 후)
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
    hooks/                                               # 플러그인 훅 (self-heal 캡처)
      hooks.json                                         # UserPromptSubmit 훅 설정
      self-heal-capture.sh                               # '수정/보강/방향전환' 발화 → signals 레인 원형 적재 (캡처 전용·비차단, cross-session)
    evals/                                               # acceptance assertion + 트리거 평가 + dry-run 리포트
  product-spec-harness/                                  # [독립 플러그인] 기획자(PM)용 기획문서(PRD)+사용자 스토리 5단계 인터랙티브 하네스 + 기획 완성도 점검(DoR)(내재화·외부 의존 없음, 단독 동작) — 개발 착수 전, 도메인 무관 (산출물은 .claude/_docs/<기획서 슬러그>/에 저장) (입력 모드 A 기획안/B 인터뷰; 경계: 프론트엔드 화면 구현·기술 설계·코드/하네스/커밋·완성 산출물 핸드오프 게이트 검수 제외)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 5단계 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·입력 모드
    agents/                                              # 모두 model: "opus" (Phase 순차)
      requirements-analyst.md                            # Phase 0 요구/문제/사용자 정의 (Discovery) — 기획안 있으면 카드 추출, 없으면 인터뷰
      dor-evaluator.md                                   # Phase 1 원본 기획안의 기획 완성도 점검(DoR) (모드 A 진입질문 필수·생성 전 선행) — # 기획 완성도 점검 결과(DoR Review) + 보완할 점 점검표(보강 체크리스트) 채팅 제시, 보강점을 PRD·스토리에 반영 (저장은 마무리 opt-in)
      prd-writer.md                                      # Phase 2 기획문서(PRD) 작성 — 배경·목표·범위·요구사항·리스크·마일스톤 (Phase 1 보강점 반영)
      story-writer.md                                    # Phase 3 사용자 스토리 + 수용기준(조건·행동·결과(Given/When/Then)) + 좋은 스토리 6가지 기준(INVEST) 자가점검 (Phase 1 보강점 반영)
      spec-reviewer.md                                   # Phase 4 적대적 검증 — 요구↔스토리 추적·INVEST·관찰성·일관성·모호 색출 (채팅 제시 + 동의 시 adversarial-review.md 저장)
    skills/
      product-spec/                                      # 진입점 오케스트레이터 (Phase 0~4 인터랙티브, 승인 게이트, 입력 모드 A/B, 산출물은 .claude/_docs/<슬러그>/에 저장·각 파일 opt-in)
        SKILL.md                                         #   오케스트레이터 본문
        references/
          prd-template.md                                #   PRD 표준 구조 + 작성기준
          user-story-guide.md                            #   As a/I want/so that + 조건·행동·결과(Gherkin) + 좋은 스토리 6가지 기준(INVEST)
          dor-review-rubric.md                           #   기획 완성도 점검(DoR) 루브릭 내재화 (# 기획 완성도 점검 결과(DoR Review)·보완할 점 점검표·Honesty Guardrail·2025+ 근거)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 15, 인접 하네스(meta/harness-generator/product-spec) reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 14 / should_not 13, 자매 하네스(frontend/product-spec/git/meta) reciprocal 가드)
  ops-harness/                                           # [독립 플러그인] 프로덕션 운영·인시던트 대응·관측성 하네스. AIOpsLab 4단계(탐지→국소화→RCA→완화). 경계: 하네스 진단(meta)·검증루프(loop)·코드리뷰(frontend/git)·상류 핸드오프(review)·PRD(product-spec) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 4단계(L1–L4) 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계
    agents/                                              # 모두 model: "opus"
      incident-detector.md                               # L1 Detection — 이상 탐지·트리아지(RED/USE)
      incident-localizer.md                              # L2 Localization — traces 우선 범인 후보 국소화
      root-cause-analyst.md                              # L3 RCA — 인과사슬 확정(anti-anchoring 가드 + Straight-Shot 폴백)
      mitigation-planner.md                              # L4 Mitigation — 완화안 + 위험/롤백/blast radius + DQ 채점(사람 집행)
    skills/
      ops-harness/                                       # 진입점 오케스트레이터 (Phase 0 텔레메트리 확보 → L1→L4 게이트)
        SKILL.md
        references/
          ops-harness-principles.md                      #   4단계·역할분리·DQ·RCA 가드레일·anti-pattern
          incident-response-research.md                  #   설계 근거 dossier (출처·등급·인용·CAVEAT)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 11, 인접 하네스 reciprocal 가드)
  backend-harness/                                       # [독립 플러그인] 백엔드/API 실행 기반 검증 구현 하네스 + test-generator 스킬. 경계: 계약 검수(review-harness/contract-review)·FE(frontend)·PRD(product-spec)·커밋(git)·하네스 진단(meta)·자율 반복(loop) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 5단계 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계
    agents/                                              # 모두 model: "opus"
      be-architect.md                                    # 설계 — 서비스 경계·API 계약·데이터 모델/마이그레이션 + 검증 후크·환경 요구사항
      env-provisioner.md                                 # 환경 — 빌드·실행·테스트 가능 상태 확보(최대 병목, 독립 1급 단계)
      be-implementer.md                                  # 구현 — API·서비스 로직·DB 스키마/마이그레이션(계약 준수)
      be-verifier.md                                     # 검증 — 실행 기반 PASS/FAIL·빌드/테스트 재실행·고커버리지·reward-hacking 가드
    skills/
      backend-harness/                                   # 진입점 오케스트레이터 (Phase 0~4 + 승인 게이트)
        SKILL.md
        references/
          backend-harness-principles.md                  #   6원칙·anti-pattern·env 독립 근거·인접 하네스 경계
          backend-harness-research.md                    #   설계 근거 dossier (출처·등급·CAVEAT)
      test-generator/                                    # 실행기반 테스트 생성+수리 루프 스킬(model-invocable)
        SKILL.md
        references/
          test-generator-guide.md                        #   공진화 루프·5 경험적 수리 템플릿·커버리지 게이트·judge 캘리브레이션
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 11, 인접 하네스 reciprocal 가드)
  cicd-harness/                                          # [독립 플러그인] 코드 커밋→프로덕션 전달 파이프라인 CI/CD·DevOps·릴리스·IaC 하네스. 경계: 배포 이후 인시던트(ops)·BE 구현(backend)·빌드그린 반복(loop)·커밋/PR(git)·계약검수(review) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 4단계 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계
    agents/                                              # 모두 model: "opus"
      pipeline-architect.md                              # Phase 1 — CI 파이프라인·릴리스 전략 설계/검수(제안만)
      iac-reviewer.md                                    # Phase 2 — IaC 검증(terraform plan 실행검증 + OPA policy-as-code 결정론적 게이트)
      release-gatekeeper.md                              # Phase 3 — 릴리스·배포 결정(flaky·rollback·feature-flag·canary, trust-tier 단계적 자율)
      delivery-verifier.md                               # Phase 4 — 전달 안정성 가드(DORA 통제: 테스트 자동화·작은 배치, defense-in-depth 승인)
    skills/
      cicd-harness/                                      # 진입점 오케스트레이터 (Phase 0 범위·trust-tier → P1→P4 게이트)
        SKILL.md
        references/
          cicd-harness-principles.md                     #   4단계·defense-in-depth·policy-as-code·trust-tier·DORA·anti-pattern
          cicd-harness-research.md                       #   설계 근거 dossier (출처·등급·CAVEAT·DORA 반증 nuance)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 13, 인접 하네스 reciprocal 가드)
```
