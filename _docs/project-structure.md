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
  harness-generator/                                     # [독립 플러그인] 도메인 무관 하네스 자동 생성 메타 플러그인
    .claude-plugin/
      plugin.json
    skills/
      harness-generator/                                 # 하네스(에이전트팀+스킬+오케스트레이터) 자동 생성 제너레이터 스킬 (+ references/)
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
```
