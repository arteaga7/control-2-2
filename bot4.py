"""
bot4.py: Check if there are evidences (*.msg) in "2. Justification" folder...
Executable:
uv run pyinstaller --onefile --name bot4 --paths . --collect-all extract_msg bot4.py
"""

import sys
from pathlib import Path
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
from mod_2.report import read_xlsx, compare_col_content
from mod_2.mail import read_msg
from mod_4.inbox import post_inbox, extraer_from_carpeta

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
parser.add_argument("--capgemini_path", type=Path,
                    default=Path(r"C:\SharePoints\Unilever\SKY_CE - emails_capgemini"))
args = parser.parse_args()

MONTH = args.month
UNILEVER_PATH = args.unilever_path
CAPGEMINI_FOLDER_PATH = args.capgemini_path
CONTROL = Path(UNILEVER_PATH).name
BOT = "Bot4"
print(f"\nSe ejecuta {BOT} de control {CONTROL}...\n")
REPORT_FOLDER = Path(UNILEVER_PATH) / MONTH / "1. Execution"
JUSTIFICATION_FOLDER = Path(UNILEVER_PATH) / MONTH / "2. Justification"
APPOVAL_FOLDER = Path(UNILEVER_PATH) / MONTH / "3. Approval"

if CONTROL == "OTB C3.2":
    COLS_REPORT = ["Reponsible", "Approver", "Line Manager", "Director"]
    REPORT_NAME = "Monthly"
    SHEET_NAME = "Rep. Auditoria"
else:
    COLS_REPORT = ["Responsable", "Justification"]
    REPORT_NAME = "CHI"
    SHEET_NAME = "Reporte"

log_file = UNILEVER_PATH / f"{CONTROL}_logs.txt"

# --------Mail content ------------
success_template = f"""Control "{CONTROL}" completo para el mes "{MONTH}"."""
# ----------------------------------


def bot4(df: pd.DataFrame):
    """Specific functions of Bot4"""
    from_justification = []
    from_justification = read_msg(folder_path=JUSTIFICATION_FOLDER,
                                  extension="*.msg", property="sender")
    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Feedback", mails=from_justification)
    print("Personas que respondieron (mandaron email de justificacion):")
    # print(df[[COLS_REPORT[0], "Feedback"]], "\n")
    # df_feed = df[df["Feedback"] == True]
    df_no_feed = df[df["Feedback"] == False]

    if not df_no_feed.empty:
        # post_inbox()
        print("Ya se actualizaron los mails")
        # remitentes = extraer_from_carpeta(CAPGEMINI_FOLDER_PATH)
        remitentes = ['Lorena.Espindola@unilever.com',
                      'colatam.automations@unilever.com', 'noreply_unilever@engage.mail.microsoft']
        print(remitentes)
        df_no_feed = compare_col_content(df=df_no_feed, col=COLS_REPORT[0],
                                         new_col="Inbox", mails=remitentes)
        df_inbox = df_no_feed.loc[df_no_feed["Inbox"] == True,
                                  [COLS_REPORT[0], "Feedback", "Inbox"]]
        df_no_inbox = df_no_feed.loc[df_no_feed["Inbox"] == False,
                                     [COLS_REPORT[0], "Feedback", "Inbox"]]
        print(f"df_inbox:\n{df_inbox}")
        print(f"df_no_inbox:\n{df_no_inbox}")

    return


def main():
    month_folder = UNILEVER_PATH / MONTH
    if not month_folder.is_dir():
        print(f"[ERROR] La carpeta del mes no existe: {month_folder}")
        sys.exit(1)
    if not REPORT_FOLDER.is_dir():
        print(f"[ERROR] La carpeta del reporte no existe: {REPORT_FOLDER}")
        sys.exit(1)

    df = read_xlsx(REPORT_FOLDER, COLS_REPORT, REPORT_NAME, SHEET_NAME)
    if df.empty:
        print(f"No hay {REPORT_NAME} Report. Ejecute 'automatizacion2.bat' para mandar correo correspondiente " +
              "o si hizo modificaciones recientemente, espere unos minutos y vuelva a intentar.")
        return

    df_time = pd.read_csv(
        log_file, sep="\t", header=None,
        names=["Control", "Bot", "Fecha"],
        parse_dates=["Fecha"],
    )
    last_exec = df_time.loc[df_time["Bot"] == "Bot2", "Fecha"].max()
    if not (datetime.now() > last_exec + timedelta(days=0)):
        print("El Bot2 se ejecuto recientemente (menos de 2 dias), espere 2 dias mas para ejecutar Bot4.")
        return

    mailto_report = read_msg(folder_path=REPORT_FOLDER, n_mails=1,
                             extension="*.msg", property="to")
    if len(mailto_report) == 0:
        print(
            f"No hay evidencia en la carpeta {REPORT_FOLDER}. Ejecute 'automatizacion2.bat' para mandar el correo correspondiente.")
        return

    df = df.drop_duplicates(subset=[COLS_REPORT[0]])
    # Se ignoran los que no tienen responsables
    df = df[df[COLS_REPORT[0]].notna()]
    df = compare_col_content(df=df, col=COLS_REPORT[0],
                             new_col="Enviado", mails=mailto_report)

    # Bot2 does not performe the following
    bot4(df)


if __name__ == "__main__":
    main()
