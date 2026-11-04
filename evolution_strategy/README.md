# ACIT4610 — Final Portfolio 2026, Problem 2: Evolution Strategies

**Group 7 | Portfolio optimization using Evolution Strategies**

This repository folder implements **Problem 2** of the ACIT4610 Evolutionary Artificial Intelligence and Robotics Final Group Project 2026. It compares three Evolution Strategies (ES) for minimizing portfolio variance subject to budget, non-negativity, and minimum expected-return constraints.

The implementation follows the **Portfolio 2026 assignment, pages 8–12**, with Lecture 2 and Lab 2 used as algorithmic references. Where the lab demonstration differs from the assignment, the assignment specification takes precedence.

## 1. Problem formulation

For a portfolio of `n` assets, the allocation vector `w` contains the fraction of the investment budget assigned to each asset. Using asset mean returns `r`, standard deviations `s`, and correlations `C`, the covariance matrix is constructed as

`Sigma[i,j] = s[i] * s[j] * C[i,j]`.

The objective is to **minimize portfolio variance**:

`V(w) = w.T @ Sigma @ w`

subject to:

- `w[i] >= 0` for every asset;
- `sum(w) = 1`;
- `R(w) = r.T @ w >= R_min`.

Variance, not standard deviation, is the objective used for optimization and reporting. All returns are represented as decimals (for example, `0.02` for 2%).

For each dataset, the minimum required return is defined by

`R_min(alpha) = (1 - alpha) * R_eq + alpha * r_max`,

where `R_eq` is the expected return under equal allocation, `r_max` is the largest individual asset mean return, and `alpha` is one of `0.25`, `0.50`, or `0.75`.


## 2. Datasets and Test Cases

### 2.1 Benchmark Datasets

The experiments use five portfolio optimization benchmark datasets from J. E. Beasley's OR-Library. Each dataset provides asset mean returns, standard deviations, and pairwise correlations.

**Official source:** [OR-Library — Portfolio Selection](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html)

| Dataset | Assets (n) | Correlation Records |
|---|---:|---:|
| `port1.txt` | 31 | 496 |
| `port2.txt` | 85 | 3,655 |
| `port3.txt` | 89 | 4,005 |
| `port4.txt` | 98 | 4,851 |
| `port5.txt` | 225 | 25,425 |

**Original dataset files:**

- [port1.txt](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port1.txt)
- [port2.txt](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port2.txt)
- [port3.txt](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port3.txt)
- [port4.txt](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port4.txt)
- [port5.txt](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port5.txt)

The original files are stored in `problem2_es/data/or_library/` and retained for reproducibility.

### 2.2 Data Loading and Covariance Construction

The portfolio parser reads:

1. The number of assets, `n`, from the first line.
2. The mean return and standard deviation of each asset from the next `n` lines.
3. The remaining pairwise correlation records.

Asset indices in the OR-Library files begin at 1 and are converted to Python's zero-based indexing. Correlations are stored symmetrically, such that `C[i,j] = C[j,i]`.

The covariance matrix is constructed as:

`Sigma[i,j] = s[i] * s[j] * C[i,j]`

where `s` represents the vector of asset standard deviations and `C` is the correlation matrix.

### 2.3 Return-Target Settings

For each dataset, three minimum-return targets are evaluated using `alpha = 0.25`, `0.50`, and `0.75`.

The required return is calculated as:

`R_min(alpha) = (1 - alpha) * R_eq + alpha * r_max`

where:

- `R_eq` is the expected return of an equally weighted portfolio.
- `r_max` is the highest individual asset mean return.
- `alpha` determines the required return level.

Combining five datasets with three return-target settings produces **15 benchmark cases**, identified from `port1_alpha025` through `port5_alpha075`.

### 2.4 Parser Validation

The `port1.txt` dataset is used to verify data loading and portfolio calculations against the reference values provided in the project specification.

| Validation Checkpoint | Expected Approximate Value |
|---|---:|
| Equal-allocation return | `0.003504064516129` |
| Equal-allocation variance | `0.001130937943724` |
| Target return (`alpha = 0.50`) | `0.007184532258065` |

All three reference values were reproduced using the original `port1.txt` dataset.

Validation is implemented in `problem2_es/src/portfolio.py`.


## 3. Evolution Strategies Implementations

Three Evolution Strategies (ES) variants are implemented for constrained portfolio optimization. Each candidate solution is represented by a real-valued vector containing the portfolio allocation weights.

The implementation follows the ES principles covered in ACIT4610 Lecture 2 and Lab 2, with algorithm-specific settings defined by the Portfolio 2026 project specification.

### 3.1 Common Initialization and Constraint Handling

Initial portfolio weights are sampled independently from a uniform distribution over `[0, 1]`.

Each candidate is repaired before objective evaluation using two operations:

**Step 1 — Simplex Projection**

Project the candidate onto the probability simplex to ensure:

- All allocation weights are nonnegative.
- The sum of the allocation weights equals 1.

**Step 2 — Minimum-Return Repair**

If the projected portfolio does not satisfy the required return, it is blended toward the asset with the highest individual expected return.

The blending coefficient is:

`beta = (R_min - R(q)) / (r_max - R(q))`

The repaired portfolio is:

`w = (1 - beta) * q + beta * e_j`

where `e_j` assigns the entire portfolio weight to the maximum-return asset.

Final solutions are validated using the specified numerical tolerance of `1e-8`.

### 3.2 Single-Parent (1+1)-ES

The (1+1)-ES maintains one parent and generates one mutated offspring per iteration.

**Algorithm parameters:**

- Parent population: 1
- Offspring per iteration: 1
- Initial step size: `0.1 / sqrt(n)`
- Step-size bounds: `[1e-8, 1.0]`

Gaussian mutation is applied independently to each coordinate using the scalar mutation step size.

The child replaces the parent only when its portfolio variance is strictly lower.

The mutation step size is updated after each trial:

- Successful mutation: `sigma *= exp(1/3)`
- Unsuccessful mutation: `sigma *= exp(-1/12)`

The updated step size is restricted to the specified bounds.

### 3.3 Population-Based Evolution Strategies

Two population-based ES variants are implemented:

| Variant | Parents (mu) | Offspring (lambda) | Survivor Selection |
|---|---:|---:|---|
| (10+70)-ES | 10 | 70 | Best 10 from parents and offspring |
| (10,70)-ES | 10 | 70 | Best 10 offspring only |

Both use the same initialization, recombination, self-adaptation, and mutation operators.

**Parent Selection**

Two distinct parents are selected uniformly at random from the current population.

**Weight Recombination**

The offspring's initial weight vector is obtained using intermediate recombination:

`w_r = (w_parent1 + w_parent2) / 2`

**Step-Size Recombination**

Strategy parameters are combined using the geometric mean:

`sigma_r = sqrt(sigma_parent1 * sigma_parent2)`

These operations are applied coordinate-wise.

**Self-Adaptive Mutation**

The recombined step-size vector is updated using:

`sigma_new[i] = sigma_r[i] * exp(tau_prime * Z0 + tau * Zi)`

where:

- `tau_prime = 1 / sqrt(2*n)`
- `tau = 1 / sqrt(2*sqrt(n))`
- `Z0` is one standard normal draw shared across the child's coordinates.
- `Zi` is an independent standard normal draw for each coordinate.

Updated step sizes are clamped to `[1e-8, 1.0]`.

After step-size adaptation, fresh independent Gaussian noise is added to the recombined weight vector. The resulting candidate is repaired before portfolio variance evaluation.

### 3.4 Survivor Selection

**(10+70)-ES — Elitist Selection**

Parents and offspring are combined, and the 10 candidates with the lowest portfolio variance are retained.

**(10,70)-ES — Non-Elitist Selection**

Only offspring participate in survivor selection. The 10 offspring with the lowest portfolio variance form the next parent population.

### 3.5 Best-So-Far Archive

All three ES variants maintain a separate archive containing the best feasible portfolio allocation discovered during the run.

The archive is updated whenever a strictly better feasible solution is evaluated, including during initialization and offspring evaluation.

For (10,70)-ES, the archive is used only for reporting and does not participate in parent or survivor selection.

The best archived solution is returned at the end of each run.

## 4. Evaluation protocol

The same cases, feasibility repair, and seed list are used for all three algorithms:

- **15 cases × 3 variants × 10 seeds = 450 independent runs**;
- **30,000 objective evaluations per run**, including initialization and all evaluated children;
- Seed list: `0 1 2 3 4 5 6 7 8 9`;
- For population ES, a complete generation produces 70 offspring. The final generation may be partial to stop exactly at the evaluation budget (30 offspring after 428 complete generations at the default budget).

Each run records the best feasible allocation, expected return, final variance, runtime, and per-evaluation best-so-far history. Summary statistics use **feasible runs** for variance calculations and include the number of feasible runs out of 10; mean runtime is calculated across all 10 runs. Lower variance is better **within the same dataset and return target**.


## 5. Requirements and Installation

### 5.1 Software Requirements

The project uses Python 3.10 or later and the following dependencies:

| Package | Required Version | Purpose |
|---|---|---|
| NumPy | `>=1.26,<3` | Numerical operations and matrix calculations |
| Matplotlib | `>=3.8,<4` | Experimental result visualization |
| pytest | `>=8,<10` | Automated testing |

All dependencies are declared in `requirements.txt`.

### 5.2 Installation

Run the following commands from the project root directory containing `requirements.txt`.

**Windows — PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 5.3 Environment Reproducibility

Record the Python version and exact installed dependencies using:

```bash
python --version
python -m pip freeze > environment-lock.txt
```

The generated `environment-lock.txt` records the package versions used in the active environment.

The `.venv` directory is excluded from version control.

### 5.4 Automated Tests

Run the automated test suite:

```bash
python -m pytest -q
```

The project includes 35 tests covering portfolio calculations, data loading, constraint handling, Evolution Strategies, and experiment utilities.

### 5.5 Smoke Test

Run a synthetic test of the three ES variants:

```bash
python -m problem2_es.experiments.smoke_test
```

This test verifies basic execution without using the official benchmark datasets.

The complete benchmark commands are provided in Section 6.

## 6. Reproducing the experiments

The original dataset files are already included in the supplied project. To obtain them again from the official source, run:

```bash
python -m problem2_es.experiments.download_data
```

If downloading is unavailable, place the unmodified `port1.txt` through `port5.txt` files in `problem2_es/data/or_library/`.

**One official case, one seed, all variants** (saved separately from the completed results):

```bash
python -m problem2_es.experiments.run_portfolio --case port1_alpha050 --variant all --seeds 0 --budget 30000 --out problem2_es/results/verification_port1
```

**Full official experiment set:**

```bash
python -m problem2_es.experiments.run_portfolio --case all --variant all --seeds 0 1 2 3 4 5 6 7 8 9 --budget 30000
```

The runner reuses existing results where the matching CSV record and raw `.npz` file exist. Use `--force` only when an experiment intentionally needs to be repeated. Input file SHA-256 hashes are recorded to prevent mixing results from changed datasets.

## 7. Results and figures

The submitted project snapshot contains **450 run records**, **45 summary rows**, all **450 compressed raw archives**, and **31 PNG figures** (one required figure plus 30 supplementary figures). Every recorded run used 30,000 evaluations and was marked feasible. The stored allocations and histories have also been validated against the supplied benchmark data.

| Output | Location | Description |
| --- | --- | --- |
| Individual run results | `problem2_es/results/runs.csv` | Case, variant, seed, target, variance, return, runtime, feasibility, evaluation count |
| Aggregate summary | `problem2_es/results/summary.csv` | One row per case and ES variant: best, mean, standard deviation, feasible-run rate, mean runtime |
| Complete raw archives | `problem2_es/results/raw/` | Best weights, all 30,000 archive-best values, evaluation indices, run metadata |
| Readable CSV exports | `problem2_es/results/readable/` | Allocation weights, sampled convergence histories, run diagnostics |
| **Required convergence figure** | `problem2_es/figures/port5_alpha050_convergence.png` | Mean archive-best variance against evaluation count for `port5_alpha050`; all three ES variants, 10 seeds each |
| Supplementary figures | `problem2_es/figures/additional/` | 15 case-level convergence figures, five boxplots, five target-comparison plots, three allocation plots, a relative-performance heatmap, and a runtime comparison |

Regenerate figures and validate saved archives without repeating optimization:

```bash
python -m problem2_es.experiments.visualize_all
python -m problem2_es.experiments.plot_portfolio
```

The `.npz` files preserve full-resolution histories and allocations. CSV exports are provided for easier review in VS Code or spreadsheet applications. See [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md) for plot definitions, interpretation guidance, and chart locations.

The relative-performance heatmap uses the **lowest mean variance among the three tested ES variants within each case** as the reference. Its `0%` values do **not** mean zero investment risk or a proven globally optimal portfolio. Historical asset statistics do not establish future investment performance.

## 8. Repository structure

```text
.
├── README.md
├── PROJECT_STATUS.md
├── VISUALIZATION_GUIDE.md
├── requirements.txt
├── pyproject.toml
├── problem2_es/
│   ├── data/or_library/        # Original portfolio datasets
│   ├── src/
│   │   ├── portfolio.py        # Parser, portfolio model, feasibility repair
│   │   └── evolution_strategies.py  # ES variants and evaluation archive
│   ├── experiments/
│   │   ├── download_data.py
│   │   ├── run_portfolio.py
│   │   ├── smoke_test.py
│   │   ├── plot_portfolio.py
│   │   └── visualize_all.py
│   ├── results/                # CSV summaries, raw NPZ, readable exports
│   └── figures/                # Required and supplementary PNG figures
└── tests/
```

Do not commit or submit local virtual environments, Python caches, or pytest cache files. Keep the **original datasets, raw per-run archives, summary tables, and reproducible figures** as required by the assignment.

## 9. Validation and limitations

Automated tests cover the core ES operations, data loading, objective calculations, feasibility repair, and experiment logic. The saved results were checked for the required case/seed combinations, the exact evaluation budget, portfolio feasibility, matching return and variance values, and non-increasing archive-best histories.

These checks establish internal consistency and feasibility, not global optimality. Since the algorithms are stochastic, individual runs vary. Comparisons should consider mean variance, variability, convergence, runtime, and the difference between elitist and non-elitist survivor selection. Report interpretation and discussion are separate deliverables.


## 10. Code Provenance and AI Use

The implementation follows the Evolution Strategies concepts presented in ACIT4610 Lecture 2 and Lab 2, together with the requirements defined in the Portfolio 2026 project specification.

Generative AI tools contributed to the development of the project-specific Python implementations, automated tests, experiment utilities, and visualizations. AI-generated code is identified in the relevant source files.

The final project report will document the AI tools used, their purpose, and the approximate percentage of AI-generated code in the submitted implementation.

This repository component covers Problem 2 — Evolution Strategies. The complete group submission also includes Problem 1 — Bees Algorithm and the combined project report.

The written final report will be produced by the group in accordance with the assignment's prohibition on AI-written report text.

## References

- **ACIT4610 Portfolio 2026**, Final Group Project, Problem 2, pp. 8–12 (primary implementation and evaluation specification).
- **ACIT4610 Lecture 2 / Lab 2**, Evolution Strategies (course algorithmic references).
- **J. E. Beasley, OR-Library**, [Portfolio selection datasets and file format](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html).
