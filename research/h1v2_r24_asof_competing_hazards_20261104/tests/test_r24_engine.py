"""R24 scientific adversarial tests; do not count as actual MT5 compile or broker fills."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
import r24_firstpass_engine as e

def test_crossing_exact_random():
 rng=np.random.default_rng(24)
 for trial in range(8):
  x=rng.integers(3000,4000,size=57,dtype=np.int32)
  s,ma,mi,_,_=e.build_tree(x,x+30)
  for _ in range(40):
   start=int(rng.integers(0,55));end=int(rng.integers(start+1,58))
   hi=int(rng.integers(3000,4000));lo=int(rng.integers(3000,4000))
   i,c=e.first_crossing(ma,mi,s,start,end,hi,lo)
   ref=next(((j,1 if x[j]>=hi else 0) for j in range(start,end) if x[j]>=hi or x[j]<=lo),(-1,-1))
   assert (i,c)==ref,(i,c,ref,start,end,hi,lo)

def test_direction_ask_bid_and_first_barrier():
 t=np.arange(0,90000,100,dtype=np.int64)
 b=np.full(len(t),10000,np.int32);a=np.full(len(t),10100,np.int32)
 # buy target requires bid >= 10220 and stop at bid<=9900
 b[120]=10220;a[120]=10320
 b[145]=9880;a[145]=9980
 s=np.asarray([1],np.int32);f=np.asarray([2],np.int32)
 labels,ev,valid=e.generate_labels(t,b,a,s,f)
 assert valid[0] and labels[0,0,0]==1,(labels,ev)
 # SELL has first adverse ask >=10200 at 12s, so STOP
 assert labels[0,1,0]==0,(labels,ev)

def test_gap_and_censor_are_not_losses():
 t=np.r_[np.arange(0,11000,100,dtype=np.int64),np.arange(30000,150000,100,dtype=np.int64)]
 b=np.full(len(t),10000,np.int32);a=b+100
 labels,ev,valid=e.generate_labels(t,b,a,np.asarray([0],np.int32),np.asarray([1],np.int32))
 assert np.all(labels[0,:,:]==3),labels

def test_prefix_future_mutation_does_not_change_features():
 t=np.arange(0,120000,100,dtype=np.int64)
 b=np.asarray(300000+np.arange(len(t)),np.int32);a=b+100
 ix=np.asarray([400,700],np.int32);g=np.asarray([0],np.int32)
 f1=e.extract_features(t,b,a,ix,g,'DUKASCOPY_RAW')
 a[900:]+=12000;b[900:]-=9000
 f2=e.extract_features(t,b,a,ix,g,'DUKASCOPY_RAW')
 assert f1.shape[1]==len(e.FEATURE_NAMES)
 assert np.array_equal(f1,f2)

def test_candidate_freshness_and_gap_reset():
 t=np.r_[np.arange(0,400000,1000,dtype=np.int64),np.arange(500000,900000,1000,dtype=np.int64)]
 b=np.full(len(t),300000,np.int32);a=b+120
 idx,g=e.candidates(t,b,a,decision_ms=1000,cap=200)
 assert all(t[i]>=300000 and not (500000<=t[i]<800000) for i in idx)
 assert t[idx[0]]==300000

def test_session_calendar_and_missing_news_fail_closed():
 t=np.arange(0,5*60*60*1000,3600000,dtype=np.int64)
 c=e.clock_by_hour(t)
 assert len(c)==5 and c.shape[1]==12
 assert np.all((c[:,1]>=0)&(c[:,1]<7))

def test_raw_source_filename_paths():
 assert str(e.source_file('DUKASCOPY_RAW','01')).endswith('XAUUSD_DUKAS_2026_01_ticks.csv.gz')
 assert str(e.source_file('MT5_BROKER_EXPORT','07')).endswith('XAUUSD_MT5_BROKER_2026_07_ticks_ALL.csv.gz')
