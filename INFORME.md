**Informe:** Escape Room

---

## 1. Introducción

Este proyecto implementa un sistema que modela un escape room como un grafo dirigido y obtiene automáticamente un camino desde una sala inicial hasta una meta. En el recorrido pueden aparecer salas bloqueadas; cada una se asocia a un subproblema modelado como un segundo grafo con costos, que se resuelve con **A\*** antes de permitir continuar la exploración principal.

La solución sigue una arquitectura en dos niveles: **búsqueda no informada** (BFS, DFS o UCS) sobre el mapa global y **búsqueda informada** sobre los acertijos, coordinadas por un motor central y acompañadas de una interfaz gráfica que separa ambos contextos.

---

## 2. Modelado del problema

El escenario se describe en **`data/escape_room.json`**. Allí se define un `global_graph` (nodos, aristas dirigidas, inicio y meta) y, aparte, un bloque `puzzles` con subgrafos independientes: nodos propios del candado, aristas con **costo**, estado inicial y meta del subproblema, y valores de **heurística** por nodo.

En código, el paquete **`graph/`** traduce ese esquema en objetos reutilizables: nodos con estado (`bloqueado`, `disponible`, `resuelto`), el grafo global (`EscapeGraph`) con listas de adyacencia, y el grafo de cada candado (`PuzzleGraph`) con pesos y función \(h(n)\) leída del JSON (con valor por defecto 0 si falta alguna clave). La orientación de las aristas respeta siempre el sentido `from` → `to` definido en el archivo.

En el escenario de referencia del repositorio, el recorrido global va desde la entrada **A** hasta la salida **M**; salas como **C** o **K** pueden aparecer bloqueadas y enlazar a un puzzle concreto (`puzzle_C`, `puzzle_K`). Los estados internos del candado (por ejemplo inicio y meta del subgrafo) no coinciden con los ids del mapa principal, lo que deja claro que el acertijo es un espacio de búsqueda aparte que solo se conecta con el global al desbloquear la sala correspondiente.

---

## 3. Búsqueda en el grafo global

En **`search/uninformed.py`** se implementan **BFS** (cola FIFO), **DFS** (pila LIFO) y **UCS** (cola de prioridad por costo acumulado). Los tres comparten la misma idea operativa: al expandir un nodo que sigue bloqueado, se invoca un callback que intenta resolver el puzzle asociado; si el desbloqueo falla, esa rama se abandona.

En el grafo global del JSON no hay pesos explícitos: **BFS** y **DFS** reportan costo en función del número de aristas del camino encontrado, mientras que **UCS** asigna costo unitario a cada arista, equivalente a un mapa homogéneo. El usuario elige el algoritmo desde la interfaz o desde línea de comandos. En la práctica, BFS tiende a hallar soluciones de menor profundidad en número de pasos cuando el costo es uniforme; DFS explora en profundidad y UCS coincide con BFS en este mapa mientras todas las aristas valgan lo mismo.

---

## 4. Resolución de candados (A\*)

Los subproblemas se resuelven en **`search/informed.py`** con **A\***: se mantiene una frontera ordenada por \(f = g + h\), donde \(g\) es el costo acumulado según las aristas del puzzle y \(h\) proviene del archivo de datos. Se lleva un registro del mejor \(g\) alcanzado por nodo para descartar caminos dominados y reducir trabajo redundante en la cola de prioridad.

El resultado incluye camino, costo total, nodos expandidos y un registro textual útil para consola o depuración.

---

## 5. Integración, métricas y ejecución

El módulo **`engine/solver.py`** (`EscapeSolver`) enlaza ambas capas: durante la búsqueda global, cada bloqueo delega en A\*; si el candado tiene éxito, el nodo pasa a disponible y se acumulan estadísticas. Si un puzzle ya fue resuelto en la misma ejecución, no se vuelve a ejecutar el algoritmo informado para ese nodo.

Las métricas quedan centralizadas en **`ExecutionMetrics`**: expansiones y profundidad en el mapa principal, costo y camino global, totales agregados de expansiones y costo en puzzles, y tiempo de ejecución de la corrida completa. El sistema también genera mensajes de trazabilidad (expansiones, detección de bloqueo, delegación al puzzle y meta alcanzada) que la interfaz o el modo consola pueden mostrar al usuario.

El punto de entrada es **`main.py`**: sin argumentos abre la interfaz; con `--cli` y el nombre del algoritmo (`BFS`, `DFS`, `UCS`) ejecuta el mismo flujo en consola. Opcionalmente `--json` indica otra ruta de escenario. Se ajustó la salida estándar a UTF-8 cuando el entorno lo permite, para evitar fallos de codificación en Windows al imprimir símbolos extendidos.

---

## 6. Interfaz gráfica

La aplicación en **`ui/interface.py`** construye una ventana con **Tkinter** y dos paneles principales con **Matplotlib** y **NetworkX**: a la izquierda el grafo global y la leyenda de estados; a la derecha el puzzle activo, con costos visibles en las aristas cuando corresponde. En la parte inferior hay una consola de mensajes y un panel de estadísticas que distingue resultados del recorrido global y de los subproblemas. La ejecución del solver se lanza en un hilo aparte para que la ventana permanezca responsiva.

En la barra superior se elige el algoritmo global, se ejecuta la búsqueda, se reinicia el estado y se puede cargar otro archivo JSON sin salir de la aplicación. Al finalizar una corrida exitosa, el camino global puede resaltarse sobre el dibujo del grafo para facilitar la lectura del resultado.

---

## 7. Conclusiones

El trabajo cumple el planteamiento del curso: modelado explícito del escape y de los candados, algoritmos no informados configurables en el nivel global, **A\*** con heurística en el nivel local, integración mediante un solo orquestador y presentación gráfica con trazas y métricas.

La organización del código por carpetas (`graph`, `search`, `engine`, `ui`) separa con claridad datos y modelos, algoritmos, lógica de integración y presentación, lo que facilita el mantenimiento y la sustentación del proyecto. Las dependencias principales (**matplotlib**, **networkx**, **numpy** y librerías asociadas) están declaradas en **`requirements.txt`**, lo que permite reproducir el entorno con un entorno virtual estándar de Python.
