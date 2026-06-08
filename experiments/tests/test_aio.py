#!/usr/bin/env python3
"""Test suite for the AIO citation probe — no network, no API credits.

Run from the experiments/ directory:  python tests/test_aio.py
Exits non-zero on the first failure (used by CI).
"""
from __future__ import annotations

import datetime as dt
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import aio_citation_probe as p  # noqa: E402


def test_wilson_ci():
    assert p.wilson_ci(0, 0) == (0.0, 1.0)
    lo, hi = p.wilson_ci(0, 6)
    assert lo < 1e-9 and 0.37 < hi < 0.41, (lo, hi)
    assert 0.18 < p.ci_halfwidth(0, 6) < 0.21
    assert p.ci_halfwidth(0, 16) <= 0.10          # decisive-zero settles ~16 runs
    lo, hi = p.wilson_ci(5, 10)
    assert lo < 0.5 < hi


def test_url_helpers():
    assert p.host_of("https://www.thedent.co.th/implants") == "thedent.co.th"
    assert p.host_of("bidc.com") == "bidc.com"
    assert p.host_of("") == ""
    assert p.domain_matches("thedent.co.th", "thedent.co.th")
    assert p.domain_matches("blog.thedent.co.th", "thedent.co.th")
    assert not p.domain_matches("notthedent.co.th", "thedent.co.th")
    assert not p.domain_matches("bidc.com", "thedent.co.th")


def test_extract_references():
    aio = {"references": [{"link": "https://thedent.co.th/x"},
                          {"link": "https://bidc.com/y", "source": "BIDC"}]}
    refs = p.extract_references(aio)
    assert len(refs) == 2 and refs[0]["link"].endswith("/x")
    assert p.extract_references({}) == []


def _mock_provider():
    """SerpApi mock: implants -> inline AIO citing The Dent (1 call),
    veneers -> page_token flow citing a competitor (2 calls),
    other -> no AIO (1 call)."""
    def fake_get(params, session, **kw):
        if params.get("engine") == "google_ai_overview":
            return {"ai_overview": {"references": [{"link": "https://bidc.com/a"}]}}, True
        q = params.get("q", "")
        if "implant" in q:
            return {"ai_overview": {"text_blocks": [{}], "references": [
                {"link": "https://www.thedent.co.th/implants"},
                {"link": "https://bidc.com/b"}]}}, True
        if "veneer" in q:
            return {"ai_overview": {"page_token": "T"}}, True
        return {"organic_results": []}, True
    return fake_get


def _cfg():
    return {
        "n_runs": 4, "min_runs": 2, "ci_halfwidth_target": 0.10,
        "monthly_call_budget": 1000, "throttle_seconds": 0,
        "target_domain": "thedent.co.th",
        "defaults": {"location": "Thailand", "gl": "th",
                     "google_domain": "google.co.th", "no_cache": True},
        "prompts": [
            {"id": "implants-en", "q": "best dental implant clinic", "hl": "en", "tier": "core"},
            {"id": "veneers-en", "q": "veneer cost thailand", "hl": "en", "tier": "core"},
            {"id": "checkup-en", "q": "dental checkup bangkok", "hl": "en", "tier": "full"},
        ],
    }


def _isolate(tmp):
    p.RESULTS_DIR = tmp / "r"; p.RESULTS_DIR.mkdir()
    p.REPORT_DIR = tmp / "o"; p.REPORT_DIR.mkdir()
    p.HISTORY_PATH = p.RESULTS_DIR / "history.jsonl"
    p.serpapi_get = _mock_provider()


def test_run_experiment_and_reports():
    from openpyxl import load_workbook
    with tempfile.TemporaryDirectory() as td:
        _isolate(pathlib.Path(td))
        s = p.run_experiment(_cfg(), "FAKE", run_date="2026-06-08")
        b = {r["prompt_id"]: r for r in s["results"]}
        assert b["implants-en"]["thedent_rate"] == 1.0
        assert b["veneers-en"]["thedent_rate"] == 0.0
        assert b["veneers-en"]["aio_rate"] == 1.0       # page_token => AIO present
        assert b["checkup-en"]["aio_rate"] == 0.0       # no AIO
        assert s["total_calls"] == 16                   # 4 + 8 + 4
        assert s["calls_used_this_month"] == 16
        # competitor share-of-voice surfaces the competitor
        agg = {}
        for r in s["results"]:
            for d, n in r["top_domains"]:
                agg[d] = agg.get(d, 0) + n
        assert agg.get("bidc.com", 0) > 0
        # workbook has all sheets
        wb = load_workbook(s["report_xlsx"])
        assert wb.sheetnames == ["Summary", "By prompt", "Competitor SoV",
                                 "Raw runs", "Weekly trend"]
        assert pathlib.Path(s["report_md"]).exists()


def test_month_accumulates_and_trends():
    with tempfile.TemporaryDirectory() as td:
        _isolate(pathlib.Path(td))
        p.run_experiment(_cfg(), "FAKE", run_date="2026-06-08")
        s2 = p.run_experiment(_cfg(), "FAKE", run_date="2026-06-15")
        assert s2["calls_used_this_month"] == 32
        hist = p.read_history()
        assert len({h["date"] for h in hist}) == 2
        assert p.month_to_date_calls(today=dt.date(2026, 6, 8)) == 32


def test_budget_guard():
    with tempfile.TemporaryDirectory() as td:
        _isolate(pathlib.Path(td))
        p.run_experiment(_cfg(), "FAKE", run_date="2026-06-08")
        p.run_experiment(_cfg(), "FAKE", run_date="2026-06-15")
        mtd = p.month_to_date_calls(today=dt.date(2026, 6, 8))
        s3 = p.run_experiment({**_cfg(), "monthly_call_budget": mtd + 3},
                              "FAKE", run_date="2026-06-08")
        assert s3["prompts_skipped"] == ["veneers-en", "checkup-en"]
        assert s3["total_calls"] <= 3


def test_max_prompts_guard():
    cfg = _cfg()
    cfg["prompts"] = [{"id": f"p{i}", "q": "x", "hl": "en"} for i in range(31)]
    try:
        p.run_experiment(cfg, "FAKE", run_date="2026-06-08")
    except ValueError:
        return
    raise AssertionError("expected ValueError for >30 prompts")


def test_webapp_routes():
    import base64
    import os
    import time
    os.environ["SERPAPI_API_KEY"] = "FAKE"
    import webapp
    webapp.probe.serpapi_get = _mock_provider()
    with tempfile.TemporaryDirectory() as td:
        _isolate(pathlib.Path(td))
        webapp.probe.RESULTS_DIR = p.RESULTS_DIR
        webapp.probe.REPORT_DIR = p.REPORT_DIR
        webapp.probe.HISTORY_PATH = p.HISTORY_PATH
        c = webapp.app.test_client()
        auth = {"Authorization": "Basic " + base64.b64encode(b"thedent:admin2026").decode()}
        bad = {"Authorization": "Basic " + base64.b64encode(b"x:y").decode()}
        assert c.get("/healthz").status_code == 200
        assert c.get("/").status_code == 401
        assert c.get("/", headers=bad).status_code == 401
        assert c.get("/", headers=auth).status_code == 200
        assert c.get("/trends", headers=auth).status_code == 200
        assert c.get("/download/../CLAUDE.md", headers=auth).status_code == 404
        assert c.get("/download/missing.xlsx", headers=auth).status_code == 404
        assert c.post("/run", headers=auth,
                      data={"prompts": "q | en", "n_runs": "2"}).status_code == 400
        many = "\n".join(f"q{i} | en" for i in range(31))
        assert c.post("/run", headers=auth,
                      data={"prompts": many, "n_runs": "1", "confirm": "on"}).status_code == 400
        pr = webapp.parse_prompts("Best implant clinic | en\nรากฟันเทียม | th\nplain line")
        assert pr[0]["hl"] == "en" and pr[1]["hl"] == "th" and pr[2]["hl"] == "en"
        assert pr[2]["q"] == "plain line"
        # full mocked run -> background job -> download link appears
        resp = c.post("/run", headers=auth, data={
            "prompts": "best dental implant clinic | en", "n_runs": "2", "confirm": "on"})
        assert resp.status_code == 302
        job_url = resp.headers["Location"]
        for _ in range(50):
            jr = c.get(job_url, headers=auth)
            if b"Download Excel" in jr.data or b"failed" in jr.data:
                break
            time.sleep(0.1)
        assert b"Download Excel" in jr.data


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {t.__name__}: {exc!r}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
