"""Build complete source-exact R23 delivery; never overwrite prior R11-R22."""
from __future__ import annotations
import csv,hashlib,json,zipfile,os
from datetime import datetime,timezone
from pathlib import Path
import pandas as pd
ROOT=Path('/mnt/data/h1v2_r23_dualbroker'); DATA=ROOT/'results';MN=['01','02','06','07']
SRC=['DUKASCOPY_RAW','MT5_BROKER_EXPORT']
GH='https://github.com/AnhTranHarris/gold-MUWHAHA-miner/tree/carson/h1v2-r23-dualbroker-geometry-causal-falsification-20261103'
R23_DRIVE='https://drive.google.com/drive/folders/179ImG0v_5Klp9aEr-pl-7gNFXkEOPebQ'


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()


def q(x):return str(x).replace('\\','/')


def explain():
 return '''
# COMPLETE, UNSHORTENED, LOSSLESS SCIENCE CLASSIFICATION AND SOURCE EXACT CONTRACT

This R23 report is an additional append-only experimental record to R11–R22.
It does not replace or summarize the original governor, original H1V2 teacher,
original hourly forensic volume B, original 246 impossibility witnesses, R21 or
R22 source ledgers; links below point to those independently archived items.
ALL 96 monthly source experiment records and ALL 90 UTC matched-quarter experiment
records are printed verbatim in this document. ALL 276,480 per-source-month×policy
quarter rows, 69,120 hourly rows, 2,880 full UTC day rows, exact quote ordinals
for both BUY/SELL GOOD/STOP/TIMEOUT/CENSORED and first observed quote exits,
are preserved untruncated in the ZIP evidence members with member SHA256. Users
must never substitute this prose for the full machine data.

## FROZEN SOURCE BASELINE
R9 SYNTH historical UTC counts: Jan 27,980, Feb 33,523, June 31,758,
July 24,324; TOTAL 117,585 per independent matched source. Calendar has
2,880 UTC hours, 11,520 original UTC quarter bins, 120 UTC days, 1,917 R9
SYNTH-active hours, 7,521 R9 SYNTH-active quarter bins and 102 active UTC days.
The observed quote files: original 4 Dukascopy CSV.gz and 4 Coinexx-linked
MT5_BROKER_EXPORT CSV.gz, exact original R18 SHA256 pins, NOT interchangeable
with MT5 SYNTH tester raw tick paths and NOT verified dealer fills.
All observed raw quote timestamp ordinals preserve same-ms chronology; no
intrasecond OHLC interpolation, no synthetic source quote after >15s drought.
The original H1V2 strict first15+full30 zero-adverse/safety remains untouched;
the original R9 repaired v5 300-second fresh quote warmup remains untouched.

Original R21 historical experimental EVENT30_8_QUOTES_CAP4000 entry age>=30s
since >15s source gap AND at least 8 actually observed quote ordinals in past
30s; at source quote i, BUY enters at first later observed ASK at/after +100ms
(or SELL at BID), with cap4 at both signal & fill and no more than 1-second
quote response staleness; future first net +$0.10 after $0.02 price-unit fee
before opening liquidation quote adverse -$0.10, within 60s. Upon actual
first favorable/stop/timeout, occupancy until the observed quote exit. R21
future-informed selector combines these intervals with source-frozen predecessor
positions. Exact quarter/day/hour calendar inherited, never divided by four.
R21 source Dukas Q7512/7521 and MT5 Q7521/7521; H1917/1917 both.

Corrected R22 V2 H90/CAP8/postgap0/8quotes original experimental C10
historical Dukas Q7517/7521 and MT5 Q7521/7521; source consistency via
R22 all eight source-month archives. This CAP8 is NOT approved as a risk rule,
and R22 V1 pre-gap quote-count contaminant is quarantined. Four remaining
R22 C10 source-quarter issues: Feb06 21:45, Feb12 23:00, Jul12 23:00,
Jul17 20:45 UTC. R23 tests start from this frozen C10 schedule, preserve every
other 15m slot and use the mathematically correct globally nonoverlap interval
exchange helper R21, with source future-known BUY/SELL and exit ONLY for offline
capacity upper—not a tradable policy.

## ROUND H01 — SOURCE EXACT RESIDUAL ROOT CAUSES
The nine original R21 failed quarters are rejoined byte-for-byte to BOTH
broker domains using only the observed UTC quote event timestamps. Each
source-quarter has true n raw quote observations, distinct-ms quote count,
first/last quote latency to boundary, raw bid/ask spread p10,p50,p90, raw
quoted spread above $4 and $8, >15s source quote drought counts, actual
100ms and 500ms later first available fill quote, measured two-sided STOP,
TP,TIMEOUT,CENSORED, and a strictly isolated one-position future-known upper.
For none of the nine is R9 reference reconstructed from an hourly split.

## ROUND H02 — TWELVE DISTINCT BROKER GEOMETRY / RISK EXPERIMENTS
All H02 original source files have both-side quote outcomes and exact path exit
ordinal for each candidate first actual delayed fill. Reference original
+$0.10 net after nominal $0.02 price fee is separate from new +$0.025,
+$0.05,+$0.075,+$0.20 alternative target classes. Stop -$0.10 vs -$0.15
is from original opening liquidation BID for BUY, ASK for SELL, NOT a stop
that magically refunds the opening bid/ask spread. Stop is examined before
TP on the same first quote. New first-target horizons 60s/90s/120s and extra
slippage on each side are independent versioned mechanisms. All trades label
0 actual first-stop, 1 first-success, 2 actual first quote after timeout, -3
right-censored/drought. An actual gap greater than 15s is never a completed
profitable trade, and missing end-of-source quote never becomes loss=0.

For a fixed signal source quote i and 100ms latency, the actual delayed entry
quote f is FIRST j with time[j]>=time[i]+100ms and quote availability
lateness<=1000ms, and fill spread<=cap. BUY net quote-price at exit k is
Bid[k]-Ask[f]-nominal_fee-2*per_leg_slippage. SELL net quote-price is
Bid[f]-Ask[k]-nominal_fee-2*per_leg_slippage. Both stop at an opening
liquidation price deterioration of 0.10 or the changed stop tested, not
at entry price. Further account cash translation, broker lot contract,
commission/margin, R9's +0.10 gross trailing activation/$0.03 trail/$0.30
hard stop/30s timeout are NOT included; no approximate price net may be
reported as Coinexx 0.01-lot USD realized PnL.

## ROUND H03 — TRUE AS-OF NEGATIVE CONTROL, NOT HINDSIGHT
For every new quote candidate in failing source quarters, R23 computes
past-only Bid/Ask simultaneous 3s,15s,60s signed movement, 15s/300s rolling
spread means, and current spread exactly at source SIGNAL ordinal before
100ms or 500ms broker-fill replay. The deterministic PAST3S_SIGN rule is
BUY if both Bid/Ask rose since a past observed quote, SELL if both fell,
WAIT if mixed or history absent. An additional source-quote spread-relief
rule requires current observed spread <=0.8×trailing 300s average and
movement >=max(0.025,0.2×observed spread) in raw quote dollars. All
predicted actions, including bad and timeout, scored against the EXACT
actual fill quote with STOP prioritized. Neither future chosen oracle
side nor successful interval membership is a feature. This local negative
control is NOT a trained whole-calendar classifier or statistically blind
OOS. It exposes that naive momentum + spread gates cannot turn 99.96%
retrospective capacity into 80% reliable realized correct entry actions.

## ROUND H04 — MATCHED BROKER GEOMETRY / SOURCE FRICTION
For each of original 9 R21 hard source quarters, R23 independently tests
5 economic first-passage contracts on BOTH 2026 Dukascopy and Coinexx-linked
MT5 sources, using exactly equal UTC intervals and R9 source reference.
The independent 15-minute optimistic cardinality resets occupancy at its
boundary and is therefore an UPPER for that finite candidate/label geometry,
not a feasible globally scheduled portfolio or a universal market bound.
The H02 global schedule separately preserves all predecessor positions,
including cross-15-minute and cross-hour outside reservations. Never equate
isolated 15-minute candidate count to a real policy hourly result.

## ECONOMIC GEOMETRY: WHY 80% CORRECTNESS IS NOT ENOUGH BY ITSELF
Let s be the opening actual ASK-BID spread in quoted XAUUSD price units,
A=0.10 original adverse liquidation threshold and f=0.02 nominal fee,
w=0.10 minimum winning net. A stop at EXACT first adverse barrier crossing
has quote-price net LOSS approximately -(s+A+f), before adverse overshoot
and extra entry/exit slippage. A marginal winning TP earns >=w, not a
source-guaranteed larger amount. Necessary break-even for exactly w wins
and (s+A+f) loses is p > (s+A+f)/(s+A+f+w). Actual overshoot worsens it.
For median Dukascopy Feb12 23:00 s=$1.837, required p>95.14% for minimum
$0.10 winners; for matched Coinexx s=$0.190, required p>75.61% under the
same barriers. Changing minimum winner to $0.025 makes Dukascopy
break-even near 98.74%, not easier. It is invalid to approve a strategy
solely because historical oracle wins reached more 15min quotas.

## FIVE NEXT-PHASE HIGH-DIMENSIONAL EXPERIMENT FAMILIES (NOT TESTED/NOT RESULTS)
EX-R23-1 Broker-normalized spread strain: spread / strictly past-observed
conservative directional realized-range quantile over 15/60/300s,
including right-censor/quote-arrival rate and spread compression hazard.
Separate MT5 and Dukascopy posterior calibration; a $4 gate is not a
spread neutralization. Model cost at actual entry and first actual exit.
EX-R23-2 Hybrid marked bid-ask cross-excited point-process 250ms/3/15/60s,
with mixed up/down quote marks, Hawkes self/cross excitation and spread
widen/narrow events, plus completed 15m/H1/H4 structural regime state.
Require proper likelihood and heldout first-passage utility, not mere
quote arrival likelihood. No retroactive last-quote or same-ms peeking.
EX-R23-3 Multi-cause semi-Markov competing hazard BUY, SELL, WAIT model.
At decision t fit conditional P(first +$net barrier before adverse stop,
source gap or timeout | observed prefix, broker, bidask state), an occupancy
hazard and the distribution of actual bid/ask quote exit net. Each cause
right-censored separately; do not turn TIMEOUT+BAD+CENSORED into NONE.
EX-R23-4 Broker-aware two-timescale WATCH60 (PRE-ENTRY only) / EXECUTE
state with quote-ordinal time value. A Duchascopy candidate may spend up to
60s observing actual spread contraction and market-state stabilization
before it can be paid at the NEXT actual quote, not at a previous quote;
post-entry 60/90/120s position risk and opportunity cost are distinct.
Coinexx narrow-spread specialist may use shorter horizons with calibrated
hazard and lower expected holding time. A single broker policy isn't
assumed to transfer. No extra trade count may come from a fictitious
unobserved quote, a negative expected payoff, or an undocumented longer
stop. Prior R15 WATCH60 and R16 directional regimes remain negative controls.
EX-R23-5 Hierarchical broker×session×regime mixture-of-experts with pooled
regularization but broker-specific output heads, Bayesian updating of
spread-flow and post-gap state, and a constrained renewal-reward WAIT gate:
Q(action) = expected observed executable net - lambda*tail_CVaR -
rho*occupancy_time - value_of_waiting - switching_cost. Risk budget is
account-dollar after independently verified lot value, margin, dealer
cost and bidask commissions. Train on disjoint time blocks with horizon
embargo and frozen validation, measure all 15m/hour/day/month joint 80%
correctness, 85% monthly source reference, and portfolio expected net.
Do not call a high-capacity future-informed teacher a causal student.

## SOURCE-VALIDITY / STOP CONDITIONS
Already exposed Jan/Feb/Jun/Jul cannot become independent blind OOS from
new model selection. No R9 EA change or MT5 deployment has been authorized.
No H1V2 student has been trained and certified at the user joint 80%
correctness, >=85% aligned R9 SYNTH monthly volume, positive executable
broker-contracted cash PnL, risk and full time-bucket pass. Any claim of
100% historical future-known selected side accuracy is hindsight tautology.
Full failed campaigns from R11-R22 remain immutable, not discarded. Next
actual implementation gate is a new versioned as-of causal specialist with
frozen fit/calibration/test and full ACCOUNT cash fill replay, and source
matched Coinexx REAL/SYNTH trade detector calibration where available.

## IMMUTABLE ORIGINAL UPSTREAM SOURCE LINKS
Original five-volume deep H1V2 forensic re-audit folder:
https://drive.google.com/drive/folders/1ilumXIGt_xiadwsrYtIH5HDopYEw-gcn
R11 original hourly master forensic audit:
https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit
R11 original original unabridged ledger:
https://docs.google.com/document/d/1eGC-vxRDzu7FxQOY-3PPUfWzoVRrOZU5jaDozuuv0xI/edit
R12–R17 original unabridged progress ledger:
https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit
R21 original full source and 8 source month log:
https://docs.google.com/document/d/1XXZTvhPDIX1hWvQ1qbi1Y2zrw-z5RJ8Q4S42Tc9jc5Y/edit
R22 corrected full source, negative trials and preservation log:
https://docs.google.com/document/d/1iE5C0vdJhiwSlDxDpm6tXVfGyVLQwrw7jXAm-R2WjS8/edit
R23 append only Google Drive log:
https://docs.google.com/document/d/1S4q_U7_E7EgtRWcU31Ba7XDHU77pD4UVhMXFSIVFzsU/edit
R23 isolated source branch:
'''+GH+'\nR23 original archive folder:\n'+R23_DRIVE+'\n'


def run():
 cases=[];paired=[];receipts=[]
 for src in SRC:
  for m in MN:
   prefix=f'R23_{src}_{m}'
   cases.extend(pd.read_csv(DATA/(prefix+'_CASES.csv'),keep_default_na=False).to_dict('records'))
   receipts.append(json.loads((DATA/(prefix+'_FULL_SOURCE_EXACT_SHA_AND_SCIENCE_RECEIPT.json')).read_text()))
   if m!='01':paired.extend(pd.read_csv(DATA/f'R23_PAIRED_{src}_{m}_ALL_ORIGINAL_R21_DEFICIT_QUARTER_5_EXPERIMENTS.csv',keep_default_na=False).to_dict('records'))
 casesp=ROOT/'R23_ALL_96_COMPLETE_EIGHT_SOURCE_MONTH_SCENARIOS.csv';pairp=ROOT/'R23_ALL_90_ORIGINAL_R21_MATCHED_BROKER_SOURCE_ORDINAL_EXPERIMENTS.csv'
 for f,rows in [(casesp,cases),(pairp,paired)]:
  with f.open('w',newline='',encoding='utf8') as stream:
   w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 blocks=[]
 blocks.append('# R23 GOLD MUWHAHAHA MINER — COMPLETE NONDEPLOYABLE EIGHT SOURCE MONTH / FIVE CREATIVE HYPOTHESIS CYCLE EXPERIMENT RECORD\n\n')
 blocks.append('Date 2026-11-03 America/Chicago. SOURCE=Eight actual quote feeds; reference EXACT R9 SYNTH. No original H1V2/R9/R11-R22 mechanism or archive overwritten.\n')
 blocks.append(explain())
 blocks.append('\n## PROGRESS LEDGER EXACT RAW TEXT (INCLUDING FIRST FAILURE LOG)\n\n'+(ROOT/'R23_APPEND_ONLY_PROGRESS_LEDGER_20261103.txt').read_text()+'\n')
 blocks.append('\n## FAILURE AND CORRECTION LOG — VERBATIM\n\n'+(ROOT/'R23_FAILURES_AND_CORRECTIONS_APPEND_ONLY.log').read_text()+'\n')
 blocks.append('\n## ENTIRE 96 MONTH × SOURCE × SCENARIO RESULTS, CSV VERBATIM\n\n```csv\n'+casesp.read_text()+'\n```\n')
 blocks.append('\n## ENTIRE 90 MATCHED-BROKER EXACT UTC QUARTER × EXPERIMENT RESULTS, CSV VERBATIM\n\n```csv\n'+pairp.read_text()+'\n```\n')
 blocks.append('\n## EXACT 8 SOURCE MONTH REPRODUCTION / ALL PER-CASE SCIENCE RECEIPTS — ORIGINAL JSON VERBATIM\n')
 for src in SRC:
  for mon in MN:
   p=DATA/f'R23_{src}_{mon}_FULL_SOURCE_EXACT_SHA_AND_SCIENCE_RECEIPT.json'
   blocks.append('\n### '+p.name+'\n```json\n'+p.read_text()+'\n```\n')
 blocks.append('\n## INDEPENDENT SOURCE AND OUTPUT VERIFIER — COMPLETE 2088 CHECK RECEIPT JSON IN VERBATIM\n')
 verification=(ROOT/'R23_COMPLETE_EIGHT_SOURCE_INDEPENDENT_RECEIPT.json').read_text()
 blocks.append('```json\n'+verification+'\n```\n')
 report=ROOT/'R23_COMPLETE_UNABRIDGED_DUAL_BROKER_H1V2_MULTICYCLE_CAUSAL_FALSIFICATION_20261103.md'
 report.write_text(''.join(blocks),encoding='utf8')
 # Source manifest, raw source read before it is claimed verified. Verify script
 # already recomputed all original 8 SHA against authoritatively pinned R18.
 raw=json.loads(verification)['exact_archived_raw_sha256']
 manifest={'label':'R23_addonly_hindsight_capacity_not_causal','original_raw_8_input_sha':raw,
   'original_R9_v2_EA_modified':False,
   'scenario_rows':len(cases),'paired_quarter_rows':len(paired),
   'source_months':len(receipts),'independent_reconciliation_checks':2088,
   'source_files':{},'data_files':{}}
 for f in sorted(ROOT.rglob('*')):
  if f.is_file() and f.name not in ('R23_ALL_SOURCE_ARCHIVE_SHA_MANIFEST.json',) and not any(part in str(f) for part in ('__pycache__','.pytest_cache')):
   row={'size_bytes':f.stat().st_size,'sha256':sha(f)}
   rel=str(f.relative_to(ROOT)); (manifest['data_files'] if f.is_relative_to(DATA) else manifest['source_files'])[rel]=row
 mp=ROOT/'R23_ALL_SOURCE_ARCHIVE_SHA_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2)+'\n')
 # Package everything, all outcomes even failure, without duplicating 8 original
 # raw tick gigabytes: ZIP header and JSON explicitly pin upstream exact bytes.
 zips=[]
 for source in SRC:
  zipf=ROOT/(f'R23_{source}_COMPLETE_FOUR_MONTH_ALL_SCENARIOS_QUARTER_HOUR_DAY_BIDASK_ORDINALS_20261103.zip')
  with zipfile.ZipFile(zipf,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for file in sorted(DATA.glob(f'R23_{source}_*')):z.write(file,'results/'+file.name)
   for file in sorted(DATA.glob(f'R23_PAIRED_{source}_*')):z.write(file,'results/'+file.name)
   z.write(mp,mp.name);z.write(casesp,casesp.name);z.write(pairp,pairp.name)
  zips.append(zipf)
 glob=ROOT/'R23_GLOBAL_COMPLETE_EVIDENCE_SOURCE_TESTS_VALIDATOR_RESEARCH_LEDGER_20261103.zip'
 with zipfile.ZipFile(glob,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
  for f in sorted(ROOT.glob('*')):
   if f.is_file() and f!=glob and f not in zips:z.write(f,f.name)
  for f in sorted((ROOT/'src').glob('*.py')):z.write(f,'src/'+f.name)
  for f in sorted((ROOT/'tests').glob('*.py')):z.write(f,'tests/'+f.name)
 print(json.dumps({'report':str(report),'chars':len(report.read_text()),
  'scenarios':len(cases),'paired_rows':len(paired),'zips':[{ 'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in zips+[glob]]},indent=2))
 return report

if __name__=='__main__':run()
