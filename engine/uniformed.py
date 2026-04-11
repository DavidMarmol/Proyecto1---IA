"""
uninformed.py
-------------
Implementa los tres algoritmos de búsqueda no informada para recorrer
el grafo global del escape room:

  - BFS  (Breadth-First Search  / Búsqueda en Amplitud)
  - DFS  (Depth-First Search    / Búsqueda en Profundidad)
  - UCS  (Uniform-Cost Search   / Búsqueda de Costo Uniforme)

Todos los algoritmos comparten la misma interfaz de retorno y manejan
el caso especial de nodos bloqueados delegando al motor (engine) a
través de un callback.

Interfaz de retorno (SearchResult):
------------------------------------
  path            : lista de node_ids desde inicio hasta meta
  nodes_expanded  : cantidad de nodos expandidos
  depth           : profundidad máxima alcanzada
  cost            : costo total acumulado (1 por arista en BFS/DFS)
  log             : lista de mensajes de ejecución para la consola UI
"""

from collections import deque
import heapq
from typing import Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from graph.escape_graph import EscapeGraph

# ======================================================================
# Resultado de búsqueda
# ======================================================================


@dataclass
class SearchResult:
    path: List[str] = field(default_factory=list)
    nodes_expanded: int = 0
    depth: int = 0
    cost: float = 0.0
    log: List[str] = field(default_factory=list)
    success: bool = False


# ======================================================================
# Tipo del callback para nodos bloqueados
# on_locked(node_id) -> True si se logró desbloquear, False si falló
# ======================================================================

UnlockCallback = Callable[[str], bool]


# ======================================================================
# BFS  –  Búsqueda en Amplitud
# ======================================================================


def bfs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    """
    Recorre el grafo global con BFS (FIFO).
    Garantiza encontrar el camino con menos aristas (no necesariamente
    el de menor costo si hubiera pesos, pero en el nivel global las
    aristas no tienen peso diferenciado).
    """
    result = SearchResult()
    start, goal = graph.start, graph.goal

    # Cola: cada elemento es (path_hasta_aquí)
    queue: deque[List[str]] = deque()
    queue.append([start])
    visited: set = set()

    result.log.append(f"> Iniciando BFS desde '{start}' → meta '{goal}'")

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        result.nodes_expanded += 1
        result.depth = max(result.depth, len(path) - 1)
        result.log.append(f"> Expandiendo nodo {set(path)}")

        # Nodo bloqueado: intentar resolver puzzle
        node = graph.get_node(current)
        if node and node.is_locked:
            result.log.append(f"— Nodo bloqueado encontrado: {{{current}}}")
            result.log.append(
                f"— Iniciando búsqueda informada para Puzzle en Nodo {{{current}}}"
            )
            unlocked = on_locked(current)
            if not unlocked:
                result.log.append(
                    f"✗ No se pudo desbloquear {{{current}}}, rama descartada"
                )
                continue
            result.log.append(f"✓ Nodo {{{current}}} desbloqueado, continuando BFS")

        # Meta alcanzada
        if current == goal:
            node.mark_solved() if node else None
            result.path = path
            result.cost = float(len(path) - 1)
            result.success = True
            result.log.append(f"✓ META alcanzada: {' → '.join(path)}")
            return result

        # Marcar como resuelto y expandir vecinos
        if node:
            node.mark_solved()

        for neighbor_id in graph.neighbors(current):
            if neighbor_id not in visited:
                queue.append(path + [neighbor_id])

    result.log.append("✗ BFS: no se encontró camino a la meta")
    return result


# ======================================================================
# DFS  –  Búsqueda en Profundidad
# ======================================================================


def dfs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    """
    Recorre el grafo global con DFS (LIFO / pila).
    Puede no encontrar el camino más corto, pero usa menos memoria
    que BFS en grafos anchos.
    """
    result = SearchResult()
    start, goal = graph.start, graph.goal

    # Pila: cada elemento es (path_hasta_aquí)
    stack: List[List[str]] = [[start]]
    visited: set = set()

    result.log.append(f"> Iniciando DFS desde '{start}' → meta '{goal}'")

    while stack:
        path = stack.pop()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        result.nodes_expanded += 1
        result.depth = max(result.depth, len(path) - 1)
        result.log.append(f"> Expandiendo nodo {set(path)}")

        node = graph.get_node(current)
        if node and node.is_locked:
            result.log.append(f"— Nodo bloqueado encontrado: {{{current}}}")
            result.log.append(
                f"— Iniciando búsqueda informada para Puzzle en Nodo {{{current}}}"
            )
            unlocked = on_locked(current)
            if not unlocked:
                result.log.append(
                    f"✗ No se pudo desbloquear {{{current}}}, rama descartada"
                )
                continue
            result.log.append(f"✓ Nodo {{{current}}} desbloqueado, continuando DFS")

        if current == goal:
            if node:
                node.mark_solved()
            result.path = path
            result.cost = float(len(path) - 1)
            result.success = True
            result.log.append(f"✓ META alcanzada: {' → '.join(path)}")
            return result

        if node:
            node.mark_solved()

        # Invertir para mantener orden de izquierda a derecha
        for neighbor_id in reversed(graph.neighbors(current)):
            if neighbor_id not in visited:
                stack.append(path + [neighbor_id])

    result.log.append("✗ DFS: no se encontró camino a la meta")
    return result


# ======================================================================
# UCS  –  Búsqueda de Costo Uniforme
# ======================================================================


def ucs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    """
    Recorre el grafo global con UCS (cola de prioridad por costo).
    En el grafo global todas las aristas tienen costo 1, por lo que
    el resultado es equivalente a BFS, pero la implementación es
    correcta para grafos con pesos si se desea extender.
    """
    result = SearchResult()
    start, goal = graph.start, graph.goal

    # heap: (costo_acumulado, path)
    # Usamos un contador para desempate estable en el heap
    counter = 0
    heap: List[Tuple[float, int, List[str]]] = [(0.0, counter, [start])]
    visited: Dict[str, float] = {}  # id -> mejor costo conocido

    result.log.append(f"> Iniciando UCS desde '{start}' → meta '{goal}'")

    while heap:
        cost, _, path = heapq.heappop(heap)
        current = path[-1]

        if current in visited:
            continue
        visited[current] = cost
        result.nodes_expanded += 1
        result.depth = max(result.depth, len(path) - 1)
        result.log.append(f"> Expandiendo nodo {set(path)} (costo={cost:.1f})")

        node = graph.get_node(current)
        if node and node.is_locked:
            result.log.append(f"— Nodo bloqueado encontrado: {{{current}}}")
            result.log.append(
                f"— Iniciando búsqueda informada para Puzzle en Nodo {{{current}}}"
            )
            unlocked = on_locked(current)
            if not unlocked:
                result.log.append(
                    f"✗ No se pudo desbloquear {{{current}}}, rama descartada"
                )
                continue
            result.log.append(f"✓ Nodo {{{current}}} desbloqueado, continuando UCS")

        if current == goal:
            if node:
                node.mark_solved()
            result.path = path
            result.cost = cost
            result.success = True
            result.log.append(
                f"✓ META alcanzada (costo={cost:.1f}): {' → '.join(path)}"
            )
            return result

        if node:
            node.mark_solved()

        for neighbor_id in graph.neighbors(current):
            if neighbor_id not in visited:
                new_cost = cost + 1.0  # aristas sin peso → costo 1
                counter += 1
                heapq.heappush(heap, (new_cost, counter, path + [neighbor_id]))

    result.log.append("✗ UCS: no se encontró camino a la meta")
    return result


# ======================================================================
# Dispatcher  –  elige el algoritmo por nombre
# ======================================================================

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
}


def run_uninformed(
    algorithm: str, graph: EscapeGraph, on_locked: UnlockCallback
) -> SearchResult:
    """
    Ejecuta el algoritmo de búsqueda no informada seleccionado.

    Parámetros
    ----------
    algorithm : "BFS", "DFS" o "UCS"
    graph     : el EscapeGraph cargado desde JSON
    on_locked : callback que recibe node_id y retorna True si logró
                desbloquear el nodo (ejecutando A* internamente)
    """
    algo = ALGORITHMS.get(algorithm.upper())
    if algo is None:
        raise ValueError(
            f"Algoritmo desconocido: {algorithm!r}. "
            f"Opciones: {list(ALGORITHMS.keys())}"
        )
    return algo(graph, on_locked)
