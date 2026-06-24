# Agent Orchestration — 원리 · 선택 규칙 · 협업 설계 · anti-pattern

> 이 문서는 agent-orchestration 하네스가 따르는 설계 원리의 근거다. 오케스트레이터(SKILL.md)와 각 에이전트가 참조한다.
> 정량 근거의 출처·인용·신뢰도·CAVEAT·반박된 주장은 [agent-orchestration-research.md](./agent-orchestration-research.md)에 정리돼 있고, 이 문서의 원칙과 상호 참조된다(§N은 research dossier의 절 번호다). 빠르게 변하는 분야이므로 수치는 vote/CAVEAT와 함께만 인용한다.

## 1. 무엇이 agent orchestration 결정인가

멀티 에이전트 설계의 첫 질문은 "에이전트를 몇 개 둘까"가 아니라 **"여기서 에이전트를 더 쓰는 게 *순이득*인가"** 이다.
이 하네스는 그 결정을 네 단계로 구조화한다 — 작업을 *평가*하고(Phase 0), 아키텍처를 *권고*하고(Phase 1),
협업 가드를 *설계*하고(Phase 2), 그 계획이 단일 baseline을 *능가하는지 검증*한다(Phase 3).

**핵심 전제(이 하네스의 제1원칙): "에이전트를 더 붙인다고 항상 이득이 아니다."**
멀티 에이전트의 이득/손해는 *에이전트 수*가 아니라 **architecture-task alignment**(작업 속성과 아키텍처의 정합)가
결정한다. 같은 작업도 토폴로지에 따라 단일 에이전트 대비 *큰 이득*과 *큰 손해*로 갈린다(§1). 그리고 협업 자체에
비용이 든다(curse of coordination, §3) — 그래서 멀티는 *비용을 정당화*해야 채택된다.

## 2. 선택 규칙 (single vs multi)

### 2.1 architecture-task alignment — 작업 속성이 아키텍처를 정한다
멀티 에이전트가 단일 대비 *크게 이득인 작업*과 *크게 손해인 작업*이 갈린다. 통제 실험은 단일 에이전트 baseline 대비 상대
성능 변화가 **분해 가능한 작업에서 큰 양(+), 순차 추론 작업에서 큰 음(−)** 으로 벌어짐을 보고한다(§1, vote high). 즉
"멀티가 좋다/나쁘다"는 보편 답이 없고 *작업에 맞는 아키텍처를 고르는 것*이 결정의 본질이다.

- **decomposability(분해 가능성) 높음 + tool density(도구 밀도) 높음** → 역할 분리(병렬·전담)가 이득일 가능성↑.
- **순차 추론(sequential planning)·강한 직렬 의존** → 병렬 이득이 작고 오류가 직렬로 누적 → *단일 권고* 신호.

### 2.2 capability ceiling — 언제 병렬화하면 *안 되는가*
**단일 에이전트가 이미 충분히 잘 푸는 작업은 에이전트를 더 붙일 때 음의 수익이 날 수 있다** — coordination 비용이
한계 개선을 넘어서기 때문이다. 연구는 단일 에이전트 정확도가 *경험적 임계*(약 45%)를 넘는 작업에서 추가 에이전트의 음의
수익을 보고한다(§2, vote high). 이를 *병렬화 금지 후보* 플래그로 쓴다.

> ⚠️ **결정론적 rule이 아니라 경험적 임계다.** 임계 회귀의 설명력은 절반 미만이라(R²≈0.51) decomposability·tool
> density·토폴로지가 임계를 무효화할 수 있다(예: 일부 작업은 분해형이라 centralized로 여전히 큰 이득; §2 CAVEAT).
> 따라서 capability-ceiling은 "병렬화를 *의심하라*"는 신호지 "병렬화 *금지*"의 단정이 아니다 — over-rule 금지.

### 2.3 멀티는 비용을 정당화할 때만
신호가 모호하거나 단일 baseline이 이미 높으면 **단일 에이전트가 기본 권고**다. 멀티는 "왜 단일보다 나은가"를 명시할 수
있을 때만 권고한다. 이 보수성은 §3의 curse of coordination(협업 비용) 때문이다.

## 3. 토폴로지 (centralized vs independent)

멀티로 갈 때 토폴로지도 결정한다. **오류 증폭이 토폴로지마다 다르다** — 연구는 independent 구성이 centralized보다
오류를 더 크게 증폭함을 보고한다(§1). 한 에이전트의 오류가 다른 에이전트로 전파되는 구조(independent)는 통합 단계에서
누적 오류가 커진다.

- **centralized**(한 오케스트레이터가 조율·통합) — 도구 밀도가 높고 통합이 필요한 작업의 *보수적 기본*. 오류 증폭이 더 작다.
- **independent**(약한 의존의 fan-out) — 하위작업이 서로 독립이고 통합이 단순할 때 고려. 단 오류 증폭이 크므로 핸드오프
  계약을 더 엄격히 한다(§4 가드).
- 토폴로지가 미상이면 centralized를 보수적 기본으로 둔다.

## 4. 협업 가드 — 세 root-cause 실패 메커니즘

에이전트 협업은 사람 팀과 다르다. **인원 추가가 생산성 증가를 보장하지 않는다** — 페어 협업이 각자 수행 대비 성공률이
떨어지는 경향이 보고된다(curse of coordination, §3). 그리고 그 실패는 무작위가 아니라 **세 가지 진단 가능한
root-cause**로 조직화된다(§4, vote high). 가드는 증상이 아니라 이 메커니즘을 겨냥한다.

1. **communication** — 채널이 *모호·부정확·타이밍 어긋난* 메시지로 정체된다. → 가드: 메시지 스키마(무엇을·언제·누구에게),
   불필요 브로드캐스트 금지, 핸드오프는 *구조화된 산출물*만.
2. **commitment** — 효과적 소통이 있어도 에이전트가 *약속/할당에서 이탈*한다. → 가드: 명시적 작업 할당·완료 정의(DoD),
   역할 경계 고정, 다른 에이전트 영역 침범 금지.
3. **expectation** — 에이전트가 *타 에이전트의 계획·관측·소통을 오해*한다. → 가드: 공유 상태의 단일 출처, 가정 명시,
   핸드오프 시 "받은 것/줄 것" 정합 확인.

연구는 **expectation 실패가 가장 크고 communication이 그다음**임을 보고한다(§4) — 가드 우선순위를 여기에 맞춘다.
또한 메시지·동기화 지점을 *필요 이상으로 늘리지 않는다*(채널 정체 자체가 communication 실패원이므로 — 최소 coordination).

## 5. 컨텍스트 격리 (context pollution 가드)

N개 에이전트가 한 오케스트레이터의 컨텍스트 윈도우를 *공유*하면, 각 에이전트의 작업 상태·부분 출력·미해결 질문이 *다른
에이전트의 결정 품질을 오염*시킬 수 있다(context pollution, §5). 이는 coordination 실패의 한 형태다.

- **per-agent 컨텍스트 격리** — 각 에이전트는 자기 작업에 필요한 것만 본다(다른 에이전트의 미해결 상태를 보지 않는다).
- **오케스트레이터의 비대칭 컨텍스트** — 오케스트레이터는 에이전트별 *경량 상태 요약*만 유지하고, 특정 에이전트를 다룰
  때만 그 *풀 컨텍스트*를 끌어온다(나머지는 요약으로 압축). 이는 벤더 비종속의 일반 격리 패턴이다.

> CAVEAT: context pollution의 *질적 메커니즘*만 채택한다 — 출처의 정량 수치는 합성 벤치 비중이 커 인용하지 않는다(§5
> CAVEAT). 다만 "subagent마다 독립 컨텍스트 윈도우를 둔다"는 실무 멀티 에이전트 시스템의 격리 관행이 이 메커니즘을 독립
> 보강한다(research dossier §5).

## 6. baseline 능가 검증 (verify-or-reject)

마지막 게이트는 **'multi라서 좋다'가 아니라 *단일 baseline 대비 순이득이 양인가*** 다. orchestration-verifier가:

```
순이득 = (멀티 기대 이득: 분해·도구 분리)
        − (coordination 비용: curse of coordination + 설계한 가드 비용)
        − (오류 증폭: 토폴로지별. independent 가중)
```

이 *양(+)이 남는지*를 적대적으로 따진다 — "단일보다 못할 시나리오"를 먼저 찾고, 못 찾을 때만 멀티를 통과시킨다.
순이득이 0 근처면 보수적으로 단일을 권고한다. **능가를 증명 못 하면 REJECT(단일 권고)가 정당한 산출물**이다 —
거절은 실패가 아니다. 통과 못 한 계획은 직접 고치지 않고 *어느 Phase로 무엇을 바꿀지*(REVISE) 신호만 낸다.

## 7. anti-pattern (피해야 할 것)

- **more-agents-is-better** — 에이전트 수를 늘리면 좋아진다는 가정. 성패는 architecture-task alignment가 결정한다(§1·§2).
- **capability-ceiling 무시** — 단일이 이미 잘 푸는 작업에 에이전트를 붙여 음의 수익을 낸다(§2).
- **capability-ceiling 과강화(over-rule)** — 경험적 임계를 결정론적 금지 rule로 단정해 정당한 멀티(분해형 centralized)를 막는다(§2 CAVEAT). 반대 방향의 실수.
- **토폴로지 무시** — single/multi만 정하고 centralized/independent를 안 정해 오류 증폭을 방치한다(§1·§3).
- **curse of coordination 무시** — 협업 비용을 0으로 가정해 멀티의 순이득을 과대평가한다(§3).
- **증상 기반 가드** — "메시지가 많아서 느리다" 같은 증상만 보고 root-cause(communication/commitment/expectation)를 안 겨냥한다(§4).
- **과잉 coordination** — 메시지·동기화 지점을 과하게 늘려 채널을 정체시킨다(communication 실패를 *스스로* 만든다, §4).
- **컨텍스트 공유 방치** — 에이전트들이 한 컨텍스트를 공유해 cross-agent 오염을 방치한다(§5).
- **검증 없는 채택** — baseline과 비교하지 않고 멀티 계획을 그대로 채택한다(§6의 게이트 생략).
- **거절을 실패로 취급** — 단일이 낫다는 결론(REJECT)을 패배로 보고 억지로 멀티를 채택한다(§6).

## 8. 결정 신호 요약 (한눈에)

| 신호 | 단일 권고 쪽 | 멀티 권고 쪽 |
|------|-------------|-------------|
| decomposability | 낮음(순차 추론) | 높음(독립 하위작업) |
| tool density | 낮음 | 높음(역할 전담 이득) |
| 의존 구조 | 강한 직렬 체인(오류 직렬 누적) | 약한 의존(병렬 fan-out 가능) |
| 단일 baseline | 이미 높음(capability ceiling) | 낮음(개선 여지 큼) |
| 토폴로지(멀티 시) | — | 통합 필요·도구 밀도↑ → centralized / 독립·단순 통합 → independent(단 오류 증폭 주의) |
| 순이득(검증) | 0 이하/경계 → 단일 | 명백한 양(+) → 멀티 |

> 모든 신호는 *경향*이지 결정론이 아니다(§2 CAVEAT, §3 비균일). 신호가 충돌하면 baseline 대비 순이득(Phase 3)으로 확정하고, 경계에서는 *단일을 보수적 기본*으로 둔다.

## 참고 문헌

출처별 구체 인용·신뢰도·CAVEAT·반박된 주장은 **[agent-orchestration-research.md](./agent-orchestration-research.md)**(deep-research dossier: 출처·인용·vote·CAVEAT + 반박된 주장(투명성) + 방법론)에 정리돼 있고, 이 문서의 원칙과 상호 참조된다.

핵심 1차(primary): "Towards a Science of Scaling Agent Systems"(arXiv:2512.08296 — architecture-task alignment·capability ceiling·오류 증폭) · "CooperBench: Why Coding Agents Cannot be Your Teammates Yet"(arXiv:2601.13295 — curse of coordination·세 실패 메커니즘) · "Dynamic Attentional Context Scoping"(arXiv:2604.07911 — context pollution, medium 신뢰·질적 메커니즘만).

> 핵심 CAVEAT(dossier 참조): capability-ceiling 45%는 경험적 임계지 결정론 rule이 아님(R²≈0.51); curse of coordination 30%는 방향성 성립·난도별 비균일; context pollution 수치는 합성 벤치 비중 커 미채택(질적 메커니즘만).
