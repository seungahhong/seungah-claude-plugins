# 자가치유(Self-Healing) 하네스 — 종합 연구 보고서

> 목적: 하네스(Claude Code 멀티 에이전트 스킬/오케스트레이터 플러그인)가 실행 중 **진행현황·실패·사용자 피드백을 `.md`로 적재**하고, 그 데이터로 **스스로 결함을 진단·교정(self-healing)** 하는 패턴을, 검증된 2023–2026 출처에 근거해 정리한다. 각 하네스에 모듈로 추가하는 아키텍처까지 포함한다.
>
> 방법: deep-research 하네스(5개 앵글 · 22개 소스 · 108개 주장 추출 → 3표 적대 검증 25개, **24 confirmed / 1 refuted**). 추론 다리(inference)는 명시 표시.
> 작성일: 2026-06-18.

---

## 0. 핵심 결론

`.md`에 진행·실패·피드백을 적재해 스스로 고치는 하네스는 **검증된 `감지→반성→저장→재시도` 루프**(Reflexion) 위에 짓고, `.md` 저장소는 **CoALA 메모리 분류**(원본 episodic 트레이스 ↔ 증류 semantic 교훈 분리)로 구조화한다.

단 — **연구가 가장 강하게 경고하는 지점** — *반성/자기교정만으로는 성능이 오히려 퇴화*할 수 있다(arXiv:2310.01798). 따라서 `.md` 저장소는 **필요하지만 불충분**하며 반드시 다음과 짝지어야 한다:
1. **외부 검증** (테스트/검증기 — "초록불" 통과만으론 부족, overfit)
2. **Pareto 비후퇴 체크** (패치가 과거 성공을 깨지 않는지)
3. **인간 승인 게이트** (자동 적용 금지)

그리고 **이 저장소는 이미 `meta-harness`에 그 아키텍처를 갖고 있다** — 빠진 건 엔진이 아니라 *각 하네스가 평소에 신호를 자동 적재하는 공통 쓰기 규약*이다.

---

## 1. 검증된 self-healing 루프 설계 패턴 *(하위질문 1)*

| # | 발견 | 신뢰 | 근거 |
|---|------|:---:|------|
| F1 | **`감지→반성→저장→재시도`** — 실패 시 피드백을 언어로 반성하고 그 반성문을 **episodic memory 버퍼**에 적재해 다음 시도 개선 | high (3-0) | Reflexion, NeurIPS 2023 (arXiv:2303.11366): *"verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer"* |
| F2 | **3-모듈 골격** = **Actor**(행동) · **Evaluator**(채점=감지) · **Self-Reflection**(언어 반성=진단/교정) → detect→diagnose→correct→re-act에 1:1 대응 | high (3-0) | 동 논문 |
| F5 | **distill = retrieve-then-reason**: 원본 episodic 트레이스를 검색→추론해 상위 교훈(reflection)을 **semantic memory에 기록** | high (3-0) | CoALA(arXiv:2309.02427) + Generative Agents(arXiv:2304.03442) |

> 당신 `meta-harness`의 "why-first causal 진단", `loop-engineering`의 `Fail→Investigate→Verify→Distill→Consult`가 이 패턴이다.

## 2. `.md` 메모리/경험 저장소 설계 *(하위질문 2 — 가장 실무적)*

| # | 발견 | 근거 |
|---|------|------|
| F3 | **CoALA 4-메모리 분류**: working(현재 사이클) · **episodic**(원본 트레이스) · **semantic**(지식/교훈) · procedural(코드). → 원본 트레이스와 증류 교훈을 *파일로 분리* | arXiv:2309.02427 (TMLR 2024) |
| F4 | 데이터를 쓸모있게 만드는 메커니즘 = **'Learning' = working→episodic 쓰기**. ⚠️ *"may be retrieved"*(보장 아님 — 무관 컨텍스트는 해로움) | 동 |
| F6 | **episodic 스키마 5속성**: 장기저장 · 내용추론 · single-shot · 인스턴스별 시간맥락 · **when/where/why 바인딩** | arXiv:2502.06975 |
| F7 | **요약만 말고 풀 트레이스 보존**: episodic의 가치는 단일 인스턴스 특이성·맥락이며 *semantic 요약이 그걸 잃는다*(둘 다 두되 원본 필수) | 동 (Tulving 1972) |
| F8 | **단일 메커니즘 대체 불가**: long-context(이력 폭증 취약)·RAG(관계/맥락 결여)·fine-tune(single-shot 불가) | 동 |
| F9 | **A-MEM 구조화 노트 스키마**(직접 이식 가능): `content · tags · category · timestamp · context · keywords · ID · links` | arXiv:2502.12110 |
| F10 | **링크 + memory evolution**: 새 메모리가 과거와 자동 연결(Zettelkasten), 기존 노트 갱신. ⚠️ 매 항목 실행은 비용/지연 → 선택적 | 동 |
| F11 | 멀티에이전트면 타입 세분화 + **메모리 전담 에이전트**: MIRIX 6타입 + **Meta Memory Manager** 라우팅 | arXiv:2507.07957 |

> ⚠️ **"append-only"는 보편 표준이 아니라 권고**다. A-MEM은 *진화하는* 메모리를 권한다. 당신 `MEMORY.md`의 `[[name]]` 링크가 F9·F10이다.

## 3. 두 참조 구현의 구체 메커니즘 *(하위질문 3)*

**Microsoft Playwright Test Agents** (playwright.dev/docs/test-agents):
- **F12 — `.md` 핸드오프 3단계**: **Planner**(앱 탐색→`specs/*.md` 계획) → **Generator**(계획→실행 테스트, 셀렉터/단언 라이브 검증) → **Healer**(실패 수리). 데이터를 Markdown/테스트 파일로 전달.
- **F13 — Healer = detect→diagnose→correct→verify**: 실패 스텝 재생 → UI 검사로 동등 요소 탐색 → 패치 제안(로케이터/대기/데이터) → **통과하거나 guardrail이 멈출 때까지 재실행**.
- **F14 — 종료/안전 출력**: 테스트는 맞는데 기능이 진짜 깨졌으면 강제 수리·무한루프 대신 **`test.fixme()`로 skip**(github …/playwright-test-healer.agent.md). → 거짓 통과(false green) 방지.

**Nous `hermes-agent-self-evolution`** (⚠️ 정확한 repo는 `NousResearch/hermes-agent-self-evolution`):
- **F15 — 트레이스 기반 진단(GEPA)**: 실행 트레이스를 읽어 *"왜 실패했는지(why, not just that)"* 자연어 진단 후 표적 개선(arXiv:2507.19457, ICLR 2026 Oral). 파이프라인 Extract→Generate-eval→Optimize→Validate→**Propose(PR)**.
- **F16 — 자동 적용 절대 금지 + 5개 하드 게이트**: ① pytest 100% ② 크기 제한 ③ 캐싱 호환 ④ **의미 보존(목적 드리프트 금지)** ⑤ **인간 PR 리뷰(직접 커밋 금지)**. *"Test failures = immediate rejection, no exceptions."*

## 4. 실패모드·안티패턴 — 설계를 좌우 *(하위질문 4)*

| # | 발견 | 근거 |
|---|------|------|
| F17 | **외부 피드백 없는 자기교정은 신뢰성 있게 개선 못 함** → 외부 검증과 반드시 짝 | ICLR 2024 arXiv:2310.01798 + TACL 2024 survey arXiv:2406.01297 |
| F18 | **자기교정이 회귀를 만든다**: *"performance even degrades"*(정답→오답 뒤집힘) → 패치 전 **Pareto 비후퇴** 필수 | arXiv:2310.01798 |
| F19 | 실패하는 정확한 구성 = **intrinsic self-correction**(외부 피드백 없이 자기 능력만). `.md` 트레이스가 그 결여된 외부 신호를 공급 | 동 |
| F20 | **테스트 통과는 불충분한 정답 오라클**: 테스트는 입출력 명세일 뿐 의도된 동작을 못 담음 → **overfit**(APR 도구 4종, 그럴듯한 패치 중 13.8–41.6%만 독립 검증 통과) | arXiv:2011.02714 + arXiv:1810.10614 |
| F21 | 적용 전 막을 **두 overfitting 안티패턴**: ① **incomplete fixing**(일부만 수정) ② **regression introduction**(멀쩡하던 입력 파손) — 직교, 다른 완화책 | 동 |

> ⚠️ **refuted (투명성)**: "모든 self-repair 연구가 인간 게이트를 강제한다"는 주장은 **반박(0-3)** — arXiv:2011.02714은 *인간 체크포인트 없는 완전자동 수리*도 기술. 즉 **"인간 게이트 상시"는 문헌의 보편 법칙이 아니라 *설계 선택*** 이다(F16·F17·F18 근거상 강력 권장되는 선택).

## 5. 기존 하네스에 모듈로 추가하는 아키텍처 *(하위질문 5)*

- **F22 (medium, 3-0)** — **`meta-harness` 패턴을 그대로 거울삼아라**: *공통 full-trace 경험저장소 + causal 진단 + Pareto 비후퇴 패치*, 패치는 하네스별 자동적용이 아니라 **명시적 사용자 승인 게이트** 뒤. (hermes 게이트+PR, APR 회귀 위험, self-correct 퇴화 근거 종합한 추론 → medium)

```
[각 하네스 실행 중]            [공통 .md 저장소]                  [단일 치유 소비자]
frontend-harness ─┐            _experience/
product-spec     ─┤  phase경계·  ├ episodic/<run>.md  (원본:실패·피드백·  ──▶ meta-harness
git-harness      ─┤  실패·       │   when/where/why)                  (causal 진단
review-harness   ─┤  redirect·   ├ semantic/lessons.md (증류 교훈)        +Pareto 비후퇴
loop-engineering ─┘  피드백 시    ├ index.json (링크·네비)                +외부검증
                     trace append└ pareto.json (빈도×severity)            +승인 게이트)
                                                                              │
                                                            자동적용❌ → 승인 후만 / 루프상한
```

**설계 결정**:
1. **공통 모듈 > 하네스별 복제** — 신호 *수집 스키마*는 1개로 표준화(교차 진단·전이학습, MIRIX 코디네이터 F11). ※ shared vs per-harness 트레이드오프는 미해결.
2. **각 하네스는 "쓰기"만 추가** — 새 엔진 금지. phase 종료/실패/redirect 시점 append 경량 스텝(또는 Stop 훅). `meta-harness`의 `trace-capturer`/`session-signal-capture` 일반화.
3. **`meta-harness` = 유일한 치유자** — 진단·Pareto 패치·승인 게이트 이미 구현. 개별 하네스 자가수정 금지(F16 PR 모델, F18 회귀 위험).
4. **트리거**: `recurring-patterns.md`의 **같은 표적 3회(needs_attention ≥3)** + 사용자 redirect. 단발/플래키엔 디바운스.
5. **안전장치 비협상**: 외부 검증(F17·F20) + Pareto 비후퇴(F18·F21) + **명시적 루프 상한**(F14, 미문서→직접 설정) + 인간 승인(F16).

### 권장 `.md` episodic 레코드 스키마 (F6·F9 종합)
```yaml
# _experience/episodic/<harness>-<run-id>.md
id: ...                                            # F9
harness: product-spec-harness
phase: 2
event: failure | redirect | feedback | progress   # F6 event
when: 2026-06-18T...                               # F6 temporal
where: SKILL.md:Phase2 / agent prd-writer          # F6 where (file:line)
why: "사용자가 'success_metrics 관찰형 아님' 지적"    # F6 why-binding
input_excerpt / output_excerpt: ...                # 원본 보존(F7, 요약 금지)
target: <file:line>                                # 진단이 grep할 표적
severity / tags / keywords / links: [[...]]        # F9·F10
```

---

## 미해결 질문 (구현 시 결정 필요)
1. **트리거 조건·디바운스** — 테스트 실패/redirect/검증실패/스케줄 중 무엇이 발동? 플래키 신호 거르기?
2. **검색 관련성 필터링** — 과거 `.md` episode surfacing이 *개선이 아니라 퇴화*를 막는 랭킹/recency/링크-팔로잉(DICE arXiv:2507.23554, 멀티에이전트 실패 survey arXiv:2503.13657의 spurious-context 경고).
3. **루프 종료 상한·에스컬레이션** — 최대 반복, "진짜 회귀/skip" 판정 임계(Playwright `test.fixme()` 류). guardrail 임계 미문서 → 직접 설정.
4. **공통 단일 저장소 vs 하네스별 내장** — 격리·교차오염·스키마 버저닝·네임스페이싱 트레이드오프.
5. **GC/컴팩션** — episodic 원본 무한 증가 → episodic→semantic 증류·프루닝 시점, 인스턴스 맥락 보존.

## 신뢰도 정직성
- **high**: 루프 패턴(Reflexion)·CoALA 분류·episodic 풀트레이스·A-MEM/MIRIX 스키마·두 참조구현·self-correct 퇴화/overfit 안티패턴.
- **medium/추론**: F5 "validated"·F6 스키마→필드 매핑·F22 아키텍처는 *명시된 추론 다리*. CoALA "may be retrieved"는 *능력*이지 보장 아님.
- **시간민감/미문서**: hermes 임계(≤15KB, pytest 100%)는 그 프로젝트 값 — 직접 정하라. Playwright guardrail 반복 상한 미기재.

---

## 출처 (검증 통과)
**Primary**
- Reflexion — arXiv:2303.11366 (NeurIPS 2023)
- CoALA — arXiv:2309.02427 (TMLR 2024)
- Generative Agents — arXiv:2304.03442
- Episodic Memory position paper — arXiv:2502.06975
- A-MEM — arXiv:2502.12110
- MIRIX — arXiv:2507.07957
- GEPA — arXiv:2507.19457 (ICLR 2026 Oral)
- LLMs Cannot Self-Correct Reasoning Yet — arXiv:2310.01798 (ICLR 2024)
- Self-correction survey (Kamoi et al.) — arXiv:2406.01297 (TACL 2024)
- APR obstacles survey — arXiv:2011.02714 ; Overfitting in APR — arXiv:1810.10614
- (참고) DICE — arXiv:2507.23554 ; Multi-agent failure survey — arXiv:2503.13657

**Implementation**
- Playwright Test Agents — https://playwright.dev/docs/test-agents
- Playwright Healer agent def — https://github.com/microsoft/playwright/blob/main/packages/playwright/src/agents/playwright-test-healer.agent.md
- Nous hermes-agent-self-evolution — https://github.com/NousResearch/hermes-agent-self-evolution
