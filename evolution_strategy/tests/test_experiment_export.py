"""Regression tests for the ES experiment CSV exporter."""

import csv
import json
import sys

import pytest

from evolution_strategy import export_experiments
from evolution_strategy.results import PORTFOLIOS, summarize_case


@pytest.fixture
def sample_summary():
    """Create a small real-data experiment for testing."""
    return summarize_case(
        dataset_name="port1",
        portfolio=PORTFOLIOS["port1"],
        alpha=0.50,
        variant="one_plus_one",
        num_runs=2,
        max_iterations=83,
    )


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_export_creates_correct_files(tmp_path, sample_summary):
    """Check saved statistics, seeds, histories and metadata."""
    folder = tmp_path / "test_case"

    export_experiments.export_case(
        sample_summary, folder, budget=83
    )

    assert (folder / "summary.csv").exists()
    assert (folder / "runs.csv").exists()
    assert (folder / "convergence.csv").exists()
    assert (folder / "complete.json").exists()

    summary_rows = read_csv(folder / "summary.csv")
    assert len(summary_rows) == 1

    assert float(
        summary_rows[0]["mean_variance"]
    ) == pytest.approx(sample_summary.mean_cost)

    runs = read_csv(folder / "runs.csv")
    assert len(runs) == 2
    assert [int(row["seed"]) for row in runs] == [0, 1]
    assert all(int(row["evaluations"]) == 83 for row in runs)
    assert all(
        len(json.loads(row["weights_json"])) == 31
        for row in runs
    )

    convergence = read_csv(folder / "convergence.csv")
    assert len(convergence) == 83
    assert int(convergence[0]["evaluation"]) == 1
    assert int(convergence[-1]["evaluation"]) == 83

    metadata = json.loads(
        (folder / "complete.json").read_text(encoding="utf-8")
    )

    assert metadata["status"] == "complete"
    assert metadata["num_runs"] == 2
    assert metadata["evaluations_per_run"] == 83


def test_export_rejects_incorrect_budget(tmp_path, sample_summary):
    """Do not mark an incomplete run as completed."""
    folder = tmp_path / "invalid_case"

    with pytest.raises(ValueError):
        export_experiments.export_case(
            sample_summary, folder, budget=100
        )

    assert not (folder / "complete.json").exists()

def test_completed_cases_are_skipped(tmp_path, monkeypatch, capsys):
    """A repeated smoke run should not recompute completed cases."""
    for variant in export_experiments.VARIANTS:
        name = f"port1_alpha050_{variant}_e83_r2"
        folder = tmp_path / "smoke" / name
        folder.mkdir(parents=True)

        (folder / "complete.json").write_text(
            '{"status": "complete"}', encoding="utf-8"
        )

        for filename in (
            "summary.csv",
            "runs.csv",
            "convergence.csv",
            "run_histories.csv",
        ):
            (folder / filename).write_text(
                "test data", encoding="utf-8"
            )

    def should_not_run(**kwargs):
        pytest.fail("Completed case was unexpectedly recomputed")

    monkeypatch.setattr(
        export_experiments, "summarize_case", should_not_run
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export_experiments",
            "--mode",
            "smoke",
            "--output",
            str(tmp_path),
        ],
    )

    export_experiments.main()

    captured = capsys.readouterr()
    assert captured.out.count("SKIP:") == 3
