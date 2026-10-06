import pandas as pd, numpy as np, json, time
from pathlib import Path
from numba import njit
from sklearn.tree import DecisionTreeRegressor, export_text
st=time.time(); raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; rich='/mnt/data/delta_a_recovered/delta_a_grid_hf_r2_rich_events_jan.csv'; parent='/mnt/data/SA100_R10AH_REVERT600_FAILURE_OWNER_EPISODES.csv'
# ticks and 1s causal features
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=D.timestamp_ms_utc.to_numpy(np.int64); mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.; sec=t//1000
ch=np.empty(len(sec),bool);ch[0]=1;ch[1:]=sec[1:]!=sec[:-1];ix=np.flatnonzero(ch);last=np.r_[ix[1:]-1,len(sec)-1];secs=sec[ix].astype(np.int64); O=mid[ix]; H=np.maximum.reduceat(mid,ix); L=np.minimum.reduceat(mid,ix); C=mid[last]; N=(last-ix+1).astype(np.float64)
sC=pd.Series(C); d=sC.diff().fillna(0).to_numpy(); ad=np.abs(d); sg=np.sign(d); turn=np.zeros(len(d));turn[1:]=(sg[1:]!=0)&(sg[:-1]!=0)&(sg[1:]!=sg[:-1])
F={}
for w in [5,10,15,30,60,120]:
 disp=sC.diff(w-1).to_numpy(); rng=(pd.Series(H).rolling(w,min_periods=w).max()-pd.Series(L).rolling(w,min_periods=w).min()).to_numpy(); travel=pd.Series(ad).rolling(w-1,min_periods=w-1).sum().to_numpy(); eff=np.abs(disp)/(travel+1e-12); trn=pd.Series(turn).rolling(w,min_periods=w).sum().to_numpy(); tick=pd.Series(N).rolling(w,min_periods=w).mean().to_numpy(); F[w]=(disp,rng,eff,trn,tick)
# unused events
R=pd.read_csv(rich);R['event_id']=np.arange(len(R));ids=set(pd.read_csv(parent,usecols=['event_id']).event_id.astype(int));R=R[~R.event_id.isin(ids)].copy().sort_values('time_ms').reset_index(drop=True)
evms=R.time_ms.to_numpy(np.int64); own=np.where(R.owner.to_numpy()=='CONT',1,-1).astype(np.int8); side=(R.cross_dir.to_numpy(np.int8)*own).astype(np.int8); eix=np.searchsorted(t,evms); eix=np.minimum(eix,len(t)-1); sidx=np.searchsorted(secs,evms//1000,side='left')-1
# features strictly prior completed second
trade_side=side.astype(float)
for w,(disp,rng,eff,trn,tick) in F.items():
 R[f'disp{w}']=disp[sidx]*trade_side;R[f'range{w}']=rng[sidx];R[f'eff{w}']=eff[sidx];R[f'turns{w}']=trn[sidx];R[f'tick{w}']=tick[sidx]
R['range30_120']=R.range30/(R.range120+1e-9);R['range10_60']=R.range10/(R.range60+1e-9);R['tick10_60']=R.tick10/(R.tick60+1e-9);R['owner_code']=own;R['session_code']=R.session.map({'OFF_SESSION':0,'LONDON':1,'OVERLAP':2,'NEWYORK':3}).fillna(-1).astype(int)
@njit
def harvest(t,mid,evms,side,eix,stop,act,trail,maxhold):
 out=np.empty(len(evms),np.float64); holds=np.empty(len(evms),np.float64)
 for q in range(len(evms)):
  i=eix[q]; sd=side[q]; entry=mid[i]+0.10*sd; sl=entry-stop*sd; end=evms[q]+maxhold*1000; k=i; ex=entry; armed=False
  while k<len(t) and t[k]<=end:
   bid=mid[k]-.10;ask=mid[k]+.10; px=bid if sd>0 else ask; pnl=(px-entry)*sd
   if pnl<=-stop: ex=entry-stop*sd;break
   if pnl>=act:
    armed=True; cand=px-trail*sd
    if sd>0:
     if cand>sl: sl=cand
    else:
     if cand<sl: sl=cand
   if armed:
    if (sd>0 and bid<=sl) or (sd<0 and ask>=sl): ex=bid if sd>0 else ask;break
   k+=1
  else: k-=1
  if k>=len(t) or t[k]>end: k=np.searchsorted(t,end,side='right')-1
  if ex==entry:
   if k<i:k=i
   ex=mid[k]-.10 if sd>0 else mid[k]+.10
  out[q]=(ex-entry)*sd; holds[q]=(t[k]-evms[q])/1000.
 return out,holds
p,holds=harvest(t,mid,evms,side,eix,5.0,.05,.02,120)
R['harv_pnl']=p;R['harv_hold']=holds
# chronological 60/40, separate owner desks
cols=['source_gap','native_spread','horizon_s','hour','session_code','disp5','range5','eff5','turns5','tick5','disp10','range10','eff10','turns10','tick10','disp15','range15','eff15','turns15','tick15','disp30','range30','eff30','turns30','tick30','disp60','range60','eff60','turns60','tick60','disp120','range120','eff120','turns120','tick120','range30_120','range10_60','tick10_60']
rows=[]; policies=[]
for owner in ['REVERT','CONT']:
 Q=R[R.owner==owner].copy().sort_values('time_ms').reset_index(drop=True); cut=int(len(Q)*.6); DQ=Q.iloc[:cut]; HQ=Q.iloc[cut:]
 med=DQ[cols].replace([np.inf,-np.inf],np.nan).median();Xd=DQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xh=HQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xa=Q[cols].replace([np.inf,-np.inf],np.nan).fillna(med)
 for depth in [2,3,4]:
  for leaf in [200,400,800,1200]:
   m=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=13)
   m.fit(Xd,DQ.harv_pnl);ld=m.apply(Xd);lh=m.apply(Xh);la=m.apply(Xa)
   good=[]
   for v in np.unique(ld):
    z=DQ[ld==v].harv_pnl
    if len(z)>=leaf and (z>0).mean()>.52 and z.mean()>0.02:good.append(v)
   if not good:continue
   md=np.isin(ld,good);mh=np.isin(lh,good);ma=np.isin(la,good)
   def met(q,mask):
    x=q.loc[mask,'harv_pnl'];return len(x),float((x>0).mean()) if len(x) else 0,float(x.mean()) if len(x) else 0,float(x.sum()),float(x[x<0].sum())
   nd,wd,ad,netd,gld=met(DQ,md);nh,wh,ah,neth,glh=met(HQ,mh);na,wa,aa,neta,gla=met(Q,ma)
   if nd>=400 and nh>=250 and wd>.5 and wh>.5 and ad>0 and ah>0 and netd>0 and neth>0:
    rows.append(dict(owner=owner,depth=depth,min_leaf=leaf,n_leaves=len(good),disc_n=nd,disc_win=wd,disc_avg=ad,disc_net=netd,disc_gl=gld,hold_n=nh,hold_win=wh,hold_avg=ah,hold_net=neth,hold_gl=glh,all_n=na,all_win=wa,all_avg=aa,all_net=neta,all_gl=gla,coverage=na/len(Q)))
    policies.append((owner,depth,leaf,good,export_text(m,feature_names=cols)))
res=pd.DataFrame(rows)
if len(res):res=res.sort_values(['all_net','all_n'],ascending=False)
res.to_csv('/mnt/data/SA100_R10AM_P4P6_VELOCITY_CANDIDATES01.csv',index=False)
# save event-level harvest result for future exact portfolio use
R[['event_id','time_ms','owner','horizon_s','cross_dir','harv_pnl','harv_hold']+cols].to_csv('/mnt/data/SA100_R10AM_P4P6_HARVEST_EVENTS01.csv',index=False)
top=[]
for _,rr in res.head(10).iterrows():
 match=[x for x in policies if x[0]==rr.owner and x[1]==rr.depth and x[2]==rr.min_leaf]
 top.append({**rr.to_dict(),'tree':match[0][4] if match else ''})
out={'status':'COMPLETE_RAW_TICK_HARVEST_META_SCREEN','events':len(R),'harvester':{'stop':5.0,'activation':.05,'trail':.02,'maxhold_s':120},'base_by_owner':R.groupby('owner').harv_pnl.agg(['size','sum','mean']).to_dict('index'),'candidates':len(res),'top':top,'elapsed_s':time.time()-st};Path('/mnt/data/SA100_R10AM_P4P6_VELOCITY_CANDIDATES01.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))