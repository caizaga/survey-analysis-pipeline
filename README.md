# Survey Analysis Pipeline

Pipeline ETL para el procesamiento, limpieza y análisis de una encuesta de campo sobre impacto de microseguros de salud en población vulnerable. Cubre el flujo completo desde Google Forms hasta un dashboard en Looker Studio, pasando por limpieza, recodificación y tablas de cruce en Python.

**Dashboard:** [Ver en Looker Studio](https://lookerstudio.google.com/reporting/597550ec-2ae1-4998-8595-81134096159d) · Dataset: 1 000 registros sintéticos con distribuciones realistas de un contexto latinoamericano

## Contexto del problema

Los microseguros de salud buscan cubrir a poblaciones con acceso limitado a servicios médicos formales. Este proyecto analiza los resultados de una encuesta de campo aplicada a afiliados de un plan de salud, con el objetivo de responder tres preguntas concretas:

1. **¿El seguro reduce la carga económica real de las familias?**
2. **¿Los afiliados perciben una mejora en su situación de salud?**
3. **¿Qué perfiles concentran mayor vulnerabilidad o menor aprovechamiento del plan?**

## Hallazgos principales

El análisis identifica tres tensiones centrales entre el diseño del plan y el comportamiento real de sus afiliados.

**Impacto económico positivo, pero concentrado.** El 43 % reporta menor gasto en salud desde la afiliación, con mayor intensidad en el segmento de ingreso bajo (menos de 1 SBU). Para el 45 % que no dispone de ningún otro seguro, el plan funciona como única red de protección — lo que eleva el costo social de cualquier discontinuidad en la cobertura.

**Uso reactivo como patrón dominante.** El 72 % utilizó el plan en el último año, pero solo 1 de cada 5 afiliados accede de forma preventiva. El 38 % acude exclusivamente ante emergencias. Los datos sugieren que el diseño de acceso no está generando el cambio de comportamiento sanitario que justificaría el plan a largo plazo.

**Cobertura percibida ≠ seguridad percibida.** Solo el 47 % se siente plenamente respaldado. El 28 % declara saber que cuenta con el servicio, pero mantiene preocupación activa por su situación de salud. Este segmento no requiere más cobertura — requiere acompañamiento. Tratarlo como problema de acceso llevaría a intervenciones equivocadas.

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
