# ACIT4610 - Evolutionary Artificial Intelligence and Robotics

**Fall 2026 group project | Group 7**

This repository contains two independent optimization subprojects for the ACIT4610 final group assignment. Code and documentation are separated so each problem can be reviewed and reproduced independently.

| Problem | Directory | Focus |
|---|---|---|
| Problem 1 | [`bees_algorithm/`](bees_algorithm/) | Bees Algorithm for symmetric TSP and continuous benchmark functions |
| Problem 2 | [`evolution_strategy/`](evolution_strategy/) | Constrained minimum-variance portfolio optimization using Evolution Strategies |

## Problem 2: Evolution Strategies

The portfolio project compares **(1+1)-ES, (10+70)-ES, and (10,70)-ES** on five OR-Library portfolio datasets, each at three required-return targets. Its experimental protocol uses 10 seeds and 30,000 objective evaluations per algorithm/case, producing 45 case summaries and 450 individual runs.

For algorithms, feasibility repair, inputs, parameters, reproducibility, tests, figures, and the CSV schema, see **[`evolution_strategy/README.md`](evolution_strategy/README.md)**.

Useful commands, executed from this repository root:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m evolution_strategy.export_experiments --mode smoke
python -u -m evolution_strategy.export_experiments --mode full
python -m evolution_strategy.plot_results --mode full --dataset port5 --alpha 0.50
python -m evolution_strategy.plot_comparisons
```

The `plot_comparisons` command expects the completed case outputs and `es_summary_45_cases.csv` in `../es_experiment_results/` by default. Plots do **not** rerun the optimization. Matplotlib is required for plotting; install with `python -m pip install matplotlib` if needed.

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

## Experimental files and collaboration

Raw ES results and generated figures are stored by default in **`../es_experiment_results/`**, outside the source worktree. This keeps large histories separate from code changes. Back up or share that folder separately; Git commits/pull requests of the source alone do not carry the generated results.

The two subprojects have different experimental designs and should be interpreted and reported separately. No claim is made here that Bees Algorithm experiments have been completed or validated.
