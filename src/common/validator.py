"""
Solution validator for Bandwidth Coloring Problem (BCP).
Ensures all vertices are colored with integers in 1..k and |c(u) - c(v)| >= d(u, v).
"""
from typing import Dict, Tuple
from .graph_loader import BCPGraph


def validate_bcp_solution(
    graph: BCPGraph, coloring: Dict[int, int]
) -> Tuple[bool, int, str]:
    """
    Validate a 1-indexed coloring {v: c_v} on a BCPGraph.
    Returns:
        (is_valid, span, message)
    """
    if len(coloring) != graph.n_vertices:
        return (
            False,
            -1,
            f"Incomplete coloring: colored {len(coloring)}/{graph.n_vertices} vertices.",
        )

    for v in range(graph.n_vertices):
        if v not in coloring:
            return False, -1, f"Vertex {v} is missing from coloring."
        if not isinstance(coloring[v], int) or coloring[v] < 1:
            return False, -1, f"Vertex {v} has invalid color {coloring[v]} (must be >= 1)."

    for u, v, w in graph.edges:
        diff = abs(coloring[u] - coloring[v])
        if diff < w:
            return (
                False,
                -1,
                f"Edge ({u}, {v}) violated: |c({u})={coloring[u]} - c({v})={coloring[v]}| = {diff} < {w}.",
            )

    span = max(coloring.values()) if coloring else 0
    return True, span, "OK"
