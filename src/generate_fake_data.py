"""
generate_fake_data.py
Genera un dataset sintético de 1000 encuestas con distribuciones plausibles
pero ficticias. Reemplaza fetch_survey.py + transform_columns.py para uso
en portafolio con datos ficticios de libre distribución.

Los datos se guardan directamente en staging/ con columnas ya normalizadas,
de modo que EDA.ipynb puede correr desde la celda de lectura de staging
(sin necesidad de correr fetch ni transform).

Uso:
    python src/generate_fake_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = BASE_DIR / "staging"

N = 1000
SEED = 42

COL_P11 = (
    "11_experiencia_de_uso_del_seguro_en_la_atención_de_una_enfermedad_o_emergencia_"
    "colocar_las_ideas_centrales_y_palabras_claves_mencionadas_por_la_persona_"
    "encuestada_ej_atención_de_un_parto_buena_experiencia_con_el_seguro_cobertura_"
    "de_hospitalización_y_gastos_al_100_opinión_regular_sobre_la_clínica_utilizada_"
    "dificultad_en_llenar_formularios_de_reembolso_colocar_n_a_en_caso_que_la_persona_"
    "encuestada_no_haya_brindado_información_registrar_experiencias_tanto_positivas_"
    "como_negativas"
)


def _pick(options, weights, n, rng):
    probs = np.array(weights, dtype=float) / sum(weights)
    return rng.choice(options, size=n, p=probs).tolist()


def _multichoice(singles, combos, sw, cw, n, rng):
    options = singles + combos
    probs = np.array(sw + cw, dtype=float)
    probs /= probs.sum()
    idx = rng.choice(len(options), size=n, p=probs)
    return [options[i] for i in idx]


def generate(output_stem: str = "survey_staging_fake") -> pd.DataFrame:
    STAGING_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Marca temporal
    base = datetime(2026, 1, 10, 8, 0, 0)
    timestamps = [
        (base + timedelta(minutes=int(rng.integers(0, 60 * 8 * 45)))).strftime("%d/%m/%Y %H:%M:%S")
        for _ in range(N)
    ]

    genero = _pick(["Femenino", "Masculino"], [62, 38], N, rng)

    rango_etario = _pick(
        ["18 a 24 años", "25 a 34 años", "35 a 44 años",
         "45 a 54 años", "55 a 64 años", "65 o más años"],
        [5, 22, 28, 24, 14, 7], N, rng,
    )

    ciudad = _pick(
        ["Ciudad Norte", "Puerto Central", "Valle Sur", "Montaña Alta",
         "Bahía Grande", "Río Verde", "Costa Nueva", "Laguna Alta"],
        [28, 18, 15, 12, 10, 8, 6, 3], N, rng,
    )

    vivienda = _pick(["Urbano", "Rural"], [58, 42], N, rng)

    actividad = _multichoice(
        singles=[
            "Ama de casa / Cuidado del hogar",
            "Emprendimiento o Pequeña/Mediana empresa familiar",
            "Empleado público (del Estado, gobiernos locales o empresas públicas)",
            "Trabajo informal / Jornalero",
            "Agricultura / Pesca / Ganadería",
            "Empleado privado",
        ],
        combos=[
            "Ventas y comercio de mercaderías, Emprendimiento o Pequeña/Mediana empresa familiar",
            "Trabajo informal / Jornalero, Agricultura / Pesca / Ganadería",
            "Emprendimiento o Pequeña/Mediana empresa familiar, Empleado privado",
        ],
        sw=[25, 22, 18, 15, 10, 8],
        cw=[5, 4, 3],
        n=N, rng=rng,
    )

    ingreso = _pick(
        ["Menos de 1 salario básico", "Al menos 1 salario básico",
         "Entre 1 y 2 salarios básicos", "Más de 2 salarios básicos",
         "Prefiere no responder"],
        [30, 32, 22, 10, 6], N, rng,
    )

    n_asegurados = rng.choice(
        [1, 2, 3, 4, 5, 6, 7, 8], size=N,
        p=[0.05, 0.18, 0.28, 0.24, 0.14, 0.07, 0.03, 0.01],
    ).tolist()

    grupos = _multichoice(
        singles=[
            "No Aplica",
            "Niños o niñas menores de 5 años",
            "Adultos mayores (más de 65 años)",
            "Mujeres embarazadas",
            "Personas con discapacidad",
        ],
        combos=[
            "Niños o niñas menores de 5 años, Adultos mayores (más de 65 años)",
            "Mujeres embarazadas, Niños o niñas menores de 5 años",
            "Adultos mayores (más de 65 años), Personas con discapacidad",
        ],
        sw=[38, 22, 18, 10, 6],
        cw=[3, 2, 1],
        n=N, rng=rng,
    )

    uso = _pick(["Sí", "No"], [72, 28], N, rng)

    necesidad = _pick(
        ["Acude regularmente",
         "Acude solo en caso de emergencias o malestar",
         "Acude y esta en tratamiento por alguna enfermedad o malestar",
         "Considera que se encuentra saludable"],
        [18, 38, 28, 16], N, rng,
    )

    exp_pool = [
        "BUENA EXPERIENCIA CON EL SERVICIO MÉDICO",
        "AFILIADO SATISFECHO CON LA ATENCIÓN RECIBIDA",
        "MUY BUENA EXPERIENCIA CON EL PLAN",
        "TUVO UN ACCIDENTE Y FUE BIEN ATENDIDO",
        "ATENCIÓN RÁPIDA Y EFICIENTE EN LA CLÍNICA",
        "COBERTURA COMPLETA EN CIRUGÍA RECIENTE",
        "CONFORME CON EL SERVICIO PERO ESPERA MEJORAS EN TIEMPOS DE ESPERA",
        "EXCELENTE SERVICIO EN ATENCIÓN DE EMERGENCIA",
        "AFILIADO CONFORME CON EL PLAN DE SALUD",
        "TUVO UN PARTO CON COBERTURA TOTAL Y BUENA ATENCIÓN",
        "REGULAR, TUVO DIFICULTADES CON EL PROCESO DE REEMBOLSO",
        "BUENA ATENCIÓN AL AFILIADO Y A LA FAMILIA",
        "N/A",
        "N/A",
        "N/A",
    ]
    exp_idx = rng.choice(len(exp_pool), size=N)
    experiencia_raw = [exp_pool[i] for i in exp_idx]

    p12 = _pick(
        ["Intentó recibir (o recibió) atención en centro médico público",
         "Pagaba de su bolsillo (ahorros o presupuesto familiar)",
         "No accedía a ningún servicio de salud",
         "Utilizaba medicina alternativa o remedios caseros"],
        [35, 40, 15, 10], N, rng,
    )

    p13 = _pick(
        ["Ha mejorado", "Mejoró mucho", "Mejoró poco",
         "Se mantiene igual", "Empeoró"],
        [28, 22, 20, 25, 5], N, rng,
    )

    p14 = _pick(
        ["Gasta menos", "Gasta igual (no percibe un cambio)", "Gasta poco", "Gasta más"],
        [42, 30, 20, 8], N, rng,
    )

    p15 = _pick(
        ["Entre $10 y $50 dólares", "Entre $50 y $100 dólares",
         "Entre $100 y $200 dólares", "Más de $200 dólares"],
        [35, 38, 18, 9], N, rng,
    )

    p16 = _pick(
        ["No dispone de otro seguro", "IESS",
         "Seguro Campesino", "Seguro privado adicional"],
        [45, 28, 18, 9], N, rng,
    )

    p17 = _pick(
        ["Se siente respaldado",
         "Sabe que cuenta con el servicio, pero le preocupa su situación de salud (o de la familia)",
         "No percibe un cambio",
         "No se siente respaldado"],
        [48, 28, 16, 8], N, rng,
    )

    df = pd.DataFrame({
        "marca_temporal": timestamps,
        "1_género_colocar_desde_la_base_de_datos": genero,
        "2_rango_etario_seleccionar_desde_la_base_de_datos": rango_etario,
        "3_ciudad_escribir_ej_quito": ciudad,
        "4_vivienda_y_habitabilidad_rural_referido_a_campo_y_periferias_de_ciudades_"
        "identificadas_como_tal_urbano_ciudades_y_centros_cantonales_o_provinciales": vivienda,
        "5_actividad_económica_de_la_persona_afiliada_indicar_la_o_las_principales_"
        "que_generan_ingresos_al_hogar": actividad,
        "6_ingreso_promedio_mensual_tomando_como_referencia_500_usd": ingreso,
        "7_no_de_personas_aseguradas_en_el_núcleo_familiar_escribir_número_sin_espacios_ej_4": n_asegurados,
        "8_grupos_de_atención_prioritaria_en_el_núcleo_asegurado": grupos,
        "9_uso_del_plan_salud_red_en_el_último_año": uso,
        "10_necesidad_del_asegurado_a_en_acudir_a_chequeos_médicos": necesidad,
        COL_P11: experiencia_raw,
        "12_antes_de_tener_el_plan_de_salud_plan_salud_red_en_caso_de_enfermedad_"
        "o_emergencias_la_familia": p12,
        "13_percepción_del_estado_de_salud_del_afiliado_a": p13,
        "14_gasto_en_salud_tomando_en_cuenta_el_uso_del_plan_salud_red": p14,
        "15_promedio_mensual_de_presupuesto_gastado_en_salud_en_el_núcleo_familiar": p15,
        "16_disponibilidad_de_otros_seguros_para_acceso_a_salud": p16,
        "17_percepción_de_respaldo_en_acceso_a_la_salud_debido_a_la_afiliación_"
        "al_plan_salud_red_de_salud": p17,
    })

    out_path = STAGING_DIR / f"{output_stem}.xlsx"
    df.to_excel(out_path, index=False)
    print(f"✓ Dataset sintético  → {out_path}  ({len(df)} filas × {len(df.columns)} cols)")

    df_dict = pd.DataFrame({
        "columna_original": list(df.columns),
        "columna_transformada": list(df.columns),
    })
    dict_path = STAGING_DIR / f"{output_stem}_column_dictionary.xlsx"
    df_dict.to_excel(dict_path, index=False)
    print(f"✓ Diccionario        → {dict_path}")
    print(f"\nSiguiente paso: abre EDA.ipynb y corre desde la celda que lee staging/")

    return df


if __name__ == "__main__":
    generate()
