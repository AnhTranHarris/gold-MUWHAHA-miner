import pandas as pd, numpy as np, json, time
from sklearn.tree import DecisionTreeRegressor, export_text
from numba import njit
from pathlib import Path
st=time.time(); raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; ev='/mnt/data/SA100_R10AM_P4P6_HARVEST_EVENTS01.csv'
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=D.timestamp_ms_utc.to_numpy(np.int64);mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.
E=pd.read_csv(ev); C=E[E.owner=='CONT'].copy(); C['desk']=np.where(C.range30>18.9,'A',np.where((C.range30<=18.9)&(C.eff15<=.32)&(C.tick15>9.83)&(C.disp120>.56),'B','X')); C=C[C.desk!='X'].sort_values('time_ms').reset_index(drop=True)
@njit
def sim(t,mid,ev,side,ix,stop,act,tr,mh):
 out=np.empty(len(ev),np.float64);hold=np.empty(len(ev),np.float64)
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
# Balanced specialized lifecycles
for desk,pars in [('A',(1.5,.20,.05,30)),('B',(.75,.10,.03,30))]:
 m=C.desk==desk; evs=C.loc[m,'time_ms'].to_numpy(np.int64); side=C.loc[m,'cross_dir'].to_numpy(np.int8); ix=np.searchsorted(t,evs);ix=np.minimum(ix,len(t)-1);p,h=sim(t,mid,evs,side,ix,*pars); C.loc[m,'v_pnl']=p; C.loc[m,'v_hold']=h
cols=['source_gap','native_spread','horizon_s','hour','session_code','disp5','range5','eff5','turns5','tick5','disp10','range10','eff10','turns10','tick10','disp15','range15','eff15','turns15','tick15','disp30','range30','eff30','turns30','tick30','disp60','range60','eff60','turns60','tick60','disp120','range120','eff120','turns120','tick120','range30_120','range10_60','tick10_60']
rows=[];details=[];selected_event_ids=[]
for desk in ['A','B']:
 Q=C[C.desk==desk].sort_values('time_ms').reset_index(drop=True);cut=int(len(Q)*.6); DQ=Q.iloc[:cut];HQ=Q.iloc[cut:];med=DQ[cols].replace([np.inf,-np.inf],np.nan).median();Xd=DQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xh=HQ[cols].replace([np.inf,-np.inf],np.nan).fillna(med);Xa=Q[cols].replace([np.inf,-np.inf],np.nan).fillna(med)
 for depth in [2,3,4]:
  for leaf in [150,250,400,600]:
   model=DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=17).fit(Xd,DQ.v_pnl);ld=model.apply(Xd);lh=model.apply(Xh);la=model.apply(Xa);good=[]
   for v in np.unique(ld):
    z=DQ.loc[ld==v,'v_pnl']
    if len(z)>=leaf and (z>0).mean()>.55 and z.mean()>.04:good.append(v)
   if not good:continue
   masks=[np.isin(ld,good),np.isin(lh,good),np.isin(la,good)]; vals=[]
   for q,mask in zip([DQ,HQ,Q],masks):
    x=q.loc[mask,'v_pnl'];vals += [len(x),float((x>0).mean()) if len(x) else 0,float(x.sum()),float(x[x<0].sum()),float(x.mean()) if len(x) else 0]
   nd,wd,netd,gld,avgd,nh,wh,neth,glh,avgh,na,wa,neta,gla,avga=vals
   if nd>=300 and nh>=180 and wd>.5 and wh>.5 and netd>0 and neth>0:
    rows.append(dict(desk=desk,depth=depth,min_leaf=leaf,n_leaves=len(good),disc_n=nd,disc_win=wd,disc_net=netd,disc_gl=gld,disc_avg=avgd,hold_n=nh,hold_win=wh,hold_net=neth,hold_gl=glh,hold_avg=avgh,all_n=na,all_win=wa,all_net=neta,all_gl=gla,all_avg=avga,coverage=na/len(Q)))
    details.append((desk,depth,leaf,good,model,Q,la))
res=pd.DataFrame(rows)
if len(res):res=res.sort_values(['all_net','all_gl'],ascending=[False,False])
res.to_csv('/mnt/data/SA100_R10AP_EXPANSION_METALABEL_CANDIDATES01.csv',index=False)
# choose per desk Pareto candidate by net - 0.15*abs(GL), while requiring >=50 hold
chosen=[]
for desk in ['A','B']:
 q=res[res.desk==desk].copy()
 if not len(q):continue
 q['score']=q.all_net-0.15*(-q.all_gl); rr=q.sort_values('score',ascending=False).iloc[0]
 det=next(x for x in details if x[0]==desk and x[1]==rr.depth and x[2]==rr.min_leaf)
 _,depth,leaf,good,model,Q,la=det; mask=np.isin(la,good); ids=Q.loc[mask,'event_id'].astype(int).tolist();selected_event_ids += ids
 chosen.append({**rr.to_dict(),'selected_leaves':good,'tree':export_text(model,feature_names=cols)})
sel=C[C.event_id.isin(selected_event_ids)].copy();sel[['event_id','time_ms','desk','cross_dir','v_pnl','v_hold']].to_csv('/mnt/data/SA100_R10AP_EXPANSION_SELECTED_EVENTS01.csv',index=False)
out={'status':'COMPLETE','base_events':len(C),'candidates':len(res),'chosen':chosen,'combined':{'n':len(sel),'win':float((sel.v_pnl>0).mean()) if len(sel) else 0,'net':float(sel.v_pnl.sum()),'gl':float(sel.loc[sel.v_pnl<0,'v_pnl'].sum())},'elapsed_s':time.time()-st};Path('/mnt/data/SA100_R10AP_EXPANSION_METALABEL01.json').write_text(json.dumps(out,indent=2,default=lambda o: int(o) if isinstance(o,(np.integer,)) else float(o) if isinstance(o,(np.floating,)) else str(o)));print(json.dumps(out,indent=2,default=lambda o: int(o) if isinstance(o,(np.integer,)) else float(o) if isinstance(o,(np.floating,)) else str(o)))