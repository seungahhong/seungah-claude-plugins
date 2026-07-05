# 세션 3 — tool-call 궤적 효율·redundant action 탐지

> 조사 렌즈: duplicate-tools / subagent-overuse / read 축 + 신규 탐지기를 궤적-낭비 실증으로 근거화. "궤적 낭비는 어떻게 분류되나", "어느 tool이 토큰을 쓰나", "task-aware 프루닝이 필요한가".
> 상태: deep-research 각도 3, 적대 검증 완료 (2026-07-04). 주요 확인: AgentDiet 3분류·읽기 76.1% 지배·SWE-Pruner task-aware 우위.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | AgentDiet: 궤적 낭비 3분류 = useless / redundant / expired; 입력토큰 39.9~59.7%·총비용 21.1~35.9% 절감·동일 성능 |
| C2 | **CONFIRMED** | 읽기 연산이 코딩 에이전트 토큰의 76.1% (execute 12.1% / edit 11.8%) |
| C3 | **CONFIRMED** | SWE-Pruner: SWE-bench Verified에서 23~38% 토큰 절감·성공률 노이즈 내 동등 |
| C4 | **CONFIRMED** | generic/token-level 압축은 코드 성공률을 떨어뜨림(LLMLingua2 62→54%) — task-aware 필요 |
| C5 | **CONFIRMED** | naive 관측치 마스킹(stale)은 예외적으로 Pareto-우수(Complexity Trap, session-1 C8과 정합) |

## 검증된 핵심 발견

**궤적 낭비는 3종으로 분리된다(AgentDiet, C1):**
- **useless** — 작업 무관(예: 파일 목록의 `__pycache__` 엔트리)
- **redundant** — 스텝 간 반복(예: edit-tool 인자가 앞서 조회한 코드를 반복)
- **expired** — 서브태스크 완료 후 폐기(예: 결함 파일 식별 후 다른 파일들의 내용)

원 스킬의 duplicate-tools(SHA-256 동일 호출)는 **redundant의 극단(정확 중복)만** 잡는다. useless는 애초 작게 요청하는 문제(giant-tool), **expired는 신규 stale-observation 탐지기**로 포착한다.

**읽기가 지배적이다(C2).** read-type 연산이 코딩 에이전트 총 토큰의 **76.1%** (execute 12.1%, edit 11.8%). 반복 코드베이스 탐색 때문. → redundancy 축을 cache와 동급(0.30)으로 올리고 read-exploration 탐지기를 신설할 강한 근거.

**프루닝은 task-aware여야 한다(C3·C4).** SWE-Pruner는 SWE-bench Verified에서 Claude Sonnet 4.5 70.6%→72.0%(+노이즈)·23.1% 토큰 절감, GLM-4.6 38.3% 절감. 반면 generic 압축(LLMLingua2·RAG·LongCodeZip)은 성공률을 **떨어뜨린다**(62%→54%). AST 정확도는 token-level 압축에서 0.29~12.4% vs task-aware 87.3%. → "무조건 압축/요약"이 아니라 "task-aware 프루닝" 또는 "stale 마스킹"만 안전.

## 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** "AgentDiet can reduce input tokens by 39.9%-59.7% and the total computational cost by 21.1%-35.9%, while maintaining the same agent performance." 궤적 낭비 taxonomy(useless/redundant/expired), 슬라이딩-윈도우 reflection 모듈(임계값 θ) — AgentDiet, **arXiv:2509.23586**.
- **[C2 · CONFIRMED]** "coding agents spend token budget overwhelmingly on repeated codebase exploration: read-type operations consume 76.1% of total tokens vs execute 12.1% and edit 11.8%." — **arXiv:2606.14066**(2026-06). read-redundancy 축 가중치의 정량 정당화.
- **[C3 · CONFIRMED]** SWE-Pruner: SWE-bench Verified 23.1%(Claude Sonnet 4.5)·38.3%(GLM-4.6) 토큰 절감, 성공률 ±1pp(노이즈 내), 에이전트 라운드 18~26%↓ — "SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents", **arXiv:2601.16746**(v4 2026-05). ※ "23~54%"의 54%는 SWE-QA(다른 태스크)이며 SWE-bench Verified는 23~38%.
- **[C4 · CONFIRMED]** token-level 압축(LLMLingua2)은 SWE-bench 성공률 62%→54%, AST 정확도 near-zero; generic LLM 요약도 56% vs task-aware 64% — SWE-Pruner. "fixed-metric 압축은 코드 구조를 깨므로 task-aware 필요"(단 stale 마스킹은 예외, C5).
- **[C5 · CONFIRMED]** naive placeholder 마스킹(오래된 tool 출력 생략)은 코드 콘텐츠 압축이 아니라 재조회 가능한 관측치를 통째 드롭 → Pareto-우수(Complexity Trap 2508.21433). session-1 C8과 정합, "generic 압축 나쁨"의 예외.

## 이 스킬에 반영 (매핑)

- **read-exploration-heavy 탐지기 신설(C2)**: read-type tool이 전체 호출의 60%+ AND 중복 재읽기 존재 시 플래그. fix는 "Grep/Glob으로 위치 먼저 → 라인범위 Read → 이미 읽은 파일 재읽기 금지". research에 76.1% 인용.
- **redundancy 축 0.20 → 0.30(C2)**: 읽기가 최대 토큰 소비원이므로 cache(0.35)와 동급으로.
- **stale-observation 탐지기 신설(C1 expired·C5)**: 서브태스크 완료 후 잔존 관측치. duplicate-tools(redundant)와 상보.
- **subagent-overuse 유지·프레이밍(session-1 C6)**: 사소 위임의 오버헤드는 실측 근거 없으나 folding 근거로 "요약 반환 위임"을 권장.
- **낭비 $는 세션 모델가로(C3)**: SWE-bench가 Sonnet/GLM 등 다양한 모델 → 플랫 Opus 폐기.

### 바꾸지 말 것
- "N개 중복 = X% 하락" 정량 감점 — 근거 없음. 중복 개수·추정 토큰만 보고.
- generic 요약을 절감 근거로 — 코드에서 성공률 하락(C4).

## 소스 (검증 상태)
- AgentDiet — arXiv:2509.23586 (3분류·39.9~59.7% 절감 확인)
- 읽기 76.1% — arXiv:2606.14066 (수치 확인)
- SWE-Pruner — arXiv:2601.16746 (v4, SWE-bench Verified 23~38% 확인; 54%는 SWE-QA로 분리)
- The Complexity Trap — arXiv:2508.21433 (NeurIPS 2025 workshop, stale 마스킹 Pareto)
- Squeez — arXiv:2604.04979 (관측치 프루닝, session-1 상술)
