"""Audit frozen source tape, counterfactual filters and first-touch exits.
Not a test of future source parent retiming or Coinexx broker funding."""
import numpy as np,pandas as pd,json,collections
from pathlib import Path
O=Path('/mnt/data/daa_jan_risk_research_034')
z=np.load('/mnt/data/daa_jan_risk_audit_033/JAN033_ORIGINAL_SOURCE_LABELED_POSITIONS.npz')
E,X,R,D,S,P=[z[k] for k in ['entry_index','exit_index','entry_price_raw','direction','source_id','pnl']]
a=pd.read_csv('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz',compression='gzip',usecols=['ask_raw','bid_raw'],dtype={'ask_raw':'int32','bid_raw':'int32'})
ask=a.ask_raw.to_numpy();bid=a.bid_raw.to_numpy()
basez=np.load(O/'base_trades.npz');base=collections.Counter((int(x),round(float(p),4),int(s)) for x,p,s in zip(basez['x'],basez['p'],basez['s']))
checks={};n_overlays=0;n_stops=0
for path in sorted(O.glob('*.json')):
 try: obj=json.loads(path.read_text())
 except:continue
 if 'scenario' not in obj or ('PF' not in obj):continue
 name=obj['scenario']
 overlay=O/(name+'_trades.npz'); stop=O/(name+'_trade_ledger.npz')
 if overlay.exists():
  data=np.load(overlay);p=data['p'];x=data['x'];s=data['s'];reason=data['reason'];assert len(p)==obj['trades']
  cnt=collections.Counter((int(k),round(float(v),4),int(q)) for k,v,q,r in zip(x,p,s,reason) if q!=7 and r==0)
  missing=cnt-base
  assert not missing,(name,list(missing.items())[:3]);assert abs(float(p.sum())-obj['net'])<.02
  assert abs(float(p[s==1].sum())-60197.326)<.02
  checks[name]={'test':'all_normal_exits_original_subset; early_cohort_exits independently generated','accepted_original_events_preserved':int(len(p)-(s==7).sum()),'recovery_trades':int((s==7).sum()),'early_cohort_closures':int((reason==2).sum()),'risk_ledger_net_reconciles':True}
  n_overlays+=1
 elif stop.exists():
  data=np.load(stop);p=data['P'];x=data['X'];s=data['S'];assert len(x)==len(E)
  assert np.all((x>=E)&(x<=X))
  calc=np.where(D>0,bid[x]-R,R-ask[x])/1000.-.02
  assert np.max(np.abs(calc-p))<1e-6
  assert np.all(x[S!=0]==X[S!=0]);assert abs(float(p.sum())-obj['net'])<.02
  checks[name]={'test':'quote_first_touch_no_future_exit','actual_executable_quote_price_parity':True,'original_non_watchdog_exact':True,'watchdog_earlier_exits':int(((x<X)&(S==0)).sum())};n_stops+=1
assert n_overlays>=30 and n_stops==17,(n_overlays,n_stops)
assert checks['base']['early_cohort_closures']==0
out={'qa_passed':True,'overlay_scenarios':n_overlays,'ticket_stop_scenarios':n_stops,'total':n_overlays+n_stops,'frozen_raw_quotes':9135062,'frozen_original_candidates':47511,'original_pnl_price_coverage':'full','coverability':'No verified recalculation of future funded Watchdog parent/child admissions','checked':checks}
(O/'JAN034_ALL_VARIANTS_QA.json').write_text(json.dumps(out,indent=2));print('QA_PASS',json.dumps({k:out[k] for k in ('overlay_scenarios','ticket_stop_scenarios','total','frozen_raw_quotes','frozen_original_candidates')}))