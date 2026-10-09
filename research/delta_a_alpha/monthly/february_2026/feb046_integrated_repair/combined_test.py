"""Compare original FEB045 profit-cushion and FEB045 prevent-only risk-frontier with same structured corrective L6 overlay.
Not endogenous full-V1. Zero forward leak into corrective entries: accepted original L3 position+completed M5/H1 only.
"""
import json,sys,numpy as np
from pathlib import Path
sys.path.insert(0,'/mnt/data/feb046')
import structural_recovery_overlay as s
import recovery_experiments as r
root=Path('/mnt/data/feb046');orig=s.L.copy();rows=[]
for name,file in [('profit','pocket_09_no_heat_ledger.npz'),('prevention','state_cut8_c22512_c25512_ledger.npz')]:
 z=np.load('/mnt/data/feb045/'+file);data={k:z[k].copy() for k in z.files};s.L=data;r.L=data
 base=r.q_metrics(data,True);print('BASE',name,base,flush=True)
 for t in [(180,1.,3.,2.),(180,2.,3.,2.),(300,1.,3.,2.),(300,2.,6.,3.),(300,3.,3.,2.)]:
  led,stats=s.scenario(t[0],t[1],t[2],t[3],source_set=(22,25));o={**stats,'baseline':name,'recovery_rule':t}
  if stats['l6_trades']>0:
   full=r.q_metrics(led,True);o['exact_dd']=full['dd'];o['maxopen']=full['maxopen']
  else:o['exact_dd']=base['dd'];o['maxopen']=base['maxopen']
  rows.append(o);print('COMBO',json.dumps(o),flush=True)
(root/'RECOVERY_COMBINED_SCREEN.json').write_text(json.dumps(rows,indent=2))