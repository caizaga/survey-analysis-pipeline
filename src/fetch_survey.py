"""
fetch_survey.py
Descarga los datos de una encuesta desde Google Sheets usando OAuth2
(autenticación con tu cuenta Google personal vía navegador).

Primera vez: abre el navegador para que apruebes el acceso.
Las siguientes veces usa el token guardado en caché automáticamente.

Uso rápido:
    python src/fetch_survey.py

Uso como módulo:
    from src.fetch_survey import fetch_survey_data
    df = fetch_survey_data()
"""

import yaml
import gspread
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_config() -> dict:
    with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def fetch_survey_data() -> pd.DataFrame:
    """
    Autentica con tu cuenta Google (OAuth2) y descarga los datos
    de la hoja configurada en config.yaml.
    """
    config = _load_config()
    gs_cfg = config["google_sheets"]

    spreadsheet_id: str = gs_cfg["spreadsheet_id"]
    sheet_name: str = gs_cfg["sheet_name"]
    cell_range: str = gs_cfg.get("range", "").strip()

    # gspread.oauth() maneja todo el flujo OAuth2 automáticamente.
    # La primera vez abre el navegador; después usa el token en caché.
    client = gspread.oauth()

    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(sheet_name)

    rows = worksheet.get(cell_range) if cell_range else worksheet.get_all_values()

    if not rows:
        print("La hoja está vacía.")
        return pd.DataFrame()

    df = pd.DataFrame(rows[1:], columns=rows[0])
    print(f"✓ {len(df)} respuestas descargadas desde '{sheet_name}'")
    return df


def save_to_raw(df: pd.DataFrame, filename: str = None) -> Path:
    """Guarda el DataFrame como XLSX en la carpeta raw/."""
    raw_dir = BASE_DIR / "raw"
    raw_dir.mkdir(exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"survey_raw_{timestamp}.xlsx"

    output_path = raw_dir / filename
    df.to_excel(output_path, index=False)
    print(f"✓ Guardado en: {output_path}")
    return output_path


if __name__ == "__main__":
    df = fetch_survey_data()
    if not df.empty:
        save_to_raw(df)
        print(df.head())
