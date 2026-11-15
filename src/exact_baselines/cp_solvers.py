"""
[Thành viên 3] Constraint Programming Formulations for BCP (OR-Tools CP-SAT & CPLEX CP).
Formulation:
    minimize z_max
    s.t. |c(u) - c(v)| >= d(u, v)   for all {u, v} in E
         1 <= c(v) <= z_max <= H(G)  for all v in V
"""
# TODO [Thành viên 3]: Implement OR-Tools CP-SAT and CPLEX CP Optimizer solvers inheriting from BaseBCPSolver.
