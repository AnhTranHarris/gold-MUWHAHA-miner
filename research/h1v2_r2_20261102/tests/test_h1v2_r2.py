import sys,math,json
from pathlib import Path
sys.path.insert(0,'/mnt/data/h1v2_r2/src')
import numpy as np
import quality_frontier as q
import hard_negative_teacher as h
import freeze_strict_fast_teacher as f

def test_quality_grid_original_monthly_floor():
 a=q.run();assert a['tested_grid']==144 and a['passing_grid']==42
 assert any(x['every_month_floor_pass'] and x['first_hit_max_ms']==3000 and x['net_min']==.1 and x['spread_max']==1.0 for x in a['all'])

def test_fast_two_hindsight_teacher_configs_keep_original_tick_nonoverlap():
 result=f.run()
 for name,v in result['configurations'].items():
  assert v['all_months_pass']
  for m,x in v['months'].items():
   assert x['count']>=math.ceil(.8*f.SYNTH[m])
   with np.load(f.OUT/x['output']) as z:
    assert len(z['side'])==x['count']
    assert set(np.unique(z['side']))=={-1,1}
    assert np.all(z['entry_tick_ix'][1:]>z['exit_tick_ix'][:-1])

def test_future_labels_excluded_from_model_inputs():
 for m in h.SYNTH:
  with np.load(h.OUT/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz') as d:
   X=d['X'];classed=d['side_class'];assert X.shape==(15000,100)
   assert classed.shape==(15000,2)
   assert np.all(np.isfinite(X)) and np.all(np.isin(classed,[0,1,2,3]))
   assert not np.any((classed==3).all(axis=1))

def test_hard_label_exact_source_mapping():
 # verify across all source months against their frozen full H1V2 teacher
 for m in h.SYNTH:
  with np.load(h.OUT/f'H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz') as d:
   indices=d['original_row'];y=d['y_original'];classes=d['side_class'];X=d['X']
   with np.load(h.ROOT/f'h1v2_dukascopy_{m}_oracle_labels.npz') as z:
    assert np.array_equal(z['tick_index'][indices],d['ix'])
    cls=z['code'][indices]
    assert np.array_equal(y,np.where(cls[:,0]==1,1,np.where(cls[:,1]==1,2,0)))
    assert np.array_equal(classes==3,(cls==1)&(z['net'][indices]>=.10)&(z['first_event_ms'][indices]>=0)&(z['first_event_ms'][indices]<=3000)&(X[:,99:100]<=1.+1e-5))

def test_overfit_does_not_claim_frozen_policy():
 p=json.loads((h.OUT/'H1V2_R2_ACTION_SELECTIVITY.json').read_text())
 assert p['side_action_rows']==120000
 train=p['models']['S1_overfit_all_4']['training']['0.3']
 assert train['n']==3219 and train['strong_correct']==3219 and train['wrong']==0 and train['neutral']==0
 july=p['models']['S2_leave_july_out']['by_month']['07']['0.1']
 assert july['n']==252 and july['strong_correct']==9 and july['wrong']==216
