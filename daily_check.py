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

load_dotenv()

def get_cred_path():
    """Return the credentials file path based on platform."""
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
    cred_path = get_cred_path()

    api = sj.Shioaji()
    api.login(os.getenv("Shioaji_ID"), os.getenv("Shioaji_secret"))
    accounts = api.list_accounts()

    # Account balance
    bal = api.account_balance()
    table_data = {
        "Status": bal.status,
        "Account Balance": round(bal.acc_balance),
        "Date": bal.date,
        "Error Message": bal.errmsg,
    }
    print(tabulate([table_data], headers="keys", tablefmt="pretty"))

    # Positions
    positions = api.list_positions(accounts[1], unit=sj.constant.Unit.Share)

    table_data = []
    total_cost = 0
    total_PNL = 0
    today = datetime.now().strftime("%y/%m/%d")

    for item in positions:
        row = {
            "ID": item.id,
            "Code": item.code,
            "Qty": item.quantity,
            "Price": item.price,
            "Last Price": item.last_price,
            "P&L": round(item.pnl),
            "YD Qty": item.yd_quantity,
            "Interest": item.interest,
            "Value": round(item.quantity * item.last_price),
        }
        total_cost += item.quantity * item.price
        total_PNL += item.pnl
        table_data.append(row)

        values = [
            str(value) if key == "Code" else float(value)
            for key, value in row.items()
        ]
        values.insert(0, today)
        gsheet(item.code, values, 18, cred_path=cred_path)

    print(tabulate(table_data, headers="keys", tablefmt="pretty"))

    # Summary row: avoid division by zero
    pnl_pct = round(total_PNL / total_cost, 4) if total_cost else 0
    gsheet(
        "TW balance",
        [today, round(total_cost), round(total_PNL), round(total_cost + total_PNL), pnl_pct],
        18,
        cred_path=cred_path,
    )

    api.logout()


if __name__ == "__main__":
    main()
