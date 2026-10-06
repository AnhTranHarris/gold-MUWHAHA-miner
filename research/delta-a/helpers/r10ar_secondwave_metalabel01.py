import pandas as pd,numpy as np,json,time
from sklearn.tree import DecisionTreeRegressor,export_text
from numba import njit
from pathlib import Path
st=time.time();rich='/mnt/data/delta_a_recovered/delta_a_grid_hf_r2_rich_events_jan.csv';parent='/mnt/data/SA100_R10AH_REVERT600_FAILURE_OWNER_EPISODES.csv';v1='/mnt/data/SA100_R10AP_EXPANSION_SELECTED_EVENTS01.csv';feat='/mnt/data/SA100_R10AM_P4P6_HARVEST_EVENTS01.csv';raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
R=pd.read_csv(rich);R['event_id']=np.arange(len(R));pid=set(pd.read_csv(parent,usecols=['event_id']).event_id.astype(int));vid=set(pd.read_csv(v1,usecols=['event_id']).event_id.astype(int));U=R[~R.event_id.isin(pid|vid)].copy().sort_values('time_ms');U['minute']=U.time_ms//60000;U['seq']=U.groupby('minute').cumcount()+1;U['first_dir']=U.groupby('minute').cross_dir.transform('first');U['first_ms']=U.groupby('minute').time_ms.transform('first');U['since_first_s']=(U.time_ms-U.first_ms)/1000.;U['opp_first']=U.cross_dir!=U.first_dir;Q=U[(U.opp_first)&(U.owner=='CONT')].copy()
F=pd.read_csv(feat); fcols=[c for c in F.columns if c not in ['event_id','time_ms','owner','horizon_s','cross_dir','harv_pnl','harv_hold']]; Q=Q.merge(F[['event_id']+fcols],on='event_id',how='left').sort_values('time_ms').reset_index(drop=True)
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=D.timestamp_ms_utc.to_numpy(np.int64);mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.;ev=Q.time_ms.to_numpy(np.int64);side=Q.cross_dir.to_numpy(np.int8);ix=np.searchsorted(t,ev);ix=np.minimum(ix,len(t)-1)
@njit
def sim(t,mid,ev,side,ix):
 out=np.empty(len(ev),np.float64);hold=np.empty(len(ev),np.float64);stop=1.;act=.5;tr=.1;mh=30
 for q in range(len(ev)):
  i=ix[q];sd=side[q];entry=mid[i]+.10*sd;sl=entry-stop*sd;end=ev[q]+mh*1000;k=i;armed=False;done=False;ex=entry
  while k<len(t) and t[k]<=end:
   px=mid[k]-.10 if sd>0 else mid[k]+.10;p=(px-entry)*sd
   if p<=-stop:ex=entry-stop*sd;done=True;break
   if p>=act:
    armed=True;c=px-tr*sd
    if (sd>0 and c>sl) or (sd<0 and c<sl):sl=c
   if armed and ((sd>0 and px<=sl) or (sd<0 and px>=sl)):ex=px;done=True;break
   k+=1
  if not done:
   k=np.searchsorted(t,end,side='right')-1
   if k<i:k=i
   ex=mid[k]-.10 if sd>0 else mid[k]+.10
  out[q]=(ex-entry)*sd;hold[q]=(t[k]-ev[q])/1000.
 return out,hold
Q['v_pnl'],Q['v_hold']=sim(t,mid,ev,side,ix)
cols=['source_gap','native_spread','horizon_s','hour','seq','since_first_s']+[c for c in fcols if c not in ['event_id']]
# dedup columns
cols=list(dict.fromkeys([c for c in cols if c in Q.columns]))
cut=int(len(Q)*.6);DQ=Q.iloc[:cut];HQ=Q.iloc[cut:];med=DQ[cols].replace([np.inf,-np.inf],np.nan).median();Xd=DQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xh=HQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xa=Q[cols].replace([np.inf,-np.inf],np.nan).fillna(med)
rows=[];models=[]
for depth in [2,3,4,5]:
 for leaf in [150,250,400,600,900]:
  m=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=19).fit(Xd,DQ.v_pnl);ld=m.apply(Xd);lh=m.apply(Xh);la=m.apply(Xa);good=[]
  for v in np.unique(ld):
   z=DQ.loc[ld==v,'v_pnl']
   if len(z)>=leaf and (z>0).mean()>.55 and z.mean()>.03:good.append(v)
  if not good:continue
  vals=[]
  for q,mask in [(DQ,np.isin(ld,good)),(HQ,np.isin(lh,good)),(Q,np.isin(la,good))]:
   x=q.loc[mask,'v_pnl'];vals += [len(x),float((x>0).mean()) if len(x) else 0,float(x.sum()),float(x[x<0].sum()),float(x.mean()) if len(x) else 0]
  nd,wd,netd,gld,avgd,nh,wh,neth,glh,avgh,na,wa,neta,gla,avga=vals
  if nd>=300 and nh>=180 and wd>.5 and wh>.5 and netd>0 and neth>0:
   rows.append(dict(depth=depth,min_leaf=leaf,n_leaves=len(good),disc_n=nd,disc_win=wd,disc_net=netd,disc_gl=gld,hold_n=nh,hold_win=wh,hold_net=neth,hold_gl=glh,all_n=na,all_win=wa,all_net=neta,all_gl=gla,all_avg=avga,coverage=na/len(Q)));models.append((depth,leaf,good,m,la))
res=pd.DataFrame(rows)
if len(res):res=res.sort_values(['all_net','all_gl'],ascending=[False,False])
res.to_csv('/mnt/data/SA100_R10AR_SECONDWAVE_METALABEL_CANDIDATES01.csv',index=False)
chosen=None
if len(res):
 q=res.copy();q['score']=q.all_net-0.15*(-q.all_gl);rr=q.sort_values('score',ascending=False).iloc[0];det=next(x for x in models if x[0]==rr.depth and x[1]==rr.min_leaf);depth,leaf,good,m,la=det;mask=np.isin(la,good);sel=Q.loc[mask].copy();sel[['event_id','time_ms','cross_dir','v_pnl','v_hold','seq','since_first_s']].to_csv('/mnt/data/SA100_R10AR_SECONDWAVE_SELECTED_EVENTS01.csv',index=False);chosen={**rr.to_dict(),'leaves':[int(x) for x in good],'tree':export_text(m,feature_names=cols)}
out={'status':'COMPLETE','base_events':len(Q),'candidates':len(res),'chosen':chosen,'elapsed_s':time.time()-st};Path('/mnt/data/SA100_R10AR_SECONDWAVE_METALABEL01.json').write_text(json.dumps(out,indent=2,default=lambda o: float(o) if isinstance(o,np.floating) else int(o) if isinstance(o,np.integer) else str(o)));print(json.dumps(out,indent=2,default=lambda o: float(o) if isinstance(o,np.floating) else int(o) if isinstance(o,np.integer) else str(o)))