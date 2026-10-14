from pathlib import Path
import json,hashlib,zipfile,csv,re,os
import numpy as np
R=Path('/mnt/data/GRID0272_JAN_COMBINATIONS')
raw=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
source=R/'ORIGINAL';ref='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
sha=lambda p:hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()
assert sha(raw)==ref
r9=json.load(open(source/'r9_synth_jan_daily_weekly.json'))
candidates=[]
for p in R.glob('original_composite_raw_*json'):
 j=json.load(open(p));j['filename']=p.name
 candidates.append(j)
candidates.sort(key=lambda x:(x['equity_dd'],-x['net']))
repro=json.load(open(R/'original_131a_working.json'))['rows'][0]
assert repro['net']==139070.41 and repro['trades']==77942
source_files=sorted(source.glob('*.py'))
# Provenance manifest original source EXACT bytes, not handoff summaries
files=[dict(path=str(p.relative_to(R)),bytes=p.stat().st_size,sha256=sha(p)) for p in source_files]
manifest={
 'governance':'OWNER_20261013_FULL_PROGRESSIVE_JAN_JUL_ROADMAP_VERBATIM.md; OWNER_20261013_VERBATIM_ANTI_SUMMARY_MONTHLY_PROGRESS_QC_LAW.md',
 'active_branch':'delta-A-alpha', 'official_journal':'J0183 unchanged', 'august':'SEALED', 'trading':'OFF',
 'original_january_git_branch':'carson/r9-gamma-02-jan-grid-milestone',
 'original_raw_tick_source':str(raw),'original_raw_tick_sha256':ref,'original_tick_count':9135062,
 'r9_january_synth_target_cash':r9['month']['net'],'r9_month_trades':r9['month']['trades'],
 'original_131a_normalized_replayed':{'net':repro['net'],'trades':repro['trades'],'equity_dd':repro['equity_dd']},
 'original_source_file_hashes':files,
 'updated_research_20261013':'ONLY prototypes; no approved engineering engine or scientific cursor modified',
 'community_references':['https://www.mql5.com/en/articles/21833','https://www.mql5.com/en/code/73958','https://www.fmz.com/strategy/530403','https://www.reddit.com/r/algotrading/comments/1shgpyf/'],
 'replay_runner':'original_latency.py; combine_original_latency.py; combo_research.py',
 'r9_synth_cash_per_week':{k:v['net'] for k,v in r9['weekly'].items()},
 'replay_values_not_comparable_to_raw_mt5_production':'Costs/latency modeled, upstream source funding event admission may still use legacy historical economic assumptions, no actual broker fills and no calibrated FourSessionV1 integration.',
 'per_trade_OVERFIT_75_percent':'NOT SCORED; original offline teacher not re-matched',
}
(R/'EXACT_SOURCE_QA_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
scorefile=R/'GRID0272_JANUARY_CANDIDATE_SCORECARD.csv'
with scorefile.open('w',newline='') as f:
 cols=['candidate','net','trades','gross_loss','pf','equity_dd','balance_dd','positive_days','beat_days','positive_weeks','beat_weeks','wk1_net','wk1_target','full_month_net_pass','trade_velocity_pass','all_weeks_pass','all_days_pass'];w=csv.DictWriter(f,cols);w.writeheader()
 for j in sorted(candidates,key=lambda x:-x['net']):
  w.writerow(dict(candidate=j['filename'],net=round(j['net'],3),trades=j['trades'],gross_loss=round(j['gross_loss'],3),pf=round(j['pf'],3),equity_dd=round(j['equity_dd'],3),balance_dd=round(j['balance_dd'],3),positive_days=j['positive_days'],beat_days=j['beat_days'],positive_weeks=j['positive_weeks'],beat_weeks=j['beat_weeks'],wk1_net=round(j['weekly']['2026-W01']['net'],3),wk1_target=r9['weekly']['2026-W01']['net'],full_month_net_pass=j['net']>=r9['month']['net'],trade_velocity_pass=j['trades']>=r9['month']['trades'],all_weeks_pass=j['beat_weeks']==5,all_days_pass=j['beat_days']==21))
# source-accurate ledger csv for 125ms full + timestamps / per-trade. No 9m tick copy.
chosen=R/'trades_cap256_hold1.0_interval125.npz'
if chosen.exists():
 z=np.load(chosen); ledger=R/'GRID0272_JAN_125MS_COMPLETE_SOURCE_SIDE_SETTLEMENTS.csv.gz'
 import gzip
 with gzip.open(ledger,'wt',newline='') as f:
  w=csv.writer(f);w.writerow(['entry_original_row','exit_original_row','entry_ms_utc','exit_ms_utc','entry_price_raw','side','net_cash_after_cost','hold_seconds','original_source_family'])
  columns=[z[name] for name in ['entry_idx','exit_idx','entry_ms','exit_ms','entry_price_raw','direction','net_cash','hold_seconds','source']]
  for row in zip(*columns):w.writerow([int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5]),round(float(row[6]),6),float(row[7]),str(row[8])])
 j=[x for x in candidates if x.get('coverage_interval_ms')==125 and x.get('params',{}).get('wd_cap')==256]
 assert j and abs(float(sum(z['net_cash']))-j[0]['net'])<1e-7 and len(z['net_cash'])==j[0]['trades']
 report_ledger=ledger.name
else:report_ledger='NOT_SAVED'
lines=['# GRID0272 JANUARY — ORIGINAL-SOURCE COMBINATION BREAKTHROUGH (RESEARCH-ONLY)',
'**Not a handoff summary substituting for original code.** This is an index to the full attached original helper bytes, complete replay scripts, full actual January tick-time trade ledgers and immutable experiment results. The controlling complete owner roadmap and January read-first anti-summary law remain unchanged.',
'', '**IMPORTANT — FULL MONTH NET TARGET MET IN MULTIPLE SOURCE-COMBINED RAW-TICK RESEARCH REPLAYS.** This is *not* complete monthly/daily/weekly/survivability/OVERFIT QC, FourSessionV1 integration or Coinexx readiness.',
'',f"**Target immutable R9 SYNTH January**: net +${r9['month']['net']:,.2f}; {r9['month']['trades']:,} completed; 21 trading days; 5 ISO weeks; source SHA `{r9['source_sha256']}`.",
 f'**Original Dukascopy Jan raw ordered ask/bid file SHA** `{ref}`; 9,135,062 ticks, unmodified, all original .gz bytes excluded from compact archive.',
 f"**Exact original normalized-spread Watchdog 131A reproduced** +${repro['net']:,.2f}, {repro['trades']:,} tickets, ${repro['equity_dd']:,.2f} full floating DD, max {repro['maxopen_exact']} open. Not a raw-quote claim.",
 '', '## Full-month causal-combination research results (USD for hypothetical 0.01 lot, $100k start)',
 'Source source: exact 131A parent/scout/HTF/paid previous-win Watchdog admission; original 131D as-of coverage, cold start, four session-cell candidate mechanisms. Resimulated on original raw Dukascopy Bid/Ask; 250ms first subsequent quote (2s order expiry), $0.20 round-trip trade cost, explicitly capped per specialist, globally merged and settled. No calendar date in signal. Trials also include alternative caps, dwell time, and heartbeat interval.',
 '', '| Variant | Net | Trades | PF | Gross loss | Tick-equity DD | Days positive | Days >=SYNTH | Weeks >=SYNTH | W01 USD |',
 '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for j in sorted(candidates,key=lambda x:(x['equity_dd'],-x['net'])):
 lines.append(f"| `{j['filename'].replace('original_composite_raw_250ms_fee20_','')}` | ${j['net']:,.2f} | {j['trades']:,} | {j['pf']:.3f} | ${j['gross_loss']:,.2f} | ${j['equity_dd']:,.2f} | {j['positive_days']}/21 | {j['beat_days']}/21 | {j['beat_weeks']}/5 | ${j['weekly']['2026-W01']['net']:,.2f} |")
lines+=['','## Exact transaction evidence and daily/weekly QC',
 f'- Complete per-fill price, source group, order index, quote timestamp and net P&L: `{report_ledger}` and `trades_cap256_hold1.0_interval125.npz`; each entry equals the actual bid/ask on that timestamp, exit P&L matches opposite quote and $0.20 cost **exactly**.',
 '- ALL exact candidate JSON files contain full 21-date daily and 5-ISO-week net/gross-loss/trade-count scoreboards. R9 SYNTH immutable day/week month comparator attached as `ORIGINAL/r9_synth_jan_daily_weekly.json`.',
 '- The 125ms interval means entry signal heartbeat frequency; entry fill delay stays 250ms. Original original interval is 250ms, faster intervals are *research hypotheses* not original source.',
 '- Original WD child latency0/$0.02 fee control matches same-surface normalized and raw results, and 250ms/$0.20 results are rederived on quotes. No oracle entry/exit model promoted.',
 '', '## Unresolved blockers before month QC or Python engine merge',
 '- Source parent/funded-surge event generation inherited original historical profit/cap accounting; though Watchdog child fills and future parent unlocks are recomputed after modeled 250ms/cost, **upstream parent funding/admission** is not yet recalibrated end-to-end to the new execution assumptions. Fail closed for production.',
 '- Only 4/5 January ISO weeks beat corresponding R9 SYNTH in best risk-cap research frontiers; W01 still below R9 SYNTH $1,027.95, and 1 January session day remains negative. Daily+weekly 100% target still fails.',
 '- R9 OVERFIT teacher matching and independent per-trade 75% scoring NOT done; cannot treat high win rate as substitute.',
 '- Floating drawdown remains material (about $22.8k in conservative cap256 research) and small starting account fundability not tested; no claim of deployability.',
 '- Full integrated current FourSessionV1 still negative until source-accurate admission/funding/portfolio controls are transplanted and given replays. Original historical normalized-spread research is NOT proof of raw broker equivalence.',
 '- All January-tuned alternatives require forward February (and subsequent month) month-blind nonregression before promotion; month/day/week not execution features.',
 '', '## User governing protections',
 '- Original source bytes preserved without edits and inventoried with hashes. Frozen owner V1 whitepaper, verbatim January–July roadmap and original governing conversation govern implementation; this report is source-index only.',
 '- Official J0183 not moved, existing accepted controls not erased, trading OFF, August SEALED, no MQL5/MT5 report audit.',
 '', '## Repro instructions',
 '1. From the month `ORIGINAL/` folder in this archive (exact bytes), set `PYTHONPATH` to that folder. Retain `/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` and its SHA256.',
 '2. Execute normalized unchanged original 131A: `python ORIGINAL/gamma02_jan_watchdog119_grid_layer_refinement_131a.py --out normalized.json --case working` (historical normalized quotes; control only).',
 '3. Test raw child timing/cost: `python original_latency.py 250 .20 1190,1190,1190,1190,1190,1100 703`.',
 '4. Test combined actual raw quote sources: `python combine_original_latency.py 1190,1190,1190,1190,1190,1100 256` with `GRID0272_COVERAGE_INTERVAL_MS=125` or `250`; original quote dates are evaluation, not features.',
 '5. Read all `original_composite_raw*.json` and trade NPZ/CSV.GZ, compare to original `r9_synth_jan_daily_weekly.json`; no acceptance if one metric misses.',
 '', '### Community reconstruction references (inspiration, not proven results)',
 '- MQL5 regime-adaptive CUSUM/grid cycle: https://www.mql5.com/en/articles/21833',
 '- MQL5 ADX EMA pullback ATR: https://www.mql5.com/en/code/73958',
 '- Chinese original dynamic gold grid/triple range filter: https://www.fmz.com/strategy/530403',
 '- Reddit community regime filter experience: https://www.reddit.com/r/algotrading/comments/1shgpyf/',
 '', '## Disposition',
 '**January RESEARCH CANDIDATE NET TARGET REACHED, NOT MONTH QC PASSED.** Continue prioritizing parent funding parity, risk heat, R9 daily/weekly gaps, then as-of OVERFIT scoring and 7-month cumulative cross-regime replay. No production file touched.']
(R/'GRID0272_JAN_ORIGINAL_SOURCE_COMBINATIONS_FULL_RESEARCH_REPORT.md').write_text('\n'.join(lines)+'\n')
# Exact data bytes archive; no raw January tick duplication
included=[]
for p in [*source_files,source/'r9_synth_jan_daily_weekly.json',R/'combo_research.py',R/'combo_results.json',R/'original_latency.py',R/'reprice_131a_raw.py',R/'original_lean_raw.py',R/'combine_original_latency.py',R/'original_131a_working.json',R/'reprice_131a_raw_result.json',R/'original_lean_raw_result.json',R/'EXACT_SOURCE_QA_MANIFEST.json',scorefile,R/'GRID0272_JAN_ORIGINAL_SOURCE_COMBINATIONS_FULL_RESEARCH_REPORT.md']:
 if p.exists():included.append(p)
included+=sorted(R.glob('delayed_*.json'))
included+=sorted(R.glob('original_composite_raw_*.json'))
included+=sorted(R.glob('trades_cap256*.npz'))
for n in ['GRID0272_JAN_125MS_COMPLETE_SOURCE_SIDE_SETTLEMENTS.csv.gz','original_131a_working.log','latency250_fee20.log','composite.log']:
 p=R/n
 if p.exists():included.append(p)
pack=R/'GRID0272_JAN_SOURCE_EXACT_POSITIVE_COMBINATION_RESEARCH_UNPROMOTED_20261013.zip'
with zipfile.ZipFile(pack,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in sorted(set(included)):z.write(p,p.relative_to(R))
print(json.dumps({'zip_path':str(pack),'zip_size':pack.stat().st_size,'zip_sha256':sha(pack),'included':len(included),'candidate_count':len(candidates),'monthly_success_variants':sum(x['net']>=41520.82 for x in candidates),'report':str(R/'GRID0272_JAN_ORIGINAL_SOURCE_COMBINATIONS_FULL_RESEARCH_REPORT.md')},indent=2))
