#!/usr/bin/env python3
"""Preservation-first, lossless 8 archive + global recovery 2026-11-03 R22."""
from __future__ import annotations
import csv,hashlib,json,zipfile,os,datetime as dt
from collections import defaultdict
from pathlib import Path
ROOT=Path('/mnt/data');LAB=ROOT/'h1v2_r22_nine_residual';RESULTS=LAB/'results_v2';EXT=LAB/'cycle2/results_v2';ARCH=LAB/'archives';ARCH.mkdir(exist_ok=True)
SOURCES=('DUKASCOPY_RAW','MT5_BROKER_EXPORT');MONTHS=('01','02','06','07')

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def read(p):return list(csv.DictReader(open(p,newline='')))

def zip_files(out,named):
 with zipfile.ZipFile(out,'w',allowZip64=True) as z:
  for name,path in named:
   path=Path(path)
   mode=zipfile.ZIP_STORED if path.suffix in ('.npz','.zip','.gz') else zipfile.ZIP_DEFLATED
   z.write(path,arcname=name,compress_type=mode,compresslevel=6 if mode==zipfile.ZIP_DEFLATED else None)
 with zipfile.ZipFile(out) as z:
  if z.testzip() is not None:raise RuntimeError('BROKEN_ZIP '+str(out))
  if len(z.namelist())!=len(named) or len(set(z.namelist()))!=len(named):raise RuntimeError('ZIP_MEMBER_COUNT_OR_DUP')
 return {'bytes':out.stat().st_size,'sha256':sha(out),'source_members':len(named),'members':{n:{'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in named}}

raws=json.loads((LAB/'R22_EIGHT_RAW_SHA_VERIFICATION.json').read_text());assert len(raws)==8 and all(x['PASS'] for x in raws)
ver=json.loads((LAB/'R22V2_INDEPENDENT_8_SOURCE_FULL_CALENDAR_AND_SHA_VERIFICATION.json').read_text());assert ver['failed']==0 and ver['passed']==616
out=[];pins={}
for src in SOURCES:
 for mon in MONTHS:
  filehead=f'R22V2_{src}_{mon}'
  named=[]
  for p in sorted(RESULTS.glob(filehead+'_*')):named.append(('R22_V2_'+src+'_'+mon+'/source_output/'+p.name,p))
  if src=='DUKASCOPY_RAW':
   for p in sorted(EXT.glob(filehead+'_*')):named.append(('R22_EXPLORATORY_NOT_OOS/'+p.name,p))
  old=ROOT/'h1v2_r21_dualbroker/results'/f'R21E_{src}_{mon}_SCENARIOS.csv'
  named.append(('ORIGINAL_R21_REFERENCE/'+old.name,old))
  pdf=ROOT/'h1v2_r19_broker_union/results_defect_diagnostics'/f'R19_{src}_{mon}_ALL_ORIGINAL_UTC_QUARTER_RAW_SPREAD_GAPS_AND_DEFICITS.csv'
  if pdf.exists():named.append(('IMMUTABLE_R19_DEFECT_SOURCE/'+pdf.name,pdf))
  archive=ARCH/f'R22V2_{src}_{mon}_COMPLETE_FULL_UTC_CALENDARS_BIDASK_NEGATIVE_ORDINALS_20261103.zip'
  rr=zip_files(archive,named)
  pins[archive.name]=rr;out.append({'source':src,'month':mon,'archive_name':archive.name,'archive_sha256':rr['sha256'],'bytes':rr['bytes']})
manifest={'research':'H1V2 R22 V2 source-exact corrections and experimental first-passage capacity',
 'classification':'LOSSLESS_RESEARCH_ARCHIVE_UNAPPROVED_FUTURE_INFORMED_HINDSIGHT_ONLY',
 'raw_source_exact_hashes':raws,'R22V2_independent_output_reconciliations':{'passed':616,'failed':0},
 'source_month_results':out,'archives':pins}
mp=LAB/'R22V2_ALL_EIGHT_COMPLETE_ARCHIVE_AND_MEMBER_SHA256_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')

# Build the UNABRIDGED scientific commentary; exact entire CSVs/NPZ reside in source ZIPs.
lines=['# R22 — H1V2 EIGHT-SOURCE FOUR-MONTH MULTI-REGIME DUAL-BROKER HINDSIGHT RESEARCH',
'','## NO SCIENTIFIC SHORTCUTS / INTERPRETATION CONTRACT',
'Every original quote sequence, UTC quarter/hour/day/month reference, original R21 baseline and original R9 EA/source remains immutable. R22 is an add-only counterfactual. The winning side and historical schedule are selected AFTER inspecting full future paths, so their resulting 100% correct selected-win rate is **not** a prediction or tradable win rate. Coinexx-linked MT5 quote exports are not verified broker live fills, and Dukascopy quotes are not a Dukascopy trading account. No causal BUY/SELL/WAIT student, positive net account PnL, portfolio risk, unseen out-of-sample or real dealer latency has been certified.',
'','## SOURCE AND EXACT UPSTREAM PINS',
'R22 isolated GitHub branch: carson/h1v2-r22-nine-residual-broker-geometry-20261103, parent carson/h1v2-r21-broker-event-readiness-20261103; original repaired R9 v2 SHA ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0. Original H1V2 source, all R11–R21 branches and MT5 production code untouched.',
'R22 progress Google Doc: https://docs.google.com/document/d/1iE5C0vdJhiwSlDxDpm6tXVfGyVLQwrw7jXAm-R2WjS8/edit ; R22 MT5_EXPAND folder https://drive.google.com/drive/folders/1QmPi5jf2Dp7t9o8uqH9k_VbuC9WweYj8',
'R9 SYNTH exact UTC-aligned reference per separate feed month Jan 27980, Feb 33523, June 31758, July 24324, total 117585. Original R21 30s/8 observed source-lane first-touch +0.10 net after nominal 0.02 price units, initial liquidation adverse -0.10, first quote at +100ms, entry/fill spread <=4.00, future first target<=60s. This is *different* from R11 strict first15/safe30 and original R9 trail/stop/timeout. Experimental R22 changes source epoch and horizon (0–240sec); no approval of any original v5 runtime change.',
'','## FULL RAW SOURCE SHA-256 READBACK — EIGHT DISTINCT FILES']
for a in raws:lines.append(f"{a['source']} 2026-{a['month']} | {a['file']} | bytes={a['size_bytes']} | SHA256={a['sha256']} | pinned_equal={a['PASS']}")
lines+=['','## EXACT EIGHT-SOURCE SOURCE-MONTH R22 V2 12-CASE OUTCOMES — ALL 96 RECORDS, NOTHING SELECTED FOR POSITIVITY']
for s in SOURCES:
 for m in MONTHS:
  f=RESULTS/f'R22V2_{s}_{m}_ALL_SCENARIOS.csv';lines.append('');lines.append(f'### {s} 2026-{m}, all 12 experimental controls')
  lines.extend(f.read_text().splitlines())
lines+=['','## EXACT FOUR-MONTH DUKASCOPY EXTRA 8-CASE HORIZON/STRESS EXPLORATION — ALL 32 RECORDS, NOT BLIND OOS']
for m in MONTHS:
 f=EXT/f'R22V2_DUKASCOPY_RAW_{m}_ALL_SCENARIOS.csv';lines+=['',f'### DUKASCOPY_RAW {m} 8 additional exploratory cases'];lines.extend(f.read_text().splitlines())
lines+=['','## ALL NINE ORIGINAL R21 FAILING QUARTERS — EVERY VERSIONED EXPERIMENT OUTCOME AND RAW R19 SOURCE GEOMETRY']
for m in MONTHS:
 qdf=read(RESULTS/f'R22V2_DUKASCOPY_RAW_{m}_ALL_UTC_QUARTERS.csv')
 bads=[x['utc_quarter'] for x in qdf if x['scenario'].startswith('C00') and x['deficit']!='0' and int(x['R9_SYNTH_reference'])>0]
 geo={x['original_UTC_quarter']:x for x in read(ROOT/'h1v2_r19_broker_union/results_defect_diagnostics'/f'R19_DUKASCOPY_RAW_{m}_ALL_ORIGINAL_UTC_QUARTER_RAW_SPREAD_GAPS_AND_DEFICITS.csv')}
 for stamp in bads:
  lines.append('');lines.append('### '+stamp+' — unchanged aligned R9 SYNTH reference '+str(next(x['R9_SYNTH_reference'] for x in qdf if x['utc_quarter']==stamp)))
  r=geo.get(stamp)
  if r:lines.append('Original R19 complete raw geometry record: '+json.dumps(r,sort_keys=True))
  lines.append('Full R22V2 12 research scenario selection counts, including failures:')
  for x in qdf:
   if x['utc_quarter']==stamp: lines.append(json.dumps(x,sort_keys=True))
  extrows=read(EXT/f'R22V2_DUKASCOPY_RAW_{m}_ALL_UTC_QUARTERS.csv')
  lines.append('Full cycle2 8 research scenario selection counts:')
  for x in extrows:
   if x['utc_quarter']==stamp:lines.append(json.dumps(x,sort_keys=True))
lines+=['','## SCIENTIFIC FAILURE LOG AND CORRECTION',
'Initial R22 version V1 fast-reopen gate mistakenly allowed trailing-30s quote count to include pre-gap quotes when readiness age<30s. No original R21 30s threshold needed this fix. Entire V1 quarantined results_v1_archived and specifically NOT accepted. Corrected V2 uses max(past30_tick_start, latest_GT15S_quote_gap_anchor), requiring 8 actual *postgap* quote observations. A separate initial test fixture incorrectly expected a >1s stale fill to be valid; fixture corrected and failed test preserved. Eight adversarial tests now pass, zero failed. R22 V2 full-source archived row verifier 616/616 checks passed. These checks use source SHA-verified original quote files read by original R18 verified loader and independently reconcile outputs; the independent output verifier itself does not rerun all raw tick first-passage labels from scratch. Original R11–R21 sources unchanged.',
'','## DEEP GEOMETRY/OBJECTIVE FINDINGS (NO OVERGENERALIZATION)',
'Under V2 C00 original R21 60sec: Dukas all-quarter volume 7512/7521, all active hours 1917/1917; Coinexx-linked MT5 export 7521/7521, all active hours 1917/1917. V2 C08 observed 8 postgap quotes, aftergap age0sec, cap4, actual100ms fill, +10c net first touch within 120sec before -10c adverse => Dukas 7516/7521, Coinexx linked remains 7521/7521, all hours3834/3834 across both source calendars. V2 C10 cap8 90sec => Dukas 7517/7521 with significantly larger spread and acquisition risk; unapproved diagnostic only. Horizon extension beyond 120sec provides more future TP candidate rows but zero additional active quarter coverage in observed four-month source. The pre-entry gap readiness relaxation is also a DISTINCT experimental break from original v5 required 300s of fresh history, and cannot be silently merged into repaired R9 runtime.',
'Future-known winner scheduling means selected GOOD count by design has 100% success. In V2 C08 targeted original-failure Dukas quarters, only 982 two-sided favorable observations versus 9,707 two-sided stopped outcomes; this is not a whole-calendar win probability but a warning that as-of side selection is the major unresolved hurdle. R22 extended exploratory full labels preserve STOP/TIMEOUT/CENSORED; zero-reference clock buckets are retained in CSVs, no synthetic entry allowed on no-quote periods.',
'','## 6 ADVANCED FALSIFIABLE MECHANISM FAMILIES — NEXT EXPERIMENTS, NOT CLAIMS',
'QH-22A: Broker-normalized actual affordable spread strain using observed realized directional range over completed 3/15/60/300s and completed 15m/1h/4h; reject when target spread+fee+slip is improbable, never rely on spread widened hard cap alone. Fit source-specific probability of first TP BEFORE stop and quote dropout, not quote movement correlation.',
'QH-22B: Multiscale marked quote process with bid and ask leadership, spread-compression shock and joint motion mixed marks, 0.25/1/3/15/60sec event-time states; Hawkes exponential kernel intensities must validate strictly on subsequently observed events, and no future side/teacher membership in features.',
'QH-22C: Hybrid competing-risks temporal transformer/point-process + time-to-event hazard for BUY/SELL/WAIT, with 4-way competing firstTP/adverse/timeout/censor under source and actual lag; utility includes one-position opportunity cost and option value of waiting. Fit earliest strict executed win rate, not future oracle membership or hindsight selected PnL.',
'QH-22D: As-of Bayesian broker-specific spread transition model: posterior probability of observed future spread compression under session/regime state, confirmation wait up to 60s before ENTRY (not extending post-entry occupancy), opportunity budget, quote age and no filled quote before it is seen. Right-censor outages and source gaps; explicit weekend/open shocks.',
'QH-22E: Dual-broker hierarchical expert router with broker identity, spread-to-move normalized geometry, volatility-of-volatility, quote arrival and flow imbalance, posterior regimes gated by reproducible source time. Train per broker and pooled with random effects; never mix broker quote streams as if simultaneously fillable on same account; report calibrated transfer under leave-one-month-and-source-out.',
'QH-22F: Calibrated bandit/portfolio constrained execution with original R9 dynamic hard stop/trail/30s timer as frozen control, action-specific TP/STOP/latency, spread fee real 0.01lot USD cash model, margin, daily max loss, equity and compounded exposure. Reject all actions without positive executable expected net. Test blinded later dates and forward MT5 before any deployment.',
'','## EXACT STATISTICAL FIREBREAK AND SCIENTIFIC STOP',
'All mechanism hyperparameters and the tested Jan/Feb/Jun/Jul dates are exposed; later-date blind OOS is required. We do not infer cash PnL from raw 0.001 price quotes or +0.10 nominal price outcome. Do not force quotas by overriding adverse risk or inferring a future price path. If all future-known historical winners cannot cover an original R9 SYNTH quarter under consistent source and safety geometry, that quarter is impossible for that particular contract; record the deficit honestly. Completed R22 hypotheses are capacity tests only; no live EA build/approval.',
'','## LOSSLESS INDEX OF BINARY/CALENDARS AND RESUME',
'All eight ZIP files preserve every R22 source-month CSV for ALL original UTC quarters, hours and days for every R22 V2 case, full both-side ordinal outcome arrays for GOOD/STOP/TIMEOUT/CENSORED and complete first-touch exit ordinal source prices, per-file SHA receipts and R21 original baseline comparator, plus separate exploratory 8-case results for each Dukascopy month. The complete raw eight gzip files are original pinned upstream dependencies, not recopied into each 20MB archive; preserve their hashes. The global ninth ZIP has the full source, eight tests, failure log, rebuild+verify scripts, full eight-month receipts and original local manifests. Resume from the most recent R22 ledger, not this text alone.','']
report=LAB/'R22V2_COMPLETE_UNABRIDGED_EIGHT_SOURCE_H1V2_RESEARCH_AND_FAILED_CASES_20261103.md';report.write_text('\n'.join(lines)+'\n')

# Global archive with full executable source/checkpoint. Do not package the bad V1
# results as approved. Preserve F01/F02 evidence in the human ledger.
core=[]
for name in ('r22_source_exact_rescue_v2.py','r22_posthoc_extension_cycle.py','verify_r22_complete_archived_outputs.py',
             'build_r22_full_delivery.py','R22_EIGHT_RAW_SHA_VERIFICATION.json',
             'R22V2_INDEPENDENT_8_SOURCE_FULL_CALENDAR_AND_SHA_VERIFICATION.json',
             'R22V2_ALL_96_MONTH_SOURCE_SCENARIOS_AND_DAY_OUTCOMES.csv',
             'R22_FAILURES_AND_CORRECTIONS_APPEND_ONLY.log',
             'R22_APPEND_ONLY_PROGRESS_LEDGER_20261103.txt',
             'R22V2_COMPLETE_UNABRIDGED_EIGHT_SOURCE_H1V2_RESEARCH_AND_FAILED_CASES_20261103.md',
             'R22V2_ALL_EIGHT_COMPLETE_ARCHIVE_AND_MEMBER_SHA256_MANIFEST.json'):
 path=LAB/name
 if path.exists():core.append((name,path))
for p in sorted((LAB/'tests').glob('*.py')):core.append(('tests/'+p.name,p))
for p in sorted(LAB.glob('R22V2_*_EXECUTION.log')):core.append(('logs/'+p.name,p))
for p in sorted((LAB/'cycle2').glob('*EXPERIMENT.log')):core.append(('logs/cycle2/'+p.name,p))
arch=ARCH/'R22V2_GLOBAL_COMPLETE_SOURCE_TESTS_SCIENCE_AND_8_SOURCE_SHA_MANIFEST_20261103.zip'
glob=zip_files(arch,core)
(ARCH/'R22V2_GLOBAL_ARCHIVE_SHA_RECEIPT.json').write_text(json.dumps({'archive':arch.name,**glob},indent=2)+'\n')
print(json.dumps({'eight_month_archives':len(out),'global_core_members':len(core),'report_chars':len(report.read_text()),'eight_zips':[(x['archive_name'],x['bytes']) for x in out],'global_zip':arch.name,'global_size':arch.stat().st_size},indent=2))
