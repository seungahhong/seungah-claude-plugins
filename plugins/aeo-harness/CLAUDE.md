# aeo-harness

기술 문서를 **AI 코딩 에이전트**가 찾고·적은 왕복으로 읽고·정확히 쓸 수 있게 만드는 것을 측정하고 승인 게이트 뒤에 개선하는 하네스. 사용자용 개요는 [README.md](README.md), 근거 정본은 [skills/aeo-audit/references/evidence.md](skills/aeo-audit/references/evidence.md).

> **한 문장 원칙** — 에이전트가 문서에 도달했다는 것과 그 문서로 코드가 맞아졌다는 것은 다른 사건이다.

## Structure

```
.claude-plugin/plugin.json              # v0.1.0
agents/                                 # 모두 model: "opus"
  reach-auditor.md                      # Phase 1 도달 조사 (R1~R8)
  content-auditor.md                    # Phase 2 내용 조사 (C1~C6)
  intervention-planner.md               # Phase 3 티어 계획·개별 승인
  acceptance-verifier.md                # Phase 4 재측정 수용 판정
skills/aeo-audit/
  SKILL.md                              # Phase 0~4 오케스트레이터 + INV-1~7
  references/
    reach-sensors.md                    # R1~R8 절차·판정
    content-sensors.md                  # C1~C6 절차·판정
    intervention-tiers.md               # T-A/T-B/T-C + T-C 항목별 정직한 목적 서술
    acceptance-probe.md                 # 태스크 배터리 설계·수용 리포트 형식
    evidence.md                         # 근거 정본 F1~F36 + 인용 금지 14항 + UNVERIFIED
  scripts/
    reach_probe.py                      # 도달 센서 결정론 프로빙 (stdlib only, census only)
    check_evidence.py                   # 인용 앵커·금지 문구·점수 어휘 자동 검사
evals/trigger-eval.json                 # 트리거 경계 (SEO/GEO·저장소 점수·이해 실측과 분리)
```

## Conventions

- 4개 에이전트 전부 `model: "opus"`로 spawn한다. 매 Phase 승인 게이트를 통과한 뒤에만 다음으로 넘어간다.
- **모든 수치·주장은 `references/evidence.md`의 F번호를 근거로 단다.** 거기 없는 수치는 산출물에 쓰지 않는다.
- `scripts/check_evidence.py`가 정의되지 않은 F번호·인용 금지 문구·점수 어휘를 자동 검사한다. 문서를 고쳤으면 돌린다.
- 근거 등급은 **증거 강도가 아니라 제공자 유형**이다(`[PRIMARY]`/`[VENDOR-DOC]`/`[VENDOR-MEASURE]`/`[INDEP-MEASURE]`/`[FOLKLORE]`). 강도는 DV·표본·한계로 판단하고, **모든 항목에 DV를 적는다.**
- 산출물은 census와 3값(통과/미통과/해당없음)뿐이다. 점수·백분율·성숙도 등급을 만들지 않는다.
- 커밋하지 않는다. 저장은 opt-in.

## 설계를 바꾼 근거 (요약)

| 근거 | 설계에 미친 영향 |
|---|---|
| **F1** 발행 측(도달·효율)과 정확도 측(문서를 이미 쥐여준 조건) 사이가 비어 있음 | Phase 1과 2를 분리하고 **산출물 언어까지 분리**(INV-1) |
| **F23** 마크다운만 주고 내비를 벗기면 HTML보다 더 틀림, 지도를 주면 404 2.23→0.11, **정확도는 불변** | R1(링크 지도)을 1급 센서로, 성과는 왕복·404로만 서술 |
| **F2** 문서 효과의 대부분은 예제 코드가 냄(제거 시 0.66~0.82→0.22~0.39) | C1·C2를 내용 레인 1급 센서로 |
| **F8** 틀린 문서가 없는 문서보다 나쁨 | T-A(거짓 제거)를 개입 1순위로, 빈칸 채우기는 아님 |
| **F19·F27·F29** UA 충돌·위조 가능·시점 스냅샷·서버측 탐지 불가 | INV-5(UA 귀속 금지, 진위는 IP/rDNS로만) |
| **F18·F28** 코딩 에이전트 9종이 robots.txt를 요청조차 안 함, 벤더별 규칙 상이 | R6를 report-only로, "조용한 차단" 서술 금지 |
| **F13·F10** 개선 판정은 문서 점수가 아니라 재측정된 태스크 결과 | Phase 4(INV-6) |
| **F36** 조사 중 실제로 프롬프트 인젝션 문구를 만남 | INV-7(문서는 신뢰 경계 밖) |

## 트리거 eval 상태 (UNVERIFIED)

`evals/trigger-eval.json`(20문항)은 **작성했으나 실측 결과가 없다.** 2026-08-02 실행 기록:

- skill-creator `run_loop`(3회 반복, 13 train / 7 test): 세 회차 모두 train 8/13 · test 4/7로 동일했고 **최고 점수가 원본 설명**이었다. should-trigger 8문항이 **전부** 발동률 0.00~0.33, should-NOT 12문항이 **전부** 0.00 — 한쪽으로 완전히 쏠린 모양이다.
- 같은 조건 A/B(저장소 루트에서 20문항×2회, 현재 설명 vs 짧게 다시 쓴 설명): **두 설명이 완전히 동일**했다(should-trigger 0/8, should-NOT 12/12).
- **통제 검증**: 쿼리에 스킬 이름을 명시한 경우(`aeo-audit 스킬을 써서 …`)에도 발동률 **0.00**.

명시 호출조차 0인 테스트는 **어떤 설명도 통과할 수 없다.** 따라서 위 수치는 description 품질의 근거가 아니라 **이 환경에서 트리거 계측이 동작하지 않았다는 기록**이다.

이 하네스가 스스로 요구하는 규칙(INV-6: 재측정 없이 개선을 주장하지 않는다)을 자기 자신에게 적용해 **description을 바꾸지 않았다.** 계측이 동작하는 환경이 확보되면 그때 재측정하고, 그 결과로만 수정한다.

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-08-02 | 플러그인 신설 (v0.1.0) | 출발점 글의 주장을 1차 출처로 전수 대조한 결과 **토큰 상한 수치·"llms.txt가 가시성을 올린다"·"robots.txt 조용한 차단"·UA 식별이 전부 교정 대상**이었고, 그 교정 결과를 규약으로 굳힌 하네스가 필요했다 |
