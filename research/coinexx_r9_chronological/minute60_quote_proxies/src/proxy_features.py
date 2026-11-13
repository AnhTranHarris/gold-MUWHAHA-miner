"""Coinexx quote-only, source-ordered proxy features for R9 M60.

Not actual executed flow, order book depth, a fitted Hawkes model, or real liquidity.
Every observation depends exclusively on tick ordinals <= the requested entry ordinal.
The six exponential marks below are *Hawkes-inspired*, with fixed kernels: they
are NOT an estimated Hawkes branching matrix or true traded-order intensity.
The latent pressure filter is a causal two-timescale scalar state-space proxy,
not a recovered market participant inventory or true demand.
"""
from __future__ import annotations
import numpy as np
from numba import njit

TAUS_MS=(200.0,1000.0,5000.0)
FEATURE_NAMES=(
  'hex_marked_up_200ms','hex_marked_down_200ms','hex_net_200ms',
  'hex_marked_up_1000ms','hex_marked_down_1000ms','hex_net_1000ms',
  'hex_marked_up_5000ms','hex_marked_down_5000ms','hex_net_5000ms',
  'hex_fast_slow_ratio','hex_200_5000_alignment','hex_mark_surprise',
  'latent_pressure_fast','latent_pressure_slow','latent_pressure_disagreement',
  'latent_innovation','latent_uncertainty','latent_gain','latent_pressure_confidence',
  'res_spread_rel_ew','res_spread_excess','res_active_shock_age_s',
  'res_active_shock_excess','res_recovery_fraction','res_recent_shock_ew',
  'res_spread_reversion_rate','res_spread_vol_ew',
)

@njit(cache=True)
def proxy_states(ms,bid,ask,entries):
    """One-pass as-of computation, O(n_ticks+n_entries), no lookahead.

    Millisecond ties are processed in original source ordinal. A segment resets
    after 60s or a >15s quote gap, matching the frozen CUSUM research scope.
    All event kernels are time-decayed and marked by relative midpoint *size*.
    Latent state is causal spread-adaptive innovation filtering with uncertainty.
    'Resilience' measures recovery of the QUOTED spread only; depth is unknowable.
    """
    n=len(ms);ne=len(entries)
    out=np.empty((ne,len(FEATURE_NAMES)),dtype=np.float32)
    taus=np.array(TAUS_MS)
    up=np.zeros(3);down=np.zeros(3)
    e=0;prev_ms=0;anchor=0;prev_mid=0.;prev_sp=0.;prev_ew_sp=20.
    latent_f=0.;latent_s=0.;latent_P=1.0;innovation=0.;gain=0.
    ew_sp=20.;ew_spvol=0.;shock_age=0.;shock_peak=0.;shock_now=0.;
    recent_shock=0.;recover=0.;sp_reversion=0.;past_mark_ew=0.5
    for i in range(n):
        now=ms[i];mid=.5*(float(bid[i])+float(ask[i]));sp=float(ask[i]-bid[i]);
        dt=0. if i==0 else max(0.,float(now-prev_ms))
        if i==0 or dt>15000 or now-anchor>=60000:
            anchor=now
            up[:]=0.;down[:]=0.
            latent_f=0.;latent_s=0.;latent_P=1.;innovation=0.;gain=0.
            ew_sp=max(sp,1.);ew_spvol=0.;shock_age=0.;shock_peak=0.;shock_now=0.;
            recent_shock=0.;recover=0.;sp_reversion=0.;past_mark_ew=.5
            dmid=0.
        else:
            dmid=mid-prev_mid
            # Mark is quote-size *relative to observed previous spread*.
            mark=min(8.0,abs(dmid)/max(5.,prev_sp))
            past_mark_ew=.99*past_mark_ew+.01*mark
            for j in range(3):
                decay=np.exp(-dt/taus[j])
                up[j]*=decay;down[j]*=decay
                if dmid>0:up[j]+=mark
                elif dmid<0:down[j]+=mark
            # Evolving latent pressure of quote marks, with spread-sensitive noise.
            # Process uncertainty diffuses in wall-clock time; gains weaken in wide spreads.
            decay_f=np.exp(-dt/900.)
            decay_s=np.exp(-dt/4500.)
            latent_f*=decay_f
            latent_s*=decay_s
            latent_P=min(10.,latent_P*decay_f*decay_f+.03+.001*min(dt,3000.))
            measurement=max(-8.,min(8.,dmid/max(5.,prev_sp)))
            noise=1.+2.*sp/max(5.,ew_sp)
            gain=latent_P/(latent_P+noise)
            innovation=measurement-latent_f
            latent_f=max(-8.,min(8.,latent_f+gain*innovation))
            latent_s=max(-8.,min(8.,latent_s+(.015+.05*(1.-decay_s))*measurement))
            latent_P=max(.005,(1.-gain)*latent_P)
            # Spread-resilience shock state, with lagged EW baseline and no book claims.
            decay_sp=np.exp(-dt/2000.)
            recent_shock*=np.exp(-dt/5000.)
            ew_spvol=ew_spvol*np.exp(-dt/10000.)+(1.-np.exp(-dt/10000.))*min(300.,abs(sp-prev_sp))
            shock_threshold=max(2.,.15*ew_sp)
            widen=sp-max(prev_sp,ew_sp)
            if widen>shock_threshold:
                recent_shock+=1.
                shock_age=0.
                shock_peak=max(shock_peak,widen)
                shock_now=sp-ew_sp
            elif shock_peak>0.:
                shock_age+=dt/1000.
                shock_now=max(0.,sp-ew_sp)
                recover=max(0.,min(1.,(shock_peak-shock_now)/max(1.,shock_peak)))
                if shock_now<max(1.,.10*ew_sp) and shock_age>0.:
                    shock_peak=0.;shock_age=0.
            sp_reversion=(prev_sp-sp)/max(1.,ew_sp)
            ew_sp=decay_sp*ew_sp+(1.-decay_sp)*sp
        if e<ne and entries[e]==i:
            row=out[e]
            for j in range(3):
                offset=3*j
                row[offset]=up[j];row[offset+1]=down[j]
                row[offset+2]=(up[j]-down[j])/(1.+up[j]+down[j])
            row[9]=(1.+up[0]+down[0])/(1.+up[2]+down[2])
            row[10]=(up[0]-down[0])*(up[2]-down[2])/(1.+(up[0]+down[0])*(up[2]+down[2]))
            row[11]=past_mark_ew
            row[12]=latent_f;row[13]=latent_s;row[14]=latent_f-latent_s
            row[15]=innovation;row[16]=latent_P;row[17]=gain
            row[18]=latent_f/(.1+np.sqrt(latent_P))
            row[19]=sp/max(1.,ew_sp)
            row[20]=sp-ew_sp
            row[21]=shock_age
            row[22]=shock_now
            row[23]=recover
            row[24]=recent_shock
            row[25]=sp_reversion
            row[26]=ew_spvol
            e+=1
        prev_ms=now;prev_mid=mid;prev_sp=sp
    if e!=ne:raise ValueError('Entry ordinals missing or unordered')
    return out
