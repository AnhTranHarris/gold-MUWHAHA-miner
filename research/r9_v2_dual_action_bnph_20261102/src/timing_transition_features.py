"""Causal transition feature view for R9 v2 WAIT/timing research.

This view is evaluated at every direction-neutral 250 ms candidate. It uses only
current and prior observed candidate states. No current/future teacher outcome is
used to choose rows or construct a feature. The target is defined separately as:
WAIT_IMPROVES = current has no strict-good side AND the next actually observed
candidate within max_wait_ms has a strict-good side.
"""
from __future__ import annotations
import numpy as np
from repaired_features import REPAIRED_FEATURE_NAMES, REPAIRED_FEATURE_COUNT

TIMING_FEATURE_VERSION='r9_v2_wait_transition_v1'
LAGS_MS=(250,500,1000)
CURRENT_NAMES=(
    'spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move','micro_bid_ask_imbalance',
    'utc_hour_sin','utc_hour_cos','utc_dow_sin','utc_dow_cos',
    'mid_disp_900000ms','spread_avg_900000ms','event_pressure_900000ms','rv_900000ms','quote_rate_900000ms','price_path_eff_900000ms',
    'mid_disp_3600000ms','event_pressure_3600000ms','rv_3600000ms','quote_rate_3600000ms',
    'mid_disp_14400000ms','spread_avg_14400000ms','rv_14400000ms','quote_rate_14400000ms',
    'grid_bid_250ms','grid_ask_250ms','grid_spread_delta_250ms','grid_bid_500ms','grid_ask_500ms','grid_spread_delta_500ms',
    'grid_bid_750ms','grid_ask_750ms','grid_spread_delta_750ms','grid_bid_1s','grid_ask_1s','grid_spread_delta_1s',
    'grid_bid_1250ms','grid_ask_1250ms','grid_bid_1500ms','grid_ask_1500ms','grid_bid_2s','grid_ask_2s',
    'geom_signed_eff_5s','geom_terminal_pos_5s','geom_extreme_order_5s','geom_turn_rate_5s','geom_range_5s',
    'geom_signed_eff_15s','geom_terminal_pos_15s','geom_extreme_order_15s','geom_turn_rate_15s','geom_range_15s',
    'exc_bid_dir_250ms','exc_ask_dir_250ms','exc_price_dir_250ms','exc_spread_balance_250ms','exc_burst_250ms',
    'exc_bid_dir_1s','exc_ask_dir_1s','exc_price_dir_1s','exc_spread_balance_1s','exc_burst_1s',
    'exc_price_dir_5s','exc_spread_balance_5s','exc_burst_5s','exc_burst_15s','exc_burst_45s',
    'exc_intensity_direction','exc_intensity_spread','exc_intensity_entropy',
)
TRANSITION_NAMES=(
    'spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move','micro_bid_ask_imbalance',
    'grid_bid_250ms','grid_ask_250ms','grid_spread_delta_250ms','grid_bid_500ms','grid_ask_500ms','grid_spread_delta_500ms',
    'grid_bid_750ms','grid_ask_750ms','grid_spread_delta_750ms','grid_bid_1s','grid_ask_1s','grid_spread_delta_1s',
    'geom_signed_eff_5s','geom_terminal_pos_5s','geom_extreme_order_5s','geom_turn_rate_5s','geom_range_5s',
    'exc_bid_dir_250ms','exc_ask_dir_250ms','exc_price_dir_250ms','exc_spread_balance_250ms','exc_burst_250ms',
    'exc_bid_dir_1s','exc_ask_dir_1s','exc_price_dir_1s','exc_spread_balance_1s','exc_burst_1s',
    'exc_price_dir_5s','exc_spread_balance_5s','exc_burst_5s','exc_intensity_direction','exc_intensity_spread','exc_intensity_entropy',
)
INDEX={n:i for i,n in enumerate(REPAIRED_FEATURE_NAMES)}
for n in CURRENT_NAMES+TRANSITION_NAMES:
    if n not in INDEX:raise RuntimeError('missing v4 feature '+n)
CURRENT_IDX=np.asarray([INDEX[n] for n in CURRENT_NAMES],np.int64)
TRANSITION_IDX=np.asarray([INDEX[n] for n in TRANSITION_NAMES],np.int64)
AGG_NAMES=(
    'candidate_dt_prev_ms','candidate_dt_prev2_ms','candidate_gap_ratio_250ms',
    'mid_accel_250ms','bid_accel_250ms','ask_accel_250ms','spread_accel_250ms',
    'bid_minus_ask_accel_250ms','quote_lead_abs_250ms','quote_lead_signed_250ms',
    'price_dir_accel_250ms','spread_balance_accel_250ms','burst_accel_250ms',
    'terminal_pos_velocity_250ms','extreme_order_velocity_250ms','range_velocity_250ms',
    'mid_sign_flip_4','price_dir_sign_flip_4','spread_balance_sign_flip_4','bid_ask_disagree_4',
    'mid_persistence_4','price_dir_persistence_4','spread_narrow_persistence_4',
)
TIMING_FEATURE_NAMES=tuple(CURRENT_NAMES)+tuple(
    f'delta_{n}_{lag}ms' for lag in LAGS_MS for n in TRANSITION_NAMES
)+tuple(f'coverage_{lag}ms' for lag in LAGS_MS)+AGG_NAMES
TIMING_FEATURE_COUNT=len(TIMING_FEATURE_NAMES)
assert len(TIMING_FEATURE_NAMES)==len(set(TIMING_FEATURE_NAMES))

def _lag_indices(ts,lag):
    ts=np.asarray(ts,np.int64)
    j=np.searchsorted(ts,ts-int(lag),side='right')-1
    return np.maximum(j,0)

def _flip_count(x):
    s=np.sign(x);out=np.zeros(len(s),np.float32)
    for k in range(1,s.shape[1]):
        a=s[:,k-1];b=s[:,k]
        out += ((a!=0)&(b!=0)&(a!=b)).astype(np.float32)
    return out

def _persistence(x,positive=True):
    return (np.mean(x>0,axis=1) if positive else np.mean(x<0,axis=1)).astype(np.float32)

def build_timing_features(X,ts):
    """Build timing view from one chronological candidate shard.

    Lag lookups use the last observed candidate at-or-before t-lag. Missing quote
    slots are never filled with future data; actual lag coverage is explicit.
    """
    X=np.asarray(X,np.float32);ts=np.asarray(ts,np.int64)
    if X.ndim!=2 or X.shape[1]!=REPAIRED_FEATURE_COUNT or len(X)!=len(ts):raise ValueError('timing input contract')
    if len(ts) and np.any(ts[1:]<ts[:-1]):raise ValueError('nonchronological timing shard')
    parts=[X[:,CURRENT_IDX]];lagmap={}
    for lag in LAGS_MS:
        j=_lag_indices(ts,lag);lagmap[lag]=j
        parts.append(X[:,TRANSITION_IDX]-X[j][:,TRANSITION_IDX])
    for lag in LAGS_MS:
        age=(ts-ts[lagmap[lag]])/float(lag)
        parts.append(np.minimum(4.,np.maximum(0.,age)).astype(np.float32)[:,None])
    j250=lagmap[250];j500=lagmap[500]
    def col(n):return X[:,INDEX[n]]
    def prev(n,j=j250):return X[j,INDEX[n]]
    dt1=(ts-ts[j250]).astype(np.float32);dt2=(ts-ts[j500]).astype(np.float32)
    last_mid=col('last_mid_move');last_bid=col('last_bid_move');last_ask=col('last_ask_move');last_sp=col('last_spread_change')
    mid_acc=last_mid-prev('last_mid_move');bid_acc=last_bid-prev('last_bid_move');ask_acc=last_ask-prev('last_ask_move');sp_acc=last_sp-prev('last_spread_change')
    pdir=col('exc_price_dir_250ms');sbal=col('exc_spread_balance_250ms');burst=col('exc_burst_250ms')
    term=col('geom_terminal_pos_5s');ext=col('geom_extreme_order_5s');rng=col('geom_range_5s')
    js=[_lag_indices(ts,l) for l in (1000,750,500,250)]
    def hist(n):
        i=INDEX[n]
        return np.column_stack([X[j,i] for j in js]+[X[:,i]])
    hmid=hist('last_mid_move');hpdir=hist('exc_price_dir_250ms');hspread=hist('exc_spread_balance_250ms')
    hbid=hist('last_bid_move');hask=hist('last_ask_move')
    disagree=np.mean((np.sign(hbid)*np.sign(hask))<0,axis=1).astype(np.float32)
    agg=np.column_stack((
        dt1,dt2,np.minimum(4.,dt1/250.),mid_acc,bid_acc,ask_acc,sp_acc,bid_acc-ask_acc,
        np.abs(bid_acc)-np.abs(ask_acc),bid_acc+ask_acc,pdir-prev('exc_price_dir_250ms'),
        sbal-prev('exc_spread_balance_250ms'),burst-prev('exc_burst_250ms'),
        term-prev('geom_terminal_pos_5s'),ext-prev('geom_extreme_order_5s'),rng-prev('geom_range_5s'),
        _flip_count(hmid),_flip_count(hpdir),_flip_count(hspread),disagree,
        np.mean(np.sign(hmid)==np.sign(hmid[:,-1,None]),axis=1).astype(np.float32),
        np.mean(np.sign(hpdir)==np.sign(hpdir[:,-1,None]),axis=1).astype(np.float32),
        _persistence(hspread,positive=True),
    )).astype(np.float32)
    parts.append(agg)
    z=np.concatenate(parts,axis=1).astype(np.float32,copy=False)
    if z.shape!=(len(X),TIMING_FEATURE_COUNT) or not np.isfinite(z).all():raise ValueError('timing feature contract failure')
    return z

def wait_improves_target(d,max_wait_ms=1000):
    """Direct all-candidate target; no future label is used to select rows."""
    good=np.asarray(d['good'],np.uint8);dt=np.asarray(d['next_dt_ms'],np.int64);next_good=np.asarray(d['next_any_good'],np.uint8)
    valid=(dt>0)&(dt<=int(max_wait_ms))
    y=((~good.any(axis=1))&valid&(next_good==1)).astype(np.uint8)
    return y,valid
