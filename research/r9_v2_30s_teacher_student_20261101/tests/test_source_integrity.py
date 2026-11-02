"""Source-exact training boundary checks; executed before packaging."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import pytest
BASE=Path('/mnt/data/v2_30s_teacher_training')
sys.path.insert(0,str(BASE))
from train_student import load, choices

@pytest.mark.parametrize('source,month',[(b,m) for b in ('coinexx','dukascopy') for m in ('01','02','06','07')])
def test_complete_original_ledger(source,month):
    raw=pd.read_pickle(BASE/'results'/f'{source}_{month}_raw.pkl')
    proven=json.loads((BASE/'results'/f'{source}_{month}_feature_provenance.json').read_text())
    micro=json.loads((BASE/'results'/f'{source}_{month}_micro_manifest.json').read_text())
    assert len(raw)==proven['entries']==micro['entries_joined']
    assert proven['source_ticks']==micro['quotes_scanned']
    assert (raw.exit_ms>=raw.entry_ms).all()
    assert (raw.entry_ms.to_numpy()[1:]>=raw.exit_ms.to_numpy()[:-1]).all()

@pytest.mark.parametrize('source,month',[(b,m) for b in ('coinexx','dukascopy') for m in ('01','02','06','07')])
def test_runtime_features_exclude_hindsight(source,month):
    policy=json.loads((BASE/'results'/f'policy_{source}_{month}'/'POLICY.json').read_text())
    fs=policy['features']
    forbidden={'net','mfe','mae','exit_ms','entry_price','win','target','neutral','quality','quality_bad',
        'teacher_positive','native_min_id','positive','day_id','week_id','month','source','second_utc'}
    assert forbidden.isdisjoint(fs)
    assert policy['no_future_features']
    assert policy['training_cutoff_utc_ms']<policy['calibration_cutoff_utc_ms']<policy['forecast_from_utc_ms']

@pytest.mark.parametrize('source,month',[(b,m) for b in ('coinexx','dukascopy') for m in ('01','02','06','07')])
def test_exact_250ms_completed_before_entry(source,month):
    d=pd.read_pickle(BASE/'results'/f'{source}_{month}_micro.pkl')
    assert d['micro_lag_ms'].ge(250).all()
    assert (d['micro_lag_ms'].to_numpy(dtype=np.int64)%250==0).all()
    # Event features never contain negative or fractional counts after normalizing.
    for c in ('micro_bu_250ms','micro_bd_250ms','micro_askonly_500ms','micro_joint_1000ms'):
        assert d[c].between(0,1).all()

@pytest.mark.parametrize('source,month',[(b,m) for b in ('coinexx','dukascopy') for m in ('01','02','06','07')])
def test_strict_and_volume_policies_reject(source,month):
    s=json.loads((BASE/'results'/f'fold_{source}_{month}_summary.json').read_text())
    v=json.loads((BASE/'results'/f'volume_{source}_{month}_summary.json').read_text())
    assert not s['all_constraints_pass']
    assert not v['all_constraints_pass']
    assert not v['daily_80pct_pass'] and not v['weekly_80pct_pass'] and not v['monthly_80pct_pass']
    assert v['selected_trades']<=v['evaluated_candidates']
    assert v['calibration']['cal_np_bad_acceptance']<=.10000001
