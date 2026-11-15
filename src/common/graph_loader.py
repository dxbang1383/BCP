"""
Loader for DIMACS Bandwidth Coloring (.col) instances (33 GEOM benchmarks).
Reference: Faber, Jabrayilov, and Mutzel (SAT 2024), Section 4 & Table 3 / Table 5.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Reference results from Table 5 (page 20 of Faber et al., SAT 2024)
# Format: instance_name -> (best_known_lb, best_known_ub, is_proven_optimal_in_paper)
TABLE5_OPTIMAL: Dict[str, Tuple[int, int, bool]] = {
    "GEOM20": (21, 21, True),
    "GEOM20a": (20, 20, True),
    "GEOM20b": (13, 13, True),
    "GEOM30": (28, 28, True),
    "GEOM30a": (27, 27, True),
    "GEOM30b": (26, 26, True),
    "GEOM40": (28, 28, True),
    "GEOM40a": (37, 37, True),
    "GEOM40b": (33, 33, True),
    "GEOM50": (28, 28, True),
    "GEOM50a": (50, 50, True),
    "GEOM50b": (35, 35, True),
    "GEOM60": (33, 33, True),
    "GEOM60a": (50, 50, True),
    "GEOM60b": (41, 41, True),
    "GEOM70": (38, 38, True),
    "GEOM70a": (61, 61, True),
    "GEOM70b": (47, 47, True),
    "GEOM80": (41, 41, True),
    "GEOM80a": (63, 63, True),
    "GEOM80b": (60, 60, True),
    "GEOM90": (46, 46, True),
    "GEOM90a": (63, 63, True),
    "GEOM90b": (69, 69, True),
    "GEOM100": (50, 50, True),
    "GEOM100a": (66, 66, True),
    "GEOM100b": (71, 71, True),
    "GEOM110": (50, 50, True),
    "GEOM110a": (69, 69, True),
    "GEOM110b": (77, 77, True),
    "GEOM120": (59, 59, True),
    "GEOM120a": (82, 82, True),
    "GEOM120b": (83, 85, False),  # Open in 1h SAT (LB=81..83, DFMM UB=85)
}


def get_table3_group(instance_name: str) -> str:
    """Map an instance name (e.g., GEOM60a) to its Table 3 group (e.g., GEOM[60a-90a])."""
    name = instance_name.replace(".col", "")
    suffix = "a" if name.endswith("a") else ("b" if name.endswith("b") else "")
    num = int(name.replace("GEOM", "").rstrip("ab"))
    if num <= 50:
        return f"GEOM[20{suffix}-50{suffix}]"
    elif num <= 90:
        return f"GEOM[60{suffix}-90{suffix}]"
    else:
        return f"GEOM[100{suffix}-120{suffix}]"


@dataclass
class BCPGraph:
    """Undirected edge-weighted graph for the Bandwidth Coloring Problem."""
    name: str
    n_vertices: int
    # Edges stored with 0-indexed vertices: (u, v, weight) with u < v
    edges: List[Tuple[int, int, int]] = field(default_factory=list)
    adj: Dict[int, List[Tuple[int, int]]] = field(default_factory=dict)

    @property
    def n_edges(self) -> int:
        return len(self.edges)

    @property
    def avg_edge_weight(self) -> float:
        if not self.edges:
            return 0.0
        return sum(w for _, _, w in self.edges) / len(self.edges)

    @property
    def max_edge_weight(self) -> int:
        if not self.edges:
            return 1
        return max(w for _, _, w in self.edges)

    def degree(self, v: int) -> int:
        return len(self.adj.get(v, []))


def load_geom_instance(filepath: str | Path) -> BCPGraph:
    """
    Read a DIMACS .col file for BCP.
    Note: Self-loops (e u u w) represent vertex weights for multicoloring (BMCP)
    and are ignored in standard Bandwidth Coloring Problem (BCP), matching Utility.py in Faber et al.
    Vertices are converted from 1-indexed (1..n) in file to 0-indexed (0..n-1).
    """
    path = Path(filepath)
    name = path.stem
    n_vertices = 0
    edge_map: Dict[Tuple[int, int], int] = {}

    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("c"):
                continue
            parts = line.split()
            if parts[0] == "p":
                n_vertices = int(parts[2])
            elif parts[0] == "e":
                u = int(parts[1]) - 1
                v = int(parts[2]) - 1
                w = int(parts[3]) if len(parts) >= 4 else 1
                if u == v:
                    # Ignore self-loops (node demands in BMCP)
                    continue
                a, b = (u, v) if u < v else (v, u)
                if (a, b) not in edge_map or w > edge_map[(a, b)]:
                    edge_map[(a, b)] = w

    edges = [(u, v, w) for (u, v), w in sorted(edge_map.items())]
    adj: Dict[int, List[Tuple[int, int]]] = {i: [] for i in range(n_vertices)}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    return BCPGraph(name=name, n_vertices=n_vertices, edges=edges, adj=adj)


def list_geom_instances(data_dir: str | Path = "data/GEOM") -> List[Path]:
    """Return all 33 GEOM .col files sorted in Table 5 order."""
    base = Path(data_dir)
    files = list(base.glob("GEOM*.col"))

    def sort_key(p: Path) -> Tuple[int, str]:
        stem = p.stem.replace("GEOM", "")
        suffix = "a" if stem.endswith("a") else ("b" if stem.endswith("b") else "")
        num = int(stem.rstrip("ab"))
        return (num, suffix)

    return sorted(files, key=sort_key)
