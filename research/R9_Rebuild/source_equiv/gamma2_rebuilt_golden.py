import sys,json,time
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,'/mnt/data')
import r9b_screen as R
import r9b_r8_recert as B
import r8_sweep_lifecycle_screen as S
H=.10
TARGET={1:{'trades':30943,'winners':25368,'net':5131.0509999771375,'gl':-6091.20650000407}}

@njit(cache=True)
def replay_hybrid(t,mid,X):
    n=len(X);o=np.empty((n,6),np.float64)
    for k in range(n):
        for z in range(6):o[k,z]=np.nan
        sig=int(X[k,0]);side=int(X[k,1]);align=X[k,3]
        if align>=3:stopd=1.;act=.10;trail=.04;maxhold=60;mode=1
        else:stopd=3.;act=.18;trail=.05;maxhold=60;mode=0
        i=np.searchsorted(t,sig)
        if i>=len(t):continue
        p=mid[i];entry=p+H if side>0 else p-H;bid=p-H;ask=p+H
        stop=bid-stopd if side>0 else ask+stopd;ot=t[i];mfe=0.;mae=0.
        for j in range(i+1,len(t)):
            tt=t[j];p=mid[j];bid=p-H;ask=p+H
            fav=bid-entry if side>0 else entry-ask;adv=entry-bid if side>0 else ask-entry
            if fav>mfe:mfe=fav
            if adv>mae:mae=adv
            if (side>0 and bid<=stop) or (side<0 and ask>=stop) or tt-ot>=maxhold*1000:
                ex=bid if side>0 else ask
                o[k,0]=(ex-entry)*side;o[k,1]=(tt-ot)/1000.;o[k,2]=mfe;o[k,3]=mae;o[k,4]=tt;o[k,5]=mode;break
            if fav>=act:
                cand=bid-trail if side>0 else ask+trail
                if side>0:
                    if cand>stop:stop=cand
                else:
                    if cand<stop:stop=cand
    return o

@njit(cache=True)
def nonoverlap(X,O):
    ix=np.argsort(X[:,0]);keep=np.empty(len(ix),np.int64);n=0;free=-1
    for q in ix:
        if X[q,0]<=free or not np.isfinite(O[q,0]):continue
        keep[n]=q;n+=1;free=int(O[q,4])
    return keep[:n]

def metrics(v):
    v=np.asarray(v,float);gp=float(v[v>0].sum());gl=float(v[v<0].sum())
    eq=np.cumsum(v);pk=np.maximum.accumulate(np.r_[0.,eq])[:-1] if len(v) else np.array([])
    return {'trades':int(len(v)),'winners':int((v>0).sum()),'win_rate':float((v>0).mean()) if len(v) else 0.,'net':float(v.sum()),'gross_profit':gp,'gross_loss':gl,'profit_factor':gp/-gl if gl<0 else 999.,'max_drawdown':float((pk-eq).max()) if len(v) else 0.}

def run(month=1,compat=None):
    t0=time.time();data=R.load_build(month);t,mid,sec=data[:3];atr=data[7];al=data[8];ash=data[9]
    su,hi,lo,cl=B.build_sec(t,mid)
    if compat is None:
        X=S.sweep_signals(t,mid,su,hi,lo,cl,sec,atr,al,ash);mode='causal'
    else:
        X=S.sweep_signals_legacy_compat(t,mid,su,hi,lo,cl,sec,atr,al,ash,**compat);mode='legacy_compat'
    O=replay_hybrid(t,mid,X);ix=nonoverlap(X,O);m=metrics(O[ix,0]);m['raw_signals']=int(len(X));m['mode']=mode;m['compat']=compat;m['elapsed']=time.time()-t0
    if month in TARGET:
        tar=TARGET[month];m['delta']={k:m[k]-tar[k] for k in ('trades','winners','net')};m['delta']['gross_loss']=m['gross_loss']-tar['gl']
    return m

if __name__=='__main__':
    out=run(1);Path('/mnt/data/GAMMA2_REBUILT_GOLDEN_CAUSAL_JAN.json').write_text(json.dumps(out,indent=2,sort_keys=True));print(json.dumps(out,indent=2,sort_keys=True))
