"""Common utilities for Bandwidth Coloring Problem (BCP) on GEOM instances."""
from .graph_loader import BCPGraph, load_geom_instance, list_geom_instances, TABLE5_OPTIMAL, get_table3_group
from .bounds import greedy_dsatur_bcp, compute_initial_bounds
from .validator import validate_bcp_solution
from .base_solver import SolverResult, BaseBCPSolver

__all__ = [
    "BCPGraph",
    "load_geom_instance",
    "list_geom_instances",
    "TABLE5_OPTIMAL",
    "get_table3_group",
    "greedy_dsatur_bcp",
    "compute_initial_bounds",
    "validate_bcp_solution",
    "SolverResult",
    "BaseBCPSolver",
]
