import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from graph.escape_graph import EscapeGraph, PuzzleGraph
from graph.node import NodeState
from engine.solver import EscapeSolver, ExecutionMetrics

import matplotlib

matplotlib.use("TkAgg")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

COLORS = {
    "bg": "#1e1e2e",  # fondo principal oscuro
    "panel": "#2a2a3e",  # fondo paneles
    "border": "#44475a",  # bordes
    "text": "#f8f8f2",  # texto principal
    "accent": "#6272a4",  # azul acento
    "green": "#50fa7b",  # nodo resuelto / inicio
    "blue": "#8be9fd",  # nodo disponible
    "gray": "#6272a4",  # nodo bloqueado
    "red": "#ff5555",  # nodo meta / alerta
    "yellow": "#f1fa8c",  # resaltado activo
    "orange": "#ffb86c",  # bordes de camino
    "console_bg": "#0d0d1a",
    "console_fg": "#50fa7b",
}

NODE_COLORS = {
    NodeState.SOLVED: COLORS["green"],
    NodeState.AVAILABLE: COLORS["blue"],
    NodeState.LOCKED: COLORS["gray"],
}


class EscapeRoomApp:

    def __init__(self, root: tk.Tk, json_path: str):
        self.root = root
        self.json_path = json_path
        self.solver: EscapeSolver = None
        self.current_algorithm = tk.StringVar(value="BFS")
        self.active_puzzle_graph: PuzzleGraph = None
        self.solution_path: list = []
        self.puzzle_path: list = []
        self._running = False

        self._setup_window()
        self._build_ui()
        self._load_graph()

    # ------------------------------------------------------------------
    # Configuración de la ventana
    # ------------------------------------------------------------------

    def _setup_window(self):
        self.root.title("Escape Room Solver")
        self.root.configure(bg=COLORS["bg"])
        self.root.geometry("1280x780")
        self.root.minsize(1100, 700)

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ── Barra superior ──────────────────────────────────────────
        top_bar = tk.Frame(self.root, bg=COLORS["panel"], height=48)
        top_bar.pack(fill=tk.X, padx=0, pady=0)
        top_bar.pack_propagate(False)

        tk.Label(
            top_bar,
            text="🔐 Escape Room Solver",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Consolas", 14, "bold"),
        ).pack(side=tk.LEFT, padx=16)

        # Selector de algoritmo
        algo_frame = tk.Frame(top_bar, bg=COLORS["panel"])
        algo_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(
            algo_frame,
            text="Algoritmo Global:",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Consolas", 10),
        ).pack(side=tk.LEFT)
        for algo in ["BFS", "DFS", "UCS"]:
            rb = tk.Radiobutton(
                algo_frame,
                text=algo,
                variable=self.current_algorithm,
                value=algo,
                bg=COLORS["panel"],
                fg=COLORS["text"],
                selectcolor=COLORS["bg"],
                activebackground=COLORS["panel"],
                activeforeground=COLORS["yellow"],
                font=("Consolas", 11, "bold"),
                indicatoron=0,
                width=5,
                relief=tk.FLAT,
                cursor="hand2",
            )
            rb.pack(side=tk.LEFT, padx=3)

        # Botón cargar JSON
        tk.Button(
            top_bar,
            text="📂 Cargar JSON",
            bg=COLORS["accent"],
            fg=COLORS["bg"],
            font=("Consolas", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._load_json_dialog,
        ).pack(side=tk.RIGHT, padx=8, pady=8)

        # Botón ejecutar
        self.btn_run = tk.Button(
            top_bar,
            text="▶  Ejecutar",
            bg=COLORS["green"],
            fg=COLORS["bg"],
            font=("Consolas", 11, "bold"),
            relief=tk.FLAT,
            padx=12,
            cursor="hand2",
            command=self._run_solver,
        )
        self.btn_run.pack(side=tk.RIGHT, padx=4, pady=8)

        # Botón reset
        tk.Button(
            top_bar,
            text="↺ Reset",
            bg=COLORS["orange"],
            fg=COLORS["bg"],
            font=("Consolas", 10, "bold"),
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._reset,
        ).pack(side=tk.RIGHT, padx=4, pady=8)

        # ── Panel de gráficas (mitad superior) ──────────────────────
        graphs_frame = tk.Frame(self.root, bg=COLORS["bg"])
        graphs_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 2))

        # Panel izquierdo: Grafo global
        left_panel = tk.LabelFrame(
            graphs_frame,
            text=" Global Graph — Uninformed Search ",
            bg=COLORS["panel"],
            fg=COLORS["blue"],
            font=("Consolas", 10, "bold"),
            bd=1,
            relief=tk.FLAT,
            labelanchor="nw",
        )
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        self.fig_global, self.ax_global = plt.subplots(figsize=(6, 4))
        self.fig_global.patch.set_facecolor(COLORS["panel"])
        self.ax_global.set_facecolor(COLORS["panel"])
        self.canvas_global = FigureCanvasTkAgg(self.fig_global, master=left_panel)
        self.canvas_global.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Leyenda global
        legend_frame = tk.Frame(left_panel, bg=COLORS["panel"])
        legend_frame.pack(fill=tk.X, padx=4, pady=2)
        for color, label in [
            (COLORS["green"], "Resuelto (inicio)"),
            (COLORS["blue"], "Disponible"),
            (COLORS["gray"], "Bloqueado"),
            (COLORS["red"], "Meta"),
        ]:
            dot = tk.Label(
                legend_frame,
                text="●",
                fg=color,
                bg=COLORS["panel"],
                font=("Consolas", 12),
            )
            dot.pack(side=tk.LEFT, padx=(6, 1))
            tk.Label(
                legend_frame,
                text=label,
                fg=COLORS["text"],
                bg=COLORS["panel"],
                font=("Consolas", 9),
            ).pack(side=tk.LEFT, padx=(0, 8))

        # Panel derecho: Puzzle solver
        right_panel = tk.LabelFrame(
            graphs_frame,
            text=" Puzzle Solver — Informed Search (A*) ",
            bg=COLORS["panel"],
            fg=COLORS["yellow"],
            font=("Consolas", 10, "bold"),
            bd=1,
            relief=tk.FLAT,
            labelanchor="nw",
        )
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        self.fig_puzzle, self.ax_puzzle = plt.subplots(figsize=(6, 4))
        self.fig_puzzle.patch.set_facecolor(COLORS["panel"])
        self.ax_puzzle.set_facecolor(COLORS["panel"])
        self.canvas_puzzle = FigureCanvasTkAgg(self.fig_puzzle, master=right_panel)
        self.canvas_puzzle.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.lbl_puzzle_title = tk.Label(
            right_panel,
            text="Sin puzzle activo",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Consolas", 9, "italic"),
        )
        self.lbl_puzzle_title.pack(pady=2)

        # ── Panel inferior: consola + estadísticas ───────────────────
        bottom_frame = tk.Frame(self.root, bg=COLORS["bg"])
        bottom_frame.pack(fill=tk.X, padx=8, pady=(2, 8))

        # Consola izquierda
        console_panel = tk.LabelFrame(
            bottom_frame,
            text=" Consola de Ejecución ",
            bg=COLORS["panel"],
            fg=COLORS["green"],
            font=("Consolas", 9, "bold"),
            bd=1,
            relief=tk.FLAT,
        )
        console_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        self.console = tk.Text(
            console_panel,
            height=8,
            bg=COLORS["console_bg"],
            fg=COLORS["console_fg"],
            font=("Consolas", 9),
            state=tk.DISABLED,
            wrap=tk.WORD,
            bd=0,
            insertbackground=COLORS["green"],
        )
        console_scroll = ttk.Scrollbar(console_panel, command=self.console.yview)
        self.console.configure(yscrollcommand=console_scroll.set)
        console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Panel de estadísticas
        stats_panel = tk.LabelFrame(
            bottom_frame,
            text=" Statistics ",
            bg=COLORS["panel"],
            fg=COLORS["yellow"],
            font=("Consolas", 9, "bold"),
            bd=1,
            relief=tk.FLAT,
            width=320,
        )
        stats_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 0))
        stats_panel.pack_propagate(False)

        self.stats_vars = {}
        stats_layout = [
            ("Global Search", None),
            ("Nodes Expanded", "global_nodes"),
            ("Depth", "global_depth"),
            ("Cost", "global_cost"),
            ("Path", "global_path"),
            ("", None),
            ("Local Puzzle", None),
            ("Nodes Expanded", "puzzle_nodes"),
            ("Total Cost", "puzzle_cost"),
            ("", None),
            ("Execution Time", "exec_time"),
        ]
        for label, key in stats_layout:
            row = tk.Frame(stats_panel, bg=COLORS["panel"])
            row.pack(fill=tk.X, padx=8, pady=1)
            if key is None:
                tk.Label(
                    row,
                    text=label,
                    bg=COLORS["panel"],
                    fg=COLORS["yellow"] if label else COLORS["panel"],
                    font=("Consolas", 9, "bold"),
                ).pack(side=tk.LEFT)
            else:
                tk.Label(
                    row,
                    text=f"  {label}:",
                    bg=COLORS["panel"],
                    fg=COLORS["text"],
                    font=("Consolas", 9),
                ).pack(side=tk.LEFT)
                var = tk.StringVar(value="—")
                self.stats_vars[key] = var
                tk.Label(
                    row,
                    textvariable=var,
                    bg=COLORS["panel"],
                    fg=COLORS["blue"],
                    font=("Consolas", 9, "bold"),
                ).pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Carga del grafo
    # ------------------------------------------------------------------

    def _load_graph(self):
        try:
            self.solver = EscapeSolver(self.json_path)
            self.solver.set_callbacks(
                on_global_step=self._cb_global_log,
                on_puzzle_start=self._cb_puzzle_start,
                on_puzzle_step=self._cb_puzzle_log,
                on_puzzle_done=self._cb_puzzle_done,
                on_node_change=self._cb_node_change,
            )
            self._draw_global_graph()
            self._log(f"✓ Grafo cargado desde: {os.path.basename(self.json_path)}")
            self._log(f"  {self.solver.escape_graph.summary()}")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def _load_json_dialog(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.json_path = path
            self._reset()

    # ------------------------------------------------------------------
    # Dibujo del grafo global
    # ------------------------------------------------------------------

    def _draw_global_graph(self, highlight_path=None):
        graph = self.solver.escape_graph
        self.ax_global.clear()
        self.ax_global.set_facecolor(COLORS["panel"])

        G = nx.DiGraph()
        for nid in graph.nodes:
            G.add_node(nid)
        for nid, neighbors in graph.edges.items():
            for nb in neighbors:
                G.add_edge(nid, nb)

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            pos = nx.spring_layout(G, seed=42, k=2.0)

        # Colores de nodos
        node_colors = []
        for nid in G.nodes():
            node = graph.get_node(nid)
            if nid == graph.goal:
                node_colors.append(COLORS["red"])
            elif node:
                node_colors.append(NODE_COLORS.get(node.state, COLORS["blue"]))
            else:
                node_colors.append(COLORS["blue"])

        # Aristas del camino solución (resaltadas)
        path_edges = set()
        if highlight_path and len(highlight_path) > 1:
            for i in range(len(highlight_path) - 1):
                path_edges.add((highlight_path[i], highlight_path[i + 1]))

        edge_colors = [
            COLORS["orange"] if e in path_edges else COLORS["border"] for e in G.edges()
        ]
        edge_widths = [3.0 if e in path_edges else 1.0 for e in G.edges()]

        nx.draw_networkx(
            G,
            pos=pos,
            ax=self.ax_global,
            node_color=node_colors,
            node_size=900,
            font_color=COLORS["bg"],
            font_size=10,
            font_weight="bold",
            edge_color=edge_colors,
            width=edge_widths,
            arrows=True,
            arrowsize=18,
            connectionstyle="arc3,rad=0.1",
        )

        self.ax_global.axis("off")
        self.fig_global.tight_layout(pad=0.5)
        self.canvas_global.draw()

    # ------------------------------------------------------------------
    # Dibujo del grafo de puzzle
    # ------------------------------------------------------------------

    def _draw_puzzle_graph(self, puzzle: PuzzleGraph, highlight_path=None):
        self.ax_puzzle.clear()
        self.ax_puzzle.set_facecolor(COLORS["panel"])

        G = nx.DiGraph()
        for nid in puzzle.nodes:
            G.add_node(nid)
        for nid, neighbors in puzzle.edges.items():
            for nb, cost in neighbors:
                G.add_edge(nid, nb, weight=cost)

        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except Exception:
            pos = nx.spring_layout(G, seed=7, k=2.5)

        # Colores
        node_colors = []
        for nid in G.nodes():
            if nid == puzzle.goal:
                node_colors.append(COLORS["red"])
            elif nid == puzzle.start:
                node_colors.append(COLORS["green"])
            else:
                node_colors.append(COLORS["blue"])

        # Camino resaltado
        path_edges = set()
        if highlight_path and len(highlight_path) > 1:
            for i in range(len(highlight_path) - 1):
                path_edges.add((highlight_path[i], highlight_path[i + 1]))

        edge_colors = [
            COLORS["orange"] if e in path_edges else COLORS["border"] for e in G.edges()
        ]
        edge_widths = [3.0 if e in path_edges else 1.0 for e in G.edges()]

        # Etiquetas de costos en aristas
        edge_labels = {(u, v): f"{d['weight']:.0f}" for u, v, d in G.edges(data=True)}

        nx.draw_networkx(
            G,
            pos=pos,
            ax=self.ax_puzzle,
            node_color=node_colors,
            node_size=800,
            font_color=COLORS["bg"],
            font_size=10,
            font_weight="bold",
            edge_color=edge_colors,
            width=edge_widths,
            arrows=True,
            arrowsize=16,
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_edge_labels(
            G,
            pos=pos,
            edge_labels=edge_labels,
            ax=self.ax_puzzle,
            font_size=8,
            font_color=COLORS["yellow"],
            bbox=dict(
                boxstyle="round,pad=0.2", fc=COLORS["panel"], ec="none", alpha=0.7
            ),
        )

        self.ax_puzzle.axis("off")
        self.fig_puzzle.tight_layout(pad=0.5)
        self.canvas_puzzle.draw()

    # ------------------------------------------------------------------
    # Ejecución del solver (en hilo separado para no bloquear la UI)
    # ------------------------------------------------------------------

    def _run_solver(self):
        if self._running:
            return
        self._running = True
        self.btn_run.configure(state=tk.DISABLED, text="⏳ Ejecutando...")
        self._reset_stats()
        self.console.configure(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.configure(state=tk.DISABLED)

        # Recargar grafo fresco
        self._load_graph()

        algo = self.current_algorithm.get()
        self._log(f"\n{'═'*48}")
        self._log(f"  Iniciando {algo} — Escape Room Solver")
        self._log(f"{'═'*48}")

        def worker():
            t0 = time.perf_counter()
            metrics = self.solver.run(algorithm=algo)
            t1 = time.perf_counter()

            # Actualizar UI en el hilo principal
            self.root.after(0, self._on_solver_done, metrics)

        threading.Thread(target=worker, daemon=True).start()

    def _on_solver_done(self, metrics: ExecutionMetrics):
        self._running = False
        self.btn_run.configure(state=tk.NORMAL, text="▶  Ejecutar")

        # Redibujar grafo con camino solución
        self.solution_path = metrics.global_path
        self._draw_global_graph(highlight_path=self.solution_path)

        # Actualizar estadísticas
        self.stats_vars["global_nodes"].set(str(metrics.global_nodes_expanded))
        self.stats_vars["global_depth"].set(str(metrics.global_depth))
        self.stats_vars["global_cost"].set(f"{metrics.global_cost:.1f}")
        self.stats_vars["global_path"].set(
            " → ".join(metrics.global_path) if metrics.global_path else "—"
        )
        self.stats_vars["puzzle_nodes"].set(str(metrics.total_puzzle_nodes))
        self.stats_vars["puzzle_cost"].set(f"{metrics.total_puzzle_cost:.1f}")
        self.stats_vars["exec_time"].set(f"{metrics.execution_time_s:.4f}s")

        if metrics.global_success:
            self._log(f"\n✓ ¡ESCAPE ROOM COMPLETADO!")
            self._log(f"  Camino: {' → '.join(metrics.global_path)}")
        else:
            self._log("\n✗ No se encontró solución.")

    # ------------------------------------------------------------------
    # Callbacks del solver → UI
    # ------------------------------------------------------------------

    def _cb_global_log(self, line: str):
        self.root.after(0, self._log, line)

    def _cb_puzzle_start(self, node_id: str, puzzle: PuzzleGraph):
        self.active_puzzle_graph = puzzle
        self.root.after(0, self._draw_puzzle_graph, puzzle)
        self.root.after(
            0,
            self.lbl_puzzle_title.configure,
            {"text": f"Puzzle: {puzzle.description}"},
        )

    def _cb_puzzle_log(self, line: str):
        self.root.after(0, self._log_puzzle, line)

    def _cb_puzzle_done(self, node_id: str, result):
        self.puzzle_path = result.path
        if self.active_puzzle_graph:
            self.root.after(
                0, self._draw_puzzle_graph, self.active_puzzle_graph, result.path
            )

    def _cb_node_change(self, node_id: str, new_state: str):
        self.root.after(0, self._draw_global_graph, self.solution_path)

    # ------------------------------------------------------------------
    # Consola
    # ------------------------------------------------------------------

    def _log(self, msg: str):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, msg + "\n")
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)

    def _log_puzzle(self, msg: str):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, "  [A*] " + msg + "\n", "puzzle")
        self.console.tag_config("puzzle", foreground=COLORS["yellow"])
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset(self):
        self.solution_path = []
        self.puzzle_path = []
        self._reset_stats()
        self.console.configure(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.configure(state=tk.DISABLED)
        self.ax_puzzle.clear()
        self.ax_puzzle.set_facecolor(COLORS["panel"])
        self.canvas_puzzle.draw()
        self.lbl_puzzle_title.configure(text="Sin puzzle activo")
        self._load_graph()

    def _reset_stats(self):
        for var in self.stats_vars.values():
            var.set("—")


# ======================================================================
# Punto de entrada de la UI
# ======================================================================


def launch(json_path: str = None):
    if json_path is None:
        # Ruta relativa al directorio del proyecto
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base, "data", "escape_room.json")

    root = tk.Tk()
    app = EscapeRoomApp(root, json_path)
    root.mainloop()
