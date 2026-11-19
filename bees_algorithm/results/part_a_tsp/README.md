# Part A Results — Discrete Route Planning (Symmetric TSP)

This folder contains the outputs from **120 independent Bees Algorithm runs** across 6 TSPLIB instances (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`, `ch150`), 2 neighbourhood operators (`SWAP`, `REVERSE`), and 10 seeds (`45–54`), each with a budget of **30,000 objective evaluations**.

## Folder Contents

### `raw/` — Per-Run Data
- **`runs.csv`** (120 data rows): One row per `(instance, neighbourhood, seed)` run:
  - `instance`: TSPLIB instance name (`eil51`, `berlin52`, `st70`, `eil76`, `kroA100`, `ch150`).
  - `cities`: Number of cities $n$.
  - `optimum`: Known TSPLIB optimal tour length $L^*$ (`426`, `7542`, `675`, `538`, `21282`, `6528`).
  - `neighbourhood`: Move operator (`SWAP` or `REVERSE`).
  - `run_idx` / `seed`: Run index (`1–10`) and RNG seed (`45–54`).
  - `evaluations`: Total objective evaluations used (capped at `30000`).
  - `initial_best`: Shortest tour length among the initial `ns = 30` random scouts.
  - `final_best`: Shortest valid tour length $L_{BA}$ found by evaluation `30000`.
  - `gap_pct`: Percentage optimality gap, $\text{Gap}(\%) = 100 \cdot \frac{L_{BA} - L^*}{L^*}$.
  - `runtime_sec`: Wall-clock runtime of the run in seconds.
  - `is_valid` / `validation_errors`: Result of post-run permutation and TSPLIB rounded-Euclidean length verification (`True` = visits every city once, starts at city `1`, includes return leg).
  - `solution`: JSON-encoded final best city permutation starting at city `1`.
- **`solutions.json`**: Structured JSON copy of all 120 runs with full tour permutations keyed by `<instance>__<neighbourhood>__seed_<seed>`.

### `histories/` — Best-So-Far Convergence Logs
- **`<instance>_<neighbourhood>.csv`** (12 files):
  - `30,000` rows (`evaluation = 1..30000`) and 10 seed columns (`seed_45` through `seed_54`).
  - Each cell is the best-so-far tour length achieved up to that evaluation for that seed (monotonically non-increasing).

### `tables/` — Aggregated Statistics
- **`summary_tsp.csv`** & **`summary_tsp.md`** (12 rows):
  - Groups runs by `(instance, cities, optimum, neighbourhood)` and reports `Valid Runs`, `Best` (min $L_{BA}$), `Mean` ($\bar{L}_{BA}$), `Std` (sample standard deviation, `ddof=1`), `Mean Gap (%)`, and `Mean Runtime (s)` (plus `mean_initial_best` in the CSV).

### `figures/` — Plots
- **`convergence_berlin52.png`**: Mean best-so-far tour length (±1 std shaded) vs. evaluations across 10 runs for `SWAP` and `REVERSE` on `berlin52`, with the optimum $L^* = 7{,}542$ marked.
- **`convergence_ch150.png`**: Mean best-so-far tour length (±1 std shaded) vs. evaluations across 10 runs for `SWAP` and `REVERSE` on `ch150`, with the optimum $L^* = 6{,}528$ marked.
- **`best_route_berlin52.png`**: Plot of the single shortest valid `berlin52` tour found across all 20 runs (`SWAP` + `REVERSE`), highlighting City `1` as the start, drawing the explicit return leg, and labeling neighbourhood, seed, tour length, and gap (%).
