"""Package full source-exact R17 per-month traces, all 460800 quarters and logs.

All original primary R9/R11/R12/R13/R14/R15/R16 files are read-only.
"""
from pathlib import Path
import csv,hashlib,json,zipfile,gzip,shutil
BASE=Path('/mnt/data/h1v2_r17_multiscale_latency');RESULTS=BASE/'results';FINAL=BASE/'final';FINAL.mkdir(exist_ok=True)
MONTHS=('01','02','06','07')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
def csvs(rows,path):
 with path.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

groups=[];allquarters=[];receipts={}
for mon in MONTHS:
 rec=json.loads((RESULTS/f'R17_{mon}_EXACT_SOURCE_AND_REPLAY_RECEIPT.json').read_text())
 receipts[mon]=rec
 with (RESULTS/f'R17_{mon}_FULL_40_MECHANISM_FALSIFICATION.csv').open(newline='') as f:groups+=list(csv.DictReader(f))
 with (RESULTS/f'R17_{mon}_ALL_{rec["full_quarter_records"]}_ORIGINAL_QUARTER_OUTCOMES.csv').open(newline='') as f:allquarters+=list(csv.DictReader(f))
assert len(groups)==160 and len(allquarters)==460800
csvs(groups,FINAL/'R17_ALL_160_SOURCE_MONTH_LANE_GATE_ATOMIC_RESULTS.csv')
cs=FINAL/'R17_ALL_460800_ORIGINAL_FROZEN_QUARTER_GATE_OUTCOMES.csv.gz'
with gzip.open(cs,'wt',encoding='utf8',newline='',compresslevel=6) as f:
 w=csv.DictWriter(f,fieldnames=list(allquarters[0]));w.writeheader();w.writerows(allquarters)
months={'01':'January','02':'February','06':'June','07':'July'}
lines=[
'# H1V2 R17 — COMPLETE SOURCE-EXACT 15M/1H/4H ADAPTIVE ENTRY FRAGILITY FALSIFICATION',
'',
'2026-11-03 | XAUUSD / Gold MUWHAHA Miner | Research only. NO R9 EA modification.',
'',
'THIS IS NOT A SHORTENED HANDOFF: The original 85KB full hourly audit, 160 complete month-lane-gate results, every 460,800 original 15-minute gate outcome row, four original source month quote ordinals, exactly reproduced R16 source-selected entry/exit chronology, five adversarial tests, four complete independent source SHA/quote-level verifications, and all 100ms outcomes are retained inside the SHA-pinned companion archives. Existing R11/R12/R13/R14/R15/R16 originals remain separately immutable and referenced.',
'',
'## Scientific separation: model knowledge, source facts, and deliberately unproven research',
'',
'1. ORIGINAL PRIMARY FROZEN R11S4 source evidence: strict +0.10 nominal net favorable by 15 sec and zero entry liquidation-side -0.10 adverse through 30sec, one-position fixed30 occupancy. 246 of 1917 R9-active hours source-infeasible within THAT contract. Original raw BID/ASK quote timestamps source exact Jan/Feb/Jun/Jul. This experiment does not overwrite those labels.',
'2. R12 source distinct first-TP exit and R16 widened experimental <=4.00 as-of admission permit MORE future-qualified nonoverlap quota count because the contract changes. Widened spread is NOT a Coinexx live account or approved broker gate.',
'3. R16 performed independent 100ms delayed frozen future-informed signals: original widened WIDE_REQUOTE 175503 GOOD / 61005 completed failed, precision 74.2059465219%. It fails 80% and has no real failed-exit economic PnL certification.',
'4. R17 implements five distinct R16 future-selected candidate source domains × eight PREDECLARED causal-prefix gating rules × four source months. The *rule features* are past-only and can be transported to a future causal predictor. The *input entry times and sides* remain selected by R16 offline future-informed oracle, therefore every R17 outcome remains a hindsight-conditioned stress test, NOT out-of-sample predictor, NOT deployable trading.',
'5. Strict actual 100ms+ first OBSERVED future quote on Dukascopy original quote sequence; BUY Ask entry/Bid liquidation, SELL Bid entry/Ask liquidation, original research fee $0.02 quote-price, +$0.10 net TP threshold; no post-entry 60s safety substitution. $0.02 source quote-price is NOT a broker cash commission in USD per 0.01 lot. Two-leg slippage 0 baseline here, original R16 has all 0/100/500ms × 0/0.02 per leg in separate immutable preservation.',
'6. One-position strict global chronology REPLAYED after each as-of gate; no use of stale busy/drop statuses to credit performance. Failed completed position occupies full30. Censor, quote/spread rejects and busy skips are not counted correct. Source 15m quota is exact original 85-day R9 SYNTH DAILY event extracted UTC clock matched; never hour/4.',
'',
'## Exact new source-only as-of geometry',
'',
'At action quote ordinal i: current executable entry bid_i,ask_i, actual spread s_i=ask_i-bid_i (integer $0.001). For each h in {900000,3600000,14400000}ms, anchor a_h is last actually observed quote index j with time_j <= time_i-h, and j < i. If absent, horizon is missing and alignment fails closed. The midpoint is used ONLY for signed trend feature, computed integer bid+ask, never as executable entry/exit. A positive side×(mid2_i-mid2_anchor) means historical direction alignment. The source quote last-admissible age at horizon is recorded and stale anchors older than horizon suppressed. Existing R16 3s signed Bid/Ask moves and its 15s/300s as-of spread EMA remain immutable. If EMA missing/nonfinite, all new gates fail closed.',
'',
'## Eight predeclared gates (NO result-dependent retuning)',
'',
'- ALL_FUTURE_SELECTED_CONTROL: unchanged R16 future-selected signal schedule; exact parity control.',
'- ORIGINAL_SPREAD_1500: actual current spread <= $1.50, never read future spread.',
'- CURRENT_SPREAD_LE_300S_EMA: current spread <= as-of existing R16 300s EMA.',
'- SPREAD_RELIEF_080_AND_3S_FLOW: current spread <= 80% of as-of EMA300 and EMA15 <= EMA300 and BOTH previously observed 3s Bid and Ask movement same sign as original side, each >= current spread + 0.12.',
'- HTF_15M_1H_SIDE_ALIGNED: as-of 15m and 1h price midpoint slopes both same sign as original future-known side.',
'- HTF_15M_1H_4H_SIDE_ALIGNED: as-of 15m, 1h and 4h midpoint slopes all match original future-known side.',
'- BROKER_ADAPTIVE_HTF_COST_GATE: original spread<=1.50 OR (spread<=4.00, spread relief + coherent3s flow + 15m/1h directional alignment), experimental ORIGINAL CONTRACT NOT APPROVED.',
'- HTF_ALIGNED_AND_ORIGINAL_SPREAD: original spread<=1.50 AND all 15m/1h/4h past-side slopes aligned.',
'',
'## Source and research dependency pins',
'',
'- Existing repaired R9 v2 SHA ded3d0dff9d9112be52d9ddb29fbc7c6b9e2a1c0; no current MT5 EA changed.',
'- Immutable H1V2 teacher SHA edce573d9c53b743dc5de1b0d741c81370af52c1.',
'- Existing additive R16 Git HEAD 0bb5f28567680dc2ef92a9ea6ceb01a0aa6975fd, published under carson/h1v2-r16-broker-adaptive-fullcalendar-20261103.',
'- R16 complete full unabridged original report https://drive.google.com/file/d/1ngyA6IMRhi0D88bjAByGCD2LIho8URr6/view ; complete R16 four-month source ZIPs and all original latency traces listed in append-only R12–R16 source ledger https://docs.google.com/document/d/1iVv1tAmJlBWhNfXMcw2N50VEVIFrawMObGOzyfUGWmI/edit .',
'- Original full forensic audit https://docs.google.com/document/d/1n8Zd37SH3k2mNYpCERHsGSeR5GL-vDNLDv780Bv5-Do/edit .',
'- Four original R17 source-hash and derived quote/feature CSV/NPZ/100ms outcome byte SHA pins and all 32,290,648 raw quote totals below appear in exact manifest and four full per-month JSON receipts.',
'',
'## Complete high-level falsifications, NOT predictive certification',
'',
'Initial frozen synthetic candidate research rejects a simple HTF filter as a viable joint solution under 100ms first-observed quote delay. The widest requote experimental lane completes 175503 GOOD /61005 BAD (74.2059%) unfiltered. Restricting to original <=$1.50 increases to 74.45% but loses widened admission and still fails 80%. Past 15m/1h/4h simple direction agreement degrades strict correctness or throughput. 60s WATCH post-entry from R15 worsens source strict labels; 60s pre-entry as R16 is sparse. No positive economic net or broker-independent high-volume result is claimed.',
'',
'## Adversarial/test boundary',
'',
'R17 synthetic 5 tests PASS: future-quote mutation after decision does not affect earlier past-only features; no prehistory is fabricated as 15m/1h/4h signal; last actual quote anchor respects horizon cutoff and ordinal; explicit side/spread/two-EMA gate; all nonfinite histories fail closed. Python compileall pass. FULL independent verifier reread every source month original SHA and both source candidate/selected NPZ and all original R16 100ms stress NPZ hashes; byte-SHA per derived full output; all original 460800 quarter×gate records, source-selected ordinals and exact side, 15m/1h/4h price anchors and arithmetic; all 100ms frozen unfiltered controls exactly parity with R16 per quote. Per-month exact receipts in archive.',
'',
'## Limits, missing broker verification and next falsifiable science',
'',
'- Current complete four-month experiment is Dukascopy BID/ASK historical stream; historical Coinexx original R9 SYNTH (synthetic Strategy Tester) and REAL (real tick Strategy Tester) have been source compared only in matched Feb02 06UTC within R13/R14/R15. Full four-month Coinexx actual observed tick source cannot be inferred from SYNTH trade event counts. Separate source exact 85-day original R9_SYNTH daily entry event index does NOT by itself prove full original source Bid/Ask quote access in this research session.',
'- Neither oracle, as-of filters using future-selected side, nor conditional data can serve as a trained BUY/SELL/WAIT as-of model. July already exposed to human research and cannot be called blind OOS; strict purged chronological calibration, broker joint data, and unseen later calendar dates are required.',
'- Next hypothesis family EX-17-A: broker-normalized dimensionless spread strain as s / conservative previously observed achievable gross 15s range; EX-17-B: as-of joint competing hazards BUY/SELL favorable-before-adverse with latency-contingent absorption; EX-17-C: market-structure graph 250ms/3s/15s/15m/1h/4h with spread-state hysteresis and no future mark; EX-17-D: bid/ask broker-specific hysteretic shadow-price WAIT policy optimizing hazard of follow-up actual quote plus one-position time value; EX-17-E: each broker independent positive expected full-trade net after actual slip and R9 original trail/stop/time-out, never use quota to force entries.',
'- Distinct broker shadow engine must compare same UTC trading hour and each 15m quota using original ticks for both broker domains and preserve runtime fill modes, quote staleness and actual commission+margin. No as-of student or OOS economic pass in this document.',
'',
'## FULL 160 original source result records (VERBATIM; all 460800 quarter records retained in separate CSV.gz and per-month ZIP)',
'',
'```csv']
with (FINAL/'R17_ALL_160_SOURCE_MONTH_LANE_GATE_ATOMIC_RESULTS.csv').open(encoding='utf8') as f:lines+=f.read().rstrip().splitlines()
lines+=['```','', '## Four atomic monthly receipts and complete files','']
for m,r in receipts.items():
 lines+=['### '+months[m]+' 2026', '```json',json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False),'```','']
lines+=['No original R9 v2 MT5 EA, original R11S1 fixed survival labels, or original R16 future-selected source were changed. All research remains nondeployable.','']
report=FINAL/'R17_COMPLETE_UNABRIDGED_FOUR_MONTH_ASOF_HTF_LATENCY_FALSIFICATION_20261103.md';report.write_text('\n'.join(lines),encoding='utf8')
# Month source ZIPs: complete derived original full quarter rows, full future-selected source quote ordinals,
# every new prefilter 100ms signal/fill/exit outcome, exact original R16 source dependencies pinned.
archives={}
for m in MONTHS:
 z=FINAL/f'R17_MONTH_{m}_COMPLETE_SOURCE_ORDINALS_ALL_100MS_INTERVENTIONS_20261103.zip'
 items=sorted(RESULTS.glob(f'R17_{m}_*'))+[BASE/'logs'/f'month_{m}.log']
 with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as dst:
  for p in items:dst.write(p,arcname=('logs/' if p.parent.name=='logs' else 'results/')+p.name)
 with zipfile.ZipFile(z) as check:assert check.testzip() is None
 archives[m]={'file':z.name,'bytes':z.stat().st_size,'sha256':sha(z),'member_count':len(items)}
core=FINAL/'R17_COMPLETE_FOUR_MONTH_RESEARCH_CODE_FULL_AUDIT_AND_ALL_ATOMIC_RESULTS_20261103.zip'
items=[BASE/'src/r17_asof_htf_latency.py',BASE/'tests/test_r17_asof.py',BASE/'verify_r17_source_exact.py', BASE/'build_r17_full_artifacts.py',
       BASE/'logs/full_independent_verify.log',RESULTS/'R17_COMPLETE_INDEPENDENT_QUOTE_SOURCE_AND_ALL_ROWS_VERIFICATION.json',
       FINAL/'R17_ALL_160_SOURCE_MONTH_LANE_GATE_ATOMIC_RESULTS.csv',FINAL/'R17_ALL_460800_ORIGINAL_FROZEN_QUARTER_GATE_OUTCOMES.csv.gz',report,
       Path('/mnt/data/H1V2_COMPLETE_DEEP_HOURLY_AUDIT_20261103.md'),
       Path('/mnt/data/R15_COMPLETE_UNABRIDGED_HINDSIGHT_WATCH60_CROSSFEED_REPORT_20261103.md')]
with zipfile.ZipFile(core,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as dst:
 for p in items:dst.write(p,arcname=('source/' if p.name.endswith('.py') else 'full_original_records/' if p.parent==Path('/mnt/data') else 'research/')+p.name)
with zipfile.ZipFile(core) as check:assert check.testzip() is None
manifest={'status':'R17_ALL_FOUR_HISTORICAL_DUKASCOPY_FUTURE_ORACLE_FRAGILITY_ONLY_NO_COINEXX_FOUR_MONTHS',
  'months':list(MONTHS),'total_orig_source_quotes':32290648,
  'strict_source_original_quarters':11520,'all_full_5lane_8gate_quarter_rows':len(allquarters),
  'all_full_month_lane_gate_results':len(groups),'independent_verifier':'R17_COMPLETE_INDEPENDENT_QUOTE_SOURCE_AND_ALL_ROWS_VERIFICATION.json',
  'month_full_archives':archives,'core_archive':{'file':core.name,'bytes':core.stat().st_size,'sha256':sha(core),'member_count':len(items)},
  'full_source_code_sha256':sha(BASE/'src/r17_asof_htf_latency.py'),
  'full_independent_verifier_sha256':sha(BASE/'verify_r17_source_exact.py'),
  'all_full_result_shas':{x.name:{'bytes':x.stat().st_size,'sha256':sha(x)} for x in [FINAL/'R17_ALL_160_SOURCE_MONTH_LANE_GATE_ATOMIC_RESULTS.csv',cs,report]},
  'source_inputs_receipts_exact':receipts,
  'no_deployment':True,'no_train_predictor':True,'no_live_coinexx_data_certification':True}
mp=FINAL/'R17_SOURCE_EXACT_ALL_FOUR_COMPLETE_SHA_AND_RECOVERY_MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'completed':True,'files':len(archives)+2,'archived_quarter_rows':len(allquarters),'group_rows':len(groups),'core_bytes':core.stat().st_size,'months':archives,'report_bytes':report.stat().st_size,'sha_manifest':str(mp)},indent=2))
