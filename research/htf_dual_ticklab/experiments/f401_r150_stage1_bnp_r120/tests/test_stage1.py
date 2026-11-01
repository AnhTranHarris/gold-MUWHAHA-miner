from pathlib import Path
import sys,hashlib,io,zipfile
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'source'))
from r150_stage1_runtime import Stage1RegimeExpert,Specialist,Phase,PINS,NativeDecision
M=Path(__file__).parents[1]/'stage1_candidate';R=Stage1RegimeExpert(M)

def inputs():
    z=np.load('/mnt/data/r150_lean_candidate/staged/dukascopy_02.npz')
    i=10000
    t0=int(z['t'][i]);side=int(z['side'][i]);ordinal=int(z['ordinal'][i]); fam={}
    for f in ('J2','L2','M2'):
        fam[f]=Specialist(*[float(z[f'{f}_{h}'][i]) for h in ('guardian','opposite','neutral')],t0+14_000,PINS[f])
    return t0,side,ordinal,fam

def ledger(t0,side,ordinal_id,**changes):
    d={'t0_ms':t0,'side':side,'ordinal':ordinal_id,'created_ms':t0,
       'submitted_ms':-1,'filled_ms':-1,'cancelled_ms':-1,'expired_ms':-1}
    d.update(changes);return d

def source_call(*,t=None,f=None,phase=None,lifecycle=None,ticks=None):
    t0,side,ordinal,fam=inputs();fam=f or fam
    if phase is None:phase=Phase(5,t0,PINS['R120'])
    if ticks is None:ticks=np.array([t0+14800,t0+15100,t0+15300],dtype=np.int64)
    return R.score_native(t0_ms=t0,side=side,ordinal=ordinal,
        quote_t_ms=ticks,quote_bid=np.array([3200000]*len(ticks)),
        quote_ask=np.array([3200003]*len(ticks)),intent_lifecycle=lifecycle or ledger(t0,side,ordinal),
        phase=phase,families=fam)

def test_valid_research_inference():
    a=source_call();assert a.action in {'PROTECT','SHADOW_VETO'}
    assert set(a.scores)=={'guardian','opposite','neutral'}
    assert all(0<=v<=1 for v in a.scores.values())

def test_future_quote_suffix_mutation():
    t0,_,_,_=inputs()
    a=source_call(ticks=np.array([t0+14800,t0+15100,t0+15300]))
    b=source_call(ticks=np.array([t0+14800,t0+15100,t0+15300,t0+30000,t0+45000]))
    assert a==b

def test_submitted_intent_never_veto():
    t0,s,o,_=inputs()
    assert source_call(lifecycle=ledger(t0,s,o,submitted_ms=t0+7000)).action=='ABSTAIN'

def test_missing_native_t1_abstains():
    t0,_,_,_=inputs()
    assert source_call(ticks=np.array([t0+14999,t0+16000])).action=='ABSTAIN'

def test_forbidden_n2_at_t1():
    t0,s,o,f=inputs();f['N2']=f['M2']
    assert source_call(f=f).action=='ABSTAIN'

def test_future_family_rejected():
    t0,s,o,f=inputs();f['J2']=Specialist(.5,.3,.2,t0+15100,PINS['J2'])
    assert source_call(f=f).action=='ABSTAIN'

def test_wrong_source_phase_rejected():
    t0,s,o,f=inputs()
    assert source_call(phase=Phase(5,t0,'wrong source')).action=='ABSTAIN'
    assert source_call(phase=Phase(5,t0+1,PINS['R120'])).action=='ABSTAIN'

def test_untrusted_lifecycle_does_not_count_as_pending():
    t0,s,o,f=inputs()
    assert source_call(lifecycle=ledger(t0,s,o,ordinal=o+1)).action=='ABSTAIN'

def test_saved_score_numeric_parity():
    a=np.load('/mnt/data/r150_lean_candidate/staged/dukascopy_02.npz')
    ids=np.array([100,10000,25000]);from r150_stage1_runtime import Stage1RegimeExpert
    with zipfile.ZipFile('/mnt/data/XAUUSD_F401_R120_MULTICLOCK_HTF_SESSION_GRID_CAUSAL_RESEARCH_UNAPPROVED_20261028.zip') as z:
        phase=np.load(io.BytesIO(z.read('R120_02_UNSUPERVISED_PHASES.npy')))
    for i in ids:
        p=NativeDecision(int(a['t'][i]),int(a['t'][i])+15100,int(a['side'][i]),True,True)
        f={q:Specialist(*[float(a[f'{q}_{h}'][i]) for h in ('guardian','opposite','neutral')],int(a['t'][i])+14000,PINS[q]) for q in ('J2','L2','M2')}
        r=R._score_t1_with_proof(proof=p,phase=Phase(int(phase[i]),int(a['t'][i]),PINS['R120']),families=f)
        for head in ('opposite','neutral'):
            saved=np.load(f'/mnt/data/r150_repair_advanced/models/r120_conditional_02_{head}.npy')
            assert abs(r.scores[head]-float(saved[i]))<3e-6


def test_absent_specialist_fail_closed():
    t0,s,o,f=inputs()
    f['L2']=Specialist(.4,.2,.3,t0+14000,PINS['L2'],False)
    assert source_call(f=f).action=='ABSTAIN'
