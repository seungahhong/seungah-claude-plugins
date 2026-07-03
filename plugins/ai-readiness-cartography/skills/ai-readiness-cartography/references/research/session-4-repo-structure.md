# 세션 4 — repository 구조(모듈 경계·의존 그래프·god file·파일 크기) ↔ agent 편집 정확도·fault localization

> 조사 렌즈: A(navigation)·D(dependency mapping) + 대형 파일 임계값(현행 300/500 lines) 휴리스틱 근거. 파일 크기·모듈 경계 조작화.
> 상태: deep-research 각도 4, 적대 검증 완료 (2026-07-03). 지어낸 출처 없음. RepoMirage "66.8→25.3%"는 원문 확인되어 신뢰도 상향, god class "2~3배"는 1차 미확인이라 배제.

## 검증 판정 요약

| Claim | 판정 | 핵심 |
|-------|------|------|
| C1 | PLAUSIBLE | localization이 지배적 실패요인(Agentless 파이프라인, framing은 해석적) |
| C2 | **CONFIRMED** | LocAgent 의존 그래프 → file-level 92.7%, Pass@10 +12%p, graph > embedding |
| C3 | **CONFIRMED** | 의존 그래프 이점은 multi-hop 어려운 케이스서 큼 |
| C4 | **CONFIRMED** | 구조 perturbation 시 66.8%→25.3%(SWE-bench 고득점 ≠ 구조 추론) |
| C5 | **CONFIRMED** | "exploration drift" — 파일 더 노출 ≠ 개선, structure-first scaffolding이 레버 |
| C6 | **CONFIRMED** (현상) | lost-in-the-middle + context rot(대형 파일 통째 주입 불리 메커니즘) |
| C7 | PLAUSIBLE / 수치 UNVERIFIABLE | coupling↔fault 방향은 정설, "2~3배"는 1차 미확인 |
| C8 | PLAUSIBLE (부재) | **"라인 수 임계값이 agent 정확도 낮춘다" 직접 검증 2025+ 1차 연구 미확인** |
| C9 | **CONFIRMED** | SWE-Bench++ 프레임워크(11,133 instances/3,971 repos/11 lang) |

## 검증된 핵심 발견

2025~2026 근거는 coding agent 실패의 주 병목이 코드 *생성/수리*보다 **fault localization(어디를 고칠지 찾기)**에 있으며, repository의 *구조적 표현*(의존 그래프)을 agent에 제공하면 localization 정확도가 오른다는 방향으로 수렴한다(LocAgent: file-level 92.7% Acc@5, graph-guided가 embedding retrieval 대비 function-level 우위).

사람 직관과 어긋나는 두 지점:
1. **agent에게 파일을 "더 많이 노출"하는 것 자체는 성능을 올리지 않는다** — RepoMirage는 넓은 컨텍스트에 접근하고도 구조 정보로 전환하지 못하는 **"exploration drift"**를 관측했고, 구조를 명시 주입(structure-first scaffolding)해야 이득이 났다.
2. **대형 파일의 해악은 라인 수 임계값보다 컨텍스트 내 위치(lost-in-the-middle)·의존 결합도로 더 잘 설명된다.**

다만 coding-agent 전용으로 검증된 "파일 라인 수 임계값"은 여전히 **미확인**이며, **300/500 line 휴리스틱은 전통 defect-prediction(god class)에서 차용된 값이지 agent 편집 정확도로 직접 검증된 값이 아니다**(C8).

### 검증 가능한 주장 (판정 태그 포함)

- **[C1 · PLAUSIBLE]** localization은 지배적 실패요인 중 하나이며 localization·repair·validation 분리 파이프라인이 강한 성능 — "Agentless: Demystifying LLM-Based SE Agents", Xia·Deng·Dunn·Lingming Zhang(UIUC), FSE 2025(ACM Distinguished Paper). "지배적" framing은 해석적.
- **[C2 · CONFIRMED]** repository를 heterogeneous 의존 그래프(import·invocation·inheritance·containment)로 표현해 주면 embedding retrieval 대비 function-level localization 상승 — "LocAgent", ACL 2025, **arXiv:2503.09089**(gersteinlab/LocAgent). file-level 92.7%, Pass@10 +12%p, function-level 77.01% vs CodeRankEmbed 58.76%.
- **[C3 · CONFIRMED]** 의존 그래프 이점은 multi-hop 추론 어려운 케이스서 큼(retrieval-only는 난이도↑ 시 급락, graph-guided 유지) — 동.
- **[C4 · CONFIRMED]** SWE-bench Verified 고득점 ≠ repository context 추론 — 의미보존 구조 perturbation 시 평균 66.8%→25.3% — "RepoMirage", 2026-05, **arXiv:2605.26177**(BUPT·Tsinghua·Tencent). 수치 원문 교차 확인.
- **[C5 · CONFIRMED]** "exploration drift" — 넓은 컨텍스트 접근하고도 구조 전환 실패. 탐색·문제해결 분리한 structure-first scaffolding(RepoAnchor)이 이득. "더 많은 파일 노출"이 아니라 "구조 먼저 정립"이 레버 — 동.
- **[C6 · CONFIRMED(현상)]** 관련 정보가 긴 컨텍스트 중간이면 정확도 30%+ 저하 U자형(lost-in-the-middle) — Liu et al.(TACL 2023) + Chroma "Context Rot"(2025-07, 18개 frontier 모델 전부, trychroma.com/research/context-rot). 편집 정확도로의 직접 매핑은 부분 추론.
- **[C7 · PLAUSIBLE / 수치 UNVERIFIABLE]** 결합도(coupling)는 결함 성향 강한 예측자, god file/class ≈ 저 cohesion — **라인 수 단독이 아니라 결합도·응집도로 조작화**. 구체 배수("2~3배")는 1차 미확인.
- **[C8 · PLAUSIBLE(부재)]** "파일 300/500 라인 임계값이 coding agent 편집 정확도를 낮춘다"를 직접 검증한 2025+ 1차 연구 **미확인**. 500 LOC는 god class 코드스멜 유래(defect proneness)이며 agent 성능 임계값 근거는 현재 없음.
- **[C9 · CONFIRMED]** 벤치 생성 프레임워크가 함수 시그니처·의존 구조를 활용해 execution-based repo-level 태스크 대규모 합성 — "SWE-Bench++", 2026, **arXiv:2512.17419**(11,133 instances/3,971 repos/11 lang). "구조 힌트 인과 기여"는 순수 ablation 아님(Med).

## Rubric v3 함의

- **D(Cross-Module Dependency) 가중치 상향 + 지표 재정의**(C2·C3·C9, 가장 강한 근거). "architecture doc·mermaid 존재" → **기계 판독 의존 구조**: (a) 정적 import/의존 그래프 추출 가능 여부(Python AST·JS module graph·monorepo workspace edges), (b) 그래프 연결성/경계 명확성. "mermaid 유무"보다 "실제 의존 그래프 파싱 가능성".
- **god-file: 라인 수 단독 임계값 대체**(C7·C8). fan-in/fan-out·export 심볼 수 대비 응집으로 재조작화. 순수 라인 수는 보조 신호로 강등, **"500줄 초과=감점"을 단독 근거로 쓰지 말 것**. 라인 수 임계는 라벨을 "휴리스틱, 근거 약함"으로 명시.
- **A(Navigation): "structure-first 정박점" 지표 추가**(C4·C5). "핵심 module에 진입점·의존 이웃·책임 경계를 명시한 구조 맵이 있는가"를 A/D 하위지표로. "CLAUDE.md 보유율"보다 "그 문서가 의존 이웃을 명시하는가".
- **E(Verification): lost-in-the-middle 완화 신호는 근거 등급 표기하여 제안**(C6). "파일 분할/모듈화 권장"을 신뢰도 Med 라벨, 강한 자동 감점 규칙으로 쓰지 말 것.
- **넣지 말 것**: "N줄 초과 = agent 정확도 X% 하락" 정량 감점(C8: 1차 근거 부재), "파일 많이 노출=좋음" 방향 지표(C5: 반증), god class "2~3배" 미확인 배수.

## 소스 (검증 상태)

- LocAgent — ACL 2025, arXiv:2503.09089 (aclanthology.org/2025.acl-long.426, 코드 공개) — CONFIRMED
- RepoMirage — 2026-05, arXiv:2605.26177 (BUPT·Tsinghua·Tencent) — CONFIRMED
- Agentless: Demystifying LLM-Based SE Agents — FSE 2025, lingming.cs.illinois.edu/publications/fse2025.pdf — 실재·귀속 CONFIRMED, C1 framing PLAUSIBLE
- Lost in the Middle — Liu et al., TACL 2023; + Chroma "Context Rot" 2025-07, trychroma.com/research/context-rot — CONFIRMED
- SWE-Bench++ — 2026, arXiv:2512.17419 (11,133/3,971/11 확인) — CONFIRMED
- Defect prediction / god class·CBO 문헌 — 방향 PLAUSIBLE, "2~3배" 수치 UNVERIFIABLE
