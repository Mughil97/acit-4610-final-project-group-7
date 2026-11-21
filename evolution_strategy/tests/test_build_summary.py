"""Regression tests for the cross-platform ES summary builder."""

import csv
import json
import sys

import pytest

from evolution_strategy import build_summary, export_experiments
from evolution_strategy.plot_comparisons import SUMMARY_COLUMNS

# =============================================================================
# BEGIN AI-ASSISTED SECTION
# Purpose: Create synthetic experiment fixtures and read CSV test outputs.
# =============================================================================

def _case(root, dataset="port1", alpha="0.25", variant="one_plus_one",
          complete=True, best=0.001):
    folder = root / f"{dataset}_alpha{int(float(alpha)*100):03d}_{variant}_e30000_r10"
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=(
            "dataset", "alpha", "variant", "num_runs", "evaluations",
            "best_variance", "mean_variance", "std_variance",
            "feasible_rate_percent", "mean_runtime_seconds", "best_weights_json",
        ))
        writer.writeheader()
        writer.writerow({
            "dataset": dataset, "alpha": alpha, "variant": variant,
            "num_runs": 10, "evaluations": 30000,
            "best_variance": best, "mean_variance": 0.002,
            "std_variance": 0.0001, "feasible_rate_percent": 100,
            "mean_runtime_seconds": 12.5,
            "best_weights_json": json.dumps([0.25, 0.75]),
        })
    with (folder / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("seed", "target_return"))
        writer.writeheader()
        writer.writerow({"seed": 0, "target_return": 0.006})
    if complete:
        (folder / "complete.json").write_text('{"status":"complete"}', encoding="utf-8")
    return folder


def _read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
    
# =============================================================================
# END AI-ASSISTED SECTION
# =============================================================================

def test_builds_one_row_per_completed_case(tmp_path):
    cases = tmp_path / "full"
    _case(cases, dataset="port2", alpha="0.75", variant="ten_comma_seventy")
    _case(cases, dataset="port1", alpha="0.50", variant="ten_plus_seventy")
    _case(cases, dataset="port1", alpha="0.25", variant="one_plus_one")
    _case(cases, dataset="port3", alpha="0.25", complete=False)
    out = tmp_path / "es_summary_45_cases.csv"
    assert build_summary.build_summary(cases, out) == 3
    rows = _read(out)
    assert len(rows) == 3
    assert set(rows[0]) == SUMMARY_COLUMNS
    assert [(r["dataset"], r["alpha"], r["variant"]) for r in rows] == [
        ("port1", "0.25", "one_plus_one"),
        ("port1", "0.50", "ten_plus_seventy"),
        ("port2", "0.75", "ten_comma_seventy"),
    ]


def test_values_match_the_case_summary_files(tmp_path):
    cases = tmp_path / "full"
    _case(cases, best=0.00037)
    rows = build_summary.build_summary(cases, tmp_path / "result.csv")
    assert rows == 1
    record = _read(tmp_path / "result.csv")[0]
    assert record["num_assets"] == "2"
    assert record["target_return"] == "0.006"
    assert record["evaluations_per_run"] == "30000"
    assert float(record["best_variance"]) == pytest.approx(0.00037)
    assert float(record["mean_variance"]) == pytest.approx(0.002)
    assert float(record["std_variance"]) == pytest.approx(0.0001)
    assert float(record["mean_runtime_seconds"]) == pytest.approx(12.5)


def test_missing_or_empty_results_are_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="Missing ES cases"):
        build_summary.build_summary(tmp_path / "absent", tmp_path / "output.csv")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError, match="No completed"):
        build_summary.build_summary(empty, tmp_path / "output.csv")
    folder = _case(empty)
    (folder / "runs.csv").unlink()
    with pytest.raises(FileNotFoundError, match="runs.csv"):
        build_summary.build_summary(empty, tmp_path / "output.csv")
    assert not (tmp_path / "output.csv").exists()


def test_full_export_writes_the_consolidated_summary(tmp_path, monkeypatch):
    """End-to-end full-mode integration using preexisting completed exports."""
    root = tmp_path / "exports"
    cases = root / "full"
    for dataset in export_experiments.PORTFOLIOS:
        for alpha in export_experiments.ALPHAS:
            for variant in export_experiments.VARIANTS:
                folder = _case(cases, dataset, str(alpha), variant)
                (folder / "convergence.csv").write_text("test\n", encoding="utf-8")
                (folder / "run_histories.csv").write_text("test\n", encoding="utf-8")


    # =====================================================================
    # BEGIN AI-ASSISTED SECTION
    # Purpose: Verify that completed experiments are not rerun.
    # =====================================================================

    def must_not_optimize(**kwargs):
        pytest.fail("Unexpected optimization of already-complete experiment")

    monkeypatch.setattr(
        export_experiments, "summarize_case", must_not_optimize
    )
    monkeypatch.setattr(sys, "argv", [
        "export_experiments", "--output", str(root),
    ])

    export_experiments.main()

    rows = _read(root / build_summary.SUMMARY_NAME)
    assert len(rows) == 45
    assert set(rows[0]) == SUMMARY_COLUMNS

    # =====================================================================
    # END AI-ASSISTED SECTION
    # =====================================================================