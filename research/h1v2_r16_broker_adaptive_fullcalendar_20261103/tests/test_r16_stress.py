import importlib.util,pathlib,sys,numpy as np
P=pathlib.Path('/mnt/data/h1v2_r16_broker_adaptive/src/r16_source_delayed_fills.py')
spec=importlib.util.spec_from_file_location('r16stress',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def stream(step=1000,secs=100,side=1):
 t=np.arange(0,secs*1000+step,step,dtype=np.int64)
 b=np.full(len(t),100_000,np.int32)
 # deterministic executable acceleration after 10s, benign no-adverse window
 move=np.maximum(0,t-10_000)//1000*70
 b=b+np.asarray(side*move,dtype=np.int32)
 a=b+500
 return t,b,a

def test_zero_lag_buy_price_and_one_position():
 t,b,a=stream()
 si=np.array([10,11],np.int64);s=np.array([1,1],np.int8)
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,si,s,0,0,1500)
 assert o[0]==1 and o[1]==-2 and x[0]>f[0]
 assert net[0]>=100

def test_zero_lag_sell_price_and_one_position():
 t,b,a=stream(side=-1)
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,np.array([10]),np.array([-1],np.int8),0,0,1500)
 assert o[0]==1 and net[0]>=100

def test_nonzero_execution_lag_reprices_at_observed_quote():
 t,b,a=stream(step=500)
 sig=np.array([20],np.int64);side=np.array([1],np.int8)
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,sig,side,550,0,1500)
 assert f[0]>sig[0] and t[f[0]]>=t[sig[0]]+550
 assert o[0]==1

def test_filled_quote_spread_rejection():
 t,b,a=stream(step=500)
 sig=np.array([20]);side=np.array([1],np.int8)
 a[22]=b[22]+2600
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,sig,side,800,0,1500)
 assert o[0]==-1 and f[0]==-1

def test_adverse_through_full30_disqualifies_even_if_early_profit():
 t,b,a=stream()
 # trade first favored, then dips below opening liquidation after 12sec
 b[35]=b[10]-150;a[35]=b[35]+500
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,np.array([10]),np.array([1],np.int8),0,0,1500)
 assert o[0]==0 and x[0]==-1

def test_unobserved_long_gap_is_censored_not_success():
 t,b,a=stream()
 # delete every quote after 10 sec up through 40 sec, retaining late recovery
 keep=(t<=10000)|(t>=41000)
 t=t[keep];b=b[keep];a=a[keep]
 o,f,x,net=m.freeze_delayed_oneposition(t,b,a,np.array([10]),np.array([1],np.int8),0,0,1500)
 assert o[0]==-3

def test_slippage_can_turn_just_profitable_quote_into_failure():
 t=np.arange(0,101000,1000,dtype=np.int64)
 b=np.full(len(t),100000,np.int32)
 a=b+200
 # move exactly $0.32 after initial entry, enough to net $0.10 with no slip
 b[11:]=b[11:]+320;a[11:]=a[11:]+320
 for slip in (0,100):
  o,_,_,_=m.freeze_delayed_oneposition(t,b,a,np.array([10]),np.array([1],np.int8),0,slip,1500)
  assert o[0]==(1 if slip==0 else 0)
