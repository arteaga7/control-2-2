"""
bot4.py: Check if there are evidences (*.msg) in "2. Justification" folder...
Executable:
uv run pyinstaller --onefile --name bot4 --paths . --collect-all extract_msg bot4.py
"""
from mod_4.approve import approve_msg
from mod_4.inbox import post_inbox, extract_from_inbox
from mod_2.mail import read_msg, print_mail
from mod_2.report import read_xlsx, compare_col_content
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
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
parser.add_argument("--bot", default="Bot4")
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
JUSTIFICATION_FOLDER = SHAREPOINT_PATH / MONTH / "2. Justification"
APPOVAL_FOLDER = SHAREPOINT_PATH / MONTH / "3. Approval"
CAPGEMINI_FOLDER_PATH = Path(UNILEVER_PATH) / "SKY_CE - emails_capgemini"
log_file = UNILEVER_PATH / "control_logs.txt"
retardo = 5
# --------Mail content ------------
saludo = "Hola Equipo,<br><br>"
despedida = "<br><br>Saludos."
missing_justification_mails = """Hola Equipo,<br><br>
Por favor subir al SharePoint los mails de justificacion faltantes:<br><br>
{df}
<br><br>
Para el mes "{mes}" del control "{control}".
<br><br>
Saludos."""
no_justification_mails = """Hola Equipo,<br><br>
Las siguientes personas no enviaron sus emails de justificacion:<br><br>
{df}
<br><br>
Para el mes "{mes}" del control "{control}".<br><br>
Por favor enviar email a sus respectivos WL2 (Line Manager).
<br><br>
Saludos."""
success_template = f"""{saludo}Control "{CONTROL}" completo para el mes "{MONTH}"{despedida}."""
nota = "\n--------------------------------\nSe envia el siguiente correo...\n--------------------------------\n"


def approval_22_or_32(df_no_feed: pd.DataFrame, df_feed: pd.DataFrame):
    """This code is executed if df_feed is not empty and control is 2.2 or 3.2."""
    approved = approve_msg(APPOVAL_FOLDER)
    if approved:
        if df_no_feed.empty:
            print(
                f"\n✅ Control {CONTROL} aprobado para:\n{df_feed}\nNo se ejecuta Bot6.")
        else:
            print(
                f"\n⚠️ Control {CONTROL} incompleto, faltan usuarios por responder.")
    else:
        print(f"\n⚠️ Control {CONTROL} incompleto, no hay mail de aprobacion.")


def df_no_feed_not_empty(df_no_feed: pd.DataFrame, last_exec_bot2: datetime):
    """This code is executed if df_no_feed is not empty."""
    # post_inbox()
    remitentes = extract_from_inbox(CAPGEMINI_FOLDER_PATH, last_exec_bot2)
    if len(remitentes) > 0:
        print("Se encontraron emails en inbox de los siguientes responsables:\n")
        for i in remitentes:
            print(i)
    df_no_feed = compare_col_content(df=df_no_feed, col=COLS_REPORT[0],
                                     new_col="Inbox", mails=remitentes)
    df_inbox = df_no_feed.loc[df_no_feed["Inbox"] == True,
                              [COLS_REPORT[0], "Inbox"]]
    df_no_inbox = df_no_feed.loc[df_no_feed["Inbox"] == False,
                                 [COLS_REPORT[0], "Inbox", COLS_REPORT[2]]]

    if not df_inbox.empty:
        print_mail(nota, df_inbox, missing_justification_mails, MONTH, CONTROL)
    if not df_no_inbox.empty:
        print_mail(nota, df_no_inbox, no_justification_mails, MONTH, CONTROL)


def bot4(df: pd.DataFrame, last_exec_bot2: datetime):
    """Specific functions of Bot4"""
    from_justification = []
    from_justification = read_msg(folder_path=JUSTIFICATION_FOLDER,
                                  extension="*.msg", property="sender")
    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Feedback", mails=from_justification)
    print("--------------------------------")
    print("Personas que respondieron (mandaron email de justificacion):")
    print(df[[COLS_REPORT[0], "Feedback"]], "\n")
    df_feed = df[df["Feedback"] == True]
    df_no_feed = df[df["Feedback"] == False]
    if not df_no_feed.empty:
        df_no_feed_not_empty(df_no_feed, last_exec_bot2)
    if not df_feed.empty and CONTROL in ["OTB C2.2", "OTB C3.2"]:
        approval_22_or_32(df_no_feed, df_feed)
    if not df_feed.empty and CONTROL == "OTB C5.2":
        pass


def main():
    month_folder = SHAREPOINT_PATH / MONTH
    if not month_folder.is_dir():
        print(f"❌ La carpeta del mes no existe: '{month_folder}'")
        return False
    if not REPORT_FOLDER.is_dir():
        print(f"❌ La carpeta del reporte no existe: '{REPORT_FOLDER}'")
        return False

    df = read_xlsx(REPORT_FOLDER, COLS_REPORT, REPORT_NAME, SHEET_NAME)
    if df.empty:
        print(f"🚨 No hay {REPORT_NAME} Report. Ejecute 'Bot2' para mandar correo correspondiente " +
              "o si hizo modificaciones recientemente, espere unos minutos y vuelva a intentar.")
        return False

    df_time = pd.read_csv(
        log_file, sep="\t", header=None, names=["Control", "Bot", "Mes", "Fecha", "Exito"], parse_dates=["Fecha"]
    )
    df_time = df_time[(df_time["Control"] == CONTROL) &
                      (df_time["Mes"] == MONTH) &
                      (df_time["Exito"] == True)]
    last_exec_bot2 = df_time.loc[df_time["Bot"] == "Bot2", "Fecha"].max()
    print(
        f"El Bot2 del control '{CONTROL}' se ejecuto correctamente el {last_exec_bot2}.")
    if not (datetime.now() > last_exec_bot2 + timedelta(minutes=retardo)):
        print(
            f"🚨 El Bot2 se ejecuto recientemente (menos de {retardo} minutes), espere {retardo} minutes mas para ejecutar Bot4.")
        return False

    mailto_report = read_msg(folder_path=REPORT_FOLDER, n_mails=1,
                             extension="*.msg", property="to")
    if len(mailto_report) == 0:
        print(
            f"🚨 No hay evidencia en la carpeta '{REPORT_FOLDER}'. Ejecute 'Bot2' para mandar el correo correspondiente.")
        return False

    df = df.drop_duplicates(subset=[COLS_REPORT[0]])
    df_na = df[df[COLS_REPORT[0]].isna()]
    if not df_na.empty:
        print("⚠️ Hay Responsables con valores nulos")
    df = df[df[COLS_REPORT[0]].notna()]
    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Enviado", mails=mailto_report)
    # Bot2 does not performe the following
    bot4(df, last_exec_bot2)
    return True


if __name__ == "__main__":
    success = main()
    with log_file.open("a", encoding="utf-8") as f:
        f.write(
            f"{CONTROL}\t{BOT}\t{MONTH}\t{datetime.now():%Y-%m-%d %H:%M:%S}\t{success}\n")
