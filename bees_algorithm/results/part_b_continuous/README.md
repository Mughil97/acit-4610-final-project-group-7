# Part B Results — Continuous Function Optimisation

This folder contains the outputs from **80 independent Bees Algorithm runs** across 4 benchmark functions (`sphere`, `rosenbrock`, `rastrigin`, `ackley`), 2 dimensions (`D = 10` and `D = 30`), and 10 seeds (`45–54`), each with a budget of **30,000 objective evaluations**. All 4 functions have a known global minimum of `0.0`.

## Folder Contents

### `raw/` — Per-Run Data
- **`runs.csv`** (80 data rows): One row per `(function, dimension, seed)` run:
  - `function`: Benchmark function name (`sphere`, `rosenbrock`, `rastrigin`, `ackley`).
  - `dimension`: Number of decision variables ($D \in \{10, 30\}$).
  - `lower` / `upper`: Search space bounds per coordinate (`[-5.12, 5.12]` for Sphere/Rastrigin, `[-5, 10]` for Rosenbrock, `[-32.768, 32.768]` for Ackley).
  - `global_minimum`: Known theoretical global minimum (`0.0`).
  - `run_idx` / `seed`: Run index (`1–10`) and RNG seed (`45–54`).
  - `evaluations`: Total objective evaluations used (capped at `30000`).
  - `initial_best`: Lowest objective value among the initial `ns = 30` random scouts.
  - `final_best`: Lowest objective value found by evaluation `30000` (equals objective error since $f^* = 0$).
  - `runtime_sec`: Wall-clock runtime of the run in seconds.
  - `is_valid` / `validation_errors`: Post-run check verifying vector dimension, finiteness, bounds adherence, and objective value consistency.
  - `solution`: JSON-encoded final best real-valued vector of length $D$.
- **`solutions.json`**: Structured JSON copy of all 80 runs with full coordinate vectors keyed by `<function>__D<dimension>__seed_<seed>`.

### `histories/` — Best-So-Far Convergence Logs
- **`<function>_D<dimension>.csv`** (8 files):
  - `30,000` rows (`evaluation = 1..30000`) and 10 seed columns (`seed_45` through `seed_54`).
  - Each cell is the best-so-far objective value achieved up to that evaluation for that seed (monotonically non-increasing).

### `tables/` — Aggregated Statistics
- **`summary_continuous.csv`** & **`summary_continuous.md`** (8 rows):
  - Groups runs by `(function, dimension)` and reports `Valid Runs`, `Best` (min `final_best`), `Mean`, `Std` (sample standard deviation, `ddof=1`), and `Mean Runtime (s)` (plus `mean_initial_best` in the CSV).

### `figures/` — Plots
- **`convergence_rastrigin_D10.png`**: Mean best-so-far objective across 10 runs vs. evaluations for `Rastrigin` at `D = 10` (with any axis transformation explicitly labeled on the Y-axis).
- **`boxplots_D30.png`**: Four-panel figure displaying boxplots (with individual run points overlaid) of the 10 final objective values at `D = 30` for `Sphere`, `Rosenbrock`, `Rastrigin`, and `Ackley`.
