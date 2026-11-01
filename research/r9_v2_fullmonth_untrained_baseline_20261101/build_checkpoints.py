#!/usr/bin/env python3
"""Lossless monthly checkpoint assembly for the completed full-month untrained lane.

No sampling, reruns, training, optimization or strategy changes here. Each checkpoint
contains the exact entire compressed trade ledger + complete source implementation.
"""
from __future__ import annotations
import csv, hashlib, json, zipfile
from pathlib import Path
ROOT=Path('/mnt/data/r9_v2_fullmonth_baseline_verified_20261101')
REPAIR=Path('/mnt/data/r9_v2_high_volume_repair')
V2=Path('/mnt/data/r9_entry_router_v2')
OUT=ROOT/'checkpoints';OUT.mkdir(exist_ok=True)
M= json.loads((ROOT/'EIGHT_MONTH_SOURCE_BASELINE.json').read_text())
with (ROOT/'SOURCE_EXACT_BASELINE_README.md').open('w') as f:
 f.write('''# R9 v2 high-volume UNTRAINED entry baseline — complete source-exact 2026 Jan/Feb/Jun/Jul

**Purpose:** Preserve the full native-month historical evidence, before Bayesian/NP fitting or optimization. Both brokers separately. This is a verified copy/independent revalidation of complete chronological runs performed in the preceding checkpoint; it is **not** a claim that 64.5m ticks were recalculated in this checkpoint. No sampling, estimation, or scaling of monthly results.

**Version boundary:** The high-volume event-stream *research specialist lane* is NOT a fitted Bayesian/Neyman–Pearson classifier, though it uses the same source-v2 rolling clocks, 250 ms event evaluation and unchanged R9-style lifecycle assumptions. The freeze is the GitHub branch `carson/r9-v2-high-volume-event-stream-repair-20261101`. Full code, not any summary, is packaged in every broker/month checkpoint. No MQL5 compile, no broker fill simulation, no live deployment.

**Contract:** Every broker/month must execute at least 85% of the identical calendar month's R9 SYNTH completed trades; BUY/SELL proposals are not counted. Trade count is a constraint, not a permission to lose money. Results fail the profitability criterion in all eight cases.

**Cost and risk:** 0.01 lot XAUUSD (price P&L in dollar-like units under an assumed 100-ounce standard lot); fixed $0.02 cost each completed trade; executable bid/ask reference marks and no slippage, stop-level, margin/capital limits or liquidity impact. These results are idealized research paths, NOT deployable account P&L. The $0.02 fee is NOT verified as the actual Coinexx broker commission. An undercapitalized EA could not sustain these modeled losses.

**Data:** Full original monthly Coinexx/Dukascopy tick files are reused by SHA-256. They are not duplicated in each checkpoint. Source file hashes are explicitly embedded. The R9 SYNTH reference month counts came from the original seven-month historical SYNTH teacher extract; SYNTH does not enter runtime decisions.

**Independent verification:** Each saved ledger was read end-to-end; closing price, direction, fixed fee, realized P&L, time order, concurrency, counts, full tick input checksum, original source blob and 85% volume gate were checked. No missing months.

**Monthly scores**

| Feed | Month | R9 SYNTH | V2 completed | Volume floor | Win% | PF | Mean net/trade | Net USD |
|---|---|---:|---:|---:|---:|---:|---:|---:|
''')
 for r in M['months']:
  f.write(f"| {r['source']} | {r['month']} | {r['r9_synth_trades']:,} | {r['closed_trades']:,} | {r['min_trades_85pct']:,} | {r['win_rate_pct']:.3f} | {r['profit_factor']:.4f} | {r['avg_net_per_trade_usd']:.5f} | {r['modeled_net_0p01_lot_usd']:,.2f} |\n")
 f.write('''\n**Verdict:** Trade throughput succeeds in all eight source-months, but economic behavior is unacceptable. This is a pretraining baseline only. Both the original strict BNP/NP path and the amended throughput lane remain distinct, preserved, and NOT promoted.
''')

all_code=[]
for base,rootname in ((REPAIR,'high_volume_repair'),(V2,'router_v2')):
 for subset in ('src','tests','docs'):
  folder=base/subset
  if folder.exists():
   all_code.extend((p,f'code/{rootname}/{subset}/'+p.relative_to(folder).as_posix()) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for p in (REPAIR/'SOURCE_PINS_AND_VOLUME_TARGETS.json',REPAIR/'README.md'):
 all_code.append((p,'code/high_volume_repair/'+p.name))
all_code.append((ROOT/'verify_fullmonth_baseline.py','audit/verify_fullmonth_baseline.py'))

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(2**20),b''):h.update(c)
 return h.hexdigest()

index=[]
for r in M['months']:
 source=r['source'];month=r['month'][-2:];tag=f'{source}_{month}'
 run=REPAIR/'results'/f'{tag}_full'
 files=[(run/'trades.csv.gz','full_run/trades.csv.gz'),(run/'result.json','full_run/result.json'),(run/'run.log','full_run/run.log'),(run/'validation.json','full_run/validation.json'),(ROOT/f'{source}_{r["month"]}_VERIFIED.json','audit/VERIFIED.json'),(ROOT/'SOURCE_EXACT_BASELINE_README.md','README.md')]+all_code
 check={'source':source,'month':r['month'],'original_ticks_sha256':r['source_file_sha256'],
        'strategy':'untrained high-volume v2 causal specialists','trained_NP':False,
        'files':{arc:{'sha256':sha(p),'bytes':p.stat().st_size} for p,arc in files}}
 name=f'R9_V2_FULLMONTH_{source.upper()}_2026_{month}_EXACT.zip';dest=OUT/name
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_STORED) as z:
  for p,arc in files:z.write(p,arc)
  z.writestr('MANIFEST.json',json.dumps(check,indent=2))
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  assert z.read('full_run/trades.csv.gz')== (run/'trades.csv.gz').read_bytes()
 index.append({'source':source,'month':r['month'],'name':name,'size':dest.stat().st_size,'sha256':sha(dest),
  'trades':r['closed_trades'],'net':r['modeled_net_0p01_lot_usd'],'source_ticks':r['ticks'],
  'source_sha256':r['source_file_sha256']})
(OUT/'CHECKPOINT_INDEX.json').write_text(json.dumps(index,indent=2))
print(json.dumps(index,indent=2))
