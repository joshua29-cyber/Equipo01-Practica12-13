//Código 4: Optimización con nowait
//Objetivo en la expo: Mostrar cómo logramos que la tarea la haga un único proceso cualquiera (como en single), pero eliminando la barrera para que los demás sigan trabajando de largo sin perder tiempo ocioso.

#include <iostream>
#include <omp.h>
#include <unistd.h> // sleep()

using namespace std;

int main() {

    cout << "=== DEMO 4: OMP SINGLE NOWAIT ===\n\n";

    #pragma omp parallel num_threads(4)
    {
        int id = omp_get_thread_num();

        #pragma omp single nowait
        {
            cout << "[Hilo " << id << "] ---> Ejecutando SINGLE con NOWAIT. Tardaré 3 segundos...\n";
            sleep(3);
            cout << "[Hilo " << id << "] ---> SINGLE con NOWAIT finalizado.\n";
        }

        cout << "[Hilo " << id << "] Avanzó sin esperar al single.\n";
    }

    return 0;
}
