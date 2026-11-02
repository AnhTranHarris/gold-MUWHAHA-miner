"""R7 full four-month causal-grid ranking and quote-ordinal single-position replay.

Side/entry choice is from model trained on named months. Only AFTER selection do
original immutable H1V2 per-side trade outcomes enter the audit. All-four fit
means explicitly in-sample selection. Holdout is LOMO descriptive, not deployed.
"""
from __future__ import annotations
import json, pathlib, numpy as np
from full_population_nested_regime import MONTHS,OUT,ORIGINAL,score_cells,wilson,N_BINS
from h1v2_teacher import SYNTH

FRACTIONS=(.0001,.0005,.001,.005,.01,.05)

def model_gate(train,fraction,min_n=30):
 s,ntr,_,_,_,_,_=score_cells(train,())
 side=np.argmax(s,axis=1)
 best=s[np.arange(len(side)),side]
 valid=ntr>=min_n
 order=np.argsort(-best,kind='stable')
 order=order[valid[order]]
 if len(order)==0:return np.zeros(len(ntr),bool),side,0.,0
 cumulative=np.cumsum(ntr[order])
 target=np.maximum(1,int(ntr.sum()*fraction))
 k=min(len(order)-1,int(np.searchsorted(cumulative,target)))
 used=order[:k+1]
 mask=np.zeros(len(ntr),bool);mask[used]=True
 return mask,side,float(best[used[-1]]),int(ntr[used].sum())

def replay_month(mon,eligible_bins,side,regime_path=None):
 with np.load(regime_path or (OUT/f'R7_FULL_REGIME_{mon}.npz'),allow_pickle=False) as d:
  bins=d['regime'].copy();idx=d['ix'].copy()
 with np.load(ORIGINAL/f'h1v2_dukascopy_{mon}_oracle_labels.npz',allow_pickle=False) as d:
  assert np.array_equal(idx,d['tick_index'])
  z=d['code'].copy();nets=d['net'].copy();exitidx=d['exit_tick_index'].copy()
 chosen=np.flatnonzero(eligible_bins[bins]);signals=len(chosen)
 if signals==0:return {'signal_candidates':0,'replayed_trades':0,'correct':0,'incorrect':0,'neutral':0,'precision':None,'model_net':0.,'max_closed_equity_drawdown':0.,'r9_synth_count':SYNTH[mon]}
 wants=side[bins[chosen]]
 classes=z[chosen,wants];good=int((classes==1).sum());neu=int((classes==0).sum());wrong=int((classes==-1).sum())
 # One position at a time, quote ordinal strictly after prior EXIT; no special
 # hindsight skip of losing executions; actual R9 exact historical exit is used.
 count=0;w=0;q=0;bad=0;unscorable=0;total=0.;eq=0.;peak=0.;max_dd=0.;lastexit=-1
 for row,wanted in zip(chosen,wants):
  opening=int(idx[row]);
  if opening<=lastexit:continue
  x=int(exitidx[row,wanted]);
  if x<=opening or not np.isfinite(nets[row,wanted]):
   # Original H1V2 has -1/Nan at tail when no future quote allows completion.
   # Unknown outcome is never a win/loss and is not fed into a model; leave it unscorable.
   unscorable+=1;continue
  value=float(nets[row,wanted]);
  lastexit=x;count+=1;total+=value;eq+=value;peak=max(peak,eq);max_dd=max(max_dd,peak-eq)
  if z[row,wanted]==1:w+=1
  elif z[row,wanted]==0:q+=1
  else:bad+=1
 assert count==w+q+bad and signals==good+neu+wrong
 return {'signal_candidates':int(signals),'signals_strict_good':good,'signals_neutral':neu,'signals_wrong':wrong,
     'signals_strict_precision':float(good/signals),
     'replayed_trades':count,'unscorable_source_boundary_events':unscorable,'correct':w,'incorrect':bad,'neutral':q,'precision':float(w/count),
     'model_net':round(total,3),'max_closed_equity_drawdown':round(max_dd,3),'r9_synth_count':SYNTH[mon],
     'r9_synth_volume_fraction':float(count/SYNTH[mon]),
     'scope':'DELIBERATE IN-SAMPLE RESEARCH or LOMO CAUSAL GRID; hypothetical original Dukascopy executions NO LATENCY/SLIPPAGE'}

def run():
 report={'science':'FULL 15.4m asof candidates; trained categorical model side+WAIT; one-position original R9 exact exit replays, NOT real trade performance',
  'fractions':list(FRACTIONS),'experiments':[]}
 fits=[('FOUR_MONTH_FIT_CONTAMINATED',MONTHS,MONTHS)]+[(f'LOMO_{m}',tuple(x for x in MONTHS if x!=m),(m,)) for m in MONTHS]
 for name,train,valid in fits:
  d={'name':name,'train_months':list(train),'evaluation_months':list(valid),'fractions':{}}
  for fraction in FRACTIONS:
   g,side,threshold,train_coverage=model_gate(train,fraction)
   key=str(fraction)
   d['fractions'][key]={'trained_regimes':int(g.sum()),'frozen_threshold_approx':threshold,'train_population_estimate':train_coverage,'months':{}}
   for mon in valid:
    d['fractions'][key]['months'][mon]=replay_month(mon,g,side)
   print('DONE',name,fraction,[(m,v['replayed_trades'],round(v['precision'] or 0,4)) for m,v in d['fractions'][key]['months'].items()],flush=True)
  report['experiments'].append(d)
  (OUT/f'R7_{name}_PERF_RECEIPT.json').write_text(json.dumps(d,indent=2))
 (OUT/'R7_EXHAUSTIVE_RANKED_TICK_REPLAY.json').write_text(json.dumps(report,indent=2))
 return report

if __name__=='__main__':run()
