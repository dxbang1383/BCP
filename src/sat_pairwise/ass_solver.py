"""
[Thành viên 1] Solver runner for ASS-S-B (Multi-shot SAT & Incremental SAT).
"""
from typing import Dict, Optional, Tuple
import time
from pysat.solvers import Solver
from src.common.base_solver import BaseBCPSolver, SolverResult
from src.common.bounds import compute_initial_bounds
from src.common.graph_loader import BCPGraph, get_table3_group
from src.common.validator import validate_bcp_solution
from .ass_encoding import build_ass_s_b_cnf


class AssSatBCPSolver(BaseBCPSolver):
    """Assignment-based SAT Solver for BCP (supports 'multi-shot' and 'incremental' modes)."""

    def __init__(
        self,
        solver_name: str = "cadical153",
        mode: str = "multi-shot",
        amo_type: str = "seqcounter",
        timeout: float = 3600.0,
    ):
        super().__init__(timeout=timeout)
        self.solver_name = solver_name
        self.mode = mode
        self.amo_type = amo_type

    def solve(self, graph: BCPGraph) -> Tuple[SolverResult, Optional[Dict[int, int]]]:
        t0 = time.perf_counter()
        lb, init_ub, best_coloring = compute_initial_bounds(graph)
        best_ub = init_ub
        encode_time = 0.0
        solve_time = 0.0
        n_vars, n_clauses = 0, 0

        if self.mode == "incremental":
            t_enc = time.perf_counter()
            cnf, x_vars, _ = build_ass_s_b_cnf(graph, init_ub, amo_type=self.amo_type)
            encode_time += time.perf_counter() - t_enc
            n_vars, n_clauses = cnf.nv, len(cnf.clauses)

            with Solver(name=self.solver_name, bootstrap_with=cnf) as solver:
                k = best_ub - 1
                while k >= lb and (time.perf_counter() - t0) < self.timeout:
                    # Forbid colors > k using unit clauses [-x_{v, c}]
                    for c_forbid in range(k + 1, best_ub + 1):
                        for v in range(graph.n_vertices):
                            solver.add_clause([-x_vars[(v, c_forbid)]])
                    t_sol = time.perf_counter()
                    sat = solver.solve()
                    solve_time += time.perf_counter() - t_sol
                    if not sat:
                        lb = k + 1
                        break
                    model_set = set(solver.get_model())
                    coloring = {}
                    for v in range(graph.n_vertices):
                        for i in range(1, k + 1):
                            if x_vars[(v, i)] in model_set:
                                coloring[v] = i
                                break
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
                cnf, x_vars, _ = build_ass_s_b_cnf(graph, k, amo_type=self.amo_type)
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
                    coloring = {}
                    for v in range(graph.n_vertices):
                        for i in range(1, k + 1):
                            if x_vars[(v, i)] in model_set:
                                coloring[v] = i
                                break
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
            method="ASS-S-B",
            mode=self.mode,
            solver_backend=self.solver_name,
            amo_type=self.amo_type,
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
