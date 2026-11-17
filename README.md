
# ACIT4610 - Evolutionary Artificial Intelligence and Robotics
**Fall 2026 group project | Group 7**

This repository contains two independent optimization subprojects for the ACIT4610 final group assignment. Code and documentation are separated so each problem can be reviewed and reproduced independently.

| Problem | Directory | Focus |
|---|---|---|
| Problem 1 | [`bees_algorithm/`](bees_algorithm/) | Bees Algorithm for symmetric TSP and continuous benchmark functions |
| Problem 2 | [`evolution_strategy/`](evolution_strategy/) | Constrained minimum-variance portfolio optimization using Evolution Strategies |

## Problem 1: Bees Algorithm

The Bees Algorithm subproject addresses symmetric Travelling Salesman Problem instances and continuous function optimization. Its code and documentation are maintained in [`bees_algorithm/`](bees_algorithm/); see [`bees_algorithm/README.md`](bees_algorithm/README.md) for the current implementation details and instructions.

## Repository layout

```text
.
├── bees_algorithm/                # Problem 1 (team-maintained)
├── evolution_strategy/            # Problem 2 ES code, datasets, tests, exporters and plots
├── main.py
├── logger.py
├── requirements.txt
└── README.md
```

## Problem 2: Evolution Strategies

The portfolio project compares **(1+1)-ES, (10+70)-ES, and (10,70)-ES** on five OR-Library portfolio datasets, each at three required-return targets. Its experimental protocol uses 10 seeds and 30,000 objective evaluations per algorithm/case, producing 45 case summaries and 450 individual runs.

For algorithms, feasibility repair, input datasets, parameters, reproducibility, CSV schemas, figures, and tests, see **[`evolution_strategy/README.md`](evolution_strategy/README.md)**.

**Latest locally verified ES results:** 45/45 completed experimental cases, 450/450 saved run records, a 45-row consolidated summary, 18 full figure pairs (PNG and PDF), and 50 passing automated tests. These describe the Evolution Strategies subproject only.

Useful commands, executed from this repository root:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m evolution_strategy.export_experiments --mode smoke
python -u -m evolution_strategy.export_experiments --mode full
python -m evolution_strategy.plot_results --mode full --dataset port5 --alpha 0.50
python -m evolution_strategy.plot_comparisons
```

The `plot_comparisons` command reads existing files in `../es_experiment_results/` by default, including individual `runs.csv` files for the boxplot. Plotting **does not rerun optimization**. The full exporter is expensive: it runs the 450-run experiment grid only when expected output files are missing.


## Versioned report outputs and raw experiment files

The following **small, final report artifacts are tracked in Git**:

- [`evolution_strategy/report_data/es_summary_45_cases.csv`](evolution_strategy/report_data/es_summary_45_cases.csv) — consolidated results for all 45 cases.
- [`evolution_strategy/figures/`](evolution_strategy/figures/) — 18 full figure pairs (PNG and PDF): 15 convergence plots plus 3 comparisons.
- [`evolution_strategy/plot_results.py`](evolution_strategy/plot_results.py) and [`evolution_strategy/plot_comparisons.py`](evolution_strategy/plot_comparisons.py) — scripts to reproduce figures from saved outputs.

The complete raw run-level evidence stays in a **separate local sibling directory**, `../es_experiment_results/full/` (45 case folders, each with `runs.csv`, `run_histories.csv`, and case metadata). **Git does not include those raw histories.** Preserve a backup and provide them separately with the final submission. See the ES README for exact commands and formats.

The Bees Algorithm and ES have different datasets and experiment protocols and should be reported separately. 
