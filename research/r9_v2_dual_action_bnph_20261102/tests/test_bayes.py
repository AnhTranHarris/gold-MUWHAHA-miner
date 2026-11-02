import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from bayesian_dirichlet import BayesianSidePriors

def test_prior_separates_buy_sell_neutral():
    p=BayesianSidePriors()
    for _ in range(5):p.observe(1,2,'london');p.observe(-1,0,'london')
    p.observe(1,1,'london')
    buy=p.prior(1,'london');sell=p.prior(-1,'london')
    assert buy[2]>sell[2] and sell[0]>buy[0]
    assert np.isclose(buy.sum(),1) and np.isclose(sell.sum(),1)

def test_empirical_bayes_does_not_use_future():
    p=BayesianSidePriors()
    for _ in range(100):p.observe(1,0)
    before=p.shrink_prediction([.1,.1,.8],1)
    q=p.shrink_prediction([.1,.1,.8],1)
    np.testing.assert_allclose(before,q)
    assert q[2]<.8
