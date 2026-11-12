"""Regression tests for CSV-only reporting; no optimization is rerun."""

import csv
from pathlib import Path

import pytest

from evolution_strategy import plot_comparisons
from evolution_strategy.plot_comparisons import (
    ALPHAS, DATASETS, VARIANTS, load_seed_variances, load_summary,
    plot_boxplot, plot_mean_variance, plot_runtime,
)


@pytest.fixture
def summary_fixture(tmp_path):
    result_root = tmp_path / "results"
    result_root.mkdir()
    path = result_root / "es_summary_45_cases.csv"
    fields = [
        "dataset", "alpha", "variant", "num_assets", "target_return", "num_runs",
        "evaluations_per_run", "best_variance", "mean_variance", "std_variance",
        "feasible_rate_percent", "mean_runtime_seconds",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for ds_index, dataset in enumerate(DATASETS):
            for alpha in ALPHAS:
                for variant in VARIANTS:
                    writer.writerow({
                        "dataset": dataset, "alpha": alpha, "variant": variant,
                        "num_assets": (31, 85, 89, 98, 225)[ds_index],
                        "target_return": 0.01, "num_runs": 10,
                        "evaluations_per_run": 30000,
                        "best_variance": 0.001, "mean_variance": 0.001,
                        "std_variance": 0.0, "feasible_rate_percent": 100.0,
                        "mean_runtime_seconds": 1.25,
                    })
    return result_root


def test_45_cases_and_summary_plots(summary_fixture):
    summary = load_summary(summary_fixture / "es_summary_45_cases.csv")
    assert len(summary) == 45
    figs = summary_fixture / "figures"
    plot_mean_variance(summary, figs)
    plot_runtime(summary, figs)
    for name in ("mean_variance_by_dataset_full", "runtime_by_dataset_full"):
        assert (figs / f"{name}.png").stat().st_size > 1000
        assert (figs / f"{name}.pdf").stat().st_size > 1000


def test_boxplot_uses_real_per_seed_rows(summary_fixture, monkeypatch):
    summary = load_summary(summary_fixture / "es_summary_45_cases.csv")
    for variant in VARIANTS:
        case_dir = summary_fixture / "full" / f"port5_alpha050_{variant}_e30000_r10"
        case_dir.mkdir(parents=True)
        with (case_dir / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "seed", "final_variance", "feasible", "evaluations"
            ])
            writer.writeheader()
            for seed in range(10):
                writer.writerow({"seed": seed, "final_variance": 0.001,
                                 "feasible": True, "evaluations": 30000})
    values = load_seed_variances(summary_fixture, summary, "port5", 0.5)
    assert values["one_plus_one"] == [0.001] * 10
    original_save = plot_comparisons._save

    def check_annotations_then_save(fig, figures_dir, filename):
        ax = fig.axes[0]
        assert ax.get_xlabel() == "Evolution Strategy variant"
        assert "Final portfolio variance" in ax.get_ylabel()
        assert len(fig.legends) == 1
        entries = [item.get_text() for item in fig.legends[0].get_texts()]
        assert entries == [
            "Box: 25th–75th percentile", "Median (line)",
            "Mean (diamond)", "Individual seed (dot)",
        ]
        return original_save(fig, figures_dir, filename)

    monkeypatch.setattr(plot_comparisons, "_save", check_annotations_then_save)
    plot_boxplot(summary, summary_fixture, summary_fixture / "figures", "port5", 0.5)
    assert (summary_fixture / "figures" / "boxplot_port5_alpha050_full.png").is_file()
    assert (summary_fixture / "figures" / "boxplot_port5_alpha050_full.pdf").is_file()


def test_missing_seed_csv_is_not_fabricated(summary_fixture):
    summary = load_summary(summary_fixture / "es_summary_45_cases.csv")
    with pytest.raises(FileNotFoundError, match="actual per-seed"):
        load_seed_variances(summary_fixture, summary, "port5", 0.5)
