## Why

The current `daily_check.py` lacks proper error handling and logging, causing:
- Silent crashes on API failures without clear error messages
- No cleanup (API logout) when errors occur mid-execution
- Hardcoded account index (`accounts[1]`) that can cause IndexError
- No logging for debugging post-mortem issues

These issues make debugging difficult and can leave the API in an inconsistent state.

## What Changes

- Add environment variable validation at startup with clear error messages
- Add try/except wrapper around main logic with graceful error handling
- Add `finally` block to ensure API logout always occurs
- Fix hardcoded `accounts[1]` to filter accounts by type instead of index
- Add classification of errors: critical (stop) vs non-critical (continue + report)
- Add logging to console and `./shioaji.log` file

## Capabilities

### New Capabilities
- `error-handling`: Defines how different error types are handled (critical vs non-critical)
- `logging`: Defines logging configuration (levels, output destinations, format)

### Modified Capabilities
(None - this is a new tool improvement, not modifying existing capabilities)

## Impact

- **File:** `daily_check.py` - main logic updates
- **New file:** `.env.example` - environment variable template (already created)
- **Dependencies:** No new pip packages required (using stdlib `logging`)