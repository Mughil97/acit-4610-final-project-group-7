"""Validate ES experiment archives and generate supplementary results.

Produces convergence plots, distribution comparisons,
relative-performance heatmaps, allocation charts, and
readable CSV exports from previously saved optimization runs.

The optimizer is not executed by this module.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

from .run_portfolio import DEFAULT_OUT
from ..src.portfolio import load_portfolio, EXPECTED_SIZES, TOLERANCE

VARIANTS = ('one_plus_one', 'mu_plus_lambda', 'mu_comma_lambda')
LABELS = {
    'one_plus_one': '(1+1)-ES',
    'mu_plus_lambda': '(10+70)-ES',
    'mu_comma_lambda': '(10,70)-ES',
}
SEEDS = tuple(range(10))
ALPHAS = (0.25, 0.50, 0.75)
CB_COLORS = {
    'one_plus_one': '#0072B2',   # blue
    'mu_plus_lambda': '#E69F00', # orange
    'mu_comma_lambda': '#009E73' # bluish green
}


def _set_zero_baseline(ax: plt.Axes, *, x: bool = False, y: bool = True) -> None:
    """Anchor numeric axes at zero where it improves honesty/readability."""
    if y:
        _, ymax = ax.get_ylim()
        ax.set_ylim(bottom=0, top=ymax)
    if x:
        _, xmax = ax.get_xlim()
        ax.set_xlim(left=0, right=xmax)


def _set_even_numeric_ticks(ax: plt.Axes, *, xbins: int | None = None, ybins: int | None = 6) -> None:
    """Use evenly spaced major ticks for quantitative axes."""
    if xbins is not None:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=xbins))
    if ybins is not None:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=ybins))


def _style_plot(ax: plt.Axes, *, grid: str = 'y') -> None:
    """Minimal scientific plotting style; same across all ES figures."""
    ax.set_axisbelow(True)
    ax.grid(axis=grid, linewidth=0.65, alpha=0.22)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', labelsize=9)
    ax.xaxis.label.set_fontsize(10)
    ax.yaxis.label.set_fontsize(10)
    ax.title.set_fontsize(12)


def _explain(fig: plt.Figure, note: str) -> None:
    """Figure footnote as an honest scientific caption, not an invented result."""
    fig.text(0.015, 0.013, note, ha='left', va='bottom', fontsize=8, alpha=0.78)



def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, fields: list[str], rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _finish(fig: plt.Figure, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(target, dpi=185, facecolor='white')
    plt.close(fig)


def build_visuals(out: Path = DEFAULT_OUT, budget: int = 30_000,
                  step: int = 100, *, strict: bool = True) -> dict:
    """Produce all supplementary plots and CSV exports from official raw results."""
    if step < 1:
        raise ValueError('step must be >= 1')
    results = _read_csv(out / 'runs.csv')
    summary = _read_csv(out / 'summary.csv')
    if not results:
        raise ValueError(f'No run rows found in {out / "runs.csv"}')
    if strict:
        if len(results) != 450 or len(summary) != 45:
            raise ValueError(f'Expected 450 runs and 45 summary rows; got {len(results)} and {len(summary)}')
        for case in [f'port{i}_alpha{int(a*100):03d}' for i in range(1,6) for a in ALPHAS]:
            for variant in VARIANTS:
                found = [r for r in results if r['case']==case and r['variant']==variant and int(r['budget'])==budget]
                if {int(r['seed']) for r in found} != set(SEEDS) or len(found)!=10:
                    raise ValueError(f'Expected seeds 0..9 exactly once for {case}/{variant}')

    figure_dir = out.parent / 'figures' / 'additional'
    readable = out / 'readable'
    readable.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    portfolios = {
        name: load_portfolio(out.parent / 'data' / 'or_library' / f'{name}.txt',
                             expected_n=n)
        for name, n in EXPECTED_SIZES.items()
    }
    summary_index = {(r['case'],r['variant']): r for r in summary}
    run_index = defaultdict(list)
    for r in results:
        run_index[(r['case'],r['variant'])].append(r)

    sample_idx = np.unique(np.r_[0, np.arange(step-1, budget, step), budget-1]).astype(int)
    sample_idx = sample_idx[sample_idx < budget]
    sums = {key: np.zeros(budget, dtype=np.float64) for key in run_index}
    sums_count = defaultdict(int)
    weights_rows = []
    sample_rows = []
    diagnostic_rows = []
    failures = []

    for r in results:
        case, variant = r['case'],r['variant']
        dataset = r['dataset']
        port = portfolios[dataset]
        path = out / r['raw_file']
        with np.load(path, allow_pickle=False) as obj:
            w = np.asarray(obj['best_weights'], dtype=float)
            history = np.asarray(obj['best_history'], dtype=float)
            evals = np.asarray(obj['evals'], dtype=int)
            obj_variance = float(obj['best_variance'])
            obj_return = float(obj['best_return'])
        if w.shape != (port.n,) or history.shape != (budget,) or evals.shape != (budget,):
            raise ValueError(f'Bad archive shape {path}: weights={w.shape}, history={history.shape}')
        if not np.array_equal(evals, np.arange(1,budget+1)):
            raise ValueError(f'Non-contiguous evaluation counters in {path}')
        if np.any(np.diff(history)>1e-10):
            raise ValueError(f'Archive best history increases in {path}')
        variance=port.variance(w)
        expected_return=port.expected_return(w)
        target=float(r['target'])
        feasible=port.validate(w,target,atol=TOLERANCE)
        if not feasible or not np.isclose(variance,float(r['variance']),atol=1e-10,rtol=1e-6) or not np.isclose(expected_return,float(r['expected_return']),atol=1e-10,rtol=1e-6) or not np.isclose(history[-1],variance,atol=1e-10,rtol=1e-6) or not np.isclose(variance,obj_variance,atol=1e-10,rtol=1e-6) or not np.isclose(expected_return,obj_return,atol=1e-10,rtol=1e-6):
            failures.append(str(path))
        sums[(case,variant)] += history
        sums_count[(case,variant)] += 1
        for idx, weight in enumerate(w, 1):
            weights_rows.append({'case':case,'variant':variant,'seed':int(r['seed']),
                                 'asset_index_1based':idx,'weight':f'{weight:.16g}',
                                 'weight_percent':f'{weight*100:.12g}'})
        for x in sample_idx:
            sample_rows.append({'case':case,'variant':variant,'seed':int(r['seed']),
                                'evaluation':int(x)+1,'archive_best_variance':f'{history[x]:.16g}'})
        diagnostic_rows.append({'case':case,'variant':variant,'seed':int(r['seed']),
                                'evaluations':int(r['evals']),'feasible':feasible,
                                'target_return':f'{target:.16g}',
                                'achieved_return':f'{expected_return:.16g}',
                                'final_best_variance':f'{variance:.16g}',
                                'population_best_at_end':r['final_population_best'],
                                'archive_minus_population':f'{variance-float(r["final_population_best"]):.16g}',
                                'initial_best_variance':r['initial_best'],
                                'improvement_percent':f'{100*(float(r["initial_best"])-variance)/max(abs(float(r["initial_best"])),1e-300):.12g}',
                                'runtime_seconds':r['runtime_seconds'],
                                'raw_file':r['raw_file']})

    if failures:
        raise ValueError(f'{len(failures)} archive(s) fail feasibility/value checks; first: {failures[:3]}')
    if strict and any(sums_count[key]!=10 for key in sums_count):
        raise ValueError('Not all curve groups have 10 seeds')
    _write_csv(readable / 'best_allocations_all_runs.csv',
               ['case','variant','seed','asset_index_1based','weight','weight_percent'],weights_rows)
    _write_csv(readable / 'convergence_sampled_all_runs.csv',
               ['case','variant','seed','evaluation','archive_best_variance'],sample_rows)
    _write_csv(readable / 'run_diagnostics.csv',
               ['case','variant','seed','evaluations','feasible','target_return','achieved_return',
                'final_best_variance','population_best_at_end','archive_minus_population',
                'initial_best_variance','improvement_percent','runtime_seconds','raw_file'],diagnostic_rows)

    figures = []
    mean_curves = {key: s / sums_count[key] for key,s in sums.items()}
    eval_axis=np.arange(1,budget+1)[sample_idx]
    # Supplementary convergence: identical y metric and descriptive titles, no false precision.
    for case in sorted({r['case'] for r in results}):
        fig, ax = plt.subplots(figsize=(9.2,5.4))
        for variant in VARIANTS:
            ax.plot(eval_axis, mean_curves[(case,variant)][sample_idx],
                    label=LABELS[variant], linewidth=2, color=CB_COLORS[variant])
        ax.set_title(f'Convergence of Evolution Strategies | {case}',loc='left',pad=12)
        ax.set_xlabel('Objective function evaluations (count)')
        ax.set_ylabel('Mean archive-best portfolio variance (return²)')
        ax.set_xlim(0,budget)
        _set_zero_baseline(ax, y=True)
        _set_even_numeric_ticks(ax, xbins=7, ybins=6)
        _style_plot(ax,grid='both')
        ax.legend(title='ES variant', frameon=False, fontsize=9, loc='best')
        _explain(fig,'Source: OR-Library data | 10 independent seeds per method | Lower variance is better.')
        target=figure_dir/'convergence'/f'{case}_convergence.png'
        _finish(fig,target);figures.append(target)

    # Seed variability: three return settings × three algorithms per portfolio dataset.
    from matplotlib.patches import Patch
    colors = [CB_COLORS[v] for v in VARIANTS]
    for d in EXPECTED_SIZES:
        fig,ax=plt.subplots(figsize=(10,5.6))
        dat=[];pos=[];box_colors=[]
        for k,a in enumerate(ALPHAS):
            case=f'{d}_alpha{int(a*100):03d}'
            for vi,v in enumerate(VARIANTS):
                dat.append([float(row['variance']) for row in run_index[(case,v)]])
                pos.append(3*k + vi + 1)
                box_colors.append(colors[vi])
        bp=ax.boxplot(dat,positions=pos,widths=.62,showfliers=True,
                      patch_artist=True,manage_ticks=False,
                      medianprops={'color':'black','linewidth':1.5})
        for patch,c in zip(bp['boxes'],box_colors):
            patch.set_facecolor(c)
            patch.set_alpha(.32)
            patch.set_edgecolor(c)
        ax.set_xticks([2,5,8],[f'{a:.2f}' for a in ALPHAS])
        ax.set_title(f'Across-seed variability in portfolio variance | {d}',loc='left',pad=12)
        ax.set_ylabel('Final archive-best portfolio variance (return²)')
        ax.set_xlabel('Minimum-return target level (α)')
        ax.legend(handles=[Patch(facecolor=c,edgecolor=c,alpha=.55,label=LABELS[v])
                           for v,c in zip(VARIANTS,colors)],
                  title='ES variant',frameon=False,fontsize=9)
        _set_zero_baseline(ax, y=True)
        _set_even_numeric_ticks(ax, ybins=6)
        _style_plot(ax)
        _explain(fig, 'Each box represents 10 independent seeds. Lower variance is better; comparisons are within the same target.')
        target=figure_dir/'boxplots'/f'{d}_variance_boxplot.png'
        _finish(fig,target);figures.append(target)

        fig,ax=plt.subplots(figsize=(9,5.4))
        for variant in VARIANTS:
            y=[float(summary_index[(f'{d}_alpha{int(a*100):03d}',variant)]['mean_variance']) for a in ALPHAS]
            ax.plot(ALPHAS,y,'o-',label=LABELS[variant],linewidth=2,markersize=5, color=CB_COLORS[variant])
        ax.set_title(f'Portfolio variance versus required return | {d}',loc='left',pad=12)
        ax.set_xlabel('Minimum-return target level (α)')
        ax.set_ylabel('Mean final feasible variance (return²)')
        ax.set_xticks((0.0,)+ALPHAS,['0.00']+[f'{a:.2f}' for a in ALPHAS])
        ax.set_xlim(0, 0.80)
        _set_zero_baseline(ax, y=True)
        _set_even_numeric_ticks(ax, ybins=6)
        _style_plot(ax,grid='both')
        ax.legend(title='ES variant',frameon=False,fontsize=9)
        _explain(fig, 'Mean of 10 runs per method at each return target; do not compare raw variances across different asset universes.')
        target=figure_dir/'variance_vs_target'/f'{d}_mean_variance_vs_alpha.png'
        _finish(fig,target);figures.append(target)

    # Heatmap compares each algorithm with the BEST OBSERVED MEAN, not a known mathematical optimum.
    cases=sorted({r['case'] for r in results})
    quality=np.zeros((len(cases),len(VARIANTS)))
    for i,case in enumerate(cases):
        vals=[float(summary_index[(case,v)]['mean_variance']) for v in VARIANTS]
        best=min(vals)
        quality[i,:]=[(x/best-1)*100 if best>0 else 0 for x in vals]
    # A stepped, monotonic, color-blind-friendly BLUE scale makes small
    # differences (0 vs 2 vs 5%) legible without assigning colors to methods.
    # Five magnitude bands: 0%, (0,5]%, (5,20]%, (20,50]%, >50%.
    band = np.select((quality <= 0, quality <= 5, quality <= 20,
                      quality <= 50), (0, 1, 2, 3), default=4)
    blue_shades = ['#F4F9FD', '#C6DBEF', '#6BAED6', '#2171B5', '#08306B']
    cmap = ListedColormap(blue_shades)
    norm = BoundaryNorm(np.arange(-.5, 5.5, 1), cmap.N)
    fig,ax=plt.subplots(figsize=(10.8,8.7))
    im=ax.imshow(band, aspect='auto', cmap=cmap, norm=norm,
                 interpolation='nearest')
    ax.set_xticks(np.arange(3), [LABELS[v] for v in VARIANTS])
    ax.set_yticks(np.arange(len(cases)), cases)
    ax.set_xlabel('Evolution Strategies variant')
    ax.set_ylabel('Portfolio case (dataset and target α)')
    ax.set_title('Relative excess mean variance by portfolio case', loc='left', pad=14)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(cases), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.3)
    ax.tick_params(which='minor', bottom=False, left=False)
    for i in range(len(cases)):
        for j in range(3):
            v = quality[i,j]
            lab = ('0.0%' if v <= 0 else '<0.1%' if v < 0.05
                   else f'{v:.1f}%')
            ax.text(j,i,lab,ha='center',va='center',fontsize=9.4,
                    fontweight='semibold' if band[i,j] == 0 else 'normal',
                    color='#FFFFFF' if band[i,j] >= 3 else '#102A43')
    cbar=fig.colorbar(im,ax=ax,ticks=np.arange(5),pad=.035,shrink=.90)
    cbar.ax.set_yticklabels(['Best (0%)', '>0–5%', '>5–20%', '>20–50%', '>50%'])
    cbar.set_label('Excess mean variance (bands)',labelpad=13)
    _explain(fig, 'Compared with the LOWEST MEAN among the three ES variants in each case; not the global optimum. Darker blue = greater excess variance.')
    target=figure_dir/'overview_relative_variance.png'
    _finish(fig,target);figures.append(target)

    # Runtime comparison: absolute timings across datasets, not cross-hardware benchmarks.
    fig,ax=plt.subplots(figsize=(9.6,5.6))
    ds=list(EXPECTED_SIZES)
    x=np.arange(len(ds),dtype=float); width=.24
    for vi,v in enumerate(VARIANTS):
        vals=[np.mean([float(summary_index[(f'{d}_alpha{int(a*100):03d}',v)]['mean_runtime_seconds']) for a in ALPHAS]) for d in ds]
        ax.bar(x+(vi-1)*width,vals,width,label=LABELS[v], color=CB_COLORS[v])
    ax.set_title('Optimization runtime by portfolio size',loc='left',pad=12)
    ax.set_xlabel('OR-Library dataset (number of assets)')
    ax.set_ylabel('Mean runtime per 30,000-evaluation run (seconds)')
    ax.set_xticks(x,[f'{d}\n(n={EXPECTED_SIZES[d]})' for d in ds])
    _set_zero_baseline(ax, y=True)
    _set_even_numeric_ticks(ax, ybins=6)
    _style_plot(ax)
    ax.legend(title='ES variant',frameon=False,fontsize=9)
    _explain(fig,'Average across 3 return targets and 10 seeds per method; timings reflect the recorded execution environment.')
    target=figure_dir/'overview_mean_runtime.png'
    _finish(fig,target);figures.append(target)

    # Allocation weights: only meaningful (>1e-6) weights among the top 15.
    # Avoid implying invisible near-zero bars are informative.
    for d in ('port1','port3','port5'):
        case=f'{d}_alpha050'
        rr=min((r for r in results if r['case']==case),key=lambda row:float(row['variance']))
        with np.load(out/rr['raw_file'],allow_pickle=False) as obj:
            w=np.asarray(obj['best_weights'],dtype=float)
        indices=np.argsort(w)[::-1]
        display=indices[:15][w[indices[:15]]>1e-6]
        if not len(display):
            raise ValueError(f'No nonzero allocation weights in {case}')
        disp=display[::-1]
        labels=[f'Asset {int(i)+1}' for i in disp]
        vals=w[disp]*100
        fig,ax=plt.subplots(figsize=(10,6.3))
        bars=ax.barh(labels,vals, color=CB_COLORS['one_plus_one'])
        ax.set_title(f'Largest portfolio allocations | {case}',loc='left',pad=13)
        ax.set_xlabel('Share of total portfolio budget (%)')
        ax.set_ylabel('Asset ID (OR-Library, 1-based index)')
        ax.set_xlim(0,max(vals)*1.17)
        _set_zero_baseline(ax, x=True, y=False)
        _set_even_numeric_ticks(ax, xbins=6, ybins=None)
        for bar,value in zip(bars,vals):
            ax.text(bar.get_width()+max(vals)*.013,bar.get_y()+bar.get_height()/2,
                    f'{value:.2f}%',va='center',ha='left',fontsize=9)
        _style_plot(ax,grid='x')
        remainder=float(np.sum(w[np.setdiff1d(np.arange(len(w)),display)]))*100
        note=(f'Best observed among 3 ES methods × 10 seeds: {LABELS[rr["variant"]]}, seed {rr["seed"]}. '
              f'Shown: {len(display)} of {len(w)} assets; others sum to {remainder:.4f}% of budget.')
        _explain(fig,note)
        target=figure_dir/'best_allocations'/f'{case}_top15_weights.png'
        _finish(fig,target);figures.append(target)

    audit={
      'dataset':'Original five OR-Library files supplied in user upload',
      'runs_checked':len(results),
      'summary_rows':len(summary),
      'evaluations_per_run':budget,
      'all_recorded_runs_feasible':all(str(r['valid']).lower()=='true' for r in results),
      'all_recomputed_allocations_feasible':len(failures)==0,
      'all_npz_histories_contain_exact_budget':True,
      'all_archives_monotone_nonincreasing':True,
      'case_variant_groups':len(run_index),
      'figures_added':len(figures),
      'csv_exports':['best_allocations_all_runs.csv','convergence_sampled_all_runs.csv','run_diagnostics.csv'],
      'note':'These supplemental plots are descriptive; the original mandatory port5_alpha050 plot remains unchanged.'
    }
    (readable/'validation_summary.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(f'Validated {len(results)} runs from original .npz archives; {len(figures)} supplementary figures generated.')
    print(f'Figures: {figure_dir}\nReadable CSV exports: {readable}')
    return audit


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=DEFAULT_OUT,help='Existing results folder')
    p.add_argument('--budget',type=int,default=30_000)
    p.add_argument('--step',type=int,default=100,help='Sampling stride for readable convergence CSV and plotting')
    p.add_argument('--allow-incomplete',action='store_true')
    args=p.parse_args()
    build_visuals(args.out,budget=args.budget,step=args.step,strict=not args.allow_incomplete)


if __name__=='__main__':
    main()
