# Evolution Strategies Experiment Results

This directory stores all raw per-run outputs, evaluation-by-evaluation convergence logs, the consolidated 45-case summary table, and generated figures for **Problem 2 (Evolution Strategies)**.

## Directory Layout

```text
results/
├── es_summary_45_cases.csv     # Consolidated 45-case statistics (5 datasets × 3 alphas × 3 variants)
├── figures/                    # Convergence and comparison figures (PNG/PDF)
└── <dataset>_alpha<alpha>_<variant>_e30000_r10/  # 45 completed case directories (450 seeded runs)
    ├── summary.csv             # Case-level variance/feasibility/runtime summary & best weight vector
    ├── runs.csv                # All 10 per-seed outcomes (seeds 0..9) including full weight vectors
    ├── convergence.csv         # Mean archive best-so-far variance across 30,000 evaluations
    ├── run_histories.csv       # Evaluation-by-evaluation archive best-so-far variance per seed
    └── complete.json           # Case completion metadata
```

## Regenerating Outputs (Without Rerunning Optimization)

Run from the repository root:

```bash
python -m evolution_strategy.build_summary
python -m evolution_strategy.plot_results
python generate_tex_tables.py
```
