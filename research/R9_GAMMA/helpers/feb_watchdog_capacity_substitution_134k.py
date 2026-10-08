import sys,json
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
B=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn):z=np.load(B/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();z=np.load(B/'feb_baseline_components_133b.npz');BB={k:z[k] for k in z.files};z.close();parts=[loadq('feb_native_pf10_stream_134c.npz'),q(BB,'COV'),loadq('feb_learner_D_stream_133c.npz'),loadq('feb_asia_quality_PF8_134k.npz'),loadq('feb_recovery_PF4_stream_134f.npz'),loadq('feb_residual_hourly_PF4_134h.npz')];S,dup=V.dedup(parts);SS,_,_=V.cap(S,768)
rows=[]
for wname in ['feb_wd_L25_C256_134e.npz','feb_wd_L30_C256_134e.npz','feb_wd_L30_C384_134e.npz','feb_wd_L35_C384_134e.npz','feb_wd_L35_C512_134e.npz']:
 wd=loadq(wname)
 for cap in [320,384,448,512,600]:
  Q,mo,sk=V.merge_watchdog(wd,SS,cap);r=V.score(D,Q,cap in (384,600));r.update(watchdog=wname,global_cap=cap,global_maxopen_event=mo);rows.append(r);print(json.dumps({k:r.get(k) for k in ['watchdog','global_cap','net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','maxopen_exact','positive_days','beat_days','positive_weeks','beat_weeks']}),flush=True)
(B/'feb_watchdog_capacity_substitution_134k.json').write_text(json.dumps({'rows':rows},indent=2))