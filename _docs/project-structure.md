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
  git-harness/                                           # [독립 플러그인] 커밋·push·PR 생성·PR 리뷰 단일 파이프라인 (진입점 선택 = 이후 단계 승인)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 구조·규약 + 변경 이력
    README.md                                            # 사용자용 개요
    skills/
      commit-pr/                                         # §0 상태 파악·진입점(commit/push/pr)·모드별 전제조건 → §9 리뷰 레인+커밋 차단 게이트 → §1~§5 커밋 → §6 push → §7 PR 생성 → §8 PR 리뷰
        references/
          commit-message.md                              # §1~§4 커밋 메시지 사양 (`이슈번호 type: 제목`, 본문 판단 프로세스, Validation)
          review-lane.md                                 # §9 code-simplifier·코드리뷰 서브에이전트 + severity 3등급 환산표
          pr-creation.md                                 # §7 타겟 추천·검증, 변경 분석, PR 제목·본문 포맷
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
  product-spec-harness/                                  # [독립 플러그인] 기획자(PM)용 기획문서(PRD)+사용자 스토리+인수조건 7단계 인터랙티브 하네스 + 기획 완성도 점검(DoR)·PRD 확정 루프(계획→설계→비평)(모두 내재화·외부 의존 없음, 단독 동작) — 개발 착수 전, 도메인 무관 (산출물은 .claude/_docs/<기획서 슬러그>/에 저장) (입력 모드 R 재갱신 재진입/A 기획안/B 인터뷰 — R을 A·B보다 먼저 판별; 생성 전 기획안 보완 문답(하나씩·건너뛰기)과 생성 후 재갱신 경로 포함; 경계: 프론트엔드 화면 구현·기술 설계·코드/하네스/커밋·완성 산출물 핸드오프 게이트 검수 제외)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 7단계 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·도구 경계·입력 모드
    agents/                                              # 모두 model: "opus" (Phase 순차)
      requirements-analyst.md                            # Phase 0 요구/문제/사용자 정의 (Discovery) — 기획안 있으면 카드 추출, 없으면 인터뷰
      dor-evaluator.md                                   # Phase 1 원본 기획안의 기획 완성도 점검(DoR) (모드 A 진입질문 필수·생성 전 선행) — # 기획 완성도 점검 결과(DoR Review) + 보완할 점 점검표(보강 체크리스트) 채팅 제시, 보강점을 PRD·스토리에 반영 (저장 opt-in — 건너뜀 1건 이상이면 Phase 1 직후, 0건이면 마무리 · 보완 문답/재갱신은 오케스트레이터 소유)
      prd-planner.md                                     # Phase 2.1 계획 — PRD §1 배경·문제 / §2 목표·성공지표(관찰형) / §3 범위(In·Out) 소유. 범위 Out 강제·발명 금지·질문은 [확인필요]로 반환 (Phase 1 보강점 반영)
      prd-designer.md                                    # Phase 2.2 설계 — PRD §4 핵심 요구사항(FR·NFR) / §5 가정·리스크 / §6 마일스톤 소유. 기획 설계 D1~D12(기술 아키텍처·스토리 문장 산출 금지), §1~§3은 [계획 변경 요청]으로 반환
      prd-critic.md                                      # Phase 2.3 비평 — 확정 전 PRD 초안(§1~§6) 읽기 전용 비평. 렌즈 C-1~C-7·원문 인용 필수·차단 닫힌 4종·처리분류 A/B/C·쓰기 권한 0·확정 거부권 없음
      story-writer.md                                    # Phase 3 사용자 스토리 + INVEST 자가점검 + 요구 커버 표 ([인수조건 인계] 메모만, 조건·행동·결과 문장은 쓰지 않음 — 단일 원본)
      acceptance-writer.md                               # Phase 5 인수조건 작성 — 조건·행동·결과(Given-When-Then)·단일 관심사·흐름 커버리지 6종·AC↔US 추적 → acceptance-criteria.md (최종 산출물, 정책·수치 발명 금지)
      spec-reviewer.md                                   # Phase 4 1차(PRD↔스토리: 추적·INVEST·일관성·모호) / Phase 6 2차(스토리↔인수조건: 빠짐·고아·관찰성·단일 관심사·흐름 커버리지·누락 마이닝) 적대적 검증 (두 회차 모두 채팅 제시만 — 리포트 파일 없음)
    skills/
      product-spec/                                      # 진입점 오케스트레이터 (Phase 0~6 인터랙티브, 승인 게이트, 입력 모드 R/A/B(R을 먼저 판별), Phase 2는 계획→설계→비평 확정 루프(회차당 게이트 1개), Phase 5 인수조건·Phase 6 2차 검증. **Phase 1.1 기획안 보완 문답**(생성 전 필수 문의·미충족 항목 하나씩·매 질문 `건너뛰기`·건너뜀은 §9 기록) + **마무리 §1 재갱신 경로**(닫힌 4라벨·상류→하류·ID 동결·쌍 규칙 재검증·T1~T6 종료 조건). 산출 파일은 **재갱신 후에도** 정확히 4개(PRD/user-stories/acceptance-criteria/product-spec-review) — 검증 리포트는 채팅 제시만, 이력은 PRD 부록 A가 정본)
        SKILL.md                                         #   오케스트레이터 본문
        references/
          prd-template.md                                #   PRD 표준 구조 + 작성기준
          user-story-guide.md                            #   As a/I want/so that + 좋은 스토리 6가지 기준(INVEST) (인수조건 문장은 범위 밖)
          dor-review-rubric.md                           #   기획 완성도 점검(DoR) 루브릭 내재화 (# 기획 완성도 점검 결과(DoR Review)·보완할 점 점검표·Honesty Guardrail·2025+ 근거)
          prd-design-checklist.md                        #   기획 설계 점검표 D1~D12 + 기술 설계 금지 어휘 + 섹션 소유 경계 (Phase 2.2 설계 내재화)
          prd-critique-lenses.md                         #   PRD 비평 렌즈 C-1~C-7 + 차단 닫힌 4종 + 처리분류 A/B/C + 정체 가드 G1~G3 + 정직성 가드레일 (Phase 2.3 비평 내재화)
          acceptance-criteria-guide.md                   #   인수조건 작성 가이드 내재화 — 조건·행동·결과 형식·단일 관심사·흐름 커버리지 6종·판정 체크·스토리↔인수조건 추적·누락 마이닝 (Phase 5·6)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 21 / should_not 22, 자매 하네스(review-harness) reciprocal 가드 + 기술 아키텍처 설계·테스트 코드 작성 오발동 가드 포함)
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
  ai-readiness-cartography/                             # [독립 플러그인] git 저장소가 'AI 에이전트가 읽고 안전하게 기여할 수 있는 코드베이스'인지를 측정하고(결정론 스코어러) 승인 게이트 뒤에 개선을 적용하는(멀티 에이전트) 단일 스킬(3모드·자유 조합). ① 측정: score.py 100점·9카테고리 + 3 blocking gate(Gate-1/2 Auto·Gate-3 Heuristic·gating) → JSON+HTML 대시보드+ROI(코드 수정 없음). ② 진단·개선: score.py 센서 위 2축 진단→빌드 가드레일→standalone→계획·개별 승인 뒤 코드 적용(S/M/L·고위험 opt-in·AST/LSP·behavior 센서)→수용 증명·재측정 4에이전트. ③ 코드 본문: legibility_scan.py census→주석·명명·구조 진단→3게이트 승인 후 코드 수정 3에이전트 + 공용 behavior-guard(개입 C0~C3). 마크업 시맨틱·테스트 설명은 census 전용 축(개입 카드 없음 — 격리 근거 부재 O-6·접근성은 표적 아님·볼륨 가점 및 자동 ARIA/alt/어서션 생성 금지). 세 모드는 배타 아닌 자유 조합(여러 개면 ①→②→③ 순·score.py는 ①②가 1회 공유·②+③이면 구조 리팩터는 ②가 적용하고 ③의 C3는 끔). 등급 단일 5밴드(L1~L5 폐기, enforcement는 Gate-3로 흡수). 별도 ai-readable-codebase(v0.2.0)·code-legibility-harness(v0.3.0)·design-principle-harness 고유 자산(v0.5.0) 흡수 후 v0.6.0에서 군살 제거(C4/C5 개입 경로·markup-test-auditor·--git-drift 삭제·description 축약)
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 루브릭 요약(3 gate) + 변경 이력
    README.md                                            # 사용자용 개요·사용법·경계·근거(3모드·자유 조합)
    agents/                                              # 8 에이전트 (② 개선 4 + ③ 본문 3 + 공용 behavior-guard, 모두 model: "opus")
      accessibility-assessor.md                          # Phase 0 Assess — score.py seed 위 2축(Q/A) 진단 + 5밴드 등급 + Gate-3 예비판정
      guardrail-architect.md                             # Phase 1 Guardrails — 빌드가 강제·문서가 설명(의존 방향 물리 강제 + 피드백 3차원 + 역할 분담)
      standalone-designer.md                             # Phase 2 Standalone — 도메인 슬라이스 독립 실행(port/adapter 치환·use-case seed·명시적 제외)
      acceptance-verifier.md                             # Phase 4 Acceptance & Re-grade — 수용 증명 + 결정론 델타(score.py 재실행) 위 강제 probe로 Gate-3·등급 재측정
      comment-auditor.md                                 # ③ 본문 — 주석 4분류(오도/stale/noise/유효) → C0·C1 후보 + comment-gap(C7~C9) → '왜/맥락' 주석 opt-in 추가
      naming-analyst.md                                  # ③ 본문 — 명명 3축(오도>무의미>모호) → C2 후보 + 도구·위험 판정
      structure-cartographer.md                          # ③ 본문 — 구조 후보(opt-in·'효과=추론' 라벨 필수)
      behavior-guard.md                                  # ②③ 공용 — 개입 클래스별 센서 실행·관측 (generator≠checker·C0~C3·C3는 행위 센서·UNVERIFIED 상한)
    skills/
      ai-readiness-cartography/                          # 진입점 오케스트레이터 (모드 선택=①②③ 부분집합 → ①→②→③ 순차; ② 5-Phase(0~4·Phase 3 Apply 게이트)·③ 5-Phase B0~B4·3게이트)
        SKILL.md
        scripts/
          score.py                                       #   v3 결정론적 스코어러 (stdlib only, gating·import 그래프 파싱·결합도 god-file·reference integrity, htmlsafe.json 동시 출력)
          test_score.py                                  #   회귀 테스트 (unittest — 가중치 불변식·골든 픽스처·Gate-1 정밀도·htmlsafe·design_signals report-only 불변)
          legibility_scan.py                             #   ③ 본문 census 스캐너 (stdlib only·등급 없음·개입 축 3: N1~N4 명명·C1~C9 주석(+comment-gap)·unit_sizes 구조 / census 전용 축 2: MK1~MK4 마크업·TL1~TL2 테스트)
          test_legibility_scan.py                        #   ③ 회귀 테스트 (68건·등급 안 만듦·stdlib-only·스코프 이스케이프 핀·census 전용 축 불변식)
        assets/
          template.html                                  #   대시보드 원본 (Inter/JetBrains Mono·인라인 SVG·gate strip·9카테고리 차트)
        references/
          scoring-rubric.md                              #   v3 루브릭 (9카테고리 + 3 gate: Gate-1/2 Auto·Gate-3 Heuristic, 근거 등급·auto/heuristic/manual 라벨)
          ai-readable-codebase-principles.md             #   진단·개선 모드 원리 (2축·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern)
          intervention-catalog.md                        #   ③ 개입 카드 C0~C3 정본 (근거·위험·1급 센서·거부 조건·서열 + markup/tests는 census 전용 명시)
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
            body-legibility/                             #     ③ 근거 dossier (naming·comments·structure·safe-application·measurement-delta·semantic-markup-tests(E-MK/E-TL/E-CG)·README, 적대 검증 24 confirmed/1 refuted)
    evals/
      evals.json                                         # 수용 평가 (3모드 불변식 file:section·score.py 함수 인용 채점)
      trigger-eval.json                                  # 트리거 경계 평가 (측정+개선+본문+조합 should_trigger 20 / 인접 도메인·census 전용 축 개입 요청 should_not 18)
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
  test-layering-harness/                                # [독립 플러그인] 인수조건(AC, Given-When-Then)을 방법론(Smoke/Sanity/Regression/nightly)×계층(Unit/Integration/E2E) 택소노미로 분해·CI 단계 배치해 계획하고, 계획→개별→최종 3단계 인간 승인 게이트로 테스트를 하나씩 순차 생성·적용·확정하는 도메인 무관 인터랙티브 단일 스킬. 초기 문의 AC·개발환경 각각 스킵 가능(환경 미입력 시 현재 경로), 적응형 3 프리셋 추천(비율% 미하드코딩), 오라클 강도 최대 리스크 가드(기대 기준 오검증·실행 그라운딩·flaky baseline). **API 경계 축(mock/live)**: unit/integration=항상 mock(인터셉터 우선·fixture 3단 폴백·정적 live 검사), E2E=모드 태그(`@e2e-mock` 기본 / `@e2e-live` 수동 on-demand)·mock 통과≠연동 검증. **sanity=변경-스코프 선택 레인**(diff→역참조 페이지/컴포넌트→관련 `@e2e-mock`·PR job·unit/int blocking + E2E non-blocking). 경계: 자가치유 QA(qa-agent)·백엔드 test-generator(backend)·AC↔테스트 커버리지 읽기전용 검수(review/test-coverage-review)·FE TDD(frontend)·실행 명세(spec-driven)·커밋(git) 제외
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 하네스 포인터 + 5-Phase·3-Gate 요약 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·정직성 원칙·경계
    skills/
      test-layering-harness/                             # 진입점 오케스트레이터 (Phase 0 초기문의 → 1 적응형 구성+조합 강도 lookup → 2 축 카드 조합 라우팅 계획(스코프 가드)+게이트A → 3 개별 적용+게이트B → 4 반영+게이트C, 단일 스킬·에이전트 팀 없음)
        SKILL.md
        references/
          test-layering-principles.md                    #   방법론×계층 매트릭스·AC 분해(§4)·축 카드 조합 라우팅(§4.5, 스코프 가드)·오라클 가드(§5, fixture-as-oracle 금지 포함)·실체화(§3.5, sanity 선택 레인 §3.5.3)·**API 경계 축 mock/live(§3.6 단일 출처)**·3 프리셋·감지 신호·anti-pattern·경계
          matrix/                                        #   방법론·계층 축 카드 7개 (12개 셀로 미리 물질화하지 않고 라우팅 시 조합)
            _index.md                                    #     축 직교성·스코프 가드(선택 안에서만 추가)·조합 라우팅 절차(Step4-b API 경계)·조합 강도 lookup(§3 STRONG/WEAK/DEGENERATE)·**sanity 선택 레인(§3-b)**·**API 경계 축 요약(§3-c)**·정직성 불변식
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
  meta-prompting-harness/                                # [독립 플러그인] 메타 프롬프팅(AI에게 입력할 프롬프트를 AI가 최적화해 생성→새 컨텍스트에 주입해 실제 작업)을 4단계 인터랙티브 4에이전트로 수행하는 도메인 무관 하네스. 널리 쓰이는 메타 프롬프팅 실천 방법론 + /deep-research(6각도·25소스·23 confirmed/2 refuted) 1차 문헌 대조 근거 등급. Phase 0 인테이크(한 번에 한 질문씩·덤프는 선택) → 1 질문 유도(한 번에 하나씩) → 2 성공·검증 조건 → 3 환경 맞춤 깎아내기 → 4 적대 점검·fresh 주입. STRONG(메타프롬프팅>직접 2401.12954·2309.03409·2310.16427 조건부·명확화 질문 ClarifyGPT·Orchid·성공+검증 Anthropic 공식·fresh context 2307.03172·은탄환 아님)·report-only folklore(환경 맞춤 변환·큰그림→축소 1차 근거 없음)·REFUTED 미사용(지휘자-전문가 프레이밍·LLM 스스로 명확화 불가). 전부위임 금지·사용자 도메인 검증 필수·프롬프트 생성만·실행은 사용자·커밋/점수화 안 함·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 4 Phase 요약 + 근거 등급 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·근거 등급·경계·예시
    agents/                                              # 4 에이전트 (모두 opus)
      context-elicitor.md                                # Phase 1 질문 유도(빠진 요소 한 번에 하나씩 되묻기·번호 선택지·답변 분기·전부위임 방지)
      success-definer.md                                 # Phase 2 성공·검증 조건(외부 기준 대비·순진한 자기수정 아님)
      prompt-carver.md                                   # Phase 3 환경 맞춤 깎아내기(큰그림→축소·최종 프롬프트)
      prompt-critic.md                                   # Phase 4 적대 점검 + fresh context 주입 안내
    skills/meta-prompting/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~4·매 Phase 승인 게이트)
      references/
        execution-environments.md                        # 환경별 하드 제약·필수 변수·엔딩 조건(Goal/ultracode/Claude Code/이미지/리서치/채팅)
        carving-principles.md                            # 깎아내기 8원칙(각 근거 등급)
        evidence.md                                      # 기법별 학술 검증·등급·1차 소스(deep-research)
    evals/
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 8 / should_not 7, 인접 하네스 reciprocal 가드)
  org-transformation-harness/                            # [독립 플러그인] 회사/팀을 목적조직·AI native로 바꾸려는 실무자·리더를 인터뷰해 현행 진단→목표 구체화→간극·실행계획→적대 검증의 4단계 4에이전트로 "무엇부터 시작할지"를 단계별 할 일로 정리하는 도메인 무관 하네스. 시드 인터뷰 프롬프트를 메타 프롬프팅 기법으로 깎아내 승격 + /deep-research(6각도) 2023~2026 1차 문헌 대조 근거 등급. Phase 0 현행 조직 진단 → 1 목표 구체화 문진(임의 정의 금지) → 2 간극표+우선순위 할 일(영향·노력·의존성)+로드맵 → 3 적대 검증·공유 요약. STRONG조건부(AI native 은탄환 아님·DORA 2024/2025 PRIMARY 체감≠delivery 안정성·team 조건 좌우)·MEDIUM(현행 진단 우선·목적조직 Cagan/Team Topologies 컨센서스)·report-only(quick-wins/additive-first Kotter·RICE/WSJF folklore)·REFUTED 미인용("GenAI 95% 실패" 반박·DORA tier 비고정). 첫 행동=현행 진단·목표 임의 정의 금지·발명 금지·은탄환/'N% 개선' 금지·제안만·점수화/커밋 안 함·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 4 Phase 요약 + 원칙 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·산출물·정직성·경계
    agents/                                              # 4 에이전트 (모두 opus)
      org-cartographer.md                                # Phase 0 현행 조직 진단(관측·발명 금지·강점도 관측)
      vision-elicitor.md                                 # Phase 1 목표 구체화 문진(목적조직·일하는 방식·AI native·임의 정의 금지)
      gap-planner.md                                     # Phase 2 간극표+우선순위 할 일+로드맵(quick-wins·additive-first)
      plan-critic.md                                     # Phase 3 적대 검증 + 경영진/팀 공유용 요약
    skills/org-transformation/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~3·첫 행동=현행 진단·매 Phase 승인 게이트)
      references/
        interview-pillars.md                             # 4기둥 질문뱅크(현재/목표/간극·한 번에 한 질문·충돌 감지)
        transformation-frames.md                         # 목적조직·AI native·일하는 방식 정의 렌즈(트레이드오프·안티패턴·등급)
        prioritization.md                                # 영향·노력·의존성·quick-wins·additive-first·로드맵
        research/README.md                               # 2023-2026 1차 조사 dossier(등급·출처·REFUTED 교정, deep-research)
    evals/
      evals.json                                         # 수용 평가 (design-conformance + 근거 정직성 13 assertion)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 8 / should_not 9, 인접 하네스 reciprocal 가드)
  spec-to-figma-harness/                                 # [독립 플러그인] 유저스토리·인수조건(AC)을 입력으로 받아, FE가 되묻지 않고 개발할 수 있도록 "Figma에 무엇을 어떻게 반영해야 하는지"를 설계해 디자이너·FE 핸드오프 패키지로 내보내는 도메인 무관 4단계 4에이전트 하네스. 한 문장 원칙 = 기획서의 '시나리오'는 상태 프레임으로, '규칙'은 레이어 어노테이션으로. Phase 0 스펙 인테이크(한 번에 한 질문·스토리 없이 화면부터 설계 금지) → 1 AC 이분 분해 + 상태 카탈로그 6축 역방향 호명 → 2 명명·프레임 목록·flow·토큰 요구·Ready for dev·기존 파일 델타(읽기 전용) → 3 어노테이션 6분류 복붙 문안(확정=어노테이션/논의중=댓글) → 4 FE 1인칭 적대 검증·owner별 준비도·남은 질문. 정직성 5불변식: INV-1 발명 금지(문구·API 필드·이벤트명·수치 경계는 입력에 있는 것만·없으면 [기획 확인 필요]) · INV-2 커버리지≠품질(효과 약속·점수화 금지) · INV-3 디자인 결정 대행 금지(Figma 쓰기 MCP 도구 호출 금지·파일 생성/수정 안 함) · INV-4 플랜 제약 정직(Code Connect=Org/Ent+Dev/Full seat 등·대체 경로·'해당없음' 처리) · INV-5 되물음은 1급 산출물. 근거 GOLD=Figma 공식 문서(Annotations 선택형 속성·"CSS 자동 부착" 아님·Dev status 3종·Variables·MCP 읽기/쓰기 분리), [관행]=티켓 ID 명명·어노테이션 vs 댓글 분기(효과 수치 금지), 인용 금지=「AC 전수 매핑→질문 0」·「happy path가 재작업 유발」·「재작업 비용 68%」. 커밋 안 함·opt-in 저장·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 4 Phase 요약 + 5 불변식 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·산출물·정직성·경계
    agents/                                              # 4 에이전트 (모두 opus)
      state-cartographer.md                              # Phase 1 AC 이분 분해 + 상태 6축 역방향 호명 + 되물음(발명 금지)
      figma-blueprinter.md                               # Phase 2 구조·명명·프레임 목록·flow·토큰 요구·델타(읽기 전용·쓰기 도구 금지)
      annotation-writer.md                               # Phase 3 레이어별 6분류 핀 문안·확정/논의중 분리·Inspect 중복 금지
      handoff-critic.md                                  # Phase 4 FE 1인칭 적대 검증·상충 탐지·owner별 준비도 3값·정직성 감사
    skills/spec-to-figma/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~4·첫 행동=스토리·AC 확보·매 Phase 승인 게이트)
      references/
        ac-to-state-matrix.md                            # 이분 분류 결정 규칙·상태 카탈로그 6축·커버리지 매트릭스·되물음 규칙
        annotation-templates.md                          # 판별 기준·핀 표준 형식·6분류 템플릿·복붙 예시·기능 제약·안티패턴
        figma-blueprint.md                               # 구조 계층·권장/지양·프레임 목록 스키마·델타 진단 순서·flow·Inspect 신뢰성·플랜 제약
        handoff-readiness.md                             # 판정 규약(점수화 금지)·owner별 체크리스트·FE 1인칭 시뮬레이션·틈 유형·정직성 감사
        evidence.md                                      # 근거 정본(등급·GOLD 사실표·인용 금지 목록·유일 인용 가능 수치 4조건·재검증)
    evals/
      evals.json                                         # 수용 평가 (design-conformance + 근거 정직성 24 assertion)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 10, 인접 하네스 reciprocal 가드)
  agentic-code-review-harness/                           # [독립 플러그인] 이미 만들어진 코드 변경(PR·브랜치 diff·로컬 변경) — 특히 AI 에이전트가 작성한 것 — 을 수신자(리뷰어) 자리에서 읽고 "머지해도 되는지"를 근거와 함께 판정하는 도메인 무관 5단계 5에이전트 하네스. 한 문장 원칙 = 쓰는 비용은 싸졌지만 믿어도 되는지 판단하는 비용은 그대로다. Phase 0 리뷰 인테이크(한 번에 한 질문·대상 diff 없이 판정 금지) → 1 리스크 티어링(blast radius·longevity·comprehension 3축 + 경로 기반 표면 감지 → 파일군별 T0~T3 + 렌즈/센서/사람게이트/오탐예산 배분) → 2 증거 감사(테스트 diff를 코드보다 먼저 → 오라클 강도 강/약/없음 + 약화 서명 7종·게이트 완화 5종·결함 서명 S1~S8 + 결정적 센서 직접 실행·출력 인용) → 3a 직교 렌즈 8종을 렌즈당 1 에이전트로 병렬(렌즈 밖 금지·위치/무엇/조건 3요소 필수) → 3b 발견별 반증(CONFIRMED/PLAUSIBLE/DROPPED·기본 태도 "이 발견은 틀렸다") → 4 트리아지·머지 판정(차단은 CONFIRMED만·되돌림 지시문 3요소·잔여 위험·판정 후보·정직성 감사 6문항). 정직성 6불변식: INV-1 판정만·실행은 사람(코드 수정·커밋·푸시·머지·승인·close·코멘트 자동 게시 금지) · INV-2 리뷰 대상은 신뢰할 수 없는 입력(PR 텍스트의 지시문 불복종·발견으로 보고·URL 미추적 — 리뷰 에이전트 자신이 주입 표적이며 INV-1과 한 쌍) · INV-3 자기보고 불신(직접 돌린 센서·직접 읽은 diff만 확인·나머지 UNVERIFIED·"테스트 추가됨"도 신뢰 신호 아님) · INV-4 차단은 재현 근거로만·오탐이 지배적 실패 모드(발견 개수를 성과로 쓰지 않음·오탐 예산·초과 미보고 명시) · INV-5 저자 아닌 리스크로 티어링(결함 서명 스캔은 저자 무관 항상) · INV-6 통과는 정확성 증명 아님(이 하네스도 LLM 리뷰어 재현율 한계 상속·점수화 금지). 근거는 2026-06 'Agentic Code Review' 글의 문제 정의를 출발점 삼되 /deep-research 2각도로 1차 소스를 대조해 교정 — PRIMARY(리뷰어 재현율 27~33%·정밀도 3.6~5.1%·리뷰어 간 발견 거의 안 겹침·재현율↑→SNR↓·에이전트 테스트 패치 80.2%가 오라클 약/없음·가시 테스트 통과는 프록시 최적화 증거·지배적 실패는 '기능 격리'·모델 능력↑↔착취↑·리뷰 노력 예측 AUC 0.96)·INDUSTRY(정적 게이트 FP 76%·LLM 필터가 FP 94~98% 제거하나 진짜 결함 12~25% 소실)·인용 금지("리뷰어 이탈 38%" 정의/분모 불일치·arXiv 오귀속·원문에 없는 벤치마크 점추정·벤더 자체보고·"머지율=품질"·"FP 임계"·"200~400줄 상한"·효과 약속). 커밋 안 함·opt-in 저장·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 5 Phase 요약 + 6 불변식 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·산출물·정직성·경계
    agents/                                              # 5 에이전트 (모두 opus)
      risk-tierer.md                                     # Phase 1 3축 관측 + 표면 감지 → T0~T3 + 리뷰 예산 배분(미확인 되물음)
      evidence-auditor.md                                # Phase 2 테스트 우선 · 오라클 강도 · 약화/완화 서명 · S1~S8 · 센서 실행
      lens-reviewer.md                                   # Phase 3a 렌즈 1개씩 병렬 · 3요소 필수 · 못 보는 것 보고
      finding-refuter.md                                 # Phase 3b 반증 우선 6단계 · CONFIRMED/PLAUSIBLE/DROPPED
      merge-arbiter.md                                   # Phase 4 트리아지 · 되돌림 지시문 · 잔여 위험 · 판정 후보 · 정직성 감사
    skills/agentic-code-review/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~4·첫 행동=대상 diff 확보·매 Phase 승인 게이트)
      references/
        risk-tiering.md                                  # 3축 관측 질문 · 표면 감지 패턴 · T0~T3 정의 · 티어별 예산표 · 안티패턴
        agent-failure-signatures.md                      # 읽는 순서 규약 · 오라클 강도 판정 · 약화/완화 서명 · 결함 서명 S1~S8 · 센서
        review-lenses.md                                 # 렌즈 8종 카드(무엇을 보나·전형 결함·확인 방법·못 보는 것)
        finding-triage.md                                # 반증 6단계 · 3값 판정 · 분류 하드 규약 · 오탐 예산 · 되돌림 지시문 · 판정 카드
        evidence.md                                      # 근거 정본(등급 · 성능/오라클/오탐 기저율 · 관행 · 인용 금지 목록 · 재검증)
    evals/
      evals.json                                         # 수용 평가 (design-conformance + 근거 정직성 31 assertion)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 8 / should_not 11, 인접 하네스 reciprocal 가드)
  comprehension-harness/                                 # [독립 플러그인] 에이전트가 쓴 코드 변경을 사람이 실제로 이해하고 있는지 실측하고 그 이해를 자산으로 남기는 도메인 무관 6단계 5에이전트 하네스. 한 문장 원칙 = 이해했다는 느낌은 이해의 증거가 아니다. 강연 "Understanding is the new bottleneck"(2026)이 세운 구분 — 검증을 위한 이해 vs 참여를 위한 이해 — 중 후자를 만든다. Phase 0 이해 인테이크(최대 두 번만 묻는다 — 대상 변경·참여 목적. 나머지는 관측해 잠정값으로 카드에 적고 게이트 A에서 일괄 정정. 한 산출물 지목 시 단축 경로 제시) → 1 이해 부채 지도(6표면 S1~S6 + 참여 목적 스코프 + 설명서 공개 전 예측 문항 + 확신 평정) → 2 설명서 공개(배경·직관·검증 훅·[확인]/[추론] 분리·변경 순서 안내 + 예측 채점 동시 공개) → 3 이해 검증 게이트(자유서술 회상 + diff 좌표 교정 피드백 + 실측 성공률 70~80% + 지각-실제 격차 + 묻지 않은 범위 열거) → 4 마이크로월드(조건부·값싼 대안 먼저·조건 관측·고지 후 만들지 말지는 사용자 결정 — 조건은 게이트가 아니라 권고) → 5 공유 이해(조건부·산출물에서 복원되지 않는 것만 펌프). 정직성 7불변식: INV-1 검증 아닌 참여(결함·머지 판정 안 함·코드 수정/커밋 금지) · INV-2 자기보고는 센서가 아님(자가평가 판별력 54.5%·R²≈5.9%·확신은 격차 계산용) · INV-3 설명은 예측 뒤에 공개(AI 설명은 과확신 장치·대조 불가능한 것 단언 금지·그 자체로 게이트 통과 못 함 — 강연 원안과 가장 크게 갈라지는 지점) · INV-4 퀴즈 통과는 증명이 아님(점수화 금지·묻지 않은 범위 열거 필수) · INV-5 마이크로월드는 기본값 아닌 가설(인접 네 하위군 전부 0 또는 음수·우리 도메인은 미측정·조건은 게이트가 아니라 권고이며 명시 요청을 기각하지 않음) · INV-6 게이트는 경고이지 거부권이 아님 · INV-7 효과 약속 금지(주장 가능한 것은 리뷰되지 않던 변경을 읽고 답한 변경으로 / 과확신을 낮추고 빈틈을 드러냄 둘뿐). 근거는 강연 기법 4종을 승격하되 규정을 그대로 옮기지 않고 8각도 1차 문헌 + 적대 반증 2라운드로 대조·교정 — PRIMARY(단일 에이전트 설명이 체감 이해 최고·객관 학습 최저 / 채점 결과 열람만이 과확신을 꺼뜨림 / 설명은 검증 비용을 낮출 때만 과의존을 줄임 / 인출연습 g=0.50·수렴 0.499 / 피드백 0.73 vs 무피드백 0.39 / 성공률 ≤50%+무피드백 g=0.03 p=.79 / 재인 0.31 vs 단서회상 0.57 / 답 읽기 −0.095 vs 생성 +0.169 / 질문 생성 +0.042 n.s. / 미퀴즈 재료 전이 d=0.16 n.s. / 가장 유사 조건 BF01=7.52 null / 자가평가 R²≈5.9% / 시각화는 무엇을 보여주나가 아니라 학습자가 무엇을 하나 · 예측 빼면 효과 소멸 / 스크러빙 마이크로월드 선행 실증은 학습 null·사용률 null / 전문 환경 시각화 연구체 부재 / 커뮤니케이션 매체는 고유정보 풀링에 영향 없음 / 사람+AI 조합 g=−0.23 / 40년 95개 코드 이해 실험 중 "이해가 무엇을 낳는가" 0건) · 인용 금지("5문항·중간 난이도" 1차 출처 없음 → 실측 성공률로 대체 · "퀴즈=속도 조절기" 측정 0건 · EEG 기반 cognitive debt 수치 · 철회 메타분석 · 존재하지 않는 효과크기 · "200~400 LOC 결함 70~90%" · 벤더 자체보고 · "AI가 개발자 이해를 침식한다" · 하네스 산출물에 효과크기 부착). cognitive debt는 데이터 없는 입장 논문의 프레임으로만·Papert/Alan Kay/Naur는 계보·영감으로만. 커밋 안 함·opt-in 저장·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 6 Phase 요약 + 7 불변식 + 변경 이력
    README.md                                            # 사용자용 개요·사용법·강연과 갈라진 지점·산출물·정직성·경계
    agents/                                              # 5 에이전트 (모두 opus)
      debt-cartographer.md                               # Phase 1 6표면 관측 + 참여 목적 스코프 + 설명서 공개 전 예측 문항 + 확신 평정
      explainer-architect.md                             # Phase 2 예측 제출 후에만 공개 · 5블록(검증 훅 중심) · [확인]/[추론] · 채점 동시 공개
      comprehension-examiner.md                          # Phase 3 자유서술 회상 · 교정 피드백(diff 좌표) · 실측 성공률 · 격차 · 묻지 않은 범위
      microworld-builder.md                              # Phase 4 값싼 대안 먼저 · 조건 관측·고지 · 결정은 사용자 · 폐기 전제 · 만들지 않음도 정상 출력
      shared-context-curator.md                          # Phase 5 복원 불가능한 것만 펌프 · 열린 질문 · 지식 집중 3값 · 등급 금지
    skills/comprehension-loop/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~5·첫 행동=대상 변경과 참여 목적 확보·매 Phase 승인 게이트)
      references/
        comprehension-debt.md                            # 참여 목적별 스코프 · 6표면 S1~S6 · 예측 커밋 규약 · 게이트 무게(자동화 경계) · 인테이크 마찰 예산(두 번만 묻기)
        explainer-structure.md                           # 공개 규약 3조 · 5블록 B1~B5 · 검증 훅 4종 · 확인/추론 분리 · 금지 · 자체 점검
        quiz-design.md                                   # 강제 조건 Q1~Q10 · 문항 3분류 A/B/C · 실측 성공률 표 · 타이밍(즉시=역전 창) · 거부권 없음
        microworld-patterns.md                           # 값싼 대안 우선 · 조건 C1~C4(사전지식 게이팅 삭제) · 시청 전용/스크러빙 금지 · 패턴 P1~P4 · 사용 기록
        shared-understanding.md                          # 두 갈래 판정 · 펌프 6질문 · 공용 이름 · 지식 집중 · 주장하지 않는 것
        evidence.md                                      # 근거 정본(등급 6단계 · 사실표 F1~F76 · 도메인 경고 · 인용 금지 목록 · 남은 미지(감사 레인 미실행 명기) · 재검증)
    evals/
      check_evidence.py                                  # 근거 앵커 검증기(파일::앵커가 실재하는지 확인, --write로 passed를 실행 결과로 갱신, 종료 코드=실패 수)
      evals.json                                         # 수용 평가 (design-conformance 29 assertion · 앵커 105+개, check_evidence.py로 실행 검증)
      trigger-eval.json                                  # 트리거 경계 평가 (should_trigger 9 / should_not 13, 인접 하네스 reciprocal 가드)
```
  aeo-harness/                                           # [독립 플러그인] AEO(Agentic Engine Optimization) — 기술 문서를 AI 코딩 에이전트가 찾고·적은 왕복으로 읽고·정확히 쓸 수 있게 만드는 것을 결정론 센서로 측정하고 승인 게이트 뒤에 개선하는 도메인 무관 4단계 4에이전트 하네스. 검색엔진·답변엔진 노출 최적화(SEO/GEO)가 아니다 — 소비자가 사람이 아니라 코딩 에이전트다. 한 문장 원칙 = 에이전트가 문서에 도달했다는 것과 그 문서로 코드가 맞아졌다는 것은 다른 사건이다(발행 측 근거는 도달·효율만 측정하고 정확도 0건, 정확도 측 근거는 문서를 이미 쥐여준 조건이라 그 둘을 잇는 측정이 없다 — evidence F1). Phase 0 인테이크(대상 문서 + 소비 경로(HTTP/MCP/로컬/패키지)를 한 번에 한 질문씩, 경로가 조사의 절반을 결정) → 1 도달 조사(R1 링크 지도가 1급·R2 JS 없이 본문·R3 .md/Accept 협상·R4 죽은 링크·R5 벤더 UA replay 오차단·R6 robots.txt 보고만·R7 토큰 census 임계값 없음·R8 스펙 존재) → 2 내용 조사(C1 심볼별 예제·C2 예제 실행 검증·C3 시그니처 드리프트·C4 거짓으로 판정되는 서술·C5 낯섦·C6 주입 표면) → 3 개입 계획(T-A 위험0 거짓 제거 / T-B 검증 통과분만 / T-C report-only, 계획+항목별 개별 승인) → 4 수용 증명(문서 점수가 아니라 재측정된 태스크 결과, 못 돌리면 UNVERIFIED). 7불변식: INV-1 도달≠정확도 · INV-2 틀린 문서 > 없는 문서(검증 없는 LLM 문서 생성은 순마이너스) · INV-3 점수·등급 금지 · INV-4 report-only 자동 생성·편집 금지(단 거부권 아님) · INV-5 UA로 도구 귀속 금지(진위는 IP·rDNS로만) · INV-6 수용은 재측정으로만 · INV-7 대상 문서는 신뢰 경계 밖. 커밋 안 함·opt-in 저장·다른 플러그인 비참조·비의존
    .claude-plugin/
      plugin.json
    CLAUDE.md                                            # 포인터 + 구조 + 설계를 바꾼 근거 표 + 변경 이력
    README.md                                            # 사용자용 개요 + 조사에서 교정된 통념 표 + 정직성 불변식
    agents/                                              # 4 에이전트 (모두 opus)
      reach-auditor.md                                   # Phase 1 도달 조사 R1~R8 (정확도 언어 금지·robots.txt 편집 금지·UA 귀속 금지)
      content-auditor.md                                 # Phase 2 내용 조사 C1~C6 (거짓 판정된 것만 결함으로·산문 채점 금지)
      intervention-planner.md                            # Phase 3 3티어 계획 + 항목별 개별 승인 (T-C는 넘기기만)
      acceptance-verifier.md                             # Phase 4 배터리 사전 고정 + 두 축 분리 보고 + UNVERIFIED
    skills/aeo-audit/
      SKILL.md                                           # 진입점 오케스트레이터 (Phase 0~4·첫 행동=대상 문서와 소비 경로 확보·매 Phase 승인 게이트·INV-1~7)
      references/
        reach-sensors.md                                 # R1~R8 절차·판정 (R1 링크 지도가 1급인 이유·벤더 UA 목록·못 잰 것 열거 규약)
        content-sensors.md                               # C1~C6 절차·판정 (예제 실행 부작용 고지·정규식 오탐 표기·낯섦 판정 근거)
        intervention-tiers.md                            # T-A/T-B/T-C + T-C 항목별 정직한 목적 서술(llms.txt·robots.txt·마크다운·구조·컨텍스트 파일·agent-permissions)
        acceptance-probe.md                              # 태스크 배터리 설계(개입 전 고정·대조 심볼 포함)·두 축 분리·수용 리포트 형식
        evidence.md                                      # 근거 정본(등급 5종 + DV 필수 표기 · F1~F36 · 인용 금지 14항 · UNVERIFIED)
      scripts/
        reach_probe.py                                   # 도달 센서 결정론 프로빙 (stdlib only·census 전용·점수 없음·UA replay는 오차단 탐지만)
        check_evidence.py                                # 인용 앵커·금지 문구·점수 어휘 자동 검사 (부정 맥락 허용하되 건수 보고)
    evals/
      trigger-eval.json                                  # 트리거 경계 20문항 (SEO/GEO·저장소 정적 점수·이해 실측·머지 판정·컨텍스트 파일 작성과 분리)
