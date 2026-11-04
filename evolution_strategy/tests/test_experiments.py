"""End-to-end test for the experiment writer using generated temporary data only.
"""
import csv
from pathlib import Path
import numpy as np
from problem2_es.experiments.run_portfolio import main


def test_experiment_runner_generates_archive_and_summary(tmp_path):
    # A toy 85-asset dataset in an isolated temp directory. NOT official port2.
    data_dir=tmp_path/"synthetic_data"
    data_dir.mkdir()
    n=85
    data_file=data_dir/"port2.txt"
    with data_file.open("w") as f:
        f.write(f"{n}\n")
        for i in range(n):
            f.write(f"{0.01 + i*0.00002:.8f} 0.1\n")
        for i in range(n):
            for j in range(i,n):
                f.write(f"{i+1} {j+1} {1.0 if i==j else 0.0}\n")
    out=tmp_path/"synthetic_results"
    args=["--case","port2_alpha050","--variant","all","--seeds","0",
          "--budget","173","--data-dir",str(data_dir),"--out",str(out)]
    main(args)
    with (out/"runs.csv").open() as f:
        runs=list(csv.DictReader(f))
    assert len(runs)==3
    assert all(int(r["evals"])==173 for r in runs)
    assert all(r["valid"]=="True" for r in runs)
    with (out/"summary.csv").open() as f:
        summary=list(csv.DictReader(f))
    assert len(summary)==3
    assert all(int(row["budget"])==173 for row in summary)
    for row in runs:
        with np.load(out/row["raw_file"],allow_pickle=False) as bundle:
            assert len(bundle["best_history"])==173
            assert len(bundle["best_weights"])==n
            assert np.all(np.diff(bundle["best_history"])<=1e-15)
    main(args)  # Resume must not duplicate or overwrite completed runs.
    with (out/"runs.csv").open() as f:
        assert len(list(csv.DictReader(f)))==3
