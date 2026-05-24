"""
helpers.py — Minimal Python utilities for the JIRA Failure Intelligence Pipeline.

This is the ONLY Python file in the project. It provides HTML fetching and
BeautifulSoup-based parsing that AI agents can invoke via `run_command`.

Usage:
    python helpers.py parse <path_or_url>        — Parse HTML report, output JSON
    python helpers.py banners <path_or_url>      — Extract banners only
    python helpers.py logs <path_or_url>         — Extract linked log paths only
    python helpers.py failed <path_or_url>       — Extract failed test cases only
"""

import json
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 is required. Install with: pip install beautifulsoup4 lxml")
    sys.exit(1)


# ---------------------------------------------------------------------------
# HTML Loading
# ---------------------------------------------------------------------------

def load_html(source: str) -> str:
    """Load HTML from a local file path or URL."""
    if source.startswith("http://") or source.startswith("https://"):
        try:
            import requests
            resp = requests.get(source, timeout=30)
            resp.raise_for_status()
            return resp.text
        except ImportError:
            print("ERROR: requests is required for URLs. Install with: pip install requests")
            sys.exit(1)
    else:
        path = Path(source)
        if not path.exists():
            print(f"ERROR: File not found: {source}")
            sys.exit(1)
        text = path.read_text(encoding="utf-8")
        # Handle markdown-wrapped HTML (```html ... ```)
        match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text


# ---------------------------------------------------------------------------
# Banner Parsing
# ---------------------------------------------------------------------------

def parse_banner_text(banner_text: str) -> dict:
    """
    Parse a banner string like:
        STEP=1 | MODULE=AUTHENTICATION | ACTION=OPEN_LOGIN_PAGE | USER=test_user
    into a dict:
        {"STEP": "1", "MODULE": "AUTHENTICATION", "ACTION": "OPEN_LOGIN_PAGE", "USER": "test_user"}
    """
    result = {}
    parts = [p.strip() for p in banner_text.split("|")]
    for part in parts:
        if "=" in part:
            key, _, value = part.partition("=")
            result[key.strip()] = value.strip()
    return result


def extract_banners(html: str) -> list[dict]:
    """Extract all banners from the HTML report."""
    soup = BeautifulSoup(html, "html.parser")
    banners = []
    for header in soup.select(".banner-header"):
        # The banner text is in the first <span> child
        span = header.find("span")
        if span:
            raw = span.get_text(strip=True)
            parsed = parse_banner_text(raw)
            parsed["_raw"] = raw
            banners.append(parsed)
    return banners


# ---------------------------------------------------------------------------
# Log Entry Extraction
# ---------------------------------------------------------------------------

def extract_log_entries(banner_content_div) -> list[dict]:
    """Extract structured log entries from a banner-content div."""
    entries = []
    for log_div in banner_content_div.select(".log-entry"):
        classes = [c for c in log_div.get("class", []) if c != "log-entry"]
        level = classes[0] if classes else "UNKNOWN"
        text = log_div.get_text(strip=True)
        # Parse timestamp from format: "10:01:07.500 | ERROR | Assertion failed"
        ts_match = re.match(r"^([\d:.]+)\s*\|\s*(\w+)\s*\|\s*(.*)", text)
        if ts_match:
            entries.append({
                "timestamp": ts_match.group(1),
                "level": ts_match.group(2),
                "message": ts_match.group(3).strip(),
            })
        else:
            entries.append({"timestamp": None, "level": level, "message": text})
    return entries


# ---------------------------------------------------------------------------
# Traceback Extraction
# ---------------------------------------------------------------------------

def extract_traceback(banner_content_div) -> str | None:
    """Extract traceback text from a banner-content div, if present."""
    tb_div = banner_content_div.select_one(".traceback")
    if tb_div:
        return tb_div.get_text(strip=False).strip()
    return None


# ---------------------------------------------------------------------------
# Test Case Parsing
# ---------------------------------------------------------------------------

def parse_test_case(test_case_div) -> dict:
    """Parse a single test-case div into structured data."""
    classes = test_case_div.get("class", [])
    status = "FAIL" if "FAIL" in classes else "PASS" if "PASS" in classes else "UNKNOWN"

    # Test header: "TEST FAILED :: test_login_invalid_password"
    header_div = test_case_div.select_one(".test-header")
    header_text = header_div.get_text(strip=True) if header_div else ""
    test_name = header_text.split("::")[-1].strip() if "::" in header_text else header_text

    # Metadata
    metadata_div = test_case_div.select_one(".metadata")
    metadata = {}
    if metadata_div:
        meta_text = metadata_div.get_text(separator="\n", strip=True)
        for line in meta_text.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                metadata[key.strip()] = val.strip()

    # Banners with their log entries
    steps = []
    for banner_div in test_case_div.select(".collapsible-banner"):
        banner_header = banner_div.select_one(".banner-header")
        banner_content = banner_div.select_one(".banner-content")

        step = {}
        if banner_header:
            span = banner_header.find("span")
            if span:
                raw = span.get_text(strip=True)
                step = parse_banner_text(raw)
                step["_raw"] = raw

        if banner_content:
            step["log_entries"] = extract_log_entries(banner_content)
            traceback = extract_traceback(banner_content)
            if traceback:
                step["traceback"] = traceback

            # Also capture any metadata within the banner content (e.g. inspect info)
            inner_meta = banner_content.select_one(".metadata")
            if inner_meta:
                step["inspect_info"] = inner_meta.get_text(separator="\n", strip=True)

        steps.append(step)

    return {
        "test_name": test_name,
        "status": status,
        "metadata": metadata,
        "steps": steps,
    }


# ---------------------------------------------------------------------------
# Summary Extraction
# ---------------------------------------------------------------------------

def extract_summary(soup: BeautifulSoup) -> dict:
    """Extract the execution summary table."""
    summary = {}
    summary_div = soup.select_one(".summary")
    if summary_div:
        for row in summary_div.select("tr"):
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                summary[th.get_text(strip=True)] = td.get_text(strip=True)
    return summary


# ---------------------------------------------------------------------------
# Raw Logs Extraction
# ---------------------------------------------------------------------------

def extract_raw_logs(soup: BeautifulSoup) -> str | None:
    """Extract captured raw logs from the <pre> block."""
    for div in soup.select(".summary"):
        h2 = div.select_one("h2")
        if h2 and "raw log" in h2.get_text(strip=True).lower():
            pre = div.select_one("pre")
            if pre:
                return pre.get_text(strip=False).strip()
    return None


# ---------------------------------------------------------------------------
# Pytest Hook Timeline
# ---------------------------------------------------------------------------

def extract_hook_timeline(soup: BeautifulSoup) -> list[dict]:
    """Extract the pytest hook timeline table."""
    hooks = []
    for div in soup.select(".summary"):
        h2 = div.select_one("h2")
        if h2 and "hook" in h2.get_text(strip=True).lower():
            rows = div.select("tr")
            for row in rows[1:]:  # skip header row
                cells = row.select("td")
                if len(cells) >= 3:
                    hooks.append({
                        "timestamp": cells[0].get_text(strip=True),
                        "hook": cells[1].get_text(strip=True),
                        "status": cells[2].get_text(strip=True),
                    })
    return hooks


# ---------------------------------------------------------------------------
# Full Report Parsing
# ---------------------------------------------------------------------------

def parse_report(html: str) -> dict:
    """Parse a full HTML report into structured JSON."""
    soup = BeautifulSoup(html, "html.parser")

    test_cases = []
    for tc_div in soup.select(".test-case"):
        test_cases.append(parse_test_case(tc_div))

    return {
        "summary": extract_summary(soup),
        "test_cases": test_cases,
        "raw_logs": extract_raw_logs(soup),
        "hook_timeline": extract_hook_timeline(soup),
    }


def extract_failed_tests(html: str) -> list[dict]:
    """Parse only the failed test cases."""
    soup = BeautifulSoup(html, "html.parser")
    failed = []
    for tc_div in soup.select(".test-case.FAIL"):
        failed.append(parse_test_case(tc_div))
    return failed


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    source = sys.argv[2]
    html = load_html(source)

    if command == "parse":
        result = parse_report(html)
    elif command == "banners":
        result = extract_banners(html)
    elif command == "logs":
        # Extract linked log paths (href attributes) — may not exist in all reports
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.select("a[href]"):
            href = a["href"]
            if any(href.endswith(ext) for ext in (".log", ".txt", ".out")):
                links.append(href)
        result = links
    elif command == "failed":
        result = extract_failed_tests(html)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
