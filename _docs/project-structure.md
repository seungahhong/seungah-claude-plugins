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
    hooks/                                               # 플러그인 훅 디렉토리 (PreToolUse·PostToolUse·Stop)
      hooks.json                                         # 훅 설정 (가드 2종 + 스킬 중복 방지 + 린트 + 의존성 알림)
      lib.sh                                             # 공용 stdin JSON 파서 (jq→python3 폴백, 부재 시 경고 후 통과)
      guard.sh                                           # PreToolUse(Bash) 위험 명령 차단 (advisory)
      write-guard.sh                                     # PreToolUse(Write) 민감 파일 생성 차단
      skill-dedup.sh                                     # PreToolUse(Write) SKILL.md 중복 생성 차단
      incremental-lint.sh                                # PostToolUse(Edit|Write) 방금 수정된 파일 1개만 lint (--fix 후 잔여 에러 exit 2 전파)
      stop-lint.sh                                       # Stop 전용(전체 diff) lint 체인 (best-effort 비차단)
      package-changed.sh                                 # PostToolUse package.json 의존성 변경 알림
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 13 / should_not 16, 자매 하네스(review-harness) reciprocal 가드 포함)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 22, 인접 하네스(meta/harness-generator/product-spec/code-as-harness) reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 14 / should_not 18, 자매 하네스(frontend/product-spec/git/meta) reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 13, 인접 하네스 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 18, 인접 하네스 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 11 / should_not 15, 인접 하네스 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 16, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 15, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 22, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 16, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10 / should_not 13, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 16, 인접 도메인 reciprocal 가드)
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
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 15, 인접 도메인 reciprocal 가드)
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
  ai-readiness-cartography/                             # [독립 플러그인] 임의 git 저장소가 'AI 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스'인지를 측정하고(결정론 스코어러) 개선을 설계하며 코드 본문을 승인 후 수정하는(멀티 에이전트) 단일 스킬(3모드·자유 조합). ① 측정: score.py 100점·9카테고리 + 3 blocking gate(Gate-1/2 Auto·Gate-3 Heuristic·gating) → JSON+HTML 대시보드+ROI. ② 진단·개선: score.py 센서 위 2축 진단→빌드 가드레일→standalone→계획·개별 승인 뒤 코드 적용(S/M/L·고위험 opt-in·AST/LSP·behavior 센서)→수용 증명·재측정 4에이전트. ③ 코드 본문 층위: legibility_scan.py census→주석·명명·granularity 진단→3게이트 승인 후 코드 수정 4에이전트. 세 모드는 배타 아닌 자유 조합(여러 개면 ①→②→③ 순·score.py는 ①②가 1회 공유·②+③이면 구조 리팩터는 ②가 적용하고 ③의 C3는 끔). 등급 단일 5밴드(L1~L5 폐기, enforcement는 Gate-3로 흡수). 별도 ai-readable-codebase(v0.2.0)·code-legibility-harness(v0.3.0) 흡수·모드 게이트 자유 조합 전환(v0.3.1)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 루브릭 요약(3 gate) + 변경 이력
    README.md                                            # 사용자용 개요·사용법·경계·근거(3모드·자유 조합)
    agents/                                              # 8 에이전트 (② 개선 4 + ③ 본문 4, 모두 model: "opus")
      accessibility-assessor.md                          # Phase 0 Assess — score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정
      guardrail-architect.md                             # Phase 1 Guardrails — 빌드가 강제·문서가 설명(의존 방향 물리 강제 + 피드백 3차원 + 역할 분담)
      standalone-designer.md                             # Phase 2 Standalone — 도메인 슬라이스 독립 실행(port/adapter 치환·use-case seed·명시적 제외)
      acceptance-verifier.md                             # Phase 4 Acceptance & Re-grade — 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 재측정
      comment-auditor.md                                 # ③ 본문 — 주석 4분류(오도/stale/noise/유효) → C0·C1 후보
      naming-analyst.md                                  # ③ 본문 — 명명 3축(오도>무의미>모호) → C2 후보 + 도구·위험 판정
      structure-cartographer.md                          # ③ 본문 — 구조 후보(opt-in·'효과=추론' 라벨 필수)
      behavior-guard.md                                  # ③ 본문 — 개입 클래스별 센서 실행·관측 (generator≠checker)
    skills/
      ai-readiness-cartography/                          # 진입점 오케스트레이터 (모드 선택=①②③ 부분집합 → ①→②→③ 순차; ② 5-Phase(0~4·Phase 3 Apply 게이트)·③ 5-Phase B0~B4·3게이트)
        SKILL.md
        scripts/
          score.py                                       #   v3 결정론적 스코어러 (stdlib only, gating·import 그래프 파싱·결합도 god-file·reference integrity, htmlsafe.json 동시 출력)
          test_score.py                                  #   회귀 테스트 (unittest — 가중치 불변식·골든 픽스처·Gate-1 정밀도·htmlsafe·design_signals report-only 불변)
          legibility_scan.py                             #   ③ 본문 census 스캐너 (stdlib only·등급 없음·7 탐지기: N1~N4 명명·C1~C6 주석·unit_sizes 구조)
          test_legibility_scan.py                        #   ③ 회귀 테스트 (49건·등급 안 만듦·stdlib-only·스코프 이스케이프 핀)
        assets/
          template.html                                  #   대시보드 원본 (Inter/JetBrains Mono·인라인 SVG·gate strip·9카테고리 차트)
        references/
          scoring-rubric.md                              #   v3 루브릭 (9카테고리 + 3 gate: Gate-1/2 Auto·Gate-3 Heuristic, 근거 등급·auto/heuristic/manual 라벨)
          ai-readable-codebase-principles.md             #   진단·개선 모드 원리 (2축·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern)
          intervention-catalog.md                        #   ③ 개입 카드 C0~C3 정본 (근거·위험·1급 센서·거부 조건)
          legibility-principles.md                       #   ③ 본문 층위 원리 (삭제>추가·이름은 채널·테스트≠등가성 오라클)
          ai-readable-codebase-research.md               #   개선 모드 근거 dossier (flex 5부작 + 2025+ 출처·인용·vote·CAVEAT)
          ai-readiness-cartography-research.md           #   측정 근거 dossier 인덱스 (루브릭→근거 매핑·정직성 노트)
          research/                                      #   2025~2026 1차 근거 (deep-research 5세션 적대 검증)
            README.md                                    #     합성 (헤드라인 반전 7개 + 리팩토링 결정 R1~R12)
            session-1-comprehension-metrics.md           #     ORACLE-SWE(2604.07789)·Nemotron-CORTEXA — 실행 신호 최상위
            session-2-context-engineering.md             #     ETH Zurich AGENTS.md(2602.11988)·Context Rot·Lost-in-the-Middle
            session-3-grounding-hallucination.md         #     USENIX slopsquatting(2025)·Ashik(2604.09515) — E1 gate·stale drift
            session-4-repo-structure.md                  #     LocAgent(2503.09089)·RepoMirage(2605.26177) — 의존 그래프·결합도 god-file
            session-5-benchmark-operationalization.md    #     Factory/Kenogami readiness — gating 집계·H/I 신규
            session-6-design-principles.md               #     SOLID·응집/결합·복잡도·중복 → 왜 report-only이고 점수화 아닌가(extras.design_signals)
            session-7-body-legibility-integration.md     #     코드 본문 층위 모드 ③ 흡수 — scorable 아닌 report-only·명명 인과·툴그래프 오귀속 금지
            body-legibility/                             #     ③ 근거 dossier (naming·comments·structure·safe-application·measurement-delta·README, 적대 검증 24 confirmed/1 refuted)
    evals/
      evals.json                                         # 수용 평가 (3모드 불변식 file:section·score.py 함수 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (측정+개선+본문+조합 should_trigger 19 / 인접 도메인 should_not 14)
  token-efficiency/                                    # [독립 플러그인] Claude Code 세션 JSONL 로그를 파싱해 레포 단위 토큰/컨텍스트 효율을 결정론적으로 측정·시각화하고 $ 절감안을 내는 단일 스킬 (4축 가중 점수 + 8개 비효율 탐지기 + 세션별 모델가 낭비 추정 → JSON 2종 + 오프라인/CSP 안전 HTML 대시보드). 에이전트 팀 없음. ai-readiness-cartography(정적 저장소 구조)와 상보(런타임 세션 로그 vs 정적 구조). 외부 스킬 improve-token-efficiency를 deep-research 5세션 적대 검증으로 개선
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 4축/8탐지기 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·개선표·경계
    skills/
      token-efficiency/                                  # 진입점 오케스트레이터 (analyze → detect → dashboard)
        SKILL.md
        scripts/
          analyze_sessions.py                            #   4축 가중 점수(메인 스레드) + message.id당 usage 1회 계상 + 서브에이전트 별도파일(subagents/**/*.jsonl) 재귀 수집(비용 분리 subagent_cost_usd) + 현행 PRICING(날짜접미사 정규화·입력가 파생 캐시배수)·--pricing/--weights·효율≠cost-of-pass 경고
          detect_patterns.py                             #   8개 탐지기 (5 기존 + 3 신규 stale/churn/read), 세션별 dominant 모델가 낭비 산정
          build_dashboard.py                             #   오프라인/CSP 안전 인라인-SVG HTML (패턴 병합·세션별 라우팅·캐시-깨짐 caveat)
          test_efficiency.py                             #   회귀 테스트 (unittest 61건 — 가중치 합·양방향 가격 동기화·탐지기·사이드체인 배제·golden 점수·경로 인코딩)
        references/
          research/                                      #   2025~2026 1차 근거 (deep-research 5세션 적대 검증)
            README.md                                    #     합성 (헤드라인 반전 7개 + 개선 결정 C1~C12)
            session-1-context-engineering.md             #     ACON(2510.00615)·Squeez(2604.04979)·Complexity Trap(2508.21433) — 압축·프루닝·folding
            session-2-prompt-caching-economics.md        #     Anthropic 캐싱 1차 — exact-prefix·배수·최소 프리픽스·현행 가격
            session-3-trajectory-redundancy.md           #     AgentDiet(2509.23586)·읽기 76.1%(2606.14066)·SWE-Pruner(2601.16746)
            session-4-cost-aware-routing.md              #     cost-of-pass(2508.02694) — 작업 의존 라우팅·캐스케이드 구조비용
            session-5-cost-of-pass-budgets.md            #     cost-of-pass 정의·frontier 반감·효율≠성공률 정직성
    evals/
      evals.json                                         # 수용 평가 (불변식 file:함수 인용 + test_efficiency 실행 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 6 / should_not 7, 인접 도메인 reciprocal 가드)
  test-layering-harness/                                # [독립 플러그인] 인수조건(AC, Given-When-Then)을 방법론(Smoke/Sanity/Regression/nightly)×계층(Unit/Integration/E2E) 택소노미로 분해·CI 단계 배치해 계획하고, 계획→개별→최종 3단계 인간 승인 게이트로 테스트를 하나씩 순차 생성·적용·확정하는 도메인 무관 인터랙티브 단일 스킬. 초기 문의 AC·개발환경 각각 스킵 가능(환경 미입력 시 현재 경로), 적응형 3 프리셋 추천(비율% 미하드코딩), 오라클 강도 최대 리스크 가드(기대 기준 오검증·실행 그라운딩·flaky baseline). 경계: 자가치유 QA(qa-agent)·백엔드 test-generator(backend)·AC↔테스트 커버리지 읽기전용 검수(review/test-coverage-review)·FE TDD(frontend)·실행 명세(spec-driven)·커밋(git) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 5-Phase·3-Gate 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·정직성 원칙·경계
    skills/
      test-layering-harness/                             # 진입점 오케스트레이터 (Phase 0 초기문의 → 1 적응형 구성+조합 강도 lookup → 2 축 카드 조합 라우팅 계획(스코프 가드)+게이트A → 3 개별 적용+게이트B → 4 반영+게이트C, 단일 스킬·에이전트 팀 없음)
        SKILL.md
        references/
          test-layering-principles.md                    #   방법론×계층 매트릭스·AC 분해(§4)·축 카드 조합 라우팅(§4.5, 스코프 가드)·오라클 가드·실체화(§3.5)·3 프리셋·감지 신호·anti-pattern·경계
          matrix/                                        #   방법론·계층 축 카드 7개 (12개 셀로 미리 물질화하지 않고 라우팅 시 조합)
            _index.md                                    #     축 직교성·스코프 가드(선택 안에서만 추가)·조합 라우팅 절차·조합 강도 lookup(STRONG/WEAK/DEGENERATE)·정직성 불변식
            methodology-{smoke,sanity,regression,nightly}.md  # 방법론 카드 4개 (suite 멤버십·실체화·CI배치·오라클 기대·조합 강도)
            layer-{unit,integration,e2e}.md              #     계층 카드 3개 (scope+size/hermeticity 판정·AC 포함/제외·오라클 프로필·조합 강도)
          research/
            test-strategy-research.md                    #     2025+ 상위 근거 dossier (A~G, 신뢰도·folklore·모순 표기, deep-research plain-text fan-out 적대 검증)
            matrix-criteria-2025.md                      #     조합 라우팅 기준 근거 dossier (직교성·계층/방법론 판정·조합 강도 lookup·정직성 원장·소스 인덱스; ISO/IEC/IEEE 29119-1:2022·ISTQB·SWE@Google·arXiv 2025+, 인용 교정)
    evals/
      evals.json                                         # 수용 평가 (핵심 불변식 file:section 인용 채점 — 3게이트·비율 미하드코딩·오라클 가드·경계)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 14, 인접 하네스(qa-agent/backend/review/frontend/spec/git) reciprocal 가드)
  methodology-advisor/                                   # [독립 플러그인] 팀의 현행 개발·회사·사업 프로세스를 먼저 진단하고, frontend-harness grill-me를 개발 방법론 선택에 특화·확장한 다각도 문진(3축) 뒤, 내장 방법론 카탈로그(14) + 컨틴전시 프레임워크(Cynefin·Stacey·Boehm-Turner home ground)에 근거해 순위 shortlist + 1순위를 제안하는 인터랙티브 4에이전트 하네스. 첫 행동=현행 진단(발명 금지)·매 Phase 승인 게이트·우열 금지·은탄환/'N% 개선' 금지·제안만. deep-research 24소스·75주장 적대 검증(70 confirmed/5 refuted)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 4 Phase 요약 + 원칙 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·방법론 목록·경계
    agents/
      process-cartographer.md                            # Phase 0 현행 진단(개발/회사/사업 3축·관측만·발명 금지)
      context-interviewer.md                             # Phase 1 grill-me 다각도 문진(3축·한 번에 한 질문·충돌 감지)
      methodology-matcher.md                             # Phase 2 방법론 매칭(shortlist + 1순위 + additive 로드맵·트레이드오프+안티패턴)
      fit-critic.md                                      # Phase 3 적대적 적합성 검증(은탄환·숨은 가정·안티패턴·정직성)
    skills/methodology-advisor/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~3 + 매 Phase 승인 게이트 + opt-in 저장)
      references/
        methodology-catalog.md                           # 14 방법론(원칙·의식·아티팩트·적합 조건·안티패턴)
        selection-frameworks.md                          # Cynefin·Stacey·Boehm-Turner home ground 5인자·risk-based 5단계·컨틴전시 축→방법론 매핑
        interview-axes.md                                # 개발/회사/사업 3축 질문뱅크·후속 깊이 패턴·충돌 감지 쌍
        research/README.md                               # 2024-2026 1차 조사(deep-research 24소스·75주장 → 70 confirmed/5 refuted, SOURCE-TIER, REFUTED 교정: DORA 90%·Boehm-Turner 5단계)
    evals/
      evals.json                                         # 수용 평가 (design-conformance + 근거 정직성 13 assertion)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 9, 인접 하네스(product-spec/harness-generator/meta/human-agent-teaming/agent-orchestration/cicd/ops/review/git) reciprocal 가드)
  design-principle-harness/                              # [독립 플러그인] 임의 git 저장소를 'AI 에이전트가 읽고 안전하게 기여할 코드베이스'로 만들기 위해 코드 설계 품질을 3단계(① scoring-rubric 점수화 → ② 쉬운 것부터 섹션별 승인 개선 → ③ 종합 결과)로 진단·개선하는 인터랙티브 4에이전트 하네스. score.py(stdlib only) 채점 — Tier A 표면 가독성 명명·주석 60 / Tier B 설계 원칙 SOLID·응집결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI 40 = 총점 100 + Tier C AI-맥락 신호(시맨틱 마크업 C1·테스트 설명 C2, report-only·총점 미포함). 총점=진단 지표(Goodhart 가드·개입 연구 없어 안전 기여 인증 아님)·명명/주석은 사람 근거+오도/stale 신호가 LLM에도 해로워 Tier A 가중↑(LLM 리네임 효과 부호 불안정)·구조 지표는 낮은 confidence 진단(타당도 외삽)·Tier C는 이득이 모델 역량 조건부이거나 개입 근거 부재라 report-only(ARIA 볼륨 가점 금지·자동 ARIA/alt/어서션 생성 금지)·리네임 AST/LSP·"테스트 통과≠동작 보존"·측정은 코드 수정 없음·개선은 승인 뒤·커밋 안 함. deep-research 2023~2026 적대 검증(v0.2.0 Tier C 추가)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 3단계 요약 + 원칙 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·두 층위·안전장치·경계
    agents/                                              # 4 에이전트 (모두 opus)
      code-scorer.md                                     # Step 1 score.py 실행·두 층위 점수표 해석(측정만)
      staged-refiner.md                                  # Step 2 쉬운 것부터 개선안 제안·개별 승인 후 적용(구조 opt-in)
      behavior-guard.md                                  # Step 2 generator≠checker·변경 클래스별 행위 센서 실행
      acceptance-reporter.md                             # Step 3 재측정 델타·종합 결과·표면 편집 오귀속 금지
    skills/design-principle-harness/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0 스코프 + Step 1~3 + 매 단계 승인 게이트)
      scripts/
        score.py                                         # 결정론 스코어러 (stdlib only, Python 3.10+, Tier A/B 총점 + Tier C report-only·confidence·개선 순서·하드닝)
        test_score.py                                    # 회귀 테스트 28건 (불변식·A~C 탐지기·Tier C 미합산 불변식·하드닝)
      references/
        scoring-rubric.md                                # 루브릭 정본 (Tier A/B 총점·Tier C report-only·배점·confidence·개선 순서·넣지 말 것)
        design-principles.md                             # SOLID·응집/결합·복잡도·중복·DI/IoC·DRY/KISS/YAGNI + Tier C(시맨틱 마크업·a11y·테스트 설명) 카탈로그·정적 측정 경계
        improvement-playbook.md                          # 쉬운 것부터 안전 개선 (메커니즘·불변식·Tier C opt-in 절·generator≠checker)
        research/                                         # 1차 근거 dossier (deep-research)
          evidence-dossier.md                            #   명명·구조 근거(2023~2026 적대 검증)
          rubric-design.md                               #   두 층위 루브릭 설계
          semantic-a11y-test-dossier.md                  #   Tier C 근거(시맨틱 HTML·ARIA/WCAG·테스트 설명, 5렌즈·적대 감사·인용 교정)
          semantic-a11y-test-raw-findings.md             #   Tier C 원자료(10 조사/검증 에이전트 원문)
          README.md                                      #   research/ 인덱스·방법론·정직성
    evals/
      evals.json                                         # 수용 평가 (design-conformance + 근거 정직성 14 assertion)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 10(+Tier C 2) / should_not 8, 인접 도메인 reciprocal 가드)
```
