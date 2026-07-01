# LLM Guardrails — 연구 dossier (cited)

> 이 문서는 `llm-guardrails-harness` 하네스 설계의 근거가 된 조사 결과다. 출발점은 **Tech-Verse 2026 S04 "Beyond
> Intelligence to Safety: External AI Guardrails"** 세션이며, 거기서 *전이 가능한 코어*(외부 강제 원칙 + 레일 taxonomy +
> OWASP 매핑)만 추출해 1차 표준·논문으로 접지했다. [llm-guardrails-harness-principles.md](./llm-guardrails-harness-principles.md)의
> 원칙과 상호 참조된다(§N은 이 dossier의 절 번호).
>
> **정직성 가드(머리말).** (1) Tech-Verse S04 발표는 부분적으로 **LINE 사내 LLM 게이트웨이 케이스 스터디**다 — 본
> 하네스는 그 조직 특유 구현이 아니라 *이전 가능한 코어*(레일 taxonomy + OWASP 매핑 + 외부-강제-우선 원칙)만
> 일반화하고, 특정 사내 구현·설정을 귀속하지 않는다. (2) **"개선 N% 보장"을 쓰지 않는다.** ASR/FPR 수치는 *세팅
> (모델·공격 스위트·정책)별 관찰값*이지 보편 법칙이 아니다. (3) **가드레일은 앱을 "안전"하게 만들지 않는다** — 위험을
> *줄이는* 방어심층(defense-in-depth)이며 적응형 공격자는 개별 레일을 우회한다(§4 SoK arXiv:2506.10597). (4) 신뢰도
> 등급은 소스의 성격(표준/피어리뷰 논문/프리프린트)에 따르며, MEDIUM 소스는 보강으로만 쓴다. (5) 시점 민감성 —
> OWASP Top 10은 2025판, NeMo Guardrails 문서는 지속 개정, arXiv 프리프린트는 개정 가능(절 번호·수치가 버전 간 바뀔 수 있음).

---

## §1. OWASP Top 10 for LLM Applications 2025 — 위험 카탈로그 [GOLD]

- **제목**: OWASP Top 10 for Large Language Model Applications (2025)
- **출처**: https://genai.owasp.org/llm-top-10/
- **신뢰도**: GOLD (커뮤니티 합의 표준, 폭넓게 채택)
- **핵심**: LLM 앱의 표준 위험 카탈로그. 본 하네스가 Phase 0에서 매핑하는 축 — **LLM01 Prompt Injection**(직접/간접,
  정렬·지시로 닫히지 않음), **LLM02 Sensitive Information Disclosure**(PII·시크릿 유출), **LLM05 Improper Output
  Handling**(raw 출력이 다운스트림 sink로 무검증 흐름), **LLM06 Excessive Agency**(과도한 기능/권한/자율성), **LLM08
  Vector and Embedding Weaknesses**(RAG 인덱스·검색 악용). LLM05→LLM06 이음매(무검증 출력이 과도한 행동을 트리거)가
  본 하네스 Phase 3 강제의 핵심 근거다.
- **본 하네스 매핑**: Phase 0 위협 모델링의 canonical 축(references §1·§5·§6). 콘텐츠/행동 카테고리를 이 목록에 접지한다.
- **CAVEAT**: 2025판 기준. 항목 번호·명칭은 판 개정 시 바뀔 수 있다(2023판과 이미 상이). 위험 *목록*이지 구현 레시피가 아니다.

## §2. NVIDIA NeMo Guardrails — 레일 taxonomy(5 rail types) [GOLD]

- **제목**: NVIDIA NeMo Guardrails — Guardrails Process / Rail Types
- **출처**: https://docs.nvidia.com/nemo/guardrails/latest/user-guides/guardrails-process.html ·
  repo https://github.com/NVIDIA-NeMo/Guardrails
- **신뢰도**: GOLD (벤더 1차 문서 + 오픈소스 구현)
- **핵심**: 프로그래머블 레일을 요청 라이프사이클의 5개 지점으로 조직한다 — **input rails**(사용자 입력에 적용, 거부/변경/
  중단), **dialog rails**(대화 흐름 제어), **output rails**(LLM 생성에 적용), **retrieval rails**(검색된 청크에 적용), **execution
  rails**(호출된 커스텀 액션/tool의 입출력에 적용). 레일은 pass/block뿐 아니라 *rewrite/mask*도 한다. → 본 하네스의 레일
  배치(Phase 0)와 Phase 1(input)·Phase 2(output/retrieval)·Phase 3(execution)의 구조적 근거.
- **본 하네스 매핑**: references §2 전체 taxonomy 커버 + Phase↔레일 대응.
- **CAVEAT**: 특정 프레임워크의 taxonomy다 — 본 하네스는 *레일 종류의 개념 구조*만 차용하고 특정 API·Colang 문법을
  요구하지 않는다(도메인 무관). 문서는 지속 개정된다.

## §3. Llama Guard — LLM 기반 input-output safeguard [GOLD]

- **제목**: "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations"
- **저자/출처**: Inan et al. (Meta), 2023-12 · arXiv:2312.06674 · https://arxiv.org/abs/2312.06674
- **신뢰도**: GOLD (피어 인용 다수·오픈 모델·표준 참조 구현)
- **핵심**: 안전 위험 taxonomy를 정의하고, 프롬프트(입력)와 응답(출력)을 **SAFE/UNSAFE + 위반 카테고리 ID**로 분류하는
  LLM 기반 safeguard. 입력·출력 모두에 적용 가능한 분류기 접근. → 본 하네스 Phase 1 "Llama-Guard 스타일 입력 분류
  (SAFE/UNSAFE + 카테고리)"와 Phase 2 출력 분류의 직접 참조 모델.
- **본 하네스 매핑**: references §2(분류형 레일) · Phase 1·2 분류 설계.
- **CAVEAT**: 특정 모델·taxonomy다 — 본 하네스는 *분류 인터페이스 패턴*(SAFE/UNSAFE + 카테고리)만 차용하고 특정 모델
  가중치를 요구하지 않는다. 분류기 자체도 공격 가능한 LLM이다(§4·§5와 연결) — 단일 분류기에 의존하지 않는다.

## §4. SoK: Evaluating Jailbreak Guardrails — ASR/FPR·적응형 우회 [GOLD]

- **제목**: "SoK: Evaluating Jailbreak Guardrails for Large Language Models"
- **출처**: arXiv:2506.10597 · https://arxiv.org/html/2506.10597v2
- **신뢰도**: GOLD (Systematization-of-Knowledge, 다수 가드레일·공격 교차 평가)
- **핵심**: jailbreak 가드레일을 체계적으로 평가한다 — 핵심 지표는 **ASR(Attack Success Rate, 놓친 공격)** 과 **FPR
  (False Positive Rate, 과차단된 benign)**. 어느 단일 가드레일도 만능이 아니며 **적응형(adaptive) 공격이 개별 방어를
  우회**한다. 고정·알려진 공격 벤치마크의 정확도가 아니라 *일반화*를 봐야 한다. → 본 하네스 Phase 3 red-team의 지표
  (ASR·FPR 함께)·다층 방어(§4)·정적 벤치마크 불신(§8)·"안전 달성 아님" 정직성(§9)의 1차 근거.
- **본 하네스 매핑**: references §4(다층)·§7(ASR/FPR)·§8(일반화)·§9(정직성).
- **CAVEAT**: SoK는 *가드레일을 평가*하는 프레임이지 특정 가드레일이 "N% 낫다"는 보증이 아니다. ASR/FPR은 *세팅별*
  관찰값 — 본 하네스는 보편 수치를 인용하지 않는다.

## §5. OWASP LLM Prompt Injection Prevention Cheat Sheet — 방어심층·최소권한·사람승인 [GOLD]

- **제목**: OWASP Cheat Sheet Series — LLM Prompt Injection Prevention
- **출처**: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- **신뢰도**: GOLD (OWASP 실무 가이드)
- **핵심**: prompt injection 방어 실무 지침 — **가드레일 LLM 자체가 injectable**이므로 단일 방어에 의존하지 말고
  **defense-in-depth**로 겹치고, **least-privilege**로 tool·권한을 좁히며, **고위험/비가역 행동에 human approval**을 둔다.
  입력 검증만으로 injection을 완전히 막을 수 없음을 명시. → 본 하네스 §1(외부 강제)·§4(다층·가드레일도 취약)·§5(최소
  권한+사람 게이트)·§3(fail-closed)의 실무 근거.
- **본 하네스 매핑**: references §1·§3·§4·§5.
- **CAVEAT**: 지속 개정되는 실무 문서다 — 특정 라이브러리를 지정하지 않는다. "완전 차단" 대신 *위험 감소*를 전제한다(§9와 일치).

## §6. Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents [SILVER, 보강]

- **제목**: "Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents"
- **출처**: arXiv:2606.26479 · https://arxiv.org/pdf/2606.26479
- **신뢰도**: SILVER(MEDIUM) — 최신 프리프린트(피어리뷰 전), 보강 근거로만 사용
- **핵심**: LLM 에이전트에 대한 *out-of-band* 방어(모델 바깥의 외부 방어)를 **적응형 공격**으로 평가한다 — 고정 공격이
  아니라 방어를 아는 적응형 공격자에 대한 강건성을 본다. 에이전트 맥락(tool 호출·검색)에서의 injection·간접 injection을
  다룬다. → 본 하네스 §6(검색/도구 반환 불신·indirect injection)·§8(적응형·미지 공격 일반화 평가)를 *보강*.
- **본 하네스 매핑**: references §6·§8(보강).
- **CAVEAT**: **보강 소스**(MEDIUM) — 프리프린트라 개정·철회 가능. 본 하네스의 1차 근거는 §1·§2·§4·§5(GOLD)이고,
  이 절은 적응형·에이전트 맥락을 구체화하는 보조 인용이다. 구체 수치·기법을 GOLD 소스에 귀속하지 않는다.

---

## 반박·비귀속 (투명성)

> 조사·설계에서 *경계로 둔* 주장이다. 본문 근거로 쓰지 않으며 투명성을 위해 기록한다.

- **사내 게이트웨이 구현의 일반화** — Tech-Verse S04는 부분적으로 LINE 사내 LLM 게이트웨이 케이스다. 그 조직 특유의
  구현·수치·아키텍처를 *일반 원칙으로 귀속하지 않는다*. 본 하네스는 이전 가능한 코어(레일 taxonomy·OWASP 매핑·외부
  강제 원칙)만 취한다(머리말 (1)).
- **"가드레일 = 안전 달성"** — 가드레일은 위험을 *제거*하지 않는다. 방어심층으로 *줄일* 뿐이며 적응형 공격자는 개별
  레일을 우회한다(§4 SoK). "가드레일을 붙였으니 안전하다"는 주장은 쓰지 않는다.
- **보편 ASR/FPR 수치** — 특정 세팅(모델·공격 스위트·정책)의 ASR/FPR을 *보편 성능*으로 인용하는 것은 과강하다. 수치는
  세팅별 관찰값으로만 읽는다(§4 CAVEAT).
- **단일 분류기 만능론** — Llama-Guard 스타일 분류기 하나로 injection을 "닫는다"는 것은 §5(가드레일 LLM도 injectable)에
  반한다. 분류기는 *다층 중 한 레일*이다.
- **"개선 N% 보장"** — 어떤 레일·구성도 개선 폭을 보장하지 않는다. 금지한다(머리말 (2)).

## 방법론 — 세션 → 1차 표준·논문 접지

- **출발점**: Tech-Verse 2026 S04 "Beyond Intelligence to Safety: External AI Guardrails" 정독 → *조직 특유 구현 제거,
  전이 가능한 코어(외부-강제-우선 · 레일 taxonomy · OWASP 매핑 · ASR/FPR 적대 검증) 추출*.
- **접지**: 각 코어를 1차 표준·피어 인용 소스로 매핑 — 위험 카탈로그=OWASP LLM Top 10 2025(§1), 레일 taxonomy=NeMo
  Guardrails(§2), 분류형 레일=Llama Guard(§3), 적대 검증·지표=SoK Jailbreak Guardrails(§4), 방어심층 실무=OWASP
  Cheat Sheet(§5), 적응형·에이전트 맥락=out-of-band 적응형 평가(§6, 보강).
- **신뢰도 등급**: GOLD(표준·벤더 1차·피어 인용 다수) 5건 + SILVER/MEDIUM(최신 프리프린트, 보강) 1건. MEDIUM은 GOLD
  결론을 *구체화*할 때만 인용하고 단독 근거로 쓰지 않는다.
- **정직성·정확 귀속 가드**: 세션 사례(조직 특유) vs 1차 표준/논문(일반 근거)을 분리. 특정 프레임워크(NeMo)·모델
  (Llama Guard)의 taxonomy·인터페이스는 *개념 패턴*으로만 차용하고 특정 API·가중치를 요구하지 않는다. 수치는 세팅별
  관찰값으로 한정, "개선 N% 보장" 금지, "가드레일=위험 감소지 제거 아님"을 명기. 시점 민감성(OWASP 2025판·NeMo 문서
  개정·arXiv 프리프린트 개정 가능)을 표기한다.
