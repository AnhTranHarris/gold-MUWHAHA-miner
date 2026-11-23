from pathlib import Path
import json,numpy as np,pandas as pd,lightgbm as lgb
R=Path(__file__).parent;orig=pd.read_csv('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
a=pd.read_csv(R/'r05_exit_teacher.csv.gz');model=lgb.Booster(model_file=str(R/'r05_exit_hazard_lgb.txt'))
features=json.loads((R/'r05_fit_receipt.json').read_text())['exit']['features'];a['p_exit']=model.predict(a[features].to_numpy('float32'),num_threads=4)
r=[]
for name,cond in [('phase_exit',lambda g:(g.p_exit>=.4)&(g.age>0)),('phase_fee_positive',lambda g:(g.p_exit>=.4)&(g.mark_c>2)&(g.age>0)),('first_fee_passage',lambda g:(g.mark_c>2)&(g.age>0))]:
 z=a[cond(a)].groupby('ref_id').head(1).copy();picked=z.set_index('ref_id')[['sec','mark_c']];fallback=a.groupby('ref_id').tail(1).set_index('ref_id')[['sec','mark_c']]
 chosen=fallback.copy();chosen.update(picked)
 refid=chosen.index.to_numpy('int64');ex=orig.iloc[refid].exit_sec.to_numpy();original_pos=(orig.iloc[refid].original_booked_net_usd.to_numpy()>0);net=chosen.mark_c.to_numpy()-2
 r.append({'mode':name,'original_forced_entries':len(refid),'original_profitable_refs':int(original_pos.sum()),'timing_within_2s':int((np.abs(chosen.sec.to_numpy()-ex)<=2).sum()),'original_winners_fee_positive_and_exit_2s':int((original_pos&(net>0)&(np.abs(chosen.sec.to_numpy()-ex)<=2)).sum()),'fee_positive':int((net>0).sum()),'net_cash_usd':round(float(net.sum())/100,2),'unknown_1003_ignored':True})
print('FORCED_REFERENCE_PROBE',json.dumps(r,indent=2))
rows=[]
for fname in ['r05_joint_mode0.csv','r05_joint_mode1.csv','r05_joint_mode9.csv','r05_joint_mode10.csv']:
 d=pd.read_csv(R/fname);out={'mode':fname}
 for leg in (1,2):
  o=orig[orig.leg==leg].copy();o['minute_id']=o.entry_sec//60
  g=d[d.leg==leg].copy();g=g.drop_duplicates('minute_id').set_index('minute_id')
  x=o.join(g,on='minute_id',rsuffix='_generated');ent=(x.entry_time_msc//1000)
  same=x.side_generated.to_numpy()==np.where(x.side=='BUY',1,-1)
  for tol in (2,5):out[f'leg{leg}_same_side_entry_{tol}s']=int((same&(abs(ent-x.entry_sec)<=tol)).sum())
  out[f'original_leg{leg}']=len(o);out[f'generated_leg{leg}']=len(g);out[f'original_leg{leg}_same_minute_generated']=int(x.entry_time_msc.notna().sum())
 rows.append(out)
print('ENTRY_ALIGNMENT',json.dumps(rows,indent=2))
(R/'R05_DECOMPOSITION.json').write_text(json.dumps({'source_only_forced_original_entry_diagnostic_not_executable':r,'independent_entry_alignment':rows},indent=2))
