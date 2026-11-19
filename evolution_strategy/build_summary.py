# This file was generated with AI assistance; Group 7 must review it.
"""Build the consolidated ES summary from completed case exports.

Run from the repository root, after extracting the archived raw results::

    python -m evolution_strategy.build_summary --mode full

This tool reads saved CSV files only; it does not run optimization.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from evolution_strategy.plot_comparisons import SUMMARY_COLUMNS

SUMMARY_NAME = "es_summary_45_cases.csv"

# A stable column order, identical to the report's committed summary schema.
COLUMNS = (
    "dataset", "alpha", "variant", "num_assets", "target_return",
    "num_runs", "evaluations_per_run", "best_variance", "mean_variance",
    "std_variance", "feasible_rate_percent", "mean_runtime_seconds",
)
assert set(COLUMNS) == SUMMARY_COLUMNS


def _first_row(path: Path) -> dict[str, str]:
    """Read exactly one representative row, rejecting missing or empty CSVs."""
    if not path.is_file():
        raise FileNotFoundError(f"Missing required ES export: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        row = next(reader, None)
        if row is None:
            raise ValueError(f"Empty ES export: {path}")
        return row


def _case_row(folder: Path) -> dict[str, str | int]:
    """Convert one completed case's raw exports to the summary schema."""
    case = _first_row(folder / "summary.csv")
    first_run = _first_row(folder / "runs.csv")
    try:
        weight_vector = json.loads(case["best_weights_json"])
        if not isinstance(weight_vector, list) or not weight_vector:
            raise ValueError("best_weights_json must contain a nonempty list")
        row = {
            "dataset": case["dataset"],
            "alpha": case["alpha"],
            "variant": case["variant"],
            "num_assets": len(weight_vector),
            "target_return": first_run["target_return"],
            "num_runs": case["num_runs"],
            "evaluations_per_run": case["evaluations"],
            "best_variance": case["best_variance"],
            "mean_variance": case["mean_variance"],
            "std_variance": case["std_variance"],
            "feasible_rate_percent": case["feasible_rate_percent"],
            "mean_runtime_seconds": case["mean_runtime_seconds"],
        }
        # Validate fields used as sort keys and reject malformed exports.
        float(row["alpha"])
        int(row["num_runs"])
        int(row["evaluations_per_run"])
        for key in (
            "target_return", "best_variance", "mean_variance", "std_variance",
            "feasible_rate_percent", "mean_runtime_seconds",
        ):
            float(row[key])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid ES results in {folder}: {error}") from error
    return row


def build_summary(cases_dir: Path, out_path: Path) -> int:
    """Write a 12-column summary of all completed case folders.

    Incomplete/unmarked case folders are ignored. A marked case with missing or
    malformed exports is an error, not a reason to silently omit a result.
    Returns the number of summary rows written.
    """
    cases_dir = Path(cases_dir)
    out_path = Path(out_path)
    if not cases_dir.is_dir():
        raise FileNotFoundError(f"Missing ES cases directory: {cases_dir}")

    folders = sorted(
        folder for folder in cases_dir.iterdir()
        if folder.is_dir() and (folder / "complete.json").is_file()
    )
    if not folders:
        raise FileNotFoundError(f"No completed ES cases in: {cases_dir}")

    rows = [_case_row(folder) for folder in folders]
    keys = [(row["dataset"], float(row["alpha"]), row["variant"]) for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate dataset/alpha/variant keys in completed ES cases")
    rows.sort(key=lambda row: (row["dataset"], float(row["alpha"]), row["variant"]))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = out_path.with_name(out_path.name + ".tmp")
    try:
        with temporary.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temporary, out_path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", type=Path, default=Path("../es_experiment_results"),
        help="Parent directory containing full/ and/or smoke/ case exports",
    )
    parser.add_argument("--mode", choices=("full", "smoke"), default="full")
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output CSV path (default: <results-dir>/es_summary_45_cases.csv for full)",
    )
    args = parser.parse_args()
    cases_dir = args.results_dir / args.mode
    out_path = args.out or (
        args.results_dir / (SUMMARY_NAME if args.mode == "full" else "es_summary_smoke.csv")
    )
    if args.mode == "full":
        completed_count = sum(
            folder.is_dir() and (folder / "complete.json").is_file()
            for folder in cases_dir.iterdir()
        ) if cases_dir.is_dir() else 0
        if completed_count != 45:
            parser.error(
                f"Expected 45 completed cases in full mode; found {completed_count}"
            )
    count = build_summary(cases_dir, out_path)
    print(f"Saved {count} ES case rows to {out_path}")


if __name__ == "__main__":
    main()
