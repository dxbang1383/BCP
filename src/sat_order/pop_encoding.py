"""
[Thành viên 2] Order Encoding / Partial-Ordering SAT Encodings (POP-S-B and POPH-S-B).
Reference: Faber et al. (SAT 2024), Section 3.1 & Section 3.3, Equations (12a), (12b), (16a)-(16e), (19), (20).
"""
from typing import Dict, Tuple
from pysat.formula import CNF, IDPool
from src.common.graph_loader import BCPGraph


def build_pop_s_b_cnf(
    graph: BCPGraph, k: int
) -> Tuple[CNF, Dict[Tuple[int, int], int], IDPool]:
    """
    Build CNF for Partial-Ordering SAT encoding (POP-S-B) for k colors (1..k).
    Variables:
        y[(v, i)] for v in 0..n-1 and color i in 1..k.
        y[(v, i)] is True iff color(v) > i (i.e., color i is smaller than vertex v).
    Clauses:
        - (12a) ~y_{v,k} for all v in V
        - (12b) y_{v,i} v ~y_{v,i+1} for all v in V, i = 1..k-1
        - (19) ~y_{u,i-1} v y_{u,i} v ~y_{v,i-d(e)} v y_{v,i+d(e)-1} for all e={u,v} in E, i = 1..k
          (with boundary convention: y_{w, idx} = True for idx < 1, y_{w, idx} = False for idx > k)
    """
    cnf = CNF()
    vpool = IDPool()
    y: Dict[Tuple[int, int], int] = {}

    for v in range(graph.n_vertices):
        for i in range(1, k + 1):
            y[(v, i)] = vpool.id(f"y_{v}_{i}")
        # (12a) Every vertex has color <= k
        cnf.append([-y[(v, k)]])
        # (12b) Order transitivity: c(v) > i+1 => c(v) > i
        for i in range(1, k):
            cnf.append([y[(v, i)], -y[(v, i + 1)]])

    # (19) Bandwidth edge constraints (1 clause per edge and color i=1..k)
    for u, v, d_e in graph.edges:
        # i = 1: y_{u,0} is True => ~y_{u,0} is False (omitted)
        clause_1 = [y[(u, 1)]]
        if d_e <= k:
            clause_1.append(y[(v, d_e)])
        cnf.append(clause_1)

        # i = 2..k
        for i in range(2, k + 1):
            clause = [-y[(u, i - 1)], y[(u, i)]]
            if i - d_e >= 1:
                clause.append(-y[(v, i - d_e)])
            if i + d_e - 1 <= k:
                clause.append(y[(v, i + d_e - 1)])
            cnf.append(clause)

    return cnf, y, vpool
