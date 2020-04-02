El programa se invoca mediante:
./blocks
o
pyhton blocks

blocks <file> [-heuristic] [-noshift] [-telpath <path>]

El primer argumento es siempre la ruta del fichero con la codificación del problema.

Opciones:
-heuristic: Se calcula una solución de forma inmediata, pero puede no ser mínima.

-noshift: Por defecto las columnas resultado se situan en stacks colocados a partir del último stack del estado inicial, si este estaba en la posición n el primer stack del resultado se colocará en n+1, esta opción coloca las columnas resultado a partir de la primera posición. Dependiendo de la configuración del problema puede producir un cálculo mucho más rápido de una solución mínima.

-telpath: Por algún motivo en algunas instalaciones no se puede localizar el binario de telingo en el PATH al invocarlo con system. Con esta opción se le puede pasar la ruta al directorio que contiene el ejecutable.
Ej: ./blocks .dom01.txt -telpath /home/user/anaconda3/bin/

Tiempos:
           P1    P2    P3    P4    P5    P6
 Default   0s    1s    1s    3.5s  6m    ~
-noshift   0s    0.1s  0.2s  0.5s  6.5s  35s