"""Build source-exact causal R9 v2 repaired entry matrices from raw quote ticks.

Only independently reconciled paired-action FULL_CHECKPOINT archives are accepted.
The historically corrupted 250 ms action-timing teacher is not a supported input.
Features are frozen at the exact matched quote index; future paths are labels only.
"""
from __future__ import annotations
import argparse, hashlib, io, json, math, time, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from repaired_features import (
    FEATURE_VERSION, LEGACY_FEATURE_COUNT, GRID_LAGS_MS, SEGMENTS_MS,
    GEOMETRY_WINDOWS_MS, EXCITATION_TAUS_MS, GRID_NAMES, EXCITATION_NAMES,
    REPAIRED_FEATURE_NAMES, REPAIRED_FEATURE_COUNT, CONTEXT_INDICES, CONTEXT_FEATURE_COUNT,
)

GRID_LAGS=np.asarray(GRID_LAGS_MS,np.int64)
SEG_SHORT=np.asarray([GRID_LAGS_MS.index(a) for a,b in SEGMENTS_MS],np.int64)
SEG_LONG=np.asarray([GRID_LAGS_MS.index(b) for a,b in SEGMENTS_MS],np.int64)
WIN_COUNTS=np.asarray([sum(x<=h for x in GRID_LAGS_MS) for h in GEOMETRY_WINDOWS_MS],np.int64)
WINDOWS=np.asarray(GEOMETRY_WINDOWS_MS,np.int64)
TAUS=np.asarray(EXCITATION_TAUS_MS,np.float64)
A=np.zeros((6,6),np.float64)
for i in range(6):A[i,i]=.035
for x,y in ((0,2),(2,0),(1,3),(3,1),(4,5),(5,4)):A[x,y]=.025
BASELINE=.02
GRID_COUNT=len(GRID_NAMES);EXC_COUNT=len(EXCITATION_NAMES)

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

def canonical(arr,side):
    a=np.asarray(arr);s=np.asarray(side)
    return np.where((s==1)[:,None],a,a[:,::-1])

def load_checkpoint(path:Path,source:str,month:str):
    name=path.name.upper()
    if 'PAIRED_ACTION' not in name or 'FULL_CHECKPOINT' not in name or '250MS_ACTION_TIMING' in name:
        raise ValueError('only source-exact paired-action FULL_CHECKPOINT archives are accepted')
    prefix=f'results/{source}_{month}'
    with zipfile.ZipFile(path) as z:
        bad=z.testzip()
        if bad:raise ValueError(f'checkpoint CRC failure: {bad}')
        receipt=json.loads(z.read(prefix+'_paired_receipt.json'))
        with np.load(io.BytesIO(z.read(prefix+'_paired_counterfactual.npz'))) as p:
            matched=p['matched'].copy();ts=p['ts'].copy();side=p['side'].copy()
            good=canonical(p['good'].copy(),side).astype(np.uint8)
            neutral=canonical(p['neutral'].copy(),side).astype(np.uint8)
            net=canonical(p['net'].copy(),side).astype(np.float32)
        with np.load(io.BytesIO(z.read(prefix+'_causal_asof.npz'))) as c:
            X=c['X'].copy().astype(np.float32);cts=c['ts'].copy();cside=c['side'].copy()
    if X.shape!=(len(matched),LEGACY_FEATURE_COUNT):raise ValueError('legacy checkpoint feature contract mismatch')
    if not (np.array_equal(ts,cts) and np.array_equal(side,cside)):raise ValueError('paired/causal row mismatch')
    if np.any(matched<0) or np.any(matched[1:]<matched[:-1]):raise ValueError('matched source indices invalid')
    return dict(X=X,matched=matched.astype(np.int64),ts=ts,side=side,good=good,neutral=neutral,net=net,receipt=receipt)

def load_raw(path:Path,source:str,month:str):
    if source=='coinexx':
        df=pd.read_csv(path,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
        offset=(120 if month in ('01','02') else 180)*60_000
        t=df.time_msc.to_numpy(np.int64)-offset
        b=df.bid.to_numpy(np.float64);a=df.ask.to_numpy(np.float64)
    elif source=='dukascopy':
        df=pd.read_csv(path,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int64','ask_raw':'int64'})
        t=df.timestamp_ms_utc.to_numpy(np.int64)
        b=df.bid_raw.to_numpy(np.float64)/1000.;a=df.ask_raw.to_numpy(np.float64)/1000.
    else:raise ValueError(source)
    del df
    if np.any(t[1:]<t[:-1]):raise ValueError('raw source is nonchronological')
    if np.any(b<=0) or np.any(a<b):raise ValueError('invalid raw quotes')
    return t,b,a

@njit(cache=True)
def _geometry_from_samples(sm,sage,current):
    m=sm.shape[0];out=np.zeros((m,len(WINDOWS)*5),np.float32)
    for r in range(m):
        col=0
        for w in range(len(WINDOWS)):
            qn=WIN_COUNTS[w];old=qn-1
            prev=sm[r,old];hi=prev;lo=prev;age_hi=sage[r,old];age_lo=sage[r,old]
            path=0.;turns=0;nsign=0;last_sign=0
            for q in range(old-1,-1,-1):
                v=sm[r,q];d=v-prev;path+=abs(d)
                sign=1 if d>1e-12 else (-1 if d<-1e-12 else 0)
                if sign:
                    if last_sign and sign!=last_sign:turns+=1
                    last_sign=sign;nsign+=1
                if v>hi:hi=v;age_hi=sage[r,q]
                if v<lo:lo=v;age_lo=sage[r,q]
                prev=v
            v=current[r];d=v-prev;path+=abs(d)
            sign=1 if d>1e-12 else (-1 if d<-1e-12 else 0)
            if sign:
                if last_sign and sign!=last_sign:turns+=1
                nsign+=1
            if v>hi:hi=v;age_hi=0
            if v<lo:lo=v;age_lo=0
            rng=hi-lo;disp=v-sm[r,old]
            out[r,col]=disp/(path+1e-9)
            out[r,col+1]=(2*(v-lo)/(rng+1e-9)-1) if rng>1e-12 else 0.
            out[r,col+2]=(age_lo-age_hi)/max(1.,float(WINDOWS[w]))
            out[r,col+3]=turns/max(1,nsign-1)
            out[r,col+4]=rng;col+=5
    return out

def build_grid_features(t,b,a,idx):
    m=len(idx);L=len(GRID_LAGS)
    now=t[idx];cb=b[idx];ca=a[idx];cm=.5*(cb+ca);cs=ca-cb
    sb=np.empty((m,L),np.float32);sa=np.empty((m,L),np.float32);sage=np.empty((m,L),np.int64)
    for q,lag in enumerate(GRID_LAGS):
        j=np.searchsorted(t,now-lag,side='right')-1;j=np.maximum(j,0)
        sb[:,q]=b[j];sa[:,q]=a[j];sage[:,q]=now-t[j]
    sm=.5*(sb+sa);ss=sa-sb
    out=np.empty((m,GRID_COUNT),np.float32);col=0
    for q,lag in enumerate(GRID_LAGS):
        out[:,col]=cb-sb[:,q];out[:,col+1]=ca-sa[:,q];out[:,col+2]=cs-ss[:,q]
        out[:,col+3]=np.minimum(1.5,sage[:,q]/float(lag));col+=4
    for x,y in zip(SEG_SHORT,SEG_LONG):
        out[:,col]=sb[:,x]-sb[:,y];out[:,col+1]=sa[:,x]-sa[:,y]
        out[:,col+2]=ss[:,x]-ss[:,y];col+=3
    g=_geometry_from_samples(sm,sage,cm)
    out[:,col:col+g.shape[1]]=g;col+=g.shape[1]
    if col!=GRID_COUNT:raise AssertionError((col,GRID_COUNT))
    return out

def decay_table(max_ms=60_000):
    dt=np.arange(max_ms+1,dtype=np.float64)
    return np.exp(-dt[None,:]/TAUS[:,None])

@njit(cache=True)
def build_excitation_features(t,b,a,idx,decays):
    m=len(idx);out=np.zeros((m,EXC_COUNT),np.float32);state=np.zeros((len(TAUS),6),np.float64)
    maxdt=decays.shape[1]-1;row=0
    for k in range(len(t)):
        if k>0:
            dt=t[k]-t[k-1]
            for z in range(len(TAUS)):
                decay=decays[z,dt] if 0<=dt<=maxdt else math.exp(-dt/TAUS[z])
                for e in range(6):state[z,e]*=decay
            db=b[k]-b[k-1];da=a[k]-a[k-1];ds=(a[k]-b[k])-(a[k-1]-b[k-1])
            vals=(db,-db,da,-da,ds,-ds)
            for e in range(6):
                if vals[e]>1e-10:
                    for z in range(len(TAUS)):state[z,e]+=1.
        while row<m and idx[row]==k:
            col=0
            for z in range(len(TAUS)):
                bu=state[z,0];bd=state[z,1];au=state[z,2];ad=state[z,3];sw=state[z,4];sn=state[z,5]
                out[row,col]=(bu-bd)/(bu+bd+1e-9);out[row,col+1]=(au-ad)/(au+ad+1e-9)
                out[row,col+2]=(bu+au-bd-ad)/(bu+au+bd+ad+1e-9);out[row,col+3]=(sn-sw)/(sn+sw+1e-9)
                total=bu+bd+au+ad+sw+sn;out[row,col+4]=math.log1p(total if total>0 else 0.);col+=5
            weighted=np.zeros(6,np.float64)
            for e in range(6):
                for z in range(len(TAUS)):weighted[e]+=state[z,e]
                weighted[e]/=len(TAUS)
            lam=np.empty(6,np.float64)
            for i in range(6):
                v=BASELINE
                for j in range(6):v+=A[i,j]*weighted[j]
                lam[i]=v
            if a[k]-b[k]<=.01:lam[5]=0.
            up=lam[0]+lam[2];down=lam[1]+lam[3]
            out[row,col]=(up-down)/(up+down+1e-12);out[row,col+1]=(lam[5]-lam[4])/(lam[5]+lam[4]+1e-12)
            total_l=0.
            for e in range(6):total_l+=lam[e]
            ent=0.
            for e in range(6):
                p=lam[e]/(total_l+1e-12)
                if p>0:ent-=p*math.log(p+1e-12)
            out[row,col+2]=ent;row+=1
    return out,row

def main(args):
    import gc
    t0=time.monotonic();paired=Path(args.paired);raw=Path(args.raw);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    d=load_checkpoint(paired,args.source,args.month);print('checkpoint',round(time.monotonic()-t0,2),flush=True)
    raw_hash=sha256(raw);expected=d['receipt']['source_tick_sha256']
    if raw_hash!=expected:raise ValueError(f'raw SHA mismatch {raw_hash} != {expected}')
    t,b,a=load_raw(raw,args.source,args.month);gc.collect();print('raw',len(t),round(time.monotonic()-t0,2),flush=True)
    if len(t)!=int(d['receipt']['ticks']):raise ValueError('raw tick count mismatch')
    if int(d['matched'][-1])>=len(t) or not np.array_equal(t[d['matched']],d['ts']):raise ValueError('matched source mismatch')

    rows=len(d['ts']);dest=out/f'{args.source}_{args.month}_repaired_X.npy'
    mm=np.lib.format.open_memmap(dest,mode='w+',dtype=np.float32,shape=(rows,REPAIRED_FEATURE_COUNT))
    c=0
    context=d['X'][:,np.asarray(CONTEXT_INDICES,dtype=np.int64)]
    mm[:,c:c+CONTEXT_FEATURE_COUNT]=context;c+=CONTEXT_FEATURE_COUNT
    del context;del d['X'];gc.collect()

    chunk=max(1000,int(args.chunk_rows))
    for lo in range(0,rows,chunk):
        hi=min(rows,lo+chunk)
        grid=build_grid_features(t,b,a,d['matched'][lo:hi])
        mm[lo:hi,c:c+grid.shape[1]]=grid
        del grid
        if lo==0 or hi==rows or (lo//chunk)%4==3:
            print('grid',hi,'/',rows,round(time.monotonic()-t0,2),flush=True)
    c+=len(GRID_NAMES);gc.collect()

    exc,hit=build_excitation_features(t,b,a,d['matched'],decay_table())
    if hit!=rows:raise ValueError(f'excitation matched only {hit}/{rows}')
    mm[:,c:c+exc.shape[1]]=exc;c+=exc.shape[1];del exc;gc.collect()
    print('exc',hit,round(time.monotonic()-t0,2),flush=True)
    if c!=REPAIRED_FEATURE_COUNT:raise ValueError('repaired feature column count mismatch')
    for lo in range(0,rows,chunk):
        if not np.isfinite(mm[lo:min(rows,lo+chunk)]).all():raise ValueError('nonfinite repaired feature')
    mm.flush();del mm

    labels=out/f'{args.source}_{args.month}_repaired_labels.npz'
    np.savez(labels,ts=d['ts'],side=d['side'],good=d['good'],neutral=d['neutral'],net=d['net'],matched=d['matched'])
    print('saved',dest,labels,round(time.monotonic()-t0,2),flush=True)
    receipt=dict(source=args.source,month=args.month,feature_version=FEATURE_VERSION,rows=rows,features=REPAIRED_FEATURE_COUNT,
                 raw_tick_sha256=raw_hash,paired_checkpoint_sha256=sha256(paired),feature_matrix_sha256=sha256(dest),labels_sha256=sha256(labels),
                 exact_matched_timestamp_rows=int(rows),legacy_features_available=LEGACY_FEATURE_COUNT,context_features=CONTEXT_FEATURE_COUNT,
                 ordered_grid_features=len(GRID_NAMES),quote_excitation_features=len(EXCITATION_NAMES),
                 feature_names=list(REPAIRED_FEATURE_NAMES),teacher_provenance='source-exact paired-action FULL_CHECKPOINT only',
                 historical_250ms_sell_bug_teacher_used=False,runtime_uses_future=False,status='REPAIRED_FEATURE_MATRIX_NOT_POLICY',
                 elapsed_sec=round(time.monotonic()-t0,2))
    (out/f'{args.source}_{args.month}_repaired_features_receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({k:v for k,v in receipt.items() if k!='feature_names'},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',choices=('coinexx','dukascopy'),required=True);p.add_argument('--month',required=True)
    p.add_argument('--paired',required=True);p.add_argument('--raw',required=True);p.add_argument('--out',required=True);p.add_argument('--chunk-rows',type=int,default=25000)
    main(p.parse_args())
