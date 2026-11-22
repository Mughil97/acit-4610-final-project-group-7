# TSPLIB Benchmark Data (Problem 1 — Part A)

The Travelling Salesman Problem (TSP) benchmark instances are obtained from [Heidelberg University TSPLIB](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/) [1], with reference optimal tour lengths from the official [TSPLIB optimal solutions table](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/TSP-BEST.html) [2]. Each compressed `.tsp.gz` archive was decompressed into this directory (`bees_algorithm/data/`).

## Instances Used

| Local Data File | Cities ($n$) | Distance Type | Optimal Tour Length ($L^*$) | Official TSPLIB Source |
| :--- | ---: | :--- | ---: | :--- |
| [`eil51.tsp`](eil51.tsp) | 51 | `EUC_2D` (2D Rounded Euclidean) | 426 | [eil51.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/eil51.tsp.gz) |
| [`berlin52.tsp`](berlin52.tsp) | 52 | `EUC_2D` (2D Rounded Euclidean) | 7,542 | [berlin52.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/berlin52.tsp.gz) |
| [`st70.tsp`](st70.tsp) | 70 | `EUC_2D` (2D Rounded Euclidean) | 675 | [st70.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/st70.tsp.gz) |
| [`eil76.tsp`](eil76.tsp) | 76 | `EUC_2D` (2D Rounded Euclidean) | 538 | [eil76.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/eil76.tsp.gz) |
| [`kroA100.tsp`](kroA100.tsp) | 100 | `EUC_2D` (2D Rounded Euclidean) | 21,282 | [kroA100.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/kroA100.tsp.gz) |
| [`ch150.tsp`](ch150.tsp) | 150 | `EUC_2D` (2D Rounded Euclidean) | 6,528 | [ch150.tsp.gz](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/ch150.tsp.gz) |

Published optimal lengths $L^*$ are used solely for post-run percentage-gap evaluation and convergence plots, never to initialize or guide the Bees Algorithm.

## Structure of a `.tsp` File

```text
NAME: <instance_name>
TYPE: TSP
COMMENT: <additional description>
DIMENSION: <number of cities n>
EDGE_WEIGHT_TYPE: EUC_2D
NODE_COORD_SECTION
<city_id> <x-coordinate> <y-coordinate>
...
EOF
```

## Validation Rules

When loading any `.tsp` file via [`bees_algorithm/utils/load_data.py`](../utils/load_data.py) (`load_data`), the parser validates:

1. All required headers (`NAME`, `TYPE`, `DIMENSION`, `EDGE_WEIGHT_TYPE`) and `NODE_COORD_SECTION` are present.
2. `NAME` matches the filename stem.
3. `TYPE` is `TSP` and `EDGE_WEIGHT_TYPE` is `EUC_2D`.
4. `DIMENSION` is an integer matching the exact number of coordinate rows.
5. Every coordinate row contains three numeric fields (`<int> <float> <float>`) with unique, contiguous city IDs `1..DIMENSION`.

These checks are covered by [`bees_algorithm/tests/test_load_data.py`](../tests/test_load_data.py).

## References

1. Reinelt, G. **TSPLIB**. Heidelberg University. [Library home page](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/).
2. Reinelt, G. **Optimal solutions for symmetric TSPs**. [Reference tour lengths](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/TSP-BEST.html).
3. Reinelt, G. **TSPLIB 95 documentation**, Sections 1 and 2.1 (file format and `EUC_2D` rounded Euclidean distances). [Documentation PDF](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/tsp/tsp95.pdf).
