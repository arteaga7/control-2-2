"""
bot2.py: Check if there is evidence in the corresponding folder and
check if an email was sent to all the people responsible in the 'Responsable' column
of the Report
Executable:
uv run pyinstaller --onefile --name bot2 --paths . --collect-all extract_msg bot2.py
"""

import sys
from pathlib import Path
import argparse
from dotenv import load_dotenv
from mod_2.report import read_xlsx, compare_col_content
from mod_2.mail import read_msg, notify, print_mail

# Carpeta real del .exe (o del .py si corres en desarrollo)
if getattr(sys, "frozen", False):
    PROJECT_DIR = Path(sys.executable).resolve().parent
else:
    PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

parser = argparse.ArgumentParser()
parser.add_argument("--month", default="10. Octubre")
parser.add_argument("--unilever_path", type=Path,
                    default=Path(r"C:\SharePoints\Unilever\IOPs Control Documentos Nuevo - Deliver\OTB C3.2"))
args = parser.parse_args()

MONTH = args.month
# UNILEVER_PATH = r"C:\SharePoints\Unilever\IOPs Control Documentos Nuevo - Deliver\OTB C3.2"
UNILEVER_PATH = args.unilever_path
CONTROL = UNILEVER_PATH.name[-3:]
print(f"\nSe ejecuta control {CONTROL}...\n")
if CONTROL == "3.2":
    COLS_REPORT = ["Reponsible", "Approver", "Line Manager", "Director"]
    REPORT_FOLDER = Path(UNILEVER_PATH) / MONTH / "1. Execution"
    REPORT_NAME = "Monthly"
    SHEET_NAME = "Rep. Auditoria"
else:
    COLS_REPORT = ["Reponsable", "Approver", "Justificacion", "Director"]
    REPORT_FOLDER = Path(UNILEVER_PATH) / MONTH / "1. CHI Report + Request"
    REPORT_NAME = "CHI"
    SHEET_NAME = "Reporte"

# --------Mail content ------------
saludo = "Hola Equipo,<br><br>\n"
despedida = "Saludos.\n"
missing_report = f"""{saludo}Por favor subir el {REPORT_NAME} Report con la estructura adecuada para el mes "{MONTH}" del control "{CONTROL}".<br><br>
{despedida}"""
missing_evidence = f"""{saludo}Por favor subir la evidencia faltante para el mes "{MONTH}" del control "{CONTROL}".<br><br>\n{despedida}"""
mising_responsibles = f"""{saludo}Por favor subir el {REPORT_NAME} Report con los responsables completos
para el mes "{MONTH}" del control "{CONTROL}".<br><br>\n{despedida}"""
mismatch_sent_template = """Hola Equipo,<br><br>
Por favor mandar un correo complementario a las personas que faltaron:<br><br>
{df}
<br><br>
Para el mes "{mes}" del control "{control}".
<br><br>
Saludos.\n"""
bot2_success = f"""{saludo}La evidencia se recibio con exito para el mes "{MONTH}" del control "{CONTROL}".<br><br>\n{despedida}"""
nota = "\nSe envia el sig. correo...\n\n"
# ----------------------------------


def build_mail(cuerpo: str) -> str:
    return f"Hola Equipo,<br><br>\n{cuerpo}<br><br>\nSaludos.\n"


def main():
    df = read_xlsx(REPORT_FOLDER, COLS_REPORT, REPORT_NAME, SHEET_NAME)
    if df.empty:
        notify(
            f"No hay {REPORT_NAME} Report.{nota}", missing_report)
        return

    mailto_report = read_msg(folder_path=REPORT_FOLDER, n_mails=1,
                             extension="*.msg", property="to")

    if len(mailto_report) == 0:
        notify(
            f"No hay correo de evidencia para evaluar.{nota}", missing_evidence)
        return

    df = df.drop_duplicates(subset=[COLS_REPORT[0]])
    df_na = df[df[COLS_REPORT[0]].isna()]
    if not df_na.empty and CONTROL == "3.2":
        print(
            f"Hay Responsables con valores nulos.{nota}", mising_responsibles)
        df = df[df[COLS_REPORT[0]].notna()]

    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Enviado", mails=mailto_report)
    print("Personas responsables:")
    print(df[[COLS_REPORT[0], "Enviado"]], "\n")
    if df["Enviado"].all():
        notify(f"Ejecución correcta.{nota}",  bot2_success)
    else:
        df_not_sent = df[(df["Enviado"] == False)]
        df_not_sent = df_not_sent[[COLS_REPORT[0], "Enviado"]]
        print_mail(nota, df_not_sent, mismatch_sent_template, MONTH, CONTROL)


if __name__ == "__main__":
    main()
