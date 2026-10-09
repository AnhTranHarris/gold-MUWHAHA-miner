from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,csv
import numpy as np
R=Path('/mnt/data/feb046');R.mkdir(exist_ok=True)
load=lambda x:json.loads((R/x).read_text())
post=load('RECOVERY_SCREEN.json');closed=post['screen'];srec=load('STRUCTURAL_RECOVERY_SCREEN.json');combo=load('RECOVERY_COMBINED_SCREEN.json');narrow=load('STRUCTURAL_EXIT_NARROW.json');relock=load('FUNDED_RELOCK_FOCUS_SCREEN.json');eq=load('EQUITY_GUARD_SCREEN.json');daily=load('DAILY_FORENSICS.json')
files={'2026-01':'/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','2026-02':'/mnt/data/XAUUSD_DUKAS_2026_02_ticks.csv(3).gz'}
hashes={k:hashlib.sha256(Path(v).read_bytes()).hexdigest() for k,v in files.items()}
expect={'2026-01':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','2026-02':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d'}
assert hashes==expect
profit=dict(net=206528.578,loss=-7616.383,pf=28.116359,trades=25443,dd=19308.087)
prevent=dict(net=200982.522,loss=-8721.152,pf=24.04541,trades=25313,dd=16458.447)
assert post['base']['net']==profit['net'] and abs(post['base']['dd']-profit['dd'])<.002
assert any(x['config']['tp']==6 for x in closed)
assert all(x['net']<=profit['net']+.001 for x in closed)
assert len(srec)==18 and len(combo)==10 and len(eq)==12 and len(relock)==6
assert all(abs(x['exact_dd']-(profit['dd'] if x['baseline']=='profit' else prevent['dd']))<.002 for x in combo)
assert all(x['net'] <= (profit['net'] if x['baseline']=='profit' else prevent['net'])+.001 for x in combo)
qa={
 'model':'FEB046 causal research overlays with original fixed source proposal tape; NOT a full V1/L6/MT5 economic certification',
 'whitepaper':'research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt',
 'source_hashes':hashes,
 'quotes_in_combined_context':11439219,
 'original_feb045_baselines':{'profit':profit,'lower_dd':prevent},
 'experiment_counts':{'post_realized_loss_overlay':len(closed),'preclose_M5_H1_recovery_overlay':len(srec),'prevention_plus_recovery_ablation':len(combo),'preclose_structural_exits_first_narrow_screen':len(narrow['cases']),'funded_loss_relock_focus':len(relock),'equity_peak_guard':len(eq)},
 'tested_minimum_evaluations':len(closed)+len(srec)+len(combo)+len(narrow['cases'])+len(relock)+len(eq),
 'new_recovery_trials_profitable':int(sum(x['l6_net']>0 for x in srec if x['l6_trades']>0)),
 'new_recovery_trials_with_actual_trades':int(sum(x['l6_trades']>0 for x in srec)),
 'recovery_overlay_coupled_base_dd_change':0,
 'strict_objectives':{'net_min':200000,'trades_min':12000,'trades_max_exclusive':30000,'pf_min_exclusive':15,'gross_loss_abs_max_exclusive':10000,'full_tick_eq_dd_max_exclusive':10000,'satisfied_all':False},
 'guard_example': next(x for x in eq if x['cut']==8 and x['limit']==12000),
 'daily_worst_profit':daily[0]['worst'],'daily_worst_prevention':daily[1]['worst'],
 'recovery_test_restrictions':'All new positions fixed 0.01; built from accepted predecessor at observed failure and prior completed M5/H1; no lost money sizing, not crediting shadow P/L. Recovery overlay does NOT feed back into original source candidate generation, so NOT complete funded V1.',
 'blocking_constraints':['source tape fixed hypothetical parent-generation remaining','native original L5 and L6 not restored','broker-execution L7/MT5 fills and realistic margin not certified','fitted in-sample February thresholds','1536-position capacity and 10/sec are not $100–$300 deployment claims'],
 'tests':'SHA256 PASS, archived profit and lower-DD exact replay reconciliation from previously validated ledgers; independent recovery-side Bid/Ask cashflow assertions PASS in tested combinations',
 'status':'DIAGNOSTIC_NULL_RESULT_NO_STRATEGY_PROMOTION'
}
(R/'FEB046_FINAL_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
lines='''# FEB046 — Integrated Loss Prevention + Funded-Failure Recovery Research

**Research status:** Completed exploratory FEB046 diagnostic; **no strategy upgrade or full-V1/MT5 certification**. Original owner *unabridged* eight-layer V1 whitepaper governs all work and remains unchanged. February is a known in-sample optimization month, not a blind forecast.

## Why portfolio repair is an original V1 responsibility

The owner's original L0→L1→L2→L3→L4→L5→L6→L7 design already demands fully cooperative session-specific grid opportunity manufacture, completed H4/H1/M15/M5 structure, dense London/overlap/NY hourly harvesting, separate Asia geometry, realized-child Watchdog renewal, native trend-within-trend routing, failure-conditioned recovery, and unified funded heat and margin risk. **Combined portfolio repair is not a new layer.** The missing engineering part is a fully endogenous source and funding/exit feedback loop. This checkpoint tests candidate risk mechanisms around the archived FEB045 accepted portfolio; it does not claim to reconstruct the missing entire V1.

## Frozen February baseline

| February source-model accepted portfolio | Net USD | Realized gross loss USD | PF | Complete trades | All-quote equity DD USD | Max modeled open |
|---|---:|---:|---:|---:|---:|---:|
| FEB045 nine-pocket profit cushion | +206,528.578 | -7,616.383 | 28.116 | 25,443 | 19,308.087 | 1,536 |
| FEB045 capped prevention | +200,982.522 | -8,721.152 | 24.045 | 25,313 | 16,458.447 | 1,536 |

Underlying February original Bid/Ask 7,538,339 quotes plus 3,900,880 January context quotes = 11,439,219. Verified January and February gzip SHA256 values in `FEB046_FINAL_QA.json`. Modeled $100k initial account, fixed 0.01 lots, $0.02 roundtrip fee, unreconstructed Coinexx fills and margin. Order admission cap is 1 per tick, up to 10 per second.

## Research families and observed results

### 1. L6 post-*realized*-loss recovery overlay

After a genuinely accepted predecessor closed at a loss, enter **only on a later observed quote** if completed M5, H1, or both support a chosen continuation/reversal direction. Model independent entry, first-touched executable Bid/Ask TP/SL, timeout, own recovery cap and the inherited baseline account capacity and 10/s rate at entry. Test 18 configurations (`recovery_experiments.py`, JSON ledger). Every new recovery trial with actual trades showed *negative incremental net*; best net-preserving screened result was a negative $43.785 with 38 recovery trades, with baseline exact DD unchanged for the independently fully checked leading variants. Because original accepted upstream entries are frozen, this is **an overlay diagnostic**, not an endogenous V1 funded simulation.

### 2. Strict pre-close L6 structural recovery overlay

Require that an *actually funded and still-open* S22 or S25 predecessor has failed after an already-elapsed 60/180/300 seconds, exhibits an entry-known adverse price displacement of $3/$6/$10, and BOTH completed M5 and H1 structural slopes support the prospective corrective trade. One fixed-lot recovery at most per observed predecessor, separate TP/SL, eight-or-sixteen own-risk capacity with the baseline account order rate. Eighteen screens (`structural_recovery_overlay.py`) rarely identified sufficiently confirmed failures; the 300s/$3 threshold allowed 16 additional trades and produced -$33.608 net at $3 TP/$2 SL. More permissive 180s/$1 thresholds generated additional trades but negative incremental profit. These are not original-L6 native geometry or a certified anti-hedge.

### 3. Prevention-only vs combination ablations

The same 5 L6 overlays were applied separately to the original FEB045 profit cushion and to its lower-DD *prevention* portfolio (`combined_test.py`). **All ten combinations reduced net and increased realized gross loss; exact maximum equity DD remained unchanged** at 19,308.087 or 16,458.447 respectively. The overlays do not regenerate future source proposals or consume broker-correct future capacity as a true active engine would. All new recovery prices/settlements are quote-side reconciled.

### 4. Pre-close structure/stop experiments

A structurally permissioned reduce-only exit requires an actual still-open position, already-elapsed failure window, first observed adverse price threshold, and *completed* M5 trend against the position. The cloned source engine re-runs chronological admissions with altered first-touch exits, not a retroactive classification of accepted trades. Six focused threshold combinations and 13 initial screens completed. The S25 180-second/$18 adverse-exit case dropped model net to $184,888 and raised gross loss to -$22,404; **true max equity DD stayed at $19,308** despite lower sampled entry-event DD. Exit timing can prematurely crystallize recoverable temporary loss.

### 5. Realized-funded-loss source re-lock

An actual source close at P/L <0 updates that source's loss timestamp; follow-on source proposals can be rejected for 5–15 minutes, optionally until completed M5 structural confirmation. Source S22/S25 accounts for only 39/58 baseline realized losers, respectively; the market-reversal floating losses come mainly from originally winning baskets. Six final 5/15-minute source re-lock screens (`run_loss_relock_focus.py`) confirmed no exact DD reduction. Relocking S17/S19 reduces net by ~$2.2K over five minutes while saving only about $0.45 gross loss. There are earlier broad 13 cases, not all completed due runtime interruption; see original logs.

### 6. L7 portfolio-wide peak-equity admission guard

A cloned portfolio engine computes actual *observed-at-proposal* account net liquidation equity from the currently accepted tickets, updates peak equity causally, and denies NEW admissions above a calibrated floating DD threshold. Twelve configurations over two source-quality policies completed. A $12k admission-event guard on the prevention variant produced +$200,245.212 net, PF 23.9609, gross loss -$8,721.152, 25,490 trades, **$19,308.087 exact all-tick DD** despite its entry-event DD of $11,923.57. The guard prevents future admissions but **does not close already adverse baskets**. This is why sampling equity at entry or throttling new tickets cannot be used as proof of the hard <$10K all-quote DD constraint.

## Important daily January→February adaptive lesson

The February profitable-trade system has **multiple** independent high-DD days: Feb 11 $19,308, Feb 20 $17,184, Feb 4 $14,131, Feb 24 $10,206, Feb 27 $10,053 intraday all-quote DD. The first three nevertheless realized +$33,732, +$50,526 and +$35,030 net respectively. A governor engineered solely to hide Feb 11 will fail on another day. See full daily/weekly data in `DAILY_FORENSICS.json`.

## Core research inference and next engineering unit

**No tested FEB046 candidate simultaneously satisfied all five previously declared targets: $200k net, 12k–<30k trades, PF>15, realized gross loss magnitude<$10k, and true full-tick floating DD<$10k.** Several controls improved snapshots but did not change peak quote DD; others cut recoverable profitable inventory and destroyed net. The observed loss is an *unrealized, correlated portfolio risk* and cannot be fixed by after-the-fact recovery.

The next test needs a **single chronological, causal economic engine**, not a fixed upstream tape and external overlays: native L0 executable ticks; L1 session-specific cell genealogy; completed H4/H1/M15/M5 states; L3 London/NY heartbeat & separate Asia; L4 close-confirmed Watchdog; L5 structural transfer; L6 actually failure-conditioned recovery and independent invalidation; L7 quote-level account/equity/margin and stress-aware incremental admission/reduction. It must feed funded exits back into the next source proposal, permit reduce-only before dangerous concentration develops, and measure capacity opportunity substitution rather than merely suppress future trades. Fix physical-genealogy gate **033** before promoting February risk fixes. Original owner V1 permanently frozen, August sealed, September reserved.

## External reconstructible technical ideas (not imported profits)

- MetaQuotes, *Building a Research-Grounded Grid EA in MQL5*, finite/restartable risk-bounded grid: https://www.mql5.com/en/articles/21833
- MetaQuotes, *Building a Correlation-Aware Multi-EA Portfolio Scorer in MQL5*, portfolio correlation exposure: https://www.mql5.com/en/articles/21955
- MetaQuotes, *Engineering Trading Discipline into Code (Part 7)*, governance state transitions: https://www.mql5.com/en/articles/22833
- MetaQuotes Chinese, *交易机器人风险管理器（第一部分）*, order-approval risk manager: https://www.mql5.com/zh/articles/18918
- Community discussion on overlapping multi-strategy heat risk: https://www.reddit.com/r/algotrading/comments/1rtwnfm/approaches_to_risk_management_and_order_size/

These published mechanisms motivate finite risk limits and heat governance; their claimed performance is not evidence of this user's EA performance. Kelly or dynamic lot escalation is **not allowed**; our experiments retained the owner's fixed 0.01 lot and no Martingale.

## Reproduction and caveats

Run from the original month archives and FEB044/FEB045 bundles whose SHA values are verified. Source scripts include `recovery_experiments.py`, `structural_recovery_overlay.py`, `combined_test.py`, `structural_exit_test_narrow.py`, `run_loss_relock_focus.py`, `run_equity_guard.py`, `daily_forensics.py`, plus cloned prototype engines. All source-model variant selections are February-exposed, **not blind**. Read `FEB046_FINAL_QA.json` and the raw scenario JSON files. No original owner whitepaper, production Delta, or MT5 EA modification is authorized or undertaken.
'''
(R/'FEB046_RESEARCH_REPORT.md').write_text(lines)
read='''# FEB046 — READ FIRST

1. Owner original literal 14,232-character V1 whitepaper: GitHub `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt`. Read all L0–L7 sections before new V1 work; do not substitute abridged L0–L8 derivatives. No changes to original V1, production Delta or MT5 EA.
2. Latest predecessor research journal is GitHub 0063 (FEB045). FEB046 owner research specification is `research/delta_a_alpha/monthly/february_2026/feb046_recovery/FEB046_OWNER_ELIMINATION_AND_RECOVERY_DIRECTIVE.md`. Update journal only as research, not promotion.
3. Source month sha: Feb `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, Jan warmup `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. 11,439,219 quote indices combined. No August or September used.
4. BASELINE FEB045 +206,528.578, PF28.116, GL -7616.383, 25,443 trades, exact equity DD19308.087; prevention-only +200,982.522, PF24.045, GL -8721.152, 25,313, DD16458.447. Both fixed 0.01 lot, source-generated input, modeled 1536 peak concurrency, 10 entries/s. Neither certified funded-V1.
5. FEB046 present tests: 18 after-paid-loss recovery, 18 strict preclose M5+H1 recovery, 10 combined prevention/recovery overlays, 19 initial/focused structural exits (13 initial, 6 focused), 6 finalized funded loss-source relocks, 12 whole-account peak equity guard variants. All are February in-sample screens. No combination obtained <$10,000 exact DD while preserving other rules. Full experiment logs and scripts in FEB046 ZIP.
6. Major source observation: large profitable S22/S25 baskets suffer temporary correlated floating loss. Later small recovery trades cannot fix their earlier equity trough. Entry-event equity DD and full-tick equity DD differ profoundly. Recovery must be endogenously linked to causal already-funded failure with original L5/L6 structural ownership and an account-wide L7 risk budget.
7. Stop loss research not automatically equivalent to risk improvement: structural adverse exits often crystallized losses from eventual winners. Never count counterfactual future trades as funded parent-child unlock credit. Ignore February outcome-fitted month switches. No Martingale/DCA; fixed research 0.01 lot.
8. Remaining next engineering unit `DAA_JAN1_FULL_V1_PHYSICAL_FUNDED_GENEALOGY_REPAIR_AND_PARITY_033`. Restore all V1 layers and endogenous generator rerun upon accepted, rejected, closed decisions; broker margin/slippage/stopout physical feasibility. Freeze JAN039 and FEB043/045 as research comparators only, August sealed September reserved.
'''
(R/'FEB046_HANDOFF_READ_FIRST.md').write_text(read)
paths=[p for p in R.iterdir() if p.is_file() and p.suffix in ['.py','.json','.md','.log']]
paths=sorted(paths,key=lambda p:p.name)
zip_path=Path('/mnt/data/FEB046_COMBINED_PORTFOLIO_RECOVERY_RESEARCH.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
 for p in paths:z.write(p,arcname='FEB046/'+p.name)
with zipfile.ZipFile(zip_path) as z:
 bad=z.testzip();n=len(z.namelist())
 assert bad is None
print('QA_SHA',json.dumps(hashes,sort_keys=True))
print('QA_SCENARIOS',json.dumps(qa['experiment_counts']),'SUM',qa['tested_minimum_evaluations'])
print('QA_BASE',json.dumps(qa['original_feb045_baselines']))
print('QA_RECOVERY_ACTIVE',qa['new_recovery_trials_with_actual_trades'],'PROFITABLE',qa['new_recovery_trials_profitable'])
print('ZIP_OK',n,zip_path.stat().st_size)