from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from DELTA_005A_FAST_CONTINUATION import (
    START_MS,END_MS,HORIZONS,load_stage_a,materialize_p75,tick_flow,
    session_code_jan_2026,q_half_raw2_to_tick,q_tick_raw
)

@__import__("numba").njit(cache=True)
def simulate_initial_hold(t,ask,bid,fast_flow,slow_flow,guard_ms,failure_depth_raw,maint_eff_floor):
    price_scale=1000;tick=10;half=150;stopd=300;tracta=100;traild=30;minrng=500;mindisp=150
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entryms=0;entrysec=0;entry_boundary=0;had=False;lastside=0
    trades=wins=losses=ebuys=esells=maxholds=trails=rearms=0
    early_count=early_wins=early_losses=0;early_pnl_sum=0.;saved_proxy_sum=0.
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

        closed=False;raw=0.
        if pos==1 and b<=stop:
            raw=(b-entry)/price_scale;closed=True
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale;closed=True
        if closed:
            ex=raw-.01
            if raw>0:gp+=ex;wins+=1
            else:gl+=ex;losses+=1
            bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.
            for q in range(5):
                if holdms>HORIZONS[q]:surv[q]+=1
                mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
            pos=0;entry=stop=0;entry_boundary=0

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
            if haveprev:tr=max(tr,abs(mh-prevclose),abs(ml-prevclose))
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
            cb=q_half_raw2_to_tick(b+a+2*half,tick);cs=q_half_raw2_to_tick(b+a-2*half,tick)

        if pos!=0:
            had=True;lastside=pos
            elapsed=tm-entryms
            invalidate=False
            if elapsed<=guard_ms:
                if pos==1:
                    lost=b<=entry_boundary-failure_depth_raw
                    flow_flip=fast_flow[i]<0. and slow_flow[i]<0.
                else:
                    lost=a>=entry_boundary+failure_depth_raw
                    flow_flip=fast_flow[i]>0. and slow_flow[i]>0.
                invalidate=lost and flow_flip and eff<maint_eff_floor

            if invalidate:
                raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
                ex=raw-.01
                if raw>0:gp+=ex;wins+=1;early_wins+=1
                else:
                    gl+=ex;losses+=1;early_losses+=1
                    saved=0.30+raw
                    if saved>0:saved_proxy_sum+=saved
                bal+=ex;trades+=1;early_count+=1;early_pnl_sum+=ex
                holdms=tm-entryms;holdsum+=holdms/1000.
                for q in range(5):
                    if holdms>HORIZONS[q]:surv[q]+=1
                    mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                pos=0;entry=stop=0;entry_boundary=0
            elif sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale;ex=raw-.01
                if raw>0:gp+=ex;wins+=1
                else:gl+=ex;losses+=1
                bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.;maxholds+=1
                for q in range(5):
                    if holdms>HORIZONS[q]:surv[q]+=1
                    mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                pos=0;entry=stop=0;entry_boundary=0
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
            had=False;lastside=0

        elif gate:
            common=eff>.70 and rng>=minrng and turns<=9
            if pending in (1,2) and a>=cb and common and disp>=mindisp:
                pos=1;entry=a;entryms=tm;entrysec=sec;entry_boundary=cb;stop=q_tick_raw(b-stopd,tick);pending=0;ebuys+=1
                bal-=.01;gl-=.01
                for q in range(5):cmfe[q]=0.;cmae[q]=0.
            elif pending in (-1,2) and b<=cs and common and disp<=-mindisp:
                pos=-1;entry=b;entryms=tm;entrysec=sec;entry_boundary=cs;stop=q_tick_raw(a+stopd,tick);pending=0;esells+=1
                bal-=.01;gl-=.01
                for q in range(5):cmfe[q]=0.;cmae[q]=0.

        if bal>bpeak:bpeak=bal
        dd=bpeak-bal
        if dd>maxbdd:maxbdd=dd

    if pos!=0:
        tm=t[-1];a=np.int64(ask[-1]);b=np.int64(bid[-1])
        raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale;ex=raw-.01
        if raw>0:gp+=ex;wins+=1
        else:gl+=ex;losses+=1
        bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.
        for q in range(5):
            if holdms>HORIZONS[q]:surv[q]+=1
            mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q]

    ints=np.array([trades,wins,losses,ebuys,esells,maxholds,trails,rearms,early_count,early_wins,early_losses],np.int64)
    vals=np.array([gp,gl,gp+gl,maxbdd,holdsum/trades if trades else 0.,early_pnl_sum,saved_proxy_sum],np.float64)
    return ints,vals,surv,mfe_sum,mae_sum

def pack(ints,vals,surv,mfe,mae):
    trades=int(ints[0])
    return {
      "trades":trades,"wins":int(ints[1]),"losses":int(ints[2]),"entry_buy":int(ints[3]),"entry_sell":int(ints[4]),
      "max_hold_exits":int(ints[5]),"trail_moves":int(ints[6]),"rearms":int(ints[7]),
      "early_invalidations":int(ints[8]),"early_invalidation_wins":int(ints[9]),"early_invalidation_losses":int(ints[10]),
      "gross_profit":round(float(vals[0]),2),"gross_loss":round(float(vals[1]),2),"net_profit":round(float(vals[2]),2),
      "max_balance_drawdown":round(float(vals[3]),2),"average_hold_seconds":float(vals[4]),
      "early_invalidation_avg_pnl":float(vals[5])/int(ints[8]) if int(ints[8]) else 0.,
      "nominal_stop_loss_saved_proxy_usd":float(vals[6]),
      "survival_pct":{str(int(h/1000)):100*int(surv[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)},
      "mean_mfe_usd":{str(int(h/1000)):float(mfe[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)},
      "mean_mae_usd":{str(int(h/1000)):float(mae[i])/trades if trades else 0. for i,h in enumerate(HORIZONS)}
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();start=time.perf_counter()
    t,sa,sb=load_stage_a(a.source);ask,bid=materialize_p75(t,sa,sb)
    f250=tick_flow(t,bid,250);f1000=tick_flow(t,bid,1000)
    variants=[]
    for guard in (1000,3000,5000):
      for depth in (0,20,50,100):
       for eff in (0.30,0.50,0.65):
        ints,vals,surv,mfe,mae=simulate_initial_hold(t,ask,bid,f250,f1000,guard,depth,eff)
        r=pack(ints,vals,surv,mfe,mae)
        r.update({"guard_ms":guard,"failure_depth_price":depth/1000.,"maintenance_efficiency_floor":eff})
        variants.append(r)
    out={"schema":"delta-005d-001-results-v1","status":"LOCAL_COMPLETE","historical_simulation_only":True,
         "ticks":int(t.size),"window":{"start_ms":int(START_MS),"end_ms_exclusive":int(END_MS)},
         "surface":"DUKAS_COINEXX_LIKE_P75","variants":variants,"runtime_seconds":time.perf_counter()-start,"august_accessed":False}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"ticks":len(t),"variants":len(variants),"runtime_seconds":out["runtime_seconds"]},indent=2))
if __name__=="__main__":main()
