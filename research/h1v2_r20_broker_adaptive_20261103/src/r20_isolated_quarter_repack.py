"""R20-7 source-exact optimistic per-quarter cardinality proof.
Inputs original R19S3 nonoverlap future winner intervals and R20 fresh evaluated
first fill quote competing first-passage actions (including ones that collide
with original winners). Future-known and excludes other source candidate lanes;
may not infer universal impossibility or causal performance.
"""
from __future__ import annotations
import csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data');R20=ROOT/'h1v2_r20_last46'
sys.path.insert(0,str(R20/'src'))
import r20_residual_quote_hazard as model

SCENARIOS=('C1_ASOF_EVERY_DISTINCT_MS_CAP4000_H60_100MS',
 'C2_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_100MS',
 'C3_ASOF_EVERY_DISTINCT_MS_CAP8000_H30_100MS',
 'C4_ASOF_EVERY_DISTINCT_MS_CAP8000_H15_100MS',
 'C5_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_500MS_SLIP20',
 'C6_ASOF_FIRST25MS_CAP8000_H60_100MS')

def count_exact(starts,ends):
 if not len(starts):return 0
 if np.any(ends<=starts):raise ValueError('NONPOSITIVE_INTERVAL')
 order=np.lexsort((np.arange(len(starts)),starts,ends))
 n=0;last=-2**62
 for k in order:
  if starts[k]>last:n+=1;last=ends[k]
 return n

def run(source,mon):
 t,b,a,_,_,_,_=model.get_frozen(source,mon)
 refs=model.r18.refs_for_month(mon,ROOT);qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 oldf,olde,base_q,miss=model.get_old(source,mon,t,refs)
 paths=R20/'results';p=paths/f'R20_{source}_{mon}_ALL_SOURCE_CANDIDATE_DUAL_ACTION_AND_ADDED_WINNER_ORDINALS.npz'
 out=[]
 with np.load(p,allow_pickle=False) as z:
  for scenario in SCENARIOS:
   fills=z[scenario+'__first_observed_fill_ordinal']
   codes=z[scenario+'__future_buy_sell_codes']
   exits=z[scenario+'__first_passage_exit_ordinal']
   win=np.argwhere(codes==1)
   newf=fills[win[:,0]];newe=exits[win[:,0],win[:,1]]
   for q in miss:
    begin=int(qkeys[q])*900000;end=begin+900000
    oldmask=(t[oldf]>=begin)&(t[oldf]<end)
    newmask=(t[newf]>=begin)&(t[newf]<end)
    si=np.r_[oldf[oldmask],newf[newmask]];ei=np.r_[olde[oldmask],newe[newmask]]
    upper=count_exact(t[si],t[ei]);old=int(base_q[q]);ref=int(qref[q])
    out.append({'source':source,'month':mon,'scenario':scenario,'UTC_quarter':refs['rows'][q]['utc_quarter'],
      'R9_SYNTH_UTC_reference':ref,'R19S3_original_future_winners':old,
      'R20_new_independently_first_passage_good_intervals':int(newmask.sum()),
      'R20_original_incumbent_intervals':int(oldmask.sum()),
      'R20_isolated_optimistic_max_nonoverlap_count':upper,
      'optimistic_reference_feasible_within_this_RESTRICTED_intervals':int(upper>=ref),
      'minimum_isolated_deficit_IN_THIS_RESTRICTED_EVENT_UNIVERSE':max(0,ref-upper),
      'source_future_oracle_only':True,'other_quarter_busy_constraints_ignored':True,
      'this_is_NOT_universal_upper_for_all_possible_quotes_or_spreads':True})
 outpath=paths/f'R20_{source}_{mon}_ISOLATED_QUARTER_REPLACEMENT_UPPER_SIX_CONTRACTS.csv';model.write_csv(outpath,out) if out else outpath.write_text('source,month,scenario,UTC_quarter,R9_SYNTH_UTC_reference,R19S3_original_future_winners,R20_new_independently_first_passage_good_intervals,R20_original_incumbent_intervals,R20_isolated_optimistic_max_nonoverlap_count,optimistic_reference_feasible_within_this_RESTRICTED_intervals,minimum_isolated_deficit_IN_THIS_RESTRICTED_EVENT_UNIVERSE,source_future_oracle_only,other_quarter_busy_constraints_ignored,this_is_NOT_universal_upper_for_all_possible_quotes_or_spreads\n')
 rec={'source':source,'mon':mon,'source_sha':model.r18.PINS[source][mon],
  'failure_quarters':len(miss),'scenario_count':len(SCENARIOS),'rows':len(out),
  'cases':{scenario:{'upper_feasible_quarters':sum(r['optimistic_reference_feasible_within_this_RESTRICTED_intervals'] for r in out if r['scenario']==scenario),
   'min_isolated_deficit':sum(r['minimum_isolated_deficit_IN_THIS_RESTRICTED_EVENT_UNIVERSE'] for r in out if r['scenario']==scenario)} for scenario in SCENARIOS},
  'result_SHA':model.sha(outpath),'candidate_source_NPZ_SHA':model.sha(p),
  'no_mutation_original_or_future_asof_training':True}
 j=paths/f'R20_{source}_{mon}_ISOLATED_REPLACEMENT_RECEIPT.json';j.write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps(rec),flush=True);return rec

if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--source',choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'),required=True)
 a.add_argument('--month',choices=('01','02','06','07'),required=True);p=a.parse_args();run(p.source,p.month)
