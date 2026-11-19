# Bees Algorithm Experiment Results

This directory stores all raw outputs, convergence histories, summary tables, and figures generated for **Problem 1 (Bees Algorithm)**.

## Directory Layout

```text
results/
├── metadata.json          # BA parameters, seed list (45–54), Python/library versions, TSPLIB optima
├── part_a_tsp/            # Part A: Symmetric Travelling Salesman Problem (120 runs)
│   ├── raw/               # Per-run scalar metrics (runs.csv) and full tour permutations (solutions.json)
│   ├── histories/         # Evaluation-by-evaluation best-so-far curves (30,000 evals × 10 seeds)
│   ├── tables/            # Aggregated statistics across 10 seeds (CSV & Markdown)
│   └── figures/           # Convergence curves and best berlin52 route plot
└── part_b_continuous/     # Part B: Continuous Function Optimisation (80 runs)
    ├── raw/               # Per-run scalar metrics (runs.csv) and full solution vectors (solutions.json)
    ├── histories/         # Evaluation-by-evaluation best-so-far curves (30,000 evals × 10 seeds)
    ├── tables/            # Aggregated statistics across 10 seeds (CSV & Markdown)
    └── figures/           # Rastrigin D=10 convergence curve and D=30 4-panel boxplots
```

## File Descriptions

- **`metadata.json`**: Records the exact `TSPConfig` and `FunctionOptimisationConfig` parameters (`max_evaluations = 30000`, `ns = 30`, `ne = 3`, `nb = 10`, `nre = 15`, `nrb = 5`, `stlim = 100`, `shrink_factor = 0.2`), the 10 seeds (`45..54`), package versions, and TSPLIB reference optima.
- **[`part_a_tsp/README.md`](part_a_tsp/README.md)**: Detailed guide to all Part A (TSP) data files, columns, metrics, tables, and plots.
- **[`part_b_continuous/README.md`](part_b_continuous/README.md)**: Detailed guide to all Part B (Continuous) data files, columns, metrics, tables, and plots.

## Regenerating Tables and Figures

To recompute `tables/` and `figures/` from the saved `raw/` and `histories/` data without re-running the optimizer:

```bash
python bees_algorithm/utils/summarizer.py
python bees_algorithm/utils/plotting.py
```
