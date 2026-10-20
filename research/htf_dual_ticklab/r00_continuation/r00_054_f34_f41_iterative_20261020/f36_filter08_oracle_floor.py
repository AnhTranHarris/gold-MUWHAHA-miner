from pathlib import Path
from zipfile import ZipFile
import sys,io,json,numpy as np
R=Path('/mnt/data');sys.path.insert(0,str(R/'R00_054_F30_ITERATIVE_CAUSAL_FILTER_20261020'))
import F27_PARENT_READONLY_SOURCE as src
z=ZipFile(R/'R00_054_FILTER08_FOUR_MONTH_70PCT_OVERFIT_RESEARCH_20261019.zip')
refs=src.r9_reference();d={};cuts=[]
for m in ('01','02','06','07'):
 for b in ('coinexx','dukascopy'):
  with np.load(io.BytesIO(z.read(f'FILTER08/FITTED_CLASSIFIER_SCORES_{b}_{m}.npz'))) as a:
   y=a['truth_class'];p=a['score'];good=y==0
   assert (good==a['kept']).__class__ is np.ndarray  # not same outcomes; just verify interface
   cut=float(np.quantile(p[good],.29,method='lower'));cuts.append(cut)
   d[(b,m)]=(cut,p.copy(),y.copy(),a['t'].copy(),a['original_side'].copy())
cut=min(cuts)
print('global oracle min positive q29 cutoff',cut,flush=True)
rows=[]
for (b,m),(local,p,y,t,s) in d.items():
 c=src.load_one(b,m)
 assert np.array_equal(t,c['t']) and np.array_equal(s,c['side']) and np.array_equal(y,c['y'])
 mask=p>=cut
 q=src.quota_stats(c,mask,refs)
 g=y==0;bad=~g
 row={'broker':b,'month':m,'local_oracle_q29':local,'common_oracle_threshold':cut,'correct_total':int(g.sum()),'bad_total':int(bad.sum()),'correct_retained':int((g&mask).sum()),'bad_removed':int((bad&~mask).sum()),'correct_retention':float(mask[g].mean()),'incorrect_rejection':float((~mask[bad]).mean()),'new_quota_fails':{v:len(q[v]) for v in ('newly_failed_hours','newly_failed_days','newly_failed_weeks','newly_failed_months')}}
 rows.append(row);print(b,m,'ret',round(row['correct_retention'],5),'rej',round(row['incorrect_rejection'],5),'quota',row['new_quota_fails'],flush=True)
P=R/'R00_054_F36_RETROSPECTIVE_TEACHER_PROOF_20261020';P.mkdir(exist_ok=True)
summary={'circular_contamination_warning':'Every raw FILTER08 score was predicted by a teacher trained using that evaluation broker-month own future labels. The common threshold itself was derived from all eight original evaluation-month correct-label quantiles. This is an UNTRADEABLE in-sample feasibility demonstration, NEVER a blind result.','source':'Original FILTER08 exact preserved per-event score, time, side, truth + original eight caches; same event identity and R9 hour/day/week/month quotas','common_threshold':cut,'rows':rows,'aggregate':{'good_total':sum(r['correct_total'] for r in rows),'bad_total':sum(r['bad_total'] for r in rows),'good_kept':sum(r['correct_retained'] for r in rows),'bad_removed':sum(r['bad_removed'] for r in rows),'all_months_hit_71_90_without_quota_misses':all(r['correct_retention']>=.71 and r['incorrect_rejection']>=.90 and not any(r['new_quota_fails'].values()) for r in rows)}}
summary['aggregate']['correct_retention']=summary['aggregate']['good_kept']/summary['aggregate']['good_total'];summary['aggregate']['incorrect_rejection']=summary['aggregate']['bad_removed']/summary['aggregate']['bad_total'];
(P/'F36_SOURCE_EXACT_RETROSPECTIVE_TEACHER_ORACLE.json').write_text(json.dumps(summary,indent=2)+'\n');print('FINISHED',json.dumps(summary['aggregate'],indent=2),flush=True)