#!/usr/bin/env python3
"""Isolated R9_SYNTH_NATIVE full source-month teacher; never an EA or causal strategy.

Each immutable source daily gzip is independently SHA checked against the ORIGINAL
R12 atomic receipt and Drive index. Decisions use only actually OBSERVED quotes,
first250ms or all distinctms; outcomes and scheduling intentionally use FUTURE
quotes. Exact synthetic tester native Bid/Ask, fee $0.02, favorable net +$0.10
by <=15s, opening liquidation adverse <=-$0.10 prohibited for ALL 30s.
Position exits at the first observed future quote with net>=+$0.10; strict
next entry after exit_ms. Source day split is conservative; first 300s warmup
and last 30s coverage, not a fictitious across-file fill. Persist atomic daily
source ordinals/traces with SHA, then combine every original R9 source UTC quarter.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,gzip,hashlib,json,os,sys,time
from collections import Counter
from pathlib import Path
import numpy as np,pandas as pd
SRC=Path('/mnt/data'); R12=SRC/'h1v2_r12'; ROOT=SRC/'h1v2_r12_native'; ATOM=ROOT/'atomic'; REPORT=ROOT/'reports';
sys.path.insert(0,str(R12/'source'))
from r12_dense_requote import asof_quote_clocks,_rolling_extrema
from r12_tp_oracle import earliest_finish_schedule,quote_tp_first,sha,write_csv
MONTHS=('01','02','06','07');OFF={'01':-2,'02':-2,'06':-3,'07':-3}

def atomic_write(path,content):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.NEW');tmp.write_bytes(content);os.replace(tmp,path)

def source_days(month):
 idx=list(csv.DictReader((SRC/'R9_SYNTH_TICK_DRIVE_INDEX.csv').open(newline='')))
 rows=[r for r in idx if r['month']==f'2026_{month}'];assert len(rows)>=20,(month,len(rows))
 # First source day of following month can still contain this month's UTC entries.
 following=f'2026_{int(month)+1:02d}'
 nextday=next((r for r in idx if r['month']==following),None)
 if nextday:rows.append(nextday)
 return rows

def read_day(row,month):
 p=SRC/row['file_name']; recp=R12/'atomic_r9_synth'/(p.name+'.entry_receipt.json')
 rec=json.loads(recp.read_text());assert p.stat().st_size==int(row['size_bytes'])==rec['gzip_bytes']; assert sha(p)==rec['source_sha256']
 assert rec['source_file_drive_id']==row['drive_file_id']
 f=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'],
               dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
 assert len(f)==rec['all_raw_source_rows']
 t=f.time_msc.to_numpy(np.int64,copy=True)+OFF[month]*3600000
 b=np.rint(f.bid.to_numpy()*1000).astype(np.int32);a=np.rint(f.ask.to_numpy()*1000).astype(np.int32)
 assert np.all(t[1:]>=t[:-1]) and np.all(b<=a) and np.all(a-b>=0)
 return t,b,a,rec

def one_day(row,month):
 ATOM.mkdir(parents=True,exist_ok=True);p=SRC/row['file_name']
 short=f'R12BN_{month}_{row["date_utc"]}';meta_path=ATOM/(short+'_receipt.json');npzpath=ATOM/(short+'_traces.npz')
 if meta_path.exists() and npzpath.exists():
  r=json.loads(meta_path.read_text());orig=json.loads((R12/'atomic_r9_synth'/(p.name+'.entry_receipt.json')).read_text())
  assert sha(p)==orig['source_sha256']==r['source_sha256'] and sha(npzpath)==r['trace_npz_sha256']
  return r
 t,b,a,rec=read_day(row,month)
 ix,flags=asof_quote_clocks(t,b,a)
 assert np.all(np.diff(ix)>0)
 # All original candidate quotes use as-of-observable price for this clock.
 min15,max15,mina15,maxa15,n15,age15,c15=_rolling_extrema(t,b,a,ix,15000)
 min30,max30,mina30,maxa30,n30,age30,c30=_rolling_extrema(t,b,a,ix,30000)
 eb=b[ix].astype(np.int64);ea=a[ix].astype(np.int64)
 gb=(max15.astype(np.int64)>=ea+120)&(min30.astype(np.int64)>eb-100)&c15&c30
 gs=(mina15.astype(np.int64)<=eb-120)&(maxa30.astype(np.int64)<ea+100)&c15&c30
 assert not np.any(gb&gs)
 goodix=ix[gb|gs]; side=np.where(gb[gb|gs],1,-1).astype(np.int8)
 ex,ex_t=quote_tp_first(t,b,a,goodix,a[goodix],b[goodix],side)
 assert np.all(ex>=0) and np.all(ex_t>t[goodix]) and np.all(ex_t<=t[goodix]+15000)
 liq=np.where(side>0,b[ex],a[ex]).astype(np.int64)
 net=(liq-np.where(side>0,a[goodix],b[goodix]).astype(np.int64))*side-20
 assert np.all(net>=100)
 distinct=(gb|gs); first250=(flags[distinct]&1)!=0
 data={}
 for key,where in [('ALL_DISTINCT_MS',np.ones(len(goodix),bool)),('FIRST250',first250)]:
  positions=np.flatnonzero(where)
  selected=positions[earliest_finish_schedule(t[goodix[positions]],ex_t[positions])] if len(positions) else np.empty(0,np.int64)
  assert not len(selected)>1 or np.all(t[goodix[selected[1:]]]>ex_t[selected[:-1]])
  data[key]={'entry_ms':t[goodix[selected]],'exit_ms':ex_t[selected],
        'entry_tick_ordinal':goodix[selected],'exit_tick_ordinal':ex[selected],
        'side':side[selected], 'source_net_after_fee_raw':net[selected],
        'raw_entry_bid':b[goodix[selected]],'raw_entry_ask':a[goodix[selected]]}
  # We cannot link across source daily files; warmup and 30s coverage at each
  # file boundary exclude marginal entries; no false positive can be created.
 np.savez_compressed(npzpath,**{key+'__'+field:value for key,dat in data.items() for field,value in dat.items()})
 receipt={'experiment':'R12BN_SYNTH_SOURCE_NATIVE_FULL_MONTH_ATOMIC_DAY','target_month':month,'source_day':row['date_utc'],
   'source_file_name':p.name,'source_drive_id':row['drive_file_id'],'source_sha256':rec['source_sha256'],
   'source_raw_quote_rows':len(t),'source_eligible_distinct_ms':len(ix),'source_eligible_first250':int(((flags&1)!=0).sum()),
   'strict_first15_favorable_safe_full30_distinctms':len(goodix),
   'strict_first15_favorable_safe_full30_first250':int(first250.sum()),
   'selected_all_distinctms':len(data['ALL_DISTINCT_MS']['entry_ms']),
   'selected_first250':len(data['FIRST250']['entry_ms']),
   'all_source_quotes_are_synthetic_tester_not_broker_real':True,
   'source_day_split_5min_warmup_30s_censor_conservative':True,
   'trace_npz_file':npzpath.name,'trace_npz_sha256':sha(npzpath)}
 atomic_write(meta_path,(json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode('utf8'))
 return receipt

def month(mon):
 REPORT.mkdir(parents=True,exist_ok=True);start=time.perf_counter();rows=source_days(mon)
 receipts=[]
 for j,row in enumerate(rows):
  r=one_day(row,mon);receipts.append(r)
  print(mon,j+1,len(rows),row['date_utc'],'selected',r['selected_all_distinctms'],flush=True)
 # Collapse original R9 ref into full month 15-minute UTC calendar (verified
 # already exact 2,880 hour/11,520 quarter source event ledger).
 refpath=R12/'results'/f'R12_{mon}_ALL_UTC_QUARTERS_WITH_R9_SYNTH_VERIFIED.csv'
 refs=list(csv.DictReader(refpath.open(newline='')))
 assert len(refs) in (2688,2880,2976)
 counts={k:Counter() for k in ['FIRST250','ALL_DISTINCT_MS']}
 written=[]
 for r in receipts:
  with np.load(ATOM/r['trace_npz_file'],allow_pickle=False) as z:
   for key in counts:
    t=z[key+'__entry_ms'];end=z[key+'__exit_ms']
    assert len(t)==r['selected_'+('first250' if key=='FIRST250' else 'all_distinctms')]
    if len(t)>1:assert np.all(t[1:]>end[:-1])
    for quarter,n in zip(*np.unique(t//900000,return_counts=True)):
     counts[key][int(quarter)]+=int(n)
  written.append({'source_day':r['source_day'],'source_sha256':r['source_sha256'],'trace_sha256':r['trace_npz_sha256'],
                  'selected_first250':r['selected_first250'],'selected_all_distinct':r['selected_all_distinctms']})
 out=[]; active=Counter(); impossible=Counter(); miss=[]
 for r in refs:
  key=r['utc_quarter'];base=int(r['R9_SYNTH_exact_15min_reference']);bucket=int(dt.datetime.strptime(key,'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp())//900
  first=counts['FIRST250'].get(bucket,0);dense=counts['ALL_DISTINCT_MS'].get(bucket,0)
  out.append({'month':'2026-'+mon,'utc_quarter':key,'utc_hour':r['utc_hour'],'r9_SYNTH_EXACT_15M_reference':base,
    'r12dq_DUKASCOPY_dense_firstTP_selected':int(r.get('R12D_QUOTA_SELECTED',r.get('R12DQ_dense_firstTP_selected',0)) or 0) if 'R12D_QUOTA_SELECTED' in r or 'R12DQ_dense_firstTP_selected' in r else '',
    'r12b_NATIVE_testlog_FIRST250_selected':first,'r12b_NATIVE_testlog_ALL_DISTINCT_SELECTED':dense,
    'r12b_FIRST250_quota_met':int(first>=base) if base else '',
    'r12b_ALL_DISTINCT_quota_met':int(dense>=base) if base else '',
    'research_domain':'SYNTHETIC_MT5_STRATEGY_TESTER_NOT_REAL_TICKS',
    'cross_daily_boundaries_conservative_30s_censor':True,'strict_safety_LABEL_future_omniscient':True})
  if base:
   active['total']+=1;active['first']+=int(first>=base);active['dense']+=int(dense>=base)
   if dense<base:miss.append({'utc_quarter':key,'ref':base,'native_dense_selected':dense,'native_first250_selected':first})
 # Original all 117585 ref counts across 4 months same daily event source; per-month
 # original R9 quarter ref checks from verified R12 quotient archive.
 expected={'01':27980,'02':33523,'06':31758,'07':24324}[mon]
 assert sum(int(r['r9_SYNTH_EXACT_15M_reference']) for r in out)==expected
 write_csv(REPORT/f'R12BN_{mon}_COMPLETE_ORIGINAL_R9_QUARTERS_SYNTH_NATIVE.csv',out,list(out[0]))
 write_csv(REPORT/f'R12BN_{mon}_ALL_UNMET_QUARTERS_SYNTH_NATIVE.csv',miss,list(miss[0]) if miss else ['utc_quarter','ref','native_dense_selected','native_first250_selected'])
 ret={'month':mon,'original_R9_SYNTH_verified_entry_reference':expected,'original_source_day_files':len(rows),
    'r9_active_quarters':active['total'],'FIRST250_source_native_quarters_met':active['first'],
    'ALL_DISTINCT_source_native_quarters_met':active['dense'], 'unmet_under_native_all_distinct':len(miss),
    'total_atomic_daily_selected_all_distinct':sum(x['selected_all_distinctms'] for x in receipts),
    'total_atomic_daily_selected_first250':sum(x['selected_first250'] for x in receipts),
    'traces_orig_source_ordinal_per_day_complete':True,
    'full_replay_EA_or_PnL_not_validated':True,'synthetic_strategy_tester_source_not_Coinexx_live_ticks':True,
    'result_csv_sha':sha(REPORT/f'R12BN_{mon}_COMPLETE_ORIGINAL_R9_QUARTERS_SYNTH_NATIVE.csv'),
    'per_daily_source_and_trace_SHA':written, 'elapsed_s':round(time.perf_counter()-start,3)}
 atomic_write(REPORT/f'R12BN_{mon}_FULLMONTH_RECEIPT.json',(json.dumps(ret,indent=2,allow_nan=False)+'\n').encode())
 print(json.dumps({k:v for k,v in ret.items() if k not in ('per_daily_source_and_trace_SHA',)},indent=2),flush=True)
 return ret
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--month',required=True,choices=MONTHS);args=a.parse_args();month(args.month)
