import pandas as pd,numpy as np,json,time
from numba import njit
from pathlib import Path
st=time.time();rich='/mnt/data/delta_a_recovered/delta_a_grid_hf_r2_rich_events_jan.csv';parent='/mnt/data/SA100_R10AH_REVERT600_FAILURE_OWNER_EPISODES.csv';v1='/mnt/data/SA100_R10AP_EXPANSION_SELECTED_EVENTS01.csv';raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'
R=pd.read_csv(rich);R['event_id']=np.arange(len(R));pid=set(pd.read_csv(parent,usecols=['event_id']).event_id.astype(int));vid=set(pd.read_csv(v1,usecols=['event_id']).event_id.astype(int));U=R[~R.event_id.isin(pid|vid)].copy().sort_values('time_ms');U['minute']=U.time_ms//60000;U['seq']=U.groupby('minute').cumcount()+1;U['first_dir']=U.groupby('minute').cross_dir.transform('first');U['opp_first']=U.cross_dir!=U.first_dir;Q=U[(U.opp_first)&(U.owner=='CONT')].copy().sort_values('time_ms').reset_index(drop=True)
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'});t=D.timestamp_ms_utc.to_numpy(np.int64);mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.;ev=Q.time_ms.to_numpy(np.int64);side=Q.cross_dir.to_numpy(np.int8);ix=np.searchsorted(t,ev);ix=np.minimum(ix,len(t)-1)
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
cut=int(len(Q)*.6);rows=[];best=None
for stop in [.5,.75,1.,1.5,2.,3.]:
 for act,tr in [(.05,.02),(.1,.03),(.2,.05),(.3,.08),(.5,.1)]:
  for mh in [15,30,60,120]:
   p,h=sim(t,mid,ev,side,ix,stop,act,tr,mh);r={'stop':stop,'act':act,'trail':tr,'maxhold':mh}
   for lab,s in [('disc',slice(0,cut)),('hold',slice(cut,None)),('all',slice(None))]:
    x=p[s];gp=x[x>0].sum();gl=x[x<0].sum();r.update({f'{lab}_n':len(x),f'{lab}_net':float(x.sum()),f'{lab}_win':float((x>0).mean()),f'{lab}_gl':float(gl),f'{lab}_pf':float(gp/(-gl)) if gl<0 else None})
   if r['disc_net']>0 and r['hold_net']>0 and r['disc_win']>.5 and r['hold_win']>.5:rows.append(r)
res=pd.DataFrame(rows)
if len(res):res=res.sort_values(['all_net','all_gl'],ascending=[False,False])
res.to_csv('/mnt/data/SA100_R10AQ_SECONDWAVE_LIFECYCLE_CANDIDATES01.csv',index=False)
out={'status':'COMPLETE','candidate_events':len(Q),'candidates':len(res),'top_net':res.head(20).to_dict('records') if len(res) else [],'top_gl':res.sort_values(['all_gl','all_net'],ascending=[False,False]).head(20).to_dict('records') if len(res) else [],'elapsed_s':time.time()-st};Path('/mnt/data/SA100_R10AQ_SECONDWAVE_LIFECYCLE01.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))