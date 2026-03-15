## Context

**Background:** `daily_check.py` is a simple on-demand script that fetches Shioaji trading account data and syncs to Google Sheets.

**Current State:**
- No environment variable validation at startup
- Hardcoded `accounts[1]` index (fragile, can cause IndexError)
- No try/except blocks — any exception crashes the script
- No logging — only console print output
- No guarantee of API logout on errors

**Constraints:**
- On-demand tool (user present when running) — no complex retry/notification system needed
- No new dependencies — use Python stdlib `logging`
- Must maintain current functionality (fetch balance, sync positions)

## Goals / Non-Goals

**Goals:**
- Fail fast with clear error messages for missing config
- Always cleanup (API logout) regardless of success or failure
- Handle errors gracefully: continue on non-critical, stop on critical
- Add logging for debugging post-mortem
- Fix fragile hardcoded account index

**Non-Goals:**
- Automated scheduling (Windows Task Scheduler / cron)
- Retry logic with exponential backoff
- Notification system (Telegram/Slack/email)
- Batch transactions (all-or-nothing writes)

## Decisions

### 1. Account Selection: Filter by Type vs Index

**Decision:** Filter accounts by type (`account_type == 'Secuities'`) instead of using hardcoded index `accounts[1]`.

**Rationale:** More robust — works regardless of how many accounts returned and their order. The hardcoded index assumes the securities account is always at index 1, which is fragile.

**Alternatives Considered:**
- `accounts[0]`: Assumes first account is the right one
- Try/except IndexError: Catches the error but still fragile

### 2. Error Classification Strategy

**Decision:** Classify errors as critical (stop) or non-critical (continue + report at end).

**Rationale:** Since this is on-demand and the user is present:
- Critical errors (login failure, no accounts, balance query failed) should stop immediately with clear message
- Non-critical errors (individual stock sync failed) should continue processing other stocks and report all failures at the end

**Classification:**
```
CRITICAL (stop immediately):
  - Login failure (bad credentials, network)
  - No securities account found
  - Account balance query failed

NON-CRITICAL (continue, report at end):
  - Individual stock worksheet missing
  - Individual stock sync failed (network/Sheets API)
```

### 3. Logging Implementation

**Decision:** Use Python stdlib `logging` with:
- Console: INFO level (user sees what's happening)
- File: DEBUG level (full detail in `./shioaji.log`)
- Simple format: `%(asctime)s | %(levelname)-8s | %(message)s`

**Rationale:** No new dependencies needed, matches existing `.gitignore` entry for `shioaji.log`.

**Alternatives Considered:**
- External library (loguru): More features but adds dependency
- Only console logging: Not enough for post-mortem debugging

### 4. Environment Validation

**Decision:** Validate required env vars at startup, fail fast with clear message.

**Rationale:** Current code tries to login with `None` if env var missing, resulting in cryptic API errors. Better to fail fast with clear message like "Missing required env var: Shioaji_ID"

## Risks / Trade-offs

- **Risk:** Google Sheets API quota limits → **Mitigation:** Non-critical errors don't stop the whole process; user can re-run
- **Risk:** Shioaji API changes account model → **Mitigation:** Filter by type is more robust than index, but could add logging to help debug
- **Trade-off:** Simple error handling means some partial failures possible → **Mitigation:** Report all non-critical errors at end so user knows what to re-run

## Migration Plan

1. Add `validate_env()` function to check required vars at startup
2. Wrap main logic in try/except with error classification
3. Add `finally` block for API logout
4. Replace `accounts[1]` with type-based filter
5. Add logging configuration at module level
6. Test with both success and failure scenarios

No rollback needed — this is a standalone script; original can be restored from git if needed.