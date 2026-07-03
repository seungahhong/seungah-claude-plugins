"""score.py 회귀 테스트 — stdlib unittest only.

실행: python3 -m unittest test_score.py  (이 디렉토리에서)
또는: python3 test_score.py

우선순위(계획 근거):
- Gate-1(reference integrity)은 오탐 1건이 전체 등급을 AI-Fragile로 상한시키는
  최고위험 로직 — 정밀도(illustrative 경로 미탐지·repo 밖 참조 미집계)를 고정한다.
- 골든 픽스처 총점을 고정해 향후 regex/임계값 수정이 등급을 조용히 이동시키면 잡는다.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score  # noqa: E402

CAT_KEYS = ("E", "D", "B", "C", "H", "A", "F", "I", "G")


def make_repo(base: Path, files: dict[str, str]) -> Path:
    for rel, content in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return base


GOLDEN_FILES = {
    "README.md": "# App\n\nRun `pytest` to test.\n\nEntry point: src/app.py\n",
    "CLAUDE.md": "# Context\n\nWhy: 주의 — build 전에 `pytest` 실행.\n",
    "src/app.py": "import os\n\n\ndef main():\n    return 1\n",
    "tests/test_app.py": "def test_main():\n    assert True\n",
    "pyproject.toml": "[tool.pytest.ini_options]\ntestpaths = ['tests']\n",
    ".github/workflows/ci.yml": "jobs:\n  test:\n    steps:\n      - run: pytest\n",
}


class ScoreTestCase(unittest.TestCase):
    def setUp(self):
        score.read_text.cache_clear()  # 테스트 간 임시 파일 재사용 오염 방지
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)


class TestWeightsInvariant(ScoreTestCase):
    def test_category_maxes_sum_to_100_and_scores_bounded(self):
        make_repo(self.repo, {"README.md": "# empty\n"})
        report = score.build_report(self.repo)
        self.assertEqual(set(report.categories.keys()), set(CAT_KEYS))
        self.assertEqual(sum(c.max for c in report.categories.values()), 100)
        for c in report.categories.values():
            self.assertGreaterEqual(c.score, 0, c.key)
            self.assertLessEqual(c.score, c.max, c.key)
        self.assertEqual(report.total, sum(c.score for c in report.categories.values()))

    def test_grade_bands(self):
        self.assertEqual(score.grade_from_score(90)[0], "AI-Native")
        self.assertEqual(score.grade_from_score(75)[0], "AI-Ready")
        self.assertEqual(score.grade_from_score(60)[0], "AI-Assisted")
        self.assertEqual(score.grade_from_score(59)[0], "AI-Fragile")
        self.assertEqual(score.grade_from_score(39)[0], "AI-Hostile")


class TestGoldenFixture(ScoreTestCase):
    """알려진 미니 저장소 → 고정 점수. regex/임계값 수정으로 등급이 조용히 밀리면 여기서 잡힌다."""

    def test_gates_pass_and_total_pinned(self):
        make_repo(self.repo, GOLDEN_FILES)
        report = score.build_report(self.repo)
        for g in report.gates:
            self.assertTrue(g.passed, f"gate {g.key} 실패: {g.detail}")
        self.assertFalse(report.grade_capped)
        # 픽스처 파일은 방금 생성돼 F(신선도)는 항상 만점 방향 — 시간 의존 없음.
        self.assertEqual(report.total, GOLDEN_TOTAL,
                         f"골든 총점 이동: {report.total} (categories: "
                         f"{ {k: c.score for k, c in report.categories.items()} })")


class TestGate1Precision(ScoreTestCase):
    def test_real_dangling_ref_caps_grade(self):
        files = dict(GOLDEN_FILES)
        files["README.md"] += "\nSee src/missing_module.py for details.\n"
        make_repo(self.repo, files)
        report = score.build_report(self.repo)
        gate1 = next(g for g in report.gates if g.key == "reference-integrity")
        self.assertFalse(gate1.passed)
        expected_grade = score.grade_from_score(min(report.total, score.GATE_CEILING_SCORE))[0]
        self.assertEqual(report.grade, expected_grade)

    def test_illustrative_path_not_flagged(self):
        # 첫 세그먼트(docs/)가 실제 top-level 디렉토리가 아니면 검증 대상에서 제외돼야 한다
        make_repo(self.repo, {"README.md": "예시: docs/example-spec.md 형태로 작성한다.\n"})
        refint = score.check_reference_integrity(self.repo, [self.repo / "README.md"])
        self.assertEqual(refint["total_paths"], 0)
        self.assertTrue(refint["passed"])

    def test_outside_repo_ref_not_probed(self):
        make_repo(self.repo, {"README.md": "부모 레포 참조: ../secret/keys.md\n"})
        refint = score.check_reference_integrity(self.repo, [self.repo / "README.md"])
        self.assertEqual(refint["total_paths"], 0)
        self.assertTrue(refint["passed"])

    def test_dangling_line_range_hits_gate_and_e1(self):
        # E1↔Gate-1 비대칭 회귀: 게이트를 뒤집는 dangling range는 E1 점수에도 반영돼야 한다
        make_repo(self.repo, {
            "README.md": "See src/app.py:1-999 for the hot path.\n",
            "src/app.py": "def main():\n    return 1\n",
        })
        refint = score.check_reference_integrity(self.repo, [self.repo / "README.md"])
        self.assertEqual(refint["total_paths"], 1)      # src/app.py 자체는 실존
        self.assertEqual(refint["total_ranges"], 1)
        self.assertEqual(len(refint["dangling_ranges"]), 1)
        self.assertFalse(refint["passed"])
        verif = score.detect_verification(self.repo)
        e = score.score_E(self.repo, refint, verif, [self.repo / "README.md"])
        # (2건 중 1건 dangling) → round(6 * 1/2) = 3. 구버전은 path만 세서 6점(비대칭 버그).
        self.assertEqual(e.sub_scores["E1_RefAccuracy"], 3)


class TestGate2Verification(ScoreTestCase):
    def test_go_manifest_without_tests_gets_build_only(self):
        make_repo(self.repo, {"go.mod": "module example.com/x\n", "main.go": "package main\n"})
        verif = score.detect_verification(self.repo)
        self.assertTrue(verif["build_cmd"])
        self.assertFalse(verif["test_cmd"], "테스트 흔적 없는 go.mod가 test_cmd를 얻으면 안 됨")
        self.assertEqual(verif["test_files"], 0)

    def test_go_manifest_with_tests_gets_test_cmd(self):
        make_repo(self.repo, {
            "go.mod": "module example.com/x\n",
            "main.go": "package main\n",
            "main_test.go": "package main\n",
        })
        verif = score.detect_verification(self.repo)
        self.assertTrue(verif["test_cmd"])


class TestHtmlSafeOutput(ScoreTestCase):
    def test_html_escape_deep(self):
        payload = {"meta": {"git_branch": "feat/<script>alert(1)</script>"},
                   "insights": ['경로 "a<b"'], "n": 3}
        safe = score.html_escape_deep(payload)
        self.assertEqual(safe["meta"]["git_branch"],
                         "feat/&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertEqual(safe["insights"][0], "경로 &quot;a&lt;b&quot;")
        self.assertEqual(safe["n"], 3)

    def test_main_writes_htmlsafe_sibling(self):
        make_repo(self.repo, GOLDEN_FILES)
        out = self.repo / "_out" / "ai-readiness-score.json"
        argv, sys.argv = sys.argv, ["score.py", str(self.repo), "--json", str(out), "--quiet"]
        try:
            rc = score.main()
        finally:
            sys.argv = argv
        self.assertEqual(rc, 0)
        self.assertTrue(out.exists())
        safe = out.with_name("ai-readiness-score.htmlsafe.json")
        self.assertTrue(safe.exists())
        # htmlsafe 사본의 어떤 문자열에도 raw '<' 가 남지 않아야 한다

        def strings(v):
            if isinstance(v, str):
                yield v
            elif isinstance(v, list):
                for x in v:
                    yield from strings(x)
            elif isinstance(v, dict):
                for k, x in v.items():
                    yield from strings(k)
                    yield from strings(x)

        data = json.loads(safe.read_text(encoding="utf-8"))
        for s in strings(data):
            self.assertNotIn("<", s)
            self.assertNotIn(">", s)


# 골든 픽스처 고정 총점 — GOLDEN_FILES/루브릭이 의도적으로 바뀌면 함께 갱신한다.
# (2026-07 핀: E17 D12 B8 C0 H0 A1 F2 I0 G0 = 40, AI-Fragile, gate 2/2 통과)
GOLDEN_TOTAL = 40


if __name__ == "__main__":
    unittest.main()
