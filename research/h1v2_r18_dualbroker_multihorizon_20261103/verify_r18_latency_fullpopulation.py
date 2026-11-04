"""R18-S1 lossless, independently rerunnable full eight-source delay-stress audit.

Read-only SHA + original quote-ordinal + full scenario and time-bucket verification.
Does not fit, promote or modify original historical H1V2/R9/R11-R18 results.
The source orders are future-known R18 choices, not causal predictor output.
"""
from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path('/mnt/data')
LAB=ROOT/'h1v2_r18_dualbroker'
OUT=LAB/'results_r18_FROZEN_DELAY'
sys.path.insert(0,str(LAB/'src'))
import r18_broker_multihorizon as r18
MONTHS=('01','02','06','07')
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
LABELS=('lag0_slip0','lag0_slip20','lag0_slip50',
        'lag100_slip0','lag100_slip20','lag100_slip50',
        'lag500_slip0','lag500_slip20','lag500_slip50')
STATUS=(1,0,2,-1,-2,-3)
SENTINEL=-2147483647

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()

def records(p):
 with p.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def independent_quote_read(source,mon):
 if source=='DUKASCOPY_RAW':
  p=ROOT/f'XAUUSD_DUKAS_2026_{mon}_ticks.csv.gz'
  assert sha(p)==r18.PINS[source][mon],f'RAW_SHA {p.name}'
  x=pd.read_csv(p,usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
  t=x.timestamp_ms_utc.to_numpy(np.int64);b=x.bid_raw.to_numpy(np.int32);a=x.ask_raw.to_numpy(np.int32)
 else:
  p=ROOT/f'XAUUSD_MT5_BROKER_2026_{mon}_ticks_ALL.csv.gz'
  assert sha(p)==r18.PINS[source][mon],f'RAW_SHA {p.name}'
  x=pd.read_csv(p,usecols=['time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
  t=x.time_msc.to_numpy(np.int64)+r18.OFFSETS[mon]*3600000
  b=np.rint(x.bid.to_numpy(np.float64)*1000).astype(np.int32)
  a=np.rint(x.ask.to_numpy(np.float64)*1000).astype(np.int32)
 del x
 assert np.all(np.diff(t)>=0) and np.all(a>=b) and np.all(b>0)
 return t,b,a

def verified_quote_read(source,mon):
 t,b,a=independent_quote_read(source,mon)
 evidence={'source_sha256':r18.PINS[source][mon], 'source_quotes':len(t)}
 if source=='MT5_BROKER_EXPORT' and mon=='06':
  t2,b2,a2=independent_quote_read(source,'07')
  _,end=r18.month_range(mon)
  take=(t2>t[-1])&(t2<end+180000)
  assert take.any() and t2[take][0]>t[-1]+15000
  evidence.update({'adjacent_month_sha256':r18.PINS[source]['07'],
                   'adjacent_month_actual_appended_quote_count':int(take.sum()),
                   'true_source_hole_ms':int(t2[take][0]-t[-1])})
  t=np.r_[t,t2[take]];b=np.r_[b,b2[take]];a=np.r_[a,a2[take]]
 return t,b,a,evidence

def full_verify(source,mon):
 tag=f'R18_LATENCY_{source}_{mon}'
 paths={'cases':OUT/f'{tag}_9_SCENARIO_RESULTS.csv',
        'q':OUT/f'{tag}_ALL_UTC_QUARTERS.csv',
        'h':OUT/f'{tag}_ALL_UTC_HOURS.csv',
        'trace':OUT/f'{tag}_ALL_FROZEN_SOURCE_ORDINAL_OUTCOME_TRACES.npz'}
 receipt=OUT/f'{tag}_SOURCE_SHA_AND_RESULT_RECEIPT.json'
 r=json.loads(receipt.read_text())
 for k,p in paths.items():
  assert p.exists(),f'MISSING:{p}'
  assert p.stat().st_size==r['member_outputs'][p.name]['bytes'],f'SIZE_{k}'
  assert sha(p)==r['member_outputs'][p.name]['sha256'],f'SHA_{k}'
 assert r['source']==source and r['month']==mon
 c=records(paths['cases']);qs=records(paths['q']);hs=records(paths['h'])
 assert len(c)==len(LABELS)==len(r['records'])
 assert len(qs)==len(LABELS)*{'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 assert len(hs)==len(qs)//4
 refs=r18.refs_for_month(mon,ROOT)
 t,b,a,evidence=verified_quote_read(source,mon)
 assert r['source_pin']['source_sha']==evidence['source_sha256']
 base_source=LAB/'results'/f'R18_{source}_{mon}_LOSSLESS_SELECTED_ORIGINAL_QUOTE_ORDINALS.npz'
 patch_source=LAB/'results_r18_JUNE_TAIL_PATCH'/'R18_JUNE_MT5_HALO_FULL_50_SOURCE_QUOTE_ORDINAL_TAIL_SETS.npz'
 base_key='R18_ADAPTIVE_UNION_4000__NEW_FIRST_TOUCH_60_BEFORE_ADVERSE'
 with np.load(base_source,allow_pickle=False) as baseline:
  original_ix=baseline[base_key+'_entry_ord']
  original_side=baseline[base_key+'_side_FUTURE_SELECTED']
  original_exit=baseline[base_key+'_firstTP_exit_ord']
 if source=='MT5_BROKER_EXPORT' and mon=='06':
  with np.load(patch_source,allow_pickle=False) as extra:
   original_ix=np.r_[original_ix,extra[base_key+'_stitched_entry_ord']]
   original_side=np.r_[original_side,extra[base_key+'_future_selected_side']]
   original_exit=np.r_[original_exit,extra[base_key+'_stitched_exit_ord']]
 assert len(original_ix)>0 and np.all(np.diff(t[original_ix])>0)
 assert np.all(original_exit>original_ix) and np.all(t[original_exit]-t[original_ix]<=60000)
 monthproof={'source':source,'month':mon,**evidence,'scenarios':[],'member_sha':{z.name:sha(z) for z in paths.values()},
            'source_original_scenario_ordinal_count':len(original_ix)}
 with np.load(paths['trace'],allow_pickle=False) as z:
  for label in LABELS:
   row=next(x for x in c if x['label']==label)
   rec=next(x for x in r['records'] if x['label']==label)
   for field in ('GOOD_60s_firstTP_before_adverse','COMPLETED_FAILED_STOP_OR_TIMEOUT','SOURCE_RIGHT_CENSORED',
                 'QUOTE_OR_SPREAD_REJECTED','OCCUPIED_SKIPPED','quarter_joint_correct_and_80pct','hour_joint_correct_and_80pct'):
    assert row[field]==str(rec[field]),f'RECEIPT_CSV_MISMATCH:{label}:{field}'
   sig=z[label+'_signal_ord'];side=z[label+'_future_selected_side'];fill=z[label+'_fill_ord'];exit=z[label+'_first_observed_exit_ord']
   st=z[label+'_outcome'];pnl=z[label+'_realized_quote_pnl_raw_or_sentinel']
   assert len(sig)==len(original_ix)==len(side)==len(fill)==len(exit)==len(st)==len(pnl)
   assert np.array_equal(sig,original_ix) and np.array_equal(side,original_side),f'ORACLE_DRIFT:{label}'
   assert np.isin(st,STATUS).all(),f'STATUS_ENUM:{label}'
   good=st==1;bad=np.isin(st,(0,2));cen=st==-3;rej=st==-1;busy=st==-2;completed=good|bad
   counts=(int(good.sum()),int(bad.sum()),int(cen.sum()),int(rej.sum()),int(busy.sum()))
   assert counts==tuple(int(row[x]) for x in ('GOOD_60s_firstTP_before_adverse','COMPLETED_FAILED_STOP_OR_TIMEOUT',
      'SOURCE_RIGHT_CENSORED','QUOTE_OR_SPREAD_REJECTED','OCCUPIED_SKIPPED')),f'COUNT_MISMATCH:{label}'
   assert np.all(fill[completed]>=0) and np.all(exit[completed]>fill[completed])
   assert np.all(fill[cen]>=0) and np.all(fill[rej|busy]<0) and np.all(exit[~completed]<0)
   assert np.all(pnl[~completed]==SENTINEL) and np.all(t[exit[good]]>t[fill[good]])
   assert np.all(t[exit[good]]-t[fill[good]]<=60000),f'TP_HORIZON:{label}'
   lag=int(row['latency_ms']);slip=int(row['per_leg_slippage_raw_0p001'])
   usable=fill>=0
   assert np.all(t[fill[usable]]>=t[sig[usable]]+lag)
   assert np.all(t[fill[usable]]<=t[sig[usable]]+lag+1000)
   assert np.all((a[fill[usable]]-b[fill[usable]])<=4000)
   if lag>0:assert np.all(fill[usable]>sig[usable])
   if lag==0:assert np.array_equal(fill[usable],sig[usable])
   ix=np.flatnonzero(completed)
   nmid=side[ix].astype(np.int64)
   raw=(np.where(nmid==1,b[exit[ix]].astype(np.int64)-a[fill[ix]].astype(np.int64),
                  b[fill[ix]].astype(np.int64)-a[exit[ix]].astype(np.int64))-2*slip-20)
   assert np.array_equal(pnl[ix].astype(np.int64),raw),f'BIDASK_NET_MISMATCH:{label}'
   assert int(raw.sum())==int(round(float(row['modeled_all_completed_bidask_net_quote_price_usd_per_1oz_not_cash'])*1000)),f'NET_AGG:{label}'
   assert np.all(pnl[good]>=100),f'FALSE_GOOD:{label}'
   for status in (1,0,2,-3,-1,-2):
    group=st==status
    if status in (1,0,2,-3):
     key=(t[fill[group]]//900000-refs['qkeys'][0]).astype(np.int64)
    else:
     key=(t[sig[group]]//900000-refs['qkeys'][0]).astype(np.int64)
    assert np.all((key>=0)&(key<len(refs['qkeys'])))
    observed=np.bincount(key,minlength=len(refs['qkeys']))
    expected_col={1:'actual_quote_fill_strictGOOD_60s',0:'completedBAD',2:'completedBAD',-3:'rightCENSOR',-1:'reject_original_signal',-2:'busy_original_signal'}[status]
    qrows=[x for x in qs if x['label']==label]
    if status==2:
     # Completed BAD contains sum of STOP and TIMEOUT, check jointly below.
     joint=np.bincount((t[fill[bad]]//900000-refs['qkeys'][0]).astype(np.int64),minlength=len(refs['qkeys']))
     assert np.array_equal(joint,np.asarray([int(x[expected_col]) for x in qrows]))
    elif status==0:
     assert np.less_equal(observed,np.asarray([int(x[expected_col]) for x in qrows])).all()
    else:
     assert np.array_equal(observed,np.asarray([int(x[expected_col]) for x in qrows])),f'QUARTER_COUNT:{label}:{status}'
   qrows=[x for x in qs if x['label']==label]
   hrows=[x for x in hs if x['label']==label]
   ref=np.array([int(x['original_R9_SYNTH_ref']) for x in qrows],np.int32)
   gq=np.array([int(x['actual_quote_fill_strictGOOD_60s']) for x in qrows],np.int32)
   bq=np.array([int(x['completedBAD']) for x in qrows],np.int32)
   calc=(ref>0)&(gq>=ref)&(gq/(gq+bq+1e-100)>=.8)
   assert np.array_equal(ref,refs['qref'])
   assert calc.sum()==int(row['quarter_joint_correct_and_80pct'])
   assert np.array_equal(gq.reshape(-1,4).sum(axis=1),np.asarray([int(x['actual_quote_fill_strictGOOD_60s']) for x in hrows]))
   assert np.array_equal(bq.reshape(-1,4).sum(axis=1),np.asarray([int(x['completedBAD']) for x in hrows]))
   hg=gq.reshape(-1,4).sum(axis=1);hb=bq.reshape(-1,4).sum(axis=1)
   assert int(((refs['href']>0)&(hg>=refs['href'])&(hg/(hg+hb+1e-100)>=.8)).sum())==int(row['hour_joint_correct_and_80pct'])
   monthproof['scenarios'].append({'name':label,'outcome_counts':counts,
      'quote_model_net_raw_int':int(raw.sum()),'source_ref_quarters':int((ref>0).sum()),
      'joint_80pct_quarters':int(calc.sum()),'source_ref_hours':int((refs['href']>0).sum()),
      'joint_80pct_hours':int(row['hour_joint_correct_and_80pct'])})
 assert len(monthproof['scenarios'])==9
 return monthproof

def run():
 verified=[]
 for source in SOURCES:
  for mon in MONTHS:
   verified.append(full_verify(source,mon))
   print('VERIFIED',source,mon,'9 scenarios','source-original ordinals & all source quarters/hours',flush=True)
 path=OUT/'R18_S1_EIGHT_SOURCE_72_SCENARIO_INDEPENDENT_VERIFIER_RECEIPT.json'
 path.write_text(json.dumps({'classification':'FROZEN_FUTURE_INFORMED_SIGNAL_STRESS_NONDEPLOYABLE',
  'complete_eight_months':True,'complete_72_scenarios':True,'all_quote_ordinals_reconciled':True,
  'underlying_source_gzip_sha256_verified':True,'source':[{'name':k,'months':v} for k,v in r18.PINS.items()],
  'complete_results':verified},indent=2)+'\n')
 print('PASS_ALL_EIGHT_SOURCES_72_SCENARIOS',sha(path),flush=True)
 return path
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=SOURCES)
 ap.add_argument('--month',choices=MONTHS)
 args=ap.parse_args()
 if bool(args.source)!=bool(args.month):ap.error('Specify source and month together')
 if args.source:
  proof=full_verify(args.source,args.month)
  p=OUT/f'R18_S1_VERIFIED_{args.source}_{args.month}_ATOMIC_SOURCE_RECEIPT.json'
  p.write_text(json.dumps(proof,indent=2)+'\n')
  print('PASS_ATOMIC_MONTH',args.source,args.month,'SHA',sha(p),flush=True)
 else:run()

