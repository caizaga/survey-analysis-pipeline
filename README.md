# Survey Analysis Pipeline

Pipeline ETL completo para el procesamiento, limpieza y análisis de encuestas de campo aplicado a un estudio de impacto de microseguros de salud en población vulnerable. Incluye exportación a Google Sheets y visualización en Looker Studio.

## Contexto del problema

Los microseguros de salud buscan cubrir a poblaciones con acceso limitado a servicios médicos formales. Este proyecto analiza los resultados de una encuesta de campo aplicada a afiliados de un plan de salud, con el objetivo de responder tres preguntas concretas:

1. **¿El seguro reduce la carga económica real de las familias?**
2. **¿Los afiliados perciben una mejora en su situación de salud?**
3. **¿Qué perfiles concentran mayor vulnerabilidad o menor aprovechamiento del plan?**

## Hallazgos principales

El análisis revela una historia en dos mitades: **el seguro cumple su promesa de acceso, pero no ha resuelto la ansiedad de sus afiliados.**

**El impacto económico es real, especialmente en los más vulnerables.** El segmento de menor ingreso (menos de 1 SBU) reporta mayoritariamente un menor gasto en salud desde su afiliación. Este efecto es aún más significativo considerando que el 45% de los encuestados no dispone de ningún otro seguro — para ellos, este plan no es una opción complementaria, es su única red de protección.

**El uso sigue siendo reactivo, no preventivo.** Solo 1 de cada 5 afiliados acude a chequeos de forma regular; el 38% lo hace únicamente ante emergencias. Los datos muestran una correlación positiva entre uso preventivo y mejor percepción del estado de salud, lo que sugiere que promover el acceso proactivo al sistema tendría un impacto directo en los resultados del plan.

**El 28% más revelador no está insatisfecho — está ansioso.** Una cuarta parte de los afiliados declara saber que cuenta con el servicio, pero sigue preocupado por su situación de salud. Este grupo no representa un problema de cobertura: representa un problema de acompañamiento. Confundir ambos llevaría a tomar decisiones incorrectas.

## ¿Qué hace?

1. **Ingesta** — descarga respuestas desde un Google Form / Google Sheets (`fetch_survey.py`)
2. **Transformación** — normaliza nombres de columnas y estructura el dataset (`transform_columns.py`)
3. **Análisis exploratorio** — limpieza de datos, recodificación, imputación y construcción del dataset analítico (`notebooks/EDA.ipynb`)
4. **Crosstabs** — genera tablas de cruce (n, % fila, % columna) en Excel con formato (`src/crosstabs.py`)
5. **Exportación** — sube el dataset limpio y el diccionario de columnas a Google Sheets para consumo en Looker Studio (`upload_to_sheets.py`)

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Manipulación de datos | pandas, numpy |
| Lectura/escritura Excel | openpyxl, gspread-dataframe |
| Google Sheets API | gspread (OAuth2) |
| Visualización | Looker Studio |
| Entorno | Jupyter Notebook (Anaconda) |

## Estructura del proyecto

```
survey-analysis-pipeline/
├── src/
│   ├── fetch_survey.py          # Descarga datos desde Google Sheets
│   ├── transform_columns.py     # Normaliza nombres de columnas
│   ├── crosstabs.py             # Genera tablas de cruce en Excel
│   ├── upload_to_sheets.py      # Sube datos limpios a Google Sheets
│   └── generate_fake_data.py    # Genera datos sintéticos para demo
├── notebooks/
│   ├── EDA.ipynb                # Análisis exploratorio y limpieza principal
│   └── quality_checks.ipynb     # Validación de calidad del dataset
├── raw/                         # Datos crudos descargados (gitignored)
├── staging/                     # Datos transformados intermedios (gitignored)
├── output/                      # Crosstabs y documentos exportados (gitignored)
├── config.yaml                  # Configuración de fuente de datos
├── pipeline.py                  # Script de orquestación del pipeline completo
└── requirements.txt
```

## Cómo correrlo (con datos sintéticos)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales de Google

El proyecto usa OAuth2 de gspread. La primera vez que corras `upload_to_sheets.py` se abrirá un navegador para autenticarte. Las credenciales quedan cacheadas en `~/.config/gspread/`.

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env y agrega tu Spreadsheet ID de destino
```

### 4. Generar datos sintéticos

```bash
python src/generate_fake_data.py
```

Esto crea `staging/survey_staging_fake.xlsx` con 1000 registros ficticios y distribuciones plausibles.

### 5. Correr el análisis

Abre `notebooks/EDA.ipynb` en Jupyter y corre desde la celda que lee el archivo de staging (puedes saltar las celdas de fetch y transform si usas datos sintéticos).

### 6. Generar crosstabs

Desde el notebook, ejecuta la celda con `generate_all(df_le, df_long_actividad, df_long_grupos)`. El resultado se guarda en `output/crosstabs.xlsx`.

### 7. Subir a Google Sheets

Asegúrate de tener `SHEETS_OUTPUT_ID` configurado en tu entorno, luego ejecuta la celda con `upload_all(df_le)`.

## Datos

Este repositorio usa datos **sintéticos** generados por `src/generate_fake_data.py`. Las distribuciones son plausibles para un estudio de seguros de salud en contexto latinoamericano, pero los valores son ficticios y no representan a ninguna empresa o persona real.
