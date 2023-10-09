from typing import Optional, List

from tabulate import tabulate

from CargaTrabajo import CargaTrabajo
from Particion import Particion
from Proceso import Estado, Proceso
from utils import kb_a_bits


class Simulador:
    """Representa una simulación. Interconecta al resto de clases y se
    encarga de la planificación de la CPU y administración de memoria."""

    def __init__(self, carga_trabajo: CargaTrabajo):
        """Inicializa un Simulador con una CargaTrabajo y una List[Particion] (memoria)."""
        # Estructuras de datos para los procesos.
        self.carga_trabajo = carga_trabajo
        self.cola_listos: List[Proceso] = []
        self.ejecutando: Optional[Proceso] = None

        # Estructuras de datos para la memoria.
        p1 = Particion(kb_a_bits(100), kb_a_bits(250))
        p2 = Particion(p1.dir_inicio + p1.memoria, kb_a_bits(120))
        p3 = Particion(p2.dir_inicio + p2.memoria, kb_a_bits(60))
        self.mem_principal: List[Particion] = [p1, p2, p3]
        self.mem_virtual: List[Particion] = []
        self.max_multiprogramacion: int = 5

        self.t: int = 0
        self.quantum: int = 0

    def grado_multiprogramacion(self) -> int:
        """Retorna la cantidad de procesos actualmente alojados en memoria (principal y virtual)."""
        particiones_ocupadas = 0
        for part in self.mem_principal:
            if part.proceso:
                particiones_ocupadas += 1

        return particiones_ocupadas + len(self.mem_virtual)

    def mem_virtual_disponible(self) -> bool:
        """ Retorna True si el grado de multiprogramación alcanzó o superó el máximo (5).
        Eso sucede si hay 3 procesos en MP y 2 en MV, o 2 en MP y 3 en MV, o 1 y 4, etc."""
        return self.grado_multiprogramacion() < self.max_multiprogramacion

    def procesos_nuevos(self) -> List[Proceso]:
        """Retorna los procesos nuevos de la carga de trabajo con tiempos de arribo alcanzados."""
        return list(filter(lambda p: p.t_arribo <= self.t and p.estado == Estado.NUEVO, self.carga_trabajo.procesos))

    def encontrar_particion(self, proceso: Proceso) -> Optional[Particion]:
        """Retorna una partición de memoria ocupada o libre para el proceso según el algoritmo best-fit."""
        mejor_part: Optional[Particion] = None

        for part in self.mem_principal:
            if part.memoria >= proceso.memoria:
                if mejor_part is None or part.memoria < mejor_part.memoria:
                    mejor_part = part

        return mejor_part

    def encontrar_particion_libre(self, proceso: Proceso) -> Optional[Particion]:
        """Retorna una partición de memoria libre para el proceso según el algoritmo best-fit."""
        mejor_part: Optional[Particion] = None

        for part in self.mem_principal:
            if part.proceso is None and part.memoria >= proceso.memoria:
                if mejor_part is None or part.memoria < mejor_part.memoria:
                    mejor_part = part

        return mejor_part

    def encontrar_particion_proceso(self, proceso: Proceso) -> Optional[Particion]:
        """Retorna la partición que está asignada al proceso pasado por parámetro."""
        for part in self.mem_principal + self.mem_virtual:
            if part.proceso == proceso:
                return part

    def encontrar_particion_victima(self, particion: Particion) -> Optional[Particion]:
        """Retorna la partición en memoria principal que debería reemplazarse por la partición ausente."""
        for part in self.mem_principal:
            if part.dir_inicio == particion.dir_inicio:
                return part

    def swap_in_particion(self, particion: Particion):
        """Trae una partición ausente en memoria virtual a la memoria principal.
        Si se requiere un swap out, la partición víctima será la del mismo tamaño que la ausente."""
        self.mem_virtual.remove(particion)
        particion.presente = True

        victima = self.encontrar_particion_victima(particion)
        if victima.proceso:
            # Si hay un proceso en la partición víctima, se hace un swap out.
            victima.proceso.estado = Estado.LISTOSUSPENDIDO
            victima.presente = False
            self.mem_virtual.append(victima)

        index = self.mem_principal.index(victima)
        self.mem_principal[index] = particion

    def admitir_proceso(self, proceso: Proceso):
        """Asigna una partición de memoria (en MP o MV) al proceso, o lo rechaza si no hay disponibles."""
        part = self.encontrar_particion_libre(proceso)
        if part and part.presente:
            # Admitir proceso listo a memoria principal
            part.proceso = proceso
            proceso.estado = Estado.LISTO
            self.cola_listos.append(proceso)
            return

        if self.mem_virtual_disponible():
            # Admitir proceso suspendido a memoria virtual
            part = self.encontrar_particion(proceso).clonar()
            part.presente = False
            self.mem_virtual.append(part)
            part.proceso = proceso
            proceso.estado = Estado.LISTOSUSPENDIDO
            self.cola_listos.append(proceso)
        else:
            # Rechazar proceso
            print(f"Proceso {proceso.id} rechazado por falta de recursos")

    def terminar_proceso(self):
        """Termina el proceso en ejecución en la CPU y libera su partición de memoria asignada."""
        part = self.encontrar_particion_proceso(self.ejecutando)
        part.proceso = None
        self.ejecutando.estado = Estado.TERMINADO
        self.ejecutando = None
        self.quantum = 0

    def expropiar_proceso(self):
        """Expropia al proceso en ejecución de la CPU y lo envía al final de la cola de listos."""
        self.cola_listos.append(self.ejecutando)
        self.ejecutando.estado = Estado.LISTO
        self.ejecutando = None

    def activar_proceso(self, proceso: Proceso):
        """Activa un proceso trayéndolo a memoria principal."""
        part = self.encontrar_particion_proceso(proceso)
        if not part.presente:
            self.swap_in_particion(part)

    def asignar_cpu(self):
        """Asigna la CPU al siguiente proceso de la cola de listos, y lo activa si está en mem virtual."""
        if 0 == len(self.cola_listos):
            self.ejecutando = None
        else:
            self.ejecutando = self.cola_listos[0]
            self.activar_proceso(self.ejecutando)
            self.cola_listos.remove(self.ejecutando)
            self.ejecutando.estado = Estado.EJECUTANDO

    def planificar_cpu(self):
        """Planifica el uso de la CPU usando un Round Robin con quantum = 2."""
        if self.ejecutando:
            self.ejecutando.progreso += 1
            if self.ejecutando.terminado():
                self.terminar_proceso()
                self.asignar_cpu()
            elif self.quantum == 2:
                self.expropiar_proceso()
                self.asignar_cpu()
        else:
            self.asignar_cpu()

    def mostrar_estado(self):
        """Imprime el estado del simulador."""
        tabla_procesador = [
            ["Proceso en ejecución", "No hay proceso en ejecución"]]
        if self.ejecutando:
            tabla_procesador[0][1] = f"Proceso {self.ejecutando.id}"
        print("\nEstado del procesador:")
        print(tabulate(tabla_procesador, tablefmt="fancy_grid"))

        tabla_memoria = []
        for pos, part in enumerate(self.mem_principal + self.mem_virtual, start=1):
            mem_en_uso = part.proceso.memoria if part.proceso else 0
            pid = part.proceso.id if part.proceso else "-"
            presente = "Sí" if part.presente else "No"
            tabla_memoria.append(
                [pos, part.dir_inicio, part.memoria, mem_en_uso, part.frag_interna(), pid, presente])
        print("\nTabla de particiones de memoria:")
        print(tabulate(tabla_memoria,
                       headers=["Partición", "Dir. Inicio", "Tamaño", "Mem. en uso", "Frag. Interna", "Proceso",
                                "Presente"],
                       tablefmt="fancy_grid"))

        print("\n Carga de trabajo:")
        print(self.carga_trabajo)
        print(
            f"t = {self.t}; quantum = {self.quantum}; grado de multiprogramación = {self.grado_multiprogramacion()}")