#!/usr/bin/env python3
"""design-principle-harness score.py 회귀 테스트 (stdlib only — `python3 test_score.py`).

핀:
- 총점 = surface + design 불변식
- 개선 순서 = 쉬운 것(주석→명명)부터, 구조는 뒤로
- 각 섹션 탐지기(명명·주석·복잡도·결합·중복·순환·과대추상)의 기본 동작
- 신뢰 불가 repo 하드닝(symlink·null byte·빈 repo)
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import score as S


def _mk(repo: Path, rel: str, content: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


class TempRepo:
    def __enter__(self):
        self._d = tempfile.TemporaryDirectory()
        S.read_text.cache_clear()
        return Path(self._d.name)

    def __exit__(self, *a):
        S.read_text.cache_clear()
        self._d.cleanup()


def sect(rep, key):
    return next(s for s in rep.sections if s.key == key)


class TestInvariants(unittest.TestCase):
    def test_total_equals_tiers(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def compute_average(values):\n    return sum(values) / len(values)\n")
            rep = S.build_report(repo)
            self.assertEqual(rep.total, rep.tier_scores["surface"]["score"] + rep.tier_scores["design"]["score"])
            # 총점 = A(surface)+B(design)만. Tier C(context)는 report-only라 합산 제외.
            self.assertEqual(rep.total, sum(s.score for s in rep.sections if s.tier != "context"))
            self.assertLessEqual(rep.total, 100)

    def test_context_tier_excluded_from_total(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def compute_average(values):\n    return sum(values) / len(values)\n")
            rep = S.build_report(repo)
            ctx = [s for s in rep.sections if s.tier == "context"]
            self.assertTrue({s.key for s in ctx} >= {"C1", "C2"})
            self.assertIn("context", rep.tier_scores)
            # context 점수를 더해도 total 은 100 이하이고 A+B 와 같아야 한다(미포함 불변식).
            self.assertEqual(rep.total, rep.tier_scores["surface"]["score"] + rep.tier_scores["design"]["score"])
            for s in ctx:
                self.assertEqual(s.confidence, "report-only")

    def test_improvement_order_easy_first(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "x = 1\n")
            rep = S.build_report(repo)
            # 주석(A3)·명명(A1/A2) 이 구조(B*) 보다 앞
            order = rep.improvement_order
            self.assertEqual(order[0], "A3")
            self.assertIn("A1", order[:3])
            self.assertIn("A2", order[:3])
            self.assertTrue(order.index("A1") < order.index("B1"))
            self.assertTrue(order.index("B3") < order.index("B2"))  # 중복(M) 이 구조(L) 앞
            self.assertEqual(rep.extras["improvement_first"], order[:3])

    def test_json_serializable(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def f():\n    return 1\n")
            rep = S.build_report(repo)
            payload = json.dumps(S.to_dict(rep), ensure_ascii=False)
            self.assertIn("improvement_order", payload)


class TestSurface(unittest.TestCase):
    def test_bad_names_lower_a1(self):
        with TempRepo() as repo:
            _mk(repo, "bad.py", "def do_stuff(tmp):\n    data = tmp\n    return data\n\nclass Mgr:\n    pass\n")
            _mk(repo, "good.py", "def calculate_total(prices):\n    running_total = 0\n    return running_total\n")
            rep = S.build_report(repo)
            bad = S.build_report  # noqa
            a1 = sect(rep, "A1")
            self.assertLess(a1.score, a1.max)
            self.assertGreater(a1.evidence["nondescriptive"], 0)

    def test_clean_names_full_a1(self):
        with TempRepo() as repo:
            _mk(repo, "clean.py",
                "def calculate_invoice_total(line_items):\n    subtotal = 0\n    return subtotal\n\n"
                "class InvoiceService:\n    def render_receipt(self):\n        return None\n")
            rep = S.build_report(repo)
            a1 = sect(rep, "A1")
            self.assertEqual(a1.evidence["nondescriptive"], 0)
            self.assertEqual(a1.score, a1.max)

    def test_casing_violation_a2_python(self):
        with TempRepo() as repo:
            _mk(repo, "c.py", "def BadName():\n    return 1\n\nclass lower_class:\n    pass\n")
            rep = S.build_report(repo)
            a2 = sect(rep, "A2")
            self.assertGreater(a2.evidence["violations"], 0)

    def test_commented_out_code_penalizes_a3(self):
        with TempRepo() as repo:
            body = "def f():\n    return 1\n" + "".join(
                f"# result = compute({i}) + helper({i});\n" for i in range(12)
            )
            _mk(repo, "co.py", body)
            rep = S.build_report(repo)
            a3 = sect(rep, "A3")
            self.assertGreater(a3.evidence["commented_out"], 5)
            self.assertLess(a3.score, a3.max)

    def test_absence_of_comments_not_penalized(self):
        with TempRepo() as repo:
            _mk(repo, "n.py", "def add(a, b):\n    return a + b\n")
            rep = S.build_report(repo)
            a3 = sect(rep, "A3")
            self.assertEqual(a3.score, a3.max)  # 주석 없음은 감점 아님(정직성)


class TestDesign(unittest.TestCase):
    def test_complex_function_b1_hotspot(self):
        with TempRepo() as repo:
            lines = ["def big(x):"]
            for i in range(18):
                lines.append(f"    if x == {i}:")
                lines.append(f"        x = x + {i}")
            lines.append("    return x")
            _mk(repo, "cx.py", "\n".join(lines) + "\n")
            rep = S.build_report(repo)
            b1 = sect(rep, "B1")
            self.assertGreater(b1.evidence["hotspots"], 0)

    def test_coupling_hotspot_b2(self):
        with TempRepo() as repo:
            # 많은 파일이 core 를 import → core fan_in 높음
            _mk(repo, "core.py", "VALUE = 1\n")
            for i in range(20):
                _mk(repo, f"m{i}.py", "import core\n")
            rep = S.build_report(repo)
            b2 = sect(rep, "B2")
            self.assertGreaterEqual(b2.evidence["coupling_hotspots"], 1)

    def test_duplication_b3(self):
        with TempRepo() as repo:
            block = "".join(f"    step_{i} = transform(value_{i}) + offset\n" for i in range(8))
            _mk(repo, "d1.py", "def a():\n" + block + "    return step_0\n")
            _mk(repo, "d2.py", "def b():\n" + block + "    return step_0\n")
            rep = S.build_report(repo)
            b3 = sect(rep, "B3")
            self.assertGreater(b3.evidence["cluster_count"], 0)

    def test_cyclic_deps_python_b4(self):
        with TempRepo() as repo:
            _mk(repo, "pa/__init__.py", "import pb\n")
            _mk(repo, "pb/__init__.py", "import pa\n")
            rep = S.build_report(repo)
            b4 = sect(rep, "B4")
            self.assertGreaterEqual(b4.evidence["cycle_count"], 1)

    def test_cyclic_deps_js_b4(self):
        with TempRepo() as repo:
            _mk(repo, "a.js", "import { b } from './b';\nexport const a = 1;\n")
            _mk(repo, "b.js", "import { a } from './a';\nexport const b = 2;\n")
            rep = S.build_report(repo)
            b4 = sect(rep, "B4")
            self.assertGreaterEqual(b4.evidence["cycle_count"], 1)

    def test_no_cycles_full_b4(self):
        with TempRepo() as repo:
            _mk(repo, "pa/__init__.py", "import pb\n")
            _mk(repo, "pb/__init__.py", "VALUE = 1\n")
            rep = S.build_report(repo)
            b4 = sect(rep, "B4")
            self.assertEqual(b4.evidence["cycle_count"], 0)
            self.assertEqual(b4.score, b4.max)

    def test_single_impl_interface_b5(self):
        with TempRepo() as repo:
            _mk(repo, "types.ts", "interface PaymentGateway { charge(): void; }\n")
            _mk(repo, "stripe.ts", "class Stripe implements PaymentGateway { charge() {} }\n")
            rep = S.build_report(repo)
            b5 = sect(rep, "B5")
            self.assertGreaterEqual(b5.evidence["single_impl_interfaces"], 1)


class TestCommentGap(unittest.TestCase):
    def test_gap_candidates_detected(self):
        with TempRepo() as repo:
            _mk(repo, "a.py",
                "import re\n"
                "def f(x):\n"
                "    limit = 86400\n"
                "    r = re.compile(r'\\d+')\n"
                "    try:\n"
                "        g(x)\n"
                "    except Exception:\n"
                "        pass\n"
                "    return limit\n")
            rep = S.build_report(repo)
            a3 = sect(rep, "A3")
            gap = a3.evidence["comment_gap"]
            self.assertGreaterEqual(gap["empty_handlers"], 1)
            self.assertGreaterEqual(gap["regex_literals"], 1)
            self.assertGreaterEqual(gap["magic_numbers"], 1)

    def test_gap_is_report_only_not_scored(self):
        # 매직 넘버/정규식이 많아도 A3 점수를 낮추지 않는다(볼륨 가점/감점 금지·report-only).
        with TempRepo() as repo:
            clean = "def add(a, b):\n    return a + b\n"
            gappy = ("import re\n"
                     "def h(x):\n"
                     "    a = 12345\n    b = 67890\n"
                     "    p = re.compile(r'x')\n"
                     "    return a + b\n")
            _mk(repo, "clean.py", clean)
            rep_clean = S.build_report(repo)
            score_clean = sect(rep_clean, "A3").score
        with TempRepo() as repo:
            _mk(repo, "gappy.py", gappy)
            rep_gappy = S.build_report(repo)
            a3 = sect(rep_gappy, "A3")
            # gap 후보가 있어도 만점 유지(감점 없음) — 삭제 신호(오도/죽은 주석/TODO)만 감점.
            self.assertEqual(a3.score, a3.max)
            self.assertGreaterEqual(a3.evidence["comment_gap"]["magic_numbers"], 2)

    def test_numbers_in_strings_not_magic(self):
        with TempRepo() as repo:
            _mk(repo, "s.py", "def f():\n    return '86400 seconds'\n")
            rep = S.build_report(repo)
            gap = sect(rep, "A3").evidence["comment_gap"]
            self.assertEqual(gap["magic_numbers"], 0)


class TestContextSignals(unittest.TestCase):
    def test_c1_flags_div_onclick(self):
        with TempRepo() as repo:
            _mk(repo, "Widget.jsx",
                "export function Widget() {\n"
                "  return (<div onClick={handle}>click</div>);\n"
                "}\n")
            rep = S.build_report(repo)
            c1 = sect(rep, "C1")
            self.assertEqual(c1.tier, "context")
            self.assertGreaterEqual(c1.evidence["nonsemantic_click"], 1)

    def test_c1_native_button_not_penalized(self):
        with TempRepo() as repo:
            _mk(repo, "Ok.jsx",
                "export function Ok() {\n"
                "  return (<nav><button onClick={go}>go</button></nav>);\n"
                "}\n")
            rep = S.build_report(repo)
            c1 = sect(rep, "C1")
            self.assertEqual(c1.evidence["nonsemantic_click"], 0)
            self.assertGreaterEqual(c1.evidence["native_semantic"], 2)

    def test_c1_role_with_native_flagged(self):
        with TempRepo() as repo:
            _mk(repo, "R.jsx", 'export const R = () => <div role="button">x</div>;\n')
            rep = S.build_report(repo)
            c1 = sect(rep, "C1")
            self.assertGreaterEqual(c1.evidence["role_with_native"], 1)

    def test_c1_na_when_no_markup(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def f():\n    return 1\n")
            rep = S.build_report(repo)
            c1 = sect(rep, "C1")
            self.assertEqual(c1.evidence.get("markup_files"), 0)

    def test_c2_flags_vague_test_names(self):
        with TempRepo() as repo:
            _mk(repo, "a.test.js",
                "describe('thing', () => {\n"
                "  it('works', () => {});\n"
                "  it('test1', () => {});\n"
                "  it('renders the invoice total for paid orders', () => {});\n"
                "});\n")
            rep = S.build_report(repo)
            c2 = sect(rep, "C2")
            self.assertEqual(c2.tier, "context")
            self.assertGreaterEqual(c2.evidence["vague_titles"], 2)

    def test_c2_selector_semantics(self):
        with TempRepo() as repo:
            _mk(repo, "b.spec.tsx",
                "test('submits the form', () => {\n"
                "  screen.getByRole('button');\n"
                "  screen.getByTestId('submit');\n"
                "  container.querySelector('.btn');\n"
                "});\n")
            rep = S.build_report(repo)
            c2 = sect(rep, "C2")
            self.assertGreaterEqual(c2.evidence["accessible_queries"], 1)
            self.assertGreaterEqual(c2.evidence["nonsemantic_queries"], 2)

    def test_c2_python_test_names(self):
        with TempRepo() as repo:
            _mk(repo, "test_thing.py",
                "def test_works():\n    pass\n\n"
                "def test_computes_invoice_total_for_paid_orders():\n    pass\n")
            rep = S.build_report(repo)
            c2 = sect(rep, "C2")
            self.assertEqual(c2.evidence["titles"], 2)
            self.assertGreaterEqual(c2.evidence["vague_titles"], 1)

    def test_c2_na_when_no_tests(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def f():\n    return 1\n")
            rep = S.build_report(repo)
            c2 = sect(rep, "C2")
            self.assertEqual(c2.evidence.get("test_files"), 0)


class TestHardening(unittest.TestCase):
    def test_empty_repo(self):
        with TempRepo() as repo:
            rep = S.build_report(repo)
            self.assertIsInstance(rep.total, int)
            self.assertEqual(rep.meta["code_files"], 0)

    def test_null_byte_py_does_not_crash(self):
        with TempRepo() as repo:
            (repo / "bad.py").write_bytes(b"def f():\x00\n    return 1\n")
            _mk(repo, "ok.py", "def g():\n    return 2\n")
            rep = S.build_report(repo)  # 예외 없이 완료
            self.assertIsInstance(rep.total, int)

    def test_symlink_not_followed(self):
        with TempRepo() as repo:
            outside = Path(tempfile.mkdtemp())
            try:
                (outside / "secret.py").write_text("SECRET = 'x'\n")
                try:
                    os.symlink(outside / "secret.py", repo / "link.py")
                except (OSError, NotImplementedError):
                    self.skipTest("symlink unsupported")
                files = S.walk_code_files(repo)
                self.assertTrue(all("link.py" not in f.name for f in files))
            finally:
                import shutil
                shutil.rmtree(outside, ignore_errors=True)

    def test_markdown_renders(self):
        with TempRepo() as repo:
            _mk(repo, "a.py", "def f():\n    return 1\n")
            rep = S.build_report(repo)
            md = S.render_markdown(rep)
            self.assertIn("설계 품질 점수표", md)
            self.assertIn("개선 순서", md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
