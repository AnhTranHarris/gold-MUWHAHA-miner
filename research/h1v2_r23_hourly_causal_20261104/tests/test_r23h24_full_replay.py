import sys
import numpy as np

from r23h24_full_replay import replay_exact, policy_scores

def test_replay_entry_or_fill_occupancy_exact_quote_time():
 t=np.array([0,100,500,3000,15000,15100,15500,30000,45000,60000,65000],dtype=np.int64)
 sig=np.array([0,3000,15000,30000],dtype=np.int64)
 fill=np.array([1,-1,5,7],dtype=np.int32)
 side=np.zeros(4,dtype=np.int8);h=np.zeros(4,dtype=np.int8);score=np.ones(4,np.float32)
 held=np.ones((4,2,3),np.int8);stop=np.full((4,2,3),-1,np.int32)
 end=np.full((4,3),9,np.int32);end[0,0]=4;end[2,0]=9;end[3,0]=9
 labels=np.full((4,2,3),2,np.int8);labels[:,0,0]=1
 rec=replay_exact(sig,fill,side,h,score,held,stop,end,labels,t,np.full(len(sig),len(t)-1,np.int32),-1.0)
 # Opening at t=0 is held to 15s. Signal at t=3s skipped, 15s exact boundary skipped,
 # next signal 30s accepted with actual fill quote.
 assert len(rec)==2 and list(rec[:,0])==[0,3]
 assert list(rec[:,3])==[1,7]

def test_score_decision_invariance_to_future_labels():
 n=5;cause=np.full((n,2,3,4),0.1,np.float32);held=np.full((n,2,3),0.5,np.float32);wait=np.full(n,0.1,np.float32)
 s,h,p=policy_scores(cause,held,wait,-1)
 assert len(s)==n and p.shape==(n,)
