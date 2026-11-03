import numpy as np
from evaluate_fullmonth_student import replay_selected

def test_exact_ordinal_one_position_no_hindsight_skip_loser():
  rows=np.array([0,1,2,3],dtype=np.int64)
  dirs=np.array([0,1,1,0],dtype=np.int8)
  entries=np.array([10,12,21,30],dtype=np.int64)
  exits=np.array([[20,22],[19,14],[32,25],[34,36]],dtype=np.int64)
  pnl=np.array([[-.25,.6],[.3,.8],[-.7,-.55],[.25,.6]],dtype=np.float32)
  code=np.array([[-1,1],[1,1],[-1,-1],[1,1]],dtype=np.int8)
  first=np.array([[300,-1],[200,1000],[1000,2000],[1200,500]],dtype=np.int32)
  s,d,g,b,n,unknown,total,drawdown,first15=replay_selected(rows,dirs,entries,exits,pnl,code,first)
  assert np.array_equal(s,[0,2,3]) # first losing BUY occupies 10-20, so skip row 1
  assert np.array_equal(d,[0,1,0])
  assert (g,b,n,unknown,first15)==(1,2,0,0,1)
  assert np.isclose(total,-.55)
  assert drawdown>.25

def test_right_censored_source_entry_not_counted():
  r,d,g,b,n,u,total,dd,f15=replay_selected(
    np.array([0,1],np.int64),np.array([1,0],np.int8),
    np.array([0,2],np.int64),np.array([[4,-1],[5,6]],np.int64),
    np.array([[.3,np.nan],[.2,.5]],np.float32),
    np.array([[1,0],[1,1]],np.int8),np.array([[200,-1],[300,300]],np.int32))
  assert u==1 and len(r)==1 and r[0]==1 and g==1
