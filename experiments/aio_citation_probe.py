#!/usr/bin/env python3
"""AIO citation-probability probe for thedent.co.th.

Measures how often Google's AI Overview (AIO) appears for a set of dental
queries and how often The Dent is cited in it, using the SerpApi
`google` + `google_ai_overview` engines (Thailand locale).

The heavy lifting lives in `run_experiment()` so the CLI here and the Flask
web app (`webapp.py`) share one code path. Run from the CLI with:

    SERPAPI_API_KEY=... python aio_citation_probe.py            # all prompts
    SERPAPI_API_KEY=... python aio_citation_probe.py --tier core
    SERPAPI_API_KEY=... python aio_citation_probe.py --smoke    # 1 prompt, 1 run

Outputs (per run):
  - workspace/geo-audits/<date>-aio-citation-probe.xlsx   (primary report)
  - workspace/geo-audits/<date>-aio-citation-probe.md     (condensed report)
  - experiments/results/<date>-raw.jsonl                  (per-run evidence)
  - experiments/results/history.jsonl                     (append-only trend log)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

# --- Paths -----------------------------------------------------------------
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RESULTS_DIR = HERE / "results"
REPORT_DIR = REPO / "workspace" / "geo-audits"
HISTORY_PATH = RESULTS_DIR / "history.jsonl"
PROMPTS_PATH = HERE / "prompts.json"

SERPAPI_ENDPOINT = "https://serpapi.com/search"
MAX_PROMPTS = 30
Z95 = 1.959963984540054  # z for 95% CI


# --- Config ----------------------------------------------------------------
def load_config(path: Path | str = PROMPTS_PATH) -> dict:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    prompts = cfg.get("prompts", [])
    if len(prompts) > MAX_PROMPTS:
        raise ValueError(f"Too many prompts: {len(prompts)} (max {MAX_PROMPTS}).")
    if not prompts:
        raise ValueError("No prompts configured.")
    return cfg


# --- Stats -----------------------------------------------------------------
def wilson_ci(successes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion. Returns (low, high)."""
    if n == 0:
        return (0.0, 1.0)
    phat = successes / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    margin = (z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def ci_halfwidth(successes: int, n: int) -> float:
    low, high = wilson_ci(successes, n)
    return (high - low) / 2.0


# --- URL helpers -----------------------------------------------------------
def host_of(value: str) -> str:
    """Best-effort hostname from a URL or a bare source string."""
    if not value:
        return ""
    v = value.strip()
    if "//" not in v:
        v = "//" + v
    host = (urlparse(v).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def domain_matches(host: str, target: str) -> bool:
    """True if host == target or is a subdomain of target."""
    target = target.lower().lstrip(".")
    return host == target or host.endswith("." + target)


# --- SerpApi (provider-isolated) -------------------------------------------
def serpapi_get(params: dict, session: requests.Session, *, timeout: int = 45,
                max_retries: int = 3) -> tuple[dict | None, bool, str | None]:
    """One SerpApi call. Returns (json_or_None, billed, error).

    `billed` marks a successful (HTTP 200, parseable) search — the only kind
    SerpApi charges for. Network/5xx errors are retried with backoff and are
    not billed. `error` is None on success, else a short diagnostic string
    (HTTP status + SerpApi's error message) so failures are explainable.
    """
    def detail(resp) -> str:
        try:
            msg = resp.json().get("error") or resp.text[:200]
        except ValueError:
            msg = resp.text[:200]
        return f"HTTP {resp.status_code}: {msg}".strip()

    backoff = 2.0
    last_err = "unknown_error"
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(SERPAPI_ENDPOINT, params=params, timeout=timeout)
        except requests.RequestException as exc:
            last_err = f"network_error: {type(exc).__name__}"
            if attempt == max_retries:
                return None, False, last_err
            time.sleep(backoff)
            backoff *= 2
            continue
        if resp.status_code == 200:
            try:
                return resp.json(), True, None
            except ValueError:
                return None, True, "HTTP 200: unparseable JSON body"
        if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_retries:
            last_err = detail(resp)
            time.sleep(backoff)
            backoff *= 2
            continue
        # 4xx (bad key, quota exhausted, etc.) — not retryable, not billed
        return None, False, detail(resp)
    return None, False, last_err


def extract_references(aio: dict) -> list[dict]:
    """Flatten an ai_overview object's references into {title, link, source}."""
    refs = []
    for ref in aio.get("references", []) or []:
        link = ref.get("link") or ref.get("url") or ""
        source = ref.get("source") or ref.get("title") or ""
        refs.append({"title": ref.get("title", ""), "link": link, "source": source})
    return refs


def fetch_aio(query: str, locale: dict, api_key: str,
              session: requests.Session) -> dict:
    """Resolve the AIO for one query. Returns dict with aio_present, references,
    calls (SerpApi searches billed), and error (str|None)."""
    base = {
        "engine": "google",
        "q": query,
        "location": locale.get("location"),
        "google_domain": locale.get("google_domain"),
        "gl": locale.get("gl"),
        "hl": locale.get("hl"),
        "no_cache": "true" if locale.get("no_cache", True) else "false",
        "api_key": api_key,
    }
    base = {k: v for k, v in base.items() if v is not None}

    calls = 0
    data, billed, err = serpapi_get(base, session)
    calls += 1 if billed else 0
    if data is None:
        return {"aio_present": False, "references": [], "calls": calls,
                "error": err or "search_failed"}

    aio = data.get("ai_overview") or {}
    has_inline = bool(aio.get("text_blocks"))
    page_token = aio.get("page_token")
    aio_present = has_inline or bool(page_token)

    references = extract_references(aio) if has_inline else []

    # Second call only when content isn't already inline but a token exists.
    err2 = None
    if not has_inline and page_token:
        follow = {"engine": "google_ai_overview", "page_token": page_token,
                  "api_key": api_key}
        data2, billed2, err2 = serpapi_get(follow, session)
        calls += 1 if billed2 else 0
        if data2:
            references = extract_references(data2.get("ai_overview") or {})

    return {"aio_present": aio_present, "references": references,
            "calls": calls, "error": err2}


# --- Per-prompt run (with adaptive early-stopping) -------------------------
def run_prompt(prompt: dict, cfg: dict, api_key: str, session: requests.Session,
               raw_fh, *, n_runs: int, calls_remaining: int,
               run_date: str, progress=None) -> dict:
    defaults = cfg.get("defaults", {})
    locale = {**defaults, **{k: prompt[k] for k in
              ("location", "gl", "hl", "google_domain", "no_cache")
              if k in prompt}}
    target = cfg.get("target_domain", "thedent.co.th")
    min_runs = int(cfg.get("min_runs", 6))
    target_hw = float(cfg.get("ci_halfwidth_target", 0.10))
    throttle = float(cfg.get("throttle_seconds", 1.5))

    aio_hits = 0
    thedent_hits = 0
    domain_counts: dict[str, int] = {}
    runs_done = 0
    calls_used = 0
    runs = []

    for i in range(1, n_runs + 1):
        if calls_remaining - calls_used < 2:  # reserve for worst-case 2 calls
            break
        res = fetch_aio(locale=locale, query=prompt["q"], api_key=api_key,
                        session=session)
        calls_used += res["calls"]
        runs_done += 1

        hosts = {host_of(r["link"]) or host_of(r["source"]) for r in res["references"]}
        hosts.discard("")
        thedent = any(domain_matches(h, target) for h in hosts)
        if res["aio_present"]:
            aio_hits += 1
            for h in hosts:
                domain_counts[h] = domain_counts.get(h, 0) + 1
        if thedent:
            thedent_hits += 1

        record = {
            "date": run_date, "prompt_id": prompt["id"], "run": i,
            "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "hl": locale.get("hl"), "aio_present": res["aio_present"],
            "thedent_cited": thedent, "domains": sorted(hosts),
            "error": res["error"],
        }
        runs.append(record)
        raw_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        raw_fh.flush()
        if progress:
            progress(prompt["id"], i, n_runs, calls_used)

        # Adaptive early-stopping once the CI is tight enough.
        if runs_done >= min_runs and ci_halfwidth(thedent_hits, runs_done) <= target_hw:
            break
        if i < n_runs:
            time.sleep(throttle)

    lo, hi = wilson_ci(thedent_hits, runs_done)
    aio_lo, aio_hi = wilson_ci(aio_hits, runs_done)
    top = sorted(domain_counts.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "prompt_id": prompt["id"], "query": prompt["q"], "hl": locale.get("hl"),
        "tier": prompt.get("tier", "full"),
        "runs": runs_done, "calls": calls_used,
        "aio_hits": aio_hits, "thedent_hits": thedent_hits,
        "aio_rate": aio_hits / runs_done if runs_done else 0.0,
        "aio_ci": (aio_lo, aio_hi),
        "thedent_rate": thedent_hits / runs_done if runs_done else 0.0,
        "thedent_ci": (lo, hi),
        "thedent_rate_given_aio": (thedent_hits / aio_hits) if aio_hits else 0.0,
        "top_domains": top,
        "raw_runs": runs,
    }


# --- Budget helpers --------------------------------------------------------
def month_to_date_calls(history_path: Path | None = None,
                        today: dt.date | None = None) -> int:
    history_path = history_path or HISTORY_PATH
    today = today or dt.date.today()
    prefix = today.strftime("%Y-%m")
    if not history_path.exists():
        return 0
    total = 0
    for line in history_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if str(rec.get("date", "")).startswith(prefix):
            total += int(rec.get("calls", 0))
    return total


def append_history(results: list[dict], run_date: str,
                   history_path: Path | None = None) -> None:
    history_path = history_path or HISTORY_PATH
    iso_week = dt.date.fromisoformat(run_date).strftime("%G-W%V")
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as fh:
        for r in results:
            lo, hi = r["thedent_ci"]
            fh.write(json.dumps({
                "date": run_date, "iso_week": iso_week, "prompt_id": r["prompt_id"],
                "query": r["query"], "hl": r["hl"], "n_runs": r["runs"],
                "calls": r["calls"], "aio_rate": round(r["aio_rate"], 4),
                "thedent_rate": round(r["thedent_rate"], 4),
                "thedent_ci_low": round(lo, 4), "thedent_ci_high": round(hi, 4),
                "top_domains": [d for d, _ in r["top_domains"][:5]],
            }, ensure_ascii=False) + "\n")


def read_history(history_path: Path | None = None) -> list[dict]:
    history_path = history_path or HISTORY_PATH
    if not history_path.exists():
        return []
    out = []
    for line in history_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


# --- Orchestration ---------------------------------------------------------
def run_experiment(cfg: dict, api_key: str, *, n_runs: int | None = None,
                   tier: str | None = None, progress=None,
                   run_date: str | None = None) -> dict:
    """Run the probe end to end and write all reports. Returns a summary dict."""
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is required.")
    run_date = run_date or dt.date.today().isoformat()
    n_runs = int(n_runs or cfg.get("n_runs", 10))
    prompts = cfg.get("prompts", [])
    if tier:
        prompts = [p for p in prompts if p.get("tier", "full") == tier or tier == "full"]
    if len(prompts) > MAX_PROMPTS:
        raise ValueError(f"Too many prompts: {len(prompts)} (max {MAX_PROMPTS}).")

    budget = int(cfg.get("monthly_call_budget", 10**9))
    used_this_month = month_to_date_calls(today=dt.date.fromisoformat(run_date))
    calls_remaining = max(0, budget - used_this_month)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RESULTS_DIR / f"{run_date}-raw.jsonl"

    results: list[dict] = []
    skipped: list[str] = []
    session = requests.Session()
    with raw_path.open("a", encoding="utf-8") as raw_fh:
        for p in prompts:
            already = sum(r["calls"] for r in results)
            if calls_remaining - already < 2:
                skipped.append(p["id"])
                continue
            r = run_prompt(p, cfg, api_key, session, raw_fh, n_runs=n_runs,
                           calls_remaining=calls_remaining - already,
                           run_date=run_date, progress=progress)
            results.append(r)

    append_history(results, run_date)

    total_calls = sum(r["calls"] for r in results)
    summary = {
        "run_date": run_date,
        "n_runs": n_runs,
        "tier": tier or "all",
        "engine": "serpapi google + google_ai_overview",
        "locale": cfg.get("defaults", {}),
        "prompts_run": len(results),
        "prompts_skipped": skipped,
        "total_calls": total_calls,
        "monthly_budget": budget,
        "calls_used_this_month": used_this_month + total_calls,
        "results": results,
    }
    xlsx = write_excel(summary, cfg)
    md = write_markdown(summary, cfg)
    summary["report_xlsx"] = str(xlsx)
    summary["report_md"] = str(md)
    summary["raw_jsonl"] = str(raw_path)
    return summary


# --- Reporting: Excel ------------------------------------------------------
def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def write_excel(summary: dict, cfg: dict) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    hdr_fill = PatternFill("solid", fgColor="0F766E")  # teal
    hdr_font = Font(bold=True, color="FFFFFF")
    green = PatternFill("solid", fgColor="DCFCE7")
    red = PatternFill("solid", fgColor="FEE2E2")
    bold = Font(bold=True)

    def style_header(ws, ncols, row=1):
        for c in range(1, ncols + 1):
            cell = ws.cell(row=row, column=c)
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = Alignment(vertical="center")
        ws.freeze_panes = ws.cell(row=row + 1, column=1)

    def autosize(ws, widths):
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w

    wb = Workbook()
    results = summary["results"]

    # Summary sheet
    ws = wb.active
    ws.title = "Summary"
    overall_runs = sum(r["runs"] for r in results)
    overall_aio = sum(r["aio_hits"] for r in results)
    overall_td = sum(r["thedent_hits"] for r in results)
    td_lo, td_hi = wilson_ci(overall_td, overall_runs)
    rows = [
        ("AIO Citation Probe — The Dent (thedent.co.th)", ""),
        ("Run date", summary["run_date"]),
        ("Engine", summary["engine"]),
        ("Locale", json.dumps(summary["locale"], ensure_ascii=False)),
        ("Runs cap (n_runs)", summary["n_runs"]),
        ("Tier", summary["tier"]),
        ("Prompts run", summary["prompts_run"]),
        ("Prompts skipped (budget)", ", ".join(summary["prompts_skipped"]) or "—"),
        ("Total SerpApi calls (this run)", summary["total_calls"]),
        ("Calls used this month / budget",
         f'{summary["calls_used_this_month"]} / {summary["monthly_budget"]}'),
        ("", ""),
        ("Overall AIO trigger rate", _pct(overall_aio / overall_runs if overall_runs else 0)),
        ("Overall The Dent citation rate",
         f"{_pct(overall_td / overall_runs if overall_runs else 0)} "
         f"(95% CI {_pct(td_lo)}–{_pct(td_hi)})"),
        ("", ""),
        ("Note", "Baseline snapshot. Site returns 403 to crawlers (see "
                 "2026-04-19-thedent-live-audit.md), so ~0% is expected pre-fix."),
        ("Accuracy", "Counts linked AIO references only. De-personalized, "
                     "country-level (Thailand) datacenter view; trust trends > absolute %."),
    ]
    for r_i, (k, v) in enumerate(rows, 1):
        ws.cell(row=r_i, column=1, value=k).font = bold
        ws.cell(row=r_i, column=2, value=v)
    ws.cell(row=1, column=1).font = Font(bold=True, size=14)
    autosize(ws, [34, 80])

    # By prompt
    ws = wb.create_sheet("By prompt")
    cols = ["Prompt ID", "Query", "Lang", "Runs", "AIO rate",
            "The Dent rate", "The Dent 95% CI", "Cited when AIO present",
            "Top cited domains"]
    ws.append(cols)
    for r in results:
        lo, hi = r["thedent_ci"]
        td_cell = _pct(r["thedent_rate"])
        ws.append([
            r["prompt_id"], r["query"], r["hl"], r["runs"], _pct(r["aio_rate"]),
            td_cell, f"{_pct(lo)}–{_pct(hi)}", _pct(r["thedent_rate_given_aio"]),
            ", ".join(f"{d} ({n})" for d, n in r["top_domains"][:3]) or "—",
        ])
        fill = green if r["thedent_rate"] > 0 else red
        ws.cell(row=ws.max_row, column=6).fill = fill
    style_header(ws, len(cols))
    autosize(ws, [18, 42, 6, 7, 10, 14, 16, 20, 46])

    # Competitor share of voice
    ws = wb.create_sheet("Competitor SoV")
    ws.append(["Domain", "Times cited (AIO-present runs)", "Is The Dent?"])
    agg: dict[str, int] = {}
    for r in results:
        for d, n in r["top_domains"]:
            agg[d] = agg.get(d, 0) + n
    target = cfg.get("target_domain", "thedent.co.th")
    for d, n in sorted(agg.items(), key=lambda kv: kv[1], reverse=True):
        ws.append([d, n, "YES" if domain_matches(d, target) else ""])
        if domain_matches(d, target):
            ws.cell(row=ws.max_row, column=1).fill = green
    style_header(ws, 3)
    autosize(ws, [40, 30, 12])

    # Raw runs
    ws = wb.create_sheet("Raw runs")
    ws.append(["Prompt ID", "Run", "UTC time", "Lang", "AIO present",
               "The Dent cited", "Cited domains", "Error"])
    for r in results:
        for run in r["raw_runs"]:
            ws.append([run["prompt_id"], run["run"], run["ts"], run["hl"],
                       run["aio_present"], run["thedent_cited"],
                       ", ".join(run["domains"]), run.get("error") or ""])
    style_header(ws, 8)
    autosize(ws, [18, 6, 22, 6, 12, 14, 50, 14])

    # Weekly trend
    ws = wb.create_sheet("Weekly trend")
    _build_trend_sheet(ws, style_header, autosize, green, red)

    out = REPORT_DIR / f"{summary['run_date']}-aio-citation-probe.xlsx"
    wb.save(out)
    return out


def _build_trend_sheet(ws, style_header, autosize, green, red) -> None:
    hist = read_history()
    if not hist:
        ws.append(["No history yet — run the probe at least twice to see trends."])
        return
    weeks = sorted({h["iso_week"] for h in hist})
    prompts = sorted({h["prompt_id"] for h in hist})
    by_key = {(h["prompt_id"], h["iso_week"]): h for h in hist}
    header = ["Prompt ID"] + weeks + ["Δ latest"]
    ws.append(header)
    for pid in prompts:
        row = [pid]
        series = []
        for w in weeks:
            rec = by_key.get((pid, w))
            if rec:
                series.append(rec["thedent_rate"])
                row.append(_pct(rec["thedent_rate"]))
            else:
                series.append(None)
                row.append("")
        vals = [v for v in series if v is not None]
        delta = ""
        if len(vals) >= 2:
            d = vals[-1] - vals[-2]
            delta = f"{d * 100:+.0f}pp"
        row.append(delta)
        ws.append(row)
    style_header(ws, len(header))
    autosize(ws, [18] + [10] * len(weeks) + [10])


# --- Reporting: Markdown ---------------------------------------------------
def write_markdown(summary: dict, cfg: dict) -> Path:
    results = summary["results"]
    overall_runs = sum(r["runs"] for r in results)
    overall_aio = sum(r["aio_hits"] for r in results)
    overall_td = sum(r["thedent_hits"] for r in results)
    td_lo, td_hi = wilson_ci(overall_td, overall_runs)

    lines = [
        f"# AIO Citation Probe — {summary['run_date']}",
        "",
        f"- **Engine:** {summary['engine']}",
        f"- **Locale:** `{json.dumps(summary['locale'], ensure_ascii=False)}`",
        f"- **Runs cap:** {summary['n_runs']} · **Tier:** {summary['tier']}",
        f"- **Prompts run:** {summary['prompts_run']}"
        + (f" · **skipped (budget):** {', '.join(summary['prompts_skipped'])}"
           if summary["prompts_skipped"] else ""),
        f"- **SerpApi calls this run:** {summary['total_calls']} · "
        f"**month-to-date / budget:** {summary['calls_used_this_month']} / "
        f"{summary['monthly_budget']}",
        "",
        f"**Overall AIO trigger rate:** {_pct(overall_aio / overall_runs if overall_runs else 0)}  ",
        f"**Overall The Dent citation rate:** "
        f"{_pct(overall_td / overall_runs if overall_runs else 0)} "
        f"(95% CI {_pct(td_lo)}–{_pct(td_hi)})",
        "",
        "## By prompt",
        "",
        "| Prompt | Lang | Runs | AIO rate | The Dent rate (95% CI) | When AIO present | Top cited domains |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lo, hi = r["thedent_ci"]
        top = ", ".join(f"{d} ({n})" for d, n in r["top_domains"][:3]) or "—"
        lines.append(
            f"| {r['query']} | {r['hl']} | {r['runs']} | {_pct(r['aio_rate'])} | "
            f"{_pct(r['thedent_rate'])} ({_pct(lo)}–{_pct(hi)}) | "
            f"{_pct(r['thedent_rate_given_aio'])} | {top} |")
    lines += [
        "",
        "## Caveats",
        "",
        "- **Baseline:** site returns 403 to crawlers (see "
        "`2026-04-19-thedent-live-audit.md`), so ~0% citation is expected pre-fix.",
        "- **Accuracy:** counts linked AIO references only; de-personalized, "
        "country-level (Thailand) datacenter view — trust trend direction over "
        "absolute %. Deltas inside the CI are sampling noise.",
        "- **Thai prompts** are first-draft and must be reviewed by a native "
        "speaker before relying on them (per CLAUDE.md).",
        "",
    ]
    out = REPORT_DIR / f"{summary['run_date']}-aio-citation-probe.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


# --- CLI -------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="AIO citation probe for thedent.co.th")
    ap.add_argument("--config", default=str(PROMPTS_PATH))
    ap.add_argument("--tier", choices=["core", "full"], default=None,
                    help="Run only prompts in this tier (full = all).")
    ap.add_argument("--n-runs", type=int, default=None, help="Override n_runs cap.")
    ap.add_argument("--smoke", action="store_true",
                    help="Smoke test: first prompt only, 1 run.")
    ap.add_argument("--yes", action="store_true", help="Skip cost confirmation.")
    args = ap.parse_args()

    api_key = os.environ.get("SERPAPI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: set SERPAPI_API_KEY in the environment.")
        return 2

    cfg = load_config(args.config)
    if args.smoke:
        cfg = {**cfg, "prompts": cfg["prompts"][:1]}
        args.n_runs = 1

    n_runs = args.n_runs or cfg.get("n_runs", 10)
    prompts = cfg["prompts"]
    if args.tier:
        prompts = [p for p in prompts if p.get("tier", "full") == args.tier
                   or args.tier == "full"]
    est_max = len(prompts) * n_runs * 2
    mtd = month_to_date_calls()
    budget = cfg.get("monthly_call_budget", "n/a")
    print(f"Prompts: {len(prompts)} | n_runs cap: {n_runs} | "
          f"est. max calls: {est_max}")
    print(f"Month-to-date calls: {mtd} | monthly budget: {budget}")
    if not args.yes and not args.smoke:
        if input("Proceed and spend SerpApi credits? [y/N] ").strip().lower() != "y":
            print("Aborted.")
            return 1

    def progress(pid, i, n, calls):
        print(f"  {pid}: run {i}/{n} (calls so far: {calls})", flush=True)

    summary = run_experiment(cfg, api_key, n_runs=args.n_runs, tier=args.tier,
                             progress=progress)
    print("\nDone.")
    print(f"  Excel:    {summary['report_xlsx']}")
    print(f"  Markdown: {summary['report_md']}")
    print(f"  Raw:      {summary['raw_jsonl']}")
    print(f"  Calls this run: {summary['total_calls']} | "
          f"month-to-date: {summary['calls_used_this_month']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
