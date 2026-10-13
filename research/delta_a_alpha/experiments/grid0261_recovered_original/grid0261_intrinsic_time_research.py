"""Research only: directional-change intrinsic-time event rearm, true executable Bid/Ask.
R9 SYNTH target; OVERFIT oracle never a runtime input. Original Dukascopy Jan-Jul.
Independent public geometry Petrov/Golub/Olsen Quantitative Finance 2020 (no PnL claimed).
"""
import numpy as np, pandas as pd, json, time, sys, gzip
from pathlib import Path
from numba import njit
from collections import defaultdict
from datetime import datetime, timezone
ROOT=Path('/mnt/data'); DEST=ROOT/'grid0261_intrinsic'; DEST.mkdir(exist_ok=True)
@njit(cache=True)
def intrinsic(t,ask,bid,threshold=1800,overshoot=400,source=0,profile=0,spread_max=850,fee=520):
    # source 0=event-side, 1=as-of last finished minute agreement, 2=reversal with last minute agreement opposite
    # profile0 45s TP4 stop3; 1=90s TP7 stop4.5; 2=20s TP2.5 stop2.5
    n=len(t)
    maxtrades=250000
    ets=np.empty(maxtrades,np.int64);xts=np.empty(maxtrades,np.int64)
    ps=np.empty(maxtrades,np.int64); sides=np.empty(maxtrades,np.int8)
    ent_sp=np.empty(maxtrades,np.int32)
    count=0;active=False;pending=False
    known_at=0; pend_side=0;pend_event_id=-1
    entry=0;enttime=0;side=0;stop=0;take=0;deadline=0;spread_in=0
    # DC detection: current direction has extreme (and register reversals)
    curdir=0;ext=0; initialized=False; event_id=0;last_consumed_id=-1
    lasttm=-1;lastquote=0; last_min=-1;minute_open=0;minute_last=0;past_min_dir=0
    total_events=0;blocked_spread=0;false_rearm=0;timedout=0;entered=0
    maxgap=120000
    for i in range(n):
        tm=t[i];a=ask[i];b=bid[i];mid=(a+b)//2;sp=a-b
        if a<b or b<=0 or (lasttm!=-1 and tm<lasttm):raise ValueError('corrupt source')
        if lasttm!=-1 and tm-lasttm>maxgap:
            pending=False; initialized=False;curdir=0;last_min=-1
            if active:
                exit_price=b if side==1 else a
                pnl=(exit_price-entry)*side-fee
                if count<maxtrades:
                    ets[count]=enttime;xts[count]=tm;ps[count]=pnl;sides[count]=side;ent_sp[count]=spread_in;count+=1
                active=False
        minute=tm//60000
        if minute!=last_min:
            if last_min!=-1:
                past_min_dir=1 if minute_last>minute_open else (-1 if minute_last<minute_open else 0)
            else:past_min_dir=0
            last_min=minute;minute_open=mid
        minute_last=mid
        # existing position exits before any new order at same quote
        if active:
            oq=b if side==1 else a
            if (side==1 and oq<=stop) or (side==-1 and oq>=stop) or (side==1 and oq>=take) or (side==-1 and oq<=take) or tm>=deadline:
                pnl=(oq-entry)*side-fee
                if count<maxtrades:
                    ets[count]=enttime;xts[count]=tm;ps[count]=pnl;sides[count]=side;ent_sp[count]=spread_in;count+=1
                active=False
        # DC event on CURRENT observation
        if not initialized:
            ext=mid;curdir=0;initialized=True
        else:
            if curdir==0:
                if mid>=ext+threshold:curdir=1;ext=mid;event_id+=1;total_events+=1
                elif mid<=ext-threshold:curdir=-1;ext=mid;event_id+=1;total_events+=1
                else:
                    # initial movement peaks must update only where range starts
                    pass
            elif curdir==1:
                if mid>ext:ext=mid
                elif mid<=ext-threshold:
                    curdir=-1;ext=mid;event_id+=1;total_events+=1
            else:
                if mid<ext:ext=mid
                elif mid>=ext+threshold:
                    curdir=1;ext=mid;event_id+=1;total_events+=1
        # Pending from a distinct actual DC event; continuation overshoot MUST occur after event.
        if pending and not active:
            if tm-known_at>=250:
                if tm-known_at>2000:
                    pending=False;timedout+=1
                elif sp>spread_max:
                    pending=False;blocked_spread+=1
                elif (mid-lastquote)*pend_side>=overshoot and (source!=1 or past_min_dir==pend_side) and (source!=2 or past_min_dir==-pend_side):
                    side=pend_side;enttime=tm;entry=a if side==1 else b;spread_in=sp
                    # spread-aware stops, but pre-fixed price risk/TP; no arbitrary R9 exact stop transplant
                    stop_dist=3000 if profile==0 else (4500 if profile==1 else 2500)
                    tp=4000 if profile==0 else (7000 if profile==1 else 2500)
                    horizon=45000 if profile==0 else (90000 if profile==1 else 20000)
                    stop=entry-side*max(stop_dist,sp*2)
                    take=entry+side*tp
                    deadline=tm+horizon
                    pending=False;active=True;entered+=1;last_consumed_id=pend_event_id
                # stay pending until ttl except on bad spread
        # create a *new* observed DC event, no event reuse
        if event_id!=last_consumed_id and event_id!=pend_event_id and curdir!=0 and not active and not pending and total_events>0:
            pending=True;known_at=tm;pend_side=curdir;pend_event_id=event_id;lastquote=mid
        lasttm=tm
    return ets[:count],xts[:count],ps[:count],sides[:count],ent_sp[:count],np.array([total_events,entered,blocked_spread,timedout],np.int64)

def load_month(m):
    name=ROOT/(f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv(2).gz' if m==7 else f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv(3).gz')
    d=pd.read_csv(name,usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    return tuple(d[col].to_numpy() for col in ['timestamp_ms_utc','ask_raw','bid_raw'])

def summarize(ets,xts,ps):
    d={};w={}
    for tm,v in zip(xts,ps):
        dt=datetime.fromtimestamp(tm/1000,tz=timezone.utc)
        m=dt.strftime('%Y-%m');iso=dt.isocalendar();k=f'{iso.year}-W{iso.week:02d}'
        for dic,key in [(d,m),(w,k)]:
            if key not in dic:dic[key]=[0,0]
            dic[key][0]+=1;dic[key][1]+=int(v)
    return {'trades':len(ps),'net_usd_per_oz':round(float(np.sum(ps)/1000),2),'gross_loss_usd_per_oz':round(float(ps[ps<0].sum()/1000),2),'positive_months':sum(k[1]>0 for k in d.values()),'months':len(d),'positive_weeks':sum(k[1]>0 for k in w.values()),'weeks':len(w),'monthly':{k:[v[0],round(v[1]/1000,2)] for k,v in d.items()}}

if __name__=='__main__':
    begin=time.monotonic();designs=[(1800,300,0,0),(1800,300,1,0),(1800,300,2,0),(2800,500,0,1),(2800,500,1,1),(2800,500,2,1),(1400,250,0,2),(1400,250,1,2)]
    tests={j:{'et':[],'xt':[],'p':[],'evt':0,'enter':0} for j in range(len(designs))}
    for mon in [1,2]:
        tm,a,b=load_month(mon)
        print('month',mon,'quotes',len(tm),flush=True)
        for idx,(threshold,overshoot,source,profile) in enumerate(designs):
            et,xt,p,sd,sp,counts=intrinsic(tm,a,b,threshold,overshoot,source,profile)
            tests[idx]['et'].append(et);tests[idx]['xt'].append(xt);tests[idx]['p'].append(p);tests[idx]['evt']+=int(counts[0]);tests[idx]['enter']+=int(counts[1]);
        del tm,a,b
    res={}
    for idx,params in enumerate(designs):
        z=tests[idx];res[str(idx)]={'params':params,'events':z['evt'],'offers':z['enter'],**summarize(*[np.concatenate(z[x]) for x in ['et','xt','p']])}
    (DEST/'grid0261_janfeb_8_prespecified_intrinsic_screens.json').write_text(json.dumps(res,indent=2))
    print(json.dumps(res,indent=2),flush=True)
    print('time',round(time.monotonic()-begin,2),flush=True)
