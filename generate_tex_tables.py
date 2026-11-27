"""Generate standalone LaTeX report tables for Problem 1 (BA) and Problem 2 (ES).

Reads the saved summary CSV files from both subprojects and writes complete
LaTeX table files into ``tex_tables/`` at the repository root (gitignored).

Run from the repository root:
    python generate_tex_tables.py
"""

import csv
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "tex_tables"

BA_TSP_CSV = (
    ROOT_DIR
    / "bees_algorithm"
    / "results"
    / "part_a_tsp"
    / "tables"
    / "summary_tsp.csv"
)
BA_CONTINUOUS_CSV = (
    ROOT_DIR
    / "bees_algorithm"
    / "results"
    / "part_b_continuous"
    / "tables"
    / "summary_continuous.csv"
)
ES_SUMMARY_CSV = (
    ROOT_DIR
    / "evolution_strategy"
    / "results"
    / "es_summary_45_cases.csv"
)

ES_VARIANTS = ("one_plus_one", "ten_plus_seventy", "ten_comma_seventy")
ES_LABELS = dict(
    zip(ES_VARIANTS, ("$(1+1)$-ES", "$(10+70)$-ES", "$(10,70)$-ES"))
)
ES_DATASETS = tuple(f"port{i}" for i in range(1, 6))
ES_ALPHAS = (0.25, 0.50, 0.75)


def _num(value: str | float, fmt: str = ".9g") -> str:
    return r"\num{" + format(float(value), fmt) + "}"


def _row(*items: object) -> str:
    return " & ".join(map(str, items)) + r"\\"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _render_table(
    *,
    caption: str,
    label: str,
    col_spec: str,
    header: str,
    body_lines: list[str],
    size: str = r"\footnotesize",
    resize: bool = True,
) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        size,
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
    ]
    if resize:
        lines.append(r"\resizebox{\linewidth}{!}{%")
    lines.extend(
        [
            rf"\begin{{tabular}}{{{col_spec}}}",
            r"\toprule",
            header + r"\\",
            r"\midrule",
            *body_lines,
            r"\bottomrule",
            r"\end{tabular}" + ("%" if resize else ""),
        ]
    )
    if resize:
        lines.append("}")
    lines.append(r"\end{table}")
    return "\n".join(lines) + "\n"


def generate_ba_tsp_table(
    source: Path = BA_TSP_CSV, output_dir: Path = OUTPUT_DIR
) -> Path | None:
    """Generate the Problem 1 Part A (TSP) summary LaTeX table."""
    if not source.exists():
        print(f"Skipping BA TSP table (missing {source})")
        return None

    rows = _read_csv(source)
    body_lines: list[str] = []
    previous_instance: str | None = None

    for r in rows:
        numeric_fields = (
            "best",
            "mean",
            "std",
            "mean_gap_pct",
            "mean_runtime_sec",
        )
        if not all(math.isfinite(float(r[k])) for k in numeric_fields):
            raise ValueError(f"Non-finite BA TSP data: {r}")

        instance = r["instance"]
        if previous_instance is not None and instance != previous_instance:
            body_lines.append(r"\addlinespace[2pt]")
        previous_instance = instance

        body_lines.append(
            _row(
                rf"\texttt{{{instance}}}",
                r["cities"],
                r["optimum"],
                rf"\texttt{{{r['neighbourhood']}}}",
                f"{r['valid_runs']}/{r['runs']}",
                f"{float(r['best']):.0f}",
                f"{float(r['mean']):.2f}",
                f"{float(r['std']):.2f}",
                f"{float(r['mean_gap_pct']):.2f}",
                f"{float(r['mean_runtime_sec']):.3f}",
            )
        )

    content = _render_table(
        caption=(
            "Problem 1 Part A (TSP) Bees Algorithm summary over ten runs per "
            "instance and neighbourhood (30,000 evaluations per run)."
        ),
        label="tab:ba-tsp",
        col_spec="lrrlcrrrrr",
        header=(
            r"Instance & Cities & $L^*$ & Neighbourhood & Valid & "
            r"Best & Mean & SD & Mean gap (\%) & Mean time (s)"
        ),
        body_lines=body_lines,
        size=r"\footnotesize",
        resize=True,
    )

    destination = output_dir / "ba_tsp.tex"
    destination.write_text(content, encoding="utf-8")
    return destination


def generate_ba_continuous_table(
    source: Path = BA_CONTINUOUS_CSV, output_dir: Path = OUTPUT_DIR
) -> Path | None:
    """Generate the Problem 1 Part B (Continuous) summary LaTeX table."""
    if not source.exists():
        print(f"Skipping BA continuous table (missing {source})")
        return None

    rows = _read_csv(source)
    body_lines: list[str] = []
    previous_function: str | None = None

    for r in rows:
        numeric_fields = ("best", "mean", "std", "mean_runtime_sec")
        if not all(math.isfinite(float(r[k])) for k in numeric_fields):
            raise ValueError(f"Non-finite BA continuous data: {r}")

        func = r["function"]
        if previous_function is not None and func != previous_function:
            body_lines.append(r"\addlinespace[2pt]")
        previous_function = func

        body_lines.append(
            _row(
                rf"\texttt{{{func}}}",
                r["dimension"],
                f"{r['valid_runs']}/{r['runs']}",
                _num(r["best"], ".4g"),
                _num(r["mean"], ".4g"),
                _num(r["std"], ".4g"),
                f"{float(r['mean_runtime_sec']):.3f}",
            )
        )

    content = _render_table(
        caption=(
            "Problem 1 Part B (Continuous Function Optimization) Bees "
            "Algorithm summary over ten runs per function and dimension "
            "(30,000 evaluations per run)."
        ),
        label="tab:ba-continuous",
        col_spec="lrcrrrr",
        header=(
            r"Function & $D$ & Valid & Best & Mean & SD & Mean time (s)"
        ),
        body_lines=body_lines,
        size=r"\small",
        resize=False,
    )

    destination = output_dir / "ba_continuous.tex"
    destination.write_text(content, encoding="utf-8")
    return destination


def generate_es_tables(
    source: Path = ES_SUMMARY_CSV, output_dir: Path = OUTPUT_DIR
) -> list[Path]:
    """Generate all seven Problem 2 (ES) LaTeX tables from the 45-case CSV."""
    if not source.exists():
        print(f"Skipping ES tables (missing {source})")
        return []

    rows = _read_csv(source)
    data = {(r["dataset"], float(r["alpha"]), r["variant"]): r for r in rows}
    expected = {
        (d, a, v) for d in ES_DATASETS for a in ES_ALPHAS for v in ES_VARIANTS
    }
    if len(rows) != 45 or set(data) != expected:
        raise ValueError("Expected exactly 45 unique ES experiment cases")

    numeric_fields = (
        "target_return",
        "best_variance",
        "mean_variance",
        "std_variance",
        "feasible_rate_percent",
        "mean_runtime_seconds",
    )
    for key, r in data.items():
        if int(r["num_runs"]) != 10 or int(r["evaluations_per_run"]) != 30000:
            raise ValueError(f"Incorrect ES run protocol: {key}")
        if not all(math.isfinite(float(r[k])) for k in numeric_fields):
            raise ValueError(f"Non-finite ES data: {key}")

    generated: list[Path] = []

    # Five complete per-dataset tables (port1..port5)
    for d in ES_DATASETS:
        body_lines: list[str] = []
        for a in ES_ALPHAS:
            if body_lines:
                body_lines.append(r"\addlinespace[2pt]")
            for v in ES_VARIANTS:
                r = data[d, a, v]
                case_tex = (
                    r"\texttt{" + d + r"\_alpha" + f"{int(a * 100):03d}" + "}"
                )
                body_lines.append(
                    _row(
                        case_tex,
                        ES_LABELS[v],
                        r["num_assets"],
                        f"{float(r['target_return']):.7f}",
                        _num(r["best_variance"]),
                        _num(r["mean_variance"]),
                        _num(r["std_variance"], ".3g"),
                        f"{float(r['feasible_rate_percent']):g}",
                        f"{float(r['mean_runtime_seconds']):.2f}",
                    )
                )

        content = _render_table(
            caption=(
                rf"Complete required ES results for \texttt{{{d}}}; "
                "each row summarizes ten runs. Variance and SD are in "
                "squared decimal-return units."
            ),
            label=f"tab:es-{d}",
            col_spec="llrrrrrrr",
            header=(
                r"Case & ES variant & $n$ & $R_{\min}$ & Best variance & "
                r"Mean variance & SD (pop.) & Feasible (\%) & Mean time (s)"
            ),
            body_lines=body_lines,
            size=r"\footnotesize",
            resize=True,
        )
        dest = output_dir / f"es_{d}.tex"
        dest.write_text(content, encoding="utf-8")
        generated.append(dest)

    # Cross-dataset comparison at alpha = 0.50
    mid_lines: list[str] = []
    for d in ES_DATASETS:
        r = data[d, 0.50, ES_VARIANTS[0]]
        mid_lines.append(
            _row(
                rf"\texttt{{{d}}}",
                r["num_assets"],
                f"{float(r['target_return']):.7f}",
                *(_num(data[d, 0.50, v]["mean_variance"]) for v in ES_VARIANTS),
            )
        )

    mid_content = _render_table(
        caption=(
            r"Mean final feasible variance over ten seeds at $\alpha=0.50$. "
            "Comparisons should be made within a dataset."
        ),
        label="tab:es-mid-target",
        col_spec="lrrrrr",
        header=r"Dataset & $n$ & $R_{\min}$ & $(1+1)$ & $(10+70)$ & $(10,70)$",
        body_lines=mid_lines,
        size=r"\small",
        resize=False,
    )
    mid_dest = output_dir / "es_alpha050.tex"
    mid_dest.write_text(mid_content, encoding="utf-8")
    generated.append(mid_dest)

    # Focused port5_alpha050 comparison table
    focus_lines: list[str] = []
    for v in ES_VARIANTS:
        r = data["port5", 0.50, v]
        focus_lines.append(
            _row(
                ES_LABELS[v],
                _num(r["best_variance"]),
                _num(r["mean_variance"]),
                _num(r["std_variance"]),
                f"{float(r['feasible_rate_percent']):g}" + r"\%",
                f"{float(r['mean_runtime_seconds']):.2f}",
            )
        )

    focus_content = _render_table(
        caption=(
            r"Summary of \texttt{port5\_alpha050} outcomes ($n=225$, ten "
            "seeds, 30,000 evaluations per run). SD is the population "
            "standard deviation over final archive-best variances."
        ),
        label="tab:es-port5-focus",
        col_spec="lrrrrr",
        header=(
            r"Variant & Best variance & Mean variance & SD & Feasible & "
            r"Time (s)"
        ),
        body_lines=focus_lines,
        size=r"\small",
        resize=False,
    )
    focus_dest = output_dir / "es_port5_focus.tex"
    focus_dest.write_text(focus_content, encoding="utf-8")
    generated.append(focus_dest)

    return generated


def generate_all_tex_tables(output_dir: Path = OUTPUT_DIR) -> list[Path]:
    """Generate all Problem 1 (BA) and Problem 2 (ES) LaTeX tables."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    tsp_table = generate_ba_tsp_table(output_dir=output_dir)
    if tsp_table is not None:
        generated.append(tsp_table)

    cont_table = generate_ba_continuous_table(output_dir=output_dir)
    if cont_table is not None:
        generated.append(cont_table)

    generated.extend(generate_es_tables(output_dir=output_dir))

    print(f"Generated {len(generated)} LaTeX tables in {output_dir}:")
    for path in generated:
        print(f"  - {path.name}")
    return generated


if __name__ == "__main__":
    generate_all_tex_tables()
