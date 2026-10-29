from r120_multiclock_geometry import build_states,FEATURES
import numpy as np

def test_synthetic_causality():
 t=np.array([0,150,249,250,499,500,501,1000,1250,1500,5000,8000,30000,30100],dtype=np.int64)
 bid=np.arange(len(t),dtype=np.int32)*10+50000
 ask=bid+20
 volume=np.ones(len(t),np.float32)
 ev=np.array([250,500,501,1000,1500,5000,30000,30001,31000],dtype=np.int64)
 side=np.ones(len(ev),np.int8)
 x=build_states(t,bid,ask,volume,volume,ev,side)
 # Change ticks published exactly at and after first event; first event is unchanged.
 bid2=bid.copy();ask2=ask.copy();bid2[t>=250]+=100000;ask2[t>=250]+=100000
 y=build_states(t,bid2,ask2,volume,volume,ev,side)
 assert np.array_equal(x[0],y[0]),'same-time/future leakage'
 # Event at 250 must see completed [0,250), not tick at 250.
 assert x[0,0] == 0 # insufficient lag history
 assert x[0,9]>=0 and x[0,9]<1e5
 assert x.shape==(len(ev),len(FEATURES))
 assert np.isfinite(x).all()
 print('PASS causal 250ms tick exclusion, completed closed candles and features',len(FEATURES))

def test_session_overlaps():
 day=20000*86400000
 t=np.array([day+7*3600000+200,day+8*3600000+200,day+13*3600000+200,day+14*3600000+200],np.int64)
 b=np.arange(4,dtype=np.int32)*100+10000;a=b+30
 e=t+1
 q=np.ones(4,dtype=np.float32);s=np.ones(4,dtype=np.int8)
 x=build_states(t,b,a,q,q,e,s)
 assert x[0,66]==1 and x[0,72]==1 and x[0,78]==0
 assert x[2,66]==0 and x[2,72]==1 and x[2,78]==1
 print('PASS Asia/London and London/NY overlapping anchored state')

def test_session_day_reset():
 day=20000*86400000
 t=np.array([day+8*3600000,day+24*3600000+100],np.int64)
 b=np.array([10000,99999],np.int32);a=b+10;q=np.ones(2,np.float32)
 ev=t+1;s=np.ones(2,np.int8)
 x=build_states(t,b,a,q,q,ev,s)
 assert x[0,66]==1 and x[1,66]==1
 assert x[1,67]==0 and np.isclose(x[1,71],np.log1p(1))
 print('PASS session daily anchor reset')

if __name__=='__main__':
 test_synthetic_causality();test_session_overlaps();test_session_day_reset()