# Few-Shot Examples

These examples show the complete input→output pipeline for reference.

---

## Example 1: Assertion Mismatch Failure

### Input (from HTML extraction)

```yaml
test_name: test_login_invalid_password
status: FAIL
metadata:
  Module: tests.authentication.test_login
  Class: TestLogin
  Function: test_login_invalid_password
  Start Time: "2026-05-24 10:01:05"
steps:
  - STEP: "1"
    MODULE: AUTHENTICATION
    ACTION: OPEN_LOGIN_PAGE
    log_entries:
      - { timestamp: "10:01:05.100", level: INFO, message: "Opening Login Page" }
      - { timestamp: "10:01:05.800", level: INFO, message: "Login page loaded" }
  - STEP: "2"
    MODULE: AUTHENTICATION
    ACTION: SUBMIT_INVALID_PASSWORD
    EXPECTED: ERROR_MESSAGE
    log_entries:
      - { timestamp: "10:01:06.100", level: STEP, message: "Entering credentials" }
      - { timestamp: "10:01:06.800", level: INFO, message: "Submitting login form" }
      - { timestamp: "10:01:07.200", level: WARNING, message: "Unexpected redirect detected" }
      - { timestamp: "10:01:07.500", level: ERROR, message: "Assertion failed" }
  - STEP: "3"
    MODULE: AUTHENTICATION
    ACTION: ASSERT_ERROR_MESSAGE
    traceback: |
      E AssertionError: Login error message mismatch
      Expected: "Invalid password"
      Actual: "Account temporarily locked"
      Location: tests/authentication/test_login.py:148
      SafeRepr: <Response status=200 body='Account temporarily locked'>
summary:
  Suite: Regression Suite
  Environment: "Python 3.12 / Windows 11"
  Total Tests: "2"
  Failed: "1"
```

### Output: jira_draft.md

```markdown
## Summary

Login error message assertion fails during invalid password test — the application returns "Account temporarily locked" instead of the expected "Invalid password" message.

## Environment

| Field | Value |
|-------|-------|
| **Module** | tests.authentication.test_login |
| **Firmware Version** | unknown |
| **DUT** | unknown |
| **Test Suite** | Regression Suite |
| **Environment** | Python 3.12 / Windows 11 |
| **Execution Date** | 2026-05-24 |

## Test Steps

1. OPEN_LOGIN_PAGE — Open the login page
2. SUBMIT_INVALID_PASSWORD — Submit login form with invalid password (expected: error message)
3. **[FAILED]** ASSERT_ERROR_MESSAGE — Verify error message displayed to user

## Failure Details

**Error:** AssertionError: Login error message mismatch

**Expected:** "Invalid password"

**Actual:** "Account temporarily locked"

**Location:** tests/authentication/test_login.py:148

### Traceback
```
E AssertionError: Login error message mismatch
Expected: "Invalid password"
Actual: "Account temporarily locked"
Location: tests/authentication/test_login.py:148
SafeRepr: <Response status=200 body='Account temporarily locked'>
```

## Relevant Log Evidence

### Inline Logs — Step 2 (10:01:06 – 10:01:07)
```
10:01:06.100 | STEP | Entering credentials
10:01:06.800 | INFO | Submitting login form
10:01:07.200 | WARNING | Unexpected redirect detected
10:01:07.500 | ERROR | Assertion failed
```

## Probable Cause (AI Suggestion)

> ⚠️ This is an AI-generated suggestion and should be verified by an engineer.
>
> The application appears to be enforcing account lockout due to prior failed login attempts,
> returning "Account temporarily locked" instead of the expected "Invalid password" error.
> The WARNING at 10:01:07.200 about an "Unexpected redirect" suggests the lockout mechanism
> may also be redirecting to a different error page. This could be a test isolation issue
> (prior tests leaving lockout state) or a product behavior change.
```

### Output: jira_draft.json

```json
{
  "title": "[AUTHENTICATION] Login error message mismatch — test_login_invalid_password",
  "description": "...(full markdown above)...",
  "priority": "Medium",
  "component": "Authentication",
  "labels": ["auto-triaged", "authentication", "assertion-error"],
  "environment": {
    "firmware_version": "unknown",
    "dut": "unknown",
    "test_suite": "Regression Suite",
    "os": "Python 3.12 / Windows 11"
  },
  "test_name": "test_login_invalid_password",
  "module": "tests.authentication.test_login",
  "failure_step": 3,
  "log_evidence": [
    {
      "source": "inline (Step 2)",
      "timestamp": "10:01:06.100",
      "snippet": "10:01:06.100 | STEP | Entering credentials\n10:01:06.800 | INFO | Submitting login form\n10:01:07.200 | WARNING | Unexpected redirect detected\n10:01:07.500 | ERROR | Assertion failed"
    }
  ]
}
```

---

## Key Patterns to Follow

1. **Title** always starts with `[MODULE]` and ends with the test function name
2. **Test steps** are derived from banner ACTION values — make them human-readable
3. **Traceback is always copied verbatim** — never edit or summarize it
4. **AI suggestions use the warning callout** and reference specific evidence
5. **Log snippets always cite source and timestamp range**
6. **Priority = Medium** for assertion mismatches, Major for blocking failures, Critical for crashes
