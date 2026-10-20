import numpy as np
from same_event_arbiter import correct, paired_score

def test_identical_event_universe():
    d=correct([1,2,3],[100,200,300],[1000,2000,3000],[1,1,-1],[.1,.8,.7],[.8,.1,.2])
    assert d['event_id'].tolist()==[1,2,3]
    assert d['quote_index'].tolist()==[100,200,300]
    assert d['time_ms'].tolist()==[1000,2000,3000]
    assert d['side'].tolist()==[-1,1,1]

def test_neutral_wrong():
    d=correct([1],[100],[1000],[1],[.1],[.8])
    r=paired_score([1],d['side'],[0])
    assert r['emitted']==1 and r['candidate_correct']==0 and r['neutral_flips']==1

def test_rescue_and_damage():
    r=paired_score([1,-1,1],[-1,1,1],[-1,-1,1])
    assert r['rescued']==1 and r['damaged']==1 and r['net']==0

def test_ties_kept_no_abstention():
    d=correct([1,2],[100,200],[1000,2000],[1,-1],[.5,.5],[.5,.5])
    assert d['side'].tolist()==[1,-1]

def test_probability_guard():
    try: correct([1],[100],[1000],[1],[.9],[.8])
    except ValueError: pass
    else: raise AssertionError('must reject impossible posterior')
