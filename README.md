# ACIT4610 - Evolutionary Artificial Intelligence and Robotics

**Fall 2026 group project | Group 7**

This repository contains two independent optimization subprojects for the ACIT4610 final group assignment. Code and documentation are separated so each problem can be reviewed and reproduced independently.

| Problem | Directory | Focus |
|---|---|---|
| Problem 1 | [`bees_algorithm/`](bees_algorithm/) | Bees Algorithm for symmetric TSP and continuous benchmark functions |
| Problem 2 | [`evolution_strategy/`](evolution_strategy/) | Constrained minimum-variance portfolio optimization using Evolution Strategies |

## Running the Complete Project

To run both Problem 1 (Bees Algorithm) and Problem 2 (Evolution Strategies) end-to-end and automatically generate all raw results, summary tables, and figures:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python main.py
```

## Problem 1: Bees Algorithm

The Bees Algorithm subproject addresses symmetric Travelling Salesman Problem instances and continuous function optimization. See **[`bees_algorithm/README.md`](bees_algorithm/README.md)** for full details and settings.

```bash
# One TSP run / one continuous run (30,000 evaluations)
python -m bees_algorithm.optimise --instance berlin52 --neighbourhood REVERSE --seed 45
python -m bees_algorithm.optimise --function rastrigin --dimension 10 --seed 45

# Full Problem 1 set (all runs, summary tables, and figures)
python -m bees_algorithm.optimise
```

## Problem 2: Evolution Strategies

The portfolio project compares **(1+1)-ES, (10+70)-ES, and (10,70)-ES** on five OR-Library portfolio datasets, each at three required-return targets. Its experimental protocol uses 10 seeds and 30,000 objective evaluations per algorithm/case, producing 45 case summaries and 450 individual runs.

For algorithms, feasibility repair, inputs, parameters, reproducibility, tests, figures, and the CSV schema, see **[`evolution_strategy/README.md`](evolution_strategy/README.md)**.

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

All post-processing commands read the committed raw case outputs and `es_summary_45_cases.csv` from `evolution_strategy/results/` by default (mirroring `bees_algorithm/results/`). Plots and summaries do **not** rerun the optimization. Matplotlib is required for plotting; install with `python -m pip install -r requirements.txt`.

## Generating LaTeX Report Tables (Optional)

To generate standalone LaTeX tables for both Problem 1 (BA) and Problem 2 (ES) from the saved summary CSVs:

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

## Experimental files and collaboration

Raw ES per-run results (`runs.csv`), evaluation-by-evaluation convergence logs (`convergence.csv`, `run_histories.csv`), and the consolidated summary (`es_summary_45_cases.csv`) are stored inside the repository under `evolution_strategy/results/`.

After installing the required dependencies, the summary and plotting scripts can use the committed experimental results without rerunning the optimization.
