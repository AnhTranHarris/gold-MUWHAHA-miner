import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from h1v2_teacher import candidate_250ms,replay_buy_sell_30s,schedule_oracle,read_ticks

def test_candidate_asof_gap_warmup_and_spread():
 t=np.array([0,250,300000,300250,300500,300750,600751],np.int64)
 b=np.ones(len(t))*100; a=b+.2;a[4]=102
 ix=candidate_250ms(t,b,a,warmup_ms=0,gap_reset_ms=600000)
 assert 4 not in ix and 6 in ix

def test_direction_bid_ask_cost_and_first_30sec():
 t=np.array([0,100,200,300],np.int64)
 b=np.array([100.,100.35,100.40,100.34]);a=b+.20
 c,n,first,dt,ix,dur=replay_buy_sell_30s(t,b,a,np.array([0],np.int64))
 assert c[0,0]==1 and c[0,1]==-1
 assert ix[0,0]>0 and n[0,0]>0

def test_both_side_oracle_independent_and_nonoverlap():
 entries=np.array([0,10,20,40],np.int64)
 code=np.array([[1,0],[1,1],[1,0],[0,1]],np.int8)
 net=np.array([[.3,-.1],[.1,.2],[.2,-.1],[-.2,.4]],np.float32)
 end=np.array([[19,-1],[25,15],[35,-1],[-1,45]],np.int64)
 sel,side,m=schedule_oracle(entries,code,net,end)
 assert m['trades']==3 and side.tolist()==[1,1,-1]
 assert sel.tolist()==[0,2,3]

def test_wrong_side_loss_from_spread_not_counted_as_correct():
 t=np.array([0,50,100,200,30000],np.int64)
 b=np.array([100.,100.05,100.03,100.01,100.]);a=b+.2
 c,n,first,dt,ix,dur=replay_buy_sell_30s(t,b,a,np.array([0],np.int64))
 assert c[0,0]!=1 and c[0,1]!=1

def test_entry_same_millisecond_quote_ignored_for_trade_exit():
 t=np.array([0,0,0,100,200],np.int64)
 b=np.array([100.,100.5,99.5,100.4,100.3]);a=b+.2
 c,n,first,dt,ix,dur=replay_buy_sell_30s(t,b,a,np.array([0],np.int64))
 assert dt[0,0]==100 and ix[0,0]>=3

def test_no_hindsight_leak_from_future_at_entry():
 t=np.array([0,100,200,300,400],np.int64)
 b=np.array([100.,100.13,100.20,100.10,100.11]);a=b+.20
 assert candidate_250ms(t,b,a,warmup_ms=0).tolist()==[0,3]
 b2=b.copy();b2[-1]=-10.;a2=a.copy();a2[-1]=-9.8
 assert candidate_250ms(t[:-1],b[:-1],a[:-1],warmup_ms=0).tolist()==[0,3]

def test_oracle_dynamic_program_optimal_against_bruteforce():
 rng=np.random.default_rng(80802)
 for _ in range(40):
  n=7;entries=np.arange(n,dtype=np.int64)*10
  code=rng.choice(np.array([-1,0,1],np.int8),size=(n,2),p=[.40,.25,.35])
  net=np.where(code==1,rng.uniform(.10,.40,size=(n,2)),-.12).astype(np.float32)
  ends=entries[:,None]+rng.integers(1,28,size=(n,2))
  sel,side,metrics=schedule_oracle(entries,code,net,ends)
  def brute(i):
   if i>=n:return 0,0.
   best=brute(i+1)
   for op in (0,1):
    if code[i,op]!=1:continue
    j=np.searchsorted(entries,ends[i,op],side='right')
    cn,profit=brute(j);choice=(1+cn,float(net[i,op])+profit)
    if choice>best:best=choice
   return best
  cn,profit=brute(0)
  assert metrics['trades']==cn
  assert abs(metrics['sum_net']-profit)<1e-3
