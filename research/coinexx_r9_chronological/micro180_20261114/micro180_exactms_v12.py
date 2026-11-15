"""V12 exact original-quote-ordinal micro180 lifecycle audit (research only).

Reads each original, SHA-pinned Coinexx monthly CSV.gz once. Price/time
arrays exist in RAM for that one month only and are never saved as ticks.
Runs *unchanged* V9. Annotations on exact original entry/exit ordinals,
including same-millisecond post-entry updates. No trade policy changes.
No intrasecond high-low reconstruction, no simulated fills from later marks.
"""
from __future__ import annotations

import argparse
from array import array
from bisect import bisect_left
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import os
import sys
import time

import numpy as np

# For the checked-out exact GitHub research source bundle.
HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('R9_RESEARCH_ROOT',
    HERE.parent if (HERE.parent/'src').is_dir() else HERE/'source'))
for sub in ('src','variable_cash_horizon_20261114','dual_basket_20261114','micro180_20261114'):
    sys.path.insert(0, str(ROOT/sub))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from v9_volume_router import VolumePreservingMicroV9

HORIZONS = (250,1000,3000,5000,15000,60000)
DRIFT_THRESHOLDS = (10,25,50,100)  # cents per ounce, relative to entry-side liquidation quote
MAX_QUOTE_GAP_MS = 2500
PRE_LOOKBACK_MS = (250,1000)
FIELDS = (
 'month','entry_ordinal','entry_time_msc','exit_ordinal','exit_time_msc','side',
 'entry_execution_u','entry_liquidation_u','entry_spread_u','exit_price_u',
 'exit_reason','hold_ms','lane_count','lanes','pre_quotes_250ms','pre_quotes_1000ms',
 'pre_mid_move_250ms_u','pre_mid_move_1000ms_u','entry_indicator_bias',
 'entry_quant_score','entry_z15','actual_quote_updates','actual_same_ms_updates',
 'actual_max_spread_u','actual_mfe_execution_u','actual_mae_execution_u',
 'actual_mfe_drift_u','actual_mae_drift_u','actual_first_adverse_10ms','actual_first_adverse_10_ordinal',
 'actual_first_favorable_10ms','actual_first_favorable_10_ordinal','forward_censored_gap','forward_censored_end',
 'forward_same_ms_updates','forward_250ms_liq_mark_u','forward_250ms_lag_ms',
 'forward_1000ms_liq_mark_u','forward_1000ms_lag_ms','forward_3000ms_liq_mark_u','forward_3000ms_lag_ms',
 'forward_5000ms_liq_mark_u','forward_5000ms_lag_ms','forward_15000ms_liq_mark_u','forward_15000ms_lag_ms',
 'forward_60000ms_liq_mark_u','forward_60000ms_lag_ms','first_drift_pos_10_ms','first_drift_pos_10_ordinal',
 'first_drift_neg_10_ms','first_drift_neg_10_ordinal',
 'first_drift_pos_25_ms','first_drift_pos_25_ordinal',
 'first_drift_neg_25_ms','first_drift_neg_25_ordinal',
 'first_drift_pos_50_ms','first_drift_pos_50_ordinal',
 'first_drift_neg_50_ms','first_drift_neg_50_ordinal',
 'first_drift_pos_100_ms','first_drift_pos_100_ordinal',
 'first_drift_neg_100_ms','first_drift_neg_100_ordinal',
)

SHA_2026 = {
'01':'1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8',
'02':'5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05',
'03':'3e9a03d97c6403036c4f5731e2e9eff43b8c4c9b25ac61adc6cc2147e3e79112',
'04':'f04660a094aa2d9738300c409f7f1c85868d5415c3bb8be11f0026740e7dc3be',
'05':'3e39c2810a40858f17245f4e07b6e15a0b52bbb48320a94fbe123a77c6343e29',
'06':'3033ccb257d067aecc123f3791d9dddc5c95841b9bba167ff1ca0cf1589dc2b4',
'07':'d9d47d40abb33935414edfb5c11f0c518d8c9cc27221da182dab0bc49b0b708d',
'08':'8e337d18377c318de17ceb72d46bbfc976a29cef4571dfa3457d3ac7fc0e1c17',
'09':'deaf191f65506178d501256f084a0ff4615fd21946f27ec1d9ee8f5e8c64b8ff',
}
EXPECTED_2026 = {
 '01':(7699274,35500,35500),'02':(7102818,42742,42742),
 '03':(8859103,51841,51841),'04':(7831685,37341,37340),
 '05':(8011360,32514,32514),'06':(9347508,37190,37190),
 '07':(8075197,33758,33758),'08':(7468061,32896,32896),
 '09':(7734341,34283,34283)
}

class ExactQuoteV9(VolumePreservingMicroV9):
    def __init__(self):
        super().__init__(R9Config(),ResearchCash(k=1.,cost=.20,
                           initial_capital=100000.,governor=False))
        self.times=array('q'); self.bids=array('i'); self.asks=array('i')
        self.trade_records=[]
        self.open_record=None
        self.highest_ordinal=0

    def on_tick(self,t):
        if t.ordinal!=self.highest_ordinal+1:
            raise ValueError('Source tick ordinal gap/reorder')
        if self.times and t.time_msc<self.times[-1]:
            raise ValueError('Nonmonotone source timestamp')
        self.highest_ordinal=t.ordinal
        self.times.append(t.time_msc)
        self.bids.append(t.bid_u)
        self.asks.append(t.ask_u)
        super().on_tick(t)

    def _open_trade(self,t,side):
        lanes=tuple(getattr(self,'_qualifying_lanes',()))
        n=len(self.entries)
        super()._open_trade(t,side)
        if len(self.entries)==n:return
        e=self.entries[-1]
        if self.open_record is not None:raise AssertionError('V9 unexpected multi-position')
        real_side=self.position.side
        if real_side not in (1,-1):raise AssertionError('Invalid direction')
        idx=t.ordinal-1
        def pre(window):
            left=bisect_left(self.times,t.time_msc-window)
            # Quote context prior to current entry, strict source ordinal.
            if idx<=left:return (0,None)
            b0=self.bids[left];a0=self.asks[left]
            return idx-left, (self.bids[idx]+self.asks[idx]-b0-a0)//2
        c250,m250=pre(250);c1000,m1000=pre(1000)
        bias=e.get('v9_buy_m1_bias' if real_side>0 else 'v9_sell_m1_bias','missing')
        quant=e.get('v9_buy_score' if real_side>0 else 'v9_sell_score','missing')
        z=e.get('v9_buy_z15' if real_side>0 else 'v9_sell_z15','missing')
        rec=dict(
         entry_ordinal=t.ordinal,entry_time_msc=t.time_msc,
         side=real_side,entry_execution_u=t.ask_u if real_side>0 else t.bid_u,
         entry_liquidation_u=t.bid_u if real_side>0 else t.ask_u,
         entry_spread_u=t.ask_u-t.bid_u,
         lane_count=len(lanes),lanes='|'.join(lanes),
         pre_quotes_250ms=c250,pre_quotes_1000ms=c1000,
         pre_mid_move_250ms_u=m250,pre_mid_move_1000ms_u=m1000,
         entry_indicator_bias=bias,entry_quant_score=quant,entry_z15=z,
         exit_ordinal=None,exit_time_msc=None,exit_price_u=None,exit_reason='OPEN'
        )
        self.trade_records.append(rec)
        self.open_record=rec

    def _record_close(self,t,reason,exit_u):
        if self.position is not None:
            rec=self.open_record
            if rec is None:raise AssertionError('Exit missing matching entry')
            rec.update(exit_ordinal=t.ordinal,exit_time_msc=t.time_msc,
                       exit_price_u=exit_u,exit_reason=reason)
            self.open_record=None
        return super()._record_close(t,reason,exit_u)


def _first(mask, ms, entry, entry_idx):
    hit=np.flatnonzero(mask)
    if not hit.size:return (None,None)
    at=int(hit[0])
    return int(ms[at]-entry), int(entry_idx+at+2) # original 1-based post-entry row ordinal


def trace_one(rec, times,bids,asks):
    """True source-ordinal sequence, including following rows at SAME ms.

    Forward observational marks after actual exit are counterfactual only;
    they never change existing exit, and cannot be interpreted as fills.
    """
    i=rec['entry_ordinal']-1
    n=len(times)
    now=int(times[i]);side=rec['side']
    max_j=min(n,int(np.searchsorted(times,now+61000,side='right')))
    future_ts=times[i+1:max_j]
    # All equal-ms following rows remain in file order; slicing by strict ordinal.
    entry_exec=rec['entry_execution_u'];entry_liq=rec['entry_liquidation_u']
    mark=np.asarray(bids[i+1:max_j] if side>0 else asks[i+1:max_j],dtype=np.int32)
    future_bid=np.asarray(bids[i+1:max_j],dtype=np.int32)
    future_ask=np.asarray(asks[i+1:max_j],dtype=np.int32)
    drift=side*(mark-entry_liq)
    execution_mark=side*(mark-entry_exec)
    if len(future_ts):
        diffs=np.diff(times[i:max_j])
        g=np.flatnonzero(diffs>MAX_QUOTE_GAP_MS)
        good_count=(int(g[0]) if g.size else len(future_ts))
    else:good_count=0
    # Distinguish no path in source file vs censoring due quote gaps.
    gap_censored=good_count<len(future_ts)
    # Horizons sample the first source quote at or after the elapsed target;
    # <=1s lag is separately exposed. First-passage always <=60s exactly.
    f_ts=future_ts[:good_count]
    f_drift=drift[:good_count]
    eligible_count=int(np.searchsorted(f_ts,now+60000,side='right'))
    passage_ts=f_ts[:eligible_count]; passage_drift=f_drift[:eligible_count]
    outcome={
       'forward_censored_gap':int(gap_censored),
       'forward_censored_end':int(not gap_censored and
                           (n==0 or int(times[-1])<now+60000)),
       'forward_same_ms_updates':int(np.count_nonzero(f_ts==now)),
    }
    for h in HORIZONS:
        key=f'forward_{h}ms_liq_mark_u'
        j=int(np.searchsorted(f_ts,now+h,side='left'))
        if j<len(f_ts) and int(f_ts[j])<=now+h+1000:
            outcome[key]=int(execution_mark[j])
            outcome[f'forward_{h}ms_lag_ms']=int(f_ts[j]-(now+h))
        else:
            outcome[key]=None
            outcome[f'forward_{h}ms_lag_ms']=None
    for threshold in DRIFT_THRESHOLDS:
        outcome[f'first_drift_pos_{threshold}_ms'],outcome[f'first_drift_pos_{threshold}_ordinal']=_first(passage_drift>=threshold,passage_ts,now,i)
        outcome[f'first_drift_neg_{threshold}_ms'],outcome[f'first_drift_neg_{threshold}_ordinal']=_first(passage_drift<=-threshold,passage_ts,now,i)

    exit_ord=rec['exit_ordinal']
    if exit_ord is None:
        outcome.update(hold_ms=None,actual_quote_updates=None,
            actual_same_ms_updates=None,actual_max_spread_u=None,
            actual_mfe_execution_u=None,actual_mae_execution_u=None,
            actual_mfe_drift_u=None,actual_mae_drift_u=None,
            actual_first_adverse_10ms=None,actual_first_adverse_10_ordinal=None,actual_first_favorable_10ms=None,actual_first_favorable_10_ordinal=None)
        return outcome
    j=exit_ord-1
    if j<i:raise AssertionError('Exit occurred before entry')
    if j>=n:raise AssertionError('Missing original exit quote')
    if times[j]!=rec['exit_time_msc']:raise AssertionError('Exit ms does not match source')
    executable=int(bids[j] if side>0 else asks[j])
    if rec['exit_price_u']!=executable:
        raise AssertionError('Exit is not executable Bid/Ask side')
    hold_ts=times[i+1:j+1]
    hold_liq=np.asarray(bids[i+1:j+1] if side>0 else asks[i+1:j+1],dtype=np.int32)
    d=side*(hold_liq-entry_liq)
    execution=side*(hold_liq-entry_exec)
    spread=np.asarray(asks[i+1:j+1],dtype=np.int32)-np.asarray(bids[i+1:j+1],dtype=np.int32)
    outcome.update(
      hold_ms=int(times[j])-now,
      actual_quote_updates=int(j-i),
      actual_same_ms_updates=int(np.count_nonzero(hold_ts==now)),
      actual_max_spread_u=int(max(rec['entry_spread_u'],int(spread.max()) if len(spread) else rec['entry_spread_u'])),
      actual_mfe_execution_u=int(max(-rec['entry_spread_u'],int(execution.max()) if len(execution) else -rec['entry_spread_u'])),
      actual_mae_execution_u=int(min(-rec['entry_spread_u'],int(execution.min()) if len(execution) else -rec['entry_spread_u'])),
      actual_mfe_drift_u=int(max(0,int(d.max()) if len(d) else 0)),
      actual_mae_drift_u=int(min(0,int(d.min()) if len(d) else 0)),
      actual_first_adverse_10ms=_first(d<=-10,hold_ts,now,i)[0],
      actual_first_adverse_10_ordinal=_first(d<=-10,hold_ts,now,i)[1],
      actual_first_favorable_10ms=_first(d>=10,hold_ts,now,i)[0],
      actual_first_favorable_10_ordinal=_first(d>=10,hold_ts,now,i)[1],
    )
    return outcome


def summarize(rows,month,quotes,source_sha,elapsed,output_file):
    stats=defaultdict(lambda:{'n':0,'hold_ms_sum':0,'hold_ms_n':0,
           'stop_n':0,'harvest_n':0,'spread_sum_u':0,'same_ms_follow_n':0,
           'first_adverse_10_n':0,'first_favorable_10_n':0,
           'mfe_positive_n':0,'mean_entry_pre_quotes_1s_sum':0,
           'forward_1000ms_observed':0,'forward_1000ms_signed_sum_u':0,
           'forward_5000ms_observed':0,'forward_5000ms_signed_sum_u':0,
           'forward_15000ms_observed':0,'forward_15000ms_signed_sum_u':0})
    exit_counts=Counter();hold_bins=Counter();bucket=Counter();lanes=Counter()
    count=0;completed=0
    with gzip.open(output_file,'wt',newline='',compresslevel=6) as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore');w.writeheader()
        for r in rows:
            count+=1
            w.writerow(r)
            if r['exit_ordinal'] is None:continue
            completed+=1
            reason=r['exit_reason'];exit_counts[reason]+=1
            ms=r['hold_ms']
            hb=('<250ms' if ms<250 else '250-999ms' if ms<1000 else '1-2.999s'
              if ms<3000 else '3-4.999s' if ms<5000 else '5-9.999s'
              if ms<10000 else '10-29.999s' if ms<30000 else '30s+')
            hold_bins[hb]+=1
            lane=r['lanes'] or 'NO_CAPTURED_LANE';lanes[lane]+=1
            sp=r['entry_spread_u'];spread_bucket='<=0.10' if sp<=10 else '0.11-0.20' if sp<=20 else '0.21-0.30' if sp<=30 else '>0.30'
            intensity='<=4' if r['pre_quotes_1000ms']<=4 else '5-15' if r['pre_quotes_1000ms']<=15 else '16-40' if r['pre_quotes_1000ms']<=40 else '>40'
            for name in ('ALL','SIDE:'+('BUY' if r['side']>0 else 'SELL'),
                         'EXIT:'+reason,'SPREAD:'+spread_bucket,
                         'PREQUOTE_1S:'+intensity,'LANE_COUNT:'+str(r['lane_count'])):
                s=stats[name];s['n']+=1;s['hold_ms_sum']+=ms;s['hold_ms_n']+=1
                s['stop_n']+=int(reason in ('stop','risk_first_available'))
                s['harvest_n']+=int(reason=='cash_010_harvest')
                s['spread_sum_u']+=sp
                s['same_ms_follow_n']+=int(r['actual_same_ms_updates']>0)
                s['first_adverse_10_n']+=int(r['actual_first_adverse_10ms'] is not None)
                s['first_favorable_10_n']+=int(r['actual_first_favorable_10ms'] is not None)
                s['mfe_positive_n']+=int(r['actual_mfe_execution_u']>0)
                s['mean_entry_pre_quotes_1s_sum']+=r['pre_quotes_1000ms']
                for horizon in (1000,5000,15000):
                    v=r[f'forward_{horizon}ms_liq_mark_u']
                    if v is not None:
                        s[f'forward_{horizon}ms_observed']+=1
                        s[f'forward_{horizon}ms_signed_sum_u']+=v
            for threshold in DRIFT_THRESHOLDS:
                a=r[f'first_drift_pos_{threshold}_ordinal'];b=r[f'first_drift_neg_{threshold}_ordinal']
                if a is not None and b is not None:
                    label='favorable_first' if a<b else 'adverse_first' if b<a else 'INVALID_EQUAL_ORDINAL'
                elif a is not None:label='favorable_only'
                elif b is not None:label='adverse_only'
                else:label='neither_observed'
                bucket[f'{threshold}c:{label}']+=1
    return {
      'month':month,'source_sha256':source_sha,'quotes':quotes,
      'entries':count,'completed_trades':completed,'open_positions':count-completed,
      'exact_source_row_ordinal':True,'month_trade_state_reset':True,
      'uses_resampled_second_bars':False,'uses_future_in_entry':False,
      'row_output':output_file.name,'row_output_bytes':output_file.stat().st_size,
      'elapsed_seconds':round(elapsed,1), 'exit_reason_counts':dict(exit_counts),
      'holding_bins':dict(hold_bins),'lane_signatures':dict(lanes),
      'first_passage_drift':dict(bucket),
      'by_group':dict(stats),'native_broker_fills_observed':False,
      'policy_or_broker_orders_changed':False,
      'note':'Forward quote marks after actual V9 exits are observational, not fills or trades.'
    }


def run_one(month,src_dir,out_dir,limit=0):
    if month not in EXPECTED_2026:raise ValueError('Invalid month')
    src=Path(src_dir)/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
    if not src.exists():raise FileNotFoundError(src)
    t0=time.monotonic()
    with src.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    if digest!=SHA_2026[month]:raise ValueError(f'{month}: SOURCE SHA mismatch {digest}')
    model=ExactQuoteV9()
    n=0
    for n,t in enumerate(iter_coinexx_ticks(src,strict=True),1):
        model.on_tick(t)
        if limit and n>=limit:break
    if not n:raise ValueError('Zero market data rows')
    if not limit or n<limit:
        if (n,len(model.entries),len(model.trades))!=EXPECTED_2026[month]:
            raise AssertionError(f'{month}: frozen V9 baseline mismatch '
                f'{n,len(model.entries),len(model.trades)} vs {EXPECTED_2026[month]}')
    if len(model.trade_records)!=len(model.entries):raise AssertionError('Missing entry events')
    if sum(x['exit_ordinal'] is not None for x in model.trade_records)!=len(model.trades):
        raise AssertionError('Missing closed trade events')
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    times=np.frombuffer(model.times,dtype=np.int64)
    bids=np.frombuffer(model.bids,dtype=np.int32)
    asks=np.frombuffer(model.asks,dtype=np.int32)
    def iter_rows():
        for rec in model.trade_records:
            yield dict(month=month,**rec,**trace_one(rec,times,bids,asks))
    ledger=out_dir/f'2026-{month}_V12_exactms_micro180_events.csv.gz'
    results=summarize(iter_rows(),month,n,digest,time.monotonic()-t0,ledger)
    output=out_dir/f'2026-{month}_V12_exactms_aggregate.json'
    output.write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'month':month,'quotes':n,'entries':results['entries'],
           'completed_trades':results['completed_trades'],
           's':round(time.monotonic()-t0,1),
           'ledger_compressed_MB':round(ledger.stat().st_size/1e6,2)}),flush=True)
    return results


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--month',required=True)
    ap.add_argument('--ticks-dir',type=Path,default=Path('/mnt/data'))
    ap.add_argument('--out-dir',type=Path,default=Path('/mnt/data/r9_micro180_v12_results'))
    ap.add_argument('--limit',type=int,default=0)
    a=ap.parse_args()
    run_one(a.month,a.ticks_dir,a.out_dir,a.limit)

if __name__=='__main__':main()
