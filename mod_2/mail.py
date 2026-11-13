# mail.py
from pathlib import Path
import extract_msg
from mod_2.report import get_files
import re
import html
import requests
import json
import pandas as pd
import os

nota = "\n\nSe envia el sig. correo...\n\n"


def extract_emails(texto: str) -> list[str]:
    """Extrae el contenido dentro de <...> del texto y retorna una lista."""
    # convierte &lt; &gt; en < >, por si vienen escapados
    texto = html.unescape(texto)
    patron = re.compile(r"<([^<>]+)>")
    return [m.strip().lower() for m in patron.findall(texto)]


def read_msg(folder_path: Path, n_mails: int | None = None,
             extension: str = "*.msg", property: str = "to") -> list[str]:
    """Extrae todas las direcciones de correo de la propiedad indicada
    ("to", "cc" o "sender") de los archivos .msg."""
    msg_names = get_files(folder_path, extension, None)
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


def send_mail(body_mail: str, control: str) -> None:
    """Send email"""
    URL = os.environ.get("EMAIL_URL")
    if not URL:
        raise RuntimeError(
            "Falta INBOX_URL en el archivo .env junto al .exe")
    headers = {"Content-Type": "application/json"}
    json_file = json.dumps({
        "mode": "refresh",
        "email": "Bulmaro.Espinoza@unilever.com",
        "cc": "Antonio.Arteaga@Unilever.com",
        "subject": f"Control {control} - Pruebita BOT",
        "body": body_mail
    })
    response = requests.post(URL, data=json_file,  headers=headers, timeout=30)
    print("\nSend mail status code: ", response.status_code, response.text)


def notify(mensaje_log: str, correo_html: str, control: str):
    """Imprime un mensaje de log y envía el correo correspondiente."""
    print(mensaje_log + correo_html.replace("<br><br>", "\n"))
    # send_mail(correo_html, control)


def print_mail(df: pd.DataFrame, template: str, mes: str, control: str):
    """Print and send Dataframe with html format"""
    mail_terminal = template.replace("<br><br>", "\n").format(
        df=df.to_string(index=False), mes=mes, control=control)
    print(f"{nota}{mail_terminal}")
    mail = template.format(
        df=df.to_html(index=False), mes=mes, control=control)
    # send_mail(mail, control)
