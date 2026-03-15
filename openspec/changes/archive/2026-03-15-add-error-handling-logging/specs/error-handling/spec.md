## ADDED Requirements

### Requirement: Environment validation
The system SHALL validate all required environment variables at startup and fail with a clear error message if any are missing.

#### Scenario: All required env vars present
- **WHEN** all required environment variables (Shioaji_ID, Shioaji_secret, GOOGLE_SHEETS_ID) are set
- **THEN** the script proceeds to login

#### Scenario: Missing required env var
- **WHEN** any required environment variable is missing or empty
- **THEN** the script exits immediately with error message listing missing variables

### Requirement: Critical error handling
The system SHALL stop execution immediately when critical errors occur.

#### Scenario: Login failure
- **WHEN** Shioaji login fails due to invalid credentials or network error
- **THEN** the script prints error message and exits without proceeding

#### Scenario: No securities account found
- **WHEN** no securities account is found after filtering accounts by type
- **THEN** the script exits immediately with error message

#### Scenario: Account balance query failure
- **WHEN** the account balance API call fails
- **THEN** the script exits immediately with error message

### Requirement: Non-critical error handling
The system SHALL continue processing when non-critical errors occur, collecting all errors to report at the end.

#### Scenario: Individual stock sync failure
- **WHEN** syncing a single stock to Google Sheets fails (network error, worksheet missing)
- **THEN** the script logs the error, continues to next stock, and reports all failures at the end

#### Scenario: Partial sync with some failures
- **WHEN** multiple stocks are synced but some fail
- **THEN** successful stocks are synced, failed stocks are reported in summary

### Requirement: Guaranteed cleanup
The system SHALL always call API logout, regardless of success or failure.

#### Scenario: Successful execution
- **WHEN** the script completes all operations successfully
- **THEN** API logout is called

#### Scenario: Execution with errors
- **WHEN** the script encounters an error and exits
- **THEN** API logout is called in finally block before exit