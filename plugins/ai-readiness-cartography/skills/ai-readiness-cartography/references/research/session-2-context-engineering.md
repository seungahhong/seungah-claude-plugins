# 세션 2 — 코딩 에이전트용 repository 문맥 엔지니어링(CLAUDE.md/AGENTS.md) 실증 효과·품질 기준·실패 모드

> 조사 렌즈: B(Context Document Quality)·C(Tribal Knowledge). B1 conciseness 목표 line 수, cross-ref·quick command 실효, "문서 많음 ≠ 좋음" 근거/반증.
> 상태: deep-research 각도 2, 적대 검증 완료 (2026-07-03). 지어낸 출처 없음 — 모든 핵심 arXiv ID·저자·연도·수치가 1차 자료(PDF 포함)와 일치. C9 절대 상한 확장 주장만 2차 경유로 완화.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | **CONFIRMED** | LLM 생성 context 파일이 성공률 저하(SWE-bench Lite −0.5%·AGENTBENCH −2%), 비용 +20% |
| C2 | **CONFIRMED** | human-written +4%·비용 +19%·태스크당 +3.92 스텝 |
| C3 | **CONFIRMED** | 해악 메커니즘 = repository overview가 grep·중복 테스트로 유도(distraction) |
| C4 | **CONFIRMED** | 에이전트가 지침 강박 준수 — 도구 언급 시 호출 0.05→2.5회, reasoning token +14~22% |
| C5 | **CONFIRMED** | context는 undocumented repo에서만 순이득 — **novelty가 핵심 변수** |
| C6 | **CONFIRMED** (효율 축 반증) | AGENTS.md가 runtime −28.64%·output token −16.58% (효율은 개선) |
| C7 | **CONFIRMED** | context rot — 18개 frontier 모델서 길이 증가 시 비균일 저하 |
| C8 | **CONFIRMED** | lost-in-the-middle — 정보가 중간이면 성능 급락(TACL 2023) |
| C9 | PLAUSIBLE | 지침 밀도↑ → 준수 저하(500 지침서 최고 68%), "150–200 peak"·"2,000 확장"은 2차 경유 |
| C10 | **CONFIRMED** | AGENTS.md → 2025-12-09 Linux Foundation AAIF 기증(벤더 무관 표준화) |

## 검증된 핵심 발견

2026년 초 두 편의 통제 실험이 "repository context 파일이 에이전트를 더 잘 만든다"는 통념을 정면으로 흔들었다. ETH Zurich(arXiv:2602.11988)는 SWE-bench Lite + 자체 AGENTBENCH(138 태스크)에서 **LLM 생성 context 파일이 task success를 오히려 낮추고(−0.5%/−2%) inference cost를 평균 20%+ 올렸으며**, 개발자 손수 작성본조차 성공률 +4%에 비용 +19%·태스크당 +3.92 스텝을 냈다 — 핵심 실패 메커니즘은 repository overview가 에이전트를 불필요한 grep·파일 읽기·중복 테스트 루프로 몰아넣는 **"distraction"**.

**효율 축 반증**: 같은 시기 Lulla et al.(arXiv:2601.20404, ICSE 2026 JAWs)은 124개 실제 PR에서 AGENTS.md가 wall-clock runtime을 중앙값 28.64%·output token을 16.58% *줄였다*고 보고 → "성공률/비용 vs 실행 효율"은 서로 다른 축.

가장 견고한 합의:
- (a) 에이전트가 지침을 거의 강박적으로 따르므로 **불필요·중복 지침이 순비용**(도구 언급 시 호출 instance당 0.05→2.5회 폭증).
- (b) context가 이미 코드베이스에서 discoverable한 정보를 중복하면 이득 0이며, **novel·비자명 정보일 때만 modest 이득**.

### 검증 가능한 주장 (판정 태그 포함)

- **[C1 · CONFIRMED]** SWE-bench Lite + 신설 AGENTBENCH(138)에서 LLM 생성 context 파일이 success 저하(−0.5%/−2%), cost 평균 20%+ 증가 — Gloaguen·Mündler·Müller·Raychev·Vechev(ETH Zurich/LogicStar.ai), **arXiv:2602.11988**, 2026-02. (여기 "AgentBench"는 기존 벤치가 아니라 본 논문 신설 스위트.)
- **[C2 · CONFIRMED]** human-written 파일도 +4%에 그치며 비용 +19%·태스크당 +3.92 스텝 — 동.
- **[C3 · CONFIRMED]** 주된 해악 = repository overview가 grep·파일 읽기·중복 테스트 루프 유도(모델 제공사 권장에도 무익) — 동(trace 분석).
- **[C4 · CONFIRMED]** 도구 언급 시 호출 0.05→2.5회, GPT-5.2/5.1 Mini는 context 있을 때 reasoning token +22%/+14% — 동(PDF 직접 확인).
- **[C5 · CONFIRMED]** context는 "완전히 문서화되지 않은 repo"에서만 순이득, 잘 관리된 repo에서는 token만 낭비 — novelty가 핵심 변수 — 동.
- **[C6 · CONFIRMED · 효율 축 반증]** 124 PR·10 repo에서 AGENTS.md가 runtime −28.64%·output token −16.58%, 완료 품질 유사 — Lulla et al., **arXiv:2601.20404**, 2026-01(ICSE 2026 JAWs). success/cost가 아닌 runtime/token 축 — 순비용 방향은 미해결.
- **[C7 · CONFIRMED]** context rot — 길이↑ 시 단순 retrieval에서도 비균일 저하, distractor 1개로도 저하. 18개 frontier 모델(Claude 4·GPT-4.1·Gemini 2.5·Qwen3) 전부 — Hong·Troynikov·Huber(Chroma), 2025-07-14.
- **[C8 · CONFIRMED]** lost-in-the-middle — 관련 정보가 처음·끝이면 최고, 중간이면 급락 — Liu et al., TACL 2023(vol.12, 157–173), **arXiv:2307.03172**.
- **[C9 · PLAUSIBLE]** frontier 모델은 지침 밀도↑ 시 준수 저하(최고 모델도 500 지침서 68%), primacy bias·모델별 decay — Jaroslawicz et al., IFScale, **arXiv:2507.11538**, 2025. "150–200 peak"·"2,000 확장"은 2차 경유 미확정.
- **[C10 · CONFIRMED]** AGENTS.md는 2025-08 공식화 후 2025-12-09 Linux Foundation AAIF에 MCP·goose와 함께 기증되어 벤더 무관 표준화. CLAUDE.md는 Anthropic 관례 — linuxfoundation.org·openai.com·anthropic.com·TechCrunch. "6만 repo" 수치만 시점 의존.

## Rubric v3 함의

- **A(Navigation) 하향 + novelty 게이트** (C1·C5). 커버리지 %를 만점 신호로 쓰지 말고 "코드베이스에서 이미 discoverable하면 감점".
- **B(Context Quality) 최우선 개편** (C3·C4·C5·C6):
  - 절대 line 수 목표 → **redundancy ratio**(문서 문장 중 코드/설정/README에서 자동 추출 가능한 비율)로 교체.
  - repository overview/아키텍처 산문의 부재·최소화를 *가점*(C3: overview가 능동적 해악).
  - quick command·exact shell invocation·"done" 검증 기준을 B 최고 배점으로.
  - "150–200줄" 문구 삭제(C9의 150–200은 *지침 개수*지 줄 수 아님).
- **C(Tribal Knowledge) 강화** — Five-Question은 C5와 정합. "MEMORY/ADR 존재" 이진 가점 → **비자명·비discoverable 지식 비율**로 채점.
- **D** — 방대한 산문·다이어그램 통째 게재는 distractor(C3·C7) → 산문 분량이 아니라 구조화·조회 가능한 dependency 신호에 가점.
- **E 유지·상향** — E1(hallucinated path 0)은 C4(경로 문자 신뢰) 때문에 더 중요.
- **G 배점 대폭 상향(5→15 권장)** — 문서 품질은 오직 실측(success·cost·token·runtime)으로만 판정 가능(C1·C2·C6).
- **신설 후보 "Cost/Context Discipline"** — context 有/無 token·step delta가 순증이면 감점(C1·C4·C7). G에 흡수 가능.
- **과잉 일반화 금지**: "redundancy 제거·novelty·command-first"는 강한 근거, **"무조건 짧게=성공률↑"는 미해결**(C6이 C1과 상충)로 분리.

## 소스 (전부 실재 확인)

- Evaluating AGENTS.md — Gloaguen et al.(ETH Zurich/LogicStar.ai), arXiv:2602.11988, 2026-02 (abs+PDF, 수치 확인)
- On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents — Lulla et al., arXiv:2601.20404, 2026-01, ICSE 2026 JAWs
- Context Rot — Hong·Troynikov·Huber(Chroma), 2025-07-14, trychroma.com/research/context-rot
- Lost in the Middle — Liu et al., TACL 2023(vol.12, 157–173), arXiv:2307.03172 (피어리뷰)
- IFScale (How Many Instructions Can LLMs Follow at Once?) — Jaroslawicz et al., arXiv:2507.11538, 2025-07 (150–200·2,000 세부는 재확인 권장)
- Linux Foundation AAIF press, 2025-12-09 — linuxfoundation.org/openai.com/anthropic.com/TechCrunch
- agents.md (표준 사이트) — 6만 repo 수치는 시점 의존
