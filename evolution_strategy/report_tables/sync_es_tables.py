# AI-generated utility: Group 7 must review and validate before use.
"""Refresh numeric ES table rows from a verified 45-case CSV; preserve captions and labels."""
import argparse
import csv
import math
import shutil
from pathlib import Path

VARIANTS = ('one_plus_one', 'ten_plus_seventy', 'ten_comma_seventy')
LABELS = dict(zip(VARIANTS, ('$(1+1)$-ES', '$(10+70)$-ES', '$(10,70)$-ES')))
DATASETS = tuple(f'port{i}' for i in range(1,6))
ALPHAS = (.25,.5,.75)

def sync(source, root):
    with source.open(newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    data = {(r['dataset'],float(r['alpha']),r['variant']):r for r in rows}
    expected = {(d,a,v) for d in DATASETS for a in ALPHAS for v in VARIANTS}
    if len(rows)!=45 or set(data)!=expected:
        raise ValueError('Expected exactly 45 unique experiment cases')
    for (d,a,v), r in data.items():
        if int(r['num_runs'])!=10 or int(r['evaluations_per_run'])!=30000:
            raise ValueError(f'Incorrect run protocol: {d,a,v}')
        if not all(math.isfinite(float(r[k])) for k in ('target_return','best_variance','mean_variance','std_variance','feasible_rate_percent','mean_runtime_seconds')):
            raise ValueError(f'Non-finite data: {d,a,v}')
    def num(x, fmt='.9g'):
        return r'\num{'+format(float(x),fmt)+'}'
    def write(name, lines):
        p=root/'tables'/name
        old=p.read_text(encoding='utf-8')
        start=old.index(r'\midrule')+len(r'\midrule')
        end=old.index(r'\bottomrule',start)
        p.write_text(old[:start]+'\n'+'\n'.join(lines)+'\n'+old[end:],encoding='utf-8')
    def row(*items):
        return ' & '.join(map(str,items))+r'\\'
    for d in DATASETS:
        lines=[]
        for a in ALPHAS:
            if lines: lines.append(r'\addlinespace[2pt]')
            for v in VARIANTS:
                r=data[d,a,v]
                lines.append(row(r'\texttt{'+d+r'\_alpha'+f'{int(a*100):03d}'+'}',LABELS[v],r['num_assets'],f"{float(r['target_return']):.7f}",num(r['best_variance']),num(r['mean_variance']),num(r['std_variance'],'.3g'),f"{float(r['feasible_rate_percent']):g}",f"{float(r['mean_runtime_seconds']):.2f}"))
        write(f'es_{d}.tex',lines)
    lines=[]
    for d in DATASETS:
        r=data[d,.5,VARIANTS[0]]
        lines.append(row(r'\texttt{'+d+'}',r['num_assets'],f"{float(r['target_return']):.7f}",*(num(data[d,.5,v]['mean_variance']) for v in VARIANTS)))
    write('es_alpha050.tex',lines)
    lines=[]
    for v in VARIANTS:
        r=data['port5',.5,v]
        lines.append(row(LABELS[v],num(r['best_variance']),num(r['mean_variance']),num(r['std_variance']),f"{float(r['feasible_rate_percent']):g}"+r'\%',f"{float(r['mean_runtime_seconds']):.2f}"))
    write('es_port5_focus.tex',lines)
    (root/'data').mkdir(parents=True, exist_ok=True)
    destination = root/'data'/'es_summary_source.csv'
    if source.resolve() != destination.resolve():
        shutil.copyfile(source, destination)
    print('Updated seven active LaTeX tables and source CSV; no report prose changed.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv',type=Path)
    p.add_argument('latex_root',type=Path)
    a=p.parse_args()
    sync(a.csv,a.latex_root)
