# Linked Log Extraction Instructions

You are analyzing log files linked from an HTML test report to find evidence related to a test failure.

## When to Use This

After HTML extraction (see `html_extraction.md`), you may have linked log file paths. These could be:
- Relative paths found in `<a href="...">` tags (e.g., `logs/serial.log`)
- Absolute paths on the filesystem
- Paths referenced in log entries themselves

**If the HTML report contains all the logs inline** (within banner-content divs), you may not need external log files. In that case, skip this step and note: "All logs were embedded in the HTML report."

## How to Extract Relevant Log Sections

### Step 1: Identify the Failure Window

From the HTML extraction, you have:
- The **failure timestamp** (from ERROR/WARNING log entries or traceback)
- The **test start time** (from metadata)
- Key **error keywords** (from traceback and error messages)

### Step 2: Open Each Log File

For each linked log:
1. Read the file contents
2. If the file doesn't exist, record: `"[log not found: <path>]"` and continue

### Step 3: Search for Relevant Sections

Search for lines containing ANY of:
- Timestamps within the failure window (±2 minutes of the failure timestamp)
- Error keywords from the traceback (e.g., `AssertionError`, `Connection reset`, error messages)
- Log level markers: `ERROR`, `CRITICAL`, `FATAL`, `FAIL`, `EXCEPTION`
- Stack trace indicators: `Traceback`, `File "`, `raise `, `assert `
- System events: `reboot`, `watchdog`, `panic`, `timeout`, `disconnect`

### Step 4: Extract with Context

For each match:
- Include **20 lines before** and **10 lines after** the match
- Merge overlapping snippets
- **Maximum 50 lines** per snippet
- Preserve the original line format including timestamps

### Step 5: Structure the Output

For each log file, produce:

```yaml
- source: "<filename>"
  found: true
  snippets:
    - timestamp: "<first timestamp in snippet>"
      lines: |
        <extracted log lines>
    - timestamp: "..."
      lines: |
        ...
```

Or if not found:

```yaml
- source: "<filename>"
  found: false
  note: "File not found at <path>"
```

## Rules

1. **Do NOT include the entire log file** — only relevant sections
2. **Preserve timestamps exactly** — do not reformat or convert
3. **Include context lines** — errors make more sense with surrounding lines
4. **Note the source file** for every snippet — this will be cited in the JIRA draft
5. **If no relevant content is found** in a log file, note: `"No failure-related entries found"` and skip
6. **Order snippets chronologically** within each log file
