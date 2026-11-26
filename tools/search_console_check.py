"""Weekly Search Console check for the pages in the live sitemap.

Asks the URL Inspection API about every sitemap URL and reports only problems
the site can fix: a different Google-selected canonical, a failed fetch, a
noindex or robots block, or a page Google crawled long ago and still left out.
Pages Google has not reached yet are listed for information only. Addresses
outside the sitemap (trailing-slash redirects, truncated links posted
elsewhere, query-string variants) are never inspected, so they never alert.

Reads an OAuth access token with the webmasters.readonly scope from
SEARCH_CONSOLE_TOKEN. Writes a Markdown report to the path given as the first
argument and exits 3 when something needs attention (other failures exit 1).
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

SITE = "https://ailab.gc.cuny.edu/"
SITEMAP = SITE + "sitemap-0.xml"
INSPECT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SITEMAPS = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps"
STALE_AFTER = timedelta(days=30)

FETCH_OK = {"SUCCESSFUL", "PAGE_FETCH_STATE_UNSPECIFIED", None}
INDEXING_OK = {"INDEXING_ALLOWED", "INDEXING_STATE_UNSPECIFIED", None}
ROBOTS_OK = {"ALLOWED", "ROBOTS_TXT_STATE_UNSPECIFIED", None}


def classify(url, result, now):
    """Return (problem or None, waiting note or None) for one inspection result."""
    status = result.get("indexStatusResult", {})
    coverage = status.get("coverageState", "unknown")
    google = status.get("googleCanonical")
    user = status.get("userCanonical")
    if google and user and google != user:
        return f"Google chose {google} as canonical instead of the declared {user}", None
    if status.get("pageFetchState") not in FETCH_OK:
        return f"Fetch failed: {status['pageFetchState']}", None
    if status.get("indexingState") not in INDEXING_OK:
        return f"Indexing blocked: {status['indexingState']}", None
    if status.get("robotsTxtState") not in ROBOTS_OK:
        return f"robots.txt: {status['robotsTxtState']}", None
    if status.get("verdict") == "PASS":
        return None, None
    crawled = status.get("lastCrawlTime")
    if crawled:
        when = datetime.fromisoformat(crawled.replace("Z", "+00:00"))
        if now - when > STALE_AFTER:
            return f"{coverage} since a crawl on {when:%Y-%m-%d}", None
        return None, f"{coverage} (crawled {when:%Y-%m-%d})"
    return None, coverage


def call(url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, headers={"Authorization": f"Bearer {token}",
                                               "Content-Type": "application/json"})
    with urlopen(request, timeout=60) as response:
        return json.load(response)


def sitemap_urls():
    with urlopen(SITEMAP, timeout=60) as response:
        return sorted(re.findall(r"<loc>([^<]+)</loc>", response.read().decode()))


def main():
    report_path = sys.argv[1]
    token = os.environ["SEARCH_CONSOLE_TOKEN"]
    now = datetime.now(timezone.utc)
    problems, waiting = [], []

    for sitemap in call(SITEMAPS.format(site=quote(SITE, safe="")), token).get("sitemap", []):
        if int(sitemap.get("errors", 0)):
            problems.append((sitemap["path"], f"Sitemap has {sitemap['errors']} errors"))

    urls = sitemap_urls()
    for url in urls:
        result = call(INSPECT, token, {"inspectionUrl": url, "siteUrl": SITE})["inspectionResult"]
        problem, note = classify(url, result, now)
        if problem:
            problems.append((url, problem))
        elif note:
            waiting.append((url, note))
        time.sleep(0.2)  # stay well under 600 requests a minute

    lines = [f"Checked {len(urls)} sitemap URLs on {now:%Y-%m-%d}.", ""]
    if problems:
        lines += ["## Needs attention", "", "| Page | Problem |", "|---|---|"]
        lines += [f"| {url} | {text} |" for url, text in problems]
        lines += ["", "Fix the site, then use **Validate fix** in Search Console's Page indexing report.", ""]
    else:
        lines += ["Nothing needs attention.", ""]
    if waiting:
        lines += [f"<details><summary>{len(waiting)} pages Google has not indexed yet (no action)</summary>",
                  "", *[f"- {url}: {note}" for url, note in waiting], "", "</details>"]
    with open(report_path, "w") as report:
        report.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(3 if problems else 0)


if __name__ == "__main__":
    main()
