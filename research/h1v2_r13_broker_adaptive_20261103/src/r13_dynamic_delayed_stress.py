"""Independent delayed stress for past-only horizon chooser, future-optimal action.

Model-free geometric after quote, 3 source x 3 lag x3 friction, all 4 quarters.
The adaptive horizon is fixed from prefix observed quotes, but the source
entry and side are still OMNISCIENT. A full30 safety condition remains for every
entry, and original 15s class is reported independently. No account P&L.
"""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
import r13_crossbroker_horizon_lanes as r
import r13_delayed_executable_stress as stress


def run():
 rows=[];qrows=[]
 for name in r.EXPECTED:
  t,b,a,pin=r.load_source(name)
  path=r.OUT/f'R13_{name}_ADAPTIVE_ASOF_HORIZON_V1_ALL_TRADE_ORDINALS.csv'
  traces=list(csv.DictReader(path.open(newline='')))
  ix=np.array([int(x['entry_source_quote_ordinal']) for x in traces],dtype=np.int64)
  side=np.array([int(x['side_future_selected']) for x in traces],dtype=np.int8)
  assert np.all(np.diff(t[ix])>0)
  assert all(x['satisfies_original_first15_safe_full30']=='True' for x in traces)
  for lag in (0,100,500):
   for slip in (0,20,50):
    out,fill,exit_,net=stress.stressed_frozen_signal(t,b,a,ix,side,lag,slip,4000)
    if lag==0 and slip==0: assert np.count_nonzero(out!=1)==0
    good=(out==1).sum();bad=(out==0).sum();den=good+bad
    row={'source':name,'horizon_ASOF_then_future_entry':True,'lag_ms':lag,'per_leg_slip_raw':slip,
       'source_future_oracle_initial_qualified':len(ix),'good_delayed_fill_strict15':int(good),
       'bad_delayed_fill_strict15':int(bad),'source_censored':int((out==-3).sum()),
       'quote_spread_rejected':int((out==-1).sum()),'position_busy_skip':int((out==-2).sum()),
       'accuracy_completed':float(good/den) if den else None,
       'strict_correct_count_hour_ge104':bool(good>=104),'joint_hour_strict_correct_ge80_and_count104':bool(good>=104 and den>0 and good/den>=.8),
       'source_raw_sha256':pin,'not_predictive':True}
    rows.append(row)
    save=r.OUT/f'R13_{name}_DYNAMIC_HORIZON_STRESS_lag{lag}_slip{slip}_ALL_ORDINALS.npz'
    np.savez_compressed(save,signal_source_quote_ordinal=ix,signal_side_future_selected=side,
     delayed_fill_quote_ordinal=fill,observed_first_tp_exit_quote_ordinal=exit_,
     delayed_strict_outcome=out,strict_good_net_raw_only=net)
    for q in range(4):
     start=r.T0+q*900000;mask=(fill>=0)&(t[np.maximum(fill,0)]>=start)&(t[np.maximum(fill,0)]<start+900000)
     g=int(np.count_nonzero(mask&(out==1)));bads=int(np.count_nonzero(mask&(out==0)))
     target=(28,27,25,24)[q]
     qrows.append({'source':name,'lag_ms':lag,'per_leg_slip_raw':slip,
       'quarter_utc':__import__('datetime').datetime.fromtimestamp(start/1000,__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:00Z'),
       'r9_SYNTH_ref':target,'good_completed':g,'bad_completed':bads,
       'accuracy_completed':g/(g+bads) if g+bads else None,'joint':bool(g>=target and g/(g+bads)>=.8 if g+bads else False),
       'selection_future_omniscient':True})
  print(name,'completed 9 delay scenarios',flush=True)
 assert len(rows)==27 and len(qrows)==108
 r.write_csv(r.OUT/'R13_ALL_27_ASOF_DYNAMIC_HORIZON_DELAY_SCENARIOS.csv',rows)
 r.write_csv(r.OUT/'R13_ALL_108_ASOF_DYNAMIC_HORIZON_DELAY_QUARTERS.csv',qrows)
 return rows
if __name__=='__main__':
 for row in run():
  if row['lag_ms']==100 and row['per_leg_slip_raw']==0: print(json.dumps(row,indent=2))
