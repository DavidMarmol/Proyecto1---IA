#libreria pip install networkx matplotlib

"""
Nota: Una vez terminado esta nota se debe borrar

    - Interfaz lista con los dos paneles, estadísticas y controles
    - Los grafos están vacíos esperando la implementación
    - Los logs todavía no funcionan (se conectan cuando estén los algoritmos)
    - TODO es un comentario que indica que pasos seguir.

    - cuando las funciones exitan se deben conectar a los botones de la interaz grafica
    def _on_run(self):
        # TODO: conectar con el algoritmo principal
        pass

    def _on_step(self):
        # TODO: avanzar un paso del algoritmo
        pass

    def _on_reset(self):
        # TODO: espacio para aplicar una funcion cuando los algoritmos existan
        self._reset_stats()
        self._clear_logs()
        draw_global_graph(self.ax_global, self.global_graph, self.global_states)
        draw_puzzle_graph(self.ax_puzzle, self.puzzle_graph, self.puzzle_states)
        self.canvas_mpl.draw()


"""

import platform
import tkinter as tk
from tkinter import ttk
import networkx as nx
import matplotlib.pyplot as plt # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # type: ignore


# ─────────────────────────────────────────────
#  COLORES
# ─────────────────────────────────────────────

BG_DARK    = "#1a1a1a"
BG_PANEL   = "#222222"
TEXT       = "#e0e0e0"
TEXT_MUTED = "#888888"

NODE_COLORS = {
    "start":     "#3B6D11",
    "available": "#185FA5",
    "locked":    "#5F5E5A",
    "active":    "#854F0B",
    "solved":    "#3B6D11",
    "goal":      "#A32D2D",
}


# ─────────────────────────────────────────────
#  FUNCIONES DE DIBUJO  
# ─────────────────────────────────────────────
# la funcion  draw_global_graph debe dibujar el grafo global, 
# y la funcion draw_puzzle_graph debe dibujar el subgrafo del puzzle (A*). 
# Ambas funciones reciben un eje de matplotlib (ax) donde se dibujará el grafo, 
# la estructura del grafo y el estado actual de cada nodo. El estado de los nodos 
# determina su color y forma al dibujarlos. 
# Estas funciones deben usar networkx para construir el grafo y matplotlib para dibujarlo, 
# aplicando un estilo oscuro al fondo del eje.

    #  ax es el eje de matplotlib donde se dibuja el grafo global.
    #  graph es un diccionario que contiene la estructura del grafo,
    #  con nodos y aristas. node_states es un diccionario que indica el estado actual de cada nodo,
    #  lo que afecta su color y forma al dibujarlos.

def draw_global_graph(ax, graph: dict, node_states: dict):

    """
    Dibuja el grafo global sobre el eje (ax) de matplotlib.

    Parámetros
    ----------
    ax : matplotlib.axes.Axes
        Eje donde se dibuja. Hacer ax.clear() al inicio.

    graph : dict  — estructura del grafo
        {
            "nodes": { "A": {"x": 60, "y": 120}, ... },
            "edges": [ {"from": "A", "to": "B"}, ... ]
        }

    node_states : dict — estado actual de cada nodo
        Valores posibles: "start", "available", "locked",
                          "active", "solved", "goal"
        Ejemplo: {"A": "solved", "B": "active", "C": "locked"}

    TODO
    
    ----
    1. ax.clear()
    2. Construir un nx.DiGraph() con los nodos y aristas del grafo
    3. Definir pos = {nodo: (x, -y)} usando las coordenadas de graph["nodes"]
    4. Armar la lista de colores: NODE_COLORS[node_states.get(n, "available")]
    5. Nodos "locked" deben dibujarse con node_shape="s" (cuadrado)
    6. Llamar nx.draw() con los parámetros de estilo
    7. Aplicar fondo oscuro al eje
    """
    ax.clear()
    ax.set_facecolor(BG_PANEL)
    ax.set_title("Global Graph", color=TEXT, fontsize=9, pad=6)
    ax.axis("off")
    # TODO:  


def draw_puzzle_graph(ax, puzzle_graph: dict, node_states: dict):
    """
    Dibuja el subgrafo del puzzle (A*) sobre el eje (ax) de matplotlib.

    Parámetros
    ----------
    ax : matplotlib.axes.Axes
        Eje donde se dibuja. Hacer ax.clear() al inicio.

    puzzle_graph : dict  — estructura del subgrafo
        {
            "nodes": { "S": {"x": 50, "y": 80}, ... },
            "edges": [ {"from": "S", "to": "N1", "cost": 3}, ... ]
        }

    node_states : dict — igual que en draw_global_graph

    TODO
    ----
    1. ax.clear()
    2. Si puzzle_graph está vacío -> solo poner título y retornar
    3. Construir nx.DiGraph(), agregar nodos y aristas
    4. Definir pos con las coordenadas del puzzle_graph
    5. Dibujar nodos con nx.draw_networkx_nodes/edges/labels
    6. Dibujar etiquetas de costo en las aristas con nx.draw_networkx_edge_labels
    7. Aplicar fondo oscuro al eje
    """
    ax.clear()
    ax.set_facecolor(BG_PANEL)
    ax.set_title("Puzzle Solver", color=TEXT, fontsize=9, pad=6)
    ax.axis("off")
    # TODO: implementar


# ─────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────
#esta funcion es la clase principal de la interfaz gráfica. Se encarga de construir toda la ventana,
# organizar los paneles, manejar la carga de grafos y actualizar la visualización.
class EscapeRoomGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Escape Room Solver")
        self.root.configure(bg=BG_DARK)
        #self.root.geometry("1100x680")
        self.root.minsize(900, 580)

        #indentificar el sistema operativo para aplicar la configuración de pantalla completa.
        so = platform.system()
        if so == "Windows":
            self.root.state("zoomed")
        elif so == "Linux":
            self.root.attributes("-zoomed", True)
        elif so == "Darwin":  # Mac
            self.root.attributes("-fullscreen", True)
        else:
            self.root.geometry("1100x720")  # fallback
            
        # Aqui se conectan las funciones de dibujo con la estructura de datos que representan los grafos y sus estados.
        #en self.global_graph se emplea la funcion load_global_graph para cargar la estructura del grafo global,
        #en self.puzzle_graph se emplea la funcion load_puzzle_graph para cargar la estructura del subgrafo del puzzle.
        #self.global_states y self.puzzle_states almacenan el estado actual de cada nodo en ambos grafos, 
        #lo que permite actualizar la visualización según el progreso de los algoritmos.
        self.global_graph  = {}
        self.puzzle_graph  = {}
        self.global_states = {}
        self.puzzle_states = {}

        self._build_ui()

    # ── Construcción de la UI ──────────────────────────

    def _build_ui(self):
        self._build_title_bar()
        self._build_graph_panels()
        self._build_console_row()
        self._build_controls()

    def _build_title_bar(self):
        bar = tk.Frame(self.root, bg="#2a2a2a", height=36)
        bar.pack(fill="x", padx=10, pady=(10, 0))
        bar.pack_propagate(False)

        dots = tk.Frame(bar, bg="#2a2a2a")
        dots.pack(side="left", padx=10, pady=8)
        for color in ("#E24B4A", "#EF9F27", "#639922"):
            tk.Label(dots, bg=color, width=2).pack(side="left", padx=2)

        tk.Label(bar, text="Escape Room Solver", bg="#2a2a2a",
                 fg=TEXT, font=("Courier New", 12, "bold")).pack(side="left", padx=16)

    def _build_graph_panels(self):
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=10, pady=8)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

   
        self.fig, (self.ax_global, self.ax_puzzle) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.patch.set_facecolor(BG_DARK)
        self.fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.02, wspace=0.08)

  
        draw_global_graph(self.ax_global, {}, {})
        draw_puzzle_graph(self.ax_puzzle, {}, {})

        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas_mpl.draw()
        self.canvas_mpl.get_tk_widget().grid(row=0, column=0, columnspan=2, sticky="nsew")

        self._build_legend(frame)
        self._build_stats(frame)
    # la funcion build_legend genera un grupo de etiquetas debajo de los gráficos para explicar el significado de los colores de los nodos en la interfaz.
    def _build_legend(self, parent):
        leg = tk.Frame(parent, bg=BG_DARK)
        leg.grid(row=1, column=0, sticky="w", padx=4, pady=(0, 4))
        items = [
            ("Start / Solved", NODE_COLORS["solved"]),
            ("Available",      NODE_COLORS["available"]),
            ("Locked",         NODE_COLORS["locked"]),
            ("Goal",           NODE_COLORS["goal"]),
        ]
        for label, color in items:
            tk.Label(leg, bg=color, width=2, height=1).pack(side="left", padx=(0, 3))
            tk.Label(leg, text=label, bg=BG_DARK, fg=TEXT_MUTED,
                     font=("Courier New", 8)).pack(side="left", padx=(0, 12))
    #build stats muestra un panel de estadísticas a la derecha de los gráficos, con etiquetas para mostrar información sobre el número de nodos expandidos, la profundidad alcanzada y el costo total del puzzle. Estas etiquetas se actualizan dinámicamente a medida que se ejecutan los algoritmos.
    def _build_stats(self, parent):
        stats = tk.Frame(parent, bg=BG_DARK)
        stats.grid(row=1, column=1, sticky="e", padx=8, pady=(0, 4))

        def stat_pair(row, col, label):
            tk.Label(stats, text=label, bg=BG_DARK, fg=TEXT_MUTED,
                     font=("Courier New", 8)).grid(row=row, column=col, sticky="w", padx=(0, 4))
            val = tk.Label(stats, text="—", bg=BG_DARK, fg=TEXT,
                           font=("Courier New", 8, "bold"))
            val.grid(row=row, column=col + 1, sticky="w", padx=(0, 16))
            return val

        tk.Label(stats, text="Global Search", bg=BG_DARK, fg=TEXT,
                 font=("Courier New", 8, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        tk.Label(stats, text="Local Puzzle", bg=BG_DARK, fg=TEXT,
                 font=("Courier New", 8, "bold")).grid(row=0, column=2, columnspan=2, sticky="w")

        self.lbl_g_expanded = stat_pair(1, 0, "Nodes Expanded:")
        self.lbl_g_depth    = stat_pair(2, 0, "Depth:")
        self.lbl_p_expanded = stat_pair(1, 2, "Nodes Expanded:")
        self.lbl_p_cost     = stat_pair(2, 2, "Total Cost:")

        self.lbl_exec_time = tk.Label(stats, text="", bg=BG_DARK, fg=TEXT_MUTED,
                                      font=("Courier New", 8))
        self.lbl_exec_time.grid(row=3, column=0, columnspan=4, sticky="e", pady=(2, 0))

    #build console row y make console row generan los paneles de log debajo de los gráficos, 
    # donde se mostrarán mensajes relacionados con la búsqueda global y la resolución del puzzle. 
    # Cada panel tiene un título y un área de texto donde se pueden escribir mensajes con diferentes etiquetas de formato (expand, locked, solved, info) 
    # para resaltar información relevante durante la ejecución de los algoritmos.

    def _build_console_row(self):
        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill="x", padx=10, pady=(0, 6))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        self.log_global = self._make_console(frame, "Global Search Log", 0)
        self.log_puzzle = self._make_console(frame, "Puzzle Solver Log",  1)

    def _make_console(self, parent, title: str, col: int) -> tk.Text:
        box = tk.Frame(parent, bg="#2a2a2a")
        box.grid(row=0, column=col, sticky="ew",
                 padx=(0, 5) if col == 0 else (5, 0))

        tk.Label(box, text=title, bg="#2a2a2a", fg=TEXT_MUTED,
                 font=("Courier New", 8)).pack(anchor="w", padx=8, pady=(4, 2))

        txt = tk.Text(box, bg="#2a2a2a", fg=TEXT, font=("Courier New", 8),
                      height=5, relief="flat", state="disabled",
                      insertbackground=TEXT)
        txt.pack(fill="x", padx=6, pady=(0, 6))

    
        txt.tag_configure("expand", foreground="#97C459")
        txt.tag_configure("locked", foreground="#EF9F27")
        txt.tag_configure("solved", foreground="#85B7EB")
        txt.tag_configure("info",   foreground=TEXT_MUTED)
        return txt

    def _build_controls(self):
        bar = tk.Frame(self.root, bg="#2a2a2a")
        bar.pack(fill="x", padx=10, pady=(0, 10))

        btn_cfg = dict(bg=BG_PANEL, fg=TEXT, font=("Courier New", 10),
                       relief="flat", padx=14, pady=4, cursor="hand2",
                       activebackground="#3a3a3a", activeforeground=TEXT)

        self.btn_run = tk.Button(bar, text="▶  Run",  command=self._on_run,   **btn_cfg)
        self.btn_run.pack(side="left", padx=(10, 4), pady=6)

        tk.Button(bar, text="Step",  command=self._on_step,  **btn_cfg).pack(side="left", padx=4, pady=6)
        tk.Button(bar, text="Reset", command=self._on_reset, **btn_cfg).pack(side="left", padx=4, pady=6)

        tk.Label(bar, text="Speed:", bg="#2a2a2a", fg=TEXT_MUTED,
                 font=("Courier New", 9)).pack(side="right", padx=(0, 6))

        self.speed_var = tk.StringVar(value="Normal")
        ttk.Combobox(bar, textvariable=self.speed_var,
                     values=["Slow", "Normal", "Fast"],
                     width=8, state="readonly").pack(side="right", padx=(0, 10))

    # ── Botones (se conectan cuando estén los algoritmos) ──

    def _on_run(self):
        # TODO: conectar con el algoritmo principal
        pass

    def _on_step(self):
        # TODO: avanzar un paso del algoritmo
        pass

    def _on_reset(self):
        # TODO: espacio para aplicar una funcion cuando los algoritmos existan
        self._reset_stats()
        self._clear_logs()
        draw_global_graph(self.ax_global, self.global_graph, self.global_states)
        draw_puzzle_graph(self.ax_puzzle, self.puzzle_graph, self.puzzle_states)
        self.canvas_mpl.draw()

    #############################################################################
    #estas funciones conectan la interfaz grafica con las funciones de dibujo.
    #Permiten cargar la estructura de los grafos global y del puzzle, actualizar su estado y redibujar la visualización.
         
    def load_global_graph(self, graph: dict, initial_states: dict):
        #Carga el grafo global y redibuja.
        self.global_graph  = graph
        self.global_states = initial_states.copy()
        draw_global_graph(self.ax_global, graph, initial_states)
        self.canvas_mpl.draw()

    def load_puzzle_graph(self, puzzle_graph: dict, initial_states: dict):
        #Carga el subgrafo del puzzle y redibuja.
        self.puzzle_graph  = puzzle_graph
        self.puzzle_states = initial_states.copy()
        draw_puzzle_graph(self.ax_puzzle, puzzle_graph, initial_states)
        self.canvas_mpl.draw()

    def refresh(self):
        # Redibuja ambos grafos con el estado actual. Llamar tras modificar node_states.
        draw_global_graph(self.ax_global, self.global_graph, self.global_states)
        draw_puzzle_graph(self.ax_puzzle, self.puzzle_graph, self.puzzle_states)
        self.canvas_mpl.draw()

    def update_stats(self, g_expanded=None, g_depth=None,
                     p_expanded=None, p_cost=None, exec_time=None):
        #Actualiza las etiquetas de estadísticas.
        if g_expanded is not None: self.lbl_g_expanded.config(text=str(g_expanded))
        if g_depth    is not None: self.lbl_g_depth.config(text=str(g_depth))
        if p_expanded is not None: self.lbl_p_expanded.config(text=str(p_expanded))
        if p_cost     is not None: self.lbl_p_cost.config(text=str(p_cost))
        if exec_time  is not None: self.lbl_exec_time.config(text=f"Execution time: {exec_time:.2f}s")

    def log(self, panel: str, message: str, tag: str = "info"):
       
        #Escribe en uno de los logs.
        #panel : "global" o "puzzle"
        #tag   : "expand", "locked", "solved", "info"

        widget = self.log_global if panel == "global" else self.log_puzzle
        widget.config(state="normal")
        widget.insert("end", message + "\n", tag)
        widget.see("end")
        widget.config(state="disabled")

    # ── Helpers internos ───────────────────────────────

    def _reset_stats(self):
        for lbl in (self.lbl_g_expanded, self.lbl_g_depth,
                    self.lbl_p_expanded, self.lbl_p_cost):
            lbl.config(text="—")
        self.lbl_exec_time.config(text="")

    def _clear_logs(self):
        for w in (self.log_global, self.log_puzzle):
            w.config(state="normal")
            w.delete("1.0", "end")
            w.config(state="disabled")


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app  = EscapeRoomGUI(root)
    root.mainloop()
