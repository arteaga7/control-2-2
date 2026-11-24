"""
bot2.py: Check if there is evidence in the corresponding folder and check if an email was sent
to all the people responsible in the 'Responsable' column of the Report
Executable:
uv run pyinstaller --onefile --name bot2 --paths . --collect-all extract_msg bot2.py
"""

from mod_2.mail import read_msg, notify, print_mail
from mod_2.report import read_xlsx, compare_col_content
from dotenv import load_dotenv
from datetime import datetime
import argparse
from pathlib import Path
import sys

# Fuerza UTF-8 en la salida (necesario en el .exe de PyInstaller en Windows)
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

# Carpeta real del .exe (o del .py si corres en desarrollo)
if getattr(sys, "frozen", False):
    PROJECT_DIR = Path(sys.executable).resolve().parent
else:
    PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

parser = argparse.ArgumentParser()
parser.add_argument("--unilever_path", type=Path,
                    default=Path(r"C:\SharePoints\Unilever"))
parser.add_argument("--control", default="OTB C3.2")
parser.add_argument("--month", default="10. Octubre")
parser.add_argument("--bot", default="Bot2")
args = parser.parse_args()
UNILEVER_PATH = args.unilever_path
CONTROL = args.control
MONTH = args.month
BOT = args.bot
print(f"\nSe ejecuta {BOT} del control {CONTROL} para el mes {MONTH}.\n")

if CONTROL == "OTB C3.2":
    SHAREPOINT_PATH = Path(UNILEVER_PATH) / \
        "Evidence GCH - Documents" / "2. Non SOX" / \
        "2026" / "OTC" / "Order Fulfilment" / "OTB C3.2"
    COLS_REPORT = ["Reponsible", "Approver", "Line Manager", "Director"]
    REPORT_NAME = "Monthly"
    SHEET_NAME = "Rep. Auditoria"
elif CONTROL == "OTB C5.2":
    SHAREPOINT_PATH = Path(UNILEVER_PATH) / \
        "Evidence GCH - Documents" / "1. SOX" / "2026" / \
        "OTC" / "Customer Billing" / "OTB C5.2"
    COLS_REPORT = ["Responsable", "Justification"]
    REPORT_NAME = "CHI"
    SHEET_NAME = "Reporte"
else:
    SHAREPOINT_PATH = Path(UNILEVER_PATH) / \
        "Evidence GCH - Documents" / "2. Non SOX" / \
        "2026" / "OTC" / "Order Management" / "OTB C2.2"
    COLS_REPORT = ["Reponsible", "Approver", "Line Manager", "Director"]
    REPORT_NAME = "Monthly"
    SHEET_NAME = "Rep. Auditoria"

REPORT_FOLDER = SHAREPOINT_PATH / MONTH / "1. Execution"
log_file = UNILEVER_PATH / "control_logs.txt"
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
nota = "\n--------------------------------\nSe envia el siguiente correo...\n--------------------------------\n"


def build_mail(cuerpo: str) -> str:
    return f"Hola Equipo,<br><br>\n{cuerpo}<br><br>\nSaludos.\n"


def main() -> bool:
    month_folder = SHAREPOINT_PATH / MONTH
    if not month_folder.is_dir():
        print(f"❌ La carpeta del mes no existe: '{month_folder}'")
        return False
    if not REPORT_FOLDER.is_dir():
        print(f"❌ La carpeta del reporte no existe: '{REPORT_FOLDER}'")
        return False

    df = read_xlsx(REPORT_FOLDER, COLS_REPORT, REPORT_NAME, SHEET_NAME)
    if df.empty:
        notify(
            f"🚨 No hay {REPORT_NAME} Report.{nota}", missing_report, CONTROL)
        return False

    mailto_report = read_msg(folder_path=REPORT_FOLDER, n_mails=1,
                             extension="*.msg", property="to")

    if len(mailto_report) == 0:
        notify(
            f"🚨 No hay correo de evidencia para evaluar.{nota}", missing_evidence, CONTROL)
        return False

    df = df.drop_duplicates(subset=[COLS_REPORT[0]])
    df_na = df[df[COLS_REPORT[0]].isna()]
    if not df_na.empty:
        notify(
            f"⚠️ Hay Responsables con valores nulos.\n{nota}", mising_responsibles, CONTROL)
        df = df[df[COLS_REPORT[0]].notna()]

    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Enviado", mails=mailto_report)
    print("--------------------------------")
    print("Personas responsables:\n", df[[COLS_REPORT[0], "Enviado"]], "\n")
    if df["Enviado"].all():
        notify(f"\n✅ Ejecución correcta.{nota}", bot2_success, CONTROL)
    else:
        df_not_sent = df.loc[df["Enviado"] == False,
                             [COLS_REPORT[0], "Enviado"]]
        print_mail(nota, df_not_sent, mismatch_sent_template, MONTH, CONTROL)
        print("\n⚠️  Control incompleto.")
    return True


if __name__ == "__main__":
    success = main()
    with log_file.open("a", encoding="utf-8") as f:
        f.write(
            f"{CONTROL}\t{BOT}\t{MONTH}\t{datetime.now():%Y-%m-%d %H:%M:%S}\t{success}\n")
