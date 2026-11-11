# Problem 1 (Optimisation using Bees Algorithm)

The problem 1 is optimisation problem using Bees Algorithm. The problem is made up of two parts Part A Symmetric Travelling Salesman Problem (TSP) and Part B Continuous Function Optimisation.

## Bees Algorithm
> TODO: Explain the algorithm and its parameters with pseudo code/flow chart

## Part A - Symmetric Travelling Salesman Problem (TSP)

> TODO

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
