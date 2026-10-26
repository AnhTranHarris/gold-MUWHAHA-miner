import numpy as np
from f408_causal_event_hazard import features,GRACE_MS

def run():
 t=np.arange(100,dtype=np.int64)*5000+1_000_000
 side=np.where(np.arange(100)%3==0,1,-1).astype(np.int8)
 truth=(np.arange(100)%3).astype(np.int8)
 a,n,end=features(t,side,truth)
 assert np.all(end<=np.arange(len(t)))
 for k in (3,20,65):
  changed=truth.copy();changed[k:]=(changed[k:]+1)%3
  b,nn,ee=features(t,side,changed)
  assert n==nn and np.array_equal(a[:k],b[:k])
  changed=truth.copy();changed[k]=2 if changed[k]!=2 else 0
  b,_,_=features(t,side,changed)
  assert np.array_equal(a[:k+1],b[:k+1])
 # No same-millisecond later event side/label affects an earlier row.
 t2=t.copy();t2[41]=t2[40]
 a,_,_=features(t2,side,truth)
 side2=side.copy();side2[41]*=-1
 truth2=truth.copy();truth2[41]=(truth2[41]+1)%3
 b,_,_=features(t2,side2,truth2)
 assert np.array_equal(a[:41],b[:41])
 # Last observed class must be at least 33.002s old.
 assert np.all(t[end[end>0]-1]<=t[np.nonzero(end>0)[0]]-GRACE_MS)
 print('PASS: four causal invariance classes; 100 synthetic events')
if __name__=='__main__':run()
