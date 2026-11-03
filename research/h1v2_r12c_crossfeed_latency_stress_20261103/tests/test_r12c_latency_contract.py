import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source'))
from r12c_latency_and_execution_stress import freeze_delayed_signal_replay, load_source

def stream(period=1000,length=40):
 t=np.arange(length,dtype=np.int64)*period
 b=np.full(length,10000,dtype=np.int32)
 a=b+100
 return t,b,a

def test_buy_no_latency_good_first_exit_after_raw_ask_fee():
 t,b,a=stream();b[1:]=10250;a[1:]=10350
 out,f,ex,n=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),0,0)
 assert list(out)==[1] and list(f)==[0] and list(ex)==[1] and int(n[0])==130

def test_cost_nonzero_consumes_both_market_order_sides():
 t,b,a=stream();b[1:]=10250;a[1:]=10350
 out,*_=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),0,20)
 assert int(out[0])==0 # 0.13 -> 0.09 after roundtrip 0.04, misses +0.10

def test_delayed_entry_recomputes_executable_prices_not_initial_signal():
 t,b,a=stream();b[1:]=10250;a[1:]=10350;b[2:]=10500;a[2:]=10600
 # Delay one second: must enter at ask[1]=10350, not original ask[0]=10100.
 out,f,ex,n=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),1000,0)
 assert int(f[0])==1 and int(ex[0])==2 and int(n[0])==130 and int(out[0])==1

def test_30_second_safety_not_stopped_at_early_tp():
 t,b,a=stream();b[1:]=10250;a[1:]=10350;b[20]=9800;a[20]=9900
 out,f,ex,n=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),0,0)
 assert int(out[0])==0 and int(ex[0])==-1 # adverse after early TP invalidates strict full30

def test_broker_sparse_no_quote_after_horizon_source_end_is_valid_if_exact_end():
 t=np.arange(0,31000,1000,dtype=np.int64)
 b=np.full(len(t),10250,np.int32);b[0]=10000;a=b+100
 out,f,ex,n=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),0,0)
 assert int(out[0])==1

def test_gapped_future_is_censored_not_positive():
 t=np.array([0,1000,2000,19000,40000],dtype=np.int64)
 b=np.array([10000,10250,10250,10250,10250],dtype=np.int32);a=b+100
 out,*_=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),0,0)
 assert int(out[0])==-3

def test_one_position_conservative_failure_occupancy_blocks_next_signal():
 t,b,a=stream(length=80);b[:]=10000;a[:]=10100
 out,*_=freeze_delayed_signal_replay(t,b,a,np.array([0,5,31]),np.ones(3,np.int8),0,0)
 assert list(out)==[0,-2,0] # failed filled action reserves full 30s, no magically immediate retry

def test_sell_bid_entry_and_ask_liquidation_and_fee():
 t,b,a=stream();b[1:]=9600;a[1:]=9700
 out,fill,ex,n=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([-1],np.int8),0,0)
 assert int(out[0])==1 and int(n[0])==280 and int(ex[0])==1

def test_invalid_source_sha_is_hard_failure(tmp_path):
 p=tmp_path/'f.csv.gz';p.write_bytes(b'bad')
 with pytest.raises(ValueError,match='SOURCE_SHA_MISMATCH'):
  load_source(p,'DUKASCOPY_RAW')

def test_late_requote_rejects_stale_observation():
 t=np.array([0,3000,4000,5000,10000,20000,30000,40000],np.int64)
 b=np.full(len(t),10000,np.int32);a=b+100
 out,*_=freeze_delayed_signal_replay(t,b,a,np.array([0]),np.array([1],np.int8),50,0)
 assert int(out[0])==-1
