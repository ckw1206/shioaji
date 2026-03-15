## 1. Environment Validation

- [x] 1.1 Add `validate_env()` function to check required env vars at startup
- [x] 1.2 Call `validate_env()` at the beginning of `main()`

## 2. Error Handling Infrastructure

- [x] 2.1 Add try/except wrapper around main logic in `main()`
- [x] 2.2 Add `finally` block to ensure `api.logout()` is always called
- [x] 2.3 Create error classification: `is_critical_error()` function

## 3. Account Selection Fix

- [x] 3.1 Replace hardcoded `accounts[1]` with type-based filtering
- [x] 3.2 Filter accounts by `account_type == 'Securities'` (or appropriate type)
- [x] 3.3 Handle case when no securities account found (raise SystemExit)

## 4. Logging Implementation

- [x] 4.1 Add `logging` module import
- [x] 4.2 Configure logging with console (INFO) and file (DEBUG) handlers
- [x] 4.3 Set log file to `./shioaji.log`
- [x] 4.4 Add logging calls for: startup, login, balance, positions, sync, completion, errors

## 5. Non-Critical Error Handling

- [x] 5.1 Create error collection list for non-critical errors
- [x] 5.2 Wrap individual stock sync in try/except inside loop
- [x] 5.3 On non-critical error, add to error list and continue
- [x] 5.4 Report all collected errors at end of execution

## 6. Testing

- [x] 6.1 Test with missing env var (should fail fast with clear message)
- [x] 6.2 Test with valid env vars (should succeed)
- [x] 6.3 Verify `shioaji.log` is created with DEBUG entries
- [x] 6.4 Verify logout is called even on errors