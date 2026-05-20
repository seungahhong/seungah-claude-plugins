---
name: branch-doc-orchestrator
description: "코드베이스와 현재 브랜치(git diff)를 기준으로 배경·목차·기술스펙·변경사항·테스트를 포함한 기술 문서를 자동 생성하고 완성도를 검증하는 오케스트레이터. '브랜치 문서 생성', '변경 문서 만들어줘', 'PR 문서', '기능 문서 자동 생성', '브랜치 기준 문서화'를 요청할 때 사용한다. 문서 '다시 생성', '재실행', '업데이트', '수정', '보완', '이전 결과 기반으로'에도 사용한다. 단순 질의는 직접 답변한다."
---

# 브랜치 문서 자동 생성 오케스트레이터

코드베이스와 현재 브랜치의 변경을 기준으로 **배경 / 목차 / 기술스펙 / 변경사항 / 테스트 / 영향·리스크**를 포함한 단일 기술 문서를 생성하고, 완성도를 검증해 미달 시 보강 루프를 돈다.

## 실행 모드

**서브에이전트** — 섹션 분석가들은 공유 컨텍스트 파일을 읽고 독립 병렬로 자기 섹션만 생성한다. 검증자는 초안만 받아 컨텍스트 격리 상태로 채점한다. 생성-검증 루프는 이 오케스트레이터가 파일 기반으로 구동한다. 실시간 토론이 필요 없어 팀 통신 비용을 들이지 않는다.

**패턴:** 파이프라인(수집) → 팬아웃/팬인(섹션 분석 병렬) → 조립 → 생성-검증(완성도 게이트, 최대 2회).

**원칙:** 모든 Agent 호출에 `model: "opus"`를 명시한다. 추론 품질이 문서 품질을 좌우한다.

---

## Phase 0 — 컨텍스트 확인

`_workspace/`를 검사해 실행 유형을 자동 판별하고 1줄 보고 후 진행한다.

- `_workspace/` 없음 → **초기 실행**.
- 있고 `meta.json`의 `commit_range`가 현재와 동일 → **부분 재실행**(보완: 변경 섹션만 다시).
- 있고 입력(base/HEAD) 변경 → **새 실행**(`_workspace/` → `_workspace_prev/` 이동 후 재생성).

사용자가 "보완/수정"을 요청하며 특정 섹션을 짚으면 해당 섹션만 Phase 3부터 다시 돈다.

## Phase 1 — 준비

- 사용자 요구를 1줄로 요약한다(대상 브랜치, base 지정 여부, 출력 위치).
- base 지정이 없으면 자동 감지 예정임을 알린다.
- `_workspace/`를 만든다(또는 이전본을 `_workspace_prev/`로 이동).

## Phase 2 — 컨텍스트 수집

context-collector 1명을 동기 호출해 변경+코드 컨텍스트를 모은다.

```
Agent(
  subagent_type="context-collector",
  model="opus",
  prompt="branch-context-collection 스킬에 따라 현재 브랜치와 base의 변경을 수집하라.
          base 지정: {사용자 입력 또는 '자동 감지'}.
          산출: _workspace/context.md, _workspace/meta.json"
)
```

산출물(`context.md`, `meta.json`)을 확인한다. diff가 비었으면 워킹 트리 포함 여부를 사용자에게 묻고 재수집한다.

## Phase 3 — 섹션 분석 (팬아웃, 병렬)

doc-section-writer를 섹션마다 **한 메시지에서 동시에** 띄운다(`run_in_background=true`). 섹션 스펙을 주입한다.

생성 섹션: `background`, `techspec`, `changes`, `tests`, `impact` (요약·목차는 조립 단계에서 생성).

```
# 아래 5개를 단일 메시지에서 동시 spawn
Agent(subagent_type="doc-section-writer", model="opus", run_in_background=true,
      prompt="doc-section-writing 스킬의 'background' 섹션 카드에 따라 _workspace/context.md를
              분석해 _workspace/section_background.md를 작성하라. section_id=background")
Agent(subagent_type="doc-section-writer", model="opus", run_in_background=true,
      prompt="... 'techspec' ... _workspace/section_techspec.md ... section_id=techspec")
Agent(subagent_type="doc-section-writer", model="opus", run_in_background=true,
      prompt="... 'changes' ... _workspace/section_changes.md ... section_id=changes")
Agent(subagent_type="doc-section-writer", model="opus", run_in_background=true,
      prompt="... 'tests' ... _workspace/section_tests.md ... section_id=tests")
Agent(subagent_type="doc-section-writer", model="opus", run_in_background=true,
      prompt="... 'impact' ... _workspace/section_impact.md ... section_id=impact")
```

모든 섹션 파일이 생성될 때까지 대기한 뒤 다음 단계로 간다.

## Phase 4 — 조립

doc-assembler 1명을 호출해 섹션을 합치고 요약·목차를 생성한다.

```
Agent(
  subagent_type="doc-assembler",
  model="opus",
  prompt="_workspace/section_*.md를 고정 순서(요약→배경→목차→기술스펙→변경사항→테스트→영향·리스크)로
          합치고, meta.json으로 머리말 표를, 본문 헤딩으로 목차를, 전체를 읽고 요약을 생성하라.
          산출: _workspace/draft.md"
)
```

## Phase 5 — 완성도 검증 (생성-검증 루프, 최대 2회)

doc-verifier 1명을 호출해 `draft.md`만 넘겨 채점한다.

```
Agent(
  subagent_type="doc-verifier",
  model="opus",
  prompt="doc-completeness-check 스킬에 따라 _workspace/draft.md의 완성도를 채점하고
          _workspace/grading.json을 산출하라. draft.md 외 다른 컨텍스트는 보지 마라."
)
```

- `verdict == "pass"` → Phase 6.
- `verdict == "revise"` → `grading.json`의 `passed:false` 항목을 `section_id`별로 묶어, 해당 섹션의 doc-section-writer만 재호출(피드백 주입) → doc-assembler 재호출 → doc-verifier 재검증. **최대 2회** 반복.
- 2회 후에도 `revise`면 남은 미달 항목을 최종 보고와 문서 말미 "알려진 한계"에 기록하고 진행한다(무한 루프 방지).

## Phase 6 — 최종 산출 및 정리

- `_workspace/draft.md`를 사용자 출력 위치로 복사한다. 기본: `docs/branch-doc-{branch}-{YYYY-MM-DD}.md`(사용자 지정 시 그 경로).
- 사용자에게 **완성도 요약**을 보고한다: `grading.json`의 `summary`(통과/미달/pass_rate)와 남은 미달 항목, 문서 경로.
- `_workspace/`는 후속 실행을 위해 **보존**한다.
- `CLAUDE.md` Change History에 1줄 추가(절대 날짜).
- Phase 7 진화: 사용자에게 개선 의견을 1회 제안한다(선택).

---

## 데이터 전달

- 단계 간 핸드오프: 합의된 `_workspace/` 경로의 파일(반환 메시지가 아니라 파일 기반 — 큰 데이터·감사 추적).
- 중간 산출물: `_workspace/{artifact}` (`context.md`, `meta.json`, `section_*.md`, `draft.md`, `grading.json`).
- 최종 산출물: `docs/branch-doc-{branch}-{date}.md`.

## 에러 정책

- 각 Agent 1회 재시도 → 실패 시 해당 결과만 누락 처리하고 진행한다. 누락 섹션은 조립 시 플레이스홀더로 표기하고 최종 보고에 명시한다.
- 충돌 데이터(예: 섹션 간 사실 불일치)는 삭제하지 않고 검증 단계가 잡아 보고하게 둔다.
- git 저장소가 아니거나 base 감지 실패 시 사용자에게 1회 확인 후 진행(추측 금지).

## 테스트 시나리오

- **정상 흐름:** `feature/login` 브랜치에서 실행 → base를 `main`으로 자동 감지 → 컨텍스트 수집 → 5개 섹션 병렬 생성 → 조립 → 검증 `pass`(pass_rate 1.0) → `docs/branch-doc-feature-login-2026-05-20.md` 생성 + 완성도 요약 보고.
- **에러 흐름(검증 미달):** 테스트 섹션에 실행 명령 누락으로 `verdict:"revise"` → 해당 섹션 작성자만 재호출해 실행 명령 보강 → 재조립 → 재검증 `pass`. 2회 후에도 근거 부재로 못 채우면 "알려진 한계: 테스트 실행 명령 미확인"을 문서에 명시하고 사용자에게 보고.
- **에러 흐름(빈 diff):** 브랜치 == base → 워킹 트리 포함 여부를 사용자에게 묻고, 거절 시 "변경 없음"을 보고하고 종료.
