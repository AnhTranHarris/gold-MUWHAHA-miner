import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from hazard_contract import first_passage_risk_sets
from competing_hazard_model import person_period_data,integrated_causes,fit_source_only,predict_horizons

def test_competing_hazard_probability_mass_and_cause_order():
 p=np.array([[[.7,.2,.1],[.5,.1,.4]]])
 z=integrated_causes(p)
 assert np.isclose(z.sum(),1.)
 assert np.isclose(z[0,2],.2+.7*.1)
 assert np.isclose(z[0,0],.1+.7*.4)
 assert np.isclose(z[0,1],.7*.5)

def test_partially_censored_interval_not_false_survival_label():
 cause=np.array([[0,0]],np.int8)
 first=np.array([[-1,-1]],np.int32)
 exitms=np.array([[100,200]],np.int32)
 endix=np.array([[9,10]],np.int64)
 val=np.array([[.1,-.2]])
 risk=first_passage_risk_sets(cause,first,exitms,endix,val)
 try:person_period_data(np.array([[1.]],np.float32),risk,0)
 except ValueError as e:assert 'no observed' in str(e)
 else:assert False

def test_synthetic_fit_is_only_training_mechanics():
 rng=np.random.default_rng(20261102)
 n=3500
 x=rng.normal(size=(n,3)).astype(np.float32)
 y=np.where(x[:,0]>.5,1,np.where(x[:,0]<-.5,-1,0)).astype(np.int8)
 c=np.column_stack((y,y)).astype(np.int8)
 first=np.where(c==0,-1,120).astype(np.int32)
 exitms=np.full((n,2),30000,dtype=np.int32)
 exitix=np.full((n,2),1000,dtype=np.int64)
 net=np.where(c==1,.2,np.where(c==-1,-.2,0.))
 risk=first_passage_risk_sets(c,first,exitms,exitix,net)
 model,receipt=fit_source_only(x,risk,0,max_candidates=1200,trees=12,leaves=10)
 assert receipt['fit_person_periods']>1200
 z=predict_horizons(model,x[:12])
 assert z.shape==(12,3) and np.allclose(z.sum(axis=1),1,atol=1e-6)
