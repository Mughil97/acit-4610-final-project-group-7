# Problem 2 experimental status — updated from Group 7 uploaded results, Nov 4, 2026

- Three required ES implementations, original OR-Library portfolio parsers and feasibility repair are present.
- The uploaded archive includes all five original OR-Library `port1.txt`–`port5.txt` datasets.
- `runs.csv` contains 450 runs: 15 cases × 3 methods × 10 seeds; every run is recorded at 30,000 objective evaluations.
- Every recorded run was revalidated from its `.npz` best allocation against the corresponding original portfolio data: nonnegative weights, total weight 1 within tolerance, required return threshold, and calculated variance/return matching logs. All 450 passed.
- All 450 `.npz` histories were checked for exact evaluation length and a nonincreasing best-so-far archive; all passed.
- `summary.csv` contains the 45 expected case–variant rows, all with 10 valid runs.
- The original mandatory `port5_alpha050_convergence.png` is present and preserved.
- The additional visualization utility generates 30 supplementary PNGs and three readable CSVs to support understanding (not all mandated by the assignment).
- The project's 35 automated tests passed in this environment.
- Still required for a final coursework submission: group interpretation and independently written report, proper AI-code attribution/declaration, final run/setup documentation review, and integration into the group repository.
- Numerical validation of saved outputs does not certify global optimality or independently verify the students' conduct of the experiments.
