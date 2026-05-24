# JIRA Draft Generation Instructions

You are generating a structured JIRA bug draft from extracted test failure data.

## Inputs You Have

By this point, you have collected:
1. **Test metadata** — test name, module, class, function, start time, DUT, firmware version
2. **Test steps** — derived from banners (STEP=N, ACTION=X)
3. **Failure details** — traceback, assertion error, expected vs actual
4. **Log evidence** — relevant log snippets with timestamps from inline logs or linked files
5. **Execution summary** — suite name, total/passed/failed counts, environment

## Draft Structure

Generate the JIRA draft in the exact format below. Replace `<placeholders>` with actual values.

---

### Title

```
[<MODULE>] <Concise failure description> — <test_name>
```

Rules for title:
- Start with the module/component name in brackets
- Describe the failure, not the test
- Include the test function name at the end
- Maximum 100 characters
- Example: `[AUTHENTICATION] Login error message mismatch — test_login_invalid_password`

### Description (Markdown)

```markdown
## Summary

<One or two sentences describing what failed and why it matters.>

## Environment

| Field | Value |
|-------|-------|
| **Module** | <module> |
| **Firmware Version** | <version or "unknown"> |
| **DUT** | <dut_id or "unknown"> |
| **Test Suite** | <suite name> |
| **Environment** | <Python version / OS> |
| **Execution Date** | <date from timestamps> |

## Test Steps

<Numbered list derived from banners. Mark the failing step.>

1. <ACTION from STEP=1 banner — human-readable>
2. <ACTION from STEP=2 banner — human-readable>
3. **[FAILED]** <ACTION from failing STEP banner — human-readable>

## Failure Details

**Error:** <assertion error or exception type>

**Expected:** <expected value from traceback>

**Actual:** <actual value from traceback>

**Location:** <file:line from traceback>

### Traceback
```
<verbatim traceback, do NOT modify>
```

## Relevant Log Evidence

### <log_source> (<timestamp range>)
```
<log snippet>
```

### <log_source_2> (<timestamp range>)
```
<log snippet>
```

## Probable Cause (AI Suggestion)

> ⚠️ This is an AI-generated suggestion and should be verified by an engineer.
>
> <Brief, specific hypothesis about what caused the failure based on the evidence.
>  Reference specific log entries or assertion values. Do NOT speculate beyond the evidence.>
```

### Priority

Suggest a priority based on:

| Priority | Criteria |
|----------|----------|
| **Critical** | System crash, data loss, kernel panic, watchdog reset |
| **Major** | Test blocked, core functionality broken, security issue |
| **Medium** | Assertion mismatch, unexpected behavior, intermittent failure |
| **Minor** | Cosmetic, logging issue, non-functional regression |

### Labels

Generate labels from:
- `"auto-triaged"` (always include)
- Module name in lowercase (e.g., `authentication`)
- Failure type in lowercase (e.g., `assertion-error`, `connection-loss`, `timeout`)

### Component

Set to the MODULE value from the banner, in Title Case (e.g., `Authentication`).

---

## Output Files

Produce TWO files:

### 1. `jira_draft.md`
The human-readable draft in the markdown format above. This is what the engineer reviews.

### 2. `jira_draft.json`
A structured JSON file ready for future MCP consumption:

```json
{
  "title": "<title>",
  "description": "<full markdown description>",
  "priority": "<Critical|Major|Medium|Minor>",
  "component": "<component>",
  "labels": ["auto-triaged", "<module>", "<failure-type>"],
  "environment": {
    "firmware_version": "<version>",
    "dut": "<dut_id>",
    "test_suite": "<suite>",
    "os": "<os/python info>"
  },
  "test_name": "<test_function_name>",
  "module": "<module_path>",
  "failure_step": <step_number>,
  "log_evidence": [
    {
      "source": "<filename>",
      "timestamp": "<timestamp>",
      "snippet": "<log text>"
    }
  ]
}
```

## Rules

1. **Never paraphrase error messages or tracebacks** — copy them verbatim
2. **Always mark AI suggestions clearly** — use the warning callout
3. **Keep the summary under 2 sentences** — engineers scan, not read
4. **Test steps must come from banners** — do not invent steps
5. **If a field is unknown, say "unknown"** — do not guess
6. **Log snippets must cite their source file** — always include filename and timestamp
