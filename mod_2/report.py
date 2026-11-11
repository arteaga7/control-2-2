# report.py
from pathlib import Path
import pandas as pd


def get_files(folder_path: Path, extension: str, name: str | None = None) -> list[Path]:
    """Regresa (ordenados) los archivos que coincidan con la extensión y, si name
    no es None, que contengan name. Ignora temporales de Office (~$...)."""
    return sorted(
        f for f in folder_path.glob(extension)
        if f.is_file()
        and not f.name.startswith("~$")
        and (name is None or name.lower() in f.name.lower())
    )


def read_report(file_path: str | Path, cols: list[str], sheet_name: str) -> pd.DataFrame:
    """Lee la hoja sheet_name con las columnas indicadas."""
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, usecols=cols, engine="openpyxl")
    except ValueError:
        print(
            f"No se encontró la hoja '{sheet_name}' o las columnas requeridas: {cols}")
        return pd.DataFrame()


def read_xlsx(folder_path: Path, cols: list[str], name: str, sheet_name: str) -> pd.DataFrame:
    """Read the xlsm file that contains name in its name."""
    xlsx_name = get_files(folder_path, extension="*.xlsx", name=name)
    if len(xlsx_name) > 0:
        xlsx_name = xlsx_name[0]
    else:
        print(f"No se encontró ningún archivo .xlsx en {folder_path}")
        return pd.DataFrame()

    return read_report(
        file_path=folder_path / xlsx_name,
        cols=cols,
        sheet_name=sheet_name
    )


def compare_col_content(df: pd.DataFrame, col: str, new_col: str,
                        mails: list[str]) -> pd.DataFrame:
    """Compare content in column "col" with "mails" and create a new column"""
    df = df.copy()
    df[col] = df[col].str.lower()
    df[new_col] = df[col].isin(mails)
    return df
