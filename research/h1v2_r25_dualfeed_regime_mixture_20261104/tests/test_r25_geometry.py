"""R25 research engine adversarial fixtures; no historical profit assertions."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
import pytest

PATH=Path(__file__).resolve().parents[1]/'src'/'r25_broker_geometry.py'
spec=importlib.util.spec_from_file_location('r25_broker_geometry',PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_source_pin_declares_all_eight():
 assert len(m.RAW_PINS)==8 and set(k[0] for k in m.RAW_PINS)==set(m.SOURCES)
 assert all(len(x)==64 for x in m.RAW_PINS.values())

def test_past_only_features_immune_to_future_mutation():
 t=np.arange(80,dtype=np.int64)*1000
 b=np.arange(80,dtype=np.int32)*5+100_000;a=b+100
 ix=np.array([60,65],np.int32)
 x1=m.prefix_features(t,b,a,ix)
 newb=b.copy();newa=a.copy();newb[66:]+=99999;newa[66:]+=99999
 x2=m.prefix_features(t,newb,newa,ix)
 np.testing.assert_array_equal(x1,x2)
 assert np.isfinite(x1).all()

def test_future_ordinal_not_in_earlier_same_ms():
 t=np.array([0,200,300,400,500,700,800,800,800,900,1000,1200,1800,2300,2500,2900,3000],np.int64)
 b=np.array([100]*len(t),np.int32);a=b+10
 x=m.prefix_features(t,b,a,np.array([7],np.int32))
 b2=b.copy();a2=a.copy();b2[8:]+=200;a2[8:]+=200
 y=m.prefix_features(t,b2,a2,np.array([7],np.int32))
 np.testing.assert_array_equal(x,y)

def fixture_run(price_series,ask_series,action,decision_ms=0,fill_ms=100,stop=100,tp=100,h=1000):
 t=np.arange(len(price_series),dtype=np.int64)*100
 b=np.asarray(price_series,np.int32);a=np.asarray(ask_series,np.int32)
 s=np.array([0],np.int32);fill=np.array([fill_ms//100],np.int32)
 X=np.zeros((1,26),np.float32)
 X[0,0]=max(0,a[0]-b[0]);X[0,4]=500;X[0,5]=500;X[0,6]=500;X[0,7]=100;X[0,10]=100;X[0,13]=100;X[0,16]=2;X[0,17]=1;X[0,18]=0;X[0,19]=0
 return t,b,a,s,fill,X

def test_first_actual_quote_tp_stop_and_net():
 # Enough history in a fixed artificial state to trigger policy 0.
 b=np.array([100000,100000,100000,100000,100000,100000,100500,100500,100500,100500,100500,100500,100500,100500],np.int32)
 a=b+50
 t,bb,aa,s,f,X=fixture_run(b,a,1)
 X[0,10]=200;X[0,13]=300
 observed=m.oneposition(t,bb,aa,s,f,X,0,0,10000)
 assert len(observed)==1 and observed[0,4]==1
 assert observed[0,5]>=100


def test_stop_before_target_is_failure_and_preserves_negative_net():
 b=np.array([100000,100000,100000,99750,100300,100300,100300,100300,100300,100300,100300,100300,100300,100300],np.int32)
 a=b+50;t,bb,aa,s,f,X=fixture_run(b,a,1)
 X[0,10]=200;X[0,13]=300
 z=m.oneposition(t,bb,aa,s,f,X,0,0,10000)
 assert z[0,4]==0 and z[0,5]<0

def test_gap_censor_never_mislabeled_tp_or_stop():
 t=np.array([0,100,200,300,500,17000,17100,17200,17300,17500],np.int64)
 b=np.array([100000,100000,100000,100000,100000,105000,105000,105000,105000,105000],np.int32)
 a=b+50;s=np.array([0],np.int32);f=np.array([1],np.int32)
 X=np.zeros((1,26),np.float32)
 X[0,0]=50;X[0,4]=500;X[0,5]=500;X[0,6]=500;X[0,7]=100;X[0,10]=200;X[0,13]=300
 z=m.oneposition(t,b,a,s,f,X,0,0,20000)
 assert len(z)==1 and z[0,4]==3

def test_unfilled_attempt_not_a_completed_win():
 t=np.arange(14,dtype=np.int64)*100;b=np.full(len(t),100000,np.int32);a=b+50
 s=np.array([0],np.int32);f=np.array([-1],np.int32);X=np.zeros((1,26),np.float32)
 X[0,0]=50;X[0,4]=500;X[0,5]=500;X[0,6]=500;X[0,7]=100;X[0,10]=200;X[0,13]=300
 z=m.oneposition(t,b,a,s,f,X,0,0,1400)
 assert len(z)==1 and z[0,4]==4 and z[0,1]==-1


def test_every_quarter_hour_day_including_zero_reference():
 mon='01';qt=np.arange(96,dtype=np.int64)*900000+int(__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc).timestamp()*1000)
 r=np.zeros(len(qt),np.int32);r[0]=1;r[2]=2
 t=np.array([qt[0],qt[0]+100,qt[0]+500,qt[2]+500,qt[3]],np.int64)
 e=np.array([[0,1,2,1,1,200,100,100,5000,0,100],[3,3,4,-1,0,-300,100,100,5000,0,100]],np.int64)
 qs,hs,ds,sq,sh,sd=m.reference_calendar(mon,qt,r,'DUKASCOPY_RAW','TEST',e,t)
 assert (len(qs),len(hs),len(ds))==(96,24,1)
 assert qs[1]['reference']==0 and qs[1]['fills']==0
 assert sq['active']==2 and sh['active']==1 and sd['active']==1
 assert sq['joint']==1 and sh['joint']==0
