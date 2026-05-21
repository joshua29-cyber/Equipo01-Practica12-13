#Código 2: Demostración de master (Sin Barrera)
#Objetivo en la expo: Mostrar que estrictamente el proceso 0 trabaja, pero los procesos 1, 2 y 3 no lo esperan, sino que avanzan y terminan de inmediato.

import multiprocessing
import time

def tarea(id_proceso):
    if id_proceso == 0:
        print(f"[Proceso {id_proceso}] ---> Ejecutando bloque MASTER (Solo Proceso 0). Esperen 3 segundos...")
        time.sleep(3)
        print(f"[Proceso {id_proceso}] ---> Bloque MASTER terminado.")
    
    print(f"[Proceso {id_proceso}] Salió del bloque y continuó inmediatamente.")

if __name__ == "__main__":
    print("=== DEMO 2: SIMULACION OMP MASTER (SIN BARRERA) ===\n")
    
    num_procesos = 4
    procesos = []
    for i in range(num_procesos):
        p = multiprocessing.Process(target=tarea, args=(i,))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()