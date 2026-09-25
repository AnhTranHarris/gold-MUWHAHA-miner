import os,glob,argparse,hashlib
import numpy as np,pandas as pd
from numba import njit

DATA='/mnt/data'; EVROOT='/mnt/data/r9_research_v2'; OUT='/mnt/data/r9_research_v2/mature_pullback_v2'
os.makedirs(OUT,exist_ok=True)
PB=np.array([.30,.50,.80,1.00,1.20,1.50],np.float64)
RC=np.array([.10,.20,.30,.50],np.float64)
HORIZ=np.array([15,30,60,120],np.int64)

@njit(cache=True)
def build_mature(t,mid,eix,edir,pb,rc,maxpbms,maxrcms):
    nE=len(eix); npb=len(pb); nrc=len(rc)
    pbt=np.full((nE,npb),-1,np.int64)
    enti=np.full((nE,npb,nrc),-1,np.int64)
    for z in range(nE):
        si=eix[z]; sd=edir[z]
        if sd==0: continue
        st=t[si]; ext=mid[si]
        trig=np.zeros(npb,np.uint8); pbext=np.empty(npb,np.float64); pbtick=np.full(npb,-1,np.int64)
        i=si+1
        hard_end=st+maxpbms+maxrcms
        while i<len(t) and t[i]<=hard_end:
            m=mid[i]; dt=t[i]-st
            if sd>0:
                if m>ext: ext=m
                if dt<=maxpbms:
                    for a in range(npb):
                        if trig[a]==0 and ext-m>=pb[a]:
                            trig[a]=1; pbt[z,a]=dt; pbtick[a]=t[i]; pbext[a]=m
                for a in range(npb):
                    if trig[a]==1:
                        if m<pbext[a]: pbext[a]=m
                        if t[i]-pbtick[a] <= maxrcms:
                            for b in range(nrc):
                                if enti[z,a,b]<0 and m-pbext[a]>=rc[b]: enti[z,a,b]=i
            else:
                if m<ext: ext=m
                if dt<=maxpbms:
                    for a in range(npb):
                        if trig[a]==0 and m-ext>=pb[a]:
                            trig[a]=1; pbt[z,a]=dt; pbtick[a]=t[i]; pbext[a]=m
                for a in range(npb):
                    if trig[a]==1:
                        if m>pbext[a]: pbext[a]=m
                        if t[i]-pbtick[a] <= maxrcms:
                            for b in range(nrc):
                                if enti[z,a,b]<0 and pbext[a]-m>=rc[b]: enti[z,a,b]=i
            if dt>maxpbms:
                done=True
                for a in range(npb):
                    if trig[a]==0: continue
                    for b in range(nrc):
                        if enti[z,a,b]<0 and t[i]-pbtick[a]<=maxrcms: done=False
                if done: break
            i+=1
    return pbt,enti

@njit(cache=True)
def horizon_pnl(t,mid,enti,edir,horiz):
    nE,npb,nrc=enti.shape; nh=len(horiz)
    out=np.full((nE,npb,nrc,nh),np.nan,np.float64)
    for z in range(nE):
      sd=edir[z]
      for a in range(npb):
       for b in range(nrc):
        j=enti[z,a,b]
        if j<0: continue
        ent=mid[j]
        for h in range(nh):
            target=t[j]+horiz[h]*1000
            k=np.searchsorted(t,target)
            if k>=len(t): k=len(t)-1
            out[z,a,b,h]=sd*(mid[k]-ent)-0.20
    return out

def load_ticks(m):
    p=glob.glob(f'{DATA}/XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz')[0]
    d=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64); mid=(d.ask_raw.to_numpy(np.float64)+d.bid_raw.to_numpy(np.float64))/2000.
    return t,mid

def struct_state(ev):
    side=ev.side.to_numpy(float); cols=['tf300_retatr','tf600_retatr','tf1200_retatr','tf3600_retatr']
    A=np.vstack([ev[c].to_numpy(float)*side for c in cols]).T
    S=np.sign(np.nan_to_num(A,nan=0.0)); pos=(S>0).sum(1);neg=(S<0).sum(1)
    direction=np.where(pos>neg,1,np.where(neg>pos,-1,0)).astype(np.int8); votes=np.maximum(pos,neg).astype(np.int8)
    strength=np.nanmean(A*direction[:,None],axis=1)
    return direction,votes,strength

def run(m):
    ev=pd.read_pickle(f'{EVROOT}/events_{m:02d}.pkl.gz',compression='gzip'); t,mid=load_ticks(m)
    direction,votes,strength=struct_state(ev); eix=np.searchsorted(t,ev.time_ms.to_numpy(np.int64)); eix=np.clip(eix,0,len(t)-1).astype(np.int64)
    pbt,enti=build_mature(t,mid,eix,direction,PB,RC,240000,120000); pnl=horizon_pnl(t,mid,enti,direction,HORIZ)
    rows=[]
    for z in range(len(ev)):
      if direction[z]==0: continue
      for a,pb in enumerate(PB):
       if pbt[z,a]<0: continue
       for b,rc in enumerate(RC):
        j=enti[z,a,b]
        if j<0: continue
        recdelay=int(t[j]-(t[eix[z]]+pbt[z,a]))
        rows.append((m,z,int(ev.time_ms.iloc[z]),int(t[j]),int(direction[z]),int(votes[z]),float(strength[z]),float(pb),float(rc),int(pbt[z,a]),recdelay,*[float(x) for x in pnl[z,a,b,:]]))
    cols=['month','event_id','event_time','entry_time','dir','votes','strength','pb','rc','pb_delay_ms','rc_delay_ms']+[f'pnl_{h}s' for h in HORIZ]
    o=pd.DataFrame(rows,columns=cols);path=f'{OUT}/mature_{m:02d}.pkl.gz';o.to_pickle(path,compression='gzip')
    print('DONE',m,'base_events',len(ev),'mature_rows',len(o),'unique_events',o.event_id.nunique(),'path',path,flush=True)
    print(o.groupby(['pb','rc']).agg(trades=('event_id','size'),net30=('pnl_30s','sum'),mean30=('pnl_30s','mean')).sort_values('net30',ascending=False).head(20).to_string(),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--month',type=int,required=True);a=ap.parse_args();run(a.month)
