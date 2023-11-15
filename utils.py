from typing import List

from colorama import Style, just_fix_windows_console

from Proceso import COLORES, Estado


def bytes_a_kb(bits: int) -> int:
    """Pasa de bytes a kilobytes."""
    return bits // 1024


def kb_a_bytes(kilobytes: int) -> int:
    """Pasa de kilobytes a bytes."""
    return kilobytes * 1024


def colorear(contenido: any, estado: Estado) -> str:
    """Formatea el contenido a un string con color del `Estado` (de un `Proceso`) pasado por parámetro."""
    return f"{COLORES[estado]}{contenido}{Style.RESET_ALL}"


def colorear_lista(lista: List, estado: Estado) -> List:
    """Formatea una fila (de cualquier tabla) para imprimirlas con colores (por consola)."""
    return [colorear(item, estado) for item in lista]

just_fix_windows_console()