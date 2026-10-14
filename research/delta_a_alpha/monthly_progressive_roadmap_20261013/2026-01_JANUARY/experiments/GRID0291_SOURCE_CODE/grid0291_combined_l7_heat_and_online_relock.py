"""GRID0291 combined L7 source-heat cap + source-specific online paid-loss re-lock.
Research only, original January Dukascopy, frozen GRID0283 original paid parent.
"""
from pathlib import Path
import json,time
import grid0290_funded_portfolio_source_heat_cap as a
HERE=Path(__file__).resolve().parent

def main():
 t0=time.perf_counter();t,bid,ask,z,kind,owner,pgid,r9,origin=a.materialize()
 configs=[('CAP1_PAUSE2_5MIN',1,2,300000),('CAP2_PAUSE1_3MIN',2,1,180000),('CAP2_PAUSE2_3MIN',2,2,180000),('CAP2_PAUSE2_5MIN',2,2,300000),('CAP2_PAUSE3_5MIN',2,3,300000),('CAP2_PAUSE2_10MIN',2,2,600000),('CAP3_PAUSE2_5MIN',3,2,300000)]
 results=[]
 for name,cap,loss,pause in configs:
  r=a.physical_replay(t,bid,ask,z,kind,owner,pgid,r9,cash=100000.,cap=256,loss_pause_n=loss,pause_ms=pause,native16_cap=cap)
  r['name']=name;results.append(r)
  neg=[(d,round(v['net'],3)) for d,v in r['daily'].items() if v['net']<=0]
  wkbad=[(w,round(v['net'],3)) for w,v in r['weekly'].items() if v['net']<=0]
  print(name,'net',round(r['net'],3),'gl',round(r['gross_loss'],3),'equitydd',round(r['max_all_tick_floating_equity_dd'],3),'n',r['trades'],'positive_days',21-len(neg),'positiveweeks',5-len(wkbad),'R9days',r['r9_synth_days_net_met'],'R9weeks',r['r9_synth_weeks_net_met'],'negdays',neg,'parent',r['verified_parent'],'child',r['verified_child'],flush=True)
 data={'id':'GRID0291_CAUSAL_SOURCE_SPECIFIC_PHYSICAL_CAP_PLUS_BOOKED_LOSS_PAUSE',
  'data_sha256':a.back.SRC_SHA,
  'claim':'Two complementary current-source known risk controls; NO day/week calendar labels used in strategy, only external performance ledger.',
  'source_prior':'GRID0283 original paid-child Watchdog full-tick candidate research; GRID0290 per-source physical cap; GRID0288 on-line source-funded loss pause',
  'limitations':['January in-sample research, not holdout, not source-regenerated full production FourSessionV1','Neither reference R9 SYNTH performance row nor R9 OVERFIT future teacher read by execution loop','Underlying normal session candidate sources still historically pre-selected','High $100k research cash and 500 leverage not small capital','No underlying broker evidence, cost schedule verification or slippage','No acceptance until R9 daily and ISO weekly per-period net AND volume/grossloss/equity DD, R9 OVERFIT six offline dimensions, Jan-July cross-month regression and owner QC'],
  'results':results,'elapsed_seconds':time.perf_counter()-t0}
 file=HERE/'grid0291_combined_heat_paid_loss_full_tick_results.json';file.write_text(json.dumps(data,indent=2));print('SAVED',file,'seconds',round(time.perf_counter()-t0,1))
if __name__=='__main__':main()
