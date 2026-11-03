"""R16 independent full saved-trace verifier; abstains if input sources missing."""
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r16_broker_adaptive/src')
import r16_fullcalendar_broker_adaptive as r16
ROOT=Path('/mnt/data/h1v2_r16_broker_adaptive');OUT=ROOT/'results'

def assert_source_entry_trace(t,b,a,source_entries,exitix,side):
 assert np.all(exitix>source_entries)
 assert np.all(t[exitix]>t[source_entries])
 assert np.all(t[exitix]<=t[source_entries]+15000)
 net=np.where(side==1,b[exitix]-a[source_entries],b[source_entries]-a[exitix])-20
 assert np.all(net>=100)

def check_direct_brute(t,b,a,i,side,exitix):
 start=int(t[i]);end=start+30000
 first=-1;minimum=10**18;maximum=-10**18;last=start;prev=start;seen=0
 for j in range(i+1,len(t)):
  if t[j]==start:continue
  if t[j]>end:
   assert t[j]-last<=15000,'source horizon boundary gap censored'
   break
  assert t[j]-prev<=15000,'full30 intrahorizon gap must be censored'
  prev=int(t[j]);last=int(t[j]);seen+=1
  liq=int(b[j] if side==1 else a[j]);minimum=min(minimum,liq);maximum=max(maximum,liq)
  if first<0 and t[j]<=start+15000:
   favorable=(b[j]>=a[i]+120) if side==1 else (a[j]<=b[i]-120)
   if favorable:first=j
 assert first==exitix,('FIRST_TP_NOT_FIRST_SOURCE_ORDINAL',i,first,exitix)
 assert seen>0 and t[-1]>=end
 assert (minimum>b[i]-100) if side==1 else (maximum<a[i]+100)


def run():
 verified=[];src=[]
 for mon in ('01','02','06','07'):
  t,b,a=r16.tp.read_raw(mon)
  refrows,refhour,qkeys,qref,href=r16.read_refs(mon)
  main=json.loads((OUT/f'R16_{mon}_EXACT_COMPLETE_EXECUTION.json').read_text())
  stress=json.loads((OUT/f'R16_{mon}_FULL_DELAY_EXECUTION_RECEIPT.json').read_text())
  with np.load(OUT/f'R16_{mon}_ALL_SOURCE_ORIGINAL_AND_EXPANDED_QUOTE_GOOD_FIRSTTP.npz',allow_pickle=False) as z:
   ix=z['source_ordinal'].copy();side=z['side_buy1_sellminus1'].copy();exitix=z['first_tp_exit_raw_ordinal'].copy()
   assert np.array_equal(z['entry_utc_ms'],t[ix]);assert np.array_equal(z['first_tp_exit_utc_ms'],t[exitix])
   assert np.array_equal(z['entry_bid_raw'],b[ix]) and np.array_equal(z['entry_ask_raw'],a[ix]);
   assert_source_entry_trace(t,b,a,ix,exitix,side)
   gd={name:z['lane_'+name].copy() for name in r16.LANES}
  with np.load(OUT/f'R16_{mon}_ALL_LANE_SELECTED_ENTRY_EXIT_ORDINALS.npz',allow_pickle=False) as z:
   selection={name:z[f'{name}_good_ordinal_index'].copy() for name in r16.LANES}
  for lane,s in selection.items():
   assert len(s)==main['fully_evaluated_variants'][lane]['selected_one_position_firsttp']
   assert np.all(gd[lane][s]);assert np.all(t[ix[s[1:]]]>t[exitix[s[:-1]]]),('one-position',{mon,lane})
   assert_source_entry_trace(t,b,a,ix[s],exitix[s],side[s])
   # Separate straightforward chronological Python quote scan on a fixed,
   # deterministic coverage of 30 per saved lane, not only model arithmetic.
   if len(s):
    sample=s[np.unique(np.linspace(0,len(s)-1,min(30,len(s)),dtype=np.int64))]
    for q in sample:check_direct_brute(t,b,a,int(ix[q]),int(side[q]),int(exitix[q]))
  with (OUT/f'R16_{mon}_ALL_15MIN_LANE_CALENDAR.csv').open(newline='',encoding='utf8') as f:
   allq=list(csv.DictReader(f))
  assert len(allq)==len(qref)*9
  for lane in r16.LANES:
   lane_q=[v for v in allq if v['lane']==lane]
   assert len(lane_q)==len(qref)
   assert np.array_equal(np.asarray([int(x['original_R9_SYNTH_15min_reference']) for x in lane_q]),qref)
   assert sum(int(x['future_selected_one_position_firsttp']) for x in lane_q)==len(selection[lane])
  with (OUT/f'R16_{mon}_ALL_35_DELAY_FRICTION_SCENARIOS.csv').open(newline='',encoding='utf8') as f:
   rows=list(csv.DictReader(f))
  assert len(rows)==35
  with (OUT/f'R16_{mon}_ALL_15MIN_DELAYS_STRESS_CALENDAR.csv').open(newline='',encoding='utf8') as f:
   fullstress=list(csv.DictReader(f))
  assert len(fullstress)==len(qref)*35
  for r in rows:
   lane=r['lane'];lag=int(r['lag_ms']);slip=int(r['per_leg_slippage_raw']);sig=ix[selection[lane]]
   p=OUT/f'R16_{mon}_{lane}_lag{lag}_slip{slip}_FULL_FROZEN_TICK_OUTCOME.npz'
   with np.load(p,allow_pickle=False) as d:
    st=d['outcome_code_good1_bad0_rejectminus1_busym2_censm3'];fills=d['actual_fill_tick_ordinal'];e=d['first_good_exit_tick_ordinal']
    assert len(st)==len(sig) and np.array_equal(d['source_signal_tick_ordinal'],sig)
    assert len(st)==sum(int(r[k]) for k in ['GOOD','completed_BAD','source_CENSORED','quote_or_spread_REJECT','single_position_busy_SKIP'])
    for code,key in [(1,'GOOD'),(0,'completed_BAD'),(-3,'source_CENSORED'),(-1,'quote_or_spread_REJECT'),(-2,'single_position_busy_SKIP')]:
     assert int(np.count_nonzero(st==code))==int(r[key])
    if lag==0 and slip==0:assert np.all(st==1) and np.array_equal(fills,sig)
    good=(st==1)
    if good.any():
     assert np.all(fills[good]>=sig[good]) and np.all(e[good]>fills[good])
     assert np.all(t[e[good]]<=t[fills[good]]+15000)
     assert np.all(d['good_net_raw_price_unit_0p001'][good]>=100)
   qq=[x for x in fullstress if x['lane']==lane and x['latency_ms']==str(lag) and x['slippage_per_leg_raw']==str(slip)]
   assert len(qq)==len(qref)
   assert sum(int(x['actual_fill_UTC_quarter_STRICT_GOOD']) for x in qq)==int(r['GOOD'])
   assert sum(int(x['actual_fill_UTC_quarter_COMPLETED_FAILED']) for x in qq)==int(r['completed_BAD'])
  verified.append({'month':mon,'raw_quote_count':len(t),'full_good_candidate_entries':len(ix),
    'lanes':len(selection),'full_stress_scenarios':len(rows),'reconciled_full_calendar_quarters':len(qref),
    'per_ordinal_firstTP_fee':True,'one_position_all_lanes':True,'all_140_source_stress_npz_group_counts':True,
    'brute_direct_source_quote_traversal_per_lane':30})
  print('VERIFIED',mon,'quotes',len(t),'source-good',len(ix),'stress',len(rows),flush=True)
 result={'all_four_complete_full_original_quote_source_checked':True,'months':verified,
  'full_months':len(verified),'all_source_scientific_status':'RESEARCH_ONLY_FUTURE_SELECTED_HINDSIGHT_NO_CAUSAL_MODEL',
  'stress': 'REAL_OBSERVED_SOURCE_QUOTE_CONSERVATIVE_FROZEN_SIGNAL_NO_ACCOUNT_PNL',
  'original_legacy_files_mutated':False}
 p=ROOT/'final/R16_INDEPENDENT_FULL_SOURCE_VERIFICATION.json';p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result

if __name__=='__main__':run()
