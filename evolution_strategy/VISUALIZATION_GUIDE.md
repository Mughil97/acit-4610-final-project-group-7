# Visualization Guide — Portfolio Optimization with Evolution Strategies

This guide describes the figures and exported data produced for **Problem 2** of the ACIT4610 Final Portfolio 2026. It explains the plotted quantities, how to compare algorithms, and how to regenerate the figures from saved runs. For installation, optimization settings, datasets, and full experiment commands, see [README.md](README.md).

## 1. Scope and figure inventory

The assignment requires **one** convergence figure for `port5_alpha050`: mean archive-best portfolio variance versus the number of objective evaluations, averaged across 10 independent seeds and showing all three ES variants on the same axes. The project also generates 30 supplementary figures for interpreting the complete experiment set.

| Figure group | Count | Location under `problem2_es/figures/` | Purpose |
| --- | ---: | --- | --- |
| **Required convergence** | **1** | `port5_alpha050_convergence.png` | Assignment-required three-method comparison |
| Supplementary convergence | 15 | `additional/convergence/` | One convergence comparison per dataset–target case |
| Across-seed boxplots | 5 | `additional/boxplots/` | Distribution of final variance across seeds |
| Variance versus return-target level | 5 | `additional/variance_vs_target/` | Sensitivity to the required-return setting within each dataset |
| Largest allocation weights | 3 | `additional/best_allocations/` | Selected portfolio's largest asset weights |
| Relative-performance heatmap | 1 | `additional/overview_relative_variance.png` | Comparison of mean variance within each case |
| Runtime comparison | 1 | `additional/overview_mean_runtime.png` | Recorded computational time by dataset |
| **Total** | **31** | | One mandatory and 30 supplementary figures |

The ES variants are consistently labeled **(1+1)-ES**, **(10+70)-ES**, and **(10,70)-ES**. Their plot colors are blue, orange, and bluish green, respectively, except for the heatmap, which uses a sequential blue scale to encode relative variance rather than algorithm identity.

The supplementary figures support exploratory analysis and interpretation of the experimental results. They are not  additional mandatory deliverables required by the assignment.


## 2. Quantities and Comparison Rules

### 2.1 Portfolio Optimization Metrics

The primary performance metric is the final best feasible portfolio variance. Portfolio variance is calculated as:

`V(w) = w.T @ Sigma @ w`

where `w` is the allocation-weight vector and `Sigma` is the covariance matrix.

Lower variance indicates a better solution when comparing algorithms on the same dataset and minimum-return target.

The following quantities are used throughout the experiments and visualizations:

- **Portfolio variance:** The risk objective minimized by the ES algorithms. It is expressed in squared decimal-return units (`return²`), not as a percentage return or standard deviation.
- **Expected portfolio return:** The weighted sum of individual asset returns, calculated as `R(w) = r.T @ w`.
- **Minimum-return target:** The required return threshold calculated using `R_min = (1 - alpha) * R_eq + alpha * r_max`.
- **Archive-best variance:** The lowest feasible portfolio variance discovered up to a given objective evaluation.
- **Runtime:** The elapsed computation time for one optimization run, recorded in seconds.

The minimum-return target level `alpha` takes the values `0.25`, `0.50`, and `0.75`. These values control the return constraint and do not represent portfolio returns of 25%, 50%, or 75%.

### 2.2 Experimental Protocol

All three ES variants are evaluated under identical experimental conditions:

| Parameter | Setting |
|---|---|
| Benchmark datasets | 5 OR-Library portfolios |
| Return-target levels | 0.25, 0.50, 0.75 |
| Total test cases | 15 |
| ES variants | (1+1)-ES, (10+70)-ES, (10,70)-ES |
| Independent runs per case and variant | 10 |
| Random seeds | 0–9 |
| Objective evaluations per run | 30,000 |
| Total experimental runs | 450 |

All ES variants use the same datasets, return targets, feasibility-repair procedure, random seed list, and evaluation budget.

Initialization and every evaluated offspring, including rejected candidates, contribute to the evaluation count.

For population-based ES, the final offspring batch may contain fewer than 70 offspring to remain within the exact 30,000-evaluation budget. These offspring are included when updating the best-so-far archive.


### 2.3 Summary Statistics and Feasibility Reporting

The experimental summary contains 45 rows, representing
15 portfolio cases evaluated using three ES variants.

For each portfolio case and ES variant, the summary
table reports the following information:


| Metric | CSV Column | Description |
|---|---|---|
| Case name | `case` | Dataset and return-target identifier, e.g., `port1_alpha050`. |
| Number of assets | `n` | Number of assets in the portfolio dataset. |
| Target return | `target` | Minimum required expected portfolio return. |
| Best variance | `best_variance` | Lowest final archive-best feasible variance across valid runs. |
| Mean variance | `mean_variance` | Average final best feasible variance across valid runs. |
| Standard deviation | `std_variance` | Standard deviation of final best feasible variance across valid runs. |
| Total runs | `runs` | Total independent runs for the case and ES variant. |
| Valid runs | `valid_runs` | Number of runs producing feasible final allocations. |
| Feasible-run rate | `feasible_run_rate` | Percentage of runs producing feasible final allocations. |
| Mean runtime | `mean_runtime_seconds` | Average runtime across all ten runs, in seconds. |


The standard deviation is calculated as the sample standard
deviation of final best feasible variances across valid runs
(using n − 1 in the denominator). Feasible-run rate is
expressed as a percentage of the total independent runs.


Each individual run also records the best feasible
allocation, achieved expected return, final portfolio
variance, runtime, random seed, and evaluation count.

A final allocation is considered feasible when:

- Each allocation weight is at least `-1e-8`.
- The absolute deviation of the weight sum from 1 is at most `1e-8`.
- The expected portfolio return is at least `R_min - 1e-8`.

Variance statistics are calculated using valid runs only.
Mean runtime includes all ten runs.

The complete summary is stored in:

`problem2_es/results/summary.csv`

Individual run information is stored in:

`problem2_es/results/runs.csv`


### 2.4 Convergence and Best-So-Far Tracking

Convergence is evaluated using the best feasible portfolio variance recorded after each objective evaluation.

All three ES variants maintain a separate best-so-far archive.

The archive is updated whenever a strictly better feasible solution is evaluated, including during initialization and offspring evaluation.

Because the archive retains the best solution discovered so far, its recorded variance cannot increase.

For (10,70)-ES, the current population's best variance may worsen because parents are excluded from survivor selection. However, the archive-best variance remains unchanged unless a better solution is found.

The convergence plots report the mean archive-best variance across ten independent runs at each evaluation count.

A decreasing curve indicates improvement, while a flat region indicates that no better archived solution was discovered during that interval. A flat curve does not establish that the global optimum has been reached.

### 2.5 Fair Comparison and Interpretation

Performance comparisons should be made between ES variants evaluated on the same dataset and minimum-return target.

The following principles apply:

- Lower mean variance indicates better average observed solution quality.
- Lower standard deviation indicates greater consistency across independent runs.
- Faster convergence indicates earlier improvement within the evaluation budget.
- Lower runtime indicates lower recorded computational cost under the execution conditions.
- A feasible-run rate of 100% indicates that all reported final allocations satisfied the specified constraints.

Portfolio variances across different datasets should not be interpreted as direct evidence that one algorithm is superior, because the datasets contain different asset universes and covariance structures.

Likewise, the lowest variance observed among the three tested ES variants is not necessarily the mathematically optimal portfolio variance.

The benchmark results describe optimization performance using historical asset statistics. They do not establish future investment performance or guarantee global optimality.


## 3. How to interpret each figure

### 3.1 Required convergence: `port5_alpha050_convergence.png`

**X-axis:** Number of objective function evaluations, from 0 to 30,000 on the displayed axis. Recorded objective evaluations begin at **1**; there is no measured result at evaluation 0.

**Y-axis:** Mean archive-best portfolio variance (`return²`), averaged pointwise across 10 seeds per ES variant. The axis is displayed from zero.

Each curve shows how quickly an algorithm discovers better feasible allocations. A falling curve indicates improvement in the mean best-so-far solution. A flat segment indicates no improvement to the archive over that interval, **not** proof of an optimum. The figure is generated from complete per-evaluation histories, not the sampled CSV export.

Generated by `problem2_es/experiments/plot_portfolio.py`.

### 3.2 Additional convergence plots (15)

**Files:** `additional/convergence/<case>_convergence.png`.

Each figure compares the same three ES variants for one of the 15 dataset–target cases. Each curve is the pointwise mean archive-best variance of 10 runs. For plotting efficiency, these supplementary curves are sampled from the complete saved histories; the start and final evaluation are retained.

Use these figures to inspect early improvement, late-stage progress, and stagnation under the same evaluation budget. They support comparisons **within a case**, not claims that a method has reached the true optimum.

### 3.3 Across-seed boxplots (5)

**Files:** `additional/boxplots/port1_variance_boxplot.png` through `port5_variance_boxplot.png`.

For each dataset, the chart groups results by target `alpha` and ES variant. Each box summarizes **10 final archive-best variances**. The median line, interquartile range, whiskers, and any outlier points show how results vary between random seeds.

Lower medians indicate lower typical observed variance; narrow boxes indicate more consistent results. Differences between `alpha` groups reflect **different return constraints**. Assess algorithm consistency within the same dataset and `alpha`.


The box extends from the first quartile (Q1) to the third quartile (Q3), with the median shown inside. Whiskers extend to the most extreme observations within 1.5 × IQR of the quartiles. Observations beyond the whiskers are displayed as potential outliers.


### 3.4 Variance versus return-target level (5)

**Files:** `additional/variance_vs_target/port1_mean_variance_vs_alpha.png` through `port5_mean_variance_vs_alpha.png`.

**X-axis:** `alpha`, with observations at `0.25`, `0.50`, and `0.75`. A tick at `0.00` is an axis reference **without experimental data**.

**Y-axis:** Mean final feasible variance (`return²`) across 10 runs.

These plots show how the achieved variance changes as the required-return threshold becomes stricter. Connecting the three observations is a visual aid; **no additional target levels were evaluated**. These are separate constrained single-objective optimization problems, **not** a Pareto front generated by a multi-objective optimizer.

### 3.5 Relative-performance heatmap (1)

**File:** `additional/overview_relative_variance.png`.

For each case, the reference value is the **smallest mean final variance among the three tested ES variants for that case**. The displayed excess percentage is:

`Excess (%) = 100 * (mean_variance / lowest_case_mean_variance - 1)`

A `0.0%` cell marks a method tied for the lowest observed mean at the displayed precision. It **does not** mean zero portfolio risk or a proven global optimum. Very small positive values can appear as `<0.1%` to avoid misleading rounding.

The five sequential blue bands are:

| Excess above the best observed mean | Meaning |
| --- | --- |
| `0%` | Lowest observed mean in that case |
| `>0–5%` | Small excess variance |
| `>5–20%` | Moderate excess variance |
| `>20–50%` | Higher excess variance |
| `>50%` | Largest excess variance band |

**Darker blue indicates greater excess variance.** Cell annotations give the actual calculated percentages more precisely than the five color bands. Read values within each row; do not infer that the darkest cells have the greatest absolute portfolio variance across all datasets.

### 3.6 Runtime comparison (1)

**File:** `additional/overview_mean_runtime.png`.

**X-axis:** Dataset and number of assets. **Y-axis:** Mean recorded runtime in seconds for a complete 30,000-evaluation run.

Each bar is the average of the reported mean runtimes over three target levels, each based on 10 seeds. Runtime depends on hardware, software environment, problem dimension, and implementation. Use the chart for comparison within the recorded execution environment; it is not a hardware-independent benchmark.

### 3.7 Largest allocation weights (3)

**Files:** `additional/best_allocations/port1_alpha050_top15_weights.png`, `port3_alpha050_top15_weights.png`, and `port5_alpha050_top15_weights.png`.

Each bar chart selects the **single lowest-variance run** among the three ES variants and 10 seeds for that specified case. It shows up to 15 largest asset weights, excluding weights at or below `1e-6` in fractional units. Asset IDs are the original OR-Library **1-based** identifiers, and bar values are percentages of the complete allocation budget.

The footnote identifies the selected ES variant and seed and reports the total share assigned to omitted assets. These charts show **one selected best observed allocation**, not a mean allocation across runs or a guaranteed optimal allocation. The complete weight vectors are available in the archives and CSV export.

## 4. Source results and readable exports

| File | Content |
| --- | --- |
| `problem2_es/results/runs.csv` | One row per run (case, variant, seed, target, final variance, return, feasibility, runtime, evaluation count) |
| `problem2_es/results/summary.csv` | One row per case–variant pair (45 rows), including best/mean/std. variance, feasible-run count/rate, and mean runtime |
| `problem2_es/results/raw/*.npz` | Full best weights and **30,000-point** evaluation/archive-best histories for each run |
| `problem2_es/results/readable/best_allocations_all_runs.csv` | All asset weights for all runs, including 1-based asset IDs and percent weights |
| `problem2_es/results/readable/convergence_sampled_all_runs.csv` | Sampled archive histories (default stride 100, plus first and last evaluation) |
| `problem2_es/results/readable/run_diagnostics.csv` | Initial/final best variance, final population best, return threshold, feasibility, improvement, and runtime |
| `problem2_es/results/readable/validation_summary.json` | Archive and dataset consistency checks reported by the visualization utility |

The `.npz` archives are **data files, not images**. Keep them for complete-resolution analyses and reproducibility. The CSV files provide readable versions for VS Code, Excel, or other analysis tools.

## 5. Regenerate figures without rerunning optimization

Open the **outer project directory** containing `requirements.txt` and activate the project Python environment. Then run:

```bash
python -m problem2_es.experiments.visualize_all
python -m problem2_es.experiments.plot_portfolio
```

The first command validates the saved run archives, generates the **30 supplementary figures**, and refreshes three CSV exports and `validation_summary.json`. By default, it expects the completed **450-run** result set and original five OR-Library datasets. The second command regenerates the **one assignment-required** convergence figure.

Neither command runs the ES optimizer or changes the original result archives. Keep the original datasets, `runs.csv`, `summary.csv`, and `.npz` files available at their documented paths.

## 6. Reporting and presentation guidance

The assignment requires the `port5_alpha050` convergence figure and a summary table for all 15 cases and three ES variants. The additional charts are optional analysis aids. For the report, select figures that directly support comparisons of **achieved variance, run-to-run variability, convergence, and runtime** rather than including every chart.

- State the dataset, return target, ES variant(s), number of seeds, and evaluation budget in relevant captions.
- Keep units explicit: evaluations (count), runtime (seconds), allocations (%), and portfolio variance (`return²`).
- Use the same ES variant labels and accessible colors across plots.
- Maintain clear, evenly spaced numerical ticks and zero baselines where meaningful; categorical axes do not have numerical zero. The plotted axis beginning at zero does **not** imply that an observation was taken at zero.
- Distinguish **best individual run**, **mean across seeds**, **variation across seeds**, and **best-so-far archive**; they answer different questions.
- Avoid describing the best observed result among these methods as the true global optimum.

See [README.md](README.md) for methods, setup, and experiment reproducibility. The final empirical interpretation belongs in the group's written report.
