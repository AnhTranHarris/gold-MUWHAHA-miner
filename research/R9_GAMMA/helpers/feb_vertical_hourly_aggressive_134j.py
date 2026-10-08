import sys,json
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn): z=np.load(BASE/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();z=np.load(BASE/'feb_baseline_components_133b.npz');B={k:z[k] for k in z.files};z.close();cov=q(B,'COV');cold=q(B,'COLD');late=q(B,'LATE21_LONG');wd=loadq('feb_wd_L30_C384_134e.npz');G=loadq('feb_learner_D_stream_133c.npz');N=loadq('feb_native_pf10_stream_134c.npz');A=loadq('feb_asia_regime_filtered_stream_134f.npz');R4=loadq('feb_recovery_PF4_stream_134f.npz')
sets=[]
for nm in ['PF4','ROBUST','TOPNET','PF2']:
 fn=BASE/f'feb_residual_hourly_{nm}_134h.npz'
 if fn.exists(): sets.append((nm,[N,cov,G,cold,A,late,R4,loadq(fn.name)]))
rows=[]
for name,parts in sets:
 S,dup=V.dedup(parts);SS,smo,ssk=V.cap(S,768)
 for gcap in [384,448,512,600,640,703,768]:
  Q,mo,sk=V.merge_watchdog(wd,SS,gcap);r=V.score(D,Q,gcap in (384,640,768));r.update(name=name,global_cap=gcap,global_maxopen_event=mo,supp_dup=dup);rows.append(r);print(json.dumps({k:r.get(k) for k in ['name','global_cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen_exact','positive_days','beat_days','positive_weeks','beat_weeks']}),flush=True)
(BASE/'feb_vertical_hourly_aggressive_134j.json').write_text(json.dumps({'rows':rows},indent=2))