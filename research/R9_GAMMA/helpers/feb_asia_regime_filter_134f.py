import sys,json,datetime
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro');t=V.load_month()[0]
z=np.load(BASE/'feb_asia_selected_stream_134f.npz');E,X,R,D,P,H,C=[z[k] for k in ['E','X','R','D','P','H','CELL']];z.close();b10=((t[E]//600000)%6).astype(np.int8);j60=np.searchsorted(t,t[E]-60000,side='left');ticks60=E-j60+1;act=np.select([ticks60<=200,ticks60<=500],[0,1],default=2).astype(np.int8)
dts=[datetime.datetime.fromtimestamp(int(x)/1000,datetime.timezone.utc) for x in t[E]];day=np.array([x.strftime('%Y-%m-%d') for x in dts]);week=np.array([f'{x.isocalendar().year}-W{x.isocalendar().week:02d}' for x in dts])

def met(p):
 gp=p[p>0].sum();gl=p[p<=0].sum();return dict(net=float(p.sum()),trades=len(p),gross_loss=float(gl),pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),exp=float(np.mean(p)))
keys=[];black=[]
for c in np.unique(C):
 for q in range(6):
  for a in range(3):
   m=(C==c)&(b10==q)&(act==a);n=int(m.sum())
   if n<20:continue
   p=P[m];ds=day[m];ws=week[m];dn=[float(p[ds==z].sum()) for z in np.unique(ds)];wn=[float(p[ws==z].sum()) for z in np.unique(ws)];r=met(p);r.update(cell=int(c),b10=q,activity=a,days=len(dn),weeks=len(wn),positive_day_frac=float(np.mean(np.array(dn)>0)),positive_week_frac=float(np.mean(np.array(wn)>0)),median_day=float(np.median(dn)))
   toxic=(len(dn)>=2 and len(wn)>=2 and r['net']<0 and r['pf']<0.8 and r['positive_day_frac']<=0.5) or (len(dn)>=3 and r['net']<0 and r['median_day']<0 and r['pf']<1.0)
   if toxic:black.append(r)
keep=np.ones(len(E),bool)
for r in black:keep &= ~((C==r['cell'])&(b10==r['b10'])&(act==r['activity']))
Q=tuple(v[keep] for v in (E,X,R,D,P,H,C));np.savez_compressed(BASE/'feb_asia_regime_filtered_stream_134f.npz',E=Q[0],X=Q[1],R=Q[2],D=Q[3],P=Q[4],H=Q[5],CELL=Q[6]);out={'blacklist':black,'metrics':met(Q[4])};(BASE/'feb_asia_regime_filter_134f.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))