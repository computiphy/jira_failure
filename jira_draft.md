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

1. OPEN_LOGIN_PAGE — Open the login page (`USER=test_user`)
2. SUBMIT_INVALID_PASSWORD — Submit login form with invalid password (`EXPECTED=ERROR_MESSAGE`)
3. **[FAILED]** ASSERT_ERROR_MESSAGE — Verify error message displayed to user

## Failure Details

**Error:** AssertionError: Login error message mismatch

**Expected:** "Invalid password"

**Actual:** "Account temporarily locked"

**Location:** tests/authentication/test_login.py:148

### Traceback
```
E AssertionError: Login error message mismatch

Expected:
"Invalid password"

Actual:
"Account temporarily locked"

Location:
tests/authentication/test_login.py:148

SafeRepr:
<Response status=200 body='Account temporarily locked'>
```

## Relevant Log Evidence

### Inline Logs — Step 2: SUBMIT_INVALID_PASSWORD (10:01:06 – 10:01:07)
```
10:01:06.100 | STEP       | Entering credentials
10:01:06.800 | INFO       | Submitting login form
10:01:07.200 | WARNING    | Unexpected redirect detected
10:01:07.500 | ERROR      | Assertion failed
```

### Inline Logs — Step 3: ASSERT_ERROR_MESSAGE (10:01:08)
```
10:01:08.001 | DEBUG      | pytest_exception_interact invoked
10:01:08.100 | DEBUG      | pytest_runtest_makereport generated failure report
```

### Raw Captured Logs
```
2026-05-24 10:01:07 [ERROR]
AssertionError raised
```

### Pytest Hook Timeline (Failure Entry)
```
10:01:07 | pytest_exception_interact | FAILURE
```

## Probable Cause (AI Suggestion)

> ⚠️ This is an AI-generated suggestion and should be verified by an engineer.
>
> The application returned "Account temporarily locked" instead of "Invalid password", suggesting
> an account lockout policy was triggered by prior failed login attempts. The WARNING at 10:01:07.200
> about an "Unexpected redirect" supports this — lockout may be redirecting to a different error
> page. Two likely root causes:
>
> 1. **Test isolation issue** — A previous test (e.g., `test_login_valid_user`) or prior test run
>    left the account in a locked state. Check if test teardown resets the lockout counter.
> 2. **Product behavior change** — The lockout threshold or error messaging may have changed in
>    a recent update. Verify the lockout policy configuration.
