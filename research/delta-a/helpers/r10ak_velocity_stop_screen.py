import pandas as pd, numpy as np, json, time
from numba import njit
from pathlib import Path
st=time.time()
raw='/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz'; rich='/mnt/data/delta_a_recovered/delta_a_grid_hf_r2_rich_events_jan.csv'; parent='/mnt/data/SA100_R10AH_REVERT600_FAILURE_OWNER_EPISODES.csv'
D=pd.read_csv(raw,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
t=D.timestamp_ms_utc.to_numpy(np.int64); mid=(D.ask_raw.to_numpy(np.float64)+D.bid_raw.to_numpy(np.float64))/2000.
sec=t//1000; ch=np.empty(len(sec),bool); ch[0]=1; ch[1:]=sec[1:]!=sec[:-1]; ix=np.flatnonzero(ch); last=np.r_[ix[1:]-1,len(sec)-1]
secs=sec[ix].astype(np.int64); hi=np.maximum.reduceat(mid,ix); lo=np.minimum.reduceat(mid,ix); close=mid[last]
R=pd.read_csv(rich); R['event_id']=np.arange(len(R)); parent_ids=set(pd.read_csv(parent,usecols=['event_id']).event_id.astype(int)); R=R[~R.event_id.isin(parent_ids)].copy().sort_values('time_ms').reset_index(drop=True)
evms=R.time_ms.to_numpy(np.int64); cross=R.cross_dir.to_numpy(np.int8); own=np.where(R.owner.to_numpy()=='CONT',1,-1).astype(np.int8); side=(cross*own).astype(np.int8); horizon=R.horizon_s.to_numpy(np.int64)
evix=np.searchsorted(t,evms); evix=np.minimum(evix,len(t)-1); entry_mid=mid[evix]; sidx=np.searchsorted(secs,evms//1000,side='right')-1
@njit
def sim(stops, evms,side,horizon,entry_mid,sidx,secs,hi,lo,close):
    out=np.empty((len(stops),len(evms)),np.float64)
    for z in range(len(stops)):
      stop=stops[z]
      for q in range(len(evms)):
        sd=side[q]; entry=entry_mid[q]+0.10*sd; endsec=evms[q]//1000+horizon[q]; j=sidx[q]+1; ex=np.nan
        while j<len(secs) and secs[j]<=endsec:
          if sd>0:
            if lo[j]-0.10 <= entry-stop: ex=entry-stop; break
          else:
            if hi[j]+0.10 >= entry+stop: ex=entry+stop; break
          j+=1
        if not np.isfinite(ex):
          k=np.searchsorted(secs,endsec,side='right')-1
          if k<sidx[q]: k=sidx[q]
          ex=close[k]-0.10 if sd>0 else close[k]+0.10
        out[z,q]=(ex-entry)*sd
    return out
stops=np.array([0.5,0.75,1.,1.5,2.,3.,5.,7.5,10.,15.])
P=sim(stops,evms,side,horizon,entry_mid,sidx,secs,hi,lo,close)
cut=int(len(R)*.6); rows=[]
for z,stop in enumerate(stops):
  r={'stop':float(stop)}
  for label,sl in [('disc',slice(0,cut)),('hold',slice(cut,None)),('all',slice(None))]:
    x=P[z,sl]; gp=x[x>0].sum(); gl=x[x<0].sum()
    r.update({f'{label}_n':len(x),f'{label}_net':float(x.sum()),f'{label}_win':float((x>0).mean()),f'{label}_gl':float(gl),f'{label}_pf':float(gp/(-gl)) if gl<0 else None})
  rows.append(r)
res=pd.DataFrame(rows); res.to_csv('/mnt/data/SA100_R10AK_VELOCITY_STOP_SCREEN01.csv',index=False)
out={'status':'COMPLETE_1S_SCREEN','unused_events':len(R),'rows':rows,'elapsed_s':time.time()-st,'note':'1-second first-passage screen; finalists require raw-tick exact replay'}
Path('/mnt/data/SA100_R10AK_VELOCITY_STOP_SCREEN01.json').write_text(json.dumps(out,indent=2)); print(res.to_string(index=False)); print('elapsed',time.time()-st)