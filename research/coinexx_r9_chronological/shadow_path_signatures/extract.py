"""One-pass source-exact R9 event extraction with as-of quote-path features.

Outputs are derived candidate-level shadow observations, NOT tick-data substitutes.
Authoritative original raw gzip files are never modified. The same complete R9
state is carried across monthly inputs; a monthly boundary is not a model reset.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,pickle,sys
from collections import Counter
from dataclasses import asdict
from datetime import datetime,timezone
from pathlib import Path
from signatures import CausalQuotePath
from coinexx_r9.r9_baseline import R9HybridGateBaseline,R9Config,session_code
from coinexx_r9.ticks import iter_coinexx_ticks

MONTHS=[f'{m:02d}' for m in range(1,10)]
BASE_FIELDS=(
  'spread_u','session','r9_atr_u','r9_disp_signed_u','r9_eff','r9_range_u',
  'r9_turns','rearm','minute_second','entry_overshoot_u',
)

# Stable row schema, never infer feature order from historical outcome.
FEATURE_FIELDS=['quote_gap_ms']
for width in (500,2000,10000):
 p=f'w{width}'
 FEATURE_FIELDS += [
  f'{p}_bid_disp',f'{p}_ask_disp',f'{p}_spread_disp',f'{p}_sig_area2',
  f'{p}_sig_area_norm',f'{p}_eff',f'{p}_churn',f'{p}_events',
  f'{p}_bid_only',f'{p}_ask_only',f'{p}_both',f'{p}_up',f'{p}_down',
  f'{p}_intensity_log',f'{p}_signed_mid_disp',f'{p}_signed_bid_ask_agreement',
 ]
HEADER=['entry_month','entry_ordinal','exit_ordinal','entry_time_msc','exit_time_msc','side',
 'entry_price_u','exit_price_u','net_price_u','hold_ms','reason']+list(BASE_FIELDS)+FEATURE_FIELDS


def baseline_snapshot(b,t,side):
 c=b.cfg
 recent=list(b.micro)[-c.velocity_lookback_sec:]
 closes=[x.bid_close_u for x in recent]
 delta=[v-u for u,v in zip(closes,closes[1:])]
 disp=closes[-1]-closes[0]
 travel=sum(abs(v) for v in delta)
 prevsign=turns=0
 for d in delta:
  s=1 if d>0 else (-1 if d<0 else 0)
  if s:
   if prevsign and s!=prevsign: turns+=1
   prevsign=s
 r=list(b.micro)[-c.range_lookback_sec:]
 rng=max(x.bid_high_u for x in r)-min(x.bid_low_u for x in r)
 entry_price=t.ask_u if side>0 else t.bid_u
 threshold=b.cycle_buy_u if side>0 else b.cycle_sell_u
 overshoot=(entry_price-threshold)*side
 return {
  'spread_u':t.spread_points,
  'session':session_code(t.time_s,c.quote_utc_offset_minutes),
  'r9_atr_u':b.atr.atr_u if b.atr.atr_u is not None else 0,
  'r9_disp_signed_u':side*disp,
  'r9_eff':abs(disp)/(1e-9+travel),
  'r9_range_u':rng,'r9_turns':turns,'rearm':b.rearms,
  'minute_second':t.time_s%60,'entry_overshoot_u':overshoot,
 }


def sha256_file(path):
 h=hashlib.sha256()
 with open(path,'rb') as fh:
  for chunk in iter(lambda: fh.read(4*1024*1024),b''):
   h.update(chunk)
 return h.hexdigest()


def process(data_dir:Path,out_dir:Path, through_month='09',resume=False):
 out_dir.mkdir(parents=True,exist_ok=True)
 ckpt=out_dir/'checkpoint.pkl'
 if resume and ckpt.exists():
  with open(ckpt,'rb') as f: state=pickle.load(f)
  b,paths,pending,global_n,completed_months,metadata=state
 else:
  b=R9HybridGateBaseline();paths=CausalQuotePath();pending={}
  global_n=0;completed_months=[];metadata={}
 # One atomic, complete file per source month. Checkpoint and output are committed
 # only after all rows have been traversed; resuming cannot duplicate partial rows.
 for month in MONTHS:
  if month in completed_months:continue
  if month>through_month:break
  raw=data_dir/f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
  if not raw.is_file():raise FileNotFoundError(raw)
  sha=sha256_file(raw)
  month_csv=out_dir/f'candidate_closes_2026_{month}.csv.gz'
  temp_csv=out_dir/f'candidate_closes_2026_{month}.partial.gz'
  output=gzip.open(temp_csv,'wt',encoding='utf-8',newline='')
  writer=csv.DictWriter(output,fieldnames=HEADER,extrasaction='raise')
  writer.writeheader()
  first=last=None
  rows=same_msc=entries=closes=0
  previous=None
  for tick in iter_coinexx_ticks(raw,ordinal_offset=global_n):
   rows+=1
   if first is None:first=tick.time_msc
   last=tick.time_msc
   if previous==tick.time_msc:same_msc+=1
   previous=tick.time_msc
   paths.observe(tick.time_msc,tick.bid_u,tick.ask_u)
   b.on_tick(tick)
   # R9 baseline has no dependence on its output lists; drain immediately to
   # retain only open-position state and prevent memory growth over nine months.
   if b.entries:
    entry=b.entries.pop()
    side=entry['side']
    snap=baseline_snapshot(b,tick,side)
    snap.update(paths.snapshot(side))
    snap.update({'entry_month':datetime.fromtimestamp(tick.time_msc/1000,timezone.utc).strftime('%Y-%m'),
     'entry_ordinal':tick.ordinal,'entry_time_msc':tick.time_msc,'side':side,
     'entry_price_u':entry['price_u']})
    pending[tick.ordinal]=snap
    entries+=1
   if b.trades:
    trade=b.trades.pop()
    snap=pending.pop(trade.entry_ordinal)
    snap.update({'exit_ordinal':trade.exit_ordinal,'exit_time_msc':trade.exit_time_msc,
     'exit_price_u':trade.exit_price_u,'net_price_u':trade.net_price_u,
     'hold_ms':trade.exit_time_msc-trade.entry_time_msc,'reason':trade.reason})
    writer.writerow(snap)
    closes+=1
  output.close()
  if rows==0:raise ValueError(f'empty source {month}')
  temp_csv.replace(month_csv)
  global_n+=rows
  metadata[month]={'rows':rows,'first_time_msc':first,'last_time_msc':last,
   'source_sha256':sha,'equal_adjacent_millisecond_rows':same_msc,
   'entries':entries,'closed_positions':closes,'open_at_month_end':len(pending)}
  completed_months.append(month)
  with open(ckpt.with_suffix('.tmp'),'wb') as f:
   pickle.dump((b,paths,pending,global_n,completed_months,metadata),f,protocol=5)
  ckpt.with_suffix('.tmp').replace(ckpt)
  (out_dir/'progress.json').write_text(json.dumps({'completed_months':completed_months,
   'rows':global_n,'open_positions':len(pending),'source_months':metadata,
   'r9_stats':dict(b.stats)},indent=2)+'\n')
  print(f'COMPLETE {month} rows={rows:,} entries={entries:,} closes={closes:,} open={len(pending)}',flush=True)
 if completed_months[-1]=='09':
  if pending:raise ValueError('open positions at September EOF; do not silently drop labels')
  receipt={'source_months':metadata,'total_rows':global_n,
   'completed_months':completed_months,'r9_stats':dict(b.stats),
   'path_signature_windows_ms':list(paths.windows),
   'candidate_rows':sum(v['closed_positions'] for v in metadata.values()),
   'cost_basis':'raw quote-side price PnL in integer 0.01 XAUUSD units; no assumed server fill/commission',
   'baseline':'carson/coinexx-r9-chronological-backtest-v1-20261112 SHA de3e617',
   'deployment':'research shadow only; no EA modification or live authorization'}
  (out_dir/'source_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print('FULL SOURCE COMPLETE',json.dumps({'rows':global_n,'trades':receipt['candidate_rows']}),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--data-dir',type=Path,default=Path('/mnt/data'))
 p.add_argument('--out-dir',type=Path,default=Path('/mnt/data/r9_shadow_path_signatures/outputs'))
 p.add_argument('--through-month',default='09')
 p.add_argument('--resume',action='store_true')
 a=p.parse_args()
 process(a.data_dir,a.out_dir,a.through_month,a.resume)
