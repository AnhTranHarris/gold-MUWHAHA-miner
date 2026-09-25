import pandas as pd,numpy as np,glob,os,json,argparse
from numba import njit
ROOT='/mnt/data/r9_research_v2'; OUT=f'{ROOT}/oracle'; os.makedirs(OUT,exist_ok=True)
@njit
def cap(t,mid,et,horizons):
 n=len(et); H=len(horizons); out=np.zeros((n,H,3),np.float64); j0=0
 for k in range(n):
  while j0<len(t) and t[j0]<et[k]: j0+=1
  if j0>=len(t): break
  p0=mid[j0]; j=j0; mx=0.; mn=0.; hi=0; maxh=horizons[-1]
  while j<len(t) and t[j]-et[k]<=maxh:
   d=mid[j]-p0
   if d>mx: mx=d
   if d<mn: mn=d
   while hi<H and t[j]-et[k]>=horizons[hi]:
    out[k,hi,0]=mx; out[k,hi,1]=-mn; out[k,hi,2]=max(mx,-mn)-.20; hi+=1
   j+=1
  while hi<H:
   out[k,hi,0]=mx; out[k,hi,1]=-mn; out[k,hi,2]=max(mx,-mn)-.20; hi+=1
 return out
def run(m):
 f=glob.glob(f'/mnt/data/XAUUSD_DUKAS_2026_{m:02d}_ticks.csv*.gz')[0]
 x=pd.read_csv(f,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw']); t=x.timestamp_ms_utc.to_numpy(np.int64); mid=(x.ask_raw.to_numpy(float)+x.bid_raw.to_numpy(float))/2000.; del x
 e=pd.read_pickle(f'{ROOT}/events_{m:02d}.pkl.gz',compression='gzip'); et=e.time_ms.to_numpy(np.int64); h=np.array([5000,10000,20000,30000,60000,120000],np.int64); a=cap(t,mid,et,h); rows=[]
 for j,hh in enumerate(h):
  z=np.maximum(a[:,j,2],0); rows.append({'month':m,'horizon_ms':int(hh),'events':len(e),'oracle_net':float(z.sum()),'positive_events':int((z>0).sum()),'mean_all':float(z.mean()),'mean_taken':float(z[z>0].mean()) if (z>0).any() else 0})
 pd.DataFrame(rows).to_csv(f'{OUT}/oracle_{m:02d}.csv',index=False); print(pd.DataFrame(rows).to_string(index=False),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--month',type=int,required=True);a=ap.parse_args();run(a.month)
