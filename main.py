import sys
from typing import List
from tabulate import tabulate


class Proceso:
    def __init__(self, pid: int, arribo: int, irrupcion: int, memoria: int):
        self.pid = pid
        self.t_arribo = arribo
        self.t_irrupcion = irrupcion
        self.memoria = memoria
        self.procesando = False

    def __str__(self):
        return f"{self.pid}|{self.t_arribo}|{self.t_irrupcion}|{self.memoria}"


class CargaTrabajo:
    headers = ["PID", "tArribo", "tIrrupción", "Mem"]

    # Inicializa una CargaTrabajo a partir de un archivo CSV.
    def __init__(self, archivo: str):
        self.procesos: List[Proceso] = []
        with open(archivo, "r") as f:
            lineas = f.readlines()
            for linea in lineas:
                [pid, ta, ti, mem] = linea.split(";")
                self.procesos.append(Proceso(int(pid), int(ta), int(ti), int(mem)))

    # Muestra la CargaTrabajo en formato tabla.
    def __str__(self):
        tabla = []
        for p in self.procesos:
            tabla.append([p.pid, p.t_arribo, p.t_irrupcion, p.memoria])

        return tabulate(tabla, headers=self.headers, tablefmt="pretty", stralign="right")


def main():
    if len(sys.argv) < 2:
        print("Falta ingresar el nombre del archivo con el workload")
        exit(1)

    carga = CargaTrabajo(sys.argv[1])
    print(carga)


if __name__ == "__main__":
    main()
