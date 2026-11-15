"""
Standardized Base Solver and Result Schema for all 3 team members.
"""
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Dict, Optional, Tuple
from .graph_loader import BCPGraph


@dataclass
class SolverResult:
    instance: str
    group: str
    n_vertices: int
    n_edges: int
    avg_weight: float
    method: str           # e.g., "ASS-S-B", "POP-S-B", "POPH-S-B", "ASS-I-B", "POP-I-B", "CP-SAT"
    mode: str             # e.g., "multi-shot", "incremental", "exact"
    solver_backend: str   # e.g., "cadical153", "glucose4", "kissat", "gurobi", "cplex-mip", "ortools"
    amo_type: str         # e.g., "seqcounter", "pairwise", "binary", "commander", "product", "none"
    n_vars: int
    n_clauses: int
    init_ub: int
    best_lb: int
    best_ub: int
    solved_optimal: bool
    encode_time_sec: float
    solve_time_sec: float
    total_time_sec: float

    def to_dict(self) -> Dict:
        return asdict(self)


class BaseBCPSolver(ABC):
    """Abstract base class that all Member 1, Member 2, and Member 3 solvers inherit from."""

    def __init__(self, timeout: float = 3600.0):
        self.timeout = timeout

    @abstractmethod
    def solve(self, graph: BCPGraph) -> Tuple[SolverResult, Optional[Dict[int, int]]]:
        """Run the solver on `graph` within `self.timeout` seconds."""
        raise NotImplementedError
