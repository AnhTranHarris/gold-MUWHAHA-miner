from pathlib import Path
import csv,sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import r13_crossbroker_horizon_lanes as r
import r13_asof_dynamic_horizon_router as dyn


def test_dynamic_horizon_is_only_past_observed_spread_and_price_displacement():
 s=np.array([200,3000,3100],dtype=np.int32)
 e=np.array([200.,4000.,4000.]);mb=np.array([700,0,0],np.int32);ma=np.array([700,0,0],np.int32)
 h=dyn.dynamic_prefix_choice(s,e,mb,ma)
 assert h.tolist()==[5000,30000,30000]
 mb[:]=0;ma[:]=0
 assert dyn.dynamic_prefix_choice(s,e,mb,ma).tolist()==[15000,30000,30000]


def test_three_source_adaptive_original_strict_label_and_position_order():
 for source in r.EXPECTED:
  p=r.OUT/f'R13_{source}_ADAPTIVE_ASOF_HORIZON_V1_ALL_TRADE_ORDINALS.csv'
  if not p.exists(): continue
  a=list(csv.DictReader(p.open(newline='')))
  assert a and all(v['satisfies_original_first15_safe_full30']=='True' for v in a)
  starts=np.array([int(v['entry_UTC_ms']) for v in a],dtype=np.int64)
  ends=np.array([int(v['exit_UTC_ms']) for v in a],dtype=np.int64)
  assert np.all(starts[1:]>ends[:-1])
  assert set(int(v['horizon_source_only_asof_ms']) for v in a).issubset({5000,15000,30000})
  for v in a:
   sd=int(v['side_future_selected']);bid=int(v['entry_bid_raw']);ask=int(v['entry_ask_raw'])
   eb=int(v['exit_bid_raw']);ea=int(v['exit_ask_raw'])
   actual=(eb-ask-20) if sd>0 else (bid-ea-20)
   assert actual==int(v['source_price_path_net_after_0p02_fee_raw'])>=100


def test_dynamic_stress_all_scenarios_and_quarters_reconcile():
 scenarios=r.OUT/'R13_ALL_27_ASOF_DYNAMIC_HORIZON_DELAY_SCENARIOS.csv'
 quarters=r.OUT/'R13_ALL_108_ASOF_DYNAMIC_HORIZON_DELAY_QUARTERS.csv'
 if not scenarios.exists():return
 rr=list(csv.DictReader(scenarios.open(newline='')))
 qq=list(csv.DictReader(quarters.open(newline='')))
 assert len(rr)==27 and len(qq)==108
 for r1 in rr:
  vals=[int(r1[k]) for k in ('good_delayed_fill_strict15','bad_delayed_fill_strict15','source_censored','quote_spread_rejected','position_busy_skip')]
  assert sum(vals)==int(r1['source_future_oracle_initial_qualified'])
  parts=[v for v in qq if (v['source'],v['lag_ms'],v['per_leg_slip_raw'])==(r1['source'],r1['lag_ms'],r1['per_leg_slip_raw'])]
  assert len(parts)==4
  assert sum(int(v['good_completed']) for v in parts)==vals[0]
  assert sum(int(v['bad_completed']) for v in parts)==vals[1]
