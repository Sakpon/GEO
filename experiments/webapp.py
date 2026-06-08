#!/usr/bin/env python3
"""Auth-gated, mobile-friendly web UI for the AIO citation probe.

Log in (HTTP Basic Auth), enter prompts in the form, run the experiment as a
background job, watch progress, view week-over-week trends, and download the
Excel/Markdown reports.

    SERPAPI_API_KEY=... python webapp.py        # binds 0.0.0.0:8000

Credentials come from env (defaults: thedent / admin2026):
    BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD
Basic Auth is unencrypted without HTTPS and the default password is weak —
change it before any real exposure.
"""
from __future__ import annotations

import datetime as dt
import os
import secrets
import threading
import uuid
from functools import wraps
from pathlib import Path

from flask import (Flask, Response, abort, redirect, render_template, request,
                   send_from_directory, url_for)

import aio_citation_probe as probe

app = Flask(__name__)

AUTH_USER = os.environ.get("BASIC_AUTH_USERNAME", "thedent")
AUTH_PASS = os.environ.get("BASIC_AUTH_PASSWORD", "admin2026")

# In-memory job registry: job_id -> {status, progress, ...}. Results persist on
# disk regardless; only live job state is lost on restart.
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


# --- Auth ------------------------------------------------------------------
def check_auth(auth) -> bool:
    return bool(auth) and secrets.compare_digest(auth.username or "", AUTH_USER) \
        and secrets.compare_digest(auth.password or "", AUTH_PASS)


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not check_auth(request.authorization):
            return Response(
                "Authentication required.", 401,
                {"WWW-Authenticate": 'Basic realm="The Dent AIO Audit"'})
        return f(*args, **kwargs)
    return wrapper


# --- Helpers ---------------------------------------------------------------
def parse_prompts(text: str) -> list[dict]:
    """Parse the textarea: one prompt per line, optional `| hl` suffix.

        Best dental implant clinic in Bangkok | en
        คลินิกรากฟันเทียมที่ดีที่สุดในกรุงเทพ | th
    """
    prompts = []
    for i, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        hl = "en"
        q = line
        if "|" in line:
            q, _, tail = line.rpartition("|")
            q = q.strip()
            tail = tail.strip().lower()
            if tail in ("en", "th"):
                hl = tail
            else:  # the bar wasn't a locale marker — keep whole line
                q = line
        prompts.append({"id": f"p{i:02d}-{hl}", "q": q, "hl": hl, "tier": "core"})
    return prompts


def default_prompts_text() -> str:
    try:
        cfg = probe.load_config()
    except Exception:
        return ""
    return "\n".join(f'{p["q"]} | {p.get("hl", "en")}' for p in cfg["prompts"])


def list_reports() -> list[dict]:
    out = []
    if probe.REPORT_DIR.exists():
        for f in sorted(probe.REPORT_DIR.glob("*-aio-citation-probe.*"),
                        reverse=True):
            if f.suffix in (".xlsx", ".md"):
                out.append({"name": f.name, "kind": f.suffix.lstrip("."),
                            "size_kb": max(1, f.stat().st_size // 1024)})
    return out


def trend_table() -> dict:
    hist = probe.read_history()
    weeks = sorted({h["iso_week"] for h in hist})
    prompts = sorted({h["prompt_id"] for h in hist})
    by_key = {(h["prompt_id"], h["iso_week"]): h for h in hist}
    rows = []
    for pid in prompts:
        series, cells = [], []
        for w in weeks:
            rec = by_key.get((pid, w))
            val = rec["thedent_rate"] if rec else None
            series.append(val)
            cells.append(None if val is None else round(val * 100))
        vals = [(i, v) for i, v in enumerate(series) if v is not None]
        delta, noise = None, False
        if len(vals) >= 2:
            (_, prev), (_, last) = vals[-2], vals[-1]
            delta = round((last - prev) * 100)
            r_last = by_key[(pid, weeks[vals[-1][0]])]
            r_prev = by_key[(pid, weeks[vals[-2][0]])]
            # within-noise if the two CIs overlap
            noise = not (r_last["thedent_ci_low"] > r_prev["thedent_ci_high"]
                         or r_prev["thedent_ci_low"] > r_last["thedent_ci_high"])
        rows.append({"pid": pid, "cells": cells, "delta": delta, "noise": noise,
                     "spark": sparkline([v for v in series if v is not None])})
    return {"weeks": weeks, "rows": rows}


def sparkline(values: list[float], w: int = 120, h: int = 28) -> str:
    """Tiny responsive inline SVG sparkline (rates 0..1)."""
    if not values:
        return ""
    if len(values) == 1:
        values = values * 2
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = (i / (n - 1)) * (w - 4) + 2
        y = h - 2 - max(0.0, min(1.0, v)) * (h - 4)
        pts.append(f"{x:.1f},{y:.1f}")
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" '
            f'class="spark" role="img" aria-label="trend">'
            f'<polyline points="{" ".join(pts)}" fill="none" '
            f'stroke="#0f766e" stroke-width="2" /></svg>')


# --- Job runner ------------------------------------------------------------
def start_job(prompts: list[dict], n_runs: int) -> str:
    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "running", "label": "", "done": 0,
                        "total": len(prompts), "calls": 0, "summary": None,
                        "error": None,
                        "started": dt.datetime.now().strftime("%H:%M:%S")}

    api_key = os.environ.get("SERPAPI_API_KEY", "").strip()
    cfg = {**probe.load_config(), "prompts": prompts}

    def progress(pid, i, n, calls):
        with JOBS_LOCK:
            j = JOBS[job_id]
            j["label"] = f"{pid} — run {i}/{n}"
            j["calls"] = calls

    def worker():
        try:
            done_ids: set[str] = set()

            def prog_wrap(pid, i, n, calls):
                progress(pid, i, n, calls)
                if i == n or pid not in done_ids:
                    done_ids.add(pid)
                    with JOBS_LOCK:
                        JOBS[job_id]["done"] = len(done_ids)

            summary = probe.run_experiment(cfg, api_key, n_runs=n_runs,
                                           progress=prog_wrap)
            with JOBS_LOCK:
                JOBS[job_id].update(status="done", summary=summary,
                                    done=summary["prompts_run"])
        except Exception as exc:  # surface failure to the UI
            with JOBS_LOCK:
                JOBS[job_id].update(status="error", error=str(exc))

    threading.Thread(target=worker, daemon=True).start()
    return job_id


# --- Routes ----------------------------------------------------------------
@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/")
@require_auth
def index():
    cfg = probe.load_config()
    return render_template(
        "index.html",
        prompts_text=default_prompts_text(),
        n_runs=cfg.get("n_runs", 10),
        budget=cfg.get("monthly_call_budget", "n/a"),
        used=probe.month_to_date_calls(),
        max_prompts=probe.MAX_PROMPTS,
        reports=list_reports(),
        api_key_set=bool(os.environ.get("SERPAPI_API_KEY", "").strip()),
    )


@app.route("/run", methods=["POST"])
@require_auth
def run():
    if not os.environ.get("SERPAPI_API_KEY", "").strip():
        abort(400, "SERPAPI_API_KEY is not set on the server.")
    if not request.form.get("confirm"):
        abort(400, "Please confirm the cost before running.")
    prompts = parse_prompts(request.form.get("prompts", ""))
    if not prompts:
        abort(400, "Enter at least one prompt.")
    if len(prompts) > probe.MAX_PROMPTS:
        abort(400, f"Too many prompts (max {probe.MAX_PROMPTS}).")
    try:
        n_runs = max(1, min(50, int(request.form.get("n_runs", 10))))
    except ValueError:
        n_runs = 10
    job_id = start_job(prompts, n_runs)
    return redirect(url_for("job_status", job_id=job_id))


@app.route("/jobs/<job_id>")
@require_auth
def job_status(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        abort(404)
    return render_template("job.html", job=job, job_id=job_id)


@app.route("/trends")
@require_auth
def trends():
    return render_template("trends.html", trend=trend_table())


@app.route("/download/<path:filename>")
@require_auth
def download(filename):
    # Restrict strictly to the reports directory (no traversal).
    name = Path(filename).name
    if name != filename:
        abort(404)
    target = (probe.REPORT_DIR / name).resolve()
    if probe.REPORT_DIR.resolve() not in target.parents or not target.exists():
        abort(404)
    return send_from_directory(probe.REPORT_DIR, name, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
