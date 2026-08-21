#!/usr/bin/env python3
"""
Utility script to upload/sync the election jobs CSV dataset to a Google Spreadsheet.
Requires 'gspread' and a Google Service Account JSON key or OAuth credentials.
"""
import sys
import csv
import os

def print_instructions():
    print("""
===================================================================
How to Import the Ontario Election Jobs CSV to Google Sheets
===================================================================

METHOD 1: Manual Direct Import (Fastest & Easiest, < 10 seconds)
-------------------------------------------------------------------
1. Open Google Sheets (https://sheets.new)
2. Click: File -> Import -> Upload
3. Select the file from your computer:
   data/election_jobs.csv
4. Choose "Replace spreadsheet" or "Insert new sheet"
5. Click "Import data"

METHOD 2: Automated Python Script via gspread
-------------------------------------------------------------------
To upload automatically via Python:
1. Install gspread:
   pip install gspread oauth2client

2. Provide your Google Service Account key as 'credentials.json' in this folder
   and share your Google Sheet with the client_email in that JSON file.

3. Run:
   python3 export_to_sheets.py --sheet-id <YOUR_GOOGLE_SHEET_ID>
===================================================================
""")

def upload_to_sheets(sheet_id_or_title: str):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
    except ImportError:
        print("[!] Missing dependencies. Run: pip install gspread oauth2client")
        return

    creds_file = "credentials.json"
    if not os.path.exists(creds_file):
        print(f"[!] '{creds_file}' not found. Please place your Google Service Account JSON key in this directory.")
        return

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)

    csv_file = "data/election_jobs.csv"
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

    try:
        if len(sheet_id_or_title) > 30 and "/" not in sheet_id_or_title:
            sheet = client.open_by_key(sheet_id_or_title).sheet1
        else:
            sheet = client.open(sheet_id_or_title).sheet1

        sheet.clear()
        sheet.update('A1', data)
        print(f"[✓] Successfully uploaded {len(data)} rows to Google Sheet '{sheet_id_or_title}'!")
    except Exception as e:
        print(f"[!] Error updating Google Sheet: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        upload_to_sheets(sys.argv[1])
    else:
        print_instructions()
