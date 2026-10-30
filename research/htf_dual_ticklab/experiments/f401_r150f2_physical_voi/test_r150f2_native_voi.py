import sys,numpy as np
sys.path.insert(0,'/mnt/data/R150F2/source')
from r150f2_native_voi import causal_quote_features,new_action_outcome,reftime,DELAYS

def source():
 t=np.arange(0,200000,50,dtype=np.int64);mid=np.arange(len(t),dtype=np.int32)*2+4010000
 bid=mid-1000;ask=mid+1000
 return t,bid,ask

def test_future_mutation_does_not_change_causal_state():
 t,b,a=source();j=500
 old=causal_quote_features(t,b,a,j,1)
 b[j+1:]+=100000;a[j+1:]+=100000
 assert np.array_equal(old,causal_quote_features(t,b,a,j,1))

def test_first_passage_outcome_uses_future_but_not_same_ms():
 t,b,a=source();j=500
 res=new_action_outcome(t,b,a,j,1)
 assert res[0] in (0,1,2)
 b[j+1:]+=50000;a[j+1:]+=50000
 res2=new_action_outcome(t,b,a,j,1)
 assert res2[0]==1

def test_wait_uses_new_timestamp_and_new_economics():
 t,b,a=source()
 x,y,obs,elapsed,fin,pnl=reftime(t,b,a,np.array([t[500]-15000],np.int64),np.array([1],np.int8),np.array([500],np.int64))
 assert obs.shape==(1,4)
 assert np.array_equal(elapsed[0],DELAYS)
 assert obs[0,0]==t[500] and obs[0,1]>obs[0,0]
 assert np.isfinite(pnl).all() and np.isfinite(x).all()

def test_missing_first_quote_is_not_fabricated():
 t,b,a=source()
 _,y,obs,_,_,_=reftime(t,b,a,np.array([0],np.int64),np.array([1],np.int8),np.array([500],np.int64))
 assert (y==-1).all() and (obs==-1).all()

def test_contract_spread_is_explicit():
 t,b,a=source();j=200
 x=causal_quote_features(t,b,a,j,1)
 assert abs(float(x[1])-2.)<1e-6
 assert np.isfinite(x).all()

def test_no_teacher_or_outcome_runtime_parameters():
 import inspect
 from r150f2_live_shadow import R150F2CausalVOI
 names=set(inspect.signature(R150F2CausalVOI.shadow).parameters)
 assert not names.intersection({'teacher','teacher_score','truth','future_ticks','future_label','hindsight','order_send'})

def test_missing_broker_model_never_changes_parent():
 from r150f2_live_shadow import R150F2CausalVOI
 m=R150F2CausalVOI('/mnt/data/R150F2/models','unknown')
 x=m.shadow(broker='unknown',parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=100000,
 decision_quote_ms=115001,verified_first_quote=True,source_state_published_ms=115001,
 source24=np.zeros(24,dtype=np.float32),already_submitted_or_filled=False)
 assert not x.override_active and x.parent_action=='VETO_NEW_UNFILLED_ORDER'

def test_real_broker_must_preserve_order_and_quote_provenance():
 from r150f2_live_shadow import R150F2CausalVOI
 m=R150F2CausalVOI('/mnt/data/R150F2/models','dukascopy')
 kw=dict(broker='dukascopy',parent_action='VETO_NEW_UNFILLED_ORDER',t0_ms=100000,
 decision_quote_ms=115001,verified_first_quote=True,source_state_published_ms=115001,
 source24=np.zeros(24,dtype=np.float32),already_submitted_or_filled=False)
 a=m.shadow(**kw)
 assert a.override_active is False
 kw['already_submitted_or_filled']=True
 assert m.shadow(**kw).score is None
 kw['already_submitted_or_filled']=False;kw['source_state_published_ms']=115002
 assert m.shadow(**kw).score is None
