#!/usr/bin/env python3
"""Delta-A-Alpha V1 cooperative vertical grid research ENGINEERING REBUILD 029.

A unified, executable L0-L8 EVENT BUS, not a February-optimized result, nor a
source-exact replication of 131E/134K.  All layers propose independently;
a single L8 funds at most one supplemental ticket per quote.  A bounded TTL
proposal queue retains simultaneous L3/L5/L6/L7 opportunities.  No future bars
or future P/L are used.  L5 unlock requires actual closed funded children.
Historical research fills are observed Dukascopy Bid/Ask with research fee;
not Coinexx MT5 execution or small-capital certification.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

DATA=Path('/mnt/data'); OUT=DATA/'daa_full_vertical_rebuild_029'; OUT.mkdir(exist_ok=True)
JAN=DATA/'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
FEB=DATA/'XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'
FEB0=1769904000000; DAY=86400000
SHA={'jan':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',
'feb':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5'}
SOURCES={3:'L3_HOURLY',4:'L4_ASIA',5:'L5_WATCHDOG',6:'L6_TREND_WITHIN_TREND',7:'L7_RECOVERY',8:'L3_HOURLY_CONTINUATION_RESEARCH'}
# Real original 019 source-specific NY phase geometry. Raw price units = $0.001.
TP16=np.array([40000,0,40000,40000,40000,0],np.int32)
SL16=np.array([20000,40000,40000,60000,60000,40000],np.int32)
H16=np.array([1200000,1200000,900000,1200000,1200000,1200000],np.int64)
TP17=np.array([80000,80000,120000,80000,0,120000],np.int32)
SL17=np.array([40000,40000,60000,40000,60000,120000],np.int32)
H17=np.full(6,1800000,np.int64)
TP18=np.array([12000,12000,12000,8000,4000,4000],np.int32)
SL18=np.array([8000,8000,6000,8000,1000,2000],np.int32)
H18=np.array([60000,60000,20000,30000,5000,10000],np.int64)
NY17_MIN=np.array([8000,8000,6000,3000,1000,0],np.int32)
NY18_MIN=np.array([0,0,500,500,2000,1000],np.int32)
NY18_MAX=np.array([100000000,100000000,100000000,100000000,100000000,6000],np.int32)
LONDON_THRESH=np.array([0,0,0,0,0,0,0,1000,3000,0,0,2000,0,4000,4000,3000,0,0,0,0,0,0,0,0],np.int32)

@njit(cache=True)
def session(t):
    """February 2026 UTC session ownership; explicit source DST boundary in future months."""
    h=(t//3600000)%24
    if h>=23 or h<7:return 0  # Asia
    if h<9:return 1
    if h<13:return 2
    if h<16:return 3
    if h<20:return 4
    if h<22:return 5
    return 6

@njit(cache=True)
def london_hold(h,h4,h1,m15,m5):
    # Exact source 019 London HTF/subphase route conditions, not naive voting.
    if h4!=1 or h1!=1:return 0
    if h==7:
        if m15==-1 and m5==-1:return 1800000
    elif h==8:
        if m15==-1 and m5==-1:return 300000
        if m15==-1 and m5==1:return 900000
    elif h==9:
        if (m15==-1 and m5==-1) or (m15==1 and m5==-1):return 1800000
    elif h==11:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 1800000
        if m15==1 and m5==-1:return 900000
    elif h==12:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
        if m15==1 and m5==-1:return 1800000
    elif h==13:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
        if m15==1 and m5==-1:return 1800000
    elif h==14:
        if m15==-1 and m5==-1:return 1800000
        if m15==-1 and m5==1:return 900000
    elif h==15:
        if (m15==-1 and m5==1) or (m15==1 and m5==-1) or (m15==1 and m5==1):return 1800000
    return 0

@njit(cache=True)
def ny_dir(h,h4,h1,m15,m5):
    if h==16:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==1 and m5==-1:return 1
        if h4==1 and h1==1 and m15==-1 and m5==1:return 1
    elif h==17:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
        if h4==1 and h1==1 and m15==-1 and m5==-1:return 1
    elif h==18:
        if h4==-1 and h1==-1 and m15==-1 and m5==-1:return -1
    return 0

@njit(cache=True)
def session_grid_gap(s,r12,adaptive):
    base=750 if s==0 else (1000 if s==2 else (750 if s==3 else (1500 if s==4 else (500 if s==5 else 0))))
    if base==0 or not adaptive or r12==0:return base
    # Causal bounded geometry for evaluation ONLY; no month tuning.
    ratio=r12/5000.
    if ratio<0.75:ratio=0.75
    if ratio>1.6:ratio=1.6
    return max(250,int(base*ratio))

@njit(cache=True)
def layer_budget(src,cap):
    if src==3 or src==8:return max(2,int(cap*.8))
    if src==4:return max(1,int(cap*.25))
    if src==5:return max(2,int(cap*.45))
    if src==6:return max(2,int(cap*.45))
    return max(1,int(cap*.10))

@njit(cache=True)
def run(t,a,b,h4,h1,m15,m5,mbkey,mbrange,cap,capital,lev,adaptive,max_spread=3000,emit_from=FEB0,hourly_expansion=0):
    """One chronological quote loop, independent L3/L4/L5/L6/L7 proposals,
    finite queue (no erased concurrent signals), then one global L8 adjudication.
    """
    aopen=np.zeros(cap,np.uint8);typ=np.zeros(cap,np.int8);direc=np.zeros(cap,np.int8)
    entry=np.zeros(cap,np.int32);entry_i=np.zeros(cap,np.int64);expires=np.zeros(cap,np.int64)
    targets=np.zeros(cap,np.int32);stops=np.zeros(cap,np.int32);owner=np.zeros(cap,np.int32)
    open_count=np.zeros(9,np.int32)
    # Q entries: at most 5 new sources each tick; each remains eligible up to 1500ms.
    QMAX=24
    qactive=np.zeros(QMAX,np.uint8);qtyp=np.zeros(QMAX,np.int8);qdir=np.zeros(QMAX,np.int8)
    qlife=np.zeros(QMAX,np.int64);qtp=np.zeros(QMAX,np.int32);qsl=np.zeros(QMAX,np.int32)
    qowner=np.zeros(QMAX,np.int32);qborn=np.zeros(QMAX,np.int64);qexpire=np.zeros(QMAX,np.int64)
    # WATCHDOG cell state; cell-day 6 ten-minute slices *243 actual signature states.
    CW=6*243
    wd_start=np.zeros(CW,np.int64);wd_end=np.zeros(CW,np.int64);wd_depth=np.zeros(CW,np.int16)
    wd_streak=np.zeros(CW,np.int16);wd_unlock=np.zeros(CW,np.uint8);wd_occupied=np.zeros(CW,np.uint8)
    wd_reference=np.zeros(CW,np.int32);wd_day=-1;wd_sent=np.zeros(CW,np.uint8)
    # L7 pending recovery only from actually funded loss
    rec_until=0;rec_price=0;rec_dir=0;rec_valid=0
    # L0 final ledger
    LIM=500000
    E=np.empty(LIM,np.int64);X=np.empty(LIM,np.int64);P=np.empty(LIM,np.float64)
    S=np.empty(LIM,np.int8);D=np.empty(LIM,np.int8);R=np.empty(LIM,np.int8);EN=np.empty(LIM,np.int32)
    O=np.empty(LIM,np.int32)
    n=0;closed_sum=0.;closed_peak=0.;baldd=0.;eqpeak=capital;eqdd=0.;mineq=capital
    minfree=capital;maxopen=0;maxlots=0.;rec_active=0;liq=0
    proposals=np.zeros(9,np.int64);fills=np.zeros(9,np.int64);denial=np.zeros((9,7),np.int64)
    dropped=np.zeros(9,np.int64);win_closed=np.zeros(9,np.int64);loss_closed=np.zeros(9,np.int64)
    init_quote=-1;init_eligible=-1;first_filled=-1;last_entry_i=-1
    current_s=-1;anchor=0;previous_cell=0;grid_seen=np.zeros((8192,2),np.uint8)
    minute=-1;minute_anchor=0;ladder_h=0;ladder_l=0;tick_count=0
    recent5=-1;range12=0;range48=0;bar_cursor=0
    hourly_last=np.full(24,-999999999999999,np.int64);hourly_prev=np.zeros(24,np.int8)
    expansion_last=np.full(24,-999999999999999,np.int64)
    native_ladder=np.zeros(24,np.int32);native_prevdir=np.zeros(24,np.int8)
    for i in range(len(t)):
        ti=int(t[i]);ask=int(a[i]);bid=int(b[i]);mid=(ask+bid)//2;spread=ask-bid
        if ti<emit_from:continue
        if init_quote<0:init_quote=i
        h=int((ti//3600000)%24);b10=int((ti//600000)%6)
        s=session(ti)
        m5bucket=ti//300000
        if m5bucket!=recent5:
            recent5=m5bucket
            # bars with key == current bucket are incomplete and never used
            while bar_cursor+1<len(mbkey) and mbkey[bar_cursor+1]<m5bucket:bar_cursor+=1
            if len(mbkey)>0 and mbkey[bar_cursor]<m5bucket:
                start=max(0,bar_cursor-11);r=mbrange[start:bar_cursor+1]
                range12=int(np.median(r))
                r48=mbrange[max(0,bar_cursor-47):bar_cursor+1]
                range48=int(np.median(r48))
        hs=int(h4[i]);hi=int(h1[i]);ph=int(m15[i]);tr=int(m5[i])
        if init_eligible<0 and hs!=0 and hi!=0 and ph!=0 and tr!=0:init_eligible=i
        # L0 CLOSE BEFORE new proposals; funded wins only, no shadow unlock
        floating=0.
        for z in range(cap):
            if aopen[z]==0:continue
            d=int(direc[z]);close=bid if d>0 else ask
            pnlraw=d*(close-int(entry[z]));reason=0
            if targets[z]!=0 and pnlraw>=d*(targets[z]-entry[z]):reason=1
            elif stops[z]!=0 and pnlraw<=d*(stops[z]-entry[z]):reason=2
            elif ti>=expires[z]:reason=3
            if reason>0:
                p=pnlraw/1000.-.02
                if n>=LIM:raise RuntimeError('ledger cap exceeded')
                E[n]=entry_i[z];X[n]=i;P[n]=p;S[n]=typ[z];D[n]=d;R[n]=reason;EN[n]=entry[z];O[n]=owner[z];n+=1
                closed_sum+=p;open_count[int(typ[z])]-=1;aopen[z]=0
                if p>0:win_closed[int(typ[z])]+=1
                else:loss_closed[int(typ[z])]+=1
                if typ[z]==5:
                    c=owner[z];wd_occupied[c]=0;wd_reference[c]=close
                    if p>0 and ti-t[entry_i[z]]<=60000:
                        wd_streak[c]+=1
                        if wd_streak[c]>=4:wd_unlock[c]=1
                    else:
                        wd_streak[c]=0;wd_unlock[c]=0;wd_start[c]=0
                if typ[z]==7:rec_active-=1
                if typ[z] in (3,4,6) and p<0 and reason in (2,3):
                    rec_valid=1;rec_until=ti+90000;rec_price=close;rec_dir=-d
            else:floating+=pnlraw/1000.-.01
        if closed_sum>closed_peak:closed_peak=closed_sum
        if closed_peak-closed_sum>baldd:baldd=closed_peak-closed_sum
        equity=capital+closed_sum+floating
        if equity>eqpeak:eqpeak=equity
        if eqpeak-equity>eqdd:eqdd=eqpeak-equity
        if equity<mineq:mineq=equity
        opened=0
        for z in range(9):opened+=open_count[z]
        if opened>maxopen:maxopen=opened
        marginunit=mid/1000./lev  # 0.01 lot assumed 1oz, leverage configurable
        used=opened*marginunit
        free=equity-used
        if free<minfree:minfree=free
        # Hard stopout: flatten, prevent funding; research model only.
        if equity<=max(0.,used*.5):
            liq+=1
            for z in range(cap):
                if aopen[z]:
                    d=int(direc[z]);close=bid if d>0 else ask;p=d*(close-int(entry[z]))/1000.-.02
                    E[n]=entry_i[z];X[n]=i;P[n]=p;S[n]=typ[z];D[n]=d;R[n]=5;EN[n]=entry[z];O[n]=owner[z];n+=1
                    closed_sum+=p;aopen[z]=0;open_count[int(typ[z])]-=1
            break
        # L1 session-specific causal grid
        if s!=current_s:
            current_s=s;anchor=mid;previous_cell=0;grid_seen[:]=0;native_ladder[:]=0;native_prevdir[:]=0
        gap=session_grid_gap(s,range12,adaptive)
        cross=0
        if gap:
            ce=(mid-anchor)//gap
            if ce!=previous_cell:
                d=1 if ce>previous_cell else -1
                # one source-owned physical proposal per observed boundary first passage
                token=(ce if d>0 else previous_cell)+4096
                if 0<=token<8192 and grid_seen[token,1 if d>0 else 0]==0:
                    grid_seen[token,1 if d>0 else 0]=1;cross=d
                previous_cell=ce
        m=ti//60000
        if m!=minute:
            minute=m;minute_anchor=mid;ladder_h=0;ladder_l=0;tick_count=0
        tick_count+=1
        # Window-local cell and child genealogy for L5
        if ti//DAY!=wd_day:
            wd_day=ti//DAY;wd_start[:]=0;wd_end[:]=0;wd_depth[:]=0
            wd_streak[:]=0;wd_unlock[:]=0;wd_occupied[:]=0;wd_sent[:]=0
        sig=(hs+1)*81+(hi+1)*27+(ph+1)*9+(tr+1)*3+2
        c=int(b10*243+sig)
        # Independently prepare all FIVE economic families (do not elif them).
        # Proposal arrays are per-tick: no source silently short-circuits another.
        ss=np.zeros(6,np.int8);ds=np.zeros(6,np.int8);life=np.zeros(6,np.int64)
        tp=np.zeros(6,np.int32);sl=np.zeros(6,np.int32);own=np.zeros(6,np.int32)
        j=0
        # L3 original 019 hourly heartbeat; own 131D historical entry signatures.
        duration=0;hd=0;threshold=0;htt=0;hsl=0;eligible=False
        if 7<=h<=15:
            duration=london_hold(h,hs,hi,ph,tr);hd=1
            threshold=int(LONDON_THRESH[h]);eligible=duration>0 and mid-minute_anchor>=threshold
        elif h in (16,17,18):
            hd=ny_dir(h,hs,hi,ph,tr)
            if hd:
                dis=(mid-minute_anchor)*hd
                if h==16:
                    eligible=dis>=500;duration=int(H16[b10]);htt=int(TP16[b10]);hsl=int(SL16[b10])
                elif h==17:
                    eligible=dis>=int(NY17_MIN[b10]);duration=int(H17[b10]);htt=int(TP17[b10]);hsl=int(SL17[b10])
                else:
                    eligible=dis>=int(NY18_MIN[b10]) and dis<int(NY18_MAX[b10]);duration=int(H18[b10]);htt=int(TP18[b10]);hsl=int(SL18[b10])
        # Legacy January owned 131D cells; separate from signal production.
        owns=(
          (h==9 and b10==0 and hs==1 and hi==1 and ph==1 and tr==-1) or
          (h==11 and b10 in (2,3) and hs==1 and hi==1 and ph==-1 and tr==-1) or
          (h==11 and b10==3 and hs==1 and hi==1 and ph==1 and tr==-1) or
          (h==12 and b10 in (0,1,2) and hs==1 and hi==1 and ph==-1 and tr==-1) or
          (h==13 and b10 in (2,3) and hs==1 and hi==1 and ph==-1 and tr==-1) or
          (h==14 and b10==3 and hs==1 and hi==1 and ph==-1 and tr==1) or
          (h==15 and b10 in (2,3) and hs==1 and hi==1 and ph==1 and tr==1) or
          (h==16 and b10 in (0,3,4) and hs==1 and hi==1 and ph==1 and tr==-1))
        if eligible and owns and (hourly_prev[h]==0 or ti-hourly_last[h]>=250):
            ss[j]=3;ds[j]=hd;life[j]=duration;tp[j]=htt;sl[j]=hsl;j+=1
            hourly_last[h]=ti
        hourly_prev[h]=1 if eligible and owns else 0
        # L3B optional HIGH-VOLUME residual continuation, a separate owner/sleeve,
        # not selected with future February winning cells or a February date key.
        # Its own funded ledger determines whether it improves or damages the system.
        if hourly_expansion and 7<=h<=18 and hs!=0 and hs==hi and spread<=1600:
            exdir=hs
            displacement=(mid-minute_anchor)*exdir
            # H4=environment, H1=parent, M15=continuation, M5=transfer timing.
            if displacement>=2250 and ph==exdir and tr!=0 and ti-expansion_last[h]>=1250:
                ss[j]=8;ds[j]=exdir;life[j]=60000;tp[j]=5000;sl[j]=2500;j+=1
                expansion_last[h]=ti
        # L4 independent Asia geometry
        if s==0 and cross and hs and hi and ph and tr:
            if hs==hi and ph==tr==-hi and cross==tr:
                ss[j]=4;ds[j]=tr;life[j]=300000;tp[j]=3000;sl[j]=1400;j+=1
            elif hs==hi and ph==-hi and tr==hi and cross==tr:
                ss[j]=4;ds[j]=tr;life[j]=120000;tp[j]=2500;sl[j]=1600;j+=1
        # L5 Watchdog first-funded parent / 4 funded fast-win unlock, true time ordering.
        wd_direction=ny_dir(17,hs,hi,ph,tr) if h==17 else 0
        if wd_direction and wd_occupied[c]==0 and wd_depth[c]<30 and spread<=2000:
            if wd_start[c]==0:
                # Scout needs no local learned history; one initial paid scout per 10-min signature cell
                if wd_sent[c]==0:
                    ss[j]=5;ds[j]=wd_direction;life[j]=120000;tp[j]=1190 if b10!=5 else 1100;sl[j]=0;own[j]=c;j+=1
            elif ti<wd_end[c] and wd_streak[c]>0 and (mid-wd_reference[c])*wd_direction>=250:
                ss[j]=5;ds[j]=wd_direction;life[j]=min(120000,wd_end[c]-ti)
                tp[j]=1190 if b10!=5 else 1100;sl[j]=0;own[j]=c;j+=1
            elif ti>=wd_end[c] and wd_unlock[c] and wd_depth[c]<30:
                ss[j]=5;ds[j]=wd_direction;life[j]=120000;tp[j]=1190 if b10!=5 else 1100;sl[j]=0;own[j]=c;j+=1
        # L6 trend within trend: grid-reclaim native and positive micro-intraminute stair.
        if s in (2,3,4,5) and hs and hi and ph and tr:
            nd=0;ntime=0;ntp=0;nsl=0
            if cross and hs==hi and ph==hi and tr==-hi and cross==hi:
                nd=cross;ntime=180000;ntp=5000;nsl=2000
            elif cross and s==5 and hs==hi==ph==tr and cross==hi:
                nd=cross;ntime=240000;ntp=4500;nsl=2000
            elif cross and s==3 and hs!=hi and ph==tr and cross==tr:
                nd=cross;ntime=120000;ntp=3000;nsl=1800
            # Same original trend-within-trend concept, enhanced independent minute stair.
            if nd==0 and hs==hi and ph==hs and tr==hs:
                movement=(mid-minute_anchor)*hs
                if movement>=1000 and movement//1000>native_ladder[h]:
                    native_ladder[h]=movement//1000
                    nd=hs;ntime=45000;ntp=3500;nsl=1800
            if nd:
                ss[j]=6;ds[j]=nd;life[j]=ntime;tp[j]=ntp;sl[j]=nsl;j+=1
        # L7 recovery only after actual funded failed ignition, no Martingale.
        if rec_valid and ti<=rec_until and rec_active<max(1,cap//10) and (mid-rec_price)*rec_dir>=750 and spread<=1600:
            if tr==rec_dir and (ph==rec_dir or (hs==rec_dir and hi==rec_dir)):
                ss[j]=7;ds[j]=rec_dir;life[j]=120000;tp[j]=3000;sl[j]=2500;j+=1
                rec_valid=0
        elif rec_valid and ti>rec_until:rec_valid=0
        # Store independent proposals in finite queue (at most one per source in-flight).
        for k in range(j):
            src=int(ss[k]);d=int(ds[k]);if_duplicate=False
            for q in range(QMAX):
                if qactive[q] and qtyp[q]==src and qdir[q]==d and qowner[q]==own[k]:
                    if_duplicate=True;break
            if if_duplicate:continue
            proposals[src]+=1
            slot=-1
            for q in range(QMAX):
                if qactive[q]==0:slot=q;break
            if slot<0:
                dropped[src]+=1;continue
            qactive[slot]=1;qtyp[slot]=src;qdir[slot]=d;qlife[slot]=life[k]
            qtp[slot]=tp[k];qsl[slot]=sl[k];qowner[slot]=own[k];qborn[slot]=ti;qexpire[slot]=ti+1500
        # L8 select one physically fundable ticket per observed tick, after all layers proposed.
        # A value-based score uses ONLY PREVIOUSLY FUNDED CLOSED outcomes and bounded layer preference.
        best=-1;bestscore=-1000000.
        for q in range(QMAX):
            if not qactive[q]:continue
            src=int(qtyp[q])
            if ti>qexpire[q]:qactive[q]=0;denial[src,6]+=1;continue
            if spread>max_spread:denial[src,1]+=1;continue
            if adaptive and src in (4,6) and range12>0 and spread*5>range12:
                denial[src,2]+=1;continue
            if opened>=cap:denial[src,0]+=1;continue
            if (open_count[3]+open_count[8] if src in (3,8) else open_count[src])>=layer_budget(src,cap):denial[src,3]+=1;continue
            if free<marginunit+max(0.,equity*.1):denial[src,4]+=1;continue
            if floating < -0.25*capital:denial[src,5]+=1;continue
            if src==5 and wd_occupied[qowner[q]]!=0:denial[src,3]+=1;continue
            if src==7 and rec_active>=max(1,cap//10):denial[src,3]+=1;continue
            priority=90. if src==3 else (87. if src==8 else (84. if src==5 else (82. if src==6 else (75. if src==4 else 65.))))
            # Completion-only funded previous evidence; never outcome-selected future state.
            nclosed=win_closed[src]+loss_closed[src]
            if nclosed>=8:priority+=12.*(win_closed[src]-loss_closed[src])/nclosed
            # Oldest eligible proposal wins inside same rank => fair source scheduling
            priority+=(ti-qborn[q])*.00005
            if priority>bestscore:bestscore=priority;best=q
        if best>=0 and last_entry_i!=i:
            z=-1
            for k in range(cap):
                if aopen[k]==0:z=k;break
            if z>=0:
                src=int(qtyp[best]);d=int(qdir[best]);e=ask if d>0 else bid
                aopen[z]=1;typ[z]=src;direc[z]=d;entry[z]=e;entry_i[z]=i
                expires[z]=ti+max(1,qlife[best]);targets[z]=e+d*qtp[best] if qtp[best]>0 else 0
                stops[z]=e-d*qsl[best] if qsl[best]>0 else 0
                owner[z]=qowner[best]
                if src==5:
                    c=int(owner[z]);wd_occupied[c]=1;wd_depth[c]+=1;wd_sent[c]=1
                    if wd_start[c]==0:wd_start[c]=ti;wd_end[c]=ti+1800000
                    wd_reference[c]=mid
                if src==7:rec_active+=1
                open_count[src]+=1;fills[src]+=1;last_entry_i=i
                if first_filled<0:first_filled=i
                qactive[best]=0
    # Explicit end of tested file mark-to-market liquidation; research convention
    zi=len(t)-1
    for z in range(cap):
        if aopen[z]:
            d=int(direc[z]);close=int(b[zi] if d>0 else a[zi]);p=d*(close-int(entry[z]))/1000.-.02
            E[n]=entry_i[z];X[n]=zi;P[n]=p;S[n]=typ[z];D[n]=d;R[n]=4;EN[n]=entry[z];O[n]=owner[z];n+=1
    return (E[:n],X[:n],P[:n],S[:n],D[:n],R[:n],EN[:n],O[:n],proposals,fills,denial,dropped,
        maxopen,baldd,eqdd,mineq,minfree,liq,init_quote,init_eligible,first_filled)

def completed_states(t,b,period_ms):
    key=t//period_ms;beg=np.r_[0,1+np.flatnonzero(key[1:]!=key[:-1])];end=np.r_[beg[1:]-1,len(t)-1]
    close=b[end].astype(float);ff=np.empty(len(close));ss=np.empty(len(close))
    ff[0]=close[0];ss[0]=close[0];af=2/9;az=2/22
    for k in range(1,len(close)):
        ff[k]=ff[k-1]+af*(close[k]-ff[k-1]);ss[k]=ss[k-1]+az*(close[k]-ss[k-1])
    states=np.sign(ff-ss).astype(np.int8);ip=np.searchsorted(key[beg],key,side='left')-1
    out=np.zeros(len(t),np.int8);ok=ip>=0;out[ok]=states[ip[ok]]
    return out

def load_data(test_days=0,warm_days=14):
    cols=['timestamp_ms_utc','ask_raw','bid_raw'];types={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'}
    d1=pd.read_csv(JAN,compression='gzip',usecols=cols,dtype=types)
    d1=d1[d1.timestamp_ms_utc>=FEB0-warm_days*DAY]
    d2=pd.read_csv(FEB,compression='gzip',usecols=cols,dtype=types)
    if test_days:d2=d2[d2.timestamp_ms_utc<FEB0+test_days*DAY]
    df=pd.concat([d1,d2],ignore_index=True);del d1,d2
    t=df.timestamp_ms_utc.to_numpy();a=df.ask_raw.to_numpy();b=df.bid_raw.to_numpy();del df
    assert np.all(t[1:]>=t[:-1]) and np.all(a>=b)
    states=[completed_states(t,b,tf) for tf in (14400000,3600000,900000,300000)]
    mid=(a.astype(np.int64)+b.astype(np.int64))//2
    keys=t//300000;beg=np.r_[0,1+np.flatnonzero(keys[1:]!=keys[:-1])]
    m5key=keys[beg];ranges=(np.maximum.reduceat(mid,beg)-np.minimum.reduceat(mid,beg)).astype(np.int32)
    return t,a,b,*states,m5key,ranges

def report(t,a,b,ret,capital,cap,tag):
    E,X,P,S,D,R,EN,O,proposals,fills,denials,dropped,*stats=ret
    assert len(E)>0,'no trades generated'
    exitquotes=np.where(D>0,b[X],a[X]);check=(exitquotes.astype(np.int64)-EN.astype(np.int64))*D/1000.-.02
    assert np.max(np.abs(check-P))<1e-9
    assert np.array_equal(EN,np.where(D>0,a[E],b[E]))
    assert np.all(X>=E) and np.all(t[E]>=FEB0)
    assert len(np.unique(E))==len(E),'one ticket per tick violated'
    frame=pd.DataFrame({'entry_idx':E,'exit_idx':X,'entry_utc':pd.to_datetime(t[E],unit='ms',utc=True),
        'exit_utc':pd.to_datetime(t[X],unit='ms',utc=True),'layer':S,'direction':D,'entry_raw':EN,
        'exit_raw':exitquotes,'owner_cell':O,'reason':R,'net':P})
    frame['day_utc']=frame.exit_utc.dt.strftime('%Y-%m-%d');frame['week_utc']=frame.exit_utc.dt.strftime('%G-W%V')
    def metrics(g):
        ps=g.net.to_numpy();gp=ps[ps>0].sum();gl=ps[ps<=0].sum()
        return pd.Series({'net':float(ps.sum()),'trades':len(ps),'gross_profit':float(gp),'gross_loss':float(gl),
        'pf':float(gp/-gl) if gl<0 else float('nan'),'win':float((ps>0).mean()),'expectancy':float(ps.mean())})
    daily=frame.groupby('day_utc',sort=True).apply(metrics,include_groups=False).reset_index()
    weekly=frame.groupby('week_utc',sort=True).apply(metrics,include_groups=False).reset_index()
    layers=frame.groupby('layer',sort=True).apply(metrics,include_groups=False).reset_index()
    m=metrics(frame)
    result={'unit':'DAA_V1_029_COOPERATIVE_VERTICAL_GRID_REBUILD','status':'INTEGRATED_RESEARCH_ENGINE_NOT_SOURCE_EXACT_134K_OR_BROKER_CERTIFIED',
     'scope':'February 2026 historical development; Jan bars pre-T0 only','capital':capital,'position_cap':cap,
     'net':float(m['net']),'trades':int(m['trades']),'gross_profit':float(m['gross_profit']),'gross_loss':float(m['gross_loss']),
     'profit_factor':float(m['pf']),'win_rate':float(m['win']),'expectancy':float(m['expectancy']),
     'positive_days':int((daily.net>0).sum()),'active_days':len(daily),
     'positive_weeks':int((weekly.net>0).sum()),'active_weeks':len(weekly),
     'max_open':int(stats[0]),'balance_drawdown':float(stats[1]),'floating_equity_drawdown':float(stats[2]),
     'min_equity':float(stats[3]),'min_modeled_free_margin':float(stats[4]),'stopout_events':int(stats[5]),
     'first_quote_utc':str(pd.Timestamp(t[stats[6]],unit='ms',tz='UTC')) if stats[6]>=0 else None,
     'first_state_ready_utc':str(pd.Timestamp(t[stats[7]],unit='ms',tz='UTC')) if stats[7]>=0 else None,
     'first_funded_trade_utc':str(pd.Timestamp(t[stats[8]],unit='ms',tz='UTC')) if stats[8]>=0 else None,
     'by_source':[dict(layer=SOURCES.get(int(row.layer),'other'),trades=int(row.trades),net=float(row.net),gross_loss=float(row.gross_loss)) for row in layers.itertuples()],
     'source_proposals':proposals.tolist(),'source_fills':fills.tolist(),'denials':denials.tolist(),'proposal_queue_dropped':dropped.tolist(),
     'limitations':['Original 049/051/075/084/119 parent-generation and Feb134K native/Asia outcome-selected cells not yet source-equivalent',
       'MT5 broker margin, slippage, swap, commission, stopout unknown; approximate research model only',
       'no February pristine blindness: earlier February data has been studied',
       'No guaranteed 5-minute first fill; order-eligibility timing can precede first valid market signal']}
    for typ,df in [('trades',frame),('daily',daily),('weekly',weekly),('layers',layers)]:df.to_csv(OUT/f'{tag}_{typ}.csv',index=False)
    (OUT/f'{tag}_metrics.json').write_text(json.dumps(result,indent=2,default=str))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--days',type=int,default=0);ap.add_argument('--cap',type=int,default=64)
    ap.add_argument('--capital',type=float,default=100000.);ap.add_argument('--leverage',type=int,default=100)
    ap.add_argument('--adaptive',type=int,choices=(0,1),default=1);ap.add_argument('--max-spread',type=int,default=3000)
    ap.add_argument('--hourly-expansion',type=int,choices=(0,1),default=0)
    args=ap.parse_args();tm=time.monotonic();data=load_data(args.days)
    print('LOADED',len(data[0]),'FEB_TICKS',int((data[0]>=FEB0).sum()),'SECONDS',round(time.monotonic()-tm,2),flush=True)
    ret=run(*data,args.cap,args.capital,args.leverage,args.adaptive,args.max_spread,FEB0,args.hourly_expansion)
    tag=f'coop029_cap{args.cap}_a{args.adaptive}_h{args.hourly_expansion}_d{args.days or 28}'
    m=report(data[0],data[1],data[2],ret,args.capital,args.cap,tag)
    print(json.dumps({k:m[k] for k in ['net','trades','gross_loss','profit_factor','win_rate','max_open','floating_equity_drawdown','positive_days','active_days','by_source']},default=str),flush=True)
    print('RUNTIME_SECONDS',round(time.monotonic()-tm,2),flush=True)
if __name__=='__main__':main()