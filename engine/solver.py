import time
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field

from graph.escape_graph import EscapeGraph
from search.uninformed import run_uninformed, SearchResult
from search.informed import solve_puzzle, PuzzleResult


@dataclass
class ExecutionMetrics:
    algorithm: str = ""
    global_nodes_expanded: int = 0
    global_depth: int = 0
    global_cost: float = 0.0
    global_path: List[str] = field(default_factory=list)
    global_success: bool = False

    puzzles_solved: List[PuzzleResult] = field(default_factory=list)
    total_puzzle_cost: float = 0.0
    total_puzzle_nodes: int = 0

    execution_time_s: float = 0.0

    def summary(self) -> str:
        lines = [
            "=" * 50,
            f"  RESULTADOS — {self.algorithm}",
            "=" * 50,
            f"  Búsqueda Global",
            f"    Nodos expandidos : {self.global_nodes_expanded}",
            f"    Profundidad      : {self.global_depth}",
            f"    Costo total      : {self.global_cost:.1f}",
            f"    Camino           : {' → '.join(self.global_path)}",
            f"    Éxito            : {'Sí' if self.global_success else 'No'}",
            "",
            f"  Puzzles resueltos  : {len(self.puzzles_solved)}",
            f"    Nodos expandidos : {self.total_puzzle_nodes}",
            f"    Costo acumulado  : {self.total_puzzle_cost:.1f}",
            "",
            f"  Tiempo de ejecución: {self.execution_time_s:.4f}s",
            "=" * 50,
        ]
        return "\n".join(lines)


class EscapeSolver:
    def __init__(self, json_path: str):
        self.graph = EscapeGraph.from_json(json_path)
        self.metrics: Optional[ExecutionMetrics] = None

        self._solved_puzzles: Dict[str, PuzzleResult] = {}

        self._on_global_step: Optional[Callable] = None  # (log_line)
        self._on_puzzle_start: Optional[Callable] = None  # (node_id, puzzle)
        self._on_puzzle_step: Optional[Callable] = None  # (log_line)
        self._on_puzzle_done: Optional[Callable] = None  # (node_id, result)
        self._on_node_change: Optional[Callable] = None  # (node_id, new_state)

    def set_callbacks(
        self,
        on_global_step: Callable = None,
        on_puzzle_start: Callable = None,
        on_puzzle_step: Callable = None,
        on_puzzle_done: Callable = None,
        on_node_change: Callable = None,
    ):
        self._on_global_step = on_global_step
        self._on_puzzle_start = on_puzzle_start
        self._on_puzzle_step = on_puzzle_step
        self._on_puzzle_done = on_puzzle_done
        self._on_node_change = on_node_change

    def run(self, algorithm: str = "BFS") -> ExecutionMetrics:
        self.metrics = ExecutionMetrics(algorithm=algorithm)
        t_start = time.perf_counter()

        global_result: SearchResult = run_uninformed(
            algorithm=algorithm, graph=self.graph, on_locked=self._handle_locked_node
        )

        t_end = time.perf_counter()

        self.metrics.global_nodes_expanded = global_result.nodes_expanded
        self.metrics.global_depth = global_result.depth
        self.metrics.global_cost = global_result.cost
        self.metrics.global_path = global_result.path
        self.metrics.global_success = global_result.success
        self.metrics.execution_time_s = t_end - t_start

        # Notificar logs globales a la UI
        if self._on_global_step:
            for line in global_result.log:
                self._on_global_step(line)

        return self.metrics

    def _handle_locked_node(self, node_id: str) -> bool:
        if node_id in self._solved_puzzles:
            self.graph.unlock_node(node_id)
            if self._on_node_change:
                self._on_node_change(node_id, "available")
            return True

        puzzle = self.graph.get_puzzle(node_id)
        if puzzle is None:
            # Nodo bloqueado sin puzzle definido → no se puede desbloquear
            return False

        # Notificar inicio del puzzle a la UI
        if self._on_puzzle_start:
            self._on_puzzle_start(node_id, puzzle)

        # Ejecutar A*
        puzzle_result = solve_puzzle(puzzle)

        # Notificar logs del puzzle a la UI
        if self._on_puzzle_step:
            for line in puzzle_result.log:
                self._on_puzzle_step(line)

        if puzzle_result.success:
            # Desbloquear en el grafo global
            self.graph.unlock_node(node_id)

            # Registrar métricas del puzzle
            self._solved_puzzles[node_id] = puzzle_result
            self.metrics.puzzles_solved.append(puzzle_result)
            self.metrics.total_puzzle_cost += puzzle_result.total_cost
            self.metrics.total_puzzle_nodes += puzzle_result.nodes_expanded

            # Notificar UI
            if self._on_puzzle_done:
                self._on_puzzle_done(node_id, puzzle_result)
            if self._on_node_change:
                self._on_node_change(node_id, "available")

            return True

        return False

    def reset(self):
        self.graph = EscapeGraph.from_json(
            self.graph._json_path
            if hasattr(self.graph, "_json_path")
            else "data/escape_room.json"
        )
        self.metrics = None
        self._solved_puzzles.clear()

    @property
    def escape_graph(self) -> EscapeGraph:
        return self.graph
