"""Independent immutable raw quote, exact bid/ask first passage, 15m/hour and SHA verification.

Verifies every R19 FUTURE-selected source quote ordinal, not a live predictor.
No source file or original R18/R11-R17 artifact is edited.
"""
from __future__ import annotations
import argparse,csv,json,sys,hashlib
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path('/mnt/data/h1v2_r19_broker_union');P=Path('/mnt/data')
sys.path.insert(0,str(ROOT/'src'))
import r19_multi_clock_union as r19
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen

@njit(cache=False)
def independently_check_first_good(t,b,a,s,fi,ex,side,slip):
 """Independent linear scanner: prove no previous stop, censor, or TP at first."""
 checked=0
 for k in range(len(s)):
  f=int(fi[k]);exitidx=int(ex[k]);sgn=int(side[k]);entry=int(a[f])+slip if sgn==1 else int(b[f])-slip
  opening=int(b[f]) if sgn==1 else int(a[f]);prev=t[f]
  passed=False
  for j in range(f+1,exitidx+1):
   if t[j]==t[f]:continue
   if t[j]-prev>15000:return -100-k
   prev=t[j]
   if t[j]>t[f]+60000:return -200-k
   if sgn==1:
    if int(b[j])<=opening-100:return -300-k
    pnl=int(b[j])-slip-entry-20
   else:
    if int(a[j])>=opening+100:return -400-k
    pnl=entry-int(a[j])-slip-20
   if pnl>=100:
    if j!=exitidx:return -500-k
    passed=True;break
  if not passed:return -600-k
  checked+=1
 return checked

def read_csv(p):
 with open(p,newline='',encoding='utf8') as f:return list(csv.DictReader(f))

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def verify(source,mon):
 srcroot=ROOT/('results_v2' if (source=='DUKASCOPY_RAW' and mon=='02') or (source=='MT5_BROKER_EXPORT' and mon in ['06','07']) else 'results')
 stem=f'R19_{source}_{mon}'
 res=srcroot/f'{stem}_SCENARIOS.csv';qs=srcroot/f'{stem}_ALL_QUARTERS.csv';hr=srcroot/f'{stem}_ALL_HOURS.csv';trace=srcroot/f'{stem}_EXACT_SELECTED_ORDINAL_TRACES.npz';receipt=srcroot/f'{stem}_SOURCE_SHA_AND_EVIDENCE.json'
 z=json.loads(receipt.read_text());
 for p in (res,qs,hr,trace):
  assert p.name in z['files'] and sha(p)==z['files'][p.name]['sha256'] and p.stat().st_size==z['files'][p.name]['size']
 assert z['original_source_SHA']==r18.PINS[source][mon]
 t,b,a,base,base_side,_,prov=get_frozen(source,mon)
 refs=r18.refs_for_month(mon,P);qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 assert np.array_equal(qref.reshape(-1,4).sum(axis=1),href)
 u,s,m,mask4,counts,pin=r19.read_unions(source,mon,t,b,a,base,base_side)
 assert pin==z['original_R18_source_sha'] and len(u)==z['union_unique_source_frozen_signals']
 assert counts==z['all_ten_source_lanes_selected_counts']
 assert len(qkeys)=={'01':2976,'02':2688,'06':2880,'07':2976}[mon]
 assert len(href)==len(qkeys)//4
 rows=read_csv(res);allq=read_csv(qs);allh=read_csv(hr)
 assert len(rows)==5 and len(allq)==5*len(qkeys) and len(allh)==5*len(href)
 detail=[]
 with np.load(trace,allow_pickle=False) as arr:
  for case in rows:
   label=case['case'];lag=int(case['latency_ms']);slip=int(case['per_leg_extra_slip_raw_0p001']);cap=int(case['actual_fill_spread_cap_raw_0p001'])
   pref=label+'__'
   sig=arr[pref+'source_signal_quote_ordinal'].astype(np.int64)
   side=arr[pref+'original_future_selected_side'].astype(np.int8)
   mask=arr[pref+'source_lane_provenance_bitmask'].astype(np.uint16)
   f=arr[pref+'actual_observed_fill_quote_ordinal'].astype(np.int64)
   exitidx=arr[pref+'first_target_exit_quote_ordinal'].astype(np.int64)
   net=arr[pref+'future_selected_nominal_bidask_net_raw'].astype(np.int64)
   assert len(sig)==len(side)==len(mask)==len(f)==len(exitidx)==len(net)==int(case['first_quote_delayed_good_trails_repacked'])
   if len(sig)>0:
    where=np.searchsorted(u,sig)
    assert np.all(where<len(u)) and np.array_equal(u[where],sig)
    assert np.array_equal(s[where],side) and np.array_equal(m[where],mask)
    assert np.all(mask4[where]),'R19_SOURCE_GATE_EXCEEDS_4_00'
    assert np.all(f>sig) and np.all(t[f]>=t[sig]+lag) and np.all(t[f]-(t[sig]+lag)<=1000)
    assert np.all((a[f].astype(np.int64)-b[f].astype(np.int64))<=cap)
    assert np.all(exitidx>f) and np.all(t[exitidx]-t[f]<=60000)
    assert np.all(t[f[1:]]>t[exitidx[:-1]]),'R19_ONE_POSITION_OCCUPIED'
    actual=np.where(side==1,b[exitidx].astype(np.int64)-a[f].astype(np.int64),b[f].astype(np.int64)-a[exitidx].astype(np.int64))-2*slip-20
    assert np.array_equal(actual,net),'R19_FALSE_ASKBID_PAYOFF'
    assert np.all(net>=100) and int(net.sum())==int(case['quoted_price_favorable_net_raw_sum'])
    result=independently_check_first_good(t,b,a,sig,f,exitidx,side,slip)
    assert result==len(sig),(label,'NOT_TRUE_FIRST_GOOD_OR_ADVERSE_VIOLATION',result)
   bins=np.bincount(t[f]//900000-qkeys[0],minlength=len(qref)).astype(np.int64)
   assert np.all((t[f]//900000-qkeys[0]>=0)&(t[f]//900000-qkeys[0]<len(qref)))
   qrecord=[x for x in allq if x['case']==label];hrecord=[x for x in allh if x['case']==label]
   assert len(qrecord)==len(qref) and len(hrecord)==len(href)
   assert np.array_equal([int(x['future_selected_good']) for x in qrecord],bins)
   assert np.array_equal([int(x['R9_SYNTH_clock_UTC_ref']) for x in qrecord],qref)
   assert np.array_equal([int(x['future_selected_good']) for x in hrecord],bins.reshape(-1,4).sum(axis=1))
   assert np.array_equal([int(x['R9_SYNTH_clock_UTC_ref']) for x in hrecord],href)
   assert int(np.sum((qref>0)&(bins>=qref)))==int(case['15m_quota_met'])
   assert int(np.sum((href>0)&(bins.reshape(-1,4).sum(axis=1)>=href)))==int(case['hourly_quota_met'])
   detail.append({'case':label,'all_future_selected_quote_indices_verified':len(sig),
     'independent_first_GOOD_before_ADVERSE_and_60s':True,'exact_source_UTC_quarter_hour_counts':True,
     'entry_exit_paid_actual_source_bidask_nominal_quote_net':True,
     'not_prospective_entry_or_cash_pnl':True})
 verified={'source':source,'month':mon,'raw_source_sha':r18.PINS[source][mon],
  'r18_original_selected_npz_sha':pin,'original_R9_UTC_reference_hash':refs['sha256'],
  'num_original_source_quote_rows_including_JUNE_tail':len(t),'original_UTC_quarters_checked':len(qkeys),
  'five_scenarios_exact_complete':True,'selected_source_count_across_scenarios':sum(x['all_future_selected_quote_indices_verified'] for x in detail),
  'source_selected_was_future_privileged':True,'no_broker_dealer_fill_verified':True,'details':detail,
  'source_file_sha256':{p.name:sha(p) for p in (res,qs,hr,trace,receipt)}}
 target=ROOT/'results_verified'/f'{stem}_INDEPENDENT_VERIFIED.json';target.parent.mkdir(exist_ok=True)
 target.write_text(json.dumps(verified,indent=2)+'\n')
 print('PASS',source,mon,'scenarios',len(detail),'quote_ordinals',verified['selected_source_count_across_scenarios'],flush=True)
 return target

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=r19.SOURCES,required=True);p.add_argument('--month',choices=r19.MONTHS,required=True);a=p.parse_args()
 verify(a.source,a.month)
