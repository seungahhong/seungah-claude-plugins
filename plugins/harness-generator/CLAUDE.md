# harness-generator

도메인 무관 하네스(에이전트 팀 + 스킬 + 오케스트레이터)를 7단계 메타 프로세스로 자동 생성하는 메타 플러그인. 사용자용 개요·사용법은 [README.md](README.md) 참조.

## Structure

```
.claude-plugin/plugin.json     # 플러그인 메타데이터
skills/
  harness-generator/SKILL.md   # 7단계 제너레이터 스킬 (+ references/)
```

## 7단계 프로세스 (요약)

| Phase | 단계 | 산출 |
|-------|------|------|
| 0 | 현황 감사 (Audit) | 신규/확장/보완 분기 판별 |
| 1 | 도메인 분석 | 입력·산출·단계 정의 |
| 2 | 아키텍처 설계 | 실행 모드(팀/서브/하이브리드) + 패턴 선택 |
| 3 | 에이전트 정의 작성 | `agents/{name}.md` |
| 4 | 스킬 작성 | `skills/{step}/SKILL.md` |
| 5 | 오케스트레이션 | 진입점 오케스트레이터 |
| 6 | 검증 (Validation) | 구조·모드·스킬 실행 테스트 |

## Conventions

- 특정 기술 스택·도구에 종속되지 않는 공통 메타 절차만 다룬다.
- 생성 결과는 에이전트 정의 + 스킬 + 오케스트레이터를 한 묶음으로 산출한다.
- 재실행·보완·기존 하네스 감사에도 같은 스킬을 사용한다(Phase 0에서 분기).

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-06-03 | 플러그인 CLAUDE.md/README.md 신설 | 플러그인 단위 문서·사용법 분리 |
