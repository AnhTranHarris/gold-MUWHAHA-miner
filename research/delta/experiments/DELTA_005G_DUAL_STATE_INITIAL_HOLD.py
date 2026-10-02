from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from DELTA_005A_FAST_CONTINUATION import (
    START_MS,END_MS,HORIZONS,load_stage_a,materialize_p75,tick_flow,
    session_code_jan_2026,q_half_raw2_to_tick,q_tick_raw
)

@__import__("numba").njit(cache=True)
def simulate(t,ask,bid,f250,f1000,validation_ms,range_ceiling_raw,min_accept_raw,never_lost_mode):
    price_scale=1000;tick=10;half=150;stopd=300;tracta=100;traild=30;minrng=500;mindisp=150
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entryms=0;entrysec=0;entry_boundary=0
    had=False;lastside=0;boundary_lost=False;direct_owned=False;validation_done=False
    trades=wins=losses=ebuys=esells=maxholds=trails=rearms=0
    direct_valid=consolidation_valid=early_invalid=0;early_pnl=0.
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
            pos=0;entry=stop=entry_boundary=0;direct_owned=False;validation_done=False;boundary_lost=False

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
        regime=tcount==14 and (a-b)<=250 and atrsum>=14*floorraw

        mi=tm//60000
        if mi!=minute:
            minute=mi;pending=2;rearm=0
            cb=q_half_raw2_to_tick(b+a+2*half,tick);cs=q_half_raw2_to_tick(b+a-2*half,tick)

        if pos!=0:
            had=True;lastside=pos
            elapsed=tm-entryms

            # Track initial ownership state causally.
            if pos==1:
                if b<entry_boundary:boundary_lost=True
                if f250[i]>=0. and f1000[i]>=0.:direct_owned=True
                accept=b-entry_boundary
            else:
                if a>entry_boundary:boundary_lost=True
                if f250[i]<=0. and f1000[i]<=0.:direct_owned=True
                accept=entry_boundary-a

            # One-time initial-hold validation.
            if (not validation_done) and elapsed>=validation_ms:
                history_ok=(not boundary_lost) if never_lost_mode==1 else True
                consolidation_ok=regime and history_ok and accept>=min_accept_raw and rng<=range_ceiling_raw
                validation_done=True
                if direct_owned:
                    direct_valid+=1
                elif consolidation_ok:
                    consolidation_valid+=1
                else:
                    raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
                    ex=raw-.01
                    if raw>0:gp+=ex;wins+=1
                    else:gl+=ex;losses+=1
                    bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.;early_invalid+=1;early_pnl+=ex
                    for q in range(5):
                        if holdms>HORIZONS[q]:surv[q]+=1
                        mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                    pos=0;entry=stop=entry_boundary=0;direct_owned=False;boundary_lost=False
                    continue

            if pos!=0:
                if sec-entrysec>=30:
                    raw=((b-entry) if pos==1 else (entry-a))/price_scale;ex=raw-.01
                    if raw>0:gp+=ex;wins+=1
                    else:gl+=ex;losses+=1
                    bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.;maxholds+=1
                    for q in range(5):
                        if holdms>HORIZONS[q]:surv[q]+=1
                        mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                    pos=0;entry=stop=entry_boundary=0;direct_owned=False;validation_done=False;boundary_lost=False
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

        elif regime:
            common=eff>.70 and rng>=minrng and turns<=9
            side=0
            if pending in (1,2) and a>=cb and common and disp>=mindisp:side=1
            elif pending in (-1,2) and b<=cs and common and disp<=-mindisp:side=-1
            if side!=0:
                pos=side;entry=a if side==1 else b;entryms=tm;entrysec=sec;entry_boundary=cb if side==1 else cs
                stop=q_tick_raw(b-stopd if side==1 else a+stopd,tick);pending=0
                if side==1:ebuys+=1
                else:esells+=1
                direct_owned=(f250[i]>=0. and f1000[i]>=0.) if side==1 else (f250[i]<=0. and f1000[i]<=0.)
                validation_done=False;boundary_lost=False
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

    ints=np.array([trades,wins,losses,ebuys,esells,direct_valid,consolidation_valid,early_invalid,maxholds,rearms],np.int64)
    vals=np.array([gp,gl,gp+gl,maxbdd,holdsum/trades if trades else 0.,early_pnl],np.float64)
    return ints,vals,surv,mfe_sum,mae_sum

def pack(ints,vals,surv,mfe,mae):
    trades=int(ints[0]);ei=int(ints[7])
    return {
      "trades":trades,"wins":int(ints[1]),"losses":int(ints[2]),"entry_buy":int(ints[3]),"entry_sell":int(ints[4]),
      "direct_validations":int(ints[5]),"consolidation_validations":int(ints[6]),"early_invalidations":ei,
      "max_hold_exits":int(ints[8]),"rearms":int(ints[9]),
      "gross_profit":round(float(vals[0]),2),"gross_loss":round(float(vals[1]),2),"net_profit":round(float(vals[2]),2),
      "max_balance_drawdown":round(float(vals[3]),2),"average_hold_seconds":float(vals[4]),
      "early_invalidation_avg_pnl":float(vals[5])/ei if ei else 0.,
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
    for validation in (250,500,1000,2000):
      for ceiling in (500,750,1000):
       for minacc in (0,50):
        for mode in (0,1):
         ints,vals,surv,mfe,mae=simulate(t,ask,bid,f250,f1000,validation,ceiling,minacc,mode)
         r=pack(ints,vals,surv,mfe,mae)
         r.update({"validation_ms":validation,"range_ceiling_price":ceiling/1000.,
                   "min_boundary_acceptance_price":minacc/1000.,
                   "boundary_history_mode":"NEVER_LOST" if mode==1 else "CURRENT_HELD"})
         variants.append(r)
    out={"schema":"delta-005g-001-results-v1","status":"LOCAL_COMPLETE","historical_simulation_only":True,
         "ticks":int(t.size),"window":{"start_ms":int(START_MS),"end_ms_exclusive":int(END_MS)},
         "surface":"DUKAS_COINEXX_LIKE_P75","variants":variants,"runtime_seconds":time.perf_counter()-start,
         "august_accessed":False}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"ticks":len(t),"variants":len(variants),"runtime_seconds":out["runtime_seconds"]},indent=2))
if __name__=="__main__":main()
