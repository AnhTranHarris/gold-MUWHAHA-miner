import numpy as np
from fullmonth_oracle_optimization import choose, Experiment
from h1v2_teacher import schedule_oracle

def test_count_equal_immutable_original_dp():
    entries=np.array([1,3,5,7,9,11,13],np.int64)
    c=np.array([[1,-1],[1,1],[1,0],[1,1],[0,-1],[1,1],[-1,1]],np.int8)
    net=np.array([[.1,-1],[.4,.1],[.3,-1],[.8,.2],[-1,-1],[.2,.1],[-1,.6]],np.float32)
    exits=np.array([[5,5],[7,7],[10,9],[13,13],[15,15],[14,14],[15,15]],np.int64)
    ix,s,rec=schedule_oracle(entries,c,net,exits)
    got,side,v,allowed=choose(entries,c,net,exits,np.full_like(exits,3000),np.full(len(entries),.5),Experiment('baseline','MAX_COUNT'))
    assert np.array_equal(ix,got)
    assert np.array_equal(s,np.where(side==0,1,-1))
    assert len(ix)==rec['trades']
    assert abs(v-rec['sum_net'])<1e-5

def test_max_net_rejects_count_tiebreak_stressor():
    entries=np.array([10,20,30],np.int64)
    code=np.ones((3,2),np.int8)
    net=np.array([[.1,.2],[.1,.1],[.8,.7]],np.float32)
    exits=np.array([[20,20],[35,35],[40,40]],np.int64)
    rows,which,total,allowed=choose(entries,code,net,exits,np.full((3,2),2000),np.full(3,.5),Experiment('maxnet','MAX_NET'))
    assert np.all(entries[rows[1:]]>exits[rows[:-1],which[:-1]]) if len(rows)>1 else True
    assert np.isclose(total,np.sum(net[rows,which]),atol=1e-6)

def test_future_censored_never_selected():
    entries=np.array([10,12,14],np.int64)
    code=np.array([[1,0],[0,1],[1,1]],np.int8)
    net=np.array([[np.nan,-1.],[-1,.3],[.2,.4]],np.float32)
    exits=np.array([[-1,-1],[-1,16],[17,17]],np.int64)
    rows,which,v,allowed=choose(entries,code,net,exits,np.full((3,2),1000),np.full(3,.5),Experiment('safe','MAX_COUNT'))
    assert not allowed[0].any()
    assert np.all(np.isfinite(net[rows,which]))
