import pandas as pd,numpy as np,glob,json,os
ROOT='/mnt/data/r9_research_v2'; OUT=f'{ROOT}/screens'; os.makedirs(OUT,exist_ok=True)
DELAY=[250,500,1000,2000,3000]; HORIZ=[2000,5000,10000,20000,30000]
THR=[.03,.05,.08,.10,.15,.20,.30,.50]; PULL=[.03,.05,.10,.15,.20]

def load(m):
 f=glob.glob(f'/mnt/data/XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz')[0]
 x=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'])
 t=x.timestamp_ms_utc.to_numpy(np.int64); mid=(x.ask_raw.to_numpy(float)+x.bid_raw.to_numpy(float))/2000.; del x
 e=pd.read_pickle(f'{ROOT}/events_{m:02d}.pkl.gz',compression='gzip')
 et=e.time_ms.to_numpy(np.int64); side=e.side.to_numpy(float); i0=np.searchsorted(t,et,side='left'); i0=np.minimum(i0,len(t)-1); p0=mid[i0]
 return t,mid,e,et,side,i0,p0

def feat_month(m):
 t,mid,e,et,side,i0,p0=load(m); out={'month':m,'n':len(e),'delay':{}}
 for delay in DELAY:
  io=np.searchsorted(t,et+delay,side='left'); io=np.minimum(io,len(t)-1); po=mid[io]; disp=(po-p0)*side
  mx=np.empty(len(e)); mn=np.empty(len(e))
  for k,(a,b,s,pp) in enumerate(zip(i0,io,side,p0)):
   v=(mid[a:b+1]-pp)*s; mx[k]=v.max(); mn[k]=v.min()
  block={'disp':disp,'max':mx,'min':mn,'pnl':{}}
  for h in HORIZ:
   ix=np.searchsorted(t,et+delay+h,side='left'); ix=np.minimum(ix,len(t)-1); px=mid[ix]
   block['pnl'][h]={'orig':(px-po)*side-.20,'fade':-(px-po)*side-.20}
  out['delay'][delay]=block
 return out

D={m:feat_month(m) for m in range(1,8)}
rows=[]
for delay in DELAY:
 for h in HORIZ:
  for thr in THR:
   specs=[('ACCEPT_CONT',lambda b,thr=thr:b['disp']>=thr,'orig'),('RECLAIM_FADE',lambda b,thr=thr:b['disp']<=-thr,'fade'),('REACTION_ROUTE',lambda b,thr=thr:np.abs(b['disp'])>=thr,'route')]
   for name,fn,act in specs:
    mm=[]; cc=[]; good=True
    for m in [1,2,3]:
     b=D[m]['delay'][delay]; mask=fn(b); cc.append(int(mask.sum()))
     pnl=np.where(b['disp']>=0,b['pnl'][h]['orig'],b['pnl'][h]['fade']) if act=='route' else b['pnl'][h][act]
     v=pnl[mask]; mean=v.mean() if len(v) else -9; mm.append(mean)
     if len(v)<250 or mean<=0: good=False
    if good:
     b=D[4]['delay'][delay]; mask=fn(b); pnl=np.where(b['disp']>=0,b['pnl'][h]['orig'],b['pnl'][h]['fade']) if act=='route' else b['pnl'][h][act]; v=pnl[mask]
     rows.append({'family':name,'delay':delay,'horizon':h,'thr':thr,'min_disc':min(mm),'avg_disc':np.mean(mm),'counts':cc,'m1':mm[0],'m2':mm[1],'m3':mm[2],'apr_n':len(v),'apr_mean':v.mean() if len(v) else np.nan,'apr_net':v.sum()})
  for pull in PULL:
   for confirm in THR:
    for name,action in [('PULLBACK_RESUME','orig'),('SWEEP_RECLAIM','fade')]:
     mm=[]; cc=[]; good=True
     for m in [1,2,3]:
      b=D[m]['delay'][delay]; mask=(b['min']<=-pull)&(b['disp']>=confirm) if name=='PULLBACK_RESUME' else (b['max']>=pull)&(b['disp']<=-confirm)
      v=b['pnl'][h][action][mask]; cc.append(int(mask.sum())); mean=v.mean() if len(v) else -9; mm.append(mean)
      if len(v)<150 or mean<=0: good=False
     if good:
      b=D[4]['delay'][delay]; mask=(b['min']<=-pull)&(b['disp']>=confirm) if name=='PULLBACK_RESUME' else (b['max']>=pull)&(b['disp']<=-confirm); v=b['pnl'][h][action][mask]
      rows.append({'family':name,'delay':delay,'horizon':h,'thr':confirm,'pull':pull,'min_disc':min(mm),'avg_disc':np.mean(mm),'counts':cc,'m1':mm[0],'m2':mm[1],'m3':mm[2],'apr_n':len(v),'apr_mean':v.mean() if len(v) else np.nan,'apr_net':v.sum()})
res=pd.DataFrame(rows); res.to_csv(f'{OUT}/break_reaction_discovery_april.csv',index=False)
if len(res)==0: print('NO DISCOVERY POSITIVE CANDIDATES'); raise SystemExit
sel=res[(res.apr_n>=150)&(res.apr_mean>0)].copy(); sel['robust']=sel[['min_disc','apr_mean']].min(axis=1); sel=sel.sort_values(['robust','apr_net'],ascending=False)
print('DISCOVERY POS',len(res),'APR POS',len(sel)); print(sel.head(40).to_string(index=False))
outs=[]
for _,r in sel.head(20).iterrows():
 vals=[]
 for m in [5,6,7]:
  b=D[m]['delay'][int(r.delay)]; fam=r.family; thr=r.thr; pull=r.get('pull',np.nan)
  if fam=='ACCEPT_CONT': mask=b['disp']>=thr; pnl=b['pnl'][int(r.horizon)]['orig']
  elif fam=='RECLAIM_FADE': mask=b['disp']<=-thr; pnl=b['pnl'][int(r.horizon)]['fade']
  elif fam=='REACTION_ROUTE': mask=np.abs(b['disp'])>=thr; pnl=np.where(b['disp']>=0,b['pnl'][int(r.horizon)]['orig'],b['pnl'][int(r.horizon)]['fade'])
  elif fam=='PULLBACK_RESUME': mask=(b['min']<=-pull)&(b['disp']>=thr); pnl=b['pnl'][int(r.horizon)]['orig']
  else: mask=(b['max']>=pull)&(b['disp']<=-thr); pnl=b['pnl'][int(r.horizon)]['fade']
  v=pnl[mask]; vals.append((len(v),float(v.mean()) if len(v) else np.nan,float(v.sum())))
 z=r.to_dict(); z['m5_n'],z['m5_mean'],z['m5_net']=vals[0]; z['m6_n'],z['m6_mean'],z['m6_net']=vals[1]; z['m7_n'],z['m7_mean'],z['m7_net']=vals[2]; z['mjj_net']=sum(v[2] for v in vals); outs.append(z)
out=pd.DataFrame(outs); out.to_csv(f'{OUT}/break_reaction_frozen_forward.csv',index=False); print('\nFROZEN MJJ'); print(out[['family','delay','horizon','thr','pull','robust','apr_mean','m5_n','m5_mean','m5_net','m6_n','m6_mean','m6_net','m7_n','m7_mean','m7_net','mjj_net']].to_string(index=False))
