import glob, json, time
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

@njit
def score_events(t,bid,ask,ev_ix,ev_side,sec_ids,so,sh,sl,sc,sn,cont_thr,fade_thr,strong):
    N=len(ev_ix); pp=np.empty(N,np.float64); starr=np.empty(N,np.int8); hh=np.empty(N,np.float64); m=np.zeros(N,np.uint8)
    for q in range(N):
        i=ev_ix[q]; tt=t[i]; side=ev_side[q]
        j=np.searchsorted(sec_ids,tt//1000)-1
        if j<0: continue
        aligned=(sc[j]-so[j])*side; r1=sh[j]-sl[j]; n1=sn[j]
        trade=0; st=0
        if aligned<=cont_thr and ((not strong) or r1+1e-12>=.285): trade=side; st=1
        elif aligned>=fade_thr and ((not strong) or n1>=5): trade=-side; st=-1
        if trade==0: continue
        entry=ask[i] if trade>0 else bid[i]
        stop=(bid[i]-5.0) if trade>0 else (ask[i]+5.0)
        end=tt+120000; ex=np.nan; ex_t=tt; k=i
        while k<len(t) and t[k]<=end:
            if (trade>0 and bid[k]<=stop) or (trade<0 and ask[k]>=stop):
                ex=bid[k] if trade>0 else ask[k]; ex_t=t[k]; break
            if trade>0 and bid[k]-entry>=.01:
                cand=bid[k]-.01
                if cand>stop+.005: stop=cand
            elif trade<0 and entry-ask[k]>=.01:
                cand=ask[k]+.01
                if cand<stop-.005: stop=cand
            k+=1
        if not np.isfinite(ex):
            k=np.searchsorted(t,end)
            if k>=len(t): k=len(t)-1
            ex=bid[k] if trade>0 else ask[k]; ex_t=t[k]
        pp[q]=(ex-entry)*trade; starr[q]=st; hh[q]=(ex_t-tt)/1000.; m[q]=1
    z=m==1
    return pp[z],starr[z],hh[z]

def second_bars(t,bid):
    sec=t//1000; ch=np.empty(len(sec),bool); ch[0]=True; ch[1:]=sec[1:]!=sec[:-1]
    ix=np.flatnonzero(ch); last=np.r_[ix[1:]-1,len(sec)-1]
    return sec[ix].astype(np.int64), bid[ix], np.maximum.reduceat(bid,ix), np.minimum.reduceat(bid,ix), bid[last], (last-ix+1).astype(np.int64)

def summarize(name,p,st,h):
    if len(p)==0:return {'name':name,'trades':0}
    gp=float(p[p>0].sum()); gl=float(p[p<0].sum()); eq=np.cumsum(p); pk=np.maximum.accumulate(np.r_[0.,eq]); dd=float(np.max(pk[1:]-eq))
    return {'name':name,'trades':int(len(p)),'net':float(p.sum()),'gp':gp,'gl':gl,'pf':float(gp/(-gl)) if gl<0 else None,'win':float((p>0).mean()),'dd':dd,'avg_hold':float(h.mean()),'cont':int((st==1).sum()),'fade':int((st==-1).sum())}

def main():
    t0=time.time(); files=sorted(glob.glob('/mnt/data/R9_REAL_2026-01-*_ticks.csv.gz'))
    configs=[('DOC_STRONG',-.255,.275,True),('DEF',-.290,.310,True)]
    acc={k:[] for k,_,_,_ in configs}; accst={k:[] for k,_,_,_ in configs}; acch={k:[] for k,_,_,_ in configs}
    event_total=0; dayrows=[]
    for pth in files:
        d=pd.read_csv(pth,compression='gzip',usecols=['time_msc','bid','ask','event'],dtype={'time_msc':'int64','bid':'float64','ask':'float64','event':'string'})
        t=d.time_msc.to_numpy(np.int64,copy=False); bid=d.bid.to_numpy(np.float64,copy=False); ask=d.ask.to_numpy(np.float64,copy=False)
        ev=d.event.to_numpy(dtype=str,copy=False); mask=(ev=='ENTRY_BUY')|(ev=='ENTRY_SELL')
        ev_ix=np.flatnonzero(mask).astype(np.int64); ev_side=np.where(ev[ev_ix]=='ENTRY_BUY',1,-1).astype(np.int8); event_total+=len(ev_ix)
        sec,so,sh,sl,sc,sn=second_bars(t,bid)
        rec={'day':Path(pth).name[8:18],'events':int(len(ev_ix))}
        for name,lo,hi,strong in configs:
            pnl,st,h=score_events(t,bid,ask,ev_ix,ev_side,sec,so,sh,sl,sc,sn,lo,hi,strong)
            acc[name].append(pnl); accst[name].append(st); acch[name].append(h)
            rec[name+'_trades']=int(len(pnl)); rec[name+'_net']=float(pnl.sum())
        dayrows.append(rec)
    rows=[]
    for name,_,_,_ in configs:
        p=np.concatenate(acc[name]) if acc[name] else np.array([])
        st=np.concatenate(accst[name]) if accst[name] else np.array([],np.int8)
        h=np.concatenate(acch[name]) if acch[name] else np.array([])
        rows.append(summarize(name,p,st,h))
    out={'status':'COMPLETE_FRESH_COINEXX_REAL_FIXED_ENTRY_JAN_REBUILD','source_files':len(files),'source_entry_events':event_total,'rows':rows,'elapsed_s':time.time()-t0}
    Path('/mnt/data/SA100_S1_COINEXX_REAL_FIXED_ENTRY_JAN_REBUILD02.json').write_text(json.dumps(out,indent=2))
    pd.DataFrame(dayrows).to_csv('/mnt/data/SA100_S1_COINEXX_REAL_FIXED_ENTRY_JAN_REBUILD02_DAILY.csv',index=False)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
