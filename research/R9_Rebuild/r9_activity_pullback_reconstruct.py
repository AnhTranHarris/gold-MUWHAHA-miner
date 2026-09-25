import argparse, glob, json, os, hashlib, sys
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
sys.path.insert(0,'/mnt/data')
import r9_research_v2 as v2

DATA_DIR='/mnt/data'; OUT=Path('/mnt/data/r9_research_v2/activity_pullback'); OUT.mkdir(parents=True,exist_ok=True)

@njit
def session_for_sec(sec):
    lon_off=60 if (sec>=1774746000 and sec<1792890000) else 0
    ny_off=-240 if (sec>=1772953200 and sec<1793512800) else -300
    lm=((sec+lon_off*60)%86400)//60; nm=((sec+ny_off*60)%86400)//60
    l=(lm>=480 and lm<990); n=(nm>=480 and nm<1020)
    if l and n: return 2
    if l: return 1
    if n: return 3
    return 0

@njit
def structural_vote(event_ms, ends15,r15, ends30,r30, ends60,r60):
    n=len(event_ms); out=np.zeros(n,np.int8)
    for k in range(n):
        sec=event_ms[k]//1000; pos=0; neg=0
        for ends,rr in ((ends15,r15),(ends30,r30),(ends60,r60)):
            j=np.searchsorted(ends,sec,side='right')-1
            if j>=0 and np.isfinite(rr[j]):
                if rr[j]>0: pos+=1
                elif rr[j]<0: neg+=1
        if pos>=2: out[k]=1
        elif neg>=2: out[k]=-1
    return out

@njit
def tf_ret(t,mid,tfsec):
    bucket=t//(tfsec*1000); n=len(t); ids=np.empty(n//10+10000,np.int64); c=np.empty(n//10+10000,np.float64); ends=np.empty(n//10+10000,np.int64)
    k=-1; last=-1
    for i in range(n):
        b=bucket[i]
        if b!=last: k+=1; ids[k]=b; last=b
        c[k]=mid[i]; ends[k]=(b+1)*tfsec
    k+=1; r=np.empty(k,np.float64); r[0]=np.nan
    for i in range(1,k): r[i]=c[i]-c[i-1]
    return ends[:k],r[:k]

@njit
def extract_entries(t,mid,event_ms,struct_side,depth,reacc,max_window_ms):
    n=len(event_ms); touch=np.full(n,-1,np.int64); rec=np.full(n,-1,np.int64); touch_delay=np.full(n,-1,np.int64); rec_delay=np.full(n,-1,np.int64)
    idx0=np.searchsorted(t,event_ms)
    for k in range(n):
        s=struct_side[k]
        if s==0: continue
        i0=idx0[k]
        if i0>=len(t): continue
        p0=mid[i0]; ext=p0; hit=False; endt=event_ms[k]+max_window_ms
        for i in range(i0+1,len(t)):
            if t[i]>endt: break
            p=mid[i]
            if not hit:
                if s*(p-p0)<=-depth:
                    hit=True; ext=p; touch[k]=i; touch_delay[k]=t[i]-event_ms[k]
            else:
                if s*(p-ext)<0: ext=p
                if rec[k]<0 and s*(p-ext)>=reacc:
                    rec[k]=i; rec_delay[k]=t[i]-event_ms[k]; break
    return touch,touch_delay,rec,rec_delay

@njit
def simulate(t,mid,entry_idx,side,stop,target,max_hold_ms):
    n=len(entry_idx); pnl=np.full(n,np.nan); exms=np.full(n,-1,np.int64); hold=np.full(n,np.nan)
    for k in range(n):
        i0=entry_idx[k]; s=side[k]
        if i0<0 or s==0: continue
        p=mid[i0]; entry=p+.10 if s>0 else p-.10; sl=entry-stop if s>0 else entry+stop; ex=entry; ei=i0; opent=t[i0]
        for i in range(i0+1,len(t)):
            tt=t[i]; p=mid[i]; bid=p-.10; ask=p+.10
            if (s>0 and bid<=sl) or (s<0 and ask>=sl): ex=bid if s>0 else ask; ei=i; break
            if (s>0 and bid>=entry+target) or (s<0 and ask<=entry-target): ex=bid if s>0 else ask; ei=i; break
            if tt-opent>=max_hold_ms: ex=bid if s>0 else ask; ei=i; break
        pnl[k]=(ex-entry)*s; exms[k]=t[ei]; hold[k]=(t[ei]-opent)/1000.
    return pnl,exms,hold

def select_seq(event_ms,delay,exms,pnl,limit_ms):
    ok=np.isfinite(pnl)&(delay>=0)&(delay<=limit_ms)&(exms>0); ids=np.where(ok)[0]; ent=event_ms[ids]+delay[ids]; ids=ids[np.argsort(ent,kind='stable')]
    ch=[]; last=-1
    for k in ids:
        et=event_ms[k]+delay[k]
        if et<=last: continue
        ch.append(k); last=int(exms[k])
    ch=np.asarray(ch,dtype=int); x=pnl[ch]; gp=x[x>0].sum(); gl=x[x<0].sum()
    return dict(trades=len(ch),net=float(x.sum()),gp=float(gp),gl=float(gl),pf=float(gp/(-gl)) if gl<0 else np.inf,win=float((x>0).mean()) if len(x) else np.nan,avg_hold=np.nan)

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def main(month):
    f=glob.glob(f'{DATA_DIR}/XAUUSD_DUKAS_2026_{month:02d}_ticks.csv*.gz')[0]
    d=pd.read_csv(f,compression='gzip',dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64','ask_volume':'float64','bid_volume':'float64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64); ask=d.ask_raw.to_numpy(float)/1000.; bid=d.bid_raw.to_numpy(float)/1000.; mid=(ask+bid)/2.; av=d.ask_volume.to_numpy(float); bv=d.bid_volume.to_numpy(float)
    sec,o,h,l,c,n,am,bm=v2.aggregate_active_seconds(t,mid,av,bv); disp,eff,rng,turns,tickratio,volimb=v2.build_s1(sec,o,h,l,c,n,am,bm); atr,_=v2.build_m5_atr_by_sec(sec,t,mid)
    qual=np.zeros(len(sec),bool)
    for i in range(len(sec)):
        if i<10 or not np.isfinite(atr[i]): continue
        ss=session_for_sec(sec[i]); floor=2.5
        if ss==1: floor=2.0
        elif ss in (2,3): floor=1.75
        if atr[i]+1e-12<floor: continue
        if eff[i]>=.70 and rng[i]>=.50 and turns[i]<=9 and abs(disp[i])>=.15: qual[i]=True
    defs={}
    burst=np.zeros(len(sec),bool)
    for i in range(len(sec)):
        if qual[i] and (i==0 or (not qual[i-1]) or sec[i]-sec[i-1]>1): burst[i]=True
    defs['burst']=np.where(burst)[0]
    idx=np.where(qual)[0]; seen=set(); mins=[]
    for i in idx:
        m=int(sec[i]//60)
        if m not in seen: seen.add(m); mins.append(i)
    defs['minute_first']=np.asarray(mins,dtype=int)
    ends15,r15=tf_ret(t,mid,900); ends30,r30=tf_ret(t,mid,1800); ends60,r60=tf_ret(t,mid,3600)
    rows=[]; detail={}
    for name,ii in defs.items():
        ems=sec[ii]*1000+999
        s=structural_vote(ems,ends15,r15,ends30,r30,ends60,r60)
        for depth in [1.20,1.35,1.50]:
          for reacc in [.35,.50]:
            touch,td,rec,rd=extract_entries(t,mid,ems,s,depth,reacc,240000)
            for mode,eidx,delay in [('touch',touch,td),('reacc',rec,rd)]:
              for stop,target in [(.9,4.5),(1.0,6.0)]:
                pnl,ex,hold=simulate(t,mid,eidx,s,stop,target,120000)
                for window in [120000,180000,240000]:
                    z=select_seq(ems,delay,ex,pnl,window)
                    ok=np.isfinite(pnl)&(delay>=0)&(delay<=window)&(ex>0); ids=np.where(ok)[0]; ent=ems[ids]+delay[ids]; ids=ids[np.argsort(ent,kind='stable')]; ch=[]; last=-1
                    for k in ids:
                        et=ems[k]+delay[k]
                        if et<=last: continue
                        ch.append(k); last=int(ex[k])
                    ch=np.asarray(ch,dtype=int); z['avg_hold']=float(np.nanmean(hold[ch])) if len(ch) else np.nan
                    z.update(month=month,wake=name,wakes=len(ii),struct_wakes=int(np.sum(s!=0)),depth=depth,reacc=reacc,entry_mode=mode,stop=stop,target=target,window_sec=window//1000)
                    rows.append(z)
        detail[name]=dict(wakes=int(len(ii)),qualified_seconds=int(qual.sum()),struct_wakes=int(np.sum(s!=0)))
    out=pd.DataFrame(rows).sort_values(['net','pf'],ascending=[False,False]); op=OUT/f'activity_pullback_screen_{month:02d}.csv'; out.to_csv(op,index=False)
    mp=OUT/f'activity_pullback_manifest_{month:02d}.json'; json.dump({'month':month,'source':os.path.basename(f),'source_sha256':sha(f),'screen_sha256':sha(op),'definitions':detail,'mechanism':'completed R9 S1 quality/activity gate -> causal burst-start or first-qualified-second-per-minute wake -> completed 15m/30m/60m structural return vote -> adverse pullback -> touch/reacceleration -> fixed targets; decision timestamp after completed second'},open(mp,'w'),indent=2)
    print(out.head(30).to_string(index=False),flush=True); print(json.dumps(json.load(open(mp)),indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--month',type=int,required=True); a=ap.parse_args(); main(a.month)
