"""
Daily check script for Shioaji (SinoPac) trading account.
Fetches account balance and positions, then syncs to Google Sheets.
"""

import sys
import os
from datetime import datetime

from tabulate import tabulate
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
import shioaji as sj
import gspread

import logging

load_dotenv()

# Configure logging
def setup_logging():
    """Configure logging with console and file handlers."""
    log_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    
    # Console handler with UTF-8 encoding for Unicode support
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))
    # Handle Unicode in Windows console
    try:
        import codecs
        console_handler.stream = codecs.getwriter('utf-8')(console_handler.stream.buffer)
    except Exception:
        pass  # Fallback if codec not available
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler('shioaji.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers = [console_handler, file_handler]

def validate_env():
    """Validate required environment variables at startup."""
    required = ['Shioaji_ID', 'Shioaji_secret', 'GOOGLE_SHEETS_ID']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        logging.error(f"Missing required environment variables: {missing}")
        raise SystemExit(f"Missing required environment variables: {missing}")
    
    logging.info("Environment validation passed")

def is_critical_error(error):
    """Classify error as critical (True) or non-critical (False).
    
    Critical errors should stop execution immediately.
    Non-critical errors should be collected and reported at end.
    """
    error_msg = str(error).lower()
    critical_keywords = ['login', 'authentication', 'account', 'balance', 'failed']
    
    # Check if error message contains critical keywords
    if any(keyword in error_msg for keyword in critical_keywords):
        return True
    
    return False


def get_cred_path():
    """Return the credentials file path.
    
    Uses CREDS_PATH env var if set, otherwise defaults based on platform:
    - Windows: ./creds.json
    - Linux: ./shioaji/creds.json
    """
    # Allow custom path via environment variable
    custom_path = os.getenv("CREDS_PATH")
    if custom_path:
        return custom_path
    
    # Default paths by platform
    if sys.platform.startswith("linux"):
        return "./shioaji/creds.json"
    if sys.platform.startswith("win"):
        return "./creds.json"
    raise SystemExit("Unsupported platform. Exiting the script.")

def gsheet(sheet_name, val, row, cred_path=None):
    """Insert a row into the named worksheet in Google Sheets."""
    cred_path = cred_path or get_cred_path()
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        cred_path, scopes
    )
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(os.getenv("GOOGLE_SHEETS_ID"))
    sheet = spreadsheet.worksheet(sheet_name)
    # sheet.append_row(val)
    sheet.insert_row(val,row)

def main():
    # Setup logging FIRST - before any logging calls
    setup_logging()
    logging.info("Script started")
    
    # Validate environment variables (uses logging, so must be after setup_logging)
    validate_env()
    
    # Validate credentials file
    cred_path = get_cred_path()
    if not os.path.exists(cred_path):
        logging.error(f"Credentials file not found: {cred_path}")
        raise SystemExit(f"Credentials file not found: {cred_path}")
    logging.info(f"Using credentials from: {cred_path}")

    api = sj.Shioaji()
    errors = []  # Non-critical errors collected during execution
    
    try:
        # Login
        logging.info("Logging into Shioaji API")
        api.login(os.getenv("Shioaji_ID"), os.getenv("Shioaji_secret"))
        logging.info("Login successful")
        
        # Get accounts and filter by type
        accounts = api.list_accounts()
        
        # Try to find stock accounts - these support balance and positions
        stock_accounts = [a for a in accounts if hasattr(a, 'account_type') and str(a.account_type) == 'AccountType.Stock']
        
        # Fallback: use first account with signed=True
        if not stock_accounts:
            stock_accounts = [a for a in accounts if getattr(a, 'signed', False)]
        
        # Final fallback: use first account
        if not stock_accounts and accounts:
            stock_accounts = [accounts[0]]
        
        # Validate we have an account
        if not stock_accounts:
            logging.error("No stock account found")
            raise SystemExit("No stock account found. Please check your Shioaji account.")
        
        account = stock_accounts[0]
        logging.info(f"Using account: {account}")
        
        # Account balance
        logging.info("Fetching account balance")
        bal = api.account_balance(account)
        
        # Check status - it can be an int or an enum like FetchStatus
        status = bal.status
        status_ok = False
        if hasattr(status, 'value'):
            # Handle enum like FetchStatus
            status_ok = status.value == 'Fetched'
        elif hasattr(status, '__int__'):
            # Handle int status
            status_ok = int(status) == 0
        else:
            # Default: check if truthy
            status_ok = bool(status)
        
        if not status_ok or not bal.acc_balance:
            logging.error(f"Account balance error: {bal.errmsg}")
            raise SystemExit(f"Failed to get account balance: {bal.errmsg}")
        
        table_data = {
            "Status": bal.status,
            "Account Balance": f"{bal.acc_balance:.2f}",
            "Date": bal.date,
            "Error Message": bal.errmsg,
        }
        print(tabulate([table_data], headers="keys", tablefmt="pretty"))
        logging.info(f"Account balance: {bal.acc_balance:.2f}")

        # Positions
        logging.info("Fetching positions")
        positions = api.list_positions(account, unit=sj.constant.Unit.Share)
        logging.info(f"Found {len(positions)} positions")

        table_data = []
        total_cost = 0
        total_PNL = 0
        today = datetime.now().strftime("%y/%m/%d")

        for item in positions:
            row = {
                "ID": item.id,
                "Code": item.code,
                "Qty": item.quantity,
                "Price": f"{item.price:.2f}",
                "Last Price": f"{item.last_price:.2f}",
                "P&L": f"{item.pnl:.2f}",
                "YD Qty": item.yd_quantity,
                "Interest": item.interest,
                "Value": f"{item.quantity * item.last_price:.2f}",
            }
            total_cost += item.quantity * item.price
            total_PNL += item.pnl
            table_data.append(row)

            # Build values for Sheets - convert to float with 2 decimal places
            values = []
            for key, value in row.items():
                if key == "Code":
                    values.append(str(value))
                elif key in ("ID", "Qty", "YD Qty", "Interest"):
                    values.append(float(value))
                elif isinstance(value, str):
                    values.append(float(value))
                else:
                    values.append(float(f"{value:.2f}"))
            values.insert(0, today)
            
            # Wrap individual stock sync in try/except (non-critical)
            try:
                gsheet(item.code, values, 18, cred_path=cred_path)
                logging.debug(f"Synced stock {item.code} to Sheets")
            except Exception as e:
                error_msg = f"Failed to sync stock {item.code}: {e}"
                logging.warning(error_msg)
                errors.append(error_msg)

        print(tabulate(table_data, headers="keys", tablefmt="pretty"))

        # Summary row: avoid division by zero
        pnl_pct = round(total_PNL / total_cost, 4) if total_cost else 0
        
        # Sync summary (non-critical)
        try:
            gsheet(
                "TW balance",
                [today, f"{total_cost:.2f}", f"{total_PNL:.2f}", f"{(total_cost + total_PNL):.2f}", pnl_pct],
                18,
                cred_path=cred_path,
            )
            logging.debug("Synced summary to TW balance")
        except Exception as e:
            error_msg = f"Failed to sync summary: {e}"
            logging.warning(error_msg)
            errors.append(error_msg)

        logging.info(f"Completed successfully - Total cost: {total_cost:.2f}, P&L: {total_PNL:.2f}")
        
    except Exception as e:
        if is_critical_error(e):
            logging.error(f"Critical error: {e}")
            raise
        else:
            logging.error(f"Non-critical error: {e}")
            errors.append(str(e))
    
    finally:
        # Always logout, regardless of success or failure
        try:
            api.logout()
            logging.info("Logged out successfully")
        except Exception as e:
            logging.warning(f"Error during logout: {e}")
    
    # Report non-critical errors at end
    if errors:
        print("\n--- Errors Encountered ---")
        for error in errors:
            print(f"  - {error}")
        logging.warning(f"Encountered {len(errors)} non-critical errors")


if __name__ == "__main__":
    main()
