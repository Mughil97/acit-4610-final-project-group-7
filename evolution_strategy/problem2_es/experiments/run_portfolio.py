"""Execute and summarize portfolio optimization experiments.

Runs the three ES variants across the configured datasets,
return targets, and random seeds. Stores individual results,
convergence histories, and aggregate statistics.
"""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from pathlib import Path
import statistics
import numpy as np

from ..src.portfolio import EXPECTED_SIZES, ALPHAS, check_port1_checkpoint, load_portfolio
from ..src.evolution_strategies import VARIANTS, run_es

PROJECT = Path(__file__).resolve().parents[2]
DATA = PROJECT/"problem2_es"/"data"/"or_library"
DEFAULT_OUT = PROJECT/"problem2_es"/"results"
SEEDS = tuple(range(10))
RAW_FIELDS = ("case","dataset","dataset_sha256","n","alpha","target","variant","seed","budget","evals",
              "initial_best","variance","expected_return","runtime_seconds","valid",
              "final_population_best","raw_file")
SUMMARY_FIELDS = ("case","dataset","n","target","variant","budget","runs","valid_runs",
                  "best_variance","mean_variance","std_variance","feasible_run_rate",
                  "mean_runtime_seconds")


def available_cases() -> dict[str,tuple[str,float]]:
    return {f"{name}_alpha{int(round(alpha*100)):03d}":(name,alpha)
            for name in EXPECTED_SIZES for alpha in ALPHAS}


def save_csv(path: Path, fieldnames: tuple[str,...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_suffix(".pending")
    with temp.open("w",newline="",encoding="utf-8") as fd:
        wr=csv.DictWriter(fd,fieldnames=fieldnames)
        wr.writeheader()
        wr.writerows(rows)
    temp.replace(path)


def load_previous_results(path: Path) -> dict[tuple[str,str,int,int],dict]:
    if not path.exists():
        return {}
    with path.open(newline="",encoding="utf-8") as fd:
        rows=list(csv.DictReader(fd))
    return {(row["case"],row["variant"],int(row["seed"]),int(row["budget"])):row for row in rows}


def generate_summary(rows: list[dict]) -> list[dict]:
    groups={}
    for row in rows:
        groups.setdefault((row["case"],row["variant"],int(row["budget"])),[]).append(row)
    summary=[]
    for (case,variant,budget), group in sorted(groups.items()):
        valids=[float(r["variance"]) for r in group if str(r["valid"]).lower()=="true"]
        summary.append(dict(case=case,dataset=group[0]["dataset"],n=group[0]["n"],
            target=group[0]["target"],variant=variant,budget=budget,runs=len(group),valid_runs=len(valids),
            best_variance=min(valids) if valids else "",
            mean_variance=statistics.mean(valids) if valids else "",
            std_variance=statistics.stdev(valids) if len(valids)>1 else "",
            feasible_run_rate=100.0*len(valids)/len(group),
            mean_runtime_seconds=statistics.mean(float(r["runtime_seconds"]) for r in group)))
    return summary


def main(argv: list[str] | None=None) -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case",default="all",choices=["all",*available_cases()])
    parser.add_argument("--variant",default="all",choices=["all",*VARIANTS])
    parser.add_argument("--seeds",nargs="+",type=int,default=list(SEEDS))
    parser.add_argument("--budget",type=int,default=30_000)
    parser.add_argument("--data-dir",type=Path,default=DATA)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    parser.add_argument("--force",action="store_true",help="Rerun cases even if raw archives exist")
    args=parser.parse_args(argv)
    selected=available_cases() if args.case=="all" else {args.case:available_cases()[args.case]}
    variants=VARIANTS if args.variant=="all" else (args.variant,)
    if len(args.seeds)!=len(set(args.seeds)):
        parser.error("Seeds must be distinct")
    for name in {t[0] for t in selected.values()}:
        file=args.data_dir/f"{name}.txt"
        if not file.is_file():
            parser.error(f"Missing original OR-Library dataset: {file}. Run python -m problem2_es.experiments.download_data")

    portfolios={name:load_portfolio(args.data_dir/f"{name}.txt",expected_n=EXPECTED_SIZES[name])
                for name in {t[0] for t in selected.values()}}
    if "port1" in portfolios:
        check_port1_checkpoint(portfolios["port1"])
    hashes={name:sha256((args.data_dir/f"{name}.txt").read_bytes()).hexdigest()
            for name in portfolios}
    previous=load_previous_results(args.out/"runs.csv")
    for case,(dataset,alpha) in selected.items():
        p=portfolios[dataset]
        for variant in variants:
            for seed in args.seeds:
                rel=f"raw/{case}/{variant}_seed{seed}_budget{args.budget}.npz"
                path=args.out/rel
                key=(case,variant,int(seed),int(args.budget))
                if key in previous and previous[key].get("dataset_sha256")!=hashes[dataset]:
                    parser.error(f"Input data changed for {case}, seed={seed}; use a separate --out directory for different data")
                if key in previous and path.is_file() and not args.force:
                    print(f"SKIP {case} {variant} seed={seed}: saved result present",flush=True)
                    continue
                result=run_es(p,alpha,variant,seed=int(seed),budget=args.budget)
                path.parent.mkdir(parents=True,exist_ok=True)
                np.savez_compressed(path,best_weights=result.best_weights,
                    best_history=result.best_history,
                    evals=np.arange(1,result.evals+1,dtype=np.int32),
                    initial_best=result.initial_best, best_variance=result.best_variance,
                    best_return=result.best_return)
                previous[key]=dict(case=case,dataset=dataset,dataset_sha256=hashes[dataset],n=p.n,alpha=alpha,
                    target=p.target(alpha),variant=variant,seed=seed,budget=args.budget,
                    evals=result.evals,initial_best=result.initial_best,
                    variance=result.best_variance,expected_return=result.best_return,
                    runtime_seconds=result.runtime_seconds,valid=result.feasible,
                    final_population_best=result.final_population_best,raw_file=rel)
                # Save after every run to avoid losing completed experiments on interruption.
                ordered=[previous[k] for k in sorted(previous)]
                save_csv(args.out/"runs.csv",RAW_FIELDS,ordered)
                save_csv(args.out/"summary.csv",SUMMARY_FIELDS,generate_summary(ordered))
                print(f"{case:18s} {variant:15s} seed={seed:2d} "
                      f"evals={result.evals} variance={result.best_variance:.9g} "
                      f"return={result.best_return:.9g} valid={result.feasible} "
                      f"time={result.runtime_seconds:.2f}s",flush=True)
    print(f"\nPer-run results: {args.out/'runs.csv'}")
    print(f"Summary statistics: {args.out/'summary.csv'}")
    print("Plotting port5_alpha050: python -m problem2_es.experiments.plot_portfolio")


if __name__ == "__main__":
    main()
