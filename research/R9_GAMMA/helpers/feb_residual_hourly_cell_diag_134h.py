import sys,json,datetime
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro')

def loadq(fn):
 z=np.load(BASE/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q

def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();t,a,b,mid,h4,h1,m15,m5,start,end=D
H=loadq('feb_hourly_heartbeat_stream_134b.npz')
z=np.load(BASE/'feb_baseline_components_133b.npz');B={k:z[k] for k in z.files};z.close()
parts=[loadq('feb_native_pf10_stream_134c.npz'),q(B,'COV'),loadq('feb_learner_D_stream_133c.npz'),q(B,'COLD'),loadq('feb_asia_regime_filtered_stream_134f.npz'),q(B,'LATE21_LONG'),loadq('feb_recovery_PF4_stream_134f.npz')]
seen=set()
for Q in parts: seen.update(map(int,Q[0]))
E,X,R,Dr,P,Hd=H; keep=np.array([int(e) not in seen for e in E],bool)
E,X,R,Dr,P,Hd=[z[keep] for z in (E,X,R,Dr,P,Hd)]
hour=((t[E]//3600000)%24).astype(np.int8);b10=((t[E]//600000)%6).astype(np.int8)
sig=((h4[E]+1)*81+(h1[E]+1)*27+(m15[E]+1)*9+(m5[E]+1)*3+(Dr+1)).astype(np.int16)
dts=[datetime.datetime.fromtimestamp(int(x)/1000,datetime.timezone.utc) for x in t[E]];day=np.array([x.strftime('%Y-%m-%d') for x in dts]);week=np.array([f'{x.isocalendar().year}-W{x.isocalendar().week:02d}' for x in dts])

def met(p):
 gp=float(p[p>0].sum());gl=float(p[p<=0].sum());return dict(net=float(p.sum()),trades=int(len(p)),gross_loss=gl,pf=float(gp/-gl if gl<0 else 999),win=float(np.mean(p>0)),exp=float(np.mean(p)))
rows=[]
keys=np.stack((hour,b10,sig),axis=1)
for key in np.unique(keys,axis=0):
 m=np.all(keys==key,axis=1);n=int(m.sum())
 if n<40:continue
 p=P[m];ds=day[m];ws=week[m];dn=np.array([p[ds==x].sum() for x in np.unique(ds)]);wn=np.array([p[ws==x].sum() for x in np.unique(ws)])
 r=met(p);r.update(hour=int(key[0]),b10=int(key[1]),sig=int(key[2]),days=int(len(dn)),weeks=int(len(wn)),positive_day_frac=float(np.mean(dn>0)),positive_week_frac=float(np.mean(wn>0)),median_day=float(np.median(dn)))
 rows.append(r)
rows.sort(key=lambda r:r['net'],reverse=True)
# conservative cell families
sets={}
for name,pred in [
 ('PF2',lambda r:r['pf']>=2 and r['net']>0 and r['trades']>=60 and r['positive_week_frac']>=0.5),
 ('PF4',lambda r:r['pf']>=4 and r['net']>0 and r['trades']>=50 and r['positive_week_frac']>=0.5),
 ('ROBUST',lambda r:r['pf']>=2 and r['net']>=200 and r['trades']>=60 and r['positive_day_frac']>=0.6 and r['positive_week_frac']>=0.75),
 ('TOPNET',lambda r:r['net']>=500 and r['pf']>=1.5 and r['trades']>=80 and r['positive_week_frac']>=0.5),
]:
 sel=[r for r in rows if pred(r)];mask=np.zeros(len(E),bool)
 for r in sel:mask |= (hour==r['hour'])&(b10==r['b10'])&(sig==r['sig'])
 Q=tuple(z[mask] for z in (E,X,R,Dr,P,Hd));np.savez_compressed(BASE/f'feb_residual_hourly_{name}_134h.npz',E=Q[0],X=Q[1],R=Q[2],D=Q[3],P=Q[4],H=Q[5]);sets[name]={'cells':len(sel),**met(Q[4])}
obj={'raw_residual':met(P),'sets':sets,'top_cells':rows[:80],'all_cells':rows};(BASE/'feb_residual_hourly_cell_diag_134h.json').write_text(json.dumps(obj,indent=2));print(json.dumps({'raw_residual':obj['raw_residual'],'sets':sets,'top10':rows[:10]},indent=2))