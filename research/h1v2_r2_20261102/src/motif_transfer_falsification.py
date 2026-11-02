"""H1V2 R2 falsification: H1V2 quote-only causal geometric motifs.

G4 tests motif against G0 at identical complexity with ALL months in training.
G5 trains on Jan/Feb/Jun, freezes then evaluates July without admission retuning.
All model predictions are diagnostics. No on-policy replay or trading.
"""
import json,hashlib,time
from pathlib import Path
import numpy as np
import lightgbm as lgb
from insample_skew_experiments import load,causal_interactions,evaluate
O=Path('/mnt/data/h1v2_r2/results')

def go():
 x,y,ts,month=load();z=causal_interactions(x,ts)
 out={'source':'60k actual as-of sampled quotes, Dukascopy JanFebJunJul','features':z.shape[1],
 'hypothesis':'Ordered multi-scale impulse/reversal and bid/ask lead-lag interactions reject neutral and wrong-sided outcomes better than raw geometry',
 'results':{},'status':'RESEARCH_FALSIFICATION_ONLY'}
 params=dict(objective='multiclass',num_class=3,verbosity=-1,force_col_wise=True,num_threads=4,seed=20261102,feature_fraction=1.)
 experiments=[('G4_same_small_capacity_motifs',np.ones(len(y),dtype=bool),70,15,90),
 ('G5_july_never_trained_motifs',month!='07',170,31,40)]
 for name,train_mask,rounds,leaves,minimum in experiments:
  t0=time.monotonic()
  model=lgb.train({**params,'num_leaves':leaves,'min_data_in_leaf':minimum,'learning_rate':.09},lgb.Dataset(z[train_mask],label=y[train_mask]),num_boost_round=rounds)
  prob=model.predict(z,num_threads=4)
  subset={'all_sample':evaluate(prob,y,month)} if train_mask.all() else {
   'train_only':evaluate(prob[train_mask],y[train_mask],month[train_mask]),
   'july_untouched':evaluate(prob[~train_mask],y[~train_mask],month[~train_mask])}
  path=O/f'{name}.txt';model.save_model(str(path))
  with path.open('rb') as fh:sha=hashlib.file_digest(fh,'sha256').hexdigest()
  out['results'][name]={'num_trees':rounds,'num_leaves':leaves,'train_rows':int(train_mask.sum()),'eval_rows':int((~train_mask).sum()),
   'sha256':sha,'artifact':path.name,'seconds':round(time.monotonic()-t0,2),'metrics':subset}
  (O/'H1V2_R2_MOTIF_FALSIFICATION.json').write_text(json.dumps(out,indent=2))
  print(json.dumps({'name':name,'seconds':out['results'][name]['seconds'],'train_at_0.5':subset.get('train_only',subset.get('all_sample'))['0.5'],
    'july_at_0.5':subset.get('july_untouched',{}).get('0.5',None)}),flush=True)
 return out
if __name__=='__main__':go()
