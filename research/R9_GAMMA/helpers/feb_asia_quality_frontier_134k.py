import sys,json,datetime
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
B=Path('/mnt/data/gamma02_jan_repro');t=V.load_month()[0]
z=np.load(B/'feb_asia_selected_stream_134f.npz');E,X,R,D,P,H,C=[z[k] for k in ['E','X','R','D','P','H','CELL']];z.close();b10=((t[E]//600000)%6).astype(np.int8);j60=np.searchsorted(t,t[E]-60000,side='left');ticks60=E-j60+1;act=np.select([ticks60<=200,ticks60<=500],[0,1],default=2).astype(np.int8)
dts=[datetime.datetime.fromtimestamp(int(x)/1000,datetime.timezone.utc) for x in t[E]];day=np.array([x.strftime('%Y-%m-%d') for x in dts]);week=np.array([f'{x.isocalendar().year}-W{x.isocalendar().week:02d}' for x in dts])
def met(p):gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),exp=float(np.mean(p)))
rows=[]
for c in np.unique(C):
 for q in range(6):
  for a in range(3):
   m=(C==c)&(b10==q)&(act==a);n=int(m.sum())
   if n<20:continue
   p=P[m];ds=day[m];ws=week[m];dn=np.array([p[ds==x].sum() for x in np.unique(ds)]);wn=np.array([p[ws==x].sum() for x in np.unique(ws)]);r=met(p);r.update(cell=int(c),b10=q,activity=a,days=len(dn),weeks=len(wn),positive_day_frac=float(np.mean(dn>0)),positive_week_frac=float(np.mean(wn>0)),median_day=float(np.median(dn)));rows.append(r)
criteria={
 'PF4':lambda r:r['pf']>=4 and r['net']>0 and r['trades']>=20,
 'PF8':lambda r:r['pf']>=8 and r['net']>0 and r['trades']>=20,
 'PF12':lambda r:r['pf']>=12 and r['net']>0 and r['trades']>=20,
 'ROBUST2':lambda r:r['net']>0 and r['pf']>=2 and r['days']>=2 and r['weeks']>=2 and r['positive_day_frac']>=.75 and r['positive_week_frac']>=.75,
 'ROBUST3':lambda r:r['net']>0 and r['pf']>=2 and r['days']>=3 and r['weeks']>=2 and r['positive_day_frac']>=.67 and r['positive_week_frac']>=.75,
}
out={}
for name,pred in criteria.items():
 sel=[r for r in rows if pred(r)];m=np.zeros(len(E),bool)
 for r in sel:m|=(C==r['cell'])&(b10==r['b10'])&(act==r['activity'])
 Q=tuple(v[m] for v in (E,X,R,D,P,H));np.savez_compressed(B/f'feb_asia_quality_{name}_134k.npz',E=Q[0],X=Q[1],R=Q[2],D=Q[3],P=Q[4],H=Q[5]);out[name]={'cells':len(sel),**met(Q[4])}
(B/'feb_asia_quality_frontier_134k.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))