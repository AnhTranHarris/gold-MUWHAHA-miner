from pathlib import Path
import json,csv,hashlib,statistics,zipfile,datetime,collections
B=Path('/mnt/data/GRID0271_JAN_RESEARCH');OUT=B/'JAN_ORIGINAL_TICK_COUNTERFACTUAL';BASE=B/'JAN_BASELINE';files={p.name:p for p in OUT.glob('*')}
a=json.load(open(OUT/'JAN_REPLAY_STATIC_COUNTERFACTUAL_11_TRIALS.json'))
b=json.load(open(OUT/'JAN_ASOF_ENTRY_MOMENTUM_COST_AND_ORACLE_43_CYCLES.json'))
c=json.load(open(OUT/'JAN_NINE_CAUSAL_NATIVE_GRID_FULL_TICK_TRIALS.json'))
ra=json.load(open(BASE/'month_full_qa.json'))
basetr=list(csv.DictReader(open(BASE/'daily_performance.csv')))
basewk=list(csv.DictReader(open(BASE/'weekly_performance.csv')))
net_ref=41520.82
src_dir='https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-gamma-02-jan-grid-milestone/research/R9_GAMMA/'
reference=['2026-W01|1027.95|1083','2026-W02|5332.33|5828','2026-W03|5817.38|6095','2026-W04|7692.42|6587','2026-W05|21650.74|8387']
weekmap={x['period_id']:x for x in basewk}
wt=['| UTC ISO week | Original R9 SYNTH net | Current V1 net | Current V1 trades | Cash gap to R9 |','|---|---:|---:|---:|---:|']
for s in reference:
 w,v,n=s.split('|');v=float(v);r=weekmap[w];cash=float(r['net_profit_usd']);wt.append(f'| {w} | +${v:,.2f} | ${cash:,.2f} | {r["trade_count"]} | ${v-cash:,.2f} |')
positive=[x for x in b['cases'] if x['method']!='INADMISSIBLE_FUTURE_ORACLE_DIAGNOSTIC_ONLY' and x['net']>0]
best_pos=max(positive,key=lambda x:x['net']) if positive else None
nonoracle=[x for x in b['cases'] if x['method']!='INADMISSIBLE_FUTURE_ORACLE_DIAGNOSTIC_ONLY']
max_dream=max((x for x in b['cases'] if x['case']=='UPPERBOUND_FUTURE_BEST_SIDE_AND_EXIT_240S'),key=lambda x:x['net'])
max_static=max(a['trials'],key=lambda x:x['net'])
rows=c['trials'];unique={tuple(r[k] for k in ('grid_gap','spread_limit','stop','target','hold_ms','max_open_config','side','confirm5','watchdog4')):r for r in rows}
best_new=max(rows,key=lambda x:x['net']);
reason_counter=collections.defaultdict(lambda:[0,0.]);
for x in csv.DictReader(open(BASE/'all_completed_shadow_trades.csv')):
 k=x['reason'];reason_counter[k][0]+=1;reason_counter[k][1]+=float(x['net_shadow_usd'])
category='\n'.join(f'| {k} | {v[0]:,} | ${v[1]:,.2f} |' for k,v in sorted(reason_counter.items(),key=lambda kv:kv[1][1]))
md=f'''# GRID0271 — January 2026 repeat-hypothesis causal tick research, original source lineage and recovery decisions
**Date:** 2026-10-13. **Status:** JANUARY SOURCE-EXACT RESEARCH CYCLES COMPLETED; **NO CANDIDATE PROMOTED**. This is an experimental record and *not* a substitute for any original owner law, runnable source, preserved accepted mechanism or raw evidence. Trading remains disabled; August SEALED; J0183 unchanged.

## Source-first verification / original authority (must read exact complete sources, not this explanation)

- **Authoritative frozen full V1 owner whitepaper:** [original complete file](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt), blob `1b92b3c89159681a7181508de158af685cf5780c`.
- **Owner's January read-first anti-summary QC:** [exact complete monthly instructions](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit). Full original ratified conversation [here](https://docs.google.com/document/d/1J9d_P4ooCnNmcxPwG1F178aE4ktpkLrFclcyQPaQJ8k/edit).
- **Frozen original January rollback branch:** `carson/r9-gamma-02-jan-grid-milestone`. Exact original January [milestone document]({src_dir}GAMMA_02_JAN_GRID_MAJOR_MILESTONE_20261007.md) blob `25c9cc0d62986cc86f0b5947f70f0abc5af48a53`.
- **Original Watchdog-119 runnable helper** [source]({src_dir}helpers/gamma02_dynamic_watchdog_router_119.py), blob `b201ed9e805784f041da004d61c25fb1181e5f8b`.
- **Original 131A January quantum/subphase original helper** [source]({src_dir}helpers/gamma02_jan_watchdog119_grid_layer_refinement_131a.py), blob `edcc9b8c2352aca1a333631210fcc8f4b03d4dab`.
- **Original 131D original session portfolio helper** [source]({src_dir}helpers/jan_session_portfolio_131d.py), blob `45d0446be7a9f7ee08c0a9f8ca2a8d38a354ffc0`.
- **Original 131E source** [profit-per-heat helper]({src_dir}helpers/jan_profit_per_heat_atomic_131e.py), blob `f8c78b11213e6beccd0c4ebd3f07206b2f731065`.
- **Original R9 SYNTH day/ISO-week/month complete archival JSON:** [original primary comparator]({src_dir}artifacts/r9_synth_jan_daily_weekly.json), blob `669df6953222340b926fe60ef4ff92a3b69d24a2`. Retrieved existing benchmark WITHOUT fresh MT5 report audit.
- **Historical scientific fallback 131E:** [original evidence]({src_dir}GAMMA_02_JAN_WD119_PROFIT_PER_HEAT_131E.md); 131D [original day/week evidence]({src_dir}GAMMA_02_JAN_SESSION_FIRM_DAILY_WEEKLY_131D.md).
- **Current V1 exact run config and code:** bundled GRID0269 January ZIP (source link from existing full [GRID0269 folder](https://drive.google.com/drive/folders/1qUp7EmAQSH8Mj59kmvSgBtSk0S4Ah4bq)). The exact currently-running V1 was not overwritten; this experiment extends the analysis with separate research-only code.
- **Jan source ticks:** original `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`, SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, **9,135,062 ordered original Bid/Ask quotes**. Previously validated; no redundant whole-data audit. Original engine entry-timestamp/quote matches at **0.000 USD/oz maximum difference** for all 3,258 actual entries on source first matching tick.

## Performance acceptance: references must not be confused
- **R9 SYNTH January:** net **+$41,520.82**, **27,980 trades**, PF **23.7154**, 87.09% winners, gross loss **−$1,827.87**, average hold **16.46s**. This is an *ideal reference*, not the Python execution feed.
- **Owner 100% acceptance** includes comparable monthly net+velocity+loss+DD, and **every** same-date trading day and same ISO week, not 21/21 merely positive days. The 5 time-matched weekly target nets are from the original Git blob above; the original per-date JSON must be joined for exact day pass claims.
- **R9 OVERFIT 75% per-trade** entry/hold/exit/profit/drawdown/gross-loss six-dimensional teacher is **NOT MEASURED** by these cycles; no matching original OVERFIT trade universe has been loaded. Do not invent a 75% score or allow outcome features into runtime.
- **Original accepted January research 131E L35_C640:** +$194,425.92 / 80,929 trades / all 21 days net positive / 5 of 5 week **net** beats, **only 13 of 21 days beat** same-date SYNTH, equity DD ~**$57,139**, peak inventory ~640. The original helpers explicitly say the research fills used **session P75-normalized Bid/Ask reconstructed from Dukascopy midpoint**, NOT the original raw Dukascopy executable quotes. Major same-tick child multiplicity also needs realistic queue handling. Preserve mechanics, DO NOT claim raw quote parity or automatic deployment.

## Unmodified engine baseline (GRID0269 original complete 2026-01)
- Model account USD net **${ra['engine_result']['net_realized']:,.2f}**, realized positions **{ra['engine_result']['closed']:,}**, profit factor **{ra['engine_result']['pf']:.3f}**, win rate **{ra['engine_result']['win_rate']:.2%}**, max original tick floating equity DD **${ra['engine_result']['max_quote_equity_dd']:,.2f}**, max simultaneous positions **{ra['engine_result']['max_open']}**. Global research cap2, 250ms latency, 0.01 lot, 1oz cash multiplier, $0.20 roundtrip research fee, $100k month account, simulated only. No broker-confirmed deals.
- **Current monthly shortfall to ideal net = ${net_ref-ra['engine_result']['net_realized']:,.2f}.** Current output = negative; % achievement of positive R9 target must not be used as meaningful progress.
- Current original July research architecture is not shown to reproduce the original January original source families or earned previous-child genealogy. Mere QA correctness is not strategy performance acceptance.

### Exit-reason cash economics from all 3,258 ORIGINAL V1 closed positions
| Current original V1 exit code | Completed trades | Realized cash net |
|---|---:|---:|
{category}

### Full original January R9 SYNTH weekly references vs actual V1 ledger (UTC month-scoped ISO weeks)
{chr(10).join(wt)}

All 21 R9 SYNTH active January dates have positive original R9 cash; V1 corresponding 21 entry/exit days were negative. Full UTC per-date close ledgers were retained in source ZIP; not removed from reports.

## Hypothesis cycle A — original-entry cost-aware exit/side sensitivity, 11 variants
Research source: `j0271_jan_counterfactual_cycles.py`. All original entry times, baseline entry quotes and raw future opposing Bid/Ask are unchanged; no runtime future features. Position-free counterfactuals do NOT re-run portfolio admission or margin, and cannot be promoted.
- Distinct configs: 10/30/60/120/240s horizon, TP/SL $1/$2, $2/$3, $3/$3, $4/$3, $4/$4, 2 trailing start/gap pairs, and 3 opposite-direction sensitivity studies; all 11 original-entry static-policy outcomes **negative**.
- Best negative among these: **{max_static['case']}** net **${max_static['net']:,.2f}** on the 3,258 baseline entry cohort, not +$41.5k. Even reversing trades did not restore positive expectancy.
- Full per-case Jan entry-cohort daily cash, costs, win/PF and two half-sample outcomes are included in the machine JSON; no cherry-picked single favorable 30-minute episode.

## Hypothesis cycle B — 43 causal as-of screens and offline oracle ceiling
Research source: `j0271_asof_entry_cycles.py`. Uses exact original quote at each entry; 1/5/30/120-second **prior** (not future) quote direction, explicitly as-of time, plus original current entry spread gates .20/.40/.60/.80 USD/oz, and bounded fixed 10/30/120-second quote-sided holding outcomes. Existing V1 entries remain fixed, so gated returns cannot be interpreted as new engine cash or release of capacity.
- Best apparently positive nonoracle cohort is a tiny **{best_pos['trades'] if best_pos else 'none'}-trade** entry-spread gate; aggregate nonoracle positives are research cohort artifacts, not volume-aware portfolio candidates. Positive selected thresholds are tested against first/second January half, not a genuine untouched holdout.
- Offline, *illegal future oracle* at same positions within 240s, with existing direction, yields **+$7,038.56** after commission. It CANNOT be traded.
- Offline, *illegal future oracle* allowed to choose best direction **and** exit within 240s, yields **+${max_dream['net']:,.2f}**, or **{max_dream['net']/net_ref:.1%}** of original January R9 SYNTH net. These are optimistic quote paths for ONLY the original 3,258 entry instances. This bound does **not** apply to alternate/new entry sets or a different holding horizon.
- **Mechanism inference (SUPPORTED):** tuning stops/exits/direction on the current sparse entry set cannot meet January R9 net in the tested horizon; source opportunity generation and paid multi-scale renewal must change materially. This is not a claim that original profitable source logic is invalid.

## Hypothesis cycle C — {len(unique)} distinct full-January native grid opportunity hypotheses (10 replay entries including one duplicate QC repeat profile)
Research-only source `j0271_native_tick_grid_experiments.py`, NOT an integrated full L0-L7 V1 or the original 119/131E script. Implemented strictly chronological raw quote crossing; tried native q=$0.80/$1.19/$1.50, trend-follow vs fade, 5s previous-momentum confirmation, spread gate $0.60/$0.78, cap2/8/16 and 60s/120s first-passage stops/targets. As-of 250ms hypothetical fills, actual Bid vs Ask exits, $0.20 fixed completed trade fee, one market action per original quote tick, and bounded capital position slots, no Martingale and no month-selection execution feature.
- Full-original-month **{c['ticks']:,}** quotes on each run; no strategy, price source or month data substituted.
- None achieved profitability. Least-negative native whole-month source prototype: **{best_new['name']}**, {best_new['closed']:,} completed trades, net **${best_new['net']:,.2f}**, PF {best_new['pf']:.3f}, quote-equity DD **${best_new['max_quote_equity_dd']:,.2f}**, only **{best_new['positive_trading_days']}** positive quoted day, **{best_new['positive_month_weeks']}** positive ISO weeks.
- Cheap dense crossings are NOT equivalent to profitable signal manufacture. More concurrency on negative after-cost edge magnified losses. Standalone simplistic q-grid is rejected as a full solution, not as a valid original Watchdog reproduction.
- The raw January spread median was **$0.70/oz**, 75th percentile **$0.83/oz**; a $0.78 gate accepted approximately 65.58% of all source observations. A simplified fast q$0.80 harvest has a material spread/fee hurdle before slippage.
- Corrected research-test scout bootstrap for four-win Watchdog proof; one duplicate cap profile reproduced the corresponding same source outcome, offering no standalone discovery. A genuine Watchdog owner needs strict as-of *funded child* settlement ancestry and physical inventory control, unlike this toy proof counter. Do not integrate prototype as V1 itself.

## Falsification ledger / stop wasting time
- **Rejected for promotion:** fixed exit tuning on unchanged original entries; broad opposite-side flipping; simple spread-only filter with ~32 eligible entries; isolated momentum-only prior 1/5/30/120s rules; simplistic q-only raw-tick grid; increasing capacity on the q-only negative edge.
- **Never promote:** hindsight-selected January R9 / original profitable stream month-cells; offline oracle future side/exit; normalized-spread Watchdog fills as if raw Ask/Bid; 600 same-timestamp fills from independent broker trade events.
- **Cause still unresolved:** what *specific* causal original January source family produces positive real Bid/Ask expected move AFTER estimated cost, while respecting tick queue capacity and avoiding high floating-equity heat. This is the next productive research target, not more sweeping new generic indicators.

## P0 source-exact next engineering steps (not implied completed)
1. **Reproduce exact original 119/131A/131D/131E source dependencies** from frozen Git branch + original Helper archive and original settings, without using a handoff summary. Extract parent ID, first-parent scout, 10-minute ownership, 4 previous *realized winning* <=60s child proof, q=1.19 (bins 0–4)/1.10 (last bin), max layer35, ASIA02/LONDON10/OVERLAP13/LATE21, source12 coldstart, and L7 capacity.
2. **Reprice original parent/child events with actual raw Dukascopy Bid/Ask and 250ms quote latency**, preserving chronological source entry/exit semantics. Compare original normalized-spread results vs raw at same realized event population; report how much return is explained by spread model, synchronization, and unrealized heat. Do not use oracle-optimized entry/exit from the future.
3. **Restore causal independent first-touch high-frequency qualified signal manufacture** and real research-only previous-child paid settlement as separate L4 shadow ancestry from broker-confirmed deals. Current V1 only carried numeric proposal IDs to 46/3258 trades. Ensure every source accepted for new trades has immutable ID; no fictitious credit for denied/unfilled shadow.
4. **Run full integrated FourSessionV1 with one exact causal structural repair at a time**; stress under full raw January ticks with 0.01 lot, booked/open cash, day/ISO-week/month from original reference and future teacher disabled. Replicate original success mechanisms, not guessed approximations. First gate is after-cost positive net and lower gross loss/DD, then 21/21 true R9 day *targets*, 5/5 week targets, monthly $41,520.82 and 27,980 positions; risk tradeoffs separately.
5. **Do not claim the R9 OVERFIT 75% target** until exact archived offline per-trade teacher data is sourced and one fixed matching protocol is preregistered. Validate matching without future leakage on the runtime side.
6. Only after source-first and acceptable January candidate, append candidate code/hash/metrics/QA to January's designated original-source→trials→QC folders, regress February, and seek owner HITL approval. No early MT5 port, official state advancement or AUG opening.

## Important scope and QA
- Three independently persisted original-tick experiment families: 11 static same-entry counterfactuals; 43 as-of screens+oracles; {len(unique)} UNIQUE native source variants each processed full 9,135,062 original January ticks (10 logged including one repeat parameter profile). **No integrated V1 candidate profit improvement claimed.**
- Source code and run outputs are in GRID0271 archive, with baseline January unchanged GRID0269 archive; nested machine results contain each param, net/gross, win, PF, UTC day/week, half-month where relevant. Original code files and accepted archive remain immutable.
- Negative findings constrain future research; we have **not** reached 100% R9 SYNTH January net/day/week or 75% R9 OVERFIT. Do not conflate passing a unit/chronology test with monthly strategy economic acceptance.
'''
report=OUT/'GRID0271_JANUARY_EMERGENCY_HALLUCINATION_CYCLE_SOURCE_EXACT_RESEARCH_REPORT.md';report.write_text(md)
meta={'original_source_github_branch':'carson/r9-gamma-02-jan-grid-milestone','original_source_sha256':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','baseline_unchanged_net_usd':ra['engine_result']['net_realized'],'r9_synth_jan_net':net_ref,'native_unique_scenarios':len(unique),'native_run_profiles':len(rows),'exit_policy_scenarios':len(a['trials']),'asof_and_oracle_scenarios':len(b['cases']),'jan_goal_met':False,'overfit_teacher_75pct_scored':False,'prepared_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(OUT/'GRID0271_QC_DISPOSITION.json').write_text(json.dumps(meta,indent=2))
# QC aggregate, including byte-level reproduction hashes for complete output
assert round(float(sum(float(r['net_profit_usd']) for r in basetr)),2)==round(ra['engine_result']['net_realized'],2)
assert round(float(sum(float(r['net_profit_usd']) for r in basewk)),2)==round(ra['engine_result']['net_realized'],2)
assert len(a['trials'])==11 and len(b['cases'])==43 and len(unique)==9
assert max(x['net'] for x in rows)<0
assert max(x['net'] for x in a['trials'])<0
assert max_dream['net']<net_ref
assert ra['engine_result']['closed']==3258
files_to_zip=[report,OUT/'GRID0271_QC_DISPOSITION.json',*OUT.glob('*.json'),*OUT.glob('*.csv'),B/'j0271_jan_counterfactual_cycles.py',B/'j0271_asof_entry_cycles.py',B/'j0271_native_tick_grid_experiments.py',B/'j0271_trials.log',B/'j0271_asof.log',B/'j0271_native.log',BASE/'daily_performance.csv',BASE/'weekly_performance.csv',BASE/'run_config.json',BASE/'original_source.sha256']
files_to_zip=list(dict.fromkeys(files_to_zip));files_to_zip=[f for f in files_to_zip if f.exists()]
zipout=B/'GRID0271_JANUARY_RESEARCH_63_CAUSAL_AND_COUNTERFACTUAL_SCREENINGS_20261013.zip'
with zipfile.ZipFile(zipout,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for x in files_to_zip:z.write(x,x.name)
manifest={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in files_to_zip};(OUT/'GRID0271_SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(zipout,'a',zipfile.ZIP_DEFLATED,compresslevel=8) as z:z.write(OUT/'GRID0271_SHA256_MANIFEST.json','GRID0271_SHA256_MANIFEST.json')
print('report',report,'characters',len(md));print('archive',zipout,'bytes',zipout.stat().st_size);print('sha256',hashlib.sha256(zipout.read_bytes()).hexdigest())
