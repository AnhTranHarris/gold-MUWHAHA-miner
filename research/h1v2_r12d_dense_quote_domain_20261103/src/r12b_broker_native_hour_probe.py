"""R12B isolated broker-native R9 SYNTH future-known quote-ordinal hindsight probe.

Experimental oracle ONLY. A new source-domain, not a Dukascopy repair or EA.
Source R9 SYNTH Strategy Tester logs are not actual broker live execution.
"""
from __future__ import annotations
import argparse,json,datetime as dt
from pathlib import Path
import numpy as np,pandas as pd
from r12_dense_requote import asof_quote_clocks,_rolling_extrema
from r12_tp_oracle import earliest_finish_schedule,quote_tp_first,sha
ROOT=Path('/mnt/data');OUT=ROOT/'h1v2_r12/results'

def probe(day='2026-02-02', hour_utc=6, variant='ALL_DISTINCT_MS'):
 p=ROOT/f'R9_SYNTH_{day}_ticks.csv.gz';rr=ROOT/'h1v2_r12/atomic_r9_synth'/(p.name+'.entry_receipt.json');r=json.loads(rr.read_text())
 assert sha(p)==r['source_sha256']
 f=pd.read_csv(p,compression='gzip',usecols=['time_msc','bid','ask'],dtype={'time_msc':np.int64,'bid':np.float64,'ask':np.float64})
 assert len(f)==r['all_raw_source_rows']
 t=f.time_msc.to_numpy(np.int64,copy=True)-2*3600000
 b=np.rint(f.bid.to_numpy()*1000).astype(np.int32);a=np.rint(f.ask.to_numpy()*1000).astype(np.int32)
 assert np.all(b<=a) and np.all(t[1:]>=t[:-1])
 hstr=f'{day}T{hour_utc:02d}:00:00Z'
 h=int(dt.datetime.strptime(hstr,'%Y-%m-%dT%H:%M:00Z').replace(tzinfo=dt.timezone.utc).timestamp()*1000)
 orig_refs=pd.read_csv(OUT/'R12_02_ORIGINAL_R9_SYNTH_ALL_ENTRY_EVENTS_CLOCKALIGNED_UTC.csv')
 rr=orig_refs[(orig_refs.utc_entry_ms>=h)&(orig_refs.utc_entry_ms<h+3600000)]
 print('start source',day,'hour',hour_utc,'original R9 events',len(rr),flush=True)
 ii,flags=asof_quote_clocks(t,b,a)
 mask=(t[ii]>=h)&(t[ii]<h+3600000)
 if variant=='FIRST250':mask&=(flags&1)!=0
 ix=ii[mask]
 print('candidate ordinals',len(ix),flush=True)
 mb15,xb15,ma15,xa15,_,_,c15=_rolling_extrema(t,b,a,ix,15000)
 mb30,xb30,ma30,xa30,_,_,c30=_rolling_extrema(t,b,a,ix,30000)
 bb=b[ix].astype(np.int64);aa=a[ix].astype(np.int64)
 goodbuy=(xb15.astype(np.int64)>=aa+120)&(mb30.astype(np.int64)>bb-100)&c15&c30
 goodsell=(ma15.astype(np.int64)<=bb-120)&(xa30.astype(np.int64)<aa+100)&c15&c30
 valid=goodbuy|goodsell;assert not np.any(goodbuy&goodsell)
 vix=ix[valid];vside=np.where(goodbuy[valid],1,-1).astype(np.int8)
 ex,xt=quote_tp_first(t,b,a,vix,a[vix],b[vix],vside)
 assert np.all(ex>=0) and np.all(xt>t[vix])
 ss=earliest_finish_schedule(t[vix],xt)
 q={};
 for j in range(4):
  q0=h+j*900000
  rid=int(np.sum((rr.utc_entry_ms>=q0)&(rr.utc_entry_ms<q0+900000)))
  ids=np.flatnonzero((t[vix]>=q0)&(t[vix]<q0+900000))
  cap=len(earliest_finish_schedule(t[vix][ids],xt[ids])) if len(ids) else 0
  chosen=int(np.sum((t[vix][ss]>=q0)&(t[vix][ss]<q0+900000)))
  q[j]={'R9_original_reference':rid,'native_SYNTH_strict_good_eligible':len(ids),'isolated_quarter_exact_max_firstTP':cap,'globally_selected':chosen,'quota_met':chosen>=rid}
 d={'research_domain':'R9_SYNTH_NATIVE_SOURCE_TESTER_QUOTE_LOGGER_NOT_DUKAS_FORESIGHT',
    'day':day,'utc_hour':hstr,'source_log_sha':r['source_sha256'],'original_R9_hour_reference':len(rr),
    'source_tick_rows_in_day':len(t),'observed_decision_event_candidate_count':len(ix),
    'strict_first15fav_and_full30survival_candidate_count':int(valid.sum()),
    'one_open_position_future_FIRST_TP_max_count_in_hour_only':len(ss),
    'four_15minute_exact_original_R9_source_counts':q,'future_privileged':True,'no_broker_fill_proof':True}
 out=OUT/f'R12B_NATIVE_R9_SYNTH_{day}_{hour_utc:02d}UTC_HINDSIGHT_PROBE.json';out.write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps(d,indent=2))
 return d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--day',default='2026-02-02');p.add_argument('--hour',type=int,default=6);p.add_argument('--variant',choices=['FIRST250','ALL_DISTINCT_MS'],default='ALL_DISTINCT_MS');x=p.parse_args();probe(x.day,x.hour,x.variant)
