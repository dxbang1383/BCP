"""
Upper bound and lower bound heuristics for Bandwidth Coloring Problem (BCP).
Matches DSaturBandwidth in Heuristiken.py of Faber, Jabrayilov, and Mutzel (SAT 2024).
"""
from queue import PriorityQueue
from typing import Dict, Tuple
from .graph_loader import BCPGraph


def greedy_dsatur_bcp(graph: BCPGraph) -> Tuple[int, Dict[int, int]]:
    """
    Compute a valid BCP coloring and upper bound H(G) using the author's greedy heuristic.
    Returns:
        (max_color, coloring) where coloring maps vertex v (0..n-1) -> color c in {1..max_color}.
    """
    n = graph.n_vertices
    colors = [-1] * n
    neighbouring_colors = [set() for _ in range(n)]
    saturations: PriorityQueue = PriorityQueue()

    max_color = 0
    while min(colors) == -1:
        uncolored = [x for x in range(n) if colors[x] == -1]
        start_v = max(uncolored, key=lambda x: graph.degree(x))
        saturations.put((start_v, 0))
        while not saturations.empty():
            v = saturations.get()[0]
            if colors[v] > -1:
                continue
            colors[v] = 0
            # Forbidden interval around each already-colored neighbor w
            intervals = [
                (colors[w] - w_uv, colors[w] + w_uv)
                for w, w_uv in graph.adj[v]
                if colors[w] > -1
            ]
            intervals.sort()
            idx = 0
            while idx < len(intervals) and colors[v] > intervals[idx][0]:
                colors[v] = max(colors[v], intervals[idx][1])
                idx += 1
            max_color = max(max_color, colors[v])
            for w, _ in graph.adj[v]:
                if colors[w] == -1:
                    neighbouring_colors[w].add(v)
                    saturations.put((w, len(neighbouring_colors)))

    # Convert 0-based colors (0..max_color) to 1-based colors (1..max_color+1)
    coloring_1based = {v: c + 1 for v, c in enumerate(colors)}
    return max_color + 1, coloring_1based


def compute_initial_bounds(graph: BCPGraph) -> Tuple[int, int, Dict[int, int]]:
    """
    Compute (lower_bound, upper_bound, init_coloring) for BCP.
    - Trivial valid lower bound from single edge: max_{e=(u,v)} (d(e) + 1) if E != empty else 1.
    - Upper bound H(G) from greedy_dsatur_bcp.
    """
    lb = 1
    if graph.edges:
        lb = max(w + 1 for _, _, w in graph.edges)
    ub, coloring = greedy_dsatur_bcp(graph)
    return lb, ub, coloring
