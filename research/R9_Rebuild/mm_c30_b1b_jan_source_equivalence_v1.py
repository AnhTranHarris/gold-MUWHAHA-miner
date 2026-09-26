import json, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
OUT=Path('/mnt/data/MM_C30_B1B_JAN_SOURCE_EQUIV'); OUT.mkdir(exist_ok=True)
TARGET_DELTA=63.60


def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def load_ticks():
    d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw','ask_volume','bid_volume'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64','ask_volume':'float64','bid_volume':'float64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    ask=d.ask_raw.to_numpy(np.float64)/1000.0
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    av=d.ask_volume.to_numpy(np.float64); bv=d.bid_volume.to_numpy(np.float64)
    return t,mid,av,bv


def aggregate_active_seconds(t,mid,av,bv):
    sec=t//1000
    ids, idx, cnt=np.unique(sec,return_index=True,return_counts=True)
    last=idx+cnt-1
    o=mid[idx]; c=mid[last]
    h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx)
    asum=np.add.reduceat(av,idx); bsum=np.add.reduceat(bv,idx)
    return ids.astype(np.int64),o,h,l,c,cnt.astype(np.int64),asum/cnt,bsum/cnt


def build_s1(sec_ids,o,h,l,c,n,am,bm):
    N=len(sec_ids); disp=np.full(N,np.nan); eff=np.full(N,np.nan); rng=np.full(N,np.nan); turns=np.full(N,99.0)
    for i in range(10,N):
        w=c[i-9:i+1]; d=np.diff(w); travel=np.abs(d).sum(); disp[i]=w[-1]-w[0]
        eff[i]=abs(disp[i])/(travel+1e-12); rng[i]=h[i-9:i+1].max()-l[i-9:i+1].min()
        nz=np.sign(d); nz=nz[nz!=0]; turns[i]=np.sum(nz[1:]!=nz[:-1]) if len(nz)>1 else 0
    return disp,eff,rng,turns


def aggregate_tf(t,mid,tf_sec):
    bucket=t//(tf_sec*1000); ids,idx,cnt=np.unique(bucket,return_index=True,return_counts=True); last=idx+cnt-1
    c=mid[last]; h=np.maximum.reduceat(mid,idx); l=np.minimum.reduceat(mid,idx); end=(ids+1)*tf_sec
    prev=np.r_[np.nan,c[:-1]]; tr=np.maximum(h-l,np.maximum(np.abs(h-prev),np.abs(l-prev)))
    atr=np.full(len(tr),np.nan); e=np.nan
    for i,x in enumerate(tr):
        if not np.isfinite(x): continue
        e=x if not np.isfinite(e) else (13/14)*e+(1/14)*x
        if i>=13: atr[i]=e
    ret=np.r_[np.nan,np.diff(c)]
    return end.astype(np.int64), ret, atr


def m5_atr_by_sec(sec_ids,t,mid):
    end,ret,atr=aggregate_tf(t,mid,300); j=np.searchsorted(end,sec_ids,side='right')-1
    out=np.full(len(sec_ids),np.nan); ok=j>=0; out[ok]=atr[j[ok]]; return out


def align5_by_sec(sec_ids,t,mid):
    out=np.zeros(len(sec_ids),np.int8)
    for tf in (60,180,300,600,1200):
        end,ret,atr=aggregate_tf(t,mid,tf); j=np.searchsorted(end,sec_ids,side='right')-1
        ok=j>=0; rr=np.full(len(sec_ids),np.nan); aa=np.full(len(sec_ids),np.nan); rr[ok]=ret[j[ok]]; aa[ok]=atr[j[ok]]
        # raw completed-scale direction; ATR availability required, matching historical side-aligned completed-scale return/ATR concept.
        out += ((rr>0)&np.isfinite(aa)).astype(np.int8)  # long-aligned count; short is 5-count of negative below handled separately
    # Also need negative-aligned count independently.
    neg=np.zeros(len(sec_ids),np.int8)
    for tf in (60,180,300,600,1200):
        end,ret,atr=aggregate_tf(t,mid,tf); j=np.searchsorted(end,sec_ids,side='right')-1
        ok=j>=0; rr=np.full(len(sec_ids),np.nan); aa=np.full(len(sec_ids),np.nan); rr[ok]=ret[j[ok]]; aa[ok]=atr[j[ok]]
        neg += ((rr<0)&np.isfinite(aa)).astype(np.int8)
    return out,neg

@njit(cache=True)
def session_for_sec(sec):
    # Same 2026 DST logic as durable r9_research_v2 source.
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    l=(lm>=480 and lm<990); n=(nm>=480 and nm<1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit(cache=True)
def replay(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec,align_long,align_short,mode):
    # mode: 0 baseline, 1 promote-preserve-current-stop, 2 promote-reset-emergency-stop-at-2s
    maxtr=max(50000,len(t)//20)
    pnls=np.empty(maxtr,np.float64); holds=np.empty(maxtr,np.float64); promoted_arr=np.empty(maxtr,np.int8)
    ntr=0; sec_idx=-1; last_sec=-1; minute=-1; buy_lvl=0.; sell_lvl=0.; pending=0; rearms=0
    pos=0; entry=0.; stop=0.; opent=0; last_pos=0; rearm_pending=0; postticks=0; promoted=0; entry_align=0
    for i in range(len(t)):
        tt=t[i]; p=mid[i]; sec=tt//1000
        if sec!=last_sec:
            while sec_idx+1<len(sec_ids) and sec_ids[sec_idx+1] < sec: sec_idx+=1
            last_sec=sec
        mn=tt//60000
        if mn!=minute:
            minute=mn; rearms=0; pending=2; buy_lvl=round((p+.15)*100.)/100.; sell_lvl=round((p-.15)*100.)/100.
        bid=p-.10; ask=p+.10
        if pos!=0:
            postticks += 1
            elapsed=tt-opent
            # Original R9 manages normally until the actual +2s transition point.
            if mode>0 and promoted==0 and elapsed>=2000:
                if entry_align>=3 and postticks>=6:
                    promoted=1
                    if mode==2:
                        stop=(entry-.30) if pos>0 else (entry+.30)
            exited=False; ex=0.
            if (pos>0 and bid<=stop) or (pos<0 and ask>=stop):
                ex=bid if pos>0 else ask; exited=True
            else:
                maxhold=60000 if promoted else 30000
                if elapsed>=maxhold:
                    ex=bid if pos>0 else ask; exited=True
                else:
                    activation=.20 if promoted else .10; trail=.08 if promoted else .03
                    if pos>0 and bid-entry>=activation:
                        cand=bid-trail
                        if cand>stop+.005: stop=cand
                    elif pos<0 and entry-ask>=activation:
                        cand=ask+trail
                        if cand<stop-.005: stop=cand
            if exited:
                pnls[ntr-1]=(ex-entry)*pos; holds[ntr-1]=elapsed/1000.; promoted_arr[ntr-1]=promoted
                last_pos=pos; pos=0; rearm_pending=1
            continue
        if rearm_pending:
            rearm_pending=0
            if tt//60000==minute and rearms<3:
                rearms+=1; pending=-last_pos
            else: pending=0
            continue
        if pending==0 or sec_idx<10: continue
        av=atrsec[sec_idx]
        if not np.isfinite(av): continue
        ss=session_for_sec(sec_ids[sec_idx]); floor=2.5
        if ss==1: floor=2.0
        elif ss==2 or ss==3: floor=1.75
        if av+1e-12<floor: continue
        side=0
        if (pending==2 or pending==1) and ask>=buy_lvl: side=1
        elif (pending==2 or pending==-1) and bid<=sell_lvl: side=-1
        if side==0: continue
        dd=s1_disp[sec_idx]; ee=s1_eff[sec_idx]; rr=s1_rng[sec_idx]; tr=s1_turns[sec_idx]
        if not(ee>=.70 and rr>=.50 and tr<=9): continue
        if side>0 and dd<.15: continue
        if side<0 and dd>-.15: continue
        if ntr>=maxtr: break
        entry=ask if side>0 else bid; stop=(entry-.30) if side>0 else (entry+.30)
        pos=side; opent=tt; pending=0; postticks=0; promoted=0
        entry_align=align_long[sec_idx] if side>0 else align_short[sec_idx]
        pnls[ntr]=np.nan; holds[ntr]=np.nan; promoted_arr[ntr]=0; ntr+=1
    good=np.isfinite(pnls[:ntr])
    return pnls[:ntr][good],holds[:ntr][good],promoted_arr[:ntr][good]

def metrics(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum()); c=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.,c])[:-1]
    return {'trades':int(len(x)),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else 1e9,
            'win':float((x>0).mean()),'maxdd':float(np.max(peak-c)) if len(x) else 0.0}

def main():
    t0=time.time(); t,mid,av,bv=load_ticks(); sec_ids,o,h,l,c,n,am,bm=aggregate_active_seconds(t,mid,av,bv)
    sd,se,sr,st=build_s1(sec_ids,o,h,l,c,n,am,bm); atr=m5_atr_by_sec(sec_ids,t,mid); al,an=align5_by_sec(sec_ids,t,mid)
    # Warm compile on full replay only once naturally; run three modes against identical raw arrays/features.
    out={}
    for mode,name in [(0,'baseline'),(1,'promote_preserve_stop'),(2,'promote_reset_stop')]:
        p,hld,pr=replay(t,mid,sec_ids,sd,se,sr,st,atr,al,an,mode); m=metrics(p); m['avg_hold']=float(np.mean(hld)); m['promoted_trades']=int(pr.sum()); out[name]=m
    for k in ('promote_preserve_stop','promote_reset_stop'):
        out[k]['delta_vs_baseline']=out[k]['net']-out['baseline']['net']; out[k]['target_delta_error']=out[k]['delta_vs_baseline']-TARGET_DELTA
    result={'job_id':'MM-C30-B1B-M01-LIFECYCLE-SOURCE-EQUIVALENCE','month':'2026-01','historical_rule10_target_delta':TARGET_DELTA,
            'rule10_definition':'>=3 of completed 1m/3m/5m/10m/20m returns aligned at entry; alive at +2s; >=6 post-entry ticks; extension max hold 60s, activation $0.20, trail $0.08',
            'candidate_transition_semantics':{'preserve_stop':'switch future activation/trail/maxhold at +2s while retaining current R9 stop','reset_stop':'at +2s reset emergency stop to entry +/-$0.30 then apply extension'},
            'metrics':out,'raw_sha256':sha256(RAW),'elapsed_seconds':time.time()-t0,
            'promotion':'SOURCE_EQUIVALENCE_ONLY_NOT_STRATEGY_PROMOTION'}
    with open(OUT/'MM_C30_B1B_M01_RESULT.json','w') as f: json.dump(result,f,indent=2,sort_keys=True)
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()