import heapq
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

from graph.escape_graph import PuzzleGraph


@dataclass
class PuzzleResult:
    puzzle_id: str
    path: List[str] = field(default_factory=list)
    nodes_expanded: int = 0
    total_cost: float = 0.0
    log: List[str] = field(default_factory=list)
    success: bool = False


def astar(puzzle: PuzzleGraph) -> PuzzleResult:
    result = PuzzleResult(puzzle_id=puzzle.puzzle_id)
    start, goal = puzzle.start, puzzle.goal

    result.log.append(f"> A* iniciado: '{start}' → meta '{goal}'")
    result.log.append(f"> Descripción: {puzzle.description}")

    counter = 0
    h_start = puzzle.h(start)
    heap: List[Tuple[float, int, float, List[str]]] = [(h_start, counter, 0.0, [start])]

    best_g: Dict[str, float] = {}

    while heap:
        f, _, g, path = heapq.heappop(heap)
        current = path[-1]

        # Si ya encontramos un camino mejor a este nodo, ignorar
        if current in best_g and best_g[current] <= g:
            continue
        best_g[current] = g

        result.nodes_expanded += 1
        h_val = puzzle.h(current)
        result.log.append(
            f"> Expandiendo nodo {{{current}}} "
            f"| g={g:.1f}  h={h_val:.1f}  f={f:.1f}"
        )

        # Meta alcanzada
        if current == goal:
            result.path = path
            result.total_cost = g
            result.success = True
            result.log.append(
                f"— Puzzle Resuelto! Costo total: {g:.1f} | "
                f"Camino: {' → '.join(path)}"
            )
            result.log.append(f"— Desbloqueando nodo en grafo global...")
            return result

        # Expandir vecinos
        for neighbor_id, edge_cost in puzzle.neighbors(current):
            new_g = g + edge_cost
            # Poda: si ya conocemos un camino mejor, ignorar
            if neighbor_id in best_g and best_g[neighbor_id] <= new_g:
                continue
            new_h = puzzle.h(neighbor_id)
            new_f = new_g + new_h
            counter += 1
            heapq.heappush(heap, (new_f, counter, new_g, path + [neighbor_id]))
            result.log.append(
                f"  ↳ Encolando {{{neighbor_id}}} "
                f"| g={new_g:.1f}  h={new_h:.1f}  f={new_f:.1f}"
            )

    result.log.append(
        f"✗ A*: no se encontró solución para el puzzle '{puzzle.puzzle_id}'"
    )
    return result


def solve_puzzle(puzzle: PuzzleGraph) -> PuzzleResult:
    return astar(puzzle)
