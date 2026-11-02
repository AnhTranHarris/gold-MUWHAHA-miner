import sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from r9_side_competing import unpack,augment,admission

def enc(trends=(1,1,1,1), spread=3,rate=2,sess=1,eff=2):
 tr=sum((v+1)*(3**i) for i,v in enumerate(trends))
 return ((((tr*5+spread)*4+rate)*4+sess)*3+eff)

def test_regime_roundtrip():
 a=unpack(np.array([enc(),enc((-1,0,1,-1),0,0,0,0)],dtype='int32'))
 assert a.shape==(2,12)
 assert np.array_equal(a[0,:8],[1,1,1,1,3,2,1,2])
 assert np.array_equal(a[1,:8],[-1,0,1,-1,0,0,0,0])

def test_augments_without_future():
 x=np.ones((2,41),np.float16)
 out=augment(x,np.array([enc(),enc((-1,0,1,-1))]))
 assert out.shape==(2,53) and np.all(out[:,:41]==1)

def test_np_suppresses_bad_neutral():
 p=np.array([[[.1,.1,.8],[.8,.1,.1]],[[.8,.1,.1],[.1,.1,.8]],[[.4,.4,.2],[.4,.4,.2]]])
 score,side,margin=admission(p)
 assert np.array_equal(side,[0,1,0]);assert score[0]>score[2] and score[1]>score[2]
 assert margin[2]==0

def test_no_hindsight_dependency():
 p=np.array([[[.3,.2,.5],[.7,.2,.1]]])
 a=admission(p)
 # future truth is never an argument to admission
 for z in a:assert np.all(np.isfinite(z))

def test_ordinal_replay_rejects_overlap_and_does_not_cherrypick():
 from r9_side_competing import _replay_ordinal_selected
 rows=np.arange(4,dtype='int64');side=np.zeros(4,dtype='int8')
 ix=np.array([0,2,4,12],dtype='int64')
 exits=np.array([[6,6],[4,4],[8,8],[16,16]],dtype='int64')
 net=np.array([[-.50,-.50],[1,1],[.4,.4],[-.3,-.3]],dtype='float32')
 c=np.array([[-1,-1],[1,1],[1,1],[0,0]],dtype='int8')
 t=_replay_ordinal_selected(rows,side,ix,exits,net,c)
 assert t[:5]==(2,0,1,1,0)
 assert abs(t[-1]+.8)<1e-5
