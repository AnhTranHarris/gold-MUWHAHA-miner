"""R12Q: source-exact, STRICT-LABEL, COUNT-NEUTRAL 15m coverage improvement.

This repair of a single *future-informed* global earliest-finish oracle's
quarter-hour allocation is NOT a causal inference model. It preserves the full
R11S1 GOOD15+SAFE30 entry label and first executable TP quote for new trades.
Original R12 max-count trace, R11S4, raw data and EA never modified.
"""
from __future__ import annotations
import csv,datetime as dt,json
from collections import Counter
from pathlib import Path
import numpy as np
from r12_tp_oracle import (load_labels,read_raw,quote_tp_first,earliest_finish_schedule,
                           sha,write_csv,quarter_key,hour_key)
ROOT=Path('/mnt/data/h1v2_r12/results')
MON='02';QUARTER='2026-02-16T13:00:00Z';BEFORE='2026-02-16T12:45:00Z'

def main():
 qstart=int(dt.datetime.strptime(QUARTER,'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
 qend=qstart+900000
 frozen=list(csv.DictReader(open(ROOT/f'R12_{MON}_ALL_EXECUTABLE_FIRSTTP_SELECTED_SOURCE_QUOTE_TRACES.csv',encoding='utf8',newline='')))
 assert len(frozen)==82027
 old=[r for r in frozen if qstart<=int(r['entry_utc_ms'])<qend]
 assert len(old)==10
 before=[r for r in frozen if int(r['entry_utc_ms'])<qstart]
 after=[r for r in frozen if int(r['entry_utc_ms'])>=qend]
 prev=before[-1];prevprev=before[-2]
 assert prev['entry_utc_quarter']==BEFORE and int(prev['exit_utc_ms'])>=qstart
 assert int(prevprev['exit_utc_ms'])<qstart
 assert len(before)+len(old)+len(after)==len(frozen)
 original_r9=list(csv.DictReader(open(ROOT/f'R12_{MON}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv',encoding='utf8',newline='')))
 original_q={r['utc_quarter']:r for r in original_r9}
 assert int(original_q[BEFORE]['R12_first_TP_global_maxcount_quarter_selected'])==17
 assert int(original_q[BEFORE]['R9_SYNTH_exact_15min_reference'])==9
 assert int(original_q[QUARTER]['R9_SYNTH_exact_15min_reference'])==11
 t0=load_labels(MON);rt,b,a=read_raw(MON)
 ix=t0['ix'];T=t0['t'];side=t0['side']
 end_ix,end_ms=quote_tp_first(rt,b,a,ix,t0['ask'],t0['bid'],side)
 idx=np.flatnonzero((T>=qstart)&(T<qend))
 loc=idx[earliest_finish_schedule(T[idx],end_ms[idx])]
 assert len(loc)==11
 assert T[loc[0]]>int(prevprev['exit_utc_ms'])
 assert end_ms[loc[-1]]<int(after[0]['entry_utc_ms'])
 new=[]
 for k in loc:
  liq=int(b[end_ix[k]] if side[k]==1 else a[end_ix[k]])
  entry=int(t0['ask'][k] if side[k]==1 else t0['bid'][k]);net=(liq-entry)*int(side[k])-20
  assert net>=100
  new.append({'month':'2026-'+MON,'entry_utc_ms':str(int(T[k])),
   'entry_utc_hour':hour_key(T[k]),'entry_utc_quarter':quarter_key(T[k]),
   'entry_tick_ordinal':str(int(ix[k])),'exit_utc_ms':str(int(end_ms[k])),
   'exit_tick_ordinal':str(int(end_ix[k])),'side':str(int(side[k])),
   'entry_ask_raw':str(int(t0['ask'][k])),'entry_bid_raw':str(int(t0['bid'][k])),
   'exit_liquidation_raw':str(liq),'nominal_net_raw_after_fee':str(net),
   'hold_ms':str(int(end_ms[k]-T[k])),
   'full_30sec_no_adverse_after_entry_verified_by_original_S1':'True',
   'not_a_causal_entry_model':'True'})
 # Invariant: previous quarter loses only its surplus last position; target
 # quarter exchanges ten later candidates for eleven earlier compatible exits.
 edited=before[:-1]+new+after
 assert len(edited)==len(frozen)
 times=np.array([int(r['entry_utc_ms']) for r in edited],np.int64)
 exits=np.array([int(r['exit_utc_ms']) for r in edited],np.int64)
 assert np.all(times[1:]>exits[:-1]) and np.all(times<exits)
 assert all(int(r['nominal_net_raw_after_fee'])>=100 for r in edited)
 assert all(r['full_30sec_no_adverse_after_entry_verified_by_original_S1']=='True' for r in edited)
 qcounts=Counter(r['entry_utc_quarter'] for r in edited)
 changes={}
 qrows=[];bad=[]
 for r in original_r9:
  q=r['utc_quarter'];old_count=int(r['R12_first_TP_global_maxcount_quarter_selected']);count=qcounts[q]
  ref=int(r['R9_SYNTH_exact_15min_reference']);upper=int(r['R12_first_TP_isolated_quarter_upper'])
  if count!=old_count:changes[q]={'old':old_count,'new':count,'reference':ref};
  r={**r,'R12Q_QUOTA_PRIORITY_SELECTED':count,'R12Q_QUARTER_MET':int(count>=ref) if ref else '',
        'R12Q_PROVEN_INFEASIBLE':int(upper<ref) if ref else '',
        'R12Q_MISSED_BUT_ISOLATED_FEASIBLE':int(count<ref and upper>=ref) if ref else ''}
  qrows.append(r)
  if ref>count:bad.append(r)
 assert changes=={BEFORE:{'old':17,'new':16,'reference':9},QUARTER:{'old':10,'new':11,'reference':11}}
 assert len(bad)==149 and all(int(r['R12Q_PROVEN_INFEASIBLE'])==1 for r in bad)
 assert sum(int(r['R12Q_QUARTER_MET']) for r in qrows if r['R12Q_QUARTER_MET']!='')==1670
 p=ROOT/'R12Q_02_SOURCE_EXACT_GLOBAL_QUOTA_PRIORITY_TP_TRACE.csv';write_csv(p,edited,list(edited[0]))
 q=ROOT/'R12Q_02_ALL_2688_15MIN_QUOTA_PRIORITY.csv';write_csv(q,qrows,list(qrows[0]))
 z=ROOT/'R12Q_02_ALL_149_PROVEN_IMPOSSIBLE_QUARTERS.csv';write_csv(z,bad,list(bad[0]))
 receipt={'research_type':'FUTURE_PRIVILEGED_QUOTA_PRIORITY_SWAP_ONLY_NOT_CAUSAL',
   'parent_branch':'carson/h1v2-r12-adaptive-tp-hour-quarter-oracle-20261103',
   'source_raw_month':'2026-02','raw_source_SHA256':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',
   'frozen_S1_label_NPZ_SHA256':t0['labels_sha256'],
   'target_quarter':QUARTER,'source_eligible_strict_candidates':len(idx),
   'target_quarter_old':10,'target_quarter_corrected':11,
   'prior_quarter_old':17,'prior_quarter_corrected':16,'prior_quarter_required':9,
   'selected_month_total_UNCHANGED':len(edited),
   'zero_overlap_every_exact_source_quote_ordinal':True,
   'all_selected_entries_original_good15_safe30':True,
   'all_exits_first_source_quote_TP_nominal_net_at_least_0p10':True,
   'February_R12_original_active_15min_covered':1669,
   'February_R12Q_active_15min_covered':1670,
   'Feb_R9_active_quarters':1819,'Feb_source_proven_impossible':149,
   'all_remaining_missed_quarters_proven_source_impossible':True,
   'not_real_execution_validated':True,
   'outputs_sha256':{f.name:sha(f) for f in (p,q,z)}}
 f=ROOT/'R12Q_02_IMMUTABLE_QUOTA_PRIORITY_SWAP_PROOF.json';f.write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2),flush=True)

if __name__=='__main__':main()
