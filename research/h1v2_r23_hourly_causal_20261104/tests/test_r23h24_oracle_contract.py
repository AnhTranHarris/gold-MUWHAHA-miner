import numpy as np
from r23h24_held_hindsight_oracle import greedy_intervals,best_lanes

def test_earliest_real_exit_nonoverlap_even_at_same_millisecond():
    t=np.array([0,100,200,200,400,500],dtype=np.int64)
    fill=np.array([0,0,3,4],dtype=np.int32)
    ends=np.array([4,2,5,5],dtype=np.int32)
    group=np.zeros(4,dtype=np.int32)
    order=np.argsort(ends,kind='stable').astype(np.int32)
    selected,counts=greedy_intervals(order,fill,ends,group,t,1)
    # The shorter first interval wins; a same-millisecond fill at t=200
    # cannot enter on the closing source event t=200.
    assert selected.tolist()==[1,3]
    assert counts.tolist()==[2]

def test_future_held_oracle_does_not_upgrade_unfilled_or_censored():
    t=np.array([0,100,200,500,1000,15100,30500,60100,61000],dtype=np.int64)
    n=3
    fill=np.array([1,3,-1],dtype=np.int32)
    label=np.full((n,2,3),2,dtype=np.int8)
    held=np.zeros((n,2,3),dtype=np.int8)
    end=np.full((n,3),8,dtype=np.int32)
    label[0,0,0]=1;held[0,0,0]=1;end[0,0]=5
    label[1,1,1]=1;held[1,1,1]=1;end[1,1]=6
    label[2,0,0]=1;held[2,0,0]=1
    ix,ends,side,hz=best_lanes({'f':fill,'l':label,'held':held,'end_ix':end},'EARLIEST_QUALIFYING_H15_H30_H60',t)
    assert ix.tolist()==[0,1]
    assert ends.tolist()==[5,6]
    assert side.tolist()==[0,1]
    assert hz.tolist()==[0,1]
