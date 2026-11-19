# Problem 1 (Optimisation using Bees Algorithm)

The problem 1 is optimisation problem using Bees Algorithm. The problem is made up of two parts Part A Symmetric Travelling Salesman Problem (TSP) and Part B Continuous Function Optimisation.

## Bees Algorithm
The bees algorithm is a population-based optimization algorithm. It maintains a whole population simultaneously instead of tracking one point. A population is a collection of bees and each bee represents one possible solution to the problem. 

A scout is a bee in the population. The bee consists of a fitness and a site. The site is a solution that can be explored further and we want to find better solutions around this site. We do this by creating new neighbouring solutions (exploitation).  The best bee is the bee with the lowest fitness and it becomes a part of the elite sites. We also select other, potentially good sites. The sites are selected based on the bee’s fitness: the lower the better. The unselected sites are replaced by new bees. 


> TODO: Explain the algorithm and its parameters with pseudo code/flow chart

## Part A - Symmetric Travelling Salesman Problem (TSP)

The travelling salesman problem involves visiting a number of cities exactly once and then returning to the start city. The objective is to find the route which minimizes the total distance travelled when doing a round trip. 

The routes are represented as permutations where the first element is the starting city. A bee is a route and its fitness is the total distance travelled when travelling this route. We calculate the distances using rounded Euclidean distances, and we include the return edge. 

The scouts are initialized randomly and the neighbours are initialized by swapping two cities (their positions) or by reversing a segment between two cities. The first city is the starting city and will always be fixed. 

**Rounded Euclidean distance**: 
$d_{ij} = \text{floor}\left\(\sqrt{(a_i-a_j)^2 + (b_i-b_j)^2} + 0.5\right)$

## Part B - Continuous Function Optimisation

The optimisation algorithms like the Bees Algorithm are evaluated using common functions. This helps to understand if the algorithm can escape local minima and reach global minima. \
For this project the Bees Algorithm will be evaluated against the following functions,

**Sphere** [1]:
$f(x) = \sum_{i=1}^D x_i^2$ \
Bounds: $x_i \in [-5.12, 5.12]$. Global minimum: $f(0) = 0$. This is a convex, unimodal function.

**Rosenbrock** [2]:
$f(x) = \sum_{i=1}^{D-1}[100(x_{i+1}-x_i^2)^2+(1-x_1)^2]$ \
Bounds: $x_1 \in [-5,10]$. Global minimum: $f(1) = 0$. Its narrow-curved valley makes progress toward the
optimum difficult.

**Rastrigin** [3]:
$f(x) = 10D + \sum_{i=1}^D [x_i^2 -10\cos(2 \pi x_i)]$ \
Bounds: $x_i \in [-5.12, 5.12]$. Global minimum: $f(𝟎) = 0$. It has many local minima.

**Ackley** [4]
$f(x) = -20 \cdot \exp( -0.2 \sqrt{\frac{1}{D} \sum_{i=1}^D x_i^2}) - \exp(\frac{1}{D} \sum_{i=1}^D \cos(2 \pi x_i)) + 20 + \exp(1)$ \
Bounds: $x_i \in [-32.768, 32.768]$. Global minimum: $f(𝟎) = 0$. It has many local minima and a relatively
flat outer region.

These functions are from the Surjanovic and Bingham's Simon Fraser
University [collection](https://www.sfu.ca/~ssurjano/optimization.html).

> TODO: Flow chart, the initialisation strategy

[1]: https://www.sfu.ca/~ssurjano/spheref.html
[2]: https://www.sfu.ca/~ssurjano/rosen.html
[3]: https://www.sfu.ca/~ssurjano/rastr.html
[4]: https://www.sfu.ca/~ssurjano/ackley.html

---

## File Structure

```text
acit-4610-final-project-group-7/
├── main.py                                   # Entry point: runs Part A, Part B, summaries, and plots
├── logger.py                                 # Console + file logging (writes to run.log)
├── requirements.txt                          # Python dependencies
└── bees_algorithm/
    ├── configs.py                            # BA parameters, seeds, function configs, TSPLIB configs & optima
    ├── functions.py                          # Sphere, Rosenbrock, Rastrigin, Ackley definitions
    ├── interface.py                          # Abstract OptimisationProblem base class
    ├── optimise.py                           # Experiment runners: optimise_tsp() and optimise_functions()
    ├── core/
    │   ├── bee.py                            # Bee candidate representation
    │   └── solver.py                         # BeesAlgorithmSolver (initialise, rank, exploit, abandon, replenish)
    ├── problem/
    │   ├── tsp.py                            # SymmetricTSP problem (SWAP / REVERSE neighbourhoods)
    │   └── continuous.py                     # ContinuousFunctionOptimisation problem
    ├── data/                                 # Official TSPLIB instances (eil51, berlin52, st70, eil76, kroA100, ch150)
    ├── tests/
    │   ├── test_functions.py                 # Benchmark function verification tests
    │   └── test_reporting.py                 # Tests for validators, writer, summarizer, and plotting
    ├── utils/
    │   ├── exceptions.py                     # DataError, BudgetExhausted
    │   ├── load_data.py                      # TSPLIB file parser
    │   ├── tracked.py                        # TrackedProblem & ProblemTracker (30,000-eval budget + best-so-far history)
    │   ├── validators.py                     # Post-run TSP tour & continuous bounds validators
    │   ├── writer.py                         # ExperimentWriter (raw CSVs, JSON solutions, per-eval histories, metadata)
    │   ├── summarizer.py                     # Aggregates raw runs into CSV and Markdown summary tables
    │   └── plotting.py                       # Generates convergence, berlin52 route, and D=30 boxplot figures
    └── results/
        ├── metadata.json                     # Recorded parameters, seed list, and package versions
        ├── part_a_tsp/
        │   ├── raw/                          # runs.csv (120 runs) and solutions.json
        │   ├── histories/                    # <instance>_<neighbourhood>.csv (30,000 evals × 10 seeds)
        │   ├── tables/                       # summary_tsp.csv and summary_tsp.md
        │   └── figures/                      # convergence_berlin52.png, convergence_ch150.png, best_route_berlin52.png
        └── part_b_continuous/
            ├── raw/                          # runs.csv (80 runs) and solutions.json
            ├── histories/                    # <function>_D<dim>.csv (30,000 evals × 10 seeds)
            ├── tables/                       # summary_continuous.csv and summary_continuous.md
            └── figures/                      # convergence_rastrigin_D10.png, boxplots_D30.png
```

## Setup & Dependencies

Tested with **Python 3.14.6** and:
- `numpy==2.5.4`
- `matplotlib==3.11.2`
- `pytest==9.2.0`

Install dependencies into a virtual environment from the repository root:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## BA Parameters & Seeds

Configured in `bees_algorithm/configs.py`:
- **Evaluation budget (`max_evaluations`):** `30000`
- **Scout population (`ns`):** `30`
- **Elite sites (`ne`):** `3`
- **Selected sites (`nb`):** `10`
- **Elite recruits (`nre`):** `15`
- **Selected recruits (`nrb`):** `5`
- **Stagnation limit (`stlim`):** `100`
- **Shrink factor (`shrink_factor`):** `0.2`
- **Seeds (`10` independent runs, `SEED = 45`):** `[45, 46, 47, 48, 49, 50, 51, 52, 53, 54]`
- **Part A instances & optima:** `eil51` (`426`), `berlin52` (`7542`), `st70` (`675`), `eil76` (`538`), `kroA100` (`21282`), `ch150` (`6528`) with `SWAP` and `REVERSE`
- **Part B functions & dimensions:** `sphere`, `rosenbrock`, `rastrigin`, `ackley` at `D = 10` and `D = 30`

## How to Run the Experiments

Run all commands from the repository root (`acit-4610-final-project-group-7/`).

### 1. Run the full suite (Part A + Part B + summaries + plots)
```bash
python main.py
```

### 2. Run only Part A (TSP) or only Part B (Continuous)
```bash
python -c "from bees_algorithm.optimise import optimise_tsp; optimise_tsp()"
python -c "from bees_algorithm.optimise import optimise_functions; optimise_functions()"
```

### 3. Run a single experiment (example)
```bash
python -c "
from bees_algorithm.configs import FunctionOptimisationConfig as foc, BERLIN52_CONFIG, SWAP
from bees_algorithm.core.solver import BeesAlgorithmSolver
from bees_algorithm.problem.tsp import SymmetricTSP
from bees_algorithm.utils.exceptions import BudgetExhausted
from bees_algorithm.utils.tracked import TrackedProblem

tsp = SymmetricTSP(seed=45, path_data=BERLIN52_CONFIG.path, strategy=SWAP)
tracked = TrackedProblem(tsp, foc.ns, foc.max_evaluations)
try:
    BeesAlgorithmSolver(tracked, foc).run()
except BudgetExhausted:
    pass
print('Final best:', tracked.tracker.best_solution.fitness, 'Evals:', tracked.tracker.evaluations)
"
```

### 4. Regenerate summary tables and plots from saved results
```bash
python bees_algorithm/utils/summarizer.py
python bees_algorithm/utils/plotting.py
```

### 5. Run tests
```bash
pytest bees_algorithm/tests
```
