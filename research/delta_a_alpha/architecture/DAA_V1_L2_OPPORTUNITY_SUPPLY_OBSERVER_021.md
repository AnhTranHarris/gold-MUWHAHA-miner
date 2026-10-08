# Delta-A-alpha V1 L2 Opportunity Supply Observer — research sidecar 021

**Status:** preserved as a VALIDATED MARKET-STATE FORECAST candidate, but **OBSERVE-ONLY**. This branch does NOT change permanent V1 L0–L8 order, live EA, original January–April monthly research ledgers or frozen state. No change to May 137 (owner-paused). August sealed.

## Exact lattice placement

```
L0  ordered real Bid/Ask tick root (execution/time/cost authority)
L1  session-specific lattice geometry (Asia vs London/overlap/NY)
L2  completed H4/H1/M15/M5 structure
    + NEW: M5 Opportunity Supply Observer (forecast ONLY)
       predicts at least 2 of next 12 M5 bars spanning >= $10
       from 8 input features of PREVIOUS 12/48/144 completed M5 bars
L3  London/overlap/NY high-volume / fresh hourly owners
L4  distinct Asia geometry
L5  Watchdog earned renewal: shadow forecast visible but not authorized to veto/fund
L6  trend-within-trend original signal router unchanged
L7  wrong-direction conditional recovery unchanged
L8  global heat/capital governor unchanged, can log prediction telemetry
```

The observer exports `probability_of_large_excursion_supply`, model training maturity/provenance and `mode=OBSERVE_ONLY_NO_ORDER_EFFECT`. It produces no direction, no buy/sell order, no calendar switch, no trade lot adjustment, no renewal credit, no hypothetical realized P/L. `lot_size=0.01`, no martingale and no loss-dependent sizing. Market activity forecast does not have economic return authority.

**January-1 chronological availability:** the January–February-frozen model cannot be used until those labeled samples mature, so activation earliest 2026-03-01 UTC. A separate experimental weekly-expanding cold-start model, trained only from labels matured in the past, could first forecast Jan 12 11:00 UTC. Neither model may affect trades until independent raw-tick execution A/B validates financial benefit.

## Completed 2026 Jan–Apr observational replay

Dukascopy ordered ticks -> 23,147 completed M5 bars -> 1,560 eligible hourly labels (no overlapping future bar target in an individual forecast). January-start weekly cold model results:

- Jan 280 forecasts, 41.43% high-opportunity hours, AUC 0.8289
- Feb 373 forecasts, 53.89%, AUC 0.8870
- Mar 408 forecasts, 60.54%, AUC 0.8496
- Apr 396 forecasts, 32.32%, AUC 0.8039

Frozen JanFeb-trained weights (756 complete prior labels), Mar AUC 0.8500, Apr AUC 0.8002. Online refit has 16 audited checkpoints with all training outcomes already matured when training happens. Exact local inference vs sklearn parity 30 vectors, largest error 1.41e-14. This is **movement-supply classification, not profitable trade backtest**.

## Critical limitation

Existing V1 MQL5 is observe-only with no order-send path; Jan/Feb/Mar historical extraordinary gains are month-outcome-selected *research frontiers*, not one rule-frozen, Jan-1-start runnable EA. No honest V1 Jan–Apr A/B daily/weekly/monthly P&L exists from those artifacts; none is asserted here. Daily/weekly/monthly **forecast** scorecards are preserved.

## Exact saved research

Project Library: `/xauusd-trading-bot/delta-A-alpha/monthly/april_2026/vertical-grid-136/jan1-v1-l2-observer-021/`

`DAA_V1_L2_JAN1_OPPORTUNITY_SUPPLY_REPLAY_REPORT.md`, `DAA_JAN1_POS_DAILY_WEEKLY_MONTHLY.xlsx`, `DAA_JAN1_BLIND_L2_REPLAY_SCORECARDS.json`, `DAA_L2_OPPORTUNITY_SUPPLY_FROZEN_JANFEB_MODEL.json`, `l2_opportunity_supply.py`, `jan1_blind_awareness_replay.py`, `validate_l2_opportunity_supply.py`, `DAA_L2_JAN1_AWARENESS_REPLAY_021.tar.gz`. Archive SHA256 `054cee78df33da86a3de47788c75dcd35285b73d3d464219c03516c5f4788cef`; raw source hashes and restored input M5 caches inside.

No production branch changes. New economic effect requires forward tick-causal full V1 generator/EA, single prior-frozen ruleset, paired A/B live-Jan1 simulation, actual executable spread/commission/portfolio margin and full floating equity.
