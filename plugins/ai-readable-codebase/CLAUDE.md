# ai-readable-codebase

코드베이스가 **AI 코딩 에이전트가 읽고 안전하게 기여할 수 있는 구조**인지를 진단·개선하는 도메인 무관 멀티 에이전트 하네스.
핵심 전제는 **"구조가 프롬프트보다 먼저다(structure before prompt)"**와 **"코드 품질(Q축)과 AI 접근성(A축)은 다른 차원이다"**이다.

사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
ai-readable-codebase/
├── .claude-plugin/
│   └── plugin.json
├── CLAUDE.md                        # (이 문서) 하네스 포인터 + Phase 요약 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·도구 경계·근거 자료
├── agents/                          # 모두 model: "opus"
│   ├── accessibility-assessor.md    # Phase 0 — 2축(Q/A) 진단 + L1~L5 등급(증거 기반) + A축 격차·백로그
│   ├── guardrail-architect.md       # Phase 1 — 구조 우선·빌드 가드레일(의존 방향 물리 강제 + 피드백 3차원 + 빌드/문서 분담)
│   ├── standalone-designer.md       # Phase 2 — 도메인 슬라이스 독립 실행(port/adapter 치환·use-case seed)
│   └── acceptance-verifier.md       # Phase 3 — 수용 증명 인프라 + 등급 적대 재측정(reward-hacking 가드)
└── skills/
    └── ai-readable-codebase/
        ├── SKILL.md                 # 오케스트레이터(진입점, 진단 승인 게이트 → 4단계 플로우)
        └── references/
            ├── ai-readable-codebase-principles.md   # 2축·L1~L5·빌드 가드레일·피드백 3차원·standalone·수용 증명·anti-pattern·경계
            └── ai-readable-codebase-research.md      # 설계 근거 dossier (flex 5부작 + 2025+ 출처·인용·vote·CAVEAT)
└── evals/
    ├── evals.json                   # 수용 평가 (design-conformance dry-run — 핵심 불변식 file:section 인용 채점)
    └── trigger-eval.json            # 트리거 경계 평가 (should_trigger / should_not, 인접 도메인 reciprocal 가드)
```

## Phase 요약

| Phase | 이름 | 호출 에이전트 | 핵심 산출물 | 게이트 |
|-------|------|---------------|-------------|--------|
| 0 | 진단 (Assess) | accessibility-assessor | 2축(Q/A) 진단 + L1~L5 등급(증거 인용) + A축 격차 + 목표 등급 + 우선순위 백로그 | **진단 승인 게이트** (개선 착수 전) |
| 1 | 구조·가드레일 (Guardrails) | guardrail-architect | 빌드 가드레일 설계(의존 방향 물리 강제 + 피드백 3차원 개선 + 빌드/CLAUDE.md 역할 분담) | 핵심 아키텍처 규칙이 빌드 계층에서 잡히는지 |
| 2 | 독립 실행 (Standalone) | standalone-designer | 도메인 슬라이스 standalone 설계(port/adapter 치환·use-case seed·독립 검증 커버리지) | 슬라이스가 전체 없이 검증 가능한지 |
| 3 | 수용 증명·재측정 (Acceptance & Re-grade) | acceptance-verifier | 수용 증명 인프라 설계 + 등급 재측정 Verdict(증거·한계·reward-hacking 점검) | 구조가 실제로 바뀌어 등급이 올랐는지(증거) |

매 단계 보고: `[Phase n] {산출물}: {핵심} — {다음 단계|보정 필요}`.
최종: `[AIRC 완료] 현재 {Lx} → 목표 {Ly}, A축 격차 {해소}/{전체} — 재측정 {증거 PASS|미달} → {산출물 경로}`

## Conventions

- **A축 ≠ Q축(분리 측정)**: 코드 품질(테스트 커버리지·복잡도·중복)과 AI 접근성(패턴 일관성·빌드 피드백·모듈 경계 예측성·의존 방향 강제·독립 실행·에이전트 가이드·자동 수용)을 *별개 축*으로 측정한다. 높은 Q축이 높은 A축을 보장하지 않는다.
- **구조가 프롬프트보다 먼저(structure-first)**: 프롬프트/CLAUDE.md를 다듬기 전에 에이전트가 기여 가능한 *코드베이스 구조*를 먼저 갖춘다.
- **빌드가 강제하고 문서가 설명한다**: 빌드 가드레일은 "무엇이 *불가능*한지"를, CLAUDE.md는 "무엇이 *바람직*한지/왜"를 맡는다. 자연어 가이드는 구조 강제 없이는 실패한다(해석 모호·컨텍스트 경쟁·피드백 부재).
- **피드백을 앞단으로·가르치게 설계**: 검증을 파이프라인 앞단으로(컴파일 > 런타임, 타입 > 컴파일 체크). 피드백 메시지는 3차원(위치 특정성·원인 명확성·수정방향 추론가능성)을 갖추고, 가장 중요한 아키텍처 규칙을 가장 빠른 계층(컴파일)에서 잡는다. 테스트 실패도 판정이 아니라 *피드백*으로 설계한다.
- **독립 실행(standalone executability)**: 도메인 슬라이스를 전체 시스템 없이 검증 가능하게(port/adapter 치환·use-case 경유 seed). 계산적 통제(테스트·린터·타입체커)가 추론적 통제보다 낫다.
- **수용 증명 우선 + 한계 명시**: 리뷰어가 PR을 열기 전에 동작 증명이 이미 존재하게 해 리뷰를 "동작하나"에서 "설계가 좋은가"로 이동시킨다. 단, 수용 증명이 못 잡는 것(성능 저하·보안 취약·동시성 일관성·가독성)은 사람 몫으로 명시한다.
- **증거 기반 등급(reward-hacking 가드)**: 등급은 자기보고가 아니라 *증거*로 매긴다 — "경계 위반이 실제로 빌드 실패를 일으키는가"를 file:line으로 확인한다. 재측정 시 구조가 실제로 바뀌어 등급이 올랐는지 적대적으로 검증한다(자기보고 불신).
- **generator/checker 분리**: 가드레일·standalone을 *설계*한 에이전트(Phase 1/2)와 등급을 *재측정*하는 검증자(Phase 3)를 분리한다.
- **스택 무관(일반화)**: 근거 시리즈의 예시는 Kotlin/Gradle/Hexagonal이지만 원리(빌드 강제·독립 실행·수용 증명)는 *스택 무관*으로 일반화한다. 특정 스택 도구를 강요하지 않는다.
- **과장 금지(정직성)**: CodeScene Code Health 등 정량 수치는 vote/CAVEAT와 함께만 인용하고 "개선 N% 보장"을 쓰지 않는다. 반박된 주장은 references dossier 투명성 섹션에만 둔다.
- **제안만(사람 집행)**: 이 하네스는 진단·등급·설계 *제안*을 산출한다. 코드를 자동 수정하지 않는다 — 실제 구조 변경 구현은 사람이 승인·집행하거나 구현 하네스(backend-harness/loop-engineering)로 라우팅한다.
- **경계**: 한 기능의 실행 기반 구현·검증(backend-harness), 상류 산출물 핸드오프 검수(review-harness), 하네스 자체 진단(meta-harness), 전달 파이프라인(cicd-harness), 실행 가능 명세 작성(spec-driven-development), 컨텍스트 페이로드 조립(context-engineering), 완성 코드 리뷰·커밋/PR(frontend/git-harness)은 범위 밖이다(일반 개념으로 변별, 타 플러그인 의존 금지).
- 4개 에이전트 협업 하네스이므로 오케스트레이터 SKILL.md의 **모든 Agent 호출에 `model: "opus"`를 명시**한다.

## Change History

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-06-25 | 플러그인 신설 | ai-readable-codebase(코드베이스의 구조적 AI 접근성 진단·개선: 2축 Q/A·L1~L5 등급 → 빌드 가드레일 → standalone 독립 실행 → 수용 증명·재측정) 멀티 에이전트 하네스. deep-research 적대 검증 근거 + 1차 출처(flex.team 'AI가 읽을 수 있는 코드베이스' 5부작, 2026-05~06) + 2025+ 학술/산업 출처 |
