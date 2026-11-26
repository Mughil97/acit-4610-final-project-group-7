# Evolution Strategies Experiment Results

This directory stores all raw per-run outputs, evaluation-by-evaluation convergence logs, figures, and the consolidated 45-case summary table for **Problem 2 (Evolution Strategies)**.

## Directory Layout

```text
results/
├── es_summary_45_cases.csv     # Consolidated 45-case statistics (5 datasets × 3 alphas × 3 variants)
├── figures/                    # 15 convergence PNGs + 3 comparison plots (PNG + PDF)
└── full/                       # 45 completed case directories (450 seeded runs)
    └── <dataset>_alpha<alpha>_<variant>_e30000_r10/
        ├── summary.csv         # Case-level variance/feasibility/runtime summary & best weight vector
        ├── runs.csv            # All 10 per-seed outcomes (seeds 0..9) including full weight vectors
        ├── convergence.csv     # Mean archive best-so-far variance across 30,000 evaluations
        ├── run_histories.csv   # Evaluation-by-evaluation archive best-so-far variance per seed
        └── complete.json       # Case completion metadata
```

## Auditing and Regenerating Outputs (Without Rerunning Optimization)

Run from the repository root:

```bash
python -m evolution_strategy.audit_results
python -m evolution_strategy.build_summary
python -m evolution_strategy.plot_results --dataset port5 --alpha 0.50
python -m evolution_strategy.plot_comparisons
```
