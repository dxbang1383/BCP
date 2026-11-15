"""
[Thành viên 1] Pairwise / Assignment-based SAT Encoding (ASS-S-B) & AMO Encodings.
Reference: Faber et al. (SAT 2024), Section 2.2, Equations (8a), (9a)-(9d), and (11).
"""
import math
from typing import Dict, List, Tuple
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from src.common.graph_loader import BCPGraph


PYSAT_AMO_MAP = {
    "pairwise": EncType.pairwise,
    "seqcounter": EncType.seqcounter,
    "binary": EncType.bitwise,
    "bitwise": EncType.bitwise,
    "ladder": EncType.ladder,
    "totalizer": EncType.totalizer,
    "mtotalizer": EncType.mtotalizer,
    "kmtotalizer": EncType.kmtotalizer,
    "sortnetwrk": EncType.sortnetwrk,
    "cardnetwrk": EncType.cardnetwrk,
}


def encode_amo_commander(lits: List[int], vpool: IDPool, group_size: int = 3) -> List[List[int]]:
    """Commander encoding for At-Most-One (AMO) over `lits`."""
    clauses: List[List[int]] = []
    current = list(lits)
    while len(current) > group_size:
        next_level: List[int] = []
        for idx in range(0, len(current), group_size):
            grp = current[idx : idx + group_size]
            if len(grp) == 1:
                next_level.append(grp[0])
                continue
            cmd_var = vpool.id()
            next_level.append(cmd_var)
            # Pairwise AMO within group + (-cmd_var)
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    clauses.append([-grp[i], -grp[j]])
                clauses.append([-grp[i], cmd_var])
            clauses.append([-cmd_var] + grp)
        current = next_level
    for i in range(len(current)):
        for j in range(i + 1, len(current)):
            clauses.append([-current[i], -current[j]])
    return clauses


def encode_amo_product(lits: List[int], vpool: IDPool) -> List[List[int]]:
    """2D Product encoding (Chen 2010) for At-Most-One (AMO) over `lits`."""
    n = len(lits)
    if n <= 1:
        return []
    p = math.ceil(math.sqrt(n))
    q = math.ceil(n / p)
    u_vars = [vpool.id() for _ in range(p)]
    v_vars = [vpool.id() for _ in range(q)]
    clauses: List[List[int]] = []
    for i in range(p):
        for j in range(i + 1, p):
            clauses.append([-u_vars[i], -u_vars[j]])
    for i in range(q):
        for j in range(i + 1, q):
            clauses.append([-v_vars[i], -v_vars[j]])
    for idx, lit in enumerate(lits):
        r = idx // q
        c = idx % q
        clauses.append([-lit, u_vars[r]])
        clauses.append([-lit, v_vars[c]])
    return clauses


def build_ass_s_b_cnf(
    graph: BCPGraph, k: int, amo_type: str = "seqcounter"
) -> Tuple[CNF, Dict[Tuple[int, int], int], IDPool]:
    """
    Build CNF for Assignment-based SAT encoding (ASS-S-B) for k colors (colors 1..k).
    Variables:
        x[(v, i)] for v in 0..n-1 and color i in 1..k.
    Clauses:
        - ALO (8a): For each vertex v, x_{v,1} v ... v x_{v,k}
        - AMO (9a-9d / PySAT CardEnc / Commander / Product): At most one color per vertex v
        - Edge distance (11): For each edge (u, v, d_uv) and i, j in 1..k with |i - j| < d_uv:
            ~x_{u,i} v ~x_{v,j}
    """
    cnf = CNF()
    vpool = IDPool()
    x: Dict[Tuple[int, int], int] = {}

    for v in range(graph.n_vertices):
        lits = []
        for i in range(1, k + 1):
            var_id = vpool.id(f"x_{v}_{i}")
            x[(v, i)] = var_id
            lits.append(var_id)
        # (8a) At-Least-One (ALO)
        cnf.append(lits)
        # (9a-9d) At-Most-One (AMO)
        if amo_type and amo_type != "none" and k > 1:
            if amo_type == "commander":
                cnf.extend(encode_amo_commander(lits, vpool))
            elif amo_type == "product":
                cnf.extend(encode_amo_product(lits, vpool))
            else:
                enc = PYSAT_AMO_MAP.get(amo_type, EncType.seqcounter)
                amo_clauses = CardEnc.atmost(lits=lits, bound=1, vpool=vpool, encoding=enc)
                cnf.extend(amo_clauses.clauses)

    # (11) Bandwidth edge constraints
    for u, v, d_e in graph.edges:
        for i in range(1, k + 1):
            j_min = max(1, i - d_e + 1)
            j_max = min(k, i + d_e - 1)
            for j in range(j_min, j_max + 1):
                cnf.append([-x[(u, i)], -x[(v, j)]])

    return cnf, x, vpool
