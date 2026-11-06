# Original OR-Library portfolio datasets

The final assignment requires these **original** datasets. They are not simulated and must not be silently replaced with synthetic inputs:

- `port1.txt`: 31 assets, 496 correlation records
- `port2.txt`: 85 assets, 3,655 records
- `port3.txt`: 89 assets, 4,005 records
- `port4.txt`: 98 assets, 4,851 records
- `port5.txt`: 225 assets, 25,425 records

Official source: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/portinfo.html

Files:
`https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/port1.txt`
(and replace `port1` with `port2` … `port5`).

From the project root, run `python -m problem2_es.experiments.download_data`. If a network blocks the download, manually place the **unchanged** files into this folder. The parser checks the declared asset count, all correlation records, and diagonal entries. The loader checks the `port1` assignment checkpoints.
