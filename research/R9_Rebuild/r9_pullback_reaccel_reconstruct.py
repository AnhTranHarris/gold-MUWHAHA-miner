import argparse, glob, json, os, hashlib
import numpy as np
import pandas as pd
from numba import njit

DATA_DIR='/mnt/data'
OUT='/mnt/data/r9_research_v2/pullback_reaccel'
os.makedirs(OUT, exist_ok=True)

@njit
def _tf_close_ret(t, mid, tf_sec):
    bucket = t // (tf_sec*1000)
    n=len(t)
    maxn=n//10+10000
    ids=np.empty(maxn,np.int64); closes=np.empty(maxn,np.float64); ends=np.empty(maxn,np.int64)
    k=-1; last=-1
    for i in range(n):
        b=bucket[i]
        if b!=last:
            k+=1; ids[k]=b; last=b
        closes[k]=mid[i]
        ends[k]=(b+1)*tf_sec
    k+=1
    ret=np.empty(k,np.float64); ret[0]=np.nan
    for i in range(1,k): ret[i]=closes[i]-closes[i-1]
    return ends[:k],ret[:k]

@njit
def _structural_vote(event_ms, ends15,r15, ends30,r30, ends60,r60):
    n=len(event_ms); out=np.zeros(n,np.int8)
    for k in range(n):
        sec=event_ms[k]//1000
        pos=0; neg=0
        for ends, rr in ((ends15,r15),(ends30,r30),(ends60,r60)):
            j=np.searchsorted(ends,sec,side='right')-1
            if j>=0 and np.isfinite(rr[j]):
                if rr[j]>0: pos+=1
                elif rr[j]<0: neg+=1
        if pos>=2: out[k]=1
        elif neg>=2: out[k]=-1
    return out

@njit
def _extract_entries(t,mid,event_ms,struct_dir,depths,reaccels,max_window_ms):
    n=len(event_ms); nm=len(depths)*(1+len(reaccels))
    ent_idx=np.full((n,nm),-1,np.int64)
    ent_delay=np.full((n,nm),-1,np.int64)
    event_i=np.searchsorted(t,event_ms)
    for k in range(n):
        s=struct_dir[k]
        if s==0: continue
        i0=event_i[k]
        if i0>=len(t): continue
        p0=mid[i0]
        endt=event_ms[k]+max_window_ms
        hit=np.zeros(len(depths),np.uint8)
        extreme=np.empty(len(depths),np.float64)
        for d in range(len(depths)): extreme[d]=p0
        for i in range(i0+1,len(t)):
            if t[i]>endt: break
            p=mid[i]
            for di in range(len(depths)):
                base=di*(1+len(reaccels))
                dep=depths[di]
                if hit[di]==0:
                    if s*(p-p0)<=-dep:
                        hit[di]=1; extreme[di]=p
                        ent_idx[k,base]=i; ent_delay[k,base]=t[i]-event_ms[k]
                else:
                    if s*(p-extreme[di])<0: extreme[di]=p
                    for ri in range(len(reaccels)):
                        col=base+1+ri
                        if ent_idx[k,col]<0 and s*(p-extreme[di])>=reaccels[ri]:
                            ent_idx[k,col]=i; ent_delay[k,col]=t[i]-event_ms[k]
            done=True
            for c in range(nm):
                if ent_idx[k,c]<0: done=False; break
            if done: break
    return ent_idx,ent_delay

@njit
def _simulate_entries(t,mid,ent_idx,side,stop_dist,target_dist,max_hold_ms):
    n,m=ent_idx.shape
    pnl=np.full((n,m),np.nan,np.float64)
    exit_ms=np.full((n,m),-1,np.int64)
    hold=np.full((n,m),np.nan,np.float64)
    mfe=np.full((n,m),np.nan,np.float64)
    mae=np.full((n,m),np.nan,np.float64)
    for k in range(n):
        s=side[k]
        if s==0: continue
        for c in range(m):
            i0=ent_idx[k,c]
            if i0<0: continue
            p=mid[i0]; entry=p+0.10 if s>0 else p-0.10
            best=0.0; worst=0.0; ex=entry; ei=i0
            opent=t[i0]
            for i in range(i0+1,len(t)):
                tt=t[i]; p=mid[i]; bid=p-0.10; ask=p+0.10
                fav=(bid-entry) if s>0 else (entry-ask)
                adv=(entry-bid) if s>0 else (ask-entry)
                if fav>best: best=fav
                if adv>worst: worst=adv
                if (s>0 and bid<=entry-stop_dist) or (s<0 and ask>=entry+stop_dist):
                    ex=bid if s>0 else ask; ei=i; break
                if (s>0 and bid>=entry+target_dist) or (s<0 and ask<=entry-target_dist):
                    ex=bid if s>0 else ask; ei=i; break
                if tt-opent>=max_hold_ms:
                    ex=bid if s>0 else ask; ei=i; break
            pnl[k,c]=(ex-entry)*s; exit_ms[k,c]=t[ei]; hold[k,c]=(t[ei]-opent)/1000.0; mfe[k,c]=best; mae[k,c]=worst
    return pnl,exit_ms,hold,mfe,mae

def load_month(month):
    f=glob.glob(f'{DATA_DIR}/XAUUSD_DUKAS_2026_{month:02d}_ticks.csv*.gz')[0]
    d=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.0
    ev=pd.read_pickle(f'/mnt/data/r9_research_v2/events_{month:02d}.pkl.gz',compression='gzip')
    return f,t,mid,ev

def sequential_metrics(event_ms, ent_delay, entry_idx, exit_ms, pnl, max_window_ms):
    ok=np.isfinite(pnl) & (entry_idx>=0) & (ent_delay>=0) & (ent_delay<=max_window_ms)
    ids=np.where(ok)[0]
    if len(ids)==0: return dict(trades=0,net=0,gp=0,gl=0,pf=np.nan,win=np.nan,avg_hold=np.nan)
    ent_time=event_ms[ids]+ent_delay[ids]
    order=ids[np.argsort(ent_time,kind='stable')]
    last_exit=-1; chosen=[]
    for k in order:
        et=event_ms[k]+ent_delay[k]
        if et<=last_exit: continue
        chosen.append(k); last_exit=int(exit_ms[k])
    ch=np.asarray(chosen,dtype=int)
    x=pnl[ch]
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return dict(trades=int(len(ch)),net=float(x.sum()),gp=gp,gl=gl,pf=float(gp/(-gl)) if gl<0 else np.inf,win=float((x>0).mean()),chosen=ch)

def main(month):
    src,t,mid,ev=load_month(month)
    e=ev.time_ms.to_numpy(np.int64)
    ends15,r15=_tf_close_ret(t,mid,900); ends30,r30=_tf_close_ret(t,mid,1800); ends60,r60=_tf_close_ret(t,mid,3600)
    s=_structural_vote(e,ends15,r15,ends30,r30,ends60,r60)
    depths=np.array([1.20,1.35,1.50],np.float64)
    reacc=np.array([0.20,0.35,0.50],np.float64)
    ent,delay=_extract_entries(t,mid,e,s,depths,reacc,240000)
    pnl,ex,hold,mfe,mae=_simulate_entries(t,mid,ent,s,0.90,4.50,120000)
    labels=[]
    for d in depths:
        labels.append(f'd{d:.2f}_touch')
        for r in reacc: labels.append(f'd{d:.2f}_reacc{r:.2f}')
    out=[]
    for w in [120000,180000,240000]:
        for c,label in enumerate(labels):
            met=sequential_metrics(e,delay[:,c],ent[:,c],ex[:,c],pnl[:,c],w)
            ch=met.pop('chosen',np.array([],dtype=int))
            met.update(month=month,window_sec=w//1000,mode=label,stop=0.90,target=4.50,max_hold=120,
                       avg_hold=float(np.nanmean(hold[ch,c])) if len(ch) else np.nan,
                       avg_mfe=float(np.nanmean(mfe[ch,c])) if len(ch) else np.nan,
                       avg_mae=float(np.nanmean(mae[ch,c])) if len(ch) else np.nan,
                       structural_events=int(np.sum(s!=0)),candidate_entries=int(np.sum((ent[:,c]>=0)&(delay[:,c]<=w))))
            out.append(met)
    odf=pd.DataFrame(out).sort_values(['net','pf'],ascending=[False,False])
    op=f'{OUT}/pullback_screen_{month:02d}.csv'; odf.to_csv(op,index=False)
    ed={'time_ms':e,'r9_side':ev.side.to_numpy(np.int8),'struct_side':s}
    for c,label in enumerate(labels):
        ed[label+'_delay_ms']=delay[:,c]; ed[label+'_pnl']=pnl[:,c]; ed[label+'_exit_ms']=ex[:,c]; ed[label+'_mfe']=mfe[:,c]; ed[label+'_mae']=mae[:,c]
    ep=f'{OUT}/pullback_events_{month:02d}.pkl.gz'; pd.DataFrame(ed).to_pickle(ep,compression='gzip')
    def sha(p):
        h=hashlib.sha256()
        with open(p,'rb') as f:
            for b in iter(lambda:f.read(1<<20),b''): h.update(b)
        return h.hexdigest()
    manifest={'month':month,'source':os.path.basename(src),'source_sha256':sha(src),'screen_sha256':sha(op),'events_sha256':sha(ep),'structural_events':int(np.sum(s!=0)),
              'mechanism':'R9 activity wake -> completed 15m/30m/60m return vote -> causal adverse pullback -> touch or causal reacceleration -> fixed .90 stop / 4.50 target / 120s max hold; modeled .20 spread; one live position at a time by entry chronology',
              'labels':labels}
    mp=f'{OUT}/pullback_manifest_{month:02d}.json'; json.dump(manifest,open(mp,'w'),indent=2)
    print(odf.head(20).to_string(index=False),flush=True)
    print(json.dumps(manifest,indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int,required=True); a=ap.parse_args(); main(a.month)
