# Proyecto1---IA

# Escape Room - Búsqueda en Grafos

Proyecto del curso de Inteligencia Artificial.

## Integrantes

| Nombre | Código |
| :----------- | :----------: |
| Miguel Angel Arboleda Grueso | 2160253-3743 |
| Diego Andres Bolaños Isiquita | 2379918-3743 |
| Jose David Marmol Otero | 202266370 - 3743|
| José Daniel Grajales Cadena | 2067513 - 3743|
| Santiago Alexander Criollo | 2380661-3743 |

## Descripción

Sistema que simula un **escape room** modelado como un grafo dirigido. Explora el mapa global con búsqueda **no informada** (BFS, DFS, UCS) para encontrar la salida, y resuelve puzzles en salas bloqueadas usando **A*** con costos y heurísticas. Incluye interfaz gráfica e interfaz de línea de comandos.

## ¿Cómo funciona?

- **Búsqueda global**: BFS, DFS o UCS exploran el mapa desde la entrada hasta la salida.
- **Puzzles**: A* resuelve los candados de salas bloqueadas usando costos y heurísticas del JSON.
- **Resultados**: Muestra el grafo, ruta recorrida y estadísticas (nodos explorados, coste total, tiempo).

## Requisitos

- Python 3.10+
- Dependencias: `matplotlib`, `networkx`, `numpy` (ver `requirements.txt`)

## Instalación y uso

**1. Instalar dependencias:**
```powershell
python -m pip install -r requirements.txt
```

**2. Ejecutar:**

Interfaz gráfica:
```powershell
python main.py
```

Línea de comandos (BFS/DFS/UCS):
```powershell
python main.py --cli BFS
```

Con otro archivo de escenario:
```powershell
python main.py --json ruta\archivo.json
python main.py --cli UCS --json ruta\archivo.json
```


