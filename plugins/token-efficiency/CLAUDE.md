# token-efficiency

Claude Code **세션 JSONL 로그**를 결정론적 스크립트로 파싱해 레포 단위 **토큰/컨텍스트 효율**을 정량 측정·시각화하고 $ 절감안을 내는 단일 스킬. 외부 스킬 `improve-token-efficiency`를 deep-research(5 세션 적대 검증)의 2025~2026 1차 근거로 개선한 버전.

사용자용 개요·사용법은 [README.md](README.md), 실행 흐름·점수 축·탐지기의 정본은 [SKILL.md](skills/token-efficiency/SKILL.md)와 `scripts/`, 근거는 [references/research/README.md](skills/token-efficiency/references/research/README.md)다.

## Conventions

- **결정론 우선, 제안만**: 스크립트가 자동 채점·탐지, LLM은 보고·해석만. 코드를 자동 수정하지 않는다.
- **점수 = 효율 프록시(≠cost-of-pass)**: 로그로 task success를 볼 수 없다. 저토큰=우수로 단정 금지(session-5).
- **현행 가격, 갱신 가능**: 두 스크립트의 가격표는 동기화(test로 핀). 새 모델은 `--pricing`으로.
- **낭비는 세션 실제 모델가로**: 혼합 플릿을 플랫 Opus로 과대계상하지 않는다.
- **giant-tool fix는 blind 절단 금지**: Squeez(Last-N 0.05 recall) — 작게 요청·stale 마스킹.
- **compact엔 캐시-깨짐 caveat**: 과도한 compact는 35% 캐시 축을 낮춘다(ACON/session-2).
- **점수·KPI는 메인 스레드, 비용은 분리**: 서브에이전트(별도 파일)는 점수·토큰·캐시 KPI·`cost_usd`(메인 세션)에서 제외하고 `subagent_cost_usd`로 분리 보고 — 서브에이전트 볼륨이 4축 점수를 오염시키지 않게. message.id당 usage 1회 계상(분할 레코드 방지). 날짜접미사 모델 ID 정규화.
- **경로 인코딩은 비영숫자 전부 `-`**: `.`·`_` 포함(실물 디렉토리 대조) — 외부 스킬은 `/`만 치환해 실패.
- **대시보드는 오프라인/CSP 안전**: 인라인 SVG, CDN 의존 없음.
- **경계**: 런타임 세션 로그의 토큰 경제만. 정적 저장소 AI 준비도(ai-readiness-cartography·상보), 새 코드·PR 리뷰(frontend/git-harness), 하네스 진단(meta-harness), AI 생성물 judge(eval-harness), 컨텍스트 조립(context-engineering)은 범위 밖.
- 단일 스킬 플러그인이므로 에이전트 팀(agents/)을 두지 않는다 — 로그 분석기 본성에 충실.

## Change History

변경 이력은 [CHANGELOG.md](CHANGELOG.md)에 있다. 변경 시 그 표 맨 위에 행을 추가한다.
