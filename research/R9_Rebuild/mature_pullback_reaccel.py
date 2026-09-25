import os, glob, gzip, json, hashlib, argparse, math
import numpy as np
import pandas as pd
from numba import njit

DATA_DIR='/mnt/data'
EV_DIR='/mnt/data/r9_research_v2'
OUT='/mnt/data/r9_research_v2/mature_pullback'
os.makedirs(OUT,exist_ok=True)

PB_LEVELS=np.array([0.30,0.50,0.80,1.00,1.20,1.50],dtype=np.float64)
RC_LEVELS=np.array([0.10,0.20,0.30,0.50],dtype=np.float64)
VOTE_REQS=(2,3)
STRENGTHS=(0.00,0.10,0.20)
PB_WINDOWS=(60,120,240)
RC_WINDOWS=(30,60,120)

@njit(cache=True)
def trade_lifecycle(t,mid,start_i,side,stopdist,activation,trail,maxhold_ms):
    p=mid[start_i]
    entry=p+0.10 if side>0 else p-0.10
    stop=entry-stopdist if side>0 else entry+stopdist
    armed=False; mfe=0.0; mae=0.0
    opent=t[start_i]
    n=len(t)
    i=start_i
    while i<n:
        tt=t[i]
        if tt-opent>maxhold_ms: break
        m=mid[i]; bid=m-0.10; ask=m+0.10
        fav=(bid-entry) if side>0 else (entry-ask)
        adv=(entry-bid) if side>0 else (ask-entry)
        if fav>mfe: mfe=fav
        if adv>mae: mae=adv
        if (side>0 and bid<=stop) or (side<0 and ask>=stop):
            ex=bid if side>0 else ask
            return (ex-entry)*side,(tt-opent)/1000.0,mfe,mae
        if side>0 and bid-entry>=activation:
            armed=True
            ns=bid-trail
            if ns>stop: stop=ns
        elif side<0 and entry-ask>=activation:
            armed=True
            ns=ask+trail
            if ns<stop: stop=ns
        i+=1
    end_i=min(i,n-1)
    p=mid[end_i]; ex=p-0.10 if side>0 else p+0.10
    return (ex-entry)*side,(t[end_i]-opent)/1000.0,mfe,mae

@njit(cache=True)
def detect_and_trade(t,mid,event_i,struct_side,pb,rc,pbwin_ms,rcwin_ms,life_code):
    n=len(t); start_t=t[event_i]; p0=mid[event_i]
    pb_i=-1; extreme=p0
    i=event_i+1
    while i<n and t[i]-start_t<=pbwin_ms:
        m=mid[i]
        if struct_side>0:
            if m>extreme: extreme=m
            if extreme-m>=pb:
                pb_i=i; break
        else:
            if m<extreme: extreme=m
            if m-extreme>=pb:
                pb_i=i; break
        i+=1
    if pb_i<0: return -1,0.,0.,0.,0.
    pb_ext=mid[pb_i]; pb_t=t[pb_i]
    i=pb_i+1
    entry_i=-1
    while i<n and t[i]-pb_t<=rcwin_ms:
        m=mid[i]
        if struct_side>0:
            if m<pb_ext: pb_ext=m
            if m-pb_ext>=rc:
                entry_i=i; break
        else:
            if m>pb_ext: pb_ext=m
            if pb_ext-m>=rc:
                entry_i=i; break
        i+=1
    if entry_i<0: return -1,0.,0.,0.,0.
    if life_code==0:
        pnl,hold,mfe,mae=trade_lifecycle(t,mid,entry_i,struct_side,.30,.10,.03,30000)
    elif life_code==1:
        pnl,hold,mfe,mae=trade_lifecycle(t,mid,entry_i,struct_side,.80,.20,.08,120000)
    elif life_code==2:
        pnl,hold,mfe,mae=trade_lifecycle(t,mid,entry_i,struct_side,1.00,.30,.10,120000)
    else:
        pnl,hold,mfe,mae=trade_lifecycle(t,mid,entry_i,struct_side,1.00,.20,.08,240000)
    return entry_i,pnl,hold,mfe,mae

def load_ticks(month):
    pats=glob.glob(f'{DATA_DIR}/XAUUSD_DUKAS_2026_{month:02d}_ticks.csv*.gz')
    if not pats: raise FileNotFoundError(month)
    f=pats[0]
    df=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=df.timestamp_ms_utc.to_numpy(np.int64)
    mid=(df.ask_raw.to_numpy(np.float64)+df.bid_raw.to_numpy(np.float64))/2000.0
    return t,mid

def structural_state(ev):
    cols=['tf300_retatr','tf600_retatr','tf1200_retatr','tf3600_retatr']
    A=np.vstack([ev[c].to_numpy(float)*ev.side.to_numpy(float) for c in cols]).T
    signs=np.sign(np.nan_to_num(A,nan=0.0))
    pos=(signs>0).sum(1); neg=(signs<0).sum(1)
    ss=np.where(pos>neg,1,np.where(neg>pos,-1,0)).astype(np.int8)
    votes=np.maximum(pos,neg).astype(np.int8)
    aligned=A*ss[:,None]
    strength=np.nanmean(aligned,axis=1)
    return ss,votes,strength

def event_tick_indices(t, times):
    ix=np.searchsorted(t,times,side='left')
    ix=np.clip(ix,0,len(t)-1)
    return ix.astype(np.int64)

def run_month(month):
    ev=pd.read_pickle(f'{EV_DIR}/events_{month:02d}.pkl.gz',compression='gzip')
    t,mid=load_ticks(month)
    ss,votes,strength=structural_state(ev)
    eix=event_tick_indices(t,ev.time_ms.to_numpy(np.int64))
    rows=[]
    for vote_req in VOTE_REQS:
      for sthr in STRENGTHS:
       eligible=np.flatnonzero((ss!=0)&(votes>=vote_req)&(strength>=sthr))
       for pb in PB_LEVELS:
        for rc in RC_LEVELS:
         for pbw in PB_WINDOWS:
          for rcw in RC_WINDOWS:
           for life in range(4):
            pnl=[]; holds=[]; mfes=[]; maes=[]; nentry=0
            for k in eligible:
                ent,p,h,mf,ma=detect_and_trade(t,mid,eix[k],int(ss[k]),pb,rc,pbw*1000,rcw*1000,life)
                if ent>=0:
                    nentry+=1; pnl.append(p); holds.append(h); mfes.append(mf); maes.append(ma)
            if nentry:
                a=np.asarray(pnl); gp=float(a[a>0].sum()); gl=float(a[a<0].sum())
                rows.append((month,vote_req,sthr,pb,rc,pbw,rcw,life,len(eligible),nentry,float(a.sum()),float(a.mean()),gp,gl,gp/(-gl) if gl<0 else 999.,float((a>0).mean()),float(np.mean(holds)),float(np.mean(mfes)),float(np.mean(maes))))
    cols=['month','votes','strength','pb','rc','pbwin','rcwin','life','eligible','trades','net','mean','gp','gl','pf','win','hold','mfe','mae']
    out=pd.DataFrame(rows,columns=cols)
    path=f'{OUT}/month_{month:02d}_screen.csv.gz'; out.to_csv(path,index=False,compression='gzip')
    print('DONE',month,len(ev),len(out),path,flush=True)
    return out

def summarize(months):
    dfs=[pd.read_csv(f'{OUT}/month_{m:02d}_screen.csv.gz') for m in months]
    allx=pd.concat(dfs,ignore_index=True)
    keys=['votes','strength','pb','rc','pbwin','rcwin','life']
    agg=allx.groupby(keys).agg(net=('net','sum'),trades=('trades','sum'),gp=('gp','sum'),gl=('gl','sum'),mean=('mean','mean'),min_month=('net','min'),months_pos=('net',lambda x:int((x>0).sum())),min_pf=('pf','min')).reset_index()
    agg['pf']=agg.gp/(-agg.gl)
    agg=agg.sort_values(['months_pos','min_month','net'],ascending=[False,False,False])
    agg.to_csv(f'{OUT}/discovery_summary.csv',index=False)
    print(agg.head(40).to_string(index=False),flush=True)
    return agg

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int); ap.add_argument('--summary',action='store_true'); args=ap.parse_args()
    if args.month: run_month(args.month)
    if args.summary: summarize([1,2,3])
