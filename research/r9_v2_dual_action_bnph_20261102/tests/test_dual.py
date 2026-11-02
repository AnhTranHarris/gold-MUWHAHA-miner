import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from source_exact import two_views,labels,canonical,chronological_masks,load
from decision import Prediction,DualActionPolicy,Limits,select_dual,calibrate_np

def test_dual_view_symmetry():
    x=np.zeros((3,102),np.float32);x[:,1]=[1,2,3];x[:,0]=.5
    z=two_views(x,np.array([1,-1,1],np.int8))
    assert z.shape==(6,103)
    assert z[0,1]==1 and z[1,1]==-1 and z[2,1]==2 and z[3,1]==-2
    assert np.all(z[:,0]==.5)

def test_direction_can_reverse_after_wait():
    rule=DualActionPolicy(buy_threshold=.75,sell_threshold=.75,limits=Limits())
    a=Prediction(1,.89,.04,.07,.20);b=Prediction(-1,.33,.45,.22,-.10)
    assert rule.decide(a,b,.2)[0]==1
    a=Prediction(1,.31,.51,.18,-.10);b=Prediction(-1,.92,.03,.05,.26)
    assert rule.decide(a,b,.2)[0]==-1
    a=Prediction(1,.61,.17,.22,.05);b=Prediction(-1,.57,.21,.22,.05)
    assert rule.decide(a,b,.2)[0]==0

def test_np_fail_closed_and_independent_sides():
    th,r=calibrate_np(np.linspace(0,1,20),np.zeros(20),min_bad=150)
    assert np.isinf(th) and r['status']=='FAIL_CLOSED'
    p=np.array([[[.03,.07,.9],[.4,.2,.4]],[[.17,.02,.81],[.02,.03,.95]]])
    net=np.array([[.2,-.1],[.1,.2]])
    assert select_dual(p,net,[.7,.7]).tolist()==[1,-1]

def test_real_full_source_pairs_no_hindsight_in_views():
    d=load('coinexx','01')
    assert d['X'].shape[0]==414938
    assert np.array_equal(d['side'],np.where(d['side']>0,1,-1))
    z=two_views(d['X'][:3],d['side'][:3]);original=z.copy()
    d['good'][:3]=1-d['good'][:3]
    np.testing.assert_array_equal(original,two_views(d['X'][:3],d['side'][:3]))

def test_chronological_split():
    ts=np.arange(20,dtype=np.int64)*86400000+86400000
    tr,cal,chk,info=chronological_masks(ts)
    assert tr.any() and cal.any() and chk.any()
    assert ts[tr].max()<ts[cal].min()<ts[chk].min()

def test_outcome_reorder_original_sell():
    a=np.array([[1,0],[0,1]])
    s=np.array([-1,1])
    assert canonical(a,s).tolist()==[[0,1],[0,1]]
