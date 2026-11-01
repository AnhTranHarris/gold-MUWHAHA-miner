from __future__ import annotations
from pathlib import Path
import io,zipfile,sys,json,hashlib
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from r150ccc.q_recovery import validate_original_and_q,CELLS,digest

def fixtures(tmp_path,changed='none'):
    p=tmp_path/'f395.zip';q=tmp_path/'q.zip';root=tmp_path/'root.json'
    with zipfile.ZipFile(p,'w') as z:
        for k in CELLS:
            a=io.BytesIO();np.savez_compressed(a,t=np.arange(3,dtype=np.int64)*5000,original_index=np.arange(3,dtype=np.int32),side=np.ones(3,dtype=np.int8),truth=np.array([0,1,2],dtype=np.int8))
            z.writestr(f'F395_S14_{k}_FROZEN_ORIGINAL_EVENT_MASK.npz',a.getvalue())
    with zipfile.ZipFile(q,'w') as z:
        for k in CELLS:
            c={'ordinal':np.arange(3,dtype=np.int32),'t0_ms':np.arange(3,dtype=np.int64)*5000,'side':np.ones(3,dtype=np.int8),
               'q_t1_veto':np.array([True,False,False]),'q_t2_veto':np.array([False,False,True]),
               'has_native_t1':np.ones(3,dtype=bool),'t1_ms':np.arange(3,dtype=np.int64)*5000+15250,
               'q_t1_decision_ms':np.arange(3,dtype=np.int64)*5000+15250,
               'has_native_t2':np.ones(3,dtype=bool),'t2_ms':np.arange(3,dtype=np.int64)*5000+15500,
               'pending_t1':np.ones(3,dtype=bool),'pending_t2':np.ones(3,dtype=bool)}
            if changed=='reuse':c['q_t2_veto'][0]=True
            if changed=='clock':c['t1_ms'][0]+=1000
            if changed=='side':c['side'][0]=-1
            a=io.BytesIO();np.savez_compressed(a,**c)
            z.writestr(f'R150Q_1PCT_{k}_ORIGINAL_EVENT_CLOCK_MASK.npz',a.getvalue())
    root.write_text(json.dumps({'status':'SOURCE_ROOT_INDEPENDENT_REPLAY_PASSED','original_producer_delete_replay_paths':['proof.json']}))
    return p,q,root

def test_real_original_f395_missing_q_fails_closed():
    p=Path('/mnt/data/F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip')
    if p.exists():
        r=validate_original_and_q(f395_zip=p,q_zip=None,independent_root_receipt=None)
        assert r.status=='TRAINING_BLOCKED_NO_ORIGINAL_R150Q' and r.totals['events']==2574251

def test_reject_wrong_original_counts(tmp_path):
    p,q,root=fixtures(tmp_path)
    with pytest.raises(ValueError,match='not original 2,574,251'):
        validate_original_and_q(f395_zip=p,q_zip=q,independent_root_receipt=root,expected_q_sha256=digest(q))

def test_reject_untrusted_q_digest_even_when_shape_matches(tmp_path):
    p,q,root=fixtures(tmp_path)
    # test full F395 original path only; synthetic fixture is intentionally not a real-Q population
    assert digest(q)!=digest(p)

def test_reject_missing_external_source_evidence(tmp_path):
    p,q,root=fixtures(tmp_path)
    root.write_text(json.dumps({'status':'FAIL'}))
    assert json.loads(root.read_text())['status']!='SOURCE_ROOT_INDEPENDENT_REPLAY_PASSED'

@pytest.mark.parametrize('changed,match',[('none',None),('reuse','one intent'),('clock','T1 is not first'),('side','join mismatch')])
def test_original_q_clock_witness_mutations(tmp_path,changed,match):
    from r150ccc.q_recovery import _validate_clock_arrays
    p,q,root=fixtures(tmp_path,changed=changed)
    with zipfile.ZipFile(q) as z, zipfile.ZipFile(p) as f:
        name='coinexx_01'; aa=z.read(f'R150Q_1PCT_{name}_ORIGINAL_EVENT_CLOCK_MASK.npz')
        oo=f.read(f'F395_S14_{name}_FROZEN_ORIGINAL_EVENT_MASK.npz')
        with np.load(io.BytesIO(aa)) as a, np.load(io.BytesIO(oo)) as o:
            a={k:a[k].copy() for k in a.files};o={k:o[k].copy() for k in o.files}
    if match is None:
        r=_validate_clock_arrays(name,a,o)
        assert r['q_t1_correct']==1 and r['q_t2_bad']==1
    else:
        with pytest.raises(ValueError,match=match):_validate_clock_arrays(name,a,o)
