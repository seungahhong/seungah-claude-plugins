# test-layering-harness

> 인수조건(AC)을 **방법론 × 계층 택소노미**로 계층별 테스트 스위트로 계획하고, **사람이 하나씩 승인**하며 순차 적용하는 독립 플러그인.

## 무엇을 하나

인수조건(Acceptance Criteria, Given-When-Then)을 입력받아:

1. **저장소를 감지**해 테스트 구성 프리셋을 추천하고(Trophy-lean / Google-pipeline / Contract-honeycomb),
2. 각 AC를 **방법론 카드 4개 + 계층 카드 3개(7개 축 카드)**를 조합해 **명확한 포함/제외 기준**으로 라우팅해 나누고(12개 셀로 미리 만들지 않고 상황에 맞게 조합; 기준은 2025+ 공식표준·논문에 연결) CI 단계에 배치한 **계획표**를 만들되 — **테스트는 사용자가 선택한 방법론·계층 안에서만** 추가하고(스코프 가드), 밖으로 필요하면 임의 추가 없이 확장을 묻고,
3. **계획 전체를 먼저 승인**받은 뒤, **개별 테스트를 하나씩 승인**받으며 순차로 생성·적용·실행하고,
4. 마지막에 **다시 확인받아** 확정("반영")한다.

세 번의 승인 게이트(계획 → 개별 → 최종)를 건너뛰지 않는다. 승인 없이는 파일을 쓰지 않는다.

## 왜 이렇게

AI가 테스트를 자동 생성할수록 위험은 "작성 속도"가 아니라 **"무엇을, 어느 층에, 어떤 오라클로 검증하는가"**로 옮겨간다. 2025+ 근거([research dossier](skills/test-layering-harness/references/research/test-strategy-research.md))가 반복해 지목하는 최대 리스크는 **오라클 강도** — LLM은 명세(기대)가 아니라 구현(실제 동작)을 그대로 굳혀, 버그를 "초록(통과)"으로 은폐한다. 그래서 이 스킬은 오라클을 **기대(AC) 기준으로 오검증**하고, 적용한 테스트를 **실제로 실행**하며, **기존 flaky를 먼저** 정리한다.

## 어떻게 쓰나

스킬을 부르고(예: "이 인수조건으로 계층별 테스트 계획 세우고 하나씩 승인받으며 추가해줘"), 초기 문의에 답한다:

- **인수조건(AC)** — 붙여넣기·파일 경로. **스킵 가능** — 스킵 시 저장소에서 후보(스토리·PRD·기존 테스트 제목)를 찾아 제안한다.
- **개발 환경(경로)** — **스킵 가능** — 미입력 시 **현재 프로젝트 경로**를 기준으로 테스트 러너·디렉토리 관습을 감지한다.

이후 스킬이 프리셋을 추천하면 확정/변경하고, 계획을 승인하고, 테스트를 하나씩 승인하면 된다.

## 정직성 원칙

- **비율%(70/20/10)를 하드코딩하지 않는다** — 원저자(Fowler)도 상대화한 folklore. 무게중심만 프리셋으로 제안한다.
- **smoke = sanity 는 ISTQB상 동의어** — "smoke=넓고얕음 / sanity=좁고깊음" 구분은 실무 컨벤션이지 표준이 아님을 병기한다.
- **근거 없는 효과 수치를 약속하지 않는다**("버그 80% 조기 포착" 등은 folklore).
- 모든 결론에 신뢰도(HIGH/MED/LOW)와 출처, 모순·folklore 표기를 계승한다.

## 도구 경계 (다른 플러그인과의 구분)

이 플러그인의 축은 **"AC → 방법론×계층 택소노미 계획 → 3게이트 순차 적용"**이다. 다음은 범위 밖:

| 이건 저기서 | 플러그인 |
|---|---|
| 리스크 기반 오라클·자가치유 실행·flaky 트리아지 end-to-end 에이전틱 QA | `qa-agent-harness` |
| 백엔드 코드의 generate→compile→execute→repair 수리 루프 | `backend-harness` / test-generator |
| AC↔테스트 커버리지 **읽기전용** 핸드오프 게이트 검수 | `review-harness` / test-coverage-review |
| FE 개발 워크플로우 내부의 TDD | `frontend-harness` |
| 에이전트가 코드 생성할 실행 가능 명세(spec) 작성 | `spec-driven-development` |
| 커밋 메시지·PR | `git-harness` |

## 구성

- `skills/test-layering-harness/SKILL.md` — 오케스트레이터(5 Phase · 3 게이트, Phase 2에서 축 카드 조합 라우팅)
- `skills/test-layering-harness/references/test-layering-principles.md` — 방법론×계층 매트릭스·AC 분해(§4)·축 카드 조합 라우팅(§4.5)·오라클 가드·실체화(§3.5)·3 프리셋·anti-pattern·경계
- `skills/test-layering-harness/references/matrix/` — **방법론·계층 축 카드 7개**(방법론 카드 4 + 계층 카드 3; `_index.md`에 스코프 가드·조합 라우팅 절차·조합 강도 lookup). 12개 셀로 미리 물질화하지 않고 라우팅 시 조합.
- `skills/test-layering-harness/references/research/test-strategy-research.md` — 2025+ 상위 근거 dossier
- `skills/test-layering-harness/references/research/matrix-criteria-2025.md` — 조합 라우팅 기준 근거 dossier(직교성·계층/방법론 판정·조합 강도 lookup·소스 인덱스)
- `evals/` — 수용 평가 + 트리거 경계 평가

다른 마켓플레이스 플러그인에 의존하지 않는 **독립 플러그인**이다.
