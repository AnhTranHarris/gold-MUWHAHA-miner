from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from r150ccc.market import build_prefix,MARK_NAMES
from r150ccc.fit import AuditPopulation,validate_population,build_training_slice,explain_teacher_residual_offline
from r150ccc.calibration import select_rescue_cut,recount
from r150ccc.contract import Stage2ACCC,ActionClock


def raw():
    t0=1761000000000
    t=np.array([t0+v for v in (0,200,700,2000,4000,7000,11000,14800,15100,16000,17500)],dtype=np.int64)
    b=np.array([3300000,3300001,3300000,3300004,3300003,3300005,3300006,3300003,3300700,3300800,3300900],np.int64)
    a=b+5
    return t0,t,b,a

def test_real_quote_prefix_excludes_decision_and_future():
    t0,t,b,a=raw();p=build_prefix(t,b,a,t0_ms=t0,t1_ms=t0+15100,side=1)
    q=build_prefix(t[:9],b[:9],a[:9],t0_ms=t0,t1_ms=t0+15100,side=1)
    assert p.quote_count==q.quote_count==8
    np.testing.assert_array_equal(p.features,q.features)
    b2=b.copy();b2[-3:]+=100000;a2=a.copy();a2[-3:]+=100000
    np.testing.assert_array_equal(p.features,build_prefix(t,b2,a2,t0_ms=t0,t1_ms=t0+15100,side=1).features)

def test_future_quote_suffix_not_accepted_as_past():
    t0,t,b,a=raw()
    with pytest.raises(ValueError):build_prefix(t[::-1],b[::-1],a[::-1],t0_ms=t0,t1_ms=t0+15100,side=1)
    with pytest.raises(ValueError):build_prefix(t,b,a,t0_ms=t0,t1_ms=t0+16000,side=0)

def test_source_quant_state_is_finite_readonly():
    t0,t,b,a=raw()
    p=build_prefix(t,b,a,t0_ms=t0,t1_ms=t0+15100,side=-1)
    assert len(p.features)==len(MARK_NAMES)==32
    assert np.isfinite(p.features).all() and not p.features.flags.writeable

def sample_population(attested=True,tamper=False):
    n=12;mask=np.array([1,0,1,0,1,0,1,0,1,0,1,0],bool)
    h=hashlib.sha256(np.packbits(mask).tobytes()).hexdigest()
    if tamper:h='1'*64
    return AuditPopulation('coinexx','01',np.arange(n),np.arange(n,dtype=np.int64)*10000,
      np.array([0,1,2]*4,dtype=np.int8),mask,h,np.arange(n*9).reshape(n,9).astype('float32'),attested,np.ones(n,bool))

def test_original_q_exact_mask_required():
    with pytest.raises(ValueError):validate_population(sample_population(False))
    with pytest.raises(ValueError):validate_population(sample_population(True,True))
    x,y,t,o=build_training_slice(sample_population())
    assert x.shape==(6,9) and len(y)==len(t)==len(o)==6

def test_source_features_not_changed_by_all_class_permutations():
    p=sample_population(); before=p.market.copy()
    for shift in [-5,1,4]:
       y=np.roll(p.truth,shift)
       assert (y!=p.truth).any()
       np.testing.assert_array_equal(p.market,before)

def test_teacher_audit_does_not_change_training_matrix():
    p=sample_population();x,_,_,_=build_training_slice(p)
    for teacher in (np.zeros(12),np.ones(12),np.linspace(-50,50,12)):
        d=explain_teacher_residual_offline(teacher_rank=teacher,truth=p.truth,market=p.market)
        assert set(d)=={'0','1','2'}
        np.testing.assert_array_equal(x,build_training_slice(p)[0])

def test_calibration_fail_closed_for_weak_selectivity():
    y=np.array([0,1]*180);s=np.linspace(1.,0.,len(y));t=np.arange(len(y))*3600_000
    cut=select_rescue_cut(score=s,truth=y,utc_ms=t,max_bad_per_correct=.10,min_correct=100)
    assert cut.cut is None and cut.status=='ABSTAIN_NO_PRECISION_TAIL'

def test_calibration_precision_and_recount_exact():
    n=250;t=np.arange(n)*3600_000;s=np.linspace(1,0,n)
    y=np.ones(n,dtype=int);y[:120]=0;y[120:140]=2
    x=select_rescue_cut(score=s,truth=y,utc_ms=t,min_correct=100,max_bad_per_correct=.5)
    assert x.cut is not None and x.rescued_correct>=100
    q=np.ones(n,bool);r=s>=x.cut
    c=recount(q_veto=q,rescue=r,truth=y,eligible=q)
    assert c['q_bad']==130 and c['q_correct_lost']==120
    assert c['new_bad']==130-c['opposite_readmitted']-c['neutral_readmitted']
    assert c['new_correct_lost']==120-c['correct_rescued']

def test_original_q_population_cannot_create_new_veto():
    q=np.array([True,False,True]);r=np.array([False,True,False]);truth=np.array([0,1,2]);e=q
    with pytest.raises(ValueError):recount(q_veto=q,rescue=r,truth=truth,eligible=e)

class SyntheticModel:
    def __init__(self,p):self.p=p
    def predict_proba(self,x):return np.tile(np.array([1-self.p,self.p]),(len(x),1))

def fake_runtime(monkeypatch,tmp_path):
    import joblib
    monkeypatch.setitem(sys.modules,'joblib',joblib)
    sha={};names={}
    for k,p in [('continuation',.97),('reliability',.93),('hard_negative',.96)]:
        name=k+'.joblib';path=tmp_path/name;joblib.dump(SyntheticModel(p),path)
        sha[k]=hashlib.sha256(path.read_bytes()).hexdigest();names[k]=name
    cfg=dict(status='RESEARCH_ONLY_UNAPPROVED',orders_authorized=False,clock='T1',
        runtime_teacher_free=True,q_source_exact=True,broker='coinexx',models=names,model_sha256=sha,
        family_archive_sha256={k:'a'*64 for k in ['J2','L2','M2']},rescue_cut=.9,min_expert=.90,
        max_disagreement=.1,feature_count=3)
    (tmp_path/'config.json').write_text(json.dumps(cfg));return Stage2ACCC(tmp_path)

def good_clock(**kwargs):
    d=dict(broker='coinexx',t0_ms=100000,t1_ms=115250,side=1,ordinal=4,pending=True,
      has_native_t1=True,original_q_veto=True,q_veto_decision_ms=115250,source_root_attested=True,
      market_asof_ms=114999,family_asof_ms={k:114000 for k in ['J2','L2','M2']},
      family_hashes={k:'a'*64 for k in ['J2','L2','M2']});d.update(kwargs);return ActionClock(**d)

def test_runtime_requires_true_pending_source_exact_q(monkeypatch,tmp_path):
    r=fake_runtime(monkeypatch,tmp_path);x=np.ones(3,dtype='float32')
    assert r.score(clock=good_clock(),features=x).action=='RESCUE_RESEARCH_ONLY'
    for key,val in [('pending',False),('has_native_t1',False),('original_q_veto',False),
                    ('source_root_attested',False),('t1_ms',116000),('broker','dukascopy'),
                    ('q_veto_decision_ms',115500),('market_asof_ms',115250)]:
        assert r.score(clock=good_clock(**{key:val}),features=x).action=='ABSTAIN'

def test_frozen_model_integrity(monkeypatch,tmp_path):
    r=fake_runtime(monkeypatch,tmp_path)
    (tmp_path/'guardian.not-used').write_text('test')
    (tmp_path/'continuation.joblib').write_bytes(b'corrupted')
    with pytest.raises(ValueError):Stage2ACCC(tmp_path)

def test_absent_models_are_not_promoted(tmp_path):
    (tmp_path/'config.json').write_text(json.dumps({'status':'RESEARCH_ONLY_UNAPPROVED','q_source_exact':False}))
    with pytest.raises(ValueError):Stage2ACCC(tmp_path)

def test_compose_193D_market_only_source_and_independent_views():
    from r150ccc.schema import compose,feature_groups,SCHEMA_SIZE
    x=compose(r120=np.zeros(128),jlm_market_scores=np.ones(9)/2,
              native=np.ones(32),bayes=np.zeros(24))
    assert x.shape==(SCHEMA_SIZE,) and not x.flags.writeable
    gr=feature_groups();assert len({tuple(v) for v in gr.values()})==3
    with pytest.raises(ValueError):compose(r120=np.zeros(127),jlm_market_scores=np.ones(9),native=np.ones(32),bayes=np.zeros(24))

def test_cannot_self_certify_missing_q_producer(tmp_path):
    from r150ccc.gate import external_evidence_gate,CELLS
    p=tmp_path/'external.json';p.write_text(json.dumps({'cells':{k:{} for k in CELLS}}))
    with pytest.raises(ValueError,match='root gate'):
        external_evidence_gate(p)


def test_first_real_quote_and_exact_integer_proof():
    t0,t,b,a=raw()
    with pytest.raises(ValueError,match='FIRST genuine'):
        build_prefix(t,b,a,t0_ms=t0,t1_ms=t0+15300,side=1)
    with pytest.raises(ValueError,match='exact integers'):
        build_prefix(t.astype(float),b,a,t0_ms=t0,t1_ms=t0+15100,side=1)

def test_future_family_state_fails_closed(monkeypatch,tmp_path):
    r=fake_runtime(monkeypatch,tmp_path)
    x=np.ones(3,dtype='float32')
    a=good_clock(family_asof_ms={'J2':115250,'L2':114000,'M2':114000})
    assert r.score(clock=a,features=x).action=='ABSTAIN'
