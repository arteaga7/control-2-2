# inbox.py

from pathlib import Path
import requests
import time
import os
from dotenv import load_dotenv
import html
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from datetime import datetime, timezone

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)
# firma de un .msg binario de Outlook
OLE_MAGIC = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"


def extraer_from(path: str | Path, exec_date: datetime) -> str:
    """Extrae el correo del remitente (From) de un correo MIME (.eml), tenga o no extensión,
    solo si la fecha del correo (Date) es más reciente que 'exec_date'."""
    data = Path(path).read_bytes()
    if data.startswith(OLE_MAGIC):
        raise ValueError(
            f"{path} es un .msg binario de Outlook; usa extract_msg")
    # Por si el archivo trae &lt; &gt; en lugar de < >
    data = html.unescape(data.decode("utf-8", errors="ignore")).encode("utf-8")
    msg = BytesParser(policy=policy.default).parsebytes(data)
    # --- Filtro por fecha del correo ---
    fecha_raw = msg.get("Date")
    if not fecha_raw:
        return ""  # sin fecha, no se puede validar

    fecha_correo = parsedate_to_datetime(
        str(fecha_raw)).astimezone()   # → hora local
    if hasattr(exec_date, "to_pydatetime"):
        exec_date = exec_date.to_pydatetime()
    exec_date = exec_date.astimezone()
    if fecha_correo <= exec_date:
        print(f"Fecha {fecha_correo} <= exec_date({exec_date})")
        return ""
    # --- Remitente ---
    valores = [str(v) for v in msg.get_all("From", [])]
    correos = [email for _, email in getaddresses(valores) if email]
    return correos[0] if correos else ""


def extract_from_inbox(folder_path: str | Path, exec_date: datetime) -> list[str]:
    """Regresa la lista de remitentes (From) de todos los archivos mas recientes que
    la fecha 'exec_date' de la carpeta sharepoint (inbox)."""
    remitentes = []

    for archivo in sorted(Path(folder_path).iterdir()):
        # Omite subcarpetas y archivos ocultos/temporales de sincronización (.xxxx)
        if not archivo.is_file() or archivo.name.startswith((".", "~$")):
            continue
        try:
            frm = extraer_from(archivo, exec_date)
            if frm:
                remitentes.append(frm)
        except Exception as e:
            print(f"[ERROR] {archivo.name}: {e}")

    return list(dict.fromkeys(remitentes))


def post_inbox():
    """Post API Rest to trigger PowerAutomate to check inbox"""
    print("Checando bandeja de entrada...")
    url = os.getenv("INBOX_URL")
    if not url:
        raise RuntimeError(f"No se encontró INBOX_URL en {ENV_PATH}")
    # json= pone el Content-Type solo
    response = requests.post(url, timeout=60, verify=False)
    if response.status_code in (200, 202):
        print("Exitoso")
    else:
        raise Exception(
            f"Power Automate fallo al checar la bandeja de entrada: "
            f"{response.status_code} - {response.text}"
        )
    print("Esperamos un minuto a que se ejecute el flujo de Power Automate para revisar inbox...")
    time.sleep(60)


if __name__ == "__main__":
    post_inbox()
