# chi_report.py:
from pathlib import Path
import pandas as pd


def get_filenames(folder_path: Path, extension: str) -> list[str]:
    """Regresa los nombres de todos los archivos que coincidan
    con la extensión."""
    return [file.name for file in folder_path.glob(extension) if file.is_file()]


def read_report(file_path: str | Path, cols: list[str]) -> pd.DataFrame:
    """Lee el archivo '.xlsx' en la hoja 'Rep. Auditoria' y extrae las columnas
    "Reponsible", "Approver", "Line Manager", "Director"."""
    df = pd.DataFrame()
    if not file_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el Monthly Report: {file_path}"
        )
    try:
        df = pd.read_excel(
            file_path,
            sheet_name="Rep. Auditoria",
            usecols=cols,
            engine="openpyxl"
        )
    except ValueError as error:
        print(
            "No se encontro la hoja o las columnas esperadas. "
            f"Columnas requeridas: {cols}"
        )
    return df


def read_xlsx(folder_path: Path, cols: list[str]) -> pd.DataFrame:
    """Read the firts xlsm file, it should be only one."""
    xlsx_name = get_filenames(folder_path, extension="*.xlsx")
    if len(xlsx_name) > 0:
        xlsx_name = xlsx_name[0]
    else:
        print(f"No se encontró ningún archivo .xlsx en {folder_path}")
        return pd.DataFrame()

    return read_report(
        file_path=folder_path / xlsx_name,
        cols=cols
    )


def compare_col_content(df: pd.DataFrame, col: str, new_col: str,
                        mails: list[str]) -> pd.DataFrame:
    """Compare content in column "col" with "mails and create a new column"""
    df = df.copy()
    df[new_col] = df[col].isin(mails)
    return df
