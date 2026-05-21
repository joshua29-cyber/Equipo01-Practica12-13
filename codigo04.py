#Código 4: Optimización con nowait
#Objetivo en la expo: Mostrar cómo logramos que la tarea la haga un único proceso cualquiera (como en single), pero eliminando la barrera para que los demás sigan trabajando de largo sin perder tiempo ocioso.

import multiprocessing
import time

def tarea(id_proceso, bandera_ejecutado):
    with bandera_ejecutado.get_lock():
        if not bandera_ejecutado.value:
            bandera_ejecutado.value = True
            print(f"[Proceso {id_proceso}] ---> Ejecutando SINGLE con NOWAIT. Tardaré 3 segundos...")
            time.sleep(3)
            print(f"[Proceso {id_proceso}] ---> SINGLE con NOWAIT finalizado.")

    print(f"[Proceso {id_proceso}] Avanzó sin esperar a que el single terminara.")

if __name__ == "__main__":
    print("=== DEMO 4: SIMULACION OMP SINGLE NOWAIT ===\n")
    
    num_procesos = 4
    ejecutado = multiprocessing.Value('b', False)
    
    procesos = []
    for i in range(num_procesos):
        p = multiprocessing.Process(target=tarea, args=(i, ejecutado))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()