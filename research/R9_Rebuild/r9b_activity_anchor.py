import numpy as np, json, time, sys
from pathlib import Path
from numba import njit
sys.path.insert(0,'/mnt/data')
import r9b_screen as R
ROOT=Path('/mnt/data/R9B_FAST_CACHE')
H=.10

@njit(cache=True)
def gen_signals(t,mid,sec_ids,s1_disp,s1_eff,s1_rng,s1_turns,atrsec,N,gap,effmin,rngmin,turnmax):
    maxs=max(10000,len(t)//max(N,1))
    sig=np.empty(maxs,np.int64); side=np.empty(maxs,np.int8); ns=0
    k=N
    while k < len(t):
        ref=mid[k-1]
        upper=ref+gap; lower=ref-gap
        end=min(k+N,len(t))
        for i in range(k,end):
            p=mid[i]; ask=p+H; bid=p-H
            s=0
            if ask>=upper: s=1
            elif bid<=lower: s=-1
            if s==0: continue
            sec=t[i]//1000
            j=np.searchsorted(sec_ids,sec)
            if j>=len(sec_ids) or sec_ids[j]!=sec or j<10: continue
            av=atrsec[j]
            if not np.isfinite(av): continue
            ss=R.session_for_sec(sec_ids[j]); floor=2.5
            if ss==1: floor=2.0
            elif ss==2 or ss==3: floor=1.75
            if av+1e-12<floor: continue
            dd=s1_disp[j]; ee=s1_eff[j]; rr=s1_rng[j]; tr=s1_turns[j]
            if ee<effmin or rr<rngmin or tr>turnmax: continue
            if s>0 and dd<gap: continue
            if s<0 and dd>-gap: continue
            if ns<maxs:
                sig[ns]=t[i]; side[ns]=s; ns+=1
            break
        k += N
    return sig[:ns],side[:ns]

@njit(cache=True)
def replay(t,mid,sig,side,stopd,act,trail,maxhold_ms):
    n=len(sig); out=np.empty((n,5),np.float64)
    for k in range(n):
        i=np.searchsorted(t,sig[k])
        if i>=len(t): out[k]=np.nan; continue
        p=mid[i]; entry=p+H if side[k]>0 else p-H; bid=p-H; ask=p+H
        stop=bid-stopd if side[k]>0 else ask+stopd; ot=t[i]; mfe=0.;mae=0.;ended=False
        for j in range(i+1,len(t)):
            tt=t[j]; p=mid[j];bid=p-H;ask=p+H
            fav=(bid-entry) if side[k]>0 else (entry-ask); adv=(entry-bid) if side[k]>0 else (ask-entry)
            if fav>mfe:mfe=fav
            if adv>mae:mae=adv
            if (side[k]>0 and bid<=stop) or (side[k]<0 and ask>=stop) or tt-ot>=maxhold_ms:
                ex=bid if side[k]>0 else ask
                out[k,0]=(ex-entry)*side[k];out[k,1]=(tt-ot)/1000.;out[k,2]=mfe;out[k,3]=mae;out[k,4]=tt;ended=True;break
            if fav>=act:
                cand=bid-trail if side[k]>0 else ask+trail
                if side[k]>0:
                    if cand>stop:stop=cand
                else:
                    if cand<stop:stop=cand
        if not ended:
            p=mid[-1];bid=p-H;ask=p+H;ex=bid if side[k]>0 else ask
            out[k,0]=(ex-entry)*side[k];out[k,1]=(t[-1]-ot)/1000.;out[k,2]=mfe;out[k,3]=mae;out[k,4]=t[-1]
    return out

@njit(cache=True)
def nonoverlap(sig,out):
    ix=np.argsort(sig); keep=np.empty(len(ix),np.int64);n=0;free=-1
    for q in ix:
        if sig[q]<=free or not np.isfinite(out[q,0]):continue
        keep[n]=q;n+=1;free=int(out[q,4])
    return keep[:n]

def met(v,h):
    v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum());eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[:-1] if len(v) else np.array([])
    return {'trades':int(len(v)),'net':float(v.sum()),'gp':gp,'gl':gl,'pf':float(gp/-gl) if gl<0 else 999.,'win':float((v>0).mean()) if len(v) else 0.,'maxdd':float((pk-eq).max()) if len(v) else 0.,'avg_hold':float(np.mean(h)) if len(h) else 0.}

def run_month(m, cfgs):
    t,mid,sec_ids,sd,se,sr,st,atr,*_=R.load_build(m)
    rows=[]
    lifes=[('R9',.30,.10,.03,30000),('H60',.60,.10,.05,60000),('HARV',.60,.06,.03,45000)]
    for N,gap,eff,rng,trn in cfgs:
        sig,side=gen_signals(t,mid,sec_ids,sd,se,sr,st,atr,N,gap,eff,rng,trn)
        for ln,stop,act,trail,mh in lifes:
            o=replay(t,mid,sig,side,stop,act,trail,mh); ix=nonoverlap(sig,o); mm=met(o[ix,0],o[ix,1])
            rows.append({'month':m,'N':N,'gap':gap,'eff':eff,'rng':rng,'turns':trn,'life':ln,'raw_signals':int(len(sig)),**mm})
    return rows
