## ADDED Requirements

### Requirement: Logging configuration
The system SHALL use Python stdlib logging module with configured output destinations and levels.

#### Scenario: Default logging configuration
- **WHEN** the script starts
- **THEN** logging is configured with console (INFO) and file (DEBUG) handlers
- **AND** log file is written to `./shioaji.log`

### Requirement: Log message format
The system SHALL use a consistent log format with timestamp and level.

#### Scenario: Log message format
- **WHEN** a log message is generated
- **THEN** the message includes timestamp, level, and the message text
- **AND** format is: `YYYY-MM-DD HH:MM:SS | LEVEL    | message`

### Requirement: Logged events
The system SHALL log significant events for debugging and post-mortem analysis.

#### Scenario: Startup logging
- **WHEN** script starts
- **THEN** log entry includes validation of environment variables

#### Scenario: Operation logging
- **WHEN** login, account balance, positions, or Sheets sync operations occur
- **THEN** log entry includes success/failure status

#### Scenario: Error logging
- **WHEN** an error occurs
- **THEN** log entry includes full error message and traceback at DEBUG level
- **AND** summary error message printed to console at ERROR level

#### Scenario: Completion logging
- **WHEN** script completes (success or failure)
- **THEN** log entry includes summary: positions processed, any errors, duration