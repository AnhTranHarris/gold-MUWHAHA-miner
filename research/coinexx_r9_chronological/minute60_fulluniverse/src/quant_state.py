"""Pre-registered compact nonlinear state summaries of 60s causal quote sequences.

Input is 120 by 500ms as-of real quote samples (not interpolated future bars).
Every statistic uses X at or before the R9 entry ordinal. Returns 28 features.
Exploratory *feature hypotheses*, not validated alpha.
"""
import numpy as np

# Backwards-compatible column labels for the frozen 2026-11-13 derived
# feature cache. The labels "max_drawdown_from_peak" and
# "max_rebound_from_trough" denote *end-point excursion* from the prior
# extrema, not a classical maximum pathwise drawdown/rebound.
COLS = [
    'mid_ret_autocorr_1','mid_ret_autocorr_2','mid_ret_autocorr_5',
    'vol_burst_5s','vol_burst_15s','vol_burst_30s',
    'arrival_burst_5s','arrival_burst_15s','arrival_burst_30s',
    'spread_burst_5s','spread_burst_15s','spread_burst_30s',
    'close_location_60s','close_location_30s','close_location_15s',
    'since_peak_seconds','since_trough_seconds',
    'max_drawdown_from_peak','max_rebound_from_trough',
    'rv_concentration_5s','rv_concentration_15s',
    'tail_asymmetry','return_skewness','return_kurtosis',
    'signed_return_last_5','signed_return_last_15',
    'net_path_burst_ratio','spread_volatility_60s'
]

def state_features(X):
    X=np.asarray(X,dtype=np.float32)
    if X.ndim!=3 or X.shape[1:]!=(5,120):raise ValueError('expected N,5,120')
    if not np.isfinite(X).all():raise ValueError('nonfinite quote features')
    r=X[:,0,:].astype(np.float64); s=X[:,1,:].astype(np.float64)
    e=np.expm1(X[:,2,:].astype(np.float64))
    p=X[:,3,:].astype(np.float64)
    eps=1e-8; outputs=[]
    for lag in (1,2,5):
        a=r[:,:-lag];b=r[:,lag:]
        ma=a.mean(1);mb=b.mean(1)
        cov=np.mean((a-ma[:,None])*(b-mb[:,None]),axis=1)
        va=np.mean((a-ma[:,None])**2,axis=1);vb=np.mean((b-mb[:,None])**2,axis=1)
        outputs.append(np.clip(cov/np.sqrt(va*vb+eps),-1,1))
    for w in (10,30,60): outputs.append((np.mean(r[:,-w:]**2,1)+eps)/(np.mean(r[:,:]**2,1)+eps))
    for w in (10,30,60): outputs.append(np.log1p(e[:,-w:].mean(1)) -np.log1p(e[:,:].mean(1)))
    for w in (10,30,60): outputs.append(np.mean(s[:,-w:],1)-np.mean(s,1))
    for w in (120,60,30):
        path=p[:,-w:];mi=path.min(1);ma=path.max(1)
        outputs.append(np.where(ma-mi>eps, (path[:,-1]-mi)/(ma-mi+eps),0.5))
    outputs.extend([(119-np.argmax(p,axis=1))*.5,(119-np.argmin(p,axis=1))*.5])
    outputs.extend([np.max(p,axis=1)-p[:,-1],p[:,-1]-np.min(p,axis=1)])
    for w in (10,30):outputs.append((np.sum(r[:,-w:]**2,1)+eps)/(np.sum(r**2,1)+eps))
    outputs.append(np.sum(np.minimum(r,0)**2,1)/(np.sum(r*r,1)+eps))
    mean=r.mean(1);c=r-mean[:,None];sd=np.sqrt(np.mean(c*c,1)+eps)
    outputs.append(np.mean(c**3,1)/sd**3)
    outputs.append(np.mean(c**4,1)/sd**4)
    outputs.extend([np.sum(r[:,-10:],1),np.sum(r[:,-30:],1)])
    outputs.append((np.abs(np.sum(r[:,-10:],1))+eps)/(np.abs(np.sum(r[:,:],1))+eps))
    outputs.append(np.std(s,axis=1))
    result=np.stack(outputs,axis=1)
    assert result.shape[1]==len(COLS),(result.shape,len(COLS))
    return np.clip(result,-10000,10000).astype(np.float32)
