#!/usr/bin/env python3
"""Regression tests for the token-efficiency scorer and detectors (stdlib unittest).

Run:  python3 -m unittest test_efficiency -v
The external skill shipped with NO tests; these pin the invariants the research
grounding depends on so a future edit can't silently regress them.
"""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr

import analyze_sessions as A
import build_dashboard as B
import detect_patterns as D


def _session_file(dirpath, name, records):
    p = os.path.join(dirpath, name)
    with open(p, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return p


def _assistant(model="claude-opus-4-8", inp=0, out=0, cw5=0, cw1h=0, cr=0, tool_uses=None,
               sidechain=False, mid=None):
    usage = {"input_tokens": inp, "output_tokens": out, "cache_read_input_tokens": cr,
             "cache_creation": {"ephemeral_5m_input_tokens": cw5, "ephemeral_1h_input_tokens": cw1h}}
    content = []
    for tu in (tool_uses or []):
        content.append({"type": "tool_use", "id": tu["id"], "name": tu["name"],
                        "input": tu.get("input", {})})
    message = {"model": model, "usage": usage, "content": content}
    if mid:
        message["id"] = mid
    rec = {"type": "assistant", "message": message}
    if sidechain:
        rec["isSidechain"] = True
    return rec


def _split_message(mid, model="claude-opus-4-8", inp=10_000, cr=20_000, out=300, tool_uses=None):
    """The real CLI splits one API message (one message.id, one usage) into
    thinking/text/tool_use records that REPEAT the same usage. Returns 3 records."""
    return [
        _assistant(model=model, inp=inp, cr=cr, out=out, mid=mid),                    # thinking
        _assistant(model=model, inp=inp, cr=cr, out=out, mid=mid),                    # text
        _assistant(model=model, inp=inp, cr=cr, out=out, mid=mid, tool_uses=tool_uses),  # tool_use
    ]


def _hi_ctx(inp=120_000, **kw):
    """Assistant turn with context > 100k (bloat territory)."""
    return _assistant(inp=inp, out=100, **kw)


def _tool_result(tu_id, chars):
    return {"type": "user", "message": {"content": [
        {"type": "tool_result", "tool_use_id": tu_id, "content": "x" * chars}]}}


class TestWeights(unittest.TestCase):
    def test_default_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(A.DEFAULT_WEIGHTS.values()), 1.0, places=9)

    def test_parse_weights_renormalizes(self):
        w = A.parse_weights("cache=1,redundancy=1,density=1,tool=1")
        self.assertAlmostEqual(sum(w.values()), 1.0, places=9)
        for v in w.values():
            self.assertAlmostEqual(v, 0.25, places=9)

    def test_every_axis_has_evidence_grade(self):
        for axis in A.DEFAULT_WEIGHTS:
            self.assertIn(axis, A.WEIGHT_EVIDENCE)


class TestPricing(unittest.TestCase):
    def test_opus_is_current_price_not_retired(self):
        # The external skill hardcoded the retired $15/$75; current Opus is $5/$25.
        self.assertEqual(A.PRICING["claude-opus-4-8"]["in"], 5.0)
        self.assertEqual(A.PRICING["claude-opus-4-8"]["out"], 25.0)

    def test_cache_multipliers_derived_from_input(self):
        for model, row in A.PRICING.items():
            if row["in"] == 0:
                continue
            self.assertAlmostEqual(row["cr"], row["in"] * 0.1, places=6)
            self.assertAlmostEqual(row["cw5"], row["in"] * 1.25, places=6)
            self.assertAlmostEqual(row["cw1h"], row["in"] * 2.0, places=6)

    def test_fable5_is_top_tier(self):
        self.assertEqual(A.PRICING["claude-fable-5"]["in"], 10.0)

    def test_pricing_tables_in_sync_across_scripts(self):
        # BIDIRECTIONAL: same model set AND same input price. A one-way check would
        # pass when a new model is added to analyze_sessions but forgotten in
        # detect_patterns — the most likely regression direction.
        self.assertEqual(set(D.INPUT_PRICE), set(A.PRICING),
                         "model sets diverged between analyze_sessions and detect_patterns")
        for model in A.PRICING:
            self.assertEqual(D.INPUT_PRICE[model], A.PRICING[model]["in"],
                             f"{model} input price out of sync between scripts")


class TestAnalyze(unittest.TestCase):
    def test_cost_and_cache_ratio(self):
        with tempfile.TemporaryDirectory() as d:
            # 1M cache-read + 1M input on Opus 4.8 → 1M*0.5 + 1M*5.0 per 1e6 = $5.50
            p = _session_file(d, "s.jsonl", [
                _assistant(inp=1_000_000, cr=1_000_000, out=0)])
            s = A.analyze_session(p, A.PRICING)
            self.assertAlmostEqual(s["cost_usd"], 5.50, places=4)
            self.assertAlmostEqual(s["cache_hit_ratio"], 0.5, places=6)

    def test_redundant_reads_counted(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(out=100, tool_uses=[
                    {"id": "a", "name": "Read", "input": {"file_path": "/x.py"}},
                    {"id": "b", "name": "Read", "input": {"file_path": "/x.py"}},
                    {"id": "c", "name": "Read", "input": {"file_path": "/x.py"}}])])
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["redundant_reads"], 2)  # 3 reads of same file → 2 redundant

    def test_sidechain_counted(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(out=10),
                _assistant(out=10, sidechain=True)])
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["num_sidechain_msgs"], 1)

    def test_dominant_model_ignores_sidechain(self):
        # One Opus main-thread turn + one Haiku SIDECHAIN turn: dominance is a
        # main-thread property (drives routing), so Opus must win — not the
        # alphabetical tie-break the naive count would produce.
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(model="claude-opus-4-8", inp=1000, out=10),
                _assistant(model="claude-haiku-4-5", inp=100, out=10, sidechain=True)])
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["dominant_model"], "claude-opus-4-8")
            self.assertEqual(s["dominant_input_price"], 5.0)

    def test_score_golden_value(self):
        # Golden pin (hand-derived): inp=50k, cr=200k, out=2k, no tools.
        # cache = min(100, 0.8/0.85*100) = 94.1176; density(od=0.008) = 68;
        # redundancy = 100; tool(tpk=0) = 70.
        # composite = 94.1176*.35 + 68*.15 + 100*.30 + 70*.20 = 87.1412 -> 87.1 (A)
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "a.jsonl", [_assistant(inp=50_000, cr=200_000, out=2000)])
            sc = A.score_session(A.analyze_session(p, A.PRICING), A.DEFAULT_WEIGHTS)
            self.assertEqual(sc["composite"], 87.1)
            self.assertEqual(sc["grade"], "A")

    def test_cost_components_sum_to_total(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "a.jsonl", [
                _assistant(inp=100_000, cr=300_000, cw5=50_000, cw1h=20_000, out=5000),
                _assistant(model="claude-haiku-4-5", inp=10_000, out=1000)])
            s = A.analyze_session(p, A.PRICING)
            comp = (s["cost_input_usd"] + s["cost_output_usd"]
                    + s["cost_cache_write_usd"] + s["cost_cache_read_usd"])
            self.assertAlmostEqual(comp, s["cost_usd"], places=9)

    def test_null_usage_record_survives_both_scripts(self):
        # Valid JSON with "usage": null / "message": null must be skipped
        # gracefully by BOTH scripts (R2 found detect crashed the whole run).
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(inp=40_000, cr=10_000, out=500),
                {"type": "assistant", "message": {"usage": None}},
                {"type": "assistant", "message": None},
                {"type": "user", "message": None},
            ])
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["input_tokens"], 40_000)
            r = D.analyze_session(p)
            self.assertIsNotNone(r)
            # empty (zero-context, zero-output) records are skipped from the
            # trajectory, not counted as turns — only the valid one survives.
            self.assertEqual(r["n_turns"], 1)

    def test_truncated_last_line_keeps_session(self):
        # Live-appended files often end in a half-written record — that record is
        # skipped, the rest of the session survives (in BOTH scripts).
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [_assistant(inp=40_000, cr=10_000, out=500)])
            with open(p, "a") as f:
                f.write('{"type": "assistant", "message": {"usage": {"inp')  # truncated
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["input_tokens"], 40_000)
            r = D.analyze_session(p)
            self.assertIsNotNone(r)
            self.assertEqual(r["n_turns"], 1)

    def test_encode_repo_path_nonalnum(self):
        # Claude Code encodes '.', '_' AND '/' as '-' (verified on real dirs).
        for enc in (A.encode_repo_path, D.encode_repo_path):
            self.assertTrue(enc("/Users/x.y_z/my repo").endswith("-Users-x-y-z-my-repo"))


class TestDetectors(unittest.TestCase):
    def test_giant_tool_output_fix_forbids_blind_truncation(self):
        # The corrected guidance must NOT recommend head/tail truncation of an existing result.
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(out=10, tool_uses=[{"id": "g", "name": "Bash"}]),
                _tool_result("g", 60_000),
                _assistant(out=10),
                _assistant(out=10)])
            r = D.analyze_session(p)
            f = r["findings"]["giant_tool_outputs"]
            self.assertIn("blind-truncate", f["fix"].lower())
            self.assertIn("Squeez", f["research"])

    def test_duplicate_tools_detected(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(out=10, tool_uses=[{"id": "a", "name": "Bash", "input": {"command": "git status"}}]),
                _assistant(out=10, tool_uses=[{"id": "b", "name": "Bash", "input": {"command": "git status"}}])])
            r = D.analyze_session(p)
            self.assertIn("duplicate_tools", r["findings"])
            self.assertEqual(r["findings"]["duplicate_tools"]["duplicate_count"], 1)

    def test_read_exploration_heavy(self):
        with tempfile.TemporaryDirectory() as d:
            reads = [{"id": f"r{i}", "name": "Read", "input": {"file_path": "/same.py"}} for i in range(5)]
            p = _session_file(d, "s.jsonl", [_assistant(out=100, tool_uses=reads)])
            r = D.analyze_session(p)
            self.assertIn("read_exploration_heavy", r["findings"])
            self.assertGreater(r["findings"]["read_exploration_heavy"]["redundant_reads"], 0)

    def test_waste_priced_at_session_model(self):
        # Same duplicate on Haiku (input $1) must cost less than on Opus (input $5).
        # 40k-char results keep the comparison away from round(…, 2) boundaries.
        with tempfile.TemporaryDirectory() as d:
            def dup(model):
                p = _session_file(d, f"{model}.jsonl", [
                    _assistant(model=model, out=10, tool_uses=[{"id": "a", "name": "Bash", "input": {"command": "x"}}]),
                    _tool_result("a", 40_000),
                    _assistant(model=model, out=10, tool_uses=[{"id": "b", "name": "Bash", "input": {"command": "x"}}]),
                    _tool_result("b", 40_000)])
                return D.analyze_session(p)["findings"]["duplicate_tools"]["waste_usd"]
            self.assertLess(dup("claude-haiku-4-5"), dup("claude-opus-4-8"))

    def test_new_detectors_registered(self):
        for key in ("stale_observation", "cache_invalidation_churn", "read_exploration_heavy"):
            self.assertIn(key, D.PATTERN_KEYS)

    def test_sidechain_does_not_break_bloat_run(self):
        # 25 main-thread turns >100k with low-context SIDECHAIN records interleaved:
        # sidechains run in a separate context, so they must neither reset the
        # consecutive-run detector nor inflate n_turns.
        with tempfile.TemporaryDirectory() as d:
            recs = []
            for _ in range(25):
                recs.append(_hi_ctx())
                recs.append(_assistant(inp=3_000, out=50, sidechain=True))
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertEqual(r["n_turns"], 25)
            self.assertEqual(r["sidechain_msgs_excluded"], 25)
            self.assertIn("context_bloat", r["findings"])

    def test_poor_cache_detects_zero_cache_turn(self):
        # cr=cw=0 with huge uncached input at high context is the WORST cache case;
        # the external skill's cr+cw==0 guard skipped exactly this.
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [_assistant(inp=200_000, out=100)])
            r = D.analyze_session(p)
            self.assertIn("poor_cache_util", r["findings"])
            self.assertEqual(r["findings"]["poor_cache_util"]["bad_turns_count"], 1)

    def test_carried_turns_cut_at_compact(self):
        # A giant output followed 2 turns later by a >50% context drop (compact)
        # must be billed only up to the drop, not for every remaining turn.
        with tempfile.TemporaryDirectory() as d:
            recs = [
                _assistant(inp=120_000, out=10, tool_uses=[{"id": "g", "name": "Bash"}]),
                _tool_result("g", 60_000),
                _assistant(inp=120_000, out=10),
                _assistant(inp=20_000, out=10),   # 120k -> 20k: compact-like drop
                _assistant(inp=25_000, out=10),
                _assistant(inp=30_000, out=10),
            ]
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            g = r["findings"]["giant_tool_outputs"]["samples"][0]
            self.assertEqual(g["remaining_turns"], 1)  # only the turn before the drop


class TestMessageIdDedup(unittest.TestCase):
    """The CLI records one API message as 3 split records with repeated usage —
    count usage ONCE per message.id (else cost/turns 2-3x inflated)."""

    def test_analyze_counts_usage_once_per_message_id(self):
        with tempfile.TemporaryDirectory() as d:
            # one logical message split into 3 records
            recs = _split_message("msg_1", inp=10_000, cr=20_000, out=300)
            p = _session_file(d, "s.jsonl", recs)
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["input_tokens"], 10_000)   # not 30_000
            self.assertEqual(s["cache_read"], 20_000)      # not 60_000
            self.assertEqual(s["output_tokens"], 300)      # not 900

    def test_analyze_tool_use_collected_across_split_records(self):
        with tempfile.TemporaryDirectory() as d:
            recs = _split_message("msg_1", tool_uses=[{"id": "a", "name": "Read",
                                                       "input": {"file_path": "/x.py"}}])
            p = _session_file(d, "s.jsonl", recs)
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["num_tool_calls"], 1)  # the tool_use in the 3rd record, once

    def test_detect_merges_split_records_into_one_turn(self):
        with tempfile.TemporaryDirectory() as d:
            recs = _split_message("msg_1", inp=110_000, tool_uses=[{"id": "a", "name": "Bash"}])
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertEqual(r["n_turns"], 1)   # 3 records → 1 logical turn

    def test_no_message_id_each_record_is_own_turn(self):
        # old logs / fixtures without message.id keep the old 1-record-1-turn behavior
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(inp=110_000, out=10), _assistant(inp=110_000, out=10)])
            r = D.analyze_session(p)
            self.assertEqual(r["n_turns"], 2)


class TestSubagentFiles(unittest.TestCase):
    """Current CLI stores subagents in <sid>/subagents/**/*.jsonl — their cost must
    be summed, but they must NOT feed main-thread redundancy/dominance."""

    def _make(self, d):
        sid = "abc"
        _session_file(d, sid + ".jsonl", [
            _assistant(model="claude-fable-5", inp=50_000, out=1000, mid="m1")])
        subdir = os.path.join(d, sid, "subagents")
        os.makedirs(subdir)
        _session_file(subdir, "agent-1.jsonl", [
            {**_assistant(model="claude-haiku-4-5", inp=20_000, out=500, mid="s1"),
             "isSidechain": True}])
        return os.path.join(d, sid + ".jsonl")

    def test_subagent_tokens_stay_out_of_main_totals(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._make(d)
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["num_subagent_files"], 1)
            self.assertGreater(s["num_sidechain_msgs"], 0)
            # main-thread token totals exclude the subagent (else scoring is polluted)
            self.assertEqual(s["input_tokens"], 50_000)   # main (fable) only
            self.assertGreater(s["subagent_cost_usd"], 0)  # subagent spend reported separately

    def test_subagent_does_not_tip_dominance(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._make(d)
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["dominant_model"], "claude-fable-5")  # main thread, not haiku

    def test_cost_is_main_only_subagent_separate(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._make(d)
            s = A.analyze_session(p, A.PRICING)
            # cost_usd is the main interactive session; subagent spend is its own number.
            # single main model → dominant cost == cost_usd; subagent cost is nonzero.
            self.assertAlmostEqual(s["dominant_model_cost_usd"], s["cost_usd"], places=9)
            self.assertGreater(s["subagent_cost_usd"], 0)


class TestZeroUsageSkip(unittest.TestCase):
    def test_synthetic_and_empty_skipped_from_trajectory(self):
        with tempfile.TemporaryDirectory() as d:
            recs = [_hi_ctx() for _ in range(25)]
            recs.insert(12, _assistant(model="<synthetic>", inp=0, out=0))
            recs.insert(6, {"type": "assistant", "message": {"usage": None}})
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertEqual(r["n_turns"], 25)          # skips synthetic + empty
            self.assertIn("context_bloat", r["findings"])  # run not broken by the inserts


class TestDuplicateStateful(unittest.TestCase):
    def test_same_input_different_result_not_waste(self):
        # git status dirty -> commit -> git status clean: same input, changed result
        with tempfile.TemporaryDirectory() as d:
            recs = [
                _assistant(out=10, tool_uses=[{"id": "a", "name": "Bash", "input": {"command": "git status"}}]),
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "a", "content": "dirty"}]}},
                _assistant(out=10, tool_uses=[{"id": "b", "name": "Bash", "input": {"command": "git status"}}]),
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "b", "content": "clean"}]}},
            ]
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertNotIn("duplicate_tools", r["findings"])  # changed result → not a dup

    def test_same_input_same_result_is_waste(self):
        with tempfile.TemporaryDirectory() as d:
            recs = [
                _assistant(out=10, tool_uses=[{"id": "a", "name": "Bash", "input": {"command": "ls"}}]),
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "a", "content": "same"}]}},
                _assistant(out=10, tool_uses=[{"id": "b", "name": "Bash", "input": {"command": "ls"}}]),
                {"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": "b", "content": "same"}]}},
            ]
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertIn("duplicate_tools", r["findings"])
            self.assertEqual(r["findings"]["duplicate_tools"]["duplicate_count"], 1)


class TestUntriggeredDetectors(unittest.TestCase):
    def test_subagent_overuse_triggered(self):
        with tempfile.TemporaryDirectory() as d:
            recs = []
            for i in range(6):
                recs.append(_assistant(out=10, tool_uses=[{"id": f"t{i}", "name": "Task"}]))
                recs.append({"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 100}]}})
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertIn("subagent_overuse", r["findings"])
            self.assertEqual(r["findings"]["subagent_overuse"]["agent_calls"], 6)

    def test_cache_churn_triggered(self):
        with tempfile.TemporaryDirectory() as d:
            # 12 high-context turns each re-writing >30% of input to cache
            recs = [_assistant(inp=20_000, cr=20_000, cw5=40_000, out=50) for _ in range(12)]
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertIn("cache_invalidation_churn", r["findings"])

    def test_cache_churn_below_min_turns_not_triggered(self):
        with tempfile.TemporaryDirectory() as d:
            recs = [_assistant(inp=20_000, cr=20_000, cw5=40_000, out=50) for _ in range(9)]
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertNotIn("cache_invalidation_churn", r["findings"])

    def test_stale_observation_triggered(self):
        with tempfile.TemporaryDirectory() as d:
            recs = [_assistant(inp=40_000, out=10, tool_uses=[{"id": "g", "name": "Bash"}])]
            recs.append({"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "g", "content": "x" * 30_000}]}})  # mid-sized
            recs += [_assistant(inp=40_000, out=10) for _ in range(12)]  # carried 12 turns
            p = _session_file(d, "s.jsonl", recs)
            r = D.analyze_session(p)
            self.assertIn("stale_observation", r["findings"])

    def test_all_eight_detectors_are_in_loop_and_keys(self):
        # PATTERN_KEYS and the detector dispatch list must stay in sync (the
        # membership test alone is near-tautological — this pins the loop too).
        import inspect
        src = inspect.getsource(D.analyze_session)
        for key in D.PATTERN_KEYS:
            self.assertIn(f'"{key}"', src, f"{key} not dispatched in analyze_session loop")


class TestDashboard(unittest.TestCase):
    def _totals(self, **over):
        t = {"sessions_dir": "/x", "cache_hit_ratio": 0.6, "cost_usd": 10.0,
             "cost_input_usd": 4.0, "cost_output_usd": 3.0, "cost_cache_write_usd": 2.0,
             "cost_cache_read_usd": 1.0, "input_tokens": 1_000_000, "output_tokens": 100_000,
             "total_input_tokens": 2_000_000, "num_tool_calls": 5,
             "cache_create_1h": 0, "cache_create_5m": 0, "cache_read": 500_000,
             "redundant_reads": 0, "image_count": 0,
             "weights": {"cache": 0.35, "redundancy": 0.30, "density": 0.15, "tool": 0.20},
             "weight_evidence": {"cache": "x", "redundancy": "x", "density": "x", "tool": "x"}}
        t.update(over)
        return t

    def _session(self, **over):
        s = {"session_id": "abc12345", "cost_usd": 10.0, "num_tool_calls": 5,
             "total_input_tokens": 1_000_000, "output_tokens": 100_000, "output_ratio": 0.1,
             "cache_hit_ratio": 0.6, "cache_read": 500_000, "redundant_reads": 0,
             "image_count": 0, "had_image": False,
             "dominant_input_price": 5.0, "dominant_model_cost_usd": 10.0,
             "scores": {"cache_score": 70, "density_score": 60, "redundancy_score": 100,
                        "tool_score": 80, "composite": 74.0, "grade": "B"}}
        s.update(over)
        return s

    def test_component_bars_sum_to_kpi(self):
        # components 4(in)+3(out)+2(write)+1(read) = 10 = cost_usd KPI; the bars
        # render the analyze component values (rounded), so their sum must equal cost.
        t = self._totals()
        comp_sum = (t["cost_input_usd"] + t["cost_output_usd"]
                    + t["cost_cache_write_usd"] + t["cost_cache_read_usd"])
        self.assertAlmostEqual(comp_sum, t["cost_usd"], places=6)
        html = B.build_html({"totals": t, "sessions": [self._session()]}, None, "x")
        self.assertIn("$10.00", html)                       # cost KPI
        self.assertIn('fill="#e6edf3">4</text>', html)       # input-cost bar (=4)

    def test_escapes_hostile_session_id(self):
        s = self._session(session_id="<script>evil</script>")
        html = B.build_html({"totals": self._totals(), "sessions": [s]}, None, "x")
        self.assertNotIn("<script>evil", html)
        self.assertIn("&lt;script&gt;", html)

    def test_effective_input_price_fallback_no_zerodiv(self):
        self.assertEqual(B.effective_input_price({"input_tokens": 0}), B.FALLBACK_IN)

    def test_looks_downgradeable_boundaries(self):
        self.assertTrue(B.looks_downgradeable(self._session(output_tokens=1000, num_tool_calls=5, output_ratio=0.001)))
        self.assertFalse(B.looks_downgradeable(self._session(dominant_input_price=1.0)))   # haiku
        self.assertFalse(B.looks_downgradeable(self._session(dominant_input_price=3.0)))   # sonnet (boundary excluded)
        self.assertFalse(B.looks_downgradeable(self._session(had_image=True)))

    def test_routing_uses_dominant_model_cost(self):
        # dominant fable ($10) session with $10 total but only $4 dominant cost →
        # save = 4 * (1 - 3/10) = 2.8, NOT 10 * 0.7 = 7.0
        s = self._session(dominant_input_price=10.0, dominant_model_cost_usd=4.0,
                          cost_usd=10.0, output_tokens=1000, output_ratio=0.001)
        sav, n = B.compute_savings(self._totals(), [s])
        self.assertAlmostEqual(sav["model_routing"], 2.8, places=6)

    def test_svg_bars_all_zero_no_error(self):
        self.assertEqual(B.svg_bars([]), "")
        B.svg_bars([("a", 0), ("b", 0)])  # must not raise


class TestCLIErrorPaths(unittest.TestCase):
    def test_parse_weights_zero_sum_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                A.parse_weights("cache=0,redundancy=0,density=0,tool=0")

    def test_parse_weights_non_numeric_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                A.parse_weights("cache=abc")

    def test_parse_weights_unknown_axis_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                A.parse_weights("cachee=1")

    def test_pricing_override_syncs_both_scripts(self):
        # load_input_prices mutates the D.INPUT_PRICE module global — save/restore
        # so this test doesn't pollute the sync test.
        saved = dict(D.INPUT_PRICE)
        try:
            with tempfile.TemporaryDirectory() as d:
                pf = os.path.join(d, "pricing.json")
                with open(pf, "w") as f:
                    json.dump({"claude-new-x": {"in": 20.0, "out": 100.0}}, f)
                table = A.load_pricing(pf)
                self.assertEqual(table["claude-new-x"]["in"], 20.0)
                D.load_input_prices(pf)
                self.assertEqual(D.INPUT_PRICE["claude-new-x"], 20.0)
        finally:
            D.INPUT_PRICE.clear()
            D.INPUT_PRICE.update(saved)

    def test_pricing_missing_out_rejected_both(self):
        saved = dict(D.INPUT_PRICE)
        try:
            with tempfile.TemporaryDirectory() as d:
                pf = os.path.join(d, "p.json")
                with open(pf, "w") as f:
                    json.dump({"m": {"in": 1.0}}, f)  # missing "out"
                for fn in (A.load_pricing, D.load_input_prices):
                    with self.assertRaises(SystemExit):
                        with redirect_stderr(io.StringIO()):
                            fn(pf)
        finally:
            D.INPUT_PRICE.clear()
            D.INPUT_PRICE.update(saved)


class TestScoreCurve(unittest.TestCase):
    def _density_at(self, output_ratio):
        s = {"cache_hit_ratio": 0.85, "output_ratio": output_ratio, "total_file_reads": 0,
             "redundant_reads": 0, "num_tool_calls": 0, "output_tokens": 1000}
        return A.score_session(s, A.DEFAULT_WEIGHTS)["density_score"]

    def _tool_at(self, tool_calls, output_tokens=1000):
        s = {"cache_hit_ratio": 0.85, "output_ratio": 0.02, "total_file_reads": 0,
             "redundant_reads": 0, "num_tool_calls": tool_calls, "output_tokens": output_tokens}
        return A.score_session(s, A.DEFAULT_WEIGHTS)["tool_score"]

    def test_density_curve_continuous_at_boundaries(self):
        eps = 1e-6
        for knot in (0.005, 0.02, 0.05):
            lo = self._density_at(knot - eps)
            hi = self._density_at(knot + eps)
            self.assertAlmostEqual(lo, hi, places=2, msg=f"density discontinuous at {knot}")

    def test_tool_curve_continuous_at_boundaries(self):
        # tpk knots at 2/10/20 tool-calls per 1k output (output_tokens=1000)
        eps = 1e-4
        for knot in (2, 10, 20):
            lo = self._tool_at(knot - eps)
            hi = self._tool_at(knot + eps)
            self.assertAlmostEqual(lo, hi, places=1, msg=f"tool discontinuous at tpk={knot}")

    def test_legacy_cache_creation_total_falls_back_to_5m(self):
        with tempfile.TemporaryDirectory() as d:
            rec = {"type": "assistant", "message": {"model": "claude-opus-4-8", "content": [],
                   "usage": {"input_tokens": 1000, "output_tokens": 10,
                             "cache_creation_input_tokens": 40_000}}}
            p = _session_file(d, "s.jsonl", [rec])
            s = A.analyze_session(p, A.PRICING)
            self.assertEqual(s["cache_create_5m"], 40_000)
            self.assertEqual(s["cache_create_1h"], 0)


class TestDatedModelPricing(unittest.TestCase):
    def test_dated_suffix_normalized_both_scripts(self):
        # claude-haiku-4-5-20251001 must price as Haiku, not the Opus-tier default.
        self.assertEqual(A.price_for("claude-haiku-4-5-20251001", A.PRICING)["in"], 1.0)
        self.assertEqual(A.normalize_model("claude-haiku-4-5-20251001"), "claude-haiku-4-5")
        self.assertEqual(D.input_price_for("claude-haiku-4-5-20251001"), 1.0)

    def test_unknown_still_opus_default(self):
        self.assertEqual(A.price_for("totally-unknown", A.PRICING)["in"], 5.0)


class TestScoreMainThreadOnly(unittest.TestCase):
    """score axes must all be main-thread (subagent volume must not move the score)."""

    def test_subagent_cache_does_not_inflate_cache_score(self):
        with tempfile.TemporaryDirectory() as d:
            sid = "z"
            # main thread: cache_read 0 → cache_score should be 0
            _session_file(d, sid + ".jsonl", [
                _assistant(model="claude-opus-4-8", inp=100_000, cr=0, out=1000, mid="m1")])
            subdir = os.path.join(d, sid, "subagents")
            os.makedirs(subdir)
            _session_file(subdir, "a.jsonl", [
                {**_assistant(model="claude-opus-4-8", inp=10_000, cr=900_000, out=100, mid="s1"),
                 "isSidechain": True}])
            s = A.analyze_session(os.path.join(d, sid + ".jsonl"), A.PRICING)
            sc = A.score_session(s, A.DEFAULT_WEIGHTS)
            self.assertEqual(s["cache_read"], 0)        # main only
            self.assertEqual(sc["cache_score"], 0.0)     # not inflated by subagent 900k


class TestDetectCorruptRecord(unittest.TestCase):
    def test_non_string_id_survives(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(inp=110_000, out=10),
                {"type": "assistant", "message": {"model": "x", "usage": {"input_tokens": 5},
                                                  "id": ["not", "hashable"], "content": []}},
                _assistant(inp=110_000, out=10)])
            r = D.analyze_session(p)          # must not raise / return None
            self.assertIsNotNone(r)
            self.assertGreaterEqual(r["n_turns"], 2)

    def test_non_dict_message_survives(self):
        with tempfile.TemporaryDirectory() as d:
            p = _session_file(d, "s.jsonl", [
                _assistant(inp=110_000, out=10),
                {"type": "assistant", "message": "garbled string"},
                _assistant(inp=110_000, out=10)])
            r = D.analyze_session(p)
            self.assertIsNotNone(r)


class TestCarriedTurnsBoundary(unittest.TestCase):
    def test_no_drop_charges_all_remaining(self):
        turns = [{"context_size": 100_000} for _ in range(5)]
        self.assertEqual(D.carried_turns(turns, 0, 5), 4)  # no drop → all remaining

    def test_observation_at_last_turn(self):
        turns = [{"context_size": 100_000} for _ in range(5)]
        self.assertEqual(D.carried_turns(turns, 4, 5), 0)  # nothing after it


if __name__ == "__main__":
    unittest.main()
