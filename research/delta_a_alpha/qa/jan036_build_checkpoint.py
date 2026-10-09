import hashlib,json,tarfile
from pathlib import Path
import pandas as pd,numpy as np
from datetime import datetime,timezone
R=Path('/mnt/data/daa_jan_lattice_036')
S=pd.read_csv(R/'JAN036_ALL_CASES.csv');S=S.sort_values('net',ascending=False)
C=pd.read_csv(R/'JAN036_SELECTED_MONTHLY.csv');W=pd.read_csv(R/'JAN036_SELECTED_WEEKLY.csv');D=pd.read_csv(R/'JAN036_SELECTED_DAILY.csv')
R9=pd.read_csv('/mnt/data/daa_jan_exact_032/output/JAN032_RAW_VS_R9_WEEKLY.csv')[['date','r9_synth_net','r9_synth_trades']].rename(columns={'date':'week'})
sel=W.merge(R9,on='week',how='left');sel['beats_r9_synth_net']=sel.net>sel.r9_synth_net
sel.to_csv(R/'JAN036_WEEKLY_VS_R9.csv',index=False)
R9day=pd.read_csv('/mnt/data/daa_jan_exact_032/output/JAN032_RAW_VS_R9_DAILY.csv')[['date','r9_synth_net','r9_synth_trades']]
selday=D.merge(R9day,on='date',how='left');selday['beats_r9_synth_net']=selday.net>selday.r9_synth_net
selday.to_csv(R/'JAN036_DAILY_VS_R9.csv',index=False)
scenarios=['lattice_base384','lock_12_90s','dyn_w1000_n128_spr1500_disp8000','dyn_w2000_n256_spr1500_lock12000','highvel_q384_w1000_n384_sp2500_lock12','highvel_q384_w1000_n256_sp1500_lock12']
rows=[]
for name in scenarios:
 r=json.loads((R/(name+'.json')).read_text())
 rows.append({k:r[k] for k in ['name','net','trades','gross_profit','gross_loss','PF','win_pct','equity_dd','recovery_trades','recovery_net','hourly_net']})
this=pd.DataFrame(rows)
report=[f'# January 036 — Adverse-Direction Hyperlattice / Original-Source Causal Candidate Research',
'',f'**Checkpoint time (UTC):** {datetime.now(timezone.utc).isoformat(timespec="seconds")}',
'**Caution: NOT original V1 L0–L7 physically funded source parity. Source entry tape remains fixed.**',
'', '## Governing document and scope','',
'- The original 14,232-character owner Google Drive V1 whitepaper, preserved verbatim on `delta-A-alpha`, is governing, *not* shortened 024–029 models.',
'- Jan 032 original 131E candidate tape: 47,511 deals; 9,135,062 actual Dukascopy ordered Bid/Ask ticks; fixed 0.01 lot assumed one oz, $0.02 fee per ticket. Commission/market impacts/broker-order throttling not Coinexx-certified.',
'- L3 London/NY harvesting preserved byte-for-byte at +$60,197.326 across all screening strategies. Dynamic rules are applied to original L4 Watchdog candidate admission; independent experimental L6 inverse scalp/runner is an original-layer-compatible *hypothesis*, **not** the historical native L5/L6.',
'- Controls use observed spread, completed trailing tick prices, actual accepted cell inventory and elapsed event time. No month/date lookup, future bars, synthetic spreads, loss-dependent lot scaling or Martingale.',
'- Historical January data used to select parameters: NOT untouched out-of-sample. Original child-parent proposal genealogy after rejecting a candidate is NOT recomputed; reperform on fully causal funded source before promotion.',
'','## Novel hyperlattice states','',
'**Continuation:** Original Watchdog owns market-side campaign; original L3 session/higher-timeframe inputs remain unchanged.',
'**Suspected failed ignition:** An already-observed 20-second price displacement against held Watchdog inventory and negative floating heat causes a 30–120s suspension of *new* Watchdog child admission, without prematurely liquidating all originals.',
'**Spatial campaign deconcentration:** An original Watchdog child can be admitted only if same-side physical inventory within its price cell is under capacity when current executable spread and/or displacement conditions imply crowding; cells release capacity only on an actual funded exit.',
'**Attempted confirmed transfer:** A separately funded 0.01-lot inverse microgrid or runner opens on first-touch observed displacement and completed M5/M15 optional confirmations; finite slots, quote-side stops and TP; all tested inverse branches lost money or did not trigger and are REJECTED.',
'','## Screening results','',f'159 full-January parameter scenarios; 8 detailed reconciled original-candidate tape replays (2 families of inverse recovery losing or inactive).',
'',this.to_markdown(index=False,floatfmt='.2f'),'','### Primary candidates and trade-offs','',
'**Profit/velocity:** `highvel_q384_w1000_n384_sp2500_lock12`: +$94,030.989 / 35,191 / gross loss -$10,347.425 / PF 10.0874 / max tick equity DD $43,224.84. Against original raw 131E it improves net, gross loss, PF, DD; reduces original 47,511 velocity but still above R9 27,980. Compared to prior C384 it raises net and reduces gross loss but does NOT lower C384 DD.',
'**Balanced low drawdown:** `dyn_w1000_n128_spr1500_disp8000`: +$87,133.389 / 29,551 / gross loss -$9,694.967 / PF 9.9875 / DD $19,744.68. Improves gross loss, PF, DD and net versus previous 035 C192 candidate, but loses 250 trades and net remains below original raw source.',
'**Stronger gross-loss/PF with velocity:** `dyn_w2000_n256_spr1500_lock12000`: +$87,482.473 / 29,858 / gross loss -$8,669.679 / PF 11.0906 / DD $28,816.56.',
'**Why no high-profit inverse runner?** 5–20s impulse + opposite entries paid actual spread and first-touch stops; loss of $845.667 over 336 inverse tickets in one scout. More patient 30s/5min directional runner lost $250.168 over 88 trades; M5-aligned scout found no opportunities. Therefore no inverse recovery branch is promoted.',
'','## Critical anti-overfit result','',
'**Every tested selected portfolio deviation from 035 C384 occurred on 2026-01-30. All other 20 R9 SYNTH trading dates were unchanged.** This is an event-local repair, not proven day-to-day learning or unknown-date transfer; no calendar identity appears in entry code.',
'### Weekly selected net vs R9 SYNTH','',
sel[sel.scenario.isin(['lattice_base384','dyn_w1000_n128_spr1500_disp8000','dyn_w2000_n256_spr1500_lock12000','highvel_q384_w1000_n384_sp2500_lock12'])][['scenario','week','net','trades','r9_synth_net','beats_r9_synth_net']].to_markdown(index=False,floatfmt='.2f'),'',
'## Community and implementation cross-references','',
'- [QuantConnect MaximumDrawdownPercentPortfolio](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumDrawdownPercentPortfolio.py) — risk gate must assess actual portfolio exposure, but blanket liquidation is not adopted.',
'- [QuantConnect MaximumSectorExposureRiskManagementModel](https://github.com/QuantConnect/Lean/blob/master/Algorithm.Framework/Risk/MaximumSectorExposureRiskManagementModel.py) — general bounded exposure principle adapted to side-and-price-cell concentration, **not** its dynamic scaling.',
'- [River ADWIN](https://github.com/online-ml/river/blob/main/river/drift/adwin.py) — prospective closed-observation regime-change detector, no unvalidated online learner has been enabled.',
'- [MetaQuotes 21833](https://www.mql5.com/en/articles/21833) — finite-grid cycle, equity-based cycle management and state-aware limits; source inspiration only, NOT performance evidence.',
'- QuantConnect trading risk models distinguish strategy signal formation from pre-trade risk and executable broker buying power; no claim of identical XAUUSD performance.',
'','## Next gate: original full-funded source genealogy','',
'1. Preserve original 049→051→075→084→119→131E funded parent event ownership, cap rejection, genuine children-only streak/unlock/relock, and all the original session/Asia/higher-timeframe/native/recovery roles.',
'2. Replace fixed precomputed hypothetical child outcomes with a single actual-quote funded trade ledger; regenerate future parent proposals after each admission denial/exit. No shadow win may unlock a funded child.',
'3. Enforce broker-correct margin, real fill latencies/order limits and stopout; replacing hundreds of identical one-quote fills is a separate execution engineering problem.',
'4. Run the new price-cell/adverse-displacement admission policies without January-special hard-coding. Optimize solely on causal market state, preserve 5-minute readiness conditional on valid history.',
'5. Compare January–July daily/weekly/monthly, source family P&L, win rate, gross loss, PF, expectancy, full tick equity DD, aggregate lots, first-quote readiness and capital survival. Keep August sealed / September reserved.',
'','## QA and failure recovery','',
'- Selected eight saved trade ledgers re-executed on all 9.135m January quote ticks and reconciled original source exact-quote-side P/L, earliest entry/exit chronology and daily/weekly/monthly economic totals.',
'- All selected maintain L3 hourly net exactly +$60,197.326. First-touch inverse branches have separate funded tickets with recorded actual Bid/Ask closes. None was profitable or accepted.',
'- Verified input and scenario integrity are recorded in `JAN036_QA_RESULTS.json`; source scripts and selected tapes are archived. No original source file or production MT5 EA modified.',
'- January performance is a *counterfactual original-entry-tape research result*, **not a certified full V1 trading EA**. Do not promote based on this result.',
]
(R/'DAA_JAN036_HYPERLATTICE_RESEARCH.md').write_text('\n'.join(report)+'\n')
readme=f'''# JAN036 — TIMEOUT SAFE READ FIRST\n\nOwner V1 original literal whitepaper hardlocked in main GitHub branch. Latest preserved Jan 036 research: {len(S)} real-quote full-January candidate-admission and inverse-grid scenarios, 8 selected complete-ledger QA passes; no MT5/physical-funded genealogy certification.\n\nUse `JAN036_SELECTED_MONTHLY.csv`, `JAN036_DAILY_VS_R9.csv`, `JAN036_WEEKLY_VS_R9.csv`, `JAN036_QA_RESULTS.json`, and the research report.\n\nHighest-profit risk-lock: $94,030.989 / 35,191 / PF10.0874 / gross loss -$10,347.425 / equity DD $43,224.84; focused lower-DD: $87,133.389 / 29,551 / PF9.9875 / gross loss -$9,694.967 / DD$19,744.68; 30k-trade higher-PF: $87,482.473 / 29,858 / PF11.0906 / gross loss -$8,669.679 / DD$28,816.56. All differences concentrate Jan30.\n\nDo NOT rerun all screening variations or mistake these for physically accepted Watchdog parent-chain performances. Next original L0–L7 physically funded genealogy 033. Preserve no lot scaling, December history dependency, August sealed and September reserved.\n'''
(R/'JAN036_HANDOFF_READ_FIRST.md').write_text(readme)
files=sorted([p for p in R.glob('*.py')]+[R/f for f in ['DAA_JAN036_HYPERLATTICE_RESEARCH.md','JAN036_HANDOFF_READ_FIRST.md','JAN036_ALL_CASES.csv','JAN036_SELECTED_MONTHLY.csv','JAN036_DAILY_VS_R9.csv','JAN036_WEEKLY_VS_R9.csv','JAN036_QA_RESULTS.json']]+list((R/'selected_tapes').glob('*.npz')))
manifest={'version':'jan036','raw_input_reference':'XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','caution':'no raw tick file or production EA changes','file_checksums':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(R/'JAN036_SHA256SUMS.json').write_text(json.dumps(manifest,indent=2)+'\n')
files.append(R/'JAN036_SHA256SUMS.json')
archive=R/'JAN036_HYPERLATTICE_SOURCE_CASES_AND_QA.tar.gz'
with tarfile.open(archive,'w:gz') as f:
 for p in files:f.add(p,arcname=str(p.relative_to(R)))
with tarfile.open(archive,'r:gz') as f:
 members=f.getmembers();ok=all(hashlib.sha256(f.extractfile(name).read()).hexdigest()==digest for name,digest in manifest['file_checksums'].items())
print('CHECKPOINT',json.dumps({'scenarios':len(S),'source_reconciled':8,'archive':str(archive),'members':len(members),'all_sha_valid':ok,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_size':archive.stat().st_size,'unique_active_dates':D.date.nunique()}))