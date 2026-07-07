# token-efficiency

Claude Code **세션 JSONL 로그**를 결정론적 스크립트로 파싱해 레포 단위 **토큰/컨텍스트 효율**을 정량 측정·시각화하고 $ 절감안을 내는 단일 스킬. 외부 스킬 `improve-token-efficiency`를 deep-research(5 세션 적대 검증)의 2025~2026 1차 근거로 개선한 버전.

사용자용 개요·사용법은 [README.md](README.md), 근거는 [references/research/](skills/token-efficiency/references/research/README.md) 참조.

## Structure

```
token-efficiency/
├── .claude-plugin/plugin.json
├── CLAUDE.md                        # (이 문서) 포인터 + 원칙 + 변경 이력
├── README.md                        # 사용자용 개요·사용법·개선표·경계
├── skills/token-efficiency/
│   ├── SKILL.md                     # 오케스트레이터(analyze → detect → dashboard)
│   ├── scripts/
│   │   ├── analyze_sessions.py      # 4축 가중 점수 + 현행 PRICING(입력가 파생 캐시배수) + --pricing/--weights
│   │   ├── detect_patterns.py       # 8개 탐지기(5 기존 + 3 신규), 사이드체인 배제, 세션별 모델가 낭비 산정, --pricing
│   │   ├── build_dashboard.py       # 오프라인/CSP 안전 인라인-SVG HTML(모델별 비용 성분·세션별 라우팅·캐시 caveat)
│   │   └── test_efficiency.py       # 회귀 테스트(61건 — 양방향 가격 동기화·탐지기·사이드체인·golden·인코딩)
│   └── references/research/         # 2025~2026 1차 근거(README + 5 세션, 적대 검증)
└── evals/
    ├── evals.json                   # 수용 평가(불변식 file:함수 인용 + test 실행)
    └── trigger-eval.json            # 트리거 경계(should/should-not, 인접 도메인 가드)
```

## 4축 점수 요약 (가중치 · 근거 등급)

| 축 | 가중치 | 등급 | 측정 |
|----|--------|------|------|
| cache | 35% | CONFIRMED | cache_read ÷ 총 입력, 0.85+ 만점 (read 0.1× vs 입력 1.0×, session-2) |
| redundancy | 30% | PLAUSIBLE | 같은 파일 반복 Read (읽기=코딩 에이전트 토큰 76.1%, 2606.14066, session-3) |
| density | 15% | HEURISTIC | output/input ~2% 적정 (성공률 인과 근거 없음) |
| tool | 20% | HEURISTIC | 출력 1k당 도구 호출 수 |

등급(11단계): A+≥90 · A≥85 · A-≥80 · B+≥75 · B≥70 · B-≥65 · C+≥60 · C≥55 · C-≥50 · D≥40 · F<40.

## 8개 탐지기

context-bloat · giant-tool-outputs · poor-cache-util · duplicate-tools · subagent-overuse · **stale-observation(신규)** · **cache-invalidation-churn(신규)** · **read-exploration-heavy(신규)**. 낭비 $는 각 세션 dominant 모델가로.

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

| 날짜 | 변경 | 내용 |
|------|------|------|
| 2026-07-07 | detect 비-dict 레코드 크래시 수정 (v0.1.1) | 보안·강건성 검토(재현 검증) — 비-dict 최상위 JSONL 라인(`[1,2,3]` 등)이 detect_patterns의 sidechain 재스캔(`r.get`)에서 AttributeError로 세션 전체를 죽이던 것(analyze와의 강건성 비대칭)을 파싱 시점 dict 필터로 배제. 테스트 60→61건 |
| 2026-07-04 | 4관점 검증 R2 반영 | R2 4관점 워크플로가 실측으로 잡은 회귀(직전 서브에이전트-수집이 유발) 수정 — **점수축 오염**(비용은 서브 합산 맞으나 input/output/cache 토큰도 합산돼 cache·density는 main+sub, tool·redundancy는 main-only → 축 분모 불일치로 실측 3세션 등급 flip): **점수·토큰·캐시 KPI·cost_usd를 메인 스레드로 되돌리고 서브에이전트 비용은 subagent_cost_usd로 분리 보고**(대시보드 "서브에이전트 +$X"). **날짜접미사 모델 ID 오매칭**(서브 haiku-4-5-20251001을 Opus 5배로 오산정 $23 과대): normalize_model로 `-YYYYMMDD` 정규화(두 스크립트). **detect 손상레코드 크래시**(비-str message.id·비-dict message가 전체 실행 중단): 레코드 단위 try/except + 타입 가드. O_NOFOLLOW 도크스트링 POSIX 한정 명시·product-spec 카운트·analyze 트리 주석 nit. 테스트 52→60건. 실측: 메인 $717.75 + 서브에이전트 $832.35·경고 0·성분합=메인비용 |
| 2026-07-04 | 4관점 검증(보안·설계·구조·테스트) 반영 | 워크플로 4관점 병렬 적대 리뷰 + 발견별 반증 검증이 실제 로그 대조로 잡은 **HIGH 3건** 수정 — **message.id 중복제거**(CLI가 한 API 메시지를 thinking/text/tool_use 레코드로 분할·usage 반복 → 레코드 단위 합산 시 비용·턴 2~3배 과대; 실측 317레코드→182메시지, 두 스크립트 모두 message.id당 usage 1회 계상·tool_use는 전 레코드 수집), **서브에이전트 별도파일 수집**(현행 CLI는 `<sid>/subagents/**/*.jsonl`에 저장 → analyze가 재귀 수집해 비용 합산, SKILL의 "in-band 포함" 오기재 정정; redundancy·dominance는 메인 스레드만), **합성·빈 레코드 궤적 제외**(context 0·`<synthetic>`이 bloat run·carried-turn 파괴). MED — 라우팅 절감을 dominant 모델 비용 성분에 적용(혼합 모델 세션 과대 방지)·duplicate를 결과 해시까지 비교(git status dirty→clean류 정당 재확인 제외)·절감카드 무근거 상수 라벨(top-14·30%·40%·3k×10턴)·"agree on one number" 도크스트링 정정. LOW — poor-cache/churn 이중계상 overlap_note·캐시적중 KPI 값기반 색·grade 범례 11단계 통일(대시보드·CLAUDE.md)·parse_weights 미지 축 exit·stale 도크스트링 mid-sized·session-2 매핑 1.9→1.15 갱신·allowed-tools를 Bash·Read로 축소·root 표 순서(ai-readiness→token-efficiency)·인접 10개 trigger-eval 카운트 정정·meta-harness 가드 다중세션화·심볼릭링크 O_NOFOLLOW·공유 시 경로노출 caveat. 테스트 24→52건(message.id·서브에이전트·zero-usage·stateful·미발화 3탐지기·대시보드 5·CLI 오류·곡선 연속). 실측 파이프라인 35세션 $1543.64·성분합=KPI·서브에이전트 2524파일 OK |
| 2026-07-04 | R2 신선 재검증 반영 | 수정확인 체크리스트 16/16 PASS(VERIFIED) + 신선 스윕 발견 수정 — **detect의 usage:null/message:null 레코드 전체-실행 크래시**(analyze와 강건성 비대칭, 재현 후 `or {}`/`or 0` None-가드로 통일), --pricing 스키마를 두 스크립트 동일(in+out 필수)로 정렬, _docs/skills.md 잔존 "40% 캐시 축"→35%. 테스트 24건 |
| 2026-07-04 | R1 다각도 검토 반영 | 3관점 적대 리뷰(코드 정확성·보안 / 컨벤션·등록 / 인용 정직성) 발견 수정 — **encode_repo_path가 비영숫자 전부 `-` 치환**(외부 스킬은 `/`만 — `.`·`_` 경로에서 세션 디렉토리 해석 실패, 실물 대조 재현)·**사이드체인 레코드 궤적 배제**·**줄 단위 파싱**(절단 마지막 줄이 세션 탈락)·**대시보드 모델별 비용 성분**(Opus 고정가 분해가 KPI와 모순)·라우팅 후보 Opus급 이상 제한·poor-cache zero-cache 턴·carried-turns compact 절단·중복 배수 CW1H→CW5·XSS esc·detect --pricing·"40% 캐시 축" 스테일→35%·이미지 40k→4.8k·mythos-5 출처·SUBAGENT 3k HEURISTIC 라벨·테스트 16→24건 |
| 2026-07-04 | 플러그인 신설 (v0.1.0) | token-efficiency(세션 로그 토큰 효율 측정·시각화). 외부 스킬 `improve-token-efficiency`를 기반으로 deep-research(5 세션 적대 검증)의 2025~2026 근거로 개선 — PRICING 현행화(Opus $15/$75 폐기가→$5/$25·Fable 5 추가·캐시배수 입력가 파생), giant-tool fix 교정(blind 절단 금지: Squeez 2604.04979), 신규 탐지기 3종(AgentDiet 2509.23586 expired·session-2 exact-prefix churn·2606.14066 읽기 76.1%), redundancy 축 0.20→0.30, model-routing 세션별 후보 판별(cost-of-pass 2508.02694), compact 캐시-깨짐 caveat(ACON 2510.00615), 효율≠cost-of-pass 정직성, 대시보드 CDN 제거(인라인 SVG), test_efficiency 신설(16건). 근거: ACON(2510.00615)·Squeez(2604.04979)·AgentDiet(2509.23586)·SWE-Pruner(2601.16746)·Complexity Trap(2508.21433)·읽기 지배(2606.14066)·cost-of-pass(2508.02694)·Anthropic 캐싱 1차. |
