"""R23 adversarial source-ordinal and future-knowledge leakage unit controls."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r23_dualbroker/src')
import r23_geometry_and_causal_controls as r


def test_true_bidask_profit_and_fee_buy_sell():
    t=np.array([0,100,200,300,40000,40100],np.int64)
    b=np.array([1000,1080,1080,1100,1100,1100],np.int32)
    a=np.array([1020,1100,1100,1120,1120,1120],np.int32)
    code,ex,net=r.quote_first_passages(t,b,a,np.array([0],np.int32),50,100,30000,0)
    assert code[0,0]==1 and ex[0,0]==3 and net[0,0]==60  # 1100 - 1020 - 20 = +60 raw


def test_stop_includes_original_spread_and_fee():
    t=np.array([0,100,250,40000],np.int64)
    b=np.array([1000,899,899,899],np.int32)
    a=np.array([1150,1049,1049,1049],np.int32)
    code,ex,net=r.quote_first_passages(t,b,a,np.array([0],np.int32),100,100,30000,0)
    assert code[0,0]==0 and ex[0,0]==1
    assert net[0,0]==899-1150-20  # loss -251 raw with spread 150


def test_source_gap_is_censor_not_loss_or_win():
    t=np.array([0,100,20000,21000,70000],np.int64)
    b=np.array([1000,1100,1250,1250,1250],np.int32)
    a=b+30
    code,ex,net=r.quote_first_passages(t,b,a,np.array([0],np.int32),100,100,60000,0)
    assert code[0,0]==-3 and ex[0,0]==-1


def test_prefix_features_do_not_see_future_mutations():
    t=np.array([0,1000,3000,5000,11000,16000,90000,120000,130000,160000,190000,210000,250000,310000],np.int64)
    b=np.arange(len(t),dtype=np.int32)*15+1000
    a=b+np.arange(len(t),dtype=np.int32)+25
    signal=np.array([3,5],np.int32)
    f=r.causal_prefix_features(t,b,a,signal)
    b2=b.copy();a2=a.copy();b2[6:]+=5000;a2[6:]+=6000
    f2=r.causal_prefix_features(t,b2,a2,signal)
    for key in f:assert np.array_equal(f[key],f2[key])


def test_case_contracts_disjoint_and_risk_bounded():
    assert len({c[0] for c in r.CASES})==len(r.CASES)
    assert all(x[3]>0 and x[4]>0 and x[5]<=120000 and x[6]>=100 for x in r.CASES)


def test_true_timeout_quote_is_observed_and_negative_net():
    t=np.array([0,100,500,1000,15000,28000,30100,35000],np.int64)
    b=np.array([1000,1002,1004,1005,1005,1005,1006,1006],np.int32)
    a=b+25
    code,ex,net=r.quote_first_passages(t,b,a,np.array([0],np.int32),100,100,30000,0)
    assert code[0,0]==2 and ex[0,0]==6
    assert net[0,0]==1006-1025-20


def test_80pct_win_rate_may_be_economically_negative_at_wide_spread():
    # Exact maximum stop quote loss includes paid spread and $0.02 fee.
    spread=3157;stop=100;fee=20;tp=100
    break_even=(spread+stop+fee)/(spread+stop+fee+tp)
    assert break_even>.96
