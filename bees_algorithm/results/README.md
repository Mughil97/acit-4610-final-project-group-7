# Bees Algorithm Experiment Results

This directory stores all raw per-run outputs, evaluation-by-evaluation convergence histories, summary tables, run metadata, and generated figures for **Problem 1 (Bees Algorithm)** — covering both **Part A (TSP)** and **Part B (Continuous Function Optimization)**.

## Directory Layout

```text
results/
├── metadata.json                           # Environment versions, BA hyperparameters, seeds (45..54), and TSPLIB optima
├── part_a_tsp/                             # Part A: Discrete Route Planning (6 instances × 2 neighbourhoods × 10 seeds = 120 runs)
│   ├── raw/
│   │   ├── runs.csv                        # All 120 per-seed outcomes including tour lengths, gaps, validity, and tours
│   │   └── solutions.json                  # Best valid tour per instance and neighbourhood
│   ├── histories/
│   │   └── <instance>_<neighbourhood>.csv  # 12 files: best-so-far tour length across 30,000 evaluations per seed
│   ├── tables/
│   │   ├── summary_tsp.csv                 # Aggregated case statistics (best, mean, std, mean gap %, mean runtime)
│   │   └── summary_tsp.md                  # Markdown summary table
│   └── figures/
│       ├── convergence_berlin52.png        # SWAP vs REVERSE mean convergence on berlin52
│       ├── convergence_ch150.png           # SWAP vs REVERSE mean convergence on ch150
│       └── best_route_berlin52.png         # Best valid berlin52 tour plot
└── part_b_continuous/                      # Part B: Continuous Function Optimization (4 functions × 2 dimensions × 10 seeds = 80 runs)
    ├── raw/
    │   ├── runs.csv                        # All 80 per-seed outcomes including objective values, validity, and vectors
    │   └── solutions.json                  # Best valid solution vector per function and dimension
    ├── histories/
    │   └── <function>_D<dimension>.csv     # 8 files: best-so-far objective value across 30,000 evaluations per seed
    ├── tables/
    │   ├── summary_continuous.csv          # Aggregated case statistics (best, mean, std, mean runtime)
    │   └── summary_continuous.md           # Markdown summary table
    └── figures/
        ├── convergence_rastrigin_D10.png   # Mean convergence on Rastrigin (D=10)
        └── boxplots_D30.png                # Final objective value boxplots across all 4 functions (D=30)
```

## Regenerating Outputs (Without Rerunning Optimization)

Run from the repository root:

```bash
python -m bees_algorithm.utils.summarizer
python -m bees_algorithm.utils.plotting
python generate_tex_tables.py
```
