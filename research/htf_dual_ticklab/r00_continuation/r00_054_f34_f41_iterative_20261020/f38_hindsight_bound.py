"""F38 retrospective score-rank diagnostic for NEW causal models, never a deployable decision rule."""
from pathlib import Path
import json,numpy as np
ROOT=Path('/mnt/data');P=ROOT/'R00_054_F38_CAUSAL_SCORE_GEOMETRY_20261020';P.mkdir(exist_ok=True)
sources=[ROOT/'R00_054_F35_CAUSAL_STRUCTURE_PHASE_20261020', ROOT/'R00_054_F37_JANFEBJUNE_CAUSAL_TRANSFER_20261020']
records=[]
for f in sources:
  for file in sorted(set(f.glob('*SCORES_*.npz')) | set(f.glob('*SOURCE_EVENT_SCORES.npz'))):
    with np.load(file) as v:
      y=v['y'];score=v['p'];t=v['t'];side=v['side']
    good=y==0;bad=~good
    assert len(y)>100000 and len(y)==len(score)==len(t)==len(side)
    for ret in (.71,.80,.90,.95,.99):
      cut=np.quantile(score[good],1-ret,method='lower');m=score>=cut
      records.append(dict(source=f.name,source_filename=file.name,desired_correct_retention=ret,oracle_cutoff=float(cut),actual_correct_retention=float(m[good].mean()),oracle_incorrect_rejection=float((~m[bad]).mean()),original_total=int(len(y)),correct_total=int(good.sum()),bad_total=int(bad.sum()),is_tradeable=False,invalid_reason='uses contemporaneous evaluation class label distribution to choose oracle threshold'))
(P/'F38_FULL_OPTIMISTIC_GEOMETRY_AND_ALL_FAILS.json').write_text(json.dumps(records,indent=2)+'\n')
for r in records:
 if r['desired_correct_retention']==.71:print(r['source_filename'],round(r['oracle_incorrect_rejection'],4))
print('F38',len(records),'diagnostic rows; NOT SCORED POLICY',flush=True)