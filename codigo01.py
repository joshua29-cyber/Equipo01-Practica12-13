#Código 1: Demostración de single (Barrera Implícita)
#Objetivo en la expo: Mostrar cómo un solo proceso ejecuta el bloque y todos los demás se quedan completamente congelados al final de este, esperando a que termine.

import multiprocessing
import time

def tarea(id_proceso, barrera_single, bandera_ejecutado):
    print(f"[Proceso {id_proceso}] Iniciando...")
    
    with bandera_ejecutado.get_lock():
        if not bandera_ejecutado.value:
            bandera_ejecutado.value = True
            print(f"[Proceso {id_proceso}] ---> Ejecutando bloque SINGLE. Esperen 3 segundos...")
            time.sleep(3)
            print(f"[Proceso {id_proceso}] ---> Bloque SINGLE terminado.")
            
    barrera_single.wait()

    print(f"[Proceso {id_proceso}] Salió del bloque y continuó inmediatamente.")

if __name__ == "__main__":
    print("=== DEMO 1: SIMULACION OMP SINGLE (CON BARRERA) ===\n")
    
    num_procesos = 4
    barrera = multiprocessing.Barrier(num_procesos)
    ejecutado = multiprocessing.Value('b', False) 
    
    procesos = []
    for i in range(num_procesos):
        p = multiprocessing.Process(target=tarea, args=(i, barrera, ejecutado))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()