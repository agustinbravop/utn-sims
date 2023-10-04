class Proceso:
    def __init__(self, id, memoria_necesaria, cuando_entra, cuanto_consume, nro_orden):
        self.id = id
        self.memoria_necesaria = memoria_necesaria
        self.tiempo_arribo = cuando_entra
        self.tiempo_irrupcion = cuanto_consume
        self.nro_orden = nro_orden  # me dice en el orden que cpu los va a ejecutar

    def __str__(self):
        return f"Proceso {self.id}|{self.memoria_necesaria} MB"


class Memoria:
    def __init__(self, id, tamaño, posicion_inicio, fragmentacion_interna, proceso_asignado):
        self.id = id
        self.tamaño = tamaño
        self.posicion_inicio = posicion_inicio
        self.fragmentacion_interna = fragmentacion_interna
        # false no hay procesos o sino contendra al propio proceso.
        self.proceso_asignado = proceso_asignado
        self.tiempo = 2  # quantum que se va restando por cada tiempo
        self.procesando = False

    def __bool__(self):
        if self.proceso_asignado == False:
            return False
        else:
            return True

    def __str__(self):
        if self.proceso_asignado != False:
            return f"contiene a proceso:{self.proceso_asignado.id}| fragmentacion: {self.fragmentacion_interna}MB|procesando:{self.procesando}"
        else:
            return "vacio"


class session:

    def __init__(self):

        def crear_memoria():
            lista = []
            for i in range(1, 4):

                if i == 1:
                    memoria = Memoria(i, 60, "001x00", 60, False)
                    lista.append(memoria)
                elif i == 2:
                    memoria = Memoria(i, 120, "005x00", 120, False)
                    lista.append(memoria)
                elif i == 3:
                    memoria = Memoria(i, 250, "010x00", 120, False)
                    lista.append(memoria)
            return lista

        def crear_entrada():
            entrada = []

            for i in range(1, 11):

                if i == 1:
                    tamaño_memoria = 100
                    entra = 0
                    consume = 3
                elif i == 2:
                    tamaño_memoria = 50
                    entra = 1
                    consume = 1
                elif i == 3:
                    tamaño_memoria = 200
                    entra = 2
                    consume = 1
                elif i == 4:
                    tamaño_memoria = 60
                    entra = 4
                    consume = 4
                elif i == 5:
                    tamaño_memoria = 120
                    entra = 2
                    consume = 6
                else:
                    tamaño_memoria = 250
                    consume = 2
                    entra = 0

                proceso = Proceso(i, tamaño_memoria, entra, consume, i)
                entrada.append(proceso)
            return entrada

        def consultar_cola_entrada(tiempo):

            # contabilizo la cantidad de procesos en el sistema para saber el grado de multiprogramacion en el tiempo x
            cont = 0
            for memoria_unitaria in self.lista_memoria:
                if memoria_unitaria.proceso_asignado != False:
                    cont += 1
            multiprogramacion = len(self.lista_listo)+cont

            # necesito ahora saber si en este tiempo hay procesos que agregar
            # si hay proceso que agregar entonces lo que hacemos es decidir en que lista lo ponemos (suspendido o listo)
            # para mas facilidad los procesos ya estan ordenados por tiempo asique si ya cambia el tiempo del proceso no es necesario seguir iterando

            for i, proceso in enumerate(self.entrada):

                # ATENCION FALTARIA VER QUE SI HAY UN PROCESO EN SUSPENDIDO PARA PONERLO EN LISTO CUANDO HAY ESPACIO
                # print(f"tiempo_arribo:{proceso.tiempo_arribo}del proceso:{proceso.id}| tiempo:{tiempo}")

                if proceso.tiempo_arribo == tiempo:

                    if multiprogramacion < 5:
                        self.lista_listo.append(proceso)

                        # print("agrege el proceso",proceso.id,"a la cola de listos")
                        multiprogramacion = multiprogramacion+1

                    else:
                        # si es igual porque mayor ya es un error
                        if multiprogramacion == 5:
                            self.lista_suspendido.append(proceso)

                            # print("agrege el proceso",proceso.id,"a la cola de suspendidos")

            # RAAAARO ESTA SOLUCION
            # creo dos listas con todo los ids
            ids_suspendidos = [proceso.id for proceso in self.lista_suspendido]
            ids_listos = [proceso.id for proceso in self.lista_listo]
            self.entrada = [proceso for proceso in self.entrada if (
                proceso.id not in ids_suspendidos) and (proceso.id not in ids_listos)]
            print("----------------------------------------------------------------")
            return multiprogramacion

        """def planificador(entrada):
            
            #la entrada se encuentra ordenada por tiempo de arribo 
            fin=False
            indice=0 #reccorre mi entrada de procesos [proceso1,proceso2,proceso3]
            tiempo_actual=0#es el que me marca en que tiempo estamos dentro del simulador
            Proceso=entrada[indice]
            while not fin :    

                
                

                if Proceso.tiempo_irrupcion>=2 and Proceso.tiempo_arribo<=tiempo_actual:
                    Proceso.tiempo_irrupcion=Proceso.tiempo_irrupcion-2
                    self.cronograma.append(Proceso.id)
                    self.cronograma.append(Proceso.id)
                    
                else:
                    if Proceso.tiempo_irrupcion==1 and Proceso.tiempo_arribo<=tiempo_actual:
                        Proceso.tiempo_irrupcion=Proceso.tiempo_irrupcion-1
                        self.cronograma.append(Proceso.id)
                        
                    else:
                        if Proceso.tiempo_arribo>tiempo_actual:
                            tiempo_actual+=1

                indice+=1
                Proceso=entrada[indice]

            

            pass"""

        # ----------------------------------------------inicio programa-------------------------------------------------------------#

        # creo la memoria del simulador y lo pongo cada particion en un elemento de la lista
        self.lista_memoria = crear_memoria()

        # creo las entradas  es decir configuro las caracteristicas de cada proceso
        self.entrada = crear_entrada()

        self.orden = 0
        # ordena por tiempo de arribo todo los procesos
        self.entrada.sort(key=lambda proceso: proceso.tiempo_arribo)

        for proceso in self.entrada:
            self.orden += 1
            proceso.nro_orden = self.orden

        # algoritmo de planificacion de procesos.
        # devuelve una lista con el cronograma de ejecucion en memoria de cada proceso. (canda elemento se corresponde a un tiempo diciendo que proceso tiene que estar procesando)
        # self.cronograma=planificador(self.entrada)

        # variables inicializadas

        self.lista_salida = []
        self.lista_listo = []
        self.lista_suspendido = []

        fin = False
        tiempo = 0  # el tiempo en que esta el programa
        # inicialmente si puedo agregar a la memoria otro.
        self.puedo_procesar_otro = True
        # me dice cual se tiene que procesar ahora en funcion al orden

        while not fin:
            print("TIEMPO:", tiempo)

            self.mutiprogramacion = consultar_cola_entrada(tiempo)

            self.control_memoria()

            self.asignar_proceso()

            tiempo += 1

            listos = [str(proceso) for proceso in self.lista_listo]
            salida = [str(proceso) for proceso in self.lista_salida]
            suspendido = [str(proceso) for proceso in self.lista_suspendido]
            print(f"cola de listos: {listos}")
            print(f"cola de suspendidos:{suspendido}")
            print(f"cola de salida:{salida}")

            print("")
            print("EN LA MEMORIA:")
            print("")
            print("")
            for i, fragmentacion in enumerate(self.lista_memoria):
                print(i, ")  ", fragmentacion)

            fin = input()

            if fin != "":
                break

    def control_memoria(self):
        """verificara que no se hayan pasado en tiempo los procesos en memoria si es el caso los saca 
        y los asignamos o a:
        cola de listos , listos y suspendidos  o  cola de salida"""

        for memoria in self.lista_memoria:

            if memoria.proceso_asignado:

                if memoria.procesando:
                    # descuento porque ya paso un tiempo
                    memoria.tiempo = memoria.tiempo-1
                    memoria.proceso_asignado.tiempo_irrupcion = memoria.proceso_asignado.tiempo_irrupcion-1

                    if memoria.tiempo <= 0 or memoria.proceso_asignado.tiempo_irrupcion <= 0:
                        # tiene que salir el proceso de memoria para eso tengo que verificar
                        # que el proceso le falte todavia o ya esta listo

                        if memoria.proceso_asignado.tiempo_irrupcion <= 0:
                            self.lista_salida.append(
                                memoria.proceso_asignado.id)
                            print("lista salida:", self.lista_salida)
                        else:
                            """si bien saque ya un proceso y la multiprogramacion =4 el proceso
                            sera el ultimo en procesarce entonces le doy espacio que un proceso
                            que esta mas tiempo en la lista de suspendidos pueda entrar"""
                            memoria.proceso_asignado.nro_orden = self.orden
                            if self.mutiprogramacion == 5:

                                self.lista_suspendido.append(
                                    memoria.proceso_asignado)
                            else:
                                self.lista_listo.append(
                                    memoria.proceso_asignado)

                            # cuando quede un proceso inicialmente estara en 1 y  cuando lo quite la
                            # asignacion este estare en 0
                            self.mutiprogramacion = self.mutiprogramacion-1

                        """reseteo todo"""
                        memoria.tiempo = 2
                        memoria.proceso_asignado = False  # saco de memoria
                        # habilito a que se elija otro para procesar.
                        self.puedo_procesar_otro = True
                        # la memoria ya no esta proceso nada.
                        memoria.procesando = False

            else:
                # verifico si puedo asignar un proceso

                for proceso in self.lista_listo:

                    if proceso.memoria_necesaria <= memoria.tamaño and not memoria.proceso_asignado:
                        # tiene la capacidad de ingresar y como el recorrido del memoria de de
                        # menor a mayor entonces es el minimo donde puede ingresar

                        memoria.fragmentacion_interna = memoria.tamaño-proceso.memoria_necesaria
                        memoria.proceso_asginado = proceso
                        break

    def asignar_proceso(self):
        """ en este apartado asigno los distintos procesos a la memoria. y ademas pregunto si ya se habilito  para que el procesador ejecute en memoria """

        # -por lo tanto tengo en la cola de listos los procesos.

        # -deberia preguntar si hay espacios en memoria en caso de que si recorro la cola de listo y veo si entra alguno en esos espacios.

        for particion in self.lista_memoria:
            if particion.proceso_asignado == False:

                tamaño = particion.tamaño

                for proceso in self.lista_listo:

                    if proceso.memoria_necesaria <= tamaño:
                        # cargo el proceso a memoria
                        particion.proceso_asignado = proceso
                        particion.fragmentacion_interna = tamaño - \
                            particion.proceso_asignado.memoria_necesaria
                        print("cargue proceso a memoria :",
                              particion.proceso_asignado.id)
                        # lo quito de la cola de listos
                        self.lista_listo.remove(proceso)

        # para este punto recorri toda la memoria y asigne si habia espacio el proceso que estaba en cola de listo.

        # -----------------------procesar memoria-----------------------------------------------#
        menor = 400009
        if self.puedo_procesar_otro:
            # si estra aca es porque puedo asignar un proceso  de los que esta en memoria a que trate el procesador segun el numero de orden
            # EL NUMERO DE ORDEN SE LE ASIGNA A LOS PROCESOS CONFORME se fueron creando O una vez que salen de memoria porque termino su turno.
            bandera = False
            for particion in self.lista_memoria:

                if particion.proceso_asignado != False:

                    if menor > particion.proceso_asignado.nro_orden:

                        menor = particion.proceso_asignado.nro_orden
                        memoria = particion
                        bandera = True
                else:
                    # si para 3 veces por aca la memoria ya esta vacia y no hay nada que asignar
                    print("")
            # cuando salga SI O SI eligio un proceos a tratar O la memoria esta vacia.

            if bandera:
                memoria.procesando = True
                print(f"procesando: {memoria.proceso_asignado.id}")


session()
