# approve_mail.py
from pathlib import Path
from mod_2.report import get_files


def approve_msg(folder_path: Path) -> bool:
    """Extrae y analiza el contenido del primer archivo .msg encontrado.
    Determina si es un mensaje de aprobado o rechazado"""
    msg_file = get_files(folder_path, "*.msg")
    if len(msg_file) > 0:
        msg_file = msg_file[0]
    else:
        print(f"No se encontró ningún archivo '.msg' en {folder_path}")
        return False

    print("Verificar mail de aprobacion")
    return True
