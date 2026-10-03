"""DH03-S06 13C pullback-event multiplicity engine. Frozen thresholds only.

pivot_policy: 0=post-pullback S15 pivot, 1=any already-causal S15 pivot.
rearm_policy:
  0=consume episode after signal;
  1=same episode -> PULLBACK_ACTIVE, require fresh exhaustion;
  2=same episode -> EXHAUSTION_CANDIDATE, require new reclaim then later reaccel;
  3=same episode -> PULLBACK_ACTIVE, require new adverse S15 extreme then exhaustion.
"""
from __future__ import annotations

import numpy as np
from numba import njit
import delta_r037_dh02_s08_cleanroom_parity as base

CE=.6468
DECL=.4533
BUF=.3242
MAXAGE=int(round(513.6575*1000.0))
DEPTH=.4743
REFF=.2854

@njit(cache=True)
def detect(t,mid,s5e,s5c,s5eff,s15e,s15h,s15l,s15c,s15eff,s30e,s30eff,
           m5e,m5atr,pe,ps,linv,sinv,phi,plo,pht,plt,pivot_policy,rearm_policy):
    state=np.zeros(2,np.int8)
    start=np.zeros(2,np.int64)
    atr=np.zeros(2,np.float64)
    imp=np.zeros(2,np.int64)
    adv=np.zeros(2,np.int64)
    nonew=np.zeros(2,np.int64)
    rtime=np.zeros(2,np.int64)
    eid=np.zeros(2,np.int64)
    last_signal=np.zeros(2,np.int64)
    needs_new_adverse=np.zeros(2,np.int8)

    outt=np.empty(100000,np.int64)
    outs=np.empty(100000,np.int8)
    oute=np.empty(100000,np.int64)

    n=0
    seq=0
    # pullback, exhaustion, reclaim, signal, parent_invalid, structural_invalid,
    # expired, depth_ready, countereff_ready, no_new_extreme_ready,
    # pivot_unavailable, rearms_after_signal, new_adverse_retry_satisfied
    cnt=np.zeros(13,np.int64)

    pi=-1
    parent=0
    longinv=0
    shortinv=0
    last15=-1
    last5=-1

    for i in range(t.size):
        tm=int(t[i])
        px=int(mid[i])

        while pi+1<pe.size and pe[pi+1]<=tm:
            pi+=1
            parent=int(ps[pi])
            longinv=int(linv[pi])
            shortinv=int(sinv[pi])

        if parent==1 and state[0]==0 and (imp[0]==0 or px>imp[0]):
            imp[0]=px
        if parent==-1 and state[1]==0 and (imp[1]==0 or px<imp[1]):
            imp[1]=px

        j15=base.bidx(s15e,tm)
        j30=base.bidx(s30e,tm)
        jm5=base.bidx(m5e,tm)
        j5=base.bidx(s5e,tm)

        for z in range(2):
            if state[z]==0:
                continue
            side=1 if z==0 else -1

            if parent==-side:
                cnt[4]+=1
                state[z]=0
                imp[z]=px
                rtime[z]=0
                last_signal[z]=0
                needs_new_adverse[z]=0
                continue

            if tm-start[z]>MAXAGE:
                cnt[6]+=1
                state[z]=0
                imp[z]=px
                rtime[z]=0
                last_signal[z]=0
                needs_new_adverse[z]=0
                continue

            iv=longinv if side==1 else shortinv
            if iv and atr[z]>0:
                bad=px<iv-BUF*atr[z] if side==1 else px>iv+BUF*atr[z]
                if bad:
                    cnt[5]+=1
                    state[z]=0
                    imp[z]=px
                    rtime[z]=0
                    last_signal[z]=0
                    needs_new_adverse[z]=0
                    continue

        if j15>=4 and j15!=last15:
            last15=j15
            if jm5>=13 and j30>=4:
                aa=float(m5atr[jm5])
                if aa>0:
                    for z in range(2):
                        side=1 if z==0 else -1
                        st=int(state[z])

                        if st==0:
                            if parent!=side or imp[z]==0:
                                continue
                            dn=(-side*(int(s15c[j15])-imp[z]))/aa
                            ce=-side*float(s15eff[j15])
                            if dn>=DEPTH:
                                cnt[7]+=1
                            if ce>=CE:
                                cnt[8]+=1
                            if dn>=DEPTH and ce>=CE:
                                seq+=1
                                state[z]=1
                                start[z]=tm
                                atr[z]=aa
                                eid[z]=seq
                                adv[z]=int(s15l[j15]) if side==1 else int(s15h[j15])
                                nonew[z]=0
                                rtime[z]=0
                                last_signal[z]=0
                                needs_new_adverse[z]=0
                                cnt[0]+=1
                            continue

                        now=int(s15l[j15]) if side==1 else int(s15h[j15])
                        new=now<adv[z] if side==1 else now>adv[z]
                        if new:
                            adv[z]=now
                            nonew[z]=0
                            if needs_new_adverse[z]:
                                needs_new_adverse[z]=0
                                cnt[12]+=1
                        else:
                            nonew[z]+=1

                        if nonew[z]>=1:
                            cnt[9]+=1

                        if st==1:
                            if needs_new_adverse[z]:
                                continue
                            d15=(-side*float(s15eff[j15-1]))-(-side*float(s15eff[j15]))
                            d30=(-side*float(s30eff[j30-1]))-(-side*float(s30eff[j30]))
                            ok=(d15>=DECL or d30>=DECL)
                            if ok and nonew[z]>=1:
                                state[z]=2
                                cnt[1]+=1

        if j5>=4 and j5!=last5:
            last5=j5
            close5=int(s5c[j5])

            # Reacceleration is evaluated before a new reclaim on this completed S5.
            for z in range(2):
                if state[z]!=3:
                    continue
                side=1 if z==0 else -1
                if tm<=rtime[z]:
                    continue
                net=int(s5c[j5])-int(s5c[j5-4])
                eff=float(s5eff[j5])
                if side*eff>=REFF and side*net>0:
                    if n<outt.size:
                        outt[n]=tm
                        outs[n]=side
                        oute[n]=eid[z]
                        n+=1
                        cnt[3]+=1

                    if rearm_policy==0:
                        state[z]=0
                        imp[z]=px
                        rtime[z]=0
                        last_signal[z]=0
                        needs_new_adverse[z]=0
                    elif rearm_policy==1:
                        state[z]=1
                        nonew[z]=0
                        if j15>=0:
                            adv[z]=int(s15l[j15]) if side==1 else int(s15h[j15])
                        rtime[z]=0
                        last_signal[z]=tm
                        needs_new_adverse[z]=0
                        cnt[11]+=1
                    elif rearm_policy==2:
                        state[z]=2
                        rtime[z]=0
                        last_signal[z]=tm
                        needs_new_adverse[z]=0
                        cnt[11]+=1
                    else:
                        state[z]=1
                        nonew[z]=0
                        if j15>=0:
                            adv[z]=int(s15l[j15]) if side==1 else int(s15h[j15])
                        rtime[z]=0
                        last_signal[z]=tm
                        needs_new_adverse[z]=1
                        cnt[11]+=1

            # LOCAL_RECLAIM on completed S5 through a causally known S15 pivot.
            if j15>=0:
                for z in range(2):
                    if state[z]!=2:
                        continue
                    if last_signal[z] and tm<=last_signal[z]:
                        continue
                    side=1 if z==0 else -1
                    lev=int(phi[j15]) if side==1 else int(plo[j15])
                    pt=int(pht[j15]) if side==1 else int(plt[j15])
                    if lev==0:
                        cnt[10]+=1
                        continue
                    allowed=True if pivot_policy==1 else pt>start[z]
                    if not allowed:
                        continue
                    cross=close5>lev if side==1 else close5<lev
                    if cross:
                        state[z]=3
                        rtime[z]=tm
                        cnt[2]+=1

    return outt[:n],outs[:n],oute[:n],cnt
