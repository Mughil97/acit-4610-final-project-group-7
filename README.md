# ACIT4610 - Evolutionary Artificial Intelligence and Robotics

**Fall 2026 group project | Group 7**

This repository contains two independent optimization subprojects for the ACIT4610 final group assignment. Code and documentation are separated so each problem can be reviewed and reproduced independently.

| Problem | Directory | Focus | Results |
|---|---|---|---|
| Problem 1 | [`bees_algorithm/`](bees_algorithm/) | Bees Algorithm for symmetric TSP and continuous benchmark functions | [`bees_algorithm/results/`](bees_algorithm/results/README.md) |
| Problem 2 | [`evolution_strategy/`](evolution_strategy/) | Constrained minimum-variance portfolio optimization using Evolution Strategies | [`evolution_strategy/results/`](evolution_strategy/results/README.md) |

## Running the Complete Project

Requires **Python 3.10+** (`requirements.txt` uses compatible lower bounds so evaluators on Python 3.10–3.14 can install without upgrading). Validated on **Python `3.14.6`** with `numpy 2.5.5`, `matplotlib 3.11.2`, and `pytest 9.2.0`.

To run both Problem 1 (Bees Algorithm) and Problem 2 (Evolution Strategies) end-to-end and automatically regenerate all raw results, summary tables, and figures:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python main.py
```

## Problem 1: Bees Algorithm

The Bees Algorithm subproject addresses symmetric Travelling Salesman Problem instances and continuous function optimization. See **[`bees_algorithm/README.md`](bees_algorithm/README.md)** for full details and settings, and **[`bees_algorithm/results/README.md`](bees_algorithm/results/README.md)** for saved outputs (summary tables, raw runs, histories, and figures).

```bash
# One TSP run / one continuous run (30,000 evaluations)
python -m bees_algorithm.optimise --instance berlin52 --neighbourhood REVERSE --seed 45
python -m bees_algorithm.optimise --function rastrigin --dimension 10 --seed 45

# Full Problem 1 set (all runs, summary tables, and figures)
python -m bees_algorithm.optimise
```

## Problem 2: Evolution Strategies

The portfolio project compares **(1+1)-ES, (10+70)-ES, and (10,70)-ES** on five OR-Library portfolio datasets, each at three required-return targets. Its experimental protocol uses 10 seeds and 30,000 objective evaluations per algorithm/case, producing 45 case summaries and 450 individual runs.

For algorithms, feasibility repair, inputs, parameters, reproducibility, tests, and commands, see **[`evolution_strategy/README.md`](evolution_strategy/README.md)**. For saved outputs, summary CSV, and figures, see **[`evolution_strategy/results/README.md`](evolution_strategy/results/README.md)**.

```bash
# One single run / one complete test case (all 3 ES variants × 10 seeds)
python -m evolution_strategy.optimise --dataset port1 --alpha 0.50 --variant one_plus_one --seed 0
python -m evolution_strategy.optimise --dataset port1 --alpha 0.50

# Full Problem 2 set (all 45 cases, summary CSV, and figures)
python -u -m evolution_strategy.optimise

# Regenerate summary CSV and plots from saved results (no optimization rerun)
python -m evolution_strategy.build_summary
python -m evolution_strategy.plot_results
```

All post-processing commands read the committed raw case outputs and [`es_summary_45_cases.csv`](evolution_strategy/results/es_summary_45_cases.csv) from `evolution_strategy/results/` by default (mirroring `bees_algorithm/results/`). Plots and summaries do **not** rerun the optimization. Matplotlib is required for plotting; install with `python -m pip install -r requirements.txt`.

## Generating LaTeX Report Tables (Optional)

To generate standalone LaTeX report tables for both Problem 1 (BA) and Problem 2 (ES) from the saved summary CSVs:

```bash
python generate_tex_tables.py
```

Generated `.tex` files are written to `tex_tables/` in the repository root (gitignored).

## Repository layout

```text
.
├── bees_algorithm/                # Problem 1 (Bees Algorithm)
├── evolution_strategy/            # Problem 2 (Evolution Strategies)
├── generate_tex_tables.py         # Standalone LaTeX table generator (BA + ES)
├── main.py
├── logger.py
├── requirements.txt
└── README.md
```

## Saved Experimental Outputs

All raw per-run outputs, evaluation-by-evaluation convergence logs, summary tables, and figures are committed directly in the repository:

- **Problem 1 (BA):** [`bees_algorithm/results/README.md`](bees_algorithm/results/README.md) · [`summary_tsp.md`](bees_algorithm/results/part_a_tsp/tables/summary_tsp.md) · [`summary_continuous.md`](bees_algorithm/results/part_b_continuous/tables/summary_continuous.md)
- **Problem 2 (ES):** [`evolution_strategy/results/README.md`](evolution_strategy/results/README.md) · [`es_summary_45_cases.csv`](evolution_strategy/results/es_summary_45_cases.csv)
