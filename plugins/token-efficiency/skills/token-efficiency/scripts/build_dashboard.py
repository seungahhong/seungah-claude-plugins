#!/usr/bin/env python3
"""Build a SELF-CONTAINED HTML efficiency dashboard from analyze_sessions.py output.

v2 changes vs the external skill's dashboard:
  - NO Chart.js CDN dependency. Renders inline SVG bars, so the file opens offline
    and survives a strict CSP (the external version broke both).
  - Category costs come from analyze_sessions' PER-MODEL component sums
    (cost_input_usd 등) — the bars always sum to the cost KPI. Savings use
    effective per-token prices derived from the fleet's actual model mix, not a
    flat Opus rate (mixed Sonnet/Haiku fleets were overstated before).
  - Model-routing savings estimated PER SESSION and only for Opus-tier-or-above
    sessions (already-cheap models are not "downgradeable"); the saving ratio is
    per-session (Fable→Sonnet 70%, Opus→Sonnet 40%). Cost-of-Pass (2508.02694):
    model cost-effectiveness is task-dependent — session-4/5.
  - The /compact recommendation carries a cache-break caveat: over-compacting
    thrashes the cache the score's 35% cache axis rewards — ACON 2510.00615 / session-2.
  - Optionally merges pattern_analysis.json (detect_patterns.py) to show a per-pattern
    waste table alongside the savings cards. The two are DIFFERENT views (detector
    waste vs forward-looking savings heuristics) and are not reconciled to one number.
  - Every session-derived string is esc()'d before entering HTML (session ids come
    from filenames; tool evidence may quote arbitrary file content).

Usage:
  python3 build_dashboard.py --input /tmp/session_analysis.json \
      [--patterns /tmp/pattern_analysis.json] --out /tmp/efficiency_report.html
"""
import argparse
import html as _html
import json
import os
import sys
from collections import Counter

# Fallback when the input JSON predates per-model component costs (Opus-tier).
FALLBACK_IN = 5.0
SONNET_IN = 3.0  # routing target price (Sonnet tier input $/1M) — session-4
# Heuristic constants used in the savings estimates (all labeled on the cards).
TOP_N = 14        # how many top-cost sessions to target with /compact
COMPACT_CUT = 0.30      # assumed cache_read reduction from /compact
TTL_SHIFT_SHARE = 0.40  # share of 1h writes assumed downgradeable to 5m
REDUNDANT_RECACHE_TURNS = 10  # turns a redundant read is re-read from cache


def esc(x):
    return _html.escape(str(x))


def effective_input_price(totals):
    """Fleet-average input $/1M implied by the actual per-model costs. Cache
    multipliers (0.1x/1.25x/2x — session-2) then derive read/write prices."""
    if totals.get("input_tokens") and totals.get("cost_input_usd"):
        return totals["cost_input_usd"] / totals["input_tokens"] * 1e6
    return FALLBACK_IN


def looks_downgradeable(s):
    """Per-session heuristic: an Opus-tier-or-above session that did little
    generation, few tools, and no images is a candidate for a cheaper model.
    Deliberately conservative — cost-of-pass is task-dependent, so we flag
    rather than assume (session-4/5)."""
    return (
        s.get("dominant_input_price", FALLBACK_IN) > SONNET_IN  # already-cheap models excluded
        and not s.get("had_image")
        and s["output_tokens"] < 30_000
        and s["num_tool_calls"] < 40
        and s["output_ratio"] < 0.02
    )


def compute_savings(totals, sessions):
    eff_in = effective_input_price(totals)
    eff_read = eff_in * 0.1
    eff_w5 = eff_in * 1.25
    eff_w1h = eff_in * 2.0

    # 1. Model routing — only genuinely-downgradeable Opus+ sessions. Apply each
    #    session's ratio to the Sonnet tier (Fable→Sonnet 70%, Opus→Sonnet 40%) to the
    #    cost attributable to its DOMINANT model, not the whole (mixed-model, incl.
    #    subagent) session cost — otherwise a Fable-dominant session's 70% ratio would
    #    be wrongly applied to Opus/Haiku spend inside it.
    dg = [s for s in sessions if looks_downgradeable(s)]
    save_model = sum(
        s.get("dominant_model_cost_usd", s["cost_usd"])
        * max(0.0, 1 - SONNET_IN / s.get("dominant_input_price", FALLBACK_IN))
        for s in dg
    )

    # 2. /compact on the top TOP_N cost sessions: cut cache_read by COMPACT_CUT — but
    #    only where it won't thrash the cache (cache-break caveat on the card). Both
    #    are heuristic constants, labeled on the card.
    top = sessions[:TOP_N]
    save_compact = sum(s["cache_read"] for s in top) * COMPACT_CUT * eff_read / 1e6

    # 3. Images: HEURISTIC, no primary source. High-res images cost up to ~4.8k
    #    tokens/image (Anthropic 1차, Opus 4.7+ — session-2 부기); kept in cache and
    #    re-read every turn. Assume ~4.8k × 50% reclaimable. 실측 후 재조정.
    img_count = sum(s["image_count"] for s in sessions)
    save_images = img_count * 4800 * 0.5 * eff_read / 1e6

    # 4. Cache TTL 1h → 5m for TTL_SHIFT_SHARE of 1h writes (spread 2.0x→1.25x).
    save_ttl = totals["cache_create_1h"] * TTL_SHIFT_SHARE * (eff_w1h - eff_w5) / 1e6

    # 5. Redundant reads: each ≈ 3k tokens re-cached (write) then re-read N turns.
    save_redundant = (totals["redundant_reads"] * 3000
                      * (eff_w5 + eff_read * REDUNDANT_RECACHE_TURNS) / 1e6)

    return {
        "model_routing": save_model,
        "compact": save_compact,
        "images": save_images,
        "ttl": save_ttl,
        "redundant": save_redundant,
    }, len(dg)


def svg_bars(pairs, width=560, bar_h=26, gap=10, color="#7ad1ff", label_w=150):
    """Horizontal bar chart as inline SVG. pairs = [(label, value)]."""
    if not pairs:
        return ""
    maxv = max(v for _, v in pairs) or 1
    plot_w = width - label_w - 60
    rows = []
    y = 0
    for label, v in pairs:
        w = int(plot_w * v / maxv)
        rows.append(
            f'<text x="0" y="{y+bar_h*0.7:.0f}" font-size="12" fill="#8b98a9">{esc(label)}</text>'
            f'<rect x="{label_w}" y="{y}" width="{w}" height="{bar_h-6}" rx="3" fill="{color}"/>'
            f'<text x="{label_w+w+6}" y="{y+bar_h*0.7:.0f}" font-size="12" fill="#e6edf3">{v:g}</text>'
        )
        y += bar_h + gap
    return f'<svg viewBox="0 0 {width} {y}" width="100%" role="img">{"".join(rows)}</svg>'


def build_html(data, patterns, repo_name):
    totals = data["totals"]
    sessions = data["sessions"]
    n = len(sessions)
    weights = totals.get("weights", {"cache": 0.35, "redundancy": 0.30, "density": 0.15, "tool": 0.20})
    wev = totals.get("weight_evidence", {})

    # Cache-hit KPI color by value (not hardcoded green): the number can be bad.
    _chr = totals["cache_hit_ratio"]
    cache_hit_cls = "good" if _chr >= 0.5 else ("warn" if _chr >= 0.3 else "bad")

    # Subagent spend is tracked separately from the main-session cost (else it
    # would pollute the score axes) — surface it on the cost KPI so the total is
    # transparent.
    sub_cost = totals.get("subagent_cost_usd", 0.0)
    subagent_kpi_note = f" · 서브에이전트 +${sub_cost:.2f}" if sub_cost else ""

    # Per-model component sums from analyze_sessions — bars sum to the cost KPI.
    # Fallback to Opus-tier derivation only for pre-v2 input files.
    eff_in = effective_input_price(totals)
    cost_cache_write = totals.get(
        "cost_cache_write_usd",
        (totals["cache_create_1h"] * eff_in * 2.0 + totals["cache_create_5m"] * eff_in * 1.25) / 1e6)
    cost_cache_read = totals.get("cost_cache_read_usd", totals["cache_read"] * eff_in * 0.1 / 1e6)
    cost_output = totals.get("cost_output_usd", totals["output_tokens"] * eff_in * 5.0 / 1e6)
    cost_input = totals.get("cost_input_usd", totals["input_tokens"] * eff_in / 1e6)

    savings, dg_count = compute_savings(totals, sessions)
    total_savings = sum(savings.values())
    save_pct = total_savings / totals["cost_usd"] * 100 if totals["cost_usd"] else 0

    comp = {k: sum(s["scores"][f"{k}_score"] for s in sessions) / n
            for k in ("cache", "density", "redundancy", "tool")}
    avg_composite = sum(s["scores"]["composite"] for s in sessions) / n

    grade_order = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
    grades = Counter(s["scores"]["grade"] for s in sessions)

    def short(sid):
        return sid[:8]

    # session_id comes from a FILENAME under ~/.claude/projects — treat as untrusted
    # (a hostile .jsonl name must not inject markup). grade is internal but esc'd
    # anyway: the input JSON is hand-editable. Any future field rendered from
    # detect_patterns (evidence/tool names/samples) MUST be esc()'d the same way.
    top_rows = "\n".join(
        f"<tr><td class='mono'>{esc(short(s['session_id']))}</td>"
        f"<td class='num'>${s['cost_usd']:.2f}</td>"
        f"<td class='num'>{s['num_tool_calls']}</td>"
        f"<td class='num'>{s['total_input_tokens']/1e6:.1f}M</td>"
        f"<td class='num'>{s['output_tokens']/1e3:.1f}k</td>"
        f"<td class='num'>{s['cache_hit_ratio']*100:.1f}%</td>"
        f"<td class='num'>{s['redundant_reads']}</td>"
        f"<td class='num'>{s['scores']['composite']}</td>"
        f"<td><span class='grade g-{esc(s['scores']['grade'][0].lower())}'>{esc(s['scores']['grade'])}</span></td></tr>"
        for s in sessions[:20]
    )

    rubric_rows = ""
    axis_meta = [
        ("캐시 활용도 (cache)", "cache", "cache_read ÷ 총 입력. 0.85 이상 만점."),
        ("중복 Read (redundancy)", "redundancy", "같은 파일 반복 Read 비중."),
        ("산출 밀도 (density)", "density", "출력 ÷ 입력, ~2% 적정."),
        ("도구 효율 (tool)", "tool", "출력 1k당 도구 호출 수, 2–10 건강."),
    ]
    for label, key, desc in axis_meta:
        pct = comp[key]
        rubric_rows += (
            f"<tr><td>{esc(label)}</td>"
            f"<td>{esc(desc)}<div class='bar'><div style='width:{pct:.0f}%'></div></div>"
            f"<div class='ev'>근거: {esc(wev.get(key, 'n/a'))}</div></td>"
            f"<td class='num'>{weights.get(key,0)*100:.0f}%</td>"
            f"<td class='num'>{pct:.1f}/100</td></tr>"
        )

    # Pattern waste table (if provided)
    patterns_html = ""
    if patterns:
        pt = patterns["totals"]["patterns"]
        rows = ""
        ko = {
            "context_bloat": "컨텍스트 부풀림", "giant_tool_outputs": "거대 도구 출력",
            "poor_cache_util": "캐시 활용 저조", "duplicate_tools": "도구 중복 호출",
            "subagent_overuse": "서브에이전트 과다", "stale_observation": "만료 관측치 잔존(신규)",
            "cache_invalidation_churn": "캐시 프리픽스 흔들림(신규)", "read_exploration_heavy": "읽기 탐색 과다(신규)",
        }
        for k, v in sorted(pt.items(), key=lambda kv: kv[1]["total_waste_usd"], reverse=True):
            if v["affected_sessions"] == 0:
                continue
            rows += (f"<tr><td>{esc(ko.get(k,k))}</td><td class='num'>{int(v['affected_sessions'])}</td>"
                     f"<td class='num bad'>${v['total_waste_usd']:.2f}</td></tr>")
        patterns_html = f"""
  <h2>비효율 패턴별 추정 낭비 (각 세션 실제 모델가 기준)</h2>
  <div class="card"><table><thead><tr><th>패턴</th><th class='num'>영향 세션</th><th class='num'>추정 낭비</th></tr></thead>
  <tbody>{rows}</tbody></table>
  <p class="note">추정치는 결정론 휴리스틱입니다. 8개 탐지기 중 3개(만료 관측치·프리픽스 흔들림·읽기 탐색)는 2025~2026 연구로 신설됐습니다.</p></div>"""

    grade_pairs = [(g, grades.get(g, 0)) for g in grade_order if grades.get(g, 0)]

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<title>{esc(repo_name)} — Claude Code 토큰 효율 리포트 (v2)</title>
<style>
 :root {{ --bg:#0b0f17; --panel:#131924; --panel2:#1a2230; --border:#232d3d; --text:#e6edf3;
   --muted:#8b98a9; --accent:#7ad1ff; --good:#4ade80; --warn:#fbbf24; --bad:#ef4444; }}
 *{{box-sizing:border-box}} body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;
   background:var(--bg);color:var(--text);margin:0;padding:32px;line-height:1.5}}
 h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:19px;margin:36px 0 14px;color:var(--accent)}}
 h3{{font-size:13px;margin:0 0 10px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}}
 .sub{{color:var(--muted);font-size:13px;margin-bottom:28px}}
 .grid{{display:grid;gap:16px}} .kpis{{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}}
 .row2{{grid-template-columns:1fr 1fr}}
 .kpi,.card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px}}
 .kpi .v{{font-size:26px;font-weight:700}} .kpi .l{{color:var(--muted);font-size:11px;text-transform:uppercase;margin-bottom:6px}}
 .kpi .s{{color:var(--muted);font-size:12px;margin-top:4px}}
 table{{width:100%;border-collapse:collapse;font-size:13px}} th,td{{padding:8px 10px;text-align:left;border-bottom:1px solid var(--border)}}
 th{{color:var(--muted);font-size:11px;text-transform:uppercase}} .num{{text-align:right;font-variant-numeric:tabular-nums}}
 .mono{{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--muted)}}
 .grade{{padding:2px 8px;border-radius:4px;font-weight:700;font-size:12px}}
 .grade.g-a{{background:#14532d;color:#86efac}} .grade.g-b{{background:#1e3a5f;color:#93c5fd}}
 .grade.g-c{{background:#633a19;color:#fbbf24}} .grade.g-d,.grade.g-f{{background:#4b1515;color:#fca5a5}}
 .bar{{height:8px;background:var(--panel2);border-radius:4px;overflow:hidden;margin:6px 0 4px}}
 .bar>div{{height:100%;background:linear-gradient(90deg,#4ade80,#60a5fa)}}
 .ev{{font-size:11px;color:var(--muted)}} .note{{color:var(--muted);font-size:12px;margin-top:10px}}
 .imp{{border-left:3px solid var(--accent);padding:12px 16px;background:var(--panel2);border-radius:0 8px 8px 0;margin-bottom:10px}}
 .imp .h{{display:flex;justify-content:space-between;margin-bottom:4px}} .imp .t{{font-weight:600}}
 .imp .s{{color:var(--good);font-weight:700}} .imp p{{margin:3px 0;color:var(--muted);font-size:13px}}
 .good{{color:var(--good)}} .warn{{color:var(--warn)}} .bad{{color:var(--bad)}}
 .footer{{margin-top:40px;color:var(--muted);font-size:12px;text-align:center}}
</style></head><body>
 <h1>Claude Code 토큰 효율 리포트 <span style="font-size:14px;color:var(--muted)">v2 · 연구 근거 반영</span></h1>
 <div class="sub">{esc(repo_name)} · 활성 세션 {n}개 · <code>{esc(totals.get('sessions_dir',''))}</code></div>

 <div class="grid kpis">
  <div class="kpi"><div class="l">메인 세션 비용</div><div class="v">${totals['cost_usd']:.2f}</div><div class="s">세션당 ${totals['cost_usd']/n:.2f}{subagent_kpi_note}</div></div>
  <div class="kpi"><div class="l">총 토큰(입력)</div><div class="v">{totals['total_input_tokens']/1e6:.0f}M</div><div class="s">메인 스레드·캐시 포함</div></div>
  <div class="kpi"><div class="l">캐시 적중률</div><div class="v {cache_hit_cls}">{totals['cache_hit_ratio']*100:.1f}%</div><div class="s">메인 스레드 read ÷ 총 입력</div></div>
  <div class="kpi"><div class="l">출력 토큰</div><div class="v">{totals['output_tokens']/1e6:.2f}M</div></div>
  <div class="kpi"><div class="l">평균 종합 점수</div><div class="v">{avg_composite:.1f}</div><div class="s">효율 프록시(≠성공률)</div></div>
 </div>

 <h2>비용 구조 & 등급 분포</h2>
 <div class="grid row2">
  <div class="card"><h3>카테고리별 비용 (USD)</h3>{svg_bars([('캐시쓰기',round(cost_cache_write,2)),('캐시읽기',round(cost_cache_read,2)),('출력',round(cost_output,2)),('입력',round(cost_input,2))])}</div>
  <div class="card"><h3>등급 히스토그램</h3>{svg_bars(grade_pairs, color='#4ade80')}</div>
 </div>

 <h2>평가 기준 (Rubric) — 축별 가중치·근거 등급</h2>
 <div class="card"><table><thead><tr><th style="width:200px">축</th><th>측정 & 근거</th><th class="num">가중치</th><th class="num">평균</th></tr></thead>
  <tbody>{rubric_rows}</tbody></table>
  <p class="note">종합 = Σ(가중치×축점수). 등급: A+≥90 · A≥85 · A-≥80 · B+≥75 · B≥70 · B-≥65 · C+≥60 · C≥55 · C-≥50 · D≥40 · F&lt;40. 가중치는
  <code>--weights</code>로 조정 가능하며 각 축에 근거 등급(CONFIRMED/PLAUSIBLE/HEURISTIC)이 붙습니다.</p></div>

 <h2>비용 상위 세션 Top 20</h2>
 <div class="card"><table><thead><tr><th>세션</th><th class="num">비용</th><th class="num">도구</th><th class="num">총입력</th><th class="num">출력</th><th class="num">캐시적중</th><th class="num">중복Read</th><th class="num">점수</th><th>등급</th></tr></thead>
  <tbody>{top_rows}</tbody></table></div>
{patterns_html}
 <h2>비용 절감 개선안 (예상 $)</h2>
 <div class="card">
  <div class="imp"><div class="h"><div class="t">1. 작업 난이도별 모델 라우팅</div><div class="s">~${savings['model_routing']:.0f}</div></div>
   <p>{dg_count}개 세션이 다운그레이드 후보(Opus급 이상 + 이미지 없음·출력 적음·도구 적음). 플랫 30% 가정이 아니라 <b>후보 세션의 실제 비용 × 세션별 절감비</b>(Fable→Sonnet 70%·Opus→Sonnet 40%)로 계산.</p>
   <p><b>근거:</b> cost-of-pass(2508.02694) — 모델 비용효율은 작업 의존. 저난도만 Sonnet/Haiku로.</p></div>
  <div class="imp"><div class="h"><div class="t">2. 장시간 세션 <code>/compact</code></div><div class="s">~${savings['compact']:.0f}</div></div>
   <p>비용 상위 {TOP_N}개 세션의 cache_read를 {COMPACT_CUT*100:.0f}% 절감 가정. <b>단, 과도한 compact는 캐시를 깨</b> 점수의 35% 캐시 축을 오히려 낮춥니다.</p>
   <p><b>근거:</b> ACON(2510.00615)/session-2. <b>휴리스틱(무근거 상수: 상위 {TOP_N}·절감률 {COMPACT_CUT*100:.0f}%)</b> — 누적 낭비가 캐시 재예열 비용을 넘을 때만.</p></div>
  <div class="imp"><div class="h"><div class="t">3. 이미지 세션 관리</div><div class="s">~${savings['images']:.0f}</div></div>
   <p>고해상 이미지는 장당 최대 ~4.8k 토큰(Anthropic 1차, Opus 4.7+)이 세션 내내 캐시 유지. 확인 후 즉시 /compact.</p>
   <p><b>근거:</b> 장당 토큰은 1차 수치, 회수율 50%는 <b>무근거 휴리스틱</b> — 실측 후 재조정.</p></div>
  <div class="imp"><div class="h"><div class="t">4. Cache TTL 1h → 5m</div><div class="s">~${savings['ttl']:.0f}</div></div>
   <p>단기 세션엔 1h 프리미엄(2×) 불필요. 5m(1.25×)로 충분. 1h 쓰기의 {TTL_SHIFT_SHARE*100:.0f}% 전환 가정.</p>
   <p><b>근거:</b> 배수는 session-2(read 0.1×/write5m 1.25×/write1h 2×), 전환 비율 {TTL_SHIFT_SHARE*100:.0f}%는 <b>무근거 휴리스틱</b>.</p></div>
  <div class="imp"><div class="h"><div class="t">5. 중복 Read 제거</div><div class="s">~${savings['redundant']:.0f}</div></div>
   <p>{totals['redundant_reads']}건 중복 감지. Grep/Glob → 라인범위 Read 순서. 읽기가 코딩 에이전트 토큰의 76.1%(2606.14066).</p>
   <p><b>근거:</b> 읽기 지배는 1차(2606.14066), 건당 3k토큰×{REDUNDANT_RECACHE_TURNS}턴 재읽기는 <b>무근거 휴리스틱</b>.</p></div>
  <div class="imp" style="border-left-color:var(--good);background:#0f2a1a">
   <div class="h"><div class="t">예상 누적 절감 (단순 합)</div><div class="s">~${total_savings:.0f} / ${totals['cost_usd']:.0f} (~{save_pct:.0f}%)</div></div>
   <p>항목 중복 고려 시 실제는 낮을 수 있음. <b>이 숫자는 실행 전 추정</b>이며 실행 후 재측정이 원칙입니다.</p></div>
 </div>

 <div class="footer">가격(1M당, USD): Opus 4.x $5/$25 · Fable 5 $10/$50 · Sonnet 5/4.6 $3/$15 · Haiku 4.5 $1/$5.
 캐시: read 0.1× · write5m 1.25× · write1h 2× (입력가 기준). 최소 캐시 프리픽스 미만은 캐시 자체가 불가
 (Opus·Haiku 4.5 4096 / Fable 5·Sonnet 4.6 2048 / Sonnet 4.5 이하 1024 토큰) — 짧은 세션의 낮은 캐시 점수는 낭비가 아닐 수 있음.
 CDN·외부 스크립트 의존 없음(오프라인/CSP 안전).</div>
</body></html>"""


def safe_open_write(path):
    """Write without following a symlink (O_NOFOLLOW) — default /tmp output guard."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    return os.fdopen(os.open(path, flags, 0o600), "w")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="/tmp/session_analysis.json")
    ap.add_argument("--patterns", help="optional pattern_analysis.json to merge in")
    ap.add_argument("--out", default="/tmp/efficiency_report.html")
    ap.add_argument("--repo-name", default=None)
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[error] input not found: {args.input} (run analyze_sessions.py first)", file=sys.stderr)
        sys.exit(2)
    with open(args.input) as f:
        data = json.load(f)
    if not data.get("sessions"):
        print("[error] no sessions in analysis output", file=sys.stderr)
        sys.exit(2)

    patterns = None
    if args.patterns and os.path.exists(args.patterns):
        with open(args.patterns) as f:
            patterns = json.load(f)

    repo_name = args.repo_name or os.path.basename(data["totals"].get("sessions_dir", "").rstrip("/")) or "Claude Code sessions"
    html = build_html(data, patterns, repo_name)
    with safe_open_write(args.out) as f:
        f.write(html)
    print(f"[ok] wrote {args.out}")
    print(f"     open it: open {args.out}")


if __name__ == "__main__":
    main()
