"""Check how the weekly Search Console check sorts inspection results."""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from search_console_check import classify  # noqa: E402

NOW = datetime(2026, 11, 26, tzinfo=timezone.utc)
URL = "https://ailab.gc.cuny.edu/docs/stem-splitter/"


def status(**fields):
    return {"indexStatusResult": fields}


def main():
    assert classify(URL, status(verdict="PASS", googleCanonical=URL, userCanonical=URL), NOW) == (None, None)

    problem, _ = classify(URL, status(verdict="NEUTRAL", userCanonical=URL,
                                      googleCanonical="https://ailab.gc.cuny.edu/stem-splitter-docs/"), NOW)
    assert problem and "stem-splitter-docs" in problem

    assert classify(URL, status(verdict="FAIL", pageFetchState="NOT_FOUND"), NOW)[0] == "Fetch failed: NOT_FOUND"
    assert classify(URL, status(verdict="FAIL", pageFetchState="SOFT_404"), NOW)[0] == "Fetch failed: SOFT_404"
    assert "BLOCKED_BY_META_TAG" in classify(URL, status(verdict="FAIL", indexingState="BLOCKED_BY_META_TAG"), NOW)[0]

    # Not reached yet, or crawled recently: listed, no alert.
    assert classify(URL, status(verdict="NEUTRAL", coverageState="Discovered - currently not indexed"), NOW) == (
        None, "Discovered - currently not indexed")
    recent = status(verdict="NEUTRAL", coverageState="Crawled - currently not indexed",
                    lastCrawlTime="2026-11-24T04:00:00Z")
    assert classify(URL, recent, NOW) == (None, "Crawled - currently not indexed (crawled 2026-11-24)")

    # Crawled more than 30 days ago and still left out: alert.
    stale = status(verdict="NEUTRAL", coverageState="Crawled - currently not indexed",
                   lastCrawlTime="2026-10-01T04:00:00Z")
    assert classify(URL, stale, NOW)[0] == "Crawled - currently not indexed since a crawl on 2026-10-01"
    print("PASS Search Console classification")


if __name__ == "__main__":
    main()
