"""Adversarial isolated first-passage/censorship/calendar tests for R12BN.
Synthetic examples are mechanical tests, not trading results.
"""
import csv,datetime as dt,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r12_native/source')
from r12b_month_native import asof_quote_clocks,_rolling_extrema,quote_tp_first,earliest_finish_schedule

ROOT=Path('/mnt/data/h1v2_r12_native/reports')

def test_all_distinct_is_asof_and_first250_subset():
 t=np.arange(0,345001,100,dtype=np.int64)
 b=np.full(len(t),4000000,np.int32);a=b+200
 ix,flags=asof_quote_clocks(t,b,a)
 assert len(ix)>0 and np.all(t[ix]>=300000)
 assert np.array_equal(ix, np.unique(ix))
 assert np.all((flags&1)!=0)==False
 assert np.any((flags&1)!=0)
 # A future quote cannot alter earlier observed eligibility or source ordinals.
 u=b.copy();u[t>325000]+=300
 i2,f2=asof_quote_clocks(t,u,u+200)
 prefix=t[ix]<=325000
 assert np.array_equal(ix[prefix],i2[t[i2]<=325000])
 assert np.array_equal(flags[prefix],f2[t[i2]<=325000])

def test_new_epoch_after_quote_gap_and_300s_warmup():
 t=np.r_[np.arange(0,320001,1000),np.arange(380000,700001,1000)].astype(np.int64)
 b=np.full(len(t),4000000,np.int32);a=b+200
 ix,flags=asof_quote_clocks(t,b,a)
 assert np.all((t[ix]>=300000)&((t[ix]<380000)|(t[ix]>=680000)))

def test_full30_safe_requires_observed_gap_coverage():
 t=np.r_[np.arange(0,320001,1000),np.arange(350000,401001,1000)].astype(np.int64)
 b=np.full(len(t),4000000,np.int32);a=b+200
 ix=np.array([np.searchsorted(t,310000)],np.int64)
 _,_,_,_,_,_,covered=_rolling_extrema(t,b,a,ix,30000)
 assert not bool(covered[0])

def test_first_observed_tp_requires_fee_and_later_ms():
 t=np.array([0,0,1,2,3,4,30000,30001],np.int64)
 b=np.array([100000,100121,100119,100119,100120,100120,100120,100120],np.int32)
 a=np.array([100000,100000,100000,100000,100000,100000,100000,100000],np.int32)
 ex,tt=quote_tp_first(t,b,a,np.array([0],np.int64),np.array([100000],np.int32),np.array([100000],np.int32),np.array([1],np.int8))
 assert int(ex[0])==4 and int(tt[0])==3

def test_interval_finish_scheduling_single_position():
 t=np.array([100,101,200,300,400],np.int64);e=np.array([500,180,280,380,450],np.int64)
 selected=earliest_finish_schedule(t,e)
 assert len(selected)==4 and np.array_equal(selected,np.array([1,2,3,4]))
 assert np.all(t[selected[1:]]>e[selected[:-1]])

def test_full_11520_utc_quarters_and_source_parity():
 import pandas as pd
 a=pd.read_csv(ROOT/'R12BN_DUKAS_COMPLETE_ALL_11520_QUARTERS_INDEPENDENT_SOURCE_DOMAIN_EVIDENCE.csv')
 assert len(a)==11520
 active=a[a.source_verified_original_R9_SYNTH_15min_reference>0]
 assert len(active)==7521 and active.source_verified_original_R9_SYNTH_15min_reference.sum()==117585
 assert (active.R12BN_SynthNative_quota_met==1).sum()==7520
 assert (active.R12DQ_Dukascopy_quota_met==1).sum()==7313
 assert (active.neither_source_hindsight_quota_met==1).sum()==0
 assert a.utc_quarter.nunique()==11520

