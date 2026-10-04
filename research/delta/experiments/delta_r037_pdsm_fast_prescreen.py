"""DELTA R037 PDH/PDL sweep -> MSS -> OB retest fast prescreen.

Implements the already-committed PDSM 17J preregistration as a source-only causal
screen before expensive surrogate-parent integration. Both PDH and PDL are kept;
no side/session split, threshold tuning, exit tuning, August, or MQL5.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import delta_r037_smor_departure_swing_prescreen as base

CONFIGS=(
    ("R037-PDSM-C01_M1_BODY_TOUCH",60_000,False),
    ("R037-PDSM-C02_M1_MIDPOINT",60_000,True),
    ("R037-PDSM-C03_M5_BODY_TOUCH",300_000,False),
    ("R037-PDSM-C04_M5_MIDPOINT",300_000,True),
)


def prior_active_day_levels(t,bid):
    day=t//base.DAY_MS
    st=np.r_[0,np.flatnonzero(day[1:]!=day[:-1])+1]
    en=np.r_[st[1:],len(t)]
    out={}; prev_hi=prev_lo=None
    for s,e in zip(st,en):
        d=int(day[s])
        if prev_hi is not None: out[d]=(int(prev_hi),int(prev_lo))
        prev_hi=int(np.max(bid[s:e])); prev_lo=int(np.min(bid[s:e]))
    return out


def visible_swings(b):
    h,l=b["high"],b["low"]
    n=len(h)
    hi=np.zeros(n,np.int64); lo=np.zeros(n,np.int64)
    hi_id=np.full(n,-1,np.int64); lo_id=np.full(n,-1,np.int64)
    lh=ll=0; lhi=lli=-1
    for i in range(n):
        p=i-2
        if p>=2:
            if base.swing_high(h,p,2): lh=int(h[p]); lhi=p
            if base.swing_low(l,p,2): ll=int(l[p]); lli=p
        hi[i]=lh; lo[i]=ll; hi_id[i]=lhi; lo_id[i]=lli
    return hi,lo,hi_id,lo_id


def last_opposite(o,c,sw,mss,side):
    # strictly after sweep and before MSS
    for j in range(mss-1,sw,-1):
        if side>0 and int(c[j])<int(o[j]): return j
        if side<0 and int(c[j])>int(o[j]): return j
    return -1


def generate(t,ask,bid,tf,require_mid):
    b=base.bars(t,bid,tf)
    o,h,l,c,e=b["open"],b["high"],b["low"],b["close"],b["end_ms"]
    vhi,vlo,vhi_id,vlo_id=visible_swings(b)
    bday=(e-1)//base.DAY_MS
    levels=prior_active_day_levels(t,bid)
    props=[]
    for d,(pdh,pdl) in levels.items():
        idx=np.flatnonzero(bday==d)
        if idx.size==0: continue
        start,end=int(idx[0]),int(idx[-1])+1
        for kind,L,side in (("PDH",pdh,-1),("PDL",pdl,1)):
            sw=-1
            for i in range(start,end):
                ok=(int(h[i])>L and int(c[i])<L) if kind=="PDH" else (int(l[i])<L and int(c[i])>L)
                if ok: sw=i; break
            if sw<0: continue
            # First causal sweep consumes this level. Freeze opposite swing visible now.
            mss_level=int(vlo[sw] if side<0 else vhi[sw])
            mss_id=int(vlo_id[sw] if side<0 else vhi_id[sw])
            if mss_id<0: continue
            mss=-1
            for j in range(sw+1,end):
                if (side<0 and int(c[j])<mss_level) or (side>0 and int(c[j])>mss_level):
                    mss=j; break
            if mss<0: continue
            ob=last_opposite(o,c,sw,mss,side)
            if ob<0: continue
            zlo=min(int(o[ob]),int(c[ob])); zhi=max(int(o[ob]),int(c[ob]))
            if zhi<=zlo: continue
            mid=(zlo+zhi)/2.0
            for k in range(mss+1,end):
                touch=int(h[k])>=zlo and int(l[k])<=zhi
                if not touch: continue
                valid=(int(c[k])<=mid and int(c[k])>=zlo) if side<0 else (int(c[k])>=mid and int(c[k])<=zhi)
                if require_mid:
                    valid=valid and int(l[k])<=mid<=int(h[k])
                # first interaction consumes zone regardless of validity
                if valid:
                    p=base.finalize_proposal(t,ask,bid,int(e[k]),side,ob)
                    props.append(p)
                break
    props.sort(key=lambda p:(p.decision_index,p.side))
    return props


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    sha=base.sha256_file(a.source)
    if sha!=base.CANONICAL_JAN_SHA256: raise SystemExit('canonical January SHA mismatch: '+sha)
    df=pd.read_csv(a.source,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype=np.int64)
    df=df[(df.timestamp_ms_utc>=base.STAGE_A_START_MS)&(df.timestamp_ms_utc<base.STAGE_A_END_MS)]
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    if t.size!=4_205_709 or np.any(t[1:]<t[:-1]): raise SystemExit(f'Stage-A chronology mismatch: {t.size}')
    ask,bid=base.p75(t,df.ask_raw.to_numpy(np.int64),df.bid_raw.to_numpy(np.int64))
    results={}; ranking=[]
    for cid,tf,mid in CONFIGS:
        props=generate(t,ask,bid,tf,mid); sp=base.supply(props,t); ex=base.simulate_source(props,t,ask,bid)
        gate={
          'minimum_proposals_8':sp['proposals']>=8,
          'minimum_distinct_days_4':sp['distinct_days']>=4,
          'minimum_accepted_entries_5':ex['accepted_entries']>=5,
          'direct_net_min_minus_2':ex['direct_net_usd']>=-2.0,
        }
        gate['fast_screen_pass']=all(gate.values()); gate['strong_fast_pass']=gate['fast_screen_pass'] and ex['direct_net_usd']>=0
        results[cid]={'supply':sp,'source_only_execution':ex,'gate':gate}
        ranking.append((int(gate['strong_fast_pass']),int(gate['fast_screen_pass']),float(ex['direct_net_usd']),int(ex['official_wins']),sp['proposals'],cid))
    ranking.sort(reverse=True)
    leaders=[{'config_id':x[-1],'strong_fast_pass':results[x[-1]]['gate']['strong_fast_pass'],'fast_screen_pass':results[x[-1]]['gate']['fast_screen_pass'],'direct_net_usd':results[x[-1]]['source_only_execution']['direct_net_usd'],'trades':results[x[-1]]['source_only_execution']['trades'],'official_wins':results[x[-1]]['source_only_execution']['official_wins'],'proposals':results[x[-1]]['supply']['proposals'],'distinct_days':results[x[-1]]['supply']['distinct_days']} for x in ranking]
    out={
      'schema':'delta-r037-pdsm-fast-prescreen-v1','status':'COMPLETE_FAST_CAUSAL_PRESCREEN','unit':'R037_PDSM_FAST_PRESCREEN','family':'R037-PDSM-v1',
      'source_sha256':sha,'stage_a_ticks':int(t.size),'surface':'DUKAS_COINEXX_LIKE_P75','numeric_retuning':False,'post_result_retuning':False,'august_accessed':False,
      'configs':results,'ranking':leaders,
      'finding':{'leading_config':leaders[0]['config_id'],'strong_survivors':[x['config_id'] for x in leaders if x['strong_fast_pass']],'screen_survivors':[x['config_id'] for x in leaders if x['fast_screen_pass']],'next':'FULL_SURROGATE_PARENT_INTEGRATION' if any(x['fast_screen_pass'] for x in leaders) else 'RETIRE_R037_PDSM_NO_RETUNE'},
      'mql5_authorized':False,
    }
    base.atomic_write_json(a.output,out); print(json.dumps({'ranking':leaders,'finding':out['finding']},separators=(',',':')))

if __name__=='__main__': main()
