# TSPLIB

The data for the travelling salesman problem is from the [Heidelberg University TSPLIB](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/).

The files used in this projects are,

| Data Files                  | Cities(n)| Distance Type       | Optimal Tour Length |
|-----------------------------|---------:|---------------------|--------------------:|
|[eli51.tsp](eli51.tsp)       |51        |2D Euclidean Distance|426                  |
|[berlin52.tsp](berlin52.tsp) |52        |2D Euclidean Distance|7542                 |
|[st70.tsp](st70.tsp)         |70        |2D Euclidean Distance|675                  |
|[eil76.tsp](eil76.tsp)       |76        |2D Euclidean Distance|538                  |
|[korA100.tsp](korA100.tsp)   |100       |2D Euclidean Distance|21282                |
|[ch150.tsp](ch150.tsp)       |150       |2D Euclidean Distance|6528                 |

## Structure of the file

```text
NAME: name of the file
TYPE: TSP (Data for symmetric travelling salesman problem)
COMMENT: Additional comment
DIMENSION: No. of cities (n)
EDGE_WEIGHT_TYPE: EUC_2D (Weights are Euclidean distances in 2-D)
NODE_COORD_SECTION
Node coordinates are given in this section. Each line is
<city> <x-coordinate> <y-coordinate>
EOF
```
