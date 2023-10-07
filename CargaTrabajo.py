from typing import List

from tabulate import tabulate

from Proceso import Proceso
from utils import kb_a_bits, bits_a_kb


class CargaTrabajo:
    """Representa un conjunto de Procesos a ejecutar."""
    headers = ["PID", "TA", "TI", "Mem (kB)", "Estado", "Progreso (%)"]

    def __init__(self, archivo: str):
        """Inicializa una CargaTrabajo a partir de un archivo CSV."""
        self.procesos: List[Proceso] = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f.readlines():
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), kb_a_bits(int(mem))))
        self.procesos.sort(key=lambda p: p.t_arribo)

    def __repr__(self):
        """Muestra la CargaTrabajo en formato tabla."""
        tabla = []
        for p in self.procesos:
            tabla.append([p.id, p.t_arribo, p.t_irrup, bits_a_kb(p.memoria), p.estado, p.porcentaje_progreso()])

        return tabulate(tabla, headers=self.headers, tablefmt="fancy_grid")
