from typing import Optional

from Proceso import Proceso


class Particion:
    """Representa una partición fija de la memoria principal."""

    def __init__(self, dir_inicio: int, memoria: int, proceso: Optional[Proceso] = None):
        self.dir_inicio = dir_inicio
        self.memoria = memoria
        self.proceso = proceso
        self.presente: bool = True

    def frag_interna(self) -> int:
        """Retorna la fragmentación interna de la partición."""
        if not self.proceso:
            return 0
        return self.memoria - self.proceso.memoria

    def clonar(self):
        """Instancia otra Particion de su mismo tamaño."""
        return Particion(self.dir_inicio, self.memoria)

    def __repr__(self):
        return f"Particion({self.dir_inicio}, {self.memoria}, {self.presente}, {self.proceso})"
