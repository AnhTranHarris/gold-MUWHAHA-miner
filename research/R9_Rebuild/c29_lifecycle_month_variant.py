import argparse, hashlib, json, os, tempfile, time
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

VARIANTS={'V2_H90':(5.0,.03,.02,90000),'HIST_H120':(5.0,.05,.02,120000),'R10_H120':(5.0,.01,.01,120000)}

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def atomic_json(p,o):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=str(p.parent),prefix=p.name+'.tmp.')
    with os.fdopen(fd,'w') as f:
        json.dump(o,f,indent=2,sort_keys=True,allow_nan=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,p)

@njit(cache=True)
def sim(t,mid,idxs,sides,stopd,act,trail,maxhold):
    n=len(idxs); pnl=np.empty(n); exms=np.empty(n,np.int64); mfe=np.empty(n); mae=np.empty(n)
    for k in range(n):
        st=idxs[k]; s=sides[k]; p=mid[st]
        entry=p+.10 if s>0 else p-.10
        stop=p-.10-stopd if s>0 else p+.10+stopd
        op=t[st]; bf=0.; ba=0.; ei=st
        for i in range(st+1,len(t)):
            tt=t[i]
            if tt-op>maxhold+2000: break
            q=mid[i]; bid=q-.10; ask=q+.10
            fav=bid-entry if s>0 else entry-ask
            adv=entry-bid if s>0 else ask-entry
            if fav>bf: bf=fav
            if adv>ba: ba=adv
            if (s>0 and bid<=stop) or (s<0 and ask>=stop) or tt-op>=maxhold:
                ei=i; break
            if s>0 and bid-entry>=act:
                cand=bid-trail
                if cand>stop+.005: stop=cand
            elif s<0 and entry-ask>=act:
                cand=ask+trail
                if cand<stop-.005: stop=cand
            ei=i
        q=mid[ei]; ex=q-.10 if s>0 else q+.10
        pnl[k]=(ex-entry)*s; exms[k]=t[ei]; mfe[k]=bf; mae[k]=ba
    return pnl,exms,mfe,mae

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--month',type=int,required=True)
    ap.add_argument('--variant',choices=VARIANTS,required=True)
    ap.add_argument('--raw',required=True)
    ap.add_argument('--events',required=True)
    ap.add_argument('--out-dir',default='/mnt/data/C29_lifecycle')
    a=ap.parse_args(); t0=time.time()
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    job=f'C29_M{a.month:02d}_{a.variant}'; man=out/f'{job}.json'
    atomic_json(man,{'job_id':job,'status':'STARTED','month':a.month,'variant':a.variant})
    ev=pd.read_pickle(a.events,compression='gzip').sort_values('time_ms').reset_index(drop=True)
    d=pd.read_csv(a.raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    ask=d.ask_raw.to_numpy(np.float64)/1000.0
    bid=d.bid_raw.to_numpy(np.float64)/1000.0
    mid=(ask+bid)*0.5
    del d
    et=ev.time_ms.to_numpy(np.int64)
    idx=np.searchsorted(t,et,side='left')
    ok=(idx<len(t))&(t[np.clip(idx,0,len(t)-1)]==et)
    if not ok.all(): raise RuntimeError(f'event tick lookup failed {(~ok).sum()} rows')
    side=ev.side.to_numpy(np.int8)
    stopd,act,trail,maxhold=VARIANTS[a.variant]
    cp,ce,cm,ca=sim(t,mid,idx,side,stopd,act,trail,maxhold)
    fp,fe,fm,fa=sim(t,mid,idx,-side,stopd,act,trail,maxhold)
    control={}
    if a.variant=='V2_H90':
        dc=np.abs(cp-ev.cont_harv_pnl.to_numpy(float))
        df=np.abs(fp-ev.fade_harv_pnl.to_numpy(float))
        control={'cont_max_abs_diff':float(np.nanmax(dc)),'fade_max_abs_diff':float(np.nanmax(df)),
                 'cont_p999':float(np.nanquantile(dc,.999)),'fade_p999':float(np.nanquantile(df,.999))}
        if control['cont_max_abs_diff']>1e-9 or control['fade_max_abs_diff']>1e-9:
            raise RuntimeError(f'V2 control equivalence failed {control}')
    z=pd.DataFrame({'time_ms':et,'side':side,'cont_pnl':cp,'cont_exit_ms':ce,'cont_mfe':cm,'cont_mae':ca,
                    'fade_pnl':fp,'fade_exit_ms':fe,'fade_mfe':fm,'fade_mae':fa})
    op=out/f'{job}.pkl.gz'; tmp=Path(str(op)+'.tmp')
    z.to_pickle(tmp,compression='gzip'); os.replace(tmp,op)
    js={'job_id':job,'status':'COMPLETED_LOCAL','month':a.month,'variant':a.variant,
        'params':{'stop':stopd,'activation':act,'trail':trail,'maxhold_ms':maxhold},'rows':len(z),
        'control_equivalence':control,'raw_sha256':sha256(a.raw),'events_sha256':sha256(a.events),
        'output_sha256':sha256(op),'elapsed_seconds':time.time()-t0}
    atomic_json(man,js); print(json.dumps(js,indent=2))

if __name__=='__main__': main()
