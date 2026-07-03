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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 19, 인접 하네스(meta/harness-generator/product-spec/code-as-harness) reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 14 / should_not 16, 자매 하네스(frontend/product-spec/git/meta) reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 12, 인접 하네스 reciprocal 가드)
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
  context-engineering/                                   # [독립 플러그인] LLM·에이전트에 넣을 컨텍스트 페이로드를 체계적으로 조립·최적화하는 하네스 (Scope→Retrieve→Process→Manage 4단계 + per-agent 격리). 경계: 에이전트 병렬화 판단·AI 산출물 평가·구현 명세 작성·PRD·하네스 진단 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 논문
    agents/                                              # 모두 model: "opus"
      context-scoper.md                                  # Phase 0 Scope — 도달 정보·토큰 예산·retrieval need(must/nice/out) 명세
      context-retriever.md                               # Phase 1 Retrieve/Generate — RAG식 후보 컨텍스트 수집·생성(출처·relevance·충돌 표기)
      context-processor.md                               # Phase 2 Process — 압축·정렬·중복제거(구조적 증분, brevity bias·lost-in-the-middle 대응)
      context-curator.md                                 # Phase 3 Manage — playbook 큐레이션·context-collapse 가드·REGISTRY/FOCUS 격리·최종 검증·조립
    skills/
      context-engineering/                               # 진입점 오케스트레이터 (Phase 0 Scope 게이트 → 4단계 조립 파이프라인)
        SKILL.md
        references/
          context-engineering-principles.md              #   4 components·anti-pattern(brevity/collapse/lost-in-middle/pollution)·REGISTRY/FOCUS·설계 지침
          context-engineering-research.md                #   설계 근거 dossier (출처·인용·vote·CAVEAT·반박된 주장; arXiv:2507.13334·2510.04618·2604.07911)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 15, 인접 도메인 reciprocal 가드)
  agent-orchestration/                                   # [독립 플러그인] 작업을 여러 에이전트로 병렬화할지·어떻게 협업시킬지 판단 규칙으로 결정하고 단일 baseline 능가를 적대 검증하는 하네스. 경계: 컨텍스트 조립·AI 출력 평가·구현 명세·단일 자율루프·하네스 생성·장애 대응 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 논문
    agents/                                              # 모두 model: "opus"
      task-decomposer.md                                 # Phase 0 — 분해 가능성·도구 밀도·의존 구조 평가 + 단일 baseline 추정
      architecture-selector.md                           # Phase 1 — 선택 규칙(architecture-task alignment·45% capability ceiling) → single/multi + 토폴로지
      coordination-designer.md                           # Phase 2 — communication/commitment/expectation 가드 + context-pollution 격리
      orchestration-verifier.md                          # Phase 3 — baseline 능가 적대 검증, 병렬화 금지면 단일 권고(REJECT)
    skills/
      agent-orchestration/                               # 진입점 오케스트레이터 (Phase 0 게이트 → 결정 → 설계 → 검증)
        SKILL.md
        references/
          agent-orchestration-principles.md              #   선택 규칙·토폴로지·협업 가드·anti-pattern·결정 신호표
          agent-orchestration-research.md                #   설계 근거 dossier (출처·인용·vote·CAVEAT·반박된 주장; arXiv:2512.08296·2601.13295·2604.07911)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  eval-harness/                                          # [독립 플러그인] AI 생성물(코드·에이전트 출력)을 엄밀 평가하는 하네스 (정의·validity→judge 구성→validity 감사→실행·집계 4단계). 경계: 컨텍스트 조립·병렬화 판단·구현 명세·일반 실행 테스트 생성·커밋/PR 리뷰 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 논문
    agents/                                              # 모두 model: "opus"
      eval-designer.md                                   # Phase 0 — 평가 대상·관찰형 성공기준 + task/outcome validity 명세 + 귀인 단위
      judge-builder.md                                   # Phase 1 — judge 구성(다중 표본 ≥3·다관점 분해·실행 grounding), single-shot 금지
      validity-auditor.md                                # Phase 2 — ABC 감사(validity·shortcut·harness≠model 귀인·instruction density), BLOCK 게이트
      eval-runner.md                                     # Phase 3 — 다중 표본 실행·집계 + confidence + CAVEAT 보고
    skills/
      eval-harness/                                      # 진입점 오케스트레이터 (Define → Build Judge → Audit → Run & Report)
        SKILL.md
        references/
          eval-harness-principles.md                     #   네 신뢰 축·judge/validity 설계지침·anti-pattern·경계
          eval-harness-research.md                       #   설계 근거 dossier (출처·인용·vote·CAVEAT·반박된 주장; arXiv:2507.02825·2412.12509·2502.12468·2507.11538·2606.17799)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 19, 인접 도메인 reciprocal 가드)
  spec-driven-development/                               # [독립 플러그인] 엔지니어용 실행 가능 명세(spec=source of truth)를 작성하고 에이전트가 명세대로 코드 생성→자기검증하게 하는 하네스 (명세작성→인수설계→구현→검증 4단계). 경계: 기획자 PRD·AI 출력 평가·컨텍스트 조립·완성 코드 리뷰·하네스 진단 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 논문
    agents/                                              # 모두 model: "opus"
      spec-author.md                                     # Phase 0 — 실행 가능 명세 작성(source of truth; 구조화 contract)
      acceptance-designer.md                             # Phase 1 — 인수기준 + 테스트 계획 + 자기검증 체크 설계(자족, 외부 의존 금지)
      spec-implementer.md                                # Phase 2 — 명세대로 코드 생성(또는 구현 가이드) + 추적성
      spec-verifier.md                                   # Phase 3 — 명세 부합 조항별 검증 + comprehension 게이트(comprehension debt 방지)
    skills/
      spec-driven-development/                           # 진입점 오케스트레이터 (Phase 0 명세 승인 게이트 → 4단계 플로우)
        SKILL.md
        references/
          spec-driven-development-principles.md          #   명세 우선 원리·spec 구성요소·anti-pattern·comprehension 게이트 설계
          spec-driven-development-research.md            #   설계 근거 dossier (출처·인용·vote·CAVEAT·반박된 주장; arXiv:2602.00180 + Osmani 2026-01)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  ai-readable-codebase/                                 # [독립 플러그인] 코드베이스의 구조적 AI 접근성(A축≠Q축)을 진단·개선하는 하네스 (진단(2축·L1~L5 증거기반)→빌드 가드레일→standalone 독립 실행→수용 증명·재측정 4단계). 경계: 한 기능 구현·검증(backend)·상류 핸드오프 검수(review)·하네스 진단(meta)·전달 파이프라인(cicd)·실행 명세(spec)·컨텍스트 조립(context)·완성 코드 리뷰(frontend/git) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·L1~L5 등급·근거 자료
    agents/                                              # 모두 model: "opus"
      accessibility-assessor.md                          # Phase 0 Assess — 2축(Q/A) 진단 + L1~L5 등급(증거 기반, 자기보고 불신) + A축 격차·백로그
      guardrail-architect.md                             # Phase 1 Guardrails — 빌드가 강제·문서가 설명(의존 방향 물리 강제 + 피드백 3차원 + 역할 분담)
      standalone-designer.md                             # Phase 2 Standalone — 도메인 슬라이스 독립 실행(port/adapter 치환·use-case seed·명시적 제외)
      acceptance-verifier.md                             # Phase 3 Acceptance & Re-grade — 수용 증명 인프라(+한계 명시) + 등급 적대 재측정(reward-hacking 가드·generator/checker 분리)
    skills/
      ai-readable-codebase/                              # 진입점 오케스트레이터 (Phase 0 진단 승인 게이트 → 4단계, 제안만·사람 집행)
        SKILL.md
        references/
          ai-readable-codebase-principles.md             #   2축·L1~L5·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern·경계
          ai-readable-codebase-research.md               #   설계 근거 dossier (flex 5부작 + 2025+ 출처·인용·vote·CAVEAT; CodeScene 9.4/5.15 미입증 투명성 §D)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 15, 인접 도메인 reciprocal 가드)
  human-agent-teaming/                                  # [독립 플러그인] 사람과 AI 에이전트가 한 팀으로 협업하도록 분업·공통기반·감독/신뢰·검증을 설계하는 하네스 (분업·위임→공통기반→모니터링 기반 감독·신뢰 보정→비례 검증·핸드오프·책임 4단계). 축은 AI↔AI 토폴로지가 아니라 사람↔에이전트 분업·감독. 경계: 여러 AI 에이전트 병렬화·토폴로지(agent-orchestration)·컨텍스트 페이로드 조립(context)·AI 출력 평가(eval)·단일 자율 반복(loop)·상류 핸드오프 검수(review)·하네스 진단(meta)·PRD(product-spec)·커밋/PR(git) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 자료
    agents/                                              # 모두 model: "opus"
      delegation-designer.md                             # Phase 0 Charter & Delegate — 분업(사람=전략·하드 트레이드오프·최종 검증·책임 / 에이전트=전문 실행)·위임(human/agent/co-delegation·trustworthy region)·자율 수준·운영 모드(HITL/HOTL)·고위험 결정점·역할 경계
      common-ground-builder.md                           # Phase 1 Establish Common Ground — 온보딩 브리핑(적혀 있지 않으면 존재하지 않음)·AI 오류 경계 노출·workspace awareness·재정렬 루프(SMM 영속)·working agreement
      oversight-designer.md                              # Phase 2 Calibrate Oversight & Trust — 모니터링 기반 감독(전수 승인 아님)·단계적 가역 권한·개입/스티어링·적절한 의존 신뢰 보정·실패모드(over-reach)/자동화 편향 가드
      verification-designer.md                           # Phase 3 Verify & Sustain — 비례 검증(코드=테스트·그 외=루브릭·Doer-Verifier fresh-context)·검증 스캐폴딩·대칭 전문성 대응·핸드오프 연속성·후속 재정렬(AAR)·책임(moral crumple zone 금지)
    skills/
      human-agent-teaming/                               # 진입점 오케스트레이터 (Phase 0 분업 승인 게이트 → 공통기반 → 감독 → 검증, 협업 설계 산출·실행 안 함)
        SKILL.md
        references/
          human-agent-teaming-principles.md              #   분업 규칙·감독 설계·검증 운영·anti-pattern·결정 신호표·경계
          human-agent-teaming-research.md                #   설계 근거 dossier (Anthropic HAT 블로그 + 1차 자료 + arXiv:2504.10918·2602.05987·출처·인용·vote·CAVEAT; 벤더=설계 의도·반박된 패턴(자기제한)·METR RCT 반례)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 12, 인접 도메인 reciprocal 가드)
  code-as-harness/                                      # [독립 플러그인] 코드를 실행 가능·검사 가능·상태 보존(operational substrate)으로 다루고 거버넌스된 Plan→Execute→Verify 제어 루프로 코드 변경을 안전·검증 가능하게 수행하는 하네스 (계획 계약→권한·샌드박스 실행→실행 검증→텔레메트리 진단·수렴 4단계). 단일 거버넌스 사이클이지 통과까지 자율 반복(loop)이 아님. 경계: 통과까지 자율 반복+학습 메모리(loop)·백엔드 환경 provisioning 구현(backend)·실행 명세 작성(spec)·AI 에이전트 병렬화(agent-orchestration)·컨텍스트 조립(context)·AI 출력 평가(eval)·하네스 진단(meta)·상류 핸드오프 검수(review)·장애 대응(ops)·PRD(product-spec)·커밋/PR(git) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 논문
    agents/                                              # 모두 model: "opus"
      plan-contractor.md                                 # Phase 0 Plan Contract — 작업 → 변경 계약(의도한 변경·결정적 센서·행동 위험 분류)
      permissioned-executor.md                           # Phase 1 Permissioned Execute — 권한·샌드박스 실행·가역 우선·안전임계 사람 게이트·구조화 실행 trace 적재
      execution-verifier.md                              # Phase 2 Execution Verify — 결정적 센서 실제 실행·조항별 PASS/FAIL/UNVERIFIED·reward-hacking·불완전 피드백·최종 너머 가드(검증 전용)
      telemetry-diagnostician.md                         # Phase 3 Telemetry Diagnose & Converge — trace 인용 진단·regression-free 수정안·무진전 ESCALATE·CONVERGED/ITERATE/ESCALATE(진단·제안만)
    skills/
      code-as-harness/                                   # 진입점 오케스트레이터 (Phase 0 계획 계약 승인 게이트 → 실행 → 검증 → 진단·수렴)
        SKILL.md
        references/
          code-as-harness-principles.md                  #   원칙·anti-pattern·결정 신호표
          code-as-harness-research.md                    #   설계 근거 dossier (출처·인용·vote·CAVEAT·반박된 주장; arXiv:2605.18747 + 인접 2604.08224·2506.11442·2604.20801·2508.00083·2512.14012 + 보강 2604.15149·2603.07084)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  llm-guardrails-harness/                               # [독립 플러그인] LLM/에이전트 앱에 런타임 외부 가드레일(input/output/retrieval/execution 레일)을 설계·강제하는 하네스 (위협모델·정책→입력 레일→출력·검색 레일→행동 강제·적대검증 4단계). 경계: 오프라인 출력 평가(eval)·장애 RCA(ops)·상류 핸드오프(review)·아이덴티티/인가 설계(agent-authorization) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 자료
    agents/                                              # 모두 model: "opus"
      threat-modeler.md                                  # Phase 0 — 앱→OWASP LLM Top 10 매핑·fail-closed 정책·레일 배치 결정
      input-rail-engineer.md                             # Phase 1 — 모델 호출 전 jailbreak/injection 탐지·Llama-Guard 분류·요청 거부/재작성
      output-rail-engineer.md                            # Phase 2 — PII 리댁션·독성/정책 필터·grounding·untrusted 검색 청크 필터링
      enforcement-redteamer.md                           # Phase 3 — 최소 권한 tool 스코핑·비가역 행동 사람 게이트·red-team(ASR/FPR)
    skills/
      llm-guardrails-harness/                            # 진입점 오케스트레이터 (Phase 0 정책 승인 게이트 → 입력 → 출력/검색 → 행동/검증)
        SKILL.md
        references/
          llm-guardrails-harness-principles.md           #   원칙·anti-pattern·결정 신호표
          llm-guardrails-harness-research.md             #   설계 근거 dossier (OWASP LLM Top 10 2025·NeMo Guardrails·Llama Guard(arXiv:2312.06674)·SoK Jailbreak(arXiv:2506.10597)·등급·CAVEAT)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  qa-agent-harness/                                     # [독립 플러그인] 리스크 기반 전략→오라클 명시 시나리오→오라클 우선 생성·게이트된 자가치유 실행→결함 vs 플래키 지능형 트리아지의 독립 end-to-end 에이전틱 QA 하네스 (4단계). 경계: FE 한정 QA(frontend)·단일 test-generator(backend)·오프라인 judge(eval)·장애 RCA(ops)·상류 핸드오프(review)·자율 반복(loop)·LLM 가드레일(llm-guardrails) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 자료
    agents/                                              # 모두 model: "opus"
      test-architect.md                                  # Phase 0 — 요구사항·변경·리스크 → 리스크 노출 등급·커버리지 우선순위 전략
      scenario-designer.md                               # Phase 1 — 스토리/API → 리스크 매핑 시나리오 + 명시적 오라클(살아있는 라이브러리)
      test-engineer.md                                   # Phase 2 — 오라클 우선 생성·실행·로케이터/DOM 드리프트 점수화·로깅된 자가치유
      failure-triager.md                                 # Phase 3 — 결함/플래키/환경 분류·공유 근본원인 클러스터링·변경 기반 재실행 우선순위
    skills/
      qa-agent-harness/                                  # 진입점 오케스트레이터 (Phase 0 전략 승인 게이트 → 시나리오 → 실행 → 트리아지)
        SKILL.md
        references/
          qa-agent-harness-principles.md                 #   원칙·anti-pattern·결정 신호표
          qa-agent-harness-research.md                   #   설계 근거 dossier (arXiv:2601.02454·2506.02943 CANDOR·2606.18168·2504.16777·등급·제외 범위·CAVEAT)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  agent-authorization-harness/                          # [독립 플러그인] 에이전트/MCP 도구/A2A 시스템의 머신 아이덴티티·인가를 벤더 무관하게 설계·red-team하는 하네스 (신뢰·스코프 모델링→그랜트·위임 설계→동의·집행→적대 인가 검증 4단계, 설계+red-team 산출물이지 IdP 배포 아님). 경계: 런타임 콘텐츠·행동 레일(llm-guardrails, LLM06 공유 이음매)·사람↔에이전트 분업(human-agent-teaming)·파이프라인 policy-as-code(cicd)·코딩 에이전트 권한(code-as-harness) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + Phase 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·근거 자료
    agents/                                              # 모두 model: "opus"
      trust-scope-modeler.md                             # Phase 0 — 참여자·authN vs authZ authority·접촉면 인벤토리·최소 스코프·신뢰 경계
      grant-delegation-designer.md                       # Phase 1 — 단명 audience-bound 토큰(RFC 8707)·토큰 교환 위임(RFC 8693 may_act)·no passthrough
      consent-enforcement-designer.md                    # Phase 2 — 인증/인가 분리·deny-by-default·동의 게이트·end-to-end audience 검증·감사 로깅
      authorization-redteamer.md                         # Phase 3 — confused-deputy·토큰재생·스코프크리프·무제한위임 적대 검증·위협 분석
    skills/
      agent-authorization-harness/                       # 진입점 오케스트레이터 (Phase 0 모델링 게이트 → 그랜트·위임 → 집행 → red-team)
        SKILL.md
        references/
          agent-authorization-harness-principles.md      #   원칙·anti-pattern·결정 신호표
          agent-authorization-harness-research.md        #   설계 근거 dossier (RFC 8707·8693·OWASP LLM06=HIGH / ID-JAG·MCP auth·A2A draft=MEDIUM, 등급·CAVEAT·정직성)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 도메인 reciprocal 가드)
  ai-readiness-cartography/                             # [독립 플러그인] 임의 git 저장소가 'AI 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스'인지를 결정론적 스코어러로 정량 측정·시각화하는 단일 스킬 (100점·9카테고리 + 2 blocking gate(gating 집계) → JSON 점수표+HTML 대시보드+ROI 리팩토링 가이드). 에이전트 팀 없음. ai-readable-codebase(정성 진단→개선)와 상보(측정 vs 개선 설계). 외부 스킬 v2를 deep-research 5세션 적대 검증으로 v3 리팩토링
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 루브릭 v3 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·경계·근거(ai-readable-codebase 비교표)
    skills/
      ai-readiness-cartography/                          # 진입점 오케스트레이터 (score.py 실행 → 대시보드 채우기 → ROI 가이드)
        SKILL.md
        scripts/
          score.py                                       #   v3 결정론적 스코어러 (stdlib only, gating·import 그래프 파싱·결합도 god-file·reference integrity)
        assets/
          template.html                                  #   대시보드 원본 (Inter/JetBrains Mono·인라인 SVG·gate strip·9카테고리 차트)
        references/
          scoring-rubric.md                              #   v3 루브릭 (9카테고리 + 2 gate, 근거 등급·auto/heuristic/manual 라벨)
          ai-readiness-cartography-research.md           #   근거 dossier 인덱스 (루브릭→근거 매핑·정직성 노트)
          research/                                      #   2025~2026 1차 근거 (deep-research 5세션 적대 검증)
            README.md                                    #     합성 (헤드라인 반전 7개 + 리팩토링 결정 R1~R12)
            session-1-comprehension-metrics.md           #     ORACLE-SWE(2604.07789)·Nemotron-CORTEXA — 실행 신호 최상위
            session-2-context-engineering.md             #     ETH Zurich AGENTS.md(2602.11988)·Context Rot·Lost-in-the-Middle
            session-3-grounding-hallucination.md         #     USENIX slopsquatting(2025)·Ashik(2604.09515) — E1 gate·stale drift
            session-4-repo-structure.md                  #     LocAgent(2503.09089)·RepoMirage(2605.26177) — 의존 그래프·결합도 god-file
            session-5-benchmark-operationalization.md    #     Factory/Kenogami readiness — gating 집계·H/I 신규
    evals/
      evals.json                                         # 수용 평가 (v3 불변식 file:section·score.py 함수 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 6 / should_not 8, ai-readable-codebase reciprocal 가드)
```
