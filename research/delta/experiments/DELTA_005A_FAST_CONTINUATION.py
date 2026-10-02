from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

START_MS=np.int64(1767225600000)
END_MS=np.int64(1768737600000)
DAY_MS=np.int64(86400000)
PROFILE_POINTS=np.array([20,20,21,21],dtype=np.int64)
HORIZONS=np.array([1000,3000,5000,10000,15000],dtype=np.int64)
FAST_WINDOWS=(250,500,1000)
SLOW_WINDOWS=(1000,3000)
FAST_THRESHOLDS=(0.0,0.1,0.2,0.3,0.4)
SLOW_THRESHOLDS=(0.0,0.1,0.2)

@njit(cache=True)
def session_code_jan_2026(t):
    tod=t%DAY_MS
    il=(8*3600000)<=tod<(16*3600000+30*60000)
    inn=(13*3600000)<=tod<(22*3600000)
    if il and inn:return 2
    if il:return 1
    if inn:return 3
    return 0

@njit(cache=True)
def q_half_raw2_to_tick(target2,tick):
    return ((target2+tick)//(2*tick))*tick

@njit(cache=True)
def q_tick_raw(raw,tick):
    return ((raw+tick//2)//tick)*tick

@njit(cache=True)
def materialize_p75(t,src_ask,src_bid,price_scale=1000):
    tick=max(1,int(round(.01*price_scale)))
    a=np.empty(t.size,np.int32);b=np.empty(t.size,np.int32)
    for i in range(t.size):
        s=session_code_jan_2026(t[i]);spread=PROFILE_POINTS[s]*tick
        mid2=np.int64(src_ask[i])+np.int64(src_bid[i])
        bb=q_half_raw2_to_tick(mid2-spread,tick);aa=bb+spread
        b[i]=bb;a[i]=aa
    return a,b

@njit(cache=True)
def tick_flow(t,bid,window_ms):
    n=t.size
    out=np.zeros(n,np.float32)
    up=np.zeros(n+1,np.int64);dn=np.zeros(n+1,np.int64)
    for i in range(1,n):
        d=bid[i]-bid[i-1]
        up[i+1]=up[i]+(1 if d>0 else 0)
        dn[i+1]=dn[i]+(1 if d<0 else 0)
    left=0
    for i in range(n):
        cutoff=t[i]-window_ms
        while left<i and t[left]<cutoff:left+=1
        u=up[i+1]-up[left];d=dn[i+1]-dn[left];z=u+d
        if z>0:out[i]=(u-d)/z
    return out

@njit(cache=True)
def simulate(t,ask,bid,fast_flow,slow_flow,fast_thr,slow_thr,use_flow):
    price_scale=1000;tick=10;half=150;stopd=300;tracta=100;traild=30;minrng=500;mindisp=150
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entryms=0;entrysec=0;had=False;lastside=0
    trades=wins=losses=ebuys=esells=maxholds=trails=rearms=0
    opportunities=selected=0;opp_side=0
    gp=0.;gl=0.;bal=100000.;bpeak=bal;maxbdd=0.;holdsum=0.
    surv=np.zeros(5,np.int64);mfe_sum=np.zeros(5,np.float64);mae_sum=np.zeros(5,np.float64)
    cmfe=np.zeros(5,np.float64);cmae=np.zeros(5,np.float64)

    for i in range(t.size):
        tm=t[i];a=np.int64(ask[i]);b=np.int64(bid[i]);sec=tm//1000

        if pos!=0:
            elapsed=tm-entryms
            fav=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
            adv=(entry-b)/price_scale if pos==1 else (a-entry)/price_scale
            if adv<0:adv=0.
            for q in range(5):
                if elapsed<=HORIZONS[q]:
                    if fav>cmfe[q]:cmfe[q]=fav
                    if adv>cmae[q]:cmae[q]=adv

        closed=False
        raw=0.
        if pos==1 and b<=stop:
            raw=(b-entry)/price_scale;closed=True
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale;closed=True
        if closed:
            ex=raw-.01
            if raw>0:gp+=ex;wins+=1
            else:gl+=ex;losses+=1
            bal+=ex;trades+=1
            holdms=tm-entryms;holdsum+=holdms/1000.
            for q in range(5):
                if holdms>HORIZONS[q]:surv[q]+=1
                mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q]
                cmfe[q]=0.;cmae[q]=0.
            pos=0;entry=stop=0;opp_side=0

        if cursec<0:
            cursec=sec;sh=sl=sclose=b
        elif sec!=cursec:
            h[sptr]=sh;l[sptr]=sl;c[sptr]=sclose;sptr=(sptr+1)%10;scount=min(10,scount+1)
            cursec=sec;sh=sl=sclose=b
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
        if curm5<0:
            curm5=m5;mh=ml=mclose=b
        elif m5!=curm5:
            tr=mh-ml
            if haveprev:
                tr=max(tr,abs(mh-prevclose),abs(ml-prevclose))
            trs[tptr]=tr;tptr=(tptr+1)%14;tcount=min(14,tcount+1)
            prevclose=mclose;haveprev=True;curm5=m5;mh=ml=mclose=b
        else:
            if b>mh:mh=b
            if b<ml:ml=b
            mclose=b
        atrsum=0
        if tcount==14:
            for k in range(14):atrsum+=trs[k]
        sess=session_code_jan_2026(tm)
        floorraw=2500 if sess==0 else 2000 if sess==1 else 1750
        gate=tcount==14 and (a-b)<=250 and atrsum>=14*floorraw

        mi=tm//60000
        if mi!=minute:
            minute=mi;pending=2;rearm=0
            cb=q_half_raw2_to_tick(b+a+2*half,tick);cs=q_half_raw2_to_tick(b+a-2*half,tick);opp_side=0

        if pos!=0:
            had=True;lastside=pos
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale
                ex=raw-.01
                if raw>0:gp+=ex;wins+=1
                else:gl+=ex;losses+=1
                bal+=ex;trades+=1
                holdms=tm-entryms;holdsum+=holdms/1000.;maxholds+=1
                for q in range(5):
                    if holdms>HORIZONS[q]:surv[q]+=1
                    mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                pos=0;entry=stop=0;opp_side=0
            else:
                fav=(b-entry) if pos==1 else (entry-a)
                if fav>=tracta:
                    ns=q_tick_raw(b-traild if pos==1 else a+traild,tick)
                    improve=ns>stop if pos==1 else ns<stop
                    if improve:stop=ns;trails+=1
        elif had:
            if rearm<3:
                rearm+=1;pending=-lastside;rearms+=1
            else:pending=0
            had=False;lastside=0;opp_side=0
        elif gate:
            common=eff>.70 and rng>=minrng and turns<=9
            base_side=0
            if pending in (1,2) and a>=cb and common and disp>=mindisp:base_side=1
            elif pending in (-1,2) and b<=cs and common and disp<=-mindisp:base_side=-1

            if base_side==0:
                opp_side=0
            else:
                if opp_side!=base_side:
                    opportunities+=1;opp_side=base_side
                ok=True
                if use_flow:
                    if base_side==1:ok=fast_flow[i]>=fast_thr and slow_flow[i]>=slow_thr
                    else:ok=fast_flow[i]<=-fast_thr and slow_flow[i]<=-slow_thr
                if ok:
                    selected+=1
                    if base_side==1:
                        pos=1;entry=a;stop=q_tick_raw(b-stopd,tick);ebuys+=1
                    else:
                        pos=-1;entry=b;stop=q_tick_raw(a+stopd,tick);esells+=1
                    entryms=tm;entrysec=sec;pending=0;opp_side=0
                    bal-=.01;gl-=.01
                    for q in range(5):cmfe[q]=0.;cmae[q]=0.

        if bal>bpeak:bpeak=bal
        dd=bpeak-bal
        if dd>maxbdd:maxbdd=dd

    if pos!=0:
        tm=t[-1];a=np.int64(ask[-1]);b=np.int64(bid[-1])
        fav=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
        adv=(entry-b)/price_scale if pos==1 else (a-entry)/price_scale
        if adv<0:adv=0.
        elapsed=tm-entryms
        for q in range(5):
            if elapsed<=HORIZONS[q]:
                if fav>cmfe[q]:cmfe[q]=fav
                if adv>cmae[q]:cmae[q]=adv
        raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
        ex=raw-.01
        if raw>0:gp+=ex;wins+=1
        else:gl+=ex;losses+=1
        bal+=ex;trades+=1
        holdms=tm-entryms;holdsum+=holdms/1000.
        for q in range(5):
            if holdms>HORIZONS[q]:surv[q]+=1
            mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q]

    metrics=np.array([opportunities,selected,trades,wins,losses,ebuys,esells,maxholds,trails,rearms],np.int64)
    vals=np.array([gp,gl,gp+gl,maxbdd,holdsum/trades if trades else 0.],np.float64)
    return metrics,vals,surv,mfe_sum,mae_sum

def load_stage_a(path:Path):
    chunks=[]
    cols=["timestamp_ms_utc","ask_raw","bid_raw"]
    dtypes={"timestamp_ms_utc":"int64","ask_raw":"int32","bid_raw":"int32"}
    for d in pd.read_csv(path,compression="gzip",usecols=cols,dtype=dtypes,chunksize=1_000_000):
        d=d[(d.timestamp_ms_utc>=START_MS)&(d.timestamp_ms_utc<END_MS)]
        if len(d):chunks.append(d)
        if len(d) and int(d.timestamp_ms_utc.iloc[-1])>=int(END_MS)-1:break
    x=pd.concat(chunks,ignore_index=True)
    return x.timestamp_ms_utc.to_numpy(np.int64),x.ask_raw.to_numpy(np.int32),x.bid_raw.to_numpy(np.int32)

def pack(m,v,s,mfe,mae):
    trades=int(m[2])
    return {
      "opportunities":int(m[0]),"selected_entries":int(m[1]),"trades":trades,"wins":int(m[3]),"losses":int(m[4]),
      "entry_buy":int(m[5]),"entry_sell":int(m[6]),"max_hold_exits":int(m[7]),"trail_moves":int(m[8]),"rearms":int(m[9]),
      "gross_profit":round(float(v[0]),2),"gross_loss":round(float(v[1]),2),"net_profit":round(float(v[2]),2),
      "max_balance_drawdown":round(float(v[3]),2),"average_hold_seconds":float(v[4]),
      "survival_pct":{str(int(h/1000)):100*int(s[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)},
      "mean_mfe_usd":{str(int(h/1000)):float(mfe[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)},
      "mean_mae_usd":{str(int(h/1000)):float(mae[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)}
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();t0=time.perf_counter()
    t,sa,sb=load_stage_a(a.source);ask,bid=materialize_p75(t,sa,sb)
    windows=sorted(set(FAST_WINDOWS+SLOW_WINDOWS));flows={}
    for w in windows:flows[w]=tick_flow(t,bid,w)
    z=np.zeros(t.size,np.float32)
    bm,bv,bs,bmfe,bmae=simulate(t,ask,bid,z,z,0.,0.,False);baseline=pack(bm,bv,bs,bmfe,bmae)
    variants=[]
    for fw in FAST_WINDOWS:
      for sw in SLOW_WINDOWS:
       for ft in FAST_THRESHOLDS:
        for st in SLOW_THRESHOLDS:
         m,v,s,mfe,mae=simulate(t,ask,bid,flows[fw],flows[sw],ft,st,True);r=pack(m,v,s,mfe,mae)
         r.update({"fast_window_ms":fw,"slow_window_ms":sw,"fast_threshold":ft,"slow_threshold":st})
         r["trade_retention_pct"]=100*r["trades"]/baseline["trades"] if baseline["trades"] else 0.
         r["win_change_pct"]=100*(r["wins"]-baseline["wins"])/baseline["wins"] if baseline["wins"] else 0.
         r["gross_loss_improvement_pct"]=100*(abs(baseline["gross_loss"])-abs(r["gross_loss"]))/abs(baseline["gross_loss"]) if baseline["gross_loss"] else 0.
         r["drawdown_improvement_pct"]=100*(baseline["max_balance_drawdown"]-r["max_balance_drawdown"])/baseline["max_balance_drawdown"] if baseline["max_balance_drawdown"] else 0.
         r["net_change_usd"]=r["net_profit"]-baseline["net_profit"]
         variants.append(r)
    out={"schema":"delta-005a-001-results-v1","status":"LOCAL_COMPLETE","historical_simulation_only":True,
         "window":{"start_ms":int(START_MS),"end_ms_exclusive":int(END_MS)},"surface":"DUKAS_COINEXX_LIKE_P75",
         "ticks":int(t.size),"baseline":baseline,"variants":variants,"runtime_seconds":time.perf_counter()-t0,
         "august_accessed":False}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"ticks":len(t),"baseline":baseline,"variants":len(variants),"runtime_seconds":out["runtime_seconds"]},indent=2))
if __name__=="__main__":main()
