# HTML Extraction Instructions

You are extracting structured data from a pytest-based HTML test report.

## HTML Report Structure

The HTML reports have this structure (elements may vary slightly between reports):

### 1. Execution Summary
- Located in a `div.summary` containing an `<h2>Execution Summary</h2>` and a `<table>`
- Fields: Suite, Execution Time, Total Tests, Passed, Failed, Environment

### 2. Test Cases
- Each test is inside a `div.test-case` with a class of `PASS`, `FAIL`, or similar
- **Test header**: `div.test-header` containing text like `TEST FAILED :: test_name`
- **Metadata**: `div.metadata` containing `Module:`, `Class:`, `Function:`, `Start Time:` (line-separated with `<br>`)

### 3. Banners (Critical)
- Inside each test case: `div.collapsible-banner` elements
- Each banner has a `div.banner-header` with a `<span>` containing pipe-separated key-value pairs:
  ```
  STEP=1 | MODULE=AUTHENTICATION | ACTION=OPEN_LOGIN_PAGE | USER=test_user
  ```
- Common keys: `STEP`, `MODULE`, `ACTION`, `USER`, `EXPECTED`, `DUT`, `VERSION`
- The banner text encodes the **test step sequence** — read them in order

### 4. Log Entries Under Banners
- Inside `div.banner-content` after each banner header
- Each entry is `div.log-entry` with a CSS class for the level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `STEP`, `CHECKPOINT`
- Format: `HH:MM:SS.mmm | LEVEL | message text`
- Custom log levels to watch for: `STEP` (test action), `CHECKPOINT` (verification point)

### 5. Tracebacks
- Inside `div.traceback` within a banner-content
- Contains assertion errors, expected vs actual values, file locations, SafeRepr output
- This is the **primary failure evidence**

### 6. Inspect Information
- `div.metadata` inside a banner-content (not the top-level metadata)
- Contains: File path, Function name, Line Number from Python `inspect`

### 7. Raw Logs
- A `div.summary` containing `<h2>Captured Raw Logs</h2>` and a `<pre>` block
- Format: `YYYY-MM-DD HH:MM:SS [LEVEL] message`

### 8. Pytest Hook Timeline
- A `div.summary` containing `<h2>Pytest Hook Timeline</h2>` and a table
- Columns: Timestamp, Hook, Status
- Look for `FAILURE` status entries

## Extraction Rules

1. **Focus on FAILED test cases** — extract all data from failed tests, skip passed tests unless needed for context
2. **Parse every banner** in failed tests — these are your test steps
3. **Capture the traceback verbatim** — do not summarize or paraphrase
4. **Extract module and version** from banner keys (`MODULE=`, `VERSION=`) or from metadata
5. **Note timestamps** from log entries — they establish the failure timeline
6. **Collect ERROR and WARNING log entries** — these are the most relevant signals
7. **If a field is missing**, set it to `"unknown"` — never fabricate values

## Using helpers.py

You can run the Python helper to get structured JSON output:

```bash
python helpers.py parse <path_to_html>     # Full structured parse
python helpers.py failed <path_to_html>    # Only failed test cases
python helpers.py banners <path_to_html>   # All banners extracted
```

Use `parse` for the full picture, `failed` when you only need the failures.
