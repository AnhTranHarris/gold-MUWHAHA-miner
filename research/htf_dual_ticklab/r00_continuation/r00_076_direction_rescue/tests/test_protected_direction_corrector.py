import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import numpy as np
from protected_direction_corrector import preserve_and_correct,paired_direction_score

def test_same_events_side_only():
    q=np.array([4,6,8]); t=np.array([100,110,120]); ids=np.array(['e1','e2','e3']); base=np.array([1,1,-1])
    dec=preserve_and_correct(ids,q,t,base,[.2,.8,.7],[.7,.1,.2])
    assert dec.event_id.tolist()==ids.tolist()
    assert dec.source_quote_index.tolist()==q.tolist()
    assert dec.event_time_ms.tolist()==t.tolist()
    assert dec.side.tolist()==[-1,1,1]
    assert dec.was_flipped.tolist()==[True,False,True]
    stat=paired_direction_score(base,dec,np.array([-1,1,0]))
    assert stat['rescued']==1 and stat['damaged']==0 and stat['neutral_flipped']==1
    assert stat['emitted']==stat['opportunities']==3

def test_never_stand_aside_and_ties_keep_original_side():
    base=np.array([-1,1]); dec=preserve_and_correct([0,1],[1,2],[1,2],base,[.5,.5],[.5,.5])
    assert dec.side.tolist()==base.tolist()
    stat=paired_direction_score(base,dec,np.array([0,0]))
    assert stat['emitted']==2 and stat['corrected_correct']==0

def test_threshold_only_affects_direction_never_event_supply():
    dec=preserve_and_correct([0,1],[1,2],[1,2],[1,-1],[.4,.9],[.6,.1],advantage_threshold=.5)
    assert dec.side.tolist()==[1,1] and len(dec.side)==2

def test_invalid_probabilities_fail_closed():
    try:preserve_and_correct([1],[1],[1],[1],[.9],[.8])
    except ValueError:pass
    else:raise AssertionError('over-summed three-class probabilities accepted')
