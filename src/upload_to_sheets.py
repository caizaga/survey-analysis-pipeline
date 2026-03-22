"""
upload_to_sheets.py
Sube los dataframes transformados a Google Sheets en tabs separados:
  - df_le → tab 'data'
  - diccionario de columnas → tab 'diccionario'

Uso como módulo (desde el notebook):
    from src.upload_to_sheets import upload_all
    upload_all(df_le)
"""

import os
import gspread
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from gspread_dataframe import set_with_dataframe

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SPREADSHEET_ID = os.environ["SHEETS_OUTPUT_ID"]
BASE_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = BASE_DIR / "staging"


def _get_or_create_worksheet(spreadsheet, name: str, rows: int, cols: int):
    """Retorna la worksheet si existe, si no la crea."""
    try:
        ws = spreadsheet.worksheet(name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=rows, cols=cols)
    return ws


def upload_all(df_le: pd.DataFrame) -> None:
    """Sube df_le y el diccionario de columnas al Google Sheet configurado."""
    client = gspread.oauth()
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    print(f"Subiendo 'data' ({len(df_le)} filas × {len(df_le.columns)} cols)...", end=" ")
    ws = _get_or_create_worksheet(spreadsheet, name="data", rows=len(df_le) + 10, cols=len(df_le.columns) + 2)
    set_with_dataframe(ws, df_le, include_index=False)
    print("✓")

    # ── Diccionario de columnas ───────────────────────────────────────────────
    dict_files = sorted(STAGING_DIR.glob("*_column_dictionary.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True)
    if dict_files:
        df_dict = pd.read_excel(dict_files[0])
        print(f"Subiendo 'diccionario' ({len(df_dict)} columnas)...", end=" ")
        ws_dict = _get_or_create_worksheet(spreadsheet, name="diccionario", rows=len(df_dict) + 10, cols=5)
        set_with_dataframe(ws_dict, df_dict, include_index=False)
        print("✓")
    else:
        print("⚠ No se encontró diccionario en staging/ — omitido.")

    print(f"\nListo → https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
