"""Resume only FROZEN R152 June/July inference; never recalibrate after February."""
import json,joblib,gc
from r152_fit_freeze_action_portfolio import ROOT,HEADS,load,infer,evaluate
models={h:joblib.load(ROOT/f'R152_{h}_JAN_FROZEN.joblib') for h in HEADS}
cal={h:joblib.load(ROOT/f'R152_{h}_FEB_CAL_FROZEN.joblib') for h in HEADS}
policies=json.loads((ROOT/'R152_FEB_FROZEN_POLICIES.json').read_text())
rows=[]
for m in ['01','02','06','07']:
 p=ROOT/f'R152_DK_{m}_FROZEN_POLICY_EVAL.json'
 if p.exists():
  rows.append(json.loads(p.read_text()));print('EXISTING_FROZEN',m,flush=True);continue
 d=load(m);pred=infer(models,cal,d);rows.append(evaluate(d,pred,policies,m))
 del d,pred;gc.collect()
(ROOT/'R152_FROZEN_FOUR_MONTH_RESULTS.json').write_text(json.dumps(rows,indent=2))
print('R152_FROZEN_FOUR_MONTHS_COMPLETED',flush=True)