from typing import List

from tabulate import tabulate

from Proceso import Proceso, Estado
from utils import kb_a_bytes, bytes_a_kb, colorear_lista


class CargaTrabajo:
    """Representa un conjunto de Procesos a ejecutar."""
    headers = ["PID", "TA", "TI", "Mem (kB)", "Estado", "Progreso (%)"]

    def terminada(self):
        """Retorna `True` si todos los procesos de la carga de trabajo están en TERMINADO o DENEGADO."""
        return all(p.estado == Estado.TERMINADO or p.estado == Estado.DENEGADO for p in self.procesos)

    def __init__(self, archivo: str):
        """Inicializa una CargaTrabajo a partir de un archivo CSV."""
        self.procesos: List[Proceso] = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f.readlines():
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), kb_a_bytes(int(mem))))
        self.procesos.sort(key=lambda p: p.t_arribo)

    def __repr__(self):
        """Muestra la CargaTrabajo en formato tabla."""
        tabla = []
        for p in self.procesos:
            tabla.append(colorear_lista(
                [p.id, p.t_arribo, p.t_irrup, bytes_a_kb(p.memoria), p.estado,
                 progreso(p.porcentaje_progreso())], p.estado))

        return tabulate(tabla, headers=self.headers, tablefmt="fancy_grid")


def progreso(porcentaje: float) -> str:
    """Muestra el progreso de un `Proceso` mediante una barra de progeso."""
    cantidad = int((15 * porcentaje / 100))
    return f"{'█' * cantidad}{'_' * (15 - cantidad)} {round(porcentaje, 1)}"
