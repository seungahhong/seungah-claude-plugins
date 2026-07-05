#!/usr/bin/env python3
"""Analyze Claude Code session JSONL files for token/context efficiency.

v2 — research-grounded evolution of the external `improve-token-efficiency` skill.
See references/research/ for the 2025~2026 evidence behind every threshold and weight.

Usage:
  python3 analyze_sessions.py --repo /path/to/repo [--out /tmp/session_analysis.json]
  python3 analyze_sessions.py --sessions-dir ~/.claude/projects/-Users-x-Projects-Foo
  python3 analyze_sessions.py --pricing ./pricing.json   # override the built-in table

The script finds the encoded session directory under ~/.claude/projects/, parses every
.jsonl file, extracts per-session token usage from each assistant message's `usage`
field, applies per-model pricing, and computes a weighted efficiency score.

WHAT CHANGED vs the external skill (all changes carry an evidence tag; see research/):
  - PRICING refreshed to the current Claude line ($5/$25 Opus, $10/$50 Fable 5, …).
    The external skill hardcoded the retired $15/$75 Opus rate, overstating cost ~3x.
  - Cache multipliers derived from the base input rate (read 0.1x / write-5m 1.25x /
    write-1h 2x) per Anthropic's published caching economics — session-2.
  - Scoring weights are configurable and every axis carries an evidence GRADE
    (CONFIRMED / PLAUSIBLE / HEURISTIC). "read-redundancy" weight is justified by the
    76.1%-of-tokens-are-reads finding (arXiv:2606.14066) — session-3.
  - Honesty: the composite is an EFFICIENCY proxy, not cost-of-pass. A session that
    burned few tokens but FAILED its task is not "good" — we cannot observe task
    success from logs, so we never claim it. Cost-of-Pass (arXiv:2508.02694) — session-5.
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Pricing (USD per 1M tokens). Keys match the exact model string the CLI records
# in `message.model`. cw5 = cache write 5m, cw1h = cache write 1h, cr = cache read.
#
# Cache multipliers are fixed relative to the base input rate and are the same for
# every model: read = 0.1x input, write-5m = 1.25x input, write-1h = 2.0x input.
# (Anthropic prompt-caching economics — session-2.) Verified 2026-07 against the
# claude-api skill. When a new model ships, add ONE row: {"in", "out"} and the
# helper fills in cw5/cw1h/cr. Override the whole table with --pricing <file.json>.
# ---------------------------------------------------------------------------
def _row(inp, out):
    return {"in": inp, "out": out, "cw5": inp * 1.25, "cw1h": inp * 2.0, "cr": inp * 0.1}

PRICING = {
    # Current line (2026-07)
    "claude-fable-5":     _row(10.00, 50.00),
    "claude-mythos-5":    _row(10.00, 50.00),
    "claude-opus-4-8":    _row(5.00, 25.00),
    "claude-opus-4-7":    _row(5.00, 25.00),
    "claude-opus-4-6":    _row(5.00, 25.00),
    "claude-sonnet-5":    _row(3.00, 15.00),   # intro $2/$10 through 2026-08-31; using list price
    "claude-sonnet-4-6":  _row(3.00, 15.00),
    "claude-haiku-4-5":   _row(1.00, 5.00),
    # Legacy (still resolvable in old sessions)
    "claude-opus-4-5":    _row(5.00, 25.00),
    "claude-sonnet-4-5":  _row(3.00, 15.00),
    "<synthetic>":        _row(0.0, 0.0),
}
# Unknown models default to Opus-tier. NOTE: not strictly "conservative" — an unknown
# model above Opus (e.g. a future Fable successor at $10+) would be UNDER-estimated.
# Register new models via --pricing rather than trusting this default.
# claude-mythos-5 / legacy opus-4-5 / sonnet-4-5 rows are NOT in references/research/
# session-2's verified table — they come straight from the Anthropic claude-api skill
# (same 1st-party source, checked 2026-07); mythos-5 shares Fable 5 pricing.
DEFAULT_PRICE = PRICING["claude-opus-4-8"]

# ---------------------------------------------------------------------------
# Scoring weights and their evidence grade. Sum must be 1.0 (asserted in tests).
# Override with --weights cache=0.35,density=0.15,redundancy=0.30,tool=0.20
#
#   cache      CONFIRMED  cache_read / total_input. Cache economics are first-party
#              (0.1x vs 1.0x). Low reuse pays full input every turn — session-2.
#   redundancy PLAUSIBLE  Read ops dominate coding-agent token spend (76.1%,
#              arXiv:2606.14066), so re-reads are the highest-leverage waste —
#              this axis is weighted at near-parity with cache (0.30 vs 0.35) — session-3.
#   density    HEURISTIC  output/input sweet-spot ~2%. Directional only; no primary
#              source ties a specific ratio to task success. Kept low-weight.
#   tool       HEURISTIC  tool calls per 1k output. Thrash proxy; no calibrated source.
# ---------------------------------------------------------------------------
DEFAULT_WEIGHTS = {"cache": 0.35, "redundancy": 0.30, "density": 0.15, "tool": 0.20}
WEIGHT_EVIDENCE = {
    "cache": "CONFIRMED (session-2: cache read 0.1x vs input 1.0x)",
    "redundancy": "PLAUSIBLE (session-3: reads=76.1% of coding-agent tokens, arXiv:2606.14066)",
    "density": "HEURISTIC (no primary source ties output-ratio to success)",
    "tool": "HEURISTIC (thrash proxy, uncalibrated)",
}


def encode_repo_path(repo_path):
    """Turn /Users/x/Projects/foo.bar_baz into -Users-x-Projects-foo-bar-baz.

    Claude Code encodes EVERY non-alphanumeric character as '-', not just '/'
    (verified against real ~/.claude/projects entries: 'seungah.hong' →
    'seungah-hong', 'hyperframe_ai' → 'hyperframe-ai'). The external skill only
    replaced '/' and silently failed on any path containing '.' or '_'."""
    abs_path = os.path.abspath(os.path.expanduser(repo_path))
    return re.sub(r"[^A-Za-z0-9]", "-", abs_path)


def resolve_sessions_dir(args):
    if args.sessions_dir:
        return os.path.expanduser(args.sessions_dir)
    repo = args.repo or os.getcwd()
    return os.path.expanduser(f"~/.claude/projects/{encode_repo_path(repo)}")


def load_pricing(path):
    """Merge a user pricing file over the built-in table. Rows may give {in,out}
    (cache fields auto-derived) or the full {in,out,cw5,cw1h,cr}."""
    with open(path) as f:
        user = json.load(f)
    table = dict(PRICING)
    for model, row in user.items():
        if not isinstance(row, dict) or "in" not in row or "out" not in row:
            print(f"[error] --pricing row for '{model}' must have at least "
                  f"{{\"in\": <usd/1M>, \"out\": <usd/1M>}}", file=sys.stderr)
            sys.exit(2)
        if "cw5" in row:
            table[model] = row
        else:
            table[model] = _row(row["in"], row["out"])
    return table


def normalize_model(model):
    """Strip a trailing dated snapshot suffix so `claude-haiku-4-5-20251001`
    matches the bare `claude-haiku-4-5` pricing key. Subagent records use the
    dated form; without this they'd fall to the Opus-tier default (Haiku → 5x)."""
    return re.sub(r"-\d{8}$", "", model or "")


def price_for(model, table):
    if model in table:
        return table[model]
    norm = normalize_model(model)
    if norm in table:
        return table[norm]
    if model and model not in price_for._warned:
        print(f"[warn] unknown model: {model}, applying Opus-tier default pricing", file=sys.stderr)
        price_for._warned.add(model)
    return table.get("claude-opus-4-8", DEFAULT_PRICE)
price_for._warned = set()


def session_files(main_path):
    """Yield (path, is_subagent) for a session. The current CLI stores subagent
    trajectories NOT inline (isSidechain) but in separate files under
    <session-id>/subagents/**/*.jsonl — those are real spend and must be summed
    for cost, so we collect them (flagged so redundancy/dominance stay main-only)."""
    yield main_path, False
    sid = os.path.basename(main_path).replace(".jsonl", "")
    subdir = os.path.join(os.path.dirname(main_path), sid, "subagents")
    if os.path.isdir(subdir):
        for root, _dirs, files in os.walk(subdir):
            for fn in sorted(files):
                if fn.endswith(".jsonl"):
                    yield os.path.join(root, fn), True


def analyze_session(path, table):
    stats = {
        "session_id": os.path.basename(path).replace(".jsonl", ""),
        "file_size": os.path.getsize(path),
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_create_5m": 0,
        "cache_create_1h": 0,
        "cache_read": 0,
        "num_assistant_msgs": 0,
        "num_user_msgs": 0,
        "num_tool_calls": 0,
        "num_sidechain_msgs": 0,   # subagent-file + inline-isSidechain assistant msgs
        "num_subagent_files": 0,
        "tool_use_counter": defaultdict(int),
        "file_read_counter": defaultdict(int),
        "first_ts": None,
        "last_ts": None,
        "models": set(),
        "cost_usd": 0.0,           # MAIN-THREAD interactive session cost
        "cost_input_usd": 0.0,
        "cost_output_usd": 0.0,
        "cost_cache_write_usd": 0.0,
        "cost_cache_read_usd": 0.0,
        "subagent_cost_usd": 0.0,  # additional spend from delegated subagents
        "image_count": 0,
        "compact_count": 0,
    }
    model_counter = Counter()          # main-thread only → drives dominance/routing
    cost_by_model = defaultdict(float)  # for dominant-model cost component (routing)
    # The CLI splits ONE API message (one message.id, one usage) into multiple
    # assistant records — one per content block (thinking/text/tool_use) — each
    # repeating the SAME usage. Summing per-record 2-3x overcounts cost/turns.
    # Count usage once per message.id; still visit every record for content blocks.
    seen_usage_ids = set()

    for fpath, is_sub in session_files(path):
        if is_sub:
            stats["num_subagent_files"] += 1
        try:
            f = open(fpath, "r")
        except OSError as e:
            if not is_sub:
                stats["error"] = str(e)
            continue
        with f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                try:
                    _consume_record(rec, stats, model_counter, cost_by_model,
                                    seen_usage_ids, table, is_sub)
                except Exception:
                    continue  # one bad record must not poison the rest

    total_input_any = (
        stats["input_tokens"]
        + stats["cache_create_5m"]
        + stats["cache_create_1h"]
        + stats["cache_read"]
    )
    stats["total_input_tokens"] = total_input_any
    stats["cache_hit_ratio"] = (stats["cache_read"] / total_input_any) if total_input_any else 0.0
    stats["uncached_ratio"] = (stats["input_tokens"] / total_input_any) if total_input_any else 0.0
    stats["output_ratio"] = (stats["output_tokens"] / total_input_any) if total_input_any else 0.0

    stats["redundant_reads"] = sum((c - 1) for c in stats["file_read_counter"].values() if c > 1)
    stats["unique_files_read"] = len(stats["file_read_counter"])
    stats["total_file_reads"] = sum(stats["file_read_counter"].values())
    stats["had_image"] = stats["image_count"] > 0

    # Dominant model (deterministic tie-break: count desc, then name asc) drives
    # per-session waste/routing pricing downstream.
    if model_counter:
        dominant = sorted(model_counter.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    else:
        dominant = ""
    stats["dominant_model"] = dominant
    stats["dominant_input_price"] = price_for(dominant, table)["in"] if dominant else DEFAULT_PRICE["in"]
    # Cost attributable to the dominant model — routing savings scale this, NOT the
    # whole (mixed-model) session cost.
    stats["dominant_model_cost_usd"] = cost_by_model.get(dominant, stats["cost_usd"])

    stats["models"] = sorted(list(stats["models"]))
    stats["tool_use_counter"] = dict(stats["tool_use_counter"])
    stats.pop("file_read_counter", None)
    return stats


def _consume_record(rec, stats, model_counter, cost_by_model, seen_usage_ids, table, is_sub):
    """Process ONE JSONL record into stats. None-safe; dedups usage by message.id;
    keeps redundancy/dominance main-thread only (is_sub or inline isSidechain excluded)."""
    is_side = bool(is_sub or rec.get("isSidechain"))
    ts = rec.get("timestamp")
    if ts:
        if stats["first_ts"] is None:
            stats["first_ts"] = ts
        stats["last_ts"] = ts

    rtype = rec.get("type")

    if rtype == "user":
        stats["num_user_msgs"] += 1
        msg = rec.get("message") or {}
        content = msg.get("content") or []
        # image_count feeds had_image (downgrade candidacy) — a MAIN-THREAD signal,
        # like the rest of scoring. Subagent vision is the subagent's concern.
        if isinstance(content, list) and not is_side:
            for c in content:
                if isinstance(c, dict) and c.get("type") == "image":
                    stats["image_count"] += 1

    elif rtype == "assistant":
        stats["num_assistant_msgs"] += 1
        if is_side:
            stats["num_sidechain_msgs"] += 1
        msg = rec.get("message") or {}
        model = msg.get("model", "") or ""
        mid = msg.get("id")
        # Usage is counted ONCE per message.id (split records repeat it). When
        # message.id is absent (old logs / fixtures) each record counts as before.
        count_usage = not (mid and mid in seen_usage_ids)
        if mid:
            seen_usage_ids.add(mid)

        if model:
            stats["models"].add(model)
            # Dominance is a MAIN-THREAD property (drives routing); count once per
            # message.id and never for subagents/sidechain.
            if not is_side and count_usage:
                model_counter[model] += 1

        if count_usage:
            usage = msg.get("usage") or {}
            price = price_for(model, table)

            inp = usage.get("input_tokens") or 0
            out = usage.get("output_tokens") or 0
            cw = usage.get("cache_creation_input_tokens") or 0
            cr = usage.get("cache_read_input_tokens") or 0

            cw_detail = usage.get("cache_creation") or {}
            cw5 = cw_detail.get("ephemeral_5m_input_tokens") or 0
            cw1h = cw_detail.get("ephemeral_1h_input_tokens") or 0
            if cw5 + cw1h == 0 and cw > 0:
                cw5 = cw  # older CLI: no breakdown, assume the cheaper 5m TTL

            c_in = inp * price["in"] / 1e6
            c_out = out * price["out"] / 1e6
            c_cw = cw5 * price["cw5"] / 1e6 + cw1h * price["cw1h"] / 1e6
            c_cr = cr * price["cr"] / 1e6
            msg_cost = c_in + c_out + c_cw + c_cr

            if is_side:
                # Subagent spend is real money but a SEPARATE trajectory — keep it
                # out of the main-thread token totals/score/KPIs (else cache/density
                # axes get polluted by subagent volume) and report it as its own
                # number. cost_usd stays the interactive session's cost.
                stats["subagent_cost_usd"] += msg_cost
            else:
                stats["input_tokens"] += inp
                stats["output_tokens"] += out
                stats["cache_create_5m"] += cw5
                stats["cache_create_1h"] += cw1h
                stats["cache_read"] += cr
                # Per-category cost at THIS message's own model price. The dashboard
                # aggregates these so category bars sum to the cost KPI.
                stats["cost_input_usd"] += c_in
                stats["cost_output_usd"] += c_out
                stats["cost_cache_write_usd"] += c_cw
                stats["cost_cache_read_usd"] += c_cr
                stats["cost_usd"] += msg_cost
                cost_by_model[model] += msg_cost

        # Tool-use blocks live in exactly one split record each, so visit every
        # record — but redundancy/tool economy are MAIN-THREAD signals (F1): a
        # subagent re-reading a file in its own context is not the user's waste.
        content = msg.get("content") or []
        if isinstance(content, list) and not is_side:
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    stats["num_tool_calls"] += 1
                    tname = c.get("name", "unknown")
                    stats["tool_use_counter"][tname] += 1
                    if tname == "Read":
                        fp = (c.get("input") or {}).get("file_path", "")
                        if fp:
                            stats["file_read_counter"][fp] += 1

    # NOTE: "compact-summary" is the record type this counter assumes; it has NOT
    # been confirmed against the current CLI schema (no /compact in sampled logs),
    # so compact_count is best-effort and may read 0 even when /compact was used.
    elif rtype == "compact-summary":
        stats["compact_count"] += 1


def score_session(s, weights):
    """0-100 per-axis scoring, weighted by `weights` (must sum to 1.0)."""
    # Cache utilization: cache_read / total_input, 85% = full marks.
    cache_score = min(100, s["cache_hit_ratio"] / 0.85 * 100)

    # Output density: sweet spot ~2%. Penalize too low (churn) and too high (monologue).
    od = s["output_ratio"]
    if od < 0.005:
        density_score = od / 0.005 * 60
    elif od < 0.02:
        density_score = 60 + (od - 0.005) / 0.015 * 40
    elif od < 0.05:
        density_score = 100 - (od - 0.02) / 0.03 * 20
    else:
        density_score = max(40, 80 - (od - 0.05) * 200)

    # Read redundancy: penalize per redundant read as share of total reads.
    total_reads = s["total_file_reads"] or 1
    redundancy_ratio = s["redundant_reads"] / total_reads
    redundancy_score = max(0, 100 - redundancy_ratio * 200)

    # Tool economy: healthy 2-10 tool calls per 1k output tokens. >20 = thrash.
    out_k = max(1, s["output_tokens"] / 1000)
    tpk = s["num_tool_calls"] / out_k
    if tpk < 2:
        tool_score = 70 + tpk * 15
    elif tpk < 10:
        tool_score = 100 - (tpk - 2) * 2
    elif tpk < 20:
        tool_score = 84 - (tpk - 10) * 4
    else:
        tool_score = max(0, 44 - (tpk - 20) * 2)

    composite = (
        cache_score * weights["cache"]
        + density_score * weights["density"]
        + redundancy_score * weights["redundancy"]
        + tool_score * weights["tool"]
    )

    return {
        "cache_score": round(cache_score, 1),
        "density_score": round(density_score, 1),
        "redundancy_score": round(redundancy_score, 1),
        "tool_score": round(tool_score, 1),
        "composite": round(composite, 1),
        "grade": grade_of(composite),
    }


def grade_of(score):
    for threshold, grade in [
        (90, "A+"), (85, "A"), (80, "A-"), (75, "B+"), (70, "B"),
        (65, "B-"), (60, "C+"), (55, "C"), (50, "C-"), (40, "D"),
    ]:
        if score >= threshold:
            return grade
    return "F"


def parse_weights(spec):
    w = dict(DEFAULT_WEIGHTS)
    if spec:
        for pair in spec.split(","):
            k, _, v = pair.partition("=")
            k = k.strip()
            if k not in w:
                print(f"[error] --weights: unknown axis '{k}' "
                      f"(valid: {', '.join(w)})", file=sys.stderr)
                sys.exit(2)
            try:
                w[k] = float(v)
            except ValueError:
                print(f"[error] --weights: '{pair.strip()}' is not <axis>=<number>",
                      file=sys.stderr)
                sys.exit(2)
    total = sum(w.values())
    if total <= 0:
        print("[error] --weights must sum to a positive number", file=sys.stderr)
        sys.exit(2)
    if abs(total - 1.0) > 1e-6:
        print(f"[warn] weights sum to {total:.3f}, not 1.0 — renormalizing", file=sys.stderr)
        w = {k: v / total for k, v in w.items()}
    return w


def safe_open_write(path):
    """Open `path` for writing WITHOUT following a symlink (O_NOFOLLOW). The
    default outputs live in world-writable /tmp; a pre-planted symlink there
    would otherwise let a co-located user redirect our write onto their target
    (CWE-59). On POSIX (where O_NOFOLLOW is defined) a symlinked path raises instead
    of clobbering; on platforms lacking it the flag degrades to 0 (best-effort)."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    return os.fdopen(fd, "w")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="Repository path (default: cwd)")
    ap.add_argument("--sessions-dir", help="Direct path to ~/.claude/projects/<encoded>/")
    ap.add_argument("--out", default="/tmp/session_analysis.json", help="Output JSON path")
    ap.add_argument("--pricing", help="JSON file overriding the built-in pricing table")
    ap.add_argument("--weights", help="e.g. cache=0.35,redundancy=0.30,density=0.15,tool=0.20")
    args = ap.parse_args()

    table = load_pricing(args.pricing) if args.pricing else dict(PRICING)
    weights = parse_weights(args.weights)
    sessions_dir = resolve_sessions_dir(args)

    if not os.path.isdir(sessions_dir):
        print(f"[error] sessions dir not found: {sessions_dir}", file=sys.stderr)
        print("        This repo may have never been opened with Claude Code.", file=sys.stderr)
        sys.exit(2)

    files = sorted(glob.glob(os.path.join(sessions_dir, "*.jsonl")))
    if not files:
        print(f"[error] no .jsonl files in {sessions_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"[info] sessions dir: {sessions_dir}")
    print(f"[info] found {len(files)} session files")

    results = []
    for fp in files:
        s = analyze_session(fp, table)
        if s["total_input_tokens"] == 0 and s["output_tokens"] == 0:
            continue
        s["scores"] = score_session(s, weights)
        results.append(s)

    if not results:
        print("[error] all sessions have empty usage (old CLI?), nothing to report", file=sys.stderr)
        sys.exit(2)

    totals = {
        "sessions_dir": sessions_dir,
        "sessions": len(results),
        "input_tokens": sum(r["input_tokens"] for r in results),
        "output_tokens": sum(r["output_tokens"] for r in results),
        "cache_create_5m": sum(r["cache_create_5m"] for r in results),
        "cache_create_1h": sum(r["cache_create_1h"] for r in results),
        "cache_read": sum(r["cache_read"] for r in results),
        "cost_usd": sum(r["cost_usd"] for r in results),
        "cost_input_usd": sum(r["cost_input_usd"] for r in results),
        "cost_output_usd": sum(r["cost_output_usd"] for r in results),
        "cost_cache_write_usd": sum(r["cost_cache_write_usd"] for r in results),
        "cost_cache_read_usd": sum(r["cost_cache_read_usd"] for r in results),
        "subagent_cost_usd": sum(r.get("subagent_cost_usd", 0.0) for r in results),
        "total_input_tokens": sum(r["total_input_tokens"] for r in results),
        "num_tool_calls": sum(r["num_tool_calls"] for r in results),
        "redundant_reads": sum(r["redundant_reads"] for r in results),
        "image_count": sum(r["image_count"] for r in results),
        "compact_count": sum(r["compact_count"] for r in results),
        "subagent_files": sum(r.get("num_subagent_files", 0) for r in results),
    }
    totals["cache_hit_ratio"] = (
        totals["cache_read"] / totals["total_input_tokens"] if totals["total_input_tokens"] else 0
    )
    # Carry the config so the dashboard/report can cite exactly what it scored on.
    totals["weights"] = weights
    totals["weight_evidence"] = WEIGHT_EVIDENCE

    results.sort(key=lambda r: r["cost_usd"], reverse=True)

    with safe_open_write(args.out) as f:
        json.dump({"totals": totals, "sessions": results}, f, default=str, indent=2)

    print(f"[ok] wrote {args.out}")
    print(f"     {len(results)} sessions, ${totals['cost_usd']:.2f}, cache hit {totals['cache_hit_ratio']*100:.1f}%")
    print("     NOTE: composite is an efficiency proxy, not cost-of-pass — it cannot "
          "see task success (session-5).")


if __name__ == "__main__":
    main()
