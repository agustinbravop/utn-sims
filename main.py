import sys
from enum import StrEnum
from typing import List, Optional

from tabulate import tabulate


# Pasa de bits a kilobytes.
def bits_a_kb(bits: int) -> int:
    return bits // 8 // 1024


# Pasa de kilobytes a bits.
def kb_a_bits(kilobytes: int) -> int:
    return kilobytes * 8 * 1024


# Representa los estados de un proceso.
class Estado(StrEnum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    LISTOSUSPENDIDO = "ListoSuspendido"
    EJECUTANDO = "Ejecutando"
    TERMINADO = "Terminado"


# Representa un programa activo a ejecutar en la CPU y alojar en memoria.
class Proceso:
    def __init__(self, pid: int, t_arribo: int, t_irrup: int, memoria: int):
        self.id = pid
        self.memoria = memoria
        self.t_arribo = t_arribo
        self.t_irrup = t_irrup
        self.estado: Estado = Estado.NUEVO
        self.progreso: int = 0
        # self.tiempo_inicio_ejecucion = None
        # self.t_fin = None
        # self.t_espera = 0
        # self.t_retorno = 0

    # Retorna True si el proceso cumplió su tiempo de irrupción y por ende terminó su tarea.
    def terminado(self) -> bool:
        return self.t_irrup - self.progreso <= 0

    # Retorna el porcentaje del tiempo de irrupción en el cual el proceso usó la CPU y progesó en su tarea.
    def porcentaje_progreso(self) -> float:
        return self.progreso / self.t_irrup * 100

    def __repr__(self):
        return f"Proceso({self.id}, {self.t_arribo}, {self.t_irrup}, {self.memoria}, {self.estado}, {self.progreso})"


# Representa un conjunto de Procesos a ejecutar.
class CargaTrabajo:
    headers = ["PID", "TA", "TI", "Mem (kB)", "Estado", "Progreso (%)"]

    # Inicializa una CargaTrabajo a partir de un archivo CSV.
    def __init__(self, archivo: str):
        self.procesos: List[Proceso] = []
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f.readlines():
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), kb_a_bits(int(mem))))
        self.procesos.sort(key=lambda p: p.t_arribo)

    # Muestra la CargaTrabajo en formato tabla.
    def __repr__(self):
        tabla = []
        for p in self.procesos:
            tabla.append([p.id, p.t_arribo, p.t_irrup, bits_a_kb(p.memoria), p.estado, p.porcentaje_progreso()])

        return tabulate(tabla, headers=self.headers, tablefmt="fancy_grid")


# Representa una partición fija de la memoria principal.
class Particion:
    def __init__(self, dir_inicio: int, memoria: int, proceso: Optional[Proceso] = None):
        self.dir_inicio = dir_inicio
        self.memoria = memoria
        self.proceso = proceso
        self.presente: bool = True

    # Retorna la fragmentación interna de la partición.
    def frag_interna(self) -> int:
        if not self.proceso:
            return 0
        return self.memoria - self.proceso.memoria

    # Instancia otra Particion de su mismo tamaño.
    def clonar(self):
        return Particion(self.dir_inicio, self.memoria)

    def __repr__(self):
        return f"Particion({self.dir_inicio}, {self.memoria}, {self.presente}, {self.proceso})"


# Es el orquestrador de la simulación que engloba al resto de clases.
class Simulador:
    # Inicializa un Simulador con una CargaTrabajo y una List[Particion] (memoria).
    def __init__(self, carga_trabajo: CargaTrabajo):
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

        # # Esto lo añadi por las consignas, pero no me anda tan bien
        # self.t_actual = 0
        # self.tt_retorno = 0
        # self.tt_espera = 0
        # self.cantidad_procesos = 0
        self.t: int = 0
        self.q: int = 0

    # # Asigna una partición de memoria a un proceso según el algoritmo best-fit.
    # def asignar_memoria(self, proceso: Proceso):
    #     mejor_part: Optional[Particion] = None
    #
    #     for part in self.mem_principal:
    #         if part.proceso is None and proceso.memoria <= part.memoria:
    #             if mejor_part is None or part.memoria < mejor_part.memoria:
    #                 mejor_part = part
    #
    #     if mejor_part is not None:
    #         mejor_part.proceso = proceso
    #         print(proceso)
    #         proceso.tiempo_inicio_ejecucion = self.t_actual
    #         self.ejecutando = proceso

    # Retorna True si el grado de multiprogramación alcanzó o superó el máximo (5).
    # Eso sucede si hay 3 procesos en MP y 2 en MV, o 2 en MP y 3 en MV, o 1 y 4, etc.
    def mem_virtual_disponible(self) -> bool:
        return self.grado_multiprogramacion() < self.max_multiprogramacion

    # Retorna la cantidad de procesos alojados en memoria (principal y virtual).
    def grado_multiprogramacion(self) -> int:
        particiones_ocupadas = 0
        for part in self.mem_principal:
            if part.proceso:
                particiones_ocupadas += 1

        return particiones_ocupadas + len(self.mem_virtual)

    # Retorna los procesos nuevos de la carga de trabajo cuyos tiempos de arribo fueron alcanzados.
    def procesos_nuevos(self) -> List[Proceso]:
        return list(filter(lambda p: p.t_arribo <= self.t and p.estado == Estado.NUEVO, self.carga_trabajo.procesos))

    # Busca una partición libre de memoria para el proceso según el algoritmo best-fit.
    def encontrar_particion(self, proceso: Proceso) -> Optional[Particion]:
        mejor_part: Optional[Particion] = None

        for part in self.mem_principal:
            if part.memoria >= proceso.memoria:
                if mejor_part is None or part.memoria < mejor_part.memoria:
                    mejor_part = part

        return mejor_part

    # Busca cualquier partición de memoria para el proceso según el algoritmo best-fit.
    def encontrar_particion_libre(self, proceso: Proceso) -> Optional[Particion]:
        mejor_part: Optional[Particion] = None

        for part in self.mem_principal:
            if part.proceso is None and part.memoria >= proceso.memoria:
                if mejor_part is None or part.memoria < mejor_part.memoria:
                    mejor_part = part

        return mejor_part

    # Retorna la partición que está asignada al proceso pasado por parámetro.
    def encontrar_particion_proceso(self, proceso: Proceso) -> Optional[Particion]:
        for part in self.mem_principal + self.mem_virtual:
            if part.proceso == proceso:
                return part

    # Retorna la partición en mem principal que se debería reemplazar por la partición ausente.
    def encontrar_particion_victima(self, particion: Particion) -> Optional[Particion]:
        for part in self.mem_principal:
            if part.dir_inicio == particion.dir_inicio:
                return part

    # Trae una partición ausente en memoria virtual a la memoria principal.
    # Si se requiere un swap out, la partición víctima será la del mismo tamaño que la ausente.
    def swap_in_particion(self, particion: Particion):
        print(self.mem_virtual, particion)
        self.mem_virtual.remove(particion)
        particion.presente = True

        victima = self.encontrar_particion_victima(particion)
        print(victima)
        if victima.proceso:
            # Si hay un proceso en la partición víctima, se hace un swap out.
            victima.proceso.estado = Estado.LISTOSUSPENDIDO
            victima.presente = False
            self.mem_virtual.append(victima)

        index = self.mem_principal.index(victima)
        print("Index", index, victima, particion)
        self.mem_principal[index] = particion

    # Asigna una partición de memoria (en MP o MV) al proceso, o lo rechaza si no hay disponibles.
    def admitir_proceso(self, proceso: Proceso):
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

    # Termina el proceso en ejecución en la CPU y libera su partición de memoria asignada.
    def terminar_proceso(self):
        part = self.encontrar_particion_proceso(self.ejecutando)
        part.proceso = None
        self.ejecutando.estado = Estado.TERMINADO
        self.ejecutando = None
        self.q = 0

    # Expropia de la CPU al proceso en ejecución y lo envía al final de la cola de listos.
    def expropiar_proceso(self):
        self.cola_listos.append(self.ejecutando)
        self.ejecutando.estado = Estado.LISTO
        self.ejecutando = None

    # Activa un proceso trayendolo a memoria principal.
    def activar_proceso(self, proceso: Proceso):
        part = self.encontrar_particion_proceso(proceso)
        if not part.presente:
            self.swap_in_particion(part)

    # Asigna la CPU al siguiente proceso de la cola de listos, y lo activa si está en mem virtual.
    def asignar_cpu(self):
        if 0 == len(self.cola_listos):
            self.ejecutando = None
        else:
            self.ejecutando = self.cola_listos[0]
            self.activar_proceso(self.ejecutando)
            self.cola_listos.remove(self.ejecutando)
            self.ejecutando.estado = Estado.EJECUTANDO

    # Planifica el uso de la CPU usando un Round Robin con quantum = 2.
    def planificar_cpu(self):
        if self.ejecutando:
            self.ejecutando.progreso += 1
            if self.ejecutando.terminado():
                self.terminar_proceso()
                self.asignar_cpu()
            elif self.q == 2:
                self.expropiar_proceso()
                self.asignar_cpu()
        else:
            self.asignar_cpu()

    # def planificar_cpu(self):
    #     if self.ejecutando is not None:
    #         self.ejecutando.t_irrup -= 1
    #         if self.ejecutando.t_irrup <= 0:
    #             # self.ejecutando.t_fin = (
    #             #         self.t_actual + 1
    #             # )
    #             # self.tt_retorno += (
    #             #         self.ejecutando.t_fin
    #             #         - self.ejecutando.t_arribo
    #             # )
    #             # self.tt_espera += (
    #             #         self.ejecutando.tiempo_inicio_ejecucion
    #             #         - self.ejecutando.t_arribo
    #             # )
    #             self.cantidad_procesos += 1
    #             self.ejecutando = None

    # Imprime el estado del simulador.
    def mostrar_estado(self):
        tabla_procesador = [["Proceso en ejecución", "No hay proceso en ejecución"]]
        if self.ejecutando:
            tabla_procesador[0][1] = f"Proceso {self.ejecutando.id}"
        print("\nEstado del procesador:")
        print(tabulate(tabla_procesador, tablefmt="fancy_grid"))

        tabla_memoria = []
        for pos, part in enumerate(self.mem_principal + self.mem_virtual, start=1):
            mem_en_uso = part.proceso.memoria if part.proceso else 0
            pid = part.proceso.id if part.proceso else "-"
            presente = "Sí" if part.presente else "No"
            tabla_memoria.append([pos, part.dir_inicio, part.memoria, mem_en_uso, part.frag_interna(), pid, presente])
        print("\nTabla de particiones de memoria:")
        print(tabulate(tabla_memoria,
                       headers=["Partición", "Dir. Inicio", "Tamaño", "Mem. en uso", "Frag. Interna", "Proceso",
                                "Presente"],
                       tablefmt="fancy_grid"))

        # # Estado de la cola de procesos listos
        # tabla_procesos_listos = []
        # for proceso in self.carga_trabajo.procesos:
        #     tabla_procesos_listos.append([proceso.id, proceso.t_arribo,
        #                                   proceso.t_irrup, proceso.memoria])
        # print("\nEstado de la cola de procesos listos:")
        # print(tabulate(tabla_procesos_listos, headers=["PID", "tArribo", "tIrrupción", "Mem", "Orden"],
        #                tablefmt="fancy_grid"))

        print("\n Carga de trabajo:")
        print(self.carga_trabajo)
        print(f"t = {self.t}; quantum = {self.q}; grado de multiprogramación = {self.grado_multiprogramacion()}")

    # por alguna razon no llegaba a esto , no cargo mas de 3 procesos
    # def finalizar_simulacion(self):
    #     if self.cantidad_procesos > 0:
    #         tiempo_promedio_retorno = self.tt_retorno / self.cantidad_procesos
    #         tiempo_promedio_espera = self.tt_espera / self.cantidad_procesos

    #         print("\nInforme Estadístico:")
    #         print(f"Tiempo promedio de retorno: {tiempo_promedio_retorno}")
    #         print(f"Tiempo promedio de espera: {tiempo_promedio_espera}")
    #     else:
    #         print("\nNo se han completado procesos para calcular los tiempos promedio.")


def input_avanzar():
    try:
        inp = input("Presione Enter para avanzar o q + Enter para salir...")
        if inp == "q":
            exit(0)
    except EOFError:
        exit(0)


def main():
    if len(sys.argv) < 2:
        print("Falta el parámetro del archivo con el workload.")
        exit(1)

    carga_trabajo = CargaTrabajo(sys.argv[1])
    simulador = Simulador(carga_trabajo)

    print("Carga de trabajo:")
    print(carga_trabajo)
    try:
        print("Presione q + Enter para terminar el programa.")
        inp = input("Presione Enter para comenzar la simulación...")
        if inp == "q":
            exit(0)
    except EOFError:
        exit(0)

    for nuevo in simulador.procesos_nuevos():
        simulador.admitir_proceso(nuevo)
    simulador.asignar_cpu()
    simulador.mostrar_estado()
    input_avanzar()

    while simulador.carga_trabajo or simulador.ejecutando:
        simulador.t += 1
        simulador.q = simulador.q % 2 + 1
        for nuevo in simulador.procesos_nuevos():
            simulador.admitir_proceso(nuevo)
        simulador.planificar_cpu()

        simulador.mostrar_estado()
        input_avanzar()


if __name__ == "__main__":
    main()
