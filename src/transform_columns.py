"""
transform_columns.py
Paso 2 del pipeline: toma el XLSX de raw/, normaliza los nombres de columnas
(minúsculas + espacios → _) y guarda:
  - El dataset transformado en staging/
  - Un diccionario de columnas (original vs transformada) en staging/

Uso rápido:
    python src/transform_columns.py

Uso como módulo:
    from src.transform_columns import transform
    df, dictionary = transform()
"""

import re
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"
STAGING_DIR = BASE_DIR / "staging"


def _latest_raw_file() -> Path:
    """Retorna el archivo XLSX más reciente dentro de raw/."""
    files = sorted(RAW_DIR.glob("*.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No hay archivos XLSX en raw/. Corre primero fetch_survey.py")
    return files[0]


def _normalize(col: str) -> str:
    """Minúsculas, reemplaza espacios y caracteres especiales por _."""
    col = col.strip().lower()
    col = re.sub(r"[^\w]+", "_", col)   # cualquier carácter no-alfanumérico → _
    col = re.sub(r"_+", "_", col)       # colapsa múltiples _ seguidos
    col = col.strip("_")                # quita _ al inicio/fin
    return col


def transform(raw_path: Path = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee el XLSX de raw/, normaliza columnas y guarda resultados en staging/.
    Retorna (df_transformado, df_diccionario).
    """
    STAGING_DIR.mkdir(exist_ok=True)

    if raw_path is None:
        raw_path = _latest_raw_file()

    print(f"Leyendo: {raw_path.name}")
    df = pd.read_excel(raw_path)

    # Diccionario original → transformada
    column_map = {col: _normalize(col) for col in df.columns}
    df_dict = pd.DataFrame(
        list(column_map.items()),
        columns=["columna_original", "columna_transformada"]
    )

    # Aplicar renombre
    df.rename(columns=column_map, inplace=True)

    # Guardar
    stem = raw_path.stem.replace("survey_raw", "survey_staging")
    output_path = STAGING_DIR / f"{stem}.xlsx"
    dict_path = STAGING_DIR / f"{stem}_column_dictionary.xlsx"

    df.to_excel(output_path, index=False)
    df_dict.to_excel(dict_path, index=False)

    print(f"✓ Dataset transformado  → {output_path}")
    print(f"✓ Diccionario columnas  → {dict_path}")
    print(f"\n{df_dict.to_string(index=False)}")

    return df, df_dict


if __name__ == "__main__":
    transform()
