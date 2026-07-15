#!/usr/bin/env python3
"""ai_access.py 회귀 테스트 (stdlib only — `python3 test_ai_access.py`).

핀:
- SCORED는 M1(의존 방향 강제)·M2(독립 실행)뿐 — 나머지는 report-only(총점 driver 아님)
- 각 탐지기(dep-cruiser·eslint-boundaries·import-linter·러너·워크스페이스·가이드·strict) 기본 동작
- 에이전트 가이드 bloat 감점·presence≠performance 정직성 핀
- 신뢰 불가 repo 하드닝(빈 repo·symlink·손상)
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import ai_access as A


def _mk(repo: Path, rel: str, content: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class TempRepo:
    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        return Path(self._d.name)

    def __exit__(self, *a):
        self._d.cleanup()


def metric(a, key):
    return next(m for m in a.metrics if m.key == key)


class TestScoredInvariant(unittest.TestCase):
    def test_only_m1_m2_scored(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            scored = {m.key for m in a.metrics if m.scored}
            self.assertEqual(scored, {"M1", "M2"})
            self.assertEqual(a.enforced_max, metric(a, "M1").max + metric(a, "M2").max)

    def test_report_only_not_in_enforced(self):
        with TempRepo() as repo:
            _mk(repo, "CLAUDE.md", "# guide\nnpm run build\n")
            a = A.build_assessment(repo)
            # 가이드/패턴 등 report-only 점수는 enforced_score에 들어가지 않는다.
            self.assertEqual(a.enforced_score,
                             metric(a, "M1").score + metric(a, "M2").score)

    def test_honesty_present(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            joined = " ".join(a.honesty)
            self.assertIn("인증", joined)
            self.assertIn("tool-index", joined)
            self.assertIn("독립 oracle", joined)


class TestDepEnforcement(unittest.TestCase):
    def test_dependency_cruiser(self):
        with TempRepo() as repo:
            _mk(repo, ".dependency-cruiser.js", "module.exports = { forbidden: [] };\n")
            a = A.build_assessment(repo)
            m = metric(a, "M1")
            self.assertIn("dependency-cruiser", m.evidence["tools"])
            self.assertGreater(m.score, 0)
            self.assertEqual(m.confidence, "STRONG")

    def test_eslint_boundaries(self):
        with TempRepo() as repo:
            _mk(repo, ".eslintrc.json", '{ "rules": { "no-restricted-imports": ["error"] } }\n')
            a = A.build_assessment(repo)
            self.assertIn("eslint-boundaries", metric(a, "M1").evidence["tools"])

    def test_import_linter(self):
        with TempRepo() as repo:
            _mk(repo, "setup.cfg", "[importlinter]\nroot_package = mypkg\n")
            a = A.build_assessment(repo)
            self.assertIn("import-linter", metric(a, "M1").evidence["tools"])

    def test_no_enforcement_zero_and_candidate(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            m = metric(a, "M1")
            self.assertEqual(m.score, 0)
            self.assertTrue(any("개선 후보" in f for f in m.findings))

    def test_ci_boost_and_warning(self):
        with TempRepo() as repo:
            _mk(repo, ".dependency-cruiser.js", "module.exports = {};\n")
            a_no_ci = A.build_assessment(repo)
        with TempRepo() as repo:
            _mk(repo, ".dependency-cruiser.js", "module.exports = {};\n")
            _mk(repo, ".github/workflows/ci.yml", "name: ci\n")
            a_ci = A.build_assessment(repo)
        self.assertGreater(metric(a_ci, "M1").score, metric(a_no_ci, "M1").score)
        self.assertTrue(any("CI 실행 흔적 미검출" in f for f in metric(a_no_ci, "M1").findings))


class TestStandalone(unittest.TestCase):
    def test_runner_and_workspaces(self):
        with TempRepo() as repo:
            _mk(repo, "package.json",
                '{ "scripts": {"test":"vitest","build":"tsc"}, "workspaces":["packages/*"] }')
            _mk(repo, "a.test.ts", "test('x', () => {});\n")
            a = A.build_assessment(repo)
            m = metric(a, "M2")
            self.assertIn("vitest", m.evidence["runners"])
            self.assertTrue(m.evidence["workspaces"])
            self.assertGreater(m.score, 5)

    def test_independent_oracle_guard_always_present(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            self.assertTrue(any("독립 oracle" in f and "81~100%" in f for f in metric(a, "M2").findings))


class TestBuildFeedback(unittest.TestCase):
    def test_ts_strict_reported(self):
        with TempRepo() as repo:
            _mk(repo, "tsconfig.json", '{ "compilerOptions": { "strict": true } }')
            a = A.build_assessment(repo)
            m = metric(a, "M3")
            self.assertTrue(m.evidence["ts_strict"])
            self.assertFalse(m.scored)  # report-only

    def test_impossiblebench_goodhart_caveat(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            self.assertTrue(any("correctness로 credit 금지" in f for f in metric(a, "M3").findings))


class TestAgentGuides(unittest.TestCase):
    def test_claude_md_non_inferable(self):
        with TempRepo() as repo:
            _mk(repo, "CLAUDE.md", "# Dev\n```\nnpm run build\n```\nboundary: a must not import b\n")
            a = A.build_assessment(repo)
            m = metric(a, "M6")
            self.assertIn("CLAUDE.md", m.evidence["guides"])
            self.assertGreater(m.evidence["non_inferable_signals"], 0)
            self.assertFalse(m.scored)

    def test_bloat_penalized(self):
        with TempRepo() as repo:
            big = "# guide\n" + "\n".join(f"line {i} npm run x" for i in range(500))
            _mk(repo, "CLAUDE.md", big)
            a = A.build_assessment(repo)
            m = metric(a, "M6")
            self.assertGreaterEqual(m.evidence["bloat_files"], 1)
            self.assertTrue(any("bloat" in f.lower() or "비대" in f for f in m.findings))

    def test_presence_not_performance_caveat(self):
        with TempRepo() as repo:
            _mk(repo, "AGENTS.md", "# x\n")
            a = A.build_assessment(repo)
            self.assertTrue(any("presence ≠ performance" in f or "presence≠performance" in f
                                for f in metric(a, "M6").findings))


class TestPatternConsistency(unittest.TestCase):
    def test_mixed_module_systems_flagged(self):
        with TempRepo() as repo:
            for i in range(5):
                _mk(repo, f"esm{i}.js", "import x from 'y';\nexport const z = 1;\n")
            for i in range(5):
                _mk(repo, f"cjs{i}.js", "const x = require('y');\n")
            a = A.build_assessment(repo)
            m = metric(a, "M5")
            self.assertTrue(m.evidence["mixed_module_systems"])
            self.assertFalse(m.scored)


class TestHardening(unittest.TestCase):
    def test_empty_repo(self):
        with TempRepo() as repo:
            a = A.build_assessment(repo)
            self.assertEqual(a.enforced_score, 0)
            self.assertEqual(a.meta["files_scanned"], 0)

    def test_json_serializable(self):
        with TempRepo() as repo:
            _mk(repo, "package.json", '{ "scripts": {"test":"jest"} }')
            a = A.build_assessment(repo)
            payload = json.dumps(A.to_dict(a), ensure_ascii=False)
            self.assertIn("enforced_score", payload)

    def test_markdown_renders(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            a = A.build_assessment(repo)
            md = A.render_markdown(a)
            self.assertIn("AI 접근성 assessment", md)
            self.assertIn("인증이 아니다", md)

    def test_corrupt_json_pkg_no_crash(self):
        with TempRepo() as repo:
            _mk(repo, "package.json", "{ not valid json ")
            a = A.build_assessment(repo)  # 예외 없이 완료
            self.assertIsInstance(a.enforced_score, int)

    def test_symlink_not_followed(self):
        with TempRepo() as repo:
            outside = Path(tempfile.mkdtemp())
            try:
                (outside / "secret.txt").write_text("SECRET\n")
                try:
                    os.symlink(outside / "secret.txt", repo / "link.txt")
                except (OSError, NotImplementedError):
                    self.skipTest("symlink unsupported")
                files = A.walk_files(repo)
                self.assertTrue(all("link.txt" not in f.name for f in files))
            finally:
                import shutil
                shutil.rmtree(outside, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
