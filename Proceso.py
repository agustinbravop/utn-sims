from enum import StrEnum


class Estado(StrEnum):
    """Representa los estados de un proceso."""
    NUEVO = "Nuevo"
    LISTO = "Listo"
    LISTOSUSPENDIDO = "ListoSuspendido"
    EJECUTANDO = "Ejecutando"
    TERMINADO = "Terminado"


class Proceso:
    """Representa un programa activo a ejecutar en la CPU y alojar en memoria."""

    def __init__(self, pid: int, t_arribo: int, t_irrup: int, memoria: int):
        self.id = pid
        self.memoria = memoria
        self.t_arribo = t_arribo
        self.t_irrup = t_irrup
        self.estado: Estado = Estado.NUEVO
        self.progreso: int = 0

    def terminado(self) -> bool:
        """Retorna True si el proceso cumplió su tiempo de irrupción y por ende terminó su tarea."""
        return self.t_irrup - self.progreso <= 0

    def porcentaje_progreso(self) -> float:
        """Retorna el porcentaje del tiempo de irrupción durante el cual el proceso se ejecutó en la CPU."""
        return self.progreso / self.t_irrup * 100

    def __repr__(self):
        return f"Proceso({self.id}, {self.t_arribo}, {self.t_irrup}, {self.memoria}, {self.estado}, {self.progreso})"
