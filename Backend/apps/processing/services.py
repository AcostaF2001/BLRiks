from pathlib import Path
import re
import unicodedata

import pandas as pd


def normalize_column_name(column_name):
    """
    Normaliza el nombre de una columna para hacer comparaciones flexibles.

    Transformaciones que aplica:
    - convierte a minúsculas
    - elimina espacios al inicio y al final
    - elimina tildes
    - reemplaza espacios o guiones por underscore
    - elimina caracteres especiales innecesarios

    Ejemplos:
    - "Identificador" -> "identificador"
    - "Categoría" -> "categoria"
    - "Valor Base" -> "valor_base"
    """
    value = str(column_name).strip().lower()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[\s\-]+", "_", value)
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value


def get_column_aliases():
    """
    Define las variantes aceptadas para cada columna estándar del sistema.

    Esto permite que el backend soporte archivos con encabezados
    ligeramente distintos sin romper el procesamiento.
    """
    return {
        "Identificador": {"identificador", "id", "codigo", "identificacion"},
        "Nombre": {"nombre", "nombres", "cliente", "persona"},
        "Valor_base": {"valor_base", "valorbase", "valor", "monto", "valor_inicial"},
        "Categoría": {"categoria", "categoría", "tipo", "grupo"},
        "Fecha": {"fecha", "fecha_registro", "fecha_corte", "fecha_proceso"},
    }


def map_dataframe_columns(df):
    """
    Mapea las columnas reales del archivo a los nombres estándar del sistema.

    Por ejemplo:
    - 'identificador' -> 'Identificador'
    - 'categoria' -> 'Categoría'

    Si falta alguna columna requerida, lanza una excepción detallada.
    """
    aliases = get_column_aliases()

    normalized_original_columns = {
        original_col: normalize_column_name(original_col)
        for original_col in df.columns
    }

    rename_map = {}
    missing_columns = []

    for canonical_name, valid_aliases in aliases.items():
        matched_original = None

        for original_col, normalized_col in normalized_original_columns.items():
            if normalized_col in valid_aliases:
                matched_original = original_col
                break

        if matched_original:
            rename_map[matched_original] = canonical_name
        else:
            missing_columns.append(canonical_name)

    if missing_columns:
        raise ValueError(
            "Faltan columnas requeridas en el archivo: "
            + ", ".join(missing_columns)
        )

    return df.rename(columns=rename_map)


def clean_dataframe(df):
    """
    Aplica una limpieza básica al DataFrame antes de procesarlo.

    Reglas:
    - elimina filas completamente vacías
    - limpia espacios de columnas de texto
    - reemplaza vacíos por None
    - convierte Valor_base a numérico
    - convierte Fecha a datetime
    """
    df = df.dropna(how="all").copy()

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    df = df.replace({"": None, "nan": None, "None": None})

    if "Valor_base" in df.columns:
        df["Valor_base"] = pd.to_numeric(df["Valor_base"], errors="coerce")

    if "Fecha" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")

    return df


def read_excel_file(file_path):
    """
    Lee un archivo Excel desde disco y devuelve un DataFrame.

    Actualmente se toma la primera hoja del archivo.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    df = pd.read_excel(path)
    return df


def process_uploaded_excel(file_path):
    """
    Orquesta el procesamiento base del archivo Excel.

    Flujo:
    1. lee el archivo
    2. imprime columnas detectadas para facilitar debugging
    3. mapea columnas a formato estándar
    4. limpia la información
    5. devuelve DataFrame y métricas básicas
    """
    df = read_excel_file(file_path)

    print("COLUMNAS LEÍDAS DEL EXCEL:", list(df.columns))

    df = map_dataframe_columns(df)
    df = clean_dataframe(df)

    total_rows = len(df)
    processed_rows = len(df)

    return {
        "dataframe": df,
        "total_rows": total_rows,
        "processed_rows": processed_rows,
    }