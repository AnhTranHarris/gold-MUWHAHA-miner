#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
import joblib

UNIT='BETA_066_NONLINEAR_DELAYED_ACTION_WAIT_SHORT_30S'
SOURCE_SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
BETA065_PROPOSAL_SHA='600e3b73d7d053f6ed0785a5dd68aadad72f1e8928054a61b3eb1b2840be8773'
FEE=0.02
HOLD_MS=30_000
DELAYS=np.array([0,250,1000,3000],dtype=np.int64)
ACTION_NAMES=np.array([
    'LONG_NOW','SHORT_NOW','WAIT_250MS_THEN_LONG','WAIT_250MS_THEN_SHORT',
    'WAIT_1S_THEN_LONG','WAIT_1S_THEN_SHORT','WAIT_3S_THEN_LONG','WAIT_3S_THEN_SHORT'
])
Q_THRESHOLDS=[0.0,0.05,0.10,0.15]
MIN_CAL_TRADES=100

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''):h.update(b)
    return h.hexdigest()

def load_source_window(path:Path, end_ms:int):
    tt=[];aa=[];bb=[];problems=[];prev=None
    for df in pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                          dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'},chunksize=750_000):
        t=df.timestamp_ms_utc.to_numpy(np.int64,copy=False)
        if not len(t):continue
        if t[0] > end_ms:break
        m=t<=end_ms
        if not m.any():continue
        t=t[m]; a=df.ask_raw.to_numpy(np.int64,copy=False)[m]; b=df.bid_raw.to_numpy(np.int64,copy=False)[m]
        if prev is not None and t[0]<prev:problems.append('cross_chunk_timestamp_descend')
        if np.any(np.diff(t)<0):problems.append('timestamp_descend')
        if np.any(a<b):problems.append('crossed_quote')
        prev=int(t[-1]);tt.append(t.copy());aa.append(a.copy());bb.append(b.copy())
        if int(t[-1])>=end_ms:break
    if not tt:raise RuntimeError('no source rows')
    return np.concatenate(tt),np.concatenate(aa),np.concatenate(bb),sorted(set(problems))

def build_labels(event_ms,t,a,b):
    n=len(event_ms); nact=8
    labels=np.full((n,nact),np.nan,np.float32)
    entry_idx=np.full((n,nact),-1,np.int32); exit_idx=np.full((n,nact),-1,np.int32)
    for di,delay in enumerate(DELAYS):
        ei=np.searchsorted(t,event_ms+delay,side='left')
        valid=ei<len(t)
        ei_safe=np.minimum(ei,len(t)-1)
        target=t[ei_safe]+HOLD_MS
        xi=np.searchsorted(t,target,side='left')
        valid &= xi<len(t)
        xi_safe=np.minimum(xi,len(t)-1)
        ask_e=a[ei_safe].astype(np.float64)*.001; bid_e=b[ei_safe].astype(np.float64)*.001
        ask_x=a[xi_safe].astype(np.float64)*.001; bid_x=b[xi_safe].astype(np.float64)*.001
        long=(bid_x-ask_e)-FEE
        short=(bid_e-ask_x)-FEE
        j=2*di
        labels[valid,j]=long[valid].astype(np.float32);labels[valid,j+1]=short[valid].astype(np.float32)
        entry_idx[valid,j]=ei[valid].astype(np.int32);entry_idx[valid,j+1]=ei[valid].astype(np.int32)
        exit_idx[valid,j]=xi[valid].astype(np.int32);exit_idx[valid,j+1]=xi[valid].astype(np.int32)
    return labels,entry_idx,exit_idx

def metrics(pnls):
    p=np.asarray(pnls,dtype=np.float64)
    if not len(p):return {'trades':0,'wins':0,'win_rate':0.0,'net':0.0,'gp':0.0,'gl':0.0,'pf':0.0,'avg':0.0,'max_dd':0.0}
    gp=float(p[p>0].sum()) if np.any(p>0) else 0.0
    gl=float(p[p<=0].sum()) if np.any(p<=0) else 0.0
    eq=np.cumsum(p);peak=np.maximum.accumulate(np.r_[0.,eq]);dd=peak[1:]-eq
    return {'trades':int(len(p)),'wins':int((p>0).sum()),'win_rate':float((p>0).mean()),'net':float(p.sum()),
            'gp':gp,'gl':gl,'pf':float(gp/abs(gl)) if gl<0 else (float('inf') if gp>0 else 0.0),
            'avg':float(p.mean()),'max_dd':float(dd.max()) if len(dd) else 0.0}

def replay(indices,event_ms,source_ord,pred,labels,entry_idx,exit_idx,threshold,collect=False):
    order=indices[np.lexsort((source_ord[indices],event_ms[indices]))]
    busy_until=-1; pnls=[]; rows=[]
    for i in order:
        if int(source_ord[i])<=busy_until:continue
        q=pred[i]
        if not np.isfinite(q).all():continue
        act=int(np.argmax(q)); qbest=float(q[act])
        if qbest<=threshold:continue
        ei=int(entry_idx[i,act]); xi=int(exit_idx[i,act]); pnl=float(labels[i,act])
        if ei<0 or xi<0 or not math.isfinite(pnl):continue
        busy_until=xi;pnls.append(pnl)
        if collect:
            rows.append((int(i),int(event_ms[i]),int(source_ord[i]),ACTION_NAMES[act],qbest,pnl,ei,xi))
    return metrics(pnls),rows

def make_model(name):
    if name=='HGB_D3_L2_5':
        base=HistGradientBoostingRegressor(max_iter=80,max_leaf_nodes=7,l2_regularization=5.0,
            learning_rate=0.06,min_samples_leaf=200,random_state=6601)
        return MultiOutputRegressor(base,n_jobs=-1)
    if name=='HGB_D4_L2_10':
        base=HistGradientBoostingRegressor(max_iter=100,max_leaf_nodes=15,l2_regularization=10.0,
            learning_rate=0.05,min_samples_leaf=250,random_state=6602)
        return MultiOutputRegressor(base,n_jobs=-1)
    if name=='EXTRA_D8_L150':
        return ExtraTreesRegressor(n_estimators=96,max_depth=8,min_samples_leaf=150,max_features=.75,
            n_jobs=-1,random_state=6603)
    raise KeyError(name)

def finite_rows(X,Y,mask):
    return mask & np.isfinite(X).all(axis=1) & np.isfinite(Y).all(axis=1)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--proposals',required=True);ap.add_argument('--source',required=True);ap.add_argument('--out-dir',required=True)
    args=ap.parse_args();out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True);start=time.time()
    prop=Path(args.proposals);src=Path(args.source)
    if sha256_file(prop)!=BETA065_PROPOSAL_SHA:raise RuntimeError('BETA065 proposal SHA mismatch')
    if sha256_file(src)!=SOURCE_SHA:raise RuntimeError('source SHA mismatch')
    z=np.load(prop,allow_pickle=True)
    event_ms=z['event_time_ms'];source_ord=z['source_ordinal'];X=z['features'].astype(np.float32);split=z['split_code'];
    feature_names=z['feature_names'];specialist_code=z['specialist_code'];specialist_names=z['specialist_names']
    if len(event_ms)!=371013:raise RuntimeError('proposal row mismatch')
    end_need=int(event_ms.max()+3000+HOLD_MS+5000)
    t,a,b,problems=load_source_window(src,end_need)
    if problems:raise RuntimeError(problems)
    if int(source_ord.max())>=len(t):raise RuntimeError('source ordinal outside loaded source')
    expected_ord=np.searchsorted(t,event_ms,side='left').astype(np.int64)
    if not np.array_equal(source_ord,expected_ord):raise RuntimeError('BETA065 source ordinal/searchsorted identity mismatch')
    labels,entry_idx,exit_idx=build_labels(event_ms,t,a,b)
    fit=split==0;cal=split==1;diag=split==2
    valid_fit=finite_rows(X,labels,fit);valid_cal=finite_rows(X,labels,cal);valid_diag=finite_rows(X,labels,diag)
    np.savez_compressed(out/'BETA_066_DELAYED_ACTION_LABELS.npz',event_time_ms=event_ms,source_ordinal=source_ord,
        labels=labels,entry_idx=entry_idx,exit_idx=exit_idx,action_names=ACTION_NAMES,delays_ms=DELAYS,
        split_code=split,specialist_code=specialist_code)
    cap={}
    for name,mask in [('FIT',valid_fit),('CAL',valid_cal),('DIAGNOSTIC',valid_diag)]:
        y=labels[mask].astype(np.float64);best=np.nanmax(y,axis=1);now=np.nanmax(y[:,:2],axis=1);delayed=np.nanmax(y[:,2:],axis=1)
        cap[name]={
            'n':int(len(y)),'oracle_all_mean':float(best.mean()),'oracle_all_positive_fraction':float((best>0).mean()),
            'oracle_now_mean':float(now.mean()),'oracle_delayed_mean':float(delayed.mean()),
            'delay_increment_mean':float((best-now).mean()),
            'best_action_counts':{ACTION_NAMES[j]:int((np.nanargmax(y,axis=1)==j).sum()) for j in range(8)}
        }
    grid=[];pred_store={};models={}
    model_names=['HGB_D3_L2_5','HGB_D4_L2_10','EXTRA_D8_L150']
    Xfit=X[valid_fit];Yfit=labels[valid_fit].astype(np.float32)
    for mn in model_names:
        ts=time.time();model=make_model(mn);model.fit(Xfit,Yfit);models[mn]=model
        pred=np.asarray(model.predict(X),dtype=np.float32);pred_store[mn]=pred
        for th in Q_THRESHOLDS:
            m,_=replay(np.flatnonzero(valid_cal),event_ms,source_ord,pred,labels,entry_idx,exit_idx,th,False)
            row={'model':mn,'threshold':th,**m};row['guard_pass']=bool(m['trades']>=MIN_CAL_TRADES and m['net']>0 and m['pf']>1 and m['avg']>0)
            grid.append(row)
        print('MODEL',mn,'sec',round(time.time()-ts,2),'best_cal',max((g for g in grid if g['model']==mn),key=lambda r:r['net']),flush=True)
    passing=[g for g in grid if g['guard_pass']]
    if passing:
        passing.sort(key=lambda r:(r['net'],-r['max_dd'],r['avg'], -model_names.index(r['model'])),reverse=True)
        selected=passing[0];status='CAL_POSITIVE_GUARDED_CANDIDATE'
    else:
        best=max(grid,key=lambda r:r['net']);selected={'model':None,'threshold':None,'selection':'SKIP_ALL','best_failed_cal':best};status='NO_GUARDED_CAL_CANDIDATE__DEMOTE_CLOCK_SURFACE'
    selected_ledgers={}
    if passing:
        pred=pred_store[selected['model']];th=float(selected['threshold'])
        for nm,mask in [('FIT',valid_fit),('CAL',valid_cal),('DIAGNOSTIC',valid_diag)]:
            met,rows=replay(np.flatnonzero(mask),event_ms,source_ord,pred,labels,entry_idx,exit_idx,th,True)
            selected_ledgers[nm]=met
            pd.DataFrame(rows,columns=['proposal_row','event_time_ms','source_ordinal','action','predicted_value','realized_pnl','entry_idx','exit_idx']).to_csv(out/f'BETA_066_SELECTED_LEDGER_{nm}.csv.gz',index=False,compression='gzip')
        joblib.dump(models[selected['model']],out/'BETA_066_SELECTED_MODEL.joblib',compress=3)
    else:
        for nm in ['FIT','CAL','DIAGNOSTIC']:
            pd.DataFrame(columns=['proposal_row','event_time_ms','source_ordinal','action','predicted_value','realized_pnl','entry_idx','exit_idx']).to_csv(out/f'BETA_066_SELECTED_LEDGER_{nm}.csv.gz',index=False,compression='gzip')
            selected_ledgers[nm]=metrics([])
    np.savez_compressed(out/'BETA_066_DELAYED_ACTION_PREDICTIONS.npz',event_time_ms=event_ms,source_ordinal=source_ord,
        **{f'pred_{k}':v for k,v in pred_store.items()},action_names=ACTION_NAMES,split_code=split)
    hashes={}
    for p in out.iterdir():
        if p.is_file():hashes[p.name]=sha256_file(p)
    result={
      'unit_id':UNIT,'status':status,'source_sha256':SOURCE_SHA,'beta065_proposal_sha256':BETA065_PROPOSAL_SHA,
      'proposal_rows':int(len(event_ms)),'valid_rows':{'FIT':int(valid_fit.sum()),'CAL':int(valid_cal.sum()),'DIAGNOSTIC':int(valid_diag.sum())},
      'feature_names':feature_names.tolist(),'action_names':ACTION_NAMES.tolist(),'delays_ms':DELAYS.tolist(),'hold_seconds':30,'fee_usd':FEE,
      'model_grid':grid,'selected':selected,'selected_replay':selected_ledgers,'oracle_capacity':cap,
      'august':'SEALED_NOT_READ','diagnostic_used_for_selection':False,'runtime_sec':round(time.time()-start,2),
      'artifact_hashes_before_result_write':hashes
    }
    (out/'BETA_066_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':status,'selected':selected,'selected_replay':selected_ledgers,'capacity':cap,'runtime_sec':result['runtime_sec']},indent=2),flush=True)

if __name__=='__main__':main()
