#!/usr/bin/env python3
"""legibility_scan.py 회귀 테스트.

실행: python3 test_legibility_scan.py   (stdlib only, 외부 의존 없음)

여기 담긴 테스트는 두 종류다:
  1. **불변식 핀** — 이 하네스가 절대 하면 안 되는 것(등급 산출, 측정 불가를 '깨끗함'으로 보고).
  2. **회귀 핀** — 개발 중 실제로 발견된 버그가 되돌아오지 못하게 막는다.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import legibility_scan as ls  # noqa: E402


def scan(files: dict[str, str], axes: str = "naming,comments,structure", **kw) -> dict:
    """임시 디렉토리에 파일을 쓰고 스캔한 결과 리포트를 반환."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return _scan_dir(root, axes, **kw)


def _scan_dir(root: Path, axes: str, top: int = 20, max_files: int = 5000) -> dict:
    """프로덕션과 동일한 파이프라인(run_scan)을 호출한다 — 테스트가 다른 코드를 재구현하지 않는다."""
    return ls.run_scan(
        root.resolve(),
        {a for a in axes.split(",") if a},
        top=top,
        max_files=max_files,
    )


def detectors(report: dict) -> dict[str, int]:
    return report["counts"]["by_detector"]


def findings_of(report: dict, detector: str) -> list[dict]:
    out = []
    for axis_findings in report["findings"].values():
        out.extend(f for f in axis_findings if f["detector"] == detector)
    return out


# ---------------------------------------------------------------------------
# 불변식 핀 — 이 하네스의 정체성
# ---------------------------------------------------------------------------
class InvariantTests(unittest.TestCase):
    def test_report_never_contains_a_grade_or_score(self):
        """등급·점수를 만들면 자매 플러그인(ai-readiness-cartography)과 충돌한다."""
        report = scan({"a.py": "def get_x():\n    pass\n"})
        blob = json.dumps(report, ensure_ascii=False).lower()
        for banned in ('"score"', '"grade":', '"total_score"', '"level"', '"band"'):
            self.assertNotIn(banned, blob, f"census에 등급성 키 {banned} 가 들어갔다")
        # `grade` 는 탐지기의 근거 등급 라벨로만 쓰인다.
        for f in findings_of(report, "N3_MISLEADING_GETTER"):
            self.assertIn(f["grade"], {"auto-high", "auto-med", "auto-low", "heuristic", "report-only"})

    def test_structure_is_report_only_with_no_threshold_verdict(self):
        """'N줄 초과 = 나쁨'을 판정할 1차 근거가 없다."""
        body = "\n".join(f"    x{i} = {i}" for i in range(200))
        report = scan({"big.py": f"def huge():\n{body}\n"})
        section = report["structure_report_only"]
        self.assertIn("임계값 없음", section["note"])
        self.assertTrue(section["largest_units"])
        # 크기만으로는 어떤 finding도 생기지 않는다.
        self.assertEqual(detectors(report).get("S1_LARGE_UNIT", 0), 0)

    def test_unmeasurable_files_are_reported_not_silently_clean(self):
        """측정 불가(too-large)는 '결함 없음'이 아니다."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "huge.py").write_text("# x\n" * 400_000, encoding="utf-8")
            self.assertGreater((root / "huge.py").stat().st_size, ls.MAX_FILE_BYTES)
            report = _scan_dir(root, "comments")
        self.assertEqual(report["scanned"]["files"], 0)
        reasons = [s["reason"] for s in report["scanned"]["skipped"]]
        self.assertTrue(any("too-large" in r for r in reasons), reasons)

    def test_symbol_collision_is_heuristic_never_promoted(self):
        """N4는 근거 없는 진단 정보다. 개입 후보로 승격하면 안 된다."""
        files = {f"m{i}.py": "def handler():\n    return 1\n" for i in range(3)}
        report = scan(files)
        hits = findings_of(report, "N4_SYMBOL_COLLISION")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["grade"], "heuristic")
        self.assertIn("근거 없음", hits[0]["extra"]["evidence"])

    def test_axes_filter_is_a_hard_scope_guard(self):
        """사용자가 고르지 않은 축은 스캔조차 하지 않는다."""
        src = "def get_thing(tmp):\n    # TODO: x\n    pass\n"
        only_comments = scan({"a.py": src}, axes="comments")
        self.assertEqual(only_comments["counts"]["by_axis"].get("naming", 0), 0)
        self.assertGreater(only_comments["counts"]["by_axis"].get("comments", 0), 0)

        only_naming = scan({"a.py": src}, axes="naming")
        self.assertEqual(only_naming["counts"]["by_axis"].get("comments", 0), 0)
        self.assertGreater(only_naming["counts"]["by_axis"].get("naming", 0), 0)


# ---------------------------------------------------------------------------
# 명명 축
# ---------------------------------------------------------------------------
class NamingTests(unittest.TestCase):
    def test_predicate_returning_non_bool_literal(self):
        report = scan({"a.py": 'def is_ready(x):\n    return "yes"\n'})
        hits = findings_of(report, "N2_MISLEADING_PREDICATE")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["extra"]["returned"], ["str"])

    def test_predicate_returning_bool_is_not_flagged(self):
        report = scan({"a.py": "def is_ready(x):\n    return bool(x) and x > 0\n"})
        self.assertEqual(detectors(report).get("N2_MISLEADING_PREDICATE", 0), 0)

    def test_predicate_with_no_return_is_flagged(self):
        report = scan({"a.py": "def has_items(x):\n    print(x)\n"})
        self.assertEqual(len(findings_of(report, "N2_MISLEADING_PREDICATE")), 1)

    def test_getter_without_return_is_flagged(self):
        report = scan({"a.py": "def get_total(xs):\n    total = sum(xs)\n    print(total)\n"})
        self.assertEqual(len(findings_of(report, "N3_MISLEADING_GETTER")), 1)

    def test_getter_with_return_is_not_flagged(self):
        report = scan({"a.py": "def get_total(xs):\n    return sum(xs)\n"})
        self.assertEqual(detectors(report).get("N3_MISLEADING_GETTER", 0), 0)

    def test_getter_returning_none_explicitly_is_not_flagged(self):
        """`find_x` 가 못 찾으면 None 을 반환하는 것은 정상이다 (거짓양성 방지)."""
        report = scan({"a.py": "def find_user(uid):\n    if uid:\n        return uid\n    return None\n"})
        self.assertEqual(detectors(report).get("N3_MISLEADING_GETTER", 0), 0)

    def test_generator_getter_is_not_flagged(self):
        report = scan({"a.py": "def get_rows(xs):\n    for r in xs:\n        yield r\n"})
        self.assertEqual(detectors(report).get("N3_MISLEADING_GETTER", 0), 0)

    def test_stub_body_is_not_flagged(self):
        src = (
            "def get_thing():\n    raise NotImplementedError\n\n"
            "def is_thing():\n    ...\n"
        )
        report = scan({"a.py": src})
        self.assertEqual(detectors(report).get("N3_MISLEADING_GETTER", 0), 0)
        self.assertEqual(detectors(report).get("N2_MISLEADING_PREDICATE", 0), 0)

    def test_nondescriptive_is_case_insensitive(self):
        """회귀 핀: `class Foo` 가 사전에 `foo` 만 있어서 빠져나갔다."""
        report = scan({"a.py": "class Foo:\n    pass\n"})
        hits = findings_of(report, "N1_NONDESCRIPTIVE")
        self.assertTrue(any(h["symbol"] == "Foo" for h in hits), hits)

    def test_loop_variable_single_char_is_exempt(self):
        report = scan({"a.py": "def run(rows):\n    for q in rows:\n        print(q)\n"})
        single = [h for h in findings_of(report, "N1_NONDESCRIPTIVE") if h["symbol"] == "q"]
        self.assertEqual(single, [])

    def test_non_loop_single_char_local_is_flagged(self):
        report = scan({"a.py": "def run(rows):\n    q = rows[0]\n    return q\n"})
        single = [h for h in findings_of(report, "N1_NONDESCRIPTIVE") if h["symbol"] == "q"]
        self.assertEqual(len(single), 1)

    def test_dunder_function_is_not_flagged(self):
        report = scan({"a.py": "class A:\n    def __init__(self):\n        pass\n"})
        self.assertEqual(detectors(report).get("N3_MISLEADING_GETTER", 0), 0)


# ---------------------------------------------------------------------------
# 주석 축
# ---------------------------------------------------------------------------
class CommentTests(unittest.TestCase):
    def test_sphinx_docstring_param_mismatch(self):
        src = 'def f(a):\n    """Do.\n\n    :param a: x\n    :param b: gone\n    """\n    return a\n'
        hits = findings_of(scan({"a.py": src}), "C2_DOCSTRING_PARAM_MISMATCH")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["extra"]["documented_but_absent"], ["b"])

    def test_google_docstring_param_mismatch(self):
        src = 'def f(a):\n    """Do.\n\n    Args:\n        a: x\n        b: gone\n\n    Returns:\n        int\n    """\n    return a\n'
        hits = findings_of(scan({"a.py": src}), "C2_DOCSTRING_PARAM_MISMATCH")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["extra"]["documented_but_absent"], ["b"])

    def test_numpy_docstring_param_mismatch(self):
        src = 'def f(a):\n    """Do.\n\n    Parameters\n    ----------\n    a : int\n    b : int\n    """\n    return a\n'
        hits = findings_of(scan({"a.py": src}), "C2_DOCSTRING_PARAM_MISMATCH")
        self.assertEqual(len(hits), 1)

    def test_matching_docstring_is_not_flagged(self):
        src = 'def f(a):\n    """Do.\n\n    :param a: x\n    """\n    return a\n'
        self.assertEqual(detectors(scan({"a.py": src})).get("C2_DOCSTRING_PARAM_MISMATCH", 0), 0)

    def test_dangling_backticked_identifier(self):
        src = '"""See `legacy_helper` for details."""\n\ndef current():\n    return 1\n'
        hits = findings_of(scan({"a.py": src}), "C1_DANGLING_IDENT")
        self.assertEqual([h["symbol"] for h in hits], ["legacy_helper"])
        self.assertEqual(hits[0]["extra"]["severity"], "not-in-index")
        self.assertEqual(hits[0]["extra"]["marker"], "strong")
        self.assertEqual(hits[0]["grade"], "auto-med")

    def test_bare_prose_token_is_weak_and_never_an_intervention_candidate(self):
        """회귀 핀: 훅 주석의 `tool_input`·`PreToolUse` 는 외부 스키마이지 이 파일의 심볼이 아니다."""
        src = "# reads tool_input on PreToolUse events\ndef handler():\n    return 1\n"
        hits = findings_of(scan({"a.py": src}), "C1_DANGLING_IDENT")
        self.assertTrue(hits)
        for h in hits:
            self.assertEqual(h["extra"]["marker"], "weak")
            self.assertEqual(h["grade"], "heuristic", h)

    def test_quoted_json_path_is_not_a_dangling_reference(self):
        """회귀 핀: `'.tool_input.command'` 는 리터럴 경로이지 심볼 참조가 아니다."""
        src = "# usage: hook_field '.tool_input.command'\ndef hook_field(path):\n    return path\n"
        hits = findings_of(scan({"a.py": src}), "C1_DANGLING_IDENT")
        self.assertEqual([h["symbol"] for h in hits], [], hits)

    def test_dotted_member_access_is_not_a_dangling_reference(self):
        src = "# result of obj.some_field is cached\ndef run(obj):\n    return obj\n"
        hits = findings_of(scan({"a.py": src}), "C1_DANGLING_IDENT")
        self.assertEqual([h["symbol"] for h in hits], [], hits)

    def test_dangling_identifier_found_elsewhere_is_marked_moved(self):
        files = {
            "a.py": "# uses `shared_helper` from the other module\ndef here():\n    return 1\n",
            "b.py": "def shared_helper():\n    return 2\n",
        }
        hits = findings_of(scan(files), "C1_DANGLING_IDENT")
        moved = [h for h in hits if h["symbol"] == "shared_helper"]
        self.assertEqual(len(moved), 1)
        self.assertEqual(moved[0]["extra"]["severity"], "moved-or-stale")

    def test_comment_with_url_is_skipped(self):
        src = "# see https://example.com/some_path/other_thing\ndef f():\n    return 1\n"
        self.assertEqual(detectors(scan({"a.py": src})).get("C1_DANGLING_IDENT", 0), 0)

    def test_identifier_present_in_file_is_not_dangling(self):
        src = "# calls `helper_fn`\ndef helper_fn():\n    return 1\n"
        self.assertEqual(detectors(scan({"a.py": src})).get("C1_DANGLING_IDENT", 0), 0)

    def test_commented_out_code_detected(self):
        src = "def f():\n    # x = 1\n    # print(x)\n    return 2\n"
        hits = findings_of(scan({"a.py": src}), "C3_COMMENTED_OUT_CODE")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["extra"]["lines"], 2)

    def test_prose_comment_is_not_code(self):
        src = "def f():\n    # this explains why we do it\n    return 2\n"
        self.assertEqual(detectors(scan({"a.py": src})).get("C3_COMMENTED_OUT_CODE", 0), 0)

    def test_directive_only_block_is_not_code(self):
        """회귀 핀: `# noqa: E501` 은 AnnAssign 으로 파싱되지만 코드가 아니다."""
        src = "# noqa: E501\n# type: ignore\ndef f():\n    return 1\n"
        self.assertEqual(detectors(scan({"a.py": src})).get("C3_COMMENTED_OUT_CODE", 0), 0)

    def test_directive_inside_block_does_not_suppress_detection(self):
        """회귀 핀: 지시자 한 줄이 블록 전체를 무효화하던 버그."""
        src = "def f():\n    # print(x)\n    # x = x * 2\n    # noqa: E501\n    return 1\n"
        hits = findings_of(scan({"a.py": src}), "C3_COMMENTED_OUT_CODE")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["extra"]["lines"], 2)
        self.assertEqual(hits[0]["line"], 2)

    def test_debt_markers(self):
        src = "# TODO: later\n# FIXME: now\ndef f():\n    return 1\n"
        self.assertEqual(detectors(scan({"a.py": src})).get("C4_DEBT_MARKER", 0), 2)


# ---------------------------------------------------------------------------
# 제네릭 언어 (auto-low)
# ---------------------------------------------------------------------------
class GenericLangTests(unittest.TestCase):
    def test_string_containing_comment_marker_is_not_a_comment(self):
        """회귀 핀: `const s = "// not a comment"` 를 주석으로 오인하면 안 된다."""
        src = 'const message = "// gone_symbol";\n'
        self.assertEqual(detectors(scan({"a.js": src})).get("C1_DANGLING_IDENT", 0), 0)

    def test_js_line_comment_dangling(self):
        src = "// calls calcTotal()\nconst realThing = 1;\n"
        hits = findings_of(scan({"a.js": src}), "C1_DANGLING_IDENT")
        self.assertEqual([h["symbol"] for h in hits], ["calcTotal"])

    def test_js_block_comment_todo(self):
        src = "/* TODO: cache this */\nfunction realWork() { return 1; }\n"
        self.assertEqual(detectors(scan({"a.js": src})).get("C4_DEBT_MARKER", 0), 1)

    def test_js_nondescriptive_declaration_is_auto_low(self):
        hits = findings_of(scan({"a.js": "const tmp = 1;\n"}), "N1_NONDESCRIPTIVE")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["grade"], "auto-low")

    def test_tsx_component_declaration_scanned(self):
        hits = findings_of(scan({"C.tsx": "function Foo() { return null; }\n"}), "N1_NONDESCRIPTIVE")
        self.assertTrue(any(h["symbol"] == "Foo" for h in hits))


# ---------------------------------------------------------------------------
# 하드닝 (신뢰할 수 없는 저장소)
# ---------------------------------------------------------------------------
class HardeningTests(unittest.TestCase):
    def test_symlinked_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            outside = root / "outside.py"
            outside.write_text("def get_x():\n    pass\n", encoding="utf-8")
            inner = root / "pkg"
            inner.mkdir()
            try:
                os.symlink(outside, inner / "link.py")
            except (OSError, NotImplementedError):
                self.skipTest("symlink 미지원 환경")
            report = _scan_dir(inner, "naming")
        self.assertEqual(report["scanned"]["files"], 0)
        self.assertTrue(any(s["reason"] == "symlink" for s in report["scanned"]["skipped"]))

    def test_symlinked_directory_is_not_followed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "target"
            target.mkdir()
            (target / "leak.py").write_text("tmp = 1\n", encoding="utf-8")
            work = root / "work"
            work.mkdir()
            try:
                os.symlink(target, work / "linked")
            except (OSError, NotImplementedError):
                self.skipTest("symlink 미지원 환경")
            report = _scan_dir(work, "naming")
        self.assertEqual(report["scanned"]["files"], 0)

    def test_null_byte_file_does_not_abort_scan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "bad.py").write_bytes(b"def f():\x00\n    pass\n")
            (root / "ok.py").write_text("tmp = 1\n", encoding="utf-8")
            report = _scan_dir(root, "naming")
        # 나쁜 파일 때문에 전체 스캔이 죽지 않는다.
        self.assertEqual(report["scanned"]["files"], 1)
        self.assertTrue(any("binary" in s["reason"] for s in report["scanned"]["skipped"]))

    def test_syntax_error_file_falls_back_not_crash(self):
        report = scan({"broken.py": "def f(:\n  pass\n# TODO: fix\n"})
        self.assertTrue(any("python-parse-failed" in s["reason"] for s in report["scanned"]["skipped"]))
        # 폴백 경로에서 주석은 여전히 읽힌다.
        self.assertEqual(detectors(report).get("C4_DEBT_MARKER", 0), 1)

    def test_long_single_line_does_not_hang(self):
        """ReDoS 가드: 긴 문자 런에서 백트래킹이 폭발하면 안 된다."""
        src = "# " + ("a" * 200_000) + "\ndef f():\n    return 1\n"
        report = scan({"a.py": src})
        self.assertIsInstance(report["counts"]["total_findings"], int)


# ---------------------------------------------------------------------------
# 독립성 핀 — 이 플러그인은 단독으로 설치·실행된다
# ---------------------------------------------------------------------------
class IndependenceTests(unittest.TestCase):
    def test_scanner_imports_are_stdlib_only(self):
        """외부 패키지도, 다른 플러그인의 모듈도 import 하지 않는다."""
        import ast as _ast
        source = (Path(__file__).parent / "legibility_scan.py").read_text(encoding="utf-8")
        imported: set[str] = set()
        for node in _ast.walk(_ast.parse(source)):
            if isinstance(node, _ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, _ast.ImportFrom) and node.module and node.level == 0:
                imported.add(node.module.split(".")[0])
        allowed = set(sys.stdlib_module_names) | {"__future__"}
        self.assertEqual(imported - allowed, set(), f"비-stdlib import: {sorted(imported - allowed)}")

    def test_no_markdown_link_escapes_the_plugin(self):
        """문서 링크가 플러그인 경계를 넘으면 단독 설치 시 깨진다."""
        import re as _re
        plugin_root = Path(__file__).resolve().parents[3]
        if not (plugin_root / ".claude-plugin" / "plugin.json").exists():
            self.skipTest("플러그인 루트 밖에서 실행됨")
        escapes = []
        for md in plugin_root.rglob("*.md"):
            for m in _re.finditer(r"\]\(([^)#]+)\)", md.read_text(encoding="utf-8")):
                link = m.group(1).strip()
                if link.startswith(("http://", "https://", "mailto:")):
                    continue
                target = (md.parent / link).resolve()
                if not str(target).startswith(str(plugin_root)):
                    escapes.append(f"{md.relative_to(plugin_root)} → {link}")
                elif not target.exists():
                    escapes.append(f"{md.relative_to(plugin_root)} → {link} (없는 대상)")
        self.assertEqual(escapes, [], f"플러그인 밖을 가리키거나 깨진 링크: {escapes}")

    def test_scanner_runs_against_a_target_outside_its_own_tree(self):
        """스캐너는 자기 위치와 무관한 저장소를 스캔한다 (cwd 비의존)."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            (target / "app.py").write_text("def get_name(u):\n    tmp = u\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "legibility_scan.py"), str(target)],
                capture_output=True, timeout=60, cwd="/",
            )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        report = json.loads(proc.stdout.decode())
        self.assertGreater(report["counts"]["total_findings"], 0)

class CommentGapTests(unittest.TestCase):
    """C7~C9 — 코드만으로 '왜'를 알기 어려운 지점(주석 *추가* 후보 · report-only)."""

    def test_silent_handler_is_a_candidate_not_a_defect(self):
        report = scan({"a.py": "def f(x):\n    try:\n        g(x)\n    except ValueError:\n        pass\n"},
                      axes="comments")
        found = findings_of(report, "C7_SILENT_HANDLER")
        self.assertEqual(len(found), 1, report["counts"]["by_detector"])
        # 후보는 report-only 라벨이어야 한다 — 결함 판정으로 승격하면 '주석 의무'가 된다.
        self.assertEqual(found[0]["grade"], "report-only")

    def test_js_silent_catch(self):
        report = scan({"a.js": "try { g(); } catch (e) {}\n"}, axes="comments")
        self.assertEqual(len(findings_of(report, "C7_SILENT_HANDLER")), 1)

    def test_magic_number_inside_string_or_comment_is_not_counted(self):
        """회귀 핀: 리터럴·주석 안의 숫자를 매직 넘버로 오판하면 census가 소음이 된다."""
        src = ('MSG = "error 404 not found"\n'
               '# see RFC 2616 for details\n'
               'TIMEOUT_MS = 5000\n')
        report = scan({"a.py": src}, axes="comments")
        found = findings_of(report, "C8_MAGIC_NUMBER")
        self.assertEqual([f["symbol"] for f in found], ["5000"], found)
        # 마스킹은 길이·줄바꿈을 보존하므로 줄번호가 원본과 일치해야 한다.
        self.assertEqual(found[0]["line"], 3)

    def test_small_numbers_are_not_magic(self):
        report = scan({"a.py": "x = arr[0] + 1 + 2\n"}, axes="comments")
        self.assertEqual(findings_of(report, "C8_MAGIC_NUMBER"), [])

    def test_regex_use_is_flagged(self):
        report = scan({"a.py": "import re\nP = re.compile(r'^a+$')\n"}, axes="comments")
        self.assertEqual(len(findings_of(report, "C9_REGEX_LITERAL")), 1)

    def test_comment_gap_is_off_when_comments_axis_not_selected(self):
        """스코프 가드 — 고르지 않은 축은 스캔하지 않는다."""
        report = scan({"a.py": "TIMEOUT = 5000\n"}, axes="naming")
        self.assertEqual(findings_of(report, "C8_MAGIC_NUMBER"), [])


class MarkupTests(unittest.TestCase):
    """MK1~MK4 — 시맨틱 마크업 & a11y (report-only · 볼륨 가점 금지)."""

    def test_nonsemantic_click_and_redundant_role(self):
        report = scan({"W.jsx": '<div onClick={go} role="button">go</div>\n'}, axes="markup")
        self.assertEqual(len(findings_of(report, "MK1_NONSEMANTIC_CLICK")), 1)
        self.assertEqual(len(findings_of(report, "MK2_REDUNDANT_ROLE")), 1)

    def test_role_without_native_equivalent_is_not_flagged(self):
        report = scan({"W.jsx": '<div role="tabpanel">x</div>\n'}, axes="markup")
        self.assertEqual(findings_of(report, "MK2_REDUNDANT_ROLE"), [])

    def test_img_with_alt_is_not_flagged(self):
        report = scan({"W.jsx": '<img src="a.png" alt="설명" />\n<img src="b.png" />\n'}, axes="markup")
        found = findings_of(report, "MK3_IMG_MISSING_ALT")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["line"], 2)

    def test_html_and_vue_files_are_scanned(self):
        report = scan({"page.html": "<div onClick=go></div>", "C.vue": "<div onclick=go></div>"},
                      axes="markup")
        self.assertEqual(report["scanned"]["markup"], 2, report["scanned"])

    def test_aria_volume_is_census_only_and_never_a_verdict(self):
        """불변식 핀: ARIA 볼륨은 어느 방향으로도 점수가 아니다(WebAIM: 볼륨↑ ⇒ 오류↑)."""
        report = scan({"W.jsx": '<nav aria-label="main" aria-hidden="false">x</nav>\n'}, axes="markup")
        found = findings_of(report, "MK4_ARIA_VOLUME")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["grade"], "report-only")
        self.assertEqual(report["markup_report_only"]["stats"]["aria_attrs"], 2)

    def test_markup_axis_off_means_no_markup_findings(self):
        report = scan({"W.jsx": '<div onClick={go}>go</div>\n'}, axes="naming,comments")
        self.assertEqual(report["counts"]["by_axis"].get("markup", 0), 0)


class TestLegibilityTests(unittest.TestCase):
    """TL1~TL2 — 테스트 설명 건강도 (report-only · 존재 가점 없음)."""

    def test_vague_title_flagged_but_descriptive_one_is_not(self):
        src = ("it('works', () => {});\n"
               "it('rejects a withdrawal larger than the balance', () => {});\n")
        report = scan({"a.test.js": src}, axes="tests")
        found = findings_of(report, "TL1_VAGUE_TEST_TITLE")
        self.assertEqual([f["symbol"] for f in found], ["works"], found)

    def test_describe_block_single_word_is_not_vague(self):
        """회귀 핀: describe 는 *대상*을 이름 짓는 자리라 한 단어가 관용이다(거짓양성 억제)."""
        report = scan({"a.test.js": "describe('Widget', () => {});\n"}, axes="tests")
        self.assertEqual(findings_of(report, "TL1_VAGUE_TEST_TITLE"), [])
        self.assertEqual(report["tests_report_only"]["stats"].get("describe_blocks"), 1)

    def test_python_test_names(self):
        src = "def test_works():\n    pass\n\ndef test_rejects_expired_token():\n    pass\n"
        report = scan({"test_auth.py": src}, axes="tests")
        found = findings_of(report, "TL1_VAGUE_TEST_TITLE")
        self.assertEqual([f["symbol"] for f in found], ["test_works"], found)

    def test_nonsemantic_selectors_reported_per_file(self):
        report = scan({"a.spec.ts": "getByTestId('x'); getByRole('button');\n"}, axes="tests")
        found = findings_of(report, "TL2_NONSEMANTIC_QUERY")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["extra"]["accessible"], 1)
        self.assertEqual(found[0]["grade"], "report-only")

    def test_non_test_files_are_ignored(self):
        report = scan({"app.js": "it('works', () => {});\n"}, axes="tests")
        self.assertEqual(report["scanned"]["tests"], 0)


class PortedAssetInvariantTests(unittest.TestCase):
    """흡수한 3자산이 이 하네스의 정직성 규약을 깨지 않는지 고정한다."""

    def test_markup_and_tests_axes_produce_no_grade(self):
        report = scan({"W.jsx": '<div onClick={go}>go</div>', "a.test.js": "it('works',()=>{});"},
                      axes="markup,tests")
        blob = json.dumps(report, ensure_ascii=False).lower()
        for banned in ('"score"', '"total_score"', '"level"', '"band"'):
            self.assertNotIn(banned, blob, f"census에 등급성 키 {banned} 가 들어갔다")
        # `grade` 는 오직 탐지기의 *근거 등급* 라벨로만 쓰인다 — 품질 등급이 아니다.
        allowed = {"auto-high", "auto-med", "auto-low", "heuristic", "report-only"}
        markup_and_tests = report["findings"].get("markup", []) + report["findings"].get("tests", [])
        self.assertTrue(markup_and_tests)
        for f in markup_and_tests:
            self.assertIn(f["grade"], allowed)

    def test_report_states_markup_tests_are_census_only(self):
        """markup·tests 축에 개입 클래스가 없다는 문구가 살아 있어야 한다(코드 수정 경로 부재)."""
        report = scan({"a.py": "x = 1\n"}, axes="comments")
        notes = " ".join(report["honesty_notes"])
        self.assertIn("census 전용", notes)
        self.assertIn("Goodhart", notes)

    def test_truncation_is_recorded_not_silent(self):
        """미보고 ≠ 없음 — 파일당 상한에 걸리면 반드시 기록한다."""
        src = "\n".join(f"x{i} = {1000 + i}" for i in range(ls.MAX_FINDINGS_PER_FILE + 5))
        report = scan({"a.py": src}, axes="comments")
        self.assertEqual(len(findings_of(report, "C8_MAGIC_NUMBER")), ls.MAX_FINDINGS_PER_FILE)
        self.assertTrue(any(t["detector"] == "C8_MAGIC_NUMBER"
                            for t in report["counts"]["truncated"]), report["counts"]["truncated"])


class CliTests(unittest.TestCase):
    def test_cli_rejects_unknown_axis(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "legibility_scan.py"), td, "--axes", "bogus"],
                capture_output=True, timeout=60,
            )
        self.assertEqual(proc.returncode, 2)

    def test_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.py").write_text("def get_x():\n    pass\n", encoding="utf-8")
            out = Path(td) / "sub" / "census.json"
            proc = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "legibility_scan.py"), td, "--out", str(out)],
                capture_output=True, timeout=60,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())


if __name__ == "__main__":
    unittest.main(verbosity=2)
