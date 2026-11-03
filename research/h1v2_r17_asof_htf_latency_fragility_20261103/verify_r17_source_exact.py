"""Independent R17 row/quote-ordinal consistency verifier on immutable original R16.

Does not verify live Coinexx; verifies genuine DUKAS source-month pins and all
new R17 derived full source rows. Duplicate candidate, calendar or artifact SHA
mismatches fail closed, including original R16 control stress parity.
"""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r17_multiscale_latency/src')
import r17_asof_htf_latency as r17
ROOT=Path('/mnt/data/h1v2_r17_multiscale_latency');out=ROOT/'results';r16=r17.r16

def readcsv(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))

def verify(mon):
 p=out/f'R17_{mon}_EXACT_SOURCE_AND_REPLAY_RECEIPT.json';rec=json.loads(p.read_text())
 assert rec['source_pins']['raw']==r17.sha(Path(f'/mnt/data/XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'))==r16.RAW_PINS[mon]
 for name,z in rec['outputs'].items():
  q=out/name;assert q.stat().st_size==z['bytes'] and r17.sha(q)==z['sha256'],name
 group=readcsv(out/f'R17_{mon}_FULL_40_MECHANISM_FALSIFICATION.csv');assert len(group)==40
 quarter=readcsv(out/f"R17_{mon}_ALL_{rec['full_quarter_records']}_ORIGINAL_QUARTER_OUTCOMES.csv")
 assert len(quarter)==rec['full_quarter_records'] and len({(x['lane'],x['asof_gate'],x['utc_quarter']) for x in quarter})==len(quarter)
 original_quarters,_,qkeys,qref,href=r16.read_refs(mon)
 t,b,a=r16.tp.read_raw(mon)
 saved=out/f'R17_{mon}_ALL_HINDSIGHT_ORIGINAL_QUOTE_ORDINAL_AND_ASOF_MTF_STRESS.npz'
 original_good=Path(f'/mnt/data/h1v2_r16_broker_adaptive/results/R16_{mon}_ALL_SOURCE_ORIGINAL_AND_EXPANDED_QUOTE_GOOD_FIRSTTP.npz')
 selected=Path(f'/mnt/data/h1v2_r16_broker_adaptive/results/R16_{mon}_ALL_LANE_SELECTED_ENTRY_EXIT_ORDINALS.npz')
 assert rec['source_pins']['r16_future_good']==r17.sha(original_good)
 assert rec['source_pins']['r16_original_selected']==r17.sha(selected)
 nchecked=0
 with np.load(saved,allow_pickle=False) as zz, np.load(original_good,allow_pickle=False) as gg, np.load(selected,allow_pickle=False) as sel:
  for lane in r17.LANES:
   full=zz[lane+'__ALL_source_quote_ordinal'];sides=zz[lane+'__ALL_side']
   idx=sel[lane+'_good_ordinal_index']
   assert np.array_equal(full,gg['source_ordinal'][idx]) and np.array_equal(sides,gg['side_buy1_sellminus1'][idx])
   for n,h in zip(('15m','1h','4h'),r17.HORIZONS):
    anchor=zz[lane+'__ALL_anchor_'+n+'_ordinal']
    age=zz[lane+'__ALL_anchor_'+n+'_age_ms']
    signed=zz[lane+'__ALL_side_signed_mid2_'+n+'_raw']
    valid=anchor>=0
    assert np.all(~valid|(anchor<full))
    assert np.all(t[anchor[valid]]<=t[full[valid]]-h)
    assert np.array_equal(age[valid], t[full[valid]]-h-t[anchor[valid]])
    direct=sides[valid].astype(np.int64)*((b[full[valid]].astype(np.int64)+a[full[valid]])-(b[anchor[valid]].astype(np.int64)+a[anchor[valid]]))
    assert np.array_equal(signed[valid],direct)
   originally=Path(f'/mnt/data/h1v2_r16_broker_adaptive/results/R16_{mon}_{lane}_lag100_slip0_FULL_FROZEN_TICK_OUTCOME.npz')
   assert rec['source_pins'][lane+'_100ms_frozen_input']==r17.sha(originally)
   with np.load(originally,allow_pickle=False) as ori:
    assert np.array_equal(zz[lane+'__ALL_original_R16_100ms_frozen_status'],ori['outcome_code_good1_bad0_rejectminus1_busym2_censm3'])
   for gate in r17.GATES:
    pre=lane+'__'+gate
    fi=zz[pre+'__original_source_quote_ordinal'];ss=zz[pre+'__source_side_buy1_sellminus1'];st=zz[pre+'__replayed_100ms_status'];fill=zz[pre+'__filled_source_quote_ordinal'];ex=zz[pre+'__exit_source_quote_ordinal']
    assert len(fi)==len(st)==len(ss)==len(fill)==len(ex)
    assert np.array_equal(fi,np.intersect1d(fi,full,assume_unique=True))
    if len(fi)>1:assert np.all(np.diff(t[fi])>0)
    groups=[v for v in group if v['lane']==lane and v['asof_gate']==gate];assert len(groups)==1
    v=groups[0];assert len(fi)==int(v['asof_gate_admitted'])
    codes={1:'selected_filtered_100ms_good',0:'selected_filtered_100ms_bad',-1:'selected_filtered_quote_reject',-2:'selected_filtered_busy_skip',-3:'selected_filtered_censored'}
    assert all(int(np.count_nonzero(st==code))==int(v[name]) for code,name in codes.items())
    if gate=='ALL_FUTURE_SELECTED_CONTROL':
     assert np.array_equal(fi,full)
     assert np.array_equal(st,zz[lane+'__ALL_original_R16_100ms_frozen_status'])
    hit=np.flatnonzero((st==1)|(st==0))
    if len(hit):
     assert np.all(fill[hit]>=0) and np.all(fill[hit]<len(t))
     assert np.all(t[fill[hit]]>=t[fi[hit]]+100)
     assert np.all(t[fill[hit]]-t[fi[hit]]-100<=1000)
     qix=(t[fill[hit]]//900000-qkeys[0]).astype(np.int64)
     assert np.all((qix>=0)&(qix<len(qkeys)))
     qtotal=np.bincount(qix,minlength=len(qkeys))
     qgood=np.bincount(qix[st[hit]==1],minlength=len(qkeys))
    else:qtotal=np.zeros(len(qkeys),np.int32);qgood=qtotal.copy()
    rows=[r for r in quarter if r['lane']==lane and r['asof_gate']==gate]
    assert len(rows)==len(qkeys)
    assert all(int(x['original_R9_SYNTH_15min_quota'])==int(qref[i]) and int(x['actual_filled_in_quarter'])==int(qtotal[i]) and int(x['actual_strict_good_in_quarter'])==int(qgood[i]) for i,x in enumerate(rows))
    nchecked+=len(rows)
 return {'month':mon,'verified':True,'original_dukascopy_raw_quote_count':len(t),'source_hour_count':len(href),'full_quarter_lane_gate_rows':nchecked,'mechanism_groups':len(group),'source_ref_quarters':len(qref)}

if __name__=='__main__':
 parts=[verify(s) for s in ('01','02','06','07')];final={'source_verified_all_four_months':True,'verification':parts,'research_only_no_coinexx_full_fourmonth':True}
 p=ROOT/'results/R17_COMPLETE_INDEPENDENT_QUOTE_SOURCE_AND_ALL_ROWS_VERIFICATION.json';p.write_text(json.dumps(final,indent=2)+'\n');print(json.dumps(final,indent=2))
