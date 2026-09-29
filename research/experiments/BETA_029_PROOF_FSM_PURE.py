#!/usr/bin/env python3
"""Deterministic BETA029 bounded *observed-tick* entry-proof engine.

This module is intentionally dependency-light and MT5-portable. It never reads
future quotes before issuing a trade. It does inspect later ticks during OFFLINE
replay, returning only that later tick's index; online MQL5 must maintain the
same state incrementally and act only when the confirming tick arrives.
Not an authorized EA and not an independent profitable signal.
"""
import numpy as np
from numba import njit

@njit(cache=True)
def observed_confirm(t,b,a,origin,side,select,mode,max_wait_ms,retreat_d,renew_d):
    """mode1 retreat->rebreak; mode2 opposite move->reversal; mode3 same-side ignition.

    t timestamps milliseconds ordered, b/a prices integer milli-dollars, origin
    source tick ordinals, side +/-1, select known at origin; on timeout/gap
    selected signals return -1 (CANCEL) and must not fill origin retroactively.
    Exit values: (entry_tick_ordinals, executed_sides, proof_type_flags).
    """
    out=origin.copy();s=side.copy();stage=np.zeros(len(origin),np.int8)
    for k in range(len(origin)):
        if not select[k]:continue
        i=origin[k];sg=side[k];p0=(b[i]+a[i])*.0005
        out[k]=-1;state=0;end_t=t[i]+max_wait_ms
        q=i+1
        while q<len(t) and t[q]<=end_t:
            if t[q]-t[q-1]>2000:break
            mid=(b[q]+a[q])*.0005
            v=(mid-p0)*sg
            prev=(b[q-1]+a[q-1])*.0005
            move=(mid-prev)*sg
            if mode==1:
                if state==0 and v<=-retreat_d:state=1
                elif state==1 and v>=renew_d and move>0:
                    out[k]=q;stage[k]=2;break
            elif mode==2:
                if state==0 and v<=-retreat_d:state=1
                elif state==1 and v<=-(retreat_d+renew_d) and move<0:
                    out[k]=q;s[k]=-sg;stage[k]=3;break
            elif mode==3:
                if v>=renew_d and move>0:
                    out[k]=q;stage[k]=4;break
            q+=1
    return out,s,stage
