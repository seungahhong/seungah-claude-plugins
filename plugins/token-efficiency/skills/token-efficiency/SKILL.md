---
name: token-efficiency
description: Claude Code 세션 JSONL 로그를 파싱해 레포 단위 토큰/컨텍스트 효율을 정량 측정·시각화하고 $ 절감안을 내는 결정론적 스킬. 4축 가중 점수(cache/redundancy/density/tool)와 8개 비효율 탐지기(context-bloat·giant-tool·poor-cache·duplicate·subagent + 신규 stale-observation·cache-invalidation-churn·read-exploration-heavy), 세션별 실제 모델가 기반 낭비 추정, 오프라인/CSP 안전 HTML 대시보드를 생성한다. '토큰 효율 분석', '세션 효율', '비용 분석', 'Claude Code usage report', 'analyze token efficiency', 'show session cost', 'improve token efficiency', 'efficiency score', 'how much did I spend on Claude', 'session report', '캐시 적중률', '토큰 낭비' 등에 반드시 트리거. 단일 세션이 아니라 여러 세션 전체의 집계·점수화·시각화가 필요할 때. 새 앱 코드 작성·PR 리뷰·하네스 진단에는 트리거하지 않는다.
allowed-tools: Bash, Read
---

# Token Efficiency

Claude Code가 `~/.claude/projects/<encoded-repo-path>/*.jsonl`에 남기는 세션 로그를 파싱해서, 레포 단위로 **토큰 사용·캐시 효율·비용·점수**를 집계하고 **비효율 패턴 + $ 절감안**을 제시하는 HTML 대시보드를 만든다.

외부 스킬 `improve-token-efficiency`를 기반으로, deep-research(5 세션 적대 검증)로 수집한 2025~2026 1차 근거로 개선한 버전이다. 근거는 [`references/research/`](references/research/README.md) 참조.

왜 JSONL을 직접 파싱하는가: CLI가 세션당 모든 assistant 메시지의 `usage` 필드(`input_tokens`, `output_tokens`, `cache_creation.ephemeral_5m/1h`, `cache_read_input_tokens`)를 기록한다. 별도 API 호출 없이 레포 전체 비용 구조를 재구성할 수 있다.

## 핵심 원칙 (정직성)

- **점수는 효율 프록시일 뿐 cost-of-pass가 아니다.** 로그로는 task success를 볼 수 없으므로, 저토큰 세션이라도 실패했다면 "우수"가 아니다(cost-of-pass, session-5). 저토큰=우수로 단정하지 않는다.
- **결정론 우선, 제안만.** 스크립트(stdlib only, Python 3.9+)가 자동 채점·탐지하고, 코드를 자동 수정하지 않는다. 측정·시각화·제안만.
- **낭비 $는 세션 실제 모델가로.** 혼합 Sonnet/Haiku 플릿을 플랫 Opus로 과대계상하지 않는다.
- **추정치는 실행 전 값.** 절감 $는 휴리스틱 추정. "실행 후 재측정"이 원칙(frontier cost-of-pass는 수개월마다 반감).

## 동작 흐름

### 1. 대상 레포 결정
사용자가 경로를 명시했으면 그것을, 아니면 `pwd`를 기준으로 삼는다. 스크립트가 `~/.claude/projects/<encoded>/` 변환을 자동 처리(예: `/Users/x/Foo` → `-Users-x-Foo`). 사용자 확인 불필요.

### 2. 세션 분석 실행 (점수화)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/token-efficiency/scripts/analyze_sessions.py \
    --repo "$(pwd)" --out /tmp/session_analysis.json
```
- `--repo` 없으면 cwd. `--sessions-dir`로 직접 지정 가능.
- `--pricing pricing.json`으로 가격표 오버라이드(새 모델 출시 대응).
- `--weights cache=0.35,redundancy=0.30,density=0.15,tool=0.20`으로 가중치 조정.
- 빈 세션(usage 0)은 자동 제외.

**4축 점수(가중 합, 각 축에 근거 등급):**

| 축 | 기본 가중치 | 근거 등급 | 측정 |
|---|---|---|---|
| **cache** | 35% | CONFIRMED (session-2) | `cache_read / total_input`, 0.85+ 만점. 캐시 read 0.1× vs 입력 1.0× |
| **redundancy** | 30% | PLAUSIBLE (session-3) | 같은 파일 반복 Read 비중. 읽기가 코딩 에이전트 토큰의 76.1%(2606.14066) → cache와 동급 |
| **density** | 15% | HEURISTIC | `output/input` ~2% 적정. 성공률 인과 근거 없음 → 저가중 |
| **tool** | 20% | HEURISTIC | 출력 1k당 도구 호출 수, 2–10 건강 |

등급: A+≥90 · A≥85 · A-≥80 · B+≥75 · B≥70 · B-≥65 · C+≥60 · C≥55 · C-≥50 · D≥40 · F<40.

### 3. 비효율 패턴 탐지 (8개 결정론 탐지기)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/token-efficiency/scripts/detect_patterns.py \
    --repo "$(pwd)" --out /tmp/pattern_analysis.json
```

| # | 탐지기 | 근거 | 신규 |
|---|--------|------|------|
| 1 | context-bloat (100k+ 20턴 지속) | ACON 2510.00615 (품질 harm) | |
| 2 | giant-tool-outputs (50k+ chars) | Squeez 2604.04979 (fix 교정: **blind 절단 금지**) | |
| 3 | poor-cache-util (hit<50% @ 30k+) | session-2 (exact-prefix 경제학) | |
| 4 | duplicate-tools (SHA-256 동일) | AgentDiet "redundant" 2509.23586 | |
| 5 | subagent-overuse (5+ 사소 위임) | Context-Folding 2510.11967 (folded vs unfolded) | |
| 6 | **stale-observation** (완료 후 잔존) | AgentDiet "expired" + Complexity Trap 2508.21433 (~52% 절감) | ✅ |
| 7 | **cache-invalidation-churn** (프리픽스 흔들림) | session-2 (exact-prefix) | ✅ |
| 8 | **read-exploration-heavy** (읽기 지배+재읽기) | arXiv:2606.14066 (읽기 76.1%) | ✅ |

낭비 $는 각 세션의 dominant 모델가로 산정(read 0.1× / write5m 1.25× / write1h 2× 배수).

### 4. 대시보드 생성 (오프라인/CSP 안전)
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/token-efficiency/scripts/build_dashboard.py \
    --input /tmp/session_analysis.json \
    --patterns /tmp/pattern_analysis.json \
    --out /tmp/efficiency_report.html
open /tmp/efficiency_report.html
```
인라인 SVG로 렌더(외부 CDN/스크립트 의존 없음 — 원 스킬의 Chart.js CDN 의존을 제거). KPI 카드, 카테고리별 비용, 등급 히스토그램, 근거 등급이 붙은 Rubric, Top 20 세션, 패턴별 낭비 표, 6종 개선 카드(세션별 라우팅·캐시-깨짐 caveat 포함).

### 5. 사용자 보고
HTML을 연 뒤 한국어로 최상위 수치와 가장 큰 개선 3가지를 2–3줄 요약. 예:
> 106 세션 / $412 / 평균 B+. 상위 14개가 비용의 63%. 최대 낭비는 **읽기 탐색 과다($X)·거대 도구 출력($Y)·캐시 저조($Z)**. 저난도 세션 N개는 Sonnet 라우팅 후보. **점수는 효율 프록시이며 작업 성공률은 반영하지 않는다.**

## 검증 (테스트)
```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/token-efficiency/scripts && python3 -m unittest test_efficiency -v
```
가중치 합·양방향 가격 동기화·탐지기 회귀·세션별 모델가·message.id 중복제거·서브에이전트 파일 수집·대시보드 esc/성분합·CLI 오류 경로를 핀한다.

## 보고 시 주의 (정보 노출)
JSON·HTML 산출물에는 절대경로·OS 사용자명(예: `sessions_dir`)이 포함된다. 대시보드를 외부(PR·Slack)로 공유하면 사용자명·로컬 디렉토리 구조가 노출되니 공유 전 확인한다.

## 에지 케이스
- **세션 디렉터리 없음**: 레포가 Claude Code로 열린 적 없음 → "분석할 세션 없음" 안내 후 종료.
- **모든 세션 빈 usage**: 오래된 CLI → 자동 필터, 남은 게 없으면 종료.
- **미등록 모델 가격**: Opus-tier 기본 적용 + `[warn]`. `--pricing`으로 갱신.
- **짧은 프리픽스 세션**: 최소 캐시 프리픽스(Opus·Haiku 4.5 = 4096 / Fable 5·Sonnet 4.6 = 2048 / Sonnet 4.5 이하 = 1024 토큰) 미만은 캐시 자체가 불가 — 낮은 cache 점수를 "낭비"로 오인하지 말 것(session-2). 대시보드 footer에도 명시.
- **서브에이전트(사이드체인) 비용은 분리 보고**: 현행 CLI는 서브에이전트 궤적을 세션 인라인이 아니라 `<세션ID>/subagents/**/*.jsonl` 별도 파일에 저장한다. analyze_sessions는 이 파일들을 재귀 수집해 **`subagent_cost_usd`로 별도 보고**한다. **점수·토큰·캐시 KPI·`cost_usd`는 메인 스레드(인터랙티브 세션) 기준**이며, 서브에이전트 볼륨이 점수축을 오염시키지 않는다. 대시보드 비용 KPI에 "서브에이전트 +$X"로 표기(`num_subagent_files`·`num_sidechain_msgs` 보고). 서브에이전트 모델 ID의 날짜 접미사(`-YYYYMMDD`)는 정규화해 정확 산정한다.
- **message.id 중복제거**: CLI는 한 API 메시지(1개 message.id·1개 usage)를 thinking/text/tool_use 레코드로 분할 기록하며 usage를 반복한다. 두 스크립트 모두 message.id당 usage를 **1회만** 계상한다(레코드 단위 합산 시 비용·턴이 2~3배 부풀음). tool_use 블록은 전 레코드에서 수집한다.
- **합성·빈 레코드**: `<synthetic>` 모델·컨텍스트 0인 API-에러 레코드는 탐지기 궤적에서 제외(bloat run·carried-turn 왜곡 방지).

## 경계
- **측정·시각화 전용.** 코드 자동 수정 없음. 새 앱 코드·PR 리뷰·버그 찾기(frontend/git-harness), 하네스 자체 진단(meta-harness), AI 생성물 평가 judge(eval-harness), 컨텍스트 페이로드 조립(context-engineering)은 범위 밖.
- **코드베이스 AI 준비도** 측정은 `ai-readiness-cartography`(정적 저장소 스코어러). 이 스킬은 **런타임 세션 로그**의 토큰 경제를 잰다 — 상보적.
