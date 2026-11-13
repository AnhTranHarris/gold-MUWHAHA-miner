"""Research-only Coinexx source-ordinal as-of quote-state features (2026-11-13).

No historical trade-volume inference, future quote labels or external indices.
CUSUM and signed intensity use only observed Bid/Ask revisions through the
specified candidate ordinal. Brownian barrier probabilities are *approximations*,
not calibrated hazards, broker fills, or evidence of tradability.
"""
from __future__ import annotations
import numpy as np
from numba import njit
from scipy.special import ndtr

FEATURE_NAMES = (
 'cusum_pos','cusum_neg','cusum_imbalance','cusum_max',
 'qint_pos_250ms','qint_neg_250ms','qint_signed_250ms','qint_total_250ms',
 'qint_pos_1000ms','qint_neg_1000ms','qint_signed_1000ms','qint_total_1000ms',
 'qint_pos_5000ms','qint_neg_5000ms','qint_signed_5000ms','qint_total_5000ms',
 'qint_pos_15000ms','qint_neg_15000ms','qint_signed_15000ms','qint_total_15000ms',
 'qint_fastslow_ratio','qint_signed_fastslow', 'qint_spread_scaled',
)
ACTION_NAMES = (
 'brownian_upper_before_lower','brownian_z_up_5s','brownian_z_down_5s',
 'brownian_z_up_15s','brownian_z_down_15s',
 'brownian_hit_upper_5s','brownian_hit_lower_5s',
 'brownian_hit_upper_15s','brownian_hit_lower_15s',
 'model_mu_cents_per_s','model_sigma_cents_sqrt_s',
)

@njit(cache=True)
def sequential_state(t,bid,ask,entries):
    """O(n_ticks + n_entries), source ordinal <= candidate; same-ms order retained.

    CUSUM updates with *previous* EW variance, and that variance then observes
    this return. EW intensity decays in quote-clock time (not fixed event count).
    Gaps > 15s OR 60s elapsed since a segment anchor reset quote state.
    This is a *segmented*, not sliding, CUSUM: prevents >60s lookback and
    deliberately makes reset phase a possible source of instability.
    """
    n=len(t);out=np.empty((len(entries),len(FEATURE_NAMES)),dtype=np.float32)
    tau=np.array([250.0,1000.0,5000.0,15000.0])
    up=np.zeros(4,dtype=np.float64);down=np.zeros(4,dtype=np.float64)
    pos=0.0;neg=0.0; ewvar=1.0;lastmid=0.0;lastspread=0.0;prevtime=0
    e=0; segment_start=0
    for i in range(n):
        now=t[i]; mid=(float(bid[i])+float(ask[i]))*.5
        spread=float(ask[i])-float(bid[i]);dt=0 if i==0 else max(0,now-prevtime)
        if i==0 or dt>15000 or now-segment_start>=60000:
            segment_start=now
            up[:]=0;down[:]=0;pos=0.;neg=0.;ewvar=1.
            dmid=0.
        else:
            dmid=mid-lastmid
            for j in range(4):
                decay=np.exp(-dt/tau[j]);up[j]*=decay;down[j]*=decay
            if dmid>0:
                up+=1
            elif dmid<0:
                down+=1
            z=dmid/np.sqrt(max(1.0,ewvar))
            z=max(-12.,min(12.,z))
            pos=max(0.,min(80.,pos+z-.25));neg=max(0.,min(80.,neg-z-.25))
            # Previous variance used to normalize this quote; no self-normalization.
            d=min(dt,5000)
            decay=np.exp(-d/1000.)
            ewvar=ewvar*decay+(1.-decay)*min(dmid*dmid,10000.)
        while e<len(entries) and entries[e]==i:
            a=out[e]
            a[0]=pos;a[1]=neg;a[2]=pos-neg;a[3]=max(pos,neg)
            for j in range(4):
                a[4+j*4]=up[j];a[5+j*4]=down[j]
                a[6+j*4]=(up[j]-down[j])/(1.+up[j]+down[j])
                a[7+j*4]=up[j]+down[j]
            a[20]=(1.+up[0]+down[0])/(1.+up[3]+down[3])
            a[21]=(up[0]-down[0])/(1.+up[0]+down[0])-(up[3]-down[3])/(1.+up[3]+down[3])
            a[22]=(up[1]+down[1])/(1.+max(1.,spread))
            e+=1
        lastmid=mid;lastspread=spread;prevtime=now
    if e!=len(entries):raise ValueError('entry ordinals not strictly increasing or out of bounds')
    return out

def gambler_upper(mu,sigma2,up,down):
    """Stable eventual upper-before-lower BM crossing probability.

    For loss bound `down` and gain bound `up` from mark-to-market origin.
    Never substitute for a finite 5-second hitting probability. Opposite drift
    signs must preserve the correct tail asymptotes even at extreme z scores.
    """
    up=np.asarray(up,float);down=np.asarray(down,float)
    mu=np.asarray(mu,float);sigma2=np.asarray(sigma2,float)
    a=np.maximum(down,1.e-5); b=np.maximum(up,1.e-5)
    k=np.clip(2.*mu/np.maximum(sigma2,1.e-7),-1.e6,1.e6)
    p=np.broadcast_to(a/(a+b),np.shape(k)).copy()
    positive=k>1.e-9
    negative=k<-1.e-9
    if np.any(positive):
        kk=k[positive];aa=a[positive];bb=b[positive]
        p[positive]=np.expm1(np.clip(-kk*aa,-700,0))/np.expm1(np.clip(-kk*(aa+bb),-700,0))
    if np.any(negative):
        kk=k[negative];aa=a[negative];bb=b[negative]
        numer=np.expm1(np.clip(kk*aa,-700,0))
        denom=np.expm1(np.clip(kk*(aa+bb),-700,0))
        p[negative]=np.exp(np.clip(kk*bb,-700,0))*(numer/denom)
    return np.clip(np.nan_to_num(p,nan=0.5,posinf=1.,neginf=0.),0.,1.)

def action_barrier_features(event_features, spread, stop,target,side):
    """Geometry computed only with pre-entry event-derived features and barriers.
    0.01-XAU cent units. ENTRY/EXIT executable sides require up=target+spread,
    down=stop-spread; side sign changes the midpoint drift.
    """
    event_features=np.asarray(event_features)
    n=len(side)
    assert event_features.shape[0]==n
    # Source exact event-engine order: 6 metrics per 100/500/1000/3000/5000/15000/60000ms.
    drift5=event_features[:,24].astype(float)/5.
    drift15=event_features[:,30].astype(float)/15.
    rv5=event_features[:,27].astype(float)
    rv15=event_features[:,33].astype(float)
    sigma2=np.maximum(1.,(rv5**2)/5.)
    sigma=np.sqrt(sigma2)
    # 5s drift prioritized; 15s as weak stabilizer. Fixed ex-ante blend.
    mu=np.nan_to_num(.8*drift5+.2*drift15,nan=0.,posinf=0.,neginf=0.)*np.asarray(side,float)
    sp=np.asarray(spread,float);sl=np.asarray(stop,float);tp=np.asarray(target,float)
    up=np.maximum(1.,tp+sp);down=np.maximum(1.,sl-sp)
    out=np.zeros((n,len(ACTION_NAMES)),np.float32)
    out[:,0]=gambler_upper(mu,sigma2,up,down)
    for j,T in enumerate((5.,15.)):
        rt=sigma*np.sqrt(T)+1e-6
        zu=(mu*T-up)/rt
        zd=(-mu*T-down)/rt
        out[:,1+j*2]=np.clip(zu,-30.,30.)
        out[:,2+j*2]=np.clip(zd,-30.,30.)
        # Reflection-principle BM hit probability approximations with frozen mean/variance;
        # not competing-risk probability (both events can occur in the same interval).
        expo_up=np.exp(np.clip(2.*mu*up/sigma2,-70,70))
        expo_down=np.exp(np.clip(-2.*mu*down/sigma2,-70,70))
        p_up=ndtr(zu)+expo_up*ndtr((-mu*T-up)/rt)
        p_down=ndtr(zd)+expo_down*ndtr((mu*T-down)/rt)
        out[:,5+j*2]=np.clip(np.nan_to_num(p_up,nan=0),0,1)
        out[:,6+j*2]=np.clip(np.nan_to_num(p_down,nan=0),0,1)
    out[:,9]=np.clip(mu,-1e4,1e4)
    out[:,10]=np.clip(sigma,0,1e4)
    return out
