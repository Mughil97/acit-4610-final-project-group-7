"""Validate saved ES raw experiments against Portfolio 2026 requirements.

Run from the repository root:
    python -m evolution_strategy.audit_results

This script only reads the existing experiment files; it never launches an ES
optimization run and it never changes experiment results.
"""

import argparse
import csv
import json
import math
import statistics
from itertools import zip_longest
from pathlib import Path

from evolution_strategy.evaluation import (
    evaluate_cost,
    evaluate_profit,
    get_target_return,
)
from evolution_strategy.results import PORTFOLIOS

VARIANTS = ("one_plus_one", "ten_plus_seventy", "ten_comma_seventy")
OR_LIBRARY_COUNTS = {"port1": 31, "port2": 85, "port3": 89, "port4": 98, "port5": 225}
TOL = 1e-8


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def close(actual, expected, context, *, abs_tol=1e-10, rel_tol=1e-8):
    require(
        math.isfinite(actual)
        and math.isfinite(expected)
        and math.isclose(actual, expected, abs_tol=abs_tol, rel_tol=rel_tol),
        f"{context}: {actual!r} is not consistent with {expected!r}",
    )


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def inspect_port1_reference():
    """Validate the three explicit port1 benchmarks from assignment page 10."""
    portfolio = PORTFOLIOS["port1"]
    uniform = [1.0 / len(portfolio)] * len(portfolio)
    observed = {
        "equal_allocation_return": evaluate_profit(portfolio, uniform),
        "equal_allocation_variance": evaluate_cost(portfolio, uniform),
        "alpha_050_target_return": get_target_return(portfolio, 0.5),
    }
    expected = {
        "equal_allocation_return": 0.003504064516129,
        "equal_allocation_variance": 0.001130937943724,
        "alpha_050_target_return": 0.007184532258065,
    }
    for key, value in expected.items():
        close(observed[key], value, f"port1 parser checkpoint: {key}")
    return observed


def inspect_histories(folder, runs, budget):
    """Stream 30,000 x 10 histories without retaining the raw CSV in memory."""
    with (
        (folder / "run_histories.csv").open(newline="", encoding="utf-8-sig") as history_file,
        (folder / "convergence.csv").open(newline="", encoding="utf-8-sig") as mean_file,
    ):
        histories = csv.reader(history_file)
        means = csv.reader(mean_file)
        seed_order = [int(row["seed"]) for row in runs]
        require(
            next(histories) == ["evaluation", *[f"seed_{seed}" for seed in seed_order]],
            f"{folder.name}: incorrect per-seed history headers",
        )
        require(
            next(means) == ["evaluation", "mean_best_variance"],
            f"{folder.name}: incorrect convergence headers",
        )
        last = [math.inf] * len(seed_order)
        count = 0
        for count, (values, mean_values) in enumerate(
            zip_longest(histories, means), start=1
        ):
            require(values is not None and mean_values is not None,
                    f"{folder.name}: mismatch between histories and mean convergence rows")
            require(len(values) == len(seed_order) + 1,
                    f"{folder.name}: missing seed values at evaluation {count}")
            require(len(mean_values) == 2, f"{folder.name}: bad mean history row {count}")
            require(int(values[0]) == count and int(mean_values[0]) == count,
                    f"{folder.name}: wrong evaluation index at row {count}")
            current = [float(v) for v in values[1:]]
            for i, value in enumerate(current):
                require(math.isfinite(value), f"{folder.name}: nonfinite seed history at {count}")
                require(value <= last[i] + 1e-12,
                        f"{folder.name}: archive history increased for seed {seed_order[i]} at {count}")
            close(float(mean_values[1]), sum(current) / len(current),
                  f"{folder.name}: average archive history at evaluation {count}")
            last = current
        require(count == budget, f"{folder.name}: expected {budget} history rows, found {count}")
        for run, history_final in zip(runs, last):
            close(history_final, float(run["final_variance"]),
                  f"{folder.name}: final history does not match seed {run['seed']}")
    return count


def inspect_case(folder, dataset, alpha, variant, budget, num_runs):
    case = folder.name
    for filename in (
        "summary.csv", "runs.csv", "convergence.csv", "run_histories.csv", "complete.json"
    ):
        require((folder / filename).is_file(), f"{case}: missing {filename}")
    marker = json.loads((folder / "complete.json").read_text(encoding="utf-8"))
    require(marker.get("status") == "complete", f"{case}: invalid completion marker")
    require(marker.get("dataset") == dataset, f"{case}: marker dataset mismatch")
    close(float(marker.get("alpha", -1)), alpha, f"{case}: marker alpha")
    require(marker.get("variant") == variant, f"{case}: marker variant mismatch")
    require(marker.get("num_runs") == num_runs, f"{case}: marker run-count mismatch")
    require(marker.get("evaluations_per_run") == budget, f"{case}: marker budget mismatch")

    portfolio = PORTFOLIOS[dataset]
    n = len(portfolio)
    require(n == OR_LIBRARY_COUNTS[dataset], f"{case}: wrong number of assets")
    target = get_target_return(portfolio, alpha)
    summary_rows = read_csv(folder / "summary.csv")
    require(len(summary_rows) == 1, f"{case}: wrong number of summary rows")
    summary = summary_rows[0]
    require(summary["dataset"] == dataset and summary["variant"] == variant,
            f"{case}: summary identity mismatch")
    close(float(summary["alpha"]), alpha, f"{case}: summary alpha")
    require(int(summary["num_runs"]) == num_runs and int(summary["evaluations"]) == budget,
            f"{case}: summary run/evaluation budget mismatch")

    runs = read_csv(folder / "runs.csv")
    require(len(runs) == num_runs, f"{case}: expected {num_runs} runs, found {len(runs)}")
    require([int(row["seed"]) for row in runs] == list(range(num_runs)),
            f"{case}: seed sequence must be 0..{num_runs - 1}")
    variances, runtimes = [], []
    for run in runs:
        seed = int(run["seed"])
        name = f"{case}, seed {seed}"
        require(int(run["evaluations"]) == budget, f"{name}: wrong evaluation budget")
        weights = json.loads(run["weights_json"])
        require(len(weights) == n, f"{name}: wrong weight-vector dimension")
        require(all(isinstance(w, (int, float)) and math.isfinite(w) for w in weights),
                f"{name}: weight vector has invalid entries")
        require(min(weights) >= -TOL, f"{name}: negative portfolio weight")
        require(abs(sum(weights) - 1.0) <= TOL, f"{name}: weights do not sum to 1")
        return_value = evaluate_profit(portfolio, weights)
        variance_value = evaluate_cost(portfolio, weights)
        require(return_value >= target - TOL, f"{name}: return target violated")
        close(float(run["target_return"]), target, f"{name}: target return")
        close(float(run["portfolio_return"]), return_value, f"{name}: reported return")
        close(float(run["final_variance"]), variance_value, f"{name}: reported variance")
        require(run["feasible"].strip().lower() == "true", f"{name}: reported infeasible")
        runtime = float(run["runtime_seconds"])
        require(math.isfinite(runtime) and runtime >= 0, f"{name}: invalid runtime")
        variances.append(variance_value)
        runtimes.append(runtime)

    close(float(summary["best_variance"]), min(variances), f"{case}: best summary variance")
    close(float(summary["mean_variance"]), statistics.mean(variances), f"{case}: mean variance")
    close(float(summary["std_variance"]), statistics.pstdev(variances),
          f"{case}: population standard deviation")
    close(float(summary["mean_runtime_seconds"]), statistics.mean(runtimes),
          f"{case}: mean runtime", abs_tol=1e-8)
    close(float(summary["feasible_rate_percent"]), 100.0, f"{case}: feasible rate")
    best_weights = json.loads(summary["best_weights_json"])
    require(len(best_weights) == n, f"{case}: summary best weights wrong length")
    close(evaluate_cost(portfolio, best_weights), min(variances),
          f"{case}: summary best allocation variance")
    inspect_histories(folder, runs, budget)
    return summary


def inspect_consolidated(path, case_summaries, budget, num_runs):
    """If the checked-in 45-row summary exists, ensure it matches raw exports."""
    if not path.is_file():
        print(f"NOTICE: consolidated summary not found at {path}; comparison skipped", flush=True)
        return False
    rows = read_csv(path)
    require(len(rows) == len(case_summaries),
            f"Consolidated summary has {len(rows)} rows, expected {len(case_summaries)}")
    keys_seen = set()
    for row in rows:
        dataset, alpha, variant = row["dataset"], float(row["alpha"]), row["variant"]
        key = dataset, alpha, variant
        require(key in case_summaries and key not in keys_seen,
                f"Consolidated summary has unexpected/duplicate case {key}")
        keys_seen.add(key)
        raw = case_summaries[key]
        require(int(row["num_assets"]) == OR_LIBRARY_COUNTS[dataset],
                f"{key}: inconsistent number of assets")
        require(int(row["num_runs"]) == num_runs and int(row["evaluations_per_run"]) == budget,
                f"{key}: consolidated budget mismatch")
        close(float(row["target_return"]),
              get_target_return(PORTFOLIOS[dataset], alpha), f"{key}: target return")
        for consolidated_key, raw_key in (
            ("best_variance", "best_variance"),
            ("mean_variance", "mean_variance"),
            ("std_variance", "std_variance"),
            ("feasible_rate_percent", "feasible_rate_percent"),
            ("mean_runtime_seconds", "mean_runtime_seconds"),
        ):
            close(float(row[consolidated_key]), float(raw[raw_key]),
                  f"{key}: consolidated {consolidated_key}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("../es_experiment_results/full"))
    parser.add_argument("--summary", type=Path,
                        default=Path("evolution_strategy/report_data/es_summary_45_cases.csv"))
    parser.add_argument("--report-out", type=Path,
                        default=Path("../es_experiment_results/validation_report.json"))
    parser.add_argument("--budget", type=int, default=30000)
    parser.add_argument("--num-runs", type=int, default=10)
    parser.add_argument("--datasets", nargs="+", default=list(OR_LIBRARY_COUNTS))
    parser.add_argument("--alphas", type=float, nargs="+", default=[0.25, 0.50, 0.75])
    parser.add_argument("--variants", nargs="+", default=list(VARIANTS))
    args = parser.parse_args()
    require(args.budget > 0 and args.num_runs > 0, "Budget and number of runs must be positive")
    parser_values = inspect_port1_reference()
    expected = {
        f"{dataset}_alpha{int(alpha * 100):03d}_{variant}_e{args.budget}_r{args.num_runs}":
        (dataset, alpha, variant)
        for dataset in args.datasets
        for alpha in args.alphas
        for variant in args.variants
    }
    require(args.results_dir.is_dir(), f"Missing experiment folder: {args.results_dir}")
    actual = {folder.name for folder in args.results_dir.iterdir() if folder.is_dir()}
    require(actual == set(expected),
            f"Unexpected/missing cases. Missing={sorted(set(expected)-actual)}; "
            f"unexpected={sorted(actual-set(expected))}")

    checked = {}
    for i, (name, (dataset, alpha, variant)) in enumerate(sorted(expected.items()), start=1):
        summary = inspect_case(args.results_dir / name, dataset, alpha, variant,
                               args.budget, args.num_runs)
        checked[(dataset, alpha, variant)] = summary
        print(f"PASS {i:02d}/{len(expected)}  {name}", flush=True)

    consolidated_checked = inspect_consolidated(args.summary, checked, args.budget,
                                                args.num_runs)
    report = {
        "status": "passed", "cases": len(expected),
        "runs": len(expected) * args.num_runs,
        "evaluations_per_run": args.budget,
        "total_objective_evaluations": len(expected) * args.num_runs * args.budget,
        "parser_reference_port1": parser_values,
        "portfolio_checks": "all weights, computed returns, computed variances, and 1e-8 feasibility constraints",
        "history_checks": "each evaluation count, nonincreasing per-seed archive, final values and mean curve",
        "summary_consistency_checked": consolidated_checked,
    }
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("\nAUDIT PASSED:", report["cases"], "cases,", report["runs"], "runs,",
          f"{report['total_objective_evaluations']:,}", "evaluations", flush=True)
    print("Saved audit report:", args.report_out, flush=True)


if __name__ == "__main__":
    main()
