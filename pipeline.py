"""
pipeline.py — Orquestador principal
  Paso 1: Descarga la encuesta desde Google Sheets → raw/
  Paso 2: Normaliza columnas → staging/
"""

from src.fetch_survey import fetch_survey_data, save_to_raw
from src.transform_columns import transform

if __name__ == "__main__":
    print("=== PASO 1: Descarga ===")
    df = fetch_survey_data()
    raw_path = save_to_raw(df)

    print("\n=== PASO 2: Transformación de columnas ===")
    transform(raw_path)
