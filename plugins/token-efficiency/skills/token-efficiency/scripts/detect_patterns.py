#!/usr/bin/env python3
"""Detect inefficiency patterns in Claude Code sessions with $ waste estimates.

v2 — research-grounded evolution of the external `improve-token-efficiency` detectors.
Each detector carries an evidence tag; full derivations in references/research/.

Detectors (5 original + 3 new, research-grounded):
  1. context-bloat        : context > 100k for 20+ consecutive turns without a >50% drop.
                            [HEURISTIC threshold; quality harm CONFIRMED — ACON 2510.00615]
  2. giant-tool-outputs   : tool_result >= 50k chars (~12.5k tokens).
                            [CONFIRMED signal — Squeez 2604.04979: ~92% of an observation is
                             prunable at recall 0.86. Fix text CORRECTED: no head/tail truncation.]
  3. poor-cache-util      : per-turn cache_hit < 50% AND context > 30k.
                            [CONFIRMED economics — session-2, cache read 0.1x vs write 1.25x]
  4. duplicate-tools      : SHA-256 of (tool_name, input). Exact repeats are pure waste.
                            [AgentDiet "redundant" category — 2509.23586]
  5. subagent-overuse     : >=5 Agent calls AND avg result <= 2k tokens.
                            [Refined by Context-Folding 2510.11967: unfolded vs folded delegation]

  NEW:
  6. stale-observation    : a MID-SIZED tool_result (20-50k chars; giant ones are handled by
                            detector 2 via carried-turns) that stays in context long after its
                            subtask likely completed ("expired" — AgentDiet). Masking stale
                            observations is ~52% cheaper at equal solve rate (Complexity Trap
                            2508.21433). [PLAUSIBLE]
  7. cache-invalidation-churn : cache writes keep recurring at high context — a symptom of a
                            shifting prompt prefix (CLAUDE.md edited mid-run, model switch,
                            late image). Exact-prefix caching means one byte change re-writes
                            the whole suffix. [CONFIRMED mechanics — session-2]
  8. read-exploration-heavy : Read/Grep/Glob dominate token spend AND redundant re-reads are
                            present. Reads are 76.1% of coding-agent tokens (2606.14066), so
                            this is the highest-$ lever. [PLAUSIBLE]

Waste is priced at the session's OWN dominant-model rate (not a flat Opus rate) so
mixed Sonnet/Haiku fleets aren't overstated. Cost multipliers per session-2.
Sidechain (subagent) records are EXCLUDED from the main trajectory (separate context).
The CLI splits one API message (one message.id) into thinking/text/tool_use records
that repeat the same usage — we merge them into ONE logical turn (usage once, tool_uses
unioned) so n_turns and carried-turn waste aren't 2-3x inflated. Synthetic / empty
API-error records (no context) are skipped so they don't reset bloat runs.

HONESTY: per-pattern waste sums can double-count the same event (a duplicated Read
of a giant file hits duplicate_tools, read_exploration_heavy, AND giant_tool_outputs)
— treat total_waste_usd as an upper-bound estimate, not additive line items.

Usage:
  python3 detect_patterns.py --repo /path/to/repo --out /tmp/pattern_analysis.json
  python3 detect_patterns.py --pricing ./pricing.json   # keep $ in sync with analyze_sessions
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

# Cache multipliers relative to base input rate (session-2). Same for every model.
# Waste formulas use the conservative 5m write tier (1.25x); the 1h tier (2.0x)
# exists but charging it here would overstate — analyze_sessions prices actuals.
CR_MULT, CW5_MULT = 0.1, 1.25
# Base input $/1M by model. Kept in sync with analyze_sessions.PRICING.
INPUT_PRICE = {
    "claude-fable-5": 10.0, "claude-mythos-5": 10.0,
    "claude-opus-4-8": 5.0, "claude-opus-4-7": 5.0, "claude-opus-4-6": 5.0, "claude-opus-4-5": 5.0,
    "claude-sonnet-5": 3.0, "claude-sonnet-4-6": 3.0, "claude-sonnet-4-5": 3.0,
    "claude-haiku-4-5": 1.0, "<synthetic>": 0.0,
}
DEFAULT_INPUT = 5.0  # unknown → Opus-tier

# Thresholds (evidence tags in module docstring)
CONTEXT_HIGH_TOKENS = 100_000
CONTEXT_BASELINE = 80_000
CONSEC_TURNS_REQUIRED = 20
COMPACT_DROP_RATIO = 0.50

GIANT_TOOL_CHARS = 50_000
CHARS_PER_TOKEN = 4

CACHE_HIT_FLOOR = 0.50
CONTEXT_FLOOR_FOR_CACHE = 30_000

SUBAGENT_MIN_CALLS = 5
TRIVIAL_RESULT_TOKENS = 2000
# HEURISTIC, no primary source (session-3: "사소 위임의 오버헤드는 실측 근거 없음").
# Rough system-prompt + framing cost per spawned agent; tune if you measure it.
SUBAGENT_OVERHEAD_TOKENS = 3000

# NEW thresholds
STALE_TOOL_CHARS = 20_000       # a 5k+ token observation is worth masking once stale
STALE_MIN_REMAINING_TURNS = 10  # ...if it then sits in context this many more turns
CHURN_MIN_TURNS = 10            # need enough high-context turns to call it churn
CHURN_WRITE_SHARE = 0.30        # cache_create is >30% of input at high context = prefix shifting
READ_TOOLS = {"Read", "Grep", "Glob", "NotebookRead"}
READ_DOMINANCE_SHARE = 0.60     # read-type tool calls are 60%+ of all tool calls


def encode_repo_path(p):
    """Claude Code encodes every non-alphanumeric char as '-' (see analyze_sessions)."""
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(os.path.expanduser(p)))


def load_input_prices(path):
    """Merge a user pricing file (same format as analyze_sessions --pricing) into
    INPUT_PRICE so both scripts price waste identically."""
    with open(path) as f:
        user = json.load(f)
    for model, row in user.items():
        # Same schema as analyze_sessions.load_pricing (in AND out) so one shared
        # file either works for BOTH scripts or fails identically in both.
        if not isinstance(row, dict) or "in" not in row or "out" not in row:
            print(f"[error] --pricing row for '{model}' must have at least "
                  f"{{\"in\": <usd/1M>, \"out\": <usd/1M>}}", file=sys.stderr)
            sys.exit(2)
        INPUT_PRICE[model] = row["in"]


def input_price_for(model):
    if model in INPUT_PRICE:
        return INPUT_PRICE[model]
    # Strip a dated snapshot suffix (claude-haiku-4-5-20251001 → claude-haiku-4-5)
    # so dated model IDs aren't mispriced at the Opus-tier default.
    return INPUT_PRICE.get(re.sub(r"-\d{8}$", "", model or ""), DEFAULT_INPUT)


def stringify(obj):
    return json.dumps(obj, sort_keys=True, default=str)


def sha256_short(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def estimate_tokens_from_content(content):
    if isinstance(content, str):
        return len(content) // CHARS_PER_TOKEN
    if isinstance(content, list):
        total = 0
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    total += len(item.get("text", "")) // CHARS_PER_TOKEN
                elif item.get("type") == "image":
                    total += 1500
        return total
    return 0


def chars_of_content(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        return sum(
            len(item.get("text", "")) if isinstance(item, dict) and item.get("type") == "text" else 0
            for item in content
        )
    return 0


def analyze_session(path):
    sid = os.path.basename(path).replace(".jsonl", "")
    # Per-LINE parse: the CLI appends live, so a truncated final line must skip that
    # record only — the external skill's list-comprehension dropped the whole session.
    records = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                # 비-dict 최상위 라인([1,2,3] 등)은 이후 r.get(...) 재스캔(sidechain 카운트)에서
                # AttributeError로 세션 전체를 죽인다(analyze와의 강건성 비대칭) — 파싱 시점에 배제.
                if isinstance(rec, dict):
                    records.append(rec)
    except OSError:
        return None

    tool_results = {}
    models_seen = []
    turn_by_key = {}   # message.id (or synthetic key) → logical turn
    key_order = []

    for rec in records:
        try:
            _consume_detect_record(rec, turn_by_key, key_order, tool_results, models_seen)
        except Exception:
            continue  # one corrupt record (non-str id, non-dict message) must not
                      # crash the whole run (parity with analyze_sessions)

    assistant_turns = [turn_by_key[k] for k in key_order]
    n_turns = len(assistant_turns)
    if n_turns == 0:
        return None

    # Dominant model (deterministic tie-break: count desc, then name asc) drives
    # per-session pricing. sidechain_msgs recomputed below from the record scan.
    sidechain_msgs = sum(1 for r in records
                         if r.get("isSidechain") and r.get("type") == "assistant")
    if models_seen:
        model = sorted(Counter(models_seen).items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    else:
        model = ""
    in_price = input_price_for(model)

    findings = {}
    for key, fn in [
        ("context_bloat", detect_context_bloat),
        ("giant_tool_outputs", detect_giant_tool_outputs),
        ("poor_cache_util", detect_poor_cache_util),
        ("duplicate_tools", detect_duplicate_tools),
        ("subagent_overuse", detect_subagent_overuse),
        ("stale_observation", detect_stale_observation),
        ("cache_invalidation_churn", detect_cache_churn),
        ("read_exploration_heavy", detect_read_exploration),
    ]:
        res = fn(assistant_turns, tool_results, n_turns, in_price)
        if res.get("triggered"):
            findings[key] = res

    return {
        "session_id": sid,
        "n_turns": n_turns,
        "sidechain_msgs_excluded": sidechain_msgs,
        "model": model,
        "peak_context": max((t["context_size"] for t in assistant_turns), default=0),
        "findings": findings,
    }


def _consume_detect_record(rec, turn_by_key, key_order, tool_results, models_seen):
    """Process ONE record into the turn/result structures (wrapped in try/except
    by the caller so a single corrupt record — non-str id, non-dict message —
    can't crash the whole run, matching analyze_sessions' per-record isolation)."""
    if not isinstance(rec, dict):
        return
    # Sidechain (subagent) records run in a SEPARATE context window — excluded from
    # the main trajectory (the caller recomputes the sidechain count separately).
    if rec.get("isSidechain"):
        return
    rtype = rec.get("type")
    if rtype == "assistant":
        msg = rec.get("message")
        if not isinstance(msg, dict):
            return
        model = msg.get("model", "") or ""
        usage = msg.get("usage") or {}
        cw_detail = usage.get("cache_creation") or {}
        cw_total = (
            (cw_detail.get("ephemeral_5m_input_tokens") or 0)
            + (cw_detail.get("ephemeral_1h_input_tokens") or 0)
        )
        if cw_total == 0:
            cw_total = usage.get("cache_creation_input_tokens") or 0

        inp = usage.get("input_tokens") or 0
        cr = usage.get("cache_read_input_tokens") or 0
        out = usage.get("output_tokens") or 0
        context_size = inp + cr + cw_total

        # Synthetic / empty API-error records carry no real context — skip so they
        # don't reset bloat runs or read as a 100% context drop.
        if model == "<synthetic>" or (context_size == 0 and out == 0):
            return

        tool_uses = []
        content = msg.get("content") or []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    tool_uses.append({
                        "id": c.get("id"),
                        "name": c.get("name", "unknown"),
                        "input": c.get("input") or {},
                    })

        # ONE logical turn per message.id (split records repeat usage). A non-str
        # id is coerced to the uuid fallback so it stays a hashable dict key.
        mid = msg.get("id")
        if not isinstance(mid, (str, int)):
            mid = None
        mid = mid or ("rec:" + str(rec.get("uuid") or len(key_order)))
        if mid in turn_by_key:
            turn_by_key[mid]["tool_uses"].extend(tool_uses)
        else:
            if model:
                models_seen.append(model)
            turn_by_key[mid] = {
                "idx": len(key_order),
                "input_tokens": inp, "cache_read": cr, "cache_create": cw_total,
                "output_tokens": out, "context_size": context_size,
                "model": model, "tool_uses": tool_uses,
            }
            key_order.append(mid)

    elif rtype == "user":
        msg = rec.get("message")
        if not isinstance(msg, dict):
            return
        content = msg.get("content") or []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_result":
                    tu_id = c.get("tool_use_id")
                    result_content = c.get("content")
                    tool_results[tu_id] = {
                        "chars": chars_of_content(result_content),
                        "tokens": estimate_tokens_from_content(result_content),
                        "result_hash": sha256_short(str(result_content))[:12],
                    }


def carried_turns(turns, obs_idx, n_turns):
    """How many turns an observation at obs_idx actually rides along: cut at the
    first >50% context drop after it (a /compact or history rewrite evicts old
    observations), instead of charging every remaining turn."""
    for j in range(obs_idx + 1, n_turns):
        prev_ctx = turns[j - 1]["context_size"]
        if prev_ctx > 0 and (prev_ctx - turns[j]["context_size"]) / prev_ctx > COMPACT_DROP_RATIO:
            return j - obs_idx - 1
    return n_turns - obs_idx - 1


# ----------------- detectors (signature: turns, tool_results, n_turns, in_price) -----

def detect_context_bloat(turns, tool_results, n_turns, in_price):
    best_run, current_run = [], []
    for i, t in enumerate(turns):
        if t["context_size"] > CONTEXT_HIGH_TOKENS:
            if current_run:
                prev_ctx = turns[current_run[-1]]["context_size"]
                this_ctx = t["context_size"]
                if prev_ctx > 0 and (prev_ctx - this_ctx) / prev_ctx > COMPACT_DROP_RATIO:
                    if len(current_run) > len(best_run):
                        best_run = current_run
                    current_run = [i]
                    continue
            current_run.append(i)
        else:
            if len(current_run) > len(best_run):
                best_run = current_run
            current_run = []
    if len(current_run) > len(best_run):
        best_run = current_run

    if len(best_run) < CONSEC_TURNS_REQUIRED:
        return {"triggered": False}

    waste_tokens = sum(max(0, turns[i]["context_size"] - CONTEXT_BASELINE) for i in best_run)
    waste_usd = waste_tokens * (in_price * CR_MULT) / 1e6
    return {
        "triggered": True,
        "evidence": f"{len(best_run)} consecutive turns above 100k context, no >50% drop",
        "consec_turns": len(best_run),
        "peak_context": max(turns[i]["context_size"] for i in best_run),
        "waste_tokens": int(waste_tokens),
        "waste_usd": round(waste_usd, 2),
        "research": "ACON 2510.00615: unbounded context growth degrades reasoning AND cost.",
        "fix": "Run /compact when accumulated waste exceeds one cache re-warm. Branch a new "
               "session for unrelated tasks. Don't compact so often you thrash the cache.",
    }


def detect_giant_tool_outputs(turns, tool_results, n_turns, in_price):
    giants = []
    for turn in turns:
        for tu in turn["tool_uses"]:
            res = tool_results.get(tu["id"])
            if res and res["chars"] >= GIANT_TOOL_CHARS:
                remaining = carried_turns(turns, turn["idx"], n_turns)
                giants.append({
                    "tool": tu["name"], "turn_idx": turn["idx"], "chars": res["chars"],
                    "tokens": res["tokens"], "remaining_turns": remaining,
                    "waste_tokens": res["tokens"] * remaining,
                })
    if not giants:
        return {"triggered": False}
    total_waste = sum(g["waste_tokens"] for g in giants)
    return {
        "triggered": True,
        "evidence": f"{len(giants)} tool result(s) >= 50k chars, persisting in context "
                    f"(carried turns cut at the first compact-like context drop)",
        "count": len(giants),
        "biggest_chars": max(g["chars"] for g in giants),
        "waste_tokens": int(total_waste),
        "waste_usd": round(total_waste * (in_price * CR_MULT) / 1e6, 2),
        "samples": giants[:3],
        "research": "Squeez 2604.04979: ~92% of a tool observation is prunable at recall 0.86; "
                    "naive truncation loses most load-bearing lines (recall First-N 0.14, "
                    "Last-N 0.05, BM25 0.22 at ~10% keep).",
        "fix": "Scope the call so the result is small (grep/targeted read/`wc -l` first, "
               "`head` only when you know the top is what you need). Do NOT blind-truncate a "
               "large result you already have — you cannot tell which lines matter. /compact "
               "after an unavoidably large read.",
    }


def detect_poor_cache_util(turns, tool_results, n_turns, in_price):
    bad = []
    for t in turns:
        if t["context_size"] < CONTEXT_FLOOR_FOR_CACHE:
            continue
        cr, cw = t["cache_read"], t["cache_create"]
        denom = cr + cw + t["input_tokens"]
        if denom == 0:
            continue
        # NOTE: a turn with cr==cw==0 but large input_tokens is the WORST case
        # (no caching at all at high context) — the external skill's `cr+cw==0:
        # continue` guard excluded exactly those turns from detection.
        hit = cr / denom
        if hit < CACHE_HIT_FLOOR:
            bad.append({"idx": t["idx"], "hit": round(hit, 3),
                        "cache_create": cw, "uncached_input": t["input_tokens"]})
    if not bad:
        return {"triggered": False}
    # Waste = write premium over a read (conservative 5m: 1.25x-0.1x) on re-written
    # cache + full-vs-read spread (1.0x-0.1x) on input that wasn't cached at all.
    waste_tokens = sum(b["cache_create"] + b["uncached_input"] for b in bad)
    waste_usd = (
        sum(b["cache_create"] for b in bad) * (in_price * (CW5_MULT - CR_MULT))
        + sum(b["uncached_input"] for b in bad) * (in_price * (1.0 - CR_MULT))
    ) / 1e6
    return {
        "triggered": True,
        "evidence": f"{len(bad)} turns with cache hit < 50% at context > 30k",
        "bad_turns_count": len(bad),
        "waste_tokens": int(waste_tokens),
        "waste_usd": round(waste_usd, 2),
        "research": "session-2: exact-prefix caching. Read is 0.1x, write is 1.25x-2x — a low hit "
                    "ratio means paying the write premium every turn.",
        "fix": "Settle CLAUDE.md before long runs; don't mutate the prompt prefix mid-session; "
               "avoid late images; don't switch models mid-session (caches are model-scoped).",
    }


def detect_duplicate_tools(turns, tool_results, n_turns, in_price):
    # Waste = SAME input AND SAME result (AgentDiet 'redundant' = repeated *content*).
    # Same input with a DIFFERENT result is a legitimate stateful re-check (git status
    # dirty→clean, Read→Edit→Read) — counted separately as "stale re-check", not waste.
    seen, dups, stateful = {}, [], 0
    for turn in turns:
        for tu in turn["tool_uses"]:
            key = sha256_short(stringify((tu["name"], tu["input"])))
            res = tool_results.get(tu["id"], {"tokens": 0, "result_hash": None})
            rhash = res.get("result_hash")
            if key in seen:
                prev_turn, prev_hash = seen[key]
                if rhash is not None and prev_hash is not None and rhash != prev_hash:
                    stateful += 1  # same call, changed world → not waste
                else:
                    dups.append({"tool": tu["name"], "first_turn": prev_turn,
                                 "dup_turn": turn["idx"], "result_tokens": res["tokens"]})
            seen[key] = (turn["idx"], rhash)
    if not dups:
        return {"triggered": False}
    waste_tokens = sum(d["result_tokens"] for d in dups)
    by_tool = defaultdict(int)
    for d in dups:
        by_tool[d["tool"]] += 1
    stateful_note = (f" ({stateful} same-input calls with changed results excluded as "
                     f"legitimate re-checks)" if stateful else "")
    return {
        "triggered": True,
        "evidence": f"{len(dups)} duplicate tool calls (same name+input+result){stateful_note}",
        "duplicate_count": len(dups),
        "stateful_recheck_count": stateful,
        "by_tool": dict(by_tool),
        "waste_tokens": int(waste_tokens),
        # Re-entered result is typically re-written to the 5m cache — 1.25x input.
        # (Multiplier choice is a heuristic; session-2 only pins the multipliers.)
        "waste_usd": round(waste_tokens * (in_price * CW5_MULT) / 1e6, 2),
        "samples": dups[:3],
        "research": "AgentDiet 2509.23586 'redundant' category — repeated *content* across steps "
                    "(we require identical result, not just identical input).",
        "fix": "Reference the earlier result from context instead of re-calling. Common culprits: "
               "re-Reading an unchanged file after an edit, re-running an unchanged Grep/Bash query.",
    }


def detect_subagent_overuse(turns, tool_results, n_turns, in_price):
    calls = []
    for turn in turns:
        for tu in turn["tool_uses"]:
            if tu["name"] in ("Agent", "Task"):
                res = tool_results.get(tu["id"], {"tokens": 0})
                calls.append({"turn_idx": turn["idx"], "result_tokens": res["tokens"]})
    if len(calls) < SUBAGENT_MIN_CALLS:
        return {"triggered": False}
    avg = sum(c["result_tokens"] for c in calls) / len(calls)
    if avg > TRIVIAL_RESULT_TOKENS:
        return {"triggered": False}
    waste_tokens = len(calls) * SUBAGENT_OVERHEAD_TOKENS
    return {
        "triggered": True,
        "evidence": f"{len(calls)} Agent calls, avg result {avg:.0f} tokens (trivial)",
        "agent_calls": len(calls),
        "avg_result_tokens": round(avg, 0),
        "waste_tokens": int(waste_tokens),
        "waste_usd": round(waste_tokens * (in_price * CW5_MULT) / 1e6, 2),
        "research": "Context-Folding 2510.11967: delegation is an efficiency ASSET only when the "
                    "sub-trajectory is folded into a concise summary. The per-agent setup "
                    "overhead figure (~3k tokens) is a HEURISTIC — no primary measurement.",
        "fix": "Inline trivial lookups (single file, simple grep). Reserve subagents for "
               ">5-turn explorations or genuinely parallel/independent work that returns a summary.",
    }


def detect_stale_observation(turns, tool_results, n_turns, in_price):
    """NEW. AgentDiet 'expired' + Complexity Trap: a large observation that stays in context
    long after its subtask completes is maskable at ~52% cost cut with equal solve rate."""
    stale = []
    for turn in turns:
        for tu in turn["tool_uses"]:
            res = tool_results.get(tu["id"])
            if res and res["chars"] >= STALE_TOOL_CHARS and res["chars"] < GIANT_TOOL_CHARS:
                # Carried tokens beyond the turn it was useful — cut at the first
                # compact-like context drop so a later /compact isn't billed as waste.
                carried = carried_turns(turns, turn["idx"], n_turns)
                if carried < STALE_MIN_REMAINING_TURNS:
                    continue
                stale.append({"tool": tu["name"], "turn_idx": turn["idx"],
                              "tokens": res["tokens"], "carried_turns": carried,
                              "waste_tokens": res["tokens"] * carried})
    if not stale:
        return {"triggered": False}
    total = sum(s["waste_tokens"] for s in stale)
    return {
        "triggered": True,
        "evidence": f"{len(stale)} mid-sized tool results (20-50k chars) carried 10+ turns past use",
        "count": len(stale),
        "waste_tokens": int(total),
        "waste_usd": round(total * (in_price * CR_MULT) / 1e6, 2),
        "samples": stale[:3],
        "research": "AgentDiet 2509.23586 'expired' + Complexity Trap 2508.21433: masking stale "
                    "observations halved cost (~52%) at equal SWE-bench solve rate.",
        "fix": "Once a sub-task is done, the file/log that got you there is dead weight. /compact "
               "at sub-task boundaries, or branch the next sub-task into a fresh session so old "
               "observations don't ride along every turn.",
    }


def detect_cache_churn(turns, tool_results, n_turns, in_price):
    """NEW. Persistent cache WRITES at high context = the cached prefix keeps shifting."""
    hi = [t for t in turns if t["context_size"] >= CONTEXT_FLOOR_FOR_CACHE]
    if len(hi) < CHURN_MIN_TURNS:
        return {"triggered": False}
    churny = [t for t in hi
              if (t["cache_create"] + t["input_tokens"] + t["cache_read"]) > 0
              and t["cache_create"] / (t["cache_create"] + t["input_tokens"] + t["cache_read"]) > CHURN_WRITE_SHARE]
    if len(churny) < CHURN_MIN_TURNS:
        return {"triggered": False}
    waste_tokens = sum(t["cache_create"] for t in churny)
    # Churn re-pays the write premium (write - read) each time.
    waste_usd = waste_tokens * (in_price * (CW5_MULT - CR_MULT)) / 1e6
    return {
        "triggered": True,
        "evidence": f"{len(churny)} high-context turns re-writing >30% of input to cache "
                    f"(prefix keeps shifting)",
        "churn_turns": len(churny),
        "waste_tokens": int(waste_tokens),
        "waste_usd": round(waste_usd, 2),
        "research": "session-2: caching is an exact-prefix match; any byte change in the prefix "
                    "re-writes the whole suffix. Mid-run CLAUDE.md edits, model switches, and late "
                    "images are the usual culprits.",
        "fix": "Freeze the prompt prefix before the long stretch: finalize CLAUDE.md, pick the "
               "model up front, attach images early. Put volatile content LAST.",
    }


def detect_read_exploration(turns, tool_results, n_turns, in_price):
    """NEW. Read/Grep/Glob dominate tool calls AND re-reads are present — the highest-$ lever
    because reads are 76.1% of coding-agent token spend (2606.14066)."""
    read_calls, total_calls = 0, 0
    file_reads = defaultdict(int)
    for turn in turns:
        for tu in turn["tool_uses"]:
            total_calls += 1
            if tu["name"] in READ_TOOLS:
                read_calls += 1
            if tu["name"] == "Read":
                fp = (tu["input"] or {}).get("file_path", "")
                if fp:
                    file_reads[fp] += 1
    if total_calls == 0:
        return {"triggered": False}
    share = read_calls / total_calls
    redundant = sum((c - 1) for c in file_reads.values() if c > 1)
    if share < READ_DOMINANCE_SHARE or redundant == 0:
        return {"triggered": False}
    # Rough: each redundant read re-enters context (~3k tokens) and is cache-read every later turn.
    waste_tokens = redundant * 3000
    return {
        "triggered": True,
        "evidence": f"read-type tools are {share*100:.0f}% of tool calls with {redundant} "
                    f"redundant re-reads",
        "read_share": round(share, 3),
        "redundant_reads": redundant,
        "waste_tokens": int(waste_tokens),
        "waste_usd": round(waste_tokens * (in_price * CW5_MULT) / 1e6, 2),
        "research": "arXiv:2606.14066: read ops are 76.1% of coding-agent tokens (vs execute 12.1%, "
                    "edit 11.8%) — read discipline is the single highest-leverage saving.",
        "fix": "Grep/Glob to locate BEFORE Read; read with line ranges, not whole files; keep a "
               "mental index of what you've already read instead of re-Reading unchanged files.",
    }


# ----------------- main -----------------

PATTERN_KEYS = ["context_bloat", "giant_tool_outputs", "poor_cache_util", "duplicate_tools",
                "subagent_overuse", "stale_observation", "cache_invalidation_churn",
                "read_exploration_heavy"]


def safe_open_write(path):
    """Write without following a symlink (O_NOFOLLOW) — the default /tmp outputs are
    in a world-writable dir; a planted symlink there would otherwise be clobbered."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    return os.fdopen(os.open(path, flags, 0o600), "w")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", help="Repo path (default cwd)")
    ap.add_argument("--sessions-dir")
    ap.add_argument("--out", default="/tmp/pattern_analysis.json")
    ap.add_argument("--pricing", help="JSON pricing override (same file as analyze_sessions)")
    args = ap.parse_args()

    if args.pricing:
        load_input_prices(args.pricing)

    if args.sessions_dir:
        sessions_dir = os.path.expanduser(args.sessions_dir)
    else:
        repo = args.repo or os.getcwd()
        sessions_dir = os.path.expanduser(f"~/.claude/projects/{encode_repo_path(repo)}")

    if not os.path.isdir(sessions_dir):
        print(f"[error] sessions dir not found: {sessions_dir}", file=sys.stderr)
        sys.exit(2)

    files = sorted(glob.glob(os.path.join(sessions_dir, "*.jsonl")))
    print(f"[info] scanning {len(files)} sessions ...")

    sessions = []
    for fp in files:
        s = analyze_session(fp)
        if s:
            sessions.append(s)

    pattern_totals = {}
    for key in PATTERN_KEYS:
        affected = [s for s in sessions if key in s["findings"]]
        affected.sort(key=lambda s: s["findings"][key]["waste_usd"], reverse=True)
        pattern_totals[key] = {
            "affected_sessions": len(affected),
            "total_waste_usd": round(sum(s["findings"][key]["waste_usd"] for s in affected), 2),
            "total_waste_tokens": sum(s["findings"][key]["waste_tokens"] for s in affected),
            "top_offenders": [
                {"session_id": s["session_id"][:8],
                 "evidence": s["findings"][key]["evidence"],
                 "waste_usd": s["findings"][key]["waste_usd"]}
                for s in affected[:5]
            ],
        }

    totals = {
        "sessions_dir": sessions_dir,
        "sessions_total": len(sessions),
        "sessions_with_any_pattern": sum(1 for s in sessions if s["findings"]),
        "patterns": pattern_totals,
        "total_waste_usd": round(sum(p["total_waste_usd"] for p in pattern_totals.values()), 2),
        "overlap_note": "패턴 간 동일 이벤트 중복 계상 가능 — 합계는 상한 추정치. 예: (1) 중복 Read된 "
                        "거대 파일은 duplicate/read-exploration/giant 3곳에서, (2) 고컨텍스트에서 "
                        "cache write가 큰 턴은 poor-cache와 cache-churn 양쪽에서 같은 cache_create를 계상.",
    }

    sessions.sort(key=lambda s: sum(f["waste_usd"] for f in s["findings"].values()), reverse=True)

    with safe_open_write(args.out) as f:
        json.dump({"totals": totals, "sessions": sessions}, f, default=str, indent=2)

    print(f"[ok] wrote {args.out}")
    print(f"     {totals['sessions_total']} sessions, {totals['sessions_with_any_pattern']} flagged")
    print(f"     total estimated waste: ${totals['total_waste_usd']:.2f} (priced at each session's "
          f"own model rate; patterns may double-count the same event — upper bound)")
    for k in PATTERN_KEYS:
        v = pattern_totals[k]
        print(f"       {k:26s}  {v['affected_sessions']:3d} sessions  ${v['total_waste_usd']:.2f}")


if __name__ == "__main__":
    main()
