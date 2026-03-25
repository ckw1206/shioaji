"""
Test module for daily_check.py
Mocks Google Sheets API to prevent real writes during testing.
"""

import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the gspread module before importing daily_check
import unittest


class MockWorksheet:
    """Mock Google Sheets worksheet."""
    
    def __init__(self, name):
        self.name = name
        self.data = []
    
    def insert_row(self, val, row=1):
        """Mock insert - just store the data."""
        self.data.append(val)
        print(f"  [MOCK] Inserted to '{self.name}': {val}")


class MockSpreadsheet:
    """Mock Google Sheets spreadsheet."""
    
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.worksheets = {}
    
    def worksheet(self, name):
        """Get or create a worksheet."""
        if name not in self.worksheets:
            self.worksheets[name] = MockWorksheet(name)
        return self.worksheets[name]
    
    def get_worksheet(self, index):
        """Get worksheet by index."""
        return list(self.worksheets.values())[index] if self.worksheets else None


class MockClient:
    """Mock gspread client."""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.spreadsheets = {}
    
    def open_by_key(self, spreadsheet_id):
        """Open spreadsheet by ID."""
        if spreadsheet_id not in self.spreadsheets:
            self.spreadsheets[spreadsheet_id] = MockSpreadsheet(spreadsheet_id)
        return self.spreadsheets[spreadsheet_id]


def mock_authorize(credentials):
    """Mock gspread.authorize()."""
    return MockClient(credentials)


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running daily_check.py tests (MOCK MODE)")
    print("=" * 60)
    print()
    
    # Set test environment variables
    os.environ['Shioaji_ID'] = 'test_id'
    os.environ['Shioaji_secret'] = 'test_secret'
    os.environ['GOOGLE_SHEETS_ID'] = 'test_spreadsheet_id'
    # Use the same credentials path as production
    os.environ['CREDS_PATH'] = './creds.json'
    
    # Mock the shioaji module
    mock_api = MagicMock()
    
    # Mock account
    mock_account = MagicMock()
    mock_account.account_type = MagicMock()
    mock_account.account_type.__str__ = lambda self: 'AccountType.Stock'
    mock_account.account_id = '1234567'
    mock_account.broker_id = '9A95'
    mock_account.signed = True
    
    # Mock balance
    mock_balance = MagicMock()
    mock_balance.status = MagicMock()
    mock_balance.status.value = 'Fetched'
    mock_balance.acc_balance = 100000.0
    mock_balance.errmsg = ''
    mock_balance.date = '2026-03-25'
    
    # Mock positions
    mock_position = MagicMock()
    mock_position.id = '0'
    mock_position.code = '0050'
    mock_position.quantity = 1000
    mock_position.price = 44.42
    mock_position.last_price = 76.45
    mock_position.pnl = 32030.0
    mock_position.yd_quantity = 1000
    mock_position.interest = 0
    
    # Configure mock API
    mock_api.list_accounts.return_value = [mock_account]
    mock_api.account_balance.return_value = mock_balance
    mock_api.list_positions.return_value = [mock_position]
    mock_api.login.return_value = None
    mock_api.logout.return_value = None
    
    # Patch modules
    with patch('shioaji.Shioaji', return_value=mock_api), \
         patch('gspread.authorize', side_effect=mock_authorize), \
         patch('oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name'):
        
        # Import and run the main function
        import importlib
        import daily_check
        importlib.reload(daily_check)
        
        print("Test 1: Environment validation")
        print("-" * 40)
        
        # Test the validate_env function
        try:
            daily_check.validate_env()
            print("  ✓ validate_env passed")
        except Exception as e:
            print(f"  ✗ validate_env failed: {e}")
        
        print()
        print("Test 2: Full run with mocked APIs")
        print("-" * 40)
        
        try:
            daily_check.main()
            print("  ✓ main() completed successfully")
        except SystemExit as e:
            if e.code == 0:
                print("  ✓ main() completed successfully")
            else:
                print(f"  ✗ main() exited with code: {e.code}")
        except Exception as e:
            print(f"  ✗ main() failed: {e}")
        
        print()
        print("Test 3: Error handling - missing env vars")
        print("-" * 40)
        
        # Save original env
        orig_id = os.environ.get('Shioaji_ID')
        os.environ['Shioaji_ID'] = ''
        
        try:
            daily_check.validate_env()
            print("  ✗ Should have raised SystemExit")
        except SystemExit as e:
            print(f"  ✓ Correctly raised SystemExit: {e}")
        finally:
            os.environ['Shioaji_ID'] = orig_id
    
    print()
    print("=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()