# Equipo01-Practica12-13

-  - Jaqueline 
- 322164583 - Oseguera Salinas Joshua Jacob
- 322216754 - Soto Fuentes Christian Ulises

---

# Contexto y teoría

Cuando se trabaja con programación multihilo en OpenMP, la regla general es que todos los hilos ejecuten el código en paralelo dentro de una región activa. Sin embargo, existen momentos clave donde se requiere un control más estricto: ya sea porque una tarea específica la debe ejecutar un solo hilo, o porque todos los hilos deben esperarse obligatoriamente en un punto específico para evitar corromper los datos en la memoria. Para lograr este control sin destruir el rendimiento del procesador, OpenMP proporciona cuatro herramientas fundamentales de sincronización fina:
El dilema de la ejecución única: master vs single
Aunque ambas directivas sirven para que un bloque de código sea ejecutado por un único hilo, su comportamiento interno es radicalmente opuesto debido a la gestión de las esperas:

#pragma omp master: Asigna el trabajo únicamente al hilo principal (el hilo 0). Los demás hilos del equipo ignoran por completo este bloque de código y continúan con las líneas siguientes de inmediato. En master no existe ninguna barrera implícita.

#pragma omp single: Delega la tarea al primer hilo que vaya llegando, sin importar su ID. Sin embargo, a diferencia de master, single sí tiene una barrera implícita al final de su bloque. Esto significa que todos los hilos esclavos que terminen temprano sus tareas previas se quedarán congelados perdiendo tiempo de CPU, esperando a que ese único hilo elegido termine de procesar el bloque single.

La optimización del flujo: nowait
La cláusula nowait es una herramienta diseñada para destruir la barrera implícita de constructores como single. Al escribir #pragma omp single nowait, se le indica a OpenMP que un solo hilo resuelva esa sección, pero que libere inmediatamente a los demás para que sigan de largo con las instrucciones subsecuentes. Es el mecanismo ideal para mantener la fluidez cuando las tareas posteriores son independientes de lo que pasa dentro del bloque single.

El freno absoluto: barrier
Cuando la lógica del algoritmo requiere obligatoriamente que una etapa termine antes de pasar a la siguiente por seguridad de los datos, se recurre a la sincronización explícita con #pragma omp barrier. Una barrera actúa como un muro: ningún hilo puede cruzarlo hasta que el último hilo del equipo haya llegado a ese punto, garantizando la consistencia de la memoria.
---

## Demo y Análisis de Resultados 

Para analizar el comportamiento de estos constructores visualmente, se utilizan dos scripts en Python mediante el módulo multiprocessing. Aunque OpenMP es nativo de C, estas simulaciones recrean la semántica exacta de la sincronización fina y la diferencia entre hilos y procesos (donde los procesos manejan memorias aisladas y los hilos comparten el mismo espacio de variables).

**Demo 1: Simulación de single (Con Barrera Implícita)**
Este código demuestra cómo los procesos libres se ven obligados a detenerse al final del bloque debido al freno automático.

Comportamiento en la Terminal:

- Los 4 procesos inician simultáneamente imprimiendo su mensaje de inicio.
- Un proceso aleatorio (por ejemplo, el Proceso 2) gana el cerrojo, entra al bloque simulado de single y se duerme por 3 segundos.
- Los procesos 0, 1 y 3 avanzan rápido, pero se quedan completamente congelados en la línea del barrera_single.wait().
- Al cumplirse los 3 segundos, el proceso 2 despierta, llega a la barrera y en ese instante se liberan los 4 procesos de golpe, imprimiendo el mensaje final al mismo tiempo.

**Demo 2: Simulación de master (Sin Barrera)**
Este segundo script demuestra la naturaleza asíncrona de master, donde el trabajo se restringe por ID estático y no existen frenos automáticos.

Comportamiento en la Terminal:

- Los procesos 1, 2 y 3 evalúan el if, ven que no son el ID 0 y saltan directo a la línea de salida. Imprimen de inmediato en la terminal que continuaron su camino, sin esperar a nadie.
- Al mismo tiempo, el Proceso 0 entra al bloque del if y se duerme por 3 segundos.
- La consola hace una pausa, pero la ejecución de los procesos 1, 2 y 3 ya concluyó con éxito.
- Pasados los 3 segundos, el Proceso 0 despierta solo, imprime que el bloque terminó y se despide de la consola de forma independiente.

**Demo 3: Simulación de single con nowait (Optimización de Rendimiento)**
El objetivo de esta demostración es mostrar cómo la cláusula nowait altera por completo al constructor single. Al retirar la barrera implícita, los procesos que no entran al bloque ya no se quedan congelados perdiendo tiempo; continúan trabajando de inmediato en paralelo.

Comportamiento en la Terminal:

- Los 4 procesos inician en paralelo.
- Un proceso toma el bloque single e inicia su espera de 3 segundos.
- A diferencia de la Demo 1, los otros 3 procesos no se detienen. Verás que inmediatamente imprimen Salió del bloque y continuó inmediatamente., terminando su trabajo al 100%
  de eficiencia de la CPU.
- Al final de los 3 segundos, el proceso rezagado despierta solo y concluye, demostrando que nowait eliminó los tiempos muertos.


**Demo 4: El efecto de quitar el barrier (Condición de Carrera)**
Esta demo expone el peligro de la asincronía descontrolada. Muestra qué sucede cuando las tareas posteriores sí dependen de los datos que se calculan dentro de una sección única, pero decidimos quitar un freno o una barrera explícita por descuido. Los procesos intentarán usar datos que aún no existen o que están incompletos.

Comportamiento en la Terminal al quitar el barrier (activar_barrera = False):

- Los procesos inician y el Proceso 0 comienza a calcular el dato (tarda 2 segundos).
- Como no hay un muro de contención, los procesos 1, 2 y 3 pasan directo a la lectura de la memoria.
- En la pantalla verás que los procesos 1, 2 y 3 imprimen: Leyendo dato compartido -> Valor leído: 0. ¡Esto es un error algorítmico grave! Leyeron basura o un estado inicial 
  inválido porque no se esperaron.
- Dos segundos después, el Proceso 0 termina e imprime ¡Dato listo!, y posteriormente lee su propio valor modificado (Valor leído: 42). El programa ha fallado silenciosamente
  debido a una condición de carrera.

Comportamiento si se activa la barrera (activar_barrera = True):

- Todos los procesos se ven obligados a congelarse. Ninguno lee la memoria hasta que el Proceso 0 termina de escribir el 42 y llega a la barrera. Al liberarse, los 4 procesos
  leen exitosamente el valor correcto (42), garantizando la consistencia.


**El peligro latente: La condición de carrera**
Si en un experimento real se cuenta con código que depende directamente de los datos calculados dentro de una sección única (como single nowait o master) y se decide retirar un #pragma omp barrier explícito necesario, el flujo se vuelve caótico. Los hilos más veloces intentarán leer las variables en memoria antes de que el hilo asignado termine de escribir en ellas, provocando una condición de carrera (race condition) que corrompe los resultados del programa haciéndolos impredecibles.


---

## Parte 3: Conclusiones 

La sincronización fina demuestra que el desarrollo eficiente en entornos de computación paralela no consiste únicamente en lanzar hilos a correr al mismo tiempo; el verdadero reto de la ingeniería de software es saber gobernarlos de forma óptima.

El gran peligro al diseñar algoritmos en OpenMP es caer en el "cuello de botella por exceso de celo". Esto ocurre cuando un programador, por miedo a que los hilos alteren el orden o generen inconsistencias, abusa de las restricciones y llena el código de barreras innecesarias. Este exceso de protección obliga a procesadores multinúcleo de última generación a quedarse ociosos en tiempos muertos, lo que destruye el paralelismo y serializa el código de forma artificial, anulando por completo las ventajas del hardware moderno.

Dominar herramientas asíncronas como master y la cláusula nowait permite eliminar esos tiempos muertos y mantener el programa lo más libre, fluido y asíncrono posible. La regla de oro de la sincronización fina es dar vía libre al procesamiento cooperativo y aplicar los frenos estricto o barreras única y exclusivamente cuando la integridad de la memoria esté verdaderamente en riesgo.


---

# Presentacion 

- https://canva.link/q68vrecijoq5jzj

---

# Fuentes

- Chapman, B., Jost, G., & van der Pas, R. (2007). Using OpenMP: Portable Shared Memory Parallel Programming. MIT Press.
- Lawrence Livermore National Laboratory. (s.f.). OpenMP Tutorial. High Performance Computing (HPC). https://hpc.llnl.gov/tutorials/openmp
- OpenMP Architecture Review Board. (2020). OpenMP Application Program Interface Specification Version 5.1. https://www.openmp.org/specifications/

