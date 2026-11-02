import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from evaluate_cross_feed_transfer import (partition_calibration,stats,paired_block_auc,
                                          load_target,sha256,calibration_admission)
from timing_transition_features import TIMING_FEATURE_VERSION,TIMING_FEATURE_COUNT
from path_config import artifact_stem
import json

def test_calibration_embargo_is_chronological_and_disjoint():
    ts=np.arange(5000,dtype=np.int64)*250
    a,b=partition_calibration(ts,embargo_ms=60000)
    assert a.any() and b.any()
    assert ts[a].max()+60000 < ts[b].min()
    with pytest.raises(ValueError):partition_calibration(ts[::-1])

def test_paired_bootstrap_preserves_same_rows_and_sign():
    rng=np.random.default_rng(9)
    n=3000;ts=np.arange(n,dtype=np.int64)*250
    y=rng.binomial(1,.25,n).astype(np.uint8)
    same=.10+.80*y+.01*rng.normal(size=n)
    cross=rng.uniform(0,1,n)
    r=paired_block_auc(y,same,cross,ts,reps=40)
    assert r['replicates']==40 and r['ci95_same_minus_cross'][0]>.35
    assert r['blocks']>=2

def test_strict_p80_gate_stays_closed():
    y=np.array([0,1,1,0],dtype=np.uint8)
    r=stats(y,np.array([.3,.4,.5,.1]),cut=.20)
    assert r['strict_p80_selected']==0 and r['strict_p80_precision'] is None
    with pytest.raises(ValueError):stats(y,np.array([.1,np.nan,.2,.3]),cut=.2)

def test_loading_requires_complete_hash_verified_source(tmp_path):
    src,mon,day='coinexx','01','2026-01-21';stem=artifact_stem(src,mon,day)
    p=tmp_path/f'{stem}_wait_transition_X.npy'
    X=np.zeros((20,TIMING_FEATURE_COUNT),np.float32);np.save(p,X)
    z=tmp_path/f'{stem}_250ms_universe.npz'
    np.savez(z,ts=np.arange(20,dtype=np.int64)*250,good=np.zeros((20,2),np.uint8),
             next_dt_ms=np.full(20,250,np.int32),next_any_good=np.zeros(20,np.uint8))
    receipt=dict(source=src,month=mon,day=day,timing_feature_version=TIMING_FEATURE_VERSION,
                 timing_features=TIMING_FEATURE_COUNT,timing_sha256=sha256(p),teacher_sha256=sha256(z))
    (tmp_path/f'{stem}_domain_shard_receipt.json').write_text(json.dumps(receipt))
    X2,t,y,_=load_target(tmp_path,src,mon,day,1000)
    assert X2.shape==X.shape and np.array_equal(t,np.arange(20)*250) and y.sum()==0
    p.write_bytes(b'tampered matrix')
    with pytest.raises(ValueError,match='SHA mismatch'):
        load_target(tmp_path,src,mon,day,1000)


def test_cross_feed_p80_false_discovery_is_blocked():
    p=np.array([1.,1.,1.]+[.05]*200)
    y=np.zeros(len(p),dtype=np.uint8)
    out=calibration_admission(y,p,cut=.08,min_n=150,min_precision=.80)
    assert out['calibration_selected']==3
    assert out['calibration_precision']==0.
    assert out['approved'] is False
    assert out['reason']=='FAIL_CLOSED_CALIBRATION'