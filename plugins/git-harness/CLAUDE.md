# git-harness

커밋·push·PR 생성·PR 리뷰를 하나의 파이프라인으로 처리하는 Git 워크플로우 플러그인.

사용자용 개요·사용법은 [README.md](README.md), 파이프라인(§0~§9)·게이트의 정본은 [SKILL.md](skills/commit-pr/SKILL.md)다.

## Conventions

- **진입점 선택 = 이후 단계 승인.** 진행 중 "push할까요?"·"PR 만들까요?"를 다시 묻지 않는다. 예외는 ① 되돌리기 어려운 행위 직전의 *내용* 확인(§5 커밋 메시지·§7 PR 제목/본문 프리뷰) ② §8 PR 리뷰 실행 여부 둘뿐이다.
- 진입점 질문 전에 §0.1 상태 파악(`git status`/`branch`/`log`/`log @{u}..HEAD`/`gh pr view`)을 조용히 수행하고, **명령 실패도 판단 근거**(upstream 없음·열린 PR 없음)로 읽는다.
- 전제 조건 검사(§0.3)는 **선택된 모드에만** 적용한다. 기존 PR 리뷰에는 보호 브랜치 검사를 적용하지 않는다(쓰기가 아니므로).
- 커밋 게이트: 리뷰 발견의 verdict(`CONFIRMED`/`PLAUSIBLE`)와 관점을 severity 3등급으로 환산해 **correctness이거나 CONFIRMED면 차단**한다. 게이트는 경고이지 거부권이 아니다 — 사용자가 명시적으로 진행을 택하면 무엇을 안고 가는지 남기고 따른다.
- 커밋은 `git commit --cleanup=whitespace -F -`(stdin)로 실행한다. 기본 cleanup은 본문의 `# 요약` 헤딩을 주석으로 지우고, 고정 경로 임시 파일은 병렬 세션에서 충돌한다.
- 내장 `/code-review`는 `disable-model-invocation`이라 Skill 호출 불가 → Agent 서브에이전트로 대체한다. 내장 `/review`(§8)는 동명 커맨드 충돌을 피해 Skill 도구로 **명시 호출**한다.
- 커밋 메시지·PR 본문·리뷰 코멘트는 한국어로 작성한다.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 아래에 행을 추가한다.
