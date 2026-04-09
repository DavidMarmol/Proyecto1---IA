import json
from typing import Dict, List, Optional, Tuple
from graph.node import Node, NodeState


class PuzzleGraph:
    def __init__(self, puzzle_id: str, data: dict):
        self.puzzle_id = puzzle_id
        self.description = data.get("description", "Puzzle sin descripción")
        self.start = data["start"]
        self.goal = data["goal"]

        # Nodos
        self.nodes: Dict[str, Node] = {}
        for n in data["nodes"]:
            self.nodes[n["id"]] = Node(n["id"], n.get("label", n["id"]))

        # Aristas con peso
        self.edges: Dict[str, List[Tuple[str, float]]] = {nid: [] for nid in self.nodes}
        for e in data["edges"]:
            cost = float(e.get("cost", 1))
            self.edges[e["from"]].append((e["to"], cost))

        # Heurísticas h(n)
        self.heuristics: Dict[str, float] = data.get("heuristics", {})
        # Asegurar que todos los nodos tengan heurística (0 como fallback)
        for nid in self.nodes:
            if nid not in self.heuristics:
                self.heuristics[nid] = 0.0

    def h(self, node_id: str) -> float:
        return self.heuristics.get(node_id, 0.0)

    def neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        return self.edges.get(node_id, [])

    def __repr__(self) -> str:
        return f"PuzzleGraph({self.puzzle_id!r}, {self.start}→{self.goal})"


class EscapeGraph:
    def __init__(self):
        self.start: str = ""
        self.goal: str = ""
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[str]] = {}
        self.puzzles: Dict[str, PuzzleGraph] = {}

    @classmethod
    def from_json(cls, filepath: str) -> "EscapeGraph":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph = cls()
        gg = data["global_graph"]

        graph.start = gg["start"]
        graph.goal = gg["goal"]

        # Construir nodos
        for n in gg["nodes"]:
            locked = n.get("locked", False)
            puzzle_id = n.get("puzzle", None)
            node = Node(
                node_id=n["id"],
                label=n.get("label", n["id"]),
                locked=locked,
                puzzle_id=puzzle_id,
            )
            graph.nodes[n["id"]] = node
            graph.edges[n["id"]] = []

        # Construir aristas
        for e in gg["edges"]:
            graph.edges[e["from"]].append(e["to"])

        # Construir puzzles
        for pid, pdata in data.get("puzzles", {}).items():
            graph.puzzles[pid] = PuzzleGraph(pid, pdata)

        return graph

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def neighbors(self, node_id: str) -> List[str]:
        return self.edges.get(node_id, [])

    def get_puzzle(self, node_id: str) -> Optional[PuzzleGraph]:
        node = self.get_node(node_id)
        if node and node.puzzle_id:
            return self.puzzles.get(node.puzzle_id)
        return None

    def unlock_node(self, node_id: str):
        node = self.get_node(node_id)
        if node:
            node.unlock()

    def summary(self) -> str:
        locked = [nid for nid, n in self.nodes.items() if n.is_locked]
        return (
            f"EscapeGraph | Nodos: {len(self.nodes)} | "
            f"Aristas: {sum(len(v) for v in self.edges.values())} | "
            f"Inicio: {self.start} | Meta: {self.goal} | "
            f"Bloqueados: {locked}"
        )

    def __repr__(self) -> str:
        return self.summary()
