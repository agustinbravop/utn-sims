from enum import StrEnum

from colorama import Fore


class Estado(StrEnum):
    """Representa los estados de un proceso."""
    NUEVO = "Nuevo"
    """Un proceso nuevo todavía no arribó o arribó pero todavía no fue admitido."""
    LISTOSUSPENDIDO = "ListoSuspendido"
    """Un proceso listo/suspendido está en la cola de listos pero en memoria virtual."""
    LISTO = "Listo"
    """Un proceso listo está en la cola de listos y en memoria principal, esperando la CPU."""
    EJECUTANDO = "Ejecutando"
    """Un proceso está ejecutando si tiene asignada la CPU."""
    TERMINADO = "Terminado"
    """Un proceso está terminado si cumplió su tiempo de irrupción completo en la CPU."""
    DENEGADO = "Denegado"
    """Un proceso es denegado si solicita una cantidad de memoria mayor al tamaño de la partición más grande."""


COLORES = {
    Estado.NUEVO: Fore.LIGHTBLACK_EX,
    Estado.LISTO: Fore.WHITE,
    Estado.LISTOSUSPENDIDO: Fore.YELLOW,
    Estado.EJECUTANDO: Fore.CYAN,
    Estado.TERMINADO: Fore.GREEN,
    Estado.DENEGADO: Fore.RED,
}
"""Asigna a cada `Estado` de un `Proceso` un color con el cual imprimirlo por consola."""


class Proceso:
    """Representa un programa activo a ejecutar en la CPU y alojar en memoria."""

    def __init__(self, pid: int, t_arribo: int, t_irrup: int, memoria: int):
        self.id = pid
        self.memoria = memoria
        self.t_arribo = t_arribo
        self.t_irrup = t_irrup
        self.estado: Estado = Estado.NUEVO
        self.progreso: int = 0  # Tiempo que el proceso estuvo ejecutandose (en EJECUTANDO)
        self.t_retorno: int = 0  # Tiempo que demora el proceso desde cargado a terminado (en llegar a TERMINADO)
        self.t_espera: int = 0  # Tiempo que el proceso pasó en la cola de listos (en LISTO o LISTOSUSPENDIDO)

    def terminado(self) -> bool:
        """Retorna True si el proceso cumplió su tiempo de irrupción y por ende terminó su tarea."""
        return self.t_irrup - self.progreso <= 0

    def porcentaje_progreso(self) -> float:
        """Retorna el porcentaje del tiempo de irrupción durante el cual el proceso se ejecutó en la CPU."""
        return self.progreso / self.t_irrup * 100

    def tick_ejecutando(self):
        """Avanza el progreso del proceso en ejecución en cada instante de tiempo o pulso de clock."""
        self.progreso += 1
        self.t_retorno += 1

    def tick_listo(self):
        """Informa al proceso en cada instante de tiempo que está en cola de listos (y listos/suspendidos)."""
        self.t_espera += 1
        self.t_retorno += 1

    def __repr__(self):
        return f"Proceso({self.id}, {self.t_arribo}, {self.t_irrup}, {self.memoria}, {self.estado}, {self.progreso})"
