"""Original-event geometry concentration atlas, descriptive only (not fitted veto)."""
import numpy as np,io,zipfile,json
from r120_multiclock_geometry import ROOT,ORIG

rows={};overall={}
with zipfile.ZipFile(ORIG) as z:
 for m in ['01','02','06','07']:
  x=np.load(ROOT/f'R120_{m}_MULTICLOCK_GEOMETRY.npy',mmap_mode='r')
  pred=np.load(ROOT/f'R120_{m}_UNSUPERVISED_PHASES.npy',mmap_mode='r')
  with np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as v:
   y=v['truth'];side=v['side'];teacher=v['final_source_shadow_veto']
  phase=pred==11
  sessions={'asia':x[:,66].astype(bool),'london':x[:,72].astype(bool),'newyork':x[:,78].astype(bool),'offsession':~(x[:,66].astype(bool)|x[:,72].astype(bool)|x[:,78].astype(bool))}
  macro=x[:,55];micro=x[:,0]
  # Physically interpretable causal conditional regimes, no hindsight in feature construction.
  cohorts={}
  for sname,ss in sessions.items():
   for s,side_name in [(1,'buy'),(-1,'sell')]:
    for trend_name,tm in [('counter_30sec',macro<-.25),('flat_30sec',(-.25<=macro)&(macro<=.25)),('aligned_30sec',macro>.25)]:
     # each event evaluated across one or more overlapping sessions. Counts descriptive not unique summands across sessions.
     a=phase&ss&(side==s)&tm
     if int(a.sum())<200:continue
     cor=int(np.sum(a&(y==0)));bad=int(np.sum(a&(y!=0)))
     cohorts[f'{sname}|{side_name}|{trend_name}']={'n':cor+bad,'right':cor,'wrong':bad,'wrong_ratio':bad/max(cor,1),'wrong_percent':bad/(cor+bad)}
  rows[m]={
    'original_events':int(len(y)),'original_bad':int((y!=0).sum()),
    'phase11_right':int((phase&(y==0)).sum()),'phase11_wrong':int((phase&(y!=0)).sum()),
    'phase11_teacher_bad_overlap':int((phase&(y!=0)&teacher).sum()),
    'phase11_teacher_correct_overlap':int((phase&(y==0)&teacher).sum()),
    'cohorts':cohorts}
  print('RECOUNT',m,'P11',rows[m]['phase11_wrong'],rows[m]['phase11_right'],flush=True)
rr={}
for k in set(kk for v in rows.values() for kk in v['cohorts']):
 vals=[v['cohorts'].get(k) for v in rows.values()]
 if all(q and q['n']>=200 for q in vals):
  rr[k]={'across_four_wrong':sum(q['wrong'] for q in vals),'across_four_right':sum(q['right'] for q in vals),
   'min_month_bad_percent':min(q['wrong_percent'] for q in vals),
   'per_month':{m:rows[m]['cohorts'][k] for m in rows}}
output={'phase11':rows,'session_subgroups_fourmonth':rr,'historical_exposed':'All source four months have prior research outcome exposure. Cohorts are DESCRIPTIVE, not prespecified validated trade rules.'}
(ROOT/'R120_PHASE11_MULTI_SESSION_SOURCE_DESCRIPTIVE_AUDIT.json').write_text(json.dumps(output,indent=2))
for k,v in sorted(rr.items(),key=lambda kv:(kv[1]['min_month_bad_percent'],kv[1]['across_four_wrong']),reverse=True)[:8]:
 print(k,'bad',v['across_four_wrong'],'good',v['across_four_right'],'worst_m_percent',round(v['min_month_bad_percent'],3))