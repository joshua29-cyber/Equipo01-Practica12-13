#Código 3: El Caos al quitar el barrier (Condición de Carrera)
#Objetivo en la expo: Mostrar el desorden que ocurre cuando los hilos avanzan a la fase final sin que el proceso principal haya terminado de preparar los datos simulados.

import multiprocessing
import time

def tarea(id_proceso, bandera_ejecutado):
    with bandera_ejecutado.get_lock():
        if not bandera_ejecutado.value:
            bandera_ejecutado.value = True
            print(f"[Proceso {id_proceso}] ---> Simulando preparación de datos (3 segundos)...")
            time.sleep(3)

    if id_proceso == 0:
        print(f"\n[Proceso {id_proceso} - Maestro] !!! ATENCION !!! Imprimiendo resultados finales...")

    print(f"[Proceso {id_proceso}] Intentando leer/escribir datos en memoria.")

if __name__ == "__main__":
    print("=== DEMO 3: SIN BARRIER (CONDICION DE CARRERA) ===\n")
    
    num_procesos = 4
    ejecutado = multiprocessing.Value('b', False)
    
    procesos = []
    for i in range(num_procesos):
        p = multiprocessing.Process(target=tarea, args=(i, ejecutado))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()