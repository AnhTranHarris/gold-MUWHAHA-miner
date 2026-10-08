import sys,json
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
B=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn):z=np.load(B/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();z=np.load(B/'feb_baseline_components_133b.npz');BB={k:z[k] for k in z.files};z.close();cov=q(BB,'COV');wd=loadq('feb_wd_L30_C384_134e.npz');G=loadq('feb_learner_D_stream_133c.npz');A=loadq('feb_asia_quality_PF8_134k.npz');R4=loadq('feb_recovery_PF4_stream_134f.npz');HR=loadq('feb_residual_hourly_PF4_134h.npz')
rows=[]
for mode,fn in [('PF10','feb_native_pf10_stream_134c.npz'),('WIN80','feb_native_win80_stream_134c.npz'),('PF5','feb_native_pf5_stream_134c.npz'),('MAXNET','feb_native_maxnet_stream_134c.npz')]:
 N=loadq(fn);parts=[N,cov,G,A,R4,HR];S,dup=V.dedup(parts);SS,_,_=V.cap(S,768)
 for cap in [320,384,448,512,600]:
  Q,mo,sk=V.merge_watchdog(wd,SS,cap);r=V.score(D,Q,cap in (384,600));r.update(native=mode,global_cap=cap,global_maxopen_event=mo);rows.append(r);print(json.dumps({k:r.get(k) for k in ['native','global_cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen_exact','positive_days','beat_days','positive_weeks','beat_weeks']}),flush=True)
(B/'feb_native_mode_vertical_134k.json').write_text(json.dumps({'rows':rows},indent=2))