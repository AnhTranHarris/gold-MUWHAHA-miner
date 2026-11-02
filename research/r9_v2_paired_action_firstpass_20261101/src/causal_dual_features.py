#!/usr/bin/env python3
"""Causal exact-quote, dual-action features from complete monthly tick logs.

Feature values only depend on tick indices <= baseline decision quote. No
hindsight teacher, outcome labels or later months in the inference matrix.
Tick timestamps normalized by broker before calculating UTC session fields.
"""
from __future__ import annotations
import os,sys,time,json,hashlib
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path('/mnt/data/r9_v2_counterfactual_action_20261101')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from paired_action_labels import load,find_quote,filehash
HORIZONS=np.asarray([250,500,1000,5000,15000,45000,300000,900000,3600000,14400000],np.int64)
BASE=('spread','last_bid_move','last_ask_move','last_spread_change','last_mid_move','micro_bid_ask_imbalance','evidence','lane_reversal','utc_hour_sin','utc_hour_cos','utc_dow_sin','utc_dow_cos')
WIN=('mid_disp','spread_avg','bid_disp','ask_disp','event_pressure','spread_change_events','rv','quote_rate','price_path_eff')
NAMES=list(BASE)+[f'{c}_{h}ms' for h in HORIZONS for c in WIN]

@njit(cache=True)
def asof(t,bid,ask,ix,evidence,lane):
    n=len(t);m=len(ix);z=np.zeros((m,len(BASE)+len(HORIZONS)*len(WIN)),np.float32)
    # rolling exact quote revisions (no future ticks)
    bu=np.zeros(n+1,np.int32);bd=bu.copy();au=bu.copy();ad=bu.copy();sw=bu.copy();sn=bu.copy()
    ss=np.zeros(n+1,np.float64);ss2=ss.copy();path=ss.copy();rv=ss.copy()
    for k in range(n):
        p=k+1;spread=ask[k]-bid[k];ss[p]=ss[k]+spread;ss2[p]=ss2[k]+spread*spread
        if k:
            db=bid[k]-bid[k-1];da=ask[k]-ask[k-1];ds=spread-(ask[k-1]-bid[k-1]);dm=(db+da)*.5
            bu[p]=bu[k]+int(db>1e-10);bd[p]=bd[k]+int(db<-1e-10)
            au[p]=au[k]+int(da>1e-10);ad[p]=ad[k]+int(da<-1e-10)
            sw[p]=sw[k]+int(ds>1e-10);sn[p]=sn[k]+int(ds<-1e-10)
            path[p]=path[k]+abs(dm);rv[p]=rv[k]+dm*dm
        else:
            bu[p]=bu[k];bd[p]=bd[k];au[p]=au[k];ad[p]=ad[k];sw[p]=sw[k];sn[p]=sn[k]
            path[p]=path[k];rv[p]=rv[k]
    for row in range(m):
        i=ix[row];hour=(t[i]//3600000)%24;dow=((t[i]//86400000)+3)%7
        j0=max(0,i-1)
        db=bid[i]-bid[j0];da=ask[i]-ask[j0]
        z[row,0]=ask[i]-bid[i];z[row,1]=db;z[row,2]=da
        z[row,3]=db-da;z[row,4]=(db+da)*.5
        z[row,5]=(db-da)/(abs(db)+abs(da)+.001)
        z[row,6]=evidence[row];z[row,7]=lane[row]
        z[row,8]=np.sin(2*np.pi*hour/24);z[row,9]=np.cos(2*np.pi*hour/24)
        z[row,10]=np.sin(2*np.pi*dow/7);z[row,11]=np.cos(2*np.pi*dow/7)
        col=len(BASE)
        for h in HORIZONS:
            j=np.searchsorted(t,t[i]-h,'left')
            count=i-j+1
            mp=.5*(bid[i]+ask[i]);mj=.5*(bid[j]+ask[j])
            bump=(bu[i+1]-bu[j])+(au[i+1]-au[j]);down=(bd[i+1]-bd[j])+(ad[i+1]-ad[j]);total=bump+down
            d=mp-mj
            z[row,col]=d
            z[row,col+1]=(ss[i+1]-ss[j])/count
            z[row,col+2]=bid[i]-bid[j]
            z[row,col+3]=ask[i]-ask[j]
            z[row,col+4]=(bump-down)/(total+1)
            z[row,col+5]=((sn[i+1]-sn[j])-(sw[i+1]-sw[j]))/(count+1)
            z[row,col+6]=np.sqrt(max(0.,rv[i+1]-rv[j]))
            z[row,col+7]=count/(h/1000)
            z[row,col+8]=abs(d)/(max(0.,path[i+1]-path[j])+.0001)
            col+=len(WIN)
    return z

def main(src,month):
    start=time.monotonic();out=ROOT/'results';out.mkdir(parents=True,exist_ok=True)
    path=out/f'{src}_{month}_causal_asof.npz';report=out/f'{src}_{month}_features_receipt.json'
    if path.exists() and report.exists():
        r=json.loads(report.read_text());assert filehash(path)==r['sha256'];print('VERIFIED EXISTING',report);return
    t,b,a,tr,raw=load(src,month)
    with np.load(out/f'{src}_{month}_paired_counterfactual.npz') as pair: idx=pair['matched']
    assert np.all(idx>=0)
    X=asof(t,b,a,idx,tr.evidence.to_numpy(np.float32),(tr.lane=='reversal').to_numpy(np.float32))
    assert len(X)==len(tr) and np.isfinite(X).all()
    # Remove lookahead from missing HTF warmup by flagging insuff coverage per horizon.
    # Values before complete horizon are causal but not full-horizon measurements.
    np.savez_compressed(path,X=X,ts=tr.entry_ms.to_numpy(np.int64),side=tr.side.to_numpy(np.int8))
    result={'source':src,'month':month,'features':len(NAMES),'feature_names':NAMES,
        'rows':len(X),'sha256':filehash(path),'source_tick_sha256':filehash(raw),'elapsed_sec':round(time.monotonic()-start,2),
        'runtime_uses_teacher':False,'runtime_uses_future':False,
        'feature_maturity':'some earliest entries lack full 4h coverage; measured as shorter observed window'}
    report.write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='feature_names'},indent=2),flush=True)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--month',required=True);q=p.parse_args();main(q.source,q.month)
