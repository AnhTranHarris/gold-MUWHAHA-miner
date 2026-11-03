"""Independent R14 result/trace integrity verification, no label refitting."""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src'))
import r14_robust_envelope as m

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def verify():
 result=root/'results'
 manifest=json.loads((result/'R14_MANIFEST.json').read_text())
 for name,rec in manifest['members'].items():
  p=result/name
  assert p.is_file() and p.stat().st_size==rec['bytes'] and sha(p)==rec['sha256'],name
 hours=list(csv.DictReader((result/'R14_ALL_72_SOURCE_LANE_ROBUSTNESS_HOURS.csv').open()))
 quarters=list(csv.DictReader((result/'R14_ALL_288_SOURCE_LANE_ROBUSTNESS_QUARTERS.csv').open()))
 traces=list(csv.DictReader((result/'R14_ALL_SELECTED_ORIGINAL_QUOTE_ORDINALS.csv').open()))
 assert len(hours)==72 and len(quarters)==288
 assert len({(r['source'],r['lane'],r['tier']) for r in hours})==72
 assert len({(r['source'],r['lane'],r['tier'],r['quarter']) for r in quarters})==288
 assert all(r['source'] in m.r13.EXPECTED for r in hours)
 count=0;verified_candidates=0;verified_ordinals=0
 for source in m.r13.EXPECTED:
  t,b,a,pin=m.r13.load_source(source)
  assert pin==m.r13.EXPECTED[source][1]
  for lane in m.LANES:
   p=result/f'R14_{source}_{lane}_COMPLETE_CANDIDATE_STRESS_MATRIX.npz'
   with np.load(p,allow_pickle=False) as f:
    ix=f['source_raw_quote_index'];ts=f['entry_time_utc_ms'];side=f['future_selected_side'];out=f['nine_scenario_outcome'];fill=f['nine_scenario_fill_quote_index'];exit=f['nine_scenario_exit_quote_index'];end=f['worst_case_occupied_until_utc_ms'];scores=f['successful_scenario_count']
   n=len(ix);verified_candidates+=n
   assert np.array_equal(t[ix],ts)
   assert np.all((side==1)|(side==-1)) and out.shape==(n,9) and fill.shape==(n,9) and exit.shape==(n,9)
   assert np.array_equal((out==1).sum(axis=1),scores)
   assert np.all(end>ts)
   for j in range(9):
    f=fill[:,j];x=exit[:,j];ok=out[:,j]==1
    assert np.all(f[ok]>=ix[ok]) and np.all(x[ok]>f[ok])
    assert np.all(t[x[ok]]>t[f[ok]])
    gross=np.where(side[ok]>0,b[x[ok]]-a[f[ok]],b[f[ok]]-a[x[ok]])
    slip=m.SLIPS[j%3]
    assert np.all(gross-2*slip-20>=100)
    assert np.all(end[ok]>=t[x[ok]])
   hs=[r for r in hours if r['source']==source and r['lane']==lane]
   assert len(hs)==4
   for h in hs:
    need=int(h['required_robust_success_scenarios']);eligible=int((scores>=need).sum())
    assert eligible==int(h['latency_robust_candidates']),h
    zz=[r for r in traces if r['source']==source and r['lane']==lane and r['tier']==h['tier']]
    assert len(zz)==int(h['globally_selected_nonoverlap_worst_scenario_reservation'])
    prev=-2**62
    for r in zz:
     i=int(r['signal_source_quote_ix']);stamp=int(r['signal_utc_ms']);ed=int(r['worst_scenario_observed_occupation_end_utc_ms'])
     assert t[i]==stamp and stamp>prev and ed>stamp
     prev=ed
     assert b[i]==int(r['quote_bid_raw']) and a[i]==int(r['quote_ask_raw'])
     assert int(r['strict_success_of_9_lag_slip'])>=need
     verified_ordinals+=1
    q=[r for r in quarters if r['source']==source and r['lane']==lane and r['tier']==h['tier']]
    assert len(q)==4 and sum(int(x['globally_selected_entries_in_quarter']) for x in q)==len(zz)
    assert sum(int(x['original_R9_synth_reference']) for x in q)==104
    assert sum(int(x['global_selection_meets_quarter']=='True') for x in q)==sum(int(x['globally_selected_entries_in_quarter'])>=int(x['original_R9_synth_reference']) for x in q)
    count+=1
 assert count==72
 return {'complete_source_hour_rows':len(hours),'full_source_quarter_rows':len(quarters),
         'verified_full_candidate_stress_matrices':len(m.r13.EXPECTED)*len(m.LANES),
         'verified_quote_candidates_all_lanes':verified_candidates,'verified_selected_source_ordinals':verified_ordinals,
         'all_22_original_result_member_sha256':True,'exact_source_bid_ask_exit_price_and_friction_checks':True,
         'all_one_position_occupancies_nonoverlapping':True,'classification':'RESEARCH_ONLY_FUTURE_HINDSIGHT_NO_DEPLOYMENT'}
if __name__=='__main__': print(json.dumps(verify(),indent=2))
