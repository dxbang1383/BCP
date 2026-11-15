"""
[Thành viên 2] Solver runner for POP-S-B & POPH-S-B (Multi-shot SAT & Incremental SAT).
"""
from typing import Dict, Optional, Tuple
import time
from pysat.solvers import Solver
from src.common.base_solver import BaseBCPSolver, SolverResult
from src.common.bounds import compute_initial_bounds
from src.common.graph_loader import BCPGraph, get_table3_group
from src.common.validator import validate_bcp_solution
from .pop_encoding import build_pop_s_b_cnf


def extract_pop_coloring(
    graph: BCPGraph, k: int, y_vars: Dict[Tuple[int, int], int], model_set: set
) -> Dict[int, int]:
    """Decode 1-based vertex colors from Partial-Ordering variables y_{v, i}."""
    coloring: Dict[int, int] = {}
    for v in range(graph.n_vertices):
        # Color of v is 1 + number of i in 1..k-1 where y_{v,i} is True
        # Equivalently, smallest i in 1..k such that y_{v,i} is False
        assigned = k
        for i in range(1, k + 1):
            if y_vars[(v, i)] not in model_set:
                assigned = i
                break
        coloring[v] = assigned
    return coloring


class PopSatBCPSolver(BaseBCPSolver):
    """Order / Partial-Ordering SAT Solver for BCP (supports 'multi-shot' and 'incremental' modes)."""

    def __init__(
        self,
        model_type: str = "POP-S-B",
        solver_name: str = "cadical153",
        mode: str = "incremental",
        timeout: float = 3600.0,
    ):
        super().__init__(timeout=timeout)
        self.model_type = model_type
        self.solver_name = solver_name
        self.mode = mode

    def solve(self, graph: BCPGraph) -> Tuple[SolverResult, Optional[Dict[int, int]]]:
        t0 = time.perf_counter()
        lb, init_ub, best_coloring = compute_initial_bounds(graph)
        best_ub = init_ub
        encode_time = 0.0
        solve_time = 0.0
        n_vars, n_clauses = 0, 0

        if self.mode == "incremental":
            t_enc = time.perf_counter()
            cnf, y_vars, _ = build_pop_s_b_cnf(graph, init_ub)
            encode_time += time.perf_counter() - t_enc
            n_vars, n_clauses = cnf.nv, len(cnf.clauses)

            with Solver(name=self.solver_name, bootstrap_with=cnf) as solver:
                k = best_ub - 1
                while k >= lb and (time.perf_counter() - t0) < self.timeout:
                    # In Order Encoding, restricting max color to <= k simply means y_{v, k} = False!
                    for v in range(graph.n_vertices):
                        solver.add_clause([-y_vars[(v, k)]])
                    t_sol = time.perf_counter()
                    sat = solver.solve()
                    solve_time += time.perf_counter() - t_sol
                    if not sat:
                        lb = k + 1
                        break
                    model_set = set(solver.get_model())
                    coloring = extract_pop_coloring(graph, k, y_vars, model_set)
                    valid, span, _ = validate_bcp_solution(graph, coloring)
                    if valid:
                        best_ub = span
                        best_coloring = coloring
                        k = span - 1
                    else:
                        break
        else:
            # Multi-shot descending linear search
            k = best_ub - 1
            while k >= lb and (time.perf_counter() - t0) < self.timeout:
                t_enc = time.perf_counter()
                cnf, y_vars, _ = build_pop_s_b_cnf(graph, k)
                encode_time += time.perf_counter() - t_enc
                if n_vars == 0:
                    n_vars, n_clauses = cnf.nv, len(cnf.clauses)

                with Solver(name=self.solver_name, bootstrap_with=cnf) as solver:
                    t_sol = time.perf_counter()
                    sat = solver.solve()
                    solve_time += time.perf_counter() - t_sol
                    if not sat:
                        lb = k + 1
                        break
                    model_set = set(solver.get_model())
                    coloring = extract_pop_coloring(graph, k, y_vars, model_set)
                    valid, span, _ = validate_bcp_solution(graph, coloring)
                    if valid:
                        best_ub = span
                        best_coloring = coloring
                        k = span - 1
                    else:
                        break

        total_time = time.perf_counter() - t0
        res = SolverResult(
            instance=graph.name,
            group=get_table3_group(graph.name),
            n_vertices=graph.n_vertices,
            n_edges=graph.n_edges,
            avg_weight=round(graph.avg_edge_weight, 2),
            method=self.model_type,
            mode=self.mode,
            solver_backend=self.solver_name,
            amo_type="order",
            n_vars=n_vars,
            n_clauses=n_clauses,
            init_ub=init_ub,
            best_lb=lb,
            best_ub=best_ub,
            solved_optimal=(lb == best_ub),
            encode_time_sec=round(encode_time, 4),
            solve_time_sec=round(solve_time, 4),
            total_time_sec=round(total_time, 4),
        )
        return res, best_coloring
