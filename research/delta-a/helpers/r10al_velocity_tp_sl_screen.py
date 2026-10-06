import pandas as pd, numpy as np, json, time
from numba import njit
from pathlib import Path
st=time.time(); raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; rich='/mnt/data/delta_a_recovered/delta_a_grid_hf_r2_rich_events_jan.csv'; parent='/mnt/data/SA100_R10AH_REVERT600_FAILURE_OWNER_EPISODES.csv'
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=D.timestamp_ms_utc.to_numpy(np.int64); mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.; sec=t//1000
ch=np.empty(len(sec),bool);ch[0]=1;ch[1:]=sec[1:]!=sec[:-1];ix=np.flatnonzero(ch);last=np.r_[ix[1:]-1,len(sec)-1];secs=sec[ix].astype(np.int64);hi=np.maximum.reduceat(mid,ix);lo=np.minimum.reduceat(mid,ix);close=mid[last]
R=pd.read_csv(rich);R['event_id']=np.arange(len(R));ids=set(pd.read_csv(parent,usecols=['event_id']).event_id.astype(int));R=R[~R.event_id.isin(ids)].copy().sort_values('time_ms').reset_index(drop=True)
evms=R.time_ms.to_numpy(np.int64); own=np.where(R.owner.to_numpy()=='CONT',1,-1).astype(np.int8); side=(R.cross_dir.to_numpy(np.int8)*own).astype(np.int8); horizon=R.horizon_s.to_numpy(np.int64); eix=np.searchsorted(t,evms);eix=np.minimum(eix,len(t)-1);emid=mid[eix];sidx=np.searchsorted(secs,evms//1000,side='right')-1
@njit
def one(sl,tp,evms,side,horizon,emid,sidx,secs,hi,lo,close):
 out=np.empty(len(evms),np.float64)
 for q in range(len(evms)):
  sd=side[q];entry=emid[q]+0.10*sd;end=evms[q]//1000+horizon[q];j=sidx[q]+1;ex=0.;done=False
  while j<len(secs) and secs[j]<=end:
   if sd>0:
    # conservative: if both touched same 1s bar, loss first
    if lo[j]-0.10<=entry-sl: ex=entry-sl;done=True;break
    if hi[j]-0.10>=entry+tp: ex=entry+tp;done=True;break
   else:
    if hi[j]+0.10>=entry+sl: ex=entry+sl;done=True;break
    if lo[j]+0.10<=entry-tp: ex=entry-tp;done=True;break
   j+=1
  if not done:
   k=np.searchsorted(secs,end,side='right')-1
   if k<sidx[q]:k=sidx[q]
   ex=close[k]-0.10 if sd>0 else close[k]+0.10
  out[q]=(ex-entry)*sd
 return out
sls=[1.,1.5,2.,3.,5.,7.5,10.,15.];tps=[.2,.3,.5,.75,1.,1.5,2.,3.,5.];cut=int(len(R)*.6);rows=[]
for sl in sls:
 for tp in tps:
  p=one(sl,tp,evms,side,horizon,emid,sidx,secs,hi,lo,close);r={'sl':sl,'tp':tp}
  for lab,s in [('disc',slice(0,cut)),('hold',slice(cut,None)),('all',slice(None))]:
   x=p[s];gp=x[x>0].sum();gl=x[x<0].sum();r.update({f'{lab}_net':float(x.sum()),f'{lab}_win':float((x>0).mean()),f'{lab}_gl':float(gl),f'{lab}_pf':float(gp/(-gl)) if gl<0 else None})
  if r['disc_net']>0 and r['hold_net']>0 and r['disc_win']>.5 and r['hold_win']>.5: rows.append(r)
res=pd.DataFrame(rows); 
if len(res):res=res.sort_values(['all_net','all_gl'],ascending=[False,False])
res.to_csv('/mnt/data/SA100_R10AL_VELOCITY_TPSL_CANDIDATES01.csv',index=False)
out={'status':'COMPLETE_1S_TPSL_SCREEN','unused_events':len(R),'candidates':len(res),'top':res.head(20).to_dict('records') if len(res) else [],'elapsed_s':time.time()-st,'note':'conservative 1s ambiguity => stop-first; raw-tick exact required'};Path('/mnt/data/SA100_R10AL_VELOCITY_TPSL_CANDIDATES01.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))