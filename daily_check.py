from tabulate import tabulate
from datetime import datetime
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# SinoPac API
import shioaji as sj

# Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# test
# Check the platform from the sys module
if sys.platform.startswith('linux'):
    cred_path = "/home/opc/.ssh/creds.json"
elif sys.platform.startswith('win'):
    cred_path = "C:/Users/Kyle/.ssh/creds.json"
else:
    print("Unsupported platform. Exiting the script.")
    sys.exit()

def gsheet(sheet_name,val,row):
    scopes = ["https://spreadsheets.google.com/feeds"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            cred_path, scopes)
    client = gspread.authorize(credentials)

    sheet = client.open_by_key(os.getenv("GOOGLE_SHEETS_ID")).worksheet(sheet_name)
    # sheet.append_row(val)
    # sheet.insert_row(val,row)
    print(val," run successfully.")

api = sj.Shioaji()
# print(sj.__version__)

# prod token
api.login(os.getenv("Shioaji_ID"), os.getenv("Shioaji_secret"))
accounts = api.list_accounts()
# print(accounts)

# Print account balance
bal = api.account_balance()
table_data = {
    'Status': bal.status,
    'Account Balance': round(bal.acc_balance),
    'Date': bal.date,
    'Error Message': bal.errmsg
}
table = tabulate([table_data], headers='keys', tablefmt='pretty')
# print(table)

# Print account positions
positions = api.list_positions(accounts[1],unit=sj.constant.Unit.Share)

table_data = []
total_cost=0
total_PNL=0
for item in positions:
    row = {
        'ID': item.id,
        'Code': item.code,
        'Qty': item.quantity,
        'Price': item.price,
        'Last Price': item.last_price,
        'P&L': round(item.pnl),
        'YD Qty': item.yd_quantity,
        'Interest': item.interest,
        'Value': round(item.quantity*item.last_price)
    }
    total_cost+=item.quantity*item.price
    total_PNL+=item.pnl
    table_data.append(row)

    # Insert results into Google Sheets
    today = datetime.now().strftime('%y/%m/%d')
    values = [float(value) for value in row.values()]
    values.insert(0, today)
    gsheet(item.code,values,18)
    gsheet('daily price',values,2)

# Print out results
table = tabulate(table_data, headers='keys', tablefmt='pretty')
# print(table)
# print("total Cost =", round(total_cost))
# print("total P&L =", round(total_PNL))
# print("total Value =", round(total_cost+total_PNL))
# print("return rate =", round(total_PNL/total_cost*100,2),"%")

gsheet('daily balance',[today,round(total_cost),round(total_PNL),round(total_cost+total_PNL),round(total_PNL/total_cost,4)],18)

# logout
api.logout()
