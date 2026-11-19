# approve_mail.py
from pathlib import Path
import re
import html
import extract_msg
from mod_2.report import get_files

# Patrones positivos
PATRONES_POSITIVOS = [
    r"\baprobad[oa]s?\b",
    r"\bautorizad[oa]s?\b",
    r"\baceptad[oa]s?\b",
    r"\bse\s+dejar[aá]\s+pasar\b",
    r"\bprocede\b",
    r"\bviable\b",
    r"\bcumple\b",
    r"\bfavorable\b",
    r"\bok\b",
    r"\bconforme\b",
    r"\baprobad[oa]\s+con\s+(?:detalles|observaciones|comentarios)\b"
]

# Patrones negativos
PATRONES_NEGATIVOS = [
    r"\brechazad[oa]s?\b",
    r"\bdenegad[oa]s?\b",
    r"\bno\s+aprobad[oa]s?\b",
    r"\bno\s+cumple\b",
    r"\bno\s+procede\b",
    r"\binviable\b",
    r"\bdesfavorable\b",
    r"\bcancelad[oa]s?\b",
    r"\bno\s+autorizad[oa]s?\b"
]


def get_msg_body(file_path: str) -> str:
    """Regresa el cuerpo de un archivo .msg como str."""
    with extract_msg.openMsg(file_path) as msg:
        body = msg.body

        # Si no hay cuerpo en texto plano, usar el HTML
        if not body and msg.htmlBody:
            raw = msg.htmlBody
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="ignore")
            raw = re.sub(r"(?is)<(script|style).*?</\1>",
                         "", raw)   # quitar scripts/estilos
            raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>",
                         "\n", raw)    # saltos de línea
            # quitar etiquetas
            body = html.unescape(re.sub(r"<[^>]+>", "", raw))

        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="ignore")

    return (body or "").strip()


def clasificar_texto(texto) -> bool:
    texto = texto.lower()
    positivos_encontrados = []
    negativos_encontrados = []

    for patron in PATRONES_POSITIVOS:
        coincidencias = re.findall(patron, texto, re.IGNORECASE)
        positivos_encontrados.extend(coincidencias)

    for patron in PATRONES_NEGATIVOS:
        coincidencias = re.findall(patron, texto, re.IGNORECASE)
        negativos_encontrados.extend(coincidencias)

    if positivos_encontrados:
        # print(f"Coincidencias positivas: {positivos_encontrados}")
        return True
    else:
        # print(f"Coincidencias negativas: {negativos_encontrados}")
        return False


def approve_msg(folder_path: Path) -> bool:
    """Extrae y analiza el contenido del primer archivo .msg encontrado.
    Determina si es un mensaje de aprobado o rechazado"""
    msg_file = get_files(folder_path, "*.msg")
    if len(msg_file) > 0:
        msg_file = msg_file[0]
    else:
        print(f"No se encontró ningún archivo '.msg' en {folder_path}")
        return False

    file_path = folder_path / msg_file
    msg_body = get_msg_body(file_path)
    # print(msg_body)
    return clasificar_texto(msg_body)
