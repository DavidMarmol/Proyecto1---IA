from collections import deque
import heapq
from typing import Callable, Dict, List, Tuple
from dataclasses import dataclass, field

from graph.escape_graph import EscapeGraph


@dataclass
class SearchResult:
    path: List[str] = field(default_factory=list)
    nodes_expanded: int = 0
    depth: int = 0
    cost: float = 0.0
    log: List[str] = field(default_factory=list)
    success: bool = False


UnlockCallback = Callable[[str], bool]


def bfs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    result = SearchResult()
    start, goal = graph.start, graph.goal

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


def dfs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    result = SearchResult()
    start, goal = graph.start, graph.goal

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


def ucs(graph: EscapeGraph, on_locked: UnlockCallback) -> SearchResult:
    result = SearchResult()
    start, goal = graph.start, graph.goal

    counter = 0
    heap: List[Tuple[float, int, List[str]]] = [(0.0, counter, [start])]
    visited: Dict[str, float] = {}

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


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
}


def run_uninformed(
    algorithm: str, graph: EscapeGraph, on_locked: UnlockCallback
) -> SearchResult:

    algo = ALGORITHMS.get(algorithm.upper())
    if algo is None:
        raise ValueError(
            f"Algoritmo desconocido: {algorithm!r}. "
            f"Opciones: {list(ALGORITHMS.keys())}"
        )
    return algo(graph, on_locked)
