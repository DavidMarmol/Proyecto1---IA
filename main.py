import sys
import os
import argparse
from pathlib import Path

# Asegurar que los módulos del proyecto sean encontrables
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_JSON = PROJECT_ROOT / "data" / "escape_room.json"


def run_cli(algorithm: str, json_path: str):
    """Ejecuta el solver en modo consola (sin interfaz gráfica)."""
    from engine.solver import EscapeSolver

    print(f"\n{'═'*52}")
    print(f"  🔐 Escape Room Solver  [Modo Consola — {algorithm}]")
    print(f"{'═'*52}")

    solver = EscapeSolver(json_path)

    # Callbacks de consola
    solver.set_callbacks(
        on_global_step=lambda line: print(f"  {line}"),
        on_puzzle_start=lambda nid, p: print(f"\n  [PUZZLE] {p.description}"),
        on_puzzle_step=lambda line: print(f"    [A*] {line}"),
        on_puzzle_done=lambda nid, r: print(
            f"\n  [A*] Puzzle resuelto! Costo={r.total_cost:.1f}  "
            f"Camino: {' → '.join(r.path)}\n"
        ),
    )

    metrics = solver.run(algorithm=algorithm)
    print(metrics.summary())

def run_gui(json_path: str):
    """Lanza la interfaz gráfica."""
    from ui.interface import launch

    launch(json_path)


def main():
    parser = argparse.ArgumentParser(
        description="Escape Room Solver — IA Búsqueda Informada y No Informada"
    )
    parser.add_argument(
        "--cli",
        metavar="ALGO",
        choices=["BFS", "DFS", "UCS"],
        help="Ejecutar en modo consola con el algoritmo indicado (BFS/DFS/UCS)",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        default=DEFAULT_JSON,
        help="Ruta al archivo JSON del escape room (default: data/escape_room.json)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"❌ Archivo no encontrado: {args.json}")
        sys.exit(1)

    if args.cli:
        run_cli(args.cli, args.json)
    else:
        run_gui(args.json)


if __name__ == "__main__":
    main()
