import sys

from CargaTrabajo import CargaTrabajo
from Simulador import Simulador


def input_avanzar(prompt: str):
    """Pide al usuario una acción para avanzar o terminar la simulación."""
    try:
        inp = input(prompt)
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
    print("Presione q + Enter para terminar el programa.")
    input_avanzar("Presione Enter para comenzar la simulación...")

    for nuevo in simulador.procesos_nuevos():
        simulador.admitir_proceso(nuevo)
    simulador.asignar_cpu()
    simulador.mostrar_estado()
    input_avanzar("Presione Enter para avanzar o q + Enter para salir...")

    while simulador.carga_trabajo or simulador.ejecutando:
        simulador.t += 1
        simulador.quantum = simulador.quantum % 2 + 1
        for nuevo in simulador.procesos_nuevos():
            simulador.admitir_proceso(nuevo)
        simulador.planificar_cpu()

        simulador.mostrar_estado()
        simulador.estadistico()
        input_avanzar("Presione Enter para avanzar o q + Enter para salir...")
    


if __name__ == "__main__":
    main()
