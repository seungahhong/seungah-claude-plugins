# token-efficiency

Claude Code **세션 JSONL 로그**를 파싱해 레포 단위 **토큰/컨텍스트 효율**을 정량 측정·시각화하고 $ 절감안을 내는 결정론적 단일 스킬. `~/.claude/projects/<encoded>/*.jsonl`의 `usage` 필드만으로 별도 API 호출 없이 전체 비용 구조·캐시 효율·비효율 패턴을 재구성한다.

## 무엇을 하나

1. **4축 가중 점수** (cache 35% / redundancy 30% / density 15% / tool 20%) — 각 축에 근거 등급(CONFIRMED/PLAUSIBLE/HEURISTIC).
2. **8개 비효율 탐지기** — context-bloat · giant-tool-outputs · poor-cache-util · duplicate-tools · subagent-overuse + 신규 **stale-observation · cache-invalidation-churn · read-exploration-heavy**.
3. **세션별 실제 모델가 기반 낭비 추정** (플랫 Opus 폐기).
4. **오프라인/CSP 안전 HTML 대시보드** (인라인 SVG, CDN 의존 없음).

## 사용법

```bash
S=plugins/token-efficiency/skills/token-efficiency/scripts
python3 $S/analyze_sessions.py --repo "$(pwd)" --out /tmp/sa.json
python3 $S/detect_patterns.py  --repo "$(pwd)" --out /tmp/pa.json
python3 $S/build_dashboard.py  --input /tmp/sa.json --patterns /tmp/pa.json --out /tmp/report.html
open /tmp/report.html
```
테스트: `cd $S && python3 -m unittest test_efficiency -v` (60건).

## 외부 스킬 대비 개선 (근거 기반)

이 플러그인은 외부 스킬 `improve-token-efficiency`를 기반으로, `deep-research`(5 세션 적대 검증)로 수집한 2025~2026 1차 근거로 개선했다. 전체 dossier는 [`skills/token-efficiency/references/research/`](skills/token-efficiency/references/research/README.md).

| 변경 | 근거 |
|------|------|
| PRICING 현행화 (Opus $15/$75 폐기가 → $5/$25, Fable 5 추가, 캐시배수 입력가 파생) | session-2 (Anthropic 1차) |
| giant-tool fix 교정 — blind head/tail 절단 금지 | Squeez arXiv:2604.04979 (Last-N 0.05 recall) |
| 신규 stale-observation 탐지기 | AgentDiet 2509.23586 "expired" + Complexity Trap 2508.21433 |
| 신규 cache-invalidation-churn 탐지기 | session-2 exact-prefix 캐싱 |
| 신규 read-exploration-heavy + redundancy 축 0.20→0.30 | arXiv:2606.14066 (읽기 76.1%) |
| model-routing을 세션별 후보 판별로 (플랫 30% 폐기) | cost-of-pass 2508.02694 (작업 의존) |
| compact 권고에 캐시-깨짐 caveat | ACON 2510.00615 |
| 점수=효율 프록시(≠cost-of-pass) 명시 | cost-of-pass 2508.02694 |
| 대시보드 CDN 제거(인라인 SVG) · 테스트 신설 | 구현 품질 |

## 경계

- **측정·시각화·제안만.** 코드를 자동 수정하지 않는다.
- **런타임 세션 로그**의 토큰 경제를 잰다. 정적 저장소의 AI 준비도는 `ai-readiness-cartography`(상보).
- 새 코드·PR 리뷰(frontend/git-harness), 하네스 진단(meta-harness), AI 생성물 judge(eval-harness), 컨텍스트 조립(context-engineering)은 범위 밖.
