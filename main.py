import sys
from typing import List
from tabulate import tabulate

class Proceso:
    def __init__(self, id, memoria_necesaria, cuando_entra, cuanto_consume, nro_orden):
        self.id = id
        self.memoria_necesaria = memoria_necesaria
        self.t_arribo = cuando_entra
        self.t_irrup = cuanto_consume
        self.nro_orden = nro_orden
        # self.tiempo_inicio_ejecucion = None
        # self.t_fin = None
        # self.t_espera = 0
        # self.t_retorno = 0

    def __str__(self):
        return f"Proceso {self.id} | Memoria: {self.memoria_necesaria} MB | Tiempo de Irrupción: {self.t_irrup} | Nro. de Orden: {self.nro_orden}"

class CargaTrabajo:
    headers = ["PID", "tArribo", "tIrrupción", "Mem", "Orden"]

    # Inicializa una CargaTrabajo a partir de un archivo CSV.
    def __init__(self, archivo: str):
        self.procesos: List[Proceso] = []
        with open(archivo, "r") as f:
            lineas = f.readlines()
            for i, linea in enumerate(lineas, start=1):
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), int(mem), i))

    # Muestra la CargaTrabajo en formato tabla.
    def __str__(self):
        tabla = []
        for p in self.procesos:
            tabla.append([p.id, p.t_arribo, p.t_irrup, p.memoria_necesaria, p.nro_orden])

        return tabulate(tabla, headers=self.headers, tablefmt="fancy_grid", stralign="right")

#clase de particiones o memoria como le vean mejoro unu
class Particion:
    def __init__(self, id, inicio, tamaño, id_proceso_asignado=None):
        self.id = id
        self.inicio = inicio
        self.tamaño = tamaño
        self.id_proceso_asignado = id_proceso_asignado
        self.fragmentación_interna = 0

class Simulador:
    def __init__(self, carga_trabajo):
        self.particiones = [
            #No tome en cuenta la particion destinado al SO ya que esa no variara ni entrara algun proceso
            Particion(1, 0, 250),  # Partición grande
            Particion(2, 0, 120),  # Partición mediana
            Particion(3, 0, 60),   # Partición pequeña
        ]
        self.cola_procesos = carga_trabajo.procesos
        self.procesando = None
        #Esto lo añadi por las consignas pero no me anda tan bien
        self.t_actual = 0
        self.tt_retorno = 0
        self.tt_espera = 0
        self.cantidad_procesos = 0

    ##Esto es para hacer las asignacions beft fit
    def asignar_memoria(self, proceso):
        bfit_particion = None

        for particion in self.particiones:
            if (
                particion.id_proceso_asignado is None
                and proceso.memoria_necesaria <= particion.tamaño
            ):
                if bfit_particion is None or particion.tamaño < bfit_particion.tamaño:
                    bfit_particion = particion

        if bfit_particion is not None:
            bfit_particion.id_proceso_asignado = proceso.id
            bfit_particion.fragmentación_interna = bfit_particion.tamaño - proceso.memoria_necesaria
            proceso.tiempo_inicio_ejecucion = self.t_actual
            self.procesando = proceso
            self.cola_procesos.remove(proceso)

    def planificar_cpu(self):
        if self.procesando is not None:
            self.procesando.t_irrup -= 1
            if self.procesando.t_irrup <= 0:
                self.procesando.t_fin = (
                    self.t_actual + 1
                )
                self.tt_retorno += (
                    self.procesando.t_fin
                    - self.procesando.t_arribo
                )
                self.tt_espera += (
                    self.procesando.tiempo_inicio_ejecucion
                    - self.procesando.t_arribo
                )
                self.cantidad_procesos += 1
                self.procesando = None

    def mostrar_estado(self):
         # Estado del procesador
        procesador_data = [["Proceso en ejecución", "No hay proceso en ejecución"]]
        if self.procesando is not None:
            procesador_data[0][1] = f"Proceso {self.procesando.id}"

        # Tabla de particiones de memoria
        memoria_data = []
        for particion in self.particiones:
            memoria_data.append([particion.id, particion.inicio, particion.tamaño,
                                particion.id_proceso_asignado, particion.fragmentación_interna])

        # Estado de la cola de procesos listos
        cola_procesos_data = []
        for proceso in self.cola_procesos:
            cola_procesos_data.append([proceso.id, proceso.t_arribo,
                                       proceso.t_irrup, proceso.memoria_necesaria, proceso.nro_orden])

        # Mostrar tablas usando tabulate
        print("\nEstado del procesador:")
        print(tabulate(procesador_data, tablefmt="fancy_grid"))

        print("\nTabla de particiones de memoria:")
        print(tabulate(memoria_data, headers=["NParticion", "Inicio", "Tamaño", "Asignado a proceso", "Fragmentación Interna"],
                        tablefmt="fancy_grid"))

        print("\nEstado de la cola de procesos listos:")
        print(tabulate(cola_procesos_data, headers=["PID", "tArribo", "tIrrupción", "Mem", "Orden"],
                        tablefmt="fancy_grid"))
    #por alguna razon no llegaba a esto , no cargo mas de 3 procesos 
    # def finalizar_simulacion(self):
    #     if self.cantidad_procesos > 0:
    #         tiempo_promedio_retorno = self.tt_retorno / self.cantidad_procesos
    #         tiempo_promedio_espera = self.tt_espera / self.cantidad_procesos

    #         print("\nInforme Estadístico:")
    #         print(f"Tiempo promedio de retorno: {tiempo_promedio_retorno}")
    #         print(f"Tiempo promedio de espera: {tiempo_promedio_espera}")
    #     else:
    #         print("\nNo se han completado procesos para calcular los tiempos promedio.")

def main():
    if len(sys.argv) < 2:
        print("Falta ingresar el nombre del archivo con el workload")
        exit(1)

    carga = CargaTrabajo(sys.argv[1])
    simulador = Simulador(carga)

    print("Carga de trabajo:")
    print(carga)

    input("Presiona Enter para comenzar la simulación...")

    while simulador.cola_procesos or simulador.procesando:
        simulador.asignar_memoria(simulador.cola_procesos[0] if simulador.cola_procesos else None)
        simulador.planificar_cpu()
        simulador.mostrar_estado()
        input("Presiona Enter para avanzar al siguiente paso...")

    # simulador.finalizar_simulacion()



if __name__ == "__main__":
    main()
