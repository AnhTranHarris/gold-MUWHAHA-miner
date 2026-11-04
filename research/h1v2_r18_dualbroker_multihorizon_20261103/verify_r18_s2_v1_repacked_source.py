"""Independent R18-S2 V1 source ordinal/payoff/UTC count verifier.

Every selected source ordinal, original frozen R18 signal/side and all 96
scenario full UTC quarter/hour rows are checked; no model was trained.
V1 lacks complete independent failed-trial arrays; that is explicitly not
verified and motivates V2, which must remain separately versioned.
"""
from __future__ import annotations
import argparse,csv,json,sys,hashlib
from pathlib import Path
import numpy as np
LAB=Path('/mnt/data/h1v2_r18_dualbroker');ROOT=Path('/mnt/data')
sys.path.insert(0,str(LAB/'src'))
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen
OUT=LAB/'results_r18_S2_LATENCY_FRONTIER'
MONS=('01','02','06','07');SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()

def readrows(p):
 with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def verify_one(src,mon):
 tag=f'R18_S2_{src}_{mon}'
 files=[OUT/f'{tag}_12_RESEARCH_SCENARIO_ROWS.csv',
        OUT/f'{tag}_ALL_UTC_15MIN_12_SCENARIOS.csv',
        OUT/f'{tag}_ALL_UTC_HOURS_12_SCENARIOS.csv',
        OUT/f'{tag}_COMPLETE_REPACKED_SOURCE_SIGNAL_QUOTE_ORDINALS.npz']
 orig=OUT/f'{tag}_SOURCE_AND_OUTPUT_SHA_RECEIPT.json';receipt=json.loads(orig.read_text())
 for p in files:
  assert p.name in receipt['outputs']
  assert sha(p)==receipt['outputs'][p.name]['sha256']
  assert p.stat().st_size==receipt['outputs'][p.name]['bytes']
 scen=readrows(files[0]);qrows=readrows(files[1]);hrows=readrows(files[2]);
 assert len(scen)==12 and len(qrows)==12*{'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 assert len(hrows)==len(qrows)//4
 t,b,a,origsignal,origside,_,source_pin=get_frozen(src,mon)
 ref=r18.refs_for_month(mon,ROOT)
 assert receipt['original_src_sha']==r18.PINS[src][mon]
 assert receipt['source_UTC_reference_sha256']==ref['sha256']
 results=[]
 with np.load(files[3],allow_pickle=False) as z:
  for record in scen:
   name=record['scenario']
   s=z[name+'_source_signal_idx'];side=z[name+'_side_future_informed']
   f=z[name+'_actual_quote_fill_idx'];x=z[name+'_first_observed_target_exit_idx']
   payoff=z[name+'_nominal_net_raw']
   assert len(s)==len(side)==len(f)==len(x)==len(payoff)==int(record['repacked_onepos_future_known_winners'])
   if len(s):
    where=np.searchsorted(origsignal,s)
    assert np.all(where<len(origsignal)) and np.array_equal(origsignal[where],s)
    assert np.array_equal(origside[where],side),f'FUTURE_SIDE_MISMATCH {name}'
    assert np.all(f>=s) and np.all(x>f)
    assert np.all(t[x]-t[f]<=60000),f'EXIT_HORIZON {name}'
    assert np.all(t[f[1:]]>t[x[:-1]]),f'OCCUPIED {name}'
    lag=int(record['nominal_delay_ms']);slip=int(record['extra_slip_quoted_price_raw_per_leg']);cap=int(record['current_actual_fill_spread_cap_raw'])
    assert np.all(t[f]>=t[s]+lag) and np.all(t[f]-(t[s]+lag)<=1000)
    assert np.all(f>s) and np.all((a[f]-b[f])<=cap)
    expected=np.where(side==1,b[x].astype(np.int64)-a[f].astype(np.int64),
                              b[f].astype(np.int64)-a[x].astype(np.int64))-2*slip-20
    assert np.array_equal(payoff.astype(np.int64),expected),f'BIDASK_FALSE_NET {name}'
    assert np.all(payoff>=100)
    assert int(payoff.astype(np.int64).sum())==int(record['selected_future_target_net_quote_price_units_0p001'])
   idx=(t[f]//900000-ref['qkeys'][0]).astype(np.int64)
   assert np.all((idx>=0)&(idx<len(ref['qkeys'])))
   bins=np.bincount(idx,minlength=len(ref['qkeys']))
   q=[row for row in qrows if row['scenario']==name]
   h=[row for row in hrows if row['scenario']==name]
   assert len(q)==len(ref['qref']) and len(h)==len(ref['href'])
   assert np.array_equal(bins,np.array([int(x['repacked_future_good']) for x in q]))
   assert np.array_equal(bins.reshape(-1,4).sum(axis=1),np.array([int(x['repacked_future_good']) for x in h]))
   assert np.array_equal(ref['qref'],np.array([int(x['R9_SYNTH_ref']) for x in q]))
   qm=(ref['qref']>0)&(bins>=ref['qref'])
   hm=(ref['href']>0)&(bins.reshape(-1,4).sum(axis=1)>=ref['href'])
   assert int(qm.sum())==int(record['repacked_15min_quotas_met'])
   assert int(hm.sum())==int(record['repacked_hourly_quotas_met'])
   results.append({'scenario':name,'selected_source_quote_interval_count':len(s),
     'complete_quarter_reconcile':True,'complete_hour_reconcile':True,
     'source_frozen_R18_oracle_universe_membership_reconciled':True,
     'executed_bidask_price_raw_net_reconciled':True})
 result={'source':src,'month':mon,'source_original_sha':r18.PINS[src][mon],
   'full_12_scenarios_verified':True,'full_original_source_UTC_quarter_and_hour_checked':True,
   'all_12_repacked_quote_ordinals_and_original_future_side_checked':True,
   'source_files':{p.name:{'sha256':sha(p),'size':p.stat().st_size} for p in files},
   'original_source_frozen_signal_count':len(origsignal),
   'complete_failed_trial_independent_source_outcomes_not_preserved_in_V1':True,
   'future_selected_100pct_accuracy_not_predictive':True,
   'scenario_results':results}
 dest=OUT/f'{tag}_INDEPENDENT_SOURCE_12_SCENARIOS_VERIFIED_V1.json'
 dest.write_text(json.dumps(result,indent=2)+'\n')
 print('PASS',src,mon,sha(dest),flush=True)
 return dest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=SOURCES,required=True)
 p.add_argument('--month',choices=MONS,required=True)
 a=p.parse_args();verify_one(a.source,a.month)
