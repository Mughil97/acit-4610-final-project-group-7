"""Run a small synthetic portfolio test for all three ES variants.

Checks execution, feasibility, evaluation counts, and
best-so-far tracking without using the official datasets.
"""
from pathlib import Path
from ..src.portfolio import load_portfolio
from ..src.evolution_strategies import VARIANTS,run_es


def main():
    fixture=Path(__file__).resolve().parents[2]/"tests"/"fixtures"/"synthetic3.txt"
    portfolio=load_portfolio(fixture,expected_n=3)
    for variant in VARIANTS:
        result=run_es(portfolio,0.5,variant,seed=42,budget=500)
        assert result.evals==500 and result.feasible
        assert result.best_variance<=result.initial_best+1e-15
        print(f"Synthetic smoke: {variant:15s} evaluations={result.evals}, "
              f"best_variance={result.best_variance:.8f}, "
              f"return={result.best_return:.7f}, feasible={result.feasible}")
    print("Synthetic smoke tests passed. These values are NOT official benchmark results.")


if __name__=="__main__":
    main()
