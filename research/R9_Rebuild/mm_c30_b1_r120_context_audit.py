import pandas as pd, numpy as np, gzip, os, json, time, hashlib, pathlib, math
from numba import njit
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import roc_auc_score

ROOT=pathlib.Path('/mnt/data')
OUT=ROOT/'MM_C30_B1_R120_CONTEXT'
OUT.mkdir(exist_ok=True)
months=[1,2,3]
raw_paths={m: sorted(ROOT.glob(f'XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz'))[0] for m in months}
ec_paths={m: ROOT/'mmc30b_preflight'/f'event_clock_{m:02d}_fixed_outcomes.pkl.gz' for m in months}
ev_paths={m: ROOT/'mmc30b_preflight'/f'events_{m:02d}_v2_recovery.pkl.gz' for m in months}

@njit(cache=True)
def rolling_tape_features(t, mid, spr, dec, side, horizons):
    n=len(dec); hN=len(horizons)
    out=np.zeros((n,hN*8),np.float64)
    for j in range(n):
        e=np.searchsorted(t, dec[j], side='right')
        if e<=0: 
            continue
        last=mid[e-1]
        for q in range(hN):
            h=horizons[q]
            s=np.searchsorted(t, dec[j]-h, side='left')
            if s>=e: s=e-1
            first=mid[s]
            hi=first; lo=first; travel=0.; turns=0.; prev=first; prevsgn=0.; sp_sum=0.
            for k in range(s,e):
                p=mid[k]
                if p>hi: hi=p
                if p<lo: lo=p
                if k>s:
                    d=p-prev
                    travel += abs(d)
                    sgn=1 if d>0 else (-1 if d<0 else 0)
                    if sgn!=0:
                        if prevsgn!=0 and sgn!=prevsgn: turns += 1.
                        prevsgn=sgn
                    prev=p
                sp_sum += spr[k]
            cnt=e-s
            disp=(last-first)*side[j]
            rng=hi-lo
            eff=abs(last-first)/(travel+1e-12)
            loc=((last-lo)/(rng+1e-12)) if side[j]>0 else ((hi-last)/(rng+1e-12))
            base=q*8
            out[j,base+0]=disp
            out[j,base+1]=rng
            out[j,base+2]=travel
            out[j,base+3]=eff
            out[j,base+4]=turns/(max(1,cnt-1))
            out[j,base+5]=cnt/(h/1000.0)
            out[j,base+6]=loc
            out[j,base+7]=sp_sum/max(1,cnt)
    return out

def maxdd(x):
    x=np.asarray(x,float)
    if not len(x): return 0.0
    c=np.cumsum(x)
    peak=np.maximum.accumulate(np.r_[0.,c])[:-1]
    return float(np.max(peak-c))

def metrics(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return dict(trades=int(len(x)),net=float(x.sum()),gp=gp,gl=gl,pf=float(gp/-gl) if gl<0 else 1e9,
                win=float((x>0).mean()),maxdd=maxdd(x))

horizons=np.array([250,1000,5000,15000,30000,60000,120000],dtype=np.int64)
hnames=['250ms','1s','5s','15s','30s','60s','120s']
allD={}; allX={}
t0=time.time()
for m in months:
    ec=pd.read_pickle(ec_paths[m],compression='gzip')
    ev=pd.read_pickle(ev_paths[m],compression='gzip')[['time_ms','base_hold']]
    z=ec.merge(ev,on='time_ms',how='left')
    z=z[(z.base_hold>=2.0)&z.h2000_last.notna()].copy().reset_index(drop=True)
    z['decision_ms']=(z.time_ms+z.h2000_obs_lag.astype(np.int64)).astype(np.int64)
    z['close2_pnl']=z.h2000_last.astype(float)-0.20
    z['keep_pnl']=z.base_pnl.astype(float)
    d=pd.read_csv(raw_paths[m],compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],
                  dtype={'timestamp_ms_utc':'int64','ask_raw':'int64','bid_raw':'int64'})
    t=d.timestamp_ms_utc.to_numpy(np.int64)
    ask=d.ask_raw.to_numpy(np.float64)/1000.
    bid=d.bid_raw.to_numpy(np.float64)/1000.
    mid=(ask+bid)/2.; spr=ask-bid
    Xarr=rolling_tape_features(t,mid,spr,z.decision_ms.to_numpy(np.int64),z.side.to_numpy(np.int64),horizons)
    cols=[]
    kinds=['disp_al','range','travel','eff','turnrate','tickrate','close_loc_al','mean_spread']
    for h in hnames:
        for k in kinds: cols.append(f'r120_{h}_{k}')
    X=pd.DataFrame(Xarr,columns=cols)
    # normalized cross-horizon relations; all causal at decision time
    for h in hnames[:-1]:
        X[f'{h}_range_share']=X[f'r120_{h}_range']/(X['r120_120s_range']+1e-9)
        X[f'{h}_travel_share']=X[f'r120_{h}_travel']/(X['r120_120s_travel']+1e-9)
    X['disp_5s_minus_30s_rate']=X['r120_5s_disp_al']/5.-X['r120_30s_disp_al']/30.
    X['disp_15s_minus_60s_rate']=X['r120_15s_disp_al']/15.-X['r120_60s_disp_al']/60.
    allD[m]=z[['time_ms','decision_ms','side','keep_pnl','close2_pnl']].copy()
    allX[m]=X.replace([np.inf,-np.inf],np.nan).fillna(0.)
    # persist compact feature artifact
    feat=pd.concat([allD[m].reset_index(drop=True),allX[m]],axis=1)
    feat.to_pickle(OUT/f'MM_C30_B1_R120_M{m:02d}.pkl.gz',compression='gzip')
    del d, ask, bid, mid, spr, t, ec, ev, z, Xarr, feat

rows=[]
for depth in (2,3,4):
    for leaf in (750,1000,1500):
        pred={}
        for tm in months:
            tr=[m for m in months if m!=tm]
            XX=pd.concat([allX[m] for m in tr],ignore_index=True)
            zz=pd.concat([allD[m] for m in tr],ignore_index=True)
            y=np.clip(zz.close2_pnl.to_numpy(float)-zz.keep_pnl.to_numpy(float),-3,3)
            model=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=120)
            model.fit(XX,y)
            pred[tm]=model.predict(allX[tm])
        for thr in (0,.03,.05,.08,.10,.15,.20):
            r={'depth':depth,'leaf':leaf,'threshold':thr}; ok=True; total_delta=0; total_gl=0; minret=10; total_close=0
            for tm in months:
                z=allD[tm]; h=pred[tm]>=thr
                vals=np.where(h,z.close2_pnl.to_numpy(float),z.keep_pnl.to_numpy(float))
                b=metrics(z.keep_pnl); c=metrics(vals)
                dn=c['net']-b['net']; dgl=c['gl']-b['gl']; ret=c['gp']/b['gp']; ddd=c['maxdd']-b['maxdd']
                r.update({f'm{tm}_net':c['net'],f'm{tm}_delta':dn,f'm{tm}_gl_improve':dgl,
                          f'm{tm}_gp_ret':ret,f'm{tm}_dd_delta':ddd,f'm{tm}_close':int(h.sum())})
                ok &= (dn>0 and dgl>0 and ret>=.95 and ddd<0 and h.sum()>0)
                total_delta+=dn; total_gl+=dgl; minret=min(minret,ret); total_close+=int(h.sum())
            r.update(all_month_pass=bool(ok),total_delta=total_delta,total_gl_improvement=total_gl,
                     min_gp_ret=minret,total_close=total_close)
            rows.append(r)
grid=pd.DataFrame(rows).sort_values(['all_month_pass','total_delta'],ascending=[False,False])
grid.to_csv(OUT/'MM_C30_B1_R120_GRID.csv',index=False)
best=grid.iloc[0].to_dict()
# feature predictive diagnostic, cross-month OOF AUC for close2 better than keep
aucs={}
for tm in months:
    tr=[m for m in months if m!=tm]
    XX=pd.concat([allX[m] for m in tr],ignore_index=True); zz=pd.concat([allD[m] for m in tr],ignore_index=True)
    ytrain=np.clip(zz.close2_pnl.to_numpy(float)-zz.keep_pnl.to_numpy(float),-3,3)
    mod=DecisionTreeRegressor(max_depth=3,min_samples_leaf=1000,random_state=120).fit(XX,ytrain)
    p=mod.predict(allX[tm]); y=(allD[tm].close2_pnl.to_numpy()>allD[tm].keep_pnl.to_numpy()).astype(int)
    aucs[tm]=float(roc_auc_score(y,p))
res={
    'job_id':'MM-C30-B1-R120-CONTEXT-AUDIT',
    'status':'COMPLETED_LOCAL',
    'scope':'original R9 +2s survivors, rolling trailing tick context only',
    'rolling_horizons_ms':horizons.tolist(),
    'months':{m:{'survivors':len(allD[m]),'baseline':metrics(allD[m].keep_pnl)} for m in months},
    'best':best,
    'pass':bool(best['all_month_pass']),
    'oof_auc_close2_better':aucs,
    'elapsed_seconds':time.time()-t0
}
with open(OUT/'MM_C30_B1_R120_RESULT.json','w') as f: json.dump(res,f,indent=2)
print(json.dumps(res,indent=2))