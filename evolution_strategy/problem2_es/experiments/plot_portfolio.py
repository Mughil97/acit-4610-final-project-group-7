"""Generate the required portfolio ES convergence comparison.

Plots mean archive-best portfolio variance against objective
evaluations for port5_alpha050 across ten independent runs.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from .run_portfolio import DEFAULT_OUT, SEEDS
from ..src.evolution_strategies import VARIANTS


def plot_convergence(out: Path, *, budget: int=30_000) -> Path:
    log=out/"runs.csv"
    if not log.is_file():
        raise FileNotFoundError(f"Missing experiment logs: {log}")
    with log.open(newline="",encoding="utf-8") as fd:
        runs=list(csv.DictReader(fd))
    fig,ax=plt.subplots(figsize=(9,5.2))
    titles={"one_plus_one":"(1+1)-ES","mu_plus_lambda":"(10+70)-ES", "mu_comma_lambda":"(10,70)-ES"}
    colors={"one_plus_one":"#0072B2","mu_plus_lambda":"#E69F00","mu_comma_lambda":"#009E73"}
    for variant in VARIANTS:
        selected={int(r["seed"]):r for r in runs if r["case"]=="port5_alpha050"
                  and r["variant"]==variant and int(r["budget"])==budget}
        if set(selected)!=set(SEEDS):
            raise ValueError(f"Need exactly seeds {list(SEEDS)} for port5_alpha050 {variant}; got {sorted(selected)}")
        histories=[]
        for seed in SEEDS:
            with np.load(out/selected[seed]["raw_file"],allow_pickle=False) as record:
                h=record["best_history"]
                if len(h)!=budget:
                    raise ValueError("Missing evaluations in convergence history")
                histories.append(h)
        mean=np.mean(np.vstack(histories),axis=0)
        ax.plot(np.arange(1,budget+1),mean,label=titles[variant],linewidth=1.8, color=colors[variant])
    ax.set_title("ES portfolio convergence | port5, α = 0.50", loc="left", pad=12)
    ax.set_xlabel("Objective function evaluations (count)")
    ax.set_ylabel("Mean archive-best portfolio variance (return²)")
    ax.set_xlim(0,budget)
    _, ymax = ax.get_ylim()
    ax.set_ylim(bottom=0, top=ymax)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=7))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.set_axisbelow(True)
    ax.grid(alpha=0.22,linewidth=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(title="ES variant",frameon=False)
    fig.text(0.015,0.013,"Mean across 10 independent seeds per ES variant; lower variance is better.",
             fontsize=8,alpha=.78)
    fig.tight_layout(rect=(0,0.06,1,1))
    path=out.parent/"figures"/"port5_alpha050_convergence.png"
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=220)
    plt.close(fig)
    print(f"Saved {path}")
    return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    parser.add_argument("--budget",type=int,default=30_000)
    args=parser.parse_args()
    plot_convergence(args.out,budget=args.budget)


if __name__ == "__main__":
    main()
