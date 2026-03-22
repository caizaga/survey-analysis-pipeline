# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ETL pipeline for processing health insurance survey data from Google Forms/Sheets. Uses synthetic data (1000 records) for portfolio demonstration. The pipeline downloads, cleans, analyzes, and exports survey data to Google Sheets for Looker Studio visualization.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # Set SHEETS_OUTPUT_ID in .env
# Edit config.yaml → set source spreadsheet_id and sheet_name
```

## Common Commands

**Generate synthetic data (portfolio mode):**
```bash
python src/generate_fake_data.py
# Output: staging/survey_staging_fake.xlsx
```

**Run the ETL pipeline (requires Google credentials):**
```bash
python pipeline.py  # fetch + transform steps
```

**Run individual steps:**
```bash
python src/fetch_survey.py       # Download from Google Sheets
python src/transform_columns.py  # Normalize column names
```

**Launch notebooks for analysis:**
```bash
jupyter notebook notebooks/EDA.ipynb            # Main cleaning & analysis
jupyter notebook notebooks/quality_checks.ipynb # Data validation
```

**Generate crosstabs and upload (from inside EDA.ipynb):**
```python
from src.crosstabs import generate_all
generate_all(df_le, df_long_actividad, df_long_grupos)  # → output/crosstabs.xlsx

from src.upload_to_sheets import upload_all
upload_all(df_le)  # → Google Sheets
```

There is no formal test suite or linter configured. Data quality checks are in `notebooks/quality_checks.ipynb`.

## Architecture

The pipeline runs in sequential stages:

```
Google Sheets (source)
  → fetch_survey.py       → raw/survey_raw_*.xlsx
  → transform_columns.py  → staging/survey_staging_*.xlsx  (+column dictionary)
  → EDA.ipynb             → df_le  (cleaned DataFrame, lives in notebook memory)
  → crosstabs.py          → output/crosstabs.xlsx
  → upload_to_sheets.py   → Google Sheets (data tab + dictionary tab)
  → Looker Studio (external visualization)
```

**Module responsibilities:**
- `pipeline.py` — orchestrates fetch + transform only; notebook steps are manual
- `src/fetch_survey.py` — OAuth2 download from Google Sheets via `gspread`
- `src/transform_columns.py` — normalizes column names (spaces→underscores, lowercase), creates column dictionary
- `src/generate_fake_data.py` — generates 1000 synthetic records with realistic distributions
- `src/crosstabs.py` — builds 17 formatted Excel cross-analyses (n, % row, % col) supporting multi-choice variables
- `src/upload_to_sheets.py` — uploads cleaned DataFrame and column dictionary to separate Google Sheets tabs

**Key design points:**
- Each `src/` module is independently callable (each has a `main()` or primary function)
- `raw/`, `staging/`, `output/` directories are gitignored — data never committed
- Google OAuth2 tokens are cached at `~/.config/gspread/` after first browser login
- The cleaned DataFrame `df_le` is the central artifact of the analysis, produced in `EDA.ipynb` and consumed by both `crosstabs.py` and `upload_to_sheets.py`

## Configuration

**`config.yaml`** — source spreadsheet:
```yaml
google_sheets:
  spreadsheet_id: "SOURCE_SPREADSHEET_ID"
  sheet_name: "Hoja1"
  range: ""  # optional, e.g. "A1:Z1000"
```

**`.env`** — destination spreadsheet:
```
SHEETS_OUTPUT_ID=DESTINATION_SPREADSHEET_ID
```
