# J E Besaley's OR Library

The data for the portfolio optimisation project is obtained from the [J E Besaley's OR Library](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html).

There are 5 files,

| Data Files           | Assets(n) | Correlations |
|:-------------------- |----------:|-------------:|
|[port1.txt](port1.txt)| 31        | 496          |
|[port2.txt](port2.txt)| 85        | 3655         |
|[port3.txt](port3.txt)| 89        | 4005         |
|[port4.txt](port4.txt)| 98        | 4851         |
|[port5.txt](port5.txt)| 225       | 25425        |

## Structure of the file

```text
number of assets(n)
for each asset i (i=1,$\dots$, n):
    mean return, standard deviation of the return
for all possible pair of assets:
    i, j correlating between assets i and j
```
