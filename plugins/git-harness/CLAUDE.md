# git-harness

Git 워크플로우(한국어 커밋 메시지 작성, 리뷰 내장 커밋·PR 생성)를 지원하는 멀티 에이전트 스킬 플러그인. 사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
.claude-plugin/plugin.json     # 플러그인 메타데이터 (v0.2.0)
skills/
  commit/SKILL.md              # 한국어 커밋 메시지 작성 (`이슈번호 type: 제목`)
  review-to-pr/SKILL.md        # 리뷰 → 커밋 → PR 생성 올인원 워크플로우
```

## Conventions

- 두 스킬 모두 `disable-model-invocation: true` — 슬래시 커맨드/명시 키워드로만 호출된다.
- `commit`은 git 계열 Bash + Read만 허용한다(`allowed-tools` 제한).
- `review-to-pr`은 단계(Commit/PR) 안에서 `/simplify` + `/review`를 서브에이전트로 자동 수행한 뒤 수정을 적용한다.
- 커밋 메시지·리뷰 코멘트는 한국어로 작성한다.

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-03 | 플러그인 CLAUDE.md/README.md 신설 | 플러그인 단위 문서·사용법 분리 |
