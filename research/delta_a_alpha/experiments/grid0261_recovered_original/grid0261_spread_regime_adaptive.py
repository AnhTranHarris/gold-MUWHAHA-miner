"""GRID0261: as-of original quote spread and completed price-path quality; NO oracle admission.
Strictly sampled research, overlapping trades not portfolio. Screens only predeclared bands.
"""
import numpy as np,json,time
from grid0261_intrinsic_time_research import load_month
from pathlib import Path
OUT=Path('/mnt/data/grid0261_intrinsic'); OUT.mkdir(exist_ok=True)
RULES=('TREND5_AND_M1','PULLBACK5_IN_M1','FADE5_IN_M1')
SPREADS=(300,450,600)
MINMOV=(600,1200)
HORIZONS=(30000,90000)
def run_month(mon):
 t,a,b=load_month(mon);mid=(a+b)//2
 bases=np.flatnonzero(np.r_[True,np.diff(t//5000)!=0]);q=np.searchsorted(t,t[bases]+250,side='left')
 keep=q<len(t);q=q[keep];bases=bases[keep]
 keep=(t[q]-t[bases]<=2000);q=q[keep]
 past5=np.searchsorted(t,t[q]-5000,side='left');past60=np.searchsorted(t,t[q]-60000,side='left')
 dr5=mid[q]-mid[past5];dr60=mid[q]-mid[past60]
 cont5=(t[q]-t[past5]>=3500);cont60=(t[q]-t[past60]>=45000)
 spread=a[q]-b[q]
 results={}
 for h in HORIZONS:
  j=np.searchsorted(t,t[q]+h,side='left')
  ok=j<len(t);j=j[ok];orig=q[ok];d5=dr5[ok];d60=dr60[ok];sp=spread[ok]
  valid=(t[j]-t[orig]<=h+2000)&cont5[ok]&cont60[ok]
  for rul in RULES:
   for limit in SPREADS:
    for minimum in MINMOV:
     if rul=='TREND5_AND_M1':side=np.sign(d5);sel=np.sign(d60)==side;sz=np.abs(d5)
     elif rul=='PULLBACK5_IN_M1':side=np.sign(d60);sel=np.sign(d5)==-side;sz=np.abs(d5)
     else:side=-np.sign(d5);sel=np.sign(d60)==side;sz=np.abs(d5)
     g=valid&(side!=0)&(sp<=limit)&sel&(sz>=minimum)
     pnl=np.where(side==1,b[j]-a[orig],b[orig]-a[j])-520
     x=pnl[g]
     k=f'{rul}|sp<={limit/1000:g}|move>={minimum/1000:g}|hold{h//1000}s'
     results[k]={'n':int(len(x)),'net_usd_oz':round(float(x.sum()/1000),3),'gross_loss_usd_oz':round(float(x[x<0].sum()/1000),3)}
 return results
if __name__=='__main__':
 start=time.monotonic();ms={}
 for m in range(1,8):
  r=run_month(m);ms[str(m)]=r
  print('month',m,'top positives',sorted([(k,x) for k,x in r.items() if x['n']>=100 and x['net_usd_oz']>0],key=lambda z:-z[1]['net_usd_oz'])[:5],flush=True)
 result=[]
 for k in ms['1'].keys():
  vals=[ms[str(j)][k] for j in range(1,8)];result.append({'rule':k,'trades':sum(v['n'] for v in vals),'net':round(sum(v['net_usd_oz'] for v in vals),2),'positive_months':sum(v['net_usd_oz']>0 for v in vals),'months':[v['net_usd_oz'] for v in vals]})
 result.sort(key=lambda x:(-x['positive_months'],-x['net']))
 (OUT/'GRID0261_CAUSAL_SPREAD_QUALITY_RESEARCH_36FIXED_RULES.json').write_text(json.dumps({'not_portfolio':True,'not_out_of_sample':True,'results':result},indent=2))
 print('best',json.dumps(result[:8],indent=2));print('time',round(time.monotonic()-start,1))
