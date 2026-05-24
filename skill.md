---
description: Analyze a pytest HTML test report and generate a JIRA bug draft
---

# JIRA Failure Intelligence — Bug Draft Workflow

When the user provides an HTML test report (file path or URL), follow these steps to analyze test failures and produce a structured JIRA bug draft.

## Prerequisites

- Python 3.11+ with `beautifulsoup4` and `lxml` installed
- The `helpers.py` file in the project root
- The prompt files in `prompts/` directory

---

## Step 1: Receive and Validate Input

The user will provide one of:
- A **local file path** to an HTML report (e.g., `sample_1.html`)
- A **URL** to an HTML report

**Action:**
1. Confirm the file exists (for local paths) or is accessible (for URLs)
2. Read the file to confirm it contains HTML test report content
3. If the file is not valid HTML or contains no test data, inform the user and stop

---

## Step 2: Extract Data from HTML Report

**Reference:** Read `prompts/html_extraction.md` for detailed parsing rules.

**Action:**
1. Run the helper to get structured data:
   ```bash
   python helpers.py parse <path_to_html>
   ```
2. Review the JSON output. Identify:
   - How many tests total, how many failed
   - Which test cases have `status: "FAIL"`
3. If no failures are found, inform the user: "No failed tests found in this report" and stop
4. For each **failed** test case, collect:
   - Test name, module, class, function, start time
   - All banner steps (in order) with their key-value pairs
   - All log entries under each banner (especially ERROR, WARNING, CHECKPOINT levels)
   - Traceback content (verbatim)
   - Inspect information if present

**If `helpers.py` output is insufficient** (e.g., report structure differs from expected), read the HTML directly and manually extract the same fields following the rules in `prompts/html_extraction.md`.

---

## Step 3: Extract Linked Log Evidence

**Reference:** Read `prompts/log_extraction.md` for detailed instructions.

**Action:**
1. Check if the HTML report contains linked log file paths (look for `<a href="*.log">` or similar)
2. Run the helper to discover log links:
   ```bash
   python helpers.py logs <path_to_html>
   ```
3. If linked logs exist:
   - Open each log file
   - Search for sections relevant to the failure (using timestamps and error keywords from Step 2)
   - Extract relevant snippets with ±20 lines of context
   - Maximum 50 lines per snippet
4. If no linked logs exist (all logs are inline in the HTML), note: "All log evidence is inline in the HTML report" and use the log entries already extracted in Step 2

---

## Step 4: Compile Test Context

**Action:** Synthesize the data from Steps 2 and 3 into a structured summary:

1. **Test Steps** — Read the banners in order. Convert each `ACTION` value into a human-readable step description. Example:
   - Banner: `STEP=1 | MODULE=AUTHENTICATION | ACTION=OPEN_LOGIN_PAGE`
   - Step: "1. Open the login page"
   - Mark the failing step with **[FAILED]**

2. **Module** — From the `MODULE` key in banners or from test metadata

3. **Version** — From the `VERSION` key in banners, or metadata, or "unknown"

4. **DUT** — From the `DUT` key in banners, or metadata, or "unknown"

5. **Failure Timeline** — Order all relevant log entries chronologically:
   ```
   10:01:05.100 — Login page opened
   10:01:06.800 — Form submitted
   10:01:07.200 — WARNING: Unexpected redirect
   10:01:07.500 — ERROR: Assertion failed
   ```

6. **Failure Point** — Identify which step failed and the root error from traceback

---

## Step 5: Generate JIRA Draft

**Reference:** Read `prompts/draft_generation.md` for the exact template and rules.
**Reference:** Read `prompts/examples.md` for a complete input→output example.

**Action:**
1. Generate `jira_draft.md` using the template from `prompts/draft_generation.md`
2. Generate `jira_draft.json` with the structured data
3. Save both files in the project directory
4. **Present the `jira_draft.md` contents to the user for review**

---

## Step 6: Engineer Review

**Action:**
1. Show the draft to the user
2. Ask: "Would you like to edit anything before creating the JIRA ticket?"
3. If the user requests changes, apply them to both `jira_draft.md` and `jira_draft.json`
4. If the user approves, proceed to Step 7
5. If the user rejects, stop and discard the draft

---

## Step 7: JIRA Creation (Future — MCP Harness)

> **Note:** The JIRA MCP server is not yet implemented. This step is a placeholder.

**When MCP becomes available:**
1. Read `jira_draft.json`
2. Call the JIRA MCP server to create the issue:
   - Set title, description, priority, component, labels, environment
   - Attach log evidence files if they exist
3. Return the created ticket key to the user (e.g., `FW-2041`)

**Until then:**
1. Inform the user: "JIRA MCP is not yet configured. The draft files are ready:"
2. Point them to:
   - `jira_draft.md` — human-readable draft
   - `jira_draft.json` — structured data for future MCP use

---

## Error Handling

- **HTML file not found** → Inform user, ask for correct path
- **No failures in report** → Inform user, stop gracefully
- **Linked log not found** → Note as missing, continue with available evidence
- **helpers.py not installed** → Read HTML directly as fallback, warn user about missing dependency
- **Banner format differs** → Fall back to reading HTML directly, adapt parsing
- **Version/DUT not found** → Set to "unknown", continue

---

## Quick Reference: File Locations

| File | Purpose |
|------|---------|
| `helpers.py` | Python HTML parser — run via CLI |
| `prompts/html_extraction.md` | How to parse the HTML structure |
| `prompts/log_extraction.md` | How to analyze linked log files |
| `prompts/draft_generation.md` | JIRA draft template and rules |
| `prompts/examples.md` | Complete input→output example |
| `configs/config.yaml` | JIRA project defaults |
