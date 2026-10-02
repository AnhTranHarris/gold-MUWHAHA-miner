from __future__ import annotations
import argparse,json,time
from pathlib import Path
import numpy as np
from DELTA_005A_FAST_CONTINUATION import (
    START_MS,END_MS,HORIZONS,load_stage_a,materialize_p75,tick_flow,
    session_code_jan_2026,q_half_raw2_to_tick,q_tick_raw
)

@__import__("numba").njit(cache=True)
def simulate_failed_break(t,ask,bid,fast_flow,slow_flow,failure_depth_raw,opp_flow_thr,timeout_ms):
    price_scale=1000;tick=10;half=150;stopd=300;tracta=100;traild=30;minrng=500;mindisp=150
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entryms=0;entrysec=0;had=False;lastside=0
    handoff_side=0;break_seen=False;break_ms=0
    trades=wins=losses=ebuys=esells=maxholds=trails=rearms=0
    direct_entries=direct_wins=reversal_entries=reversal_wins=0
    break_attempts=timeouts=cancels=0
    gp=0.;gl=0.;bal=100000.;bpeak=bal;maxbdd=0.;holdsum=0.
    surv=np.zeros(5,np.int64);mfe_sum=np.zeros(5,np.float64);mae_sum=np.zeros(5,np.float64)
    cmfe=np.zeros(5,np.float64);cmae=np.zeros(5,np.float64);entry_kind=0

    for i in range(t.size):
        tm=t[i];a=np.int64(ask[i]);b=np.int64(bid[i]);sec=tm//1000;mid2=np.int64(a)+np.int64(b)

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
            if raw>0:
                gp+=ex;wins+=1
                if entry_kind==1:direct_wins+=1
                elif entry_kind==2:reversal_wins+=1
            else:gl+=ex;losses+=1
            bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.
            for q in range(5):
                if holdms>HORIZONS[q]:surv[q]+=1
                mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
            pos=0;entry=stop=0;entry_kind=0

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
            if handoff_side!=0:cancels+=1
            minute=mi;pending=2;rearm=0
            cb=q_half_raw2_to_tick(b+a+2*half,tick);cs=q_half_raw2_to_tick(b+a-2*half,tick)
            handoff_side=0;break_seen=False

        if pos!=0:
            had=True;lastside=pos
            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale;ex=raw-.01
                if raw>0:
                    gp+=ex;wins+=1
                    if entry_kind==1:direct_wins+=1
                    elif entry_kind==2:reversal_wins+=1
                else:gl+=ex;losses+=1
                bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.;maxholds+=1
                for q in range(5):
                    if holdms>HORIZONS[q]:surv[q]+=1
                    mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q];cmfe[q]=0.;cmae[q]=0.
                pos=0;entry=stop=0;entry_kind=0
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
            had=False;lastside=0;handoff_side=0;break_seen=False

        else:
            common=gate and eff>.70 and rng>=minrng and turns<=9
            base_side=0
            if common and pending in (1,2) and a>=cb and disp>=mindisp:base_side=1
            elif common and pending in (-1,2) and b<=cs and disp<=-mindisp:base_side=-1

            if handoff_side==0 and base_side!=0:
                flow_ok=(fast_flow[i]>=0. and slow_flow[i]>=0.) if base_side==1 else (fast_flow[i]<=0. and slow_flow[i]<=0.)
                if flow_ok:
                    if base_side==1:
                        pos=1;entry=a;stop=q_tick_raw(b-stopd,tick);ebuys+=1
                    else:
                        pos=-1;entry=b;stop=q_tick_raw(a+stopd,tick);esells+=1
                    entryms=tm;entrysec=sec;pending=0;direct_entries+=1;entry_kind=1
                    bal-=.01;gl-=.01
                    for q in range(5):cmfe[q]=0.;cmae[q]=0.
                else:
                    handoff_side=base_side;break_seen=False

            if pos==0 and handoff_side!=0:
                boundary=cb if handoff_side==1 else cs
                if not break_seen:
                    crossed=(mid2>=2*boundary) if handoff_side==1 else (mid2<=2*boundary)
                    if crossed:
                        break_seen=True;break_ms=tm;break_attempts+=1
                else:
                    if tm-break_ms>timeout_ms:
                        handoff_side=0;break_seen=False;timeouts+=1
                    elif gate:
                        if handoff_side==1:
                            failed=mid2<=2*(boundary-failure_depth_raw)
                            flow_flip=fast_flow[i]<=-opp_flow_thr and slow_flow[i]<=-opp_flow_thr
                            if failed and flow_flip:
                                pos=-1;entry=b;stop=q_tick_raw(a+stopd,tick);esells+=1
                                entryms=tm;entrysec=sec;pending=0;reversal_entries+=1;entry_kind=2
                                bal-=.01;gl-=.01
                                for q in range(5):cmfe[q]=0.;cmae[q]=0.
                                handoff_side=0;break_seen=False
                        else:
                            failed=mid2>=2*(boundary+failure_depth_raw)
                            flow_flip=fast_flow[i]>=opp_flow_thr and slow_flow[i]>=opp_flow_thr
                            if failed and flow_flip:
                                pos=1;entry=a;stop=q_tick_raw(b-stopd,tick);ebuys+=1
                                entryms=tm;entrysec=sec;pending=0;reversal_entries+=1;entry_kind=2
                                bal-=.01;gl-=.01
                                for q in range(5):cmfe[q]=0.;cmae[q]=0.
                                handoff_side=0;break_seen=False

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
        raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale;ex=raw-.01
        if raw>0:
            gp+=ex;wins+=1
            if entry_kind==1:direct_wins+=1
            elif entry_kind==2:reversal_wins+=1
        else:gl+=ex;losses+=1
        bal+=ex;trades+=1;holdms=tm-entryms;holdsum+=holdms/1000.
        for q in range(5):
            if holdms>HORIZONS[q]:surv[q]+=1
            mfe_sum[q]+=cmfe[q];mae_sum[q]+=cmae[q]

    ints=np.array([trades,wins,losses,ebuys,esells,direct_entries,direct_wins,reversal_entries,reversal_wins,break_attempts,timeouts,cancels],np.int64)
    vals=np.array([gp,gl,gp+gl,maxbdd,holdsum/trades if trades else 0.],np.float64)
    return ints,vals,surv,mfe_sum,mae_sum

def pack(ints,vals,surv,mfe,mae):
    trades=int(ints[0])
    return {
      "trades":trades,"wins":int(ints[1]),"losses":int(ints[2]),"entry_buy":int(ints[3]),"entry_sell":int(ints[4]),
      "direct_entries":int(ints[5]),"direct_wins":int(ints[6]),"reversal_entries":int(ints[7]),"reversal_wins":int(ints[8]),
      "break_attempts":int(ints[9]),"timeouts":int(ints[10]),"cancels":int(ints[11]),
      "gross_profit":round(float(vals[0]),2),"gross_loss":round(float(vals[1]),2),"net_profit":round(float(vals[2]),2),
      "max_balance_drawdown":round(float(vals[3]),2),"average_hold_seconds":float(vals[4]),
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
    for depth in (0,20,50):
      for thr in (0.,0.1,0.2):
       for timeout in (1000,3000,5000):
        ints,vals,surv,mfe,mae=simulate_failed_break(t,ask,bid,f250,f1000,depth,thr,timeout)
        r=pack(ints,vals,surv,mfe,mae)
        r.update({"failure_depth_price":depth/1000.,"opposite_flow_threshold":thr,"timeout_ms":timeout})
        variants.append(r)
    out={"schema":"delta-005c-001-results-v1","status":"LOCAL_COMPLETE","historical_simulation_only":True,
         "ticks":int(t.size),"window":{"start_ms":int(START_MS),"end_ms_exclusive":int(END_MS)},
         "surface":"DUKAS_COINEXX_LIKE_P75","variants":variants,"runtime_seconds":time.perf_counter()-start,"august_accessed":False}
    a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"ticks":len(t),"variants":len(variants),"runtime_seconds":out["runtime_seconds"]},indent=2))
if __name__=="__main__":main()
