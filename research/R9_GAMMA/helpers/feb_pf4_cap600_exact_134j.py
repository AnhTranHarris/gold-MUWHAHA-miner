import sys,json
from pathlib import Path
import numpy as np
sys.path[:0]=['/mnt/data','/mnt/data/gamma02_jan_repro']
import feb_vertical_stack_134b as V
BASE=Path('/mnt/data/gamma02_jan_repro')
def loadq(fn): z=np.load(BASE/fn);Q=tuple(z[x] for x in ['E','X','R','D','P','H']);z.close();return Q
def q(z,pre):return tuple(z[pre+'_'+x] for x in ['E','X','R','D','P','H'])
D=V.load_month();z=np.load(BASE/'feb_baseline_components_133b.npz');B={k:z[k] for k in z.files};z.close();parts=[loadq('feb_native_pf10_stream_134c.npz'),q(B,'COV'),loadq('feb_learner_D_stream_133c.npz'),q(B,'COLD'),loadq('feb_asia_regime_filtered_stream_134f.npz'),q(B,'LATE21_LONG'),loadq('feb_recovery_PF4_stream_134f.npz'),loadq('feb_residual_hourly_PF4_134h.npz')];wd=loadq('feb_wd_L30_C384_134e.npz');S,dup=V.dedup(parts);SS,_,_=V.cap(S,768);Q,mo,sk=V.merge_watchdog(wd,SS,600);r=V.score(D,Q,True);r.update(global_cap=600,global_maxopen_event=mo,supp_dup=dup);(BASE/'feb_pf4_cap600_exact_134j.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:r.get(k) for k in ['net','trades','gross_loss','pf','win','expectancy','balance_dd','equity_dd','min_total_equity','maxopen_exact','positive_days','beat_days','positive_weeks','beat_weeks']}))