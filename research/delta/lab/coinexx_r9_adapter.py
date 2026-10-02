from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from math import floor
import numpy as np
import pandas as pd
from numba import njit

DAY_MS=86_400_000
US_DST_START_2026_MS=np.int64(1772953200000)
UK_DST_START_2026_MS=np.int64(1774746000000)

@dataclass(frozen=True)
class CoinexxR9Config:
    lot:float=0.01
    usd_per_price_unit_at_0p01:float=1.0
    commission_per_entry_deal_usd:float=0.01
    commission_per_exit_deal_usd:float=0.01
    point_price:float=0.01
    tick_size_price:float=0.01
    gap_half_price:float=0.15
    stop_distance_price:float=0.30
    trail_activation_price:float=0.10
    trail_distance_price:float=0.03
    max_hold_seconds:int=30
    max_same_minute_rearms:int=3
    min_directional_displacement_price:float=0.15
    min_directional_efficiency:float=0.70
    min_s1_range_price:float=0.50
    max_s1_turns:int=9
    max_spread_points:int=25
    initial_balance_usd:float=100000.0

def q_tick_price(x:float,tick:float=0.01)->float:
    return floor(x/tick+0.5+1e-12)*tick

def quality_pass(side:int,disp:float,eff:float,rng:float,turns:int,cfg:CoinexxR9Config=CoinexxR9Config())->bool:
    if not (eff>cfg.min_directional_efficiency and rng>=cfg.min_s1_range_price and turns<=cfg.max_s1_turns):
        return False
    return disp>=cfg.min_directional_displacement_price if side>0 else disp<=-cfg.min_directional_displacement_price

def _book_exit(raw:float,a:dict,cfg:CoinexxR9Config)->None:
    exit_deal=raw-cfg.commission_per_exit_deal_usd
    if raw>0:
        a["wins"]+=1; a["gross_profit"]+=exit_deal
    else:
        a["losses"]+=1; a["gross_loss"]+=exit_deal
    a["net_profit"]+=exit_deal

def replay_logger_oracle(df:pd.DataFrame,cfg:CoinexxR9Config=CoinexxR9Config())->dict:
    pos=0; entry=0.; sl=0.; entry_sec=0
    had=False; lastside=0; pending=0; rearm=0; minute=None
    bal=cfg.initial_balance_usd; bpeak=bal; epeak=bal; maxbdd=0.; maxedd=0.
    acc={"trades":0,"wins":0,"losses":0,"gross_profit":0.,"gross_loss":0.,"net_profit":0.,"hold_seconds_sum":0.}
    events=[]; counts=Counter(); trades=[]
    cols=["time_msc","bid","ask","cycle_buy","cycle_sell","gate_open","s1_disp","s1_eff","s1_range","s1_turns","minute_start"]
    for row in df[cols].itertuples(index=False,name=None):
        tms,bid,ask,cb,cs,gate,disp,eff,rng,turns,minute_start=row; sec=int(tms)//1000
        if pos==1 and bid<=sl+1e-12:
            raw=(float(bid)-entry)*cfg.usd_per_price_unit_at_0p01
            _book_exit(raw,acc,cfg); bal+=raw-cfg.commission_per_exit_deal_usd
            acc["trades"]+=1; acc["hold_seconds_sum"]+=sec-entry_sec
            trades.append((1,entry,float(bid),raw,sec-entry_sec,"STOP")); pos=0; entry=sl=0.
        elif pos==-1 and ask>=sl-1e-12:
            raw=(entry-float(ask))*cfg.usd_per_price_unit_at_0p01
            _book_exit(raw,acc,cfg); bal+=raw-cfg.commission_per_exit_deal_usd
            acc["trades"]+=1; acc["hold_seconds_sum"]+=sec-entry_sec
            trades.append((-1,entry,float(ask),raw,sec-entry_sec,"STOP")); pos=0; entry=sl=0.

        ev="NONE"
        if minute_start!=minute:
            minute=minute_start; pending=2; rearm=0; ev="MINUTE_START"

        if pos:
            had=True; lastside=pos
            if sec-entry_sec>=cfg.max_hold_seconds:
                px=float(bid if pos==1 else ask)
                raw=((px-entry) if pos==1 else (entry-px))*cfg.usd_per_price_unit_at_0p01
                _book_exit(raw,acc,cfg); bal+=raw-cfg.commission_per_exit_deal_usd
                acc["trades"]+=1; acc["hold_seconds_sum"]+=sec-entry_sec
                trades.append((pos,entry,px,raw,sec-entry_sec,"MAX_HOLD")); pos=0; entry=sl=0.; ev="EXIT_MAX_HOLD"
            else:
                fav=(float(bid)-entry) if pos==1 else (entry-float(ask))
                if fav>=cfg.trail_activation_price:
                    nsl=q_tick_price(float(bid)-cfg.trail_distance_price if pos==1 else float(ask)+cfg.trail_distance_price,cfg.tick_size_price)
                    improve=nsl>sl+1e-12 if pos==1 else nsl<sl-1e-12
                    if improve: sl=nsl; ev="TRAIL_MOVE"
        elif had:
            if rearm<cfg.max_same_minute_rearms:
                rearm+=1; pending=-lastside; ev="REARM"
            else: pending=0
            had=False; lastside=0
        elif bool(gate):
            if pending in (1,2) and float(ask)>=float(cb)-1e-12:
                if quality_pass(1,float(disp),float(eff),float(rng),int(turns),cfg):
                    pos=1; entry=float(ask); entry_sec=sec
                    sl=q_tick_price(float(bid)-cfg.stop_distance_price,cfg.tick_size_price); pending=0
                    bal-=cfg.commission_per_entry_deal_usd; acc["gross_loss"]-=cfg.commission_per_entry_deal_usd; acc["net_profit"]-=cfg.commission_per_entry_deal_usd
                    ev="ENTRY_BUY"
                else: ev="QUALITY_REJECT_BUY"
            elif pending in (-1,2) and float(bid)<=float(cs)+1e-12:
                if quality_pass(-1,float(disp),float(eff),float(rng),int(turns),cfg):
                    pos=-1; entry=float(bid); entry_sec=sec
                    sl=q_tick_price(float(ask)+cfg.stop_distance_price,cfg.tick_size_price); pending=0
                    bal-=cfg.commission_per_entry_deal_usd; acc["gross_loss"]-=cfg.commission_per_entry_deal_usd; acc["net_profit"]-=cfg.commission_per_entry_deal_usd
                    ev="ENTRY_SELL"
                else: ev="QUALITY_REJECT_SELL"

        bpeak=max(bpeak,bal); maxbdd=max(maxbdd,bpeak-bal)
        eq=bal+(float(bid)-entry)*cfg.usd_per_price_unit_at_0p01 if pos==1 else bal+(entry-float(ask))*cfg.usd_per_price_unit_at_0p01 if pos==-1 else bal
        epeak=max(epeak,eq); maxedd=max(maxedd,epeak-eq)
        events.append(ev); counts[ev]+=1

    acc["ending_balance"]=bal; acc["max_balance_drawdown"]=maxbdd; acc["max_equity_drawdown"]=maxedd
    acc["average_hold_seconds"]=acc["hold_seconds_sum"]/acc["trades"] if acc["trades"] else 0.
    for k in ("gross_profit","gross_loss","net_profit"): acc[k]=round(acc[k],10)
    return {"events":events,"event_counts":counts,"trades":trades,"accounting":acc}

def compare_logger_oracle(df:pd.DataFrame,cfg:CoinexxR9Config=CoinexxR9Config())->dict:
    sim=replay_logger_oracle(df,cfg); actual=df["event"].astype(str).tolist()
    mism=[i for i,(a,b) in enumerate(zip(sim["events"],actual)) if a!=b]
    return {"rows":len(df),"event_mismatches":len(mism),"event_match_rate":1-len(mism)/len(df) if len(df) else 1.0,
            "first_mismatch_indices":mism[:20],"event_counts_equal":sim["event_counts"]==Counter(actual),
            "event_counts":dict(sim["event_counts"]),"accounting":sim["accounting"]}

@njit(cache=True)
def _session_2026(t):
    tod=t%DAY_MS
    ls=7*3_600_000 if t>=UK_DST_START_2026_MS else 8*3_600_000; le=ls+8*3_600_000+30*60_000
    ns=12*3_600_000 if t>=US_DST_START_2026_MS else 13*3_600_000; ne=ns+9*3_600_000
    il=ls<=tod<le; inn=ns<=tod<ne
    if il and inn:return 2
    if il:return 1
    if inn:return 3
    return 0

@njit(cache=True)
def _q_tick_raw(raw,tick): return ((raw+tick//2)//tick)*tick

@njit(cache=True)
def _q_half_raw2_to_tick(target2,tick): return ((target2+tick)//(2*tick))*tick

@njit(cache=True)
def run_raw_r9(t,ask,bid,price_scale=1000,trade_start_ms=0):
    tick=max(1,int(round(.01*price_scale))); half=int(round(.15*price_scale)); stopd=int(round(.30*price_scale))
    tracta=int(round(.10*price_scale)); traild=int(round(.03*price_scale)); minrng=int(round(.50*price_scale)); mindisp=int(round(.15*price_scale))
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entrysec=0;had=False;lastside=0
    trades=wins=losses=ebuys=esells=maxholds=trails=rearms=0
    gp=0.;gl=0.;bal=100000.;bpeak=bal;epeak=bal;maxbdd=0.;maxedd=0.;holdsum=0.
    for i in range(t.size):
        tm=np.int64(t[i]);a=np.int64(ask[i]);b=np.int64(bid[i]);sec=tm//1000
        if pos==1 and b<=stop:
            raw=(b-entry)/price_scale; ex=raw-.01
            if raw>0:gp+=ex;wins+=1
            else:gl+=ex;losses+=1
            bal+=ex;trades+=1;holdsum+=sec-entrysec;pos=0;entry=stop=0
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale;ex=raw-.01
            if raw>0:gp+=ex;wins+=1
            else:gl+=ex;losses+=1
            bal+=ex;trades+=1;holdsum+=sec-entrysec;pos=0;entry=stop=0

        if cursec<0:cursec=sec;sh=sl=sclose=b
        elif sec!=cursec:
            h[sptr]=sh;l[sptr]=sl;c[sptr]=sclose;sptr=(sptr+1)%10;scount=min(10,scount+1);cursec=sec;sh=sl=sclose=b
        else:
            if b>sh:sh=b
            if b<sl:sl=b
            sclose=b
        disp=travel=rng=turns=0
        if scount==10:
            first=sptr;disp=c[(sptr+9)%10]-c[first];maxh=h[first];minl=l[first];prev=c[first];prevsign=0
            for k in range(1,10):
                idx=(first+k)%10
                if h[idx]>maxh:maxh=h[idx]
                if l[idx]<minl:minl=l[idx]
                d=c[idx]-prev;travel+=abs(d);sgn=1 if d>0 else -1 if d<0 else 0
                if sgn!=0:
                    if prevsign!=0 and sgn!=prevsign:turns+=1
                    prevsign=sgn
                prev=c[idx]
            rng=maxh-minl
        eff=abs(disp)/travel if travel>0 else 0.

        m5=tm//300000
        if curm5<0:curm5=m5;mh=ml=mclose=b
        elif m5!=curm5:
            tr=mh-ml
            if haveprev:
                x=abs(mh-prevclose);y=abs(ml-prevclose);tr=max(tr,x,y)
            trs[tptr]=tr;tptr=(tptr+1)%14;tcount=min(14,tcount+1);prevclose=mclose;haveprev=True;curm5=m5;mh=ml=mclose=b
        else:
            if b>mh:mh=b
            if b<ml:ml=b
            mclose=b
        atrsum=0
        if tcount==14:
            for k in range(14):atrsum+=trs[k]
        sess=_session_2026(tm);floorraw=int(round((2.5 if sess==0 else 2.0 if sess==1 else 1.75)*price_scale))
        gate=tcount==14 and (a-b)<=25*tick and atrsum>=14*floorraw

        mi=tm//60000
        if mi!=minute:
            minute=mi;pending=2;rearm=0;cb=_q_half_raw2_to_tick(b+a+2*half,tick);cs=_q_half_raw2_to_tick(b+a-2*half,tick)
        if pos!=0:
            had=True;lastside=pos
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale;ex=raw-.01
                if raw>0:gp+=ex;wins+=1
                else:gl+=ex;losses+=1
                bal+=ex;trades+=1;holdsum+=sec-entrysec;maxholds+=1;pos=0;entry=stop=0
            else:
                fav=(b-entry) if pos==1 else (entry-a)
                if fav>=tracta:
                    ns=_q_tick_raw(b-traild if pos==1 else a+traild,tick);improve=ns>stop if pos==1 else ns<stop
                    if improve:stop=ns;trails+=1
        elif had:
            if rearm<3:rearm+=1;pending=-lastside;rearms+=1
            else:pending=0
            had=False;lastside=0
        elif tm>=trade_start_ms and gate:
            common=eff>.70 and rng>=minrng and turns<=9
            if pending in (1,2) and a>=cb:
                if common and disp>=mindisp:
                    pos=1;entry=a;entrysec=sec;stop=_q_tick_raw(b-stopd,tick);pending=0;ebuys+=1;bal-=.01;gl-=.01
            elif pending in (-1,2) and b<=cs:
                if common and disp<=-mindisp:
                    pos=-1;entry=b;entrysec=sec;stop=_q_tick_raw(a+stopd,tick);pending=0;esells+=1;bal-=.01;gl-=.01

        bpeak=max(bpeak,bal);maxbdd=max(maxbdd,bpeak-bal)
        eq=bal+(b-entry)/price_scale if pos==1 else bal+(entry-a)/price_scale if pos==-1 else bal
        epeak=max(epeak,eq);maxedd=max(maxedd,epeak-eq)
    ints=np.array([trades,wins,losses,ebuys,esells,maxholds,trails,rearms],np.int64)
    fl=np.array([gp,gl,gp+gl,maxbdd,maxedd,holdsum/trades if trades else 0.],np.float64)
    return ints,fl

def raw_result_dict(ints,floats):
    return {"trades":int(ints[0]),"wins":int(ints[1]),"losses":int(ints[2]),"entry_buy":int(ints[3]),"entry_sell":int(ints[4]),
            "max_hold_exits":int(ints[5]),"trail_moves":int(ints[6]),"rearms":int(ints[7]),
            "gross_profit":float(floats[0]),"gross_loss":float(floats[1]),"net_profit":float(floats[2]),
            "max_balance_drawdown":float(floats[3]),"max_equity_drawdown":float(floats[4]),"average_hold_seconds":float(floats[5])}
