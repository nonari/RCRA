El programa se invoca mediante:
./blocks
o
pyhton blocks

blocks <file> [-heuristic] [-telpath <path>]

El primer argumento es siempre la ruta del fichero con la codificación del problema.

Opciones:
-heuristic: Se calcula una solución de forma rápida, pero puede no ser mínima (lo es en todos los problemas propuestos).
La heuristica consiste en desapilar primero de aquel stack en el que el próximo movimiento constructivo está a menor profundidad.

-telpath: Por algún motivo en algunas instalaciones no se puede localizar el binario de telingo en el PATH al invocarlo con system. Con esta opción se le puede pasar la ruta al directorio que contiene el ejecutable.
Ej: ./blocks .dom01.txt -telpath /home/user/anaconda3/bin/

Aclaraciones:
El programa representa internamente los movimientos como mov(B,S), donde S es un stack.
No tenemos movimientos m(B,0) ya que cada bloque desapilado no constructivo siempre se apila en un stack
nombrado como el propio bloque.
Tras recuperar la solución de telingo los movimientos se traducen al formato propuesto en el enunciado del problema m(B1,B2).

El problema 4 tarda 15s, los siguientes tardan demasiado.