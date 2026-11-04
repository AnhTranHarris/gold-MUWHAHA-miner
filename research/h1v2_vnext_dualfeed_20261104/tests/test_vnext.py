from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from vnext import prefix_features,first_seconds,source_replay,source_report,policy,quota,MONTHS

def test_asof_future_mutation_invariance_including_same_ms_revisions():
 t=np.arange(5000,dtype=np.int64)*100
 b=4_000_000+np.arange(len(t),dtype=np.int32)
 a=b+200
 ix=np.array([3000,4000],np.int32)
 f=prefix_features(t,b,a,ix,np.array([300000,400000]))
 b2=b.copy();a2=a.copy();b2[4001:]+=500000;a2[4001:]+=500000
 np.testing.assert_array_equal(prefix_features(t,b2,a2,ix,np.array([300000,400000])),f)

def test_one_position_buy_true_bid_ask_target_and_slippage():
 t=np.array([0,100,110,200,300,400,500],np.int64)
 b=np.array([10000,10000,10000,10080,10250,10250,10250],np.int32)
 a=b+100
 r=source_replay(t,b,a,np.array([0,2],np.int32),np.array([0,0],np.int8),np.array([1000,1000],np.int32),np.array([100,100],np.int32),np.array([100,100],np.int32),np.array([],np.int32),'MT5_BROKER_EXPORT')
 assert len(r)==1
 assert tuple(r[0,:6])==(0,1,4,1,0,1000)
 assert r[0,6]==130 # 10250 - 10100 - 20

def test_sell_uses_ask_liquidation_no_fabricated_quote():
 t=np.array([0,100,200,300,400,500],np.int64)
 b=np.array([10000,10000,9920,9840,9700,9700],np.int32)
 a=b+100
 r=source_replay(t,b,a,np.array([0],np.int32),np.array([1],np.int8),np.array([1000],np.int32),np.array([100],np.int32),np.array([100],np.int32),np.array([],np.int32),'MT5_BROKER_EXPORT')
 assert len(r)==1 and r[0,3]==1 and r[0,2]==4
 assert r[0,6]==10000-9800-20

def test_quotegap_censors_not_target_after_drought():
 t=np.array([0,100,200,300,100000,100100],np.int64)
 b=np.array([10000,10000,10010,10020,20000,20000],np.int32)
 a=b+100
 r=source_replay(t,b,a,np.array([0],np.int32),np.array([0],np.int8),np.array([200000],np.int32),np.array([100],np.int32),np.array([100],np.int32),np.array([4],np.int32),'DUKASCOPY_RAW')
 assert len(r)==1 and r[0,3]==3 and r[0,6]==0

def test_wait_broker_differentiation_and_no_quota_in_policy():
 x=np.zeros((4,23),dtype=np.float32);x[:,0]=[100,1000,200,2000];x[:,3]=[-1100,-300,-1000,-100];x[:,4]=[1400,1800,1500,3000];x[:,5]=[1700,1000,2000,1000];x[:,6]=[3000,5000,3000,3000];x[:,10]=100;x[:,18]=10
 d=policy(x,'DUKASCOPY_RAW',1);m=policy(x,'MT5_BROKER_EXPORT',1)
 assert d[0].shape==(4,) and m[0].shape==(4,)
 assert np.all(np.isin(d[0],np.array([-1,0,1])))
 assert not np.array_equal(d[0],m[0])  # broker-dependent geometry gate

def test_source_calendar_reference_all_4_months():
 if not Path('/mnt/data/R23_DUKASCOPY_RAW_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip').is_file():
  import pytest;pytest.skip('authenticated original R23 data ZIP not mounted')
 for mon,n,ref in [('01',2976,27980),('02',2688,33523),('06',2880,31758),('07',2976,24324)]:
  e,r=quota(mon);assert len(e)==n and int(r.sum())==ref and np.all(np.diff(e)==900000)
