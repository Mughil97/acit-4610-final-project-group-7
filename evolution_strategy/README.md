# Problem 2: Portfolio optimization with Evolution Strategies

ACIT4610 Evolutionary Artificial Intelligence and Robotics, Fall 2026, Group 7.

This package implements and evaluates three continuous Evolution Strategy (ES) variants for long-only minimum-variance portfolio optimization with a required expected return. Run all commands from the repository root (the directory containing `evolution_strategy/`).

## Problem formulation

The covariance matrix is constructed once when each dataset is loaded:

$$
\Sigma_{ij} = s_i s_j \rho_{ij}
$$

The portfolio variance is then calculated as $V(\mathbf{w}) = \mathbf{w}^{T}\Sigma\mathbf{w}$.

The implementation stores and reuses the symmetric covariance matrix during objective evaluations. Portfolio weights and covariance calculations use Python lists rather than NumPy arrays.

A candidate solution is a vector of asset weights $\mathbf{w} = (w_1, \ldots, w_n)$. We minimize portfolio variance:

$$
V(\mathbf{w}) =
\sum_{i=1}^{n} w_i^2 s_i^2
+ 2\sum_{i=1}^{n}\sum_{j=i+1}^{n}
w_i w_j s_i s_j \rho_{ij}
$$

subject to non-negative weights, full budget allocation, and a minimum expected return:

$$
w_i \geq 0, \qquad
\sum_{i=1}^{n} w_i = 1, \qquad
R(\mathbf{w}) = \sum_{i=1}^{n} w_i r_i \geq R^*
$$

Here $r_i$ is the expected return of asset $i$, $s_i$ is its standard deviation, and $\rho_{ij}$ is the correlation between assets $i$ and $j$. Target returns are set for $\alpha \in \{0.25, 0.50, 0.75\}$:

$$
R^* = (1 - \alpha) R_{\mathrm{eq}} + \alpha R_{\max}
$$

where $R_{\mathrm{eq}}$ is the return of an equally weighted portfolio and $R_{\max}$ is the highest individual asset return.

## Datasets and exploratory analysis

Official dataset source:
[OR-Library Portfolio Optimization](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html).

The original benchmark files are included in
`evolution_strategy/data/`.

The five OR-Library benchmark files in `evolution_strategy/data/` contain weekly stock data from five equity indices:

| Dataset | Market index | Assets ($n$) | Correlation records | Negative-return assets | $R_{\mathrm{eq}}$ | $R_{\max}$ | Equal-weight variance | Mean pairwise corr. |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `port1.txt` | Hang Seng (Hong Kong) | 31 | 496 | 0 / 31 | 0.350% | 1.087% | 0.001131 | 0.527 |
| `port2.txt` | DAX 100 (Germany) | 85 | 3,655 | 20 / 85 | 0.149% | 0.979% | 0.000265 | 0.207 |
| `port3.txt` | FTSE 100 (UK) | 89 | 4,005 | 4 / 89 | 0.266% | 0.821% | 0.000303 | 0.248 |
| `port4.txt` | S&P 100 (USA) | 98 | 4,851 | 8 / 98 | 0.287% | 0.919% | 0.000208 | 0.163 |
| `port5.txt` | Nikkei 225 (Japan) | 225 | 25,425 | 177 / 225 | -0.151% | 0.397% | 0.000942 | 0.476 |

### Assignment parser validation

The `port1.txt` dataset was validated against the reference
values provided in Portfolio 2026, Problem 2, page 10.

| Validation | Expected | Verified |
|---|---:|---:|
| Equal-allocation return | 0.003504064516129 | 0.003504064516129 |
| Equal-allocation variance | 0.001130937943724 | 0.001130937943724 |
| Target return (alpha = 0.50) | 0.007184532258065 | 0.007184532258065 |

These checks are included in `tests/test_covariance.py`.
In `port1`, the single safest company (Stock #29) has variance `0.001285`, whereas splitting capital evenly across all 31 stocks lowers variance to `0.001131`. That equal split still misses higher return targets because its return is only `0.350%`. Across markets, `port2`, `port3`, and `port4` have much lower average pairwise correlations (`0.163` to `0.248`) than `port1` (`0.527`) and `port5` (`0.476`), so combining stocks cancels more variance there. `port5` also behaves differently on returns: 177 of its 225 stocks have negative weekly mean returns, pulling $R_{\mathrm{eq}}$ to `-0.151%` and leaving the $\alpha = 0.25$ target slightly negative (`-0.014%`).

On `port1` at $\alpha = 0.50$ ($R^* = 0.7185\%$), putting 100% into the highest-return asset (Stock #5) is feasible with variance `0.004776`, and a 50/50 blend of equal-weight and Stock #5 lowers variance to `0.002066`. Running the population ES variants for 30,000 evaluations brings mean variance down to `0.001171` at the same return target.

## Algorithms and constraint repair

All three ES variants are implemented in `algorithms.py` and exposed through `run_es()` in `evolution_strategies.py`:

| Variant | Algorithm | Survivor selection |
|---|---|---|
| `one_plus_one` | (1+1)-ES | Replace parent with offspring only on strictly lower variance |
| `ten_plus_seventy` | (10+70)-ES | Keep the best 10 from 10 parents and 70 offspring |
| `ten_comma_seventy` | (10,70)-ES | Keep the best 10 from the 70 offspring only |

`(1+1)-ES` starts from one repaired random portfolio with Gaussian step size `sigma = 0.1 / sqrt(n)`. After each evaluated child, `sigma` is multiplied by `exp(1/3)` on a strict improvement and by `exp(-1/12)` otherwise, clamped to `[1e-8, 1.0]`. Initialization counts as one objective evaluation.

`(10+70)-ES` and `(10,70)-ES` maintain 10 parents and generate up to 70 offspring per generation, shrinking the final batch if needed to stop at the exact evaluation budget. Each offspring picks two distinct parents at random, averages their weights, and takes the geometric mean of their per-asset step sizes. Step sizes are then mutated log-normally using `tau_prime = 1 / sqrt(2n)` and `tau = 1 / sqrt(2 sqrt(n))` (clamped to `[1e-8, 1.0]`), and weights are perturbed with Gaussian noise. All three variants track a best-so-far archive of feasible repaired portfolios, so recorded convergence curves never rise even for `(10,70)-ES`, where the current parent population can worsen between generations.

Before any initial or mutated candidate is evaluated, `repair.py` restores feasibility in two steps. First it projects the raw vector onto the Euclidean simplex ($w_i \geq 0$, $\sum_i w_i = 1$). Then, if $R(\mathbf{w}) < R^*$, it blends $\mathbf{w}$ with a unit weight on the highest-return asset using the smallest mixing fraction that hits $R^*$. Final feasibility is checked to tolerance `1e-8` on non-negativity, unit sum, and target return.

All initial weight coordinates are independently sampled
from a uniform distribution in [0, 1] before repair.

The population variants initialize every coordinate's
step size to `0.1 / sqrt(n)`. Each offspring uses one shared
standard-normal draw for global step-size adaptation,
independent coordinate-specific draws, and fresh independent
Gaussian draws for weight mutation.

In (10,70)-ES, the best-so-far archive is used for reporting
only and does not participate in parent or survivor selection.

## Running the code

### Validated execution environment

| Component | Tested version |
|---|---|
| Operating system | Windows |
| Python | 3.13.5 |
| Matplotlib | 3.11.2 |
| NumPy | 2.5.5 |
| pytest | 9.2.0 |

NumPy is installed as a plotting dependency. The ES
optimization algorithms use standard Python lists.

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pytest evolution_strategy/tests -v
```

The ES regression tests cover simplex projection,
target-return repair, (1+1)-ES step-size adaptation,
evaluation budgets, covariance construction, assignment
reference values, independent variance calculations,
CSV export, summary building, and plotting.

Latest validation:

- ES regression suite: 87 passed.
- Covariance regression suite: 33 passed.
- Overall project regression suite: 124 passed.

### Full pipeline via `main.py`

Running the root entry point executes both Problem 1 (Bees Algorithm) and Problem 2 (Evolution Strategies):

```bash
python main.py
```

For Problem 2, `main.py` calls `optimise_es()`, `summarize_all_es()`, and `generate_all_plots_es()`. Completed folders under `evolution_strategy/results/full/` are skipped automatically, so repeated runs do not recompute finished cases.

### Individual commands

Experiments, summary building, and auditing:

```bash
# Single seeded run
python -c "from evolution_strategy.results import PORTFOLIOS; from evolution_strategy.evolution_strategies import run_es; r = run_es(PORTFOLIOS['port1'], alpha=0.50, variant='one_plus_one', max_iterations=30000, seed=0); print('feasible=', r.is_valid, 'evaluations=', len(r.history), 'variance=', r.cost)"

# Complete port1_alpha050 case for (1+1)-ES, 10 seeds
python -c "from evolution_strategy.results import PORTFOLIOS, summarize_case; r = summarize_case('port1', PORTFOLIOS['port1'], 0.50, 'one_plus_one', num_runs=10, max_iterations=30000); print(r.best_cost, r.mean_cost, r.std_cost, r.feasible_rate, r.mean_runtime)"

# Full 45-case export (skips completed cases)
python -u -m evolution_strategy.export_experiments

# Fresh full experiment using a new, unused output directory
python -u -m evolution_strategy.export_experiments --output evolution_strategy/results_covariance

# Rebuild the consolidated summary from saved cases
python -m evolution_strategy.build_summary

# Audit the existing 45 cases and 450 runs
python -m evolution_strategy.audit_results
```

The default experiment directory contains the existing
recorded experiments. Completed cases are skipped when
all required output files exist.

Use a new, unused output directory when reproducing
experiments with a modified implementation. Existing
completion markers do not verify the source-code
revision that generated the results.

Generating figures without rerunning optimization:

```bash
# Single convergence plot (e.g. port5, alpha=0.50)
python -m evolution_strategy.plot_results --dataset port5 --alpha 0.50

# Comparison plots (mean variance, runtime, and port5 alpha=0.50 boxplot; PNG + PDF)
python -m evolution_strategy.plot_comparisons

# Dataset correlation matrix and pairwise-correlation boxplot (reads data/ only)
python -m evolution_strategy.plot_datasets

# All convergence, comparison, and dataset plots in one call
python -c "from evolution_strategy.plot_results import generate_all_plots_es; generate_all_plots_es()"
```

`plot_comparisons` also accepts `--summary-only` (generates the first two plots from `es_summary_45_cases.csv` without per-seed `runs.csv` files) and `--results-dir path/to/results`.

## Experimental protocol and saved outputs

| Setting | Value |
|---|---|
| Datasets | 5 (`port1` to `port5`) |
| Return targets ($\alpha$) | `0.25`, `0.50`, `0.75` |
| ES variants | 3 (`one_plus_one`, `ten_plus_seventy`, `ten_comma_seventy`) |
| Seeds per case | `0` through `9` (10 independent runs via `random.seed(seed)`) |
| Budget per seed | `30,000` objective evaluations (`max_iterations` counts evaluations, including initialization and rejected offspring) |
| Totals | 45 cases, 450 runs, 13,500,000 objective evaluations |

`results.py` summarizes each 10-run case using best variance,
mean variance, population standard deviation (denominator `N`),
feasible-run percentage, mean runtime, and the mean archive
convergence curve.

Variance statistics are calculated over valid runs only,
while mean runtime is calculated across all ten runs.

Raw outputs and report artifacts are stored inside the repository:

```text
evolution_strategy/
├── data/
│   ├── port1.txt
│   ├── port2.txt
│   ├── port3.txt
│   ├── port4.txt
│   └── port5.txt
├── figures/
├── results/
│   ├── es_summary_45_cases.csv
│   ├── validation_report.json     # Generated by audit
│   └── full/
│       └── <case_name>/
│           ├── summary.csv
│           ├── runs.csv
│           ├── convergence.csv
│           ├── run_histories.csv
│           └── complete.json
└── tests/                     # Regression tests
```

## Module overview

| Module | Role |
|---|---|
| `portfolio.py` | Load OR-Library datasets and construct covariance matrices |
| `evaluation.py` | Expected return, cached covariance-based variance, and target-return calculations |
| `repair.py` | Euclidean simplex projection and target-return mixing |
| `algorithms.py` | `(1+1)-ES`, `(10+70)-ES`, and `(10,70)-ES` with best-so-far archive |
| `evolution_strategies.py` | Single-seed runner, runtime tracking, and feasibility check |
| `results.py` | 10-seed case summarization, mean convergence history, default paths |
| `export_experiments.py` | Resumable 45-case runner (`optimise_es`) and atomic CSV exporter |
| `build_summary.py` | Consolidated 45-case summary builder (`summarize_all_es`) |
| `audit_results.py` | Integrity audit over all 45 cases, 450 runs, and 13.5M evaluations |
| `plot_results.py` | Convergence plots and unified plot entry point (`generate_all_plots_es`) |
| `plot_comparisons.py` | Mean-variance, runtime, and per-seed boxplot comparisons |
| `plot_datasets.py` | Dataset correlation matrix and pairwise-correlation boxplot |

## Experimental results provenance

The existing 450-run experimental dataset was committed
in revision `8768729`, before the covariance precomputation
improvement in revision `173116b`.

The Git revision identifies when the results were committed,
but the exact original execution environment and generating
source revision have not been independently established.

Subsequent implementation validation included:

- 500 numerical objective comparisons.
- 45 seeded comparisons at 1,000 evaluations.
- Nine representative runs at 30,000 evaluations.
- 33 permanent covariance regression tests.
- 87 passing ES regression tests.
- Independent auditing of all 450 stored experimental runs.

The nine full-budget checks covered port1, port3, and port5
at alpha = 0.50, seed 0, using all three ES variants.
All nine reproduced the recorded final variance within
numerical tolerance, satisfied feasibility constraints,
and completed exactly 30,000 evaluations.

The stored runtime measurements belong to the historical
experiments. They must not be interpreted as new runtime
measurements of the updated covariance implementation.

The targeted reproducibility checks do not constitute
a complete rerun of all 450 experiments.


## Summary of results and caveats

Across the 45 cases in `results/es_summary_45_cases.csv`, all 450 runs are 100% feasible. Both population strategies reach lower mean final variance than `(1+1)-ES` in all 15 dataset/alpha combinations: `(10+70)-ES` is lowest in 8 of 15 cases and `(10,70)-ES` in 7 of 15. `(1+1)-ES` finishes fastest in all 15 cases, taking about 1.4 s per run on `port1` and 48 to 50 s on `port5`, compared with 1.8 to 1.9 s and 51 to 55 s for the population variants.

Because asset sets and return targets change across datasets and $\alpha$ levels, compare variance only within the same `(dataset, alpha)` case. Runtimes depend on hardware and load, and the 8 vs. 7 split between `(10+70)-ES` and `(10,70)-ES` is descriptive only, with no formal significance test attached.
