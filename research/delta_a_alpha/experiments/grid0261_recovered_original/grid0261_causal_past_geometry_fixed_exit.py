"""GRID0261 causal 5s observed-sample, past-only multi-speed geometry on Dukascopy.
Fixed horizon EXIT at first observed future tick (not oracle); preliminary overlapping
source-only per-candidate screening, NOT portfolio PnL. Exact executable Ask/Bid.
"""
import numpy as np,pandas as pd,json,time
from pathlib import Path
from grid0261_intrinsic_time_research import load_month
OUT=Path('/mnt/data/grid0261_intrinsic');OUT.mkdir(exist_ok=True)
FAMILIES=('FAST5_WITH_M1','M1_WITH_M5','FIVE_SEC_PULLBACK_M1_TREND','FAST5_FADE_M1','M1_WITH_M15')
PARAMS=(600,1400,2400)

def calc(mon):
 t,a,b=load_month(mon);mid=(a+b)//2
 source=np.flatnonzero(np.r_[True,np.diff(t//5000)!=0])
 idx=np.searchsorted(t,t[source]+250,side='left')
 valid=idx<len(t);idx=idx[valid];source=source[valid]
 valid=(t[idx]-t[source]<=2000)&(a[idx]-b[idx]<=900)
 idx=idx[valid];source=source[valid]
 pre={}
 for window in (5000,30000,60000,300000,900000):
  j=np.searchsorted(t,t[idx]-window,side='left')
  # past state must have at least 80% of requested coverage (not a weekend gap)
  ready=(t[idx]-t[j]>=int(window*.8))
  v=mid[idx]-mid[j]
  v[~ready]=0
  pre[window]=v
 out={}
 for H in (30000,90000):
  ex=np.searchsorted(t,t[idx]+H,side='left')
  z=ex<len(t);x=ex[z];qidx=idx[z]
  zsmall=(t[x]-t[qidx]<H+2000)
  x=x[zsmall];ii=qidx[zsmall]
  p={k:v[z][zsmall] for k,v in pre.items()}
  for family in FAMILIES:
   for thr in PARAMS:
    if family=='FAST5_WITH_M1':
     sign=np.sign(p[5000]);gate=(abs(p[5000])>=thr)&(sign==np.sign(p[60000]))
    elif family=='M1_WITH_M5':
     sign=np.sign(p[60000]);gate=(abs(p[60000])>=thr)&(sign==np.sign(p[300000]))
    elif family=='FIVE_SEC_PULLBACK_M1_TREND':
     sign=np.sign(p[60000]);gate=(abs(p[5000])>=thr)&(sign==-np.sign(p[5000]))&(sign==np.sign(p[300000]))
    elif family=='FAST5_FADE_M1':
     sign=-np.sign(p[5000]);gate=(abs(p[5000])>=thr)&(sign==np.sign(p[60000]))
    else:
     sign=np.sign(p[60000]);gate=(abs(p[60000])>=thr)&(sign==np.sign(p[900000]))
    gate&=(sign!=0)
    # Ask buys / Bid sells, exit at opposite quote, fixed non-oracle clock
    pnl=np.where(sign==1,b[x]-a[ii],b[ii]-a[x])-520
    sel=pnl[gate]
    key=f'{family}/move{thr/1000:g}/hold{H/1000:g}s'
    out[key]={'n':int(gate.sum()),'net_usd_oz':float(sel.sum()/1000),'wins':int((sel>0).sum()),'gross_loss':float(sel[sel<0].sum()/1000)}
 return out
if __name__=='__main__':
 st=time.monotonic();m={}
 for mon in range(1,8):
  d=calc(mon);m[str(mon)]=d
  positive=[(k,v) for k,v in d.items() if v['n']>=100 and v['net_usd_oz']>0]
  print('month',mon,'positive source per-candidate screens',len(positive), 'top',sorted(positive,key=lambda x:-x[1]['net_usd_oz'])[:3],flush=True)
 ks=list(m['1'].keys());scores=[]
 for key in ks:
  vals=[m[str(mm)][key] for mm in range(1,8)]
  scores.append({'geometry':key,'n':sum(v['n'] for v in vals),'net':round(sum(v['net_usd_oz'] for v in vals),2),'positive_months':sum(v['net_usd_oz']>0 for v in vals),'months':[round(v['net_usd_oz'],1) for v in vals]})
 scores.sort(key=lambda x:(-x['positive_months'],-x['net']))
 record={'limits':['Overlapping source samples are NOT realized funded fills','Fixed-lifetime exits no protective stop. NO candidate promotion.','In-sample historical Jan-Jul, August SEALED'], 'scores':scores}
 (OUT/'GRID0261_CAUSAL_GEOMETRY_FIXED_EXIT_MONTHWISE_SOURCE_SCREEN.json').write_text(json.dumps(record,indent=2))
 print('TOP',json.dumps(scores[:15],indent=2),flush=True)
 print('seconds',round(time.monotonic()-st,2),flush=True)
