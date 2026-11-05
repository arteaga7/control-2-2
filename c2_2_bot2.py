"""
c2_2_bot2.py: Check if there is evidence in the folder 'Execution' and
check if an email was sent to all the people responsible in the 'Responsable' column
of the Monthly_Report
"""

from pathlib import Path
import argparse
from mod_2_2.monthly_report import read_xlsx, compare_col_content
from mod_2_2.mail import read_msg, notify, print_mail


PROJECT_DIR = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--month", default="10. Octubre")
parser.add_argument("--unilever_path", type=Path, default=PROJECT_DIR)
args = parser.parse_args()
MONTH = "10. Octubre"  # args.month
UNILEVER_PATH = Path(r"C:\SharePoints")  # args.unilever_path

FOLDER_PATH = (
    UNILEVER_PATH / "Unilever"
    / "IOPs Control Documentos Nuevo - OTB C2.2"
)
COLS_REPORT = ["Reponsible", "Approver", "Line Manager", "Director"]
REPORT_FOLDER = Path(FOLDER_PATH) / MONTH / "Execution"

# --------Mail content ------------
missing_report = """Hola Equipo,<br><br> 
Por favor subir el Monthly Report con la estructura adecuada.<br><br>
Saludos.\n"""
missing_evidence = """Hola Equipo,<br><br>
Por favor subir la evidencia faltante.<br><br>
Saludos.\n"""
mising_responsibles = """Hola Equipo,<br><br>
Por favor subir el Monthly Report con los responsables completos.<br><br>
Saludos.\n"""
mismatch_sent_template = """Hola Equipo,<br><br>
Por favor mandar un correo complementario a las personas que faltaron:<br><br>
{df}
<br><br>
Saludos.\n"""
c2_2_bot2_success = """Hola Equipo,<br><br>
La evidencia se recibio con exito.<br><br>
Saludos.\n"""
# ----------------------------------


def main():
    df = read_xlsx(REPORT_FOLDER, COLS_REPORT)
    mailto_report = read_msg(folder_path=REPORT_FOLDER, n_mails=1,
                             extension="*.msg", property="to")

    if df.empty:
        notify(
            "No hay CHI_Report.\nSe envia el sig. correo...\n\n", missing_report)
        return

    if len(mailto_report) == 0:
        notify("No hay correo de evidencia para evaluar.\nSe envia el sig. correo...\n\n", missing_evidence)
        return

    df_na = df[df["Reponsible"].isna()]
    if not df_na.empty:
        print("Hay Responsables con valores nulos.\nSe envia el sig. correo...\n\n",
              mising_responsibles)
        df = df[df["Reponsible"].notna()]

    if len(mailto_report) > 0:
        df = compare_col_content(df=df, col="Reponsible",
                                 new_col="Enviado", mails=mailto_report)
        print("Personas responsables:")
        print(df[["Reponsible", "Enviado"]], "\n")
        if df["Enviado"].all():
            notify("Ejecución correcta. Se envia el sig. correo...\n\n",
                   c2_2_bot2_success)
        else:
            df_not_sent = df[(df["Enviado"] == False)]
            df_not_sent = df_not_sent[["Reponsible", "Enviado"]]
            print_mail("\nSe envia el sig. correo...\n\n",
                       df_not_sent, mismatch_sent_template)

        return


if __name__ == "__main__":
    main()
