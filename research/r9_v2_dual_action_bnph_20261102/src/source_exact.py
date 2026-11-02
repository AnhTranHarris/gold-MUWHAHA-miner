"""Full original R9 v2 paired-action source. Read ZIP members, not log summaries.

This source is *baseline-entry-event* research, not a full quote-time action universe.
Hindsight labels never enter runtime features. The original teacher's SELL net-sign
issue is not propagated: independent original R9 paired-action source archived
full initial-side lifecycle reconciliation, and a new executable-side sign test is
mandatory prior to any live-grade use.
"""
from __future__ import annotations
import hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
from path_config import paired_action_root
MONTHS=('01','02','06','07')
ORIENTED = np.array([i for i,n in enumerate((
    ['spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move',
     'micro_bid_ask_imbalance','evidence','lane_reversal',
     'utc_hour_sin','utc_hour_cos','utc_dow_sin','utc_dow_cos'] +
    [f'{c}_{h}ms' for h in (250,500,1000,5000,15000,45000,300000,900000,3600000,14400000)
     for c in ('mid_disp','spread_avg','bid_disp','ask_disp','event_pressure','spread_change_events','rv','quote_rate','price_path_eff')]))
    if n in ('last_bid_move','last_ask_move','last_mid_move') or n.startswith(('mid_disp_','bid_disp_','ask_disp_','event_pressure_'))], dtype=np.int64)


def sha(b): return hashlib.sha256(b).hexdigest()

def path_for(source, month, root=None):
    if source not in ('coinexx','dukascopy') or month not in MONTHS:raise ValueError('source/month')
    base=paired_action_root(root)
    candidates=list(base.glob(f'R9_V2_PAIRED_ACTION_{source.upper()}_2026_{month}_FULL_CHECKPOINT.zip'))
    if len(candidates)!=1:raise FileNotFoundError((source,month))
    return candidates[0]

def load(source,month,root=None):
    arc=path_for(source,month,root); key=f'{source}_{month}'
    with zipfile.ZipFile(arc) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        manifest=json.loads(z.read('SOURCE_EXACT_MANIFEST.json'))
        for n in (f'results/{key}_paired_counterfactual.npz',f'results/{key}_causal_asof.npz'):
            entry=next((v for k,v in manifest.get('files',{}).items() if k==n),None)
            # Read both complete binary source members, not embedded prose.
            buf=z.read(n)
            if entry and isinstance(entry,dict) and entry.get('sha256') and sha(buf)!=entry['sha256']:
                raise ValueError('manifest hash mismatch '+n)
            with np.load(io.BytesIO(buf),allow_pickle=False) as d:
                if n.endswith('causal_asof.npz'):
                    x=d['X'].copy();tx=d['ts'].copy();side=d['side'].copy()
                else:
                    ts=d['ts'].copy();y=d['good'].copy();neutral=d['neutral'].copy()
                    net=d['net'].copy();exit_ms=d['exit_time'].copy();original=d['side'].copy()
    assert np.array_equal(ts,tx) and np.array_equal(side,original)
    assert x.shape==(len(ts),102) and y.shape==(len(ts),2)
    assert np.isfinite(x).all()
    # A terminal-end censored counterfactual may legitimately have NaN net.
    # Do NOT invent missing future returns; mark unavailable counterfactuals
    # in a separate VALID mask, excluded from model fitting and scoring.
    assert np.all((y+neutral)<=1)
    return dict(X=x,t=ts,side=side,good=y,neutral=neutral,net=net,exit_ms=exit_ms,
                archive=str(arc), archive_sha256=hashlib.sha256(arc.read_bytes()).hexdigest(),
                valid=np.isfinite(net).all(axis=1))


def two_views(X,original_side):
    """Canonical [BUY, SELL] views, ALWAYS; no baseline-side decision inheritance.

    The old research source stored [baseline_side, reverse_side] outcomes; we
    reorder targets separately. Its original-side flag remains a causal
    covariate only if explicitly included in X, never a hard direction vote.
    """
    n=len(X)
    s=np.tile(np.asarray([1.,-1.],np.float32),n)
    z=np.repeat(X.astype(np.float32,copy=False),2,axis=0)
    z[:,ORIENTED]*=s[:,None]
    return np.column_stack((z,s)).astype(np.float32,copy=False)

def canonical(arr,side):
    """Reorder [original,reverse] -> [BUY,SELL] without changing outcomes."""
    a=np.asarray(arr)
    assert a.ndim==2 and a.shape[1]==2 and len(side)==len(a)
    return np.where((np.asarray(side)==1)[:,None], a, a[:,::-1])

def labels(d):
    good=canonical(d['good'],d['side']);neutral=canonical(d['neutral'],d['side'])
    return np.where(good.reshape(-1)==1,2,
                    np.where(neutral.reshape(-1)==1,1,0)).astype(np.uint8)

def chronological_masks(ts, embargo_ms=60000):
    days=np.unique(ts//86400000)
    if len(days)<6:raise ValueError('need >5 active days')
    a=max(1,int(len(days)*.50));b=max(a+1,int(len(days)*.72))
    if b>=len(days):raise ValueError('insufficient split days')
    fit_end=int(days[a])*86400000
    cal_end=int(days[b])*86400000
    # The teacher labels observe up to 60s even when R9 exits earlier.
    tr=(ts<fit_end-embargo_ms)
    cal=(ts>=fit_end+embargo_ms)&(ts<cal_end-embargo_ms)
    check=(ts>=cal_end+embargo_ms)
    assert ts[tr].max()<ts[cal].min() and ts[cal].max()<ts[check].min()
    return (tr,cal,check,dict(days=len(days),fit_end=fit_end,cal_end=cal_end,
                                  embargo_ms=embargo_ms))