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

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -u -m evolution_strategy.export_experiments
python -m evolution_strategy.audit_results
python -m evolution_strategy.build_summary
python -m evolution_strategy.plot_results --dataset port5 --alpha 0.50
python -m evolution_strategy.plot_comparisons
```

All post-processing commands read the committed raw case outputs and `es_summary_45_cases.csv` from `evolution_strategy/results/` by default (mirroring `bees_algorithm/results/`). Plots, summaries, and audits do **not** rerun the optimization. Matplotlib is required for plotting; install with `python -m pip install -r requirements.txt`.

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

Raw ES per-run results (`runs.csv`), evaluation-by-evaluation convergence logs (`convergence.csv`, `run_histories.csv`), consolidated summary (`es_summary_45_cases.csv`), and validation report (`validation_report.json`) are stored inside the repository under **`evolution_strategy/results/`**, mirroring **`bees_algorithm/results/`**. Every audit, summary, and plotting script runs out of the box after cloning.

The two subprojects have different experimental designs and should be interpreted and reported separately. No claim is made here that Bees Algorithm experiments have been completed or validated.
