"""ES selection, budget, feasibility and reproducibility tests.
"""
from pathlib import Path
import numpy as np
import pytest
from problem2_es.src.portfolio import load_portfolio
from problem2_es.src.evolution_strategies import run_es,VARIANTS,MU
from problem2_es.experiments.run_portfolio import generate_summary

P=load_portfolio(Path(__file__).parent/"fixtures"/"synthetic3.txt",expected_n=3)


@pytest.mark.parametrize("variant",VARIANTS)
@pytest.mark.parametrize("budget",[71,80,139,150,500])
def test_exact_budget_and_archive(variant,budget):
    res=run_es(P,0.5,variant,seed=123,budget=budget)
    assert res.evals==budget
    assert len(res.best_history)==budget
    assert res.feasible
    assert np.all(np.diff(res.best_history)<=1e-15)
    assert res.best_history[-1]==pytest.approx(res.best_variance)
    assert res.best_history[0]>=res.best_variance-1e-15
    assert res.best_variance<=res.initial_best+1e-15
    assert res.best_return>=P.target(0.5)-1e-8
    assert res.best_weights.sum()==pytest.approx(1.0,abs=1e-8)
    assert np.min(res.best_weights)>=-1e-8


@pytest.mark.parametrize("variant",VARIANTS)
def test_reproducible_for_a_seed(variant):
    a=run_es(P,0.75,variant,seed=4,budget=170)
    b=run_es(P,0.75,variant,seed=4,budget=170)
    assert np.array_equal(a.best_history,b.best_history)
    assert np.array_equal(a.best_weights,b.best_weights)


def test_plus_parent_best_never_worsens():
    r=run_es(P,0.5,"mu_plus_lambda",seed=2,budget=350)
    assert r.final_population_best==pytest.approx(r.best_variance)


def test_comma_archive_is_separate():
    # With non-elitist survivor selection, final population may be worse.
    result=run_es(P,0.5,"mu_comma_lambda",seed=7,budget=180)
    assert result.best_variance <= result.final_population_best+1e-15


def test_small_population_budget_rejected():
    with pytest.raises(ValueError):
        run_es(P,0.5,"mu_comma_lambda",seed=0,budget=MU-1)


def test_summary_valid_rate_mean():
    rows=[{"case":"port1_alpha025","dataset":"port1","n":"31","target":"0.01",
           "variant":"one_plus_one","seed":str(i),"budget":"30000", "valid":str(i!=2),
           "variance":str(0.01+i/100),"runtime_seconds":str(i+1)} for i in range(4)]
    summary=generate_summary(rows)[0]
    assert summary["runs"]==4 and summary["valid_runs"]==3
    assert summary["feasible_run_rate"]==pytest.approx(75)
    assert summary["mean_runtime_seconds"]==pytest.approx(2.5)
