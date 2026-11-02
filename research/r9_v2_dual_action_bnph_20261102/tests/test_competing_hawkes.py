import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from competing_hawkes import CompetingQuoteHawkes

def test_hawkes_causal_and_bid_ask_difference():
    h=CompetingQuoteHawkes()
    h.observe(0,100.,100.2)
    h.observe(250,100.05,100.2) # bid-only upward
    z=h.features()
    assert z['lambda_channels'][0]>z['lambda_channels'][1]
    h.observe(500,100.05,100.26) # ask-only upward
    q=h.features()
    assert q['lambda_channels'][2]>q['lambda_channels'][3]
    assert q['fitted'] is False

def test_hawkes_no_future_prefix_change():
    a=CompetingQuoteHawkes();b=CompetingQuoteHawkes()
    for t,p in [(0,100.),(250,100.02),(500,100.04)]:
        a.observe(t,p,p+.2);b.observe(t,p,p+.2)
    before=b.features()
    a.observe(750,99.,99.3)
    np.testing.assert_allclose(before['lambda_channels'],b.features()['lambda_channels'])

def test_hawkes_stability_and_spread_gate():
    h=CompetingQuoteHawkes()
    h.observe(0,100.,100.005);h.observe(500,100.01,100.015)
    assert h.intensities()[5]==0.
    for i in range(500):h.observe(1000+i*250,100+i*.0001,100.05+i*.0001)
    assert np.isfinite(h.intensities()).all()
