import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from action_router import decide_actions,BUY,SELL,WAIT

def call(p,lower,**kw):
 n=len(p)
 shape=(n,2)
 return decide_actions(np.array(p),np.array(lower),np.full(shape,.5),np.full(shape,.5),
                       np.full(shape,.02),np.zeros(shape),np.zeros(shape),
                       np.full(n,.5),**kw)

def test_independent_eligibility_never_chooses_failed_high_prospect_side():
 # First side has highest raw GOOD, but inadequate calibrated confidence.
 p=[[[.02,.02,.96],[.06,.04,.90]]]
 r=call(p,[[.3,.91]],min_directional_margin=0.)
 assert r['action'].tolist()==[SELL]
 assert r['eligible'].tolist()==[[False,True]]

def test_wait_rejects_economically_negative_both_sides():
 p=[[[.5,.1,.4],[.45,.1,.45]]]
 r=call(p,[[.99,.99]],min_directional_margin=0.)
 assert r['action'].tolist()==[WAIT]

def test_good_positive_margin_action():
 p=[[[.05,.05,.90],[.5,.2,.3]]]
 r=call(p,[[.85,.01]])
 assert r['action'].tolist()==[BUY]

def test_spread_hard_veto_and_no_fake_posterior():
 p=[[[.01,.01,.98],[.5,.4,.1]]]
 r=decide_actions(p,[[.95,.1]],[[1.,1.]],[[.5,.5]],[[.1,.1]],[[0,0]],[[0,0]],[2.])
 assert r['action'].tolist()==[WAIT]
 with pytest.raises(ValueError):call([[[.2,.2,.8],[.5,.3,.2]]],[[.95,.95]])
