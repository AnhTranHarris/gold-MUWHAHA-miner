from __future__ import annotations
import argparse,json,math,time
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from DELTA_005A_FAST_CONTINUATION import (
    START_MS,END_MS,load_stage_a,materialize_p75,tick_flow,
    session_code_jan_2026,q_half_raw2_to_tick,q_tick_raw
)

OBS_H=np.array([0,250,500,1000,2000,3000],dtype=np.int64)
MAX_OBS=120000
COLS=[
 "trade_id","horizon_ms","side","session","boundary_acceptance","boundary_exec_distance",
 "unrealized","flow250_aligned","flow1000_aligned","flow_delta","s1_eff","s1_eff_delta",
 "s1_disp_aligned","s1_range","s1_turns","mfe","mae","path_eff","aligned_tick_fraction",
 "extreme_renewals","ticks_since_entry","spread","boundary_lost_ever"
]
LABS=["survive_5s","survive_10s","survive_15s","eventual_win","final_hold_ms"]

@njit(cache=True)
def census(t,ask,bid,f250,f1000):
    price_scale=1000;tick=10;half=150;stopd=300;tracta=100;traild=30;minrng=500;mindisp=150
    h=np.zeros(10,np.int64);l=np.zeros(10,np.int64);c=np.zeros(10,np.int64);scount=0;sptr=0;cursec=-1;sh=sl=sclose=0
    trs=np.zeros(14,np.int64);tcount=0;tptr=0;curm5=-1;mh=ml=mclose=0;prevclose=0;haveprev=False
    minute=-1;cb=cs=0;pending=0;rearm=0;pos=0;entry=stop=0;entryms=0;entrysec=0;entry_boundary=0
    had=False;lastside=0;trade_id=0;next_h=0;trade_obs_start=0
    entry_eff=0.;entry_mid2=0;last_mid2=0;path_abs2=0;aligned_up=0;aligned_dn=0
    fav_extreme=0;extreme_renewals=0;boundary_lost=False;entry_index=0
    cmfe=0.;cmae=0.
    obs=np.zeros((MAX_OBS,len(COLS)),np.float64)
    labs=np.full((MAX_OBS,len(LABS)),-1,np.int64)
    on=0

    for i in range(t.size):
        tm=t[i];a=np.int64(ask[i]);b=np.int64(bid[i]);sec=tm//1000;mid2=a+b

        closed=False;raw=0.;holdms=0
        if pos==1 and b<=stop:
            raw=(b-entry)/price_scale;closed=True
        elif pos==-1 and a>=stop:
            raw=(entry-a)/price_scale;closed=True
        if closed:
            holdms=tm-entryms
            win=1 if raw>0 else 0
            for z in range(trade_obs_start,on):
                labs[z,0]=1 if holdms>5000 else 0
                labs[z,1]=1 if holdms>10000 else 0
                labs[z,2]=1 if holdms>15000 else 0
                labs[z,3]=win;labs[z,4]=holdms
            pos=0;entry=stop=entry_boundary=0;next_h=0

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
            dmid=mid2-last_mid2
            path_abs2+=abs(dmid)
            sd=dmid*pos
            if sd>0:aligned_up+=1
            elif sd<0:aligned_dn+=1
            last_mid2=mid2
            if pos==1:
                fav=(b-entry)/price_scale;adv=(entry-b)/price_scale
                bd=(a-entry_boundary)/price_scale;bed=(b-entry_boundary)/price_scale
                cur_ext=b
                if bd<0:boundary_lost=True
                if cur_ext>fav_extreme:fav_extreme=cur_ext;extreme_renewals+=1
            else:
                fav=(entry-a)/price_scale;adv=(a-entry)/price_scale
                bd=(entry_boundary-b)/price_scale;bed=(entry_boundary-a)/price_scale
                cur_ext=a
                if bd<0:boundary_lost=True
                if cur_ext<fav_extreme:fav_extreme=cur_ext;extreme_renewals+=1
            if fav>cmfe:cmfe=fav
            if adv>cmae:cmae=adv
            if cmae<0:cmae=0.
            elapsed=tm-entryms
            while next_h<OBS_H.size and elapsed>=OBS_H[next_h] and on<MAX_OBS:
                z=on
                obs[z,0]=trade_id;obs[z,1]=OBS_H[next_h];obs[z,2]=pos;obs[z,3]=sess
                obs[z,4]=bd;obs[z,5]=bed;obs[z,6]=fav
                obs[z,7]=pos*f250[i];obs[z,8]=pos*f1000[i];obs[z,9]=pos*(f250[i]-f1000[i])
                obs[z,10]=eff;obs[z,11]=eff-entry_eff;obs[z,12]=pos*disp/price_scale
                obs[z,13]=rng/price_scale;obs[z,14]=turns;obs[z,15]=cmfe;obs[z,16]=cmae
                obs[z,17]=abs(mid2-entry_mid2)/path_abs2 if path_abs2>0 else 0.
                den=aligned_up+aligned_dn;obs[z,18]=aligned_up/den if den>0 else .5
                obs[z,19]=extreme_renewals;obs[z,20]=i-entry_index
                obs[z,21]=(a-b)/price_scale;obs[z,22]=1. if boundary_lost else 0.
                on+=1;next_h+=1

            if sec-entrysec>=30:
                raw=((b-entry) if pos==1 else (entry-a))/price_scale;holdms=tm-entryms;win=1 if raw>0 else 0
                for z in range(trade_obs_start,on):
                    labs[z,0]=1 if holdms>5000 else 0;labs[z,1]=1 if holdms>10000 else 0
                    labs[z,2]=1 if holdms>15000 else 0;labs[z,3]=win;labs[z,4]=holdms
                pos=0;entry=stop=entry_boundary=0;next_h=0
            else:
                favraw=(b-entry) if pos==1 else (entry-a)
                if favraw>=tracta:
                    ns=q_tick_raw(b-traild if pos==1 else a+traild,tick)
                    improve=ns>stop if pos==1 else ns<stop
                    if improve:stop=ns

        elif had:
            if rearm<3:rearm+=1;pending=-lastside
            else:pending=0
            had=False;lastside=0

        elif gate:
            common=eff>.70 and rng>=minrng and turns<=9
            side=0
            if pending in (1,2) and a>=cb and common and disp>=mindisp:side=1
            elif pending in (-1,2) and b<=cs and common and disp<=-mindisp:side=-1
            if side!=0:
                pos=side;entry=a if side==1 else b;entryms=tm;entrysec=sec;entry_boundary=cb if side==1 else cs
                stop=q_tick_raw(b-stopd if side==1 else a+stopd,tick);pending=0
                trade_id+=1;trade_obs_start=on;next_h=0;entry_eff=eff;entry_mid2=mid2;last_mid2=mid2
                path_abs2=0;aligned_up=0;aligned_dn=0;extreme_renewals=0;entry_index=i;boundary_lost=False
                fav_extreme=b if side==1 else a;cmfe=0.;cmae=(a-b)/price_scale
                # Entry snapshot is written on this same causal tick.
                while next_h<OBS_H.size and OBS_H[next_h]==0 and on<MAX_OBS:
                    bd=(a-entry_boundary)/price_scale if side==1 else (entry_boundary-b)/price_scale
                    bed=(b-entry_boundary)/price_scale if side==1 else (entry_boundary-a)/price_scale
                    obs[on,0]=trade_id;obs[on,1]=0;obs[on,2]=side;obs[on,3]=sess
                    obs[on,4]=bd;obs[on,5]=bed;obs[on,6]=-(a-b)/price_scale
                    obs[on,7]=side*f250[i];obs[on,8]=side*f1000[i];obs[on,9]=side*(f250[i]-f1000[i])
                    obs[on,10]=eff;obs[on,11]=0.;obs[on,12]=side*disp/price_scale
                    obs[on,13]=rng/price_scale;obs[on,14]=turns;obs[on,15]=0.;obs[on,16]=(a-b)/price_scale
                    obs[on,17]=0.;obs[on,18]=.5;obs[on,19]=0.;obs[on,20]=0.;obs[on,21]=(a-b)/price_scale;obs[on,22]=0.
                    on+=1;next_h+=1

    if pos!=0:
        tm=t[-1];a=np.int64(ask[-1]);b=np.int64(bid[-1]);raw=(b-entry)/price_scale if pos==1 else (entry-a)/price_scale
        holdms=tm-entryms;win=1 if raw>0 else 0
        for z in range(trade_obs_start,on):
            labs[z,0]=1 if holdms>5000 else 0;labs[z,1]=1 if holdms>10000 else 0
            labs[z,2]=1 if holdms>15000 else 0;labs[z,3]=win;labs[z,4]=holdms
    return obs[:on],labs[:on],trade_id

BINS={
 "boundary_acceptance":[-1e9,-.10,-.05,-.02,0,.02,.05,.10,1e9],
 "flow":[-1.01,-.50,-.20,0,.20,.50,1.01],
 "eff":[-.01,.30,.50,.70,.85,1.01],
 "eff_delta":[-1.01,-.30,-.10,-.03,.03,.10,.30,1.01],
 "mfe_mae":[-.001,.02,.05,.10,.20,.30,1000.],
 "path_eff":[-.01,.20,.40,.60,.80,1.01],
 "aligned_fraction":[-.01,.35,.45,.50,.55,.65,1.01],
 "turns":[-.5,2.5,4.5,6.5,8.5,100.],
 "range":[-.01,.50,.75,1.0,1.5,2.0,1000.]
}

def matrix(df,x,y,xb,yb,label,min_support):
    xi=pd.cut(df[x],xb,right=False,include_lowest=True)
    yi=pd.cut(df[y],yb,right=False,include_lowest=True)
    g=df.groupby([xi,yi],observed=False)[label].agg(["count","mean"]).reset_index()
    counts=g.pivot(index=x,columns=y,values="count").fillna(0)
    rates=(100*g.pivot(index=x,columns=y,values="mean"))
    supported=rates.where(counts>=min_support)
    vals=supported.to_numpy(dtype=float)
    finite=vals[np.isfinite(vals)]
    return {
      "x":x,"y":y,"label":label,"min_support":int(min_support),
      "row_labels":[str(v) for v in counts.index],"col_labels":[str(v) for v in counts.columns],
      "counts":counts.astype(int).values.tolist(),
      "rates_pct":rates.round(4).where(pd.notna(rates),None).values.tolist(),
      "supported_min_pct":float(np.nanmin(vals)) if finite.size else None,
      "supported_max_pct":float(np.nanmax(vals)) if finite.size else None,
      "supported_separation_pp":float(np.nanmax(vals)-np.nanmin(vals)) if finite.size else None
    }

def analyse(obs,labs):
    df=pd.DataFrame(obs,columns=COLS)
    for i,n in enumerate(LABS):df[n]=labs[:,i]
    out={"schema":"delta-005e-census-v1","bins":BINS,"horizons":{},"rankings":[]}
    families=[
      ("boundary_acceptance","flow250_aligned",BINS["boundary_acceptance"],BINS["flow"]),
      ("boundary_acceptance","flow1000_aligned",BINS["boundary_acceptance"],BINS["flow"]),
      ("flow250_aligned","flow1000_aligned",BINS["flow"],BINS["flow"]),
      ("s1_eff","boundary_acceptance",BINS["eff"],BINS["boundary_acceptance"]),
      ("s1_eff_delta","boundary_acceptance",BINS["eff_delta"],BINS["boundary_acceptance"]),
      ("mfe","mae",BINS["mfe_mae"],BINS["mfe_mae"]),
      ("path_eff","mae",BINS["path_eff"],BINS["mfe_mae"]),
      ("aligned_tick_fraction","boundary_acceptance",BINS["aligned_fraction"],BINS["boundary_acceptance"]),
      ("s1_turns","flow250_aligned",BINS["turns"],BINS["flow"]),
      ("s1_range","boundary_lost_ever",BINS["range"],[-.5,.5,1.5])
    ]
    for h in OBS_H:
        q=df[df.horizon_ms==h].copy();n=len(q);ms=max(30,int(math.ceil(.005*n)))
        hkey=str(int(h));base={lab:100*q[lab].mean() for lab in ("survive_5s","survive_10s","survive_15s")}
        mats=[]
        for x,y,xb,yb in families:
            for lab in ("survive_5s","survive_10s"):
                z=matrix(q,x,y,xb,yb,lab,ms);z["horizon_ms"]=int(h);mats.append(z)
                if z["supported_separation_pp"] is not None:
                    out["rankings"].append({"horizon_ms":int(h),"matrix":x+"__"+y,"label":lab,
                      "separation_pp":z["supported_separation_pp"],"supported_max_pct":z["supported_max_pct"],
                      "supported_min_pct":z["supported_min_pct"],"n":n,"min_support":ms})
        # session x boundary-state table
        q["boundary_state"]=pd.cut(q.boundary_acceptance,[-1e9,-.02,0,.02,.05,1e9],right=False)
        sess=q.groupby(["session","boundary_state"],observed=False)[["survive_5s","survive_10s"]].agg(["count","mean"])
        out["horizons"][hkey]={"observations":n,"base_rates_pct":base,"min_supported_cell":ms,
          "matrices":mats,"session_boundary":sess.reset_index().to_dict(orient="records")}
    out["rankings"]=sorted(out["rankings"],key=lambda x:x["separation_pp"],reverse=True)
    return out,df

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--observations",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();start=time.perf_counter()
    t,sa,sb=load_stage_a(a.source);ask,bid=materialize_p75(t,sa,sb)
    f250=tick_flow(t,bid,250);f1000=tick_flow(t,bid,1000)
    obs,labs,trades=census(t,ask,bid,f250,f1000)
    analysis,df=analyse(obs,labs)
    analysis.update({"status":"LOCAL_COMPLETE","historical_forensic_only":True,"candidate_promotion_allowed":False,
      "ticks":int(t.size),"trades":int(trades),"observations":int(len(df)),"runtime_seconds":time.perf_counter()-start,
      "window":{"start_ms":int(START_MS),"end_ms_exclusive":int(END_MS)},"surface":"DUKAS_COINEXX_LIKE_P75",
      "august_accessed":False})
    df.to_csv(a.observations,index=False,compression="gzip")
    a.output.write_text(json.dumps(analysis,indent=2,default=str)+"\n")
    print(json.dumps({"ticks":len(t),"trades":trades,"observations":len(df),"runtime_seconds":analysis["runtime_seconds"],
      "top_rankings":analysis["rankings"][:10]},indent=2))
if __name__=="__main__":main()
