from typing import List

from colorama import Style

from Proceso import COLORES, Estado


def bits_a_kb(bits: int) -> int:
    """Pasa de bits a kilobytes."""
    return bits // 8 // 1024


def kb_a_bits(kilobytes: int) -> int:
    """Pasa de kilobytes a bits."""
    return kilobytes * 8 * 1024


def colorear(contenido: any, estado: Estado) -> str:
    """Formatea el contenido a un string con color del `Estado` (de un `Proceso`) pasado por parámetro."""
    return f"{COLORES[estado]}{contenido}{Style.RESET_ALL}"


def colorear_lista(lista: List, estado: Estado) -> List:
    """Formatea una fila (de cualquier tabla) para imprimirlas con colores (por consola)."""
    return [colorear(item, estado) for item in lista]
