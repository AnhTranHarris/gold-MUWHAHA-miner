#!/usr/bin/env python3
"""Independent second read of every saved R12BN future-selected source quote ordinal.
Rehash every source/day, recompute actual full15 favorable and full30 adverse
survivability on RAW SOURCE in a second pass. No student or live qualification.
"""
import csv,hashlib,json,sys,time
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2_r12_native');sys.path.insert(0,str(ROOT/'source'))
from r12b_month_native import read_day,source_days,_rolling_extrema,sha,atomic_write

def run():
 allchecks=[]; start=time.perf_counter()
 for mon in ('01','02','06','07'):
  for row in source_days(mon):
   tag=f'R12BN_{mon}_{row["date_utc"]}';rp=ROOT/'atomic'/(tag+'_receipt.json');npz=ROOT/'atomic'/(tag+'_traces.npz')
   saved=json.loads(rp.read_text());assert sha(npz)==saved['trace_npz_sha256']
   t,b,a,rec=read_day(row,mon)
   report={'month':mon,'day':row['date_utc'],'source_SHA':rec['source_sha256'],'NPZ_SHA':sha(npz),'raw_source_quotes':len(t)}
   with np.load(npz,allow_pickle=False) as z:
    for mode in ('FIRST250','ALL_DISTINCT_MS'):
     ix=z[mode+'__entry_tick_ordinal'];ex=z[mode+'__exit_tick_ordinal'];t0=z[mode+'__entry_ms'];end=z[mode+'__exit_ms'];side=z[mode+'__side'];recordnet=z[mode+'__source_net_after_fee_raw'];
     assert len(ix)==len(ex)==len(t0)==len(end)==len(side)==len(recordnet)
     assert len(ix)==saved['selected_'+('first250' if mode=='FIRST250' else 'all_distinctms')]
     assert np.all(ix<ex) and np.all(t[ix]==t0) and np.all(t[ex]==end)
     assert np.all(end>t0) and np.all(end<=t0+15000)
     if len(ix)>1:assert np.all(t0[1:]>end[:-1])
     liq=np.where(side>0,b[ex],a[ex]);entry=np.where(side>0,a[ix],b[ix]);net=(liq.astype(np.int64)-entry.astype(np.int64))*side-20
     assert np.array_equal(net,recordnet) and np.all(net>=100)
     # Source-exact full path, independent of stored S1 derived labels.
     mn15,mx15,ma15,xa15,_,_,cov15=_rolling_extrema(t,b,a,ix,15000)
     mn30,mx30,ma30,xa30,_,_,cov30=_rolling_extrema(t,b,a,ix,30000)
     buy=(side==1);sell=~buy
     assert np.all(cov15&cov30)
     assert np.all(mx15[buy].astype(np.int64)>=a[ix[buy]].astype(np.int64)+120)
     assert np.all(ma15[sell].astype(np.int64)<=b[ix[sell]].astype(np.int64)-120)
     assert np.all(mn30[buy].astype(np.int64)>b[ix[buy]].astype(np.int64)-100)
     assert np.all(xa30[sell].astype(np.int64)<a[ix[sell]].astype(np.int64)+100)
     report[mode+'_selected_rechecked']=len(ix)
   allchecks.append(report)
  print(mon,'days verified',len([v for v in allchecks if v['month']==mon]),flush=True)
 out={'source':'R12BN_SECOND_INDEPENDENT_SOURCE_REHASH_AND_ENTIRE_FUTURE_SELECT_TRACE_PNL_15_30_PROOF',
      'full_daily_receipt_count':len(allchecks),'raw_daily_months':list(('01','02','06','07')),
      'selected_rechecked_FIRST250':sum(x['FIRST250_selected_rechecked'] for x in allchecks),
      'selected_rechecked_ALL_DISTINCT':sum(x['ALL_DISTINCT_MS_selected_rechecked'] for x in allchecks),
      'every_complete_source_day_checked_against_raw':allchecks,
      'every_selected_side_15s_and30s_recomputed':True,
      'exec_correctness_not_broker_fills':True,'original_r9_EA_unchanged':True,
      'elapsed_seconds':round(time.perf_counter()-start,3)}
 path=ROOT/'reports'/'R12BN_ALL_FOUR_MONTHS_INDEPENDENT_EXACT_SOURCE_SELECTED_TRACE_VERIFICATION.json';
 atomic_write(path,(json.dumps(out,indent=2)+'\n').encode());print('COMPLETE',len(allchecks),out['selected_rechecked_FIRST250'],out['selected_rechecked_ALL_DISTINCT'],flush=True)
if __name__=='__main__':run()
