# mail.py
from pathlib import Path
import extract_msg
from mod_2_2.report import get_filenames
import re
import html
import requests
import json
import pandas as pd
import os


def extract_emails(texto: str) -> list[str]:
    """Extrae el contenido dentro de <...> del texto y retorna una lista."""
    # convierte &lt; &gt; en < >, por si vienen escapados
    texto = html.unescape(texto)
    patron = re.compile(r"<([^<>]+)>")
    return [m.strip().lower() for m in patron.findall(texto)]


def read_msg(folder_path: Path, n_mails: int | None = None,
             extension: str = "*.msg", property: str = "to") -> list[str]:
    """
    Extrae todas las direcciones de correo de la propiedad indicada
    ("to", "cc" o "sender") de los archivos .msg.
    """
    msg_names = get_filenames(folder_path, extension, None)
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
    URL = os.environ.get("PA_INBOX_URL")
    if not URL:
        raise RuntimeError(
            "Falta PA_INBOX_URL en el archivo .env junto al .exe")
    headers = {"Content-Type": "application/json"}

    json_file = json.dumps({
        "mode": "refresh",
        # "sas_uri": "https://dbstorageda09p930814.blob.core.windows.net/",
        # "blob_path": "unilever/FillRate/Flujo_Casa_Ley.xlsx",
        # "site": "https://unilever.sharepoint.com/sites/SKY_CE",
        # "sharepoint_path": "/Shared Documents/CEX SILVER/CASA LEY/",
        # "file_name": "Flujo_Casa_Ley.xlsx",
        "email": "Bulmaro.Espinoza@unilever.com",
        "cc": "Antonio.Arteaga@Unilever.com",
        "subject": "Control 2.2 - Pruebita BOT",
        "body": body_mail
    })
    response = requests.post(URL, data=json_file,  headers=headers)
    print(response.status_code)
    print(response.text)


def notify(mensaje_log: str, correo_html: str):
    """Imprime un mensaje de log y envía el correo correspondiente."""
    print(mensaje_log + correo_html)
    send_mail(correo_html)


def print_mail(mensaje: str, df: pd.DataFrame, template: str, mes: str, control: str):
    """Print and send Dataframe with html format"""
    print(f"\n{mensaje}\n", df)
    mail = template.format(
        df=df.to_html(index=False), mes=mes, control=control)
    send_mail(mail)
