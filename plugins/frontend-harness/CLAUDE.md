# frontend-harness

프론트엔드 개발 전 과정(Research → PRD → Develop → Review → Verify)을 지원하는 멀티 에이전트 스킬·커맨드·훅 플러그인. 사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
.claude-plugin/plugin.json     # 플러그인 메타데이터
commands/                      # 상위 워크플로우 커맨드 (스킬을 서브에이전트로 spawn)
  orchestrator.md              # research → prd → develop → review → verify 6단계
  research.md prd.md frontend-guidelines.md review.md verifier.md verify.md
hooks/                         # PreToolUse·PostToolUse·Stop 훅
  hooks.json                   # 훅 설정
  lib.sh                       # 공용 stdin JSON 파서 (jq→python3 폴백, 부재 시 경고 후 통과)
  guard.sh write-guard.sh skill-dedup.sh stop-lint.sh package-changed.sh
skills/                        # 13개 스킬 (각 SKILL.md, 일부 + references/)
  planner architecture critic grill-me tdd
  a11y semantic-html seo-geo-optimizer figma-extract
  e2e-verifier lighthouse-performance qa-inspector security-audit
```

## Conventions

- 각 스킬은 `skills/<skill>/SKILL.md`에 정의하고 frontmatter는 `name`/`description` 필수 + 필요 시 `allowed-tools`/`disable-model-invocation`만 추가 허용한다.
- 커맨드는 스킬을 직접 실행하지 않고 Agent 도구로 서브에이전트를 spawn한다(모든 spawn에 `model: "opus"` 명시).
- 스킬 간 교차 참조는 상대 경로(예: `../a11y/SKILL.md`)를 쓴다.
- 참고 자료는 `skills/<skill>/references/` 하위에 배치한다.
- Review 단계는 사용자가 선택한 관점만 단일 메시지에서 동시 spawn한다(병렬).

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-03 | 플러그인 CLAUDE.md/README.md 신설 | 플러그인 단위 문서·사용법 분리 |
| 2026-07-03 | 훅·권한·트리거 정비 (v1.3.1) | 유효하지 않은 FileChanged 이벤트 제거 → package-changed를 PostToolUse로 재배선, 훅 파서 공용화(lib.sh, jq→python3 폴백·부재 시 경고 후 통과), guard.sh 차단 regex 보강(분리형 rm 플래그·`/*`·`git add ./`), stop-lint 이벤트 분기(PostToolUse=수정 파일만·Stop=전체 diff), qa-inspector/security-audit allowed-tools 최소화(Write/Edit 제거), planner·tdd·architecture·critic·grill-me·qa-inspector에 인접 하네스 역방향 배제 문구, 커맨드 spawn에 model:"opus" 명시 |
| 2026-06-21 | figma-extract 스킬 추가 | Figma 링크→디자인 컨텍스트 추출 전용 스킬. metadata 노드맵 우선 → 대상 노드만 get_design_context/variable_defs/screenshot 상세 추출 → `.claude/design/`에 json·spec·png 파일화, 부모엔 경로+요약만(토큰 폭주 차단). 코드 생성은 책임 밖. 단독 동작 |
| 2026-07-05 | 인수조건(AC) 계약 + TDD 선행 + 수렴 루프 | **(1) prd.md** — 각 기능(FR)을 사용자 스토리(US)와 관찰형 인수조건(AC-n.m, Given/When/Then)으로 전개(product-spec-harness 방법론 내재화·플러그인 의존 없음), FR↔US↔AC 추적 매트릭스·§7 기능단위 체크리스트 추가, critic이 인수조건 계약(빠짐·판정불가) 검수. **(2) frontend-guidelines.md** — 선택 스킬에 TDD가 있으면 **TDD 선행(2-A, 순차)** → 나머지 스킬 **병렬(2-B)**, TDD는 AC를 RED 테스트 근거로 수령, 최종 점검을 **기능(FR/US) 단위 인수조건 충족**으로 수행. **(3) verify.md·orchestrator.md** — E2E를 **인수조건(AC) 단위**로 판정하고 **자동 인수조건 충족률**(브라우저로 못 고치는 `[수동]` AC는 분수에서 제외·수동 확인 체크리스트로 분리 → 종료 조건 100% 도달 가능성 보장) 산출, 자동 충족률 100% 미만이면 **Develop→Review→Verify 수렴 루프**(미충족 자동 AC만 재구현, 매 라운드 사용자 게이트·소프트 캡 5회·정체 가드, 무시 시 "알려진 미충족(사용자 승인)" 명시). **(4) e2e-verifier·tdd·verifier** — AC-keyed 시나리오·자동 충족률 보고(오케스트레이션 시 리프 메뉴 억제·상위 루프 위임), AC가 RED 테스트 목록을 시드, 상위 재호출 시 스킬 재선택 안 함. **[검수] deep-review 3렌즈(요구충족·일관성·불변식) → 추가 검증 2회(closure 재확인 + 실행-트레이스 시뮬레이션)로 결함 반영**: **AC 검증 3-레인 정교화(E2E/TDD/수동)** — TDD-only AC(서버 로직)가 E2E 충족률 분모에 끼어 100% 도달불가/게이트 우회되던 구조 결함 수정, **배포 게이트 = E2E 자동 충족률 100% AND TDD 자동 충족률 100% AND `[수동]` 확인 완료**(레인 0개면 N/A), WARNING/FAIL 배타화(승인 여부로), `[수동]` 확인 소유권(verify 수집·orchestrator 소비)·라운드 캐싱, 루프 라우팅 레인 분기(browser-only는 E2E 재검증), 0/0 충족률·단독 실행(PRD 부재 AC 도출·2-B 공집합·`호출맥락` 플래그) 엣지 보강 |
