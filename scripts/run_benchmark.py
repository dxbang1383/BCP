#!/usr/bin/env python3
"""
Benchmark runner for Bandwidth Coloring Problem (BCP) on the 33 GEOM instances.
Usage examples:
    python3 scripts/run_benchmark.py --check-dataset
    python3 scripts/run_benchmark.py --method POP-S-B --mode incremental --limit 5
    python3 scripts/run_benchmark.py --method ASS-S-B --mode multi-shot --amo seqcounter --limit 5
"""
import argparse
import csv
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.common.bounds import compute_initial_bounds
from src.common.graph_loader import (
    TABLE5_OPTIMAL,
    get_table3_group,
    list_geom_instances,
    load_geom_instance,
)
from src.common.validator import validate_bcp_solution


def inspect_dataset(data_dir: str = "data/GEOM") -> None:
    files = list_geom_instances(ROOT_DIR / data_dir)
    print(f"Found {len(files)} GEOM instances in '{data_dir}':")
    print(
        f"{'Instance':<10} {'Group':<16} {'|V|':>5} {'|E|':>6} {'avg(d)':>7} "
        f"{'Init LB':>8} {'Greedy UB':>10} {'Paper Opt':>10} {'Valid?':>7}"
    )
    print("-" * 86)
    for fpath in files:
        g = load_geom_instance(fpath)
        lb, ub, col = compute_initial_bounds(g)
        ok, _, _ = validate_bcp_solution(g, col)
        ref_lb, ref_ub, is_opt = TABLE5_OPTIMAL.get(g.name, (-1, -1, False))
        opt_str = str(ref_ub) if is_opt else f"[{ref_lb},{ref_ub}]"
        print(
            f"{g.name:<10} {get_table3_group(g.name):<16} {g.n_vertices:>5} {g.n_edges:>6} "
            f"{g.avg_edge_weight:>7.2f} {lb:>8} {ub:>10} {opt_str:>10} {str(ok):>7}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BCP benchmarks on 33 GEOM instances.")
    parser.add_argument("--check-dataset", action="store_true", help="Verify all 33 GEOM instances and Greedy UB")
    parser.add_argument("--method", type=str, default="POP-S-B", choices=["ASS-S-B", "POP-S-B"])
    parser.add_argument("--mode", type=str, default="incremental", choices=["multi-shot", "incremental"])
    parser.add_argument("--solver", type=str, default="cadical153", help="PySAT solver name")
    parser.add_argument("--amo", type=str, default="seqcounter", help="AMO encoding for ASS-S-B")
    parser.add_argument("--timeout", type=float, default=60.0, help="Timeout per instance in seconds")
    parser.add_argument("--limit", type=int, default=0, help="Max number of instances to run (0 = all 33)")
    parser.add_argument("--out", type=str, default="results/raw_logs/benchmark.csv", help="Output CSV path")
    args = parser.parse_args()

    if args.check_dataset:
        inspect_dataset()
        return

    from src.sat_order.pop_solver import PopSatBCPSolver
    from src.sat_pairwise.ass_solver import AssSatBCPSolver

    files = list_geom_instances(ROOT_DIR / "data/GEOM")
    if args.limit > 0:
        files = files[: args.limit]

    out_path = ROOT_DIR / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    for fpath in files:
        g = load_geom_instance(fpath)
        if args.method == "ASS-S-B":
            runner = AssSatBCPSolver(
                solver_name=args.solver, mode=args.mode, amo_type=args.amo, timeout=args.timeout
            )
        else:
            runner = PopSatBCPSolver(
                model_type="POP-S-B", solver_name=args.solver, mode=args.mode, timeout=args.timeout
            )
        res, _ = runner.solve(g)
        results.append(res.to_dict())
        print(
            f"[{res.method} | {res.mode}] {res.instance:<10} "
            f"UB={res.best_ub} (Optimal={res.solved_optimal}) "
            f"Vars={res.n_vars} Clauses={res.n_clauses} Time={res.total_time_sec:.3f}s"
        )

    if results:
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved {len(results)} records to {out_path}")


if __name__ == "__main__":
    main()
