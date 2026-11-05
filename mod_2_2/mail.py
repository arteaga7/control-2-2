# mail.py
from pathlib import Path
import extract_msg
from mod_2_2.monthly_report import get_filenames
import re
import html
import requests
import json
import pandas as pd


def extract_emails(texto: str) -> list[str]:
    """Extrae el contenido dentro de <...> del texto y retorna una lista."""
    # convierte &lt; &gt; en < >, por si vienen escapados
    texto = html.unescape(texto)
    patron = re.compile(r"<([^<>]+)>")
    return [m.strip() for m in patron.findall(texto)]


def read_msg(folder_path: Path, n_mails: int | None = None,
             extension: str = "*.msg", property: str = "to") -> list[str]:
    """
    Extrae todas las direcciones de correo de la propiedad indicada
    ("to", "cc" o "sender") de los archivos .msg.
    """
    msg_names = get_filenames(folder_path, extension)
    if n_mails is not None:
        msg_names = msg_names[:n_mails]

    addresses = []
    for msg_name in msg_names:
        file_path = folder_path / msg_name
        message = None
        try:
            message = extract_msg.Message(file_path)
            value = getattr(message, property, None)
            if value:
                addresses.extend(extract_emails(value))
        except Exception:
            pass
        finally:
            if message is not None:
                message.close()
    return addresses


def send_mail(body_mail: str) -> None:
    """Send email"""
    headers = {"Content-Type": "application/json"}
    URL = "https://defaultf66fae025d36495bbfe078a6ff9f8e.6e.environment.api.powerplatform.com:443/powerautomate/automations/direct/cu/05/workflows/9560f13a31ba4795b346c4b0ae2df14f/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ksORmCQP6YZcCPu2kkxxfA7v_hztHNaX8MJnaCcw1Bk"
    json_file = json.dumps({
        "mode": "refresh",
        # "sas_uri": "https://dbstorageda09p930814.blob.core.windows.net/",
        # "blob_path": "unilever/FillRate/Flujo_Casa_Ley.xlsx",
        # "site": "https://unilever.sharepoint.com/sites/SKY_CE",
        # "sharepoint_path": "/Shared Documents/CEX SILVER/CASA LEY/",
        # "file_name": "Flujo_Casa_Ley.xlsx",
        "email": "Antonio.Arteaga@Unilever.com",
        "cc": "",
        "subject": "Control 2.2 - Pruebita BOT",
        "body": body_mail
    })
    response = requests.post(URL, data=json_file,  headers=headers)
    print(response.status_code)
    print(response.text)


def notify(mensaje_log: str, correo_html: str):
    """Imprime un mensaje de log y envía el correo correspondiente."""
    print(mensaje_log + correo_html)
    # send_mail(correo_html)


def print_mail(mensaje: str, df: pd.DataFrame, template: str):
    """Print and send Dataframe with html format"""
    print(f"\n{mensaje}\n", df)
    success_mail = template.format(
        df=df.to_html(index=False))
    send_mail(success_mail)
