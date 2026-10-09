# Delta-A-alpha V1 — physical funded execution repair 033, PHASE A

**Status: partial ENGINEERING implementation, NOT full owner V1 parity, NOT a new trading algorithm, NOT an MT5 release.** First source of trading truth remains the **literal 14,232-character OWNER-FROZEN V1 whitepaper** `research/delta_a_alpha/whitepapers/DAA_V1_OWNER_GOOGLE_WHITEPAPER_FULL_VERBATIM_030.txt` (Git blob `1b92b3c89159681a7181508de158af685cf5780c`). Source lineage `049→051→075→084→119→131D→131E`, February original `134E/134K` is immutable. No rewriting the whitepaper, no switching from L0–L7 to a simplified architecture.

## Preserve accepted research evidence (unchanged)

- Jan039 **+$201,226.483 / 12,520 / PF37.1768 / gross loss -$5,562.307 / exact source-model DD $12,640.925**.
- February frozen FEB045 and FEB047 accepted *research-only* alternatives remain intact; e.g. FEB047 profit **+$206,303.048 /25,443/PF28.09/GL-$7,615.393/DD$17,183.829**, FEB047 lowest DD **+$200,329.84 /25,313/PF23.97057/GL-$8,721.152/DD$15,741.936**.
- Their **original** binary archives/hashes are anchored in `FROZEN_JAN_FEB_RESEARCH_033.json`. No global auto-activation by month name, and no claim these results will be retained under new funded source regeneration.

## Real code now built and tested

`v1_funded_core_033.py`: one actual executed-fill state ledger for L3–L6 signals; chronological true ask-entry/bid-exit and bid-entry/ask-exit; fixed 0.01; entry and exit commission; single per-quote/per-second order budget; explicit diagnostic leverage/margin, exposure and signed-direction and cell/source limits; portfolio gross realized P/L, full tick-floating-equity peak/DD; account reduce-only queue; no phantom liquidation; L4 funded scout+family+earned child gate and relocks from only **actual L4 closes**; L6 no recovery without genuinely funded predecessor, observed adverse quote/M5 evidence, limited window and one recovery per parent; chronological decision feedback to all source adapters; actual history timestamps for all completed H4/H1/M15/M5 required; early eligibility with genuine already-completed bar history; no runtime month identity; no Martingale or loss-dependent sizing.

`OriginalHourlyHeartbeatL3`: online causal entries extracted **without future exit arrays** from original 019 `heartbeat_candidates` (UTC hour, completed source H4/H1/M15/M5, source cadence and TP/SL/timeout). `test_original_heartbeat_parity_033.py` extracts the archived original 019 functions and compares complete entry records against the new online adapter on deterministic synthetic tick fixtures. Other original L3 and distinct Asia generators are **not** yet integrated.

`economic_scorecard_033.py`: trade, hour, UTC day, ISO week, month and year partitions of genuine closed fills, strictly after the fact; not calendar execution switches.

`real_dukas_event_smoke_033.py`: independently verified original January/February compressed Dukascopy hashes, January 10-day genuine warm-up and February continuous 1,136,212-tick subset (2026-02-02..03); uses original 131E `stmr_janjul.bar_states_span` exact function for *diagnostic* as-of EMA sign state, **not a faithful implementation of all original H4/H1/M15/M5 structural roles**. $100K research balance and an explicitly diagnostic 16-position/3 order-sec mock broker. Result was **−$583.745 net, 836 completed L3-only positions, PF0.7246, exact all-tick DD $1,158.88**. **Not Feb performance and not a comparison to Jan039 or Feb047; do not promote or optimize this diagnostic.**

Tests:
```
python -m unittest -v test_v1_funded_core_033.py test_original_heartbeat_parity_033.py test_scorecard_033.py
python real_dukas_event_smoke_033.py --root /mnt/data --max-events 1250000
```
Python 3.11+; numpy, pandas. The original 019 comparison and February diagnostic need existing `JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip` and true Jan/Feb `.csv.gz` archives in `/mnt/data`; no August data.

## Critical remaining work — gate 033 NOT closed

1. **L1 source parity:** incorporate original first-touch session grid event genealogies, independent Asia geometry, London, NY and late handoffs. The original online L3 heartbeat adapter is only one subset; never substitute a generic grid.
2. **L2 original full structural role parity:** reconstruct completed original H4 environment/H1 parent location/M15 phase/M5 transfer beyond EMA sign diagnostic; exact pre-T0 genuine history, timezone/DST/market closures and five-minute qualified initial quote rule.
3. **L3 full source parity:** load all original hourly and Asia stream geometries and precondition gates from archived 049–131E and February 134E/134K, as online source functions rather than frozen future-result proposals.
4. **L4 complete 049→051→075→084→119→131D/E native campaign parity:** exact original renewal geometry, cell ownership, scout children, dynamic regime handoff, profit/hold transitions, relock, layer-depth and rescout semantics. The kernel enforces actual credit and boundedness; **it does not independently recreate all original Watchdog proposed entries**.
5. **L5 full source-native continuation / pullback selector**, bounded L6 recovery proposal generator/exit/invalidation (kernel has eligibility/finite budget but NOT original trade signal), and truly cooperative sharing of state and capital with L3/L4.
6. **L7 broker parity:** actual Coinexx XAUUSD contract, fee, tick-value, leverage, position accounting (hedging vs netting), spread/slippage, queue, order acceptance, margin-call/stopout model. An idealized quote-side research fill with a diagnostic margin calculation **does not certify Coinexx fills**.
7. **Jan+Feb regression:** replay all original V1 source events endogenously across **9,135,062 January + 7,538,339 February quotes**, compare original baseline and frozen JAN039/FEB045/FEB047 options. Correcting previously phantom descendants may materially alter historical profits. Record causal differences before promotion; don't silently calibrate to historical ceiling.
8. **MQL5 port:** only after reproducible layer-level Python source equivalence and broker risk parity; compile clean in actual MetaEditor, MT5 Every tick based on real ticks, then long demo/survivability. The existing `Experts/GoldMuwahahaMiner_DeltaAAlpha_V1.mq5` v1.05 is observe-only and remains unchanged.

**March research remains on hold until full original V1 source-engine funded parity (gate 033) is closed.** Preserve August sealed, September reserved. The objective is robust long-term adaptive market-state learning based on *completed observable data and actually realized funded outcomes*, not calendar-month knowledge, retrospective winning-parameter lookup, or infinite position inventory.