# LLM Guardrails — 원칙·anti-pattern·결정 신호표

> `llm-guardrails-harness` 하네스의 설계 헌법. 모든 Phase가 따른다. 근거는 [llm-guardrails-harness-research.md](./llm-guardrails-harness-research.md)
> (§N은 그 dossier의 절). 핵심 전제: **안전은 모델을 믿는 게 아니라 모델 바깥을 감싸는 외부·인라인 제어 평면
> (external control plane)** — prompt injection은 LLM의 근본 설계를 악용하므로 정렬·지시로 닫히지 않는다. 본 하네스는
> 이 위에서 **위협 모델링 → 입력 레일 → 출력·검색 레일 → 행동 강제·적대 검증**의 4단계를 운영한다(research §1·§2).

---

## §1. 외부 강제 우선 (external enforcement over system-prompt trust)

안전은 모델 바깥의 **별도 제어 평면 계층**이다 — "절대 유출하지 마" 같은 시스템 프롬프트 지시는 *강제 경계가 아니다*
(research §1 OWASP LLM01 · §5 Prompt Injection Prevention Cheat Sheet).

- prompt injection은 LLM의 근본 설계(지시와 데이터를 같은 채널로 받음)를 악용하므로 정렬·지시만으로 닫을 수 없다.
- 따라서 검사·거부·재작성은 모델 *바깥*의 레일이 한다. 시스템 프롬프트는 방어의 *일부*지 강제 경계가 아니다.

## §2. 전체 레일 taxonomy 커버 (input · dialog · output · retrieval · execution)

레일은 요청 라이프사이클의 서로 다른 지점을 지킨다(research §2 NeMo Guardrails 5 rail types).

- **input** 레일(모델 호출 전) · **dialog** 레일(대화 흐름) · **output** 레일(생성 후) · **retrieval** 레일(검색 시점) ·
  **execution** 레일(tool 호출).
- 각 레일은 pass/block뿐 아니라 **재작성/마스킹**도 한다(예: PII 토큰 치환 후 통과). 단일 지점만 지키면 다른 지점이 뚫린다.

## §3. fail-closed 기본값 (fail-closed by default)

레일 오류·타임아웃·분류기 불확실 시 통과가 아니라 **차단·강등**한다(research §5 Cheat Sheet defense-in-depth).

- 부하·공격 트래픽이 가장 높을 때가 레일이 실패하기 쉬운 때다 — 그때 fail-open하면 모델이 정확히 무방비가 된다.
- 불확실은 안전 방향으로 해석한다(deny by default). Phase 0 정책이 카테고리별 기본 동작을 못 박는다.

## §4. 가드레일 자체가 공격 가능한 LLM — 다층 방어

가드레일이 LLM이면 그것도 동일한 injection에 취약하다 — **단일 신뢰점을 두지 않는다**(research §5 Cheat Sheet · §4 SoK).

- input/output/retrieval/execution 레일을 겹치고, 최소 권한 스코프·사람 승인으로 다시 겹친다(defense-in-depth).
- 어떤 단일 분류기/레일도 "충분"으로 단정하지 않는다. 입력에서 놓친 것을 출력·검색·실행 레일이 잡도록 설계한다.

## §5. excessive agency 최소 권한 + 사람 게이트 (LLM06:2025)

excessive agency를 **최소 권한 tool 스코핑·인자/결과 검증·비가역 행동 사람 승인**으로 강제한다(research §1 OWASP LLM06 · §5).

- tool마다 스코프를 좁히고(ambient·broad 스코프 금지), 인자와 결과를 검증한다(execution rails).
- **raw LLM 출력이 고폭발 반경 행동을 직접 트리거하지 않게 한다** — 이것이 LLM05(Improper Output Handling)를
  LLM06(Excessive Agency)로 잇는 이음매다.
- 삭제·전송·결제·외부 egress·프로덕션 접촉 등 비가역/파괴적 행동은 *실행 전 사람 승인*(전수 승인이 아니라 비가역에 집중).

## §6. 검색/도구 반환 콘텐츠 불신 (retrieval rails, LLM08:2025)

검색된 청크와 도구 반환 값을 **untrusted**로 다룬다 — retrieval 레일이 필터/검증한다(research §1 OWASP LLM08 · §6 적응형 평가).

- indirect prompt injection은 검색·도구 결과에 심긴 악성 지시로 실행된다 → 모델/사용자 도달 전에 걸러야 한다.
- 벡터/임베딩 약점(오염된 인덱스·출처 위장)을 출처 검증·격리로 완화한다. "검색 결과는 안전"이라는 가정을 금지한다.

## §7. safety-utility 트레이드오프 — ASR ↔ FPR 함께 측정

**ASR(놓친 공격)** 과 **FPR(과차단)** 을 *둘 다* 측정한다(research §4 SoK).

- ASR만 낮추려 공격적으로 차단하면 FPR이 올라 benign 사용자가 차단된다 → 사용자가 레일을 우회·비활성화한다.
- 두 지표의 트레이드오프를 명시적으로 최적화하며, 어느 한쪽만 보고하는 것을 금지한다.

## §8. 런타임·인라인·관측 (정적 벤치마크 불신)

레일은 **라이브 요청 경로에서 텔레메트리와 함께** 실행된다 — 이는 오프라인 판정과 다르다(research §4·§6).

- 평가는 알려진 jailbreak 고정 벤치마크 정확도가 아니라 *미지·적응형 공격 일반화*를 본다(오염·정적 벤치마크는 거짓 확신).
- red-team은 *레일을 검증*하지 산출물을 채점하지 않는다(오프라인 평가 도메인과 구분).

## §9. 정직성·falsifiability

- 세션 사례(Tech-Verse S04)는 일부 사내 게이트웨이 케이스다 — **전이 가능한 코어**(레일 taxonomy·OWASP 매핑·외부강제
  원칙)만 일반화하고 *특정 사내 구현을 귀속하지 않는다*(research 정직성 가드).
- **"개선 N% 보장"을 쓰지 않는다.** ASR/FPR 수치는 *세팅별 관찰값*이지 보편 법칙이 아니다.
- 가드레일은 위험을 *줄이는* 방어심층이지 *제거*가 아니다 — 적응형 공격자는 개별 레일을 우회한다(research §4 SoK).
- 판정 자원(grounding 대조·red-team 트래픽)이 없으면 PASS/"안전"을 단정하지 말고 **UNVERIFIED**로 표시한다.

---

## Anti-pattern (하지 말 것)

| Anti-pattern | 왜 나쁜가 | 올바른 패턴 | 근거 |
|---|---|---|---|
| 시스템 프롬프트만으로 가드("절대 유출 마") | 직접/간접 injection에 손쉽게 우회 — 지시는 강제 경계가 아님 | 외부·인라인 레일로 검사·거부·재작성 | §1·research §1·§5 |
| 단일 분류기/레일을 은탄환으로 | 가드레일 LLM도 injectable — 뚫리면 무방비 | input/output/retrieval/execution + 사람 승인 다층 | §4·research §5 |
| 과차단(높은 FPR) | 사용자가 레일을 우회·비활성화 | ASR·FPR 함께 측정·트레이드오프 최적화 | §7·research §4 |
| 오염·정적 벤치마크로 거짓 확신 | 알려진 공격만 통과, 적응형·미지 공격에 뚫림 | 미지 공격 일반화 평가 | §8·research §4·§6 |
| 검색/도구 반환 콘텐츠를 안전으로 신뢰 | retrieval 레일 없으면 indirect injection 실행 | 검색 청크 untrusted·필터/검증 | §6·research §1(LLM08)·§6 |
| broad·ambient tool 스코프, raw 출력→파괴 행동 직결 | excessive agency로 고폭발 반경 손상 | 최소 권한 스코핑·비가역 행동 사람 게이트 | §5·research §1(LLM06) |
| 레일 실패 시 fail-open | 부하·공격 시 정확히 무방비 | fail-closed(차단·강등) 기본값 | §3·research §5 |
| "안전 달성" 단정·개선 N% 주장 | 가드레일=위험 감소지 제거 아님 | 잔여 위험·과차단 정직 보고·UNVERIFIED | §9·research §4 |

## 결정 신호표 — 이 하네스인가, 인접 도메인인가?

| 신호 | 이 하네스(llm-guardrails-harness) | 인접 도메인 |
|---|---|---|
| "LLM 앱을 OWASP LLM Top 10에 위협 모델링하고 알맞은 가드레일 설계" | ✅ | — |
| "입력에 jailbreak/prompt-injection 탐지, 출력에 PII 리댁션·독성 필터" | ✅ | — |
| "excessive agency 가드레일 + 파괴적 행동 사람 승인 게이트" | ✅ | — |
| "가드레일 red-team하고 ASR 대 FPR 보고" | ✅ | — |
| "AI 출력을 *LLM judge로 사후 채점*하고 benchmark validity 감사" | ❌ | 평가(offline judge) |
| "프로덕션 LLM 서비스 *장애 탐지·국소화·RCA*" | ❌ | 운영(post-hoc RCA) |
| "코드 착수 전 *PRD·API 계약·QA 핸드오프* 게이트 검수" | ❌ | 핸드오프 리뷰 |
| "사람↔에이전트 *분업·감독·신뢰* 협업 설계" | ❌ | 사람-에이전트 협업 |
| "작업을 *여러 에이전트로 병렬화·토폴로지* 결정" | ❌ | 멀티 에이전트 오케스트레이션 |
| "*/orders REST 엔드포인트* 구현·실행 검증" | ❌ | 백엔드 구현 |
| "*코딩 에이전트의 파일 편집 권한·샌드박스* 거버넌스" | ❌ | 코드 변경 거버넌스 |
| "React 폼의 *XSS 취약점* 수정" | ❌ | 웹 보안 감사 |
| "MCP tool용 *스코프 OAuth 토큰·위임·동의* 설계" | ❌ | 인가/아이덴티티 |

경계가 모호하면 한 질문으로 확인한다 — "*돌아가는 LLM 앱의 입력·출력·검색·행동에 런타임 가드레일을 외부에서
인라인 강제*하려는 건가요, 아니면 *다른 것*(오프라인 출력 채점·장애 RCA·상류 핸드오프 검수·사람-에이전트 협업 설계·
에이전트 병렬화·백엔드 기능 구현·코딩 에이전트 코드 거버넌스·웹 소스 취약점 스캔·아이덴티티/인가 설계)인가요?"
