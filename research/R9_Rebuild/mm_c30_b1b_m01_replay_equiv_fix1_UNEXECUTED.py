import json, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

RAW=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
CACHE=Path('/mnt/data/mmc30_b1b_replay/MM_C30_B1B_M01_CAUSAL_CACHE.npz')
OUT=Path('/mnt/data/MM_C30_B1B_M01_REPLAY_EQUIV'); OUT.mkdir(exist_ok=True)
TARGET=63.60
EXPECTED_RAW='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
EXPECTED_CACHE='71fc132e208589857dfe5dd6b8b1a204bd626d65c249890e842b6d5647ba65a5'

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def metrics(x,holds,prom):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    c=np.cumsum(x); peak=np.maximum.accumulate(np.r_[0.,c])[:-1]
    return {'trades':int(len(x)),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else 1e9,
            'win':float((x>0).mean()) if len(x) else 0.0,'maxdd':float(np.max(peak-c)) if len(x) else 0.0,
            'avg_hold':float(np.mean(holds)) if len(holds) else 0.0,'promoted_trades':int(prom.sum())}

@njit(cache=False)
def session_for_sec(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    l=(lm>=480 and lm<990); n=(nm>=480 and nm<1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit(cache=False)
def replay(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec,align_long,align_short,mode):
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
        entry=ask if side>0 else bid; stop=(bid-.30) if side>0 else (ask+.30)
        pos=side; opent=tt; pending=0; postticks=0; promoted=0
        entry_align=align_long[sec_idx] if side>0 else align_short[sec_idx]
        pnls[ntr]=np.nan; holds[ntr]=np.nan; promoted_arr[ntr]=0; ntr+=1
    good=np.isfinite(pnls[:ntr])
    return pnls[:ntr][good],holds[:ntr][good],promoted_arr[:ntr][good]

def main():
    t0=time.time()
    raw_sha=sha256(RAW); cache_sha=sha256(CACHE)
    assert raw_sha==EXPECTED_RAW,(raw_sha,EXPECTED_RAW)
    assert cache_sha==EXPECTED_CACHE,(cache_sha,EXPECTED_CACHE)
    z=np.load(CACHE)
    sec_ids=z['sec_ids']; sd=z['s1_disp']; se=z['s1_eff']; sr=z['s1_range']; st=z['s1_turns']; atr=z['m5_atr']; al=z['align_long']; an=z['align_short']
    d=pd.read_csv(RAW,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy(np.int64,copy=False)
    ask=d.ask_raw.to_numpy(np.float64)/1000.; bid=d.bid_raw.to_numpy(np.float64)/1000.; mid=(ask+bid)*.5
    out={}
    for mode,name in ((0,'baseline'),(1,'promote_preserve_stop'),(2,'promote_reset_stop')):
        p,h,pr=replay(t,mid,sec_ids,sd,se,sr,st,atr,al,an,mode)
        out[name]=metrics(p,h,pr)
    for k in ('promote_preserve_stop','promote_reset_stop'):
        out[k]['delta_vs_baseline']=out[k]['net']-out['baseline']['net']
        out[k]['target_delta_error']=out[k]['delta_vs_baseline']-TARGET
    # equivalence decision deliberately based on closest absolute checksum error, not economic superiority.
    errs={k:abs(out[k]['target_delta_error']) for k in ('promote_preserve_stop','promote_reset_stop')}
    closest=min(errs,key=errs.get)
    tol=0.50
    result={'job_id':'MM-C30-B1B-M01-REPLAY-EQUIV','status':'COMPLETED_LOCAL','month':'2026-01',
      'historical_rule10_target_delta':TARGET,'checksum_tolerance':tol,
      'rule10_definition':'>=3/5 completed 1m/3m/5m/10m/20m returns aligned at entry; alive +2s; >=6 post-entry ticks; extension 60s max hold, +$0.20 activation, $0.08 trail',
      'candidate_transition_semantics':{'preserve_stop':'retain the live R9 stop at +2s, switch only future activation/trail/maxhold','reset_stop':'reset emergency stop to entry +/-$0.30 at +2s, then apply extension'},
      'metrics':out,'closest_semantic':closest,'closest_abs_target_error':float(errs[closest]),'source_equivalent':bool(errs[closest] <= tol),
      'raw_sha256':raw_sha,'cache_sha256':cache_sha,'elapsed_seconds':time.time()-t0,
      'baseline_source_fix':'initial stop restored to authoritative r9_research_v2 semantics: bid-0.30 / ask+0.30','promotion':'SOURCE_EQUIVALENCE_ONLY_NOT_STRATEGY_PROMOTION'}
    p=OUT/'MM_C30_B1B_M01_REPLAY_RESULT.json'; p.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()