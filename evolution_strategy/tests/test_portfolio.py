"""Tests for project formulas."""
from pathlib import Path
import numpy as np
import pytest
from problem2_es.src.portfolio import load_portfolio,project_simplex,repair

FIXTURE = Path(__file__).parent/"fixtures"/"synthetic3.txt"


def test_parse_and_covariance():
    p=load_portfolio(FIXTURE,expected_n=3)
    assert p.n==3
    assert np.allclose(np.diag(p.covariance),[0.01,0.04,0.09])
    assert np.allclose(p.correlation,np.eye(3))


def test_explanatory_variance_and_return():
    p=load_portfolio(FIXTURE,expected_n=3)
    a=np.array([0.50,0.30,0.20]); b=np.array([0.60,0.30,0.10])
    assert p.variance(a)==pytest.approx(0.0097)
    assert p.variance(b)==pytest.approx(0.0081)
    assert p.expected_return(a)==pytest.approx(0.048)
    assert p.expected_return(b)==pytest.approx(0.040)


def test_targets():
    p=load_portfolio(FIXTURE,expected_n=3)
    assert p.equal_return==pytest.approx(0.06)
    assert p.target(0.5)==pytest.approx(0.08)
    assert p.target(0.25)==pytest.approx(0.07)


@pytest.mark.parametrize("z",[[1,1,1],[-1,2,3],[2,-10,1],[-5,-5,-5],[0.2,0.1,0.7]])
def test_simplex_projection(z):
    w=project_simplex(np.array(z,dtype=float))
    assert np.min(w)>=-1e-12
    assert w.sum()==pytest.approx(1,abs=1e-12)


def test_return_repair_example():
    p=load_portfolio(FIXTURE,expected_n=3)
    w=repair(np.array([1.0,0,0]),p,target=0.08)
    assert np.allclose(w,[0.25,0.0,0.75],atol=1e-12)
    assert p.validate(w,0.08)


def test_return_repair_random():
    p=load_portfolio(FIXTURE,expected_n=3)
    rng=np.random.default_rng(9)
    for alpha in (0.25,0.50,0.75):
        for _ in range(50):
            w=repair(rng.normal(size=3),p,p.target(alpha))
            assert p.validate(w,p.target(alpha))


def test_duplicate_and_missing_correlation_rejected(tmp_path):
    fixture=FIXTURE.read_text()
    broken=tmp_path/"broken.txt"
    broken.write_text(fixture.replace("2 3 0","1 2 0"))
    with pytest.raises(ValueError,match="Duplicate"):
        load_portfolio(broken)
    broken.write_text("\n".join(fixture.splitlines()[:-1])+"\n")
    with pytest.raises(ValueError,match="record count"):
        load_portfolio(broken)


def test_repair_impossible_target():
    p=load_portfolio(FIXTURE)
    with pytest.raises(ValueError,match="greater"):
        repair(np.array([1.0,0,0]),p,0.30)
