# Shioaji Daily Check

A Python script that fetches your Shioaji (SinoPac) trading account balance and positions, then syncs the data to Google Sheets for tracking.

## What It Does

- Connects to Shioaji API and retrieves account balance
- Lists all positions (stocks) with details: quantity, price, P&L, value
- Inserts position data into per-stock worksheets in Google Sheets
- Writes a summary (total cost, P&L, P&L %) to a "TW balance" worksheet
- Prints formatted tables to the console

## Prerequisites

- Python 3.11+
- Shioaji trading account (永豐金證券)
- Google Cloud project with Sheets API enabled
- Google service account JSON credentials

## Installation

1. **Clone or download this repo**

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   source venv/bin/activate # Linux / macOS
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
Shioaji_ID=your_shioaji_api_id
Shioaji_secret=your_shioaji_api_secret
GOOGLE_SHEETS_ID=your_google_spreadsheet_id

# Optional: Custom path for Google service account credentials
# Defaults: ./creds.json (Windows) or ./shioaji/creds.json (Linux)
# CREDS_PATH=./path/to/your/creds.json
```

### 2. Credentials

- **Shioaji**: Use your Shioaji API credentials (ID and secret) in `.env`.

- **Google Sheets**: Create a service account in [Google Cloud Console](https://console.cloud.google.com/), enable the Google Sheets API, and download the JSON key file. Save it as `creds.json` in the project root.

- **Custom Path**: Use `CREDS_PATH` environment variable to specify a different location for `creds.json`.

### 3. Google Sheets

- Create a Google Spreadsheet and share it with your service account email (found in the JSON key).
- Add a worksheet named `TW balance` for the summary.
- The script creates/uses worksheets named by stock code (e.g. `2330`, `0050`) for each position.

## Usage

```bash
python daily_check.py
```

## Supported Platforms

| Platform | Default Credentials Path |
|:---------|:------------------------:|
| Windows  | `./creds.json`           |
| Linux    | `./creds.json`           |

**Note**: Use `CREDS_PATH` environment variable to override the default path.

## Project Structure

```bash
shioaji/
├── daily_check.py    # Main script
├── requirements.txt  # Python dependencies
├── .env.example      # Template for environment variables
├── .env              # Your credentials (create this, do not commit)
├── creds.json        # Google service account key (do not commit)
├── shioaji.log       # Log file (generated on run)
└── README.md
```

## Dependencies

- **shioaji** – SinoPac/Shioaji trading API
- **gspread** – Google Sheets API
- **oauth2client** – Google OAuth2 authentication
- **python-dotenv** – Load `.env` variables
- **tabulate** – Pretty-print tables

## Features

- **Error Handling**: Validates environment variables at startup, handles critical vs non-critical errors gracefully
- **Logging**: Logs to console (INFO) and `./shioaji.log` (DEBUG) for debugging
- **Account Detection**: Automatically detects the correct stock account
- **Custom Credentials Path**: Use `CREDS_PATH` env var to specify custom creds.json location
